"""Independent stage013 split/selection/metric and training-only-statistic audit."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score,roc_auc_score,precision_recall_curve,auc
from lobbench.direct import base_features,weights
from lobbench.direct_run import splits,subset
from lobbench.portable import interactions,ae_encode,normalize,dense

def verify(root,dataset,protocol,output,engineering=False):
 cfg=json.loads(protocol.read_text());dh=hashlib.sha256(dataset.read_bytes()).hexdigest();ph=hashlib.sha256(protocol.read_bytes()).hexdigest();d=dict(np.load(dataset));known={(f,s) for f in ['date']+['combined-'+s for s in cfg['stocks']] for s in cfg['seeds']};seen=set();checks=[]
 for path in sorted(root.glob('**/metrics.json')):
  r=json.loads(path.read_text())
  if r.get('evidence_class')!=('engineering_only' if engineering else 'stage013_frozen_semisynthetic') or 'feature_hashes' not in r:continue
  key=(r['fold'],r['seed'])
  if key not in known or key in seen:raise ValueError('Unknown or duplicate run')
  seen.add(key)
  if r['dataset_sha256']!=dh or r['protocol_sha256']!=ph or set(r['methods'])!=set(cfg['methods']):raise ValueError('Input/protocol/method mismatch')
  for name,h in r['source_sha256'].items():
   if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h:raise ValueError('Code changed: '+name)
  _,eligible,va,te=next(v for v in splits(d,cfg,r['fold'].split('-')[0]) if v[0]==r['fold']);tr=subset(eligible,r['seed'],cfg['training_cap'])
  if engineering:
   def small(ix):return np.concatenate([ix[d['y'][ix]==v][:12] for v in [0,1]])
   tr,va,te=map(small,(tr,va,te))
  split=np.load(path.parent/'split.npz')
  for name,ix in [('train_ids',tr),('validation_ids',va),('test_ids',te),('eligible_train_ids',eligible)]:np.testing.assert_array_equal(split[name],d['id'][ix])
  np.testing.assert_array_equal(split['training_y'],d['y'][tr]);np.testing.assert_allclose(split['training_weights'],weights(d['y'][tr]),rtol=0,atol=1e-12)
  base=base_features({k:d[k][tr] for k in ['raw','manual','aligned']});extra=interactions(d['aligned'][tr]);staterrors=[]
  def checkstats(x,file):
   expected=StandardScaler().fit(x);saved=np.load(path.parent/file);np.testing.assert_allclose(saved['mean'],expected.mean_,rtol=1e-12,atol=1e-12);np.testing.assert_allclose(saved['scale'],expected.scale_,rtol=1e-12,atol=1e-12)
   if 'keep' in saved:np.testing.assert_array_equal(saved['keep'],expected.var_>0)
   staterrors.append(dict(file=file,max_mean_error=float(abs(saved['mean']-expected.mean_).max()),max_scale_error=float(abs(saved['scale']-expected.scale_).max())))
  checkstats(base,'base-normalizer.npz');checkstats(np.concatenate([base,extra],axis=1),'all-normalizer.npz');checkstats(d['raw'][tr].reshape(-1,20),'raw-normalizer.npz')
  norm=np.load(path.parent/'raw-normalizer.npz');raw=((d['raw'][tr].astype('float64')-norm['mean'])/norm['scale']).astype('float32');rep=ae_encode(dict(np.load(path.parent/'lob-ae.npz')),raw);joined=np.concatenate([rep,d['manual'][tr][:,:,[0,1,2,3,12]].reshape(len(tr),-1),d['aligned'][tr].reshape(len(tr),-1)],axis=1);checkstats(joined,'shared-normalizer.npz')
  if len(r['representation']['loss'])!=(1 if engineering else cfg['epochs_lob']):raise ValueError('LOB epoch mismatch')
  for method,item in r['methods'].items():
   p=np.load(path.parent/(method+'-predictions.npz'));selection=item['selection'];trials=selection['trials']
   for name,ix in [('id',te),('validation_id',va),('y',te),('validation_y',va)]:np.testing.assert_array_equal(p[name],d['id' if name in ('id','validation_id') else 'y'][ix])
   for name in ['stock','date','kind']:np.testing.assert_array_equal(p[name],d[name][te])
   if len(trials)!=6:raise ValueError('Trial budget mismatch')
   best=max(trials,key=lambda t:t['validation_ap'])
   if best['trial']!=selection['trial'] or best['configuration']!=selection['selected']:raise ValueError('Not first validation maximum')
   np.testing.assert_allclose(average_precision_score(p['validation_y'],p['validation_score']),selection['validation_ap'],rtol=0,atol=1e-12)
   neg=np.sort(p['validation_score'][p['validation_y']==0]);threshold=float(neg[min(len(neg)-1,int(np.ceil(.99*len(neg))))])
   if selection['threshold']!=threshold:raise ValueError('Threshold changed')
   y,score=p['y'],p['score'];precision,recall,_=precision_recall_curve(y,score);values=dict(ap=average_precision_score(y,score),auroc=roc_auc_score(y,score),pr_auc_trapezoidal=auc(recall,precision),n=len(y),positives=int(y.sum()),prevalence=y.mean(),test_fpr=np.mean(score[y==0]>threshold),recall_at_validation_1pct_fpr=np.mean(score[y==1]>threshold))
   for name,v in values.items():np.testing.assert_allclose(v,item['metrics'][name],rtol=0,atol=1e-10)
   if method.startswith('hgb'):
    if len(json.loads((path.parent/(method+'.json')).read_text())['trees'])!=(3 if engineering else cfg['hgb_grid']['max_iter']):raise ValueError('HGB iteration mismatch')
    grid=[dict(max_leaf_nodes=k,learning_rate=lr) for k in cfg['hgb_grid']['max_leaf_nodes'] for lr in cfg['hgb_grid']['learning_rate']]
   elif method.startswith('cascade'):
    if len(item['training']['loss'])!=(1 if engineering else cfg['epochs_fusion']):raise ValueError('Fusion epoch mismatch')
    expected_alpha=0 if method=='cascade_no_scl' else cfg['fusion_alpha']
    if item['training']['alpha']!=expected_alpha:raise ValueError('Contrastive alpha mismatch')
    grid=[dict(nu=n,gamma_factor=g) for n in cfg['detector_grid']['nu'] for g in cfg['detector_grid']['gamma_factor']]
    detector=np.load(path.parent/(method+'-detector.npz'));ix=detector['normal_train_indices'];np.testing.assert_array_equal(d['y'][tr][ix],0)
    normalix=np.flatnonzero(d['y'][tr]==0)
    take=np.arange(len(normalix)) if len(normalix)<=cfg['normal_detector_cap'] else np.random.default_rng(r['seed']).choice(len(normalix),cfg['normal_detector_cap'],replace=False)
    np.testing.assert_array_equal(ix,normalix[take])
    sharednorm=np.load(path.parent/'shared-normalizer.npz');shared=normalize(joined,sharednorm['mean'],sharednorm['scale'],sharednorm['keep']);z=dense(dict(np.load(path.parent/(method+'-encoder.npz'))),shared,embedding=True);sc=StandardScaler().fit(z[d['y'][tr]==0])
    np.testing.assert_allclose(detector['mean'],sc.mean_,rtol=1e-12,atol=1e-12);np.testing.assert_allclose(detector['scale'],sc.scale_,rtol=1e-12,atol=1e-12)
    if not set(detector['support_train_indices'])<=set(ix):raise ValueError('Support rows outside normal training subset')
    expected_support=(z[detector['support_train_indices']].astype('float64')-sc.mean_)/sc.scale_
    np.testing.assert_allclose(detector['support'],expected_support,rtol=1e-12,atol=1e-12)
   else:
    if any(len(t['training']['loss'])!=(1 if engineering else cfg['mlp_epochs']) for t in trials):raise ValueError('Direct epoch mismatch')
    grid=[dict(lr=lr,weight_decay=wd) for lr in cfg['mlp_grid']['lr'] for wd in cfg['mlp_grid']['weight_decay']]
   if [t['configuration'] for t in trials]!=grid:raise ValueError('Search grid changed')
  checks.append(dict(fold=key[0],seed=key[1],methods=len(r['methods']),normalizers=staterrors,metrics_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 if not checks:raise ValueError('No stage013 results')
 report=dict(passed=True,complete_suite=seen==known,fold_seed_runs=len(seen),selected_evaluations=sum(x['methods'] for x in checks),expected_evaluations=cfg['expected_selected_evaluations'],missing=sorted(known-seen),dataset_sha256=dh,protocol_sha256=ph,checks=checks,scope='Independent split/label/train-only-statistic/selection/grid/budget/metric audit; reload is separately checked; no real intent proof')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','missing']},indent=2));return report
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['root','dataset','protocol','output']:p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();verify(a.root,a.dataset,a.protocol,a.output)
