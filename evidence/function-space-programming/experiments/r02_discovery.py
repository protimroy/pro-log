"""R02 CPU pilot. Generate a blinded packet, then replay the frozen proposals."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import secrets
import time

import torch
from torch import nn

torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)
AXIS = torch.eye(2)
DESIGN = [[-1,-1], [.5,-1], [1,-1], [-1,.5], [-1,1], [-.5,.25], [.25,-.5], [.75,.75]]


def generate(seed):
    rng = torch.Generator().manual_seed(seed)
    def uniform(shape):
        return torch.rand(shape, generator=rng)
    for task in range(12):
        bias = float(.8 * uniform(()) - .4)
        signs = torch.where(uniform((2,)) < .5, -1., 1.)
        amplitudes = signs * (.6 + uniform((2,)) * .9)
        knots = .9 * uniform((2,)) - .45
        x = torch.cat((torch.tensor(DESIGN), 2 * uniform((24, 2)) - 1))
        inner = 2 * uniform((2048, 2)) - 1
        outer = 4 * uniform((8192, 2)) - 2
        outer = outer[outer.abs().amax(1) > 1][:2048]
        yield task, (bias, amplitudes, knots), x, inner, outer


def design(x, knots):
    return torch.cat((torch.ones((len(x), 1)), (x - knots).relu()), dim=1)


def compile_expression(params):
    bias, amplitudes, knots = params
    network = nn.Sequential(nn.Linear(2, 2), nn.ReLU(), nn.Linear(2, 1))
    with torch.no_grad():
        network[0].weight.copy_(AXIS)
        network[0].bias.copy_(-knots)
        network[2].weight.copy_(amplitudes)
        network[2].bias.fill_(bias)
    return network


def prediction(network, x):
    return network(x).flatten()


def algebraic_fit(y):
    bias = y[0]
    slopes = 2 * (y[[2, 4]] - y[[1, 3]])
    knots = .5 - (y[[1, 3]] - bias) / slopes
    return float(bias), slopes, knots


def symbolic_fit(x, y):
    # Grid proposes hinge locations. Least squares fits the output coefficients.
    grid = torch.linspace(-.5, .5, 21)
    knots = torch.cartesian_prod(grid, grid)
    features = torch.cat((torch.ones((len(knots), len(x), 1)),
                          (x[None] - knots[:, None]).relu()), dim=2)
    coefficients = torch.linalg.pinv(features) @ y
    best = int((features @ coefficients.unsqueeze(-1) - y[None, :, None]).square().mean((1, 2)).argmin())
    return float(coefficients[best, 0]), coefficients[best, 1:], knots[best]


def backprop(x, y, seed):
    torch.manual_seed(seed)
    model = nn.Sequential(nn.Linear(2, 2), nn.ReLU(), nn.Linear(2, 1))
    optimizer = torch.optim.Adam(model.parameters(), lr=.025)
    for _ in range(750):
        optimizer.zero_grad()
        (prediction(model, x) - y).square().mean().backward()
        optimizer.step()
    return model


def emit(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["packet", "score"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    folder = args.directory
    seed_file = folder / "seed.json"
    if args.command == "packet":
        if seed_file.exists():
            parser.error("choose a new packet directory")
        folder.mkdir(parents=True, exist_ok=True)
        seed = secrets.randbits(63)
        emit(seed_file, {"seed": seed})
        packets = []
        for task, (bias, amps, knots), x, _, _ in generate(seed):
            y = design(x, knots) @ torch.cat((torch.tensor([bias]), amps))
            packets.append({"task": task, "rows": [[*p, round(float(v), 5)] for p, v in zip(x.tolist(), y)]})
        emit(folder / "packet.json", packets)
        return

    seed = json.loads(seed_file.read_text())["seed"]
    packet_file = folder / "packet.json"
    proposal_file = folder / "proposals.json"
    packets = json.loads(packet_file.read_text())
    proposals = json.loads(proposal_file.read_text())["candidates"]
    if len(proposals) != 12 or len(packets) != 12 or any(len(row) != 5 for row in proposals):
        parser.error("expected 12 five-parameter proposals")
    scores = []
    for task, true_params, x, inner, outer in generate(seed):
        bias, amps, knots = true_params
        coeff = torch.cat((torch.tensor([bias]), amps))
        expected = [design(t, knots) @ coeff for t in (inner, outer)]
        pb, a, b, u, v = proposals[task]
        direct = (pb, torch.tensor([a, b]), torch.tensor([u, v]))
        probes = torch.cartesian_prod(*[torch.cat((torch.linspace(-2, 2, 65), true_params[2][i:i+1],
                                                 direct[2][i:i+1])) for i in range(2)])
        for count in (8, 32):
            train_x = x[:count]
            labels = packets[task]["rows"][:count]
            assert torch.equal(train_x, torch.tensor([row[:2] for row in labels]))
            y = torch.tensor([row[2] for row in labels])
            scale = max(.01, float(y.std(correction=0)))
            fits = torch.linalg.pinv(design(train_x, direct[2])) @ y
            models = {
                "oracle": compile_expression(true_params),
                "direct": compile_expression(direct),
                "refit": compile_expression((float(fits[0]), fits[1:], direct[2])),
                "symbolic_grid": compile_expression(symbolic_fit(train_x, y)),
                "algebraic": compile_expression(algebraic_fit(y)),
            }
            started = time.perf_counter()
            for start in range(5):
                models[f"mlp_{start}"] = backprop(train_x, y, 1000 + start)
            elapsed = time.perf_counter() - started
            with torch.no_grad():
                metrics = {}
                for arm, network in models.items():
                    metrics[arm] = {
                        "normalized_rmse": [float((prediction(network, t) - target).square().mean().sqrt()) / scale
                                            for t, target in zip((inner, outer), expected)],
                        "parameters": {k: w.tolist() for k, w in network.state_dict().items()},
                    }
                    if arm in ("direct", "oracle", "refit", "symbolic_grid", "algebraic"):
                        bias_out = network[2].bias
                        amps_out = network[2].weight.flatten()
                        knots_out = -network[0].bias
                        if arm == "oracle":
                            bias_out, amps_out, knots_out = true_params
                        if arm == "direct":
                            bias_out, amps_out, knots_out = direct
                        expression = bias_out + (probes - knots_out).relu() @ amps_out
                        error = float((prediction(network, probes) - expression).abs().max())
                        assert error <= 1e-12
                        metrics[arm]["compiler_max_abs_error"] = error
                scores.append({"task": task, "count": count, "arms": metrics, "mlp_seconds": elapsed})
    emit(folder / "results.json", {
        "scores": scores,
        "torch": torch.__version__,
        "symbolic_candidates_per_task_budget": 441,
        "mlp_steps_per_start": 750,
        "inputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (Path(__file__), seed_file, packet_file, proposal_file)},
    })


if __name__ == "__main__":
    main()
