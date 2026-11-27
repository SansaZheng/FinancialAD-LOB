"""Stage013 matched-cohort factorial and cascade/direct pipeline runner."""
import argparse,hashlib,json,os,platform,resource,time,warnings
from pathlib import Path
import joblib,numpy as np,sklearn,torch
from torch import nn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from sklearn.metrics import average_precision_score
from lobbench.direct import base_features,weights
from lobbench.direct_run import splits,subset,fit_mlp
from lobbench.cascade import Fusion,jfds_autoencoder
from lobbench.cascade_run import train_representation,train_fusion,evaluate
from lobbench.portable import batched_interactions,interactions,block_indices,normalize,array_hash,export_hgb,tree_score,export_dense,dense,export_ae,ae_encode,rbf,ocsvm_score

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def selected_threshold(y,score):
 neg=np.sort(score[y==0]);return float(neg[min(len(neg)-1,int(np.ceil(.99*len(neg))))])

def transform_fit(x,nt,path):
 sc=StandardScaler().fit(x[:nt]);keep=sc.var_>0
 np.savez_compressed(path,mean=sc.mean_,scale=sc.scale_,keep=keep)
 return normalize(x,sc.mean_,sc.scale_,keep)

class SharedBCE(nn.Module):
 def __init__(self,dimensions):
  super().__init__();fusion=Fusion(dimensions);self.layers=nn.Sequential(*list(fusion.encoder.children()),nn.Linear(32,1))
 def forward(self,x):return self.layers(x).squeeze(-1)

def fit_shared(x,y,seed,cfg,epochs,device):
 torch.manual_seed(seed);model=SharedBCE(x.shape[1]).to(device);optimizer=torch.optim.Adam(model.parameters(),**cfg);rng=np.random.default_rng(seed);classes=[np.flatnonzero(y==v) for v in [0,1]];losses=[]
 for epoch in range(epochs):
  model.train();total=0.;steps=max(1,int(np.ceil(len(y)/256)))
  for _ in range(steps):
   ix=np.concatenate([rng.choice(c,128,replace=len(c)<128) for c in classes]);rng.shuffle(ix);xx=torch.as_tensor(x[ix],device=device);yy=torch.as_tensor(y[ix],dtype=torch.float32,device=device)
   optimizer.zero_grad();loss=nn.functional.binary_cross_entropy_with_logits(model(xx),yy)
   if not torch.isfinite(loss):raise FloatingPointError('Nonfinite sharedBCE loss')
   loss.backward();nn.utils.clip_grad_norm_(model.parameters(),5);optimizer.step();total+=float(loss.detach())
  losses.append(total/steps)
 return model,dict(loss=losses,parameters=sum(p.numel() for p in model.parameters()),input_dimensions=x.shape[1],batch='same balanced class schedule as fusion',optimizer='Adam')

def fit_detector(z,y,zval,yval,seed,dest):
 sc=StandardScaler().fit(z[y==0]);normal=(np.asarray(z[y==0],dtype=np.float64)-sc.mean_)/sc.scale_;eligible=np.flatnonzero(y==0)
 take=np.arange(len(normal)) if len(normal)<=5000 else np.random.default_rng(seed).choice(len(normal),5000,replace=False)
 normal=normal[take];trials=[];best=None;kernels={}
 for i,(nu,g) in enumerate((nu,g) for nu in [.01,.05,.1] for g in [.1,1.]):
  started=time.monotonic();gamma=g/z.shape[1]
  if gamma not in kernels:kernels[gamma]=rbf(normal,normal,gamma)
  model=OneClassSVM(nu=nu,kernel='precomputed',cache_size=256).fit(kernels[gamma]);v=dict(mean=sc.mean_,scale=sc.scale_,support=normal[model.support_],dual=model.dual_coef_.ravel(),gamma=np.array(gamma),normal_train_indices=eligible[take],support_train_indices=eligible[take][model.support_])
  score=ocsvm_score(v,zval);ap=float(average_precision_score(yval,score));cfg=dict(nu=nu,gamma_factor=g);trials.append(dict(trial=i,configuration=cfg,validation_ap=ap,seconds=time.monotonic()-started,warnings=[]))
  if best is None or ap>best['ap']:
   best=dict(ap=ap,trial=i,configuration=cfg,values=v,score=score.copy());np.savez_compressed(dest.with_suffix('.npz'),**v);joblib.dump(model,dest.with_suffix('.joblib'),compress=3)
 return best,trials

