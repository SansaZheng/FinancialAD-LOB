"""Combine registered full-day shards and independently replay before labeling."""
import argparse,json,os,tempfile
from pathlib import Path
from scripts.prepare_full_benchmark import prepare

def main(sources,output,protocol):
    if not os.environ.get('CQ_JOB_ID'):raise RuntimeError('CQ required')
    cfg=json.loads(protocol.read_text());dates=sum([cfg[k] for k in ('train_dates','validation_dates','test_dates')],[])
    with tempfile.TemporaryDirectory(prefix='lob-source-links-') as tmp:
        merged=Path(tmp);base=None;parts=[];transfers=[]
        for folder in sources:
            audit=json.loads((folder/'audit.json').read_text())
            if audit['status']!='complete':raise ValueError('Incomplete source')
            if base is None:base=dict(audit)
            for p in audit['partitions']:
                if p['date'] not in dates or p['stock'] not in cfg['stocks']:raise ValueError('Unregistered source')
                for kind in ['raw','book']:
                    target=merged/p[kind+'_file']
                    if target.exists():raise ValueError('Duplicate source')
                    target.symlink_to((folder/p[kind+'_file']).resolve())
                parts.append(p)
            transfers+=audit['transfers']
        if {(p['stock'],p['date']) for p in parts}!={(s,d) for s in cfg['stocks'] for d in dates}:raise ValueError('Missing registered stock-days')
        base.update(partitions=sorted(parts,key=lambda p:(p['stock'],p['date'])),transfers=transfers)
        (merged/'audit.json').write_text(json.dumps(base,indent=2)+'\n')
        prepare(merged,output,generator='passive',registered_dates=dates,seed=cfg['generator_seed'])
        (output/'source-audit.json').write_text((merged/'audit.json').read_text())
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/012-preregistered.json'));a=p.parse_args();main(a.sources,a.output,a.protocol)
