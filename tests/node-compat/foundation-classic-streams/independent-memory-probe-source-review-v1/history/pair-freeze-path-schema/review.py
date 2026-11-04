"""Independent source/data review only. Never imports owner code or artifacts."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import stat

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
SOURCE=BASE/'measurement-memory-probe-candidate-v1'
SOURCE_SHA='41a6f1b92c705c1ffe1a74d055614c4de344ddd5314f7ceddd4f5c124e7e6271'
OLD=BASE/'measurement-execution-activated-v2'
TIMING=BASE/'measurement-composition-timing-admission-amendment-v1'
ADOPTION=BASE/'production-adoption-v1'
REFS={};CACHE={}
def describe(path,sha=None,size=None):
 path=Path(path).absolute();before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 key=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
 if key not in CACHE:
  h=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
  CACHE[key]=h.hexdigest()
 after=path.lstat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 actual={'path':str(path),'sha256':CACHE[key],'bytes':before.st_size}
 if sha is not None:assert actual['sha256']==sha,(str(path),actual['sha256'],sha)
 if size is not None:assert actual['bytes']==size,str(path)
 previous=REFS.setdefault(str(path),actual);assert previous==actual
 return actual
def raw(path,sha=None):describe(path,sha);return Path(path).read_bytes()
def load(path,sha=None):return json.loads(raw(path,sha))
def put(name,value):
 with(HERE/name).open('x') as output:json.dump(value,output,indent=2);output.write('\n')
def indexed(root,sha=None):
 doc=load(root/'index.json',sha);assert len(doc['files'])==len({row['path'] for row in doc['files']})
 for row in doc['files']:
  name=Path(row['path']);assert not name.is_absolute() and '..' not in name.parts
  describe(root/name,row['sha256'],row['bytes'])
 return doc
def compact(oracle,index):
 one=oracle[index-index%2]['expected'];assert one['iterations']==1 and len(one['records'])==1
 record=one['records'][0];value=2166136261
 for item in [record['checksum'],record['units']]:value=((value^(item&0xffffffff))*16777619)&0xffffffff
 signed=value if value<2**31 else value-2**32
 return {'result':{'scenario':one['scenario'],'iterations':1,'checksum':signed,'unsignedChecksum':value,'totalUnits':one['totalUnits'],'scheduledCallbacks':one['scheduledCallbacks'],'records':[]}}
def stringify(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def tree(root):
 result=[]
 def visit(current):
  for path in sorted(current.iterdir()):
   info=path.lstat();kind='symlink' if stat.S_ISLNK(info.st_mode) else 'directory' if stat.S_ISDIR(info.st_mode) else 'file' if stat.S_ISREG(info.st_mode) else None
   assert kind;result.append({'path':str(path.relative_to(root)),'kind':kind})
   if kind=='directory':visit(path)
 visit(root);return sorted(result,key=lambda row:row['path'])
def main():
 source=indexed(SOURCE,SOURCE_SHA);assert len(source['files'])==20
 source_files={row['path']:row for row in source['files']}
 inputs=load(SOURCE/'input-freeze.json');assert len(inputs['inputs'])==10295
 actual_inputs={row['path']:row for row in inputs['inputs']};assert len(actual_inputs)==10295
 for row in actual_inputs.values():assert Path(row['path']).is_absolute();describe(row['path'],row['sha256'],row['bytes'])
 # Reconstruct the producer's entire finite manifest without running its sealer.
 expected={}
 def add(path,sha=None,size=None):
  item=describe(path,sha,size);prior=expected.setdefault(item['path'],item);assert prior==item
 inherited=load(TIMING/'input-freeze.json');assert len(inherited['inputs'])==9205
 for row in inherited['inputs']:add(row['path'],row['sha256'],row['bytes'])
 for folder,sha in [(TIMING,'78b3e5a0e3389f3d347a9b5700852361aae59cdbdc26813d9ff290f8ddf3e538'),(OLD,'1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'),(BASE/'measurement-stock-composition-candidate-v1','257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da'),(BASE/'independent-composed-timing-integrity-review-v1','3843d019f0976310f982e1b964bdcd2a09e8c85960e755214a89a03ac8117644')]:
  doc=indexed(folder,sha);add(folder/'index.json')
  for row in doc['files']:add(folder/row['path'],row['sha256'],row['bytes'])
 for name in ['reviewed-composed-timing-phase-v1.json','common-byte-composed-timing-root-results-v1.json','common-byte-composed-timing-output-closure-v1.json']:add(ADOPTION/name)
 closure=load(ADOPTION/'common-byte-composed-timing-output-closure-v1.json','adaff03059c935da603a1314c67c9aeaed3b1941964765430caa236f8fc31b3a')
 assert len(closure['regularOutputFiles'])==1037 and closure['rootObservedExitCode']==0
 for row in closure['regularOutputFiles']:add(row['path'],row['sha256'],row['bytes'])
 phase=load(ADOPTION/'reviewed-composed-timing-phase-v1.json','a822a7b02e0b81aae15504dd90d439be789c884336bfab7a7eddcccc0aec6890')
 for arm,record in phase['components'].items():
  add(record['componentPath'],record['componentSha256'],record['componentBytes'])
  for row in record['transpiledFiles']:add(Path(record['modulePath']).parent/row['name'],row['sha256'],row['bytes'])
  add(Path(record['modulePath']).parent.parent/'package.json','1239d4d885dcad42201a27ed9324f8f0f760b78700d8db9ced39a511cffe7eae',18)
 assert sorted(expected.values(),key=lambda row:row['path'])==inputs['inputs']
 contracts=raw(SOURCE/'contracts.mjs').decode();parent=raw(SOURCE/'parent.mjs').decode();worker=raw(SOURCE/'worker.mjs').decode();tests=raw(SOURCE/'tests.mjs').decode()
 tuples=ast.literal_eval(re.search(r'export const tuples=(\{.*?\});',contracts,re.S).group(1))
 glue_sha='747296bc080f83a7a97657224a6aff71cfeaff124a47d4266c5c65124d99a53c';dts_sha='e6e5d4c3d021092d6a6b662c6235f34987eca59672915aa18ab0e1618f3defe8'
 pair=load(OLD/'reviewed-pair.json','f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e')
 # Native metadata and freezes are read as data, never verified by owner mains.
 freezes=[]
 for label in ['benchmark-classic-on','benchmark-classic-off']:
  pin=pair['variants'][label]
  frozen=load(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);assert len(frozen['copies'])==525
  for row in frozen['copies']:describe(row['path'],row['sha256'],row['bytes']);assert row['path'] in actual_inputs
  metadata=load(pin['enginePath']+'.build.json',pin['metadataSha256'])
  assert metadata['diagnosticOnly'] is True and metadata['productionSelectorRefused'] is True
  freezes.append({'label':label,'engineSha256':pin['engineSha256'],'metadataSha256':pin['metadataSha256'],'copies':525,'diagnosticOnly':True})
 original_inputs=load(OLD/'input-freeze.json');assert len(original_inputs['toolTrees'])==2 and len(original_inputs['toolLinks'])==22
 for row in original_inputs['toolTrees']:
  assert str(Path(row['path']).resolve())==row['realPath'];assert tree(Path(row['path']))==row['entries']
 for row in original_inputs['toolLinks']:
  path=Path(row['path']);assert path.is_symlink() and os.readlink(path)==row['linkText'] and str(path.resolve())==row['resolvedTarget']
 oracle=load(OLD/'node-common-oracle.json')['cases']+load(OLD/'node-control-oracle.json')['cases'];assert len(oracle)==14
 cases=[{'index':index,'iterations':1,'setupReturn':oracle[index]['setup'],'batchRaw':stringify(compact(oracle,index)),'units':compact(oracle,index)['result']['totalUnits']} for index in [1,5]]
 descriptors=[];tuple_ledger=[]
 comparisons=[('same-engine-binding',['native-on','canonical-on']),('whole-profile',['canonical-on','canonical-off']),('different-stock-provider',['canonical-on','stock-on'])]
 for comparison,arms in comparisons:
  for repetition in range(3):
   order=arms[::-1] if repetition==1 else arms[:]
   for position,arm in enumerate(order):
    r=phase['components'][arm];root=Path(r['modulePath']).parent;core=next(row for row in r['transpiledFiles'] if row['name']=='common_byte.core.wasm')
    assert tuples[arm]==[r['componentSha256'],r['componentBytes'],core['sha256'],core['bytes']]
    assert r['coreFiles']==['common_byte.core.wasm'] and r['modulePath']==str(root/'common_byte.js')
    component={'path':r['componentPath'],'sha256':r['componentSha256'],'bytes':r['componentBytes']}
    critical=[component]+[{'path':str(root/name),'sha256':next(row for row in r['transpiledFiles'] if row['name']==name)['sha256'],'bytes':next(row for row in r['transpiledFiles'] if row['name']==name)['bytes']} for name in ['common_byte.core.wasm','common_byte.js','common_byte.d.ts']]+[{'path':str(root.parent/'package.json'),'sha256':'1239d4d885dcad42201a27ed9324f8f0f760b78700d8db9ced39a511cffe7eae','bytes':18}]
    assert critical[2]['sha256']==glue_sha and critical[2]['bytes']==133860 and critical[3]['sha256']==dts_sha and critical[3]['bytes']==2209
    native=pair['variants']['benchmark-classic-off' if arm=='canonical-off' else 'benchmark-classic-on']
    descriptor={'schemaVersion':1,'state':'PARENT_AUTHENTICATED_SMALL_MEMORY_WORKER_INPUT_V1','sourceIndexSha256':SOURCE_SHA,'parentPhaseSha256':'a822a7b02e0b81aae15504dd90d439be789c884336bfab7a7eddcccc0aec6890','comparison':comparison,'repetition':repetition,'runOrder':order,'position':position,'arm':arm,'component':component,'modulePath':r['modulePath'],'coreFiles':r['coreFiles'],'criticalFiles':critical,'expected':{'identityRaw':stringify(r['identity']),'probeRaw':stringify(r['checkpointProbe']),'cases':cases},'nativeEvidence':{'engineSha256':native['engineSha256'],'metadataSha256':native['metadataSha256'],'notLoadedByWorker':True}}
    compact_bytes=len(stringify(descriptor).encode());pretty_bytes=len((json.dumps(descriptor,ensure_ascii=False,indent=2)+'\n').encode());assert compact_bytes<=16384 and pretty_bytes<=16384
    descriptors.append({'descriptor':descriptor,'compactBytes':compact_bytes,'prettyBytes':pretty_bytes})
 for arm,r in phase['components'].items():tuple_ledger.append({'arm':arm,'component':{'path':r['componentPath'],'sha256':r['componentSha256'],'bytes':r['componentBytes']},'core':tuples[arm][2:],'modulePath':r['modulePath'],'criticalFilesPerWorker':5,'nativeHashOnlyProvenance':True})
 helper=describe(OLD/'instantiate.mjs','0b9d3cee8d40160a9fa0c56165e60d6a8ef57e10a9c722069f30d5f162c3492b',646)
 self_manifest={'schemaVersion':1,'sourceIndexSha256':SOURCE_SHA,'files':[{'path':str(SOURCE/name),'sha256':source_files[name]['sha256'],'bytes':source_files[name]['bytes']} for name in ['worker.mjs','contracts.mjs']]+[helper]}
 assert len((json.dumps(self_manifest,indent=2)+'\n').encode())<=4096
 # Confirm executable source boundaries/control flow without importing those entries.
 assert parent.index('const {index,inputSha}=await ownIndex()')<parent.index("await import('./contracts.mjs')")
 assert parent.index('validateAuthority(JSON.parse(authorityRaw),ownSha)')<parent.index("await import(pathToFileURL(join(timing,'admission.mjs')))")<parent.index('await mkdir(output)')
 assert worker.index('const manifestRaw=')<worker.index("await import('./contracts.mjs')")<worker.index('const raw=await small(descriptorPath')<worker.index('const {loadCompiled}=await import')
 assert worker.index('for(const row of descriptor.criticalFiles)await streamed')<worker.index('const {loadCompiled}=await import')
 assert worker.index("await persist('raw-'+label,observed)")<worker.index('assert.equal(typeof actual')<worker.index('if(serialized!==expectedRaw)')
 assert parent.index('const captured=await collectWorker')<parent.index('assert(captured.terminalExitZeroObserved')<parent.index('const actual=JSON.parse(captured.stdout)')
 assert parent.index('finally{try{const after=await auditParent()')<parent.index("await persist(join(output,'results.json')")<parent.index("await persist(join(output,'completion.json')")
 for forbidden in ['auditComposedCorrectness','executionPreflight','verifyConsumedSeal','selectTimingPhase','measure-body.mjs','input-freeze.json','global.gc(','.exports.memory','WebAssembly.Memory','getHeapStatistics','getHeapSnapshot','_malloc']:
  assert forbidden not in worker,forbidden
 assert '{deadlineMs:600000' in parent and "'2GiB starting capacity guard'" in parent and '800*1024**2' in parent
 for value in ['capacityBytes:null','growCount:null','guestHeapBytes:null','maxRssBeforeFinalHashKilobytes','terminalMaxRssKilobytes','compile-and-binding-load','after-final-critical-file-hash']:assert value in worker
 for value in ['detached:true','SIGTERM','SIGKILL','timeoutMs+2*graceMs+1000','await handle.sync()','terminalExitZeroObserved','ownedGroupGone','outputLimitExceeded']:
  assert value in raw(OLD/'owned-host.mjs').decode()
 collector=raw(OLD/'collect-worker.mjs').decode();assert 'args:[entry,...args]' in collector and 'maxOutputBytes:4*1024*1024' in collector
 null=load(SOURCE/'future-root-authority.json');assert null['sourceIndexSha256'] is None and null['memorySupplementAllowed'] is False
 for name in ['phase','timingReport','timingRootReceipt','integrityIndex']:assert null[name] is None
 checks=load(SOURCE/'source-checks.json');assert checks['pureChecks']==35 and checks['syntaxChecks']==4
 for command in checks['commands']:
  assert command['exitCode']==0
  for name in ['stdout','stderr']:
   row=command[name];describe(SOURCE/row['path'],row['sha256'],row['bytes'])
 assert json.loads(raw(SOURCE/'check-00.stdout.log'))['passed']==35
 # Inspect the sole executable pure test's dependency boundary before a separate authorized run.
 imports=re.findall(r"from\s+'([^']+)'",tests)
 assert set(imports)=={'node:assert/strict','node:fs/promises','node:path','node:url','./contracts.mjs'}
 assert not re.search(r'\b(?:import|require)\s*\(',tests)
 assert set(re.findall(r"from\s+'([^']+)'",contracts))=={'node:assert/strict'}
 old_root_names=['builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/factories.generated.h','builtins/node-compat/classic-streams/transformation-receipt.json','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs']
 repo=HERE.parents[3];root_impacts=[{'row':number,**row} for number,row in enumerate(inputs['inputs']) if row['path'] in [str(repo/name) for name in old_root_names]];assert len(root_impacts)==5
 result={'schemaVersion':1,'state':'INDEPENDENT_MEMORY_PROBE_SOURCE_STRUCTURE_AND_CLOSURE_PASSED','candidateIndexSha256':SOURCE_SHA,'indexedFiles':20,'consumedInputs':10295,'manifestReconstructionExact':True,'inheritedTimingRows':9205,'priorTimingOutputs':1037,'originalToolTrees':2,'originalToolLinks':22,'nativeFreezeWitnesses':freezes,'componentTuples':tuple_ledger,'plannedProcesses':18,'schedule':'AB/BA/AB per comparison; small1 then large5 on one instance; N1','descriptorMaxPrettyBytes':max(row['prettyBytes'] for row in descriptors),'descriptorMaxCompactBytes':max(row['compactBytes'] for row in descriptors),'descriptorLimitBytes':16384,'selfManifestBytes':len((json.dumps(self_manifest,indent=2)+'\n').encode()),'selfManifestLimitBytes':4096,'selfManifestFiles':3,'expectedPublicReturnsPerWorker':7,'expectedTotalPublicReturns':126,'actualProbeReturnsObserved':0,'ownerStoredPureChecks':35,'ownerStoredSyntaxChecks':4,'ownerTerminalsObservedByThisReader':False,'currentRoot5Dependencies':root_impacts,'noBlockerFound':True,'authorityOverlay':{'checkedInAuthorityClosed':True,'separateCallerHashedPathSupported':True,'sourceIndexMustEqualCandidate':True,'rootAuthorityIssuedByThisReader':False,'sealedSourceMutationRequired':False,'requiresExplicitMemorySupplementPermission':True,'priorTimingPermissionAloneInsufficient':True},'scope':['Source proposal only; no RSS or operational timing measurements exist in this review.','Parent audits proof/native/source before workers and in finally afterward; worker never loads full proof reports or native engine.','RSS stages include validation buffers, streaming I/O, compiler/cache/glue/allocator retention; not guest heap or cold physical startup.','18fresh processes means3 per arm/comparison, not18 independent observations of each arm. AB/BA/AB has2:1 first-arm imbalance.','Small precedes large on the same instance; ordering/retention effects persist.','600s is an operational deadline, not universal adequacy. No warmups/pilots/throughput samples/forcedGC/private memory.','Inherited five oldRoot preimages must remain until execution finishes, or a new explicitly context-aware source family is reviewed.','A future Root authority overlay can be supplied without mutating this20-file source; it remains a separate unissued action prerequisite.'],'noOwnerActionsOrRuntimeExecuted':True}
 put('results.json',result);put('expected-descriptor-ledger.json',{'descriptors':descriptors,'selfManifest':self_manifest,'expectedOnlyNotObservedGuestValues':True});put('external-references.json',{'files':sorted(REFS.values(),key=lambda row:row['path']),'binaryCopiesInsideReview':False})
 print(json.dumps({'state':result['state'],'inputs':10295,'descriptors':18,'maxDescriptorBytes':result['descriptorMaxPrettyBytes'],'selfManifestBytes':result['selfManifestBytes'],'stableReferencePaths':len(REFS),'runtimeActions':False}))
if __name__=='__main__':main()
