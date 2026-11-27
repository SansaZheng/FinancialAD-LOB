import hashlib,json,tempfile,unittest
from pathlib import Path
import numpy as np
from scripts.summarize_direct import summarize

class DirectReportingTests(unittest.TestCase):
 def test_analytic_paired_gain_and_partial_status(self):
  protocol=Path('configs/012-preregistered.json');cfg=json.loads(protocol.read_text())
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);folder=root/'date-s0';folder.mkdir()
   y=np.tile([0,0,1],6);stock=np.repeat(['A','B'],9);date=np.tile(np.repeat(['d1','d2','d3'],3),2);kind=np.tile(['background','benign_burst','layered'],6)
   record=dict(fold='date',seed=0,evidence_class='stage012_frozen_semisynthetic',protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),methods={})
   for method in cfg['methods']:
    score=np.ones(len(y)) if method=='hgb' else y.astype(float)
    np.savez_compressed(folder/(method+'-predictions.npz'),y=y,score=score,stock=stock,date=date,kind=kind)
    record['methods'][method]=dict(selection={'threshold':.5},metrics=dict(ap=1/3 if method=='hgb' else 1.,test_fpr=1. if method=='hgb' else 0.,recall_at_validation_1pct_fpr=1.))
   (folder/'metrics.json').write_text(json.dumps(record));r=summarize(root,protocol,root/'report',replicates=25)
   self.assertEqual(r['status'],'partial');self.assertEqual(r['fold_seed_runs'],1)
   contrast=next(x for x in r['contrasts'] if x['method']=='interaction_mlp_hard' and x['reference']=='hgb')
   self.assertAlmostEqual(contrast['mean_stock_day_ap_delta'],2/3)
   np.testing.assert_allclose(contrast['exploratory_95pct_interval'],[2/3,2/3])

class DirectVerifierTests(unittest.TestCase):
 def test_accepts_schema_fixture_and_rejects_validation_label_tampering(self):
  # Analytic artifact fixture only: no claimed financial model training.
  from tests.test_direct import fixture
  from lobbench.direct import base_features,interaction_features,mine
  from lobbench.direct_run import splits
  from lobbench.cascade_run import evaluate
  from scripts.verify_direct_results import verify
  from sklearn.preprocessing import StandardScaler
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);folder=root/'date-s0';folder.mkdir();d=fixture();dataset=root/'data.npz';np.savez_compressed(dataset,**d)
   cfg=json.loads(Path('configs/012-preregistered.json').read_text());cfg['methods']=['hgb'];protocol=root/'config.json';protocol.write_text(json.dumps(cfg))
   _,tr,va,te=next(splits(d,cfg,'date'));np.savez_compressed(folder/'split.npz',train_ids=d['id'][tr],validation_ids=d['id'][va],test_ids=d['id'][te],eligible_train_ids=d['id'][tr])
   b=base_features(d)[tr];extra=interaction_features(d['aligned'][tr])
   for name,x in [('base',b),('interaction',np.concatenate([b,extra],axis=1))]:
    scaler=StandardScaler().fit(x);np.savez_compressed(folder/(name+'-normalizer.npz'),mean=scaler.mean_,scale=scaler.scale_,keep=scaler.var_>0)
   groups=np.char.add(np.char.add(d['stock'][tr],'|'),d['date'][tr]);mining,folds=mine(extra,d['y'][tr],groups,0,engineering=True)
   np.savez_compressed(folder/'mining.npz',ids=d['id'][tr],y=d['y'][tr],groups=groups,**mining);(folder/'mining-folds.json').write_text(json.dumps(folds))
   prediction=dict(id=d['id'][te],y=d['y'][te],score=d['y'][te].astype(float),stock=d['stock'][te],date=d['date'][te],kind=d['kind'][te],validation_id=d['id'][va],validation_y=d['y'][va],validation_score=d['y'][va].astype(float))
   np.savez_compressed(folder/'hgb-predictions.npz',**prediction);(folder/'hgb.joblib').write_bytes(b'unit-test-presence-marker')
   record=dict(fold='date',seed=0,evidence_class='stage012_frozen_semisynthetic',dataset_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest(),protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),methods={'hgb':dict(metrics=evaluate(d['y'][te],prediction['score'],0.),selection=dict(trial=0,selected={},validation_ap=1.,threshold=0.,trials=[dict(trial=i,configuration={},validation_ap=1.) for i in range(6)]))})
   record['source_sha256']={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in ['lobbench/direct.py','lobbench/direct_run.py']}
   (folder/'metrics.json').write_text(json.dumps(record));r=verify(root,dataset,protocol,root/'receipt.json');self.assertTrue(r['passed']);self.assertFalse(r['complete_suite'])
   normpath=folder/'interaction-normalizer.npz';norm=dict(np.load(normpath));original=norm['mean'].copy();norm['mean'][-1]+=.01;np.savez_compressed(normpath,**norm)
   with self.assertRaises(AssertionError):verify(root,dataset,protocol,root/'tampered-norm.json')
   norm['mean']=original;np.savez_compressed(normpath,**norm)
   prediction['validation_y']=1-prediction['validation_y'];np.savez_compressed(folder/'hgb-predictions.npz',**prediction)
   with self.assertRaises(AssertionError):verify(root,dataset,protocol,root/'receipt.json')
