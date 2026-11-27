"""Stage013 numerical contract and data-only inference exports.

Qualification is empirical across recorded environments, not a universal IEEE or
library-version compatibility guarantee. No labels or fitted statistics enter
interaction features. Historical stage012 code is intentionally unchanged.
"""
import hashlib,json
from pathlib import Path
import numpy as np

BLOCKS={'gram':slice(0,100),'lag':slice(100,400),'moments':slice(400,488)}

def array_hash(x):
 x=np.ascontiguousarray(x)
 return hashlib.sha256(str(x.shape).encode()+x.dtype.str.encode()+x.tobytes()).hexdigest()

def interactions(aligned):
 x=np.asarray(aligned,dtype=np.float64).reshape(-1,25,2,5,4)
 if not np.isfinite(x).all():raise ValueError('Nonfinite observed input')
 a=np.log1p(np.maximum(x[...,0],0))*x[...,2];r=np.log1p(np.maximum(x[...,1],0))*x[...,3]
 def unit(v):return v/np.maximum(np.sqrt((v*v).sum(axis=1,keepdims=True)),1e-8)
 aa,rr=unit(a),unit(r);feats=[]
 for v,original in [(aa,a),(rr,r)]:
  g=np.einsum('ntsl,ntsk->nslk',v,v,optimize=False)
  for k in range(5):g[:,:,k,k]=(original[:,:,:,k].sum(axis=1)>0).astype(float)
  feats.append(g.reshape(len(x),-1))
 for lag in (0,1,2,4,8,12):
  before=aa[:,:25-lag] if lag else aa;after=rr[:,lag:] if lag else rr
  feats.append(np.einsum('ntsl,ntsk->nslk',before,after,optimize=False).reshape(len(x),-1))
 t=np.arange(25,dtype=np.float64)[None,:,None,None]/24
 for v in (a,r):
  total=v.sum(axis=1);center=(v*t).sum(axis=1)/np.maximum(total,1e-8);width=(v*(t-center[:,None])**2).sum(axis=1)/np.maximum(total,1e-8)
  for z in (np.log1p(total),v.max(axis=1),center,width):feats.append(z.reshape(len(x),-1))
  pooled=v.sum(axis=3);mass=pooled.sum(axis=1)
  for z in (pooled.max(axis=1)/np.maximum(mass,1e-8),(v>0).sum(axis=3).max(axis=1)/5):feats.append(z)
 out=np.round(np.concatenate(feats,axis=1),6).astype(np.float32)
 if out.shape[1]!=488 or not np.isfinite(out).all():raise ValueError('Invalid canonical features')
 return out

def block_indices(name):
 if name=='perlevel':return np.r_[400:440,444:484]
 parts=list(BLOCKS) if name=='all' else ([] if name=='base' else name.split('_'))
 if len(set(parts))!=len(parts) or any(p not in BLOCKS for p in parts):raise ValueError('Unknown feature subset')
 return np.array([i for p in parts for i in range(BLOCKS[p].start,BLOCKS[p].stop)],dtype=int)

def normalize(x,mean,scale,keep):
 # Identical elementwise arithmetic in bounded batches, avoiding full-size
 # float64 temporaries when two workers share provider RAM.
 out=np.empty((len(x),int(np.sum(keep))),dtype=np.float32)
 for begin in range(0,len(x),512):
  value=np.array(x[begin:begin+512],dtype=np.float64,copy=True);value-=mean;value/=scale
  out[begin:begin+len(value)]=value[:,keep]
 return out

def batched_interactions(aligned):
 out=np.empty((len(aligned),488),dtype=np.float32)
 for begin in range(0,len(aligned),512):out[begin:begin+512]=interactions(aligned[begin:begin+512])
 return out

def export_hgb(model,path):
 if len(model.classes_)!=2 or np.any(model.is_categorical_):raise ValueError('Binary numeric HGB only')
 trees=[]
 for stage in model._predictors:
  if len(stage)!=1:raise ValueError('Binary tree shape required')
  node=stage[0].nodes
  trees.append({k:node[k].tolist() for k in ['value','feature_idx','num_threshold','missing_go_to_left','left','right','is_leaf']})
 doc=dict(format='hgb-numeric-v1',baseline=float(model._baseline_prediction.ravel()[0]),trees=trees)
 Path(path).write_text(json.dumps(doc,separators=(',',':'))+'\n');return doc

