"""Portable constructor/context runtime DATA reader; no target or project imports."""
from pathlib import Path,PurePosixPath
import hashlib,io,json,re,tarfile
HERE=Path(__file__).resolve().parent
IDS=['fresh-branches','cross-owner-promises','shared-readiness','disable-captures','normal-timer-abort']
SELECTED={'wasi:cli/environment@0.2.10','wasi:cli/stdout@0.2.10','wasi:cli/stderr@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:random/random@0.2.10','wasi:filesystem/types@0.2.10','wasi:filesystem/preopens@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:http/types@0.2.10','wasi:http/outgoing-handler@0.2.10'}
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def projection(result):
 assert set(result)=={'schemaVersion','suite','call','boundaryMode','records','passed','logicalBranchesOnly','actualHttpResourceConcurrencyProved','nativeOwnerIdentityOrTeardownProved','resetOrGcWorkload','peakPlannedWaits'}
 assert result['schemaVersion']==1 and result['suite']=='CONTEXT_INTERLEAVING_FIVE_CONTROLS_V1' and result['passed'] is True
 assert type(result['call']) is int and result['boundaryMode'] in ['node-public-empty-store-projection','actual-native-private-boundaries']
 assert [r['id'] for r in result['records']]==IDS
 out=[]
 for record in result['records']:
  assert set(record)=={'id','passed','assertions','events','requiredEdges'}
  assert all(set(a)=={'id','passed'} and isinstance(a['id'],str) for a in record['assertions']) and all(isinstance(e,str) for e in record['events'])
  assert record['passed'] is True and all(a['passed'] is True for a in record['assertions'])
  assert len({a['id'] for a in record['assertions']})==len(record['assertions']) and len(set(record['events']))==len(record['events'])
  for a,b in record['requiredEdges']:assert a in record['events'] and b in record['events'] and record['events'].index(a)<record['events'].index(b)
  out.append(dict(id=record['id'],assertions=sorted(record['assertions'],key=lambda a:a['id']),eventIds=sorted(record['events']),requiredEdges=sorted(record['requiredEdges'],key=lambda x:json.dumps(x,separators=(',',':')))))
 return dict(call=result['call'],records=out)
