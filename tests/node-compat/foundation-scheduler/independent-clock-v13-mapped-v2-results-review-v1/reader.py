"""Independent combined355 freeze DATA audit; no producer/verifier/tool execution."""
from pathlib import Path
import ast,base64,hashlib,json,os,re,stat,subprocess,time
P=Path(__file__).resolve().parent;S=P.parent;C=S/'clock-v13-runtime-candidate-v2';F=Path('/private/tmp/starling-node-compat/clock-v13-jco-mapped-v2');E=Path(str(F)+'-external-root');checks=0;seen={};identities={};copy_evidence=[];raw_copies=[]
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
rootrow=dict(path=str(S/'clock-v13-map-v2-root-results.json'),sha256='f76bc8059b32efa2309f1c7432ad46cda7df258564c718c31d8bd4bfd850c1da',bytes=4581);R=read(rootrow);A=read(R['rootAuthority']);cfg=read(R['rootConfig']);invocation=read(R['invocation']);refs=load(C/'references.json');I=load(C/'source-inputs.json')
need(R['sourceIndex']['sha256']=='135d1e45ea4214a99e2a835cfab0b212c92519ea6600a7c802336e7a323be384'and R['toolObservation']==dict(sessionId=19813,rawExitCode=0,kind='Actual exec-command terminal observation'),'actual135d/Root19813')
family(R['sourceIndex']);peer=proof(R['sourcePeer']);need(peer['state']=='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V2'and peer['sourceIndexSha256']==R['sourceIndex']['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True,'actual dd8f Source-only peer')
need(len(I['files'])==12079 and len(I['families'])==18,'whole current declared Source12079/18')
for x in I['files']:verify(x)
for x in I['families']:family(x)
need(A['state']=='ROOT_REVIEWED_CLOCK_V13_REACTDOM_DIFFERENTIAL_V2'and A['phase']=='mapped-transpile'and A['sourceIndex']==R['sourceIndex']==cfg['sourceIndex']and cfg['rootAuthority']==R['rootAuthority']and A['entry']==row(C/'entry.mjs')and A['externalController']==row(C/'external.py')and A['sourceIndependentReview']==R['sourcePeer'],'whole actual mapping Root/config/caller')
for k in ['mappedTranspileAllowed','jcoCompilerWasmHelpersAllowed','nativeReadOnlyPreflightAllowed','standardShimWorkerThreadsAllowed']:need(A[k]is True,'only mapped/native-read permission '+k)
for k in ['generatedApplicationImportAllowed','ordinaryRunAllowed','stockWasmtimeAllowed','customHostServicesAllowed','componentConstructionAllowed','nativeBuildAllowed','engineReplacementAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','otherGuestAllowed','resourceSevenCaseProfileAccepted','clockProfilePromotionAllowed','dateTimerSnapshotTeardownAccepted','resetOrReuseAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(A[k]is False,'closed runtime/adoption phase '+k)
need(A['actualMappedOutputReview']is None and A['outputRoot']==str(F)and A['externalOutputRoot']==str(E)and A['requiredExternalParentDeadlineSeconds']==1200 and A['ownedWorkerDeadlineMs']==180000,'fresh bounded map-only phase')
art=proof(refs['actualArtifactReview']);ac=read(refs['actualArtifactContract']);need(art['state']=='INDEPENDENT_CLOCK_V13_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and art['verifiedPassed']is True and art['componentSha256']=='5c002f8da675016fd7061d245074965413d6914e4f40eb2a32a8141c1f3b7460'and art['nativeSourceFiles']==342 and art['externalEmbeddingSources']==3 and art['fullMetadataFields']==64 and art['selectedManifestCount']==9,'genuine b073 native342/3/64/9 artifact')
need(art['artifacts']==ac['artifacts']==refs['artifacts']and art['emittedImports']==A['selectedInterfaces']==refs['selectedInterfaces'],'whole component map/three0.2.10 caps')
for x in refs['artifacts'].values():verify(x)
for k in ['node','jcoApi','parser','shimClocks','shimIo','nativeEngine','nativeMetadata','nativePins','packageInventory']:verify(refs[k])
M=read(R['mappingResult']);ix=read(R['actualIndex']);completion=read(R['actualCompletion']);by={}
for m in ix['files']:
 n=m['path'];need(n not in by and n and not n.startswith('/')and all(v not in('','.','..')for v in n.split('/')),'confined unique actual output');d=dict(m,path=str(F/n));verify(d);by[n]=d
need(len(by)==13,'all13 indexed/15 actual mapped files');tree(F,[*by,'index.json','completion.json']);need(stat.S_IMODE(F.stat().st_mode)==0o700,'private mapped root700')
for q in F.rglob('*'):
 if q.is_file():need(identity(q)[5:]==(0o600,1),'all mapped files600/independent inode')
need(dict(completion['index'],path=str(F/completion['index']['path']))==R['actualIndex']and completion['mappingResult']==R['mappingResult']and completion['state']=='CLOCK_V13_MAPPED_OUTPUT_COMPLETE_EXTERNAL_RAW_ZERO_AND_SEPARATE_REVIEW_REQUIRED_V2','whole mapped completion')
need(M['state']=='CLOCK_V13_MAPPED_OUTPUT_COMPLETE_UNREVIEWED_V2'and M['sourceIndex']==R['sourceIndex']and M['config']==R['rootConfig']and M['rootAuthority']==R['rootAuthority']and M['component']==refs['component']and M['mappingOptions']==refs['mappingOptions']==A['mappingOptions'],'whole actual mapped result phase inputs')
need(M['jcoCompilerWasmHelpersInvoked']is True and M['applicationGeneratedModuleImported']is M['ordinaryApplicationExportsInvoked']is M['fullClockProfileAcceptance']is False,'compiler-Wasm vs application execution separation')
mapped=M['mappedFiles'];need(set(mapped)==set(refs['generatedFiles'])and len(mapped)==7,'complete exact seven generated loading files')
for name,d in mapped.items():need(d['path']==str(F/'transpiled'/name)and d==by['transpiled/'+name],'all generated files actual indexed once')
for name in mapped:
 if name!='clock_v13.js':need(mapped[name]['sha256']==refs['generatedFiles'][name]['sha256']and mapped[name]['bytes']==refs['generatedFiles'][name]['bytes'],'every non-glue generated whole file unchanged')
need(M['mappedCore']==mapped['clock_v13.core.wasm']and M['originalCore']==refs['generatedFiles']['clock_v13.core.wasm'],'exact actual/original core roles')
old=Path(refs['generatedFiles']['clock_v13.js']['path']).read_bytes();new=Path(mapped['clock_v13.js']['path']).read_bytes();marker=b'let dv = new DataView(new ArrayBuffer());';need(old.count(marker)==new.count(marker)==1,'single common generated body boundary');oa,ob=old.split(marker,1);na,nb=new.split(marker,1);need(ob==nb,'ENTIRE mapped suffix byte-identical to b073 original; only prefix changes')
cores=[]
for literal in re.findall(rb'base64Compile\([\'"]([A-Za-z0-9+/=]+)[\'"]\)',new):
 raw=base64.b64decode(literal+b'='*((-len(literal))%4),validate=True);need(raw.startswith(b'\0asm\1\0\0\0')and literal.rstrip(b'=')==base64.b64encode(raw).rstrip(b'='),'complete canonical core literal');cores.append(dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
need(cores==refs['inlineCoreModules']==M['staticAudit']['inlineCoreModules']and len(cores)==3,'three complete inline core modules byte-identical')
need(Path(mapped['package.json']['path']).read_bytes()==b'{"type":"module"}\n','exact ESM package file');dt=Path(mapped['clock_v13.d.ts']['path']).read_text();need(re.findall(r'export\s+function\s+([^;]+);',dt)==['run(): string'],'same sole scalar run()->string ABI')
shape=load(F/'transpile-return-shape.json');need(shape==dict(type='object',imports=[refs['shimClocksUrl'],refs['shimIoUrl']],exports=[['run','function']],fileNames=[n for n in mapped if n!='package.json'],applicationGeneratedModuleImported=False),'whole genuine Jco return shape6files plus caller package')
static=load(F/'mapped-source-audit.json');need(static==M['staticAudit']and static['standardInterfaces']==refs['selectedInterfaces']and static['shimModuleUrls']==[refs['shimClocksUrl'],refs['shimIoUrl']]and static['publicExports']==['_util','run']and static['topLevelAwait']is True and static['generatedApplicationImported']is False,'whole captured actual AST audit')
# Independently parse actual glue and selected shim Sources; never import them.
worker=Path(refs['shimIo']['path']).parent.parent/'io/worker-io.js';verify(next(x for x in I['files']if x['path']==str(worker)))
cmd=[refs['node']['path'],str(P/'parse.mjs'),str(C/'references.json'),mapped['clock_v13.js']['path']];t0=time.monotonic();proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=P,timeout=60);(P/'parser.stdout.log').write_bytes(proc.stdout);(P/'parser.stderr.log').write_bytes(proc.stderr);save('parser-terminal.json',dict(schemaVersion=1,argv=cmd,executable=refs['node'],parser=refs['parser'],readerSource=row(P/'parse.mjs'),rawExitCode=proc.returncode,stdout=row(P/'parser.stdout.log'),stderr=row(P/'parser.stderr.log'),operationalSeconds=time.monotonic()-t0,hostParserOnly=True,generatedApplicationOrShimImported=False,applicationOrMappingApiInvoked=False));need(proc.returncode==0 and proc.stderr==b'','genuine pinned host grammar/static parser raw0');parsed=json.loads(proc.stdout);need(parsed['passed']is True and parsed['inlineCoreModules']==cores and parsed['exactMappedImportBindings']is parsed['wholeGeneratedSourceParsed']is parsed['standardPollBindingHasPollableAndPoll']is True,'fresh actual AST binding/core/export evidence')
# Full actual read-only native DATA and genuine physical private package.
frame=load(F/'native-frame-data.json');fs=load(F/'native-frame-shape.json');metadata=read(refs['nativeMetadata']);pins=read(refs['nativePins']);need(set(frame)=={'enginePath','sourceRoot','metadata','pin','variant'}and frame['enginePath']==refs['nativeEngine']['path']and frame['sourceRoot']==refs['nativeSourceRoot']and frame['variant']=='normal-off'and frame['metadata']==metadata and frame['pin']==pins['variants']['normal-off'],'entire actual original preflight frame/pin/native equality')
need(len(metadata)==64 and len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==9,'full64/342+3/nine manifests')
expected={k:dict(type='object'if k in ['metadata','pin']else'string',writable=False,configurable=False,enumerable=True)for k in frame};expected['recheck']=dict(type='function',writable=False,configurable=False,enumerable=True);need(fs==expected,'full native frame DATA/recheck descriptor separation')
package=read(refs['packageInventory'])['package'];need(len(package['files'])==4889 and len(package['links'])==21 and package['root']==refs['loaderPackageRoot'],'whole exact private package4889+21');names=set();links={}
for x in package['files']:verify(x);st=Path(x['path']).stat();need(st.st_nlink==1 and stat.S_IMODE(st.st_mode)==x['mode'],'all actual package file modes/inodes');names.add(x['relativePath'])
for x in package['links']:
 p=Path(package['root'])/x['path'];need(p.is_symlink()and os.readlink(p)==x['target']and str(p.resolve())==x['resolvedPath'],'all declared standard package alias text/target');links[x['path']]=x['target']
tree(package['root'],names,links);need(stat.S_IMODE(Path(package['root']).stat().st_mode)==0o700,'private package root mode')
phase=load(F/'phase-inputs.json');need(phase==dict(sourceIndex=R['sourceIndex'],config=R['rootConfig'],rootAuthority=R['rootAuthority'],component=refs['component'],mappingOptions=refs['mappingOptions'],originalGeneratedFiles=refs['generatedFiles'],applicationGeneratedModuleImported=False),'entire saved phase-input frame')
T=read(R['externalParentTerminal']);need(T['pid']==37754 and T['rawExitCode']==0 and T['timeout']is T['forcedCleanup']is False and T['parentOwnedGroupGone']is T['allObservedOwnedGroupsGone']is True and T['authority']==R['rootAuthority'],'actual owned Node raw0/clean')
for k in ['interruptedSignals','remainingObservedPids','signals','errors']:need(T[k]==[],'whole clean lifecycle '+k)
need(T['finalGroups']==[dict(pgid=37754,alive=False,signalAllowed=False)]and len(T['observedProcesses'])==1 and T['observedProcesses'][0]['pid']==37754 and T['observedProcesses'][0]['command']==refs['node']['path'],'one exact pinned Node observed process/group')
started=load(E/'started.json');owned=load(E/'owned-0000.json');need(started['pid']==37754 and started['timeoutSeconds']==1200 and started['authority']==R['rootAuthority']and started['argv']==[refs['node']['path'],str(C/'entry.mjs'),'map',json.dumps(R['rootConfig'],separators=(',',':'))]and owned['sequence']==0 and owned['process']==T['observedProcesses'][0],'whole actual parent launch/config/birth binding')
tree(E,['started.json','terminal.json','stdout.log','stderr.log','owned-0000.json']);verify(T['stdout']);verify(T['stderr']);need(T['stderr']['bytes']==0 and json.loads(Path(T['stdout']['path']).read_bytes())==dict(root=str(F),index=completion['index'],completion=dict(path='completion.json',sha256=R['actualCompletion']['sha256'],bytes=R['actualCompletion']['bytes'])),'whole Node raw completion return')
lines=[json.loads(x)for x in verify(R['parentStdout']).read_text().splitlines()];verify(R['parentStderr']);need(lines==[dict(pid=37754,timeoutSeconds=1200),R['actualReturnEnvelope']]and R['parentStderr']['bytes']==0,'whole Root caller two-record launch/return')
env=read(R['environmentPolicy']);need(env['valuesRetained']is False and env['requiredNativeReadOnlyEnvironmentSetByReviewedExternalController']is True and env['keys']==['HOME','LOGNAME','PATH','PYTHONDONTWRITEBYTECODE','TMPDIR','USER'],'finite Root caller names-only environment record')
# Retain current phase text only. Core/native binaries and history stay references.
def retain(p,n):
 p=Path(p);a=row(p);q=P/'raw-evidence'/n;need(not q.exists(),'new independent raw copy');q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb')as f:f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
 os.chmod(q,0o600);b=row(q);need(a['bytes']==b['bytes']and a['sha256']==b['sha256']and identity(p)[:2]!=identity(q)[:2],'full raw copied bytes/independent inode');raw_copies.append(dict(original=a,copy=b,distinctInode=True))
for label,root in [('mapping',F),('owned',E),('caller',Path(R['parentStdout']['path']).parent)]:
 for q in sorted(root.rglob('*')):
  if q.is_file()and q.suffix!='.wasm':retain(q,Path(label)/q.relative_to(root))
for x in [rootrow,R['rootAuthority'],R['rootConfig'],R['invocation']]:retain(x['path'],Path('root')/Path(x['path']).name)
for p,i in list(identities.items()):need(identity(Path(p))==i,'current-review final identity bookend')
phasepaths={str(rootrow['path']),*[R[k]['path']for k in ['rootAuthority','rootConfig','invocation']],R['sourceIndex']['path'],R['sourcePeer']['index']['path'],R['sourcePeer']['result']['path'],str(C/'source-inputs.json'),*[refs[k]['path']for k in ['node','jcoApi','parser','shimClocks','shimIo','nativeEngine','nativeMetadata','nativePins','packageInventory']],art['typeGraph']['path'],art['callableCoreGraph']['path']};allrows=[seen[k]for k in sorted(seen)if not Path(k).is_relative_to(P)];current=[x for x in allrows if Path(x['path']).is_relative_to(F)or Path(x['path']).is_relative_to(E)or Path(x['path']).is_relative_to(Path(R['parentStdout']['path']).parent)or x['path']in phasepaths]
save('input-hashes.json',dict(schemaVersion=1,files=current,reviewedSourceInputs=row(C/'source-inputs.json'),reviewedSourceRowsRehashed=12079,reviewedFamilyIndices=I['families'],uniqueActualInputsRehashed=len(allrows),historicalTreesRecopied=False));save('raw-copy-map.json',dict(schemaVersion=1,files=raw_copies));save('core-and-source-relation.json',dict(schemaVersion=1,largeCore=mapped['clock_v13.core.wasm'],originalLargeCore=refs['generatedFiles']['clock_v13.core.wasm'],inlineCores=cores,allFourWholeBytesEqual=True,mappedPrefixBytes=len(na),originalPrefixBytes=len(oa),wholeRemainingGlueBytesEqual=True,remainingGlueBytes=len(nb)+len(marker),mappedSourceParsedByPinnedParser=True,generatedModuleImported=False))
fixed=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_V13_MAPPED_V2_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,sourceIndexSha256=R['sourceIndex']['sha256'],componentSha256=refs['component']['sha256'],nativeEngineSha256=refs['nativeEngine']['sha256'],nativeSourceFiles=342,externalEmbeddingSources=3,fullMetadataFields=64,selectedManifestCount=9,allFourActualCoreBytesUnchanged=True,allNewGeneratedFilesAndStaticBindingsVerified=True,applicationGeneratedModuleImported=False,ordinaryApplicationExportsInvoked=False,jcoCompilerWasmHelpersInvoked=True,reviewerPinnedHostParserInvoked=True,reviewerApplicationOrMappingOrGuestActionsInvoked=False,fullClockProfileAcceptance=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
direct=dict(sourceIndex=R['sourceIndex'],sourcePeer=R['sourcePeer'],component=refs['component'],mappingOptions=refs['mappingOptions'],mappingResult=R['mappingResult'],actualIndex=R['actualIndex'],actualCompletion=R['actualCompletion'],mappingRootAuthority=R['rootAuthority'],mappingConfig=R['rootConfig'],rootObservation=rootrow,externalParentTerminal=R['externalParentTerminal'],mappedFiles=mapped,actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],node=refs['node'],jcoApi=refs['jcoApi'],parser=refs['parser'],shimClocks=refs['shimClocks'],shimIo=refs['shimIo'],inputHashes=row(P/'input-hashes.json'),rawCopyMap=row(P/'raw-copy-map.json'),parserTerminal=row(P/'parser-terminal.json'),coreAndSourceRelation=row(P/'core-and-source-relation.json'))
coverage=dict(indexedMappingFiles=13,actualMappingFiles=15,generatedLoadingFiles=7,externalCoreFiles=1,inlineCoreModules=3,componentCapabilityInterfaces=3,staticJsShimImports=2,staticShimBindings=3,mappedUndefinedBindingGuards=6,soleScalarRunFunctions=1,emptyUtilHelpers=1,sourceRowsRehashed=12079,sourceFamilies=18,packageFiles=4889,packageLinks=21,actualOwnedNodeProcesses=1,ownedGroups=1,rawTextCopies=len(raw_copies),uniqueActualInputsRehashed=len(allrows),compactCurrentDescriptorRows=len(current))
limits=[
 'Mapping/transpile only. Genuine Jco compiler-Wasm helpers were invoked by Root; the generated application module and its ordinary export were never imported/called. No application native engine/stock-Wasmtime runtime behavior is proved by this phase.',
 'All seven returned loading files plus caller package are accounted: six Jco files, caller adds exact package.json as seventh. Large external core and three complete literal inline cores match b073 component bytes. All non-glue files match original output; the entire glue suffix after the mapped prefix is byte-identical. Fresh pinned Node/Acorn parser checked every actual import/destructure/undefined guard, export/helper/TLA/core-loader binding and standard shim Source exports without importing application/shim modules.',
 'Two file-URL JS shim imports are not a new component capability footprint. Original unchanged component has exactly monotonic-clock/wall-clock/poll@0.2.10 from b073 type/callable graph proof. No new binary/WIT decode or individual host-call trace is claimed. Static shim presence/callability expectations do not substitute for the future runtime test.',
 'Whole actual native read-only frame has original64 fields/native342+3/nine manifests/pin, preserving original/tmp native paths and separate private package roots. No355/75/80-field metadata or state is projected. The recheck callable is a descriptor record, never serialized executable authority.',
 'Current declared12079rows/18families and physical4889+21 package bytes/modes/aliases were independently checked. Compact ledger references the sealed Source input manifest/family indices and records current mapping/phase/tool descriptors; no inherited trees were recopied. Actual invocation final protections are Source-controlled flow plus clean0/returned DATA, not standalone per-read snapshots or global environment/OS attestation.',
 'Root Node37754 exited0, all observed owned groups gone, no signals/timeouts/forced/errors and empty stderr. Root tool19813raw0 remains reported tool evidence; operational54.4s is not a benchmark. Node/Acorn host grammar parser was the only new reviewer tool action; map API/Jco/engine/guest actions were not rerun.',
 'Historical pure-profile failures and first-clock single-WT evidence remain unchanged; neither is relabeled as full clock acceptance. Retained/fresh Jco and stock-WT ReactDOM differential, plus all seven resource/Date/monotonic/snapshot/timer cancellation/self-clear/fatal/all-invalid/interest teardown tests remain separate future gates. A new Root-reviewed mapped-output record is still required before runtime.'
]
save('results.json',{**fixed,**direct,'coverage':coverage,'checks':checks,'selectedInterfaces':refs['selectedInterfaces'],'jcoReturnedJsImports':shape['imports'],'fullStaticAudit':parsed,'limits':limits,'rootReviewedMappedRecord':None,'runtimeAuthority':None})
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredExactDescriptors=direct,requiredCoverage=coverage,limitationsMustBePreserved=limits,issuesAnyRuntimeAuthority=False))
(P/'README.md').write_text('Independent clock-v13 mapped-v2 DATA review\n\nBounded mapped-output PASS. Seven generated loading files, four unchanged core modules, full static standard-shim bindings/sole scalar ABI, current native/package/source and actual raw0 ownership are verified. Only the pinned host grammar parser ran; application/generated module/Jco map/engine/guest APIs were not invoked by the reviewer.\n\n'+ '\n\n'.join(limits)+'\n')
save('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CLOCK_V13_MAPPED_V2_DATA_REVIEW_V1',result=row(P/'results.json'),contract=row(P/'result-contract.json'),inputHashes=row(P/'input-hashes.json'),rawCopyMap=row(P/'raw-copy-map.json'),reviewerHostGrammarParserOnly=True,generatedApplicationImported=False,operationalAdmission=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():r=row(q);files.append(dict(r,path=q.relative_to(P).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for n in ['index.json','results.json','result-contract.json','receipt.json']:print(json.dumps(row(P/n)))
print(json.dumps(dict(sealed=True,members=len(files),checks=checks,currentDescriptorRows=len(current),allRehashedInputs=len(allrows),rawCopies=len(raw_copies),generatedOrMapActions=False)))
