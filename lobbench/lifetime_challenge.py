"""Predeclared test-only marginal-matched benign-wave challenge."""
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np
from lobbench.passive_overlay import merge_visible,level_flows
from lobbench.semisynthetic import inputs


def offsets(bits):
    k=np.arange(5);return np.where(np.asarray(bits,dtype=bool),k,4-k)


def build(primary,test_source,output,protocol,challenge):
    if not os.environ.get('CQ_JOB_ID'):raise RuntimeError('CQ required')
    cfg=json.loads(protocol.read_text());spec=json.loads(challenge.read_text());d=dict(np.load(primary/'benchmark.npz',allow_pickle=False));ix=np.flatnonzero(np.isin(d['date'],cfg['test_dates']));data={k:v[ix].copy() for k,v in d.items()}
    ledger={e['id']:e for e in json.loads((primary/'injection-ledger.json').read_text())}
    audit=json.loads((test_source/'audit.json').read_text());lookup={(p['stock'],p['date']):p for p in audit['partitions']};cache={};keep=np.ones(len(ix),bool);changes=[];censored=[]
    for i in np.flatnonzero(data['kind']=='benign_wave'):
        identifier=str(data['id'][i]);e=ledger[identifier];key=(str(data['stock'][i]),str(data['date'][i]))
        if key not in cache:
            p=lookup[key];path=test_source/p['book_file']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=p['book_sha256']:raise ValueError('Base book hash mismatch')
            cache[key]=dict(np.load(path,allow_pickle=False))
        b=cache[key];row=int(identifier.rsplit('-',1)[1]);start=int(np.searchsorted(b['source_row'],row))
        if b['source_row'][start]!=row:raise ValueError('Source ID missing')
        book=b['x'][start:start+25];ts=b['time_ns'][start:start+25]
        seed=int(hashlib.sha256((identifier+'|'+str(spec['seed'])).encode()).hexdigest()[:16],16);rng=np.random.default_rng(seed)
        off=offsets(rng.integers(2,size=5));stops=e['center']+off;starts=np.asarray(e['placement_steps']);window=book.copy()
        try:
            for t in range(25):window[t]=merge_visible(book[t],e['side'],e['prices'],e['added_volume'],(starts<=t)&(t<stops))
        except ValueError as exc:
            if str(exc)!='marketable_intervention_requires_matching_engine':raise
            keep[i]=False;censored.append(identifier);continue
        raw,manual,_=inputs(window,ts);data['raw'][i]=raw;data['manual'][i]=manual;data['aligned'][i]=level_flows(window,True);data['rank'][i]=level_flows(window,False)
        changes.append(dict(id=identifier,withdrawal_steps=stops.tolist(),offsets=off.tolist(),observational_collision=bool(np.all(np.diff(off)==1) or np.all(np.diff(off)==-1))))
    output.mkdir(parents=True,exist_ok=True);np.savez_compressed(output/'challenge.npz',**{k:v[keep] for k,v in data.items()})
    report=dict(status='complete',primary_sha256=hashlib.sha256((primary/'benchmark.npz').read_bytes()).hexdigest(),dataset_sha256=hashlib.sha256((output/'challenge.npz').read_bytes()).hexdigest(),challenge_protocol_sha256=hashlib.sha256(challenge.read_bytes()).hexdigest(),windows=int(keep.sum()),changed_controls=len(changes),censored_ids=censored,positive_observational_collisions=sum(x['observational_collision'] for x in changes),source_job=os.environ.get('CQ_JOB_ID'),changes=changes,role='Frozen-model test-only robustness, not training or selection')
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');(output/'progress.txt').write_text('1/1 complete\n');print(json.dumps({k:v for k,v in report.items() if k not in ['changes','censored_ids']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primary',type=Path,required=True);p.add_argument('--test-source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/012-preregistered.json'));p.add_argument('--challenge-protocol',type=Path,default=Path('configs/012-robustness.json'));a=p.parse_args();build(a.primary,a.test_source,a.output,a.protocol,a.challenge_protocol)
