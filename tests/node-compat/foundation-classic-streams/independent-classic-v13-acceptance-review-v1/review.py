"""Narrow DATA-only acceptance audit. No referenced owner/helper is executed."""
import hashlib,json,stat
from pathlib import Path,PurePosixPath
HERE=Path(__file__).parent
CLASSIC=HERE.parent
REPO=Path('/Users/dan/dev/StarlingMonkey')
ACCEPT=CLASSIC/'production-acceptance-v13'
witnesses={};checks=[]
def need(value,message):
    if not value:raise AssertionError(message)
def read(path,expected=None,size=None):
    p=Path(path);before=p.lstat();need(stat.S_ISREG(before.st_mode),'Regular data witness')
    raw=p.read_bytes();after=p.lstat()
    need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Stable data witness')
    digest=hashlib.sha256(raw).hexdigest();need(expected is None or digest==expected,'Data hash: '+str(p));need(size is None or len(raw)==size,'Data bytes')
    witnesses[str(p)]={'path':str(p),'sha256':digest,'bytes':len(raw)};return raw
def load(path,expected=None,size=None):return json.loads(read(path,expected,size))
def ref(row):return load(row['path'],row['sha256'],row['bytes'])
def passed(name,**data):checks.append({'check':name,'passed':True,**data})
def packet(path,expected,size=None):
    p=Path(path);index=load(p,expected,size);seen=set()
    for row in index['files']:
        name=row['path'];q=PurePosixPath(name)
        need(not q.is_absolute() and str(q)==name and all(v not in('','.','..')for v in q.parts) and name not in seen,'Finite proof index member')
        seen.add(name);read(p.parent/name,row['sha256'],row['bytes'])
    return index
index=packet(ACCEPT/'index.json','398ecd5257b09a8038edae81ec7bcb2c2c3f9233ff2d41aeb783a48cd752b8b2')
receipt=load(ACCEPT/'acceptance-receipt.json','86e2230a6be37639f4ecadec8900bd1238ac38711f63150ec515d1f1e49bcc2b',16997)
need(len(index['files'])==2 and receipt['accepted']is True and receipt['state']=='ACCEPTED_BOUNDED_FOUNDATIONS_V13_CLASSIC_STREAMS' and receipt['overallRoadmapComplete']is False,'Bounded new authority')
parent=ref(receipt['parentAcceptance']);need(receipt['parentAcceptance']['sha256']=='9494e66c433346ee4c94e541b4dbd4844e6767e03a500dc9361c531a9747d769','Original v12 authority unchanged')
need(receipt['newCommitCreated']is False and receipt['workingTreeLayeredSourcesRequired']is True,'Source layering explicit')
passed('exactV13TwoFilesAndOriginalParentV12Authority',acceptanceSha256='86e2230a6be37639f4ecadec8900bd1238ac38711f63150ec515d1f1e49bcc2b',overallRoadmapComplete=False)

need(len(receipt['proofIndices'])==11 and len(receipt['references'])==13,'Exact reference bounds')
proofs={};proof_files=0
for name,row in receipt['proofIndices'].items():
    p=Path(row['path']);ix=packet(p,row['sha256'],row['bytes']);proof_files+=len(ix['files'])
    target=next(r for r in ix['files']if r['path']=='results.json')
    proofs[name]=load(p.parent/'results.json',target['sha256'],target['bytes'])
for row in receipt['references']:ref(row)
passed('allElevenProofIndicesMembersAndThirteenExplicitReferences',indices=11,indexedMembers=proof_files,explicitReferences=13,oldConsumedRowsFollowed=False)

