"""Portable paired CDP-positive DATA reader. No target, browser, engine or project imports."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, re, tarfile
HERE=Path(__file__).resolve().parent
SELECTED={
 'wasi:cli/environment@0.2.10','wasi:cli/stdout@0.2.10','wasi:cli/stderr@0.2.10',
 'wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:random/random@0.2.10',
 'wasi:filesystem/types@0.2.10','wasi:filesystem/preopens@0.2.10','wasi:io/error@0.2.10',
 'wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:http/types@0.2.10','wasi:http/outgoing-handler@0.2.10'}
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
 if (HERE/'index.json').exists():
  rows=json.loads((HERE/'index.json').read_text())['files'];assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}=={r['path'] for r in rows}|{'index.json'}
  for r in rows:assert digest((HERE/r['path']).read_bytes())=={k:r[k] for k in ['bytes','sha256']}
 capsule=json.loads((HERE/'capsule.json').read_text());assert digest((HERE/'data.tar.gz').read_bytes())=={k:capsule['bundle'][k] for k in ['bytes','sha256']}
 expected={r['path']:r for r in capsule['entries']};assert len(expected)==len(capsule['entries']);data={};origins={}
 with tarfile.open(HERE/'data.tar.gz','r:gz') as archive:
  members=archive.getmembers();assert len(members)==len(expected)
  for m in members:
   p=PurePosixPath(m.name);assert m.isfile() and not p.is_absolute() and '..' not in p.parts and m.name in expected and m.name not in data
   b=archive.extractfile(m).read();row=expected[m.name];assert digest(b)=={k:row['original'][k] for k in ['bytes','sha256']}
   if row['kind']=='utf8':b.decode('utf8')
   else:assert row['kind']=='png' and b.startswith(b'\x89PNG\r\n\x1a\n')
   data[m.name]=b;assert row['original']['path'] not in origins;origins[row['original']['path']]=m.name
 assert set(data)==set(expected)
 def obj(n):return json.loads(data[n])
 def ref(r):
  n=origins[r['path']];assert digest(data[n])=={k:r[k] for k in ['bytes','sha256']};return n
 def terminal(prefix,code):
  t=obj(prefix+'/terminal.json');assert type(t['rawExitCode']) is int and t['rawExitCode']==code
  assert t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
  assert all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids']) and all(g['alive'] is False for g in t['finalGroups'])
  for k in ['authority','stdout','stderr']:ref(t[k])
  start=obj(prefix+'/started.json');assert start['pid']==t['pid'] and start['authority']==t['authority']
  events=[obj(n) for n in sorted(data) if n.startswith(prefix+'/owned-')]
  assert [r['sequence'] for r in events]==list(range(len(events))) and [r['process'] for r in events]==t['observedProcesses']
  return t,start,len(events)
 ca=obj('authority/constructor.json');ra=obj('authority/runtime.json');cr=obj('constructor/result.json');rr=obj('runtime/result.json')
 assert ca['state']=='ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2' and ra['state']=='ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2'
 for r in capsule['sourceFamilies']:
  index=obj(ref(r));base=Path(r['path']).parent
  for row in index['files']:ref({**row,'path':str(base/row['path'])})
 assert cr['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2' and cr['passed'] is True and cr['error'] is None and cr['finalProtection']=={'unchanged':True}
 assert cr['entryMode']==ca['entryMode']=='real-next' and cr['callerIndex']==ca['callerIndex']==ra['constructionCallerIndex']
 for k in ['metadataFrameProjected','ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted']:assert cr[k] is False
 for k in ['component','componentAudit','inputEntry','inputSourceIndex']:assert cr['artifacts'][k]==ra[k]==rr[k]
 assert rr['constructionResult']==ra['constructionResult']==dict(path=ca['outputRoot']+'/result.json',**digest(data['constructor/result.json']))
 assert cr['artifacts']['engine']==ca['engine'] and cr['artifacts']['nativeMetadata']==ca['nativeMetadata']
 assert cr['artifacts']['engine']['sha256']=='4623640b79b97eb91dc8559b3766fdb430a1807fe90b6ace6c85668a97f13067'
 assert cr['artifacts']['inputSourceIndex']['sha256']=='73b583bed57a6e988debe5abca156abcd2e4b5ed331b1b4171f8636d33bf1042'
 assert cr['artifacts']['inputEntry']['sha256']=='1e49ddc61094f25a46056f10869e2ec409ef03d1b2a762670720666d3dc9bf4c'
 for k in ['rootAuthority','callerIndex','plan']:ref(cr[k])
 for k in ['rootAuthority','sourceIndex','inputEntry','inputSourceIndex']:ref(rr[k])
 assert [c['label'] for c in cr['commands']]==['componentize-init','component-validate','component-wit'];processes=0
 for c in cr['commands']:
  assert c['rawExitCode']==0 and c['clean'] is True
  t,s,n=terminal('constructor/'+c['label'],0);processes+=n
  assert s['argv']==c['argv'] and s['timeoutSeconds']==c['capSeconds']
  for k in ['terminal','stdout','stderr']:ref(c[k])
  assert c['stdout']==t['stdout'] and c['stderr']==t['stderr'] and c['stderr']['bytes']==0
 ct,cs,n=terminal('constructor-outer',0);processes+=n
 assert cs['timeoutSeconds']==2400 and cs['argv'][-1]==ct['authority']['sha256'] and cs['argv'][-3]==ct['authority']['path']
 frames=[json.loads(line) for line in data['constructor-outer/stdout.log'].splitlines()]
 assert len(frames)==4 and frames[-1]=={'result':ra['constructionResult'],'passed':True,'error':None}
 assert [(x['pid'],x['timeoutSeconds']) for x in frames[:3]]==[(obj('constructor/'+c['label']+'/started.json')['pid'],c['capSeconds']) for c in cr['commands']]
 audit=obj('constructor/component-audit.json');assert audit['state']=='NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1' and audit['passed'] is True
 assert audit['component']==rr['component'] and audit['engine']==ca['engine'] and audit['nativeMetadata']==ca['nativeMetadata']
 assert len(audit['emittedImports'])==13 and set(audit['emittedImports'])==set(audit['selectedInterfaces'])==set(rr['emittedImports'])==set(rr['selectedInterfaces'])==SELECTED
 assert audit['exports']==['wasi:http/incoming-handler@0.2.10'] and audit['allEmittedVersion']=='0.2.10' and audit['noExternalPreview1OrCustomImports'] is True and audit['unusedSelectedInterfaces']==[]
 wit=data['constructor/component-wit/stdout.log'].decode();world=wit.split('world root {',1)[1].split('}',1)[0]
 assert set(re.findall(r'^  import ([^;]+);$',world,re.M))==SELECTED and re.findall(r'^  export ([^;]+);$',world,re.M)==audit['exports']
 assert 'handle: func(request: incoming-request, response-out: response-outparam);' in wit
 imports=obj('constructor/api-return/returned-imports.json');assert len(imports)==131 and {r[0] for r in imports}==SELECTED and all(len(r)==2 and all(type(x) is str for x in r) for r in imports)
 def props(x):return {r['key']['string']:r['value'] for r in x['properties']}
 shape=obj('constructor/api-return/returned-own-shape.json');assert shape['type']=='object';fields=props(shape);assert set(fields)=={'component','imports','debug'} and fields['debug']=={'type':'undefined'}
 v=fields['component'];assert v['type']=='Uint8Array' and v['file']==rr['component'] and v['sha256']==rr['component']['sha256'] and v['byteLength']==rr['component']['bytes']
 array=props(fields['imports']);assert fields['imports']['type']=='Array' and array['length']=={'type':'number','value':'131'}
 assert [[props(array[str(i)])[str(j)]['value'] for j in range(2)] for i in range(131)]==imports
 assert rr['state']=='NEXT_WASMTIME_DEPLOYMENT_CONTRACTS_PASSED_UNREVIEWED_V2' and rr['passed'] is True and rr['adoption'] is False
 assert rr['originalInputsPreserved'] is True and rr['readonlyAppPreserved'] is True
 assert rr['applicationCopy']=={'files':2218,'bytes':48808299,'byteIdentical':True,'independentInodes':True}
 plan=obj(ref(ra['plan']));rt,rs,n=terminal('runtime-outer',0);processes+=n
 assert rs['timeoutSeconds']==600 and rs['argv'][-1]==rr['rootAuthority']['path'] and rs['argv'][0]==plan['node']['path']
 assert Path(rs['argv'][1]).name=='deploy.mjs' and ref(dict(path=rs['argv'][1],**digest(data[origins[rs['argv'][1]]])))
 outer=obj('runtime-outer/observation.json');assert outer['result']==dict(path=rr['outputRoot']+'/result.json',**digest(data['runtime/result.json']))
 assert outer['rawExitCode']==0 and outer['ownedGroupsClean'] is True and outer['protectedInputsPreserved'] is True and outer['passed'] is True and outer['adoption'] is False
 assert outer['terminal']==dict(path=rr['outputRoot']+'-external-root/terminal.json',**digest(data['runtime-outer/terminal.json']))
 assert rr['server']['exit']=={'code':0,'signal':None,'error':None} and rr['server']['shutdownRequested'] and rr['server']['sigintSent'] and rr['server']['forcedCleanup'] is False
 assert rr['client']['exit']=={'code':0,'signal':None,'error':None}
 for owner in ['server','client']:
  for k in ['stdout','stderr']:ref(rr[owner][k])
 client=obj(ref(rr['client']['result']));assert client['passed'] is True and client['errors']==[] and client['transportErrors']==[]
 plan=obj(ref(ra['plan']));command=rr['server']['command'];assert command[0]==plan['wasmtime']['path'] and plan['wasmtime'] in capsule['externalReferences'] and command[-1]==rr['component']['path']
 assert command[1]=='serve' and command[command.index('--addr')+1]==rr['portLease']['address']+':'+str(rr['portLease']['port'])
 assert command[command.index('--max-instance-reuse-count')+1]=='128' and command[command.index('--idle-instance-timeout')+1]=='60s'
 assert command[command.index('-S')+1]=='cli=y,tcp=n,udp=n,allow-ip-name-lookup=n'
 assert client['origin']==rr['portLease']['origin']==rr['server']['readyOrigin'] and rr['portLease']['fallbackAllowed'] is False
 assert data['runtime/wasmtime.stderr.log']==('Serving HTTP on '+client['origin']+'/\n').encode()
 # The stock arm is real Node/Module/HTTP-bridge control, not a guest target.
 stock=obj('stock/result.json');sa=obj('authority/stock.json');sp=obj(ref(sa['plans']))
 st,ss,n=terminal('stock-outer',0);processes+=n
 assert ss['timeoutSeconds']==300 and ss['argv']==sp['arms']['stock']['argv'] and st['authority']==dict(path=ss['authority']['path'],**digest(data[ref(ss['authority'])]))
 assert sa['state']=='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1'and sa['arm']=='stock'
 for k in ['guestAllowed','engineAllowed','nativeBuildAllowed','compilerAllowed','externalApplicationDeploymentAllowed']:assert sa[k]is False
 so=obj('stock-outer/observation.json');assert so['rawExitCode']==0 and so['ownedGroupsClean']is True and so['protectedInputsPreserved']is True and so['hostExperimentPassed']is True and so['guestOrNativeExecuted']is False
 assert so['result']==next(x['original']for x in capsule['entries']if x['path']=='stock/result.json')
 assert stock['passed']is True and stock['guestExecuted']is False and stock['applicationModified']is False and stock['prepared']is True and stock['originalApplicationInputsPreserved']is True and stock['freshOwnedCacheReset']is True
 assert stock['installed']=={'next':'16.4.5','react':'19.3.1','react-dom':'19.3.1'}and stock['node']=='v22.14.0'
 assert stock['errors']==stock['transportErrors']==[]and stock['applicationCopy']['modesEqual']is True and stock['applicationCopy']['independentInodes']is True and stock['applicationCopy']['byteIdentical']is True
 assert stock['applicationCopy']['files']==2218 and stock['applicationCopy']['bytes']==48808299
 assert capsule['stockCurrentImmutableCopyFiles']==2217 and capsule['stockOwnedCacheExcludedFromImmutableCopyClaim']is True
 for k in ['bridge','harness','moduleSource','hostModuleProvider']:ref(stock[k])
 contract=obj('inputs/fixture-contract.json');application=obj('inputs/application-inputs.json');appfiles={r['path']:r for r in application['files']}
 def client_check(client,prefix,expected_cdp):
  assert client['passed']is True and client['errors']==client['transportErrors']==[]
  assert len(contract['requests'])==23 and len(client['http'])==24
  assert [x['id']for x in client['http'][:23]]==[x['id']for x in contract['requests']];bodies={}
  for i,row in enumerate(client['http']):
   b=data[prefix+'/responses/'+row['id']+'.txt'];assert len(b)==row['bodyBytes']and hashlib.sha256(b).hexdigest()==row['bodySha256'];text=b.decode();bodies[row['id']]=text
   assert row['passed']is True and row.get('failures',[])==[]
   if i==23:
    assert row['id']=='server-action-submit'and row['status']==303 and row['headers']['location']=='/action-result?value=fixture-action';continue
   e=contract['requests'][i];assert row['status']==e['status']
   for value in e.get('includes',[]):assert value in text
   if e.get('location'):assert row['headers']['location']==e['location']
   for k,v in e.get('json',{}).items():assert json.loads(text)[k]==v
   for k,v in e.get('responseHeaders',{}).items():assert row['headers'][k]==v
   for k,values in e.get('responseHeaderIncludes',{}).items():
    for v in values:assert v in row['headers'][k]
   if e.get('equalJsonTo'):assert text==bodies[e['equalJsonTo']]
  before=json.loads(bodies['cache-first']);after=json.loads(bodies['cache-after-revalidate']);assert client['cacheInvalidation']==dict(before=before,after=after,passed=True)and before['generation']==1 and after['generation']==2
  chunks=obj(prefix+'/stream-chunks.json');text='';shell=ready=-1
  for i,chunk in enumerate(chunks):
   b=base64.b64decode(chunk['base64'],validate=True);assert len(b)==chunk['bytes'];text+=b.decode()
   if shell<0 and'NEXT_STREAM_SHELL'in text:shell=i
   if ready<0 and'NEXT_STREAM_READY'in text:ready=i
  assert len(chunks)==5 and shell==0 and ready==2 and client['streaming']==dict(chunks=5,shellChunk=0,readyChunk=2,complete=True,incrementalDeliveryObserved=True)
  browser=obj(prefix+'/browser/result.json');assert client['browser']==browser and browser['origin']==client['origin']and client['browserExit']==dict(code=0,signal=None)
  assert all(browser[k]is True for k in ['functionalPassed','browserErrorFree','assetCapturePassed','passed','browserClosed','ephemeralContexts'])
  assert browser['userProfileUsed']is False and browser['wasmBrowserRun']is None and browser['perTestTimeoutMs']==20000
  assert browser['beforeCloseNetworkCompletionWait']is False and browser['responseCaptureDrainBeforeCloseLimitMs']==500 and browser['responseFinishedDrainAfterCloseLimitMs']==2000
  assert all(browser[k]==[]for k in ['errors','pageerrors','consoleerrors','failedrequests'])
  assert[(x['id'],x['passed'],x['timedOut'])for x in browser['tests']]==[('client-counter',True,False),('server-action',True,False)]
  for t in browser['tests']:
   ref(t['screenshot']);assert t['error']is None and t['observations']['readiness']['ready']is True and t['observations']['readiness']['handlerInvoked']is False and t['cdpEnabledBeforeFirstAppRequest']is True
  assert browser['tests'][0]['observations']['afterClick']=='NEXT_CLIENT_COUNT:1'
  assert browser['tests'][1]['observations']['value']=='browser-action'and browser['tests'][1]['observations']['actualFormPostObserved']is True and browser['tests'][1]['observations']['builtActionIdNotHardcoded']is True
  assert len(browser['actionPosts'])==1 and b'browser-action'in base64.b64decode(browser['actionPosts'][0]['bodyBase64'],validate=True)
  assert len(browser['trace'])==142 and[x['sequence']for x in browser['trace']]==list(range(1,143))
  assert len(browser['responseFinishedObservations'])==14 and all(x['error']is None for x in browser['responseFinishedObservations'])
  assert len(browser['bodyCaptures'])==10 and len(browser['assetBodies'])==9
  scripts={}
  for capture in browser['assetBodies']:
   assert capture['resourceType']=='script'and capture['sourceMatch']is True and capture['decodedBody']is not None and capture['wireBodySha256']is None
   raw=data[ref(capture['decodedBody'])];assert digest(raw)==dict(bytes=capture['decodedBytes'],sha256=capture['decodedSha256'])
   e=capture['expected'];assert digest(raw)=={k:e[k]for k in ['bytes','sha256']}
   r=appfiles['.next/'+e['path'].removeprefix('/_next/')];assert digest(raw)=={k:r[k]for k in ['bytes','sha256']}
   key=(capture['test'],e['path']);assert key not in scripts;scripts[key]=digest(raw)
  assert len(scripts)==9 and len({k[1]for k in scripts})==5
  posts=[x for x in browser['bodyCaptures']if x['method']=='POST'];assert len(posts)==1
  post=posts[0];assert post['status']==200 and post['decodedBody']is not None and'bodyError'not in post and post['wireBodySha256']is None
  raw=data[ref(post['decodedBody'])];assert digest(raw)==dict(bytes=post['decodedBytes'],sha256=post['decodedSha256'])and len(raw)==2963
  # Complete protocol JSON is retained. CDP and Playwright IDs are distinct;
  # timestamp namespaces are not converted or treated as transport wire bytes.
  events=browser['cdpEvents'];assert len(events)==expected_cdp
  allowed=['Network.requestWillBeSent','Network.responseReceived','Network.dataReceived','Network.loadingFinished','Network.loadingFailed','Page.navigatedWithinDocument','Page.frameNavigated']
  assert browser['cdpScope']['events']==allowed and all(x['event']in allowed and x['event']!='Network.loadingFailed'for x in events)
  for t in browser['tests']:
   own=[x for x in events if x['test']==t['id']];stats=t['cdpObserver'];assert[x['sequence']for x in own]==list(range(1,len(own)+1))
   assert stats==dict(events=len(own),payloadBytes=sum(x['payloadBytes']for x in own),stopped=False,eventsAfterStop=0,overflow=None)
   assert len(own)<=8000 and all(0<x['payloadBytes']<=262144 and type(x['payload'])is dict for x in own)and stats['payloadBytes']<=8388608
   assert[int(x['arrivalNs'])for x in own]==sorted(int(x['arrivalNs'])for x in own)
  reqs=[x for x in events if x['event']=='Network.requestWillBeSent'];assert len(browser['cdpCorrelations'])==len(reqs)==14
  for c in browser['cdpCorrelations']:
   e=next(x for x in reqs if x['test']==c['test']and x['sequence']==c['cdpSequence']);payload=e['payload']
   assert c['identityProved']is False and c['cdpRequestId']==payload['requestId']and c['cdpTimestamp']==payload['timestamp']and c['cdpArrivalNs']==e['arrivalNs']and c['url']==payload['request']['url']and c['method']==payload['request']['method']
   candidates=[dict(requestId=x['requestId'],arrivalNs=x['ns'])for x in browser['trace']if x['test']==c['test']and x['event']=='request'and x['url']==c['url']and x['method']==c['method']]
   assert c['playwrightCandidates']==candidates
  request=next(x for x in reqs if x['test']=='server-action'and x['payload']['request']['method']=='POST');pid=request['payload']['requestId'];frame=request['payload']['frameId'];loader=request['payload']['loaderId']
  actionevents=[x for x in events if x['test']=='server-action'];finish=next(x for x in actionevents if x['event']=='Network.loadingFinished'and x['payload']['requestId']==pid)
  history=next(x for x in actionevents if x['event']=='Page.navigatedWithinDocument'and x['payload']['url'].endswith('/action-result?value=browser-action'))
  assert history['payload']['navigationType']=='historyApi'and history['payload']['frameId']==frame and int(finish['arrivalNs'])<int(history['arrivalNs'])
  initial=next(x for x in actionevents if x['event']=='Page.frameNavigated'and x['payload']['frame']['id']==frame);assert initial['payload']['frame']['loaderId']==loader
  pwfinish=next(x for x in browser['trace']if x['test']=='server-action'and x['event']=='requestfinished'and x['requestId']==post['requestId'])
  body=next(x for x in browser['trace']if x['test']=='server-action'and x['event']=='response-body-captured'and x['requestId']==post['requestId'])
  assert int(pwfinish['ns'])<int(body['ns'])and int(history['arrivalNs'])<int(body['ns'])
  worker=client['browserArgv'][1];ref(dict(path=worker,**digest(data[origins[worker]])))
  return dict(httpPassed=24,cacheGeneration=[1,2],streamChunks=5,streamShell=0,streamReady=2,browserFunctionalPassed=2,strictBrowserPassed=True,strictBrowserErrors=0,cdpEvents=len(events),cdpEventCountsByTest={t['id']:t['cdpObserver']['events']for t in browser['tests']},cdpOverflow=False,loadingFailed=False,
              actionCdpRequestId=pid,actionFrameId=frame,actionLoaderId=loader,cdpLoadingFinishedArrivalNs=finish['arrivalNs'],historyNavigationArrivalNs=history['arrivalNs'],playwrightRequestFinishedNs=pwfinish['ns'],bodyCapturedNs=body['ns'],rscBody=post['decodedBody'],scriptHashes=scripts,worker=worker)
 native_summary=client_check(client,'runtime/client',81);stock_summary=client_check(stock,'stock',94)
 assert native_summary['scriptHashes']==stock_summary['scriptHashes']
 assert data[origins[native_summary['worker']]]==data[origins[stock_summary['worker']]],'identical browser/CDP worker bytes'
 native_summary.pop('scriptHashes');stock_summary.pop('scriptHashes')
 assert native_summary['rscBody']['sha256']!=stock_summary['rscBody']['sha256'],'opaque RSC bytes differ; no normalization'
 native=obj('inputs/native-metadata.json');assert all(native[k]==v and type(native[k])is type(v)for k,v in ra['metadataExpectedFixedValues'].items())
 assert native['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'and native['freshFrontendCompileRows']==1 and native['unchangedBaselineCompileDatabaseRows']==79
 guard=obj('inputs/full-world-guard.json');cg=obj('constructor-outer/world-guard.json');expectedWorld=dict(sourceIndex=ca['worldSourceIndex'],members=28,witFiles=8,exactFileAndDirectoryMembership=True,noSymlinkOrHardlinkAliases=True)
 assert guard['before']==guard['after']==cg['before']==cg['after']==expectedWorld and guard['unchanged']is True and guard['nativeInputsPreserved']is True and guard['authority']==rr['rootAuthority']
 return dict(schemaVersion=1,state='PAIRED_ACTUAL_NEXT_CDP_POSITIVE_DATA_REVIEW_PASSED_V1',verifiedEvidence=True,nativeActualPassed=True,stockActualPassed=True,native=native_summary,stock=stock_summary,
             component=rr['component'],engine=ca['engine'],nativeMetadata=ca['nativeMetadata'],nativeRuntimeResult=outer['result'],stockRuntimeResult=so['result'],
             standardImports=13,constructorThreeAndOuterRaw0=True,rawParentsClean=True,currentNativeAppReadback=capsule['currentAppReadback'],stockImmutableCopyFilesCurrent=2217,stockMutableOwnedCacheExcluded=True,
             retainedFiles=len(capsule['entries']),selectedOriginalDescriptors=capsule['currentOriginalsRehashedBeforeFinal'],sameObserverBytes=True,nineScriptBodiesMatchAcrossTrials=True,opaqueRscByteEqual=False,
             priorV5StrictFailureUnresolved=True,priorFailureRelabeled=False,causeOrReliabilityProved=False,physicalStoreIdentityOrNativeCleanupProved=False,performanceOrAdoptionProved=False,sourceAuthorRelationship='Reviewer authored earlier ALS/constructor tooling/pipe facade; separate actual DATA readback.',newTargetsInvoked=False,binariesSdkOrAppPayloadCopied=False)
if __name__=='__main__':print(json.dumps(main(),indent=2))
