"""Dormant source-only entry. Authenticate this whole family before custom import."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-build-controller-candidate-v1')
def initial(row):
    p=Path(row['path']);assert p.is_absolute()and '..'not in p.parts
    for x in(p,*p.parents):assert not x.is_symlink()
    a=p.stat();assert p.is_file();raw=p.read_bytes();b=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
    assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return raw
def entry(config_row):
    assert __debug__ and sys.dont_write_bytecode
    config=json.loads(initial(config_row));ix=config['controllerIndex'];assert ix['path']==str(OWN/'index.json')
    index=json.loads(initial(ix));names=set()
    for r in index['files']:
        n=r['path'];assert n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/'))and n not in names;names.add(n);initial(dict(path=str(OWN/n),sha256=r['sha256'],bytes=r['bytes']))
    assert not any(p.is_symlink()for p in OWN.rglob('*'))
    assert{p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}==names|{'index.json'}
    spec=importlib.util.spec_from_file_location('scheduler_resource_normal_build_guard',OWN/'guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    frame=guard.authorize(config_row)
    try:
        assert not guard.EXTERNAL.exists()and not guard.EXTERNAL.is_symlink()
        assert not guard.WORK.exists()and not guard.WORK.is_symlink()and not guard.BUILD_OUTPUT.exists()and not guard.BUILD_OUTPUT.is_symlink()
        monitor=next(r for r in frame['ownRows']if r['path']==str(OWN/'monitor.py'));guard.checked(monitor)
        spec=importlib.util.spec_from_file_location('scheduler_resource_owned_external_monitor',OWN/'monitor.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        guard.recheck(frame['captured'],frame['families']);guard.EXTERNAL.mkdir(mode=0o700)
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
        argv=[sys.executable,'-B','-I',str(OWN/'build.py'),json.dumps(config_row,separators=(',',':'))]
        terminal=module.monitor(argv,str(guard.REPO),env,guard.EXTERNAL,7200,config['rootAuthority'])
        assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True
        assert terminal['remainingObservedPids']==[]and not terminal['forcedCleanup']and not terminal['timeout']and not terminal['errors']and not terminal['interruptedSignals']
        print(json.dumps(terminal),flush=True)
    finally:guard.recheck(frame['captured'],frame['families'])
if __name__=='__main__':assert len(sys.argv)==2;entry(json.loads(sys.argv[1]))
