"""Complete stage013 paired metrics and registered factorial contrasts."""
import argparse,json
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score

def summarize(root,protocol,output,replicates=2000):
 cfg=json.loads(protocol.read_text());records=[];seen=set()
 for p in sorted(root.glob('**/metrics.json')):
  r=json.loads(p.read_text())
  if r.get('evidence_class')!='stage013_frozen_semisynthetic':continue
  key=(r['fold'],r['seed'])
  if key in seen or set(r['methods'])!=set(cfg['methods']):raise ValueError('Duplicate/incomplete runs')
  seen.add(key)
  for method,item in r['methods'].items():
   pred=np.load(p.parent/(method+'-predictions.npz'));groups={}
   for stock,date in sorted(set(zip(pred['stock'],pred['date']))):
    mask=(pred['stock']==stock)&(pred['date']==date)
    if len(set(pred['y'][mask]))!=2:raise ValueError('One-class stock-day')
    groups[stock+'|'+date]=float(average_precision_score(pred['y'][mask],pred['score'][mask]))
   benign=np.char.startswith(pred['kind'],'benign_');background=pred['kind']=='background';threshold=item['selection']['threshold']
   records.append(dict(fold=r['fold'],regime=r['fold'].split('-')[0],seed=r['seed'],method=method,clusters=groups,metrics=item['metrics'],benign_fpr=float((pred['score'][benign]>threshold).mean()),background_fpr=float((pred['score'][background]>threshold).mean()),seconds=item['seconds']))
 expected={(f,s) for f in ['date']+['combined-'+s for s in cfg['stocks']] for s in cfg['seeds']};summary=[];contrasts=[]
 pairs=[('hgb_all',x) for x in ['hgb_base','hgb_perlevel','hgb_moments','hgb_gram_lag','hgb_gram_moments','hgb_lag_moments']]+[('hgb_moments','hgb_perlevel'),('mlp_all','hgb_all'),('mlp_base','cascade_ocsvm'),('shared_bce','cascade_ocsvm'),('cascade_ocsvm','cascade_no_scl'),('shared_bce','cascade_no_scl')]
 def name(parts):return 'hgb_'+('_'.join(parts) if parts else 'base') if len(parts)<3 else 'hgb_all'
 effects={a+' factorial marginal':[] for a in ['gram','lag','moments']}
 blocks=['gram','lag','moments']
 for a in blocks:
  rest=[b for b in blocks if b!=a]
  for mask in range(4):
   without=[b for j,b in enumerate(rest) if mask&(1<<j)];with_a=[b for b in blocks if b in without+[a]]
   effects[a+' factorial marginal'].append((name(with_a),name(without),.25))
 for regime in ['date','combined']:
  subset=[r for r in records if r['regime']==regime]
  if not subset:continue
  by={m:{(r['fold'],r['seed']):r for r in subset if r['method']==m} for m in cfg['methods']}
  for m in cfg['methods']:
   rr=list(by[m].values());seedmeans=[np.mean([np.mean(list(r['clusters'].values())) for r in rr if r['seed']==s]) for s in sorted(set(r['seed'] for r in rr))]
   summary.append(dict(regime=regime,method=m,fold_seeds=len(rr),mean_stock_day_ap=float(np.mean(seedmeans)),seed_sd=float(np.std(seedmeans,ddof=1)) if len(seedmeans)>1 else None,mean_fold_pooled_ap=float(np.mean([r['metrics']['ap'] for r in rr])),benign_fpr=float(np.mean([r['benign_fpr'] for r in rr])),background_fpr=float(np.mean([r['background_fpr'] for r in rr])),test_fpr=float(np.mean([r['metrics']['test_fpr'] for r in rr])),recall=float(np.mean([r['metrics']['recall_at_validation_1pct_fpr'] for r in rr])),mean_seconds=float(np.mean([r['seconds'] for r in rr]))))
  todo={a+' minus '+b:[(a,b,1.)] for a,b in pairs};todo.update(effects)
  todo['gram by lag interaction, averaged over moments']=[('hgb_gram_lag','hgb_gram',.5),('hgb_lag','hgb_base',-.5),('hgb_all','hgb_gram_moments',.5),('hgb_lag_moments','hgb_moments',-.5)]
  for label,terms in todo.items():
   accum={}
   for a,b,weight in terms:
    if by[a].keys()!=by[b].keys():raise ValueError('Unpaired comparison')
    for key,ra in by[a].items():
     for group,v in ra['clusters'].items():accum[(key,group)]=accum.get((key,group),0.)+weight*(v-by[b][key]['clusters'][group])
   grouped={}
   for (key,g),v in accum.items():grouped.setdefault(g,[]).append(v)
   means={g:float(np.mean(v)) for g,v in grouped.items()};dates=sorted({g.split('|')[1] for g in means});rng=np.random.default_rng(17090);boot=[]
   for _ in range(replicates):
    draw=[]
    for d in rng.choice(dates,len(dates),replace=True):
     groups=[g for g in means if g.endswith('|'+d)];draw.extend(means[g] for g in rng.choice(groups,len(groups),replace=True))
    boot.append(np.mean(draw))
   contrasts.append(dict(regime=regime,contrast=label,mean_stock_day_ap_delta=float(np.mean(list(means.values()))),exploratory_95pct_interval=np.quantile(boot,[.025,.975]).tolist(),test_dates=len(dates),stock_days=len(means),positive_groups=sum(v>0 for v in means.values()),stock_day_deltas=means))
 report=dict(status='complete' if seen==expected else 'partial',fold_seed_runs=len(seen),selected_evaluations=len(records),expected=cfg['expected_selected_evaluations'],missing=sorted(expected-seen),summary=summary,contrasts=contrasts,records=records,scope='Six new testdates/one market/semi-synthetic policy labels. Paired seed-averaged exploratory date/stock intervals; no multiplicity adjustment or real-intent/original-paper claim. Equal validation trials are not equal pipeline compute.')
 output.mkdir(parents=True,exist_ok=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');lines=['# Stage013 component and pipeline results','',f"Status: {report['status']}; {len(seen)}/30 runs; {len(records)}/{report['expected']} evaluations.",'','| Regime | Method | Macro AP | Seed SD | Benign FPR | Recall |','|---|---|---:|---:|---:|---:|']
 for x in summary:lines.append(f"|{x['regime']}|{x['method']}|{x['mean_stock_day_ap']:.4f}|{x['seed_sd'] if x['seed_sd'] is not None else 'NA'}|{x['benign_fpr']:.4f}|{x['recall']:.4f}|")
 lines+=['','中文结论：以上结果仅限固定新日期半合成协议；组件收益、同数据级联对照、数值核验和负结果须共同解释，不能直接等同于真实操纵检测或CCF A达标。'];(output/'report.md').write_text('\n'.join(lines)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['root','protocol','output']:p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();r=summarize(a.root,a.protocol,a.output);print(r['status'],r['fold_seed_runs'])
