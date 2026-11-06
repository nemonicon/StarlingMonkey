"""Root-gated single-frontend/native archive+link delta. Import is inert.
No CMake/configure/Ninja/Cargo/Rustup/engine/guest execution.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,posixpath,shlex,stat,sys,time,traceback
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


def load_utility(row,name):
 p=checked(row);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


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


def family(row):
 value=read(row);root=Path(row['path']).parent;names=set()
 for f in value['files']:
  rel=confined(f['path']);assert rel.as_posix()not in names;names.add(rel.as_posix());checked(dict(path=str(root/rel),sha256=f['sha256'],bytes=f['bytes']))
 assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{Path(row['path']).name};assert not any(p.is_symlink()for p in root.rglob('*'));return value

def archive_members(path):
 data=Path(path).read_bytes();assert data[:8]==b'!<arch>\n','regular (not thin) ar required';offset=8;strings=b'';records=[]
 while offset<len(data):
  header=data[offset:offset+60];assert len(header)==60 and header[58:]==b'`\n';size=int(header[48:58]);name=header[:16].decode('ascii').strip();body=data[offset+60:offset+60+size];assert len(body)==size;offset+=60+size+(size%2)
  if name=='//':strings=body;continue
  if name in ['/','/SYM64/']:continue
  if name.startswith('#1/'):
   n=int(name[3:]);name=body[:n].rstrip(b'\0').decode();body=body[n:]
  elif name.startswith('/'):
   begin=int(name[1:]);end=strings.index(b'/\n',begin);name=strings[begin:end].decode()
  else:name=name.rstrip('/')
  assert name and '/'not in name and name not in ['.','..'];records.append(dict(name=name,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body)))
 assert offset==len(data)and len({x['name']for x in records})==len(records);return records

def commands(plan,work):
 work=Path(work);assert work.is_absolute()and'..'not in work.parts;base=Path(plan['baselineRoot']);old=plan['originalCompileRow'];argv=shlex.split(old['command']);assert argv[argv.index('-c')+1]==old['file'];argv[argv.index('-o')+1]=str(work/plan['archiveMember'])
 argv += ['-ivfsoverlay',str(work/'overlay.json'),'-MD','-MF',str(work/'module-kernel.d'),'-MT',str(work/plan['archiveMember'])]
 original=plan['originalLinkArgv'];link=[original[0],*plan['additionalLinkFlags']];assert plan['additionalLinkFlags']==['-Wl,--strip-debug'];inputs=[];i=1
 while i<len(original):
  token=original[i]
  if token=='-o':link += ['-o',str(work/'raw.wasm')];i+=2;continue
  if token=='-mthread-model':link+=original[i:i+2];i+=2;continue
  if token.startswith('-'):assert '@'not in token;link.append(token)
  else:
   assert token.endswith(('.a','.o','.obj','.rsp'))and not token.startswith('@'),'unexpected link token: '+token
   path=Path(token)if Path(token).is_absolute()else base/'build'/token;assert path.is_absolute();inputs.append(str(path))
   link.append(str(work/'libbuiltin_node_compat.a')if str(path)==plan['originalArchive']['path']else str(path))
  i+=1
 assert link.count(str(work/'libbuiltin_node_compat.a'))==1
 post=plan['originalPostprocessArgv'];assert post[1:]==['--strip-debug','-O3','-o','starling-raw.wasm','starling-raw.wasm']
 result=[('compile',argv),('archive',[plan['tools']['llvmAr']['path'],'r',str(work/'libbuiltin_node_compat.a'),str(work/plan['archiveMember'])]),('ranlib',[plan['tools']['llvmRanlib']['path'],str(work/'libbuiltin_node_compat.a')]),('link',link),('optimize',[plan['tools']['wasmOpt']['path'],*post[1:3],'-o',str(work/'raw.wasm'),str(work/'raw.wasm')])]
 return result,inputs

def authority(row):
 a=read(row);assert a['schemaVersion']==1 and a['state']=='ROOT_SINGLE_MODULE_UTF16_NATIVE_DELTA_AUTHORITY_V1'
 assert a['singleFrontendCompileAllowed']is True and a['privateArchiveReplacementAllowed']is True and a['relinkAndOptimizeAllowed']is True
 for k in ['fullBuildAllowed','configureAllowed','cargoOrRustupAllowed','engineOrGuestAllowed','networkAllowed']:assert a[k]is False
 assert descriptor(sys.executable)==read(a['plan'])['hostPython'];assert a['entry']==descriptor(__file__)and a['plan']==descriptor(HERE/'plan.json')and Path(a['callerIndex']['path'])==HERE/'index.json'
 family(a['callerIndex']);work=Path(a['workRoot']);assert work.is_absolute()and str(work).startswith('/private/tmp/starling-node-compat/next-native-module-utf16-delta-')and'..'not in work.parts
 for p in work.parents:assert not p.is_symlink()
 plan=read(a['plan']);assert plan['actionsAllowed']is False;return a,plan,work

def input_rows(plan):
 meta=read(plan['baselineMetadata']);assert meta['metadataKind']=='EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1';result=read(plan['baselineResult']);assert result['passed']is True and result['engineCandidate']==meta['engine']and result['metadata']==plan['baselineMetadata']
 review=read(plan['baselineReview']);assert review['state']=='INDEPENDENT_ACTUAL_NEXT_INTL_NATIVE_BUILD_DATA_REVIEW_PASSED_V1'and review['engine']==meta['engine']and review['nativeMetadata']==plan['baselineMetadata'];review_index=family(plan['baselineReviewIndex']);assert sum(str(Path(plan['baselineReviewIndex']['path']).parent/r['path'])==plan['baselineReview']['path']and all(r[k]==plan['baselineReview'][k]for k in ['sha256','bytes'])for r in review_index['files'])==1;family(plan['afterimageFamily'])
 assert plan['originalCompileRow']in meta['actualCompileRows']and len(meta['actualCompileRows'])==80 and len(meta['actualSeparateEmbeddingCompileRows'])==1
 assert plan['afterimage']['path'].endswith('/after/builtins/node-compat/module-kernel.cpp')and plan['originalCompileSource']in meta['compiledAfterInputs']
 assert plan['afterimage']['path']==str(Path(plan['afterimageFamily']['path']).parent/'after/builtins/node-compat/module-kernel.cpp');patch=read(plan['afterimageFamily']);selected=[r for r in patch['files']if r['path']=='after/builtins/node-compat/module-kernel.cpp'];assert len(selected)==1 and all(plan['afterimage'][k]==selected[0][k]for k in ['sha256','bytes'])
 rows=[plan[k]for k in ['baselineResult','baselineMetadata','baselineEnvironmentPolicy','baselineReviewIndex','baselineReview','baselineAuthority','originalCompileSource','originalObject','originalArchive','afterimage','afterimageFamily','monitor','lifecycle','compilerWrapper','hostPython','hostBash']]+list(plan['tools'].values())
 rows += [r['target']for r in result['sourceCopies']]+meta['linkAndRustInputs']+meta['compiledAfterInputs']+[r['source']for r in meta['embeddingInputManifest']]+[meta['engine'],meta['initialTreeProtection'],meta['wholeNinjaCommands'],meta['compileDatabase'],meta['recipe'],meta['rootAuthority'],meta['actualAggregateLock'],meta['actualLibrary'],meta['actualSavedFrameHeader'],meta['actualConfigHeader'],meta['actualConfdefs']]
 for tree in meta['toolTreeInputs'].values():
  rows += [tree['inventory'],tree['provenance']]
  if 'archive'in tree:rows.append(tree['archive'])
 unique={}
 for r in rows:
  if r['path']in unique:assert unique[r['path']]==r
  unique[r['path']]=r;checked(r)
 members=archive_members(checked(plan['originalArchive']));selected=[m for m in members if m['name']==plan['archiveMember']];assert len(members)==15 and len(selected)==1 and all(selected[0][k]==plan['originalObject'][k]for k in ['sha256','bytes'])
 return meta,list(unique.values()),members

def environment(plan,work):
 env=read(plan['baselineEnvironmentPolicy'])['environment'];env=dict(env)
 for k in ['HOME','home','CODEX_HOME']:
  if k in os.environ:env[k]=os.environ[k]
  else:env.pop(k,None)
 env.update(TMPDIR=str(work/'tmp'),CARGO_HOME=str(work/'unused-cargo-home'),CARGO_TARGET_DIR=str(work/'unused-rust-target'),CARGO_NET_OFFLINE='true',MAKEFLAGS='-j1',CARGO_BUILD_JOBS='1');return env

def free_bytes(path):
 s=os.statvfs(path);return s.f_bavail*s.f_frsize

def private_bytes(work):return sum(p.stat().st_size for p in work.rglob('*')if p.is_file())

def worker(packet_row):
 packet=read(packet_row);a,p,w=authority(packet['authority']);expected=dict(commands(p,w)[0]);assert packet['argv']==expected[packet['label']]and packet['environment']==environment(p,w)and packet['cwd']==str(w)
 life=load_utility(p['lifecycle'],'genuine_f751_delta_lifecycle');assert life.MINIMUM_FREE==800*1024**2 and life.REQUIRED_START_FREE==2*1024**3
 out=w/'results'/packet['label'];samples=[]
 def free():
  n=free_bytes(w);samples.append(dict(monotonic=time.monotonic(),bytes=n));return n
 with(out/'command.log').open('xb')as log:
  record=life.monitor_owned_command(packet['argv'],str(w),packet['environment'],log,free,minimum_free=p['disk']['stopBytes']);log.flush();os.fsync(log.fileno())
 record.update(argv=packet['argv'],diskSamples=samples,log=descriptor(out/'command.log'));save(out/'worker-result.json',record);print(json.dumps(record),flush=True)
 c=record.get('ownedGroupCleanup')or{};okay=record['rawChildExitCode']==0 and record['childStarted']is True and record['lifecycleComplete']is True and not record['launcherErrors']and not record['stoppedForDiskSpace']and not record['stopReason']and not record['sigtermReceived']and c.get('complete')is True and c.get('events')==[]and c.get('errors')==[]
 return 0 if okay else 1

def dependency_paths(text):
 text=text.replace('\\\n',' ');assert ':'in text
 words=shlex.split(text.split(':',1)[1]);assert words and all(Path(x).is_absolute()for x in words)
 return list(dict.fromkeys(words))

def core_surface(path):
 data=Path(path).read_bytes();assert data[:8]==b'\0asm\1\0\0\0';offset=8;sections={}
 def number(buf,pos):
  value=0;shift=0
  while True:
   b=buf[pos];pos+=1;value|=(b&127)<<shift
   if b<128:return value,pos
   shift+=7;assert shift<70
 def name(buf,pos):
  n,pos=number(buf,pos);return buf[pos:pos+n].decode(),pos+n
 while offset<len(data):
  kind=data[offset];offset+=1;n,offset=number(data,offset);end=offset+n;assert end<=len(data)
  if kind:assert kind not in sections;sections[kind]=data[offset:end]
  offset=end
 types=[];buf=sections[1];count,pos=number(buf,0)
 for _ in range(count):
  assert buf[pos]==0x60;pos+=1;n,pos=number(buf,pos);params=list(buf[pos:pos+n]);pos+=n;n,pos=number(buf,pos);results=list(buf[pos:pos+n]);pos+=n;types.append(dict(params=params,results=results))
 assert pos==len(buf);imports=[];function_types=[];buf=sections.get(2,b'\0');count,pos=number(buf,0)
 for _ in range(count):
  module,pos=name(buf,pos);field,pos=name(buf,pos);kind=buf[pos];pos+=1;assert kind==0,'expected current all-function core imports';index,pos=number(buf,pos);function_types.append(index);imports.append(dict(module=module,name=field,kind=kind,type=types[index]))
 assert pos==len(buf);buf=sections[3];count,pos=number(buf,0)
 for _ in range(count):index,pos=number(buf,pos);function_types.append(index)
 assert pos==len(buf);exports=[];buf=sections[7];count,pos=number(buf,0)
 for _ in range(count):
  field,pos=name(buf,pos);kind=buf[pos];pos+=1;index,pos=number(buf,pos);row=dict(name=field,kind=kind)
  if kind==0:row['type']=types[function_types[index]]
  else:assert kind in [1,2,3]
  exports.append(row)
 assert pos==len(buf)
 return dict(imports=sorted(imports,key=lambda r:(r['module'],r['name'],r['kind'])),exports=sorted(exports,key=lambda r:(r['name'],r['kind'])),nonFunctionExportLimitsOrGlobalValuesCompared=False,componentCapabilitiesProved=False)

def identity(row):
 s=Path(row['path']).stat();return dict(dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,mode=stat.S_IMODE(s.st_mode),mtimeNs=s.st_mtime_ns)

def main(authority_path):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
 root_row=descriptor(authority_path);a,p,w=authority(root_row);meta,protected,old_members=input_rows(p);expected,link_inputs=commands(p,w)
 for path in link_inputs:assert any(x['path']==path for x in protected),path
 baseline=Path(p['baselineRoot']);tree_roots={role:row['root']for role,row in meta['toolTreeInputs'].items()};tree_roots.update(nativeSource=str(baseline/'native-source'),embeddingSource=str(baseline/'componentize-source'))
 # Installed OpenSSL headers can be selected by the original -isystem flag.
 compile_argv=shlex.split(p['originalCompileRow']['command']);tree_roots['opensslHeaders']=compile_argv[compile_argv.index('-isystem')+1]
 before={name:tree_snapshot(path)for name,path in tree_roots.items()}
 initial=read(meta['initialTreeProtection'])
 for name in meta['toolTreeInputs']:assert before[name]==initial[name],'baseline tool tree differs: '+name
 assert not w.exists()and not w.is_symlink();starting_free=free_bytes(w.parent);assert starting_free>=p['disk']['startBytes'];os.umask(0o077);w.mkdir(mode=0o700)
 immutable_private=[];input_identities={row['path']:identity(row)for row in protected}
 result=dict(initialFreeBytes=starting_free,diskPolicy=p['disk'],schemaVersion=1,state='EXPERIMENTAL_MODULE_UTF16_NATIVE_DELTA_RUNNING_V1',phases=[],primaryError=None,collectorErrors=[],inputProtection=None,passed=False,engineOrGuestExecuted=False,fullBuildOrConfigureOrCargoExecuted=False)
 def recheck():
  checked(root_row);family(a['callerIndex']);family(p['afterimageFamily'])
  for row in protected+immutable_private:
   checked(row)
   if row['path']in input_identities:assert identity(row)==input_identities[row['path']],row['path']
  for name,path in tree_roots.items():assert tree_snapshot(path)==before[name],name
 def budget():
  return dict(freeBytes=free_bytes(w),privateBytes=private_bytes(w))
 def require_budget(value):
  assert value['freeBytes']>=p['disk']['stopBytes'],'limited phase free-space floor'
  assert value['privateBytes']<=p['disk']['maximumAcceptedPrivateBytes'],'limited persistent-output budget'
 try:
  for name in ['tmp','results','unused-cargo-home','unused-rust-target']:(w/name).mkdir(mode=0o700)
  save(w/'root-authority.json',a);save(w/'protection-before.json',before);copy_exclusive(p['afterimage'],w/'module-kernel.cpp',0o600);copy_exclusive(p['originalArchive'],w/'libbuiltin_node_compat.a',0o600)
  overlay=dict(version=0,**{'case-sensitive':True},**{'use-external-names':False},roots=[dict(type='file',name=p['originalCompileRow']['file'],**{'external-contents':str(w/'module-kernel.cpp')})]);save(w/'overlay.json',overlay);immutable_private.extend([descriptor(w/'overlay.json'),descriptor(w/'module-kernel.cpp')])
  env=environment(p,w);save(w/'environment.json',env);monitor=load_utility(p['monitor'],'genuine_0af_delta_monitor')
  for label,argv in expected:
   recheck();pre=budget();require_budget(pre);out=w/'results'/label;out.mkdir(mode=0o700);packet=dict(authority=descriptor(w/'root-authority.json'),label=label,argv=argv,cwd=str(w),environment=env);save(out/'packet.json',packet);monitor_dir=out/'owned-monitor';monitor_dir.mkdir(mode=0o700)
   terminal=monitor.monitor([sys.executable,'-B','-I',str(Path(__file__).resolve()),'--worker-packet',str(out/'packet.json')],str(w),env,monitor_dir,p['timeouts'][label],descriptor(w/'root-authority.json'));actual=read(descriptor(out/'worker-result.json'))if(out/'worker-result.json').exists()else None;post=budget()
   phase=dict(label=label,argv=argv,preBudget=pre,postBudget=post,outerTerminal=descriptor(monitor_dir/'terminal.json'),workerResult=descriptor(out/'worker-result.json')if actual else None);result['phases'].append(phase);save(out/'phase.json',phase);require_budget(post);recheck()
   assert terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['forcedCleanup']is False and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True
   for key in ['errors','signals','interruptedSignals','remainingObservedPids']:assert terminal[key]==[]
   assert actual and actual['rawChildExitCode']==0 and actual['lifecycleComplete']is True and actual['childStarted']is True and not actual['launcherErrors']and not actual['stoppedForDiskSpace']and not actual['stopReason']and not actual['sigtermReceived']
   c=actual['ownedGroupCleanup'];assert c['complete']is True and c['events']==[]and c['errors']==[]
   if label=='compile':
    known={str(Path(snapshot['root'])/row['path']):row for snapshot in before.values()for row in snapshot['entries']if row['kind']=='file'}
    deps=[]
    for dep in dependency_paths((w/'module-kernel.d').read_text()):
     if dep in [p['originalCompileRow']['file'],str(w/'module-kernel.cpp')]:deps.append(dict(path=dep,role='exact-vfs-afterimage',source=p['afterimage']));continue
     actual=Path(dep).resolve(strict=True);assert str(actual)in known,'dependency not authenticated before compile: '+dep
     row=known[str(actual)];observed=descriptor(actual);assert all(observed[k]==row[k]for k in ['sha256','bytes']);deps.append(dict(path=dep,physical=observed,role='authenticated-before-compile'))
    result['compileDependencies']=dict(depfile=descriptor(w/'module-kernel.d'),files=deps,allActualDependenciesAuthenticatedBeforeCompilation=True)
   if label=='ranlib':
    new_members=archive_members(w/'libbuiltin_node_compat.a');assert [x['name']for x in new_members]==[x['name']for x in old_members]
    for old,new in zip(old_members,new_members):
     if old['name']==p['archiveMember']:assert all(new[k]==descriptor(w/p['archiveMember'])[k]for k in ['sha256','bytes'])
     else:assert old==new
    result['archiveAudit']=dict(old=old_members,new=new_members,onlySelectedCodeMemberReplaced=True)
  result['commandsSucceeded']=True;copy_exclusive(descriptor(w/'raw.wasm'),w/'starlingmonkey_embedding.wasm',0o600);assert (w/'starlingmonkey_embedding.wasm').read_bytes()[:8]==b'\x00asm\x01\x00\x00\x00';result['engineCandidate']=descriptor(w/'starlingmonkey_embedding.wasm');result['coreSurface']=core_surface(w/'starlingmonkey_embedding.wasm');assert result['coreSurface']==core_surface(meta['engine']['path']),'changed core import/export names or function types';result['coreSurfaceMatchesBaseline']=True;result['finalBudget']=budget();require_budget(result['finalBudget'])
 except BaseException as error:result['primaryError']=dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc())
 finally:
  try:
   result['artifacts']=[descriptor(path)for path in [w/p['archiveMember'],w/'module-kernel.d',w/'libbuiltin_node_compat.a',w/'raw.wasm',w/'starlingmonkey_embedding.wasm']if path.exists()]
   metadata=dict(schemaVersion=1,metadataKind=p['newMetadataKind'],baselineResult=p['baselineResult'],baselineMetadata=p['baselineMetadata'],baselineReview=p['baselineReview'],baselineCompileDatabaseRows=80,unchangedBaselineCompileDatabaseRows=79,baselineSeparateEmbeddingRows=1,freshFrontendCompileRows=1 if result.get('compileDependencies')else 0,plannedFrontendCompileRows=1,freshCompileCommand=expected[0][1],compileDependencies=result.get('compileDependencies'),virtualOriginalSource=p['originalCompileSource'],actualAfterimage=p['afterimage'],sourceOverlay=descriptor(w/'overlay.json')if(w/'overlay.json').exists()else None,coreSurface=result.get('coreSurface'),coreImportsExportsAndFunctionTypesMatchBaseline=result.get('coreSurfaceMatchesBaseline')is True,additionalLinkFlags=p['additionalLinkFlags'],sourceChangeCount=1,baselineNativePolicyInputCount=435,baselineSupportCount=387,baselineEmbeddingInputCount=3,archiveAudit=result.get('archiveAudit'),phases=result['phases'],artifacts=result['artifacts'],engine=result.get('engineCandidate'),rootAuthority=descriptor(w/'root-authority.json')if(w/'root-authority.json').exists()else None,recipe=descriptor(__file__),intendedReuseOtherInputsReadOnly=True,all80FreshCompilationClaimed=False,linkMayPerformLTOBackendsForAllInputs=True,fullBuildOrConfigureOrCargoExecuted=False,oldMetadataProjected=False,engineOrGuestExecuted=False,runtimeAcceptance=False)
   save(w/'metadata.json',metadata);result['metadata']=descriptor(w/'metadata.json')
  except BaseException as error:result['collectorErrors'].append(dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc()))
  errors=[]
  try:
   last_budget=budget();require_budget(last_budget);assert last_budget['privateBytes']+len(json.dumps(result).encode())+4096<=p['disk']['maximumAcceptedPrivateBytes'];result['budgetBeforePublication']=last_budget
  except BaseException as error:result['collectorErrors'].append(dict(type=type(error).__name__,message=str(error),phase='final-output-budget'))
  try:recheck()
  except BaseException as error:errors.append(dict(type=type(error).__name__,message=str(error),stack=traceback.format_exc()))
  result['inputProtection']=dict(rows=len(protected),trees=len(tree_roots),unchanged=not errors,errors=errors,currentBeforePhaseFinalOnly=True)
  result['passed']=result.get('commandsSucceeded')is True and result['primaryError']is None and result['collectorErrors']==[]and not errors
  result['state']='EXPERIMENTAL_MODULE_UTF16_NATIVE_DELTA_COMPLETED_RUNTIME_PENDING_V1'if result['passed']else'EXPERIMENTAL_MODULE_UTF16_NATIVE_DELTA_FAILED_UNACCEPTED_V1'
  required=private_bytes(w)+len((json.dumps(result,indent=2)+'\n').encode())
  if required>p['disk']['maximumAcceptedPrivateBytes']:
   result['passed']=False;result['state']='EXPERIMENTAL_MODULE_UTF16_NATIVE_DELTA_FAILED_UNACCEPTED_V1';result['collectorErrors'].append(dict(type='OutputBudgetError',requiredBytes=required))
  try:save(w/'result.json',result)
  except BaseException as error:print(json.dumps(dict(publicationError=repr(error),wholeResult=result)),flush=True);return 1
 print(json.dumps(dict(result=descriptor(w/'result.json'),passed=result['passed'],engine=result.get('engineCandidate'),metadata=result.get('metadata'))),flush=True);return 0 if result['passed']else 1

if __name__=='__main__':
 parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--authority');group.add_argument('--worker-packet');args=parser.parse_args()
 raise SystemExit(worker(descriptor(args.worker_packet))if args.worker_packet else main(args.authority))
