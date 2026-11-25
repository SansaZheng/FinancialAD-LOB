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
    p=argparse.ArgumentParser();p.add_argument('--device',choices=['cpu','cuda'],default='cpu');a=p.parse_args()
    out=Path(os.environ['CQ_OUTPUT_DIR']);out.mkdir(exist_ok=True,parents=True)
    started=time.monotonic();dataset=out/'fixture.npz';np.savez_compressed(dataset,**fixture(20))
    if a.device=='cuda':
        if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
        print(torch.cuda.get_device_name(0),flush=True)
    reports=run(dataset,out/'smoke',['date'],[0],1,a.device,engineering=True)
    assert len(reports)==1 and len(reports[0]['methods'])==10
    report=dict(passed=True,evidence_class='engineering_only_not_financial_performance',device=a.device,
                torch=torch.__version__,numpy=np.__version__,python=platform.python_version(),
                seconds=time.monotonic()-started,peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                peak_cuda_bytes=torch.cuda.max_memory_allocated() if a.device=='cuda' else 0,
                source_sha256={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['lobbench/cascade.py','lobbench/cascade_run.py','lobbench/semisynthetic.py']})
    (out/'cascade-qualification.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'progress.txt').write_text('1/1 complete\n')
    print(json.dumps(report,indent=2))
