"""Independently audit direct-suite splits, mining and saved metric values."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score,roc_auc_score,precision_recall_curve,auc
from sklearn.model_selection import GroupKFold
from lobbench.direct_run import splits,subset
from lobbench.direct import base_features,interaction_features


def verify(root,dataset,protocol,output):
 cfg=json.loads(protocol.read_text());d=dict(np.load(dataset,allow_pickle=False));dh=hashlib.sha256(dataset.read_bytes()).hexdigest();ph=hashlib.sha256(protocol.read_bytes()).hexdigest()
 expected={f:(tr,va,te) for g in cfg['regimes'] for f,tr,va,te in splits(d,cfg,g)};keys={(f,s) for f in expected for s in cfg['seeds']};seen=set();checks=[]
 for p in sorted(root.glob('**/metrics.json')):
  r=json.loads(p.read_text())
  if r.get('evidence_class')!='stage012_frozen_semisynthetic':continue
  key=(r['fold'],r['seed'])
  if key in seen or key not in keys:raise ValueError('Duplicate/unregistered run')
  seen.add(key)
  if r['dataset_sha256']!=dh or r['protocol_sha256']!=ph or set(r['methods'])!=set(cfg['methods']):raise ValueError('Input/protocol/method mismatch')
  for source in ['lobbench/direct.py','lobbench/direct_run.py']:
   if r['source_sha256'][source]!=hashlib.sha256(Path(source).read_bytes()).hexdigest():raise ValueError('Frozen training source mismatch: '+source)
  eligible,va,te=expected[r['fold']];tr=subset(eligible,r['seed'],cfg['training_cap']);saved=np.load(p.parent/'split.npz')
  for name,ix in [('train',tr),('validation',va),('test',te),('eligible_train',eligible)]:np.testing.assert_array_equal(saved[name+'_ids'],d['id'][ix])
  train_data={k:d[k][tr] for k in ['raw','manual','aligned']};base=base_features(train_data);extra=interaction_features(train_data['aligned'])
  normalization_checks=[]
  for enhanced in [False,True]:
   x=np.concatenate([base,extra],axis=1) if enhanced else base
   norm=np.load(p.parent/('interaction-normalizer.npz' if enhanced else 'base-normalizer.npz'))
   mean=x.mean(axis=0,dtype=np.float64);scale=x.std(axis=0,dtype=np.float64);keep=np.ptp(x,axis=0)>0;scale[~keep]=1
   # Stored base features are identical; regenerated float32 interactions can
   # differ across NumPy/platform log/reduction kernels below float32 precision.
   width=base.shape[1]
   for field,actual,rtol in [('mean',mean,1e-10),('scale',scale,1e-8)]:
    np.testing.assert_allclose(norm[field][:width],actual[:width],rtol=rtol,atol=1e-10)
    if enhanced:np.testing.assert_allclose(norm[field][width:],actual[width:],rtol=5*np.finfo(np.float32).eps,atol=1e-10)
   np.testing.assert_array_equal(norm['keep'],keep)
   normalization_checks.append(dict(interaction=enhanced,mean_max_absolute_error=float(np.max(np.abs(norm['mean']-mean))),scale_max_absolute_error=float(np.max(np.abs(norm['scale']-scale)))))
  del base,extra,x,train_data
  m=np.load(p.parent/'mining.npz');np.testing.assert_array_equal(m['ids'],d['id'][tr]);np.testing.assert_array_equal(m['y'],d['y'][tr])
  groups=np.char.add(np.char.add(d['stock'][tr],'|'),d['date'][tr]);np.testing.assert_array_equal(m['groups'],groups)
  folds=json.loads((p.parent/'mining-folds.json').read_text())
  for k,(fit,hold) in enumerate(GroupKFold(n_splits=3).split(tr,d['y'][tr],groups)):
   np.testing.assert_array_equal(m['fold'][hold],k);assert not set(groups[fit])&set(groups[hold])
   assert folds[k]['fit_groups']==sorted(set(groups[fit])) and folds[k]['score_groups']==sorted(set(groups[hold]))
  if not np.isfinite(m['score']).all():raise ValueError('Nonfinite OOF scores')
  y=d['y'][tr];negative=np.flatnonzero(y==0);order=negative[np.argsort(-m['score'][negative],kind='stable')];hard=np.zeros(len(tr),bool);hard[order[:max(1,int(np.ceil(.1*len(negative))))]]=True
  np.testing.assert_array_equal(m['hard'],hard)
  for name in ['ordinary_weight','hard_weight']:
   w=np.where(hard,5.,1.) if name=='hard_weight' else np.ones(len(tr))
   for c in [0,1]:w[y==c]*=(len(tr)/2)/w[y==c].sum()
   np.testing.assert_allclose(m[name],w,rtol=0,atol=1e-12)
  for method,item in r['methods'].items():
   pred=np.load(p.parent/(method+'-predictions.npz'))
   for name,ix in [('id',te),('validation_id',va),('y',te),('validation_y',va)]:np.testing.assert_array_equal(pred[name],d['id' if name in ('id','validation_id') else 'y'][ix])
   for name in ['stock','date','kind']:np.testing.assert_array_equal(pred[name],d[name][te])
   s=item['selection'];trials=s['trials'];best=max(trials,key=lambda x:x['validation_ap'])
   if len(trials)!=6 or best['trial']!=s['trial'] or best['configuration']!=s['selected']:raise ValueError('Selection is not first validation maximum')
   np.testing.assert_allclose(average_precision_score(pred['validation_y'],pred['validation_score']),s['validation_ap'],atol=1e-12,rtol=0)
   nv=np.sort(pred['validation_score'][pred['validation_y']==0]);threshold=float(nv[min(len(nv)-1,int(np.ceil(.99*len(nv))))])
   if threshold!=s['threshold']:raise ValueError('Threshold mismatch')
   y,score=pred['y'],pred['score'];precision,recall,_=precision_recall_curve(y,score)
   values=dict(ap=average_precision_score(y,score),auroc=roc_auc_score(y,score),pr_auc_trapezoidal=auc(recall,precision),n=len(y),positives=y.sum(),prevalence=y.mean(),test_fpr=np.mean(score[y==0]>threshold),recall_at_validation_1pct_fpr=np.mean(score[y==1]>threshold))
   for name,v in values.items():np.testing.assert_allclose(v,item['metrics'][name],atol=1e-10,rtol=0)
   if 'mlp' in method and any(len(t['training']['loss'])!=cfg['mlp_epochs'] for t in trials):raise ValueError('Training budget mismatch')
   if not (p.parent/(method+('.pt' if 'mlp' in method else '.joblib'))).exists():raise ValueError('Selected estimator absent')
  checks.append(dict(fold=r['fold'],seed=r['seed'],methods=len(r['methods']),normalization_checks=normalization_checks,metrics_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 if not checks:raise ValueError('No scientific results found')
 report=dict(passed=True,complete_suite=seen==keys,fold_seed_runs=len(seen),selected_evaluations=sum(x['methods'] for x in checks),missing=sorted(keys-seen),dataset_sha256=dh,protocol_sha256=ph,checks=checks,scope='Artifact consistency, exact train cap and group-disjoint OOF mining, weights, labels/splits/selection/metrics; not real intent or scientific superiority')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','missing']},indent=2));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/012-preregistered.json'));p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.root,a.dataset,a.protocol,a.output)
