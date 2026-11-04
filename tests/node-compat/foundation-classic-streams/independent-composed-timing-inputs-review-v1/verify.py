#!/usr/bin/env python3
"""Pure data/hash emulation of admission; never issues/executes a timing phase."""
import hashlib,json,os,re,stat
from pathlib import Path

HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;ADOPT=FAMILY/'production-adoption-v1'
CANDIDATE=ADOPT/'composed-timing-phase-candidate-v1.UNREVIEWED.json'
CANDIDATE_SHA='5793eef62685295cebe4a9b454ba90a55050d388a314d2736f2a523bd9d301cb'
SOURCE=FAMILY/'measurement-execution-activated-v2'
OWN=FAMILY/'measurement-composition-timing-admission-amendment-v1'
COLLECTOR=FAMILY/'measurement-stock-composition-candidate-v1'
SOURCE_SHA='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
OWN_SHA='78b3e5a0e3389f3d347a9b5700852361aae59cdbdc26813d9ff290f8ddf3e538'
COLLECTOR_SHA='257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da'
PAIR_SHA='f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e'
MAP_SHA='17b2461b9ae41b30678f0a4245aa59dd0151b3a2c3e44268be5d2d8199f8e553'
ARMS=['native-on','canonical-on','canonical-off','stock-on'];seen={}

def checked(path,digest=None,size=None):
 p=Path(path);a=p.lstat();assert stat.S_ISREG(a.st_mode)and not p.is_symlink(),str(p);h=hashlib.sha256()
 with p.open('rb')as src:
  for block in iter(lambda:src.read(1024*1024),b''):h.update(block)
 z=p.lstat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns),str(p)
 row={'path':str(p),'sha256':h.hexdigest(),'bytes':a.st_size};assert digest is None or row['sha256']==digest,str(p);assert size is None or row['bytes']==size,str(p)
 assert str(p)not in seen or seen[str(p)]==row;seen[str(p)]=row;return row['sha256']
def read(path,digest=None,size=None):
 digest=checked(path,digest,size);raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;return json.loads(raw)
def descriptor(d):return read(d['path'],d['sha256'],d['bytes'])
def exact(a,b,label):
 assert type(a)is type(b),label+' type'
 if isinstance(a,dict):
  assert set(a)==set(b),label+' keys'
  for k in a:exact(a[k],b[k],label+'/'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),label+' length'
  for i,(x,y)in enumerate(zip(a,b)):exact(x,y,label+'/'+str(i))
 else:assert a==b,label
def index(root,digest,count=None):
 d=read(root/'index.json',digest);assert d['schemaVersion']==1;assert count is None or len(d['files'])==count
 names=set()
 for row in d['files']:
  assert not Path(row['path']).is_absolute()and '..'not in Path(row['path']).parts and row['path']not in names;names.add(row['path']);checked(root/row['path'],row['sha256'],row['bytes'])
 return d
def all_descriptors(value):
 if isinstance(value,dict):
  if {'path','sha256','bytes'}<=set(value)and Path(value['path']).is_absolute():checked(value['path'],value['sha256'],value['bytes'])
  for x in value.values():all_descriptors(x)
 elif isinstance(value,list):
  for x in value:all_descriptors(x)
def component_tuple(r):return{k:r[k]for k in['arm','componentPath','componentSha256','componentBytes','enginePath','engineSha256','engineMetadataSha256','modulePath','bundleSha256','transpiledFiles','coreFiles']}
def proof_result(idx,row):
 d=index(Path(idx['path']).parent,idx['sha256']);checked(idx['path'],idx['sha256'],idx['bytes'])
 members=[r for r in d['files']if str(Path(idx['path']).parent/r['path'])==row['path']]
 assert members==[{'path':Path(row['path']).name,'sha256':row['sha256'],'bytes':row['bytes']}]
 return descriptor(row)

