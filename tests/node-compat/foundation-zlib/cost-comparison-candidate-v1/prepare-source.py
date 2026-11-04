"""Source/data preparation ONLY. No codec/library, selector or owner is imported."""
from pathlib import Path
import ast,hashlib,json,re,stat
HERE=Path(__file__).parent.resolve()
REPO=Path('/Users/dan/dev/StarlingMonkey')
TOOL=Path('/tmp/starling-node-compat/native-toolchain-lock')
STAGE=Path('/tmp/starling-node-compat/zlib-source-v4')
FREEZE=Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze')
inputs={};checks=[]
def need(value,message):
    if not value:raise AssertionError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,expected=None,size=None):
    declared=Path(path);p=declared.resolve(strict=True);info=p.lstat();need(stat.S_ISREG(info.st_mode),'Regular source')
    raw=p.read_bytes();need(expected is None or sha(raw)==expected,'Source SHA');need(size is None or len(raw)==size,'Source bytes')
    inputs[str(declared)]={'path':str(declared),'canonicalPath':str(p),'sha256':sha(raw),'bytes':len(raw)};return raw
def load(path,h=None,n=None):return json.loads(read(path,h,n))
def write(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def done(name):checks.append({'check':name,'passed':True,'sourceOrDataOnly':True})
ledger=load(REPO/'docs/node-compat/zlib-cost-comparison-source-inputs.json')
read(REPO/'docs/node-compat/zlib-cost-comparison-proposal.md')
for row in ledger['files']:read(row['path'],row['sha256'],row['bytes'])
package=load(TOOL/'node_modules/fflate/package.json');need(package['version']=='0.8.3'and package['exports']['./browser']['import']['default']=='./esm/browser.js','Explicit browser entry')
browser=read(TOOL/'node_modules/fflate/esm/browser.js').decode()
need(not re.search(r'^\s*import\s',browser,re.M),'Browser module no static dependency import')
need('if (o.mtime != 0)'in browser and 'new Date(o.mtime || Date.now())'in browser and 'opt.level == null ? 6 : opt.level'in browser,'Inspected fixed sync branches')
adapter=TOOL/'node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/zlib.js'
need('import * as host from "jco:node/zlib@0.1.0";'in read(adapter).decode(),'Existing Jco nonportable host delegation')
done('pinnedFflateAndCustomHostAdapterInspectedWithoutInvocation')
function_names=['zlibSync','unzlibSync','gzipSync','gunzipSync','deflateSync','inflateSync']
segments=[]
for name in function_names:
    match=re.search(r'^export function '+name+r'\([^\n]*\) \{\n.*?^\}',browser,re.M|re.S);need(match is not None,'Actual sync function')
    source=match.group();segments.append({'symbol':name,'startLine':browser.count('\n',0,match.start())+1,'sha256':sha(source.encode()),'source':source})
write('fflate-source-inspection.json',{'schemaVersion':1,'state':'PINNED_SOURCE_INSPECTED_NOT_EXECUTED','packageVersion':'0.8.3','browserEntry':ledger['files'][1],'functions':segments,'gzipHeaderDateBranchUntakenByFixedMtime0':'Source conditional only; actual bundle and runtime proof pending','asyncWorkerBlobRoutes':'Present in unselected async source; not erased/proven guest-compatible','codecInvoked':False})

specs=[('empty',0,'empty'),('small-repeat',64,'repeat-abc123'),('small-prng',64,'xorshift32-low-byte'),('large-repeat',524288,'repeat-abc123'),('large-prng',524288,'xorshift32-low-byte')]
fixtures=[]
for name,size,pattern in specs:
    data=bytearray(size);state=0x6d2b79f5
    for i in range(size):
        if pattern=='repeat-abc123':data[i]=b'abc123'[i%6]
        else:
            state^=(state<<13)&0xffffffff;state^=state>>17;state^=(state<<5)&0xffffffff;state&=0xffffffff;data[i]=state&255
    fnv=2166136261
    for value in data:fnv=((fnv^value)*16777619)&0xffffffff
    fixtures.append({'id':name,'bytes':size,'pattern':pattern,'seed':0x6d2b79f5 if 'prng'in name else None,'rawSha256':sha(data),'rawFNV1aU32':fnv,'statisticalIncompressibilityClaim':False})
operations=[('deflateSync','zlibSync','zlib','encode'),('inflateSync','unzlibSync','zlib','decode'),('gzipSync','gzipSync','gzip','encode'),('gunzipSync','gunzipSync','gzip','decode'),('deflateRawSync','deflateSync','raw','encode'),('inflateRawSync','inflateSync','raw','decode')]
cases=[{'id':'codec-v1.'+f['id']+'.'+op,'fixture':f['id'],'operation':op,'format':fmt,'direction':direction,'logicalUncompressedBytesPerOperation':f['bytes'],'timingNMax':128 if f['bytes']>64 else 32768,'encodedInputOracle':None,'providerOutputOracle':None}for f in fixtures for op,ff,fmt,direction in operations]
write('fixtures.json',{'schemaVersion':1,'state':'RAW_FIXTURE_HASHES_ONLY_NO_CODEC_ORACLE','fixtures':fixtures,'encodedFixtures':None,'NodeCrossDecodeProof':None})
protocol={'schemaVersion':1,'state':'SOURCE_PROPOSAL_NO_ACTION_AUTHORITY','version':'bounded-zlib-cost-v1','operationMap':[{'native':op,'fflateBrowser':ff,'format':fmt,'direction':direction}for op,ff,fmt,direction in operations],'cases':cases,'caseCount':30,'caps':{'allCodecInputsBytes':1048576,'allCodecOutputsBytes':16777216,'rawFixtureBytesMax':524288,'everyActualEncodingMustFitDecodeInputCap':True},'nativeOptions':None,'fflateEncoderInternalOptions':{'level':6},'fflateGzipInternalOptions':{'level':6,'mtime':0},'validDomainOnly':True,'encodedByteIdentityRequired':False,'fullUntimedCorrectness':{'encoderStreams':45,'crossDecoderEdges':135,'threeRetainedRotations':True,'freshJco':True,'freshWasmtime':True,'firstAndRetainedCountersAndOwnership':True,'actualFixtureByteEquality':True,'allProviderCompressedInputsSizeCheckedBeforeDecode':True},'arms':['native-on','fflate-on','fflate-off'],'comparisons':[{'id':'same-engine-provider','A':'native-on','B':'fflate-on','sameActualEngineRequired':True},{'id':'unused-profile','A':'fflate-on','B':'fflate-off','identicalGuestBundleRequired':True}],'sampling':{'repetitions':3,'order':'AB/BA/AB','warmups':3,'samplesPerTimedWorker':7,'timedWorkersIfAll30CasesAdmitted':360,'calibration':'Positive full-unit pilots; geometric N=1,2,4,... to case bound; choose the same smallest power of two meeting50ms for BOTH arms. If either cannot reach target within bounds, refuse entire timing phase; no omit, clipping or silently revised cap.','sampleTargetMs':50,'maxOperationN':32768,'largeCaseOperationNMax':128,'pilotsBeforeTimingRequired':True,'pilotAndPublicCaseHardMs':600000,'workerHardMaxMs':7200000,'workerBudget':'ceil(2*pilotPerOperationMs*N*(3+7)+pilotPerOperationMs*N+120000+2*max(0,pilotWholeProcessMs-pilotPerOperationMs)); refuse if above ceiling; do not run old16-iteration budget helper with new N.','noDeadlineExtensionOrSampleOmission':True},'measurement':{'timedFullOutputFNV':True,'timedFullByteExpectedComparison':False,'untimedFullBytesAndCrossDecode':True,'controls':['consume-input','copy-input-and-consume','harness-no-codec'],'controlsSubtracted':False,'logicalByteUnit':'Uncompressed fixture bytes, encode AND decode','emptyByteThroughput':None,'emptyOutputRatio':None,'emptyMetric':'operations/second','rawCompressedInputAndOutputLengthsRequired':True,'freshProcessReplicatesNotIndependentWithinWorkerSamples':True},'allFutureAuthorityNull':True,'operational350AdmissionChanged':False,'metadataProjection':False}
need(len(cases)==30 and len({r['id']for r in cases})==30,'Thirty finite cases')
need(protocol['sampling']['timedWorkersIfAll30CasesAdmitted']==30*2*3*2,'Exact worker count')
protocol['proposedPublicABI']={'allReturns':'string','observe':'Untimed full raw-output base64 JSON, <=2MiB; never called in timing worker','batch':'Compact complete checksum/counter JSON; no retained payload arrays','actualEmittedWITAndTypes':None,'newNativeEngineExports':False,'emptyBackingIdentityIsolationClaim':False}
write('protocol.json',protocol);done('fiveRawFixturesThirtyCasesAndExplicitBoundsPreparedWithoutCodec')

pins=load(REPO/'tests/node-compat/foundation-zlib/reviewed-native-v4-validation-bootstrap-pins-v1.json')
facts=[];catalog=set()
for label in ['normal-off','disabled-off']:
    pin=pins['variants'][label];meta_path=FREEZE/(label+'.engine.wasm.build.json');meta=load(meta_path)
    freeze_path=FREEZE/(label+'-freeze-receipt.json');freeze=load(freeze_path,pin['freezeReceiptSha256'])
    need(meta['engineSha256']==pin['engineSha256'] and len(meta['sourceManifest'])==350,'Genuine350 data tuple')
    for row in meta['sourceManifest']:read(FREEZE/'source'/row['path'],row['sha256'])
    catalog.update(row['path']for row in meta['selectedModuleManifests'])
    facts.append({'label':label,'engineSha256':meta['engineSha256'],'engineBytes':meta['engineBytes'],'metadata':inputs[str(meta_path)],'freezeReceipt':inputs[str(freeze_path)],'sourceRoot':str(FREEZE/'source'),'nativeInputs':350,'freezeCopyRecords':len(freeze['copies']),'zlibEnabled':meta['zlibEnabled'],'gcStress':meta['gcStress'],'entropyPolicy':meta['entropyPolicy'],'selectedManifests':meta['selectedModuleManifests'],'costPairAdmission':False})
write('existing-native-facts.DATA-ONLY.json',{'schemaVersion':1,'state':'EXISTING_BUILD_VALIDATION_FACTS_NOT_COST_OR_OPERATIONAL_AUTHORITY','variants':facts,'sourceManifest350':meta['sourceManifest'],'newCostEnginePins':None,'newBackendAdmission':None,'existingFactsPromoteNoRuntimeBackendBoolean':True})

selector_paths={
 'tests/node-compat/module-selection.mjs','tests/node-compat/private-ticks-admission.mjs','tests/node-compat/classic-streams-admission.mjs','tests/node-compat/zlib-admission.mjs','builtins/node-compat/validate-manifest.mjs','builtins/node-compat/manifest.schema.json','tests/node-compat/legacy-stream-web-receipts.json',
 'tests/node-compat/foundation-zlib/native-integration-candidate-v4/compile-input.mjs','tests/node-compat/foundation-zlib/native-integration-candidate-v4/admission-pins.json','tests/node-compat/foundation-zlib/native-integration-candidate-v4/policy.json','tests/node-compat/foundation-zlib/native-integration-candidate-v4/layer-policy.py',
 'tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json','tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json','tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py',
 'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/admission-pins.json','tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/policy.json','tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/layer-policy.py',*catalog}
snapshot=[]
for name in sorted(selector_paths):
    source=STAGE/name;raw=read(source);target=HERE/'selector-snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb')as out:out.write(raw)
    snapshot.append({'originalPath':str(source),'canonicalOriginalPath':str(source.resolve()),'snapshotPath':str(target.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
by_snapshot={str((STAGE/name).resolve())for name in selector_paths}
literal_edges=[]
for name in sorted(selector_paths):
    if not name.endswith('.mjs'):continue
    source=STAGE/name;text=source.read_text()
    requests=re.findall(r"(?:from\s*|new URL\()(['\"])(\.[^'\"]+)\1",text)
    for quote,request in requests:
        target=(source.parent/request).resolve()
        if name=='tests/node-compat/module-selection.mjs' and request=='../../':
            need(target==STAGE.resolve() and target.is_dir(),'Exact configured repository context')
            literal_edges.append({'importer':name,'request':request,'kind':'configured-repository-directory','resolvedSnapshotPath':'selector-snapshot'})
        else:
            need(str(target)in by_snapshot,'Selected JS literal read/import missing: '+str(target))
            literal_edges.append({'importer':name,'request':request,'kind':'exact-file-import-or-data','resolvedSnapshotPath':str(Path('selector-snapshot')/target.relative_to(STAGE.resolve()))})
native_index=load(REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4/index.json')
for suffix in ['module-selection.mjs','zlib-admission.mjs']:
    row=next(r for r in native_index['files']if r['path']=='source/tests/node-compat/'+suffix)
    read(STAGE/'tests/node-compat'/suffix,row['sha256'],row['bytes'])
need('operational admission CLOSED'in (STAGE/'tests/node-compat/zlib-admission.mjs').read_text(),'Operational350 remainsclosed')
write('selector-snapshot.json',{'schemaVersion':1,'state':'ACTUAL350_SELECTOR_AND_LITERAL_JS_READ_SOURCE_SNAPSHOT_NOT_EXECUTED','files':snapshot,'literalImportAndDataEdges':literal_edges,'nativeSourceReads':'350 genuine frozen source files, separately pinned in DATA-ONLY facts/input manifest','selectedCatalogSize':len(catalog),'operationalAdmission':'CLOSED, preserved source','PythonAncestryTreeOrPackagingClosureComplete':False})
done('actual350SelectorStaticImportsLiteralReadsAndCatalogCopiedExclusiveWithoutImport')

reuse_root=REPO/'tests/node-compat/foundation-classic-streams/measurement-execution-activated-v2'
reuse=[]
for name in ['owned-host.mjs','collect-worker.mjs','deadline-policy.mjs','instantiate.mjs','bundle-matched.mjs']:
    read(reuse_root/name);reuse.append({'file':inputs[str(reuse_root/name)],'scope':'Source mechanism only. Old preflights/consumed families HELD; no executable reuse authority.'})
memory_root=REPO/'tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v2'
for name in ['worker.mjs','contracts.mjs']:read(memory_root/name);reuse.append({'file':inputs[str(memory_root/name)],'scope':'Small proof-free worker/strict actual-type pattern; new codec worker not implemented.'})
scalar=REPO/'tests/node-compat/foundations/native-scalar-harness.mjs'
read(scalar);reuse.append({'file':inputs[str(scalar)],'scope':'Pattern only: separate sourceRoot, genuine selected manifests, explicit adapter and imports[]/scalarWIT. Unmodified helper is NOT usable: old registrar pin/operational selector,120s sync child,mutable here report writes. No invocation.'})
for name in ['dist/bundle.js','dist/bundle.d.ts']:
    read(TOOL/'node_modules/@bytecodealliance/jco'/name)
need('bundleComponentChunk'in (TOOL/'node_modules/@bytecodealliance/jco/dist/bundle.d.ts').read_text(),'Actual supported bundle API')
write('reuse.json',{'schemaVersion':1,'state':'PINNED_MECHANISMS_SOURCE_INSPECTED_ONLY','files':reuse,'oldN16BudgetFunctionReusableUnchanged':False,'oldFamilyInvoked':False,'newCodecsDoNotRequirePrivateQueueExport':True})
write('future-authority.json',{'schemaVersion':1,'state':'UNCONFIGURED_ZLIB_COST_SOURCE_PROPOSAL','rootReview':None,'pairPins':None,'correctnessProof':None,'packagingPhysicalClosure':None,'actualComponentTuples':None,'actualEmittedABI':None,'quietWindow':None,'actionsAllowed':False,'timingAllowed':False,'operationalAdmissionAllowed':False})
write('packaging-context-plan.json',{'schemaVersion':1,'state':'FRESH_CONTEXT_IMPLEMENTATION_REQUIRED_BEFORE_ANY_ACTION','configuredNativeSourceRoot':str(STAGE),'frozenNativeSourceRoot':str(FREEZE/'source'),'preparationProvenance':'native-integration-candidate-v4 source/index facts only; do not follow historical prep/oldRoot consumed rows after promotion','freshPackagingToolRoot':None,'physicalConsumedClosure':None,'noRootLiveOldFiveFallback':True,'no350To355Projection':True,'newExplicitDiagnosticCostGate':None,'genuineBuildOnlyGate':'validateZlibBuildSourceAdmission','ordinaryOperational350Gate':'validateZlibSourceAdmission remains CLOSED','requiredNewClosure':['350 frozen native inputs/external3 and actual two variant metadata/freezes','full fresh selector snapshot and immutable literal read dependencies','all exact packaging/loader/ComponentizeJS/Jco/Rolldown files and declared tool links','regular LIVE preview1 adapter988224 and seven standardWITpackage files','all provider/fixture/guest/publicWIT/worker/oracle/correctness sources','packaging runner/ownedcollector/deadline/newfinitebudget/results collector','actual bundle resolver/physical/virtual source graph and exact options','actual final binary typegraph/core/imports[]/publicABI and common Buffer provenance'],'existingNativeToolClosureAloneSufficient':False,'allOldZlibContextsHeld':True})
write('cli-plan.json',{'schemaVersion':1,'state':'CLI_CONTRACT_ONLY_NO_RUNNABLE_AUTHORIZED_ENTRY','entries':{'prepareAndSeal':None,'untimedNodeOracleAndCrossDecode':None,'buildComponents':None,'guestCorrectness':None,'pilots':None,'measure':None,'audit':None},'futureArguments':['fresh immutable input-manifest path+SHA','new Root reviewed genuine350 pair authority path+SHA','exact actual correctness index/result','new output directory, exclusive/noresume','bounded worker descriptor path+SHA'], 'sourceCLIImplemented':False,'actionsAllowed':False})
done('collectorApiAndFreshContextRequirementsPinnedWithoutOwnerActions')
for p in HERE.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
need(all(v['bytes']<=524288 for v in fixtures)and all(v['bytes']<=1048576 for v in fixtures),'Raw input bounds')
need(all(v['encodedInputOracle']is None and v['providerOutputOracle']is None for v in cases),'No fabricated codec oracles')
done('sourceSyntaxClosedAuthorityAndNoFutureOracleFabrication')
write('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_PROPOSAL_INPUT_BYTES_ONLY_NOT_PACKAGING_CLOSURE','inputs':list(inputs.values()),'actualFuturePackagingPhysicalClosure':None,'ownerHelpersInvoked':False,'codecOrLibraryInvoked':False})
write('source-checks.json',{'schemaVersion':1,'state':'PURE_SOURCE_AND_DATA_PREPARATION_CHECKS_PASSED','checks':checks,'count':len(checks),'codecLibraryNodeOracleBundleNativeGuestHostOrTimingInvoked':False,'operational350AdmissionChanged':False})
print(json.dumps({'sourceDataGroups':len(checks),'fixtures':5,'cases':30,'selectorSnapshotFiles':len(snapshot),'literalEdges':len(literal_edges),'sourceInputs':len(inputs),'actions':False}))
