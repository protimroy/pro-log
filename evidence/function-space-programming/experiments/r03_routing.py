"""CPU pilot for semantic routing over frozen scalar modules."""
import argparse
import itertools
import json
import random
import re
from pathlib import Path

import torch

torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)
NAMES = ("line", "square", "saturate", "root")
CODES = ("K", "H", "Q", "M")
DOCS = ("linear signed response", "quadratic and sign-invariant",
        "bounded signed saturation", "signed square-root compression")
CUES = ("preserve the sign and grow at a constant rate", "respond equally to either sign and grow faster at larger magnitude",
        "keep the sign and level off at large magnitude", "keep the sign and compress magnitudes with a half-power law")
OPS = ("add", "subtract", "multiply")
GRAPHS = list(itertools.product(range(3), range(4), range(4)))


def frozen_modules():
    grid = torch.linspace(-2, 2, 129)
    targets = torch.stack((grid, grid.square(), grid.tanh(), grid.sign() * grid.abs().sqrt()), 1)
    basis = torch.cat((grid[:, None], ((grid[:, None] - grid[None, 1:-1]).relu() -
                                      (-grid[None, 1:-1]).relu())), 1)
    weights = torch.linalg.lstsq(basis, targets, driver="gelsd").solution
    return grid[1:-1], weights


def library(x, knots, weights):
    basis = torch.cat((x[..., None], (x[..., None] - knots).relu() - (-knots).relu()), -1)
    return basis @ weights


def graph_matrix(x, knots, weights):
    z = library(x, knots, weights)
    columns = []
    for op, first, second in GRAPHS:
        a, b = z[:, 0, first], z[:, 1, second]
        columns.append((a + b, a - b, a * b)[op])
    return torch.stack(columns, 1)


def execute_graph(x, graph, knots, weights, gain):
    op, first, second = graph
    left = library(x[:, 0], knots, weights[:, first])
    right = library(x[:, 1], knots, weights[:, second])
    return (left + right, left - right, left * right)[op] * gain


def task_cards():
    order = GRAPHS.copy()
    random.Random(734).shuffle(order)
    for i, (op, a, b) in enumerate(order):
        shuffle = list(range(4))
        random.Random(9900 + i).shuffle(shuffle)
        yield i, (op, a, b), shuffle


def samples(i, budget):
    rng = torch.Generator().manual_seed(8300+i)
    first = torch.rand((8, 2), generator=rng) * 2 - 1
    first[:, 1] = 0
    extra = torch.rand((24, 2), generator=rng) * 2 - 1
    return torch.cat((first, extra))[:budget]


def cue_vector(op, desc_a, desc_b):
    words = ("linear", "quadratic", "saturation", "square-root", "constant", "equally", "level off", "half-power")
    return torch.tensor([float(op == k) for k in OPS] +
                        [float(w in desc) for desc in (desc_a, desc_b) for w in words])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("packet", "score"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    knots, weights = frozen_modules()
    cards = list(task_cards())
    folder = args.directory
    if args.command == "packet":
        prompts = []
        for i, (op, a, b), shuffle in cards[36:]:
            x = samples(i, 8)
            y = graph_matrix(x, knots, weights)[:, GRAPHS.index((op, a, b))]
            prompts.append(dict(id=i, target_operation=OPS[op], hints=[CUES[a], CUES[b]],
                                library=dict(zip(CODES, DOCS)),
                                shuffled_library=dict(zip(CODES, [DOCS[j] for j in shuffle])),
                                observations=torch.cat((x, y[:, None]), 1).tolist()))
        print(json.dumps(prompts, indent=2))
        return

    # Train slot predictions on development graphs using only the module-card text.
    dev_x, dev_y = [], []
    for _, (op, a, b), _ in cards[:36]:
        dev_x.append(cue_vector(OPS[op], DOCS[a], DOCS[b]))
        dev_y.append(torch.nn.functional.one_hot(torch.tensor([a,b]), 4).flatten().double())
    dev_x = torch.stack(dev_x)
    router = torch.linalg.solve(dev_x.T @ dev_x + .01 * torch.eye(dev_x.shape[1]), dev_x.T @ torch.stack(dev_y))
    proposals = json.loads((folder / "proposals.json").read_text())["proposals"]
    records = []
    for i, truth, shuffle in cards[36:]:
        op, a, b = truth
        target = GRAPHS.index(truth)
        probe = torch.rand((2048, 2), generator=torch.Generator().manual_seed(10000+i)) * 4 - 2
        test = graph_matrix(probe, knots, weights)
        for n in (8, 32):
            train = graph_matrix(samples(i, n), knots, weights)
            y = train[:, target]
            # Every graph uses the same one-coefficient least-squares fitter.
            gain = (train.T @ y) / train.square().sum(0).clamp_min(1e-24)
            residual = (train * gain - y[:, None]).square().mean(0)
            typed = [j for j, graph in enumerate(GRAPHS) if graph[0] == op]
            record = dict(task=i, examples=n, truth=truth, arms={})
            for cond in ("true", "shuffled", "labels"):
                mapping = list(range(4)) if cond == "true" else shuffle
                semantic = (mapping.index(a), mapping.index(b))
                # Canonical phrase retrieval uses the published cue-to-description map.
                # The learned router receives the same canonicalized descriptors.
                learned = (cue_vector(OPS[op], DOCS[semantic[0]], DOCS[semantic[1]]) @ router).reshape(2,4)
                best = float(residual[typed].min())
                ties = [j for j in typed if float(residual[j]) <= best + 1e-12]
                def routed(j):
                    _, left, right = GRAPHS[j]
                    return float(learned[0,left] + learned[1,right])
                proposed = proposals[str(i)][cond]
                nominated = GRAPHS.index((OPS.index(proposed[0]), CODES.index(proposed[1]), CODES.index(proposed[2])))
                arms = {"enumeration": ties[0], "oracle": target}
                if cond != "labels":
                    arms["semantic_lookup"] = max(ties, key=lambda j: sum(k == v for k,v in zip(GRAPHS[j][1:], semantic)))
                    arms["learned_router"] = max(ties, key=routed)
                proposer = "llm" if cond != "labels" else "tie_policy"
                arms[f"{proposer}_frozen"] = nominated
                arms[f"{proposer}_rerank"] = nominated if nominated in ties else ties[0]
                for arm, j in arms.items():
                    predicted = execute_graph(probe, GRAPHS[j], knots, weights, gain[j])
                    parity = float((predicted - test[:, j] * gain[j]).abs().max())
                    assert parity < 1e-10
                    err = (predicted - test[:, target]).square().mean().sqrt()
                    record["arms"][f"{cond}/{arm}"] = dict(graph=GRAPHS[j], exact=j == target,
                                                           rmse=float(err), gain=float(gain[j]), parity=parity,
                                                           equivalent=bool(err < 1e-9), tied=len(ties))
            records.append(record)
    summary = {}
    for n in (8,32):
        subset = [row["arms"] for row in records if row["examples"] == n]
        summary[n] = {k: dict(exact=sum(r[k]["exact"] for r in subset),
                              equivalent=sum(r[k]["equivalent"] for r in subset),
                              mean_rmse=sum(r[k]["rmse"] for r in subset)/len(subset)) for k in subset[0]}
    print(json.dumps(dict(summary=summary, tasks=records, torch=torch.__version__), indent=2))


if __name__ == "__main__":
    main()
