"""Late-authority-only actual deployment, original0af600s outer ownership."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r,r['path']
def family(ref):
    verify(ref);root=Path(ref['path']).parent;j=read(ref['path']);names=[r['path'] for r in j['files']];assert len(names)==len(set(names))
    assert set(names)|{'index.json'}=={x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
    for r in j['files']:
        rel=Path(r['path']);assert not rel.is_absolute() and '..' not in rel.parts and not(root/rel).is_symlink();verify(dict(r,path=str(root/rel)))
def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv)==2
    authpath=Path(sys.argv[1]).resolve();a=read(authpath);plan=read(HERE/'plan.json')
    assert a['state']=='ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V1' and a['sourceIndex']==row(HERE/'index.json') and a['plan']==row(HERE/'plan.json')
    for k in ['localhostServeAllowed','actualNextGuestAllowed','browserAllowed']:assert a[k] is True
    for k in ['compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed']:assert a[k] is False
    def protect():
        family(a['sourceIndex'])
        for r in plan['protectedInputs']:verify(r)
        for ref in plan['sourceFamilies']:family(ref)
        for k in ['constructionResult','component','componentAudit']:verify(a[k])
    protect();output=Path(plan['outputRoot']);outer=Path(plan['monitorOutputRoot']);assert not output.exists() and not outer.exists();outer.mkdir(mode=0o700)
    spec=importlib.util.spec_from_file_location('genuine_next_wasmtime_outer_monitor',plan['monitor']['path']);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    env={k:os.environ[k] for k in ['HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH=str(Path(plan['node']['path']).parent)+':/usr/bin:/bin',NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1',CI='1')
    terminal=monitor.monitor([plan['node']['path'],str(HERE/'deploy.mjs'),str(authpath)],plan['cwd'],env,outer,600,row(authpath))
    preserved=True
    try:protect()
    except BaseException:preserved=False
    clean=terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['timeout'] and not terminal['forcedCleanup'] and all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
    result=read(output/'result.json') if(output/'result.json').exists() else None
    observation=dict(schemaVersion=1,state='ROOT_NEXT_WASMTIME_DEPLOYMENT_OBSERVATION_V1',rawExitCode=terminal['rawExitCode'],ownedGroupsClean=clean,protectedInputsPreserved=preserved,terminal=row(outer/'terminal.json'),result=row(output/'result.json') if result else None,passed=bool(terminal['rawExitCode']==0 and clean and preserved and result and result['passed']),adoption=False)
    (outer/'observation.json').write_text(json.dumps(observation,indent=2)+'\n');print(json.dumps(observation),flush=True);raise SystemExit(0 if observation['passed'] else 1)
if __name__=='__main__':main()
