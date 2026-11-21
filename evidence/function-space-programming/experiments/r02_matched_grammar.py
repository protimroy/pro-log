"""Replay R02 with fixed input directions and trainable hinges."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, median

import torch

from r02_discovery import algebraic_fit, compile_expression, design, generate, prediction


def train(x, y, seed, method):
    generator = torch.Generator().manual_seed(seed)
    bias = torch.zeros(1, requires_grad=True)
    slopes = (torch.rand(2, generator=generator) - .5).requires_grad_()
    knots = (torch.rand(2, generator=generator) - .5).requires_grad_()
    params = [bias, slopes, knots]
    optimizer = torch.optim.Adam(params, lr=.025) if method == "adam" else torch.optim.LBFGS(
        params, max_iter=750, line_search_fn="strong_wolfe",
        tolerance_grad=1e-12, tolerance_change=1e-16,
    )
    evaluations = 0

    def closure():
        nonlocal evaluations
        optimizer.zero_grad()
        error = (design(x, knots) @ torch.cat((bias, slopes)) - y).square().mean()
        error.backward()
        evaluations += 1
        return error

    for _ in range(750 if method == "adam" else 1):
        optimizer.step(closure)
    return (float(bias.detach()[0]), slopes.detach(), knots.detach()), evaluations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r02", type=Path)
    args = parser.parse_args()
    files = {key: args.r02 / f"{key}.json" for key in ("seed", "packet", "proposals")}
    data = {key: json.loads(path.read_text()) for key, path in files.items()}
    result = []
    for task, truth, x, inner, outer in generate(data["seed"]["seed"]):
        oracle = compile_expression(truth)
        outputs = [prediction(oracle, points).detach() for points in (inner, outer)]
        for count in (8, 32):
            rows = torch.tensor(data["packet"][task]["rows"][:count])
            assert torch.equal(rows[:, :2], x[:count])
            y = rows[:, 2]
            scale = max(.01, float(y.std(correction=0)))

            def score(params, evaluations=0):
                network = compile_expression(params)
                with torch.no_grad():
                    errors = [float((prediction(network, points) - expected).square().mean().sqrt()) / scale
                              for points, expected in zip((inner, outer), outputs)]
                return dict(error=errors, evaluations=evaluations,
                            parameters=[params[0], *params[1].tolist(), *params[2].tolist()])

            proposal = data["proposals"]["candidates"][task]
            result.append(dict(task=task, count=count,
                               direct=score((proposal[0], torch.tensor(proposal[1:3]), torch.tensor(proposal[3:]))),
                               algebraic=score(algebraic_fit(y)),
                               **{method: [score(*train(x[:count], y, seed, method))
                                           for seed in range(1000, 1005)]
                                  for method in ("adam", "lbfgs")}))
    summary = {}
    for count in (8, 32):
        rows = [row for row in result if row["count"] == count]
        summary[count] = {
            method: [median(mean(run["error"][i] for run in row[method]) if isinstance(row[method], list)
                            else row[method]["error"][i] for row in rows)
                     for i in (0, 1)]
            for method in ("direct", "algebraic", "adam", "lbfgs")
        }
    print(json.dumps(dict(torch=torch.__version__, summary=summary, tasks=result,
                          inputs={key: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for key, path in files.items()}), separators=(",", ":")))


if __name__ == "__main__":
    main()
