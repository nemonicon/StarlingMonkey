"""Dormant disk-frugal Intl native build. Import is inert; Root authority required.
Uses original owned monitor/lifecycle. No engine, guest, tests or freeze execution.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,posixpath,re,shlex,stat,sys,tarfile,time,tomllib,traceback
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


def phase_worker(packet_row):
 packet=read(packet_row);authority=read(packet['authority']);work=validate_authority(authority);assert descriptor(__file__)==authority['entry'];assert authority['plan']==descriptor(HERE/'plan.json');plan=effective_plan(authority);expected=[x[1]for x in command_plan(authority,plan,work)[0]];ninja=next(t['executable']['path']for t in plan['hostTools']if t['name']=='ninja');expected.append([ninja,'-C',str(work/'build'),'-t','commands']);assert packet['argv']in expected;assert packet['cwd']==str(work)and packet['environment']==environment(plan,authority,work);assert packet['output'].startswith(str(work)+'/results/');out=Path(packet['output']);assert out.is_dir()
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
 python=a['wrapperPython']['path'];command=[python,'-B','-I',str(HERE/'run.py'),'--worker-packet',str(output/'packet.json')];outer=output/'owned-monitor';outer.mkdir(mode=0o700)
 terminal=monitor.monitor(command,str(work),env,outer,timeout,descriptor(work/'root-authority.json'))
 worker=json.loads((output/'worker-result.json').read_bytes())if(output/'worker-result.json').exists()else None
 inner=worker.get('ownedGroupCleanup')or{}if worker else{}
 inner_clean=bool(worker and inner.get('complete')is True and not inner.get('events')and not inner.get('errors')and not worker.get('launcherErrors')and not worker.get('sigtermReceived')and worker.get('stopReason')is None)
 record=dict(label=label,argv=argv,innerOwnedClean=inner_clean,rawExitCode=None if worker is None else worker['rawChildExitCode'],outerTerminal=descriptor(outer/'terminal.json'),workerResult=descriptor(output/'worker-result.json')if worker else None,outerRawExitCode=terminal['rawExitCode'],ownedGone=terminal['parentOwnedGroupGone']and terminal['allObservedOwnedGroupsGone'],timeout=terminal['timeout'],forcedCleanup=terminal['forcedCleanup'],errors=terminal['errors'],signals=terminal['signals'],interruptedSignals=terminal['interruptedSignals'],remainingObservedPids=terminal['remainingObservedPids'])
 save(output/'phase.json',record);return record


def phase_succeeded(record):
 # Actual original0af terminal arrays are mandatory, including a raw0 command
 # that was signaled/interrupted and recovered before its terminal receipt.
 return record['rawExitCode']==record['outerRawExitCode']==0 and record['ownedGone']is True and record['innerOwnedClean']is True and record['timeout']is False and record['forcedCleanup']is False and record['errors']==[] and record['signals']==[] and record['interruptedSignals']==[] and record['remainingObservedPids']==[]


def cache_values(path):
 values={}
 if Path(path).exists():
  for line in Path(path).read_text().splitlines():
   if line.startswith(('#','//'))or':'not in line or'='not in line:continue
   name,tail=line.split(':',1);kind,value=tail.split('=',1);values[name]=dict(type=kind,value=value)
 return values


def validate_authority(a):
 assert a['schemaVersion']==1 and a['state']=='ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1'
 assert a['buildAllowed']is True and a['configureAllowed']is True and a['coherentPatchedIntlLibraryAndHeaders']is True
 for key in ['engineOrGuestExecutionAllowed','freezeAllowed','networkAllowed','rustupAllowed']:assert a[key]is False
 for key in ['entry','plan','callerIndex','composition','installedGeneratorResult','intlLockfile','offlineCargoConfig','intlCargoAudit','spidermonkeyEvidence','savedFramePatchIndex','portableSelection','portableCargoSelection','wrapperPython','generatorNode','installedGeneratorCallerIndex','installedGeneratorRootAuthority']:assert isinstance(a[key],dict),key
 spec=read(a['plan']);assert a['wrapperPython']==spec['wrapperPython'] and descriptor(Path(sys.executable).resolve())==spec['wrapperPython'],'pinned wrapperPython3.11 required'
 w=Path(a['workRoot']);assert w.is_absolute()and'..'not in w.parts and str(w).startswith('/private/tmp/starling-node-compat/next-native-intl-build-')
 for parent in w.parents:assert not parent.is_symlink(),parent
 return w

def portable_admission(a,spec):
 external=spec['portableAdmissionSourceIndex'];index_row=dict(path=str(HERE.parents[4]/external['repositoryPath']),sha256=external['sha256'],bytes=external['bytes']);index=check_family(index_row)
 member=spec['portableAdmissionModule'];matches=[r for r in index['files']if r['path']==member['relativePath']];assert len(matches)==1 and all(matches[0][k]==member[k]for k in ['sha256','bytes'])
 row=dict(path=str(Path(index_row['path']).parent/member['relativePath']),sha256=member['sha256'],bytes=member['bytes'])
 module=load_utility(row,'held_original_portable_next_source_admission')
 selection=module.admit(a['portableSelection'],spec['portableSourcePolicy'],HERE.parents[4])
 return module,selection

def cargo_admission(a,spec):
 source_module,source_selection=portable_admission(a,spec)
 member=spec['cargoAdmissionModule'];module=load_utility(dict(path=str(HERE/member['relativePath']),sha256=member['sha256'],bytes=member['bytes']),'portable_cargo_build_admission')
 admitted=module.admit(a['portableCargoSelection'],source_selection,a,spec['portableCargoPolicy'],HERE.parents[4])
 assert a['wrapperPython']==spec['wrapperPython']
 for key in ['intlLockfile','offlineCargoConfig','intlCargoAudit']:assert a[key]==admitted[key],key+' must equal admitted Cargo role'
 for role in ['intl-firefox','intl-vendor']:assert a['reusedTrees'][role]==admitted['reusedTrees'][role],role+' must equal admitted tree'
 return module,admitted

def recheck_cargo(a,spec,before=None):
 module,admitted=cargo_admission(a,spec)
 if before is not None:assert admitted==before,'portable Cargo source/proof/physical selection changed'
 return admitted

def effective_plan(a):
 spec=read(a['plan']);assert a['plan']==descriptor(HERE/'plan.json')and spec['actionsAllowed']is False
 p=read(spec['basePlan']);p['hostTools']=[x for x in p['hostTools']if x['name']not in ['rustup','cargo','rustc']]
 p.update(disk=spec['disk'],timeouts=spec['timeouts'],cmakeFlags={**p['cmakeFlags'],**spec['cmakeAdditions']})
 p['cargo']=a['cargo'];p['rustc']=a['rustc'];p['wrapperPython']=spec['wrapperPython'];assert a['wrapperPython']==spec['wrapperPython'] and descriptor(Path(sys.executable).resolve())==spec['wrapperPython'];module,selection=portable_admission(a,spec)
 support=module.role_copies(selection,'build-support');p['supportCopies']=[r for r in support if r['relativePath']!='runtime/crates/staticlib-template/Cargo.intl.toml.in']
 assert len(p['supportCopies'])==386
 return p

def tree_snapshot(root):
 """Read-only complete physical tree, including directories and safe links.
 Hashes follow regular files only. Never follow directory links during traversal.
 """
 root=Path(root);assert root.is_absolute()and'..'not in root.parts
 for q in (root,*root.parents):assert not q.is_symlink(),q
 assert root.is_dir();rows=[]
 def walk(p):
  for q in sorted(p.iterdir()):
   s=q.lstat();r=dict(path=q.relative_to(root).as_posix(),mode=stat.S_IMODE(s.st_mode),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,mtimeNs=s.st_mtime_ns)
   if stat.S_ISLNK(s.st_mode):
    target=os.readlink(q);assert not Path(target).is_absolute();logical=posixpath.normpath(posixpath.join(q.parent.relative_to(root).as_posix(),target));assert logical!='..'and not logical.startswith('../');physical=q.resolve(strict=True);assert physical==root or root in physical.parents
    r.update(kind='symlink',target=target)
   elif stat.S_ISDIR(s.st_mode):r['kind']='directory'
   else:
    assert stat.S_ISREG(s.st_mode),q;r.update(kind='file',sha256=descriptor(q)['sha256'],bytes=s.st_size)
   rows.append(r)
   if r['kind']=='directory':walk(q)
 walk(root);s=root.stat();return dict(root=str(root),rootIdentity=dict(mode=stat.S_IMODE(s.st_mode),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,mtimeNs=s.st_mtime_ns),entries=rows)

def tree_content(snapshot):
 return dict(root=snapshot['root'],rootMode=snapshot['rootIdentity']['mode'],entries=[{k:v for k,v in r.items()if k not in ['dev','ino','nlink','mtimeNs']}for r in snapshot['entries']])

def authenticate_tree(spec):
 expected=read(spec['inventory']);actual=tree_snapshot(spec['root']);assert tree_content(expected)==tree_content(actual),'tree inventory differs: '+spec['root'];return actual

def check_family(index_row):
 index=read(index_row);assert isinstance(index['files'],list);parent=Path(index_row['path']).parent;names=set()
 for row in index['files']:
  rel=confined(row.get('path',row.get('relativePath','')));name=rel.as_posix();assert name not in names;names.add(name);checked(dict(path=str(parent/rel),sha256=row['sha256'],bytes=row['bytes']))
 actual={p.relative_to(parent).as_posix()for p in parent.rglob('*')if p.is_file()};assert actual==names|{Path(index_row['path']).name};assert not any(p.is_symlink()for p in parent.rglob('*'));return index

def require_member(row,root):
 checked(row);p=Path(row['path']);assert Path(root)in p.parents,p

def inputs(a,spec,p):
 rows=[a['entry'],a['plan'],a['callerIndex'],a['wrapperPython'],a['portableCargoSelection'],spec['baseRunner'],spec['basePlan'],spec['portableBaseMap'],spec['baseBuildResult'],a['composition'],a['installedGeneratorResult'],a['intlLockfile'],a['offlineCargoConfig'],a['spidermonkeyEvidence'],a['savedFramePatchIndex'],a['cargo'],a['rustc'],a['smLibrary'],a['smSavedFrameHeader'],a['smConfigHeader'],a['smConfdefsHeader']]
 assert Path(a['callerIndex']['path'])==HERE/'index.json';check_family(a['callerIndex']);check_family(a['savedFramePatchIndex'])
 module,portable=portable_admission(a,spec);assert a['composition']==portable['composition'];cargo_module,cargo_selection=cargo_admission(a,spec);rows+=cargo_selection['protectedInputs']
 assert a['componentizeSources']==module.role_copies(portable,'componentize-embedding')
 assert a['supportAdditions']==[r for r in module.role_copies(portable,'build-support')if r['relativePath']=='runtime/crates/staticlib-template/Cargo.intl.toml.in']
 rows+=portable['protectedInputs']+[a['generatorNode']]
 composition=read(a['composition']);source=Path(composition['sourceRoot']);assert source.name=='source'and source.is_absolute();assert composition['nativeSourceFiles']==len(composition['files'])==435
 generated=read(a['installedGeneratorResult']);assert generated['sourceIndex']==a['installedGeneratorCallerIndex']and generated['rootAuthority']==a['installedGeneratorRootAuthority'];check_family(a['installedGeneratorCallerIndex']);rows+=module.validate_generators(generated,portable,a['generatorNode'],spec['portableSourcePolicy'],a['portableSelection']);assert generated['passed']is True and generated['sourceFiles']==435 and generated['sourceBeforeAfterUnchanged']is True and generated['nativeOrGuestExecuted']is False
 assert len(generated['commands'])==10 and all(x['rawExitCode']==0 and x['stderrSha256']==hashlib.sha256(b'').hexdigest()for x in generated['commands'])
 names=set()
 for r in composition['files']:
  rel=confined(r['path']);assert rel.as_posix()not in names;names.add(rel.as_posix());rows.append(dict(path=str(source/rel),sha256=r['sha256'],bytes=r['bytes']))
 assert {x.relative_to(source).as_posix()for x in source.rglob('*')if x.is_file()}==names;assert not any(x.is_symlink()for x in source.rglob('*'))
 rows+=composition['inputs']
 embedding=a['componentizeSources'];assert len(embedding)==3 and {r['relativePath']for r in embedding}=={'CMakeLists.txt','embedding/embedding.cpp','embedding/embedding.h'}
 additions=a['supportAdditions'];assert len(additions)==1 and additions[0]['relativePath']=='runtime/crates/staticlib-template/Cargo.intl.toml.in'and additions[0]['mode']==0o600
 support=p['supportCopies']+additions;assert len(support)==387 and len({r['relativePath']for r in support})==387
 assert not names&{r['relativePath']for r in support},'support/native overlap must be explicitly recomposed'
 for r in embedding+support:confined(r['relativePath']);rows.append(r['source'])
 rows += [p['cbindgen'],p['cpmModule'],p['monitor'],p['lifecycle']]+[r['executable']for r in p['hostTools']]
 trees=a['reusedTrees'];assert set(trees)==set(spec['reusedTrees'])
 for role,tree in trees.items():
  fixed=spec['reusedTrees'][role];rows.append(tree['inventory']);rows.append(tree['provenance'])
  if role in ['intl-firefox','intl-vendor']:assert tree==cargo_selection['reusedTrees'][role]
  else:
   assert fixed['root']is None or tree['root']==fixed['root']
   if fixed['provenance']is not None:assert tree['provenance']==fixed['provenance']
   if 'archive'in fixed:assert tree['archive']==fixed['archive'];rows.append(tree['archive'])
 for r in [a['cargo'],a['rustc']]:require_member(r,trees['rust']['root'])
 assert Path(a['rustc']['path']).name=='rustc'and Path(a['cargo']['path']).name=='cargo'
 assert list((Path(trees['rust']['root'])/'lib/rustlib/wasm32-wasip1/lib').glob('libstd-*.rlib')),'wasip1 stdlib absent'
 for r in [a['smLibrary'],a['smSavedFrameHeader'],a['smConfigHeader'],a['smConfdefsHeader']]:require_member(r,trees['spidermonkey']['root'])
 assert a['smSavedFrameHeader']['path']==str(Path(trees['spidermonkey']['root'])/'include/js/SavedFrameAPI.h')
 patch=read(a['savedFramePatchIndex']);headers=[r for r in patch['files']if r['path']=='after/js/public/SavedFrameAPI.h'];assert len(headers)==1
 assert all(a['smSavedFrameHeader'][k]==headers[0][k]for k in ['sha256','bytes']),'installed API header must equal the actual selected patch afterimage'
 assert a['smLibrary']['path']==str(Path(trees['spidermonkey']['root'])/'libspidermonkey.a')
 with checked(a['smLibrary']).open('rb')as library:assert library.read(8)==b'!<arch>\n'
 assert a['smConfdefsHeader']['path']==str(Path(trees['spidermonkey']['root'])/'include/js-confdefs.h')
 h=checked(a['smSavedFrameHeader']).read_text();assert re.search(r'^#define JS_HAS_SAVEDFRAME_IS_EVAL 1$',h,re.M)and'GetSavedFrameIsEval'in h
 assert a['smConfigHeader']['path']==str(Path(trees['spidermonkey']['root'])/'include/js-config.h')
 assert re.search(r'^#[ \t]*define[ \t]+JS_HAS_INTL_API[ \t]+1[ \t]*$',checked(a['smConfigHeader']).read_text(),re.M),'coherent Intl js-confdefs required'
 # New actual offline metadata result is admitted by cargo-selection.py;
 # oldac935 audit/path identities are ancestry only, never retargeted proof.
 assert a['intlCargoAudit']==cargo_selection['intlCargoAudit']
 config=tomllib.loads(checked(a['offlineCargoConfig']).read_text());assert config['source']['intl-vendor']['directory']==trees['intl-vendor']['root']
 extraction=read(spec['baseBuildResult']);assert extraction['passed']is True
 # Old extraction JSON remains archive provenance; old compiled outputs/source
 # locations are not requirements or evidence for these fresh portable inputs.
 for role in ['wasi-sdk','binaryen','wasm-tools','wasmtime','weval']:
  old=next(x for x in extraction['archives']if x['role']==role);assert old['archive']==trees[role]['archive']and old['extractedRoot']==trees[role]['root']
 openssl=next(x for x in extraction['archives']if x['role']=='openssl')['archive'];rows.append(openssl)
 unique={}
 for r in rows:
  if r['path']in unique:assert unique[r['path']]==r
  unique[r['path']]=r;checked(r)
 return composition,source,embedding,support,trees,openssl,list(unique.values())

def environment(p,a,work):
 t=a['reusedTrees'];env={k:os.environ[k]for k in ['HOME','home','CODEX_HOME','USER','LOGNAME']if k in os.environ}
 dirs=[str(work/'tools/bin'),str(Path(a['rustc']['path']).parent),str(Path(t['wasi-sdk']['root'])/'bin')]
 dirs += list(dict.fromkeys(str(Path(x['executable']['path']).parent)for x in p['hostTools']))
 env.update(CARGO_BUILD_JOBS='1',MAKEFLAGS='-j1',CARGO_INCREMENTAL='0',CCACHE_DISABLE='1',SCCACHE_DISABLE='1',PATH=':'.join(dirs)+':/usr/bin:/bin',RUSTC=a['rustc']['path'],CARGO_HOME=str(work/'cargo-home'),CARGO_TARGET_DIR=str(work/'rust-target'),CARGO_NET_OFFLINE='true',CARGO_NET_GIT_FETCH_WITH_CLI='false',CPM_SOURCE_CACHE=str(work/'cache'),STARLINGMONKEY_SRC=str(work/'native-source'),SPIDERMONKEY_BINARIES=t['spidermonkey']['root'],HOST_API='wasi-0.2.10',WPT_ROOT=str(work/'wpt-unused'),TMPDIR=str(work/'tmp'),LC_ALL='C',LANG='C',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_CONFIG_NOSYSTEM='1',GIT_TEMPLATE_DIR=str(work/'git-template'),GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='core.hooksPath',GIT_CONFIG_VALUE_0=str(work/'git-hooks'),GIT_CONFIG_KEY_1='core.fsmonitor',GIT_CONFIG_VALUE_1='false',GIT_CONFIG_KEY_2='maintenance.auto',GIT_CONFIG_VALUE_2='false',GIT_OPTIONAL_LOCKS='0')
 return env

def command_plan(a,p,work):
 trees=a['reusedTrees'];cmake=next(x['executable']['path']for x in p['hostTools']if x['name']=='cmake')
 flags={**p['cmakeFlags'],'Rust_COMPILER':a['rustc']['path'],'Rust_CARGO':a['cargo']['path'],'NODE_COMPAT_INTL_LOCKFILE':a['intlLockfile']['path'],'NODE_COMPAT_INTL_FIREFOX_SOURCE':trees['intl-firefox']['root']}
 for role,name in [('wasi-sdk','wasi-sdk'),('binaryen','binaryen'),('wasm-tools','wasm-tools'),('wasmtime','wasmtime'),('weval','weval'),('corrosion','corrosion')]:flags['CPM_'+name+'_SOURCE']=trees[role]['root']
 flags['CPM_OpenSSL_SOURCE']=str(work/'private-openssl/openssl-3.0.17')
 return [('rust-version',[a['rustc']['path'],'--version','--verbose'],p['timeouts']['tool']),('cargo-version',[a['cargo']['path'],'--version','--verbose'],p['timeouts']['tool']),('rust-sysroot',[a['rustc']['path'],'--print','sysroot'],p['timeouts']['tool']),('configure',[cmake,'-S',str(work/'componentize-source'),'-B',str(work/'build'),'-G','Ninja',*['-D'+k+'='+v for k,v in flags.items()]],p['timeouts']['configure']),('build',[cmake,'--build',str(work/'build'),'--target','starlingmonkey_embedding','--parallel','1','--','-d','keeprsp'],p['timeouts']['build'])],flags

def validate_configured(work,a,spec):
 root=work/'build/starling-raw.wasm';lock=descriptor(root/'Cargo.lock');assert lock['sha256']==a['intlLockfile']['sha256']and lock['bytes']==a['intlLockfile']['bytes']
 actual=tomllib.loads((root/'Cargo.toml').read_text());reference=tomllib.loads((Path(a['intlLockfile']['path']).parent/'Cargo.toml').read_text());expected=copy.deepcopy(reference)
 base={'rust-encoding':'crates/rust-encoding','rust-hooks':'crates/rust-hooks','rust-url':'crates/rust-url','multipart':'crates/rust-multipart'}
 for name,relative in base.items():expected['dependencies'][name]['path']=str(work/'native-source'/relative)
 assert 'features'not in expected['dependencies']['unicode-bidi-ffi'];expected['dependencies']['unicode-bidi-ffi']['features']=[]
 assert actual==expected,'configured aggregate differs beyond four verified native base paths and known empty bidi features'
 names=list(actual['dependencies']);assert len(names)==6 and set(names)==set(spec['requiredAggregateDependencyNames'])
 assert actual['workspace']=={} and actual['lib']=={'crate-type':['staticlib'],'path':'rust-staticlib.rs'}
 assert actual['dependencies']['icu_capi']['default-features']is False and actual['dependencies']['icu_capi']['features']==['any_provider','compiled_data','segmenter','calendar']
 return dict(lock=lock,manifest=descriptor(root/'Cargo.toml'),dependencyNames=names,fullNonPathSemanticsVerified=True,basePathsBoundToCopiedNativeSources=True)

def main(authority_path):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1
 authority_row=descriptor(authority_path);a=read(authority_row);work=validate_authority(a);assert a['entry']==descriptor(__file__);spec=read(a['plan']);p=effective_plan(a)
 composition,source,embedding,support,trees,openssl,protected=inputs(a,spec,p);selection=selected_manifests(a,source);cargo_module,cargo_before=cargo_admission(a,spec)
 before={role:authenticate_tree(t)for role,t in trees.items()}
 assert not work.exists()and not work.is_symlink();free=os.statvfs(work.parent);assert free.f_bavail*free.f_frsize>=p['disk']['startBytes'];os.umask(0o077);work.mkdir(mode=0o700)
 for name in ['results','tools/bin','cargo-home','rust-target','cache/cpm','tmp','wpt-unused','git-template','git-hooks']:(work/name).mkdir(parents=True,mode=0o700,exist_ok=True)
 save(work/'root-authority.json',a);save(work/'protection-before.json',before)
 result=dict(schemaVersion=1,state='EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_RUNNING_V1',sourceComposition=a['composition'],sourceCopies=[],phases=[],primaryError=None,postCollectionErrors=[],inputProtection=None,engineOrGuestExecuted=False,adoption=False,runnerVersion=3,wrapperPython=a['wrapperPython'],portableCargoSelection=a['portableCargoSelection'])
 def recheck():
  checked(authority_row);check_family(a['callerIndex']);check_family(a['savedFramePatchIndex']);check_family(a['installedGeneratorCallerIndex']);portable_admission(a,spec);recheck_cargo(a,spec,cargo_before)
  if result.get('workBaseVerified'):cargo_module.verify_work_base(cargo_before,work/'native-source')
  for r in protected:checked(r)
  for role,t in trees.items():assert tree_snapshot(t['root'])==before[role],'reused tree changed: '+role
 try:
  recheck()
  for r in composition['files']:result['sourceCopies'].append(copy_exclusive(dict(path=str(source/confined(r['path'])),sha256=r['sha256'],bytes=r['bytes']),work/'native-source'/r['path'],0o600))
  for r in support:result['sourceCopies'].append(copy_exclusive(r['source'],work/'native-source'/confined(r['relativePath']),r['mode']))
  for r in embedding:result['sourceCopies'].append(copy_exclusive(r['source'],work/'componentize-source'/confined(r['relativePath']),0o600))
  result['verifiedWorkBase']=cargo_module.verify_work_base(cargo_before,work/'native-source');result['workBaseVerified']=True
  (work/'componentize-source/lib').mkdir(mode=0o700);copy_exclusive(p['cbindgen'],work/'tools/bin/cbindgen',0o755);copy_exclusive(p['cpmModule'],work/'cache/cpm/CPM_0.42.0.cmake',0o600);copy_exclusive(a['offlineCargoConfig'],work/'cargo-home/config.toml',0o600)
  private_ssl=safe_extract(checked(openssl),work/'private-openssl');assert private_ssl.name=='openssl-3.0.17';result['privateOpenSSL']=dict(archive=openssl,root=str(private_ssl),freshExtraction=True)
  env=environment(p,a,work);save(work/'environment-policy.json',dict(environment=env,HOMEInherited='HOME'in os.environ and env.get('HOME')==os.environ['HOME'],rustupInvoked=False,privateCargoHome=True,offline=True))
  monitor=load_utility(p['monitor'],'genuine_original_next_intl_build_monitor');commands,flags=command_plan(a,p,work)
  for label,argv,timeout in commands:
   recheck();record=phase(monitor,a,p,work,label,argv,env,timeout);result['phases'].append(record);recheck();assert phase_succeeded(record),label+' failed'
   log=(work/'results'/label/'command.combined.log').read_text()
   if label=='rust-version':assert re.search(r'^release: 1\.88\.0$',log,re.M)
   elif label=='cargo-version':assert log.startswith('cargo 1.88.0 ')
   elif label=='rust-sysroot':assert log.strip()==trees['rust']['root']
   elif label=='configure':
    result['configuredRust']=validate_configured(work,a,spec);save(work/'configured-inputs.json',[descriptor(work/'native-source'/r['path'])for r in composition['files']])
  result['buildCommandSucceeded']=True
 except BaseException as error:result['primaryError']=dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc())
 finally:
  try:
   cache=work/'build/CMakeCache.txt';db=work/'build/compile_commands.json';observed=cache_values(cache);result.update(cmakeCache=descriptor(cache)if cache.exists()else None,compileDatabase=descriptor(db)if db.exists()else None,observedCMake=observed)
   artifact=work/'componentize-source/lib/starlingmonkey_embedding.wasm';result['engineCandidate']=descriptor(artifact)if artifact.exists()else None
   if 'monitor'in locals()and(work/'build/build.ninja').exists():
    recheck();ninja=next(t['executable']['path']for t in p['hostTools']if t['name']=='ninja');record=phase(monitor,a,p,work,'ninja-commands',[ninja,'-C',str(work/'build'),'-t','commands'],env,p['timeouts']['harvest']);result['phases'].append(record);recheck();result['wholeNinjaCommands']=descriptor(work/'results/ninja-commands/command.combined.log');assert phase_succeeded(record)
   result['sourceAfter']=[descriptor(work/'native-source'/r['path'])for r in composition['files']if(work/'native-source'/r['path']).exists()]
   result['linkInputs']=[descriptor(q)for q in sorted((work/'build').rglob('*'))if q.is_file()and(q.suffix in ['.a','.o','.obj','.rsp']or q.name in ['Cargo.toml','Cargo.lock','rust-staticlib.rs'])]
   compile_rows=json.loads(db.read_bytes())if db.exists()else None
   if result.get('buildCommandSucceeded'):
    assert artifact.read_bytes()[:8]==b'\x00asm\x01\x00\x00\x00';assert len(compile_rows)==80 and len({r['file']for r in compile_rows})==80
    ninja_text=checked(result['wholeNinjaCommands']).read_text();embedding_rows=[line for line in ninja_text.splitlines()if ' -c '+str(work/'componentize-source/embedding/embedding.cpp')in line];assert len(embedding_rows)==1
    assert all(observed.get(k,{}).get('value')==v for k,v in flags.items())
    assert observed['Rust_TOOLCHAIN_IS_RUSTUP_MANAGED']['value']not in ['TRUE','ON','1']if 'Rust_TOOLCHAIN_IS_RUSTUP_MANAGED'in observed else True
    assert read(descriptor(work/'configured-inputs.json'))==result['sourceAfter'];validate_configured(work,a,spec)
   metadata=dict(schemaVersion=1,metadataKind='EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1',sourceComposition=a['composition'],sourceRoot=str(source),compiledSourceRoot=str(work/'native-source'),compiledAfterInputs=result['sourceAfter'],compilerTools=p['hostTools'],actualRustTools=dict(cargo=a['cargo'],rustc=a['rustc']),nativePolicyInputCount=len(composition['files']),nativePolicyInputManifest=composition['files'],buildSupportInputCount=len(support),buildSupportInputManifest=support,embeddingInputCount=len(embedding),embeddingInputManifest=embedding,selectedModuleManifests=selection,requestedCMake=flags if 'flags'in locals()else None,observedCMake=observed,compileDatabase=result['compileDatabase'],actualCompileRows=compile_rows,wholeNinjaCommands=result.get('wholeNinjaCommands'),actualSeparateEmbeddingCompileRows=embedding_rows if 'embedding_rows'in locals()else None,actualLibrary=a['smLibrary'],actualSavedFrameHeader=a['smSavedFrameHeader'],actualConfigHeader=a['smConfigHeader'],actualConfdefs=a['smConfdefsHeader'],patchedSpiderMonkeyEvidence=a['spidermonkeyEvidence'],savedFramePatchIndex=a['savedFramePatchIndex'],actualAggregateLock=a['intlLockfile'],actualRustConfiguration=result.get('configuredRust'),offlineCargoConfig=a['offlineCargoConfig'],validatedCargoAudit=a['intlCargoAudit'],portableCargoSelection=a['portableCargoSelection'],portableCargoAdmission=cargo_before,wrapperPython=a['wrapperPython'],buildToolPython=next(r['executable']for r in p['hostTools']if r['name']=='python3'),portableBuildAdmissionVersion=3,logicalCargoAuditDescriptorFromVerifiedCapsule=True,validatedCargoProofCapsule=spec['portableCargoPolicy']['metadataArchive'],validatedCargoProofIndex=spec['portableCargoPolicy']['metadataArchiveIndex'],toolTreeInputs=trees,initialTreeProtection=descriptor(work/'protection-before.json'),originalExtractionWholeTreeAttestationClaimed=False,linkAndRustInputs=result['linkInputs'],engine=result.get('engineCandidate'),phases=result['phases'],recipe=a['entry'],rootAuthority=descriptor(work/'root-authority.json'),old83MetadataProjected=False,engineExecuted=False,guestExecuted=False,adoption=False)
   save(work/'metadata.json',metadata);result['metadata']=descriptor(work/'metadata.json')
  except BaseException as error:result['postCollectionErrors'].append(dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc()))
  errors=[]
  try:recheck()
  except BaseException as error:errors.append(dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc()))
  result['inputProtection']=dict(files=len(protected),wholeTrees=len(trees),unchanged=not errors,errors=errors,currentBeforeFinalOnly=True)
  result['passed']=result.get('buildCommandSucceeded')is True and result['primaryError']is None and not result['postCollectionErrors']and not errors
  result['state']='EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_COMPLETED_RUNTIME_PENDING_V1'if result['passed']else'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_FAILED_UNACCEPTED_V1'
  try:save(work/'result.json',result)
  except BaseException as error:
   result['passed']=False;result['resultWriteError']=repr(error);print(json.dumps(dict(resultWriteFailed=True,wholeResult=result)),flush=True);return 1
 print(json.dumps(dict(result=descriptor(work/'result.json'),passed=result['passed'],engine=result.get('engineCandidate'),metadata=result.get('metadata'))),flush=True);return 0 if result['passed']else 1

if __name__=='__main__':
 parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--authority');group.add_argument('--worker-packet');args=parser.parse_args()
 if args.worker_packet:raise SystemExit(phase_worker(descriptor(args.worker_packet)))
 raise SystemExit(main(args.authority))
