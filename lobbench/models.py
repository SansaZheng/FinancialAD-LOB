"""Candidate only: price-aligned liquidity + causal temporal convolution.

No claim of novel or superior performance. Comparison must include a Transformer
and TCN with the same input channels, parameter budget and supervision.
"""
import torch
from torch import nn
from torch.nn import functional as F


class LiquidityDynamics(nn.Module):
    def __init__(self, channels=8, width=32, dilations=(1, 2, 4)):
        super().__init__()
        self.level = nn.Sequential(nn.Linear(channels, width), nn.GELU(), nn.Linear(width, width))
        self.attention = nn.Linear(width, 1)
        self.temporal = nn.ModuleList([nn.Conv1d(width, width, 3, dilation=d) for d in dilations])
        self.dilations = dilations
        self.head = nn.Linear(width, 1)

    def forward(self, x, level_mask=None):
        # [batch,time,price-level,channel]; predictions only depend on past/present.
        h = self.level(x)
        a = self.attention(h).squeeze(-1)
        if level_mask is not None:
            if not level_mask.any(dim=-1).all():
                raise ValueError("Each timestamp needs an observed level")
            a = a.masked_fill(~level_mask, float("-inf"))
        h = (h * a.softmax(dim=-1).unsqueeze(-1)).sum(dim=-2).transpose(1, 2)
        for conv, d in zip(self.temporal, self.dilations):
            h = h + F.gelu(conv(F.pad(h, (2 * d, 0))))
        return self.head(h.transpose(1, 2)).squeeze(-1)


def paired_loss(logits, paired_logits, labels, weight=0.1):
    """Only label-preserving, causally valid augmentations may form pairs.

    No event IDs, generator parameters or future messages enter the network.
    Controlled invariant pairs are experimental, not an observed-market claim.
    """
    if weight < 0:
        raise ValueError("Negative consistency weight")
    supervised = .5 * (F.binary_cross_entropy_with_logits(logits, labels) +
                       F.binary_cross_entropy_with_logits(paired_logits, labels))
    return supervised + weight * F.mse_loss(logits.sigmoid(), paired_logits.sigmoid())
