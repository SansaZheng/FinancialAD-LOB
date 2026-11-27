"""Verify complete-day archives and independent replay samples before labels."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import numpy as np
from lobbench.wselob import WSEBook
from lobbench.semisynthetic import build


def prepare(source,output,generator='snapshot',registered_dates=None,seed=None):
    if not os.environ.get('CQ_JOB_ID'):
        raise RuntimeError('Full-day processing requires CQ')
    audit=json.loads((source/'audit.json').read_text())
    expected=5*len(registered_dates) if registered_dates is not None else 15
    if audit['status']!='complete' or len(audit['partitions'])!=expected:
        raise ValueError('Complete registered partition contract not met')
    if len({(p['stock'],p['date']) for p in audit['partitions']})!=expected:
        raise ValueError('Duplicate partitions')
    checks=[]
    for p in audit['partitions']:
        for kind in ('raw','book'):
            path=source/p[kind+'_file']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=p[kind+'_sha256']:
                raise ValueError(f'{path.name} SHA256 mismatch')
        raw=np.load(source/p['raw_file'],allow_pickle=False)['orders']
        books=np.load(source/p['book_file'],allow_pickle=False)
        if len(raw)!=p['source_rows'] or p['source_rows']!=p['retained_rows']:
            raise ValueError('Incomplete source partition')
        if not (raw['time'][books['source_row']]==books['time_ns']).all():
            raise ValueError('Snapshot/source timestamp mismatch')
        check=np.unique(np.linspace(0,len(books['x'])-1,100,dtype=int))
        lookup={int(books['source_row'][k]):k for k in check}
        book=WSEBook();checked=0
        for i,record in enumerate(raw):
            row={k:(v.decode('ascii') if isinstance(v,bytes) else int(v)) for k,v in zip(raw.dtype.names,record)}
            book.apply(row)
            if i not in lookup:continue
            j=lookup[i];ref=book.snapshot();expected=np.zeros((2,5,2))
            for side,key in enumerate(('bid','ask')):
                for level,(price,volume) in enumerate(ref[key]):expected[side,level]=[float(price),volume]
            np.testing.assert_array_equal(books['x'][j],expected)
            assert bool(books['valid'][j])==(ref['complete_depth'] and not ref['crossed_or_locked'])
            checked+=1
        checks.append(dict(stock=p['stock'],date=p['date'],all_daily_rows_replayed=len(raw),independent_snapshots_verified=checked))
        print(json.dumps(checks[-1]),flush=True)
    output.mkdir(exist_ok=True,parents=True)
    (output/'full-day-validation.json').write_text(json.dumps(dict(passed=True,partitions=checks),indent=2)+'\n')
    if generator=='passive':
        from lobbench.passive_overlay import build as make
    else:make=build
    options={}
    if registered_dates is not None:options['registered_dates']=registered_dates
    if seed is not None:options['seed']=seed
    report=make(source,output,**options)
    for p in report['partitions']:
        if p['windows']<100 or p['positive']<2:
            raise ValueError('Insufficient qualified windows/labels; do not train')
    (output/'progress.txt').write_text('1/1 complete\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--generator',choices=['snapshot','passive'],default='snapshot')
    a=p.parse_args();prepare(a.source,a.output,a.generator)
