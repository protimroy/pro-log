"""R01 exploratory pilot. Run from repository root with Python 3.12."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics

CENTERS = ((0.0, 0.0), (1.0, 0.0), (0.28, 0.28))
CORE, PROTECTED = 0.10, 0.25
BUDGET = 8


def distance(point, center):
    return max(abs(a - b) for a, b in zip(point, center))


def split(center, seed, count):
    rng = random.Random(seed)
    regions = {"target": [], "boundary": [], "protected": []}
    while min(map(len, regions.values())) < count:
        point = (rng.random(), rng.random())
        radius = distance(point, center)
        region = "target" if radius <= CORE else "protected" if radius >= PROTECTED else "boundary"
        if len(regions[region]) < count:
            regions[region].append(point)
    return regions


def score(center, data, patch):
    dx, dy, radius, amplitude = patch
    patch_center = (center[0] + dx, center[1] + dy)
    target = abs(center[0] - center[1]) < 0.5
    signed_amplitude = amplitude if target else -amplitude
    result = {}
    for region, points in data.items():
        hits = changed = 0
        drifts = []
        for point in points:
            base = abs(point[0] - point[1])
            drift = signed_amplitude * max(0.0, 1 - distance(point, patch_center) / radius)
            prediction = base + drift >= 0.5
            hits += prediction == target
            changed += prediction != (base >= 0.5)
            drifts.append(abs(drift))
        result[region] = {
            "count": len(points),
            "flipped_target_accuracy": hits / len(points),
            "prediction_agreement": 1 - changed / len(points),
            "mean_drift": statistics.fmean(drifts),
            "max_drift": max(drifts),
        }
    return result


def select(center, dev, candidates):
    def rank(candidate):
        result = score(center, dev, candidate)
        return (
            result["target"]["flipped_target_accuracy"],
            result["protected"]["prediction_agreement"],
            -result["protected"]["max_drift"],
            -result["protected"]["mean_drift"],
        )
    return max(candidates, key=rank)


def random_candidates(seed):
    rng = random.Random(seed)
    return [
        (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15),
         rng.uniform(0.08, 0.40), rng.uniform(0.35, 1.5))
        for _ in range(BUDGET)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proposals", type=Path)
    args = parser.parse_args()
    raw = args.proposals.read_bytes()
    proposals = json.loads(raw)["candidates"]
    bounds = ((-0.15, 0.15), (-0.15, 0.15), (0.08, 0.40), (0.35, 1.5))
    if len(proposals) != BUDGET or any(
        len(p) != len(bounds) or not all(lo <= x <= hi for x, (lo, hi) in zip(p, bounds))
        for p in proposals
    ):
        parser.error("expected eight in-grammar candidates")
    results = []
    for i, center in enumerate(CENTERS):
        dev = split(center, 100 + i, 256)
        search = [
            select(center, dev, random_candidates(seed))
            for seed in range(700, 720)
        ]
        selected = {
            "unedited": (0, 0, 0.20, 0),
            "analytic_reference": (0, 0, 0.20, 1.10),
            "structured_search": select(
                center, dev, [(0, 0, radius, amp)
                              for radius in (0.16, 0.20, 0.24, 0.28)
                              for amp in (0.80, 1.20)]
            ),
            "chatgpt": select(center, dev, proposals),
        }
        test = split(center, 200 + i, 4096)
        results.append({
            "center": center,
            "arms": {name: {"patch": patch, "test": score(center, test, patch)}
                     for name, patch in selected.items()},
            "random_search": [{"seed": seed, "patch": patch, "test": score(center, test, patch)}
                              for seed, patch in zip(range(700, 720), search)],
        })
    print(json.dumps({
        "schema": 1,
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "proposal_sha256": hashlib.sha256(raw).hexdigest(),
        "candidate_budget_per_task": BUDGET,
        "tasks": results,
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
