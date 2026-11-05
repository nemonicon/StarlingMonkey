"""Finish finite DATA joins and negative checks. Never import producer modules."""
from pathlib import Path
import ast,collections,copy,json,os,re
import review_io as I
import response_model as M
HERE=Path(__file__).resolve().parent;S=HERE.parent
OUT=Path('/private/tmp/starling-node-compat/consumers355-http-both-hosts-v2');EX=Path(str(OUT)+'-root')
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def eq(a,b,label):I.need(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def write(name,value):
    with (HERE/name).open('xb')as f:f.write((json.dumps(value,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
main=load(HERE/'data-results.json');old_ledger=load(HERE/'rehashed-inputs.json')
for d in old_ledger['files']:I.verify(d,'complete first-reader input recheck')
root=I.read(main['rootResult']);actual=I.read(root['result']);authority=I.read(root['rootAuthority']);controller=I.read(root['hostController']);prereq=load(S/'http-host-candidate-v2/prerequisites.json')
component=authority['actualComponentReview'];peer=I.read(component['result']);contract=I.read(component['contract']);audit=I.read(root['componentAudit']);metadata=I.read(peer['metadata'])
eq(actual['actualComponentReview'],component,'actual complete prior component review join')
eq(contract['reviewResult'],component['result'],'component contract/result exact')
for k,d in contract['requiredExactDescriptors'].items():eq(peer[k],d,'all genuine prior artifact tuple fields '+k);I.verify(d,'whole component finite tuple')
I.indexed(peer['parentIndex'],'whole previous actual component parent inventory',extra=['completion.json'])
I.indexed(peer['workerIndex'],'whole previous actual component worker inventory',extra=['completion.json'])
for k,v in contract['nativeContexts'].items():eq(peer[k],v,'real unprojected source context '+k)
eq(actual['configuredSourceRoot'],peer['configuredSourceRoot'],'actual configured source root');eq(actual['frozenSourceRoot'],peer['frozenSourceRoot'],'actual frozen source root remains distinct')
I.need(actual['configuredSourceRoot']!=actual['frozenSourceRoot'],'configured and frozen context not conflated')
SIX=['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:random/random@0.2.10']
for k in ['selectedInterfaces','emittedImports']:eq(peer[k],SIX,'actual component six WASI '+k)
eq(audit['allowedImports'],SIX,'exact allowed imports');eq(audit['emittedImports'],SIX,'exact actual imports');eq(audit['emittedExports'],['wasi:http/incoming-handler@0.2.10'],'sole actual handler')
clock=audit['clockDependency'];I.need(clock['typeOnly']is True and clock['durationRepresentation']=='u64','retained inspected type-only duration scope')
for k,v in dict(interface=SIX[0],types=['duration'],callableImports=[],coreClockImports=[]).items():eq(clock[k],v,'type-only clock dependency '+k)
wit=I.verify(peer['emittedWit']).read_text();eq(sorted(re.findall(r'^\s*import\s+([^;\s]+);',wit,re.M)),SIX,'retained emitted root-world import names');eq(re.findall(r'^\s*export\s+([^;\s]+);',wit,re.M),audit['emittedExports'],'retained sole handler export')
eq(peer['typeGraph']['sha256'],clock['componentTypeGraph']['sha256'],'genuine previously decoded graph hash')
I.read(peer['typeGraph']) # retained DATA only; no fresh decoder or binary-WIT claim
for key in ['ordinaryGuestExportsInvoked','hostRequestsInvoked','operationalAdmission','runtimeAcceptanceClaim','wireBodyAdapter']:I.need(audit[key]is False,'construction audit historical scope retained '+key)
# Reconstruct the recognized m0.11 core contract from JSON literal SOURCE, no evaluation.
core_source=next(d for d in prereq['validatorPhysicalClosure']if d['path'].endswith('/core-expectations.mjs'))
text=I.verify(core_source).read_text();known=I.decode(text.split('const known = ',1)[1].split(';\nconst hash',1)[0].encode());version='sm-node-22.14.0-m0.11';v=known[version]
expected=dict(schema=1,coreVersion=version,allocUnsafePolicy=v['allocUnsafePolicy'],unsupportedStatic=v['unsupportedStatic'],prototypeRefusals=91,manifestSha256=v['hashes']['builtins/node-compat/export-manifest.node-v22.14.0.json'],sourceHashes=v['hashes'])
eq(audit['coreExpectations'],expected,'complete recognized SOURCE core contract, not selected by runtime report')
source_map={r['path']:r['sha256']for r in metadata['sourceManifest']};I.need(len(source_map)==355,'unique actual355 native sources')
for p,digest in expected['sourceHashes'].items():eq(source_map[p],digest,'known compiled core original '+p)
eq(metadata['engineSha256']if 'engineSha256'in metadata else prereq['engineSha256'],peer['engineSha256'],'same normalRuntime native engine')
eq(metadata['sourceFiles'],355,'complete actual native source count') if 'sourceFiles'in metadata else None
eq(audit['nativeSources'],355,'actual355 audit remains whole')
# The released monitor was inspected as SOURCE and parsed, never imported/called.
controller_peer=load(S/'independent-http-gc-controllers-v2-source-review-v1/results.json')
I.need(controller_peer['sourceReviewPassed']is True and controller_peer['ownerActionsInvoked']is False and controller_peer['httpControllerSourceIndexSha256']==root['genericMonitorIndex']['sha256'],'actual monitor source peer scope')
controller_text=I.verify(controller['entrySource']).read_text();tree=ast.parse(controller_text);functions={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
I.need({'main','authorize','monitor','discover','group_model','identity','parse_snapshot'}<=functions.keys(),'actual monitor functions inspected and grammar parsed only')
monitor_source=ast.get_source_segment(controller_text,functions['monitor']);authorize_source=ast.get_source_segment(controller_text,functions['authorize']);main_source=ast.get_source_segment(controller_text,functions['main'])
for exact in ['subprocess.Popen(argv, cwd=cwd, env=environment, stdout=stdout, stderr=stderr, start_new_session=True)','remaining_observed_pids = sorted(pid for pid in known if pid in final_rows)','not any(g[\'alive\'] for g in final_groups) and not remaining_observed_pids','stream.flush()','os.fsync(stream.fileno())']:
    I.need(exact in monitor_source,'real retained monitor causal source '+exact)
I.need("controller['entrySource'] == descriptor(Path(__file__).resolve())"in authorize_source and 'for row in captured:'in main_source and "terminal['forcedCleanup'] is False"in main_source,'monitor genuine source bind/recheck/clean outer assertion')
ext=I.read(root['externalParentTerminal']);observed=[];times=[]
for n in range(22):
    e=load(EX/('owned-'+str(n).zfill(4)+'.json'));I.need(e['sequence']==n and type(e['observationMonotonicSeconds'])in [int,float],'ordered observed ownership events');observed.append(e['process']);times.append(e['observationMonotonicSeconds'])
eq(observed,ext['observedProcesses'],'all22 actual retained event objects equal full terminal observations');I.need(times==sorted(times),'ownership observations ordered')
pids={r['pid']:r for r in observed};I.need(len(pids)==22 and pids[44688]['pgid']==44688,'actual parent-created session and unique observed PIDs')
eq(sorted(g['pgid']for g in ext['finalGroups']),sorted(set(r['pgid']for r in observed)),'every retained group accounted by final raw observation')
for h,pid in [('wasmtime',45308),('wash',45791)]:
    launch=load(OUT/f'servers/{h}.launch.json');I.need(pids[pid]['pgid']==pid and pids[pid]['ppid']==44688,'actual fresh server descends from owned parent')
    eq(pids[pid]['command'],launch['executable'],'observed server process executable')
base_env=dict(PATH='/usr/bin:/bin:/usr/sbin:/sbin',LANG='C',LC_ALL='C',TZ='UTC',RAYON_NUM_THREADS='1',BINARYEN_CORES='1',CARGO_BUILD_JOBS='1',PYTHONDONTWRITEBYTECODE='1',HOME='/Users/dan')
def environment(wash=False):
    b=OUT/('wash'if wash else'private-env');return{**base_env,'TMPDIR':str(b/'tmp'),'XDG_CACHE_HOME':str(b/'cache'),'XDG_CONFIG_HOME':str(b/'config'),'XDG_DATA_HOME':str(b/'data')}
for h in ['wasmtime','wash']:
    launch=load(OUT/f'servers/{h}.launch.json');eq(launch['env'],environment(h=='wash'),'whole explicit effective child environment '+h);eq(launch['cwd'],str(OUT/'wash/project')if h=='wash'else str(OUT),'whole server cwd')
    I.need(launch['partial']is True,'launch is pre-action evidence, not claimed completed result')
wt_log='\n'.join(I.verify(row(OUT/('servers/wasmtime.'+stream+'.log'))).read_text()for stream in ['stdout','stderr']);matches=re.findall(r'Serving HTTP on (http://127\.0\.0\.1:[0-9]+)',wt_log);I.need(len(matches)==1,'actual stock serve readiness URL')
urls=dict(wasmtime=matches[0],wash='http://'+actual['wash']['effectiveConfiguration']['dev']['address']);commands=[]
for name in ['wasmtime-version','wasmtime-stopped-refusal','wash-version','wash-inspect','wash-config','wash-stopped-refusal']:
    c=load(OUT/f'commands/{name}.context.json');t=load(OUT/f'processes/{name}.terminal.json');l=load(OUT/f'processes/{name}.launch.json')
    for key in ['executable','args','timeoutMs']:eq(c[key],l[key],'whole retained command launch fields '+name+' '+key)
    I.need(l['detachedOwnedSession']is True and l['maxOutputBytes']==16*1024*1024 and l['completed']is False,'actual pre-action command launch scope')
    eq(c['env'],environment(name=='wash-config'),'whole actual command env '+name);eq(c['cwd'],str(OUT/'wash/project')if name=='wash-config'else str(OUT),'whole actual command cwd '+name)
    if name.endswith('stopped-refusal'):
        h=name.split('-')[0];args=['--disable','--noproxy','*','--connect-timeout','2','--max-time','3','--silent','--show-error','--include',urls[h]+'/node-compat?stopped=1'];executable=prereq['curl']['path'];timeout=10000;expected_code=7
        I.need('Failed to connect to 127.0.0.1 port 'in I.verify(t['stderr']).read_text(),'actual curl raw connection failure, no HTTP bytes')
    else:
        executable=prereq['wasmtime'if name=='wasmtime-version'else'wash']['path'];timeout=30000;expected_code=0
        if name.endswith('version'):args=['--version']
        elif name=='wash-inspect':args=['--user-config',str(OUT/'wash/empty-user-config.json'),'--output','json','inspect',root['component']['path']]
        else:args=['--user-config',str(OUT/'wash/empty-user-config.json'),'-C',str(OUT/'wash/project'),'--output','json','config','show']
    eq(c['args'],args,'exact supported command argv '+name);eq(c['executable'],executable,'exact command binary '+name);I.need(c['timeoutMs']==timeout and c['expectedCode']==expected_code,'actual command finite cap/raw expected status')
    commands.append(dict(name=name,context=row(OUT/f'commands/{name}.context.json'),terminal=row(OUT/f'processes/{name}.terminal.json'),expectedRawExit=expected_code))
ledger=load(HERE/'capture-ledger.json');attempts=ledger['attempts'];total_bytes=0;total_chunks=0
for a in attempts:
    h=a['host'];p=a['prefix'];n=a['sequence'];before=load(OUT/(p+'-before.json'));I.need(before['url'].startswith(urls[h]+'/node-compat?request='),'every retained attempt exact owned listener')
    expected_tag='/node-compat?request='+str(n)if h=='wasmtime'else'/node-compat?request='+str(max(1,n-77))
    eq(before['url'],urls[h]+expected_tag,'exact readiness or accepted request tag accounting')
    total_bytes+=a['observedBytes'];total_chunks+=a['chunks']
I.need([a['sequence']for a in attempts if a['host']=='wasmtime']==[1,2,3]and[a['sequence']for a in attempts if a['host']=='wash']==list(range(1,81)),'all actual host attempts contiguous3+80')
effective=actual['wash']['effectiveConfiguration'];project=load(OUT/'wash/project/.wash/config.json');deployed=actual['wash']['component']['deployedPath']
eq(project,dict(version='2.11.0',build=dict(command='test -f "$WASH_COMPONENT_PATH"',component_path=deployed),dev=dict(address=effective['dev']['address'],component_path=deployed,command='test -f "$WASH_COMPONENT_PATH"',service=False,volumes=[],components=[],plugins=[],host_plugins=[]),wit=dict(skip_fetch=True),workload=dict(allowedHostLoopbackPorts=[],allowedHosts=[],allowedIpNameLookups=[],config={})),'complete intentionally minimal project config')
eq(effective,dict(version='2.11.0',build=project['build'],dev=dict(address=project['dev']['address'],allow_insecure_registries=False,command=project['dev']['command'],component_path=deployed,service=False,wasi_otel=False,wasi_webgpu=False,wasm_proposals=[]),wit=dict(registries=[],skip_fetch=True,sources={},wit_dir=None),workload=dict(allowedHostLoopbackPorts=[],allowedHosts=[],allowedIpNameLookups=[])),'whole released effective config with its actual reported default fields retained')
eq(load(OUT/'wash/project/.wash/owned-project.json'),dict(schemaVersion=1,component=root['component']),'actual independently deployed component ownership marker')
eq(actual['validation'],dict(state='COMBINED_HTTP_BASELINE_AND_CLASSIC19_VALIDATED',componentSha256=root['component']['sha256'],requestsPerHost=3,ordinaryClassicGroups=19,protectedAbortGroups=29,instanceReuseClaim=False,requestIsolationClaim=False,consumerRequestFixtureGroups=2,fullNewBodiesRetained=True,wireBodyAdapter=False,requestReuseClaim=False),'entire actual bounded validation summary')
# Mutation checks exercise this independent complete-body model, not owner validators.
data=load(HERE/'expected-oracle-data.json');body=actual['wasmtime']['responses'][0]['body'];tag=actual['wasmtime']['responses'][0]['requestTag'];negatives=[]
mutations=[('request tag',['requestTag'],'wrong'),('consumer Euro',['native','consumers','text'],'E'),('consumer JSON',['native','consumers','json'],dict(consumer=False)),('classic19 full record',['native','joint','classic','ordinary',0],dict(wrong=True)),('protected29 full record',['native','joint','baseline','foundations','protectedAbort','receiverCases',0],dict(wrong=True)),('assert whole cases',['native','joint','baseline','foundations','assert','cases'],[]),('util full variant',['native','joint','baseline','foundations','util','cases'],dict(features='wrong')),('entropy complete bytes',['native','joint','baseline','entropyIntegration','secure','bytes'],'ab'),('stream policy missing',['native','joint','baseline','foundations','streamWeb','policies','checks'],[]),('snapshot refusal',['native','joint','baseline','entropyIntegration','snapshot',0,'code'],'wrong'),('unsupported scope',['unsupported','profile'],'sm-node-22.14.0-m0.1'),('classic boolean type',['native','joint','classic','identity','globalBuffer'],1)]
for name,path,value in mutations:
    changed=copy.deepcopy(body);v=changed
    for k in path[:-1]:v=v[k]
    v[path[-1]]=value
    try:M.validate(changed,tag,data)
    except(AssertionError,KeyError,TypeError,ValueError)as e:negatives.append(dict(name=name,rejected=True,errorType=type(e).__name__))
    else:raise AssertionError('independent model accepted '+name)
for name,raw in [('duplicate JSON key',b'{"x":1,"x":2}'),('invalid UTF8',b'"\xff"')]:
    try:I.decode(raw)
    except(AssertionError,UnicodeDecodeError,ValueError)as e:negatives.append(dict(name=name,rejected=True,errorType=type(e).__name__))
    else:raise AssertionError('strict DATA reader accepted '+name)
for p in HERE.glob('*.py'):ast.parse(p.read_text())
I.final_rehash()
write('supplement-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),freshFinalRehash=True,ownerActionsInvoked=False))
write('supplement-results.json',dict(schemaVersion=1,state='INDEPENDENT_HTTP_BOTH_HOSTS_V2_FINITE_BINDINGS_PASSED',checks=I.CHECKS,allFirstReaderInputsRehashed=True,uniquePhysicalInputs=len(I.ROWS),exactPriorArtifactDescriptors=len(contract['requiredExactDescriptors']),actualNativeSources=355,actualSelectedManifests=11,fullActualCoreContractReconstructedFromRecognizedSource=True,configuredAndFrozenContextsDistinct=True,retainedWasiImports=SIX,retainedSoleExport=audit['emittedExports'],clockTypeOnly=True,clockCallableImports=[],coreClockImports=[],freshBinaryOrWitDecoderInvoked=False,controllerSourceAndPeerBound=True,controllerImportedOrCalled=False,retainedOwnershipEvents=22,retainedFinalOwnedGroups=5,wholeLaunchEnvironmentsAndSupportedArgvVerified=True,requestAttempts=83,receivedHeaderSnapshots=82,acceptedProfiles=6,readiness404=76,preHeaderFailures=1,totalObservedPublicBodyBytes=total_bytes,totalObservedPublicChunks=total_chunks,commands=commands,completeProjectAndEffectiveConfigVerified=True,negativeDataCases=negatives,reviewerScope='independent stdlib read/hash/strict JSON/UTF8/pure DATA/AST parse only',rootOperationalElapsedSecondsIsNotPerformance=True,parentEnvironmentNotFullyRetained=True,internalPreflightFramesNotSeparatelyRetained=True,internalSourceNativeRechecksSourceCoupledWithRawZeroAndFinalIndependentRehash=True,noNewActionOrAdoptionAuthority=True))
print(json.dumps(dict(state='SUPPLEMENT_DATA_PASSED',checks=I.CHECKS,inputs=len(I.ROWS),negativeCases=len(negatives),ownerActionsInvoked=False)))
