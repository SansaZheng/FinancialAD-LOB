"""CQ-only synthetic stage013 implementation/device qualification."""
import os,json,time,resource,unittest
from pathlib import Path
import numpy as np,torch
from tests.test_components import fixture
from lobbench.component_run import run
from lobbench.direct import DirectMLP
from lobbench.cascade import jfds_autoencoder,reconstruct
from scripts.reload_components import reload_run
if __name__=='__main__':
 if not os.environ.get('CQ_JOB_ID'):raise RuntimeError('CQ required')
 out=Path(os.environ['CQ_OUTPUT_DIR']);out.mkdir(parents=True,exist_ok=True);start=time.monotonic();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 if not torch.cuda.is_available():raise RuntimeError('CUDA qualification required')
 model=DirectMLP(2113).cuda();model(torch.randn(256,2113,device='cuda')).square().mean().backward();del model
 ae=jfds_autoencoder().cuda();x=torch.randn(256,25,20,device='cuda');reconstruct(ae,x).square().mean().backward();del ae,x;torch.cuda.empty_cache()
 suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_portable');tests=unittest.TextTestRunner(verbosity=1).run(suite)
 if not tests.wasSuccessful():raise RuntimeError('Portable invariants failed')
 dataset=out/'fixture.npz';np.savez_compressed(dataset,**fixture());r=run(dataset,out/'models/date-s0','date','date',0,Path('configs/013-preregistered.json'),device='cuda',engineering=True);audit=reload_run(dataset,out/'models/date-s0');(out/'reload.json').write_text(json.dumps(audit,indent=2)+'\n')
 report=dict(passed=audit['passed'] and len(r['methods'])==14,evidence_class='engineering_only',seconds=time.monotonic()-start,peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,peak_cuda_bytes=torch.cuda.max_memory_allocated(),cuda_devices=[dict(name=torch.cuda.get_device_name(i),memory=torch.cuda.get_device_properties(i).total_memory) for i in range(torch.cuda.device_count())],versions=r['versions'],source_sha256=r['source_sha256'],protocol_sha256=r['protocol_sha256'])
 (out/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');(out/'progress.txt').write_text('1/1 complete\n');print(json.dumps(report),flush=True)
