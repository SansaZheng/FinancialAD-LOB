"""Evaluate frozen models on predeclared matched-lifetime controls; no fitting."""
import argparse,hashlib,json,os,platform,resource,time
from pathlib import Path
import joblib
import numpy as np
import torch
import sklearn
from sklearn.metrics import average_precision_score
from lobbench.direct import base_features,interaction_features,DirectMLP
from lobbench.direct_run import predict


def evaluate(root,challenge,output,protocol,engineering=False):
 started=time.monotonic()
 if not os.environ.get('CQ_JOB_ID') and not engineering:raise RuntimeError('CQ required')
 if engineering and challenge.stat().st_size>10*1024**2:raise ValueError('Engineering budget exceeded')
 cfg=json.loads(protocol.read_text());d=dict(np.load(challenge,allow_pickle=False));torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 output.mkdir(parents=True,exist_ok=True);seen=set();records=[]
 for path in sorted(root.glob('**/metrics.json')):
  r=json.loads(path.read_text())
  if r.get('evidence_class')!=('engineering_only' if engineering else 'stage012_frozen_semisynthetic'):continue
  key=(r['fold'],r['seed'])
  if key in seen:raise ValueError('Duplicate primary fold-seed')
  seen.add(key);mask=np.ones(len(d['y']),bool) if r['fold']=='date' else d['stock']==r['fold'].split('-',1)[1]
  ix=np.flatnonzero(mask);sub={k:d[k][ix] for k in ['raw','manual','aligned']};base=base_features(sub);extra=interaction_features(sub['aligned']);normalized={}
  for enhanced in [False,True]:
   norm=np.load(path.parent/('interaction-normalizer.npz' if enhanced else 'base-normalizer.npz'))
   x=np.concatenate([base,extra],axis=1) if enhanced else base.copy()
   x-=norm['mean'];x/=norm['scale'];normalized[enhanced]=np.ascontiguousarray(x[:,norm['keep']],dtype=np.float32)
  dest=output/(r['fold']+'-s'+str(r['seed']));dest.mkdir(exist_ok=True);methods={}
  for method,item in r['methods'].items():
   x=normalized[method.startswith('interaction_')];model_path=path.parent/(method+('.pt' if 'mlp' in method else '.joblib'))
   if 'mlp' in method:
    model=DirectMLP(x.shape[1]);model.load_state_dict(torch.load(model_path,map_location='cpu',weights_only=True));score=predict(model,x,'cpu')
   else:model=joblib.load(model_path);score=model.predict_proba(x)[:,1]
   p=np.load(path.parent/(method+'-predictions.npz'));lookup={z:k for k,z in enumerate(p['id'])};j=np.array([lookup[z] for z in d['id'][ix]])
   np.testing.assert_array_equal(p['y'][j],d['y'][ix]);primary=p['score'][j];unchanged=d['kind'][ix]!='benign_wave'
   np.testing.assert_allclose(score[unchanged],primary[unchanged],rtol=1e-4,atol=1e-4)
   threshold=item['selection']['threshold'];benign=np.char.startswith(d['kind'][ix],'benign_');groups={}
   for stock,date in sorted(set(zip(d['stock'][ix],d['date'][ix]))):
    m=(d['stock'][ix]==stock)&(d['date'][ix]==date)
    groups[stock+'|'+date]=dict(primary_ap=float(average_precision_score(d['y'][ix][m],primary[m])),challenge_ap=float(average_precision_score(d['y'][ix][m],score[m])))
   np.savez_compressed(dest/(method+'-predictions.npz'),id=d['id'][ix],y=d['y'][ix],score=score,primary_score=primary,stock=d['stock'][ix],date=d['date'][ix],kind=d['kind'][ix])
   methods[method]=dict(primary_matched_ap=float(average_precision_score(d['y'][ix],primary)),challenge_ap=float(average_precision_score(d['y'][ix],score)),primary_benign_fpr=float(np.mean(primary[benign]>threshold)),challenge_benign_fpr=float(np.mean(score[benign]>threshold)),validation_threshold=threshold,groups=groups,unchanged_threshold_flips=int(np.sum((score[unchanged]>threshold)!=(primary[unchanged]>threshold))),max_unchanged_score_error=float(np.abs(score[unchanged]-primary[unchanged]).max()),model_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest())
  record=dict(fold=r['fold'],seed=r['seed'],methods=methods,primary_metrics_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),challenge_sha256=hashlib.sha256(challenge.read_bytes()).hexdigest(),evidence_class='engineering_only' if engineering else 'stage012_lifetime_challenge',device='cpu',no_refitting=True)
  (dest/'challenge-run.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record);print(r['fold'],r['seed'],'complete',flush=True)
 expected={(f,s) for f in ['date']+['combined-'+s for s in cfg['stocks']] for s in cfg['seeds']}
 summary=[]
 for regime in ['date','combined']:
  for method in cfg['methods']:
   rr=[r['methods'][method] for r in records if r['fold'].split('-')[0]==regime]
   if not rr:continue
   summary.append(dict(regime=regime,method=method,fold_seeds=len(rr),primary_macro_ap=float(np.mean([np.mean([g['primary_ap'] for g in r['groups'].values()]) for r in rr])),challenge_macro_ap=float(np.mean([np.mean([g['challenge_ap'] for g in r['groups'].values()]) for r in rr])),primary_benign_fpr=float(np.mean([r['primary_benign_fpr'] for r in rr])),challenge_benign_fpr=float(np.mean([r['challenge_benign_fpr'] for r in rr]))))
 report=dict(status='engineering_only' if engineering else ('complete' if seen==expected else 'partial'),fold_seeds=len(seen),summary=summary,seconds=time.monotonic()-started,peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,versions=dict(python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,sklearn=sklearn.__version__),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Predeclared secondary controls on matched IDs, no re-fitting or threshold calibration; only3test dates and synthetic labels')
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');(output/'progress.txt').write_text(f'{len(seen)}/30 complete\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--challenge',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/012-preregistered.json'));a=p.parse_args();evaluate(a.root,a.challenge,a.output,a.protocol)
