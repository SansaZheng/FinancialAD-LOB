"""Stage012 saved-artifact parity diagnostic only; no fitting or AP selection."""
import json,hashlib,platform
from pathlib import Path
import numpy as np,joblib,torch,sklearn
from lobbench.direct import base_features,interaction_features,DirectMLP
from lobbench.direct_run import predict,splits,subset
r=Path('results/cq-012/j-1127-02f40d/batch/date-s0');cfg=json.load(open('configs/012-preregistered.json'));d=dict(np.load('results/cq-012/j-1127-1d410b/benchmark/benchmark.npz'));c=dict(np.load('results/cq-012/j-1127-d406c2/challenge/challenge.npz'))
_,tr,va,te=next(splits(d,cfg,'date'));tr=subset(tr,0,12000);ix=np.concatenate([tr,va,te]);nt=len(tr)+len(va)
a=interaction_features(d['aligned'][ix])[nt:];b=interaction_features(c['aligned']);look={v:i for i,v in enumerate(d['id'][te])};j=np.array([look[z] for z in c['id']]);unchanged=c['kind']!='benign_wave';aa=a[j];diff=abs(aa[unchanged]-b[unchanged]);print('extra differences',float(diff.max()),np.sum(diff!=0),np.flatnonzero(np.any(diff!=0,axis=0)).tolist(),flush=True)
base=base_features(c);rr=json.load(open(r/'metrics.json'));report=dict(versions=dict(python=platform.python_version(),numpy=np.__version__,sklearn=sklearn.__version__,torch=torch.__version__),max_interaction_rebuild_difference=float(diff.max()),different_coordinates=np.flatnonzero(np.any(diff!=0,axis=0)).tolist(),models={});torch.set_num_threads(1)
for m,item in rr['methods'].items():
 enhanced=m.startswith('interaction_');norm=np.load(r/('interaction-normalizer.npz' if enhanced else 'base-normalizer.npz'));x=np.concatenate([base,b],axis=1) if enhanced else base.copy();x-=norm['mean'];x/=norm['scale'];x=np.ascontiguousarray(x[:,norm['keep']],dtype=np.float32)
 if 'mlp' in m:model=DirectMLP(x.shape[1]);model.load_state_dict(torch.load(r/(m+'.pt'),map_location='cpu',weights_only=True));score=predict(model,x,'cpu')
 else:model=joblib.load(r/(m+'.joblib'));score=model.predict_proba(x)[:,1]
 p=np.load(r/(m+'-predictions.npz'));err=abs(score[unchanged]-p['score'][j][unchanged]);info=dict(max_error=float(err.max()),mismatch_count=int(np.sum(err>1e-4+1e-4*abs(p['score'][j][unchanged]))));report['models'][m]=info;print(m,info,flush=True)
Path('results/engineering/direct-012/local-reload-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n')
