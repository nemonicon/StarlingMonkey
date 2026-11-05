"""Actual completed HTTP DATA audit. No owner code/CLI/host/process action."""
from pathlib import Path
import ast,json,re,os,hashlib,collections
import review_io as I
import response_model as M
HERE=Path(__file__).resolve().parent;S=HERE.parent
OUT=Path('/private/tmp/starling-node-compat/consumers355-http-both-hosts-v2');EX=Path(str(OUT)+'-root')
ROOT_SHA='a1d2b9a258de95e47bc253a422dbca64c4153a3b36091111664f88985e0f3181'
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def same(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def eq(a,b,msg):I.need(same(a,b),msg)
def write(name,v,raw=False):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(v if raw else(json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
    return row(p)
root_row=dict(path=str(S/'http-both-hosts-v2-root-results.json'),sha256=ROOT_SHA,bytes=4748)
root=I.read(root_row);I.need(root['rootObservedToolRawExitCode']==0 and root['rootToolSessionId']==72742,'final raw Root tuple, never partial outputs')
index,members=I.indexed(root['index'],'actual complete HTTP-v2 output',extra=['completion.json']);I.need(len(members)==391,'391 indexed output members')
for r in members:
    st=I.canonical(r['path']).stat();I.need(st.st_nlink==1 and st.st_size<=1024**3,'ordinary independently owned bounded actual output')
result=I.read(root['result']);complete=I.read(root['completion']);I.verify_descriptors(root,'actual Root observation binding')
for key in ['result','index']:eq(complete[key],{**root[key],'path':'results.json' if key=='result' else key+'.json'},'completion exact '+key)
eq(complete['sourceIndex'],root['sourceIndex'],'source/completion join');eq(complete['component'],root['component'],'same component completion')
I.need(result['state']=='CONSUMERS355_HTTP_BOTH_HOSTS_COMPLETE_UNREVIEWED_EXTERNAL_ZERO_REQUIRED_V2'and complete['state']=='HTTP_HOSTS_COMPLETE_EXTERNAL_PARENT_ZERO_AND_INDEPENDENT_REVIEW_REQUIRED_V2','literal original unreviewed state preserved')
authority=I.read(root['rootAuthority']);config=I.read(root['config']);phase=I.read(root['componentPhase']);controller=I.read(root['hostController'])
eq(config,dict(schemaVersion=1,sourceIndex=root['sourceIndex'],rootAction=root['rootAuthority']),'genuine fixed actual config')
eq(result['sourceIndex'],root['sourceIndex'],'actual source seal');eq(result['rootAction'],root['rootAuthority'],'actual Root authority');eq(result['component'],root['component'],'actual component identity')
for key in ['componentPhase','hostController']:eq(authority[key],root[key],'actual phase '+key)
I.need(authority['state']=='ROOT_REVIEWED_CONSUMERS355_HTTP_BOTH_HOSTS_V2'and authority['hostRequestsAllowed']is True and authority['actionAllowed']is True,'separate genuine Root host permission')
I.need(phase['hostExecutionAllowed']is True and controller['hostExecutionAllowed']is True and controller['externalParentDeadlineSeconds']==2400,'actual independently reviewed phase/controller')
for key in ['wireBodyAdapterAllowed','metadataProjection','ordinary350Admission','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed']:I.need(authority[key]is False,'bounded Root scope '+key)
for key in ['sourceIndex','sourceReviewIndex','controllerReviewIndex','genericMonitorIndex']:
    I.indexed(root[key],'actual '+key,exact=True)
peer=I.read(authority['sourceIndependentReview']['result']);I.need(peer['sourceReviewPassed']is True and peer['sourceIndexSha256']==root['sourceIndex']['sha256']and peer['ownerActionsInvoked']is False,'actual source peer not host authority')
source_ledger=I.read(row(S/'independent-http-host-v2-source-review-v1/rehashed-inputs.json'))
for r in source_ledger['files']:I.verify(r,'complete source/native/artifact source-peer physical input')
native_ledger=I.read(row(S/'independent-http-host-v2-source-review-v1/native-context/rehashed-inputs.json'))
for r in native_ledger['physicalFiles']:I.verify(r,'actual original355 complete native/context input')
prereq=load(S/'http-host-candidate-v2/prerequisites.json');I.verify_descriptors(prereq,'actual immutable source/native/host prerequisites')
component_review=I.read(authority['actualComponentReview']['result']);contract=I.read(authority['actualComponentReview']['contract'])
I.indexed(authority['actualComponentReview']['index'],'actual immutable component review')
for k,v in contract['requiredFixedValues'].items():eq(component_review[k],v,'complete same-component prerequisite '+k)
audit=I.read(root['componentAudit']);eq(audit,result['fullActualComponentAudit'],'whole actual component audit unchanged')
metadata=I.read(component_review['metadata']);eq(metadata,audit['fullActualNativeMetadata'],'full actual355 metadata unchanged, no projection')
I.need(len(metadata['sourceManifest'])==355 and metadata['entropyPolicy']=='runtime-only'and metadata['gcStress']is False and len(audit['actualSelectedManifests'])==11,'full actual normalRuntime355 context')
snap=Path(load(S/'http-construction-candidate-v1/prerequisites.json')['paths']['packagingRoot']);suite=snap/'tests/node-compat'
for r,m in zip(metadata['selectedModuleManifests'],audit['actualSelectedManifests']):
    src=next(x for x in metadata['sourceManifest']if x['path']==r['path']);path=Path(prereq['constructionSourceIndex']['path']).parent # not a projected source root
    frozen=Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze/source')/r['path'];d=row(frozen);I.need(d['sha256']==src['sha256'],'selected actual manifest hash');eq(load(frozen),m,'whole selected manifest file')
# Rebuild expected public oracle DATA from immutable original fixtures.
events=load(suite/'foundation-events/native-node-results.json');owned=load(suite/'entropy/owned-input-node-results.json')
construction=load(S/'http-construction-candidate-v1/prerequisites.json');classic_path=Path(construction['paths']['classicNodeOracle']);classic=load(classic_path)
I.need(row(classic_path)['sha256']=='88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce'and len(classic['expected'])==19,'actual original full19 Node oracle')
o=audit['foundationOracles'];eq(o,result['fullActualComponentAudit']['baselineAndClassic']['foundationOracles'],'unchanged whole oracle origins')
for name in ['assert','querystring']:
    original=load(suite/('foundation-'+name)/'native-node-results.json');eq(o[name],dict(cases=original['cases'],profile=original['sourceProfile']),'whole original '+name+' oracle')
util=load(suite/'foundation-util/native-node-results.json');eq(o['util'],dict(variants=util['variants'],expectedExports=util['expectedExports']),'whole original util variants')
po=load(suite/'foundation-add-abort/production-native-m0.10/node-results.json')
for name in ['publicCases','nestedOnceCases','receiverCases']:eq(o['protectedAbort'][name],po[name],'all original protected29 records '+name)
eq(o['protectedAbort']['counts'],po['passed'],'original protected counts');eq(o['protectedAbort']['nodeSymbol'],po['targetSymbolInfo'],'original Node symbol descriptor/deviation origin')
I.need(o['protectedAbort']['oracleSha256']==row(suite/'foundation-add-abort/production-native-m0.10/node-results.json')['sha256'],'protected oracle bytes')
for name,digest in o['protectedAbort']['sources'].items():I.need(row(suite/'foundation-add-abort/production-native-m0.10'/name)['sha256']==digest,'protected fixture source origin '+name)
graph=load(OUT.parent/'consumers355-http-component-v1/worker/bundle-graph.json');eq(graph['foundationOracles'],o,'actual graph exact oracle DATA')
virtual={}
for r in graph['virtualModules']:
    d={**r,'path':str(Path(graph['bundle']['path']).parent/r['path'])};text=I.verify(d,'immutable actual virtual JSON source').read_text();I.need(text.startswith('export default ')and text.endswith(';'),'literal JSON-only virtual module, never evaluated');virtual[r['id']]=I.decode(text[len('export default '):-1].encode())
I.need(len(virtual['node-compat:oracle-vectors']['strings'])==381 and len(virtual['node-compat:oracle-vectors']['bytes'])==250,'full source corpus count origins')
data=dict(foundationOracles=o,eventsOracle=events,entropyOwnership=owned['cases'],classic19=classic['expected'],coreExpectations=audit['coreExpectations'],corpusSeed=virtual['node-compat:oracle-vectors']['seed'])
ext=I.read(root['externalParentTerminal']);started=I.read(root['externalParentStarted']);I.verify_descriptors(ext,'full raw external terminal/streams')
I.need(ext['pid']==44688 and ext['rawExitCode']==0 and ext['timeout']is False and ext['forcedCleanup']is False and ext['parentOwnedGroupGone']is True and ext['allObservedOwnedGroupsGone']is True,'actual external raw0 clean lifecycle')
for key in ['interruptedSignals','remainingObservedPids','signals','errors']:eq(ext[key],[],'external none '+key)
I.need(all(g['alive']is False and g['signalAllowed']is False for g in ext['finalGroups']),'all final observed owned groups gone')
eq(ext['authority'],root['rootAuthority'],'controller/authority');eq(started['authority'],root['rootAuthority'],'started/authority')
I.need(started['pid']==44688 and started['timeoutSeconds']==2400 and started['argv'][:2]==[prereq['node']['path'],str(S/'http-host-candidate-v2/run.mjs')],'pinned actual parent argv/context')
eq(I.decode(started['argv'][2].encode()),root['config'],'exact actual parent config argument')
parent_stdout=I.verify(ext['stdout']).read_bytes();I.need(ext['stderr']['bytes']==0 and len(parent_stdout.splitlines())==1,'whole clean parent raw streams')
eq(I.decode(parent_stdout),{k:{**root[k],'path':'results.json' if k=='result' else k+'.json'}for k in ['result','index','completion']},'whole raw parent completion tuple')
external_files=[]
for f in EX.iterdir():
    I.need(f.is_file()and not f.is_symlink(),'regular complete external monitor file');external_files.append(f.name);I.verify(row(f),'actual complete external inventory')
owned_names=sorted(n for n in external_files if re.fullmatch('owned-[0-9]{4}\.json',n));I.need(len(owned_names)==len(ext['observedProcesses'])==22,'all22 observed PID records retained')
I.need(set(external_files)=={'started.json','terminal.json','stdout.log','stderr.log',*owned_names},'exact26 external files')
# Every response capture is decoded from its own complete header/chunk artifacts.
caps=result['responseCaptures'];I.need(len(caps)==83,'all83 attempts separate from6 accepted profiles')
attempts=[];aggregates={};counts=collections.Counter();prefixes=set();accepted=[]
def local(d):
    name=I.member(d['path']);I.need(any(r['path']==name and r['sha256']==d['sha256']and r['bytes']==d['bytes']for r in index['files']),'capture row indexed exactly');return I.verify({**d,'path':str(OUT/name)},'complete actual capture bytes')
for cap in caps:
    aggregate=cap['aggregateBodyFile'];I.need(aggregate is not None,'actual aggregate retained');path=local(aggregate);match=re.fullmatch('(requests/(wasmtime|wash)-([0-9]{4,6}))-body(\.partial)?\.bin',aggregate['path']);I.need(match is not None,'owned finite capture name');prefix,host,sequence=match.group(1),match.group(2),int(match.group(3));I.need(prefix not in prefixes,'unique complete attempts');prefixes.add(prefix)
    before=load(OUT/(prefix+'-before.json'));header_name=prefix+('-headers.json'if cap['receivedHeaders']else'-headers.partial.json');header=load(OUT/header_name)
    eq(before['url'],header['url'],'same exact attempted URL');I.need(before['method']=='GET'and header['publicFetchHeadersNotWireBytes']is True,'ordinary public GET/header scope')
    eq(header['status'],cap['status'],'full retained status');eq(header['receivedHeaders'],cap['receivedHeaders'],'received-header availability');eq(header['headersComplete'],cap['headersComplete'],'complete header iterator state')
    I.need(cap['headersRecordRetained']is True and cap['fetchInvoked']is True and cap['allObservedChunkFilesRetained']is True and cap['allObservedBodyBytesRetained']is True and cap['availableRawRetained']is True,'actual observed public prefix durably retained')
    eq(cap['captureWriteFailures'],[],'no actual response capture write failures')
    chunks=[]
    for ordinal,d in enumerate(cap['retainedChunkFiles'],1):
        I.need(d['path']==prefix+'-chunks/'+str(ordinal).zfill(4)+'.bin','whole ordered raw chunk sequence');chunks.append(local(d).read_bytes())
    raw=path.read_bytes();I.need(b''.join(chunks)==raw and sum(map(len,chunks))==cap['observedBodyBytes']==len(raw)and len(chunks)==cap['observedChunks'],'every full chunk sequence equals aggregate bytes')
    if cap['requestFailed']:
        I.need(host=='wash'and sequence==1 and cap['status']is None and cap['receivedHeaders']is False and cap['headersComplete']is False and cap['completeResponseRetained']is False and cap['bodyStreamEnded']is False and cap['failureRecordRetained']is True and raw==b''and chunks==[],'single pre-header failure is empty observed prefix, never complete')
        failure=load(OUT/(prefix+'-failure.json'));I.need(failure['acceptedResponse']is False and failure['readinessRetryAllowed']is True and failure['requestFailed']is True,'failed attempt only permitted readiness retry')
        eq(failure['response']['headers'],[],'no invented preheader values');eq(failure['thrown'],cap['primaryFailure'],'whole compact primary failure');I.need(failure['failureRecordRetained']is False,'receipt stores pre-write durability; actual caller carrier reports post-write true')
    else:
        I.need(cap['receivedHeaders']is True and cap['headersComplete']is True and cap['bodyStreamEnded']is True and cap['completeResponseRetained']is True and cap['failureRecordRetained']is None,'complete public response retained')
        raw_meta=load(OUT/(prefix+'-raw.json'));eq(raw_meta['headers'],header['headers'],'whole public header values unchanged');eq(raw_meta['bodyFile'],aggregate,'actual aggregate descriptor');eq(raw_meta['chunkFiles'],cap['retainedChunkFiles'],'exact raw chunk descriptors');I.need(raw_meta['bodyBytes']==len(raw)and raw_meta['bodyReadState']=='ended','whole raw response metadata')
        I.need(cap['status']in [200,404],'only accepted profile or exact readiness transient status')
        if cap['status']==404:I.need(host=='wash','readiness404 only wash')
        else:accepted.append(prefix)
    counts[(str(cap['status']),cap['requestFailed'])]+=1;aggregates[prefix]=dict(raw=raw,header=header,cap=cap,host=host,sequence=sequence)
    attempts.append(dict(prefix=prefix,host=host,sequence=sequence,status=cap['status'],requestFailed=cap['requestFailed'],observedBytes=len(raw),chunks=len(chunks),aggregate=aggregate,headers=row(OUT/header_name),completeResponseRetained=cap['completeResponseRetained'],availableRawRetained=True))
I.need(dict(counts)=={('200',False):6,('404',False):76,('None',True):1},'all actual83 status/failure counts')
I.need({r['path'][:-len('-before.json')]for r in index['files']if r['path'].endswith('-before.json')}==prefixes,'no unaccounted HTTP request attempts')
validations=[];entropy=[];profile_prefixes=[]
for host in ['wasmtime','wash']:
    report=result[host];eq(load(OUT/(host+'-results.json')),report,'whole per-host report')
    I.need(len(report['responses'])==3,'three accepted profile responses per host')
    terminal=load(OUT/f'servers/{host}.terminal.json');eq(terminal,report['ownedTerminal'],'whole raw server terminal');I.need(terminal['pid']==(45308 if host=='wasmtime' else 45791),'exact fresh owned server PID')
    I.need(terminal['status']==0 and terminal['signal']is None and terminal['closed']is True and terminal['spawnError']is None and terminal['timedOut']is False and terminal['outputLimitExceeded']is False and terminal['externalSignal']is None and terminal['ownedGroupGone']is True and terminal['thrown']is None,'raw zero graceful server only')
    eq(terminal['errors'],[],'server errors none');eq(terminal['shutdownSignals'],['SIGINT'],'no forced server termination');eq(report['process'],dict(stopped=True,exitStatus=dict(code=0,signal=None)),'accepted graceful process record')
    launch=load(OUT/f'servers/{host}.launch.json');owned=load(OUT/f'servers/{host}.owned.json');I.need(owned['pid']==terminal['pid']and owned['processGroup']==-terminal['pid']and owned['detachedOwnedSession']is True and launch['detachedOwnedGroup']is True and launch['timeoutMs']==600000,'actual detached owned session')
    for k in ['executable','args','env','cwd']:eq(owned[k],launch[k],'full launch/owned context '+k)
    if host=='wasmtime':eq(launch['args'],['serve','--addr','127.0.0.1:0',root['component']['path']],'actual stock serve command');eq(launch['executable'],prereq['wasmtime']['path'],'stock WT pinned executable')
    else:eq(launch['args'],['--user-config',str(OUT/'wash/empty-user-config.json'),'-C',str(OUT/'wash/project'),'--log-level','info','--meters','duration','dev'],'actual released wash command');eq(launch['executable'],prereq['wash']['path'],'released wash pinned executable')
    I.need(any(g['pgid']==terminal['pid']and g['alive']is False for g in ext['finalGroups']),'external final observation of each server group')
    eq(launch['env'].get('HOME'),'/Users/dan','actual unchanged HOME path');I.need('home'not in launch['env']and 'CODEX_HOME'not in launch['env'],'actual absent optional inherited home spellings')
    for i,response in enumerate(report['responses'],1):
        I.need(response['status']==200 and response['requestTag']=='/node-compat?request='+str(i),'exact accepted200 request tag')
        prefix=response['rawBodyFile'][:-len('-body.bin')];I.need(prefix in accepted and aggregates[prefix]['host']==host,'accepted response refers to actual200 capture, not readiness prefix')
        raw=aggregates[prefix]['raw'];text=raw.decode('utf-8','strict');I.need(text==response['text'],'all complete raw accepted UTF8 text unchanged');body=I.decode(raw);eq(body,response['body'],'all raw JSON fields equal recorded body')
        h={k.lower():v for k,v in aggregates[prefix]['header']['headers']};eq(response['headers'],dict(contentType=h.get('content-type'),cacheControl=h.get('cache-control')),'whole selected public header values');I.need(h['content-type'].startswith('application/json')and h['cache-control']=='no-store','actual public status/header acceptance')
        validation=M.validate(body,response['requestTag'],data);entropy.append(validation['entropyHex']);profile_prefixes.append(prefix);validations.append(dict(host=host,ordinal=i,prefix=prefix,rawBytes=len(raw),rawSha256=hashlib.sha256(raw).hexdigest(),validation=validation))
eq(sorted(profile_prefixes),sorted(accepted),'exact6 accepted profiles, no transient adoption');I.need(len(set(entropy))==6,'six full32-byte samples show no obvious replay, no entropy quality proof')
# Commands: full raw versions/config/inspection and stopped refusal controls.
for name,expected in [('wasmtime-version',0),('wasmtime-stopped-refusal',7),('wash-version',0),('wash-inspect',0),('wash-config',0),('wash-stopped-refusal',7)]:
    t=load(OUT/f'processes/{name}.terminal.json');I.verify_descriptors(t,'full actual command raw streams')
    I.need(t['status']==expected and t['closed']is True and t['ownedGroupGone']is True and t['signal']is None and t['spawnError']is None and t['timedOut']is False and t['externalSignal']is None and t['outputLimitExceeded']is False,'clean raw command/expected code '+name);eq(t['errors'],[],'command errors');eq(t['signals'],[],'command collector no cleanup signals')
    context=load(OUT/f'commands/{name}.context.json');eq(t['executable'],context['executable'],'command executable');eq(t['args'],context['args'],'whole command argv')
    if expected==7:
        I.need(t['stdout']['bytes']==0,'stopped listener has no HTTP bytes');host=name.split('-')[0];eq(result[host]['stoppedServerRefusal'],dict(rawExitCode=7,stdout=t['stdout'],stderr=t['stderr'],ownedGroupGone=True),'complete raw stopped control')
    elif name=='wasmtime-version':I.need(I.verify(t['stdout']).read_text().startswith('wasmtime 42.0.1 '),'actual WT42 version')
    elif name=='wash-version':I.need(I.verify(t['stdout']).read_text().strip()=='wash 2.11.0','actual wash2.11 version')
    elif name=='wash-inspect':
        inspected=I.read(t['stdout']);I.need(inspected['success']is True,'actual released inspection');wit=inspected['data']['wit']
        for kind,expected_names in [('import',audit['emittedImports']),('export',audit['emittedExports'])]:eq(sorted(re.findall(r'^\s*'+kind+r'\s+([^;\s]+);',wit,re.M)),sorted(expected_names),'same actual six/handler names in released inspection')
    elif name=='wash-config':eq(I.read(t['stdout'])['data'],result['wash']['effectiveConfiguration'],'whole actual effective config output')
deployed=Path(result['wash']['component']['deployedPath']);d=row(deployed);I.need(d['sha256']==root['component']['sha256']and d['bytes']==root['component']['bytes'],'same complete deployed component bytes')
a=deployed.stat();b=Path(root['component']['path']).stat();I.need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'actual independently owned deployed inode')
eq(load(OUT/'wash/empty-user-config.json'),{},'explicit empty wash user config')
effective=result['wash']['effectiveConfiguration'];project_config=load(OUT/'wash/project/.wash/config.json')
for k in ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts']:eq(effective['workload'][k],[],'no outgoing capability allowlist '+k)
for k in ['volumes','plugins','components','host_plugins']:eq(effective['dev'].get(k,[]),[],'no selected extension '+k)
eq(effective['dev']['address'],project_config['dev']['address'],'actual exact configured loopback bind')
for flag in ['wireBodyAdapter','instanceReuseClaim','requestIsolationClaim','gcOrBackendProofClaim','operationalAdmission','runtimeAcceptanceClaim']:I.need(result[flag]is False,'bounded actual result '+flag)
I.need(result['sourceRecheckPassed']is True,'source-coupled full recheck completion declared with clean final')
I.full_construction_closure(I.read(prereq['constructionClosure']));I.final_rehash()
write('expected-oracle-data.json',data)
write('capture-ledger.json',dict(schemaVersion=1,attempts=attempts,acceptedProfiles=validations,totalAttempts=83,accepted200=6,readiness404=76,preHeaderFailures=1,unacceptedReadinessAttempts=77,allChunksEqualFullAggregates=True,allAvailablePublicRawRetained=True,writeFailures=0,actualModelChecks=M.CHECKS,allSixEntropySamplesUnique=True,noEntropyQualityOrRequestReuseClaim=True))
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),freshFinalRehash=True,ownerCodeExecuted=False))
write('data-results.json',dict(schemaVersion=1,state='INDEPENDENT_COMPLETED_HTTP_BOTH_HOSTS_V2_DATA_REVIEW_PASSED',rootResult=root_row,sourceIndex=root['sourceIndex'],sourceReviewIndex=root['sourceReviewIndex'],actualIndex=root['index'],actualResult=root['result'],actualCompletion=root['completion'],rootAuthority=root['rootAuthority'],config=root['config'],componentPhase=root['componentPhase'],hostController=root['hostController'],externalParentTerminal=root['externalParentTerminal'],externalParentStarted=root['externalParentStarted'],genericMonitorIndex=root['genericMonitorIndex'],controllerReviewIndex=root['controllerReviewIndex'],component=root['component'],componentAudit=root['componentAudit'],actualIndexedFiles=391,actualRegularFiles=393,externalFiles=26,observedPids=22,acceptedResponses=6,acceptedPerHost=3,totalCaptureAttempts=83,readiness404=76,preHeaderFailure=1,unacceptedReadinessAttempts=77,validatedClassicGroupRecords=114,validatedProtectedGroupRecords=174,validatedConsumerProbeValues=12,allRawChunksAndBodiesVerified=True,allSixCompleteRawUtf8AndJsonVerified=True,allInspectedSourceAndOraclePredicatesPassed=True,wholeActual355AuditMetadataManifestsUnchanged=True,sourceRechecksDeclaredAndSourceCoupled=True,retainedAllObservedPidsAndGroupsGone=True,liveProcessQueriesOrSignalsInvokedByReviewer=False,rootHelperPreflightAndBothHostsAndCurlExecuted=True,reviewerOwnerHelpersNodeCliNetworkHostGuestGcActionsInvoked=False,uniquePhysicalInputsFinallyRehashed=len(I.ROWS),readerChecks=I.CHECKS,responseModelChecks=M.CHECKS,concreteBlockers=[]))
print(json.dumps(dict(state='COMPLETED_HTTP_DATA_AUDIT_PASSED',accepted=6,attempts=83,readiness404=76,preHeaderFailure=1,modelChecks=M.CHECKS,checks=I.CHECKS,inputs=len(I.ROWS),ownerActionsInvoked=False)))
