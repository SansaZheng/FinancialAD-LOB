import json,tempfile,unittest
from pathlib import Path
import numpy as np,torch
from tests.test_direct import fixture as old_fixture
from lobbench.component_run import run,SharedBCE
from lobbench.cascade import Fusion

def fixture():
 d=old_fixture();cfg=json.loads(Path('configs/013-preregistered.json').read_text());old=sorted(set(d['date']));days=cfg['train_dates']+cfg['validation_dates']+cfg['test_dates']
 # Reuse only synthetic array shapes, create all12registered dates independently.
 pieces=[]
 for i,day in enumerate(days):
  ix=np.flatnonzero(d['date']==old[i%len(old)]);part={k:v[ix].copy() for k,v in d.items()};part['date']=np.repeat(day,len(ix));part['id']=np.array([f'fixture013-{i}-{j}' for j in range(len(ix))]);part['start_ns']=np.full(len(ix),i*10**9)+np.arange(len(ix))*100;part['end_ns']=part['start_ns']+24;pieces.append(part)
 return {k:np.concatenate([p[k] for p in pieces]) for k in d}

class ComponentTests(unittest.TestCase):
 def test_shared_encoder_initialization_matches_cascade(self):
  torch.manual_seed(4);a=Fusion(15);torch.manual_seed(4);b=SharedBCE(15)
  for x,y in zip(a.encoder.parameters(),list(b.layers.parameters())[:4]):torch.testing.assert_close(x,y,rtol=0,atol=0)
 def test_registered14methods_fixture_and_reusable_models(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=root/'fixture.npz';np.savez_compressed(p,**fixture());r=run(p,root/'out','date','date',0,Path('configs/013-preregistered.json'),engineering=True)
   from scripts.reload_components import reload_run
   receipt=reload_run(p,root/'out');self.assertTrue(receipt['passed']);self.assertEqual(len(receipt['methods']),14)
   self.assertEqual(len(r['methods']),14);self.assertEqual(r['evidence_class'],'engineering_only')
   from scripts.verify_components import verify
   checked=verify(root/'out',p,Path('configs/013-preregistered.json'),root/'audit.json',engineering=True);self.assertTrue(checked['passed']);self.assertEqual(checked['selected_evaluations'],14)
   bad=root/'out/metrics.json';data=json.loads(bad.read_text());data['methods']['hgb_base']['selection']['threshold']+=.01;bad.write_text(json.dumps(data))
   with self.assertRaises(ValueError):verify(root/'out',p,Path('configs/013-preregistered.json'),root/'bad.json',engineering=True)
   for m,v in r['methods'].items():self.assertEqual(len(v['selection']['trials']),6);self.assertTrue((root/'out'/(m+'-predictions.npz')).exists())
