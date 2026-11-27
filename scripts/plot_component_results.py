"""Static paper figure from independently audited stage013 aggregate evidence."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(report, output):
    data = json.loads(report.read_text())
    if data['status'] != 'complete':
        raise ValueError('Final paper figure requires the complete registered suite')
    methods = ['hgb_base','hgb_gram','hgb_lag','hgb_perlevel','hgb_moments','hgb_gram_lag','hgb_gram_moments','hgb_lag_moments','hgb_all','mlp_base','mlp_all','cascade_ocsvm','cascade_no_scl','shared_bce']
    labels = ['HGB base','+ Gram','+ Lag','+ Per-level80','+ Moments88','+ Gram/Lag','+ Gram/Moments','+ Lag/Moments','+ All488','MLP base','MLP All488','Cascade OC-SVM','Cascade no SCL','Shared BCE']
    fig, axes = plt.subplots(1, 2, figsize=(12, 7), sharey=True, layout='constrained')
    colors = ['#187c80' if m == 'hgb_all' else '#718096' if m.startswith('hgb') else '#526d9c' for m in methods]
    for ax, regime, title in zip(axes, ['date', 'combined'], ['Held-out dates', 'Held-out dates and stocks']):
        rr = {r['method']: r for r in data['summary'] if r['regime'] == regime}
        values = [rr[m]['mean_stock_day_ap'] for m in methods]
        error = [rr[m]['seed_sd'] or 0 for m in methods]
        y = np.arange(len(methods))
        ax.barh(y, values, xerr=error, color=colors, capsize=2, alpha=.9)
        ax.set_yticks(y, labels); ax.set_xlim(0, 1); ax.set_title(title)
        ax.set_xlabel('Macro stock-day average precision')
        ax.grid(axis='x', alpha=.2); ax.set_axisbelow(True)
        for i, value in enumerate(values):
            ax.text(min(value + error[i] + .012, .94), i, f'{value:.3f}', va='center', fontsize=8)
    axes[0].invert_yaxis()
    fig.suptitle('Component ablations and common-cohort pipeline comparison\nFive seeds; error bars: seed SD; semi-synthetic policy labels', fontsize=12)
    output.parent.mkdir(parents=True, exist_ok=True)
    for ext in ['png', 'pdf', 'svg']:
        fig.savefig(output.with_suffix('.' + ext), dpi=220)
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); plot(a.report, a.output)
