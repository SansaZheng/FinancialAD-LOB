"""Explicit snapshot-overlay benchmark; generated styles, never real intent labels.

No matching engine or endogenous market response is simulated. Manipulation-like
and benign controls share added-volume and side distributions. All book windows
are disjoint, contiguous source events; invalid states and resets break windows.
Only observed prices/volumes/times are inputs, never the injection ledger.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

GENERATOR_VERSION='wse-event-overlay-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlay(book, rng, kind):
    x=book.copy()
    side=int(rng.integers(2)); start=int(rng.integers(2,6)); stop=int(rng.integers(17,22))
    scale=float(rng.uniform(1.0,3.0))
    weights=rng.dirichlet(np.ones(5)*4)
    # Scale from only the prefix available when placing the synthetic orders.
    total=float(np.median(book[:start,:, :,1].sum(axis=2)))*scale
    prices=book[start,side,:,0].copy()
    starts=np.minimum(start+np.arange(5)[::-1],stop-1)
    if kind=='layered':
        stops=np.repeat(stop,5)
    elif kind=='staggered':
        stops=np.minimum(stop+np.arange(5),24)
    elif kind=='persistent':
        stops=np.repeat(25,5)
    elif kind=='independent':
        stops=np.minimum(starts+rng.integers(3,12,size=5),24)
    else:
        raise ValueError(kind)
    for k,p in enumerate(prices):
        for t in range(int(starts[k]),int(stops[k])):
            level=np.flatnonzero(x[t,side,:,0]==p)
            if len(level):
                x[t,side,level[0],1]+=total*weights[k]
    return x,dict(side=side,start=start,stop=stop,scale=scale,prices=prices.tolist(),
                  placement_steps=starts.tolist(),withdrawal_steps=stops.tolist(),added_volume=(total*weights).tolist())


def inputs(x,time_ns,aligned=True):
    """Raw 20-channel LOB, available manual channels, and withdrawal dynamics.

Prices are relative to the initial mid and initial spread (not verified ticks).
Event time deltas are seconds; background D messages are not called cancels.
Trade/cancel manual channels remain unavailable, zero for every example.
    """
    price=x[...,0]; volume=x[...,1]
    mid=(price[0,0,0]+price[0,1,0])/2
    spread=max(price[0,1,0]-price[0,0,0],1e-8)
    raw=np.stack(((price-mid)/spread,np.log1p(volume)),axis=-1).reshape(25,20)
    manual=np.zeros((25,13),dtype=np.float64)
    for side in range(2):
        manual[1:,side]=np.diff(np.log(price[:,side,0]))
        manual[1:,side+2]=np.diff(manual[:,side])
    manual[1:,12]=np.log1p(np.diff(time_ns)/1e9)
    delta=np.zeros((25,2,5)); observed=np.zeros_like(delta)
    denom=np.maximum(volume[0].mean(axis=1),1)
    for t in range(1,25):
        for s in range(2):
            for k in range(5):
                match=np.flatnonzero(price[t-1,s]==price[t,s,k]) if aligned else np.array([k])
                if len(match):
                    delta[t,s,k]=(volume[t,s,k]-volume[t-1,s,match[0]])/denom[s]
                    observed[t,s,k]=1
    added=np.maximum(delta,0); removed=np.maximum(-delta,0)
    # Same-length 25-event sequences summarized without future events after endpoint.
    # Channels: side-wise added/removed sums, simultaneous affected levels,
    # observation coverage and volume imbalance. Retain time to learn ordering.
    dyn=np.concatenate((added.sum(2),removed.sum(2),(added>0).mean(2),
                        (removed>0).mean(2),observed.mean(2),
                        np.log1p(volume.sum(2))),axis=1)
    return raw.astype('float32'),manual.astype('float32'),dyn.astype('float32')


def build(folder,output,stride=64,seed=17086):
    audit=json.loads((folder/'audit.json').read_text())
    if audit['status']!='complete' or audit['snapshot_stride_events']!=1:
        raise ValueError('Requires complete daily event-level acquisition')
    output.mkdir(parents=True,exist_ok=True)
    arrays={k:[] for k in ('raw','manual','aligned','rank','y','stock','date','id','kind','start_ns','end_ns')}
    ledger=[]; stats=[]
    for p in audit['partitions']:
        source=folder/p['book_file']
        if sha(source)!=p['book_sha256']:
            raise ValueError('Book hash mismatch')
        data=np.load(source,allow_pickle=False)
        x,ts,valid,rows=(data[k] for k in ('x','time_ns','valid','source_row'))
        key=f"{p['stock']}-{p['date']}"
        rng=np.random.default_rng(int(hashlib.sha256((key+str(seed)).encode()).hexdigest()[:16],16))
        count=positive=benign=excluded=0
        for start in range(0,len(x)-24,stride):
            sl=slice(start,start+25)
            if not valid[sl].all() or not (np.diff(rows[sl])==1).all() or (np.diff(ts[sl])>60*10**9).any():
                excluded+=1; continue
            u=rng.random()
            kind='background' if u>=.10 else ('layered' if u<.025 else 'staggered' if u<.05 else 'persistent' if u<.075 else 'independent')
            y=int(kind in ('layered','staggered'))
            window=x[sl].copy()
            identifier=f'{key}-{int(rows[start])}'
            if kind!='background':
                window,details=overlay(window,rng,kind)
                ledger.append(dict(id=identifier,style=kind,label=y,**details))
            raw,manual,dyn=inputs(window,ts[sl],True)
            rank=inputs(window,ts[sl],False)[2]
            for k,v in dict(raw=raw,manual=manual,aligned=dyn,rank=rank,y=y,stock=p['stock'],date=p['date'],id=identifier,kind=kind,start_ns=ts[start],end_ns=ts[start+24]).items():
                arrays[k].append(v)
            count+=1; positive+=y; benign+=int(kind in ('persistent','independent'))
        stats.append(dict(stock=p['stock'],date=p['date'],windows=count,positive=positive,benign_controls=benign,excluded_windows=excluded))
    path=output/'benchmark.npz'
    np.savez_compressed(path,**{k:np.asarray(v) for k,v in arrays.items()})
    (output/'injection-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
    report=dict(status='complete',generator=GENERATOR_VERSION,seed=seed,sequence_length=25,stride_events=stride,
                source_audit_sha256=sha(folder/'audit.json'),dataset_sha256=sha(path),partitions=stats,
                evidence_class='semisynthetic_procedural_pattern_detection',
                limitations=['Not real spoofing ground truth','No matching engine or endogenous price response',
                             'Event-time volume overlays, not paper millisecond injection','Background intent is unknown',
                             'Cancel/execution channels unavailable for all samples','Clock-filtered sessions lack halt flags'],
                causal_input_fields=['raw','manual','aligned','rank'],metadata_not_model_inputs=['y','id','kind','stock','date','injection-ledger'])
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();build(args.source,args.output)
