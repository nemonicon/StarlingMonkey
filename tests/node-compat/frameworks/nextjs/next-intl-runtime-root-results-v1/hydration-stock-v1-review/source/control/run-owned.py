"""Dormant per-arm original0af300s runner; never launches both implicitly."""
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
    verify(ref);root=Path(ref['path']).parent;index=read(ref['path']);names=[r['path'] for r in index['files']]
    assert len(names)==len(set(names))
    assert set(names)|{'index.json'}=={x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
    for r in index['files']:
        p=Path(r['path']);assert not p.is_absolute() and '..' not in p.parts and not(root/p).is_symlink()
        assert row(root/p)==dict(r,path=str(root/p))
def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv)==3
    arm=sys.argv[1];assert arm == 'stock';authority_path=Path(sys.argv[2]).resolve();authority=read(authority_path);plan=read(HERE/'plans.json')
    assert authority['state']=='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1' and authority['arm']==arm
    assert authority['sourceIndex']==row(HERE/'index.json') and authority['plans']==row(HERE/'plans.json')
    assert authority['localhostServerAllowed'] is authority['browserAllowed'] is True
    for k in ['compilerAllowed','nativeBuildAllowed','guestAllowed','engineAllowed','externalApplicationDeploymentAllowed']:assert authority[k] is False
    family(authority['sourceIndex'])
    for ref in plan['sourceFamilies']:family(ref)
    for ref in plan['protectedInputs']:verify(ref)
    selected=plan['arms'][arm];output=Path(selected['outputRoot']);monitor_output=Path(selected['monitorOutputRoot'])
    assert not output.exists() and not monitor_output.exists()
    monitor_output.mkdir(mode=0o700)
    spec=importlib.util.spec_from_file_location('original_owned_browser_phase_monitor',plan['monitor']['path']);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    env={k:os.environ[k] for k in ['HOME','USER','LOGNAME'] if k in os.environ};env.update(PATH=str(Path(plan['node']['path']).parent)+':/usr/bin:/bin',NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1',CI='1')
    terminal=monitor.monitor(selected['argv'],plan['cwd'],env,monitor_output,300,row(authority_path))
    preserved=True
    try:
        family(authority['sourceIndex'])
        for ref in plan['sourceFamilies']:family(ref)
        for ref in plan['protectedInputs']:verify(ref)
    except BaseException:preserved=False
    clean=terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup'] and not terminal['timeout'] and all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
    result_path=output/'result.json';result=read(result_path) if result_path.exists() else None
    observation=dict(schemaVersion=1,state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_OBSERVATION_V1',arm=arm,rawExitCode=terminal['rawExitCode'],ownedGroupsClean=clean,protectedInputsPreserved=preserved,terminal=row(monitor_output/'terminal.json'),result=row(result_path) if result_path.exists() else None,hostExperimentPassed=bool(terminal['rawExitCode']==0 and clean and preserved and result and result['passed']),guestOrNativeExecuted=False)
    (monitor_output/'observation.json').write_text(json.dumps(observation,indent=2)+'\n');print(json.dumps(observation),flush=True)
    raise SystemExit(0 if observation['hostExperimentPassed'] else 1)
if __name__=='__main__':main()
