"""Independent actual compile/link/library/metadata DATA; no owner/tool execution."""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,struct,tarfile,importlib.util,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;d=json.loads((P/'audit-data.json').read_text());seen={};checks=0

def need(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def verify(path,sha=None,size=None):
 path=Path(path);a=path.lstat();need(stat.S_ISREG(a.st_mode),'Ordinary actual witness');h=hashlib.sha256();n=0
 with path.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b);n+=len(b)
 b=path.lstat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns,a.st_mode)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns,b.st_mode),'Stable actual witness bytes/mode');need((sha is None or h.hexdigest()==sha)and(size is None or n==size),'Exact actual witness digest/size')
 seen[str(path)]=dict(path=str(path),sha256=h.hexdigest(),bytes=n);return seen[str(path)]
def data(r):verify(r['path'],r['sha256'],r.get('bytes'));return json.loads(Path(r['path']).read_text())
def filebyhash(path,sha):r=verify(path,sha);return Path(path).read_bytes()
def dump(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
m=data(d['metadata']);source=Path(d['configuredSourceRoot']);work=Path(d['workRoot']);build=Path(m['cmakeCachePath']).parent;controller=P.parent/'combined-clock-diagnostics-native-integration-candidate-v3';refs=json.loads((controller/'references.json').read_text());spec=data(refs['policy']);base=data(spec['basePolicy'])
modelFile=Path(refs['metadataModel']['path']);verify(modelFile,refs['metadataModel']['sha256'],refs['metadataModel']['bytes']);modelSpec=importlib.util.spec_from_file_location('independent_actual_clock357_pure_metadata_model',modelFile);model=importlib.util.module_from_spec(modelSpec);modelSpec.loader.exec_module(model)
policy=model.assemble_policy(spec,base)
classification=model.validate_metadata(m,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
need(classification==json.loads(Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-build-result/result.json').read_bytes())['metadataClassification'],'Whole genuine82 pure shape return')
need(len(m)==82 and m['sourceManifest']==policy['expectedNativeSourceManifest']and len(m['sourceManifest'])==357 and m['componentizeSourceManifest']==policy['expectedComponentizeSourceManifest']and len(m['componentizeSourceManifest'])==3,'Exact current82-field diagnostic357+3 metadata,not combined80 or secret75')
need(m['selectedModuleManifests']==policy['selectedModuleManifests']and len(m['selectedModuleManifests'])==11 and m['classicTraceSourcePolicy']==policy['classicTraceSourcePolicy'],'Complete real11 manifests and original Source policy')
for item in m['sourceManifest']:verify(source/item['path'],item['sha256'])
for item in m['selectedModuleManifests']:
 raw=filebyhash(source/item['path'],item['sha256']);value=json.loads(raw);need(value in m['combinedNativeSourcePolicy']['selectedManifests'],'Whole actual selected JSON,not fabricated count')
need(m['enginePath']==d['engine']['path']and m['engineSha256']==d['engine']['sha256']and m['engineBytes']==d['engine']['bytes']and Path(d['engine']['path']).read_bytes()[:8]==b'\0asm\1\0\0\0','Actual native core-Wasm header/engine relation,no execution/decoder')
for k in ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled']:need(m[k]is False,'Ordinary normalOFF '+k)
need(m['entropyPolicy']=='off'and m['hostApi']=='wasi-0.2.10'and m['requestedCMakeOptions']==m['observedCMakeOptions'],'Whole selected noentropy host policy/configuration')
cachetext=filebyhash(m['cmakeCachePath'],m['cmakeCacheSha256']).decode();cache={}
for line in cachetext.splitlines():
 k,sep,v=line.partition(':')
 if sep and '='in v:cache[k]=v.partition('=')[2]
for k,v in m['observedCMakeOptions'].items():need(cache[k]==v,'Actual cached configured option '+k)
need(cache['CMAKE_BUILD_TYPE']=='Release'and cache['NODE_COMPAT_GC_STRESS']==cache['NODE_COMPAT_OOM_TESTING']=='OFF'and cache['NODE_COMPAT_ENTROPY_MODE']=='OFF'and cache['WASI_SDK_VERSION']=='30','Actual Release/OFF/noOOM/SDK30')
ext=Path(cache['CMAKE_HOME_DIRECTORY']);need(str(ext)==m['combinedNativeSourcePolicy']['externalConfiguredSourceRoot']and str(ext).startswith(str(work)+'/'),'Real new external ABI source context')
for item in m['componentizeSourceManifest']:verify(ext/item['path'],item['sha256'])
stem=Path(d['engine']['path']).stem
for prefix,sha,expected in [('source-inputs-',m['sourceInputManifestSha256'],m['sourceManifest']),('componentize-native-inputs-',m['componentizeInputManifestSha256'],m['componentizeSourceManifest'])]:need(json.loads(filebyhash(work/(prefix+stem+'.json'),sha))==expected,'Whole genuine pre-build Source snapshot')
need(filebyhash(work/('recipe-'+stem+'.sha256'),None).decode().strip()==m['buildRecipeSha256']==refs['recipe']['sha256'],'Actual own recipe before/after binding')
fresh=m['combinedNativeSourcePolicy']['freshAbiEvidence'];freshfile=m['combinedNativeSourcePolicy']['freshAbiEvidenceFile'];need(json.loads(filebyhash(freshfile['path'],freshfile['sha256']))==fresh and fresh['sourceDir']==str(ext)and fresh['buildDir']==str(build)and fresh['artifact']==d['engine']['path'],'Whole actual fresh ABI observation')
for k in ['sourceDirExisted','buildDirExisted','artifactExisted','compilerLauncherReuseAllowed','rustIncrementalReuseAllowed']:need(fresh[k]is False,'Fresh/nonreuse actual '+k)
db=json.loads(filebyhash(m['compileCommandsPath'],m['compileCommandsSha256']));need(len(db)==69,'Actual69 compiler DB rows');native_names={r['path']for r in m['sourceManifest']};policy_names={r['path']for r in m['sourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))};need(len(policy_names)==63,'Genuine selected63 policy CPP sources')
classified=[];commands={};objects=[]
for r in db:
 words=shlex.split(r['command']);need(words.count('-c')==words.count('-o')==1 and words[words.index('-c')+1]==r['file']and '--target=wasm32-wasi'in words and [w for w in words if w.startswith('-O')]==['-O3']and '-DNDEBUG'in words and '-fsyntax-only'not in words,'Actual finite Release compile command input/output')
 need(not any(w.startswith(('@','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY','-DDEBUG'))for w in words),'No diagnostic/GC/OOM/runtimeentropy/response compilation')
 path=Path(r['file']);name=path.relative_to(source).as_posix()if path.is_relative_to(source)else None
 if name:
  need(name in native_names,'Every configured command source in real357');kind='policy'if name in policy_names else'other-configured';commands[name]=r['command']
 else:need(path==build/'starling-raw.wasm/null.cpp','Only generated null outside configured SOURCE');kind='generated-null';verify(path)
 if kind=='policy':
  for macro in ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_ENTROPY_POLICY','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER']:need('-D'+macro+'=1'in words,'Required native macro '+macro)
  for macro,on in [('NODE_COMPAT_CLASSIC_STREAMS',name in policy['privateTargetCpp']),('NODE_COMPAT_STREAM_CONSUMERS',name in policy['privateTargetCpp']),('NODE_COMPAT_ZLIB',name.startswith('builtins/node-compat/')),('NODE_COMPAT_STREAM_WEB',name.startswith('builtins/node-compat/'))]:need([w for w in words if w=='-D'+macro or w.startswith('-D'+macro+'=')]==(['-D'+macro+'=1']if on else[]),'Exact selected/private layout macro '+macro)
 obj=Path(words[words.index('-o')+1]);obj=obj if obj.is_absolute()else Path(r['directory'])/obj;verify(obj);raw=obj.read_bytes()[:8];need(raw[:8]==b'\0asm\1\0\0\0'or raw[:4]in[b'BC\xc0\xde',b'\xde\xc0\x17\x0b'],'Actual Wasm/LLVM object magic');objects.append(seen[str(obj)]);classified.append(dict(file=str(path),kind=kind))
need({k:sum(x['kind']==k for x in classified)for k in ['policy','other-configured','generated-null']}==dict(policy=63,**{'other-configured':5,'generated-null':1}),'Actual69=63policy+5other+1null;no embedding DB row')
need(set(m['combinedNativeSourcePolicy']['actualPolicyCppCompileCommands'])=={commands[n]for n in policy_names}and m['internalTickPolicy']['actualLayoutCompileCommands']==m['combinedNativeSourcePolicy']['actualPolicyCppCompileCommands'],'Every exact policy compiler witness from current DB')
for values,count in [(m['strictEventExceptionPolicy']['actualNativeCompileCommands'],4),(m['classicStreamsPolicy']['actualPrivateTargetCompileCommands'],6),(m['cryptoKeyOwnershipBuildEvidence']['changedNativeCompileCommands'],3),(m['cryptoSecretFailureBuildEvidence']['changedNativeCompileCommands'],2),(m['taskSelectionPolicy']['actualEventLoopCompileCommands'],1),(m['taskSelectionPolicy']['actualHostApiCompileCommands'],1)]:need(len(values)==count and all(v in commands.values()for v in values),'Current strict/private/crypto/secret/task witness exact')
emb=m['actualEmbeddingCompileCommands'];need(len(emb)==1 and emb==m['combinedNativeSourcePolicy']['actualSeparateEmbeddingCompileCommands']==m['internalTickPolicy']['actualEmbeddingCompileCommands'],'Genuine separate embedding1,not compileDB projection');ew=shlex.split(emb[0]);need(ew[ew.index('-c')+1]==str(ext/'embedding/embedding.cpp')and ew[0]==str(work/'cache/wasi-sdk/85e6/bin/clang++')and '-O3'in ew and '-DNDEBUG'in ew and not any(w.startswith(('-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-flto','@'))for w in ew),'Actual separate Release embedding source/flags')
verify(build/ew[ew.index('-o')+1]);verify(build/'build.ninja');verify(build/'CMakeFiles/rules.ninja');ninja=(build/'build.ninja').read_text();need(str(ext/'embedding/embedding.cpp')in ninja and ew[ew.index('-o')+1]in ninja,'Actual current parentNinja separate embedding source/output')
install=m['zlibPolicy']['codecWitness']['install'];text=filebyhash(install['path'],install['sha256']).decode()
for name in ['builtins::web::timers','builtins::web::crypto','builtins::node_compat','componentize::embedding']:need(text.count('NS_DEF('+name+')')==1,'Actual single installation '+name)
for mk,pk in [('cryptoKeyOwnershipPolicy','cryptoKeyOwnershipSourcePolicy'),('cryptoSecretFailureSourcePolicy','cryptoSecretFailureSourcePolicy')]:need(m[mk]==policy[pk],'Whole current native crypto Source policy')
for mk,pk in [('resourceOwnershipPolicy','resourceOwnershipSourcePolicy'),('taskSelectionPolicy','taskSelectionSourcePolicy'),('zlibErrorSemanticsPolicy','zlibErrorSemanticsSourcePolicy'),('combinedNativeSourcePolicy','combinedSourcePolicy')]:need(m[mk]['sourcePolicy']==policy[pk]and m[mk]['policyFileSha256']==refs['policy']['sha256']and m[mk]['helperSha256']==refs['helper']['sha256'],'Whole actual current combined Source policy '+mk)
need(m['taskSelectionPolicy']['nativeAllInvalidRuntimeValidation']is None and m['resourceOwnershipPolicy']['nativeRuntimeValidation']is None and m['combinedNativeSourcePolicy']['runtimeValidation']is None and m['zlibErrorSemanticsPolicy']['remainingDeviationsApproved']is False,'No runtime/task/reset/remaining-zlib deviation acceptance')
rust=m['generatedRustProject']
for key,sha in [('manifestPath','manifestSha256'),('lockPath','lockSha256'),('versionedLockPath','versionedLockSha256')]:verify(rust[key],rust[sha])
need(Path(rust['lockPath']).read_bytes()==Path(rust['versionedLockPath']).read_bytes()and rust['cargoBuildLocked']is rust['manifestAndLockCheckedBeforeAndAfterBuild']is True and len(rust['actualCargoBuildCommands'])==1,'Real generated/versioned lockedRust exact')
cargo=shlex.split(rust['actualCargoBuildCommands'][0]);need('--release'in cargo and '--locked'in cargo and '--target=wasm32-wasip1'in cargo and '--target-dir'in cargo,'Actual bounded private lockedRust command')
for value in cargo:
 if value.startswith('CARGO_BUILD_RUSTC='):verify(value.split('=',1)[1])
 elif value.endswith('/bin/cargo'):verify(value)
wrapper=filebyhash(build/'cxx-wrapper',None).decode();need(str(work/'cache/wasi-sdk/85e6/bin/clang++')in wrapper and str(source/'scripts')in wrapper,'Real compiler wrapper selects newSDK/genuineSource scripts')
w=m['zlibPolicy']['codecWitness'];need(w['runtimeBackendProof']==m['zlibPolicy']['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)and w['guestExecuted']is False and w['sourceInputsCheckedBeforeAndAfterBuild']is True,'Backend runtime proof remains false/null/null')
for r in w['witnessFiles']:verify(r['path'],r['sha256'],r['bytes'])
need(w['selectedCompileInput']==m['zlibSelectedCodecInput']and w['actualKernelCompileCommands']==[commands['builtins/node-compat/zlib/kernel.cpp']],'Selected codec actual kernel/source tuple')
raw=filebyhash(w['postBuildLinkEvidence']['path'],w['postBuildLinkEvidence']['sha256']).decode();linkline,=[x for x in raw.splitlines()if'libspidermonkey.a'in x and' -c 'not in x];parts=[shlex.split(x)for x in linkline.split(' && ')];need(parts[0]==[':']and len(parts)==4,'Genuine compiler/cd/in-place optimizer compound');compiler,cd,opt=parts[1:];target=build/compiler[compiler.index('-o')+1]
expected=dict(rawCommand=linkline,expandedArguments=compiler,kind='compiler-cd-inplace-wasm-opt-v1',compilerArguments=compiler,compilerExpandedArguments=compiler,compilerOutputPath=str(target),postOptimizerArguments=opt,postOptimizerWorkingDirectory=cd[1],postOptimizerInputPath=str(target),postOptimizerOutputPath=str(target),sameWasmOutputProved=True)
need(w['postBuildLinkEvidence']['commands']==[expected]and w['postBuildLinkEvidence']['responseFiles']==[]and w['postBuildLinkEvidence']['beforeBuildCaptureExists']is False,'Entire compound link witness independently reconstructed')
need((Path(cd[1])/opt[-1]).resolve()==target and opt[1:]==['--strip-debug','-O3','-o','starling-raw.wasm','starling-raw.wasm'],'Same in-place output and exact optimizer flags');verify(target,d['engine']['sha256'],d['engine']['bytes']);verify(ext/'lib/starlingmonkey_embedding.wasm',d['engine']['sha256'],d['engine']['bytes']);need(target.stat().st_ino!=Path(d['engine']['path']).stat().st_ino,'Final engine copy byte-exact independent inode')
archives=[]
for name in compiler:
 if name.endswith('.a'):
  q=Path(name)if name.startswith('/')else build/name;archives.append(verify(q))
need(len(archives)>0 and len({r['path']for r in archives})>0,'Actual ordered static library arguments measured, not inferred from historical build')
nm=w['archiveSymbolEvidence'];verify(nm['nm']['path'],nm['nm']['sha256'],nm['nm']['bytes']);need(nm['exitCode']==0 and len(nm['selectedDefinitions'])==7,'Captured nm raw0/seven selected symbols,no rerun');nmstdout=Path(next(r['path']for r in w['witnessFiles']if r['path'].endswith('nm.stdout.txt'))).read_text()
for name,line in nm['selectedDefinitions'].items():need(line in nmstdout and len(re.findall(r'\bMOZ_Z_'+re.escape(name)+r'\s+T\s',nmstdout))==1,'Unique actual captured selected archive definition '+name)
ssl=m['openssl'];audit=ssl['completeSourceAudit'];before=json.loads(filebyhash(audit['beforeReportPath'],audit['beforeReportSha256']));need(all(audit[k]==v for k,v in before.items())and audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True and audit['unexpectedFiles']==audit['missingFiles']==[]and ssl['version']=='3.0.17'and ssl['entropy']=='OFF'and ssl['randSeed']=='none','Actual complete before/after OpenSSL Source receipt')
verify(audit['archivePath'],audit['archiveSha256']);expected_ssl={}
with tarfile.open(audit['archivePath'])as tar:
 for member in tar:
  if member.isfile():
   prefix,sep,name=member.name.partition('/');need(prefix=='openssl-3.0.17'and sep and name not in expected_ssl,'Finite unique regular OpenSSL archive Source member');expected_ssl[name]=audit['patchedSources'].get(name)or hashlib.sha256(tar.extractfile(member).read()).hexdigest()
root=Path(audit['sourceDirectory']);actual={}
for q in sorted(root.rglob('*')):
 need(not q.is_symlink(),'No unexpected OpenSSL Source alias')
 if q.is_file():actual[q.relative_to(root).as_posix()]=verify(q)['sha256']
need(actual==expected_ssl and len(actual)==4650,'All4650 actual patched/source archive bytes and exact file membership')
canonical=[dict(path=n,sha256=h)for n,h in sorted(actual.items())];need(hashlib.sha256(json.dumps(canonical,separators=(',',':')).encode()).hexdigest()==audit['sourceManifestSha256'],'Actual lexical-relative-path canonical OpenSSL Source digest')
for key in ['configureRecipe','configdata']:r=ssl[key];verify(r['path'],r['sha256']);need(seen[r['path']]['bytes']>0,'Actual missing descriptor sizes measured '+key)
need(Path(ssl['configureRecipe']['path']).read_text()==ssl['configureRecipe']['contents']and '--with-rand-seed=none'in ssl['configureRecipe']['contents']and '--release;-O3'in ssl['configureRecipe']['contents'],'Actual original OpenSSL configure text,not metadata projection');verify(ssl['receiptPath'],ssl['receiptSha256']);verify(ssl['library']['path'],ssl['library']['sha256'],ssl['library']['bytes'])
lib=Path(ssl['library']['path']).read_bytes();need(lib[:8]==b'!<arch>\n','Actual ordinary GNU static library');pos=8;boundaries=set();symtab=None
while pos<len(lib):
 boundaries.add(pos);header=lib[pos:pos+60];need(len(header)==60 and header[-2:]==b'`\n','Complete static archive header');length=int(header[48:58].strip());name=header[:16].strip();blob=lib[pos+60:pos+60+length];need(len(blob)==length,'Complete static archive member bytes')
 if name==b'/':symtab=blob
 pos+=60+length+(length&1)
need(pos==len(lib)and symtab is not None,'Whole GNU archive symbol table boundary');count=struct.unpack('>I',symtab[:4])[0];offsets=struct.unpack('>'+str(count)+'I',symtab[4:4+4*count]);names=symtab[4+4*count:].split(b'\0');need(len(names)>=count and all(o in boundaries for o in offsets),'All actual symbol definitions point into members')
required=['BN_free','BN_clear_free','EVP_PKEY_free','EVP_PKEY_CTX_free','CRYPTO_free','OSSL_PARAM_BLD_free','EVP_MAC_CTX_free'];cleanup={}
for name in required:
 needle=name.encode();need(names[:count].count(needle)==1,'Unique linked archive cleanup symbol '+name);i=names.index(needle);cleanup[name]=offsets[i]
for r in m['downloadedArchives']:verify(r['path'],r['sha256'])
for r in m['wasiSdkVersionFiles']:need(filebyhash(r['path'],None).decode()==r['contents']and r['contents'].startswith('30.0\n')and'Llvm'not in r['contents']and'llvm-version: 21.1.4'in r['contents'],'Actual SDK30/LLVM21.1.4 version file')
log=Path(d['buildLog']['path']).read_text();need(sum(c['command']in log for c in db)==0 and emb[0]not in log,'Explicit qualification: compileDB/Ninja/fresh objects,not per-command raw terminal strings')
diagnostic=model.classify_diagnostic_commands(policy,db,emb,m['requestedCMakeOptions'],m['observedCMakeOptions'])
need(diagnostic==m['clockLifecycleDiagnosticBuildEvidence']['actualSharedCompileCommands']and len(diagnostic)==7,'All six native shared TUs plus separate embedding diagnostic flags')
need(text.count('NS_DEF(diagnostics::clock_lifecycle)')==1,'Actual one diagnostic installation')
need('NODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1'in (source/'include/clock-lifecycle-diagnostics.h').read_text()or 'NODE_COMPAT_LIFECYCLE_DIAGNOSTICS'in (source/'include/clock-lifecycle-diagnostics.h').read_text(),'Real private diagnostic header selected')
negative=[]
import copy
for name,mutate in [('extra-raw-field',lambda x:x.update(unreviewedField=True)),('missing-native-source',lambda x:x['sourceManifest'].pop()),('wrong-recipe',lambda x:x.update(buildRecipeSha256='0'*64)),('missing-whole-manifest',lambda x:x['selectedModuleManifests'].pop()),('wrong-context',lambda x:x['combinedNativeSourcePolicy'].update(workRoot='/private/tmp/not-the-owned-work')),('diagnostics-off',lambda x:x['observedCMakeOptions'].update(NODE_COMPAT_LIFECYCLE_DIAGNOSTICS='OFF')),('separate-embedding-macro-missing',lambda x:x['actualEmbeddingCompileCommands'].__setitem__(0,x['actualEmbeddingCompileCommands'][0].replace('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1 ',''))),('wrong-entropy',lambda x:x.update(entropyPolicy='runtime-only')),('debug-enabled',lambda x:x.update(debuggerEnabled=True)),('strong-getter-premature',lambda x:x['clockLifecycleDiagnosticBuildEvidence'].update(actualStrongGetterLinkProved=True))]:
 candidate=copy.deepcopy(m);mutate(candidate)
 try:model.validate_metadata(candidate,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
 except (AssertionError,KeyError):negative.append(name)
 else:raise AssertionError('Pure negative accepted: '+name)
need(len(negative)==10,'Actual pure model negative coverage')
summary=dict(schemaVersion=1,passed=True,checks=checks,nativeSourceFiles=357,externalEmbeddingSources=3,rawMetadataFields=82,wholeManifests=11,compileDatabaseRows=69,policyCppCommands=63,otherConfiguredCommands=5,generatedNullCommands=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6,actualObjectFiles=objects,staticArchiveArguments=archives,uniqueLinkedArchives=len({r['path']for r in archives}),opensslSources=4650,opensslArchiveSymbolCount=count,cleanupDefinitionMemberOffsets=cleanup,actualCompoundLinkVerified=True,diagnosticSharedCompileCommands=diagnostic,pureModelNegatives=negative,metadataClassification=classification,postOptimizedBytesEqualActualEngine=True,backendRuntimeProofFalse=True,standaloneCompilerTerminalsObserved=False,extraInputs=list(seen.values()),ownerToolsOrEngineOrGuestInvoked=False)
dump('metadata-review.json',summary);print(json.dumps(dict(metadataAuditPassed=True,checks=checks,files=len(seen),archives=len({r['path']for r in archives}),opensslSources=4650)))
