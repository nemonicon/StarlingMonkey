"""Finite actual compact-plan read/hash/data review. Never imports owner code."""
from pathlib import Path
import hashlib,json,base64,os,stat
P=Path(__file__).resolve().parent;Z=P.parent;S=Z/'cost-pilot-timing-candidate-v3';OUT=Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v3')
SOURCE='c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9'
checks=0;seen={};physical={};proofs={}
def need(ok,msg):
 global checks
 if not ok:raise AssertionError(msg)
 checks+=1
def identity(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=size)
def verify(r,role):
 p=Path(r['path']);need(p.is_absolute() and p.is_file() and not p.is_symlink(),'ordinary absolute input '+str(p))
 real=str(p.resolve());a=p.stat()
 if real not in physical:
  got=row(p);b=p.stat();need(identity(a)==identity(b),'stable full streamed bytes');physical[real]=dict(sha256=got['sha256'],bytes=got['bytes'],identity=identity(b))
 else:need(identity(a)==physical[real]['identity'],'stable repeated input')
 got=physical[real];need(got['sha256']==r['sha256'] and got['bytes']==r['bytes'],'exact bytes '+str(p))
 if str(p)not in seen:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']=set()
 seen[str(p)]['roles'].add(role);return r
def data(r,role='JSON'):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def descriptors(v):
 result=[]
 def visit(x):
  if isinstance(x,dict):
   if isinstance(x.get('path'),str) and Path(x['path']).is_absolute() and isinstance(x.get('sha256'),str) and type(x.get('bytes'))is int:result.append({k:x[k]for k in ['path','sha256','bytes']})
   for y in x.values():visit(y)
  elif isinstance(x,list):
   for y in x:visit(y)
 visit(v);return result
def local(n):need(isinstance(n,str) and n and not n.startswith('/') and '\\'not in n and all(x not in ['', '.', '..']for x in n.split('/')),'safe local member');return n
def indexed(r,count=None):
 x=data(r,'index');need(x['schemaVersion']==1 and isinstance(x['files'],list),'finite schema1 index')
 if count is not None:need(len(x['files'])==count,'exact indexed count '+str(count))
 rows=[];names=set()
 for v in x['files']:
  n=local(v['path']);need(n not in names,'unique member');names.add(n);a=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(a,'indexed-member');rows.append(a)
 return x,rows
def ledger(r,role):
 x=data(r,role);rs=x['files']if isinstance(x,dict)else x
 need(isinstance(rs,list),'finite retained input ledger')
 for v in rs:verify(v,role+'-input')
 return len(rs)
def membership(root,names):
 actual=set()
 for p in root.rglob('*'):
  need(not p.is_symlink(),'no symlink evidence member')
  if p.is_file():actual.add(str(p.relative_to(root)))
 need(actual==set(names),'whole exact physical membership '+str(root))
def contracted(p,state):
 ix,rs=indexed(p['index']);v=data(p['result'],'actual-sealed-proof-result');c=data(p['contract'],'actual-stable-proof-contract')
 need(sum(r==p['result']for r in rs)==sum(r==p['contract']for r in rs)==1,'result/contract uniquely indexed')
 need(v['verifiedPassed'] is True and v['state']==state==c['requiredReviewState'],'actual proof state')
 for k,w in c.get('requiredFixedValues',{}).items():need(v[k]==w,'whole fixed proof field '+k)
 for k,w in c.get('requiredCoverage',{}).items():need(v['coverage'][k]==w,'whole proof coverage '+k)
 bound=descriptors(v)+rs
 for k,r in c['requiredExactDescriptors'].items():need(r in bound,'exact contract descriptor bound '+k);verify(r,'contract-'+k)
 components=v.get('components',v.get('requiredComponents'));need(components==c['requiredComponents'],'exact three actual components')
 for r in descriptors(v)+descriptors(c):verify(r,'complete-contracted-proof-descriptor')
 # Actual output membership/bytes were also consumed by the real parent guards.
 if v.get('actualIndex'):
  actual,ars=indexed(v['actualIndex']);membership(Path(v['actualIndex']['path']).parent,[r['path']for r in actual['files']]+['index.json','completion.json'])
 for r in rs:
  if r['path'].endswith(('rehashed-inputs.json','bindings-rehashed-inputs.json','peer-bytes-inputs.json','peer-raw-inputs.json')):ledger(r,'retained-complete-proof-inputs')
 return v,c,rs
