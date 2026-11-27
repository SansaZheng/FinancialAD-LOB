"""Unlabeled whole-cohort numerical fingerprint; no fitted preprocessing."""
import argparse,hashlib,json,platform
from pathlib import Path
import numpy as np
from lobbench.direct import base_features
from lobbench.portable import interactions

def fingerprint(dataset,output,reference=None):
 archive=np.load(dataset,allow_pickle=False);d={k:archive[k] for k in ['raw','manual','aligned']};n=len(d['raw']);hashes={}
 for key,width in [('base',1625),('interaction',488)]:
  h=hashlib.sha256(str((n,width)).encode()+np.dtype('float32').str.encode())
  for start in range(0,n,512):
   x=base_features({k:v[start:start+512] for k,v in d.items()}) if key=='base' else interactions(d['aligned'][start:start+512])
   if x.shape[1]!=width or not np.isfinite(x).all():raise ValueError('Invalid source features')
   h.update(np.ascontiguousarray(x).tobytes())
  hashes[key]=h.hexdigest()
 r=dict(passed=True,windows=n,dataset_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest(),feature_hashes=hashes,portable_source_sha256=hashlib.sha256(Path('lobbench/portable.py').read_bytes()).hexdigest(),versions=dict(python=platform.python_version(),numpy=np.__version__),platform=platform.platform(),scope='All unlabelled source-window features; no statistics fitted or labels read')
 if reference:
  original=json.loads(reference.read_text())
  for k in ['windows','dataset_sha256','feature_hashes','portable_source_sha256']:
   if r[k]!=original[k]:raise ValueError('Whole-cohort feature mismatch: '+k)
  r['reference_sha256']=hashlib.sha256(reference.read_bytes()).hexdigest()
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--reference',type=Path);a=p.parse_args();fingerprint(a.dataset,a.output,a.reference)