c=read(CANDIDATE,CANDIDATE_SHA,15105)
assert c['schemaVersion']==1 and c['state']=='UNREVIEWED_COMPOSED_COMMON_BYTE_MEASUREMENT_INPUTS_V2'
assert c['timingAllowed']is False and c['coordinatedWindow']=='NOT_ISSUED'
assert c['runtimeAcceptanceClaim']is c['performanceClaim']is False
assert c['sourceFamilyIndexSha256']==SOURCE_SHA and c['timingAdmissionSourceIndexSha256']==OWN_SHA and c['collectorSourceIndexSha256']==COLLECTOR_SHA and c['pairPinsSha256']==PAIR_SHA
index(SOURCE,SOURCE_SHA,35);index(OWN,OWN_SHA,22);index(COLLECTOR,COLLECTOR_SHA,20)
index(FAMILY/'independent-composition-timing-admission-source-review-v1','4e3175d50a215e079ec16b07abc6ca9f1adaa95cc8fb9fe23c5e75ab838ed8e0',7)
mapping=read(ADOPT/'timing-prerequisite-input-map-v1.UNREVIEWED.json',MAP_SHA)
all_descriptors(mapping)
assert set(c['components'])==set(ARMS)
for arm in ARMS:
 row=c['components'][arm];assert row['arm']==arm and row['emittedImports']==[]
 for k in['correctnessPassed','identityPassed','checkpointProbePassed']:assert row[k]is True
 assert isinstance(row['transpiledFiles'],list)and row['transpiledFiles']
 checked(row['componentPath'],row['componentSha256'],row['componentBytes']);checked(row['enginePath'],row['engineSha256']);checked(row['enginePath']+'.build.json',row['engineMetadataSha256'])
 for f in row['transpiledFiles']:checked(Path(row['modulePath']).parent/f['name'],f['sha256'],f['bytes'])
assert c['components']['native-on']['engineSha256']==c['components']['canonical-on']['engineSha256']==c['components']['stock-on']['engineSha256']
assert c['components']['canonical-on']['engineSha256']!=c['components']['canonical-off']['engineSha256']
assert c['components']['canonical-on']['bundleSha256']==c['components']['canonical-off']['bundleSha256']
literal=re.search(r'export const protocol=Object.freeze\((\{[^\n]+\})\);',(SOURCE/'protocol.mjs').read_text()).group(1)
protocol=json.loads(re.sub(r'([A-Za-z_$][\w$]*)\s*:',r'"\1":',literal));exact(c['protocol'],protocol,'complete protocol')
reviews={};reports={}
for name in['actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts']:
 row=c[name];assert row['reviewedPassed']is True
 reports[name]=read(row['reportPath'],row['reportSha256'])
 r=read(row['rootReviewPath'],row['rootReviewSha256']);reviews[name]=r
 assert r['schemaVersion']==1 and r['state']=='ROOT_REVIEWED_COMMON_BYTE_PREREQUISITE_V1'and r['prerequisite']==name
 assert r['reportPath']==row['reportPath']and r['reportSha256']==row['reportSha256']and r['pairPinsSha256']==PAIR_SHA and r['sourceContractVersion']=='sm-classic-trace-source-v1'
 assert r['reviewedPassed']is True and r['performanceClaim']is r['timingAllowedByThisPrerequisiteReview']is False
 assert r['prerequisiteInputMapSha256']==MAP_SHA and r['native342SourceManifestsComparedEqualAcrossFiveActualEngines']is True
 all_descriptors(r)
