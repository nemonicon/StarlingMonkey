"""Portable first/repeat hydration V5 DATA read; no engine/browser/process calls."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, re, tarfile
HERE=Path(__file__).resolve().parent
SELECTED={'wasi:cli/environment@0.2.10','wasi:cli/stdout@0.2.10','wasi:cli/stderr@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:random/random@0.2.10','wasi:filesystem/types@0.2.10','wasi:filesystem/preopens@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:http/types@0.2.10','wasi:http/outgoing-handler@0.2.10'}
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
 if (HERE/'index.json').exists():
  rows=json.loads((HERE/'index.json').read_text())['files']
  assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}=={r['path'] for r in rows}|{'index.json'}
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
 for r in capsule['sourceFamilies']:
  index=obj(ref(r));base=Path(r['path']).parent
  for row in index['files']:ref({**row,'path':str(base/row['path'])})
 cr=obj('constructor/result.json');audit=obj('constructor/component-audit.json');prior=obj('prior-constructor-review/review.json')
 assert capsule['priorConstructorReviewIndex']['sha256']=='03a56dd3139b84e1490033e5ca8282af67f4acd7da3125d45e2c799b9762d289'
 assert capsule['priorConstructorReview']['sha256']=='07e47d0f709d928cc70017e6bbb52c48d3acad26b91f82497b6f41acf7682c05'
 ref(capsule['priorConstructorReview']);ref(capsule['priorConstructorReviewIndex'])
 pi=obj('prior-constructor-review/index.json');assert digest(data['prior-constructor-review/review.json'])=={k:next(r for r in pi['files'] if r['path']=='review.json')[k] for k in ['bytes','sha256']}
 assert prior['verifiedEvidence'] and prior['constructorPassed'] and prior['constructorInnerRawExitCodes']==[0,0,0] and prior['constructorOuterRawExitCode']==0
 assert prior['runtimeOriginalPassed'] is False and prior['httpPassed']==24 and prior['browserOriginalPassed'] is False
 assert cr['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2' and cr['passed'] is True and cr['error'] is None and cr['finalProtection']=={'unchanged':True}
 assert cr['artifacts']['component']==prior['component'] and cr['artifacts']['inputEntry']==prior['inputEntry'] and cr['artifacts']['inputSourceIndex']==prior['inputSourceIndex']
 assert cr['artifacts']['engine']==prior['engine'] and cr['artifacts']['nativeMetadata']==prior['nativeMetadata']
 for k in ['metadataFrameProjected','ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted']:assert cr[k] is False
 assert audit['state']=='NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1' and audit['passed'] is True and audit['component']==cr['artifacts']['component']
 assert len(audit['emittedImports'])==13 and set(audit['emittedImports'])==set(audit['selectedInterfaces'])==SELECTED and audit['exports']==['wasi:http/incoming-handler@0.2.10']
 assert audit['allEmittedVersion']=='0.2.10' and audit['noExternalPreview1OrCustomImports'] is True and audit['unusedSelectedInterfaces']==[]
 wit=data['constructor/component-wit/stdout.log'].decode();world=wit.split('world root {',1)[1].split('}',1)[0]
 assert set(re.findall(r'^  import ([^;]+);$',world,re.M))==SELECTED and re.findall(r'^  export ([^;]+);$',world,re.M)==audit['exports']
 imports=obj('constructor/api-return/returned-imports.json');assert len(imports)==131 and {r[0] for r in imports}==SELECTED
 def props(x):return {r['key']['string']:r['value'] for r in x['properties']}
 shape=obj('constructor/api-return/returned-own-shape.json');assert shape['type']=='object';fields=props(shape)
 assert set(fields)=={'component','imports','debug'} and fields['debug']=={'type':'undefined'}
 v=fields['component'];assert v['type']=='Uint8Array' and v['file']==cr['artifacts']['component'] and v['sha256']==v['file']['sha256'] and v['byteLength']==v['file']['bytes']
 array=props(fields['imports']);assert array['length']=={'type':'number','value':'131'} and [[props(array[str(i)])[str(j)]['value'] for j in range(2)] for i in range(131)]==imports
 assert [c['rawExitCode'] for c in cr['commands']]==[0,0,0] and all(c['clean'] for c in cr['commands'])
 pins=obj('sources/browser-hydration-candidate-v1/asset-pins.json')['assets'];assert len(pins)==5
 pinned={p['path']:{k:p[k] for k in ['path','sha256','bytes']} for p in pins}
 contract=obj('inputs/fixture-contract.json');assert len(contract['requests'])==23
 assert [r['label'] for r in capsule['runs']]==['first','repeat'];summaries=[];hostPids=[];originsSeen=[]
 for run in capsule['runs']:
  label=run['label'];prefix=label+'/';rr=obj(prefix+'runtime/result.json');ra=obj(prefix+'authority/runtime.json');client=obj(prefix+'runtime/client/result.json');browser=obj(prefix+'runtime/client/browser/result.json')
  ref(run['runtimeResult']);ref(run['rootAuthority']);assert rr['rootAuthority']==run['rootAuthority']
  assert rr['state']=='NEXT_WASMTIME_DEPLOYMENT_CONTRACTS_PASSED_UNREVIEWED_V2' and rr['passed'] is True and rr['contractsPassed'] is True and rr['adoption'] is False and rr['errors']==[]
  assert ra['state']=='ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2'
  for k in ['component','componentAudit','inputEntry','inputSourceIndex']:assert rr[k]==ra[k]==cr['artifacts'][k]
  assert rr['constructionResult']==ra['constructionResult']==prior['constructionResult'] and ra['constructionCallerIndex']==cr['callerIndex']
  assert rr['sourceIndex']==ra['sourceIndex'] and rr['sourceIndex']['sha256']=='dd05c1774fbeba27320536e34aad42848b034373c07e0ed74e403e983ac441d0'
  for r in [ra['plan'],rr['sourceIndex'],rr['inputEntry'],rr['inputSourceIndex']]:ref(r)
  plan=obj(ref(ra['plan']));assert ra['localhostServeAllowed'] and ra['actualNextGuestAllowed'] and ra['browserAllowed']
  assert all(ra[k] is False for k in ['compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed'])
  t=obj(prefix+'runtime-outer/terminal.json');s=obj(prefix+'runtime-outer/started.json');outer=obj(prefix+'runtime-outer/observation.json')
  assert t['rawExitCode']==0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
  assert all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids']) and all(g['alive'] is False for g in t['finalGroups'])
  assert s['authority']==t['authority']==rr['rootAuthority'] and s['pid']==t['pid'] and s['timeoutSeconds']==600
  assert s['argv']==[plan['node']['path'],str(Path(rr['sourceIndex']['path']).parent/'deploy.mjs'),rr['rootAuthority']['path']]
  for k in ['authority','stdout','stderr']:ref(t[k])
  events=[obj(n) for n in sorted(data) if n.startswith(prefix+'runtime-outer/owned-')]
  assert [e['sequence'] for e in events]==list(range(len(events))) and [e['process'] for e in events]==t['observedProcesses']
  assert outer['result']==run['runtimeResult'] and outer['rawExitCode']==0 and outer['passed'] and outer['ownedGroupsClean'] and outer['protectedInputsPreserved'] and not outer['adoption']
  assert outer['terminal']==dict(path=rr['outputRoot']+'-external-root/terminal.json',**digest(data[prefix+'runtime-outer/terminal.json']))
  assert json.loads(data[prefix+'runtime-outer/stdout.log'])=={'state':rr['state'],'passed':True,'errors':[]}
  assert rr['originalInputsPreserved'] is True and rr['readonlyAppPreserved'] is True and rr['applicationCopy']=={'files':2218,'bytes':48808299,'byteIdentical':True,'independentInodes':True}
  assert rr['server']['exit']=={'code':0,'signal':None,'error':None} and rr['server']['sigintSent'] and rr['server']['shutdownRequested'] and not rr['server']['forcedCleanup']
  assert rr['client']['exit']=={'code':0,'signal':None,'error':None}
  for owner in ['server','client']:
   for stream in ['stdout','stderr']:ref(rr[owner][stream])
  assert ref(rr['client']['result'])==prefix+'runtime/client/result.json'
  command=rr['server']['command'];assert command[0]==plan['wasmtime']['path'] and plan['wasmtime'] in capsule['externalReferences'] and command[1]=='serve' and command[-1]==rr['component']['path']
  assert command[command.index('--max-instance-reuse-count')+1]=='128' and command[command.index('--idle-instance-timeout')+1]=='60s' and command[command.index('-S')+1]=='cli=y,tcp=n,udp=n,allow-ip-name-lookup=n'
  assert command[command.index('--addr')+1]==rr['portLease']['address']+':'+str(rr['portLease']['port'])
  assert client['origin']==browser['origin']==rr['portLease']['origin']==rr['server']['readyOrigin'] and rr['portLease']['fallbackAllowed'] is False
  assert data[prefix+'runtime/wasmtime.stderr.log']==('Serving HTTP on '+client['origin']+'/\n').encode()
  assert client['passed'] is True and client['errors']==[] and client['transportErrors']==[] and len(client['http'])==24
  assert [r['id'] for r in client['http'][:23]]==[r['id'] for r in contract['requests']];bodies={}
  for i,row in enumerate(client['http']):
   b=data[prefix+'runtime/client/responses/'+row['id']+'.txt'];assert digest(b)==dict(bytes=row['bodyBytes'],sha256=row['bodySha256']);text=b.decode();bodies[row['id']]=text
   assert row['passed'] is True and row.get('failures',[])==[]
   if i==23:assert row['id']=='server-action-submit' and row['status']==303 and row['headers']['location']=='/action-result?value=fixture-action';continue
   expected=contract['requests'][i];assert row['status']==expected['status']
   for value in expected.get('includes',[]):assert value in text
   if expected.get('location'):assert row['headers']['location']==expected['location']
   for k,v in expected.get('json',{}).items():assert json.loads(text)[k]==v
   for k,v in expected.get('responseHeaders',{}).items():assert row['headers'][k]==v
   for k,values in expected.get('responseHeaderIncludes',{}).items():
    for value in values:assert value in row['headers'][k]
   if expected.get('equalJsonTo'):assert text==bodies[expected['equalJsonTo']]
  before=json.loads(bodies['cache-first']);after=json.loads(bodies['cache-after-revalidate'])
  assert client['cacheInvalidation']=={'before':before,'after':after,'passed':True} and before['generation']==1 and after['generation']==2
  chunks=obj(prefix+'runtime/client/stream-chunks.json');text='';shell=ready=-1
  for i,c in enumerate(chunks):
   b=base64.b64decode(c['base64'],validate=True);assert len(b)==c['bytes'];text+=b.decode()
   if shell<0 and 'NEXT_STREAM_SHELL' in text:shell=i
   if ready<0 and 'NEXT_STREAM_READY' in text:ready=i
  assert len(chunks)==5 and shell==0 and ready==2 and client['streaming']=={'chunks':5,'shellChunk':0,'readyChunk':2,'complete':True,'incrementalDeliveryObserved':True}
  assert client['browser']==browser and client['browserExit']=={'code':0,'signal':None}
  assert [(r['id'],r['passed'],r['timedOut']) for r in browser['tests']]==[('client-counter',True,False),('server-action',True,False)]
  assert all(browser[k] is True for k in ['functionalPassed','browserErrorFree','assetCapturePassed','passed','browserClosed','ephemeralContexts'])
  assert all(browser[k]==[] for k in ['pageerrors','consoleerrors','failedrequests','errors']) and browser['wasmBrowserRun'] is None and browser['userProfileUsed'] is False and browser['perTestTimeoutMs']==20000
  assert [x['sequence'] for x in browser['trace']]==list(range(1,137)) and len(browser['responseHeaders'])==len(browser['responseFinishedObservations'])==14
  assert all(x['error'] is None for x in browser['responseFinishedObservations'])
  assert len(browser['bodyCaptures'])==10 and len(browser['assetBodies'])==9
  captures={(x['test'],x['requestId']):x for x in browser['bodyCaptures']};assert len(captures)==10
  assets={(x['test'],x['requestId']):x for x in browser['assetBodies']};assert len(assets)==9
  headers={(x['test'],x['requestId']):x for x in browser['responseHeaders']};assert len(headers)==14
  for key,c in captures.items():
   b=data[ref(c['decodedBody'])];assert digest(b)==dict(bytes=c['decodedBytes'],sha256=c['decodedSha256'])
   assert c['status']==200 and c['wireBodySha256'] is None and 'decoded' in c['wireBodyCapture']
   assert type(c['encodedSizes']['responseBodySize']) is int and c['encodedSizes']['responseBodySize']>=0
   assert headers[key]['status']==c['status'] and headers[key]['url']==c['url']
   if key in assets:
    assert c==assets[key] and c['sourceMatch'] is True and c['expected']==pinned[c['expected']['path']] and digest(b)=={k:c['expected'][k] for k in ['bytes','sha256']}
  assert {x['expected']['path'] for x in browser['assetBodies'] if x['test']=='client-counter'}==set(pinned)
  assert {x['expected']['path'] for x in browser['assetBodies'] if x['test']=='server-action'}==set(pinned)-{'/_next/static/chunks/app/client/page-1d3eef49152dd249.js'}
  unpinned=[x for k,x in captures.items() if k not in assets];assert len(unpinned)==1 and unpinned[0]['method']=='POST' and unpinned[0]['url']==client['origin']+'/actions' and unpinned[0]['decodedBytes']==2963
  tests={x['id']:x for x in browser['tests']};counter=tests['client-counter'];action=tests['server-action']
  assert counter['observations']['initial']=='NEXT_CLIENT_COUNT:0' and counter['observations']['afterClick']=='NEXT_CLIENT_COUNT:1' and counter['observations']['hydratedClickObserved'] is True
  assert action['observations']['actualFormPostObserved'] is True and action['observations']['builtActionIdNotHardcoded'] is True and action['observations']['value']=='browser-action'
  for test in browser['tests']:
   assert test['error'] is None and test['captureDrainBeforeCloseComplete'] is True and test['elapsedMs']<20000;ref(test['screenshot'])
   readiness=test['observations']['readiness'];assert readiness['ready'] is True and readiness['handlerInvoked'] is False and readiness['readyState']=='complete'
   assert all(snapshot['value']['handlerInvoked'] is False for snapshot in test['domSnapshots'])
  assert len(browser['actionPosts'])==1 and b'browser-action' in base64.b64decode(browser['actionPosts'][0]['bodyBase64'],validate=True)
  assert client['browserArgv'][1]==str(Path(next(r['path'] for r in capsule['sourceFamilies'] if '/browser-hydration-candidate-v1/' in r['path'])).parent/'browser-check.mjs')
  scriptAssets=[dict(test=x['test'],path=x['expected']['path'],decodedSha256=x['decodedSha256'],decodedBytes=x['decodedBytes'],encodedResponseBodyBytes=x['encodedSizes']['responseBodySize']) for x in browser['assetBodies']]
  summaries.append(dict(run=label,originalPassed=True,runtimeResult=run['runtimeResult'],rootAuthority=run['rootAuthority'],outerRawExitCode=0,ownedGroupsClean=True,wasmtimeGracefulExitCode=0,clientExitCode=0,httpPassed=24,httpTotal=24,cacheGeneration=[1,2],strictStreamChunks=5,shellChunk=0,readyChunk=2,browserPassed=2,browserTotal=2,strictBrowserErrors=dict(page=0,console=0,requests=0,collector=0),browserTraceEvents=136,responseFinishedObservations=14,decodedBodyCaptures=10,pinnedScriptFetches=9,uniquePinnedScripts=5,scriptAssets=scriptAssets,actionResponse=dict(decodedBody=unpinned[0]['decodedBody'],encodedSizes=unpinned[0]['encodedSizes']),wireBodyHashesAvailable=False,sourceInputsAndPhysicalReadonlyCopyPreserved=True,observedOwnedProcessRecords=len(events)))
  hostPids.append(rr['server']['pid']);originsSeen.append(client['origin'])
 assert len(set(hostPids))==len(set(originsSeen))==2
 return dict(schemaVersion=1,state='ACTUAL_NEXT_NATIVE_HYDRATION_V5_FIRST_AND_REPEAT_DATA_REVIEW_PASSED_V1',verifiedEvidence=True,runs=summaries,sourceIndexSha256='dd05c1774fbeba27320536e34aad42848b034373c07e0ed74e403e983ac441d0',browserSourceIndexSha256='b7f4ff002ea5732d1ee4a3b85359044bf0e2d37eb71d613884a7ba94a19aca5f',inputEntry=cr['artifacts']['inputEntry'],inputSourceIndex=cr['artifacts']['inputSourceIndex'],component=cr['artifacts']['component'],engine=cr['artifacts']['engine'],nativeMetadata=cr['artifacts']['nativeMetadata'],standardInterfaces=13,externalPreview1OrCustomImports=False,reusedConstructorEvidence=prior['constructionResult'],priorV4RuntimeRemainsFailed=True,allRecordedContractStagesPassedInEachRun=True,currentApplicationReadbacks=capsule['currentAppReadbacks'],sameInstanceAcrossRequestsProved=False,snapshotResetOrSecurityProved=False,publicAdoptionGranted=False,newTargetsInvokedByReader=False,bigBinaryOrAppTreeCopied=False,decodedNetworkBodiesAndScreenshotsRetained=True,
  sourceAuthorRelationship='Reviewer authored AsyncResource and FS option facades; this is actual retained DATA review, not independent Source certification.',scope='Two separate owned stock Wasmtime executions of the same experimental component and immutable fixture app. Browser decoded-body SHA and encoded sizes are distinct; no wire hashes are inferred. Physical readonly app modes do not establish WASI readonly preopen rights. No general Node conformance, warm-instance/reset safety, cost, production security, external deployment or public admission follows.')
if __name__=='__main__':print(json.dumps(main(),indent=2))
