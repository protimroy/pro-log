"""MNIST function-space experiment: frozen constructed features + closed-form ridge.
Usage: uv run --with torch --with torchvision python mnist_function_space.py
Downloads MNIST on first run (network required). No gradient descent is used.
"""
import argparse
import time
import torch
import torch.nn.functional as F
from torchvision.datasets import MNIST


def features(x, mode='designed'):
    # x: N x 1 x 28 x 28, [0,1]. All transformations fixed before seeing labels.
    if mode == 'pixels':
        return x.flatten(1)
    z = x[:, 0]
    ink = z.sum((1, 2), keepdim=False).unsqueeze(1) / 784
    yy = torch.arange(28, device=x.device, dtype=x.dtype).view(1, 28, 1)
    xx = torch.arange(28, device=x.device, dtype=x.dtype).view(1, 1, 28)
    denom = z.sum((1, 2)).clamp_min(1e-5)
    cy = (z * yy).sum((1, 2)) / denom / 27
    cx = (z * xx).sum((1, 2)) / denom / 27
    dx = (z[:, :, 1:] - z[:, :, :-1]).abs().mean((1, 2))
    dy = (z[:, 1:, :] - z[:, :-1, :]).abs().mean((1, 2))
    symmetry = (z * z.flip(2)).mean((1, 2))
    # Spatial occupancy and gradients (fixed pooling, no fitted kernels).
    pooled = F.adaptive_avg_pool2d(x, (7, 7)).flatten(1)
    edge_h = F.adaptive_avg_pool2d((x[:, :, :, 1:] - x[:, :, :, :-1]).abs(), (7, 7)).flatten(1)
    edge_v = F.adaptive_avg_pool2d((x[:, :, 1:, :] - x[:, :, :-1, :]).abs(), (7, 7)).flatten(1)
    # Fixed directional stroke filters, each pooled to 4x4.
    kernels = torch.tensor([
        [[-1., 0., 1.], [-1., 0., 1.], [-1., 0., 1.]],
        [[-1., -1., -1.], [0., 0., 0.], [1., 1., 1.]],
        [[-1., -1., 0.], [-1., 0., 1.], [0., 1., 1.]],
        [[0., 1., 1.], [-1., 0., 1.], [-1., -1., 0.]],
    ], dtype=x.dtype, device=x.device).unsqueeze(1)
    strokes = F.adaptive_avg_pool2d(F.conv2d(x, kernels, padding=1).abs(), (4, 4)).flatten(1)
    stats = torch.stack([cy, cx, dx, dy, symmetry], 1)
    return torch.cat([ink, stats, pooled, edge_h, edge_v, strokes], 1)


def load_split(root, train):
    ds = MNIST(root=root, train=train, download=True)
    return ds.data.unsqueeze(1).float().div_(255), ds.targets.long()


def solve_and_score(train_x, train_y, test_x, test_y, alpha):
    # Standardize using training data only. Intercept unpenalized.
    mean = train_x.mean(0)
    std = train_x.std(0).clamp_min(1e-4)
    a = ((train_x - mean) / std).double()
    b = ((test_x - mean) / std).double()
    a = torch.cat([a, torch.ones(a.size(0), 1, dtype=a.dtype)], 1)
    b = torch.cat([b, torch.ones(b.size(0), 1, dtype=b.dtype)], 1)
    gram = a.T @ a
    reg = torch.eye(gram.size(0), dtype=gram.dtype) * alpha
    reg[-1, -1] = 0
    rhs = a.T @ F.one_hot(train_y, 10).double()
    w = torch.linalg.solve(gram + reg, rhs)
    pred = (b @ w).argmax(1)
    return int((pred == test_y).sum()), {'mean': mean, 'std': std, 'weights': w}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', default='./data')
    p.add_argument('--train-limit', type=int, default=60000)
    p.add_argument('--test-limit', type=int, default=10000)
    p.add_argument('--alpha', type=float, default=100.0)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--checkpoint')
    args = p.parse_args()
    if not 2 <= args.train_limit <= 60000 or not 1 <= args.test_limit <= 10000:
        p.error('train-limit must be 2–60000 and test-limit 1–10000')
    if not 0 < args.alpha < float('inf'):
        p.error('alpha must be finite and positive')
    checkpoints = {}
    torch.manual_seed(args.seed)
    train, ty = load_split(args.data_dir, True)
    test, vy = load_split(args.data_dir, False)
    train, ty = train[:args.train_limit], ty[:args.train_limit]
    test, vy = test[:args.test_limit], vy[:args.test_limit]
    for name in ['pixels', 'designed']:
        start = time.perf_counter()
        a = torch.cat([features(c, name) for c in train.split(1024)])
        b = torch.cat([features(c, name) for c in test.split(1024)])
        correct, checkpoints[name] = solve_and_score(a, ty, b, vy, args.alpha)
        print(f'{name}: features={a.shape[1]} correct={correct}/{len(vy)} test_accuracy={correct/len(vy):.4%} elapsed={time.perf_counter()-start:.1f}s')
    # Matched-dimensional frozen random ReLU projection, independent of labels.
    dim = features(train[:1], 'designed').shape[1]
    w = torch.randn(784, dim) / (784 ** 0.5)
    a = F.relu(train.flatten(1) @ w)
    b = F.relu(test.flatten(1) @ w)
    correct, checkpoints['random_relu'] = solve_and_score(a, ty, b, vy, args.alpha)
    checkpoints['random_relu']['projection'] = w
    print(f'random_relu: features={dim} correct={correct}/{len(vy)} test_accuracy={correct/len(vy):.4%}')
    if args.checkpoint:
        torch.save(checkpoints, args.checkpoint)

if __name__ == '__main__':
    main()
