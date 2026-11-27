"""Post-fit mining composition audit; generator-kind metadata never trains models."""
import argparse,json
from pathlib import Path
import numpy as np

def audit(root,dataset,output):
 data=np.load(dataset,allow_pickle=False);kind_by_id=dict(zip(data['id'],data['kind']));rows=[]
 for p in sorted(root.glob('**/mining.npz')):
  metrics=p.parent/'metrics.json'
  if not metrics.exists():continue
  r=json.loads(metrics.read_text())
  if r.get('evidence_class')!='stage012_frozen_semisynthetic':continue
  m=np.load(p);normal=m['y']==0;hard=m['hard'];kind=np.array([kind_by_id[i] for i in m['ids']]);benign=np.char.startswith(kind,'benign_')
  rows.append(dict(fold=r['fold'],seed=r['seed'],training_normals=int(normal.sum()),hard_normals=int(hard.sum()),normal_benign_fraction=float(benign[normal].mean()),hard_benign_fraction=float(benign[hard].mean()),benign_capture_fraction=float(hard[normal&benign].mean()) if (normal&benign).any() else None,hard_source_groups={str(g):int((hard&(m['groups']==g)).sum()) for g in sorted(set(m['groups']))}))
 report=dict(rows=rows,evidence='Post-fit composition only; metadata excluded from training, OOF scoring, weighting and hyperparameter selection')
 output.parent.mkdir(exist_ok=True,parents=True);output.write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.root,a.dataset,a.output)
