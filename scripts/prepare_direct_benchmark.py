"""Combine registered full-day shards and independently replay before labeling."""
import argparse,hashlib,json,os,tempfile
from pathlib import Path
from scripts.prepare_full_benchmark import prepare

def main(sources,output,protocol):
    if not os.environ.get('CQ_JOB_ID'):raise RuntimeError('CQ required')
    cfg=json.loads(protocol.read_text());dates=sum([cfg[k] for k in ('train_dates','validation_dates','test_dates')],[])
    with tempfile.TemporaryDirectory(prefix='lob-source-links-') as tmp:
        merged=Path(tmp);base=None;parts=[];transfers=[];shards=[]
        for folder in sources:
            audit=json.loads((folder/'audit.json').read_text())
            if audit['status']!='complete':raise ValueError('Incomplete source')
            shards.append(dict(folder=str(folder),audit_sha256=hashlib.sha256((folder/'audit.json').read_bytes()).hexdigest(),cq_job=audit.get('cq_job'),partitions=len(audit['partitions'])))
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
        base.update(cq_job=os.environ['CQ_JOB_ID'],source_cq_jobs=[s['cq_job'] for s in shards],partitions=sorted(parts,key=lambda p:(p['stock'],p['date'])),transfers=transfers)
        (merged/'audit.json').write_text(json.dumps(base,indent=2)+'\n')
        prepare(merged,output,generator='passive',registered_dates=dates,seed=cfg['generator_seed'])
        (output/'source-audit.json').write_text((merged/'audit.json').read_text())
        (output/'source-shards.json').write_text(json.dumps(dict(shards=shards,scope='Merged audit creator is this benchmark job; original source job IDs and audit hashes retained separately'),indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/012-preregistered.json'));a=p.parse_args();main(a.sources,a.output,a.protocol)
