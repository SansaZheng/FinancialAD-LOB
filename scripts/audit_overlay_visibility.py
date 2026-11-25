"""Audit the known visible-support limitation without fitting any detector."""
import io
import json
from pathlib import Path
import subprocess
import numpy as np


def main():
    base=Path('results/cq-010/j-1125-5d4369/full-sessions')
    ledger=json.loads(Path('results/cq-010/j-1125-344a3f/benchmark/injection-ledger.json').read_text())
    audit=json.loads((base/'audit.json').read_text());rows=[]
    for p in audit['partitions']:
        path=base/p['book_file']
        # Verified raw working copies may be removed after GitHub archival.
        payload=path.read_bytes() if path.exists() else subprocess.check_output(['git','show','HEAD:'+str(path)])
        source=np.load(io.BytesIO(payload),allow_pickle=False);book=source['x'];indices=source['source_row']
        prefix=p['stock']+'-'+p['date']+'-'
        for event in (e for e in ledger if e['id'].startswith(prefix)):
            row=int(event['id'].rsplit('-',1)[1]);start=int(np.searchsorted(indices,row));assert indices[start]==row
            expected=missing=0;missing_volume_steps=0;passive_missing=0;marketable=0
            for k,price in enumerate(event['prices']):
                for t in range(event['placement_steps'][k],event['withdrawal_steps'][k]):
                    expected+=1
                    if not (book[start+t,event['side'],:,0]==price).any():
                        missing+=1;missing_volume_steps+=event['added_volume'][k]
                        side=event['side'];current=book[start+t]
                        crosses=price>=current[1,0,0] if side==0 else price<=current[0,0,0]
                        in_top=price>=current[0,-1,0] if side==0 else price<=current[1,-1,0]
                        marketable+=int(crosses)
                        passive_missing+=int(in_top and not crosses)
            rows.append(dict(id=event['id'],style=event['style'],expected_active_level_steps=expected,
                             missing_visible_level_steps=missing,missing_share_steps=missing_volume_steps,passive_would_be_visible_steps=passive_missing,marketable_steps=marketable))
    report=dict(evidence_class='generator_fidelity_audit_not_model_performance',injections=len(rows),
                injections_with_visible_support_loss=sum(r['missing_visible_level_steps']>0 for r in rows),
                expected_active_level_steps=sum(r['expected_active_level_steps'] for r in rows),
                missing_visible_level_steps=sum(r['missing_visible_level_steps'] for r in rows),
                injections_with_passive_visible_truncation=sum(r['passive_would_be_visible_steps']>0 for r in rows),
                passive_would_be_visible_steps=sum(r['passive_would_be_visible_steps'] for r in rows),
                injections_with_marketable_orders=sum(r['marketable_steps']>0 for r in rows),
                marketable_steps=sum(r['marketable_steps'] for r in rows),
                interpretation='Overlay volumes exist only at prices in the unmodified visible top-five book. This is not a conservation-respecting replay of inserted orders, and is explicitly not an execution simulator.',
                by_style={style:dict(injections=sum(r['style']==style for r in rows),affected=sum(r['style']==style and r['missing_visible_level_steps']>0 for r in rows)) for style in sorted(set(r['style'] for r in rows))},
                action='Do not alter the frozen benchmark after results; require order-consistent intervention and duration-matched benign controls on untouched dates for a stronger follow-up.',events=rows)
    output=Path('results/engineering/cascade-010/overlay-visibility-audit.json');output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='events'},indent=2))

if __name__=='__main__':main()
