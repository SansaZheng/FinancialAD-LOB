import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from scripts.summarize_cascade import summarize

class ReportingTests(unittest.TestCase):
    def test_paired_constant_gain_and_incomplete_suite(self):
        methods=json.loads(Path('configs/010-preregistered.json').read_text())['methods']
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);dest=root/'date-seed0';dest.mkdir()
            y=np.tile([0,1],4);base=np.ones(8);perfect=y.astype(float)
            stock=np.repeat(['A','A','B','B'],2);date=np.repeat(['d1','d2','d1','d2'],2)
            report=dict(fold='date',seed=0,seconds=1,evidence_class='semisynthetic_external_dataset_adaptation',methods={})
            for method in methods:
                score=base if method=='cascade_ocsvm' else perfect
                np.savez_compressed(dest/(method+'-predictions.npz'),y=y,score=score,stock=stock,date=date,kind=np.where(y,'layered','persistent'))
                report['methods'][method]={'selection':{'threshold':.5},'metrics':{'ap':.5 if method=='cascade_ocsvm' else 1.,'test_fpr':0.,'recall_at_validation_1pct_fpr':1.}}
            (dest/'metrics.json').write_text(json.dumps(report))
            summarize(root,root/'report',replicates=25)
            result=json.loads((root/'report/report.json').read_text())
            self.assertEqual(result['status'],'partial');self.assertEqual(result['expected_fold_seeds'],60)
            contrast=next(x for x in result['paired_stock_day_intervals'] if x['method']=='price_cascade_ocsvm')
            self.assertEqual(contrast['exploratory_95pct_interval'],[.5,.5])
            strong=next(x for x in result['paired_stock_day_intervals'] if x['method']=='price_cascade_ocsvm' and x['reference']=='supervised_hgb')
            self.assertEqual(strong['exploratory_95pct_interval'],[0.,0.])

if __name__=='__main__':unittest.main()
