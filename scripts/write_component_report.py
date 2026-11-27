"""Render the final bilingual report only from a fully audited stage013 suite."""
import argparse,json
from pathlib import Path

def write(summary,audit,mac,cpu,output):
 r=json.loads(summary.read_text());a=json.loads(audit.read_text());m=json.loads(mac.read_text());c=json.loads(cpu.read_text())
 if r['status']!='complete' or not a['passed'] or not a['complete_suite'] or not all(x['passed'] and x['complete'] and x['selected_evaluations']==420 for x in [m,c]):raise ValueError('Complete matrix and both actual-model reload gates required')
 if a['fold_seed_runs']!=30 or r['selected_evaluations']!=420:raise ValueError('Incomplete evaluation count')
 by={(x['regime'],x['method']):x for x in r['summary']};con={(x['regime'],x['contrast']):x for x in r['contrasts']};methods=[x['method'] for x in r['summary'] if x['regime']=='date']
 def val(reg,method):
  x=by[(reg,method)];return f"{x['mean_stock_day_ap']:.4f} ± {x['seed_sd']:.4f}"
 def interval(x):return f"{x['mean_stock_day_ap_delta']:+.4f} [{x['exploratory_95pct_interval'][0]:+.4f}, {x['exploratory_95pct_interval'][1]:+.4f}]"
 lines=['# Stage013 verified components and same-cohort comparisons','',
 'Thirty fold-seed runs and420selected evaluations completed through CQ. Every selected model, validation trial, score, threshold, source partition and failure record is archived. Independent split/normalizer/selection/metric audits and actual-model reloads in both CQCPU and Mac are required gates for this report.',
 '', '本轮完成30组训练、420项同数据方法评估及两个环境的真实模型重载；工程资格模型未计入金融结果。',
 '', '## Data and protocol','',
 'Twelve new source dates × five stocks yield60complete stock-days,4,712,637independently replayed records and6,000matched reference snapshots. The frozen passive generator yields69,642windows,3,405positive policy labels and3,519benign controls;1,335invalid source windows and88marketable overlays are excluded, and36observational collisions remain recorded. Training/validation/test windows:14,449/14,157/41,036. Source dates across stages total27; the present test evidence contains only six distinct dates and30stock-days. Dates may remain serially dependent.',
 '', 'All methods use identical registered source IDs,6000training windows per fold-seed, validation-only model/threshold selection and six trials. Combined folds exclude both test and separate validation stocks from training. A shared frozen compactTransformerAE feeds the two cascades and sharedBCE. The price-aligned cascade is an external adaptation, not an exact original-private-data reproduction. Six trials do not mean equal compute or identical tuning scope.',
 '', '## Complete performance','',
 'Primary metric: macro stock-day average precision. ± denotes training-seed SD, not uncertainty over independent market samples. Fold-pooled AP and trapezoidal PR AUC are separately retained in the detailed CSV.',
 '', '| Method | Unseen dates AP ± seed SD | Unseen dates and stocks AP ± seed SD |','|---|---:|---:|']
 for method in methods:lines.append(f'|{method}|{val("date",method)}|{val("combined",method)}|')
 lines+=['','## Registered component contrasts','','Intervals below are exploratory95%date/stock bootstrap intervals after averaging training seeds; they are not multiplicity adjusted.','', '| Contrast | Unseen dates ΔAP [interval] | Dates + stocks ΔAP [interval] |','|---|---:|---:|']
 comparisons=['hgb_all minus hgb_base','hgb_all minus hgb_perlevel','hgb_all minus hgb_moments','hgb_moments minus hgb_perlevel','gram factorial marginal','lag factorial marginal','moments factorial marginal','gram by lag interaction, averaged over moments','mlp_all minus hgb_all','shared_bce minus cascade_ocsvm','cascade_ocsvm minus cascade_no_scl']
 for label in comparisons:lines.append('|'+label+'|'+interval(con[('date',label)])+'|'+interval(con[('combined',label)])+'|')
 lines+=['', 'Moments88 contains80per-level coordinates and8pooled synchrony/breadth coordinates. The pureperlevel80 control is distinct. Gram100 and lag300 contain both same-level and cross-level terms; these family contrasts do not prove that individual off-diagonal terms are necessary. The factorial averages each family addition across all four settings of the other two families.',
 '', '## Alarm quality and cost','','The threshold is selected from pooled validation negatives. A1%overall target is not a1%conditional benign-control target. Rates below are macro averages of fold/seed rates against generated policy labels; background intent is not adjudicated.',
 '', '| Method | Date benign FPR / overall FPR / recall | Combined benign FPR / overall FPR / recall |','|---|---:|---:|']
 for method in ['hgb_base','hgb_perlevel','hgb_moments','hgb_all','mlp_all','cascade_ocsvm','shared_bce']:
  cells=[]
  for regime in ['date','combined']:
   x=by[(regime,method)];cells.append(' / '.join(f'{100*x[k]:.2f}%' for k in ['benign_fpr','test_fpr','recall']))
  lines.append('|'+method+'|'+'|'.join(cells)+'|')
 lines+=['', 'Per-stock/day/style diagnostics retain all4,200group rows. The detailed420row table includes actual method/worker time, resource peaks, input dimensions, selected configurations and environment versions. The first cascade includes sharedAE fitting/encoding cost; no-SCL and sharedBCE reuse it. standalone_pipeline_seconds adds that cost for the latter two; worker time is summed only once per run.',
 '', '## Actual-model portability','','| Reload environment | Runs / evaluations | Maximum absolute score error | Threshold flips |','|---|---:|---:|---:|']
 for label,x in [('CQ CPU',c),('Mac ARM64',m)]:lines.append(f"|{label}|{x['fold_seed_runs']} / {x['selected_evaluations']}|{x['max_absolute_score_error']:.12g}|{x['threshold_flips']}|")
 lines+=['', 'Every feature and frozen embedding hash matches. The preregistered numerical contract uses float64canonical inference, quantized features/embeddings, HGBscore tolerance1e-12 and dense/OC-SVM tolerance1e-7, with zero threshold flips required. Original trusted native checkpoints and explicit numerical exports are both retained. This establishes empirical compatibility for these archived models/inputs/environments, not a universal cross-version guarantee. The stage012CPUfailure is unchanged and remains evidence.',
 '', '## Interpretation and limits','']
 for regime in ['date','combined']:
  x=con[(regime,'hgb_all minus hgb_moments')];lo=x['exploratory_95pct_interval'][0]
  lines.append(f"Primary contrast, {regime}: {interval(x)}; positive in{x['positive_groups']}/{x['stock_days']}seed-averaged stock-days. "+('The exploratory interval is positive.' if lo>0 else 'The interval does not establish a stable positive incremental gain over Moments88.'))
 lines+=['', 'The same-input BCE/cascade comparison still differs in optimization objective and search allocation. High performance on injected policies does not validate real manipulator intent or an endogenous market response. One market, six testdates, fixed generator family, missing authoritative labels and unexecuted recent published baselines remain substantive CCF A-quality gaps. No result here is directly compared numerically with the [original paper0.675](https://arxiv.org/html/2508.17086v2).',
 '', '## Artifacts','',
 '- Protocol: configs/013-preregistered.json and paper/013-protocol.md; execution: docs/reproduce-013.md.',
 '- Data: results/cq-013/j-1128-e7a9cf/benchmark and docs/dataset-013.md; sources remain in the four acquisition jobs.',
 '- Primary CQ job map: cq/013-primary-jobs.json; every original model and prediction is in its job/batch folder.',
 '- Aggregates, paired contrasts, detailed/group tables and scientific figures: results/reports/013-complete/.',
 '- Full independent audit and reload aggregates: results/engineering/components-013/.',
 '- Fidelity and subsequent data leads: paper/013-fidelity-and-data-leads.md. No proposed dataset or unexecuted baseline is counted as evidence.',
 '', '中文结论：组件消融、更多独立日期、同数据级联/直接监督/HGB比较和真实模型跨环境重载已完整执行并核验。具体收益与负结果以上表为准；完整特征若未稳定优于含跨档汇总的统计特征，就不能宣称复杂组件创新成立。当前证据仍不足以宣称真实操纵识别、原论文可比超越或CCF A达标。']
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text('\n'.join(lines)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['summary','audit','mac','cpu','output']:p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();write(a.summary,a.audit,a.mac,a.cpu,a.output)
