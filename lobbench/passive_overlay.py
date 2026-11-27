"""Persistent passive-order overlays with matched marginal intervention timing.

A conditional counterfactual book view, NOT an exchange/matching simulator.
Base order flow does not react to inserted liquidity. Marketable interventions
are censored for both classes rather than inventing fills or instant cancels.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import numpy as np
from lobbench.semisynthetic import inputs,sha

VERSION='persistent-passive-depth-v2'


def merge_visible(base,side,prices,amounts,active):
    """Top-five(base full book + active insertions) needs only base top-five.

An unseen base level is either worse than all five visible levels (cannot enter
this top-five after additions), or absent. Synthetic quantities persist even
when their price disappears from the base's visible list.
    """
    opposite=base[1-side,0,0]
    live_prices=np.asarray(prices)[active]
    if ((live_prices>=opposite).any() if side==0 else (live_prices<=opposite).any()):
        raise ValueError('marketable_intervention_requires_matching_engine')
    result=base.copy();combined={float(p):float(v) for p,v in base[side]}
    for price,volume,live in zip(prices,amounts,active):
        if live:combined[float(price)]=combined.get(float(price),0)+int(volume)
    selected=sorted(combined,reverse=side==0)[:5]
    result[side]=np.asarray([[p,combined[p]] for p in selected])
    if result[0,0,0]>=result[1,0,0]:raise AssertionError('Overlay created a crossed book')
    return result


def intervention(book,rng,style):
    side=int(rng.integers(2));start=int(rng.integers(1,8))
    starts=start+np.arange(5)[::-1]
    prices=book[start,side,:,0].copy()
    scale=float(rng.uniform(1.,3.));weights=rng.dirichlet(np.ones(5)*4)
    total=float(np.median(book[:start,:,:,1].sum(axis=2)))*scale
    amounts=np.maximum(1,np.rint(total*weights)).astype(np.int64)
    if style in ('layered','benign_burst'):
        center=int(rng.integers(start+7,21))
        # Same per-order marginal lifetime distribution, different dependence.
        noise=np.repeat(rng.integers(-2,3),5) if style=='layered' else rng.integers(-2,3,5)
        stops=center+noise
    elif style in ('staggered','benign_wave'):
        center=int(rng.integers(start+5,20))
        if style=='staggered':
            offset=np.arange(5);offset=offset if rng.integers(2) else offset[::-1]
        else:offset=rng.permutation(5)
        stops=center+offset
    else:raise ValueError(style)
    if not (starts<stops).all() or not (stops<25).all():raise AssertionError('Invalid lifecycle')
    result=book.copy();visible_steps=0;active_steps=0;retained_absent_steps=0
    for t in range(25):
        active=(starts<=t)&(t<stops)
        result[t]=merge_visible(book[t],side,prices,amounts,active)
        for k in np.flatnonzero(active):
            active_steps+=1
            visible=(result[t,side,:,0]==prices[k]).any();visible_steps+=int(visible)
            retained_absent_steps+=int(visible and not (book[t,side,:,0]==prices[k]).any())
    # Random benign policies can realize the same observable coordination.
    collision=(style=='benign_burst' and len(set(map(int,stops)))==1) or (
        style=='benign_wave' and (np.all(np.diff(stops)==1) or np.all(np.diff(stops)==-1)))
    return result,dict(side=side,start=start,center=center,scale=scale,prices=prices.tolist(),added_volume=amounts.tolist(),
                       placement_steps=starts.tolist(),withdrawal_steps=stops.tolist(),active_level_steps=active_steps,
                       visible_level_steps=visible_steps,retained_absent_base_level_steps=retained_absent_steps,
                       benign_policy_observational_collision=bool(collision))


def level_flows(book,aligned=True):
    """Depth-resolved additions/current levels and removals/previous levels.

