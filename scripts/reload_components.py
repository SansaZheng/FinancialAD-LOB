"""Rebuild frozen stage013 predictions from numeric exports; never fit/select."""
import argparse,hashlib,json,platform,time
from pathlib import Path
import numpy as np
from lobbench.direct import base_features
from lobbench.portable import interactions,normalize,block_indices,array_hash,tree_score,dense,ae_encode,ocsvm_score

def reload_run(dataset,folder):
 start=time.monotonic();r=json.loads((folder/'metrics.json').read_text());d=dict(np.load(dataset,allow_pickle=False))
 if hashlib.sha256(dataset.read_bytes()).hexdigest()!=r['dataset_sha256']:raise ValueError('Input dataset hash mismatch')
 for name,digest in r.get('artifact_sha256',{}).items():
  if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=digest:raise ValueError('Saved artifact hash mismatch: '+name)
 split=np.load(folder/'split.npz');lookup={v:i for i,v in enumerate(d['id'])};index=np.array([lookup[v] for key in ['train_ids','validation_ids','test_ids'] for v in split[key]]);nt,nv=len(split['train_ids']),len(split['validation_ids']);sub={k:d[k][index] for k in ['raw','manual','aligned']};base=base_features(sub);extra=interactions(sub['aligned']);hashes=dict(base=array_hash(base),interaction=array_hash(extra));normalized={};shared=None;items=[]
 for method,m in r['methods'].items():
  if method.startswith('hgb_'):
   inds=block_indices(method[4:]);x=np.concatenate([base,extra[:,inds]],axis=1) if len(inds) else base;scores=tree_score(json.loads((folder/(method+'.json')).read_text()),x[nt:]);tol=1e-12
  else:
   if method.startswith('mlp_'):
    name=method[4:]
    if name not in normalized:
     norm=np.load(folder/(name+'-normalizer.npz'));x=np.concatenate([base,extra],axis=1) if name=='all' else base;normalized[name]=normalize(x,norm['mean'],norm['scale'],norm['keep'])
    x=normalized[name]
   else:
    if shared is None:
     norm=np.load(folder/'raw-normalizer.npz');raw=((sub['raw'].astype('float64')-norm['mean'])/norm['scale']).astype('float32');rep=ae_encode(dict(np.load(folder/'lob-ae.npz')),raw);joined=np.concatenate([rep,sub['manual'][:,:,[0,1,2,3,12]].reshape(len(index),-1),sub['aligned'].reshape(len(index),-1)],axis=1);norm=np.load(folder/'shared-normalizer.npz');shared=normalize(joined,norm['mean'],norm['scale'],norm['keep']);hashes.update(ae_embedding=array_hash(rep),shared=array_hash(shared));del raw,rep,joined
    x=shared
   if method.startswith('cascade'):
    z=dense(dict(np.load(folder/(method+'-encoder.npz'))),x,embedding=True);hashes[method+'_embedding']=array_hash(z);scores=ocsvm_score(dict(np.load(folder/(method+'-detector.npz'))),z[nt:]);del z
   else:scores=dense(dict(np.load(folder/(method+'.npz'))),x[nt:])
   tol=1e-7
  p=np.load(folder/(method+'-predictions.npz'));reference=np.concatenate([p['validation_score'],p['score']]);np.testing.assert_array_equal(p['validation_id'],split['validation_ids']);np.testing.assert_array_equal(p['id'],split['test_ids']);np.testing.assert_allclose(scores,reference,rtol=0,atol=tol)
  threshold=m['selection']['threshold'];flips=int(np.sum((scores>threshold)!=(reference>threshold)))
  if flips:raise ValueError('Unchanged input decision flips: '+method)
  items.append(dict(method=method,points=len(scores),max_absolute_score_error=float(np.max(np.abs(scores-reference))),threshold_flips=flips,tolerance=tol))
 if hashes!=r['feature_hashes']:raise ValueError('Canonical feature/embedding hash mismatch: '+str({k:(r['feature_hashes'].get(k),v) for k,v in hashes.items() if v!=r['feature_hashes'].get(k)}))
 return dict(passed=True,fold=r['fold'],seed=r['seed'],evidence_class=r['evidence_class'],methods=items,feature_hashes=hashes,seconds=time.monotonic()-start,versions=dict(python=platform.python_version(),numpy=np.__version__),platform=platform.platform())

def main(dataset,root,output):
 rows=[]
 for p in sorted(root.glob('**/metrics.json')):
  r=json.loads(p.read_text())
  if r.get('evidence_class') not in ['stage013_frozen_semisynthetic','engineering_only'] or 'feature_hashes' not in r:continue
  row=reload_run(dataset,p.parent);rows.append(row);print(row['fold'],row['seed'],'reload passed',flush=True)
 if not rows:raise ValueError('No stage013 results')
 out=dict(passed=True,fold_seed_runs=len(rows),selected_evaluations=sum(len(r['methods']) for r in rows),rows=rows,no_refitting=True,scope='Numeric export, feature/embedding hash and prediction/decision parity in this recorded environment; no universal platform guarantee')
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for name in ['dataset','root','output']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();main(a.dataset,a.root,a.output)
