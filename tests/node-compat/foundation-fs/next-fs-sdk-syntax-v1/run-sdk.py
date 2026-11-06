"""Dormant syntax-only driver. Root must issue a separate concrete authority."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import stat
import sys

HERE=Path(__file__).resolve().parent

def descriptor(path):
    path=Path(path);b=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))

def read(path):return json.loads(Path(path).read_text())

def verify(row):
    assert descriptor(row['path'])=={k:row[k] for k in ('path','sha256','bytes')},row['path']
    if 'identity' in row:
        s=Path(row['path']).lstat()
        assert dict(device=s.st_dev,inode=s.st_ino,mode=stat.S_IMODE(s.st_mode),links=s.st_nlink)==row['identity'],row['path']

def family(index):
    verify(index);root=Path(index['path']).parent;data=read(index['path'])
    names=[r['path'] for r in data['files']];assert len(names)==len(set(names))
    assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}==set(names)|{'index.json'}
    for r in data['files']:
        p=Path(r['path']);assert not p.is_absolute() and '..' not in p.parts
        assert not (root/p).is_symlink()
        verify(dict(r,path=str(root/p)))

def clean(t):
    return (t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True
        and t['timeout'] is False and t['forcedCleanup'] is False
        and all(t[k]==[] for k in ('signals','errors','interruptedSignals','remainingObservedPids')))

def preflight(plan):
    assert plan['state']=='DORMANT_NEXT_FS_SDK_SYNTAX_PLAN_V1'
    assert len(plan['units'])==3 and plan['compilerSecondsPerUnit']==60
    for index in plan['sourceFamilies']:family(index)
    for r in plan['protectedRows']:verify(r)
    for a in plan['aliases']:
        assert os.readlink(a['path'])==a['linkText']
        assert str(Path(a['path']).resolve())==a['resolvedPath']
    for unit in plan['units']:
        argv=unit['argv'];assert Path(unit['main']).is_file()
        assert argv[0]==plan['compiler']['path'] and argv[-1]==unit['main']
        assert '-fsyntax-only' in argv and '-DNODE_COMPAT_FS=1' in argv
        assert '-c' not in argv and '-o' not in argv and not any(x.startswith('@') for x in argv)
        assert '-DNDEBUG' in argv and '--target=wasm32-wasi' in argv
    assert plan['objectOrLinkAllowed'] is plan['nativeOrGuestAllowed'] is False

def main():
    assert sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==2
    authority_path=Path(sys.argv[1]).resolve();authority=read(authority_path)
    index=descriptor(HERE/'index.json');assert authority['sourcePlanIndex']==index
    family(index)
    assert authority['state']=='ROOT_NEXT_FS_SDK_SYNTAX_AUTHORIZED_V1'
    assert authority['compilerSyntaxAllowed'] is True
    for k in ['objectAllowed','linkAllowed','nativeBuildAllowed','engineAllowed','guestAllowed','runtimeAdmissionAllowed']:assert authority[k] is False
    plan=read(HERE/'plan.json');assert authority['plan']==descriptor(HERE/'plan.json')
    preflight(plan)
    output=Path(plan['outputRoot']);assert not output.exists()
    output.mkdir(mode=0o700);(output/'tmp').mkdir(mode=0o700)
    (output/'overlay.json').write_text(json.dumps(plan['overlay'],indent=2)+'\n')
    env={k:os.environ[k] for k in ['HOME','USER','LOGNAME'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin',TMPDIR=str(output/'tmp'))
    terminals=[];primary=None
    try:
        spec=importlib.util.spec_from_file_location('genuine_original_owned_monitor',plan['monitor']['path'])
        monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
        for unit in plan['units']:
            preflight(plan)
            out=output/unit['id'];out.mkdir(mode=0o700)
            t=monitor.monitor(unit['argv'],unit['directory'],env,out,60,descriptor(authority_path))
            terminals.append(dict(id=unit['id'],terminal=t))
            assert clean(t),'cleanup/interruption refusal'
    except BaseException as e:primary=e
    preserved=False
    try:preflight(plan);preserved=True
    except BaseException as e:
        if primary is None:primary=e
    deps=[];dependency_error=None
    try:
        for unit in plan['units']:
            f=Path(unit['dependencies'])
            if f.exists():
                target,body=f.read_text().replace('\\\n','').split(':',1)
                assert target==unit['id']
                for name in shlex.split(body):
                    logical=str(Path(unit['directory'])/name)
                    actual=next((r['external-contents'] for r in plan['overlay']['roots'] if r['name']==logical),logical)
                    deps.append(dict(unit=unit['id'],reportedPath=logical,actual=descriptor(actual)))
    except BaseException as e:
        dependency_error=dict(type=type(e).__name__,message=str(e))
        if primary is None:primary=e
    result=dict(schemaVersion=1,state='NEXT_FS_ACTUAL_SDK_SYNTAX_RESULT_V1',
        passed=primary is None and preserved and len(terminals)==3 and all(t['terminal']['rawExitCode']==0 for t in terminals),
        terminals=terminals,sourceCompilerDatabaseMonitorPreserved=preserved,dependenciesCapturedAfterCompile=deps,dependencyCaptureError=dependency_error,
        dependencyScope='Current dependency hashes captured after compilation; no whole-SDK preauthenticated closure or before/after identity proof.',
        error=None if primary is None else dict(type=type(primary).__name__,message=str(primary)),
        compilerReplayPerformed=False,objectBuilt=False,linked=False,nativeOrGuestExecuted=False)
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],result=descriptor(output/'result.json'))),flush=True)
    raise SystemExit(0 if result['passed'] else 1)

if __name__=='__main__':main()
