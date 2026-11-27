"""Frozen stage012 direct supervised suite; all scientific fitting requires CQ."""
import argparse,hashlib,json,os,platform,resource,time,warnings
from pathlib import Path
import joblib
import numpy as np
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.preprocessing import StandardScaler
import torch
from lobbench.direct import base_features,interaction_features,mine,DirectMLP
from lobbench.cascade_run import evaluate


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def splits(data,cfg,regime):
    masks=[np.isin(data['date'],cfg[k]) for k in ('train_dates','validation_dates','test_dates')]
    if regime=='date':yield 'date',*[np.flatnonzero(m) for m in masks]
    elif regime=='combined':
        for i,s in enumerate(cfg['stocks']):
            v=cfg['stocks'][(i+1)%len(cfg['stocks'])]
            mm=[masks[0]&~np.isin(data['stock'],[s,v]),masks[1]&(data['stock']==v),masks[2]&(data['stock']==s)]
            yield 'combined-'+s,*[np.flatnonzero(m) for m in mm]
    else:raise ValueError(regime)


def subset(indices,seed,cap):
    return np.sort(np.random.default_rng(seed).choice(indices,min(len(indices),cap),replace=False))


def predict(model,x,device):
    model.eval();out=[]
    with torch.no_grad():
        for start in range(0,len(x),512):out.append(model(torch.as_tensor(x[start:start+512],device=device)).cpu().numpy())
    return np.concatenate(out)


def fit_mlp(x,y,w,xval,seed,cfg,device,epochs):
    torch.manual_seed(seed);rng=np.random.default_rng(seed)
    model=DirectMLP(x.shape[1]).to(device);opt=torch.optim.AdamW(model.parameters(),**cfg)
    losses=[]
    for _ in range(epochs):
        order=rng.permutation(len(y));total=0.;model.train()
        for start in range(0,len(y),256):
            ix=order[start:start+256];xx=torch.as_tensor(x[ix],device=device)
            yy=torch.as_tensor(y[ix],dtype=torch.float32,device=device);ww=torch.as_tensor(w[ix],dtype=torch.float32,device=device)
            opt.zero_grad();loss=(torch.nn.functional.binary_cross_entropy_with_logits(model(xx),yy,reduction='none')*ww).mean()
            if not torch.isfinite(loss):raise FloatingPointError('Nonfinite training loss')
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5.);opt.step();total+=float(loss.detach())*len(ix)
        losses.append(total/len(y))
    return model,predict(model,xval,device),dict(loss=losses,parameters=sum(p.numel() for p in model.parameters()),input_dimensions=x.shape[1])


