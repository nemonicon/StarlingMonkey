"""Read-only actual-build DATA verifier. Default is portable text verification.
--current additionally reads/hashes original external artifacts and tool trees.
No subprocess, imports of candidate utilities, extraction or build/guest actions.
"""
from pathlib import Path
import argparse,collections,hashlib,json,os,posixpath,re,shlex,stat,tarfile
HERE=Path(__file__).resolve().parent

def digest(data):return hashlib.sha256(data).hexdigest()
def descriptor(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def clean(t):
 assert type(t['rawExitCode'])is int and t['rawExitCode']==0
 assert t['timeout']is False and t['forcedCleanup']is False and t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
 for k in ['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]

def verify(current=False):
 if (HERE/'index.json').exists():
  index=json.loads((HERE/'index.json').read_bytes());assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={x['path']for x in index['files']}|{'index.json'}
  for row in index['files']:
   p=HERE/row['path'];assert not p.is_symlink();observed=descriptor(p);assert all(observed[k]==row[k]for k in ['sha256','bytes'])
 manifest=json.loads((HERE/'capsule.json').read_bytes());archive=HERE/'raw-text.tar.gz';actual=descriptor(archive);assert all(actual[k]==manifest['archive'][k]for k in ['sha256','bytes'])
 rows={r['member']:r for r in manifest['files']};assert len(rows)==len(manifest['files'])and len(rows)==2526;data={}
 with tarfile.open(archive,'r:gz')as t:
  for item in t:
   assert item.isfile()and item.name in rows and item.name not in data and not Path(item.name).is_absolute()and'..'not in Path(item.name).parts
   b=t.extractfile(item).read();r=rows[item.name]['original'];assert len(b)==r['bytes']and digest(b)==r['sha256'];data[item.name]=b
 assert set(data)==set(rows);by_path={r['original']['path']:data[n]for n,r in rows.items()}
 def j(name):return json.loads(data[name])
 def ref(r):
  b=by_path[r['path']];assert len(b)==r['bytes']and digest(b)==r['sha256'];return b
 result=j('build/result.json');meta=j('build/metadata.json');a=j('build/root-authority.json');plan=j('inputs/plan');base=j('inputs/base-plan.json');comp=j('inputs/composition');work=Path(a['workRoot'])
 assert result['state']=='EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_COMPLETED_RUNTIME_PENDING_V1'and result['passed']is True and result['buildCommandSucceeded']is True
 assert result['primaryError']is None and result['postCollectionErrors']==[]and result['inputProtection']==dict(files=3542,wholeTrees=10,unchanged=True,errors=[],currentBeforeFinalOnly=True)
 assert meta['metadataKind']=='EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'and meta['engine']==result['engineCandidate']==manifest['engine']and result['metadata']==manifest['nativeMetadata']
 ref(result['metadata']);assert result['sourceComposition']==meta['sourceComposition']==a['composition'];ref(a['composition']);ref(a['entry']);ref(a['plan']);ref(a['callerIndex'])
 assert j('inputs/repo-authority.json')==a and a['state']=='ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1'and a['configureAllowed']is True and a['buildAllowed']is True and a['coherentPatchedIntlLibraryAndHeaders']is True
 for k in ['engineOrGuestExecutionAllowed','freezeAllowed','networkAllowed','rustupAllowed']:assert a[k]is False
 for k in ['old83MetadataProjected','engineExecuted','guestExecuted','adoption','originalExtractionWholeTreeAttestationClaimed']:assert meta[k]is False
 assert result['engineOrGuestExecuted']is False and result['adoption']is False
 assert meta['nativePolicyInputCount']==len(comp['files'])==435 and meta['nativePolicyInputManifest']==comp['files']
 support=base['supportCopies']+a['supportAdditions'];embedding=a['componentizeSources'];assert len(support)==meta['buildSupportInputCount']==387 and len(embedding)==meta['embeddingInputCount']==3
 assert meta['buildSupportInputManifest']==support and meta['embeddingInputManifest']==embedding
 expected={str(work/'native-source'/r['path']):dict(source=dict(path=str(Path(comp['sourceRoot'])/r['path']),sha256=r['sha256'],bytes=r['bytes']),mode=0o600)for r in comp['files']}
 for r in support:assert str(work/'native-source'/r['relativePath'])not in expected;expected[str(work/'native-source'/r['relativePath'])]=dict(source=r['source'],mode=r['mode'])
 for r in embedding:expected[str(work/'componentize-source'/r['relativePath'])]=dict(source=r['source'],mode=0o600)
 assert len(result['sourceCopies'])==len(expected)==825
 for r in result['sourceCopies']:
  e=expected[r['target']['path']];assert r['source']==e['source']and r['mode']==e['mode']and r['singleLink']is True and r['distinctInode']is True
  assert all(r['target'][k]==r['source'][k]for k in ['sha256','bytes'])
 after={r['path']:r for r in result['sourceAfter']};assert len(after)==435 and result['sourceAfter']==meta['compiledAfterInputs']==j('build/configured-inputs.json')
 for r in comp['files']:
  target=after[str(work/'native-source'/r['path'])];assert all(target[k]==r[k]for k in ['sha256','bytes'])
 db=j('configured/compile_commands.json');assert db==meta['actualCompileRows']and len(db)==80 and len({r['file']for r in db})==80;ref(meta['compileDatabase'])
 node=[];groups=collections.Counter()
 for r in db:
  file=Path(r['file']);tokens=shlex.split(r['command']);assert tokens[0]in [str(work/'build/cxx-wrapper'),str(Path(a['reusedTrees']['wasi-sdk']['root'])/'bin/clang')]and '--target=wasm32-wasi'in tokens and '-DNDEBUG'in tokens
  if tokens[0]!=str(work/'build/cxx-wrapper'):assert file==work/'native-source/host-apis/wasi-0.2.10/bindings/bindings.c'
  assert '-c'in tokens and tokens[tokens.index('-c')+1]==str(file)and r['directory']==str(work/'build')
  if file==work/'build/starling-raw.wasm/null.cpp':assert '-include'not in tokens
  else:assert '-include'in tokens and tokens[tokens.index('-include')+1]==a['smConfdefsHeader']['path']
  if work/'native-source'in file.parents:
   assert str(file)in after;rel=file.relative_to(work/'native-source').as_posix();groups[rel.split('/')[0]]+=1
   if rel.startswith('builtins/node-compat/'):node.append(r)
  else:assert file==work/'build/starling-raw.wasm/null.cpp';groups['generated']+=1
 assert dict(groups)==dict(builtins=61,runtime=13,**{'host-apis':4,'crates':1,'generated':1})and len(node)==15
 required=['NODE_COMPAT_ASYNC_LOCAL_STORAGE','NODE_COMPAT_CRYPTO_HASH_HMAC','NODE_COMPAT_CRYPTO_RANDOM','NODE_COMPAT_ENTROPY_POLICY','NODE_COMPAT_ENTROPY_RUNTIME_ONLY','NODE_COMPAT_CLASSIC_STREAMS_TOWEB','NODE_COMPAT_FS','NODE_COMPAT_MODULE','NODE_COMPAT_NEXT_HTTP','NODE_COMPAT_NEXT_IMPORTS','NODE_COMPAT_NEXT_PERFORMANCE','NODE_COMPAT_NEXT_STARTUP','NODE_COMPAT_TIMERS','NODE_COMPAT_VM_DATA','NODE_COMPAT_ZLIB_STREAMING','NODE_COMPAT_STRICT_INITIALIZATION']
 for r in node:
  tokens=shlex.split(r['command']);assert all('-D'+k+'=1'in tokens for k in required)
  assert not any(x in r['command']for x in ['-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_CRYPTO_AUDITED_BORROW','-DJS_DEBUG'])
 ninja=ref(meta['wholeNinjaCommands']).decode();separate=[x for x in ninja.splitlines()if ' -c '+str(work/'componentize-source/embedding/embedding.cpp')in x]
 assert separate==meta['actualSeparateEmbeddingCompileRows']and len(separate)==1;assert a['smConfdefsHeader']['path']in separate[0]and '-DNODE_COMPAT_ASYNC_LOCAL_STORAGE=1'in separate[0]
 link=[x for x in ninja.splitlines()if a['smLibrary']['path']in x];assert len(link)==1 and 'librust_staticlib.a'in link[0]and'libcrypto.a'in link[0]and'libbuiltin_componentize_embedding.a'in link[0]
 assert '--allow-undefined'not in link[0]and'--import-undefined'not in link[0]
 assert len(meta['linkAndRustInputs'])==len(result['linkInputs'])==1078 and meta['linkAndRustInputs']==result['linkInputs']
 lock=ref(meta['actualRustConfiguration']['lock']);assert lock==ref(a['intlLockfile'])and len(re.findall(rb'^\[\[package\]\]$',lock,re.M))==84
 cargo=ref(meta['actualRustConfiguration']['manifest']).decode();tail=cargo.split('[dependencies]',1)[1].split('\n[',1)[0];names=re.findall(r'^([A-Za-z0-9_-]+)\s*=',tail,re.M)
 assert names==meta['actualRustConfiguration']['dependencyNames']and set(names)==set(plan['requiredAggregateDependencyNames'])and len(names)==6
 assert 'default-features = false'in tail and 'features = ["any_provider", "compiled_data", "segmenter", "calendar"]'in tail
 assert 'ca612daf1c08c53abe07327cb3e6ef6e0a760f0c'in cargo and a['reusedTrees']['intl-firefox']['root']in cargo
 for k in ['smSavedFrameHeader','smConfigHeader','smConfdefsHeader']:ref(a[k])
 assert re.search(rb'^#define JS_HAS_SAVEDFRAME_IS_EVAL 1$',ref(a['smSavedFrameHeader']),re.M)and b'GetSavedFrameIsEval'in ref(a['smSavedFrameHeader'])
 assert re.search(rb'^#define JS_HAS_INTL_API 1$',ref(a['smConfigHeader']),re.M)and ref(a['smConfdefsHeader'])!=b'// Placeholder\n'
 assert meta['actualLibrary']==a['smLibrary']and meta['actualSavedFrameHeader']==a['smSavedFrameHeader']and meta['actualConfigHeader']==a['smConfigHeader']and meta['actualConfdefs']==a['smConfdefsHeader']
 evidence=json.loads(ref(a['spidermonkeyEvidence']));assert evidence['coherentPatchedIntlLibraryAndHeaders']is True and evidence['smLibrary']==a['smLibrary']and evidence['smSavedFrameHeader']==a['smSavedFrameHeader']
 selection=meta['selectedModuleManifests'];assert len(selection['public'])==22 and len(selection['private'])==2
 for r in selection['public']+selection['private']:assert json.loads(ref(r['descriptor']))==r['wholeManifest']
 labels=['rust-version','cargo-version','rust-sysroot','configure','build','ninja-commands'];assert [r['label']for r in result['phases']]==labels and result['phases']==meta['phases'];min_disk=None
 env=j('build/environment-policy.json')['environment'];assert env['CARGO_NET_OFFLINE']=='true'and env['CARGO_BUILD_JOBS']=='1'and env['CARGO_INCREMENTAL']=='0'and env['RUSTC']==a['rustc']['path']and env['CARGO_HOME']==str(work/'cargo-home')
 assert not any(x.startswith('RUSTUP_')for x in env)
 for phase in result['phases']:
  label=phase['label'];prefix='phases/'+label+'/';packet=j(prefix+'packet.json');worker=json.loads(ref(phase['workerResult']));terminal=json.loads(ref(phase['outerTerminal']));started=j(prefix+'owned-monitor/started.json');clean(terminal)
  assert type(phase['rawExitCode'])is int and phase['rawExitCode']==phase['outerRawExitCode']==0 and phase['innerOwnedClean']is True and phase['ownedGone']is True and phase['timeout']is False and phase['forcedCleanup']is False
  for k in ['errors','signals','interruptedSignals','remainingObservedPids']:assert phase[k]==[]
  assert worker['argv']==phase['argv']==packet['argv']and packet['cwd']==str(work)and packet['environment']==env
  assert worker['rawChildExitCode']==0 and worker['childStarted']is True and worker['lifecycleComplete']is True and worker['stoppedForDiskSpace']is False and worker['stopReason']is None and type(worker['sigtermReceived'])is int and worker['sigtermReceived']==0 and worker['launcherErrors']==[]
  cleanup=worker['ownedGroupCleanup'];assert cleanup['complete']is True and cleanup['events']==[]and cleanup['errors']==[]
  assert json.loads(ref(terminal['stdout']))==worker and ref(terminal['stderr'])==b''and ref(worker['rawCombinedLog'])==data[prefix+'command.combined.log']
  assert '--worker-packet'in started['argv']and started['argv'][3]==a['entry']['path']
  assert all(x['bytes']>=1024**3 for x in worker['diskSamples']);n=min(x['bytes']for x in worker['diskSamples']);min_disk=n if min_disk is None else min(min_disk,n)
 assert 'release: 1.88.0'in data['phases/rust-version/command.combined.log'].decode()and data['phases/cargo-version/command.combined.log'].startswith(b'cargo 1.88.0 ')
 assert data['phases/rust-sysroot/command.combined.log'].decode().strip()==a['reusedTrees']['rust']['root']
 top=j('root-monitor/terminal.json');clean(top);assert ref(top['stderr'])==b'';jsonl=[json.loads(line)for line in ref(top['stdout']).splitlines()];assert len(jsonl)==7;assert jsonl[:-1]==[dict(pid=j('phases/'+label+'/owned-monitor/started.json')['pid'],timeoutSeconds=j('phases/'+label+'/owned-monitor/started.json')['timeoutSeconds'])for label in labels];assert jsonl[-1]==dict(result=manifest['actualResult'],passed=True,engine=manifest['engine'],metadata=manifest['nativeMetadata'])
 topstart=j('root-monitor/started.json');assert topstart['argv'][3]==a['entry']['path']and topstart['argv'][-1]==rows['inputs/repo-authority.json']['original']['path'];ref(topstart['authority'])
 for k,v in meta['requestedCMake'].items():assert meta['observedCMake'][k]['value']==v
 for k in ['NODE_COMPAT_GC_STRESS','NODE_COMPAT_OOM_TESTING','NODE_CRYPTO_AUDITED_BORROW','ENABLE_JS_DEBUGGER','WEVAL']:assert meta['requestedCMake'][k]=='OFF'
 assert meta['requestedCMake']['SPIDERMONKEY_INTL']=='ON'and meta['requestedCMake']['NODE_COMPAT_LOCKED_RUST']=='ON'and meta['requestedCMake']['NODE_COMPAT_PREINSTALLED_RUST']=='ON'and meta['requestedCMake']['Rust_RESOLVE_RUSTUP_TOOLCHAINS']=='OFF'
 assert meta['observedCMake']['NODE_COMPAT_PREINSTALLED_RUST_CHANNEL']['value']=='1.88.0'
 observed=json.loads((HERE/'engine-import-observation.json').read_bytes());assert observed['engine']==manifest['engine']and observed['format']=='core-wasm-v1'and observed['nativeGetSavedFrameIsEvalImportedUnresolved']is False and observed['componentInterfaceVersionsOrCapabilitiesProved']is False
 current_rows=0;current_trees=0
 if current:
  expectations={}
  def checked(r):
   nonlocal current_rows
   if r['path']in expectations:assert expectations[r['path']]==r;return
   p=Path(r['path']);assert p.is_absolute()and'..'not in p.parts
   for q in (p,*p.parents):assert not q.is_symlink(),q
   assert descriptor(p)==r,p;expectations[r['path']]=r;current_rows+=1
  # Full declared source/input boundary derived as data, never imports/calls
  # the candidate's input/bootstrap/recheck/admit/helper functions.
  fixed=[a[k]for k in ['entry','plan','callerIndex','composition','installedGeneratorResult','intlLockfile','offlineCargoConfig','intlCargoAudit','spidermonkeyEvidence','savedFramePatchIndex','cargo','rustc','smLibrary','smSavedFrameHeader','smConfigHeader','smConfdefsHeader']]
  fixed += [plan[k]for k in ['baseRunner','basePlan','portableBaseMap','baseBuildResult']]+comp['inputs']+[base[k]for k in ['cbindgen','cpmModule','monitor','lifecycle']]+[x['executable']for x in base['hostTools']if x['name']not in ['rustup','cargo','rustc']]
  fixed += [dict(path=str(Path(comp['sourceRoot'])/r['path']),sha256=r['sha256'],bytes=r['bytes'])for r in comp['files']]+[r['source']for r in support+embedding]
  old=json.loads(Path(plan['baseBuildResult']['path']).read_bytes());fixed += [old['engineCandidate'],old['metadata']]+old['sourceAfter']+[x['target']for x in old['sourceCopies']if '/componentize-source/'in x['target']['path']]
  for tree in a['reusedTrees'].values():
   fixed += [tree['inventory'],tree['provenance']]
   if 'archive'in tree:fixed.append(tree['archive'])
  fixed.append(next(x['archive']for x in old['archives']if x['role']=='openssl'))
  for r in fixed:checked(r)
  assert len(expectations)==3542
  for r in manifest['files']:checked(r['original'])
  for r in [manifest['engine'],*meta['linkAndRustInputs'],*meta['compiledAfterInputs']]:checked(r)
  for copied in result['sourceCopies']:
   p=Path(copied['target']['path']);s=p.stat();assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==copied['mode']
  before=j('build/protection-before.json');assert set(before)==set(a['reusedTrees'])and len(before)==10
  for role,snapshot in before.items():
   root=Path(snapshot['root']);s=root.stat();assert dict(mode=stat.S_IMODE(s.st_mode),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,mtimeNs=s.st_mtime_ns)==snapshot['rootIdentity']
   actual_names={p.relative_to(root).as_posix()for p in root.rglob('*')};assert actual_names=={r['path']for r in snapshot['entries']}
   for r in snapshot['entries']:
    p=root/r['path'];s=p.lstat();assert dict(mode=stat.S_IMODE(s.st_mode),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,mtimeNs=s.st_mtime_ns)=={k:r[k]for k in ['mode','dev','ino','nlink','mtimeNs']}
    if r['kind']=='file':assert stat.S_ISREG(s.st_mode);checked(dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']))
    elif r['kind']=='symlink':assert stat.S_ISLNK(s.st_mode)and os.readlink(p)==r['target'];target=p.resolve(strict=True);assert root in target.parents or target==root
    else:assert r['kind']=='directory'and stat.S_ISDIR(s.st_mode)
   current_trees+=1
 return dict(schemaVersion=1,state='INDEPENDENT_ACTUAL_NEXT_INTL_NATIVE_BUILD_DATA_REVIEW_PASSED_V1',portableTextFiles=len(rows),engine=manifest['engine'],nativeMetadata=manifest['nativeMetadata'],actualResult=manifest['actualResult'],native435=True,support387=True,embedding3=True,freshCompileDatabaseRows=80,nativeSourceCompileRows=79,generatedNullCompileRows=1,separateEmbeddingCompileRows=1,nodeCppRows=15,aggregateRustPackages=84,aggregateRootDependencies=6,sourceCopies=825,rawOwnedPhases=6,rawOwnedRoot=1,minimumObservedFreeBytes=min_disk,currentExternalReadback=current,currentExternalRows=current_rows,currentWholeTrees=current_trees,sourceCallerAuthorRelationshipDisclosed=True,engineOrGuestExecutedByReviewer=False,guestRuntimeOrComponentInterfaceAdmission=False,old83MetadataProjected=False)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--current',action='store_true');args=parser.parse_args();print(json.dumps(verify(args.current),indent=2))
