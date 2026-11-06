"""Experimental Next native build CLI. Inert on import; Root authority required.
No engine/guest/test/crypto execution. New metadata is generated from this build.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,posixpath,shlex,stat,sys,tarfile,time,traceback
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def descriptor(path):
 path=Path(path);h=hashlib.sha256();size=0
 with path.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);size+=len(b)
 return dict(path=str(path),sha256=h.hexdigest(),bytes=size)
def checked(row):
 p=Path(row['path']);assert p.is_absolute()and'..'not in p.parts
 for a in (p,*p.parents):assert not a.is_symlink(),a
 assert p.is_file();r=descriptor(p);assert all(r[k]==row[k]for k in ('path','sha256','bytes')),p;return p
def read(row):assert row['bytes']<=32*1024**2;return json.loads(checked(row).read_bytes())
def save(path,value):
 path=Path(path);fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:
  with os.fdopen(fd,'w',closefd=False)as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fchmod(fd,0o600);os.fsync(fd)
 finally:os.close(fd)
def copy_exclusive(row,target,mode):
 source=checked(row);target=Path(target);target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 try:
  with source.open('rb')as src,os.fdopen(fd,'wb',closefd=False)as dst:
   for block in iter(lambda:src.read(1024**2),b''):dst.write(block)
   dst.flush();os.fchmod(fd,mode);os.fsync(fd)
 finally:os.close(fd)
 actual=descriptor(target);a=source.stat();b=target.stat();assert actual['sha256']==row['sha256']and actual['bytes']==row['bytes'];assert(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)and b.st_nlink==1 and stat.S_IMODE(b.st_mode)==mode
 return dict(source=row,target=actual,mode=mode,singleLink=True,distinctInode=True)
def confined(relative):
 p=Path(relative);assert not p.is_absolute()and'..'not in p.parts and p.parts;return p

def validate_authority(a):
 assert a['schemaVersion']==1 and a['state']=='ROOT_EXPERIMENTAL_NEXT_NATIVE_BUILD_AUTHORITY_V1'
 assert a['buildAllowed']is True and a['engineOrGuestExecutionAllowed']is False
 for key in ['entry','plan','composition','joinedFrontendResult','installedGeneratorResult']:assert isinstance(a[key],dict)
 assert isinstance(a['selectedPublicManifests'],list)and isinstance(a['selectedPrivateManifests'],list)
 work=Path(a['workRoot']);assert work.is_absolute()and str(work).startswith('/private/tmp/starling-node-compat/next-native-build-')and'..'not in work.parts
 return work

def inputs(a,plan):
 rows=[a['entry'],a['plan'],a['composition'],a['joinedFrontendResult'],a['installedGeneratorResult']]
 composition=read(a['composition']);source=Path(composition['sourceRoot']);assert source.name=='source'and str(source.parent).startswith('/private/tmp/starling-node-compat/next-native-profile-');assert len(composition['files'])==composition['nativeSourceFiles']
 assert read(a['joinedFrontendResult'])['passed']is True;generated=read(a['installedGeneratorResult']);assert generated['passed']is True and generated['sourceFiles']==composition['nativeSourceFiles']
 names=set()
 for r in composition['files']:
  rel=confined(r['path']);assert str(rel)not in names;names.add(str(rel));rows.append(dict(path=str(source/rel),sha256=r['sha256'],bytes=r['bytes']))
 assert {p.relative_to(source).as_posix()for p in source.rglob('*')if p.is_file()}==names;assert not any(p.is_symlink()for p in source.rglob('*'))
 rows+=composition['inputs']
 embedding=[]
 for r in a['componentizeSources']:
  rel=confined(r['relativePath']);checked(r['source']);embedding.append(r);rows.append(r['source'])
 assert {r['relativePath']for r in embedding}=={'CMakeLists.txt','embedding/embedding.cpp','embedding/embedding.h'}
 rows += [r['source']for r in plan['supportCopies']]+[r['source']for r in plan['archiveCopies']]+[plan['cbindgen'],plan['rustup'],plan['monitor'],plan['lifecycle'],plan['cpmModule']]
 rows += [t['executable']for t in plan['hostTools']]
 unique={}
 for r in rows:
  if r['path']in unique:assert unique[r['path']]==r
  unique[r['path']]=r;checked(r)
 return composition,source,embedding,list(unique.values())

def selected_manifests(a,source):
 public=[];private=[];modules=set()
 for name in a['selectedPublicManifests']:
  p=source/confined(name);m=json.loads(p.read_bytes());assert m['schemaVersion']==1 and m['nodeVersion']=='v22.14.0'and isinstance(m['profileVersion'],str)and isinstance(m['modules'],dict)
  for module,body in m['modules'].items():assert module.startswith('node:')and module not in modules and len(body['exports'])==len(set(body['exports']));modules.add(module)
  public.append(dict(relativePath=name,descriptor=descriptor(p),wholeManifest=m))
 for name in a['selectedPrivateManifests']:
  p=source/confined(name);m=json.loads(p.read_bytes());assert m['publicNodeManifest']is False and m['specifier'].startswith('starling:');private.append(dict(relativePath=name,descriptor=descriptor(p),wholeManifest=m))
 assert len(public)==22 and len(private)==2;assert len(public)==len(set(a['selectedPublicManifests']))and len(private)==len(set(a['selectedPrivateManifests']))
 return dict(public=public,private=private,moduleNames=sorted(modules))

def load_utility(row,name):
 p=checked(row);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def safe_extract(archive,destination):
 # Authenticated archive only; no absolute/traversing/special members. Links
 # must resolve inside its root; no shell/tar command or preexisting path used.
 destination=Path(destination);destination.mkdir(mode=0o700)
 with tarfile.open(archive,'r:*')as t:
  members=t.getmembers();tops=set()
  for m in members:
   p=confined(m.name);tops.add(p.parts[0]);assert m.isfile()or m.isdir()or m.issym()or m.islnk();assert not(m.mode&0o6000)
   if m.issym()or m.islnk():
    link=posixpath.normpath(posixpath.join(posixpath.dirname(m.name),m.linkname)if m.issym()else m.linkname);assert not link.startswith('/')and link!='..'and not link.startswith('../')
  assert len(tops)==1;t.extractall(destination,members=members)
 return destination/next(iter(tops))

def clean_environment(plan,work,source,sm,sdk):
 env={k:os.environ[k]for k in ['HOME','home','CODEX_HOME','USER','LOGNAME']if k in os.environ}
 tool_dirs=[]
 for t in plan['hostTools']:
  d=str(Path(t['executable']['path']).parent)
  if d not in tool_dirs:tool_dirs.append(d)
 env.update(PATH=str(work/'tools/bin')+':'+str(sdk/'bin')+':'+':'.join(tool_dirs)+':/usr/bin:/bin',RUSTUP_HOME=str(work/'rustup-home'),CARGO_HOME=str(work/'cargo-home'),CARGO_TARGET_DIR=str(work/'rust-target'),RUSTUP_TOOLCHAIN='1.88.0',CPM_SOURCE_CACHE=str(work/'cache'),STARLINGMONKEY_SRC=str(source),SPIDERMONKEY_BINARIES=str(sm),HOST_API='wasi-0.2.10',WPT_ROOT=str(work/'wpt-unused'),TMPDIR=str(work/'tmp'),LC_ALL='C',LANG='C',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_CONFIG_NOSYSTEM='1',GIT_TEMPLATE_DIR=str(work/'git-template'),GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='core.hooksPath',GIT_CONFIG_VALUE_0=str(work/'git-hooks'),GIT_CONFIG_KEY_1='core.fsmonitor',GIT_CONFIG_VALUE_1='false',GIT_CONFIG_KEY_2='maintenance.auto',GIT_CONFIG_VALUE_2='false',GIT_OPTIONAL_LOCKS='0')
 return env

def phase_worker(packet_row):
 packet=read(packet_row);authority=read(packet['authority']);work=validate_authority(authority);assert descriptor(__file__)==authority['entry'];assert authority['plan']==descriptor(HERE/'plan.json');plan=read(authority['plan']);assert packet['argv'][0]in {t['executable']['path']for t in plan['hostTools']}|{str(work/'tools/bin/rustup')};assert packet['output'].startswith(str(work)+'/results/');out=Path(packet['output']);assert out.is_dir()
 life=load_utility(plan['lifecycle'],'genuine_next_build_lifecycle');assert life.MINIMUM_FREE==800*1024**2 and life.REQUIRED_START_FREE==2*1024**3
 samples=[]
 def free():
  s=os.statvfs(work);n=s.f_bavail*s.f_frsize;samples.append(dict(monotonic=time.monotonic(),bytes=n));return n
 result={}
 with(out/'command.combined.log').open('xb')as log:
  result=life.monitor_owned_command(packet['argv'],packet['cwd'],packet['environment'],log,free,minimum_free=plan['disk']['stopBytes']);log.flush();os.fsync(log.fileno())
 result.update(argv=packet['argv'],diskSamples=samples,rawCombinedLog=descriptor(out/'command.combined.log'))
 try:save(out/'worker-result.json',result)
 except BaseException as error:result['resultWriteError']=repr(error)
 print(json.dumps(result),flush=True)
 cleanup=result.get('ownedGroupCleanup')or{}
 clean=cleanup.get('complete')is True and not cleanup.get('events')and not cleanup.get('errors')and not result.get('sigtermReceived')and result.get('stopReason')is None
 return 0 if result['rawChildExitCode']==0 and result['lifecycleComplete']and clean and not result['launcherErrors']and not result['stoppedForDiskSpace']and not result.get('resultWriteError')else 1

def phase(monitor,a,plan,work,label,argv,env,timeout):
 s=os.statvfs(work);assert s.f_bavail*s.f_frsize>=plan['disk']['stopBytes'];output=work/'results'/label;output.mkdir(mode=0o700);packet=dict(authority=descriptor(work/'root-authority.json'),argv=argv,cwd=str(work),environment=env,output=str(output));save(output/'packet.json',packet)
 python=next(t['executable']['path']for t in plan['hostTools']if t['name']=='python3');command=[python,'-B','-I',str(HERE/'run.py'),'--worker-packet',str(output/'packet.json')];outer=output/'owned-monitor';outer.mkdir(mode=0o700)
 terminal=monitor.monitor(command,str(work),env,outer,timeout,descriptor(work/'root-authority.json'))
 worker=json.loads((output/'worker-result.json').read_bytes())if(output/'worker-result.json').exists()else None
 inner=worker.get('ownedGroupCleanup')or{}if worker else{}
 inner_clean=bool(worker and inner.get('complete')is True and not inner.get('events')and not inner.get('errors')and not worker.get('launcherErrors')and not worker.get('sigtermReceived')and worker.get('stopReason')is None)
 record=dict(label=label,argv=argv,innerOwnedClean=inner_clean,rawExitCode=None if worker is None else worker['rawChildExitCode'],outerTerminal=descriptor(outer/'terminal.json'),workerResult=descriptor(output/'worker-result.json')if worker else None,outerRawExitCode=terminal['rawExitCode'],ownedGone=terminal['parentOwnedGroupGone']and terminal['allObservedOwnedGroupsGone'],timeout=terminal['timeout'],forcedCleanup=terminal['forcedCleanup'],errors=terminal['errors'])
 save(output/'phase.json',record);return record

def cache_values(path):
 values={}
 if Path(path).exists():
  for line in Path(path).read_text().splitlines():
   if line.startswith(('#','//'))or':'not in line or'='not in line:continue
   name,tail=line.split(':',1);kind,value=tail.split('=',1);values[name]=dict(type=kind,value=value)
 return values

def main(authority_path):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
 a=json.loads(checked(descriptor(authority_path)).read_bytes());work=validate_authority(a);assert descriptor(__file__)==a['entry'];assert a['plan']==descriptor(HERE/'plan.json');plan=read(a['plan']);assert plan['actionsAllowed']is False
 composition,source,embedding,protected=inputs(a,plan);selection=selected_manifests(a,source);assert not work.exists()and not work.is_symlink();os.umask(0o077)
 free=os.statvfs(work.parent);assert free.f_bavail*free.f_frsize>=plan['disk']['startBytes'];work.mkdir(mode=0o700)
 for name in ['results','tools/bin','rustup-home','cargo-home','rust-target','cache/cpm','tmp','wpt-unused','git-template','git-hooks','archives']:(work/name).mkdir(parents=True,mode=0o700,exist_ok=True)
 save(work/'root-authority.json',a);result=dict(schemaVersion=1,state='EXPERIMENTAL_NEXT_NATIVE_BUILD_RUNNING_V1',sourceComposition=a['composition'],nativePolicyInputs=len(composition['files']),embeddingInputs=embedding,sourceCopies=[],phases=[],primaryError=None,postCollectionErrors=[],inputProtection=None,engineOrGuestExecuted=False,adoption=False)
 try:
  for r in composition['files']:result['sourceCopies'].append(copy_exclusive(dict(path=str(source/confined(r['path'])),sha256=r['sha256'],bytes=r['bytes']),work/'native-source'/r['path'],0o600))
  for r in plan['supportCopies']:
   target=work/'native-source'/confined(r['relativePath'])
   if target.exists():continue # explicitly selected native overlay wins; no overwrite
   result['sourceCopies'].append(copy_exclusive(r['source'],target,r['mode']))
  for r in embedding:result['sourceCopies'].append(copy_exclusive(r['source'],work/'componentize-source'/confined(r['relativePath']),0o600))
  (work/'componentize-source/lib').mkdir(mode=0o700)
  for name in ['rustup','cargo','rustc']:copy_exclusive(plan['rustup'],work/'tools/bin'/name,0o755)
  copy_exclusive(plan['cbindgen'],work/'tools/bin/cbindgen',0o755);copy_exclusive(plan['cpmModule'],work/'cache/cpm/CPM_0.42.0.cmake',0o600)
  archive_roots={};archive_records=[]
  for r in plan['archiveCopies']:
   target=work/'archives'/Path(r['source']['path']).name;copy_exclusive(r['source'],target,0o600);root=safe_extract(target,work/('extracted-'+r['role']));archive_roots[r['role']]=root;archive_records.append(dict(role=r['role'],archive=descriptor(target),extractedRoot=str(root)))
  env=clean_environment(plan,work,work/'native-source',archive_roots['spidermonkey'],archive_roots['wasi-sdk']);save(work/'environment-policy.json',dict(removedStartupNames=sorted(k for k in os.environ if k.startswith('BASH_FUNC_')or k in ['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE']),privateRustupHome=env['RUSTUP_HOME'],privateCargoHome=env['CARGO_HOME'],globalRustupMutationAllowed=False))
  monitor=load_utility(plan['monitor'],'genuine_original_next_build_monitor')
  cmake=next(t['executable']['path']for t in plan['hostTools']if t['name']=='cmake');ninja=next(t['executable']['path']for t in plan['hostTools']if t['name']=='ninja')
  commands=[('rust-setting',[str(work/'tools/bin/rustup'),'set','auto-self-update','disable'],300),('rust-install',[str(work/'tools/bin/rustup'),'toolchain','install','1.88.0','--profile','minimal'],plan['timeouts']['rustInstall']),('rust-target',[str(work/'tools/bin/rustup'),'target','add','--toolchain','1.88.0','wasm32-wasip1'],plan['timeouts']['rustTarget'])]
  flags=['-D'+k+'='+v for k,v in plan['cmakeFlags'].items()];overrides={'wasi-sdk':'wasi-sdk','binaryen':'binaryen','wasm-tools':'wasm-tools','wasmtime':'wasmtime','weval':'weval','openssl':'OpenSSL'}
  flags += ['-DCPM_'+name+'_SOURCE='+str(archive_roots[role])for role,name in overrides.items()]
  configure=[cmake,'-S',str(work/'componentize-source'),'-B',str(work/'build'),'-G','Ninja',*flags]
  build=[cmake,'--build',str(work/'build'),'--target','starlingmonkey_embedding','--parallel','1','--','-d','keeprsp']
  commands += [('configure',configure,plan['timeouts']['configure']),('build',build,plan['timeouts']['build'])]
  for label,argv,timeout in commands:
   for r in protected:checked(r)
   record=phase(monitor,a,plan,work,label,argv,env,timeout);result['phases'].append(record)
   assert record['rawExitCode']==record['outerRawExitCode']==0 and record['ownedGone']and record['innerOwnedClean']and not record['timeout']and not record['forcedCleanup']and not record['errors'],label+' failed'
   if label=='rust-setting':
    settings=work/'rustup-home/settings.toml';raw=settings.read_text();assert [x.strip()for x in raw.splitlines()if x.strip().startswith('auto_self_update')]==['auto_self_update = "disable"'];save(work/'rustup-before.json',dict(settings=descriptor(settings),raw=raw,historicalBeforeInstallData=True))
   if label=='configure':
    # Genuine configured source includes CMake's install_builtins generator.
    save(work/'configured-inputs.json',[descriptor(work/'native-source'/r['path'])for r in composition['files']])
    lock=work/'build/starling-raw.wasm/Cargo.lock';assert descriptor(lock)['sha256']==plan['privateRust']['aggregateLockSha256']
  result['buildCommandSucceeded']=True
 except BaseException as error:result['primaryError']=dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc())
 finally:
  # Preserve actual partial artifacts/cache/DB even if the command/postcollector
  # fails. Never existence-admit an engine or mask original failure with Y.
  try:
   cache=work/'build/CMakeCache.txt';db=work/'build/compile_commands.json';observed=cache_values(cache);result['cmakeCache']=descriptor(cache)if cache.exists()else None;result['compileDatabase']=descriptor(db)if db.exists()else None;result['observedCMake']=observed
   artifact=work/'componentize-source/lib/starlingmonkey_embedding.wasm';result['engineCandidate']=descriptor(artifact)if artifact.exists()else None
   if result.get('buildCommandSucceeded'):
    assert artifact.is_file()and artifact.stat().st_size>8
    with artifact.open('rb')as f:assert f.read(8)==b'\x00asm\x01\x00\x00\x00','not a core Wasm engine'
   if 'monitor'in locals()and(work/'build/build.ninja').exists():
    record=phase(monitor,a,plan,work,'ninja-commands',[ninja,'-C',str(work/'build'),'-t','commands'],env,plan['timeouts']['harvest']);result['phases'].append(record);result['wholeNinjaCommands']=descriptor(work/'results/ninja-commands/command.combined.log');assert record['rawExitCode']==record['outerRawExitCode']==0 and record['ownedGone']and record['innerOwnedClean']and not record['errors']and not record['timeout']and not record['forcedCleanup'],'whole Ninja capture failed'
   if result.get('buildCommandSucceeded'):
    assert all(observed.get(k,{}).get('value')==v for k,v in plan['cmakeFlags'].items()),'observed CMake flags differ'
   result['sourceAfter']=[descriptor(work/'native-source'/r['path'])for r in composition['files']if(work/'native-source'/r['path']).exists()]
   result['archives']=archive_records if 'archive_records'in locals()else[];result['linkInputs']=[descriptor(p)for p in sorted((work/'build').rglob('*'))if p.is_file()and(p.suffix in ['.a','.o','.obj','.rsp']or p.name in ['Cargo.toml','Cargo.lock','rust-staticlib.rs'])]
   result['privateRustSettingsCurrent']=descriptor(work/'rustup-home/settings.toml')if(work/'rustup-home/settings.toml').exists()else None
   configured=work/'configured-inputs.json'
   if result.get('buildCommandSucceeded'):assert read(descriptor(configured))==result['sourceAfter'],'private source changed during compilation'
   # This is a fresh schema, not old83 with changed counts or projected policies.
   sdk_tools=[]
   for name in ['clang','clang++','wasm-ld','llvm-ar','llvm-ranlib']:
    selected=archive_roots['wasi-sdk']/'bin'/name;sdk_tools.append(dict(selectedPath=str(selected),resolved=descriptor(selected.resolve()),linkText=os.readlink(selected)if selected.is_symlink()else None))
   metadata=dict(schemaVersion=1,metadataKind='EXPERIMENTAL_NEXT_NATIVE_BUILD_ACTUAL_V1',sourceComposition=a['composition'],sourceRoot=str(source),compiledSourceRoot=str(work/'native-source'),nativePolicyInputCount=len(composition['files']),nativePolicyInputManifest=composition['files'],embeddingInputCount=len(embedding),embeddingInputManifest=embedding,buildSupportInputCount=len(plan['supportCopies']),selectedModuleManifests=selection,requestedCMake=plan['cmakeFlags'],observedCMake=observed,compileDatabase=result['compileDatabase'],phases=result['phases'],archiveIdentities=result['archives'],compilerTools=plan['hostTools'],actualSdkTools=sdk_tools,actualCompilerWrapper=descriptor(work/'build/cxx-wrapper')if(work/'build/cxx-wrapper').exists()else None,actualCompileRows=json.loads(db.read_bytes())if db.exists()else None,wholeNinjaCommands=result.get('wholeNinjaCommands'),actualPrebuiltSpiderMonkeyLibraries=[descriptor(p)for p in archive_roots['spidermonkey'].rglob('*.a')],compiledAfterInputs=result['sourceAfter'],linkAndRustInputs=result['linkInputs'],engine=result['engineCandidate'],recipe=descriptor(__file__),rootAuthority=descriptor(work/'root-authority.json'),old83MetadataProjected=False,engineExecuted=False,guestExecuted=False,adoption=False)
   save(work/'metadata.json',metadata);result['metadata']=descriptor(work/'metadata.json')
  except BaseException as error:result['postCollectionErrors'].append(dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc()))
  errors=[]
  for r in protected:
   try:checked(r)
   except BaseException as error:errors.append(dict(path=r['path'],error=repr(error)))
  result['inputProtection']=dict(files=len(protected),unchanged=not errors,errors=errors);result['passed']=result.get('buildCommandSucceeded')is True and result['primaryError']is None and not result['postCollectionErrors']and not errors;result['state']='EXPERIMENTAL_NEXT_NATIVE_BUILD_COMPLETED_RUNTIME_PENDING_V1'if result['passed']else'EXPERIMENTAL_NEXT_NATIVE_BUILD_FAILED_UNACCEPTED_V1';
  try:save(work/'result.json',result)
  except BaseException as error:
   result['passed']=False;result['resultWriteError']=repr(error);print(json.dumps(dict(resultWriteFailed=True,wholeResult=result)),flush=True);return 1
 print(json.dumps(dict(result=descriptor(work/'result.json'),passed=result['passed'],engine=result.get('engineCandidate'),metadata=result.get('metadata'))),flush=True);return 0 if result['passed']else 1

if __name__=='__main__':
 parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--authority');group.add_argument('--worker-packet');args=parser.parse_args()
 if args.worker_packet:raise SystemExit(phase_worker(descriptor(args.worker_packet)))
 raise SystemExit(main(args.authority))
