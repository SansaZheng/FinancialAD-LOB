"""Paper-described frozen-LOB / contrastive-fusion cascade, WSE adaptation.

Upstream JFDS Transformer implementation is preserved verbatim. Only its training
forward path is adapted here to make device placement portable. 64/128/2 width,
feed-forward width and layers are a registered compact-budget adaptation.
"""
import importlib.util
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F


def jfds_autoencoder():
    path=Path(__file__).resolve().parents[1]/'vendor/jfds_reference/models/models.py'
    spec=importlib.util.spec_from_file_location('jfds_preserved',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    torch.autograd.set_detect_anomaly(False) # avoid upstream process-global debug overhead
    return module.TransformerAutoencoder(20,25,64,128,2)


def encode(model,x):
    return model.encoding(model.embedding(x))


def reconstruct(model,x):
    context=encode(model,x)
    target=model.embedding(torch.cat((torch.zeros_like(x[:,:1]),x[:,:-1]),dim=1))
    mask=nn.Transformer.generate_square_subsequent_mask(x.shape[1],device=x.device)
    return model.linear_output(model.decoder(tgt=target,memory=context[:,None],tgt_mask=mask))


class Fusion(nn.Module):
    def __init__(self,dimensions):
        super().__init__()
        hidden=max(8,(200000-dimensions-32)//(2*dimensions+65))
        self.encoder=nn.Sequential(nn.Linear(dimensions,hidden),nn.ReLU(),nn.Linear(hidden,32))
        self.decoder=nn.Sequential(nn.Linear(32,hidden),nn.ReLU(),nn.Linear(hidden,dimensions))
    def forward(self,x):
        z=self.encoder(x)
        return z,self.decoder(z)


def paper_contrastive(z,y,temperature=.1):
    """Paper Eq. 1: log of positive sum / nonself sum, stable logsumexp.

This differs from the common mean of per-positive log probabilities. Anchors
without another same-class sample contribute zero and are excluded from mean.
    """
    logits=F.normalize(z,dim=1)@F.normalize(z,dim=1).T/temperature
    nonself=~torch.eye(len(y),device=z.device,dtype=torch.bool)
    positive=(y[:,None]==y[None,:]) & nonself
    eligible=positive.any(1)
    if not eligible.any():
        return z.sum()*0
    return (torch.logsumexp(logits.masked_fill(~nonself,float('-inf')),1)[eligible]-
            torch.logsumexp(logits.masked_fill(~positive,float('-inf')),1)[eligible]).mean()
