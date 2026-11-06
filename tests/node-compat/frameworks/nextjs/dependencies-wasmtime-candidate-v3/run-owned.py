"""Dormant late-grant dependency control. Original0af180s; no build/packager API."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,stat,sys,traceback
HERE=Path(__file__).resolve().parent
def row(path):
 p=Path(path);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(r):
 p=Path(r['path']);assert p.is_absolute()and'..'not in p.parts
 assert all(not x.is_symlink()for x in(p,*p.parents));assert row(p)==r,r['path'];return p
def read(path):return json.loads(Path(path).read_bytes())
def family(ref):
 root=verify(ref).parent;j=read(ref['path']);names=[x['path']for x in j['files']];assert len(names)==len(set(names));assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(names)|{'index.json'}
 for r in j['files']:
  rel=Path(r['path']);assert not rel.is_absolute()and'..'not in rel.parts;verify(dict(r,path=str(root/rel)))
def write(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:
  with os.fdopen(fd,'w',closefd=False)as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(fd)
 finally:os.close(fd)
def clean(t):
 return t['rawExitCode']==0 and t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True and t['timeout']is False and t['forcedCleanup']is False and all(t[k]==[]for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
def main(path):
 assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
 authority=Path(path).resolve();ar=row(authority);a=read(authority);p=read(HERE/'plan.json');assert a['schemaVersion']==1 and a['state']=='ROOT_NEXT_DEPENDENCIES_WASMTIME_AUTHORIZED_V3'
 assert a['sourceIndex']==row(HERE/'index.json')and a['plan']==row(HERE/'plan.json');assert re.fullmatch('[a-z0-9][a-z0-9-]{0,48}',a['runId'])
 for k in ['localhostServeAllowed','dependencyGuestAllowed']:assert a[k]is True
 for k in ['fullNextApplicationAllowed','compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed']:assert a[k]is False
 def protect():
  verify(ar);family(a['sourceIndex']);family(a['constructorSourceIndex'])
  for k in ['node','wasmtime','monitor','applicationInputs','dependencyEntry','inputSourceIndex']:verify(p[k])
  for k in ['constructionResult','component','componentAudit','engine','nativeMetadata']:verify(a[k])
 protect();app=read(p['applicationInputs']['path']);assert app['root']==p['applicationSource']and app['regularFiles']==2218
 def application():
  root=Path(app['root']);assert root.resolve()==root;actual_files=set();actual_dirs={'.'}
  for q in root.rglob('*'):
   assert not q.is_symlink();rel=q.relative_to(root).as_posix()
   if q.is_dir():actual_dirs.add(rel)
   else:assert q.is_file();actual_files.add(rel)
  assert actual_files=={r['path']for r in app['files']}and actual_dirs=={r['path']for r in app['directories']}
  for r in app['files']:
   path=root/r['path'];verify(dict(path=str(path),sha256=r['sha256'],bytes=r['bytes']));s=path.stat();assert(stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino,s.st_nlink)==(r['mode'],r['dev'],r['ino'],r['nlink'])
  for r in app['directories']:
   s=(root/r['path']).stat();assert(stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino)==(r['mode'],r['dev'],r['ino'])
 application();output=Path(p['outputPrefix']+'-'+a['runId']);outer=Path(str(output)+'-external-root');assert not output.exists()and not outer.exists();os.umask(0o077);outer.mkdir(mode=0o700)
 terminal=None;error=None;final=[];argv=[p['node']['path'],str(HERE/'serve.mjs'),str(authority)]
 try:
  protect();application()
  spec=importlib.util.spec_from_file_location('genuine_dependency_original0af',verify(p['monitor']));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  env={k:os.environ[k]for k in ['HOME','home','CODEX_HOME','USER','LOGNAME']if k in os.environ};env.update(PATH=str(Path(p['node']['path']).parent)+':/usr/bin:/bin',LC_ALL='C',LANG='C',NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1',CI='1')
  terminal=m.monitor(argv,p['cwd'],env,outer,180,ar);assert clean(terminal),'Original owned monitor rejected terminal'
  result=read(output/'result.json');assert result['passed']is True and result['state']=='NEXT_NATIVE_DEPENDENCIES_WASMTIME_PASSED_UNREVIEWED_V3'
 except BaseException as e:error=dict(type=type(e).__name__,message=str(e),stack=traceback.format_exc())
 finally:
  for name,fn in [('source-and-artifact',protect),('application-original',application)]:
   try:fn()
   except BaseException as e:final.append(dict(scope=name,type=type(e).__name__,message=str(e),stack=traceback.format_exc()))
  try:result=read(output/'result.json')if(output/'result.json').is_file()else None
  except BaseException as e:
   result=None;final.append(dict(scope='partial-result-parse',type=type(e).__name__,message=str(e),stack=traceback.format_exc()))
  passed=error is None and not final and terminal is not None and clean(terminal)and result is not None and result['passed']is True
  observation=dict(schemaVersion=1,state='NEXT_DEPENDENCIES_WASMTIME_ROOT_OBSERVATION_V3',passed=passed,authority=ar,sourceIndex=a['sourceIndex'],plan=a['plan'],argv=argv,capSeconds=180,terminal=row(outer/'terminal.json')if terminal is not None else None,rawExitCode=terminal['rawExitCode']if terminal is not None else None,allOwnedClean=clean(terminal)if terminal is not None else False,result=row(output/'result.json')if result else None,error=error,finalProtectionErrors=final,originalApplicationModesAndInodesPreserved=not any(x['scope']=='application-original'for x in final),fullNextApplicationServed=False,adoption=False)
  try:write(outer/'observation.json',observation)
  except BaseException as e:
   observation['passed']=False;observation['observationWriteError']=repr(e);print(json.dumps(observation),flush=True);return 1
  print(json.dumps(observation),flush=True)
 return 0 if passed else 1
if __name__=='__main__':
 assert len(sys.argv)==2
 raise SystemExit(main(sys.argv[1]))