rootrow=dict(path=str(Z/'cost-measurement-plan-v3-root-results.json'),sha256='b58486734f95f62bebfe589369706dad544b6ef2be65f152ef25fc1623ed3ec5',bytes=4172)
root=data(rootrow,'Root-result')
for r in descriptors(root):verify(r,'Root-bound-input')
need(root['sourceIndex']['sha256']==SOURCE and root['rawParentExitCode']==0 and root['parentPid']==25616 and root['rootSession']==76299,'exact actual source/Root terminal tuple')
ix,source_rows=indexed(root['sourceIndex'],50);membership(S,[r['path']for r in ix['files']]+['index.json'])
source_by={Path(r['path']).name:r for r in source_rows};refs=data(source_by['references.json'],'source-references');inherited=data(source_by['inherited-source.json'],'immutable-source-ancestry')
for name,count in [('heldV1Index',85),('heldV2Index',26)]:
 old,rs=indexed(inherited[name],count);membership(Path(inherited[name]['path']).parent,[r['path']for r in old['files']]+['index.json'])
for r in descriptors(inherited):verify(r,'source-ancestry')
ledger(source_by['source-inputs.json'],'full918-source-preparation-closure')
need(len(data(source_by['runtime-dependencies.json'])['files'])==28 and len(data(source_by['worker-dependencies.json'])['files'])==20,'exact parent/worker import source closures')
for n in ['runtime-dependencies.json','worker-dependencies.json']:
 for r in data(source_by[n])['files']:verify(r,'actual-source-module-dependency')
