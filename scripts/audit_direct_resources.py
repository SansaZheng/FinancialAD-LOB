"""Summarize saved resource observations without rerunning any experiment."""
import argparse,json
from pathlib import Path

def audit(root,output):
 rows=[];warnings=[];versions=[]
 for p in sorted(root.glob('**/metrics.json')):
  r=json.loads(p.read_text())
  if r.get('evidence_class')!='stage012_frozen_semisynthetic':continue
  rows.append(dict(fold=r['fold'],seed=r['seed'],cq_job=r['cq_job'],seconds=r['seconds'],peak_rss_kib=r['peak_rss_native'],peak_allocated_cuda_bytes=r['peak_cuda_bytes'],sizes=r['sizes'],method_seconds={m:v['seconds'] for m,v in r['methods'].items()}))
  if r['versions'] not in versions:versions.append(r['versions'])
  for m,v in r['methods'].items():
   for t in v['selection']['trials']:
    if t.get('warnings'):warnings.append(dict(fold=r['fold'],seed=r['seed'],method=m,trial=t['trial'],warnings=t['warnings']))
 if not rows:raise ValueError('No saved scientific results')
 if len({(r['fold'],r['seed']) for r in rows})!=len(rows):raise ValueError('Duplicate runs')
 d=dict(fold_seeds=len(rows),rows=rows,versions=versions,warnings=warnings,max_worker_rss_kib=max(x['peak_rss_kib'] for x in rows),max_worker_allocated_cuda_bytes=max(x['peak_allocated_cuda_bytes'] for x in rows),sum_worker_seconds=sum(x['seconds'] for x in rows),scope='Linux ru_maxrss KiB; CUDA tensor allocation excludes context; worker seconds are not provider walltime or GPU quota')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.root,a.output)
