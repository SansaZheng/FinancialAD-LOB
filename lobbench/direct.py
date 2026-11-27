"""Observable interaction features and train-only cross-fitted negative mining."""
import numpy as np
import torch
from torch import nn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold


def interaction_features(aligned):
    """No labels, metadata, fitted quantities or post-window observations."""
    x=np.asarray(aligned,dtype=np.float32).reshape(-1,25,2,5,4)
    # Coverage is shared with the baseline. Unknown flows contribute no mass.
    a=np.log1p(np.maximum(x[...,0],0))*x[...,2]
    r=np.log1p(np.maximum(x[...,1],0))*x[...,3]
    feats=[]
    def unit(v):return v/np.maximum(np.sqrt((v*v).sum(axis=1,keepdims=True)),1e-8)
    aa,rr=unit(a),unit(r)
    for v in (aa,rr):feats.append(np.einsum('ntsl,ntsk->nslk',v,v).reshape(len(x),-1))
    # Addition-to-later-removal co-occurrence at fixed observed level positions.
    # Absolute-price matching is in the input flows, not invented order identity.
    for lag in (0,1,2,4,8,12):
        before=aa[:,:25-lag] if lag else aa
        after=rr[:,lag:] if lag else rr
        feats.append(np.einsum('ntsl,ntsk->nslk',before,after).reshape(len(x),-1))
    t=np.arange(25,dtype=np.float32)[None,:,None,None]/24
    for v in (a,r):
        total=v.sum(axis=1);center=(v*t).sum(axis=1)/np.maximum(total,1e-8)
        width=(v*(t-center[:,None])**2).sum(axis=1)/np.maximum(total,1e-8)
        for z in (np.log1p(total),v.max(axis=1),center,width):feats.append(z.reshape(len(x),-1))
        pooled=v.sum(axis=3);mass=pooled.sum(axis=1)
        for z in (pooled.max(axis=1)/np.maximum(mass,1e-8),((v>0).sum(axis=3)).max(axis=1)/5):feats.append(z)
    out=np.concatenate(feats,axis=1).astype('float32')
    if not np.isfinite(out).all():raise ValueError('Nonfinite interactions')
    return out


def base_features(data):
    n=len(data['raw'])
    return np.concatenate([data['raw'].reshape(n,-1),data['manual'][:,:,[0,1,2,3,12]].reshape(n,-1),data['aligned'].reshape(n,-1)],axis=1).astype('float32')


def weights(y,hard=None):
    y=np.asarray(y);w=np.ones(len(y),dtype=float)
    if hard is not None:w[(y==0)&np.asarray(hard)]=5.
    for c in (0,1):
        mask=y==c
        if not mask.any():raise ValueError('Both training classes required')
        w[mask]*=(len(y)/2)/w[mask].sum()
    return w


def mine(x,y,groups,seed,engineering=False):
    """Cross-fit fixed miner across complete source stock-day groups."""
    if len(set(groups))<3:raise ValueError('At least three independent training groups required')
    score=np.full(len(y),np.nan);assignment=np.full(len(y),-1,dtype=int);folds=[]
    for k,(tr,va) in enumerate(GroupKFold(n_splits=3).split(x,y,groups)):
        if set(groups[tr])&set(groups[va]):raise AssertionError('Mining group leakage')
        model=HistGradientBoostingClassifier(max_iter=3 if engineering else 60,max_leaf_nodes=15,learning_rate=.1,early_stopping=False,random_state=seed)
        model.fit(x[tr],y[tr],sample_weight=weights(y[tr]))
        score[va]=model.predict_proba(x[va])[:,1];assignment[va]=k
        folds.append(dict(fold=k,fit_groups=sorted(set(groups[tr])),score_groups=sorted(set(groups[va]))))
    if not np.isfinite(score).all() or (assignment<0).any():raise AssertionError('Missing OOF scores')
    negative=np.flatnonzero(y==0)
    # Exact top10%; stable index tie break, no random over-emphasis of tied scores.
    order=negative[np.argsort(-score[negative],kind='stable')]
    hard=np.zeros(len(y),dtype=bool);hard[order[:max(1,int(np.ceil(.1*len(negative))))]]=True
    return dict(score=score,fold=assignment,hard=hard,ordinary_weight=weights(y),hard_weight=weights(y,hard)),folds


class DirectMLP(nn.Module):
    def __init__(self,dimensions):
        super().__init__()
        width=max(8,round((200000-129)/(dimensions+65)))
        self.layers=nn.Sequential(nn.Linear(dimensions,width),nn.ReLU(),nn.Linear(width,64),nn.ReLU(),nn.Linear(64,1))
    def forward(self,x):return self.layers(x).squeeze(-1)
