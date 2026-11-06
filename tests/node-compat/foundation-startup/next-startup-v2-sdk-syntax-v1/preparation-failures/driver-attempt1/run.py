"""Root-authorized six frontend-only observations; no object/link/target run."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,stat,sys,time,traceback
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[3]
SOURCE=OWN.parent/'next-startup-candidate-v2';PLAN=SOURCE/'sdk-syntax-plan.json';INDEX=SOURCE/'index.json';ROOT=Path('/private/tmp/starling-node-compat/next-startup-v2-sdk-syntax-v1')
def d(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def write(path,value):
 path=Path(path);data=(json.dumps(value,indent=2)+'\n').encode();fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 try:
  with os.fdopen(fd,'wb',closefd=False)as f:f.write(data);f.flush();os.fchmod(fd,0o600);os.fsync(fd)
 finally:os.close(fd)
def identity(p):
 s=Path(p).stat();return dict(mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,links=s.st_nlink,bytes=s.st_size,mtimeNs=s.st_mtime_ns,ctimeNs=s.st_ctime_ns)
def physical(p):
 p=Path(p);assert p.is_absolute()and'..'not in p.parts
 if str(p).startswith('/tmp/'):
  assert Path('/tmp').is_symlink()and os.readlink('/tmp')=='private/tmp'and str(Path('/tmp').resolve())=='/private/tmp';p=Path('/private'+str(p))
 for a in (p,*p.parents):assert not a.is_symlink(),a
 assert stat.S_ISREG(p.lstat().st_mode),p
 return p
files={};aliases={};trees={};absences={}
def check(row):
 p=physical(row['path']);before=identity(p);actual=d(p);assert actual['sha256']==row['sha256']and actual['bytes']==row['bytes'],row['path'];assert identity(p)==before
 value=dict(row={k:row[k]for k in ('path','sha256','bytes')},identity=before)
 assert files.get(row['path'],value)==value,row['path'];files[row['path']]=value;return p
def read(row):assert row['bytes']<=32*1024**2;return json.loads(check(row).read_bytes())
def family(row):
 root=Path(row['path']).parent;idx=read(row);expected=[]
 for r in idx['files']:
  rel=Path(r['path']);assert not rel.is_absolute()and'..'not in rel.parts and r['path']!='index.json';expected.append(r['path']);check(dict(r,path=str(root/rel)))
 assert len(expected)==len(set(expected));actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()};assert actual==set(expected)|{'index.json'}
 assert not any(p.is_symlink()for p in root.rglob('*'))
def tree(root):
 root=Path(root);out=dict(files=[],aliases=[],directories={})
 for p in (root,*root.rglob('*')):
  rel=p.relative_to(root)
  if '.git'in rel.parts:continue
  if p.is_symlink():out['aliases'].append(rel.as_posix())
  elif p.is_file():out['files'].append(rel.as_posix())
  else:
   assert p.is_dir();s=p.stat();out['directories'][rel.as_posix()]=[s.st_dev,s.st_ino,stat.S_IMODE(s.st_mode)]
 out['files'].sort();out['aliases'].sort();return out
def alias(row):
 p=Path(row['path']);assert p.is_symlink()and os.readlink(p)==row['linkText']and str(p.resolve(strict=True))==row['resolved'];s=p.lstat();return dict(linkText=os.readlink(p),resolved=row['resolved'],mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino)
def absent(path):
 p=Path(path);assert not p.exists()and not p.is_symlink();return [(str(a),a.stat().st_dev,a.stat().st_ino,stat.S_IMODE(a.stat().st_mode))for a in p.parents if a.exists()and not a.is_symlink()]
def protect_final():
 errors=[]
 for r in list(files.values()):
  try:check(r['row'])
  except BaseException as e:errors.append(dict(path=r['row']['path'],error=repr(e)))
 for p,r in aliases.items():
  try:assert alias(r['row'])==r['observed']
  except BaseException as e:errors.append(dict(path=p,error=repr(e)))
 for p,r in trees.items():
  try:assert tree(p)==r
  except BaseException as e:errors.append(dict(path=p,error=repr(e)))
 for p,r in absences.items():
  try:assert absent(p)==r
  except BaseException as e:errors.append(dict(path=p,error=repr(e)))
 return dict(files=len(files),aliases=len(aliases),trees=len(trees),absentIncludes=len(absences),unchanged=not errors,errors=errors)
def terminal_ok(t):return t['rawExitCode']==0 and t['parentOwnedGroupGone']and t['allObservedOwnedGroupsGone']and not t['forcedCleanup']and not t['timeout']and all(t[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
def main():
 assert __debug__and sys.flags.isolated and sys.dont_write_bytecode
 assert d(PLAN)['sha256']=='f1292843caca167a796ecbc2546e8fdc495eb51ad809efd18610e7ef19fad7a6'and d(INDEX)['sha256']=='7a54dcda7ff2e104cc6c87e735bdb31dd2b9b748191b30d34240ff0bc72aa04b'
 assert not ROOT.exists()and not ROOT.is_symlink();os.umask(0o077)
 authority=dict(schemaVersion=1,state='ROOT_AUTHORIZED_NEXT_STARTUP_V2_SIX_SDK_FRONTENDS_V1',authorization='Explicit Root task: actual six ONLY SDK syntax frontends, plan f129/index7a54,120s each/original0af, no object/link/engine/guest',plan=d(PLAN),sourceIndex=d(INDEX),entry=d(__file__),python=d(sys.executable),unitIds=['buffer','module-p2','startup','rng','registration','performance'],compilerFrontendAllowed=True,maximumSecondsPerCommand=120,objectAllowed=False,linkAllowed=False,engineAllowed=False,guestAllowed=False,cryptoOrKeyOrGcWorkloadAllowed=False)
 write(OWN/'root-authorization.json',authority);print('Authenticating inherited originals/source/tool boundary before monitor import',flush=True)
 family(authority['sourceIndex']);check(authority['entry']);check(authority['python']);check(d(OWN/'root-authorization.json'));plan=read(authority['plan'])
 for k,r in plan['references'].items():
  if k.endswith('Index'):family(r)
  else:check(r)
 ledger=read(plan['references']['inputLedger']);assert len(ledger['files'])==21451
 for row in ledger['files']:check(row)
 alias_data=read(plan['references']['aliasInventory'])
 for row in alias_data['symlinks']:aliases[row['path']]=dict(row=row,observed=alias(row))
 assert alias_data['archiveHardlinks']==[]
 inherited=read(d(REPO/'tests/node-compat/async-context/native-als-candidate-v3/sdk-plan.json'))
 for r in inherited['protectedTrees']:
  snap=tree(r['path']);assert len(snap['files'])==r['regularFiles']and len(snap['aliases'])==r['symlinks'];trees[r['path']]=snap
 for r in plan['sourceCopies']:check(r['source'])
 for p in plan['observedAbsentInheritedIncludeDirectories']:absences[p]=absent(p)
 # Actual selected clang aliases must resolve to the authenticated leaf.
 compiler=Path(plan['units'][0]['argv'][0]);assert compiler.resolve()==Path(plan['references']['compilerLeaf']['path']);assert all(u['argv'][0]==str(compiler)for u in plan['units'])
 print('Protected %d files/%d aliases; staging68 private Source copies'%(len(files),len(aliases)),flush=True)
 ROOT.mkdir(mode=0o700);(ROOT/'commands').mkdir(mode=0o700);(ROOT/'tmp').mkdir(mode=0o700);write(ROOT/'root-authorization.json',authority)
 result=dict(schemaVersion=1,state='NEXT_STARTUP_V2_SDK_FRONTENDS_RUNNING',plan=authority['plan'],sourceIndex=authority['sourceIndex'],authorization=d(ROOT/'root-authorization.json'),units=[],sourceCopies=[],compilerInvoked=False,nativeEngineOrGuestExecuted=False,objectOrLinkExecuted=False,finalProtection=None,primaryError=None)
 write(ROOT/'start.json',result)
 try:
  for r in plan['sourceCopies']:
   src=check(r['source']);dest=Path(r['privatePath']);assert dest.is_relative_to(ROOT)if hasattr(dest,'is_relative_to')else str(dest).startswith(str(ROOT)+'/');dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
   fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
   try:
    with src.open('rb')as source,os.fdopen(fd,'wb',closefd=False)as out:
     while True:
      b=source.read(1024*1024)
      if not b:break
      out.write(b)
     out.flush();os.fchmod(fd,0o600);os.fsync(fd)
   finally:os.close(fd)
   a=src.stat();b=dest.stat();assert b.st_nlink==1 and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)and stat.S_IMODE(b.st_mode)==0o600
   assert d(dest)['sha256']==r['source']['sha256'];result['sourceCopies'].append(dict(source=r['source'],private=d(dest),mode=0o600,links=1,distinctInode=True))
  assert len(result['sourceCopies'])==68
  write(ROOT/'overlay.json',plan['overlayTemplate'])
  monitor_file=Path(plan['references']['monitorIndex']['path']).parent/'monitor.py';monitor_desc=next(r for r in json.loads(Path(plan['references']['monitorIndex']['path']).read_bytes())['files']if r['path']=='monitor.py');check(dict(monitor_desc,path=str(monitor_file)))
  assert d(monitor_file)['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
  spec=importlib.util.spec_from_file_location('root_owned_next_startup_v2_frontend_monitor',monitor_file);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
  env={k:os.environ[k]for k in ['HOME','home','CODEX_HOME','USER','LOGNAME']if k in os.environ};env.update(PATH=str(compiler.parent)+':/usr/bin:/bin',TMPDIR=str(ROOT/'tmp'),LC_ALL='C',LANG='C')
  for u in plan['units']:
   argv=u['argv'];assert '-fsyntax-only'in argv and'-c'not in argv and'-o'not in argv;assert argv[-1]==u['privateMainPath']and Path(argv[-1]).is_file();output=ROOT/'commands'/u['id'];output.mkdir(mode=0o700)
   print('Frontend '+u['id'],flush=True);result['compilerInvoked']=True
   terminal=monitor.monitor(argv,u['actualCompileRow']['directory'],env,output,120,d(ROOT/'root-authorization.json'))
   row=dict(id=u['id'],argv=argv,terminal=d(output/'terminal.json'),stdout=d(output/'stdout.log'),stderr=d(output/'stderr.log'),rawExitCode=terminal['rawExitCode'],ownedClean=terminal_ok(terminal),dependencies=None,dependencyFiles=[],dependencyErrors=[])
   dep=ROOT/'commands'/(u['id']+'.d')
   if dep.exists():
    row['dependencies']=d(dep);text=dep.read_text().replace('\\\n','');target,sep,names=text.partition(':');assert sep and target.strip()==u['id'];names=shlex.split(names,comments=False,posix=True)
    for name in names:
     p=Path(name)
     if not p.is_absolute():p=Path(u['actualCompileRow']['directory'])/p
     physical_path=Path(name)
     original_to_private={r['logicalPath']:r['privatePath']for r in plan['sourceCopies']}
     if str(p)in original_to_private:physical_path=Path(original_to_private[str(p)])
     else:physical_path=p
     try:
      desc=d(physical_path);row['dependencyFiles'].append(dict(logicalPath=str(p),physical=desc))
      if str(physical_path).startswith(str(ROOT)+'/'):assert any(desc['sha256']==r['private']['sha256']and desc['path']==r['private']['path']for r in result['sourceCopies'])
      elif physical_path.is_symlink():
       assert str(physical_path)in aliases;assert alias(aliases[str(physical_path)]['row'])==aliases[str(physical_path)]['observed']
      else:check(dict(desc,path=str(physical_path)))
     except BaseException as e:row['dependencyErrors'].append(dict(logicalPath=str(p),physicalPath=str(physical_path),error=repr(e)))
   result['units'].append(row);write(ROOT/('result-'+u['id']+'.json'),row)
 except BaseException as e:result['primaryError']=dict(type=type(e).__name__,message=str(e),stack=traceback.format_exc())
 finally:
  print('Rechecking full protected boundary',flush=True);result['finalProtection']=protect_final();result['passed']=result['primaryError']is None and len(result['units'])==6 and all(r['ownedClean']and r['dependencies']and not r['dependencyErrors']for r in result['units'])and result['finalProtection']['unchanged'];result['state']='NEXT_STARTUP_V2_SDK_FRONTENDS_PASSED'if result['passed']else'NEXT_STARTUP_V2_SDK_FRONTENDS_FAILED_UNACCEPTED';write(ROOT/'result.json',result)
 print(json.dumps(dict(result=d(ROOT/'result.json'),passed=result['passed'],units=[dict(id=r['id'],rawExitCode=r['rawExitCode'],dependencyErrors=r['dependencyErrors'])for r in result['units']],finalProtection=result['finalProtection'])),flush=True);return 0 if result['passed']else 1
if __name__=='__main__':raise SystemExit(main())