peer_ix,peer_rows=indexed(root['sourceReview']['index'],11);peer=data(root['sourceReview']['result'],'source-peer')
need(peer['state']=='INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1' and peer['sourceIndexSha256']==SOURCE and peer['sourceOnly'] is True and peer['ownerActionsInvoked'] is False,'exact source-only peer')
ledger(next(r for r in peer_rows if r['path'].endswith('/verified-inputs.json')),'source-peer-complete-inputs')
auth=data(root['rootAuthority'],'read-only-Root-authority');options=data(root['rootOptions'],'exact-options');terminal=data(root['externalTerminal'],'external-raw-terminal');started=data(root['started'],'external-started')
need(auth['state']=='ROOT_AUTHORIZED_READ_ONLY_CODEC_MEASUREMENT_PLAN_DATA_V1' and auth['dataPublicationAllowed'] is True and auth['codecGuestPilotOrTimingAllowed'] is False and auth['outputRoot']==str(OUT) and auth['sourceIndexSha256']==SOURCE,'only read-only plan authority')
need(auth['sourceIndependentReview']==root['sourceReview']==options['sourceIndependentReview'] and options['sourceIndex']==root['sourceIndex'] and options['planAuthority']==root['rootAuthority'],'whole source/peer/authority/options identity')
need(terminal['pid']==25616 and terminal['rawExitCode']==0 and terminal['timeout'] is False and terminal['parentOwnedGroupGone'] is True and terminal['deadlineSeconds']==900,'external raw0/gone/not timed out')
need(terminal['argv']==started['argv'] and terminal['argv'][1]==root['rootInvocation']['path'] and terminal['argv'][2]==root['rootOptions']['sha256'] and terminal['authority']==root['rootAuthority'] and terminal['options']==root['rootOptions'],'actual exact invoked read-only entry/options')
for name in ['stdout','stderr']:verify(terminal[name],'whole-external-stream')
need(terminal['stderr']['bytes']==0 and terminal['readOnlyProofAndCompactDataOnly'] is True and terminal['generatedGuestCodecWorkerPilotTimingOrSourcePromotionAllowed'] is False,'actual raw streams/action scope')
plan=data(root['preparedPlan'],'actual-compact-plan');oix,ors=indexed(root['index'],1);membership(OUT,['prepared-plan.json','index.json','completion.json'])
need(stat.S_IMODE(OUT.stat().st_mode)==0o700 and all(stat.S_IMODE(q.stat().st_mode)==0o600 and q.stat().st_nlink==1 for q in OUT.iterdir()),'actual private singleton publication files')
complete=data(root['completion'],'actual-completion')
for name,k in [('preparedPlan','result'),('index','index')]:need(complete[k]==dict(root[name],path=Path(root[name]['path']).name),'completion binds '+name)
need(complete['rootAuthority']==root['rootAuthority'] and complete['state']=='READ_ONLY_COMPACT_PLAN_DATA_COMPLETE_NOT_ACTION_AUTHORITY','completion no action grant')
stdout=json.loads(Path(terminal['stdout']['path']).read_bytes());need(stdout==dict(result=complete['result'],index=complete['index'],completion=dict(root['completion'],path='completion.json')),'whole raw publication stdout')
correct,cc,crs=contracted(refs['fullCorrectness'],'INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_V3_RESULTS_REVIEW_PASSED_V1')
transport,tc,trs=contracted(refs['stockWasmtimeStrings'],'INDEPENDENT_ZLIB_COST_STOCK_WASMTIME42_STRING_TRANSPORT_RESULTS_VERIFIED_V1')
controls,xc,xrs=contracted(refs['actualControlsProof'],'INDEPENDENT_ZLIB_COST_JCO_CONTROL_V2_RESULTS_REVIEW_PASSED_V1')
need(correct['controlOperations']==0 and correct['actualBatchControlProofPending'] is True and transport['actualBatchControlProofPending'] is True,'historical control0/pending proof values untouched')
need(controls['controlOperations']==540 and controls['codecCalls']==0 and controls['pilotPrerequisitesSatisfied'] is False,'separate actual540 control proof still no phase authority')
need(correct['components']==transport['components']==controls['requiredComponents'],'all proof artifacts same actual tuples')
# Full source/native/tool/artifact closure is inherited from the exact independent artifact proof.
aix,ars=indexed(refs['actualComponentReviewIndex'],26);aggregate=data(next(r for r in ars if r['path'].endswith('/results.json') and Path(r['path']).parent==Path(refs['actualComponentReviewIndex']['path']).parent),'actual-all-arm-artifact-proof')
for r in ars:
 if r['path'].endswith('/rehashed-inputs.json') or r['path'].endswith('/rehashed-common-inputs.json'):ledger(r,'complete-source-native-tool-component-closure')
artifacts={}
for arm in ['native-on','fflate-on','fflate-off']:
 ar=aggregate['actualComponentReviews'][arm];per=data(ar['result'],'actual-per-arm-artifact-proof')
 need(per['verifiedPassed'] is True and per['arm']==arm and per['component']==correct['components'][arm] and per['ordinaryGuestExportsInvoked'] is False,'actual component relation '+arm)
 artifacts[arm]=dict(parentAuditedActualComponent=True,**{k:per[k]for k in ['component','glue','core','dts','wit','transpileMetadata','packageJson']})
 for r in descriptors(per):verify(r,'actual-artifact-native-package-context')
