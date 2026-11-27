"""Bounded CQ direct-model runtime qualification, never financial evidence."""
import argparse,json,os,resource,time
from pathlib import Path
import numpy as np
import torch
from tests.test_direct import fixture
from lobbench.direct import DirectMLP
from lobbench.direct_run import run

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--device',default='cuda',choices=['cpu','cuda']);a=p.parse_args()
 out=Path(os.environ['CQ_OUTPUT_DIR']);out.mkdir(exist_ok=True,parents=True);start=time.monotonic();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 if a.device=='cuda':
  model=DirectMLP(2113).cuda();x=torch.randn(256,2113,device='cuda');model(x).square().mean().backward();torch.cuda.synchronize();del model,x
 data=out/'fixture.npz';np.savez_compressed(data,**fixture())
 result=run(data,out/'smoke','date','date',0,Path('configs/012-preregistered.json'),a.device,engineering=True)
 report=dict(passed=len(result['methods'])==10,evidence_class='engineering_only',seconds=time.monotonic()-start,peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,peak_cuda_bytes=torch.cuda.max_memory_allocated() if a.device=='cuda' else 0,cuda_devices=[dict(name=torch.cuda.get_device_name(i),memory=torch.cuda.get_device_properties(i).total_memory) for i in range(torch.cuda.device_count())],versions=result['versions'],source_sha256=result['source_sha256'])
 (out/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');(out/'progress.txt').write_text('1/1 complete\n');print(json.dumps(report))
