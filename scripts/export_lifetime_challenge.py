"""Export verified frozen-model secondary results separately from primary data."""
import argparse,csv,json
from pathlib import Path
import numpy as np

def export(root,verification,output,ledger):
 a=json.loads(verification.read_text());s=json.loads((root/'report.json').read_text());execution=json.loads((root/'execution-status.json').read_text())
 if not a['passed'] or not a['complete_suite'] or s['status']!='complete' or not execution['success']:raise ValueError('Complete successful independent verification required')
 rows=[];add=[];seen=set()
 for p in sorted(root.glob('*/challenge-run.json')):
  r=json.loads(p.read_text())
  for m,x in r['methods'].items():
   key=(r['fold'],r['seed'],m)
   if key in seen:raise ValueError('Duplicate result')
   seen.add(key)
   common=dict(artifact=str(p),cq_job=root.parent.name,fold=r['fold'],seed=r['seed'],method=m,dataset_sha256=r['challenge_sha256'],protocol_sha256=__import__('hashlib').sha256(Path('configs/012-robustness.json').read_bytes()).hexdigest(),evidence_class='stage012_lifetime_challenge')
   v={k:x[k] for k in ['primary_matched_ap','challenge_ap','primary_benign_fpr','challenge_benign_fpr','max_unchanged_score_error','unchanged_threshold_flips']}
   for label in ['primary','challenge']:v[label+'_macro_ap']=float(np.mean([g[label+'_ap'] for g in x['groups'].values()]))
   rows.append(dict(common,**v,validation_threshold=x['validation_threshold'],model_sha256=x['model_sha256'],device=r['device'],no_refitting=r['no_refitting']))
   for k,value in v.items():add.append(dict(common,metric=k,value=value,aggregation='stock-day mean within fold' if k.endswith('macro_ap') else 'single fold and training seed on common IDs'))
 if len(rows)!=300:raise ValueError('Expected300 paired selected-method evaluations')
 output.parent.mkdir(parents=True,exist_ok=True)
 with output.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 with ledger.open(newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;old=[x for x in r if x['evidence_class']!='stage012_lifetime_challenge']
 with ledger.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(old+add)
 return dict(paired_evaluations=len(rows),new_metric_rows=len(add),previous_rows=len(old))
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['root','verification','output','ledger']:p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();print(json.dumps(export(a.root,a.verification,a.output,a.ledger),indent=2))
