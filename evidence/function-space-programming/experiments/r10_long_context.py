"""Compile a parameter-budgeted eight-character predictor and compare matched controls."""
import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import platform
from time import perf_counter

import numpy as np
import torch
from torch import nn

from r09_character_model import ALPHABET, LOG2, SHA256, SOURCE, V, load_splits


HISTORY = 8
WIDTH = 64
BUDGET = 220_510
DISCOUNTS = (0.5, 0.75, 0.9, 0.95, 0.99)
LAG_WEIGHTS = (0.125, 0.25, 0.5, 0.75, 1.0)


def encode(tokens):
    keys = np.zeros(tokens.shape[0], dtype=np.int64)
    for column in tokens.T:
        keys = keys * V + column
    return keys


def windows(tokens):
    rows = np.lib.stride_tricks.sliding_window_view(tokens.numpy(), HISTORY + 1).copy()
    return rows[:, :-1], rows[:, -1]


def lookup(keys, values, query):
    index = np.searchsorted(keys, query)
    index = index.clip(max=len(keys) - 1)
    return np.where(keys[index] == query, values[index], 0)


@dataclass
class Level:
    keys: np.ndarray
    counts: np.ndarray
    histories: np.ndarray
    types: np.ndarray
    totals: np.ndarray

    @classmethod
    def create(cls, keys, counts):
        histories, starts, types = np.unique(keys // V, return_index=True, return_counts=True)
        return cls(keys, counts, histories, types, np.add.reduceat(counts, starts))

    def terms(self, history, target):
        return (
            lookup(self.keys, self.counts, history * V + target),
            lookup(self.histories, self.types, history),
            lookup(self.histories, self.totals, history),
        )


class KneserNey:
    def __init__(self, raw, history):
        unigram = np.bincount(raw[1].keys % V, minlength=V) + 0.5
        self.unigram = unigram / unigram.sum()
        self.levels = []
        for h in range(1, history + 1):
            if h == history:
                level = raw[h]
            else:
                keys, counts = np.unique(raw[h + 1].keys % V ** (h + 1), return_counts=True)
                level = Level.create(keys, counts)
            self.levels.append(level)

    def terms(self, history, target):
        return [level.terms(history % V**h, target) for h, level in enumerate(self.levels, 1)]

    def evaluate(self, target, discount, terms):
        probs = self.unigram[target]
        for observed, types, total in terms:
            adjusted = np.maximum(observed - discount, 0)
            probs = np.where(total, (adjusted + discount * types * probs) / np.maximum(total, 1), probs)
        return probs

    def matrix(self, keys, discount):
        histories = np.repeat(keys, V)
        target = np.tile(np.arange(V), len(keys))
        return self.evaluate(target, discount, self.terms(histories, target)).reshape(-1, V)


class Decoder(nn.Module):
    def __init__(self, hidden):
        super().__init__()
        self.tokens = nn.Embedding(V, WIDTH)
        self.positions = nn.Parameter(torch.empty(HISTORY, WIDTH))
        self.q = nn.Linear(WIDTH, WIDTH, bias=False)
        self.kv = nn.Linear(WIDTH, 2 * WIDTH, bias=False)
        self.mix = nn.Linear(WIDTH, WIDTH, bias=False)
        self.residual = nn.Linear(WIDTH, WIDTH, bias=False)
        self.up = nn.Linear(WIDTH, hidden)
        self.out = nn.Linear(hidden, V)
        self.skip = nn.Linear(WIDTH, V, bias=False)
        nn.init.normal_(self.tokens.weight, std=0.15)
        nn.init.normal_(self.positions, std=0.15)

    def forward(self, sequence):
        x = self.tokens(sequence) + self.positions
        last = x[:, -1]
        head_width = WIDTH // HISTORY
        q = self.q(last).reshape(-1, HISTORY, 1, head_width)
        k, v = self.kv(x).reshape(-1, HISTORY, 2, HISTORY, head_width).permute(2, 0, 3, 1, 4)
        # The readout is at the final position. Every key is at or before it.
        attended = nn.functional.scaled_dot_product_attention(q, k, v).reshape(-1, WIDTH)
        features = self.mix(attended) + self.residual(last)
        return self.out(self.up(features).relu()) + self.skip(features)


def parameter_count(model):
    return sum(x.numel() for x in model.parameters())


def one_hot_bits():
    return (np.arange(V)[:, None] >> np.arange(6)) & 1


@torch.no_grad()
def compile_program(program, hidden, suffix_weight, lag_weight, *, history_deltas=()):
    model = Decoder(hidden)
    for param in model.parameters():
        param.zero_()
    bits = torch.tensor(one_hot_bits(), dtype=torch.float32)
    head_width = WIDTH // HISTORY
    model.tokens.weight[:, :6] = bits
    for position in range(HISTORY):
        start = position * head_width
        model.positions[position, 6 + position] = 1
        model.q.weight[start, 6:6 + HISTORY] = 1
        model.kv.weight[start, 6 + position] = 64 * math.sqrt(head_width)
        for bit in range(6):
            model.kv.weight[WIDTH + start + bit, bit] = 1
    model.mix.weight.copy_(torch.eye(WIDTH))

    gate = 0

    def write(symbols, logits):
        nonlocal gate
        ones = 0
        for pos, char in symbols:
            start = pos * head_width
            bit_pattern = bits[char]
            model.up.weight[gate, start:start + 6] = 2 * bit_pattern - 1
            ones += int(bit_pattern.sum())
        model.up.bias[gate] = 1 - ones
        model.out.weight[:, gate] = torch.from_numpy(logits)
        gate += 1

    for char in range(V):
        write([(7, char)], program.bigram[char])
    for pair, correction in zip(program.pairs, program.pair_delta):
        write([(6, pair // V), (7, pair % V)], correction)
    if suffix_weight:
        for suffix, delta in zip(program.suffixes, program.suffix_delta):
            write([(5, suffix // V**2), (6, suffix // V % V), (7, suffix % V)], delta)
    if lag_weight:
        for position, ratios in enumerate(program.lag_delta):
            for char, logits in enumerate(ratios):
                write([(position, char)], lag_weight * logits)
    for length, key, delta in history_deltas:
        symbols = [(HISTORY - 1 - offset, key // V**offset % V) for offset in range(length)]
        write(symbols, delta)
    return model, gate


class Program:
    def __init__(self, x, y, raw, base, base_discount, suffix_limit):
        # Fetch probabilities after one level, then subtract their logits from the pair logits.
        target = np.tile(np.arange(V), V)
        histories = np.repeat(np.arange(V), V)
        observed, types, total = base.levels[0].terms(histories, target)
        lower = base.unigram[target]
        probs = np.where(total, (np.maximum(observed - base_discount, 0)
                                + base_discount * types * lower) / np.maximum(total, 1), lower)
        self.bigram = np.log(probs.reshape(V, V))
        self.pairs = raw[2].histories
        self.pair_delta = np.log(base.matrix(self.pairs, base_discount)) - self.bigram[self.pairs % V]
        order = np.lexsort((raw[3].histories, -raw[3].totals))
        self.suffixes = np.sort(raw[3].histories[order[:suffix_limit]])
        next_symbols = np.arange(V)
        delta_counts = lookup(raw[3].keys, raw[3].counts, self.suffixes[:, None] * V + next_symbols)
        lower = base.matrix(self.suffixes % V**2, base_discount)
        posterior = (delta_counts + 16 * lower) / (delta_counts.sum(axis=1, keepdims=True) + 16)
        self.suffix_delta = np.log(posterior) - np.log(lower)
        marginal = np.bincount(y, minlength=V) + 0.5
        marginal /= marginal.sum()
        self.lag_delta = []
        for position in range(HISTORY - 2):
            counts = np.bincount(x[:, position] * V + y, minlength=V**2).reshape(V, V)
            posterior = (counts + 64 * marginal) / (counts.sum(axis=1, keepdims=True) + 64)
            self.lag_delta.append(np.log(posterior) - np.log(marginal))

    def parts(self, x):
        histories = encode(x)
        pair_idx = lookup(self.pairs, np.arange(1, len(self.pairs) + 1), histories % V**2)
        suffix_idx = lookup(self.suffixes, np.arange(1, len(self.suffixes) + 1), histories % V**3)
        zero = np.zeros((1, V))
        base = self.bigram[x[:, -1]] + np.vstack((zero, self.pair_delta))[pair_idx]
        suffix = np.vstack((zero, self.suffix_delta))[suffix_idx]
        lag = sum(ratio[x[:, i]] for i, ratio in enumerate(self.lag_delta))
        return base, suffix, lag


def bits_per_char(logits, target):
    maxima = logits.max(axis=1, keepdims=True)
    stable = logits - maxima
    loss = np.log(np.exp(stable).sum(axis=1)) - stable[np.arange(len(target)), target]
    return float(loss.mean() / LOG2)


@torch.no_grad()
def predict(model, x, batch=512):
    return np.concatenate([model(part).numpy() for part in torch.from_numpy(x).split(batch)])


def train_model(seed, hidden, x, y, dev, steps):
    torch.manual_seed(seed)
    start = perf_counter()
    model = Decoder(hidden)
    opt = torch.optim.AdamW(model.parameters(), lr=0.003)
    batch = 256
    x, y = torch.from_numpy(x), torch.from_numpy(y)
    best_loss = math.inf
    history = []
    permutation = iter(())
    for step in range(steps + 1):
        if step % 100 == 0 or step == steps:
            loss = bits_per_char(predict(model, dev[0]), dev[1])
            history.append({"step": step, "validation_subset_bpc": loss})
            if loss < best_loss:
                best_loss, selected_step = loss, step
                checkpoint = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if step == steps:
            break
        indices = next(permutation, None)
        if indices is None:
            permutation = iter(torch.randperm(len(y)).split(batch))
            indices = next(permutation)
        opt.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(x[indices]), y[indices])
        loss.backward()
        opt.step()
    model.load_state_dict(checkpoint)
    return model, {"seed": seed, "steps_run": steps, "selected_step": selected_step,
                   "fit_seconds": perf_counter() - start, "history": history}


def run(args):
    torch.set_num_threads(args.threads)
    torch.manual_seed(123)
    splits = [windows(tokens) for tokens in load_splits(args.corpus, 100_000)]
    train, dev, test = splits
    start = perf_counter()
    joint_keys = encode(train[0]) * V + train[1]
    raw = {h: Level.create(*np.unique(joint_keys % V**(h + 1), return_counts=True))
           for h in range(1, HISTORY + 1)}
    dev_keys = encode(dev[0])
    test_keys = encode(test[0])
    controls = {}
    kn = {}
    for h in range(1, HISTORY + 1):
        kn[h] = KneserNey(raw, h)
        terms = kn[h].terms(dev_keys, dev[1])
        scores = {discount: -float(np.log2(kn[h].evaluate(dev[1], discount, terms)).mean())
                  for discount in DISCOUNTS}
        selected = min(scores, key=scores.get)
        controls[h] = {"validation_bpc_by_discount": scores, "discount": selected,
                       "validation_bpc": scores[selected],
                       "conditional_entries": sum(len(level.keys) for level in kn[h].levels)}
    chosen_history = min(controls, key=lambda h: controls[h]["validation_bpc"])
    count_seconds = perf_counter() - start

    hidden = (BUDGET - parameter_count(Decoder(1))) // (WIDTH + 1 + V) + 1
    suffix_limit = hidden - V - len(raw[2].histories) - (HISTORY - 2) * V
    start = perf_counter()
    program = Program(*train, raw, kn[2], controls[2]["discount"], suffix_limit)
    program_fit_seconds = perf_counter() - start
    base, suffix, lag = program.parts(dev[0])
    variants = {"base": (0, (0.0,)), "suffix": (1, (0.0,)),
                "lag": (0, LAG_WEIGHTS), "combined": (1, LAG_WEIGHTS)}
    candidates = {}
    for name, (use_suffix, weights) in variants.items():
        scores = {weight: bits_per_char(base + use_suffix * suffix + weight * lag, dev[1])
                  for weight in weights}
        selected = min(scores, key=scores.get)
        candidates[name] = {"validation_bpc_by_lag_weight": scores, "validation_bpc": scores[selected],
                            "lag_weight": selected, "suffix": bool(use_suffix)}
    winner = min(candidates, key=lambda name: candidates[name]["validation_bpc"])
    print(f"Validation selected {winner} and Kneser–Ney history {chosen_history}.", flush=True)

    base, suffix, lag = program.parts(test[0])
    for name, result in candidates.items():
        result["test_bpc"] = bits_per_char(base + result["suffix"] * suffix + result["lag_weight"] * lag, test[1])
    for h, result in controls.items():
        terms = kn[h].terms(test_keys, test[1])
        result["test_bpc"] = -float(np.log2(kn[h].evaluate(test[1], result["discount"], terms)).mean())

    synthetic = np.random.default_rng(913).integers(V, size=(4096, HISTORY))
    sb, ss, sl = program.parts(synthetic)
    for name in dict.fromkeys((winner, "combined")):
        settings = candidates[name]
        weight, use_suffix = settings["lag_weight"], settings["suffix"]
        start = perf_counter()
        model, gates = compile_program(program, hidden, use_suffix, weight)
        elapsed = perf_counter() - start
        logits = predict(model, test[0])
        errors = []
        for actual, expected in ((logits, base + use_suffix * suffix + weight * lag),
                                 (predict(model, synthetic), sb + use_suffix * ss + weight * sl)):
            actual = torch.from_numpy(actual).double().softmax(-1)
            expected = torch.from_numpy(expected).softmax(-1)
            errors.append(float((actual - expected).abs().max()))
        if max(errors) > 2e-6 or parameter_count(model) > BUDGET:
            raise AssertionError((errors, parameter_count(model)))
        settings["compiled"] = {"optimizer_steps": 0, "active_gates": gates, "compile_seconds": elapsed,
                                "test_bpc": bits_per_char(logits.astype(np.float64), test[1]),
                                "max_probability_error_test": errors[0], "max_probability_error_synthetic": errors[1]}
        if args.checkpoint_dir:
            args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), args.checkpoint_dir / f"compiled_{name}.pt")

    validation_slice = np.linspace(0, len(dev[1]) - 1, 8192, dtype=int)
    selection_dev = tuple(values[validation_slice] for values in dev)
    runs = []
    for seed in args.seeds:
        model, result = train_model(seed, hidden, *train, selection_dev, args.steps)
        for name, split in (("validation", dev), ("test", test)):
            result[f"{name}_bpc"] = bits_per_char(predict(model, split[0]).astype(np.float64), split[1])
        runs.append(result)
        print(f"AdamW seed {seed}: {result['test_bpc']:.6f} BPC", flush=True)
        if args.checkpoint_dir:
            torch.save(model.state_dict(), args.checkpoint_dir / f"adamw_seed_{seed}.pt")

    return {"corpus": {"url": SOURCE, "sha256": SHA256, "alphabet": ALPHABET,
                       "scored_windows": [len(split[1]) for split in splits]},
            "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                        "torch": torch.__version__, "device": "cpu", "threads": args.threads},
            "architecture": {"parameters": parameter_count(Decoder(hidden)), "budget": BUDGET,
                             "history": HISTORY, "width": WIDTH, "mlp_width": hidden,
                             "observed_pairs": len(program.pairs), "chosen_suffixes": len(program.suffixes)},
            "timings": {"counting_and_kn_validation_seconds": count_seconds,
                        "program_fit_seconds_after_counts": program_fit_seconds},
            "selected_candidate": winner, "candidates": candidates, "synthetic_parity_contexts": len(synthetic),
            "selected_kn_history": chosen_history, "kneser_ney": controls,
            "adamw": {"validation_selection_windows": len(validation_slice), "batch_size": 256, "runs": runs}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path("data/r09-tinyshakespeare.txt"))
    parser.add_argument("--output", type=Path, default=Path("runs/r10/metrics.json"))
    parser.add_argument("--checkpoint-dir", type=Path)
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--seeds", type=int, nargs="+", default=[17, 29, 43])
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if args.steps < 0 or args.threads < 1:
        parser.error("steps must be nonnegative and threads positive")
    results = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
