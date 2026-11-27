"""Record only this project's primary job allocation and measured worker cost."""
import argparse,json,re,subprocess
from pathlib import Path

def audit(manifest,root,output,cq):
 mapping=json.loads(manifest.read_text());jobs=[mapping['pilot']]+[b['job_id'] for b in mapping['batches']]
 if any(j is None for j in jobs) or len(set(jobs))!=7:raise ValueError('Seven unique primary allocations required')
 records=[];workers=[]
 for job in jobs:
  r=json.loads(subprocess.check_output([cq,'--json','show',job],text=True))
  if r['work']!='FinancialAD-LOB':raise ValueError('Foreign project')
  metered=re.search(r'Kaggle, ([0-9.]+) h',r.get('reason') or '')
  records.append(dict(job=job,state=r['state'],host=r.get('host'),requested_resources=r['spec']['resources'],limits=r['spec']['limits'],max_usd=r['spec']['limits']['max_usd'],allow_rent=r['spec']['placement']['allow_rent'],allocation_wall_seconds=(r['finished']-r['started']) if r.get('finished') and r.get('started') else None,cq_reported_hours_rounded=float(metered.group(1)) if metered else None))
  for p in (root/job/'batch').glob('*/metrics.json'):
   m=json.loads(p.read_text());workers.append(dict(job=job,fold=m['fold'],seed=m['seed'],seconds=m['seconds'],peak_rss_kib=m['peak_rss_native'],peak_cuda_allocated_bytes=m['peak_cuda_bytes'],versions=m['versions'],shared_ae_seconds=m['representation']['total_seconds']))
 result=dict(complete=all(r['state']=='done' for r in records) and len(workers)==30,jobs=records,workers=workers,worker_seconds_sum=sum(x['seconds'] for x in workers),worker_peak_rss_kib_max=max((x['peak_rss_kib'] for x in workers),default=None),cq_reported_hours_rounded_sum=sum(x['cq_reported_hours_rounded'] or 0 for x in records),scope='Primary allocations only; worker time sums each run once. Requested CPU/RAM are not proof of physical provider hardware. Exact CPU model was not recorded for each worker. Peak CUDA is allocator memory, not entire-device utilization. Rounded provider hours are approximate; acquisition/qualification/reload are separately listed in CQ specs.')
 if any(r['max_usd']!=0 or r['allow_rent'] for r in records):raise ValueError('Unexpected paid resource authorization')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');print(result['complete'],len(workers),result['cq_reported_hours_rounded_sum'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,default=Path('cq/013-primary-jobs.json'));p.add_argument('--root',type=Path,default=Path('results/cq-013'));p.add_argument('--output',type=Path,required=True);p.add_argument('--cq',default='cq');a=p.parse_args();audit(a.manifest,a.root,a.output,a.cq)
