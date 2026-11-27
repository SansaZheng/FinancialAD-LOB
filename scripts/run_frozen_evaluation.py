"""CQ output-preserving wrapper: backend completion is not scientific success.

Even a failed parity audit writes diagnostic artifacts. Inspect success AND the
complete report and independent verification before interpreting any score.
"""
import argparse,json,traceback,datetime
from pathlib import Path
from scripts.evaluate_lifetime_challenge import evaluate
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ['root','challenge','output','protocol']:p.add_argument('--'+k,type=Path,required=True)
 p.add_argument('--device',choices=['cpu','cuda'],required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 try:
  report=evaluate(a.root,a.challenge,a.output,a.protocol,device=a.device)
  state=dict(finished=True,success=report['status']=='complete',scientific_status=report['status'])
 except Exception:
  error=traceback.format_exc();print(error,flush=True);(a.output/'failure.log').write_text(error)
  state=dict(finished=True,success=False,scientific_status='failed',error=error)
 state['timestamp']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (a.output/'execution-status.json').write_text(json.dumps(state,indent=2)+'\n')
 print(json.dumps(state),flush=True)
