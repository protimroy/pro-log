"""Compare zero-update suffix compilation and backprop at a shared loss target."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import time
from types import SimpleNamespace

import numpy as np
import torch

from r09_character_model import SHA256, V, load_splits
from r10_long_context import (BUDGET, HISTORY, WIDTH, Decoder, KneserNey, Level,
                              bits_per_char, compile_program, encode, parameter_count, predict, windows)


DISCOUNT = 0.95
ORDER = 6
RANKINGS = ("frequency", "relative_entropy", "support_shrunk")
TARGET = 3.05
SEEDS = (17, 29, 43)


class Meter:
    """Read each accessible CPU package at most once. Average watts are joules / seconds."""

    def __init__(self):
        self.zones = {}
        for root in (Path("/sys/class/powercap"), Path("/sys/class/power_cap")):
            for path in [*root.glob("*/energy_uj"), *root.glob("*/*/energy_uj")]:
                zone = path.parent
                try:
                    name = (zone / "name").read_text().strip()
                    if name.startswith("package-"):
                        int(path.read_text())
                        self.zones[path.resolve()] = int((zone / "max_energy_range_uj").read_text())
                except (OSError, ValueError):
                    continue

    def read(self):
        values = {}
        for path in self.zones:
            try:
                values[path] = int(path.read_text())
            except (OSError, ValueError):
                pass
        return time.perf_counter(), time.process_time(), values

    def elapsed(self, start):
        end = self.read()
        seconds = end[0] - start[0]
        joules = None
        if start[2] and start[2].keys() == end[2].keys() == self.zones.keys():
            joules = 1e-6 * sum((end[2][p] - v) % self.zones[p] for p, v in start[2].items())
        return {"wall_seconds": seconds, "process_cpu_seconds": end[1] - start[1],
                "package_joules": joules, "mean_package_watts": None if joules is None else joules / seconds}


def fit_teacher(train):
    context_keys = encode(train[0])
    keys = context_keys * V + train[1]
    raw = {h: Level.create(*np.unique(keys % V**(h + 1), return_counts=True))
           for h in range(1, ORDER + 1)}
    return KneserNey(raw, ORDER), raw


def build_tables(kn, raw):
    distributions = {0: np.log(kn.unigram[None, :])}
    candidates = []
    for length in range(1, ORDER + 1):
        level = raw[length]
        histories = level.histories
        queries = np.repeat(histories, V)
        targets = np.tile(np.arange(V), len(histories))
        terms = kn.terms(queries, targets)
        full = kn.evaluate(targets, DISCOUNT, terms[:length]).reshape(-1, V)
        short = kn.evaluate(targets, DISCOUNT, terms[:length - 1]).reshape(-1, V)
        distributions[length] = dict(zip(histories, np.log(full)))
        if length > 2:
            kl = (full * (np.log(full) - np.log(short))).sum(axis=1)
            candidates.extend((length, int(key), int(count), float(gain))
                              for key, count, gain in zip(histories, level.totals, kl))
    return distributions, candidates


def choose_suffixes(distributions, candidates, hidden, ranking):
    base = set(distributions[2])
    room = hidden - V - len(base)
    def priority(row):
        length, key, count, kl = row
        score = count
        if ranking != "frequency":
            score *= kl
        if ranking == "support_shrunk":
            score *= count / (count + 4)
        return (-score, length, key)

    selected = {(length, key) for length, key, _, _ in sorted(candidates, key=priority)[:room]}
    bigram = np.tile(distributions[0], (V, 1))
    for key, value in distributions[1].items():
        bigram[key] = value
    pairs = np.array(sorted(base))
    pair_delta = np.stack([distributions[2][key] - bigram[key % V] for key in pairs])
    extra = []
    for length, key in sorted(selected):
        parent = bigram[key % V]
        for h in range(length - 1, 1, -1):
            suffix = key % V**h
            if (h, suffix) in selected or (h == 2 and suffix in base):
                parent = distributions[h][suffix]
                break
        extra.append((length, key, distributions[length][key] - parent))
    return SimpleNamespace(bigram=bigram, pairs=pairs, pair_delta=pair_delta), extra


def direct(distributions, program, extra, x):
    keys = encode(x)
    result = program.bigram[x[:, -1]].copy()
    for length, group in [(2, {(2, key) for key in program.pairs})] + [
        (h, {(h, key) for level, key, _ in extra if level == h}) for h in range(3, ORDER + 1)
    ]:
        retained = sorted(key for _, key in group)
        if not retained:
            continue
        idx = np.searchsorted(retained, keys % V**length).clip(max=len(retained) - 1)
        mask = np.array(retained)[idx] == keys % V**length
        result[mask] = np.stack([distributions[length][key] for key in retained])[idx[mask]]
    return result


def dense_forward_flops(hidden):
    # Projection and QK/AV operations only. Each multiply-accumulate counts as two FLOPs.
    return 2 * (2 * HISTORY * WIDTH**2 + 3 * WIDTH**2 + WIDTH * hidden
                + hidden * V + WIDTH * V + 2 * HISTORY * WIDTH)


def train(seed, train_split, dev, hidden, steps, meter):
    start = meter.read()
    torch.manual_seed(seed)
    model = Decoder(hidden)
    opt = torch.optim.AdamW(model.parameters(), lr=0.003)
    x, y = (torch.from_numpy(v) for v in train_split)
    permutation = iter(())
    curves, count, best = [], 0, math.inf
    first, first_state = None, None
    for step in range(steps + 1):
        if step % 100 == 0 or step == steps:
            loss = bits_per_char(predict(model, dev[0]).astype(np.float64), dev[1])
            snapshot = {"step": step, "validation_subset_bpc": loss, "training_windows_processed": count,
                        "validation_windows_processed": (len(curves) + 1) * len(dev[1]),
                        "cost": meter.elapsed(start)}
            curves.append(snapshot)
            if loss < best:
                best, best_row = loss, snapshot
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            if loss <= TARGET and first is None:
                first = snapshot
                first_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if step == steps:
            break
        idx = next(permutation, None)
        if idx is None:
            permutation = iter(torch.randperm(len(y)).split(256))
            idx = next(permutation)
        opt.zero_grad(set_to_none=True)
        nn_loss = torch.nn.functional.cross_entropy(model(x[idx]), y[idx])
        nn_loss.backward()
        opt.step()
        count += len(idx)
    cost = meter.elapsed(start)
    test_states = {"best": best_state}
    if first_state is not None:
        test_states["first_target"] = first_state
    return model, test_states, {"seed": seed, "total_cost": cost, "best": best_row,
                                "first_target": first, "curve": curves}


def token_reference(path):
    record = {"encoding": "o200k_base", "actual_session_tokens": None}
    try:
        import tiktoken
        encoding = tiktoken.get_encoding(record["encoding"])
        for name in ("prompt", "spec"):
            record[f"reference_{name}_tokens"] = len(encoding.encode((path / f"design-{name}.txt").read_text()))
    except (ImportError, OSError, ValueError) as exc:
        record["reference_unavailable"] = type(exc).__name__
    return record


def run(args):
    torch.set_num_threads(args.threads)
    meter = Meter()
    prep = meter.read()
    train_split, dev_full, test = [windows(x) for x in load_splits(args.corpus, 100_000)]
    dev = tuple(x[np.linspace(0, len(dev_full[1]) - 1, 8192, dtype=int)] for x in dev_full)
    hidden = (BUDGET - parameter_count(Decoder(1))) // (WIDTH + 1 + V) + 1
    shared = meter.elapsed(prep)
    records = {"sha256": SHA256, "threads": args.threads, "parameters": parameter_count(Decoder(hidden)),
               "matched_validation_bpc": TARGET, "splits": [len(x[1]) for x in (train_split, dev_full, test)],
               "shared_preparation": shared, "energy_domains": [str(p) for p in meter.zones],
               "dense_forward_projection_and_attention_flops_per_window": dense_forward_flops(hidden),
               "llm_tokens": token_reference(args.design_dir)}
    if args.arm in ("all", "compiled", "direct"):
        started = meter.read()
        kn, raw = fit_teacher(train_split)
        reference_validation = -np.log2(kn.evaluate(dev[1], DISCOUNT, kn.terms(encode(dev[0]), dev[1]))).mean()
        records["direct_kn"] = {"validation_subset_bpc": float(reference_validation), "cost": meter.elapsed(started)}
        if args.arm != "direct":
            distributions, candidates = build_tables(kn, raw)
            methods, installations = {}, {}
            for ranking in RANKINGS:
                attempt = meter.read()
                program, extra = choose_suffixes(distributions, candidates, hidden, ranking)
                model, gates = compile_program(program, hidden, False, 0, history_deltas=extra)
                loss = bits_per_char(predict(model, dev[0]).astype(np.float64), dev[1])
                methods[ranking] = {"validation_subset_bpc": loss, "active_gates": gates,
                                    "long_gates_by_length": dict(Counter(length for length, _, _ in extra)),
                                    "incremental_cost": meter.elapsed(attempt)}
                installations[ranking] = (program, extra, model)
            chosen = min(methods, key=lambda name: methods[name]["validation_subset_bpc"])
            records["compiled"] = {"selection": chosen, "total_cost": meter.elapsed(started),
                                   "optimizer_steps": 0, "methods": methods}
            synthetic = np.random.default_rng(913).integers(V, size=(4096, HISTORY))
            for name, (program, extra, model) in installations.items():
                test_logits = predict(model, test[0]).astype(np.float64)
                methods[name]["test_bpc"] = bits_per_char(test_logits, test[1])
                for label, inputs, logits in (("test", test[0], test_logits),
                                               ("random", synthetic, predict(model, synthetic).astype(np.float64))):
                    expected = torch.from_numpy(direct(distributions, program, extra, inputs)).softmax(-1)
                    actual = torch.from_numpy(logits).softmax(-1)
                    error = float((expected - actual).abs().max())
                    if error > 2e-6:
                        raise RuntimeError(f"Compiler parity failed: {error}")
                    methods[name][f"max_probability_error_{label}"] = error
                if name == chosen and args.checkpoint:
                    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
                    torch.save(model.state_dict(), args.checkpoint)
        records["direct_kn"]["test_bpc"] = -float(np.log2(kn.evaluate(
            test[1], DISCOUNT, kn.terms(encode(test[0]), test[1]))).mean())
    if args.arm in ("all", "adamw"):
        records["adamw"] = []
        for seed in args.seeds:
            model, states, row = train(seed, train_split, dev, hidden, args.steps, meter)
            for name, state in states.items():
                model.load_state_dict(state)
                row[name]["test_bpc"] = bits_per_char(predict(model, test[0]).astype(np.float64), test[1])
            records["adamw"].append(row)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=Path("data/r09-tinyshakespeare.txt"), type=Path)
    parser.add_argument("--design-dir", default=Path("runs/r11"), type=Path)
    parser.add_argument("--output", default=Path("runs/r11/metrics.json"), type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--arm", choices=("all", "compiled", "adamw", "direct"), default="all")
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if args.steps < 0 or args.threads < 1:
        parser.error("steps must be nonnegative and threads positive")
    result = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
