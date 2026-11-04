#!/usr/bin/env python3
"""Independent JSON/hash/source-data reader; never imports the owner checker."""
import hashlib,json,math,re,stat
from pathlib import Path
P=Path(__file__).resolve().parent
Z=P.parent
C=Z/'node-deviation-contract-candidate-v1'
seen={}
def need(v,m):
 if not v:raise AssertionError(m)
def row(p,e=None):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'ordinary final file '+str(p));h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 after=p.lstat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'stable read')
 r=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
 if e:need(all(r[k]==e[k] for k in ('sha256','bytes')),'exact tuple '+str(p))
 seen[str(p)]=r;return r
def data(p):return json.loads(Path(p).read_text())
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def main():
 ix=row(C/'index.json');need(ix['sha256']=='de59758c44bf45638c7c1b620068da519d88b847ea72a0c03f029dc2e33d1469','sealed source index');index=data(C/'index.json');need(len(index['files'])==6,'six source files');names=set()
 for x in index['files']:
  p=Path(x['path']);need(p.parent==C and p.name not in names,'finite absolute original source context');names.add(p.name);row(p,x)
 refs=data(C/'source-inputs.json');need(refs['parentConsumedManifestsFollowed'] is False,'not a runtime packaging closure');refs=refs['files'];need(len(refs)==129 and len({x['path'] for x in refs})==129,'exact129 input rows')
 refmap={x['path']:x for x in refs}
 for x in refs:row(x['path'],x)
 c=data(C/'contract.proposal.json');need(c['state']=='SOURCE_ONLY_UNAPPROVED_ZLIB_M0_13_NODE_DEVIATION_CONTRACT' and c['sourceOnly'] is True,'unapproved source-only proposal')
 for k in ['actionsExecuted','operationalAdmission','sourcePromotionIssued','runtimeAcceptanceClaim','performanceClaim','errorParityClaim']:need(c[k] is False,'closed '+k)
 for k in ['actionAuthority','approvedDecision','enginePins']:need(c[k] is None,'null '+k)
 ledger=data(c['sourceLedger']['path']);need(c['sourceLedger']['sha256']==refmap[c['sourceLedger']['path']]['sha256'],'exact historical ledger')
 old={x['index']:x for x in ledger['rows']};rows=c['rows'];need(len(rows)==22 and len({x['id'] for x in rows})==22 and {x['index'] for x in rows}==set(old),'exact22 unique observed differences')
 nodepath=rows[0]['citations']['nodeOracle']['path'];node=data(nodepath);need(node['node']=='v22.14.0' and node['nodeExecutableSha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','historical Node identity')
 groups={};allowed={'FUTURE_SEMANTIC_FIX_CANDIDATE','PROPOSED_INTENTIONAL_PROFILE_LIMIT','PROPOSED_STRICT_LIMIT_REQUIRES_EXPLICIT_DECISION'}
 for g in c['groups']:
  need(g['classification'] in allowed,'unapproved known classification')
  for i in g['indices']:need(i not in groups,'no overlapping proposal groups');groups[i]=g
 need(set(groups)==set(old),'group partition covers exact22')
 observations=0;rawpaths=set();audit=[]
 for r in rows:
  i=r['index'];need({k:v for k,v in r.items() if k!='proposedDisposition'}==old[i],'all original row values/null labels preserved')
  n=node['cases'][i];need(n['index']==i and n['id']==r['id'] and n['node']==r['nodeOutcomeAndErrorAsRecorded'] and n['deviation']==r['sourceDeviationValuePreserved'],'same actual Node/corpus row')
  need(r['citations']['nodeOracle']['jsonPointer']==f'/cases/{i}/node','exact Node pointer')
  need(r['citations']['sourceCorpus']['caseIndex']==i and r['citations']['sourceCorpus']['caseId']==r['id'],'exact corpus identity citation')
  disp=r['proposedDisposition'];g=groups[i];need(disp['decisionState']=='UNAPPROVED_SOURCE_PROPOSAL' and disp['classification']==g['classification'] and disp['group']==g['id'] and disp['validationExpectation']==g['proposal'],'proposal separate from original row')
  error=r['profileErrorAsObserved'];need(set(error)=={'name','fields'} and 'message' not in error,'guest message unrecorded')
  if n['node']['kind']=='ok':diff=['outcome']
  else:
   need(n['node']['kind']=='error','finite Node outcome');diff=[]
   if error['name']!=n['node']['name']:diff.append('error.name')
   for k in ['code','errno']:
    if {a:error['fields'][k][a] for a in ['type','value']}!=n['node'][k]:diff.append('error.'+k)
  need(diff==r['comparisonDifferences'],'independently reconstructed field differences')
  for cit in r['citations']['guestRawObservations']:
   path=cit['path'];need(path in refmap and path not in rawpaths,'unique manifest-bound guest record');rawpaths.add(path);raw=data(path);need(raw['index']==i and raw['id']==r['id'] and raw['outcome']=='error' and raw['error']==error,'full actual guest error record equality')
   need(raw['partialOutputPublished'] is False and raw['inputImmutable'] is True,'recorded no partial output and input ownership')
   fields=raw['error']['fields'];e=fields['errno'];op=fields['operation']
   if e['own']:need(e['type']=='number' and type(e['value']) is int and math.isfinite(e['value']) and op==dict(own=False,type='undefined',value=None),'native numeric errno/absent operation as captured')
   else:need(e==dict(own=False,type='undefined',value=None) and op['own'] and op['type']=='string','facade operation and absent errno as captured')
   observations+=1
  need(r['observationCount']==len(r['citations']['guestRawObservations']),'actual citation counts')
  audit.append(dict(index=i,id=r['id'],recomputedDifferences=diff,sourceDeviationValuePreserved=r['sourceDeviationValuePreserved'],guestObservationCount=r['observationCount'],proposedGroup=g['id'],classification=g['classification'],decisionApproved=False,guestMessageRecorded=False,nodeOwnPropertyFlagsRecorded=False,citations=r['citations']))
 need(observations==100 and len(rawpaths)==100,'all100 actual error records')
 errno=[x['index'] for x in audit if x['recomputedDifferences']==['error.errno']];need(errno==[7,10,24,27,41,44],'six additional errno-only cases')
 need(sum(x['sourceDeviationValuePreserved'] is None for x in audit)==11,'eleven null labels remain')
 need(all(node['cases'][i]['node']['result']['bytes']==16777217 for i in [12,29,46]),'Node oracle declared global over-cap lengths')
 need([node['cases'][i]['node']['result']['bytes'] for i in [15,16,32,33,49,50]]==[512,256,256,256,256,256],'nonuniform Node concatenation/trailing observations')
 need(node['cases'][51]['node']['errno']['value']==2 and old[51]['profileErrorAsObserved']['fields']['errno']['value']==2,'dictionary errno2 both sides')
 need(node['cases'][56]['node']['code']['value']=='ERR_BUFFER_TOO_LARGE' and old[56]['profileErrorAsObserved']['fields']['code']['value']=='ERR_OUT_OF_RANGE','fractional decision not hidden')
 prior=data(Z/'independent-normal-codec-validation-v2-results-review-v1/results.json');need(prior['fullSuccessfulByteObservations']==138,'historical full-byte result count only')
 constant=c['constantDeviation'];need(constant['node']==node['inventory']['constants']['ZLIB_VERNUM']['value']==4865 and constant['observedProfile']==prior['sourceCoupledVernum']==4880,'separate observed numeric constant difference')
 need(constant['unchangedHistoricalRuntimeBackendProof']==prior['runtimeBackendProof']==dict(verified=False,version=None,vernum=None) and constant['sourceCoupledInferenceOnly'] and constant['privateVersionObserved'] is False,'private backend proof remains false/null/null')
 need(c['domain']['inputBytesMax']==1048576 and c['domain']['outputBytesMax']==16777216 and c['domain']['optionValidationPrecedesInputValidation'],'explicit public logical caps')
 for pair in c['actualNativeSourceIdentity']:
  need(pair['frozen']['path'] in refmap and pair['proposalAncestry']['path'] in refmap,'both source ancestry contexts bound');need(Path(pair['frozen']['path']).read_bytes()==Path(pair['proposalAncestry']['path']).read_bytes(),'actual frozen350 bytes equal original proposal ancestry')
 frozen=Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze/source/builtins/node-compat/zlib');facade=(frozen/'facade.mjs').read_text();kernel=(frozen/'kernel.cpp').read_text();bounded=(frozen/'bounded-codec.h').read_text()
 need(facade.index('const limit = outputLimit(options, operation)')<facade.index('const source = bytes(input, operation)'),'options precede input validation')
 need('!isInteger(value) || value < 1 || value > MAX_OUTPUT' in facade,'current strict fractional option boundary')
 need('const char *runtime = zlibVersion();' in kernel and 'std::strcmp(runtime, ZLIB_VERSION) != 0' in kernel and 'JS::Int32Value(static_cast<int32_t>(ZLIB_VERNUM))' in kernel,'source-coupled public number guarded by header/runtime comparison')
 need('result.status = stream.value.avail_in == 0 ? Status::Ok : Status::TrailingData' in bounded,'one-stream exact consumption source')
 nodejs=Z/'source-freeze/node/lib/zlib.js';text=nodejs.read_text();need('value: ObjectFreeze(codes)' in text,'concrete primary-source codes-freeze counterexample')
 constant_source=(frozen/'constant-data.generated.mjs').read_text();need('Object.freeze(Object.assign(Object.create(null)' in constant_source,'profile frozen null-prototype data source')
 need('Frozen default/constants/codes differs from Node mutability' in c['domain']['namespace'],'preserve exact overbroad source statement as finding')
 finding=dict(id='NODE-DEVIATION-CONTRACT-SOURCE-M1',severity='SOURCE_ACCURACY_QUALIFICATION_REQUIRED',affectedProposal='domain.namespace and README mutability sentence; inherited manifest wording is not rewritten',source=dict(**row(nodejs),line=922),sourceWitness='value: ObjectFreeze(codes)',conclusion='Pinned Node22 also freezes codes. Frozen status of codes alone is not a Node deviation. Default/constants/codes descriptor/prototype/mutability distinctions need separately pinned or observed evidence.',errorRowsAffected=0,actionOrPolicyAuthorized=False)
 for x in refs:row(x['path'],x)
 result=dict(schemaVersion=1,state='INDEPENDENT_NODE_DEVIATION_CONTRACT_DATA_VERIFIED_SOURCE_QUALIFICATION_HOLD',disposition='DATA_INTEGRITY_PASS_SOURCE_MUTABILITY_CLAIM_REQUIRES_QUALIFICATION',sourceIndex=ix,sourceFilesRehashed=6,inputReferencesRehashed=129,originalLedgerRowsPreserved=22,nodeRecordsCompared=22,actualGuestErrorRecordsCompared=100,outcomeOrCodeDifferences=16,additionalErrnoOnlyDifferences=6,originalNullDeviationLabels=11,guestMessagesInvented=False,nodeOwnPropertyFlagsInferred=False,nodeErrnoUndefinedIsNotOwnAbsenceClaim=True,groupClassificationsApproved=False,fractionalOptionDecisionApproved=False,extraErrnoSemanticFixApproved=False,proposedPolicyAccepted=False,sourceFinding=finding,separateConstantDifference=dict(observedProfile=4880,node=4865,sourceCoupledInferenceOnly=True,privateVersionObserved=False),historicalRuntimeBackendProof=dict(verified=False,version=None,vernum=None),historicalSuccessfulByteObservations=138,successfulBytesReexecutedOrRevalidatedByThisSourceReview=False,ownerCheckerOrHelperInvoked=False,NodeCodecGuestNativeOrHostActionsInvoked=False,operationalAdmission=False,sourcePromotionIssued=False,runtimeAcceptanceClaim=False,performanceClaim=False,uniqueInputsRehashed=len(seen))
 write('row-audit.json',audit);write('source-findings.json',[finding]);write('rehashed-inputs.json',[seen[k] for k in sorted(seen)]);write('results.json',result);print(json.dumps(dict(state=result['state'],rows=22,guestErrors=100,uniqueInputs=len(seen),sourceFindings=1)))
if __name__=='__main__':main()
