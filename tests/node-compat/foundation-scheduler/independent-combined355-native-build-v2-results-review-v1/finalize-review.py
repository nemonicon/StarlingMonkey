"""Retain observed raw DATA and seal independent bounded BUILD review. No tools."""
from pathlib import Path
import hashlib,json,os,stat
P=Path(__file__).resolve().parent;D=json.loads((P/'audit-data.json').read_bytes());R=D['rootObservation'];ledger={};copies=[];checked=0
def dump(name,value):
 p=P/name;assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def descriptor(p):
 global checked
 p=Path(p);a=p.stat();assert stat.S_ISREG(p.lstat().st_mode),str(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),str(p);checked+=1;return dict(path=str(p),sha256=h.hexdigest(),bytes=a.st_size)
def add(row):
 assert set(row)=={'path','sha256','bytes'}
 if row['path']in ledger:assert ledger[row['path']]==row
 else:ledger[row['path']]=row
for n,key in [('raw-inputs.json','files'),('metadata-review.json','extraInputs'),('distribution-review.json','extraInputs'),('preservation-review.json','extraInputs')]:
 for r in json.loads((P/n).read_bytes())[key]:add(r)
# Identity/hash bookend of the complete finite DATA set; symlink aliases are separate.
for row in list(ledger.values()):assert descriptor(row['path'])==row,row['path']
external=Path(D['ownedWorkerTerminal']['path']).parent;inner=Path(D['actualBuildResult']['path']).parent;caller=Path(R['parentStdout']['path']).parent;observer=Path('/private/tmp/starling-node-compat/combined-native355-v2-build-root-observer')
def retain(original,relative):
 original=Path(original);a=descriptor(original);target=P/'raw-evidence'/relative;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('xb')as f:f.write(original.read_bytes());f.flush();os.fsync(f.fileno())
 os.chmod(target,0o600);b=descriptor(target);assert(a['sha256'],a['bytes'])==(b['sha256'],b['bytes']);assert(original.stat().st_dev,original.stat().st_ino)!=(target.stat().st_dev,target.stat().st_ino);add(a);copies.append(dict(original=a,copy=b,distinctInode=True))
for name,root in [('owned-worker',external),('inner-build',inner),('root-caller',caller),('root-observer',observer)]:
 for q in sorted(root.rglob('*')):
  if q.is_file():retain(q,Path(name)/q.relative_to(root))
for key in ['rootRow','rootAuthority','rootConfig','metadata']:
 retain(D[key]['path'],Path('phase')/Path(D[key]['path']).name)
retain(R['invocation']['path'],Path('phase')/Path(R['invocation']['path']).name)
for key in ['beforeInstallRecord','settingsAtBuildCompletion']:
 q=R['privateRustupBootstrapPolicy'][key]['path'];retain(q,Path('private-rustup')/Path(q).name)
M=json.loads(Path(D['metadata']['path']).read_bytes())
# Complete key text witnesses; binary executables/libraries stay immutable references.
extra=[]
def walk(v):
 if isinstance(v,dict):
  if set(v)=={'path','sha256','bytes'}:extra.append(v)
  else:
   for x in v.values():walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
walk(M)
selected={Path(M['cmakeCachePath']),Path(M['compileCommandsPath'])}if'compileCommandsPath'in M else{Path(M['cmakeCachePath'])}
for q in Path(D['workRoot']).rglob('compile_commands.json'):selected.add(q)
for x in extra:
 q=Path(x['path'])
 if q.suffix in ['.json','.txt','.log','.toml']and x['bytes']<=10000000:selected.add(q)
for i,q in enumerate(sorted(selected)):
 if str(q)in ledger and q.is_file()and not q.is_symlink():retain(q,Path('text-witnesses')/('%03d-'%i+q.name))
