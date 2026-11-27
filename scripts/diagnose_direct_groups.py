"""Post-fit paired stock-day/seed diagnoses; never used for model selection."""
import argparse,json
from pathlib import Path
import numpy as np

def diagnose(report,output):
 d=json.loads(report.read_text());rows=[]
 for regime in ['date','combined']:
  for a,b in [('interaction_hgb_hard','hgb'),('interaction_hgb_hard','interaction_hgb'),('interaction_mlp_hard','interaction_hgb_hard')]:
   aa={(r['fold'],r['seed']):r for r in d['records'] if r['regime']==regime and r['method']==a};bb={(r['fold'],r['seed']):r for r in d['records'] if r['regime']==regime and r['method']==b}
   assert aa.keys()==bb.keys();diff={}
   for key,r in aa.items():
    assert r['clusters'].keys()==bb[key]['clusters'].keys()
    for group,value in r['clusters'].items():diff.setdefault(group,[]).append(value-bb[key]['clusters'][group])
   means={k:float(np.mean(v)) for k,v in sorted(diff.items())}
   rows.append(dict(regime=regime,method=a,reference=b,seed_averaged_stock_day_deltas=means,positive_groups=sum(v>0 for v in means.values()),total_groups=len(means),min_delta=min(means.values()),max_delta=max(means.values())))
 output.write_text(json.dumps(dict(status=d['status'],comparisons=rows,scope='Descriptive same-ID stock-day comparisons averaged over training seeds; no additional independent dates'),indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();diagnose(a.report,a.output)