need(plan['artifacts']==artifacts,'entire exact three actual artifact tuples')
need(plan['schemaVersion']==1 and plan['state']=='PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1' and plan['sourceIndexSha256']==SOURCE and plan['calibrationDecisionSha256']==refs['calibrationDecision']['sha256'] and plan['operationalAdmission'] is False and plan['actionAuthority'] is False,'compact plan identity/source-only calibration/no action')
# Decode actual retained streams as DATA only. No compression/decompression API.
cases=data(refs['cases'],'actual30-cases');facts=data(refs['controlInputFacts'],'independent30-input-facts');raw=data(refs['rawFixtures'],'fixture-definitions');catalog=data(refs['reviewedEncoderStreams'],'reviewed60-encoder-catalog')
actual=data(cc['requiredExactDescriptors']['actualEncoderStreams'],'whole-actual60-encoded-streams');oracle=data(cc['requiredExactDescriptors']['oracle'],'whole-actual-Node-oracle')
def fnv(bs):
 h=2166136261
 for value in bs:h=((h^value)*16777619)&0xffffffff
 return h
def fingerprint(bs):return dict(bytes=len(bs),sha256=hashlib.sha256(bs).hexdigest(),fnv1aU32=fnv(bs))
raw_bytes={};raw_rows={v['id']:v for v in raw['fixtures']}
for k,r in raw_rows.items():
 if r['pattern']=='empty':bs=b''
 elif r['pattern']=='repeat-abc123':bs=(b'abc123'*((r['bytes']+5)//6))[:r['bytes']]
 else:
  need(r['pattern']=='xorshift32-low-byte','exact PRNG fixture');x=r['seed'];out=bytearray()
  for _ in range(r['bytes']):
   x^=(x<<13)&0xffffffff;x^=x>>17;x^=(x<<5)&0xffffffff;x&=0xffffffff;out.append(x&255)
  bs=bytes(out)
 f=fingerprint(bs);need(f==dict(bytes=r['bytes'],sha256=r['rawSha256'],fnv1aU32=r['rawFNV1aU32']),'independent whole raw fixture '+k)
 nr=next(v for v in oracle['rawFixtures'] if v['id']==k);need(base64.b64decode(nr['base64'],validate=True)==bs and {q:nr[q]for q in ['bytes','sha256','fnv1aU32']}==f,'actual Node raw fixture whole bytes '+k);raw_bytes[k]=bs
all_streams=actual['primary']+actual['off'];need(len(all_streams)==len(catalog['streams'])==60,'all60 actual whole streams')
streams={};stream_ledger=[]
for r in all_streams:
 bs=base64.b64decode(r['encodedBase64'],validate=True);f=fingerprint(bs);need(f==dict(bytes=r['encodedBytes'],sha256=r['encodedSha256'],fnv1aU32=r['encodedFNV1aU32']),'whole actual encoded bytes '+r['streamId'])
 key=(r['provider'],r['fixture'],r['format']);need(key not in streams,'one actual provider stream per fixture/format');streams[key]=(r,bs)
 reviewed=next(v for v in catalog['streams'] if v['streamId']==r['streamId']);need(all(reviewed[k]==r[k]for k in ['provider','fixture','format','caseId','encodedBytes','encodedFNV1aU32','encodedSha256']),'catalog values match actual full retained stream '+r['streamId'])
 if r['provider']=='node-22.14.0':
  n=next(v for v in oracle['encodedStreams'] if v['fixture']==r['fixture'] and v['format']==r['format']);need(base64.b64decode(n['encodedBase64'],validate=True)==bs,'actual Node oracle full encoder stream')
 stream_ledger.append(dict(streamId=r['streamId'],provider=r['provider'],fixture=r['fixture'],format=r['format'],**f))
need(len(cases)==len(facts)==30 and len(plan['expected'])==90,'full finite30 cases and90 rows')
expected=[];case_ledger=[]
for arm in ['native-on','fflate-on','fflate-off']:
 for i,c in enumerate(cases):
  f=facts[i];bs=raw_bytes[c['fixture']];enc,encoded=streams[(arm,c['fixture'],c['format'])];node,nodebytes=streams[('node-22.14.0',c['fixture'],c['format'])]
  need(c['index']==f['index']==i and c['id']==f['caseName'] and f['fixture']==c['fixture'] and f['direction']==c['direction'] and f['format']==c['format'],'ordered primary/input identity')
  inp=bs if c['direction']=='encode'else nodebytes;out=encoded if c['direction']=='encode'else bs;ff=fingerprint(inp)
  need(f['inputBytes']==len(inp) and f['inputFNV1aU32']==ff['fnv1aU32'] and f['inputSha256']==ff['sha256'] and f['logicalUncompressedBytes']==len(bs)==c['logicalUncompressedBytesPerOperation'],'whole input and logical units')
  need(f['inputSource']==('raw-fixture'if c['direction']=='encode'else'node-oracle-input') and f['parentDeclaredInputSha256']==(None if c['direction']=='encode'else hashlib.sha256(inp).hexdigest()),'source/declared digest exact')
  cap=32768 if i<18 else 128;need(c['timingNMax']==cap,'declared small/large cap only')
  v=dict(schemaVersion=1,caseId=i,caseName=c['id'],arm=arm,direction=c['direction'],logicalBytes=len(bs),inputBytes=len(inp),inputFNV=fnv(inp),outputBytes=len(out),outputFNV=fnv(out),oracleSha256=correct['oracleSha256'],inputSource=f['inputSource'],parentDeclaredInputSha256=f['parentDeclaredInputSha256'],timingNMax=cap)
  expected.append(v);case_ledger.append(dict(planRow=len(expected)-1,expected=v,inputSha256=hashlib.sha256(inp).hexdigest(),outputSha256=hashlib.sha256(out).hexdigest(),outputStreamId=enc['streamId']if c['direction']=='encode'else None,inputStreamId=node['streamId']if c['direction']=='decode'else None,caseCitation=dict(path=refs['cases']['path'],index=i),inputCitation=dict(path=refs['controlInputFacts']['path'],index=i)))
need(plan['expected']==expected,'entire90-row compact plan independently reconstructed, no normalization')
for real,r in physical.items():need(identity(Path(real).stat())==r['identity'],'final stable full closure')
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
save('per-row-ledger.json',dict(schemaVersion=1,rows=case_ledger,encodedStreams=stream_ledger,codecInvoked=False))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],uniquePhysicalFilesHashed=len(physical),ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,dataReviewPassed=True,rootResult=rootrow,sourceIndex=root['sourceIndex'],sourceReview=root['sourceReview'],rootAuthority=root['rootAuthority'],preparedPlan=root['preparedPlan'],actualIndex=root['index'],actualCompletion=root['completion'],externalTerminal=root['externalTerminal'],artifacts=artifacts,arms=3,expectedRows=90,allFiveRawFixturesWholeBytesRecomputed=True,all60ActualEncodedStreamsWholeBytesRehashedAndFnvRecomputed=True,all15NodeEncodedStreamsWholeBytesMatched=True,all90ExpectedRowsExactlyReconstructed=True,actualIndexedFiles=1,actualRegularFiles=3,externalParentExitCode=0,parentOwnedGroupGone=True,historicalCorrectnessControlOperations=correct['controlOperations'],historicalCorrectnessPendingControl=correct['actualBatchControlProofPending'],historicalTransportPendingControl=transport['actualBatchControlProofPending'],separateActualControlOperations=controls['controlOperations'],separateActualControlCodecCalls=controls['codecCalls'],separateActualControlPilotPrerequisitesSatisfied=controls['pilotPrerequisitesSatisfied'],fullCorrectness=refs['fullCorrectness'],stockWasmtimeStrings=refs['stockWasmtimeStrings'],actualControlsProof=refs['actualControlsProof'],calibrationDecision=refs['calibrationDecision'],uniqueDeclaredInputsVerified=len(seen),uniquePhysicalFilesHashed=len(physical),checks=checks,reviewerOwnerHelpersPreflightNodeGuestCodecNativePilotOrTimingActionsInvoked=False,actionAuthority=False))
print(json.dumps(dict(dataReviewPassed=True,rows=90,arms=3,actualFiles=3,uniquePaths=len(seen),physical=len(physical),checks=checks)))
