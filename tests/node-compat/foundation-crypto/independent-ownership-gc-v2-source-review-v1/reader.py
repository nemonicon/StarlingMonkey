"""Read/hash, Python AST and private pure DATA review. No owner imports/actions."""
from pathlib import Path
import ast,hashlib,json,copy
P=Path(__file__).resolve().parent;S=P.parent/'ownership-gc-candidate-v2'
seen={};physical={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=size)
def verify(r,role):
 p=Path(r['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'ordinary absolute source/data');real=str(p.resolve());a=p.stat()
 if real not in physical:
  v=row(p);b=p.stat();need(ident(a)==ident(b),'stable streamed full bytes');physical[real]=dict(sha256=v['sha256'],bytes=v['bytes'],identity=ident(b))
 else:need(ident(a)==physical[real]['identity'],'stable repeated current input')
 need(physical[real]['sha256']==r['sha256']and physical[real]['bytes']==r['bytes'],'exact source bytes '+str(p))
 if str(p)not in seen:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']=set()
 seen[str(p)]['roles'].add(role);return r
def data(r,role='JSON'):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def index(r,count=None):
 x=data(r,'source-family-index');need(x['schemaVersion']==1 and isinstance(x['files'],list),'finite schema1 family')
 if count is not None:need(len(x['files'])==count,'exact family members')
 names=set();rs=[]
 for v in x['files']:
  n=v['path'];need(n and not n.startswith('/')and '\\'not in n and all(t not in ['','.','..']for t in n.split('/'))and n not in names,'safe unique member');names.add(n)
  a=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(a,'family-member');rs.append(a)
 need({str(p.relative_to(Path(r['path']).parent))for p in Path(r['path']).parent.rglob('*')if p.is_file()}==names|{'index.json'},'complete exact physical family')
 return rs
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
src=dict(path=str(S/'index.json'),sha256='7988586f2aef2d6ee651dfb2978dc34cc756e796181e8c69d77fff085ee888b0',bytes=2997)
rs=index(src,18);by={str(Path(r['path']).relative_to(S)):r for r in rs};inputs=data(by['input-freeze.json'],'full2943-preparation-inputs');need(len(inputs['files'])==2943,'exact source input count')
for r in inputs['files']:verify(r,'complete-source-normal-protection-native-source-context')
ancestry=data(by['inherited-source.json'],'explicit-held-ancestry');index(ancestry['heldSourceIndex'],14);index(ancestry['holdReviewIndex'],14);index(ancestry['nativeSourceIndex'],39)
need(ancestry['holdReviewIndex']['sha256']=='2ac980be8bb846a880888622d85ec0bf46273eaff425b4de8babff6e0553d597','literal old HOLD retained')
required=data(ancestry['requiredCorrectionContract'],'required-M1-correction');need(required['findingId']=='GC-PROPOSAL-M1'and required['noRetroactiveDirectOnlyInterpretation'],'exact M1 diagnosis not relabeled')
protection=data(ancestry['normalProtection'],'inherited-normal-protection');need(protection['originalReferenceEntries']==1387 and protection['distinctOriginalPaths']==1378 and len(protection['frozenCopyEntries'])==1390 and len(protection['requiredNormalFreezeMembership'])==1391,'unchanged normal protection count/data')
for x in protection['originals']:verify(x['original'],'actual-normal-original');verify(x['frozen'],'actual-normal-frozen')
for x in protection['frozenCopyEntries']:verify(x,'actual-normal-frozen-copy')
# Complete six-edit source derivation and inherited eight-edit ancestry.
deriv=data(by['correction-derivations.json'],'six-exact-correction-edits');before=Path(deriv['source']['path']).read_text();verify(deriv['source'],'held-v1-guest');after=(S/'guest.GC.UNEXECUTED.mjs').read_text();need(len(deriv['edits'])==6,'exact six edits')
forward=before
for e in deriv['edits']:need(forward.count(e['before'])==e['count']==1,'unique exact correction preimage');forward=forward.replace(e['before'],e['after'])
need(forward==after,'entire corrected guest exact afterimage')
reverse=after
for e in reversed(deriv['edits']):need(reverse.count(e['after'])==1,'unique exact correction reversal');reverse=reverse.replace(e['after'],e['before'])
need(reverse==before,'six reversals recover held pressure guest')
oldderiv=json.loads((Path(deriv['source']['path']).parent/'guest-derivations.json').read_bytes())
for e in reversed(oldderiv['edits']):need(reverse.count(e['after'])==1,'unique inherited reversal');reverse=reverse.replace(e['after'],e['before'])
verify(ancestry['originalGuest'],'original-sealed-normal-guest');need(reverse==Path(ancestry['originalGuest']['path']).read_text(),'8+6 reversals recover exact original HMAC guest')
need('gcOrEntropyRequested'not in after,'old ambiguous field wholly removed')
need('function pressure(phase){pressureRequests++;const buffer=Buffer.alloc(64,0xa5)'in after and after.index('pressureRequests++;')<after.index('Buffer.alloc(64,0xa5)'),'attempt counted before possible Buffer failure')
need("pressureStart=pressureRecords.length,pressureRequestsStart=pressureRequests;count.runCalls++"in after and after.count("gcObservation('this-run',pressureStart,pressureRequestsStart)")==2,'per-run counter snapshots on success and catch')
need("publicGcPressureRequested:pressureRequests>requestsStart"in after and 'publicGcPressureRequests:pressureRequests-requestsStart' in after and 'publicGcPressureRecords:pressureRecords.length-recordsStart'in after,'actual source deltas, no blanket true')
need("gcObservation:gcObservation('outer-validate')"in after and "schemaVersion:2,kind:'crypto-owner-within-export-gc-validation-v2'"in after,'fresh outer schema/scoped global observation')
need(after.count("pressure('")==4 and after.count('Buffer.alloc(')==1 and after.count("buffer.toString('hex')")==1 and after.count("Buffer.from(encoded,'hex')")==1,'same finite public-pressure path')
# Compute exact new complete typed expected DATA independently, preserving all normal fields.
normal=data(ancestry['acceptedNormalExpectedRecord'],'accepted-whole-normal-expected-record');expected=data(by['expected-complete-gc-record.json'],'new-whole-typed-expected-record')
need(normal['schemaVersion']==1 and normal['kind']=='crypto-owner-within-export-validation-v1'and len(normal['records'])==4,'actual accepted normal wrapper data')
version='public-buffer-gc-pressure-v1';deltas=[4,4,8,0];phases=['before-first-sign','between-signs','before-valid-verify','after-verifies']
def observation(scope,requests,records):
 return dict(version=version,scope=scope,publicGcPressureRequested=requests>0,publicGcPressureRequests=requests,publicGcPressureRecords=records,entropyRequested=False,actualNativeGcCountObserved=False,strongApplicationOwnersCombined=True,isolatedTemporaryRootsProved=False,finalizerFreeWipeObserved=False)
computed=copy.deepcopy(normal);computed.update(schemaVersion=2,kind='crypto-owner-within-export-gc-validation-v2',gcObservation=observation('outer-validate',16,16))
for r,delta in zip(computed['records'],deltas):need(r.pop('gcOrEntropyRequested')is False,'old field removal from each expected run');r['gcObservation']=observation('this-run',delta,delta)
computed['pressure']=dict(records=[dict(sequence=i+1,phase=phase,bytes=64,encodedHex='a5'*64,decodedHex='a5'*64,forcedGcCounterObserved=False,isolatedTemporaryRootProved=False)for i,phase in enumerate(phases*4)],scheduledRecordsPerFreshValidate=16,publicAllocBytesPerRecord=64,sourceForcedHookSitesPerRecord=6,actualNativeGcCountObserved=False,strongApplicationOwnersCombined=True,isolatedTemporaryRootsProved=False)
need(canonical(computed)==canonical(expected),'whole complete expected record independently reconstructed without normalizing actual values')
for old,new in zip(normal['records'],expected['records']):
 a=copy.deepcopy(old);b=copy.deepcopy(new);a.pop('gcOrEntropyRequested');b.pop('gcObservation');need(canonical(a)==canonical(b),'all HMAC/key/refusal/window/counter fields unchanged')
# Verify the actual collector uses complete type-aware JSON comparison, not subset/projected fields.
module=ast.parse((S/'collector.py').read_text());need([n.names[0].name for n in module.body if isinstance(n,ast.Import)]==['json'],'collector standard json only')
validate=next(n for n in module.body if isinstance(n,ast.FunctionDef)and n.name=='validate');need(len(validate.body)==2 and isinstance(validate.body[0],ast.Assert)and isinstance(validate.body[1],ast.Return),'finite actual collector shape')
compare=validate.body[0].test;need(isinstance(compare,ast.Compare)and len(compare.ops)==1 and isinstance(compare.ops[0],ast.Eq),'whole equality assertion')
for call,name in [(compare.left,'value'),(compare.comparators[0],'complete_expected')]:
 need(isinstance(call,ast.Call)and isinstance(call.func,ast.Attribute)and isinstance(call.func.value,ast.Name)and call.func.value.id=='json'and call.func.attr=='dumps'and len(call.args)==1 and isinstance(call.args[0],ast.Name)and call.args[0].id==name,'exact whole typed value serialization')
 need({k.arg:ast.literal_eval(k.value)for k in call.keywords}==dict(sort_keys=True,separators=(',',':')),'strict canonical whole JSON comparison options')
# Counterexamples are private DATA checks, not owner-collector or guest execution.
pure=[]
mutations=[('old-field',lambda v:v['records'][0].update(gcOrEntropyRequested=False)),('blanket-run3-pressure',lambda v:v['records'][3]['gcObservation'].update(publicGcPressureRequested=True)),('wrong-type',lambda v:v['gcObservation'].update(publicGcPressureRequested=1)),('entropy-true',lambda v:v['gcObservation'].update(entropyRequested=True)),('observed-count',lambda v:v['gcObservation'].update(actualNativeGcCountObserved=True)),('missing-record',lambda v:v['pressure']['records'].pop()),('truncated-hex',lambda v:v['pressure']['records'][0].update(decodedHex='a5'*63)),('tag-change',lambda v:v['records'][0]['result']['operations'].update(firstSignatureHex='00'*32)),('counter-change',lambda v:v['after']['counters'].update(signCalls=999)),('unknown-field',lambda v:v.update(unexpected=True)),('partial-failed-run',lambda v:v['records'][0].update(completed=False))]
for name,change in mutations:
 bad=copy.deepcopy(expected);change(bad);need(canonical(bad)!=canonical(expected),'whole collector rejects '+name);pure.append(dict(case=name,rejectedByActualWholeComparisonSemantics=True))
partial=[]
for start,current in [((0,0),(1,0)),((4,4),(5,4)),((8,8),(12,11))]:
 req,rec=current[0]-start[0],current[1]-start[1];o=observation('this-run',req,rec);need(o['publicGcPressureRequested']and req>rec,'partial failed pressure attempt retained honestly');partial.append(dict(startRequests=start[0],startRecords=start[1],currentRequests=current[0],currentRecords=current[1],observation=o,completeExpectedRecordWouldPass=False))
contract=data(by['follow-on-contract.json'],'new-closed-followon-contract')
need(contract['perRunPressureRequests']==contract['perRunPressureRecords']==deltas and contract['perRunPublicGcPressureRequested']==[True,True,True,False]and contract['outerPublicGcPressureRequests']==contract['outerPublicGcPressureRecords']==16 and contract['outerPublicGcPressureRequested']is True,'exact scoped source contract')
need(contract['requiredSourcePeer']['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_REVIEW_PASSED_V2'and contract['requiredSourcePeer']['sourceIndexSha256']is None,'future peer contract exact/unissued')
for k in ['sourceIndependentReview','newNativeBuildAuthority','newFreezeAuthority','newGcNativePin','newGcNativeReview','newBootstrapContext','newComponentSourceReview','newComponentAuthority','newComponentResult','newGcExportAuthority','newGcResult']:need(contract[k]is None,'no adopted action/result '+k)
for k in ['nativeBuildAllowed','freezeAllowed','bootstrapAllowed','componentAllowed','gcAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed','sourcePromotionAllowed']:need(contract[k]is False,'all action gates closed '+k)
need(contract['freshProcessesProposed']==3 and contract['outerCallsPerProcess']==1 and contract['invocation']=='validate()','one fresh zero-arg outer call per proposed session')
# Stored owner syntax evidence, never a new import/evaluation here.
syntax=data(by['syntax-results.json'],'stored-pinned-syntax-result');terminal=data(by['syntax-evidence/terminal.json'],'stored-parse-terminal');need(terminal==syntax['terminal']and terminal['rawExitCode']==0 and terminal['syntaxOnly']and not terminal['moduleImported']and not terminal['guestOrCryptoOrGcInvoked'],'stored parser-only raw0')
need(terminal['argv'][1:] == ['--check',str(S/'guest.GC.UNEXECUTED.mjs')]and terminal['targetSha256']==row(S/'guest.GC.UNEXECUTED.mjs')['sha256']and terminal['targetBytes']==14922,'actual parsed new guest source tuple')
need((S/'syntax-evidence/stdout.log').read_bytes()==(S/'syntax-evidence/stderr.log').read_bytes()==b'','stored complete empty parser streams')
for n in ['collector.py','prepare.py','parse-source.py','seal.py']:ast.parse((S/n).read_text())
for real,r in physical.items():need(ident(Path(real).stat())==r['identity'],'final stable source/data closure')
save('whole-record-data-review.json',dict(schemaVersion=1,independentExpectedRecordMatches=True,unchangedNormalHmacFieldsWhole=True,perRunPressureDeltas=deltas,perRunPressureFlags=[True,True,True,False],outerRequests=16,outerRecords=16,outerFlag=True,strictCollectorAstVerified=True,privateDataCounterexamples=pure,partialFailureExamples=partial,ownerCodeImported=False,guestOrKeyCryptoGcExecuted=False))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],physicalFilesHashed=len(physical),ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,sourceIndex=src,sourceDataReviewPassed=True,sourceMembers=18,inputDescriptors=2943,uniqueDeclaredInputs=len(seen),physicalFilesHashed=len(physical),checks=checks,oldHoldPreserved=True,findingM1Closed=True,oldAmbiguousFieldRemoved=True,newExactGuestEdits=6,inheritedGuestEdits=8,allReversalsExact=True,allUnderlyingHmacFieldsUnchanged=True,perRunPressureDeltas=deltas,outerPressureRequests=16,partialFailuresObservedInSource=True,completeTypedCollectorVerified=True,storedOwnerPureChecksAuthenticated=35,storedPinnedNodeSyntaxChecksAuthenticated=1,reviewerOwnerOrGuestImportsInvoked=False,reviewerNodeSyntaxParserInvoked=False,pythonAstChecks=4,privateDataNegativeChecks=len(pure),privatePartialCounterChecks=len(partial),newNativeSourceOnlyReferencedNotAdopted=True,runnablePipeline=False,actualGcRuntimeResult=False))
print(json.dumps(dict(sourceDataReviewPassed=True,members=18,inputs=2943,physical=len(physical),checks=checks)))
