"""Paired reporting of a frozen suite; seed variation is not market uncertainty."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score


def summarize(root,output,replicates=2000):
    output.mkdir(parents=True,exist_ok=True)
    records=[]
    for path in sorted(root.glob('**/metrics.json')):
        report=json.loads(path.read_text())
        if report.get('evidence_class')!='semisynthetic_external_dataset_adaptation':continue
        regime=report['fold'].split('-')[0]
        for method,item in report['methods'].items():
            pred=np.load(path.parent/(method+'-predictions.npz'),allow_pickle=False)
            benign=np.isin(pred['kind'],['persistent','independent'])
            per_style={}
            for style in ('layered','staggered'):
                ix=(pred['y']==0)|(pred['kind']==style)
                if len(set(pred['y'][ix]))==2:
                    per_style[style]=float(average_precision_score(pred['y'][ix],pred['score'][ix]))
            clusters={}
            for stock,date in sorted(set(zip(pred['stock'],pred['date']))):
                ix=(pred['stock']==stock)&(pred['date']==date)
                if len(set(pred['y'][ix]))==2:
                    clusters[stock+'|'+date]=float(average_precision_score(pred['y'][ix],pred['score'][ix]))
            records.append(dict(regime=regime,fold=report['fold'],seed=report['seed'],method=method,
                                metrics=item['metrics'],clusters=clusters,per_style=per_style,
                                benign_fpr=float(np.mean(pred['score'][benign]>item['selection']['threshold'])) if benign.any() else None,
                                benign_n=int(benign.sum()),prediction_sha256=hashlib.sha256((path.parent/(method+'-predictions.npz')).read_bytes()).hexdigest()))
    summary=[];intervals=[]
    for regime in sorted(set(r['regime'] for r in records)):
        for method in sorted(set(r['method'] for r in records)):
            rr=[r for r in records if r['regime']==regime and r['method']==method]
            if not rr:continue
            seeds=sorted(set(r['seed'] for r in rr))
            seedmeans=[np.mean([r['metrics']['ap'] for r in rr if r['seed']==seed]) for seed in seeds]
            summary.append(dict(regime=regime,method=method,fold_seed_runs=len(rr),seeds=seeds,
                                mean_fold_ap=float(np.mean(seedmeans)),seed_sd=float(np.std(seedmeans,ddof=1)) if len(seeds)>1 else None,
                                mean_test_fpr=float(np.mean([r['metrics']['test_fpr'] for r in rr])),
                                mean_recall_at_validation_1pct_fpr=float(np.mean([r['metrics']['recall_at_validation_1pct_fpr'] for r in rr])),
                                mean_benign_fpr=float(np.mean([r['benign_fpr'] for r in rr if r['benign_fpr'] is not None]))))
        methods=['price_cascade_ocsvm','rank_cascade_ocsvm','price_no_scl','price_no_lob','dynamics_ocsvm','raw_ocsvm']
        base={(r['fold'],r['seed']):r for r in records if r['regime']==regime and r['method']=='cascade_ocsvm'}
        for method in methods:
            delta={}
            for r in records:
                if r['regime']!=regime or r['method']!=method:continue
                b=base[(r['fold'],r['seed'])]
                if r['clusters'].keys()!=b['clusters'].keys():raise ValueError('Unpaired stock-day groups')
                for key,ap in r['clusters'].items():delta.setdefault(key,[]).append(ap-b['clusters'][key])
            # Average paired seeds first; resample observed dates, then stocks within date.
            means={k:np.mean(v) for k,v in delta.items()};dates=sorted(set(k.split('|')[1] for k in means))
            if not means:continue
            rng=np.random.default_rng(17086);boot=[]
            for _ in range(replicates):
                values=[]
                for date in rng.choice(dates,len(dates),replace=True):
                    keys=[k for k in means if k.endswith('|'+date)]
                    values.extend(means[k] for k in rng.choice(keys,len(keys),replace=True))
                boot.append(np.mean(values))
            intervals.append(dict(regime=regime,method=method,reference='cascade_ocsvm',
                                  mean_stock_day_ap_delta=float(np.mean(list(means.values()))),
                                  exploratory_95pct_interval=np.quantile(boot,[.025,.975]).tolist(),
                                  dates=len(dates),stock_days=len(means),bootstrap_replicates=replicates,
                                  limitation='Conditional on observed date' if len(dates)==1 else 'Only three observed dates; not a strong population-level guarantee'))
    report=dict(status='complete',summary=summary,paired_stock_day_intervals=intervals,records=records,
                paper_comparison='WSE adaptation only; not a direct reproduction or numerical comparison to paper 0.675',
                inference='Intervals exploratory, no multiple-comparison correction; five seeds are not five independent market samples')
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Frozen WSE semi-synthetic experiment results','',
           '| Regime | Method | Mean fold AP | Seed SD | Test FPR | Benign FPR |','|---|---|---:|---:|---:|---:|']
    for r in summary:
        sd='n/a' if r['seed_sd'] is None else f"{r['seed_sd']:.4f}"
        lines.append(f"| {r['regime']} | {r['method']} | {r['mean_fold_ap']:.4f} | {sd} | {r['mean_test_fpr']:.4f} | {r['mean_benign_fpr']:.4f} |")
    lines+=['','Paired stock-day intervals, exact split/seed records and prediction hashes are in report.json. These intervals are exploratory with very few independent dates.',
            '', '中文结论：以上仅为固定 WSE 半合成协议上的结果。是否改进须结合配对差值、消融和正常大额流动性对照判断；任何数值超过 0.675 都不能直接证明超过原论文。']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(runs=len(set((r['fold'],r['seed']) for r in records)),summary=summary),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();summarize(a.root,a.output)
