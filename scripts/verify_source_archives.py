"""Read-only SHA256 and row/index/coverage checks for acquired daily shards."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np

def verify(root,protocol,output):
 cfg=json.loads(protocol.read_text());dates=sum([cfg[k] for k in ['train_dates','validation_dates','test_dates']],[]);expected={(s,d) for s in cfg['stocks'] for d in dates};seen=set();rows=[]
 for p in sorted(root.glob('*/full-sessions/audit.json')):
  a=json.loads(p.read_text())
  if a['status']!='complete':raise ValueError('Incomplete source job')
  for item in a['partitions']:
   key=(item['stock'],item['date'])
   if key not in expected or key in seen:raise ValueError('Unexpected/duplicate source day')
   seen.add(key)
   for kind in ['raw','book']:
    f=p.parent/item[kind+'_file']
    if f.stat().st_size!=item[kind+'_bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=item[kind+'_sha256']:raise ValueError('Source file identity mismatch: '+str(f))
   raw=np.load(p.parent/item['raw_file'],allow_pickle=False)['orders'];book=np.load(p.parent/item['book_file'],allow_pickle=False)
   if len(raw)!=item['source_rows'] or len(raw)!=item['retained_rows'] or len(book['x'])!=item['session_snapshots']:raise ValueError('Source coverage mismatch')
   if (np.diff(raw['time'])<0).any() or (np.diff(book['source_row'])<=0).any():raise ValueError('Source ordering mismatch')
   np.testing.assert_array_equal(raw['time'][book['source_row']],book['time_ns'])
   if int(book['valid'].sum())!=item['valid_snapshots']:raise ValueError('Validity count mismatch')
   rows.append(dict(stock=key[0],date=key[1],source_rows=len(raw),snapshots=len(book['x']),raw_sha256=item['raw_sha256'],book_sha256=item['book_sha256'],source_job=a['cq_job'],source_audit_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 if not rows:raise ValueError('No acquired source shards')
 report=dict(passed=True,complete=seen==expected,stock_days=len(rows),expected_stock_days=len(expected),dates=sorted({x['date'] for x in rows}),source_rows=sum(x['source_rows'] for x in rows),rows=rows,missing=sorted(expected-seen),scope='SHA256/full declared row count/causal index checks; independent full-book replay is a separate benchmark prerequisite')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['rows','missing']},indent=2));return report
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['root','protocol','output']:p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();verify(a.root,a.protocol,a.output)
