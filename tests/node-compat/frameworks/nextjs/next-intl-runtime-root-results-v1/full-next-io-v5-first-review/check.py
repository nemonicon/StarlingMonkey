"""Portable actual V5 strict-failure DATA reader. No target, browser, engine or project imports."""
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
 assert rr['state']=='NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2' and rr['passed'] is False and rr['adoption'] is False
 assert rr['originalInputsPreserved'] is True and rr['readonlyAppPreserved'] is True
 assert rr['applicationCopy']=={'files':2218,'bytes':48808299,'byteIdentical':True,'independentInodes':True}
 plan=obj(ref(ra['plan']));rt,rs,n=terminal('runtime-outer',1);processes+=n
 assert rs['timeoutSeconds']==600 and rs['argv'][-1]==rr['rootAuthority']['path'] and rs['argv'][0]==plan['node']['path']
 assert Path(rs['argv'][1]).name=='deploy.mjs' and ref(dict(path=rs['argv'][1],**digest(data[origins[rs['argv'][1]]])))
 outer=obj('runtime-outer/observation.json');assert outer['result']==dict(path=rr['outputRoot']+'/result.json',**digest(data['runtime/result.json']))
 assert outer['rawExitCode']==1 and outer['ownedGroupsClean'] is True and outer['protectedInputsPreserved'] is True and outer['passed'] is False and outer['adoption'] is False
 assert outer['terminal']==dict(path=rr['outputRoot']+'-external-root/terminal.json',**digest(data['runtime-outer/terminal.json']))
 assert rr['server']['exit']=={'code':0,'signal':None,'error':None} and rr['server']['shutdownRequested'] and rr['server']['sigintSent'] and rr['server']['forcedCleanup'] is False
 assert rr['client']['exit']=={'code':1,'signal':None,'error':None}
 for owner in ['server','client']:
  for k in ['stdout','stderr']:ref(rr[owner][k])
 client=obj(ref(rr['client']['result']));assert client['passed'] is False and client['errors']==[] and client['transportErrors']==[]
 plan=obj(ref(ra['plan']));command=rr['server']['command'];assert command[0]==plan['wasmtime']['path'] and plan['wasmtime'] in capsule['externalReferences'] and command[-1]==rr['component']['path']
 assert command[1]=='serve' and command[command.index('--addr')+1]==rr['portLease']['address']+':'+str(rr['portLease']['port'])
 assert command[command.index('--max-instance-reuse-count')+1]=='128' and command[command.index('--idle-instance-timeout')+1]=='60s'
 assert command[command.index('-S')+1]=='cli=y,tcp=n,udp=n,allow-ip-name-lookup=n'
 assert client['origin']==rr['portLease']['origin']==rr['server']['readyOrigin'] and rr['portLease']['fallbackAllowed'] is False
 assert data['runtime/wasmtime.stderr.log']==('Serving HTTP on '+client['origin']+'/\n').encode()
 contract=obj('inputs/fixture-contract.json');assert len(contract['requests'])==23 and len(client['http'])==24
 assert [x['id'] for x in client['http'][:23]]==[x['id'] for x in contract['requests']];bodies={}
 for i,row in enumerate(client['http']):
  b=data['runtime/client/responses/'+row['id']+'.txt'];assert len(b)==row['bodyBytes'] and hashlib.sha256(b).hexdigest()==row['bodySha256'];text=b.decode();bodies[row['id']]=text
  assert row['passed'] is True and row.get('failures',[])==[]
  if i==23:assert row['id']=='server-action-submit' and row['status']==303 and row['headers']['location']=='/action-result?value=fixture-action';continue
  expected=contract['requests'][i];assert row['status']==expected['status']
  for value in expected.get('includes',[]):assert value in text
  if expected.get('location'):assert row['headers']['location']==expected['location']
  for k,v in expected.get('json',{}).items():assert json.loads(text)[k]==v
  for k,v in expected.get('responseHeaders',{}).items():assert row['headers'][k]==v
  for k,values in expected.get('responseHeaderIncludes',{}).items():
   for v in values:assert v in row['headers'][k]
  if expected.get('equalJsonTo'):assert text==bodies[expected['equalJsonTo']]
 before=json.loads(bodies['cache-first']);after=json.loads(bodies['cache-after-revalidate'])
 assert client['cacheInvalidation']=={'before':before,'after':after,'passed':True} and before['generation']==1 and after['generation']==2
 chunks=obj('runtime/client/stream-chunks.json');text='';shell=ready=-1
 for i,chunk in enumerate(chunks):
  b=base64.b64decode(chunk['base64'],validate=True);assert len(b)==chunk['bytes'];text+=b.decode()
  if shell<0 and 'NEXT_STREAM_SHELL' in text:shell=i
  if ready<0 and 'NEXT_STREAM_READY' in text:ready=i
 assert len(chunks)==5 and shell==0 and ready==2 and client['streaming']=={'chunks':5,'shellChunk':0,'readyChunk':2,'complete':True,'incrementalDeliveryObserved':True}
 browser=obj('runtime/client/browser/result.json');assert client['browser']==browser and browser['origin']==client['origin'] and client['browserExit']=={'code':1,'signal':None}
 assert [(x['id'],x['passed'],x['timedOut'])for x in browser['tests']]==[('client-counter',True,False),('server-action',True,False)]
 assert browser['functionalPassed']is True and browser['assetCapturePassed']is True and browser['browserErrorFree']is False and browser['passed']is False and browser['wasmBrowserRun']is None
 assert browser['perTestTimeoutMs']==20000 and browser['beforeCloseNetworkCompletionWait']is False
 stats={k:len(browser[k])for k in ['pageerrors','consoleerrors','failedrequests','errors','trace','responseFinishedObservations','bodyCaptures']}
 assert stats==dict(pageerrors=0,consoleerrors=0,failedrequests=1,errors=2,trace=136,responseFinishedObservations=13,bodyCaptures=10)
 assert [x['sequence']for x in browser['trace']]==list(range(1,137))
 failed=browser['failedrequests'][0];assert failed['failure']['errorText']=='net::ERR_ABORTED'and failed['phase']=='action-result-assert'and failed['method']=='POST'and failed['requestId']==7
 assert [x['stage']for x in browser['errors']]==['server-action-response-body','server-action-response-finished-rejected']
 assert 'No data found for resource with given identifier'in browser['errors'][0]['message']and'navigated away from'in browser['errors'][0]['message']and'has been closed'in browser['errors'][1]['message']
 for test in browser['tests']:
  ref(test['screenshot']);assert test['error']is None and test['observations']['readiness']['ready']is True and test['observations']['readiness']['handlerInvoked']is False
 assert browser['tests'][0]['observations']['afterClick']=='NEXT_CLIENT_COUNT:1'and browser['tests'][0]['observations']['hydratedClickObserved']is True
 assert browser['tests'][1]['observations']['actualFormPostObserved']is True and browser['tests'][1]['observations']['value']=='browser-action'and browser['tests'][1]['observations']['builtActionIdNotHardcoded']is True
 assert len(browser['actionPosts'])==1 and b'browser-action'in base64.b64decode(browser['actionPosts'][0]['bodyBase64'],validate=True)
 scripts=[x for x in browser['bodyCaptures']if x['resourceType']=='script'];assert scripts==browser['assetBodies']and len(scripts)==9
 app=obj('inputs/application-inputs.json');appfiles={x['path']:x for x in app['files']};scriptpins=set()
 for capture in scripts:
  assert capture['decodedBody']is not None and capture['sourceMatch']is True and capture['wireBodySha256']is None
  raw=data[ref(capture['decodedBody'])];assert digest(raw)==dict(bytes=capture['decodedBytes'],sha256=capture['decodedSha256'])
  expected=capture['expected'];assert digest(raw)=={k:expected[k]for k in ['bytes','sha256']}
  name=expected['path'].removeprefix('/_next/');source=appfiles['.next/'+name]
  assert digest(raw)=={k:source[k]for k in ['bytes','sha256']};scriptpins.add(expected['path'])
 assert len(scriptpins)==5
 post=[x for x in browser['bodyCaptures']if x['method']=='POST'];assert len(post)==1 and post[0]['requestId']==7 and post[0]['status']==200 and post[0]['decodedBody']is None and'No data found'in post[0]['bodyError']['message']
 assert post[0]['encodedSizes']['responseBodySize']==0 and post[0]['wireBodySha256']is None
 tr=browser['trace'];nav=next(x for x in tr if x['sequence']==122);abort=next(x for x in tr if x['sequence']==124);unavailable=next(x for x in tr if x['sequence']==125);close=next(x for x in tr if x['sequence']==131);rejected=next(x for x in tr if x['sequence']==133)
 assert nav['event']=='main-frame-navigated'and abort['event']=='requestfailed'and unavailable['event']=='response-body-unavailable'and close['phase']=='context-close-start'and rejected['event']=='response.finished-rejected'
 assert int(nav['ns'])<int(abort['ns'])<int(unavailable['ns'])<int(close['ns'])<int(rejected['ns'])
 native=obj('inputs/native-metadata.json');assert native['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'
 assert all(native[k]==v and type(native[k])is type(v)for k,v in ra['metadataExpectedFixedValues'].items())
 assert native['freshFrontendCompileRows']==1 and native['baselineCompileDatabaseRows']==80 and native['unchangedBaselineCompileDatabaseRows']==79 and native['baselineSeparateEmbeddingRows']==1 and native['oldMetadataProjected']is False
 guard=obj('inputs/full-world-guard.json');cg=obj('constructor-outer/world-guard.json')
 expectedWorld=dict(sourceIndex=ca['worldSourceIndex'],members=28,witFiles=8,exactFileAndDirectoryMembership=True,noSymlinkOrHardlinkAliases=True)
 assert cg['before']==cg['after']==expectedWorld and cg['unchanged']is True
 assert guard['before']==guard['after']==expectedWorld and guard['unchanged']is True and guard['nativeInputsPreserved']is True and guard['authority']==rr['rootAuthority']
 assert ca['worldSourceIndex']==ra['worldSourceIndex']
 idx=obj(ref(ca['worldSourceIndex']));wits=[dict(x,path=str(Path(ca['worldSourceIndex']['path']).parent/x['path']))for x in idx['files']if x['path'].endswith('.wit')]
 assert len(idx['files'])==28 and len(wits)==8 and all(x in ca['newSourceEvidence']and x in ra['worldInputs']for x in wits)
 for x in wits:ref(x)
 assert capsule['currentAppReadback']['currentBeforeAndFinalAppHashesMatch']is True
 return dict(schemaVersion=1,state='ACTUAL_NEXT_FULL_IO_V5_STRICT_FAILURE_DATA_REVIEW_PASSED_V1',verifiedEvidence=True,constructorPassed=True,constructorInnerRawExitCodes=[0,0,0],constructorOuterRawExitCode=0,
  runtimeOriginalPassed=False,runtimeOuterRawExitCode=1,wasmtimeOwnedGracefulExitCode=0,clientExitCode=1,
  httpPassed=24,httpTotal=24,fullBaseContractAndActionPostIndependentlyChecked=True,cachePassed=True,cacheGeneration=[1,2],strictStreamingPassed=True,streamChunks=5,
  browserFunctionalPassed=2,browserFunctionalTotal=2,browserOriginalPassed=False,browserStats=stats,browserFailuresRetained=True,
  decodedScriptsMatched=9,distinctScriptPins=5,postRscBodyAvailable=False,postAbortedBeforeExplicitContextClose=True,bodyUnavailableAfterNavigationBeforeContextClose=True,responseFinishedRejectedAfterContextClose=True,causeOrBenignClassificationProved=False,
  component=rr['component'],inputEntry=rr['inputEntry'],inputSourceIndex=rr['inputSourceIndex'],constructionResult=ra['constructionResult'],runtimeResult=outer['result'],runtimeRootAuthority=rr['rootAuthority'],engine=ca['engine'],nativeMetadata=ca['nativeMetadata'],standardInterfaces=13,externalPreview1OrCustomImports=False,observedProcessRecords=processes,
  currentAppReadback=capsule['currentAppReadback'],sourceAuthorRelationship='Reviewer authored earlier ALS, constructor tooling and signal-aware pipe facade; this separate actual DATA readback is not independent authorship of those Sources.',
  actualWasmtimeTargetEstablishedByParentCommandComponentOriginAndOwnedTerminal=True,genericBrowserRuntimeFlagPreservedNone=True,
  allStagesOrFullNextAccepted=False,sameInstanceIdentityProved=False,snapshotResetOrSecurityProved=False,newTargetsInvokedByReader=False,bigBinaryOrAppPayloadsCopied=False,rawBrowserTraceScreenshotsAndChunksRetained=True,
  retainedFiles=len(capsule['entries']),selectedOriginalDescriptors=capsule['currentOriginalsRehashedBeforeFinal'],
  scope='Original operation guards plus current finite Source/artifact/app readbacks; strict browser failures remain failures. Timeline does not prove cause. Physical app modes do not prove read-only WASI preopen rights.')
if __name__=='__main__':print(json.dumps(main(),indent=2))