def run(dataset,output,regime,fold,seed,protocol,device='cpu',engineering=False):
 if not engineering and not os.environ.get('CQ_JOB_ID'):raise RuntimeError('Scientific fitting requires CQ')
 if engineering and dataset.stat().st_size>10*1024**2:raise ValueError('Fixture too large')
 cfg=json.loads(protocol.read_text());started=time.monotonic();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 if device=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
 archive=np.load(dataset,allow_pickle=False);d={k:archive[k] for k in ['raw','manual','aligned','y','stock','date','id','kind','start_ns','end_ns']};dates=sum([cfg[k] for k in ['train_dates','validation_dates','test_dates']],[])
 if set(d['date'])!=set(dates) or set(d['stock'])!=set(cfg['stocks']) or len(set(d['id']))!=len(d['y']):raise ValueError('Source group/identity mismatch')
 choices=[v for v in splits(d,cfg,regime) if v[0]==fold]
 if len(choices)!=1:raise ValueError('Unregistered fold')
 _,eligible,va,te=choices[0];tr=subset(eligible,seed,cfg['training_cap'])
 if engineering:
  def small(ix):return np.concatenate([ix[d['y'][ix]==v][:12] for v in [0,1]])
  tr,va,te=map(small,(tr,va,te))
 if set(tr)&set(va) or set(tr)&set(te) or set(va)&set(te):raise ValueError('Split overlap')
 if d['end_ns'][tr].max()>=d['start_ns'][va].min() or d['end_ns'][va].max()>=d['start_ns'][te].min():raise ValueError('Nonchronological')
 if any(len(set(d['y'][ix]))!=2 for ix in [tr,va,te]):raise ValueError('One-class split')
 output.mkdir(parents=True,exist_ok=True);nt,nv=len(tr),len(va);index=np.concatenate([tr,va,te]);vv=slice(nt,nt+nv);tt=slice(nt+nv,None);y=d['y'][tr];w=weights(y);sub={k:d[k][index] for k in ['raw','manual','aligned']};base=base_features(sub);extra=batched_interactions(sub['aligned'])
 np.savez_compressed(output/'split.npz',train_ids=d['id'][tr],validation_ids=d['id'][va],test_ids=d['id'][te],eligible_train_ids=d['id'][eligible],training_weights=w,training_y=y)
 result=dict(fold=fold,seed=seed,cq_job=os.environ.get('CQ_JOB_ID'),evidence_class='engineering_only' if engineering else 'stage013_frozen_semisynthetic',device=device,inference='canonical_numpy_float64',dataset_sha256=sha(dataset),protocol_sha256=sha(protocol),source_sha256={str(p):sha(p) for p in ['lobbench/component_run.py','lobbench/portable.py','lobbench/direct.py','lobbench/direct_run.py','lobbench/cascade.py','lobbench/cascade_run.py']},versions=dict(python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,sklearn=sklearn.__version__),sizes=dict(eligible_train=len(eligible),train=nt,validation=nv,test=len(te)),feature_hashes=dict(base=array_hash(base),interaction=array_hash(extra)),methods={})
 # All neural normalization is fitted to exactly the common training rows.
 normalized={};shared=None
 epochs=1 if engineering else cfg['mlp_epochs']
 for method in cfg['methods']:
  before=time.monotonic();training={};trials=[];best=None
  if method.startswith('hgb_'):
   inds=block_indices(method[4:]);x=np.concatenate([base,extra[:,inds]],axis=1) if len(inds) else base
   for i,(leaves,lr) in enumerate((k,lr) for k in cfg['hgb_grid']['max_leaf_nodes'] for lr in cfg['hgb_grid']['learning_rate']):
    ts=time.monotonic();params=dict(max_leaf_nodes=leaves,learning_rate=lr)
    with warnings.catch_warnings(record=True) as observed:
     warnings.simplefilter('always');model=HistGradientBoostingClassifier(max_iter=3 if engineering else cfg['hgb_grid']['max_iter'],early_stopping=False,random_state=seed,**params).fit(x[:nt],y,sample_weight=w)
    doc=export_hgb(model,output/'tree-current.json');vscore=tree_score(doc,x[vv]);np.testing.assert_allclose(vscore,model.predict_proba(x[vv])[:,1],atol=6e-13,rtol=0);ap=float(average_precision_score(d['y'][va],vscore));trials.append(dict(trial=i,configuration=params,validation_ap=ap,seconds=time.monotonic()-ts,warnings=[dict(category=z.category.__name__,message=str(z.message)) for z in observed]))
    if best is None or ap>best['ap']:
     best=dict(ap=ap,trial=i,configuration=params,vscore=vscore.copy(),doc=doc);(output/(method+'.json')).write_text(json.dumps(doc,separators=(',',':'))+'\n');joblib.dump(model,output/(method+'.joblib'),compress=3)
   score=tree_score(best['doc'],x[tt]);dimensions=x.shape[1];(output/'tree-current.json').unlink()
  else:
   if method.startswith('mlp_'):
    name=method[4:]
    if name not in normalized:
     x=np.concatenate([base,extra],axis=1) if name=='all' else base
     normalized[name]=transform_fit(x,nt,output/(name+'-normalizer.npz'))
    x=normalized[name]
   else:
    if shared is None:
     ae_start=time.monotonic();sc=StandardScaler().fit(sub['raw'][:nt].reshape(-1,20));raw=((sub['raw'].astype('float64')-sc.mean_)/sc.scale_).astype('float32');np.savez_compressed(output/'raw-normalizer.npz',mean=sc.mean_,scale=sc.scale_)
     _,info=train_representation(raw[:nt],raw[:1],seed,1 if engineering else cfg['epochs_lob'],device,output)
     ae=jfds_autoencoder();ae.load_state_dict(torch.load(output/'lob-ae.pt',map_location='cpu',weights_only=True));state=export_ae(ae,output/'lob-ae.npz');rep=ae_encode(state,raw);del ae,raw
     joined=np.concatenate([rep,sub['manual'][:,:,[0,1,2,3,12]].reshape(len(index),-1),sub['aligned'].reshape(len(index),-1)],axis=1);shared=transform_fit(joined,nt,output/'shared-normalizer.npz');del joined
     result['feature_hashes'].update(ae_embedding=array_hash(rep),shared=array_hash(shared));result['representation']=dict(info,canonical_encoding_seconds=time.monotonic()-ae_start-info['seconds'],total_seconds=time.monotonic()-ae_start);del rep
    x=shared
   dimensions=x.shape[1]
   if method.startswith('cascade'):
    alpha=0. if method=='cascade_no_scl' else cfg['fusion_alpha'];fusion_start=time.monotonic();_,training=train_fusion(x[:nt],y,x[:1],seed,1 if engineering else cfg['epochs_fusion'],device,alpha,output/(method+'.pt'));fusion=Fusion(dimensions);fusion.load_state_dict(torch.load(output/(method+'.pt'),map_location='cpu',weights_only=True));values=export_dense(fusion,output/(method+'-encoder.npz'),encoder=True);z=dense(values,x,embedding=True);del fusion
    result['feature_hashes'][method+'_embedding']=array_hash(z);training['seconds']=time.monotonic()-fusion_start
    chosen,trials=fit_detector(z[:nt],y,z[vv],d['y'][va],seed,output/(method+'-detector'));best=dict(ap=chosen['ap'],trial=chosen['trial'],configuration=chosen['configuration'],vscore=chosen['score']);score=ocsvm_score(chosen['values'],z[tt]);del z
   else:
    for i,(lr,wd) in enumerate((lr,wd) for lr in cfg['mlp_grid']['lr'] for wd in cfg['mlp_grid']['weight_decay']):
     ts=time.monotonic();params=dict(lr=lr,weight_decay=wd)
     if method=='shared_bce':model,info=fit_shared(x[:nt],y,seed,params,epochs,device)
     else:model,_,info=fit_mlp(x[:nt],y,w,x[nt:nt+1],seed,params,device,epochs)
     values=export_dense(model,output/'dense-current.npz');vscore=dense(values,x[vv]);ap=float(average_precision_score(d['y'][va],vscore));trials.append(dict(trial=i,configuration=params,validation_ap=ap,seconds=time.monotonic()-ts,warnings=[],training=info))
     if best is None or ap>best['ap']:
      best=dict(ap=ap,trial=i,configuration=params,vscore=vscore.copy(),values=values);training=info;torch.save(model.cpu().state_dict(),output/(method+'.pt'));np.savez_compressed(output/(method+'.npz'),**values)
     del model
    score=dense(best['values'],x[tt]);(output/'dense-current.npz').unlink()
  if not np.isfinite(score).all() or not np.isfinite(best['vscore']).all():raise ValueError('Nonfinite scores')
  threshold=selected_threshold(d['y'][va],best['vscore']);selection=dict(trial=best['trial'],selected=best['configuration'],validation_ap=best['ap'],threshold=threshold,trials=trials)
  np.savez_compressed(output/(method+'-predictions.npz'),id=d['id'][te],y=d['y'][te],score=score,stock=d['stock'][te],date=d['date'][te],kind=d['kind'][te],validation_id=d['id'][va],validation_y=d['y'][va],validation_score=best['vscore'])
  result['methods'][method]=dict(metrics=evaluate(d['y'][te],score,threshold),selection=selection,training=training,input_dimensions=dimensions,seconds=time.monotonic()-before)
  (output/'metrics.partial.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(fold=fold,seed=seed,method=method,seconds=result['methods'][method]['seconds'])),flush=True)
 result['artifact_sha256']={p.name:sha(p) for p in sorted(output.iterdir()) if p.suffix in ('.pt','.npz','.joblib','.json') and not p.name.startswith('metrics')}
 result.update(seconds=time.monotonic()-started,peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,peak_cuda_bytes=torch.cuda.max_memory_allocated() if device=='cuda' else 0)
 (output/'metrics.json').write_text(json.dumps(result,indent=2)+'\n');(output/'progress.txt').write_text('1/1 complete\n');return result

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['dataset','output','protocol']:p.add_argument('--'+k,type=Path,required=True)
 p.add_argument('--regime',choices=['date','combined'],required=True);p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--engineering',action='store_true');a=p.parse_args();run(a.dataset,a.output,a.regime,a.fold,a.seed,a.protocol,a.device,a.engineering)
