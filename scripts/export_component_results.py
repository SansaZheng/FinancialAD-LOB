"""Export a complete independently verified stage013 component suite without mixing cohorts."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def export(root, summary, verification, output, ledger):
    audit = json.loads(verification.read_text())
    report = json.loads(summary.read_text())
    if not audit['passed'] or not audit['complete_suite'] or report['status'] != 'complete':
        raise ValueError('Complete independent verification required')
    grouped = {(r['fold'], r['seed'], r['method']): r for r in report['records']}
    details = []; additions = []
    for p in sorted(root.glob('**/metrics.json')):
        r = json.loads(p.read_text())
        if r.get('evidence_class') != 'stage013_frozen_semisynthetic':
            continue
        for method, item in r['methods'].items():
            group = grouped[(r['fold'], r['seed'], method)]
            values = dict(item['metrics'])
            values.update(macro_stock_day_ap=float(np.mean(list(group['clusters'].values()))), benign_fpr=group['benign_fpr'], background_fpr=group['background_fpr'])
            common = dict(artifact=str(p), cq_job=r['cq_job'], fold=r['fold'], seed=r['seed'], method=method, dataset_sha256=r['dataset_sha256'], protocol_sha256=r['protocol_sha256'], evidence_class=r['evidence_class'])
            for metric, value in values.items():
                additions.append(dict(common, metric=metric, value=value, aggregation='mean of test stock-day AP within fold' if metric == 'macro_stock_day_ap' else 'single fold and training seed'))
            details.append(dict(common, **values, train_windows=r['sizes']['train'], validation_windows=r['sizes']['validation'], test_windows=r['sizes']['test'], threshold=item['selection']['threshold'], selected_configuration=json.dumps(item['selection']['selected'], sort_keys=True), validation_ap=item['selection']['validation_ap'], trials=len(item['selection']['trials']), warning_count=sum(len(t['warnings']) for t in item['selection']['trials']), method_seconds=item['seconds'], shared_ae_seconds=r['representation']['total_seconds'], standalone_pipeline_seconds=item['seconds']+(r['representation']['total_seconds'] if method in ('cascade_no_scl','shared_bce') else 0), worker_seconds=r['seconds'], worker_peak_rss_kib=r['peak_rss_native'], worker_peak_allocated_cuda_bytes=r['peak_cuda_bytes'], device=r['device'], versions=json.dumps(r['versions'], sort_keys=True), training_source_sha256=json.dumps(r['source_sha256'], sort_keys=True)))
    if len(details) != 420 or len(grouped) != 420:
        raise ValueError('Expected420 unique method evaluations')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(details[0])); writer.writeheader(); writer.writerows(details)
    with ledger.open(newline='') as f:
        reader = csv.DictReader(f); fields = reader.fieldnames
        old = [r for r in reader if r['evidence_class'] != 'stage013_frozen_semisynthetic']
    with ledger.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(old + additions)
    return dict(selected_evaluations=len(details), new_metric_rows=len(additions), previous_cohort_rows=len(old))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['root', 'summary', 'verification', 'output', 'ledger']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(export(a.root, a.summary, a.verification, a.output, a.ledger), indent=2))
