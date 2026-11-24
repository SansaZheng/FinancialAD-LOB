"""Matched-input causal controls; generic Transformer is NOT Lin-Yang reproduction."""
import math
import torch
from torch import nn
from torch.nn import functional as F
from .models import LiquidityDynamics


def observation_gate(x):
    """Discard imputed values whose acquisition/price visibility mask is false."""
    if x.shape[-1] != 10 or not torch.isfinite(x).all():
        raise ValueError("Expected ten finite observation-aware features")
    masks = x[..., 7:10]
    if not torch.all((masks == 0) | (masks == 1)):
        raise ValueError("Observation masks must be binary")
    gated = x.clone()
    gated[..., 3:5] = torch.where(masks[..., 0:1].bool(), x[..., 3:5], 0.)
    gated[..., 5] = torch.where(masks[..., 1].bool(), x[..., 5], 0.)
    gated[..., 6] = torch.where(masks[..., 2].bool(), x[..., 6], 0.)
    return gated


class SequenceControl(nn.Module):
    def __init__(self, method, width, levels=10, channels=10, layers=2, gate=True):
        super().__init__()
        if method not in ("liquidity", "tcn", "transformer"):
            raise ValueError("Unknown sequence method")
        self.method, self.width, self.levels, self.channels, self.gate = method, width, levels, channels, gate
        if method == "liquidity":
            self.network = LiquidityDynamics(channels=channels, width=width)
        else:
            self.input = nn.Linear(levels*channels, width)
            if method == "tcn":
                self.temporal = nn.ModuleList([nn.Conv1d(width, width, 3, dilation=d) for d in (1, 2, 4)])
            else:
                if width % 4:
                    raise ValueError("Transformer width must be divisible by four")
                # Construct layers independently, avoiding cloned identical initialization.
                self.temporal = nn.ModuleList([nn.TransformerEncoderLayer(width, 4, 2*width,
                    dropout=0., batch_first=True, norm_first=True) for _ in range(layers)])
            self.head = nn.Linear(width, 1)

    def forward(self, x):
        if x.ndim != 4 or x.shape[-2:] != (self.levels, self.channels):
            raise ValueError("Sequence dimensions do not match model contract")
        x = observation_gate(x) if self.gate else x
        if self.method == "liquidity":
            return self.network(x)
        h = self.input(x.flatten(-2))
        if self.method == "tcn":
            h = h.transpose(1, 2)
            for layer, dilation in zip(self.temporal, (1, 2, 4)):
                h = h + F.gelu(layer(F.pad(h, (2*dilation, 0))))
            h = h.transpose(1, 2)
        else:
            t = h.shape[1]
            pos = torch.arange(t, device=x.device, dtype=x.dtype)[:, None]
            frequency = torch.exp(torch.arange(0, self.width, 2, device=x.device, dtype=x.dtype)
                                  * (-math.log(10000.)/self.width))
            encoding = torch.zeros(t, self.width, device=x.device, dtype=x.dtype)
            encoding[:, 0::2] = torch.sin(pos*frequency)
            encoding[:, 1::2] = torch.cos(pos*frequency)
            h = h + encoding
            mask = torch.ones(t, t, device=x.device, dtype=torch.bool).triu(1)
            for layer in self.temporal:
                h = layer(h, src_mask=mask)
        return self.head(h).squeeze(-1)


def parameter_count(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def budget_model(method, target, levels=10, channels=10, gate=True):
    """Largest width within a shared parameter ceiling; report actual counts.

    Chosen using architecture alone, never validation or test performance.
    RNG state is restored so width search does not alter final initialization.
    """
    state = torch.random.get_rng_state()
    best = None
    try:
        for width in range(4, 257, 4 if method == "transformer" else 1):
            candidate = SequenceControl(method, width, levels, channels, gate=gate)
            if parameter_count(candidate) > target:
                break
            best = width
    finally:
        torch.random.set_rng_state(state)
    if best is None:
        raise ValueError("Parameter ceiling too small")
    return SequenceControl(method, best, levels, channels, gate=gate)
