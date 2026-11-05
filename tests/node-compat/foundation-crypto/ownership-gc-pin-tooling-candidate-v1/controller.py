"""Dormant2400s outer monitor for one explicit export or bootstrap phase."""
from pathlib import Path
import hashlib,importlib.util,json,sys,os
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-gc-pin-tooling-candidate-v1')
def primitive(row):
    path=Path(row['path']);assert path.is_absolute() and '..' not in path.parts
    for p in (path,*path.parents):assert not p.is_symlink()
    a=path.stat();assert path.is_file();h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=path.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    assert h.hexdigest()==row['sha256'] and a.st_size==row['bytes'];return path

def primitive_read(row):
    raw=primitive(row).read_bytes()
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
    return json.loads(raw)

def main(config_row,phase):
    assert phase in ('export','bootstrap') and __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k)for k in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'))
    config=primitive_read(config_row);ix=config['toolingIndex'];assert ix['path']==str(OWN/'index.json')
    index=primitive_read(ix);names=set()
    for r in index['files']:
        name=r['path'];assert name not in names and name and not name.startswith('/') and all(p not in ('','.','..')for p in name.split('/'))
        names.add(name);primitive(dict(path=str(OWN/name),sha256=r['sha256'],bytes=r['bytes']))
    assert not any(p.is_symlink()for p in OWN.rglob('*'))
    assert {p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}==names|{'index.json'}
    spec=importlib.util.spec_from_file_location('crypto_gc_pin_outer_guard',OWN/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    frame=guard.authorize(config_row,phase)
    try:
        tooling=guard.read(config['toolingRootAuthority'])
        out=Path(tooling['externalOutputRoot']);assert not out.exists() and not out.is_symlink()
        row=next(r for r in frame['toolingFrame']['captured'] if r['path']=='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v2/controller.py')
        guard.recheck_frame(frame)
        spec=importlib.util.spec_from_file_location('reviewed_gc_pin_owned_monitor',guard.checked(row))
        monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
        guard.recheck_frame(frame);out.mkdir(mode=0o700)
        argv=[sys.executable,'-B','-I',str(OWN/'action.py'),phase,json.dumps(config_row,separators=(',',':'))]
        terminal=monitor.monitor(argv,str(guard.REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},out,2400,config['rootAuthority'])
        if phase=='export' and (Path(guard.BUILD_OUTPUT)/'gc-pin.UNREVIEWED.json').is_file():
            # Own actual action result is still UNREVIEWED. This does not adopt a pin.
            path=Path(guard.BUILD_OUTPUT)/'gc-pin.UNREVIEWED.json';raw=path.read_bytes()
            frame['toolingFrame']['expectedCandidate']=dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
        assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True
        assert terminal['remainingObservedPids']==[] and terminal['forcedCleanup']is False and terminal['timeout']is False
        assert terminal['errors']==[] and terminal['interruptedSignals']==[]
        print(json.dumps(terminal),flush=True)
    finally:
        guard.recheck_frame(frame)

if __name__=='__main__':
    assert len(sys.argv)==3
    main(json.loads(sys.argv[2]),sys.argv[1])
