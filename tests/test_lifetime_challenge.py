import itertools,unittest
import numpy as np
from lobbench.lifetime_challenge import offsets

class LifetimeChallengeTests(unittest.TestCase):
 def test_exact_per_level_marginals_match_positive_two_direction_policy(self):
  controls=np.stack([offsets(b) for b in itertools.product([0,1],repeat=5)])
  positive=np.stack([np.arange(5),np.arange(5)[::-1]])
  for k in range(5):np.testing.assert_array_equal(np.sort(controls[:,k]),np.sort(np.repeat(positive[:,k],16)))
  # Middle-level bit is redundant: four of32 patterns equal a positive wave.
  collisions=np.array([np.all(np.diff(x)==1) or np.all(np.diff(x)==-1) for x in controls])
  self.assertEqual(collisions.sum(),4)
 def test_all_lifecycles_stay_within_declared_window(self):
  for start in range(1,8):
   placements=start+np.arange(5)[::-1]
   for center in range(start+5,20):
    for b in itertools.product([0,1],repeat=5):
     stops=center+offsets(b);self.assertTrue((stops>placements).all());self.assertTrue((stops<25).all())
 def test_saved_estimator_prediction_parity(self):
  import json,tempfile
  from pathlib import Path
  from tests.test_direct import fixture
  from lobbench.direct_run import run
  from scripts.evaluate_lifetime_challenge import evaluate
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);data=fixture();data['kind']=np.where(data['y']==0,'benign_burst','layered');dataset=root/'fixture.npz';np.savez_compressed(dataset,**data)
   protocol=Path('configs/012-preregistered.json');run(dataset,root/'models'/'date-s0','date','date',0,protocol,engineering=True)
   pred=np.load(root/'models/date-s0/hgb-predictions.npz');lookup={v:i for i,v in enumerate(data['id'])};ix=np.array([lookup[v] for v in pred['id']]);challenge=root/'challenge.npz';np.savez_compressed(challenge,**{k:v[ix] for k,v in data.items()})
   r=evaluate(root/'models',challenge,root/'scores',protocol,engineering=True);self.assertEqual(r['status'],'engineering_only')
   for s in r['summary']:
    self.assertAlmostEqual(s['primary_macro_ap'],s['challenge_macro_ap']);self.assertAlmostEqual(s['primary_benign_fpr'],s['challenge_benign_fpr'])
   from scripts.verify_lifetime_challenge import verify
   audit=verify(root/'models',challenge,root/'scores',protocol,root/'verified.json',engineering=True)
   self.assertTrue(audit['passed']);self.assertEqual(audit['selected_evaluations'],10)
   bad=root/'scores/date-s0/hgb-predictions.npz';values=dict(np.load(bad));values['primary_score'][0]+=.01;np.savez_compressed(bad,**values)
   with self.assertRaises(AssertionError):verify(root/'models',challenge,root/'scores',protocol,root/'tampered.json',engineering=True)
