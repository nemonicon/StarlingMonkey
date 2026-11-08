"""Late Root authority only. Original0af owns the 600s controller and children."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys

HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):
 p=Path(r['path']);assert p.is_absolute()and str(p.resolve())==str(p)and not p.is_symlink()and p.is_file()and p.stat().st_nlink==1
 assert row(p)==r
def family(ref):
 verify(ref);root=Path(ref['path']).parent;rows=read(ref['path'])['files'];names=[r['path']for r in rows];nodes=list(root.rglob('*'))
 assert len(names)==len(set(names))and not any(p.is_symlink()for p in nodes)
 assert all(p.is_file()or p.is_dir()for p in nodes)
 assert set(names)|{'index.json'}=={p.relative_to(root).as_posix()for p in nodes if p.is_file()}
 dirs=set()
 for r in rows:
  q=Path(r['path']);assert not q.is_absolute()and'..'not in q.parts
  dirs.update(x.as_posix()for x in q.parents if x!=Path('.'));verify(dict(r,path=str(root/q)))
 assert dirs=={p.relative_to(root).as_posix()for p in nodes if p.is_dir()}
def derive(a,p):
 assert a['state']=='ROOT_NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_AUTHORIZED_V1'and type(a['schemaVersion'])is int and a['schemaVersion']==1
 assert isinstance(a['runId'],str)and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',a['runId'])
 for k in ['hostOnlyDirectStandaloneAllowed','localhostServeAllowed','browserAllowed','publicRequestCorrelationAllowed']:assert a[k]is True
 for k in ['compilerAllowed','nativeBuildAllowed','engineAllowed','guestAllowed','componentConstructionAllowed','packageInstallAllowed','applicationSourceMutationAllowed','externalDeploymentAllowed','adoptionAllowed']:assert a[k]is False
 assert p['outputPrefix']=='/private/tmp/starling-node-compat/next-pristine-redirect-runtime-v1'and p['outerSeconds']==600 and p['minimumLaunchFreeBytes']==1073741824
 assert not any(k in a for k in ['argv','outputRoot','monitorOutputRoot','environment'])
 output=Path(p['outputPrefix']+'-'+a['runId']);return output,Path(str(output)+'-external-root')
def main():
 assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==2
 p=read(HERE/'plan.json');assert p['prospectiveBindingsPending'] is False,'Root actual app/client/asset/protection bindings pending'
 for key in ['applicationSource','applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentity','applicationRootIdentityEvidence','expectedApplication','clientSource','clientSourceIndex','browserWorker','browserIndex','assetSelection','assetPins','sourceFamilies','protectedInputs','outputPrefix','runId']:assert p[key] is not None,'Missing Root binding:'+key
 authpath=Path(sys.argv[1]).resolve();ref=row(authpath);a=read(authpath)
 assert a['sourceIndex']==row(HERE/'index.json')and a['plan']==row(HERE/'plan.json')
 assert a['runId']==p['runId']
 output,outer=derive(a,p)
 def protect():
  verify(ref);family(a['sourceIndex'])
  for r in p['sourceFamilies']:family(r)
  for r in p['protectedInputs']:verify(r)
 protect();assert not any(x.exists()or x.is_symlink()for x in [output,outer])
 free=shutil.disk_usage(output.parent).free;assert free>=p['minimumLaunchFreeBytes'],'Conservative1GiB start admission, not a continuous floor'
 outer.mkdir(mode=0o700)
 spec=importlib.util.spec_from_file_location('original_direct_standalone_owner',p['monitor']['path']);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
 env={k:os.environ[k]for k in ['HOME','USER','LOGNAME']if k in os.environ};env.update(PATH=str(Path(p['node']['path']).parent)+':/usr/bin:/bin',LANG='C',LC_ALL='C',NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1',CI='1')
 terminal=None;error=None;preserved=False
 try:terminal=monitor.monitor([p['node']['path'],str(HERE/'control.mjs'),str(authpath)],p['cwd'],env,outer,600,ref)
 except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught))
 finally:
  try:protect();preserved=True
  except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught))
 clean=bool(terminal and terminal['parentOwnedGroupGone']and terminal['allObservedOwnedGroupsGone']and not terminal['timeout']and not terminal['forcedCleanup']and all(terminal[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids']))
 result=read(output/'result.json')if(output/'result.json').exists()else None
 obs=dict(schemaVersion=1,state='ROOT_NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_OBSERVATION_V1',runId=a['runId'],rawExitCode=terminal['rawExitCode']if terminal else None,ownedGroupsClean=clean,protectedInputsPreserved=preserved,error=error,freeBytesAtAdmission=free,continuousDiskGuardClaimed=False,terminal=row(outer/'terminal.json')if terminal else None,result=row(output/'result.json')if result else None,passed=bool(terminal and terminal['rawExitCode']==0 and clean and preserved and error is None and result and result['passed']),guestExecuted=False,adoption=False)
 (outer/'observation.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs),flush=True);raise SystemExit(0 if obs['passed']else 1)
if __name__=='__main__':main()