def run(dataset,output,regime,fold,seed,protocol,device='cpu',engineering=False):
    if not engineering and not os.environ.get('CQ_JOB_ID'):raise RuntimeError('Scientific fitting requires CQ')
    if engineering and dataset.stat().st_size>10*1024**2:raise ValueError('Engineering fixture too large')
    config=json.loads(protocol.read_text());torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    if device=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
    started=time.monotonic();data=dict(np.load(dataset,allow_pickle=False));n=len(data['y'])
    if set(data['date'])!=set(config['train_dates']+config['validation_dates']+config['test_dates']) or set(data['stock'])!=set(config['stocks']):raise ValueError('Unregistered source groups')
    if len(set(data['id']))!=n:raise ValueError('Duplicate window IDs')
    if not np.isfinite(data['raw']).all():raise ValueError('Nonfinite source')
    candidates=[x for x in splits(data,config,regime) if x[0]==fold]
    if len(candidates)!=1:raise ValueError('Invalid fold')
    _,original_train,va,te=candidates[0];tr=subset(original_train,seed,config['training_cap'])
    if engineering:
        def small(ix):return np.concatenate([ix[data['y'][ix]==v][:12] for v in [0,1]])
        tr,va,te=map(small,(tr,va,te))
    if set(tr)&set(va) or set(tr)&set(te) or set(va)&set(te):raise ValueError('Split overlap')
    if data['end_ns'][tr].max()>=data['start_ns'][va].min() or data['end_ns'][va].max()>=data['start_ns'][te].min():raise ValueError('Nonchronological split')
    for ix in [tr,va,te]:
        if len(set(data['y'][ix]))!=2:raise ValueError('One-class split')
    output.mkdir(parents=True,exist_ok=True);index=np.concatenate([tr,va,te]);nt,nv=len(tr),len(va)
    # Construct features only from observed within-window inputs. No labels/kinds.
    base=base_features(data)[index];extra=interaction_features(data['aligned'][index]);y=data['y'][tr]
    groups=np.char.add(np.char.add(data['stock'][tr],'|'),data['date'][tr])
    mining,folds=mine(extra[:nt],y,groups,seed,engineering)
    np.savez_compressed(output/'mining.npz',ids=data['id'][tr],y=y,groups=groups,**mining)
    (output/'mining-folds.json').write_text(json.dumps(folds,indent=2)+'\n')
    np.savez_compressed(output/'split.npz',train_ids=data['id'][tr],validation_ids=data['id'][va],test_ids=data['id'][te],eligible_train_ids=data['id'][original_train])
    normalized={}
    for use_extra in (False,True):
        x=np.concatenate([base,extra],axis=1) if use_extra else base
        scaler=StandardScaler().fit(x[:nt]);keep=scaler.var_>0
        xx=np.ascontiguousarray(scaler.transform(x)[:,keep],dtype=np.float32)
        normalized[use_extra]=(xx,keep,scaler)
        np.savez_compressed(output/('interaction-normalizer.npz' if use_extra else 'base-normalizer.npz'),mean=scaler.mean_,scale=scaler.scale_,keep=keep)
    result=dict(fold=fold,seed=seed,cq_job=os.environ.get('CQ_JOB_ID'),evidence_class='engineering_only' if engineering else 'stage012_frozen_semisynthetic',
                dataset_sha256=digest(dataset),protocol_sha256=digest(protocol),device=device,
                source_sha256={p:digest(p) for p in ['lobbench/direct.py','lobbench/direct_run.py',str(protocol)]},
                versions=dict(python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,sklearn=sklearn.__version__),
                sizes=dict(eligible_train=len(original_train),train=nt,validation=nv,test=len(te)),methods={})
    for method in config['methods']:
        before=time.monotonic();family='mlp' if 'mlp' in method else ('hgb' if 'hgb' in method else 'logistic')
        x,keep,scaler=normalized[method.startswith('interaction_')];w=mining['hard_weight' if method.endswith('_hard') else 'ordinary_weight']
        if family=='mlp':grid=[dict(lr=lr,weight_decay=wd) for lr in config['mlp_grid']['lr'] for wd in config['mlp_grid']['weight_decay']]
        elif family=='hgb':grid=[dict(max_leaf_nodes=leaves,learning_rate=lr) for leaves in config['hgb_grid']['max_leaf_nodes'] for lr in config['hgb_grid']['learning_rate']]
        else:grid=[dict(C=c) for c in config['logistic_grid']['C']]
        best=None;trials=[]
        for i,cfg in enumerate(grid):
            t=time.monotonic();info={}
            with warnings.catch_warnings(record=True) as observed:
                warnings.simplefilter('always')
                if family=='mlp':model,vscore,info=fit_mlp(x[:nt],y,w,x[nt:nt+nv],seed,cfg,device,1 if engineering else config['mlp_epochs'])
                else:
                    if family=='hgb':model=HistGradientBoostingClassifier(max_iter=3 if engineering else config['hgb_grid']['max_iter'],early_stopping=False,random_state=seed,**cfg)
                    else:model=LogisticRegression(solver='liblinear',max_iter=config['logistic_grid']['max_iter'],random_state=seed,**cfg)
                    model.fit(x[:nt],y,sample_weight=w);vscore=model.predict_proba(x[nt:nt+nv])[:,1]
                warn=[dict(category=z.category.__name__,message=str(z.message)) for z in observed]
            if not np.isfinite(vscore).all():raise ValueError('Nonfinite validation prediction')
            ap=float(average_precision_score(data['y'][va],vscore))
            trials.append(dict(trial=i,configuration=cfg,validation_ap=ap,seconds=time.monotonic()-t,warnings=warn,training=info))
            if best is None or ap>best['ap']:
                if best is not None:del best
                best=dict(ap=ap,model=model,vscore=vscore.copy(),trial=i,configuration=cfg,training=info)
            elif family=='mlp':del model
        model=best['model'];negative=np.sort(best['vscore'][data['y'][va]==0]);threshold=float(negative[min(len(negative)-1,int(np.ceil(.99*len(negative))))])
        if family=='mlp':score=predict(model,x[nt+nv:],device);torch.save(model.cpu().state_dict(),output/(method+'.pt'))
        else:score=model.predict_proba(x[nt+nv:])[:,1];joblib.dump(model,output/(method+'.joblib'),compress=3)
        np.savez_compressed(output/(method+'-predictions.npz'),id=data['id'][te],y=data['y'][te],score=score,
                            stock=data['stock'][te],date=data['date'][te],kind=data['kind'][te],validation_id=data['id'][va],validation_y=data['y'][va],validation_score=best['vscore'])
        result['methods'][method]=dict(metrics=evaluate(data['y'][te],score,threshold),selection=dict(trial=best['trial'],selected=best['configuration'],validation_ap=best['ap'],threshold=threshold,trials=trials),
                                      training=best['training'],input_dimensions=int(keep.sum()),weighting='hard' if method.endswith('_hard') else 'ordinary',seconds=time.monotonic()-before)
        (output/'metrics.partial.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(method=method,seconds=result['methods'][method]['seconds'])),flush=True)
        del model,best
    result.update(seconds=time.monotonic()-started,peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,peak_cuda_bytes=torch.cuda.max_memory_allocated() if device=='cuda' else 0)
    (output/'metrics.json').write_text(json.dumps(result,indent=2)+'\n');(output/'progress.txt').write_text('1/1 complete\n');return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--regime',choices=['date','combined'],required=True);p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/012-preregistered.json'));p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--engineering',action='store_true')
    a=p.parse_args();run(a.dataset,a.output,a.regime,a.fold,a.seed,a.protocol,a.device,a.engineering)
