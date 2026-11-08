"""Dormant per-arm original0af300s runner; never launches both implicitly."""
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r,r['path']
def family(ref):
    verify(ref);root=Path(ref['path']).parent;index=read(ref['path']);names=[r['path'] for r in index['files']]
    assert len(names)==len(set(names))
    assert set(names)|{'index.json'}=={x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
    for r in index['files']:
        p=Path(r['path']);assert not p.is_absolute() and '..' not in p.parts and not(root/p).is_symlink()
        assert row(root/p)==dict(r,path=str(root/p))
def derive_invocation(authority, plan, here):
    # New local pure selector, not an ownership or embedding API.
    assert authority['state']=='ROOT_NEXT_PUBLIC_CORRELATION_HOST_AUTHORIZED_V1' and authority['arm']=='stock'
    run_id=authority['runId']
    assert isinstance(run_id,str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',run_id)
    assert all(key not in authority for key in ['outputRoot','monitorOutputRoot','argv'])
    assert plan['outputPrefix']=='/private/tmp/starling-node-compat/next-portable-cache-stock-v2'
    selected=plan['arms']['stock']
    assert selected['outputRoot'] is selected['monitorOutputRoot'] is selected['argv'] is None
    assert selected['timeoutSeconds']==300
    output=Path(plan['outputPrefix']+'-'+run_id)
    monitor_output=Path(str(output)+'-monitor')
    argv=[plan['node']['path'],str(here/'run-stock.mjs'),str(output),plan['standaloneSource'],plan['browserTools'],run_id,authority['rootAuthorityPath']]
    return output,monitor_output,argv

def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv)==3
    arm=sys.argv[1];assert arm == 'stock';plan=read(HERE/'plans.json');assert plan['bindingState']=='READY_CURRENT_CORRELATION_BROWSER','Unbound Source: no authority/monitor/output/actor'
    authority_path=Path(sys.argv[2]).resolve();authority_ref=row(authority_path);authority=read(authority_path)
    assert authority['state']=='ROOT_NEXT_PUBLIC_CORRELATION_HOST_AUTHORIZED_V1' and authority['arm']==arm
    assert authority['sourceIndex']==row(HERE/'index.json') and authority['plans']==row(HERE/'plans.json')
    assert authority['localhostServerAllowed'] is authority['browserAllowed'] is authority['publicRequestCorrelationAllowed'] is True
    assert authority['rootAuthorityPath']==str(authority_path)
    for k in ['compilerAllowed','nativeBuildAllowed','guestAllowed','engineAllowed','externalApplicationDeploymentAllowed']:assert authority[k] is False
    verify(authority_ref)
    family(authority['sourceIndex'])
    for ref in plan['sourceFamilies']:family(ref)
    for ref in plan['protectedInputs']:verify(ref)
    output,monitor_output,argv=derive_invocation(authority,plan,HERE)
    assert not output.exists() and not output.is_symlink() and not monitor_output.exists() and not monitor_output.is_symlink()
    monitor_output.mkdir(mode=0o700)
    spec=importlib.util.spec_from_file_location('original_owned_browser_phase_monitor',plan['monitor']['path']);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    env={k:os.environ[k] for k in ['HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH=str(Path(plan['node']['path']).parent)+':/usr/bin:/bin',NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1',CI='1')
    terminal=monitor.monitor(argv,plan['cwd'],env,monitor_output,300,authority_ref)
    preserved=True
    try:
        verify(authority_ref)
        family(authority['sourceIndex'])
        for ref in plan['sourceFamilies']:family(ref)
        for ref in plan['protectedInputs']:verify(ref)
    except BaseException:preserved=False
    clean=terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup'] and not terminal['timeout'] and all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
    result_path=output/'result.json';result=read(result_path) if result_path.exists() else None
    observation=dict(schemaVersion=1,state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_OBSERVATION_V1',arm=arm,runId=authority['runId'],outputRoot=str(output),monitorOutputRoot=str(monitor_output),rawExitCode=terminal['rawExitCode'],ownedGroupsClean=clean,protectedInputsPreserved=preserved,terminal=row(monitor_output/'terminal.json'),result=row(result_path) if result_path.exists() else None,hostExperimentPassed=bool(terminal['rawExitCode']==0 and clean and preserved and result and result['passed']),guestOrNativeExecuted=False)
    (monitor_output/'observation.json').write_text(json.dumps(observation,indent=2)+'\n');print(json.dumps(observation),flush=True)
    raise SystemExit(0 if observation['hostExperimentPassed'] else 1)
if __name__=='__main__':main()
