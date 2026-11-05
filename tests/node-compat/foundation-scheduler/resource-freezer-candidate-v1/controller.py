"""Dormant owned2400s freeze caller, authenticating whole own source before import."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-freezer-candidate-v1')
def initial(row):
 p=Path(row['path']);assert type(row['path'])is str and row['path'].startswith('/')and str(p)==row['path']and '..'not in p.parts
 for q in(p,*p.parents):assert not q.is_symlink()
 a=p.stat();assert p.is_file();raw=p.read_bytes();b=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
 assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return raw
def entry(config_row):
 assert __debug__ and sys.dont_write_bytecode
 cfg=json.loads(initial(config_row));ix=cfg['freezerIndex'];assert ix['path']==str(OWN/'index.json');index=json.loads(initial(ix));names=set()
 for r in index['files']:
  n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names;names.add(n);initial(dict(path=str(OWN/n),sha256=r['sha256'],bytes=r['bytes']))
 assert not any(p.is_symlink()for p in OWN.rglob('*'))and{p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}==names|{'index.json'}
 spec=importlib.util.spec_from_file_location('resource342_freeze_guard',OWN/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);frame=g.authorize(config_row)
 try:
  assert not g.EXTERNAL.exists()and not g.EXTERNAL.is_symlink()and not g.FREEZE.exists()and not g.FREEZE.is_symlink()
  spec=importlib.util.spec_from_file_location('resource342_generic_owned_freeze_monitor',OWN/'monitor.py');monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor);g.recheck(frame)
  g.EXTERNAL.mkdir(mode=0o700);argv=[sys.executable,'-B','-I',str(OWN/'freeze.py'),json.dumps(config_row,separators=(',',':'))]
  terminal=monitor.monitor(argv,str(g.REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},g.EXTERNAL,2400,cfg['rootAuthority'])
  assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True
  assert not terminal['forcedCleanup']and not terminal['timeout']and not terminal['errors']and not terminal['interruptedSignals']and terminal['remainingObservedPids']==[]
  print(json.dumps(terminal),flush=True)
 finally:g.recheck(frame)
if __name__=='__main__':assert len(sys.argv)==2;entry(json.loads(sys.argv[1]))
