import torch
from torch import nn

model = nn.Sequential(nn.Linear(2,2), nn.ReLU(), nn.Linear(2,1))
with torch.no_grad():
    model[0].weight.copy_(torch.tensor([[1.,-1.],[-1.,1.]]))
    model[0].bias.zero_()
    model[2].weight.copy_(torch.tensor([[1.,1.]]))
    model[2].bias.zero_()

x = torch.tensor([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
expected = torch.tensor([[0.],[1.],[1.],[0.]])
with torch.no_grad():
    predicted = model(x)
print('inputs:', x.tolist())
print('predicted:', predicted.flatten().tolist())
print('expected:', expected.flatten().tolist())
print('exact:', torch.equal(predicted, expected))
assert torch.equal(predicted, expected)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint')
    args = parser.parse_args()
    if args.checkpoint:
        torch.save(model.state_dict(), args.checkpoint)
