"""Export a figure from checked reports; seed SD is not market uncertainty."""
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot(source,output):
 r=json.loads(source.read_text())
 if r['status']!='complete':raise ValueError('Complete suite required')
 rows={(x['regime'],x['method']):x for x in r['summary']}
 methods=['cascade_ocsvm','l1_cascade_ocsvm','price_cascade_ocsvm','price_no_scl','supervised_logistic','supervised_hgb']
 labels=['Paper-structure adaptation','L1 control','Price-aligned candidate','Without contrastive loss','Logistic regression','Histogram boosting']
 colors=['#b8c3cf','#8394a8','#2464ad','#9ab9d8','#c69a68','#d66c3a']
 fig,axes=plt.subplots(1,2,figsize=(13,4.8),layout='constrained')
 for ax,key,title in zip(axes,['mean_fold_ap','mean_benign_fpr'],['Detection average precision (higher is better)','Benign-control false positives (lower is better)']):
  for j,(m,label,color) in enumerate(zip(methods,labels,colors)):
   x=np.arange(4)+(j-2.5)*.135
   values=[rows[(g,m)][key] for g in ['date','stock','combined','style']]
   errors=[rows[(g,m)]['seed_sd'] for g in ['date','stock','combined','style']] if key=='mean_fold_ap' else None
   ax.bar(x,values,width=.125,label=label,color=color,yerr=errors,capsize=2,error_kw={'linewidth':.8})
  ax.set_xticks(range(4),['Date','Stock','Date + stock','Unseen style']);ax.set_ylim(0,.65 if key=='mean_fold_ap' else .4)
  ax.set_title(title,fontsize=11);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
  ax.spines[['top','right']].set_visible(False)
 handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,frameon=False,fontsize=9)
 fig.suptitle('WSE semi-synthetic benchmark: 5 stocks, 3 fresh dates, 5 training seeds\nAP error bars: seed SD only; no direct comparison with the original paper',fontsize=12)
 output.parent.mkdir(parents=True,exist_ok=True)
 for ext in ['png','pdf','svg']:fig.savefig(output.with_suffix('.'+ext),dpi=160)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plot(a.report,a.output)
