"""Create a small execution-only Git tree without changing main/worktree files.

Canonical main retains every archived result. The execution commit has the same
source/config/vendor files and only the explicitly selected result/input prefix.
Its source identity and omissions are recorded; push it to a codex/* branch.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def make(source,keep,receipt,code_only=False):
    env={**os.environ,'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_NOSYSTEM':'1','GIT_TERMINAL_PROMPT':'0'}
    def git(*args,local_env=None):
        return subprocess.check_output(['git',*args],env=local_env or env,text=True).strip()
    source=git('rev-parse',source)
    paths=git('ls-tree','-r','--name-only',source).splitlines()
    prefixes=[keep] if isinstance(keep,str) else (keep or [])
    if (not prefixes and not code_only) or any(not p.startswith('results/') or p.endswith('/') or '..' in p.split('/') for p in prefixes):
        raise ValueError('Keep prefixes must name exact result/input folders')
    for prefix in prefixes:
        if not any(p.startswith(prefix+'/') for p in paths):
            raise ValueError('Untracked or empty keep prefix: '+prefix)
    retained=[p for p in paths if any(p.startswith(prefix+'/') for prefix in prefixes)]
    if not code_only and not any(p.endswith(('/benchmark.npz','/audit.json','/metrics.json','/challenge.npz')) for p in retained):
        raise ValueError('Tracked benchmark, audited source, fitted model or challenge input required')
    removed=[p for p in paths if p.startswith('results/') and p not in retained]
    before=git('write-tree')
    with tempfile.TemporaryDirectory(prefix='financialad-runtime-index-') as temporary:
        isolated={**env,'GIT_INDEX_FILE':str(Path(temporary)/'index')}
        git('read-tree',source,local_env=isolated)
        for start in range(0,len(removed),200):
            git('update-index','--force-remove','--',*removed[start:start+200],local_env=isolated)
        tree=git('write-tree',local_env=isolated)
        commit=git('-c','user.name=Codex','-c','user.email=codex@openai.com','commit-tree',tree,'-p',source,
                   '-m','Execution-only tree: unchanged code plus registered benchmark input',local_env=isolated)
    if git('write-tree')!=before:raise RuntimeError('Main index unexpectedly changed')
    # Compare tree metadata in two bounded reads. Resolving every blob in a
    # separate Git process is unnecessarily slow on a memory-constrained Mac.
    # Deliberately omit -l: requesting blob sizes hydrates a partial clone.
    def blobs(ref):
        result={}
        for entry in git('ls-tree','-r','-z',ref).split('\0'):
            if not entry:continue
            metadata,path=entry.split('\t',1)
            result[path]=metadata.split()[2]
        return result
    excluded=set(removed)
    canonical={p:h for p,h in blobs(source).items() if p not in excluded}
    execution=blobs(commit)
    if canonical!=execution:raise RuntimeError('Execution-tree content differs')
    report=dict(source_commit=source,runtime_commit=commit,runtime_tree=tree,keep_results=keep,
                unchanged_retained_paths=len(canonical),removed_result_paths=removed,
                retained_git_blob_ids=canonical,main_index_unchanged=True,
                note='This trims only an execution commit; canonical main and its complete data/results are preserved')
    receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('removed_result_paths','retained_git_blob_ids')},indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='HEAD');group=p.add_mutually_exclusive_group(required=True);group.add_argument('--keep-results',nargs='+');group.add_argument('--code-only',action='store_true');p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args();make(a.source,a.keep_results,a.receipt,a.code_only)
