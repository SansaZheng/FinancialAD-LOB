import json,tempfile,unittest
from pathlib import Path
import numpy as np
from lobbench.direct import interaction_features,base_features,weights,mine
from lobbench.direct_run import splits,subset,run


def fixture():
 cfg=json.loads(Path('configs/012-preregistered.json').read_text());dates=cfg['train_dates']+cfg['validation_dates']+cfg['test_dates'];rng=np.random.default_rng(12)
 stock=[];day=[];y=[];starts=[]
 for s in cfg['stocks']:
  for d,ds in enumerate(dates):
   for k in range(6):stock.append(s);day.append(ds);y.append(k%2);starts.append(d*10**9+k*100)
 n=len(y);flow=np.maximum(rng.normal(size=(n,25,2,5,4)),0).astype('float32');flow[...,2:]=1
 return dict(raw=rng.normal(size=(n,25,20)).astype('float32'),manual=rng.normal(size=(n,25,13)).astype('float32'),aligned=flow.reshape(n,25,40),y=np.array(y),stock=np.array(stock),date=np.array(day),id=np.array(['fixture'+str(i) for i in range(n)]),kind=np.array(['background' if z==0 else 'layered' for z in y]),start_ns=np.array(starts),end_ns=np.array(starts)+24)


class DirectTests(unittest.TestCase):
 def test_unknown_mass_ignored_and_zero_finite(self):
  x=np.zeros((3,25,40),dtype='float32');baseline=interaction_features(x);x.reshape(3,25,2,5,4)[...,:2]=1000
  np.testing.assert_array_equal(interaction_features(x),baseline);self.assertEqual(baseline.shape,(3,488))
 def test_synchronized_withdrawal_has_greater_cross_level_cooccurrence(self):
  x=np.zeros((2,25,2,5,4),dtype='float32');x[...,2:]=1
  x[0,10,0,:,1]=1
  for k in range(5):x[1,8+k,0,k,1]=1
  f=interaction_features(x.reshape(2,25,40));self.assertGreater(f[0,50:75].sum(),f[1,50:75].sum())
 def test_hard_weights_preserve_class_mass(self):
  y=np.array([0]*20+[1]*4);hard=np.arange(24)<2;w=weights(y,hard)
  self.assertAlmostEqual(w[y==0].sum(),12);self.assertAlmostEqual(w[y==1].sum(),12);self.assertAlmostEqual(w[0]/w[2],5)
 def test_mining_is_group_out_of_fold(self):
  rng=np.random.default_rng(1);y=np.tile([0,0,0,1],12);groups=np.repeat(['A','B','C','D','E','F'],8)
  m,folds=mine(rng.normal(size=(48,8)),y,groups,0,engineering=True)
  self.assertEqual(m['hard'].sum(),4);self.assertFalse(m['hard'][y==1].any());self.assertTrue(np.isfinite(m['score']).all())
  for f in folds:self.assertFalse(set(f['fit_groups'])&set(f['score_groups']))
 def test_miner_held_out_labels_cannot_change_their_own_scores(self):
  rng=np.random.default_rng(3);x=rng.normal(size=(96,8));y=np.tile([0,0,0,1],24);groups=np.repeat(['A','B','C','D','E','F'],16)
  original,_=mine(x,y,groups,0,engineering=True);held=original['fold']==0;changed=y.copy();changed[held]=1-changed[held]
  new,_=mine(x,changed,groups,0,engineering=True)
  np.testing.assert_array_equal(original['score'][held],new['score'][held])
 def test_metadata_and_labels_do_not_enter_predictors(self):
  d=fixture();x=base_features(d);d['y']=1-d['y'];d['kind']=np.repeat('unrelated',len(x));d['id']=d['id'][::-1]
  np.testing.assert_array_equal(x,base_features(d))
 def test_all_fresh_splits_and_shared_subset(self):
  d=fixture();cfg=json.loads(Path('configs/012-preregistered.json').read_text())
  for regime in ['date','combined']:
   for fold,tr,va,te in splits(d,cfg,regime):
    self.assertFalse(set(tr)&set(va) or set(tr)&set(te) or set(va)&set(te));self.assertLess(d['end_ns'][tr].max(),d['start_ns'][va].min())
    if regime=='combined':self.assertFalse(set(d['stock'][tr])&set(d['stock'][te]))
    np.testing.assert_array_equal(subset(tr,3,15),subset(tr,3,15))
 def test_all_ten_methods_execute_bounded_fixture(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);data=root/'fixture.npz';np.savez_compressed(data,**fixture())
   r=run(data,root/'out','date','date',0,Path('configs/012-preregistered.json'),engineering=True)
   self.assertEqual(len(r['methods']),10)
   for m in r['methods'].values():self.assertEqual(len(m['selection']['trials']),6)
   self.assertEqual(r['evidence_class'],'engineering_only')
