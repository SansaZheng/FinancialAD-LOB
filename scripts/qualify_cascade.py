"""Bounded CQ CPU/GPU qualification with generated engineering-only fixtures."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import time
import numpy as np
import torch
from tests.test_cascade import fixture
from lobbench.cascade_run import run

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--protocol',type=Path,default=Path('configs/010-preregistered.json'));a=p.parse_args();config=json.loads(a.protocol.read_text())
    out=Path(os.environ['CQ_OUTPUT_DIR']);out.mkdir(exist_ok=True,parents=True)
    started=time.monotonic();dataset=out/'fixture.npz';np.savez_compressed(dataset,**fixture(20,depth_resolved=config.get('feature_schema')=='depth-resolved-v2'))
    if a.device=='cuda':
        if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
        print(torch.cuda.get_device_name(0),flush=True)
        from lobbench.cascade import jfds_autoencoder,reconstruct,Fusion,paper_contrastive
        torch.set_num_threads(1)
        probe=jfds_autoencoder().cuda();sample=torch.randn(256,25,20,device='cuda')
        (reconstruct(probe,sample)-sample).square().mean().backward()
        del probe,sample
        fusion=Fusion(1400).cuda();sample=torch.randn(256,1400,device='cuda');y=torch.arange(256,device='cuda')%2
        z,rec=fusion(sample);loss=(rec-sample).square().mean()+.1*paper_contrastive(z,y);loss.backward()
        del fusion,sample,y,z,rec,loss
        torch.cuda.synchronize()
    reports=run(dataset,out/'smoke',['date'],[0],1,a.device,engineering=True,protocol=a.protocol)
    assert len(reports)==1 and len(reports[0]['methods'])==len(config['methods'])
    report=dict(passed=True,evidence_class='engineering_only_not_financial_performance',device=a.device,
                torch=torch.__version__,numpy=np.__version__,python=platform.python_version(),
                seconds=time.monotonic()-started,peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                peak_cuda_bytes=torch.cuda.max_memory_allocated() if a.device=='cuda' else 0,
                cuda_devices=[dict(name=torch.cuda.get_device_name(i),total_memory=torch.cuda.get_device_properties(i).total_memory) for i in range(torch.cuda.device_count())],
                cpu_count=os.cpu_count(),system_memory_bytes=os.sysconf('SC_PHYS_PAGES')*os.sysconf('SC_PAGE_SIZE'),
                source_sha256={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['lobbench/cascade.py','lobbench/cascade_run.py','lobbench/semisynthetic.py','lobbench/passive_overlay.py',str(a.protocol)]})
    (out/'cascade-qualification.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'progress.txt').write_text('1/1 complete\n')
    print(json.dumps(report,indent=2))
