"""Submit only the two prepared stage013 batches when free reservations permit.

No method/configuration changes, retries, cancellations, rentals or other work.
"""
import argparse,json,re,subprocess,time
from pathlib import Path

def main(cq):
 manifest=Path('cq/013-primary-jobs.json');state=Path('results/engineering/components-013/remainder-reservations.json')
 while True:
  data=json.loads(manifest.read_text());pending=[b for b in data['batches'] if not b['job_id']]
  if not pending:return
  jobs=json.loads(subprocess.check_output([cq,'--json','jobs','--work','FinancialAD-LOB','--limit','100'],text=True))['jobs']
  for batch in pending:
   spec=json.loads(Path(batch['spec']).read_text());matches=[j for j in jobs if j['name']==spec['name']]
   if matches:
    if len(matches)!=1:raise ValueError('Ambiguous duplicate batch')
    batch['job_id']=matches[0]['id'];manifest.write_text(json.dumps(data,indent=2)+'\n');break
  else:
   result=subprocess.run([cq,'status'],capture_output=True,text=True,check=True)
   line=next(x for x in result.stdout.splitlines() if x.startswith('Kaggle:'))
   available=float(re.search(r'; ([0-9.]+) left of',line).group(1));batch=pending[0];spec=json.loads(Path(batch['spec']).read_text());need=spec['limits']['max_hours']
   state.write_text(json.dumps(dict(free_gpu_hours=available,next_spec=batch['spec'],required_reservation_hours=need,decision='submit' if available>=need else 'wait'),indent=2)+'\n')
   if available>=need:
    if spec['limits']['max_usd']!=0 or spec['placement']['allow_rent']:raise ValueError('Free CQ only')
    out=subprocess.check_output([cq,'submit',batch['spec']],text=True);batch['job_id']=re.search(r'j-\d{4}-[a-z0-9]+',out).group();p=Path(batch['spec']);p.with_name(p.stem+'-submission.txt').write_text(out);manifest.write_text(json.dumps(data,indent=2)+'\n');print(out.strip(),flush=True)
   else:time.sleep(45)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cq',default='cq');a=p.parse_args();main(a.cq)