native_manifest=None
expected_modes={'normal-off':(False,'off',True),'normal-runtime':(False,'runtime-only',True),'gc-off':(True,'off',True),'disabled-off':(False,'off',False)}
need(set(receipt['productionEngines'])==set(expected_modes),'Exactly four production variants')
for label,engine in receipt['productionEngines'].items():
    metadata=ref(engine['metadata']);freeze=ref(engine['freezeReceipt'])
    need((engine['gcStress'],engine['entropyPolicy'],engine['classicStreamsEnabled'])==expected_modes[label],'Actual finite variant')
    need(engine['nativeInputs']==freeze['nativeInputsVerified']==342 and engine['externalEmbeddingInputs']==freeze['externalEmbeddingInputsVerified']==3 and engine['frozenCopies']==len(freeze['copies'])==474,'Actual342/3/474 tuple')
    need(engine['sha256']==metadata['engineSha256']==freeze['engineSha256'] and engine['bytes']==metadata['engineBytes']==freeze['engineBytes'],'Engine tuple digest and size')
    need((metadata['gcStress'],metadata['entropyPolicy'],metadata['classicStreamsEnabled'])==expected_modes[label],'Actual metadata mode')
    need(freeze['state']=='immutable-trace-release-engine-frozen','Corrected production freeze state')
    if native_manifest is None:native_manifest=metadata['sourceManifest']
    need(metadata['sourceManifest']==native_manifest and len(native_manifest)==342,'Same genuine342 source manifests')
for row in native_manifest:read(REPO/row['path'],row['sha256'])
post=proofs['independent-five-file-classic-source-promotion-review-v1']
need(post['verifiedPassed']is True and post['changedRootPaths']==5 and post['unchangedOtherNativeInputs']==339 and post['currentNativeSourceInputs']==342,'Post-promotion exact5/339')
promotion=load(CLASSIC/'production-adoption-v1/five-file-corrected-classic-source-promotion-root-review-v1.json','30bdf0dc728ca7fa516f6964ed4a701be4fc4dc9b8de756cf6b39cd8f14604f9')
for change in promotion['changes']:
    after=change['reviewedAfter'];read(REPO/change['path'],after['sha256'],after['bytes'])
    need(oct(stat.S_IMODE((REPO/change['path']).lstat().st_mode))==change['modeBefore'],'Promoted mode retained')
need(receipt['zlib350OrConsumers355Accepted']is False and receipt['nativeInputs']==342,'No350/355 acceptance projection')
passed('fourCorrectedProductionTuplesAndCurrent342IncludingFiveAnd339',productionVariants=4,copiesPerVariant=474,allLive342HashesMatch=True,oldFreezeInventoriesReexecuted=False)

classic=proofs['independent-corrected-classic-results-review-v1']
classic_count=sum(len(v['structuralWitAudits'])for v in classic['variants'].values())
need(classic_count==15 and set(classic['variants'])=={'normal-off','normal-runtime','gc-off'} and classic['disabled']['componentBuilt']is False,'15 actual classic components and disabled refusal control')
node11=proofs['independent-corrected-node11-component-review-v1'];need(node11['nodeCases']==11 and node11['nodeCompatibilityPassed']is True,'Corrected11 source cases')
replay=proofs['independent-corrected-replay-results-review-v1'];need(replay['freshStageCount']==8 and replay['physicalFinalComponentCount']==40 and replay['reusedResults']==0,'Eight fresh stages40')
follow=proofs['independent-corrected-followon-results-review-v1'];need(follow['actualDerivedComponentCount']==20 and len(follow['gates'])==5,'Five follow-on gates20')
http=proofs['independent-corrected-http-results-review-v1'];need(http['responsesVerified']==6 and http['requestsPerHost']==3 and http['protectedAbortGroupsPerResponse']==29 and http['ordinaryClassicGroupsPerResponse']==19,'HTTP same-byte baseline/classic scope')
need(receipt['productionGateOccurrencesSeparate']=={'classicSuites':15,'node11Additional':1,'baselineReplay':40,'followon':20,'sameByteHttp':1} and receipt['globallyUniqueComponentCountClaim']is False,'Occurrences notglobal uniqueness')
passed('correctedProductionOccurrences15Plus1Plus40Plus20Plus1',occurrences=77,globalUniquenessClaim=False)

