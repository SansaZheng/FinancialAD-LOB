"""Summarize the fixed direct suite with paired stock-day comparisons."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score


def summarize(root,protocol,output,replicates=2000):
 cfg=json.loads(protocol.read_text());records=[];seen=set();ph=hashlib.sha256(protocol.read_bytes()).hexdigest()
 for p in sorted(root.glob('**/metrics.json')):
  r=json.loads(p.read_text())
  if r.get('evidence_class')!='stage012_frozen_semisynthetic':continue
  key=(r['fold'],r['seed'])
  if key in seen or set(r['methods'])!=set(cfg['methods']) or r['protocol_sha256']!=ph:raise ValueError('Duplicate, partial or different protocol')
  seen.add(key);regime=r['fold'].split('-')[0]
  for method,item in r['methods'].items():
   pred=np.load(p.parent/(method+'-predictions.npz'));y,s=pred['y'],pred['score'];clusters={}
   for stock,date in sorted(set(zip(pred['stock'],pred['date']))):
    mask=(pred['stock']==stock)&(pred['date']==date)
    if len(set(y[mask]))!=2:raise ValueError('Missing class in test stock-day')
    clusters[stock+'|'+date]=float(average_precision_score(y[mask],s[mask]))
   rates={}
   for label,mask in [('benign',np.char.startswith(pred['kind'],'benign_')),('background',pred['kind']=='background')]:rates[label+'_fpr']=float(np.mean(s[mask]>item['selection']['threshold'])) if mask.any() else None
   records.append(dict(fold=r['fold'],regime=regime,seed=r['seed'],method=method,clusters=clusters,metrics=item['metrics'],**rates))
 expected={(f,s) for f in ['date']+['combined-'+z for z in cfg['stocks']] for s in cfg['seeds']};summary=[];contrasts=[]
 pairs=[('interaction_mlp_hard',z) for z in ['hgb','hgb_hard','interaction_hgb','interaction_hgb_hard','mlp_hard','interaction_mlp']]
 pairs+=[('interaction_hgb_hard','hgb'),('interaction_hgb','hgb')]+[(m+'_hard',m) for m in ['logistic','hgb','mlp','interaction_hgb']]
 for regime in sorted(set(r['regime'] for r in records)):
  for method in cfg['methods']:
   rr=[r for r in records if r['regime']==regime and r['method']==method]
   if not rr:continue
   sd={s:np.mean([np.mean(list(r['clusters'].values())) for r in rr if r['seed']==s]) for s in sorted(set(r['seed'] for r in rr))}
   summary.append(dict(regime=regime,method=method,fold_seeds=len(rr),mean_stock_day_ap=float(np.mean(list(sd.values()))),seed_sd=float(np.std(list(sd.values()),ddof=1)) if len(sd)>1 else None,mean_fold_pooled_ap=float(np.mean([r['metrics']['ap'] for r in rr])),benign_fpr=float(np.mean([r['benign_fpr'] for r in rr if r['benign_fpr'] is not None])),background_fpr=float(np.mean([r['background_fpr'] for r in rr if r['background_fpr'] is not None])),test_fpr=float(np.mean([r['metrics']['test_fpr'] for r in rr])),recall=float(np.mean([r['metrics']['recall_at_validation_1pct_fpr'] for r in rr]))))
  for method,reference in pairs:
   a={(r['fold'],r['seed']):r for r in records if r['regime']==regime and r['method']==method};b={(r['fold'],r['seed']):r for r in records if r['regime']==regime and r['method']==reference}
   if a.keys()!=b.keys():raise ValueError('Unpaired comparisons')
   delta={}
   for k in a:
    if a[k]['clusters'].keys()!=b[k]['clusters'].keys():raise ValueError('Unpaired test days')
    for group in a[k]['clusters']:delta.setdefault(group,[]).append(a[k]['clusters'][group]-b[k]['clusters'][group])
   means={g:np.mean(v) for g,v in delta.items()};dates=sorted(set(g.split('|')[1] for g in means));rng=np.random.default_rng(17088);boot=[]
   for _ in range(replicates):
    draw=[]
    for d in rng.choice(dates,len(dates),replace=True):
     groups=[g for g in means if g.endswith('|'+d)];draw.extend(means[g] for g in rng.choice(groups,len(groups),replace=True))
    boot.append(np.mean(draw))
   contrasts.append(dict(regime=regime,method=method,reference=reference,mean_stock_day_ap_delta=float(np.mean(list(means.values()))),exploratory_95pct_interval=np.quantile(boot,[.025,.975]).tolist(),dates=len(dates),stock_days=len(means)))
 report=dict(status='complete' if seen==expected else 'partial',fold_seed_runs=len(seen),expected=30,missing=sorted(expected-seen),summary=summary,contrasts=contrasts,records=records,limitation='Only three test dates in one market, semi-synthetic policy labels; exploratory intervals and no multiplicity correction; not original paper comparison')
 output.mkdir(parents=True,exist_ok=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# Direct supervised scores on fresh dates','',f"Status: {report['status']}, {len(seen)}/30 fold-seed runs.",'','| Regime | Method | Macro stock-day AP | Pooled fold AP | Benign FPR | Background FPR | Recall |','|---|---|---:|---:|---:|---:|---:|']
 for r in summary:lines.append(f"| {r['regime']} | {r['method']} | {r['mean_stock_day_ap']:.4f} | {r['mean_fold_pooled_ap']:.4f} | {r['benign_fpr']:.4f} | {r['background_fpr']:.4f} | {r['recall']:.4f} |")
 lines+=['','中文结论：以上为固定新日期半合成协议的结果；须同时比较原始与增强强基线、难负例误报和配对差值，不能直接等同于真实操纵检测或超过原论文。'];(output/'report.md').write_text('\n'.join(lines)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/012-preregistered.json'));p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=summarize(a.root,a.protocol,a.output);print(r['status'],r['fold_seed_runs'])
