"""Teach a small frozen decoder a new behavior using a compiled activation function."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import torch
from torch import nn

N = 17
LEFT, RIGHT, ADD, NEW = range(N, N + 4)
WIDTH = 48
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.tokens = nn.Embedding(N + 4, WIDTH)
        self.positions = nn.Parameter(torch.randn(3, WIDTH) * .1)
        self.block = nn.TransformerEncoderLayer(WIDTH, 4, 96, dropout=0, batch_first=True, norm_first=True)
        self.head = nn.Linear(WIDTH, N, bias=False)
        self.register_buffer("mask", torch.ones(3, 3, dtype=torch.bool).triu(1))

    def states(self, tokens):
        return self.block(self.tokens(tokens) + self.positions, src_mask=self.mask)

    def residual(self, tokens):
        return self.states(tokens)[:, -1]

    def forward(self, tokens):
        return self.head(self.residual(tokens))


def tokens(pairs, task):
    return torch.cat((pairs, torch.full((len(pairs), 1), task)), 1)


def fit_decoder(model, x, y, steps, seed, lr):
    rng = torch.Generator().manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    for _ in range(steps):
        rows = torch.randint(len(x), (64,), generator=rng)
        opt.zero_grad()
        nn.functional.cross_entropy(model(x[rows]), y[rows]).backward()
        opt.step()
    return model.eval()


def measure(logits, labels):
    return {
        "correct": int((logits.argmax(-1) == labels).sum()),
        "total": len(labels),
        "cross_entropy": float(nn.functional.cross_entropy(logits, labels)),
    }


def digest(model):
    return hashlib.sha256(b"".join(t.detach().contiguous().numpy().tobytes()
                                  for t in model.state_dict().values())).hexdigest()


def operation(name, left, right):
    if name == "subtract":
        return (left - right) % N
    if name == "add":
        return (left + right) % N
    if name == "left":
        return left
    raise ValueError(name)


def probe_features(hidden):
    return torch.cat((hidden, torch.ones((*hidden.shape[:-1], 1))), -1)


def fit_probe(hidden, labels):
    features = probe_features(hidden)
    gram = features.T @ features + .001 * torch.eye(features.shape[1])
    return torch.linalg.solve(gram, features.T @ labels)


def injected_logits(model, x, probes, lift, name, position_local=False):
    states = model.states(x)
    hidden = states[:, -1].clone()
    rows = x[:, -1] == NEW
    if position_local:
        decoded = torch.stack([(probe_features(states[rows, i]) @ probes[i]).argmax(-1)
                               for i in range(2)], 1)
    else:
        decoded = (probe_features(hidden[rows]) @ probes).reshape(-1, 2, N).argmax(-1)
    selected = operation(name, decoded[:, 0], decoded[:, 1])
    target = 8 * nn.functional.one_hot(selected, N).float()
    # Apply the minimum-norm write that sends the existing head to the target logits.
    update = (target - model.head(hidden[rows])) @ lift.T
    hidden[rows] += update
    return model.head(hidden), decoded


def run(seed, proposal):
    torch.manual_seed(seed)
    all_pairs = torch.cartesian_prod(torch.arange(N), torch.arange(N))
    eight = all_pairs[(all_pairs[:, 1] == 0) & (all_pairs[:, 0] >= 1) & (all_pairs[:, 0] <= 8)]
    unused = all_pairs[~(all_pairs[:, None] == eight).all(-1).any(1)]
    unused = unused[torch.randperm(len(unused), generator=torch.Generator().manual_seed(983))]
    train_pairs, test = unused[:177], unused[177:]
    calibrate = train_pairs[:144]
    adaptation = torch.cat((eight, train_pairs[144:168]))
    x_old = torch.cat([tokens(train_pairs, task) for task in (LEFT, RIGHT, ADD)])
    y_old = torch.cat((train_pairs[:, 0], train_pairs[:, 1], train_pairs.sum(1) % N))
    x_protected = torch.cat([tokens(test, task) for task in (LEFT, RIGHT, ADD)])
    y_protected = torch.cat((test[:, 0], test[:, 1], test.sum(1) % N))
    model = fit_decoder(Decoder(), x_old, y_old, 950, seed, .003)
    with torch.no_grad():
        model.tokens.weight[NEW].copy_(model.tokens.weight[ADD])
        before = digest(model)
        h = model.states(tokens(calibrate, ADD))
        y_probe = nn.functional.one_hot(calibrate, N).float()
        probes = fit_probe(h[:, -1], y_probe.flatten(1))
        local_probes = [fit_probe(h[:, i], y_probe[:, i]) for i in range(2)]
        lift = torch.linalg.pinv(model.head.weight)
        actual = operation("subtract", test[:, 0], test[:, 1])
        test_new = tokens(test, NEW)
        mix = torch.cat((test_new, x_protected))
        out, decoded = injected_logits(model, mix, probes, lift, proposal)
        local, local_decoded = injected_logits(model, mix, local_probes, lift, proposal, position_local=True)
        old_logits = model(mix)[len(test):]
        protected_drift = float((out[len(test):] - old_logits).abs().max())
        local_drift = float((local[len(test):] - old_logits).abs().max())
        assert protected_drift == local_drift == 0
        assert digest(model) == before
        arms = {
            "frozen": measure(model(test_new), actual),
            "injected": measure(out[:len(test)], actual),
            "position_local": measure(local[:len(test)], actual),
            "position_local_max_logit_drift": local_drift,
            "position_local_operand_accuracy": float((local_decoded == test).float().mean()),
            "protected": measure(old_logits, y_protected),
            "protected_max_logit_drift": protected_drift,
            "held_out_operand_accuracy": float((decoded == test).float().mean()),
            "output_head_rank": int(torch.linalg.matrix_rank(model.head.weight)),
            "base_parameter_sha256": before,
        }

    for n in (8, 32):
        observed = adaptation[:n]
        a, b = observed.unbind(1)
        labels = operation("subtract", a, b)
        grammar = ("add", "left", "subtract")
        fits = [int((operation(name, a, b) == labels).sum()) for name in grammar]
        selected = grammar[fits.index(max(fits))]
        with torch.no_grad():
            symbolic, _ = injected_logits(model, test_new, local_probes, lift, selected, position_local=True)
        adapted = fit_decoder(copy.deepcopy(model), tokens(observed, NEW), labels, 250, seed + 100, .001)
        with torch.no_grad():
            adapted_old = adapted(x_protected)
            arms[str(n)] = {
                "symbolic_selected": selected,
                "symbolic_candidates_fitting_all": [name for name, count in zip(grammar, fits) if count == n],
                "symbolic": measure(symbolic, actual),
                "fine_tune": measure(adapted(test_new), actual),
                "fine_tune_protected": measure(adapted_old, y_protected),
                "fine_tune_protected_max_logit_drift": float((adapted_old - old_logits).abs().max()),
            }
    return arms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proposal", type=Path)
    args = parser.parse_args()
    proposal = json.loads(args.proposal.read_text())
    print(json.dumps({"torch": torch.__version__, "parameters": sum(p.numel() for p in Decoder().parameters()),
                      "seeds": {i: run(i, proposal["operation"]) for i in (17, 31, 57)}}, indent=2))


if __name__ == "__main__":
    main()