def tree_score(doc,x):
 x=np.asarray(x,dtype=np.float64);out=np.full(len(x),doc['baseline'])
 for tree in doc['trees']:
  t={k:np.asarray(v) for k,v in tree.items()};nodes=np.zeros(len(x),dtype=int);active=np.arange(len(x))
  while len(active):
   n=nodes[active];leaf=t['is_leaf'][n].astype(bool);done=active[leaf];out[done]+=t['value'][n[leaf]];active=active[~leaf]
   if len(active):
    n=nodes[active];v=x[active,t['feature_idx'][n].astype(int)];go=np.where(np.isnan(v),t['missing_go_to_left'][n].astype(bool),v<=t['num_threshold'][n]);nodes[active]=np.where(go,t['left'][n],t['right'][n]).astype(int)
 # Stable logistic conversion, then fixed score contract.
 prob=np.empty(len(out));positive=out>=0;prob[positive]=1/(1+np.exp(-out[positive]));z=np.exp(out[~positive]);prob[~positive]=z/(1+z)
 return np.round(prob,12)

def export_dense(model,path,encoder=False):
 import torch
 layers=model.encoder if encoder else model.layers
 values={};n=0
 for layer in layers:
  if isinstance(layer,torch.nn.Linear):values['w'+str(n)]=layer.weight.detach().cpu().numpy();values['b'+str(n)]=layer.bias.detach().cpu().numpy();n+=1
  elif not isinstance(layer,torch.nn.ReLU):raise ValueError('Unsupported dense activation')
 values['layers']=np.array(n);np.savez_compressed(path,**values);return values

def dense(values,x,embedding=False):
 out=[]
 for begin in range(0,len(x),1024):
  z=np.asarray(x[begin:begin+1024],dtype=np.float64)
  for k in range(int(values['layers'])):
   z=z@np.asarray(values['w'+str(k)],dtype=np.float64).T+values['b'+str(k)]
   if k+1<int(values['layers']):z=np.maximum(z,0)
  out.append(z)
 z=np.concatenate(out)
 return np.round(z,6).astype('float32') if embedding else np.round(z.reshape(-1),8)

def export_ae(model,path):
 state={k:v.detach().cpu().numpy() for k,v in model.state_dict().items() if k.startswith(('linear_embedding.','pe.','encoder.layers.','linear_encoding.'))}
 np.savez_compressed(path,**state);return state

def ae_encode(state,raw,batch=128):
 def linear(x,p):return x@np.asarray(state[p+'.weight'],dtype=np.float64).T+state[p+'.bias']
 def norm(x,p):return (x-x.mean(axis=-1,keepdims=True))/np.sqrt(x.var(axis=-1,keepdims=True)+1e-5)*state[p+'.weight']+state[p+'.bias']
 result=[]
 for begin in range(0,len(raw),batch):
  x=linear(np.asarray(raw[begin:begin+batch],dtype=np.float64),'linear_embedding')+state['pe.pe'][:,:25]
  for layer in range(2):
   p='encoder.layers.'+str(layer);q,k,v=np.split(x@np.asarray(state[p+'.self_attn.in_proj_weight'],dtype=np.float64).T+state[p+'.self_attn.in_proj_bias'],3,axis=-1)
   def heads(z):return z.reshape(len(x),25,8,8).transpose(0,2,1,3)
   q,k,v=map(heads,(q,k,v));attention=q@k.swapaxes(-1,-2)/np.sqrt(8.);attention-=attention.max(axis=-1,keepdims=True);attention=np.exp(attention);attention/=attention.sum(axis=-1,keepdims=True)
   value=(attention@v).transpose(0,2,1,3).reshape(len(x),25,64);x=norm(x+linear(value,p+'.self_attn.out_proj'),p+'.norm1');x=norm(x+linear(np.maximum(linear(x,p+'.linear1'),0),p+'.linear2'),p+'.norm2')
  result.append(linear(x.reshape(len(x),-1),'linear_encoding'))
 return np.round(np.concatenate(result),6).astype('float32')

def rbf(x,y,gamma):
 x=np.asarray(x,dtype=np.float64);y=np.asarray(y,dtype=np.float64)
 return np.exp(-gamma*np.maximum((x*x).sum(1)[:,None]+(y*y).sum(1)[None,:]-2*x@y.T,0))

def ocsvm_score(values,z):
 x=(np.asarray(z,dtype=np.float64)-values['mean'])/values['scale'];out=[]
 for start in range(0,len(x),256):out.append(-rbf(x[start:start+256],values['support'],float(values['gamma']))@values['dual'])
 return np.round(np.concatenate(out),8)
