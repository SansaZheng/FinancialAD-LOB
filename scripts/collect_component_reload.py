"""Consolidate disjoint actual-model reload receipts, never fixture results."""
import argparse,hashlib,json
from pathlib import Path

def collect(reports,protocol,output):
 cfg=json.loads(protocol.read_text());expected={(f,s) for f in ['date']+['combined-'+x for x in cfg['stocks']] for s in cfg['seeds']};seen=set();rows=[];sources=[]
 for path in reports:
  report=json.loads(path.read_text())
  if not report['passed'] or not report['no_refitting']:raise ValueError('Unverified reload receipt')
  sources.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  for r in report['rows']:
   key=(r['fold'],r['seed'])
   if key in seen or key not in expected:raise ValueError('Duplicate or unknown fold-seed')
   if not r['passed'] or r['evidence_class']!='stage013_frozen_semisynthetic':raise ValueError('Actual stage013 models required')
   if {m['method'] for m in r['methods']}!=set(cfg['methods']) or len(r['methods'])!=len(cfg['methods']):raise ValueError('Incomplete method set')
   for m in r['methods']:
    if m['threshold_flips'] or m['max_absolute_score_error']>m['tolerance']:raise ValueError('Parity violation')
   seen.add(key);rows.append(r)
 result=dict(passed=bool(rows),complete=seen==expected,fold_seed_runs=len(rows),selected_evaluations=sum(len(r['methods']) for r in rows),missing=sorted(expected-seen),max_absolute_score_error=max((m['max_absolute_score_error'] for r in rows for m in r['methods']),default=None),threshold_flips=sum(m['threshold_flips'] for r in rows for m in r['methods']),sources=sources,rows=rows,no_refitting=True,scope='Aggregate of explicitly supplied disjoint real-model receipts; each underlying reload enforces feature/embedding and artifact hashes. No universal environment guarantee.')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--reports',type=Path,nargs='+',required=True);p.add_argument('--protocol',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=collect(a.reports,a.protocol,a.output);print(json.dumps({k:v for k,v in r.items() if k not in ['rows','sources','missing']},indent=2))