full=proofs['independent-workload-v2-results-review-v1'];common=proofs['independent-common-byte-stock-and-composition-results-review-v1'];timing=proofs['independent-composed-timing-integrity-review-v1'];rss=proofs['independent-process-rss-supplement-v2-results-review-v1']
need(full['individualReturnedObservations']==105 and full['fullNodeWorkloadCases']==20 and full['fullNodeBoundaryCases']==14,'Full20+14 diagnostic105')
need(common['composedDurableObservations']==308 and common['wholeOldParentPassed']is False,'308 preserved composition no failedparent relabel')
need(timing['freshWorkerPids']==168 and timing['pilotsDecoded']==42 and timing['timedWorkersDecoded']==126 and timing['actualPerBatchCompactValuesRetained']is False,'Original168 worker limitations')
need(rss['workers']==18 and rss['publicCalls']==126 and rss['typedReturns']=={'number':36,'string':90} and rss['old168WorkerThroughputReportUnchangedAndSeparate']is True,'RSS18/126 separate')
need(receipt['diagnosticEvidenceSeparate']=={'full20WorkloadsAnd14Boundaries':105,'commonByteCorrectnessObservations':308,'timingWorkers':168,'processRssSupplementWorkers':18,'productionPerformanceTransferClaim':False} and receipt['performanceAdvantageClaim']is False,'No diagnostic production-performance transfer')
need(full['engineSha256']=='12a8f7dc79e12e8bc3519b3fe72e898b226bbabde6930e63d3a6c30706b88274' and full['engineSha256']not in{e['sha256']for e in receipt['productionEngines'].values()},'Diagnostic engine distinct from production four')
size=receipt['sizeObservationSeparate'];need(size['sameEngineRegisteredVsBundledComponentBytesSaved']==14168969-13056344 and abs(size['sameEngineSavedPercent']-100*(14168969-13056344)/14168969)<1e-12,'Separate diagnostic same-engine size arithmetic')
passed('diagnostic10530816818EvidenceSeparatedFromProductionPerformance',diagnosticObservations=105,composedObservations=308,timingWorkers=168,rssWorkers=18,productionPerformanceTransfer=False)

pres=receipt['preservation'];actual=proofs['independent-artifact-preservation-results-review-v1']
need((pres['archiveFiles'],pres['copiedObjects'],pres['protectedOriginalDescriptors'],pres['selectedContextRows'],pres['sdkHostReferenceOccurrences'])==(21682,10835,17884,50894,55),'Bounded preservation cardinalities')
need(actual['regularFilesVerified']==21682 and actual['copiedObjectsVerified']==10835 and actual['verifiedPassed']is True,'Actual archive proof')
for key in ['embeddedPendingLabelsUnchanged','referencesAreNotCopiedBytes','sevenStatusSnapshotsAreDistinctCapturedObservations','oldTwelveZlibContextsRemainHeld']:need(pres[key]is True,'Preserved bounded semantics')
need(pres['contextCoverage']=='selected-rows' and pres['all17885OldByteSequencesPreservedClaim']is False and pres['oldPreflightRerunAuthorized']is False and pres['unavailableInspectionReadmeSha256']=='24e4ac4e3edb505e7e1fd6acf342352f5088628f4b966856bf8cce16facfa5ab','One unavailable and selected coverage')
need(post['oldZlibContextsHeld']==12 and post['oldContextTupleBytesVerified']==60,'Old contexts heldafterpromotion')
passed('preservationScopeOneUnavailableSevenSnapshots55ReferencesAndTwelveHolds',archiveBytesRetested=False,proofSource='f804 and b663 exact indexed bytes',selectedContextCoverage=True)

manifest=ref(receipt['publicClassicManifest']);need(manifest['profileVersion']==receipt['publicClassicProfileVersion']=='sm-node-22.14.0-m0.12','Exact classic profile')
need(manifest['status']=='UNAPPLIED optional classic-stream state-machine candidate. Host algorithms only; no selected native engine/component evidence.' and receipt['historicalManifestSourceOnlyLabelPreserved']is True,'Historical sourcelabel notrewritten')
for package,expected in [('@bytecodealliance/jco','1.40.0'),('@bytecodealliance/componentize-js','0.23.0')]:
    value=load(Path('/tmp/starling-node-compat/native-toolchain-lock/node_modules')/package/'package.json');need(value['version']==expected,'Locked package version')
