"""Independent combined355 freeze DATA audit; no producer/verifier/tool execution."""
from pathlib import Path
import ast,collections,hashlib,json,os,shlex,stat
P=Path(__file__).resolve().parent;S=P.parent;C=S/'combined-native-freezer-candidate-v1';F=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze');E=Path(str(F)+'-external-root');checks=0;seen={};identities={};copy_evidence=[];raw_copies=[]
def need(v,label):
 global checks
 checks+=1
 assert v,label
def identity(p):
 s=p.lstat();need(stat.S_ISREG(s.st_mode),'regular actual file');return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def row(p):
 p=Path(p);a=identity(p)
 if str(p)in seen:need(identities[str(p)]==a,'same captured identity');return seen[str(p)]
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(a==identity(p),'stable hash read');r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);seen[str(p)]=r;identities[str(p)]=a;return r
def verify(r):need(row(r['path'])=={k:r[k]for k in['path','sha256','bytes']},'exact actual descriptor');return Path(r['path'])
def read(r):return json.loads(verify(r).read_bytes())
def load(p):return read(row(p))
def same(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b
def tree(root,names,allowlinks=None):
 root=Path(root);fs=set();links={}
 for q in root.rglob('*'):
  n=q.relative_to(root).as_posix()
  if q.is_symlink():links[n]=os.readlink(q)
  elif q.is_file():fs.add(n)
 need(fs==set(names)and links==(allowlinks or{}),'complete current exact tree')
def family(r):
 ix=read(r);base=Path(r['path']).parent;names={'index.json'};rs=[]
 for m in ix['files']:
  n=m['path'];need(n not in names and n and not n.startswith('/')and all(s not in('','.','..')for s in n.split('/')),'unique confined indexed member');names.add(n);q=dict(m,path=str(base/n));verify(q);rs.append(q)
 tree(base,names);return ix,rs
def proof(pair):
 _,rs=family(pair['index']);need(pair['result']in rs,'result indexed once');return read(pair['result'])
def save(n,v):
 p=P/n;need(not p.exists(),'new reviewer output only');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
rootrow=row(S/'combined-native355-v2-freeze-root-results.json');R=read(rootrow);need(R['state']=='ROOT_OBSERVED_COMBINED355_FREEZE_ZERO_UNREVIEWED_V2'and R['toolObservation']==dict(sessionId=4533,rawExitCode=0,kind='Actual exec-command tool terminal observation'),'actual Root tool observation')
A=read(R['rootAuthority']);cfg=read(R['rootConfig']);invocation=read(R['invocation']);receipt=read(R['receipt']);control=read(receipt['freezerControl']);refs=load(C/'references.json');plan=load(C/'capture-plan.json');prot=load(C/'protection.json')
need(R['rootAuthority']['sha256']=='48a652fa3b317759fc4aec384bfb21370a7fc2cf5559a36f4cac3c7f1b4c5a8e'and R['rootConfig']['sha256']=='b3552faaeca9a68ae022101552b891384ac690ad42e3a222dc59ced8420dadfd','held actual Root/config')
need(cfg['rootAuthority']==R['rootAuthority']and cfg['freezerIndex']==receipt['freezerSourceIndexed']and cfg['nativeSourceIndex']==receipt['nativeSourceIndexed'],'whole genuine phase/config/receipt Source')
need(receipt['freezerSourceIndexSha256']==receipt['freezerSourceIndexed']['sha256']=='5230be984948519000c818450ada155917097ca26f259ee37dbcc3bb36728a4b'and receipt['nativeSourceIndexSha256']==receipt['nativeSourceIndexed']['sha256']=='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65','actual own/native Source identities')
family(receipt['freezerSourceIndexed']);family(receipt['nativeSourceIndexed']);peer=proof(receipt['sourceIndependentReview']);need(receipt['sourceIndependentReview']==R['sourcePeer']==A['sourceIndependentReview']and peer['state']=='INDEPENDENT_COMBINED355_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1'and peer['freezerSourceIndexSha256']==receipt['freezerSourceIndexSha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True,'actual Source peer6a74')
for k in ['ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked']:need(peer[k]is False,'Source peer scope '+k)
for item in refs['families']:family(item['index'])
for x in refs['files']:verify(x)
need(A['state']=='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_FREEZE_V1'and A['phase']=='freeze'and A['variant']=='normal-off'and A['freezerIndex']==receipt['freezerSourceIndexed'],'actual only freeze authority')
for k in ['freezeAllowed','readOnlySourceAdmissionAllowed','postBuildNinjaCommandsAllowed']:need(A[k]is True,'genuine phase permission '+k)
for k in ['buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:need(A[k]is False,'closed other phase '+k)
need(A['externalParentDeadlineSeconds']==2400 and A['requiredStartFreeBytes']==2147483648 and A['engine']==refs['engine']and A['metadata']==refs['metadata'],'actual bounded raw build pair')
build=proof(refs['actualBuildReview']);bc=read(refs['actualBuildContract']);need(receipt['actualBuildReview']==refs['actualBuildReview']and build['state']=='INDEPENDENT_COMBINED355_NATIVE_BUILD_V2_RESULTS_REVIEW_PASSED_V1'and build['verifiedPassed']is True,'genuine actual BUILD prerequisite')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for k,v in bc[group].items():need(same(build[k],v),'whole completed BUILD contract '+k)
need(same(build['coverage'],bc['requiredCoverage'])and build['rawMetadataFields']==80,'complete actual build coverage80')
originals=read(refs['buildInputLedger']);need(len(originals['files'])==receipt['verifiedOriginalReferenceCount']==20816 and receipt['verifiedBuildInputLedger']==refs['buildInputLedger']==build['inputHashes'],'complete actual20816 original-reference ledger')
for x in originals['files']:verify(x)
need(len(prot['files'])==20816 and len(prot['modePairs'])==1613 and len(prot['trees'])==2,'whole protection scopes')
for x in prot['files']:
 s=verify(x['descriptor']).stat();need(stat.S_IMODE(s.st_mode)==x['mode']and s.st_nlink==x['nlink'],'original mode/link count protected')
for x in prot['modePairs']:
 a=verify(x['copy']).stat();b=verify(x['original']).stat();need(stat.S_IMODE(a.st_mode)==x['copyMode']and stat.S_IMODE(b.st_mode)==x['originalMode']and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'all1613 original/stage mode/inode pairs preserved')
for t in prot['trees']:need(stat.S_IMODE(Path(t['root']).stat().st_mode)==t['mode'],'original tree root mode');tree(t['root'],t['files'],t['links'])
for x in receipt['verifiedReferenceAliases']:need(Path(x['path']).is_symlink()and os.readlink(x['path'])==x['linkText']and str(Path(x['path']).resolve())==x['resolved'],'all31 original reference aliases')
for x in receipt['declaredArchiveHardlinks']:need(x['sameInode']is True and os.path.samefile(x['path'],x['target']),'original archive hardlink witness retained')
need(len(receipt['verifiedReferenceAliases'])==31 and len(receipt['declaredArchiveHardlinks'])==1,'exact alias scope not frozen link claim')
# Verify every frozen whole file, corresponding original and independent inode.
need(F.is_dir()and not F.is_symlink()and stat.S_IMODE(F.stat().st_mode)==0o700,'private freeze root700');frozen={};inodes=set();roles=collections.Counter()
for x in receipt['copies']:
 p=Path(x['path']);need(p.is_relative_to(F),'all copies confined to actual freeze');n=p.relative_to(F).as_posix();need(n not in frozen,'unique frozen destination');verify(x);i=identity(p);need(i[5:]==(0o600,1)and i[:2]not in inodes,'all frozen600/singlelink/distinct inode');inodes.add(i[:2]);frozen[n]=x;roles[x['role']]+=1
 if x['original']is not None:
  verify(x['original']);need(x['sha256']==x['original']['sha256']and x['bytes']==x['original']['bytes']and i[:2]!=identity(Path(x['original']['path']))[:2],'whole exact original/copy and distinct inode')
 copy_evidence.append(dict(copy={k:x[k]for k in['path','sha256','bytes']},original=x['original'],role=x['role'],mode=i[5],nlink=i[6],device=i[0],inode=i[1],originalDistinctInode=x['original']is None or i[:2]!=identity(Path(x['original']['path']))[:2]))
need(len(frozen)==2596 and len(inodes)==2596 and roles['selected-static-library']==29 and roles['actual-compiled-object-DATA']==69 and roles['current-native355-source']==355 and roles['actual-external-embedding-source']==3,'entire frozen2596/native355+3/libs29/objects69')
ri=identity(Path(R['receipt']['path']));need(ri[5:]==(0o600,1)and ri[:2]not in inodes,'receipt independent600 inode');tree(F,[*frozen,'normal-off-freeze-receipt.json'])
for q in F.rglob('*'):
 if q.is_dir():need(not q.is_symlink()and stat.S_IMODE(q.stat().st_mode)==0o700,'all frozen directories700')
need(len(plan['copies'])==plan['baseCopies']==2544,'exact base2544 plus authenticated dynamic captures')
for x in plan['copies']:
 y=frozen[x['destination']];need(y['original']==x['source']and y['role']==x['role'],'base plan actual copy role/source exact')
need(roles['new-combined355-freezer-source-capsule']==27 and roles['new-freezer-source-review']==16 and roles['new-freeze-config']==roles['new-freeze-authority']==1 and roles['fresh-source-admission-Ninja-or-control-data']==7,'all52 additional current-source/peer/phase/generated records accounted')
# Whole own frozen source and peer capsule must equal actual authenticated families.
for prefix,ixrow in [('artifact-tools/source',receipt['freezerSourceIndexed'])]:
 ix=read(ixrow);need(frozen[prefix+'/index.json']['sha256']==ixrow['sha256'],'complete frozen own index exact')
 for m in ix['files']:need(frozen[prefix+'/'+m['path']]['sha256']==m['sha256']and frozen[prefix+'/'+m['path']]['bytes']==m['bytes'],'every actual own source file copied exactly')
M=read(receipt['metadata']);need(M==read(refs['metadata'])and len(M)==80 and receipt['engine']['sha256']==refs['engine']['sha256']=='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'and receipt['metadata']['sha256']=='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3','raw original80 metadata and engine immutable')
need(M['enginePath']==refs['engine']['path']and receipt['engine']['path']==str(F/'normal-off.engine.wasm')and M['enginePath']!=receipt['engine']['path'],'explicit original engine metadata/frozen artifact roles; no rewrite')
need(receipt['configuredSourceRoot']==refs['configuredSourceRoot']=='/private/tmp/starling-node-compat/combined-native355-v1-source'and receipt['workRoot']==refs['workRoot']=='/private/tmp/starling-node-compat/combined-native355-v2-build'and receipt['sourceRoot']==str(F/'source')and receipt['componentizeSourceRoot']==str(F/'componentize-source'),'genuine literal configured/work/frozen contexts')
for key,prefix,count in [('sourceManifest','source',355),('componentizeSourceManifest','componentize-source',3)]:
 need(len(M[key])==count,'whole exact native/embedding manifest count')
 for x in M[key]:need(frozen[prefix+'/'+x['path']]['sha256']==x['sha256'],'all frozen native/embedding paths exact metadata')
need(len(M['selectedModuleManifests'])==11,'full11 native manifests not9 selector projection')
for x,value in zip(M['selectedModuleManifests'],refs['selectedManifestValues']):need(load(F/'source'/x['path'])==value and value['profileVersion']==x['profileVersion'],'whole selected manifest object/profile')
need(receipt['sourcePolicies']=={k:M[k]for k in refs['copiedMetadataPolicyKeys']}and receipt['privateRustupBootstrapPolicy']==M['privateRustupBootstrapPolicy'],'full native policies and genuine private Rustup provenance')
for k,n in dict(nativeInputsVerified=355,unchangedSecretParentFiles=348,nativeReplacements=7,externalEmbeddingInputsVerified=3,selectedManifestCount=11,rawMetadataFields=80,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredSourceRows=5,generatedNullCppRows=1,embeddingRowsInCompileDatabase=0,separatePostBuildEmbeddingCommands=1,actualStrictCommands=4,actualPrivateClassicCommands=6,staticLibrariesPhysicallyCopied=29).items():need(receipt[k]==n,'exact actual frozen count '+k)
# Saved compile DB preserves original configured paths and exact build commands.
db=load(F/'build-evidence/compile_commands.json');need(len(db)==68 and len({x['file']for x in db})==68,'all68 actual compile rows');dbcommands={x['file']:x['command']for x in db};combined=M['combinedNativeSourcePolicy'];need(set(combined['actualPolicyCppCompileCommands'])<=set(dbcommands.values())and len(combined['actualPolicyCppCompileCommands'])==62 and len(combined['actualOtherConfiguredCompileCommands'])==5 and len(combined['actualGeneratedNullCompileCommands'])==1,'DB62policy+5other+1null')
for x in db:
 argv=shlex.split(x['command']);need(argv.count('-c')==argv.count('-o')==1 and argv[argv.index('-c')+1]==x['file']and '-O3'in argv and '-DNDEBUG'in argv and '-fsyntax-only'not in argv,'actual CPP compile semantics preserved')
need(len(M['actualEmbeddingCompileCommands'])==1 and M['actualEmbeddingCompileCommands']==combined['actualSeparateEmbeddingCompileCommands'],'separate embedding1 not DB row')
# Actual source-admission and Ninja -t commands raw captures; no tool rerun.
for role,k,cap in [('source-admission','sourceAdmissionEvidence',600),('embedding-after','postBuildEmbeddingEvidence',120)]:
 e=receipt[k];t=read(e['terminal']);verify(e['stdout']);verify(e['stderr']);need(t['schemaVersion']==1 and t['role']==role and t['rawExitCode']==0 and t['timedOut']is False and t['errorType']is None and t['capturedStreamsComplete']is True and t['postBuildOnly']is True and t['compilerExecuted']is t['engineExecuted']is False and t['stdout']==e['stdout']and t['stderr']==e['stderr']and t['cwd']==refs['configuredSourceRoot']and t['timeoutSeconds']==cap and e['stderr']['bytes']==0,'whole actual read-only helper terminal '+role)
 for part in ['stdout','stderr','terminal']:need({k:frozen['helper-calls/'+role+'/'+('terminal.json'if part=='terminal'else part+'.log')][k]for k in['path','sha256','bytes']}==e[part],'whole receipt/helper raw binding')
ad=read(receipt['sourceAdmissionEvidence']['stdout']);need(ad['state']=='COMBINED355_NORMAL_OFF_BUILD_SOURCE_ADMISSION_PASSED_V1'and ad['nativeSourceIndexSha256']==receipt['nativeSourceIndexSha256']and ad['freezerSourceIndexSha256']==receipt['freezerSourceIndexSha256']and ad['configuredSourceRoot']==refs['configuredSourceRoot']and ad['genuineLayerRoot']==str(Path(refs['layer']['path']).parent)and ad['metadata']==refs['metadata'],'actual native seven-argument configured admission roles')
need(ad['sourceManifest']==M['sourceManifest']and ad['externalSourceManifest']==M['componentizeSourceManifest']and ad['selectedManifestRows']==M['selectedModuleManifests']and ad['selectedManifests']==refs['selectedManifestValues']and ad['sourcePolicies']==receipt['sourcePolicies']and ad['privateRustupBootstrapPolicy']==M['privateRustupBootstrapPolicy'],'whole actual admission metadata/manifests/policies')
need(ad['metadataClassifier']==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)and ad['engineHashedAsGuardData']is True and ad['engineExecuted']is ad['operationalAdmission']is ad['runtimeAcceptanceClaim']is False,'shape-only classifier no execution/adoption')
for k,n in dict(nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,rawMetadataFields=80,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredSourceRows=5,generatedNullCppRows=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6).items():need(ad[k]==n,'all actual admission counters '+k)
at=read(receipt['sourceAdmissionEvidence']['terminal']);need(at['argv']==[refs['python']['path'],'-B','-I',str(C/'entry.py'),'admit',json.dumps(R['rootConfig'],separators=(',',':'))],'actual literal own source-admission child argv')
et=read(receipt['postBuildEmbeddingEvidence']['terminal']);need(et['argv']==[refs['ninja']['path'],'-C',str(Path(M['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding'],'actual read-only Ninja commands argv')
commands=[]
for line in verify(receipt['postBuildEmbeddingEvidence']['stdout']).read_text().splitlines():
 if ' -c 'in line:
  argv=shlex.split(line)
  if argv.count('-c')==1 and argv[argv.index('-c')+1]==refs['externalSourceRoot']+'/embedding/embedding.cpp':commands.append(line)
need(commands==M['actualEmbeddingCompileCommands']==receipt['postBuildEmbeddingEvidence']['commands'],'whole actual separate embedding command capture')
# Current107 bytes and historical368-record/nested57 descriptor never conflated.
before=load(F/'build-evidence/private-rustup-settings-before-install.json');current=F/'build-evidence/private-rustup-settings-at-build-completion.toml';need(before==refs['rustupBeforeValue']and before['settings']['bytes']==57 and before['settings']['sha256']=='c199d646911907e3bf8b419c59b0dedf08d1a133d6d69e1e01e7d733be995437','historical record/nested57 digest preserved DATA')
need(current.read_text()==refs['rustupCurrentSettingsText']and row(current)['sha256']=='507d63504ab8c6965537b030791071f2fda00eba98bb317e48f17af32a595699'and row(current)['bytes']==107,'exact current private107 settings')
need(frozen['build-evidence/private-rustup-settings-before-install.json']['original']==refs['rustupBeforeRecord']and frozen['build-evidence/private-rustup-settings-at-build-completion.toml']['original']==refs['rustupCurrentSettings'],'independent original/current settings provenance')
for k in ['nativeSourceIndexed','retryBuildControllerIndexed','freezerSourceIndexed','rootAuthority','sourceIndependentReview','actualBuildReview']:need(control[k]==receipt[k],'whole control receipt binding '+k)
need(control['activeEntry']==A['entry']and control['activeBody']==row(C/'freeze.py')and control['genuineAdmissionModel']==refs['configuredModel']and control['genuineAdmissionLayer']==refs['layer'],'actual own entry/body and genuine configured helper roles')
# Actual owned lifecycle and complete whole frozen-verifier return.
T=read(R['ownedWorkerTerminal']);need(T['pid']==32744 and T['rawExitCode']==0 and T['parentOwnedGroupGone']is T['allObservedOwnedGroupsGone']is True and T['forcedCleanup']is T['timeout']is False,'actual parent raw0')
for k in ['remainingObservedPids','signals','errors','interruptedSignals']:need(T[k]==[],'actual no lifecycle issue '+k)
need(T['finalGroups']==[dict(pgid=32744,alive=False,signalAllowed=False)]and[p['pid']for p in T['observedProcesses']]==[32744,33363]and all(p['pgid']==32744 for p in T['observedProcesses']),'two observed Python processes same exact owned group')
events=[load(x)for x in sorted(E.glob('owned-*.json'))];need([x['sequence']for x in events]==[0,1]and[x['process']for x in events]==T['observedProcesses'],'complete owned process records');tree(E,['started.json','terminal.json','stdout.log','stderr.log','owned-0000.json','owned-0001.json'])
started=load(E/'started.json');need(started['pid']==32744 and started['timeoutSeconds']==2400 and started['authority']==T['authority']==R['rootAuthority'],'actual monitored launch/deadline/authority');need(started['argv']==[refs['python']['path'],'-B','-I',str(C/'entry.py'),'freeze',json.dumps(R['rootConfig'],separators=(',',':'))],'literal Source entry freeze argv')
for k in ['stdout','stderr']:verify(T[k])
expected_return=dict(schemaVersion=1,state='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1',receipt=R['receipt'],engine=receipt['engine'],metadata=receipt['metadata'],copies=2596,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifests=11,rawMetadataFields=80,originalBuildReferencesNotReexecuted=True,requiresExternalParentZeroAndIndependentReview=True,engineExecuted=False,bootstrapExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
need(same(json.loads(Path(T['stdout']['path']).read_bytes()),expected_return)and same(R['actualReturnEnvelope'],expected_return)and T['stderr']['bytes']==0,'whole actual frozen-payload verifier return and raw streams')
parent=[json.loads(x)for x in verify(R['parentStdout']).read_text().splitlines()];need(parent==[dict(pid=32744,timeoutSeconds=2400),T]and R['parentStderr']['bytes']==0,'whole caller two-record launch/terminal JSONL');verify(R['parentStderr']);env=read(R['environmentPolicy']);need(env['removedNames']==[]and env['homeValuesPreserved']is True and env['valuesRecorded']is False,'bounded Root environment report not whole attestation')
# Source/data-only verification of actual frozen verifier code path and roles.
vsrc=(C/'verify.py').read_text();fsrc=(C/'freeze.py').read_text();ast.parse(vsrc);ast.parse(fsrc);need("g.load_own(frame,'verify.py').verify_frozen"in fsrc and "self_path=Path(__file__).resolve()"in vsrc and "self_path.read_bytes()"in vsrc and "pure_model('models.py')"in vsrc and "pure_model('metadata_model.py')"in vsrc,'actual original Source verifier self-auth plus frozen pure-model path; no blanket allreads-FROZEN claim')
for k in ['engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim','gcReconfigureAllowed','historicalPreinstallSettingsRawBytesSeparatelyRetained','zlibRemainingDeviationsApproved']:need(receipt[k]is False,'no extra actual artifact claim '+k)
need(receipt['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)and receipt['nativeAllInvalidRuntimeValidation']is receipt['resourceNativeRuntimeValidation']is receipt['reviewedEnginePins']is None,'remaining runtime/adoption gates unchanged')
for k in ['rawMetadataBytesUnchanged','rawMetadataOriginalConfiguredPathsPreserved','allInputsValidatedBeforeHelperImports','allInputsValidatedBeforeCopies','allCopiesAndOriginalsRehashed','receiptRequiresExternalParentZeroAndIndependentReview','verifiedReferencesNotAllCopied','referenceAliasesNotCopiedAsLinks']:need(receipt[k]is True,'actual finite source/copy protection '+k)
# Compact whole raw text retention; all binary/SDK/library files remain hash references.
def retain(p,n):
 p=Path(p);a=row(p);q=P/'raw-evidence'/n;need(not q.exists(),'fresh reviewer copy');q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb')as f:f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
 os.chmod(q,0o600);b=row(q);need(a['sha256']==b['sha256']and a['bytes']==b['bytes']and identity(p)[:2]!=identity(q)[:2],'whole raw evidence distinct copies');raw_copies.append(dict(original=a,copy=b,distinctInode=True))
for name,root in [('owned',E),('caller',Path(R['parentStdout']['path']).parent),('helper-calls',F/'helper-calls')]:
 for q in sorted(root.rglob('*')):
  if q.is_file():retain(q,Path(name)/q.relative_to(root))
for q in [Path(rootrow['path']),Path(R['rootAuthority']['path']),Path(R['rootConfig']['path']),Path(R['invocation']['path']),F/'normal-off-freeze-receipt.json',F/'normal-off-freezer-control.json',F/'normal-off.engine.wasm.build.json',F/'build-evidence/private-rustup-settings-before-install.json',current]:retain(q,Path('phase')/q.name)
for p,i in list(identities.items()):need(identity(Path(p))==i,'own current-file final identity bookend')
all_rehashed=[seen[k]for k in sorted(seen)if not Path(k).is_relative_to(P)];phase_paths={str(rootrow['path']),*[R[k]['path']for k in ['rootAuthority','rootConfig','invocation']],receipt['freezerSourceIndexed']['path'],receipt['nativeSourceIndexed']['path'],R['sourcePeer']['index']['path'],R['sourcePeer']['result']['path'],refs['actualBuildReview']['index']['path'],refs['actualBuildReview']['result']['path'],refs['actualBuildContract']['path'],refs['buildInputLedger']['path']};callerroot=Path(R['parentStdout']['path']).parent
external_inputs=[x for x in all_rehashed if Path(x['path']).is_relative_to(F)or Path(x['path']).is_relative_to(E)or Path(x['path']).is_relative_to(callerroot)or x['path']in phase_paths]
save('input-hashes.json',dict(schemaVersion=1,files=external_inputs,reviewedBuildInputLedger=refs['buildInputLedger'],reviewedBuildReferencesRehashed=20816,reviewedInheritedFamilies=[x['index']for x in refs['families']],currentReviewUniqueRehashedFiles=len(all_rehashed),frozenPayloadAndPhaseRowsOnly=True,historicalTreesRecopied=False));save('frozen-copy-inventory.json',dict(schemaVersion=1,files=copy_evidence,receipt=R['receipt'],wholeMembershipFiles=2597,allCopyInodesUnique=True,allOriginalCopyInodesDistinct=True));save('raw-copy-map.json',dict(schemaVersion=1,files=raw_copies));save('actual-verifier-return.json',expected_return)
fixed=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_NATIVE_FREEZE_V2_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,nativeSourceIndexSha256=receipt['nativeSourceIndexSha256'],freezerSourceIndexSha256=receipt['freezerSourceIndexSha256'],variant='normal-off',nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,rawMetadataFields=80,engineSha256=receipt['engine']['sha256'],metadataSha256=receipt['metadata']['sha256'],freezeReceiptSha256=R['receipt']['sha256'],rawFreezeParentExitCode=0,allObservedOwnedGroupsGone=True,actualFrozenPayloadVerifierReturned=True,reviewerFrozenVerifierInvoked=False,actualVerifierSelfSourceAuthOutsideFrozen=True,engineExecuted=False,bootstrapExecuted=False,componentOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,reviewerOwnerHelperToolEngineOrGuestActionsInvoked=False)
direct=dict(freezeReceipt=R['receipt'],freezerControl=receipt['freezerControl'],engine=receipt['engine'],metadata=receipt['metadata'],rootObservation=rootrow,rootAuthority=R['rootAuthority'],rootConfig=R['rootConfig'],rootInvocation=R['invocation'],ownedWorkerTerminal=R['ownedWorkerTerminal'],sourceIndependentReview=R['sourcePeer'],actualBuildReview=receipt['actualBuildReview'],nativeSourceIndex=receipt['nativeSourceIndexed'],retryBuildControllerIndex=receipt['retryBuildControllerIndexed'],freezerSourceIndex=receipt['freezerSourceIndexed'],sourceAdmissionEvidence=receipt['sourceAdmissionEvidence'],postBuildEmbeddingEvidence=receipt['postBuildEmbeddingEvidence'],frozenVerifierRawStdout=T['stdout'],inputHashes=row(P/'input-hashes.json'),frozenCopyInventory=row(P/'frozen-copy-inventory.json'),rawCopyMap=row(P/'raw-copy-map.json'))
coverage=dict(frozenCopies=2596,frozenRegularFiles=2597,baseCopyPlan=2544,generatedAdmissionNinjaControlFiles=7,newSourceCapsuleFiles=27,newSourcePeerFiles=16,newPhaseFiles=2,staticLibraries=29,actualObjectFiles=69,verifiedOriginalBuildReferences=20816,protectedStageOriginalPairs=1613,failedV1WorkFiles=755,originalReferenceAliases=31,originalArchiveHardlinks=1,sourceFamilies=len(refs['families']),rawMetadataFields=80,nativeSourceFiles=355,retainedSecretParentFiles=348,replacedNativeFiles=7,externalEmbeddingSources=3,wholeManifests=11,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredCommands=5,generatedNullCppCommands=1,embeddingRowsInCompileDatabase=0,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6,observedProcesses=2,ownedGroups=1,sourceAdmissionReadOnlyProcesses=1,postBuildNinjaMetadataCommands=1,rawEvidenceCopies=len(raw_copies),currentActualInputFiles=len(all_rehashed),newCurrentPayloadLedgerFiles=len(external_inputs))
limits=[
 'Actual immutable normal-off native freeze only.2596complete frozen files plus receipt2597 are hash/mode/membership/inode verified; frozen engine and raw80-field sidecar remain byte-identical to reviewed build. No compiler/build/engine/bootstrap/component/guest/key/GC/export/pin/runtime-adoption action is granted.',
 'The actual producer invoked the original authenticated Source verify.py through g.load_own. It reads its own original Source __file__ to authenticate against the frozen source index, then payload reads and its two pure models use frozen copies. This is frozen-payload verification with original active verifier-code self-authentication, not a blanket claim that every verifier read was underFROZEN or that an independently copied helper ran standalone. No verifier was invoked by this reviewer.',
 'The compact new ledger enumerates current frozen/phase/raw payload rows and reuses the sealed20816-row BUILD ledger plus15 Source-family index descriptors. All inherited rows were currently rehashed; historical trees were not recopied.',
 'All20816 declared original build references, modes/link counts,1613 source/original pairs, two exact protected trees(including failed755) and31alias+onearchive-hardlink witnesses were independently rechecked. This does not expand to unrelated whole historical normal-freeze receipts. Most verified references were intentionally not physically copied.',
 'Historical368-byte before-install record preserves nested57-byte settings digest without separately retained57raw bytes. Current post-install settings are107bytes and copied independently. The stale nested descriptor is DATA and was not recursively opened or rewritten as current.',
 'Metadata engine/source/compiler paths remain original WORKv2/configuredSOURCEv1 paths. Frozen engine/source/embedding paths are separate actual receipt descriptors. Full355=348secret-parent+7native replacements, embedding3,11whole manifests and80raw metadata fields are retained without projections.',
 'Source-admission and post-build Ninja -t commands have complete raw0 captures. Ninja only printed one separate embedding command; no compiler ran during freeze. CompileDB68=62policy+5other+1null,zero embedding rows; embedding1 separately preserved. Earlier BUILD proof remains the compilation evidence; no standalone per-C++ terminal claim is added.',
 'Actual parent32744 and source-admission child33363 shared owned group32744 and exited cleanly; Root tool4533raw0 is retained as Root-reported tool observation. Environment report is names/Root-reported homes scope, not whole environment/OS attestation. Durations are operational, not performance.',
 'Native all-invalid task/runtime/resource tests remain pending; zlib remaining deviations are unapproved and backendRuntimeProof staysfalse/null/null. No erasure/free/wipe/security completeness, public Nodecrypto, reset/reuse, capability adoption or runtime acceptance follows.'
]
save('results.json',{**fixed,**direct,'coverage':coverage,'checks':checks,'frozenCopyRoles':dict(roles),'limitations':limits,'reviewedEnginePins':None,'exportResult':None,'bootstrapResult':None,'runtimeAuthority':None})
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredExactDescriptors=direct,requiredCoverage=coverage,limitationsMustBePreserved=limits,issuesAnyActionAuthority=False))
(P/'README.md').write_text('Independent combined355-v2 normal-off frozen artifact DATA review\n\nBounded PASS: whole2596copy/2597file receipt, raw80/native355+3/11, actual raw0 ownership and complete original/source/build protections are verified without invoking any producer/verifier/tool/engine.\n\n'+ '\n\n'.join(limits)+'\n')
save('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMBINED355_NATIVE_FREEZE_V2_DATA_REVIEW_V1',result=row(P/'results.json'),contract=row(P/'result-contract.json'),inputHashes=row(P/'input-hashes.json'),copyInventory=row(P/'frozen-copy-inventory.json'),rawCopyMap=row(P/'raw-copy-map.json'),reviewerDataOnly=True,engineExecuted=False,operationalAdmission=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():r=row(q);files.append(dict(r,path=q.relative_to(P).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for n in ['index.json','results.json','result-contract.json','receipt.json','input-hashes.json']:print(json.dumps(row(P/n)))
print(json.dumps(dict(sealed=True,members=len(files),checks=checks,inputFiles=len(external_inputs),frozenCopies=2596,rawCopies=len(raw_copies),reviewerActions=False)))
