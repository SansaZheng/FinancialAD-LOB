"""CQ experiment runner: fixed splits, matched supervision, validation-only choice."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import resource
import sys
import sklearn
import time
import numpy as np
import torch
from sklearn.ensemble import IsolationForest,HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,roc_auc_score,precision_recall_curve,auc
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from lobbench.cascade import jfds_autoencoder,encode,reconstruct,Fusion,paper_contrastive

METHODS=('raw_ocsvm','dynamics_ocsvm','cascade_ocsvm','cascade_if','price_cascade_ocsvm','rank_cascade_ocsvm','price_no_scl','price_no_lob','supervised_logistic','supervised_hgb')


def splits(data,regime):
    dates=sorted(set(data['date']));stocks=sorted(set(data['stock']))
    if len(dates)!=3 or len(stocks)!=5:
        raise ValueError('Registered stage010 expects exactly three dates and five stocks')
    if regime in ('date','style'):
        masks=[data['date']==d for d in dates]
        if regime=='style':
            masks=[m & (data['kind']!=('staggered' if i<2 else 'layered')) for i,m in enumerate(masks)]
        yield regime,*[np.flatnonzero(m) for m in masks]
    else:
        for i,stock in enumerate(stocks):
            valstock=stocks[(i+1)%len(stocks)]
            masks=[~np.isin(data['stock'],[stock,valstock]),data['stock']==valstock,data['stock']==stock]
            if regime=='combined':
                masks=[m & (data['date']==d) for m,d in zip(masks,dates)]
            yield regime+'-'+stock,*[np.flatnonzero(m) for m in masks]


def standardize(train,others):
    scaler=StandardScaler().fit(train)
    return [scaler.transform(x).astype('float32') for x in others],scaler


def tensors(x,device):
    return torch.as_tensor(x,dtype=torch.float32,device=device)


def batches(n,rng,batch=256):
    order=rng.permutation(n)
    for start in range(0,n,batch):
        yield order[start:start+batch]


def embeddings(model,x,device):
    model.eval()
    with torch.no_grad():
        return np.concatenate([encode(model,tensors(x[i:i+256],device)).cpu().numpy() for i in range(0,len(x),256)])


def fusion_embeddings(model,x,device):
    model.eval()
    with torch.no_grad():
        return np.concatenate([model.encoder(tensors(x[i:i+256],device)).cpu().numpy() for i in range(0,len(x),256)])


def train_representation(train,allx,seed,epochs,device,output):
    torch.manual_seed(seed)
    model=jfds_autoencoder().to(device)
    optim=torch.optim.Adam(model.parameters(),lr=1e-4)
    rng=np.random.default_rng(seed)
    losses=[]
    for epoch in range(epochs):
        model.train();total=0
        for ix in batches(len(train),rng):
            x=tensors(train[ix],device);optim.zero_grad()
            loss=torch.nn.functional.mse_loss(reconstruct(model,x),x)
            loss.backward();optim.step();total+=float(loss.detach())*len(ix)
        losses.append(total/len(train))
    torch.save(model.cpu().state_dict(),output/'lob-ae.pt')
    model.to(device)
    for p in model.parameters():p.requires_grad_(False)
    encoded=embeddings(model,allx,device)
    info=dict(loss=losses,parameters=sum(p.numel() for p in model.parameters()))
    del model
    return encoded,info


def train_fusion(xtrain,ytrain,allx,seed,epochs,device,alpha,output):
    torch.manual_seed(seed)
    model=Fusion(xtrain.shape[1]).to(device)
    optim=torch.optim.Adam(model.parameters(),lr=1e-4)
    rng=np.random.default_rng(seed)
    classes=[np.flatnonzero(ytrain==y) for y in (0,1)]
    if min(map(len,classes))<2:raise ValueError('Insufficient training labels')
    losses=[]
    for epoch in range(epochs):
        model.train();total=0
        steps=max(1,int(np.ceil(len(xtrain)/256)))
        for _ in range(steps):
            # Identical balanced batch schedule for every fusion variant.
            ix=np.concatenate([rng.choice(c,128,replace=len(c)<128) for c in classes]);rng.shuffle(ix)
            x=tensors(xtrain[ix],device);y=torch.as_tensor(ytrain[ix],device=device)
            optim.zero_grad();z,rec=model(x)
            loss=(1-alpha)*torch.nn.functional.mse_loss(rec,x)+alpha*paper_contrastive(z,y)
            loss.backward();optim.step();total+=float(loss.detach())
        losses.append(total/steps)
    torch.save(model.cpu().state_dict(),output)
    model.to(device);z=fusion_embeddings(model,allx,device)
    info=dict(loss=losses,alpha=alpha,parameters=sum(p.numel() for p in model.parameters()),input_dimensions=allx.shape[1])
    del model
    return z,info


def detector_fit(ztrain,ytrain,zval,yval,kind,seed):
    normal=ztrain[ytrain==0]
    scaler=StandardScaler().fit(normal)
    normal=scaler.transform(normal);v=scaler.transform(zval)
    # A deterministic cap is shared by all detectors, selected before test access.
    if len(normal)>5000:normal=normal[np.random.default_rng(seed).choice(len(normal),5000,replace=False)]
    grid=([dict(nu=nu,gamma_factor=g) for nu in (.01,.05,.1) for g in (.1,1.)] if kind=='ocsvm'
          else [dict(max_samples=n,max_features=f) for n in (128,256,512) for f in (.5,1.)])
    best=None;trials=[]
    for trial,cfg in enumerate(grid):
        if kind=='ocsvm':
            model=OneClassSVM(nu=cfg['nu'],gamma=cfg['gamma_factor']/normal.shape[1],cache_size=256)
        else:
            model=IsolationForest(n_estimators=100,random_state=seed,n_jobs=1,**cfg)
        model.fit(normal)
        score=-model.score_samples(v)
        ap=float(average_precision_score(yval,score));trials.append(dict(trial=trial,validation_ap=ap,**cfg))
        if best is None or ap>best[0]:best=(ap,model,score,cfg)
    ap,model,score,cfg=best
    negative=np.sort(score[yval==0])
    # Strict score > threshold; conservative upper order statistic (<= target empirical FPR).
    threshold=float(negative[min(len(negative)-1,int(np.ceil(.99*len(negative))))])
    return model,scaler,dict(selected=cfg,validation_ap=ap,threshold=threshold,trials=trials),score


def supervised_fit(xtrain,ytrain,xval,yval,method,seed):
    grid=([dict(C=c) for c in (.01,.1,1.,10.,100.,1000.)] if method=='supervised_logistic'
          else [dict(max_leaf_nodes=n,learning_rate=lr) for n in (7,15,31) for lr in (.03,.1)])
    best=None;trials=[]
    for trial,cfg in enumerate(grid):
        if method=='supervised_logistic':
            model=LogisticRegression(solver='liblinear',max_iter=1000,class_weight='balanced',random_state=seed,**cfg)
        else:
            model=HistGradientBoostingClassifier(max_iter=100,early_stopping=False,class_weight='balanced',random_state=seed,**cfg)
        model.fit(xtrain,ytrain);score=model.predict_proba(xval)[:,1]
        ap=float(average_precision_score(yval,score));trials.append(dict(trial=trial,validation_ap=ap,**cfg))
        if best is None or ap>best[0]:best=(ap,model,score,cfg)
    ap,model,score,cfg=best;negative=np.sort(score[yval==0])
    threshold=float(negative[min(len(negative)-1,int(np.ceil(.99*len(negative))))])
    return model,dict(selected=cfg,validation_ap=ap,threshold=threshold,trials=trials),score


def evaluate(y,score,threshold):
    precision,recall,_=precision_recall_curve(y,score)
    return dict(ap=float(average_precision_score(y,score)),pr_auc_trapezoidal=float(auc(recall,precision)),
                auroc=float(roc_auc_score(y,score)),prevalence=float(y.mean()),n=len(y),positives=int(y.sum()),
                recall_at_validation_1pct_fpr=float(np.mean(score[y==1]>threshold)),
                test_fpr=float(np.mean(score[y==0]>threshold)))


def run(dataset,output,regimes,seeds,epochs=10,device='cpu',engineering=False,folds=None):
    if not engineering and not os.environ.get('CQ_JOB_ID'):
        raise RuntimeError('Scientific runs require CQ')
    if engineering and (epochs>1 or dataset.stat().st_size>10*1024**2):
        raise ValueError('Local engineering run budget exceeded')
    if device=='cuda' and not torch.cuda.is_available():raise RuntimeError('Requested GPU unavailable')
    output.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    all_data=np.load(dataset,allow_pickle=False)
    data={k:all_data[k] for k in all_data.files}
    raw=data['raw'];manual=data['manual'].reshape(len(raw),-1)
    dynamics={k:data[k].reshape(len(raw),-1) for k in ('aligned','rank')}
    reports=[]
    for regime in regimes:
        for fold,tr,va,te in splits(data,regime):
            if folds is not None and fold not in folds:continue
            if engineering:
                # Take a bounded balanced prefix per split; no scientific interpretation.
                def small(ix):
                    return np.concatenate([ix[data['y'][ix]==y][:16] for y in (0,1)])
                tr,va,te=map(small,(tr,va,te))
            for ix in (tr,va,te):
                if len(np.unique(data['y'][ix]))!=2:raise ValueError('One-class split')
            assert not (set(tr)&set(va) or set(tr)&set(te) or set(va)&set(te))
            train_end={s:int(data['end_ns'][tr][data['stock'][tr]==s].max()) for s in set(data['stock'][tr])}
            if regime in ('date','style','combined') and data['end_ns'][tr].max()>=data['start_ns'][va].min():
                raise ValueError('Nonchronological split')
            for seed in seeds:
                started=time.monotonic();random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
                dest=output/f'{fold}-seed{seed}';dest.mkdir(exist_ok=True)
                index=np.concatenate([tr,va,te]);ntr=len(tr);nva=len(va)
                # Transform fit on training only. Test transforms are fixed and contain no fit/update.
                norm=StandardScaler().fit(raw[tr].reshape(-1,20))
                rx=norm.transform(raw[index].reshape(-1,20)).reshape(-1,25,20).astype('float32')
                rep,repinfo=train_representation(rx[:ntr],rx,seed,epochs,device,dest)
                np.savez_compressed(dest/'split.npz',train_ids=data['id'][tr],validation_ids=data['id'][va],test_ids=data['id'][te],
                                    raw_mean=norm.mean_,raw_scale=norm.scale_)
                runinfo=dict(fold=fold,seed=seed,epochs=epochs,device=device,cq_job=os.environ.get('CQ_JOB_ID'),
                             dataset_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest(),
                             versions=dict(python=sys.version,numpy=np.__version__,torch=torch.__version__,sklearn=sklearn.__version__),
                             code_sha256={f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ['lobbench/cascade.py','lobbench/cascade_run.py','lobbench/semisynthetic.py','configs/010-preregistered.json']},
                             sizes=dict(train=len(tr),validation=len(va),test=len(te)),representation=repinfo,methods={},
                             evidence_class='engineering_only' if engineering else 'semisynthetic_external_dataset_adaptation')
                cached={}
                for method in METHODS:
                    israw=method=='raw_ocsvm';isdyn=method=='dynamics_ocsvm';issuper=method.startswith('supervised_')
                    if issuper:features=np.concatenate([rx.reshape(len(rx),-1),manual[index],dynamics['aligned'][index]],axis=1)
                    elif israw:features=rx.reshape(len(rx),-1)
                    elif isdyn:features=np.concatenate([manual[index],dynamics['aligned'][index]],axis=1)
                    else:
                        parts=[] if method=='price_no_lob' else [rep]
                        parts.append(manual[index])
                        if method.startswith('price'):parts.append(dynamics['aligned'][index])
                        elif method.startswith('rank'):parts.append(dynamics['rank'][index])
                        features=np.concatenate(parts,axis=1)
                    (features,),sc=standardize(features[:ntr],[features])
                    fusionkey='cascade' if method in ('cascade_ocsvm','cascade_if') else method
                    modelinfo={}
                    if not israw and not isdyn and not issuper:
                        if fusionkey not in cached:
                            cached[fusionkey]=train_fusion(features[:ntr],data['y'][tr],features,seed,epochs,device,
                                                          0 if method=='price_no_scl' else .1,dest/(fusionkey+'.pt'))
                        z,modelinfo=cached[fusionkey]
                    else:z=features
                    kind='if' if method=='cascade_if' else 'ocsvm'
                    if issuper:
                        detector,selection,vscore=supervised_fit(z[:ntr],data['y'][tr],z[ntr:ntr+nva],data['y'][va],method,seed)
                        testscore=detector.predict_proba(z[ntr+nva:])[:,1]
                        detscaler=None
                    else:
                        detector,detscaler,selection,vscore=detector_fit(z[:ntr],data['y'][tr],z[ntr:ntr+nva],data['y'][va],kind,seed)
                        testscore=-detector.score_samples(detscaler.transform(z[ntr+nva:]))
                    # Test labels are consumed only after representation and detector selection.
                    metrics=evaluate(data['y'][te],testscore,selection['threshold'])
                    np.savez_compressed(dest/(method+'-predictions.npz'),id=data['id'][te],stock=data['stock'][te],date=data['date'][te],
                                        kind=data['kind'][te],y=data['y'][te],score=testscore,validation_id=data['id'][va],validation_y=data['y'][va],
                                        validation_score=vscore)
                    # Rebuild embeddings from saved model states, inputs and normalizers; no unsafe pickle of sklearn estimators.
                    np.savez_compressed(dest/(method+'-normalizers.npz'),feature_mean=sc.mean_,feature_scale=sc.scale_,
                                        detector_mean=detscaler.mean_ if detscaler else np.zeros(z.shape[1]),
                                        detector_scale=detscaler.scale_ if detscaler else np.ones(z.shape[1]))
                    runinfo['methods'][method]=dict(metrics=metrics,selection=selection,fusion=modelinfo)
                    (dest/'metrics.json').write_text(json.dumps(runinfo,indent=2)+'\n')
                    print(f'{fold} seed={seed} {method} AP={metrics["ap"]:.6f}',flush=True)
                runinfo['seconds']=time.monotonic()-started
                runinfo['peak_rss_native']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                if device=='cuda':runinfo['peak_cuda_bytes']=torch.cuda.max_memory_allocated()
                (dest/'metrics.json').write_text(json.dumps(runinfo,indent=2)+'\n')
                reports.append(runinfo)
                (output/'summary.json').write_text(json.dumps(dict(status='partial',runs=reports),indent=2)+'\n')
                (output/'progress.txt').write_text(f'{len(reports)} completed fold-seed runs\n')
    (output/'summary.json').write_text(json.dumps(dict(status='complete',runs=reports),indent=2)+'\n')
    return reports

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--regimes',nargs='+',choices=['date','stock','combined','style'],default=['date','stock','combined'])
    p.add_argument('--seeds',nargs='+',type=int,default=[0,1,2,3,4]);p.add_argument('--epochs',type=int,default=10)
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--engineering',action='store_true')
    p.add_argument('--folds',nargs='+')
    args=p.parse_args();run(args.dataset,args.output,args.regimes,args.seeds,args.epochs,args.device,args.engineering,args.folds)