assert c['freshFull20And14']['workloadCases']==20 and c['freshFull20And14']['boundaryCases']==14
assert reports['freshFull20And14']['status']=='ACTUAL_CLASSIC_DIAGNOSTIC_20_WORKLOAD_14_BOUNDARY_CORRECTNESS_PASSED'
assert reports['freshFull20And14']['workloadCases']==20 and reports['freshFull20And14']['boundaryCases']==14 and reports['freshFull20And14']['engineSha256']==c['components']['native-on']['engineSha256']
assert reports['freshFull20And14']['interfaceAudit']['emittedImports']==[]
assert c['freshHttpBothHosts']['sameBytes']is True and c['freshHttpBothHosts']['requestsPerHost']==[3,3]and c['freshHttpBothHosts']['stopCodes']==[0,0]
assert c['freshHttpBothHosts']['standardInterfaces']=='6@0.2.10; clock duration type only'
assert reports['freshHttpBothHosts']['state']=='COMBINED_HTTP_BASELINE_AND_CLASSIC19_VALIDATED'
assert reports['freshReplay']['state']=='passed'and len(reports['freshReplay']['jobs'])==8
assert len(reviews['freshReplay']['explicitSupplementalFollowons'])==5
exact(reviews['freshReplay']['explicitSupplementalFollowons'],mapping['prerequisites']['freshReplay']['requiredAdditionalFollowonEvidence'],'five followons exact')
report=reports['actualCorrectness'];review=reviews['actualCorrectness']
assert report['state']=='COMPOSED_COMMON_BYTE_FOUR_ARM_CORRECTNESS_EVIDENCE'and report['collectorSourceIndexSha256']==COLLECTOR_SHA and report['pairPinsSha256']==PAIR_SHA
assert len(report['records'])==4 and [x['record']['arm']for x in report['records']]==ARMS
assert report['failedParent']['rawOuterExit']==1 and report['failedParent']['wholeParentGatePassed']is False and report['failedParent']['sourceFamilyIndexSha256']==SOURCE_SHA
for k in['timingAllowed','runtimeAcceptanceClaim','performanceClaim','queueEmptyProof','rootIsolationProof','cppStateMachineClaim','unaffectedThreeArmsRerun','controlsSubtracted']:assert report[k]is False
assert report['original28CounterexamplesPreserved']is True and report['commonCases']==8 and report['controlCases']==6
assert review['evidenceKind']==report['state']and review['sourceFamilyIndexSha256']==SOURCE_SHA and review['collectorSourceIndexSha256']==COLLECTOR_SHA and review['timingAdmissionSourceIndexSha256']==OWN_SHA
origins=[{'arm':x['record']['arm'],**x['origin']}for x in report['records']];exact(review['origins'],origins,'Root origins')
for entry in report['records']:
 r=entry['record'];row=c['components'][r['arm']]
 for key,value in row.items():exact(value,r[key],'compact component '+r['arm']+'/'+key)
 assert entry['origin']['guestSourceFamilyIndexSha256']==SOURCE_SHA
proof=review['compositionProof'];assert proof['rawOuterExit']==0
composition_proof=proof_result(proof['independentProofIndex'],proof['independentProofResult'])
stock_proof=proof_result(proof['stockIndependentProofIndex'],proof['stockIndependentProofResult'])
assert composition_proof['schemaVersion']==1 and composition_proof['state']=='INDEPENDENT_COMPOSED_COMMON_BYTE_CORRECTNESS_VERIFIED_V1'
assert composition_proof['compositionReportSha256']==c['actualCorrectness']['reportSha256']and composition_proof['rawCompositionOuterExit']==0
assert stock_proof['schemaVersion']==1 and stock_proof['state']=='INDEPENDENT_COMMON_BYTE_STOCK_ONLY_CORRECTNESS_VERIFIED_V1'and stock_proof['rawStockOuterExit']==0
for p in[composition_proof,stock_proof]:
 assert p['guestSourceFamilyIndexSha256']==SOURCE_SHA and p['collectorSourceIndexSha256']==COLLECTOR_SHA and p['pairPinsSha256']==PAIR_SHA
 assert p['verifiedPassed']is True and p['timingAllowed']is p['performanceClaim']is False
