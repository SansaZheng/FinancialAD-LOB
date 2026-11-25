"""Independently recompute saved metrics and verify fixed source-group splits."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score,roc_auc_score,precision_recall_curve,auc
from lobbench.cascade_run import splits


def verify(root,dataset,output,exclude_jobs=(),protocol=Path('configs/010-preregistered.json')):
    source=np.load(dataset,allow_pickle=False)
    data={k:source[k] for k in ('id','y','stock','date','kind','start_ns','end_ns')}
    expected={fold:(tr,va,te) for regime in ('date','stock','combined','style') for fold,tr,va,te in splits(data,regime)}
    source_hash=hashlib.sha256(dataset.read_bytes()).hexdigest()
    methods=json.loads(protocol.read_text())['methods']
    seen=set();checks=[]
    for path in sorted(root.glob('**/metrics.json')):
        if any(job in path.parts for job in exclude_jobs):continue
        record=json.loads(path.read_text())
        if record.get('evidence_class')!='semisynthetic_external_dataset_adaptation':continue
        key=(record['fold'],record['seed'])
        if key in seen:raise ValueError('Duplicate final fold-seed')
        seen.add(key)
        if record['dataset_sha256']!=source_hash or set(record['methods'])!=set(methods) or 'seconds' not in record:
            raise ValueError('Input hash mismatch or incomplete run')
        tr,va,te=expected[record['fold']]
        ids=np.load(path.parent/'split.npz',allow_pickle=False)
        for name,index in [('train',tr),('validation',va),('test',te)]:
            np.testing.assert_array_equal(ids[name+'_ids'],data['id'][index])
        if not set(ids['train_ids']).isdisjoint(ids['test_ids']):raise ValueError('Train/test overlap')
        if len(record['representation']['loss'])!=10:raise ValueError('Incorrect pretraining budget')
        for method,entry in record['methods'].items():
            pred=np.load(path.parent/(method+'-predictions.npz'),allow_pickle=False)
            for name,index in [('id',te),('validation_id',va)]:np.testing.assert_array_equal(pred[name],data['id'][index])
            for name,index in [('y',te),('validation_y',va)]:np.testing.assert_array_equal(pred[name],data['y'][index])
            for name in ('stock','date','kind'):np.testing.assert_array_equal(pred[name],data[name][te])
            score,y=pred['score'],pred['y'];vscore,vy=pred['validation_score'],pred['validation_y']
            if not np.isfinite(score).all() or not np.isfinite(vscore).all():raise ValueError('Nonfinite predictions')
            selection=entry['selection']
            np.testing.assert_allclose(average_precision_score(vy,vscore),selection['validation_ap'],rtol=0,atol=1e-12)
            trials=selection['trials']
            if len(trials)!=6:raise ValueError('Incorrect validation-trial budget')
            selected=max(trials,key=lambda t:t['validation_ap'])
            cfg={k:v for k,v in selected.items() if k not in ('trial','validation_ap')}
            if cfg!=selection['selected']:raise ValueError('Selected trial differs from first validation maximum')
            negatives=np.sort(vscore[vy==0]);threshold=float(negatives[min(len(negatives)-1,int(np.ceil(.99*len(negatives))))])
            if threshold!=selection['threshold']:raise ValueError('Threshold used test information or a different calibration rule')
            precision,recall,_=precision_recall_curve(y,score)
            recomputed=dict(ap=average_precision_score(y,score),auroc=roc_auc_score(y,score),pr_auc_trapezoidal=auc(recall,precision),
                            prevalence=y.mean(),n=len(y),positives=y.sum(),test_fpr=np.mean(score[y==0]>threshold),
                            recall_at_validation_1pct_fpr=np.mean(score[y==1]>threshold))
            for name,value in recomputed.items():np.testing.assert_allclose(value,entry['metrics'][name],rtol=0,atol=1e-10)
            if entry['fusion'] and len(entry['fusion']['loss'])!=10:raise ValueError('Incorrect fusion budget')
        checks.append(dict(fold=record['fold'],seed=record['seed'],methods_checked=len(methods),metrics_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    receipt=dict(passed=True,complete_suite=len(seen)==60,fold_seed_runs=len(seen),selected_method_evaluations=sum(x['methods_checked'] for x in checks),
                 dataset_sha256=source_hash,excluded_jobs=list(exclude_jobs),checks=checks,
                 guarantees=['fixed split IDs','identical labels across methods','six validation trials','validation-only threshold',
                             'all saved AP/AUROC/PR AUC/FPR/recall independently recomputed','ten epochs per trained stage'],
                 limitation='Verifies artifact consistency, not the correctness of real manipulation labels or scientific superiority')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='checks'},indent=2))
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--exclude-jobs',nargs='*',default=[]);p.add_argument('--protocol',type=Path,default=Path('configs/010-preregistered.json'));a=p.parse_args();verify(a.root,a.dataset,a.output,a.exclude_jobs,a.protocol)