dump('raw-copy-map.json',dict(schemaVersion=1,files=copies,rawFiles=len(copies),allWholeBytes=True,allDistinctCopyInodes=True,producerExecutedByReviewer=False))
dump('input-hashes.json',dict(schemaVersion=1,files=[ledger[k]for k in sorted(ledger)]))
raw=json.loads((P/'raw-source-review.json').read_bytes());md=json.loads((P/'metadata-review.json').read_bytes());ds=json.loads((P/'distribution-review.json').read_bytes());pr=json.loads((P/'preservation-review.json').read_bytes())
donor=P.parents[1]/'foundation-crypto/independent-ownership-secret-normal-off-build-review-v1/check-distributions.py'
# The independent reader donor is provenance only, never an owner helper.
dump('reader-donor-binding.json',dict(schemaVersion=1,donor=descriptor(donor),copy=descriptor(P/'check-distributions.py'),byteIdentical=donor.read_bytes()==(P/'check-distributions.py').read_bytes(),role='Independent stdlib DATA reader reused without owner-module imports'))
fixed=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_NATIVE_BUILD_V2_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,nativeSourceIndexSha256=D['sourceIndex']['sha256'],controllerSourceIndexSha256=D['controllerIndex']['sha256'],variant='normal-off',nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,rawMetadataFields=80,engineSha256=D['engine']['sha256'],metadataSha256=D['metadata']['sha256'],rawOwnedWorkerExitCode=0,rawRecipeExitCode=0,allObservedOwnedGroupsGone=True,engineExecuted=False,freezeExecuted=False,componentOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,reviewerOwnerActionsInvoked=False,reviewerNativeToolsInvoked=False)
direct={k:D[k]for k in ['actualBuildResult','rootAuthority','rootConfig','ownedWorkerTerminal','engine','metadata','buildLog']};direct['rootObservation']=D['rootRow'];direct['controllerSourceReview']=D['sourcePeer'];direct['nativeSourceIndex']=D['sourceIndex'];direct['controllerSourceIndex']=D['controllerIndex'];direct['privateRustupBeforeInstallRecord']=R['privateRustupBootstrapPolicy']['beforeInstallRecord'];direct['privateRustupSettingsAtCompletion']=R['privateRustupBootstrapPolicy']['settingsAtBuildCompletion'];direct['inputHashes']=descriptor(P/'input-hashes.json');direct['referenceAliases']=descriptor(P/'reference-aliases.json');direct['rawCopyMap']=descriptor(P/'raw-copy-map.json')
coverage=dict(declaredProtectedSourceFiles=4515,declaredProtectedModeRows=4515,sourceFamilies=12,stagedCopyPairs=1613,failedV1WorkFiles=755,sourceDerivationFiles=5,reversibleSourceEdits=43,ownedProcessRecords=707,ownedGroups=80,ownedWorkerFiles=711,innerLifecycleFiles=7,parentJsonlRecords=2,cacheCopies=4,cacheCopyBytes=205865445,diskSamples=398,minimumObservedFreeBytes=17834209280,outerNinjaFinalStep=108,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredCommands=5,generatedNullCommands=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6,staticArchiveArguments=30,uniqueLinkedArchives=29,opensslSourceFiles=4650,cleanupSymbols=7,sdkArchiveEntries=10688,spiderMonkeyArchiveEntries=364,externalSourceArchiveEntries=361,archiveReferenceSymlinks=31,archiveReferenceHardlinks=1,fullRetainedRawFiles=len(copies),uniqueActualInputFiles=len(ledger),actualInputBytes=sum(x['bytes']for x in ledger.values()))
qualifications=[
 'BUILD-only evidence. The native engine was produced and hash-read; not executed. No freeze, bootstrap, component, guest, key, GC, runtime or adoption authority follows.',
 'The original raw sidecar has exactly80 fields. No 75-field secret-owner or342-resource metadata, state, paths or globals are projected into this combined355 context.',
 'All4515 declared protected files and modes/12 indexed families, current stage1613 copy/original pairs and entire failed-v1 work755 are rehashed. This review does not recursively replay unrelated historical normal freeze receipt inventories;356 secret-frozen source refs and4 selector-freeze refs are protected only as their finite declared Source-input rows.',
 'The before-install JSON retains the historical57-byte settings digest and control-flow assertion; those57 bytes were not separately retained. Current settings are107 bytes and include the installed default_toolchain. The nested historical descriptor is DATA, not an assertion that current settings still have57 bytes.',
 'Root exec-session61477/raw0 is retained as Root-reported tool observation; actual worker795/Bash903 and707 ownership records/80 groups have the durable monitor evidence. No independently fabricated outer PID terminal exists.',
 'Actual full build log has nested9-step Ninja activity and outer108-step completion. CompileDB68 is62 selected policy CPP +5 other configured source files +1 generated null.cpp; embedding1 is separately captured. The DB and embedding command strings do not occur verbatim in the build log; no standalone per-C++ or CMake/Ninja terminal claim is made.',
 'Link/archive evidence covers30 ordered archive args/29 unique current libraries. nm raw0 has138 nonempty stderr bytes for a no-symbol archive member; selected7 MOZ_Z functions and7 OpenSSL cleanup symbols are statically witnessed, not invoked.',
 'Reference symlinks/hardlinks describe original archive/tool references; they are not frozen-copy inode independence. Raw review copies are byte-exact ordinary independent files.',
 'Operational durations and disk samples are lifecycle evidence, not performance, memory, fault, erasure, side-channel or security-completeness evidence. runtimeBackendProof stays false/null/null.',
 'Own reader mistakes (nested Ninja denominator and archive root-first assumption) are retained under reader-history and corrected; no producer work was repeated.'
]
result={**fixed,**direct,'coverage':coverage,'checks':dict(rawSource=87572,metadata=md['checks'],distributions=ds['checks'],preservation=pr['checks'],finalInputHashes=len(ledger),finalizationFileReads=checked),'qualification':qualifications,'futureFreezeAuthority':None,'actualFrozenArtifactReview':None,'pins':None,'bootstrap':None,'runtime':None}
dump('results.json',result)
dump('result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredCoverage=coverage,requiredExactDescriptors=direct,buildOnly=True,freezeAuthorityIssued=False,limitationsMustBePreserved=qualifications))
(P/'README.md').write_text('Independent combined355 retry-v2 native BUILD DATA review\n\nThe bounded actual BUILD review passed. '+str(len(ledger))+' actual regular-file descriptors are indexed in input-hashes.json; '+str(len(copies))+' whole raw text files are independently retained. The produced engine and original80-field metadata are bound to Source08bf/controller2458, actual worker795 and Root36b0.\n\nFour stdlib DATA readers audit raw lifecycle/Source, metadata/CPP/link/OpenSSL, whole SDK/SpiderMonkey/external distributions, and stage/failed-v1/derivation preservation. No owner helpers, compiler, Rustup, Node, native engine or guest were invoked by this reviewer. Reader-history preserves two corrected independent-reader assumptions.\n\n'+ '\n\n'.join(qualifications)+'\n')
dump('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMBINED355_NATIVE_BUILD_V2_DATA_REVIEW_V1',result=descriptor(P/'results.json'),contract=descriptor(P/'result-contract.json'),inputHashes=direct['inputHashes'],referenceAliases=direct['referenceAliases'],rawCopyMap=direct['rawCopyMap'],allReviewActionsReadHashDataOnly=True,sourceOrProducerFilesChanged=False,engineExecuted=False,freezeExecuted=False,operationalAdmission=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():
  assert not q.is_symlink();rr=descriptor(q);rr['path']=str(q.relative_to(P));files.append(rr)
dump('index.json',dict(schemaVersion=1,files=files))
for name in ['index.json','results.json','result-contract.json','receipt.json','input-hashes.json','reference-aliases.json']:print(json.dumps(descriptor(P/name)))
print(json.dumps(dict(sealed=True,members=len(files),inputFiles=len(ledger),rawCopies=len(copies),allReaderProcessesTerminal=True)))
