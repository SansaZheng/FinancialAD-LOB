import hashlib,json,tempfile,unittest
from pathlib import Path
import numpy as np
from scripts.summarize_components import summarize

class ComponentReportingTests(unittest.TestCase):
 def test_analytic_factorial_and_no_false_completion(self):
  protocol=Path('configs/013-preregistered.json');cfg=json.loads(protocol.read_text())
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);f=root/'date-s0';f.mkdir();y=np.tile([0,0,1],12);stock=np.repeat(['A','B'],18);dates=np.tile(np.repeat(cfg['test_dates'],3),2);kind=np.tile(['background','benign_wave','layered'],12)
   report=dict(fold='date',seed=0,evidence_class='stage013_frozen_semisynthetic',protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),dataset_sha256='analytic-unit-fixture-only',methods={})
   for method in cfg['methods']:
    perfect=method.startswith('hgb') and ('gram' in method or method=='hgb_all');score=y.astype(float) if perfect else np.zeros(len(y));np.savez_compressed(f/(method+'-predictions.npz'),y=y,score=score,stock=stock,date=dates,kind=kind)
    report['methods'][method]=dict(selection=dict(threshold=.5),metrics=dict(ap=1. if perfect else 1/3,test_fpr=0.,recall_at_validation_1pct_fpr=1. if perfect else 0.),seconds=1.)
   (f/'metrics.json').write_text(json.dumps(report));r=summarize(root,protocol,root/'summary',replicates=20);self.assertEqual(r['status'],'partial');self.assertEqual(r['selected_evaluations'],14)
   effects={x['contrast']:x for x in r['contrasts']}
   self.assertAlmostEqual(effects['gram factorial marginal']['mean_stock_day_ap_delta'],2/3)
   for name in ['lag factorial marginal','moments factorial marginal','gram by lag interaction, averaged over moments']:self.assertAlmostEqual(effects[name]['mean_stock_day_ap_delta'],0.)
   np.testing.assert_allclose(effects['gram factorial marginal']['exploratory_95pct_interval'],[2/3,2/3])
   report['protocol_sha256']='tampered';(f/'metrics.json').write_text(json.dumps(report))
   with self.assertRaises(ValueError):summarize(root,protocol,root/'bad',replicates=2)
