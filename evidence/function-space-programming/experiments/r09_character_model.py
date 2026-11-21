"""Fit character predictors, compile a trigram into a fresh decoder, and compare AdamW."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
from time import perf_counter
from urllib.request import urlopen

import torch
from torch import nn
import torch.nn.functional as F


SOURCE = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
SHA256 = "86c4e6aa9db7c042ec79f339dcb96d42b0075e16b8fc2e86bf0ca57e2dc565ed"
ALPHABET = "abcdefghijklmnopqrstuvwxyz \n.,!?;:'-�"
V = len(ALPHABET)
LOG2 = math.log(2)


def load_splits(path, train_limit):
    if not path.exists():
        with urlopen(SOURCE, timeout=30) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != SHA256:
            raise ValueError("Downloaded corpus SHA-256 mismatch")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("Corpus SHA-256 mismatch")
    ids = {char: i for i, char in enumerate(ALPHABET)}
    tokens = torch.tensor([ids.get(char, V - 1) for char in raw.decode().lower()])
    train_end, dev_end = len(tokens) * 8 // 10, len(tokens) * 9 // 10
    return (
        tokens[:train_end][:train_limit],
        tokens[train_end:dev_end],
        tokens[dev_end:],
    )


def count_trigrams(tokens):
    keys = (tokens[:-2] * V + tokens[1:-1]) * V + tokens[2:]
    return keys.bincount(minlength=V**3).reshape(V, V, V).double()


def witten_bell(counts, lower, extra_mass=0):
    total = counts.sum(dim=-1, keepdim=True)
    distinct = (counts > 0).sum(dim=-1, keepdim=True)
    mass = distinct + extra_mass
    result = (counts + mass * lower) / (total + mass).clamp_min(1)
    return torch.where(total > 0, result, lower)


def discount(counts, lower, amount):
    total = counts.sum(dim=-1, keepdim=True)
    kept = (counts - amount).clamp_min(0)
    result = (kept + (total - kept.sum(dim=-1, keepdim=True)) * lower)
    return torch.where(total > 0, result / total.clamp_min(1), lower)


def bpc(log_probs, counts):
    return float(-(log_probs * counts).sum() / counts.sum() / LOG2)


class Decoder(nn.Module):
    """One causal self-attention block and one ReLU MLP, with residual connections."""

    def __init__(self, hidden):
        super().__init__()
        width = 3 * V
        self.tokens = nn.Embedding(V, width)
        self.positions = nn.Parameter(torch.empty(2, width))
        self.qkv = nn.Linear(width, 3 * width, bias=False)
        self.attention_out = nn.Linear(width, width, bias=False)
        self.up = nn.Linear(width, hidden)
        self.down = nn.Linear(hidden, width, bias=False)
        self.readout = nn.Linear(width, V, bias=False)
        self.register_buffer("causal", torch.ones(2, 2, dtype=torch.bool).tril(), persistent=False)
        for param in self.parameters():
            nn.init.normal_(param, std=0.04)

    def forward(self, pairs):
        x = self.tokens(pairs) + self.positions
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        scores = q @ k.transpose(-2, -1) / math.sqrt(x.shape[-1])
        attention = scores.masked_fill(~self.causal, -torch.inf).softmax(dim=-1)
        last = (x + self.attention_out(attention @ v))[:, -1]
        last = last + self.down(self.up(last).relu())
        return self.readout(last)


@torch.no_grad()
def compile_predictor(bigram, trigram, seen):
    model = Decoder(V + len(seen))
    for param in model.parameters():
        param.zero_()
    symbols = torch.arange(V)
    model.tokens.weight[symbols, symbols] = 1
    model.qkv.weight[6 * V + symbols, symbols] = 1
    model.attention_out.weight[V + symbols, symbols] = 1
    model.readout.weight[symbols, 2 * V + symbols] = 1

    # The current one-hot and the causal mean recover the previous one-hot exactly.
    model.up.weight[symbols, symbols] = 1
    previous, current = seen.unbind(dim=-1)
    gates = V + torch.arange(len(seen))
    model.up.weight[gates, V + previous] = 2
    model.up.weight[gates, previous] -= 1
    model.up.weight[gates, current] += 1
    model.up.bias[gates] = -1

    log_bigram = bigram.log().float()
    model.down.weight[2 * V:, :V] = log_bigram.T
    corrections = trigram[previous, current].log().float() - log_bigram[current]
    model.down.weight[2 * V:, V:] = corrections.T
    return model


@torch.no_grad()
def model_log_probs(model, contexts):
    return model(contexts).double().log_softmax(dim=-1).reshape(V, V, V)


def train_decoder(seed, train, dev, contexts, seen, steps, lr):
    torch.manual_seed(seed)
    start = perf_counter()
    model = Decoder(V + len(seen))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    counts = train[seen[:, 0], seen[:, 1]].float()
    weights = counts / counts.sum()
    best_loss = math.inf
    best_state = {}
    history = []
    for step in range(steps + 1):
        if step == 0 or step % 25 == 0 or step == steps:
            loss = bpc(model_log_probs(model, contexts), dev)
            history.append({"step": step, "validation_bpc": loss})
            if loss < best_loss:
                best_loss, best_step = loss, step
                best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        if step == steps:
            break
        optimizer.zero_grad(set_to_none=True)
        loss = -(model(seen).log_softmax(dim=-1) * weights).sum()
        loss.backward()
        optimizer.step()
    model.load_state_dict(best_state)
    return model, {
        "seed": seed,
        "steps_run": steps,
        "selected_step": best_step,
        "fit_seconds": perf_counter() - start,
        "history": history,
    }


def run(args):
    torch.set_num_threads(args.threads)
    tokens = load_splits(args.corpus, args.train_limit)
    start = perf_counter()
    train, dev, test = (count_trigrams(split) for split in tokens)
    count_seconds = perf_counter() - start
    seen = (train.sum(dim=-1) > 0).nonzero()
    contexts = torch.cartesian_prod(torch.arange(V), torch.arange(V))
    start = perf_counter()
    counts2 = train.sum(dim=0)
    counts1 = counts2.sum(dim=0) + 0.5
    unigram = counts1 / counts1.sum()
    bigram = witten_bell(counts2, unigram)
    teacher = witten_bell(train, bigram, (train == 1).sum(dim=-1, keepdim=True))
    teacher_fit_seconds = perf_counter() - start
    candidates = {"bigram_witten_bell": bigram.expand_as(train), "trigram_witten_bell": witten_bell(train, bigram)}
    variants = defaultdict(dict)
    continuation2 = (train > 0).sum(dim=0).double()
    continuation1 = (counts2 > 0).sum(dim=0).double() + 0.5
    continuation1 /= continuation1.sum()
    kn_bigrams = {}
    for amount in (0.1, 0.25, 0.5, 0.75, 0.9):
        variants["absolute_discount"][amount] = discount(train, bigram, amount)
        kn_bigrams[amount] = discount(continuation2, continuation1, amount)
        variants["interpolated_kneser_ney"][amount] = discount(
            train, kn_bigrams[amount], amount
        )
    tuning = {}
    for name, options in variants.items():
        losses = {amount: bpc(probs.log(), dev) for amount, probs in options.items()}
        chosen = min(losses, key=losses.get)
        candidates[name] = options[chosen]
        tuning[name] = {"validation_bpc_by_discount": losses, "selected_discount": chosen}

    def scores(log_probs):
        return {"validation_bpc": bpc(log_probs, dev), "test_bpc": bpc(log_probs, test)}

    def check_compile(lower, target):
        start = perf_counter()
        model = compile_predictor(lower, target, seen)
        elapsed = perf_counter() - start
        predicted = model_log_probs(model, contexts)
        max_error = float((predicted.exp() - target).abs().max())
        if max_error > 2e-6:
            raise RuntimeError(f"Failed exhaustive compiler parity: {max_error:.3g}")
        return model, scores(predicted) | {"optimizer_steps": 0,
                                          "max_probability_error": max_error,
                                          "compile_seconds": elapsed}

    compiled, teacher_compiled_scores = check_compile(bigram, teacher)
    kn_name = "interpolated_kneser_ney"
    kn_discount = tuning[kn_name]["selected_discount"]
    kn_compiled, kn_compiled_scores = check_compile(kn_bigrams[kn_discount], candidates[kn_name])

    gradient_runs = []
    if args.checkpoint_dir:
        args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        torch.save(compiled.state_dict(), args.checkpoint_dir / "compiled_teacher.pt")
        torch.save(kn_compiled.state_dict(), args.checkpoint_dir / "compiled_kneser_ney.pt")
    for seed in args.seeds:
        model, metadata = train_decoder(seed, train, dev, contexts, seen, args.steps, args.lr)
        gradient_runs.append(metadata | scores(model_log_probs(model, contexts)))
        print(f"seed {seed}: test {gradient_runs[-1]['test_bpc']:.6f} BPC", flush=True)
        if args.checkpoint_dir:
            torch.save(model.state_dict(), args.checkpoint_dir / f"adamw_seed_{seed}.pt")

    return {
        "corpus": {"url": SOURCE, "sha256": SHA256, "alphabet": ALPHABET,
                   "split": "80/10/10 contiguous, train truncated after splitting",
                   "split_characters": [len(split) for split in tokens],
                   "scored_characters": [len(split) - 2 for split in tokens]},
        "runtime": {"python": platform.python_version(), "torch": torch.__version__,
                    "device": "cpu", "threads": args.threads},
        "architecture": {"context": 2, "width": 3 * V, "mlp_width": V + len(seen),
                         "parameters": sum(p.numel() for p in compiled.parameters()),
                         "observed_contexts": len(seen), "possible_contexts": V**2},
        "baseline_counts_seconds": count_seconds,
        "teacher_fit_seconds_after_counts": teacher_fit_seconds,
        "teacher_direct": scores(teacher.log()),
        "teacher_compiled": teacher_compiled_scores,
        "kneser_ney_compiled": kn_compiled_scores,
        "baselines": {name: scores(probs.log()) for name, probs in candidates.items()},
        "discount_tuning": tuning,
        "adamw": {"learning_rate": args.lr, "gradient": "full batch, weighted by trigram counts",
                  "runs": gradient_runs},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path("data/r09-tinyshakespeare.txt"))
    parser.add_argument("--output", type=Path, default=Path("runs/r09/metrics.json"))
    parser.add_argument("--checkpoint-dir", type=Path)
    parser.add_argument("--train-limit", type=int, default=100_000)
    parser.add_argument("--steps", type=int, default=600)
    parser.add_argument("--lr", type=float, default=0.005)
    parser.add_argument("--seeds", nargs="+", type=int, default=[17, 29, 43])
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    if args.train_limit < 3 or args.steps < 0 or args.lr <= 0 or args.threads < 1:
        parser.error("require train-limit >= 3, steps >= 0, lr > 0 and threads >= 1")
    report = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