Absence implies zero only inside the other snapshot's observed price support.
Outside its top-five support the corresponding channel is masked unknown.
Channels per side/level: added, removed, addition-observed, removal-observed.
    """
    output=np.zeros((25,2,5,4),dtype=np.float64)
    scale=np.maximum(book[0,:,:,1].mean(axis=1),1)
    for t in range(1,25):
        for side in range(2):
            previous,current=book[t-1,side],book[t,side]
            for k in range(5):
                price,volume=current[k]
                match=np.flatnonzero(previous[:,0]==price)
                known=bool(len(match)) or (price>=previous[-1,0] if side==0 else price<=previous[-1,0])
                if known:
                    old=(previous[match[0],1] if len(match) else 0) if aligned else previous[k,1]
                    output[t,side,k,0]=max(volume-old,0)/scale[side];output[t,side,k,2]=1
                price,volume=previous[k]
                match=np.flatnonzero(current[:,0]==price)
                known=bool(len(match)) or (price>=current[-1,0] if side==0 else price<=current[-1,0])
                if known:
                    new=(current[match[0],1] if len(match) else 0) if aligned else current[k,1]
                    output[t,side,k,1]=max(volume-new,0)/scale[side];output[t,side,k,3]=1
    return output.reshape(25,40).astype('float32')


def build(folder,output,stride=64,seed=17087,registered_dates=None):
    audit=json.loads((folder/'audit.json').read_text())
    if audit['status']!='complete' or audit['snapshot_stride_events']!=1:raise ValueError('Complete event snapshots required')
    dates=registered_dates or ['2017-01-16','2017-01-17','2017-01-18']
    if sorted(set(p['date'] for p in audit['partitions']))!=sorted(dates):
        raise ValueError('Source dates differ from registered dates')
    output.mkdir(parents=True,exist_ok=True)
    arrays={k:[] for k in ('raw','manual','aligned','rank','y','stock','date','id','kind','start_ns','end_ns')}
    ledger=[];stats=[]
    for p in audit['partitions']:
        path=folder/p['book_file']
        if sha(path)!=p['book_sha256']:raise ValueError('Source hash mismatch')
        data=np.load(path,allow_pickle=False);x,ts,valid,rows=(data[k] for k in ('x','time_ns','valid','source_row'))
        key=p['stock']+'-'+p['date'];rng=np.random.default_rng(int(hashlib.sha256((key+str(seed)).encode()).hexdigest()[:16],16))
        counts=dict(windows=0,positive=0,benign_controls=0,invalid_source_windows=0,marketability_censored=0)
        attempted={k:0 for k in ('layered','staggered','benign_burst','benign_wave')};censored=dict.fromkeys(attempted,0)
        for start in range(0,len(x)-24,stride):
            sl=slice(start,start+25)
            if not valid[sl].all() or not (np.diff(rows[sl])==1).all() or (np.diff(ts[sl])>60*10**9).any():
                counts['invalid_source_windows']+=1;continue
            u=rng.random();kind='background' if u>=.10 else ('layered' if u<.025 else 'staggered' if u<.05 else 'benign_burst' if u<.075 else 'benign_wave')
            window=x[sl].copy();identifier=f'{key}-{int(rows[start])}';y=int(kind in ('layered','staggered'))
            if kind!='background':
                attempted[kind]+=1
                try:window,details=intervention(window,rng,kind)
                except ValueError as error:
                    if str(error)!='marketable_intervention_requires_matching_engine':raise
                    counts['marketability_censored']+=1;censored[kind]+=1;continue
                ledger.append(dict(id=identifier,style=kind,label=y,**details))
            raw,manual,_=inputs(window,ts[sl])
            values=dict(raw=raw,manual=manual,aligned=level_flows(window,True),rank=level_flows(window,False),y=y,
                        stock=p['stock'],date=p['date'],id=identifier,kind=kind,start_ns=ts[start],end_ns=ts[start+24])
            for k,v in values.items():arrays[k].append(v)
            counts['windows']+=1;counts['positive']+=y;counts['benign_controls']+=int(kind.startswith('benign_'))
        stats.append(dict(stock=p['stock'],date=p['date'],attempted_by_style=attempted,censored_by_style=censored,**counts))
    path=output/'benchmark.npz';np.savez_compressed(path,**{k:np.asarray(v) for k,v in arrays.items()})
    (output/'injection-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
    report=dict(status='complete',generator=VERSION,seed=seed,sequence_length=25,stride_events=stride,
                source_audit_sha256=sha(folder/'audit.json'),dataset_sha256=sha(path),partitions=stats,
                generator_code_sha256=sha(Path(__file__)),numpy_version=np.__version__,cq_job=os.environ.get('CQ_JOB_ID'),
                license=audit.get('license'),source_url=audit.get('source'),
                evidence_class='persistent_passive_semisynthetic_risk_patterns',feature_schema='depth-resolved-v2',
                feature_channels=['added_at_current_level','removed_at_previous_level','addition_observed','removal_observed'],
                retained_absent_base_level_steps=sum(e['retained_absent_base_level_steps'] for e in ledger),
                benign_observational_collisions=sum(e['benign_policy_observational_collision'] for e in ledger),
                limitations=['No endogenous response or matching engine','Marketable interventions censored for both classes',
                             'Not real manipulation intent labels','Event-time interventions, not paper millisecond injection',
                             f'Only {len(dates)} registered evaluation dates','Burst per-order lifetimes matched; wave lifetime multiset matched; level/time dependence intentionally differs',
                             'Eight trade/cancel manual fields unavailable; five observed fields used'],
                metadata_not_predictors=['id','y','stock','date','kind','injection-ledger'])
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.source,a.output)
