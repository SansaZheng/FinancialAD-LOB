"""Independently audit frozen-model challenge artifacts and recompute metrics."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(primary_root, challenge, scores, protocol, output, engineering=False):
    cfg = json.loads(protocol.read_text())
    data = np.load(challenge, allow_pickle=False)
    lookup = {v: i for i, v in enumerate(data['id'])}
    assert len(lookup) == len(data['id'])
    cls = 'engineering_only' if engineering else 'stage012_frozen_semisynthetic'
    primary = {}
    for p in primary_root.glob('**/metrics.json'):
        r = json.loads(p.read_text())
        if r.get('evidence_class') != cls:
            continue
        key = (r['fold'], r['seed'])
        assert key not in primary, 'Duplicate primary run'
        primary[key] = (p, r)
    checked = {}
    for p in sorted(scores.glob('**/challenge-run.json')):
        r = json.loads(p.read_text()); key = (r['fold'], r['seed'])
        assert key not in checked, 'Duplicate challenge run'
        source, original = primary[key]
        assert r['no_refitting'] and r['primary_metrics_sha256'] == sha(source)
        assert r['challenge_sha256'] == sha(challenge)
        assert set(r['methods']) == set(cfg['methods'])
        mask = np.ones(len(data['y']), bool) if key[0] == 'date' else data['stock'] == key[0].split('-', 1)[1]
        rows = np.flatnonzero(mask)
        for method, item in r['methods'].items():
            a = np.load(p.parent / (method + '-predictions.npz'))
            for name in ['id', 'y', 'stock', 'date', 'kind']:
                np.testing.assert_array_equal(a[name], data[name][rows])
            b = np.load(source.parent / (method + '-predictions.npz'))
            ix = {v: i for i, v in enumerate(b['id'])}
            np.testing.assert_array_equal(a['primary_score'], b['score'][[ix[v] for v in a['id']]])
            assert np.isfinite(a['score']).all()
            threshold = original['methods'][method]['selection']['threshold']
            assert item['validation_threshold'] == threshold
            model = source.parent / (method + ('.pt' if 'mlp' in method else '.joblib'))
            assert item['model_sha256'] == sha(model)
            benign = np.char.startswith(a['kind'], 'benign_')
            unchanged = a['kind'] != 'benign_wave'
            np.testing.assert_allclose(a['score'][unchanged], a['primary_score'][unchanged], rtol=1e-4, atol=1e-4)
            values = {
                'primary_matched_ap': average_precision_score(a['y'], a['primary_score']),
                'challenge_ap': average_precision_score(a['y'], a['score']),
                'primary_benign_fpr': np.mean(a['primary_score'][benign] > threshold),
                'challenge_benign_fpr': np.mean(a['score'][benign] > threshold),
                'max_unchanged_score_error': np.abs(a['score'][unchanged] - a['primary_score'][unchanged]).max(),
                'unchanged_threshold_flips': np.sum((a['score'][unchanged] > threshold) != (a['primary_score'][unchanged] > threshold)),
            }
            for name, value in values.items():
                np.testing.assert_allclose(value, item[name], rtol=0, atol=1e-12)
            groups = set(zip(a['stock'], a['date']))
            assert set(item['groups']) == {s + '|' + d for s, d in groups}
            for stock, date in groups:
                m = (a['stock'] == stock) & (a['date'] == date)
                for label, field in [('primary_ap', 'primary_score'), ('challenge_ap', 'score')]:
                    np.testing.assert_allclose(average_precision_score(a['y'][m], a[field][m]), item['groups'][stock + '|' + date][label], rtol=0, atol=1e-12)
        checked[key] = r
    assert checked, 'No challenge results'
    report = json.loads((scores / 'report.json').read_text())
    assert report['fold_seeds'] == len(checked)
    summary_keys = [(row['regime'], row['method']) for row in report['summary']]
    expected_summary = {(key[0].split('-')[0], method) for key in checked for method in cfg['methods']}
    assert len(summary_keys) == len(set(summary_keys)) and set(summary_keys) == expected_summary
    for row in report['summary']:
        rr = [r['methods'][row['method']] for key, r in checked.items() if key[0].split('-')[0] == row['regime']]
        assert row['fold_seeds'] == len(rr)
        for label in ['primary', 'challenge']:
            macro = np.mean([np.mean([g[label + '_ap'] for g in r['groups'].values()]) for r in rr])
            np.testing.assert_allclose(row[label + '_macro_ap'], macro, rtol=0, atol=1e-12)
            np.testing.assert_allclose(row[label + '_benign_fpr'], np.mean([r[label + '_benign_fpr'] for r in rr]), rtol=0, atol=1e-12)
    expected = {(f, s) for f in ['date'] + ['combined-' + x for x in cfg['stocks']] for s in cfg['seeds']}
    assert set(checked) <= expected
    complete = set(checked) == expected
    assert report['status'] == ('engineering_only' if engineering else ('complete' if complete else 'partial'))
    result = dict(passed=True, complete_suite=complete, fold_seeds=len(checked), selected_evaluations=len(checked)*len(cfg['methods']), challenge_sha256=sha(challenge), unchanged_threshold_flips=sum(m['unchanged_threshold_flips'] for r in checked.values() for m in r['methods'].values()), scope='Independent artifact and metric consistency; model execution parity is checked on unchanged rows, not a proof of real manipulation intent')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['primary-root', 'challenge', 'scores', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--protocol', type=Path, default=Path('configs/012-preregistered.json'))
    a = p.parse_args()
    print(json.dumps(verify(a.primary_root, a.challenge, a.scores, a.protocol, a.output), indent=2))