def main():
 if (HERE/'index.json').exists():
  index=json.loads((HERE/'index.json').read_text());rows=index['files']
  assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}=={r['path'] for r in rows}|{'index.json'}
  for r in rows:assert digest((HERE/r['path']).read_bytes())=={k:r[k] for k in ['bytes','sha256']}
 capsule=json.loads((HERE/'capsule.json').read_text());assert digest((HERE/'data.tar.gz').read_bytes())=={k:capsule['bundle'][k] for k in ['bytes','sha256']}
 expected={r['path']:r for r in capsule['entries']};data={};origins={}
 with tarfile.open(HERE/'data.tar.gz','r:gz') as tar:
  members=tar.getmembers();assert len(members)==len(expected)==len(capsule['entries'])
  for m in members:
   p=PurePosixPath(m.name);assert m.isfile() and not p.is_absolute() and '..' not in p.parts and m.name in expected and m.name not in data
   b=tar.extractfile(m).read();r=expected[m.name];assert digest(b)=={k:r['original'][k] for k in ['bytes','sha256']}
   if r['kind']=='utf8':b.decode('utf8')
   else:assert r['kind']=='gzip' and b.startswith(b'\x1f\x8b')
   data[m.name]=b;assert r['original']['path'] not in origins;origins[r['original']['path']]=m.name
 assert set(data)==set(expected)
 def obj(n):return json.loads(data[n])
 def ref(r):
  n=origins[r['path']];assert digest(data[n])=={k:r[k] for k in ['bytes','sha256']};return n
 def terminal(prefix,code):
  t=obj(prefix+'/terminal.json');s=obj(prefix+'/started.json');assert type(t['rawExitCode']) is int and t['rawExitCode']==code
  assert t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
  assert all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids']) and all(g['alive'] is False for g in t['finalGroups'])
  assert t['pid']==s['pid'] and t['authority']==s['authority']
  for k in ['authority','stdout','stderr']:ref(t[k])
  events=[obj(n) for n in sorted(data) if n.startswith(prefix+'/owned-')]
  assert [e['sequence'] for e in events]==list(range(len(events))) and [e['process'] for e in events]==t['observedProcesses']
  return t,s,len(events)
 for r in capsule['sourceFamilies']:
  index=obj(ref(r));base=Path(r['path']).parent
  for item in index['files']:ref({**item,'path':str(base/item['path'])})
 cr=obj('constructor/result.json');ca=obj('authority/constructor.json');audit=obj('constructor/component-audit.json')
 assert cr['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2' and cr['passed'] is True and cr['entryMode']=='context-interleaving'
 assert cr['error'] is None and cr['finalProtection']=={'unchanged':True} and cr['callerIndex']==ca['callerIndex']
 assert cr['artifacts']['inputSourceIndex']['sha256']=='1885f096554597f5ec47c653012468e4a1d2bf255c563d858b9200da3889cf9c'
 assert cr['artifacts']['inputEntry']['sha256']=='63afd3bd32b12820e609aa4693a2bc56379712175c6f6b819224bd8f972195ec'
 for k in ['metadataFrameProjected','ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted']:assert cr[k] is False
 for k in ['rootAuthority','callerIndex','plan']:ref(cr[k])
 for k in ['inputEntry','inputSourceIndex','returnedImports','returnedOwnShape','componentAudit']:ref(cr['artifacts'][k])
 metadata=obj('constructor/api-return/native-metadata-input.json');assert metadata['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'
 assert digest(data['constructor/api-return/native-metadata-input.json'])=={k:cr['artifacts']['nativeMetadata'][k] for k in ['bytes','sha256']}
 assert cr['artifacts']['engine']==ca['engine'] and cr['artifacts']['nativeMetadata']==ca['nativeMetadata']
 assert cr['artifacts']['component']['sha256']=='938e69130063b1d5d4b0f558882932c9598b5ebf28f9d6a2afcc08a18c9ca32b'
 assert [c['label'] for c in cr['commands']]==['componentize-init','component-validate','component-wit'];processes=0
 for c in cr['commands']:
  assert c['rawExitCode']==0 and c['clean'] is True;t,s,n=terminal('constructor/'+c['label'],0);processes+=n
  assert s['argv']==c['argv'] and s['timeoutSeconds']==c['capSeconds']
  for k in ['terminal','stdout','stderr']:ref(c[k])
  assert c['stdout']==t['stdout'] and c['stderr']==t['stderr'] and c['stderr']['bytes']==0
 ct,cs,n=terminal('constructor-outer',0);processes+=n;assert cs['timeoutSeconds']==2400
 frames=[json.loads(line) for line in data['constructor-outer/stdout.log'].splitlines()];assert len(frames)==4
 assert frames[-1]=={'result':capsule['actualConstructorResult'],'passed':True,'error':None}
 assert [(x['pid'],x['timeoutSeconds']) for x in frames[:3]]==[(obj('constructor/'+c['label']+'/started.json')['pid'],c['capSeconds']) for c in cr['commands']]
 world=obj('constructor-outer/world-guard.json');assert world['unchanged'] is True and world['before']==world['after']
 assert world['before']==dict(sourceIndex=capsule['worldSourceIndex'],members=28,witFiles=8,exactFileAndDirectoryMembership=True,noSymlinkOrHardlinkAliases=True)
 worldIndex=obj(ref(capsule['worldSourceIndex']));assert len(worldIndex['files'])==28
 for r in worldIndex['files']:
  if r['path'].endswith('.wit'):ref({**r,'path':str(Path(capsule['worldSourceIndex']['path']).parent/r['path'])})
 directory=str(Path(capsule['worldSourceIndex']['path']).parent)
 initial=obj('constructor/api-return/tool-preopens-initial.json');configured=obj('constructor/api-return/tool-preopens-configured.json');final=obj('constructor/api-return/tool-preopens-final.json')
 assert initial=={'count':0,'virtualNames':[]} and configured['count']==1 and configured['virtualNames']==[directory] and configured['hostMappings']=={directory:directory}
 assert final=={'count':1,'virtualNames':[directory],'mountConfigured':True} and configured['module'] in capsule['externalReferences']
 options=obj('constructor/api-return/requested-options.json');assert options['engine']==cr['artifacts']['engine']['path'] and options['preview2Adapter']==cr['artifacts']['adapter']['path'] and options['witPath']==directory and options['worldName']=='next-http'
 assert options['disableFeatures']==['fetch-event'] and options['enableFeatures']==[] and options['enableAot'] is False and options['env']=={}
 assert options['debug']=={'bindings':False,'binary':False,'wizerLogging':False} and all(options[k] is False for k in ['debugBindings','debugBuild','enableWizerLogging'])
 assert audit['state']=='NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1' and audit['passed'] is True and audit['component']==cr['artifacts']['component']
 assert len(audit['emittedImports'])==13 and set(audit['emittedImports'])==set(audit['selectedInterfaces'])==SELECTED and audit['exports']==['wasi:http/incoming-handler@0.2.10']
 assert audit['allEmittedVersion']=='0.2.10' and audit['noExternalPreview1OrCustomImports'] and audit['unusedSelectedInterfaces']==[]
 wit=data['constructor/component-wit/stdout.log'].decode();worldText=wit.split('world root {',1)[1].split('}',1)[0]
 assert set(re.findall(r'^  import ([^;]+);$',worldText,re.M))==SELECTED and re.findall(r'^  export ([^;]+);$',worldText,re.M)==audit['exports']
 imports=obj('constructor/api-return/returned-imports.json');assert len(imports)==131 and {r[0] for r in imports}==SELECTED and all(len(r)==2 and all(type(x) is str for x in r) for r in imports)
 def props(x):return {p['key']['string']:p['value'] for p in x['properties']}
 shape=obj('constructor/api-return/returned-own-shape.json');assert shape['type']=='object';fields=props(shape)
 assert set(fields)=={'component','imports','debug'} and fields['debug']=={'type':'undefined'}
 v=fields['component'];assert v['type']=='Uint8Array' and v['file']==cr['artifacts']['component'] and v['sha256']==v['file']['sha256'] and v['byteLength']==v['file']['bytes']
 pairs=props(fields['imports']);assert pairs['length']=={'type':'number','value':'131'} and [[props(pairs[str(i)])[str(j)]['value'] for j in range(2)] for i in range(131)]==imports
 source='sources/context-interleaving-candidate-v1/'
 host=obj(source+'host-check-results.json');oracle=[json.loads(line) for line in data[source+'node-oracle.stdout.jsonl'].splitlines()]
 assert host['passed'] is True and host['hostOnly'] is True and host['sourceProtectionPassed'] is True and len(oracle)==7 and oracle[-1]==host['summary']
 assert oracle[-1]['collections']==6 and oracle[-1]['controlsPerCollection']==5 and oracle[-1]['nativeBoundaryParityClaimed'] is False and oracle[-1]['guestOrEngineExecuted'] is False
 projections=[]
 for i,frame in enumerate(oracle[:-1]):
  assert set(frame)=={'kind','variant','call','observed'} and frame['kind']=='whole-collection'
  assert frame['variant']==('node-original' if i<3 else 'node-sealed-facade') and frame['call']==i%3+1
  assert frame['observed']['boundaryMode']=='node-public-empty-store-projection' and sum(len(r['assertions']) for r in frame['observed']['records'])==153
  projections.append(projection(frame['observed']))
 assert projections[:3]==projections[3:]
 # The monitored host oracle remains separate from ordinary native responses.
 innerIndex=obj(source+'host-raw-index.json');assert digest(data[source+'host-raw.tar.gz'])=={k:innerIndex['bundle'][k] for k in ['bytes','sha256']}
 innerRows={r['path']:r for r in innerIndex['files']};inner={};innerOrigins={r['originalPath']:r['path'] for r in innerIndex['files']}
 with tarfile.open(fileobj=io.BytesIO(data[source+'host-raw.tar.gz']),mode='r:gz') as archive:
  members=archive.getmembers();assert len(members)==len(innerRows)
  for m in members:
   p=PurePosixPath(m.name);assert m.isfile() and not p.is_absolute() and '..' not in p.parts and m.name in innerRows and m.name not in inner
   b=archive.extractfile(m).read();assert digest(b)=={k:innerRows[m.name][k] for k in ['bytes','sha256']};inner[m.name]=b
 assert inner['node-oracle/stdout.log']==data[source+'node-oracle.stdout.jsonl']
 for phase in host['phases']:
  t=json.loads(inner[phase['name']+'/terminal.json']);s=json.loads(inner[phase['name']+'/started.json'])
  assert t['rawExitCode']==0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
  assert all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
  assert s['timeoutSeconds']==120 and s['argv']==phase['argv'] and s['pid']==t['pid']
 rr=obj('runtime/result.json');ra=obj('authority/runtime.json');outer=obj('runtime-outer/observation.json')
 assert ra['state']=='ROOT_CONTEXT_INTERLEAVING_HTTP_PROBE_AUTHORIZED_V1' and ra['ordinaryProbeAllowed'] is True and ra['loopbackServeAllowed'] is True
 assert all(ra[k] is False for k in ['appMountAllowed','componentConstructionAllowed','fullNextAcceptanceAllowed','adoptionAllowed'])
 assert ref(rr['rootAuthority'])=='authority/runtime.json'
 assert rr['sourceIndex']==ra['sourceIndex'] and rr['constructionCallerIndex']==ra['constructionCallerIndex']==cr['callerIndex']
 assert rr['constructionResult']==ra['constructionResult']==capsule['actualConstructorResult'] and rr['probeSourceIndex']==cr['artifacts']['inputSourceIndex']
 for k in ['component','componentAudit','engine','nativeMetadata']:assert rr[k]==ra[k]==cr['artifacts'][k]
 assert rr['engineBuildEvidence']==ra['engineBuildEvidence']==cr['artifacts']['engineBuildEvidence']
 for k in ['sourceIndex','nodeOracleHostChecks']:ref(rr[k])
 for k in ['nodeOracleStdout','nodeOracleTerminal','nodeOracleStarted']:
  assert rr[k]==ra[k]
  name=innerOrigins[ra[k]['path']];assert digest(inner[name])=={key:ra[k][key] for key in ['bytes','sha256']}
 # Original monitored stdout and the published fixture copy are distinct roles.
 assert {k:ra['nodeOracleStdout'][k] for k in ['bytes','sha256']}==digest(data[source+'node-oracle.stdout.jsonl'])
 assert rr['comparisonScope']=='original-Node-public-projection-plus-independent-native-assertions'
 assert rr['nativeBoundaryParityClaimed'] is False and rr['nativeOwnerIdentityOrTeardownProved'] is False
 assert all(rr[k] is False for k in ['applicationMounted','applicationImported','fullNextAcceptance','adoption'])
 runtimeCode=0 if rr['observationsValid'] and rr.get('nodeSelectedParity') is True else 1
 rt,rs,n=terminal('runtime-outer',runtimeCode);processes+=n
 assert rs['timeoutSeconds']==180 and rs['authority']==rr['rootAuthority']
 plan=obj(ref(ra['plan']));assert rs['argv']==[plan['node']['path'],str(Path(ra['sourceIndex']['path']).parent/'collect.mjs'),rr['rootAuthority']['path']]
 collector='sources/'+Path(ra['sourceIndex']['path']).parent.name+'/'
 prepared=obj(collector+'results.json');dataTests=obj(collector+'checks/data.stdout.log');dataChecks=obj(collector+'checks/results.json')
 assert prepared['sourceOnly'] is True and prepared['pureDataChecks']==85 and prepared['actualGuestAssertions'] is None
 assert dataTests['pureDataCases']==dataTests['passed']==85 and dataTests['actualGuestAssertionsVerified']==0 and len(dataTests['rows'])==85 and all(r['passed'] is True for r in dataTests['rows'])
 assert all(dataTests[k] is False for k in ['oracleInvoked','collectorInvoked','guestInvoked']) and dataChecks['pureDataRawExitCode']==0 and len(dataChecks['grammar'])==4 and all(r['rawExitCode']==0 for r in dataChecks['grammar'])
 assert dataChecks['networkFilesystemWritesTimersOrGuestInvoked'] is False
 history='preparation-history/unexecuted-context-collector-v1-authority.json'
 assert history in data and obj(history)['sourceIndex']['sha256']=='f35fd81efc4c0441b031b70c4de37f5edbe1af8968fb7992f19e90a43c30b036'
 assert ra['sourceIndex']['sha256']=='44e03e0e12927bb5a98c6c45f4b14b930cfa3ff3a1b6c0c89272822916f88ae1'
 assert outer['state']=='ROOT_CONTEXT_INTERLEAVING_PROBE_OBSERVATION_V1' and outer['rawExitCode']==runtimeCode and outer['ownedGroupsClean'] is True and outer['protectedInputsPreserved'] is True
 assert outer['result']==capsule['actualRuntimeResult'] and outer['nodeSelectedParity']==rr.get('nodeSelectedParity')
 assert outer['terminal']==dict(path=str(Path(capsule['actualRuntimeResult']['path']).parent)+'-external-root/terminal.json',**digest(data['runtime-outer/terminal.json']))
 assert rr['inputsPreserved'] is True and rr['server']['forcedCleanup'] is False and rr['server']['shutdownRequested'] is True and rr['server']['sigintSent'] is True
 assert rr['server']['exit']=={'code':0,'signal':None,'error':None}
 for k in ['stdout','stderr']:ref(rr['server'][k])
 command=rr['server']['command'];assert command[0]==plan['wasmtime']['path'] and command[1]=='serve' and command[-1]==cr['artifacts']['component']['path']
 assert command[command.index('--max-instance-reuse-count')+1]=='32' and command[command.index('--idle-instance-timeout')+1]=='60s' and '--dir' not in command
 assert command[command.index('-S')+1]=='cli=y,tcp=n,udp=n,allow-ip-name-lookup=n'
 assert rr['portLease']['singleAttempt'] is True and rr['portLease']['fallbackAllowed'] is False
 assert 0<=len(rr['responses'])<=3
 responses=[];nativeTotal=0;allNativeComplete=True;actualProjections=[]
 for i,record in enumerate(rr['responses']):
  assert record['call']==i+1
  if 'body' not in record:
   assert 'transportError' in record;allNativeComplete=False;responses.append(dict(call=i+1,transportError=record['transportError'],completeNativeAssertions=0));continue
  raw=data[ref(record['body'])];assert record['rawValueType']=='Uint8Array'
  try:payload=json.loads(raw.decode('utf8'))
  except (UnicodeError,ValueError):
   assert record['safety']['safeToReuse'] is False;allNativeComplete=False;responses.append(dict(call=i+1,status=record['status'],body=record['body'],decodeRefused=True,completeNativeAssertions=0));continue
  assert record['safety']['envelope']==payload
  collection=payload.get('collection') if isinstance(payload,dict) else None
  summary=dict(call=i+1,status=record['status'],body=record['body'],reportedCollectionPassed=collection.get('passed') if isinstance(collection,dict) else None,safeToReuse=record['safety']['safeToReuse'],completeNativeAssertions=0)
  try:
   assert set(payload)=={'schemaVersion','marker','call','method','collection'} and payload['schemaVersion']==1 and payload['marker']=='NEXT_NATIVE_CONTEXT_INTERLEAVING_V1' and payload['call']==i+1 and payload['method']=='GET'
   value=payload['collection'];assert value['boundaryMode']=='actual-native-private-boundaries' and value['logicalBranchesOnly'] is True
   assert all(value[k] is False for k in ['actualHttpResourceConcurrencyProved','nativeOwnerIdentityOrTeardownProved','resetOrGcWorkload'])
   assert type(value['peakPlannedWaits']) is int and 0<=value['peakPlannedWaits']<=8
   projected=projection(value);assert projected==projections[i] and sum(len(r['assertions']) for r in value['records'])==153
   assert sum(len(r['requiredEdges']) for r in value['records'])==29
   assert record['status']==200 and 'application/json' in record['headers']['content-type']
   assert record['safety']['safeToReuse'] is True
   if 'typedPayload' in record:assert record['typedPayload']==payload
   if rr.get('comparisonComplete') is True:
    assert record['typedPayload']==payload and record['ordinalValidated'] is True and record['nativeAssertionsVerified']==153 and record['requiredEdgesVerified']==29
   summary.update(completeNativeAssertions=153,requiredEdges=29,publicProjectionMatched=True,peakPlannedWaits=value['peakPlannedWaits']);nativeTotal+=153;actualProjections.append(projected)
  except (AssertionError,KeyError,TypeError,ValueError) as failure:
   allNativeComplete=False;summary['independentValidationRefusal']=type(failure).__name__
   assert rr['observationsValid'] is False or rr.get('nodeSelectedParity') is False
  responses.append(summary)
 accepted=rr['observationsValid'] is True and rr.get('nodePublicProjectionParity') is True
 if accepted:
  assert rr['state']=='CONTEXT_INTERLEAVING_SELECTED_PARITY_OBSERVED_V1' and runtimeCode==0 and len(responses)==3 and allNativeComplete and nativeTotal==459
  assert rr['allThreeCaptureAttemptsComplete'] is True and rr['allThreePassingResponsesCaptured'] is True and rr['comparisonComplete'] is True and rr['errors']==[]
  assert rr['nativeAssertionsVerified']==459 and rr['nodeHostAssertionsVerified']==918 and rr['nodeHostCollectionsCaptured']==6 and rr['selectedDifferences']==[]
  assert data['runtime/node-oracle.stdout.jsonl']==data[source+'node-oracle.stdout.jsonl'] and rr['nodeOracleOriginalCollections']==[f['observed'] for f in oracle[:3]]
  assert len(rr['comparisons'])==15
  for j,comparison in enumerate(rr['comparisons']):
   call=j//5;index=j%5
   assert comparison['call']==call+1 and comparison['id']==IDS[index] and comparison['classification']=='matches-node-public-projection'
   assert comparison['actualProjection']==actualProjections[call]['records'][index] and comparison['nodeProjection']==projections[call]['records'][index]
   assert comparison['actualFullRecord']==obj('runtime/response-'+str(call+1)+'.body')['collection']['records'][index] and comparison['nodeOriginalFullRecord']==oracle[call]['observed']['records'][index]
 else:
  assert runtimeCode==1 and rr['state'] in ['CONTEXT_INTERLEAVING_FAILED_OBSERVATION_PRESERVED_V1','CONTEXT_INTERLEAVING_SELECTED_DIFFERENCES_OBSERVED_V1']
  if rr.get('safetyStop'):
   assert rr['discardOwnedServerRequired'] is True and rr['responses'][-1]['call']==rr['safetyStop']['call']
 return dict(schemaVersion=1,state='ACTUAL_CONTEXT_INTERLEAVING_CONSTRUCTOR_AND_RUNTIME_DATA_REVIEWED_V1',verifiedEvidence=True,constructorPassed=True,constructorInnerRawExitCodes=[0,0,0],constructorOuterRawExitCode=0,worldRootBeforeAfterUnchanged=True,worldSourceIndex=capsule['worldSourceIndex'],worldMembers=28,worldWitFiles=8,
  hostOracleCollections=6,hostAssertionsVerified=918,hostAssertionsAreNativeProof=False,collectorPreparationPureDataChecks=85,collectorPreparationGuestAssertions=0,unexecutedV1GrantRetainedAsPreparationOnly=True,runtimeOriginalState=rr['state'],runtimeOuterRawExitCode=runtimeCode,runtimeObservationsValid=rr['observationsValid'],nativeSelectedAcceptance=accepted,nativeCompleteAssertionsVerified=nativeTotal,responseSummaries=responses,nativeAndOriginalNodePublicProjectionMatched=accepted,
  component=cr['artifacts']['component'],engine=cr['artifacts']['engine'],nativeMetadata=cr['artifacts']['nativeMetadata'],fixtureSourceIndex=cr['artifacts']['inputSourceIndex'],fixtureEntry=cr['artifacts']['inputEntry'],constructionResult=capsule['actualConstructorResult'],runtimeResult=capsule['actualRuntimeResult'],runtimeSourceIndex=ra['sourceIndex'],standardInterfaces=13,externalPreview1OrCustomImports=False,observedOwnedProcessRecords=processes,
  sourceAuthorRelationship=capsule['sourceAuthorRelationship'],sourceProtectionScope='Original own operation guards plus selected current DATA bookends, not all-time filesystem/process attestation or full SDK closure.',
  sameStoreHttpResourceConcurrencyProved=False,nativeOwnerIdentityOrTeardownProved=False,unrefAcrossCallsOrPeerDisconnectTested=False,resetGcOrFaultWorkload=False,newTargetActionsByReader=False,fullNextAcceptance=False,publicAdoptionGranted=False,bigComponentSdkArchiveOrAppPayloadCopied=False)
if __name__=='__main__':print(json.dumps(main(),indent=2))