exact(composition_proof['origins'],origins,'independent origins');exact(composition_proof['componentTuples'],[component_tuple(x['record'])for x in report['records']],'four tuples')
stock=report['records'][3];exact(stock_proof['componentTuple'],component_tuple(stock['record']),'stock tuple')
assert stock_proof['stockReportSha256']==stock['origin']['recordSha256']and stock_proof['stockRootReceiptSha256']==report['newStockRootReceipt']['sha256']
complete=descriptor(proof['completion']);assert complete['state']=='COMPOSITION_REPORT_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED'and complete['collectorSourceIndexSha256']==COLLECTOR_SHA and complete['requiresIndependentRawOuterExitZero']is True
assert complete['oldParentRawExit']==1 and complete['timingAllowed']is complete['runtimeAcceptanceClaim']is False
exact(complete['result'],{'path':c['actualCorrectness']['reportPath'],'sha256':c['actualCorrectness']['reportSha256'],'bytes':Path(c['actualCorrectness']['reportPath']).stat().st_size},'completion pointer')
terminal=descriptor(proof['terminal']);assert terminal['returncode']==0
checked(terminal['command'][0],'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
assert Path(terminal['command'][0]).resolve()==Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node').resolve()
exact(terminal['command'][1:],[str(COLLECTOR/'compose.mjs'),COLLECTOR_SHA,report['threeArmAuthority']['path'],report['threeArmAuthority']['sha256'],report['newStockRootReceipt']['path'],report['newStockRootReceipt']['sha256'],str(Path(c['actualCorrectness']['reportPath']).parent)],'actual compose command')
failure=read(report['failedParent']['receiptPath'],report['failedParent']['receiptSha256']);assert failure['rawOuterExit']==1 and failure['wholeFourArmGatePassed']is False
three=read(report['threeArmAuthority']['path'],report['threeArmAuthority']['sha256']);assert three['failedParentRawOuterExit']==1 and three['wholeFailedParentPassed']is False and three['pairPinsSha256']==PAIR_SHA
stock_root=read(report['newStockRootReceipt']['path'],report['newStockRootReceipt']['sha256']);assert stock_root['rawOuterExit']==0 and stock_root['collectorSourceIndexSha256']==COLLECTOR_SHA and stock_root['pairPinsSha256']==PAIR_SHA
assert stock_root['result']['path']==stock['origin']['recordPath']and stock_root['result']['sha256']==stock['origin']['recordSha256']
for i,entry in enumerate(report['records']):
 origin=entry['origin'];data=read(origin['recordPath'],origin['recordSha256'],origin.get('recordBytes'))
 exact(data['records'][0]if i==3 else data,entry['record'],'original record exact')
 if i<3:assert origin['originalParentRawOuterExit']==1 and origin['wholeOriginalParentGatePassed']is False
 else:assert origin['rawOuterExit']==0 and origin['collectorSourceIndexSha256']==COLLECTOR_SHA
native={}
for key,row in mapping['actualEngineTuples'].items():
 m=descriptor(row['metadata']);native[key]={x['path']:x['sha256']for x in m['sourceManifest']};assert len(native[key])==342
assert all(value==native['diagnostic-on']for value in native.values())
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'INDEPENDENT_UNREVIEWED_COMPOSED_TIMING_INPUTS_DATA_REVIEW_PASSED_NO_TIMING_AUTHORIZATION','candidate':{'path':str(CANDIDATE),'sha256':CANDIDATE_SHA,'bytes':15105},'pathsRehashed':len(seen),'rootPrerequisiteReviews':{key:{'path':c[key]['rootReviewPath'],'sha256':c[key]['rootReviewSha256']}for key in reviews},'allNonAuthorityPhaseMeasureAdmissionDataPredicatesPassed':True,'fourCompactRecordsEveryFieldEqualsActualCompositionRecord':True,'elevenFieldTuplesIdentitiesProbesOperationalCostFieldsPreserved':True,'actualProofSchemasIndexMembershipSourcesOriginsRawZeroBound':True,'twentyAndFourteenRawReportSchemaAndDiagnosticEngineMatch':True,'eightStageAndFiveSupplementalFollowonReportsBound':True,'allFiveActual342SourceManifestsEqual':True,'httpSameByteThreeRequestsEachStopZeroSixInterfacesTypeOnlyClockBound':True,'protocolByteDataEquivalentToSealedParentLiteral':True,'missingOrIncorrectDataKeys':[],'expectedClosedIssuedAuthorityGates':[{'field':'state','actual':c['state'],'requiredByIssuedPhase':'ROOT_REVIEWED_COMPOSED_COMMON_BYTE_MEASUREMENT_INPUTS_V2'},{'field':'timingAllowed','actual':False,'requiredByIssuedPhase':True},{'field':'coordinatedWindow','actual':'NOT_ISSUED','requiredByIssuedPhase':'ROOT_EXPLICIT_SINGLE_MEASUREMENT_WINDOW'}],'candidateUnmodified':True,'rootAuthorityOrPhaseCreated':False,'timingAllowed':False,'measurementsExecuted':False,'remainingConditions':['New final Root-issued phase after separate quiet-window decision and fresh integrity checks.','Existing78b3 directly hashes one freshReplay raw report; five followons are explicitly Root-reviewed here, not separately auto-hashed at every measurement boundary.','Keep original failed parent raw1 and provider/GC/getter/Symbol/no-reuse limits; no new compatibility/performance or memory claim.'],'readerScope':'Python data/hash/source-literal comparisons only, no owner admission/phase/measure imports or helpers, Node/preflight/guest/native/host/timing actions.'}
with(HERE/'results.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n')
with(HERE/'verified-paths.json').open('x')as out:json.dump(list(seen.values()),out,indent=2);out.write('\n')
print(json.dumps({'state':result['state'],'paths':len(seen),'incorrectDataKeys':0,'closedAuthorityGates':3}))