need((receipt['nodeRelease'],receipt['jcoVersion'],receipt['componentizeJsVersion'],receipt['wasiVersion'])==('22.14.0','1.40.0','0.23.0','0.2.10'),'Pinned versions')
wash=load('/tmp/starling-node-compat/production-classic-corrected-http-v1/http/http-joint-wasmcloud-results.json')
need(wash['host']['version']=='2.11.0' and wash['host']['embeddedWasmtimeVersion']=='48.0.7','Actual officialwash declared version')
need(receipt['targetHosts']==['Wasmtime42.0.1','official wasmCloud wash2.11.0 (embedded Wasmtime48.0.7)'],'Exact hostscope')
passed('versionLabelsAndHistoricalSourceOnlyManifestRemainGenuine',node='22.14.0',jco='1.40.0',componentizeJs='0.23.0',wasi='0.2.10',hosts=['Wasmtime42.0.1','wash2.11.0/Wasmtime48.0.7'])

expected_http=['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:random/random@0.2.10']
need(receipt['http']['imports']==expected_http and receipt['http']['clockTypeOnly']is True and receipt['http']['countersPerHost']==[[1,1,1],[1,1,1]]and receipt['http']['sameInstanceReuseClaim']is False,'Exact HTTP caps/counterlimits')
need(receipt['http']['componentSha256']==http['componentSha256'] and receipt['http']['componentBytes']==http['componentBytes'],'Same exact HTTP tuple')
need(receipt['pureComponentsRequireNoImports']is True and receipt['runtimeOnlyPureCapability']==['wasi:random/random@0.2.10'],'Pure/runtimecaplimits')
need(receipt['nodeCallbackReturnParity']is False and receipt['completeNodeOrBufferClaim']is False and receipt['resetOrALSClaim']is False,'Known limitsnotpromoted')
limitations=' '.join(receipt['preservedLimitations'])
for phrase in ['getter parity is false','Symbol registry','combined owners','stdout bytes were not retained','Generic traps','168-worker','shared-machine n3','TLS']:need(phrase in limitations,'Explicit known limitation '+phrase)
getter=next(g for g in follow['gates']if g['gate']=='getter');need(getter['nodeCompatibilityPassed']is False and getter['nodeGetterReads']==[1,1,0]and getter['jcoAndWasmtimeGetterReads']==[0,0,0],'Gettercounterexample retained')
need(len(receipt['outstanding'])==7 and receipt['overallRoadmapComplete']is False,'Fullroadmapleftopen')
passed('getterSymbolCombinedGCRawStreamsHTTPResetALSAndCapabilityLimitsRemainExplicit',overallRoadmapComplete=False,newExecutionOrAuthorityIssued=False)

result={'schemaVersion':1,'state':'INDEPENDENT_BOUNDED_CLASSIC_V13_ACCEPTANCE_SCOPE_AND_REFERENCES_VERIFIED','acceptanceIndexSha256':'398ecd5257b09a8038edae81ec7bcb2c2c3f9233ff2d41aeb783a48cd752b8b2','acceptanceReceiptSha256':'86e2230a6be37639f4ecadec8900bd1238ac38711f63150ec515d1f1e49bcc2b','scopeReviewPassed':True,'concreteScopeOverclaims':[],'checks':checks,'proofIndicesVerified':11,'explicitReferencesVerified':13,'ownerHelpersOrConsumedRowsFollowed':False,'oldArchiveBytesRetested':False,'newAuthorityOrSourcePromotionIssued':False,'guestNativeHostTimingOrBuildExecuted':False,'overallRoadmapComplete':False}
for name,value in [('results.json',result),('byte-witnesses.json',{'schemaVersion':1,'files':list(witnesses.values())})]:
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'passed':len(checks),'proofIndices':11,'proofIndexedFiles':proof_files,'byteWitnesses':len(witnesses)}))
