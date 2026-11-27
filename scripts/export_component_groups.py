"""Post-fit per-stock/day policy-label diagnostics, never used for tuning."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score

def export(root,verification,output):
 audit=json.loads(verification.read_text())
 if not audit['passed'] or not audit['complete_suite']:raise ValueError('Complete independent suite audit required')
 rows=[];seen=set()
 for path in sorted(root.glob('**/metrics.json')):
  r=json.loads(path.read_text())
  if r.get('evidence_class')!='stage013_frozen_semisynthetic':continue
  for method,m in r['methods'].items():
   pred=np.load(path.parent/(method+'-predictions.npz'));threshold=m['selection']['threshold'];decision=pred['score']>threshold
   for stock,date in sorted(set(zip(pred['stock'],pred['date']))):
    key=(r['fold'],r['seed'],method,str(stock),str(date))
    if key in seen:raise ValueError('Duplicate group')
    seen.add(key);ix=(pred['stock']==stock)&(pred['date']==date);y=pred['y'][ix];score=pred['score'][ix];kind=pred['kind'][ix];alarm=decision[ix]
    row=dict(fold=r['fold'],seed=r['seed'],method=method,stock=stock,date=date,n=int(ix.sum()),positive=int(y.sum()),ap=float(average_precision_score(y,score)),threshold=threshold,policy_negative_fpr=float(alarm[y==0].mean()),recall=float(alarm[y==1].mean()),artifact=str(path),cq_job=r['cq_job'])
    for name in ['background','benign_burst','benign_wave','layered','staggered']:
     mask=kind==name;row[name+'_n']=int(mask.sum());row[name+'_alarm_rate']=float(alarm[mask].mean()) if mask.any() else None
    rows.append(row)
 if len(rows)!=4200:raise ValueError('Expected 2 regimes x 14 methods x 30 stock-days x 5 seeds')
 output.parent.mkdir(parents=True,exist_ok=True)
 with output.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 note=dict(rows=len(rows),scope='Descriptive post-fit policy-label groups, not new independent market observations or real manipulation intent. Background is assumed-negative under this generator. No model selection from these results.')
 output.with_suffix('.json').write_text(json.dumps(note,indent=2)+'\n');print(note)
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['root','verification','output']:p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();export(a.root,a.verification,a.output)
