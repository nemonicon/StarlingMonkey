"""Late-authority-only actual deployment, original0af600s outer ownership."""
import hashlib
import importlib.util
import json
import os
import re
import shutil
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
def require_capacity(free):
    assert type(free) is int and free>=1073741824,'Root conservative1GiB start guard'
def derive_invocation(authority,plan,here,authority_path):
    run_id=authority['runId'];assert isinstance(run_id,str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',run_id)
    assert all(key not in authority for key in ['outputRoot','monitorOutputRoot','argv'])
    assert plan['outputPrefix']=='/private/tmp/starling-node-compat/next-action-wire-native-v1'
    output=Path(plan['outputPrefix']+'-'+run_id)
    return output,Path(str(output)+'-external-root'),[plan['node']['path'],str(here/'deploy.mjs'),str(authority_path)]
def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv)==2
    authpath=Path(sys.argv[1]).resolve();a=read(authpath);plan=read(HERE/'plan.json')
    assert a['state']=='ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2' and a['sourceIndex']==row(HERE/'index.json') and a['plan']==row(HERE/'plan.json')
    for k in ['localhostServeAllowed','actualNextGuestAllowed','wireClientAllowed']:assert a[k] is True
    assert a['browserAllowed'] is False
    for k in ['compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed']:assert a[k] is False
    run_id=a['runId'];output,outer,argv=derive_invocation(a,plan,HERE,authpath)
    for key in ['constructionCallerIndex','inputSourceIndex','inputEntry']:
        ref=a[key];assert isinstance(ref,dict) and set(ref)=={'path','sha256','bytes'}
        path=Path(ref['path']);assert path.is_absolute() and str(path.resolve())==str(path)
        if key!='inputEntry':assert path.name=='index.json'
    def protect():
        family(a['sourceIndex']);family(a['constructionCallerIndex']);family(a['inputSourceIndex']);verify(a['inputEntry'])
        entry_base=Path(a['inputSourceIndex']['path']).parent;entry_relative=Path(a['inputEntry']['path']).relative_to(entry_base).as_posix()
        entry=next(r for r in read(a['inputSourceIndex']['path'])['files'] if r['path']==entry_relative)
        assert dict(entry,path=str(entry_base/entry_relative))==a['inputEntry']
        for r in plan['protectedInputs']:verify(r)
        for ref in plan['sourceFamilies']:family(ref)
        for k in ['constructionResult','component','componentAudit']:verify(a[k])
    protect();assert not output.exists() and not output.is_symlink() and not outer.exists() and not outer.is_symlink();free=shutil.disk_usage(output.parent).free;require_capacity(free);outer.mkdir(mode=0o700)
    spec=importlib.util.spec_from_file_location('genuine_next_wasmtime_outer_monitor',plan['monitor']['path']);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    env={k:os.environ[k] for k in ['HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH=str(Path(plan['node']['path']).parent)+':/usr/bin:/bin',NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1',CI='1')
    terminal=monitor.monitor(argv,plan['cwd'],env,outer,600,row(authpath))
    preserved=True
    try:protect()
    except BaseException:preserved=False
    clean=terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['timeout'] and not terminal['forcedCleanup'] and all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
    result=read(output/'result.json') if(output/'result.json').exists() else None
    observation=dict(schemaVersion=1,state='ROOT_NEXT_WASMTIME_DEPLOYMENT_OBSERVATION_V2',runId=run_id,outputRoot=str(output),rawExitCode=terminal['rawExitCode'],ownedGroupsClean=clean,protectedInputsPreserved=preserved,terminal=row(outer/'terminal.json'),result=row(output/'result.json') if result else None,passed=bool(terminal['rawExitCode']==0 and clean and preserved and result and result['passed']),adoption=False,fullNextAcceptance=False,freeBytesAtAdmission=free,minimumFreeBytes=1073741824)
    (outer/'observation.json').write_text(json.dumps(observation,indent=2)+'\n');print(json.dumps(observation),flush=True);raise SystemExit(0 if observation['passed'] else 1)
if __name__=='__main__':main()
