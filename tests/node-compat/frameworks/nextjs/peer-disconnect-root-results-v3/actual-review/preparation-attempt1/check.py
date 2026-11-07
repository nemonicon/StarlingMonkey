"""Read-only portable DATA reader. No JS/process/oracle/compiler/guest calls."""
from pathlib import Path,PurePosixPath
import base64,hashlib,json,re,sys,tarfile
HERE=Path(__file__).resolve().parent
def need(ok,message):
 if not ok:raise AssertionError(message)
def equal(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(equal(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(equal(x,y)for x,y in zip(a,b))
 return a==b
def digest(data,ref):need(len(data)==ref['bytes']and hashlib.sha256(data).hexdigest()==ref['sha256'],'bytes/hash '+ref['path'])
def clean(t,raw=0):
 need(type(t['rawExitCode'])is int and t['rawExitCode']==raw,'expected raw terminal')
 need(t['timeout']is False and t['forcedCleanup']is False,'timeout/forced')
 need(t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True,'owned groups')
 need(all(t[k]==[]for k in ['signals','errors','interruptedSignals','remainingObservedPids']),'terminal diagnostics')
 need(all(g['alive']is False for g in t['finalGroups']),'remaining group')
def main():
 if(HERE/'index.json').exists():
  own=json.loads((HERE/'index.json').read_bytes());names=[r['path']for r in own['files']]
  need(len(names)==len(set(names)),'duplicate own member')
  need(set(names)|{'index.json'}=={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()},'own membership')
  need(not any(p.is_symlink()for p in HERE.rglob('*')),'own symlink')
  for r in own['files']:digest((HERE/r['path']).read_bytes(),dict(r,path=r['path']))
 cap=json.loads((HERE/'capsule.json').read_bytes());digest((HERE/'data.tar.gz').read_bytes(),cap['archive'])
 rows=cap['files'];need(len(rows)==cap['retainedFileCount'] and len({r['path']for r in rows})==len(rows),'retained membership')
 blobs={};origins={}
 with tarfile.open(HERE/'data.tar.gz','r:gz')as archive:
  members=archive.getmembers();need(sorted(m.name for m in members)==sorted(r['path']for r in rows),'whole archive membership')
  for m in members:
   p=PurePosixPath(m.name);need(m.isfile()and not p.is_absolute()and'..'not in p.parts,'unsafe archive member')
   blobs[m.name]=archive.extractfile(m).read()
 for r in rows:
  digest(blobs[r['path']],r['original']);origins.setdefault(r['original']['path'],[]).append(blobs[r['path']])
 def retained(ref):
  need(ref['path']in origins,'missing retained '+ref['path'])
  for b in origins[ref['path']]:digest(b,ref)
 def readref(ref):retained(ref);return json.loads(origins[ref['path']][0])
 def load(name):return json.loads(blobs[name])
 for family in cap['families']:
  idx=readref(family['index']);base=Path(family['index']['path']).parent
  need(family['memberDescriptors']==[{**r,'path':str(base/r['path'])}for r in idx['files']],'family index/member joins')
  if family['retainedMembers']:
   for r in family['memberDescriptors']:retained(r)
 r=load('runtime/result.json');c=load('constructor/result.json');a=readref(r['rootAuthority']);ca=readref(c['rootAuthority'])
 plan=load('sources/peer-disconnect-wasmtime-collector-v3/plan.json');fixture=load('sources/peer-disconnect-candidate-v3/plan.json');cp=readref(c['plan'])
 need(cap['runtimeResult']['sha256']=='f25bed1f17b115d6e92845999c3f57608282bdafd6cf80b89ac574bee74624ab','exact actual result')
 need(r['state']=='PEER_DISCONNECT_DIAGNOSTIC_OBSERVATIONS_COMPLETE_V2'and r['observationsValid']is True and r['functionChecksPassed']is True and r['withinExportIoPathsObserved']is True,'actual observation/function/path flags')
 need(r['coverageComplete']is True and r['collectorAccepted']is True and r['signalChecksPassed']is True and r['observedIoRequestSignalImplemented']is True and r['coverageStatus']=='within-export-paths-and-js-history-only','bounded V3 acceptance')
 need(r['errors']==[]and r['inputsPreserved']is True,'preservation/no collector errors')
 for k in ['nativeDisposalCountsOrStoreDeathProved','independentPeerDisconnectSignal','instantIdlePeerAbortClaimed','httpBodyCompletionOrTrailersProved','fullNextAcceptance','adoption']:need(r[k]is False,k)
 for k in ['component','componentAudit','constructionResult','constructionCallerIndex','engine','nativeMetadata','engineBuildEvidence','constructionOuterTerminal','constructionWorldGuard']:need(equal(r[k],a[k]),'Root runtime role '+k)
 need(a['state']=='ROOT_PEER_DISCONNECT_HTTP_PROBE_AUTHORIZED_V2'and a['firstHostCase']=='peer-'+r['runId'],'exact Root case')
 need(c['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'and c['passed']is True and c['entryMode']=='peer-disconnect'and c['error']is None and c['finalProtection']['unchanged']is True,'actual construction')
 for k in ['ordinaryExportsInvoked','httpServed','appMountedAtInit','metadataFrameProjected','productionProfilePromoted']:need(c[k]is False,'construction scope '+k)
 need(ca['state']=='ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2'and ca['entryMode']=='peer-disconnect'and ca['callerIndex']==r['constructionCallerIndex'],'constructor authority')
 need(cp['entries']=={'peer-disconnect':plan['probeEntry']}and cp['inputSourceIndex']==plan['probeSourceIndex']==r['probeSourceIndex'],'exact Source/entry')
 need(cp['witDirectory']==fixture['witDirectory']==plan['witDirectory']==str(Path(ca['worldSourceIndex']['path']).parent),'world directory')
 need(ca['worldSourceIndex']==fixture['worldSourceIndex'],'world index')
 for k,v in {'component':r['component'],'componentAudit':r['componentAudit'],'engine':r['engine'],'nativeMetadata':r['nativeMetadata'],'inputSourceIndex':plan['probeSourceIndex'],'inputEntry':plan['probeEntry'],'adapter':plan['adapter']}.items():need(c['artifacts'][k]==v,'constructed artifact '+k)
 native=readref(r['nativeMetadata']);need(native['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1','genuine native generation')
 need(equal(a['metadataExpectedFixedValues'],ca['metadataExpectedFixedValues'])and a['engineBuildEvidence']==ca['engineBuildEvidence'],'same native selection')
 for k,v in a['metadataExpectedFixedValues'].items():need(equal(native[k],v),'actual native fixed field '+k)
 need(native['freshFrontendCompileRows']==1 and native['baselineCompileDatabaseRows']==80 and native['unchangedBaselineCompileDatabaseRows']==79 and native['baselineSeparateEmbeddingRows']==1,'incremental provenance')
 need(native['all80FreshCompilationClaimed']is False and native['oldMetadataProjected']is False,'no old-frame or fresh80 claim')
 need(r['component']['sha256']=='643742a2ad5a0a00672edef3cc66d7dbfb088ea29864f3e3e30c2ca329cc1e54'and r['engine']['sha256']=='4623640b79b97eb91dc8559b3766fdb430a1807fe90b6ace6c85668a97f13067','binary descriptors')
 for prefix in ['runtime-monitor','constructor-monitor']:
  t=load(prefix+'/terminal.json');clean(t)
  for k in ['stdout','stderr','authority']:retained(t[k])
  need(t['stderr']['bytes']==0,'outer stderr')
  s=load(prefix+'/started.json');need(s['authority']==t['authority']and s['pid']==t['pid'],'outer started/authority')
  need(t['authority']==(r['rootAuthority']if prefix=='runtime-monitor'else c['rootAuthority']),'exact outer Root authority')
 need(load('runtime-monitor/started.json')['timeoutSeconds']==240,'runtime monitor budget')
 need(load('constructor-monitor/started.json')['timeoutSeconds']==2400,'constructor monitor budget')
 world=load('constructor-monitor/world-guard.json');need(world['unchanged']is True and world['before']==world['after'],'world bookends')
 for name in ['constructor-monitor/terminal.json','constructor-monitor/world-guard.json']:
  ref=next(x['original']for x in rows if x['path']==name)
  need(ref in a['nativeProtectedInputs'],'constructor outer/world receipt protected by runtime Root')
 need(c['rootAuthority']in a['nativeProtectedInputs'],'constructor Root protected by runtime Root')
 need(world['before']==dict(sourceIndex=ca['worldSourceIndex'],members=28,witFiles=8,exactFileAndDirectoryMembership=True,noSymlinkOrHardlinkAliases=True),'whole world receipt')
 wi=readref(ca['worldSourceIndex']);wits=[{**x,'path':str(Path(ca['worldSourceIndex']['path']).parent/x['path'])}for x in wi['files']if x['path'].endswith('.wit')]
 need(len(wits)==8 and all(x in ca['newSourceEvidence']for x in wits),'eight Root WIT inputs')
 for x in wits:retained(x)
 need([x['label']for x in c['commands']]==['componentize-init','component-validate','component-wit'],'three actual commands')
 for command in c['commands']:
  t=readref(command['terminal']);clean(t);s=load('constructor/'+command['label']+'/started.json')
  need(s['argv']==command['argv']and s['timeoutSeconds']==command['capSeconds']and s['pid']==t['pid'],'actual constructor argv/cap')
  need(t['authority']==c['rootAuthority']and command['rawExitCode']==0 and command['clean']is True,'command status/authority')
  for k in ['stdout','stderr']:need(t[k]==command[k],'command stream role');retained(t[k])
  need(command['stderr']['bytes']==0,'command stderr')
 init=[json.loads(x)for x in blobs['constructor/componentize-init/stdout.log'].splitlines()]
 need(len(init)==1 and init[0]['state']=='NEXT_NATIVE_COMPONENT_API_CAPTURE_COMPLETE_V1'and init[0]['entryMode']=='peer-disconnect','whole API capture frame')
 for k in ['component','returnedImports','returnedOwnShape']:need(init[0]['artifacts'][k]==c['artifacts'][k],'API capture artifact '+k)
 outer=[json.loads(x)for x in blobs['constructor-monitor/stdout.log'].splitlines()]
 need(len(outer)==4 and outer[-1]['result']==cap['constructionResult']and outer[-1]['passed']is True and outer[-1]['error']is None,'whole constructor parent JSONL')
 need([x['timeoutSeconds']for x in outer[:3]]==[1800,120,120],'actual child budgets')
 audit=readref(r['componentAudit']);need(audit['passed']is True and audit['entryMode']=='peer-disconnect'and audit['component']==r['component'],'actual typed audit')
 selected=plan['selectedInterfaces'];need(len(selected)==len(set(selected))==13 and selected==fixture['selectedInterfaces']==audit['selectedInterfaces'],'selected13')
 need(len(audit['emittedImports'])==len(set(audit['emittedImports']))and set(audit['emittedImports'])<=set(selected)and all(x.endswith('@0.2.10')for x in audit['emittedImports']),'standard imports')
 need(audit['exports']==['wasi:http/incoming-handler@0.2.10']and audit['noExternalPreview1OrCustomImports']is True and audit['allEmittedVersion']=='0.2.10','standard graph/export')
 wit=blobs['constructor/component-wit/stdout.log'].decode();root=wit.split('world root {',1)[1].split('}',1)[0]
 need(re.findall(r'^  import ([^;]+);$',root,re.M)==audit['emittedImports']and re.findall(r'^  export ([^;]+);$',root,re.M)==audit['exports'],'whole raw WIT world')
 need('handle: func(request: incoming-request, response-out: response-outparam);'in wit,'resource ABI')
 need({x[0]for x in load('constructor/api-return/returned-imports.json')}==set(audit['emittedImports']),'whole import tuples')
 shape=load('constructor/api-return/returned-own-shape.json');props={x['key']['string']:x for x in shape['properties']}
 need(set(props)=={'component','imports','debug'}and props['debug']['value']=={'type':'undefined'},'API typed own shape')
 v=props['component']['value'];need(v['type']=='Uint8Array'and v['file']==r['component']and v['byteLength']==r['component']['bytes']and v['sha256']==r['component']['sha256'],'full returned-byte witness')
 def http(raw,partial=False):
  header,sep,encoded=raw.partition(b'\r\n\r\n');need(bool(sep),'HTTP headers')
  status=int(header.split(b' ')[1]);headers=header.decode('latin1');body=[]
  if b'transfer-encoding: chunked'in header.lower():
   offset=0;complete=False
   while offset<len(encoded):
    end=encoded.find(b'\r\n',offset)
    if end<0:need(partial,'chunk header');break
    count=int(encoded[offset:end].split(b';')[0],16);need(count>=0,'chunk size');offset=end+2
    if count==0:
     need(encoded[offset:]==b'\r\n','complete empty trailer terminator');complete=True;break
    if offset+count+2>len(encoded):need(partial,'chunk data');break
    need(encoded[offset+count:offset+count+2]==b'\r\n','chunk CRLF');body.append(encoded[offset:offset+count]);offset+=count+2
   need(complete or partial,'normal complete HTTP chunk framing')
  else:
   body=[encoded];length=re.search(rb'\r\ncontent-length:\s*(\d+)',header,re.I)
   if length:need(len(encoded)==int(length[1]),'HTTP content length')
  return status,headers,b''.join(body)
 def guest_log(raw):
  text=raw.decode('utf8');need(text.endswith('\n'),'whole guest stderr line')
  events=[];host=[]
  for line in text.splitlines():
   try:x=json.loads(line)
   except ValueError:host.append(line);continue
   if not isinstance(x,dict)or x.get('marker')!='NEXT_PEER_DISCONNECT_DIAGNOSTIC_V1':host.append(line);continue
   need(x['schemaVersion']==1 and x['origin']=='actual-wasi-guest'and x['phase']in plan['allowedGuestPhases'],'typed guest log')
   events.append(x)
  need([x['sequence']for x in events]==list(range(1,len(events)+1)),'whole cohort log sequence')
  return events,host
 host=readref(plan['referenceHostChecks']);need(host['passed']is True and host['sourceProtectionPassed']is True and host['hostOnly']is True and host['guestOrEngineOrCompilerExecuted']is False,'original Node scope')
 phase=next(x for x in host['phases']if x['name']=='node-localhost-reference');nt=load('node-reference/terminal.json');clean(nt);ns=load('node-reference/started.json')
 need(ns['argv']==phase['argv']==[plan['node']['path'],'--unhandled-rejections=strict',str(Path(plan['referenceHostChecks']['path']).parent/'node-control.mjs')]and ns['timeoutSeconds']==180 and ns['pid']==nt['pid']and ns['authority']==nt['authority'],'original Node HTTP/net argv')
 for k in ['stdout','stderr','authority']:retained(nt[k])
 node=load('node-reference/stdout.log');need(node['hostReferenceCollectionPassed']is True and node['nodeVersion']=='v22.14.0'and node['forcedCleanup']is False and node['remainingSockets']==node['waiters']==0,'Node actual reference')
 need(node['guestOrEngineOrCompilerExecuted']is False and node['wasiGuestPeerDisconnectCoverage']is False and node['nodeWasiTcpParityClaimed']is False and node['requestSignalLinkedToPeer']is False,'no fabricated Node/WASI parity')
 need(node['nodeEvents']==[json.loads(x)for x in blobs['node-reference/stderr.log'].splitlines()],'whole Node event stream')
 need(len(node['cases'])==6 and len(node['nodeEvents'])==163,'finite Node controls')
 for case in node['cases']:
  raw=base64.b64decode(case['rawBase64'],validate=True);need(len(raw)==case['rawBytes'],'whole Node raw bytes')
  status,headers,body=http(raw,case['label']=='output-close');need((status,headers)==(case['status'],case['headers'])and body==base64.b64decode(case['decodedBodyBase64'],validate=True),'Node whole framing/body')
 need(any(x['phase']=='node-input-read-failed'and x['error'].get('code')=='ECONNRESET'for x in node['nodeEvents']),'actual separate Node input category')
 need(any(x['phase']=='node-output-write-failed'and x['error'].get('code')=='ERR_STREAM_DESTROYED'for x in node['nodeEvents']),'actual separate Node output category')
 need([x['id']for x in r['cohorts']]==['upload','output'],'two fixed cohorts')
 need(len({x['host']['pid']for x in r['cohorts']})==2,'two fresh owned processes')
 healthy=0;raw_responses=0;event_counts={};host_lines_by_cohort={}
 for cohort in r['cohorts']:
  cid=cohort['id'];need(cohort['independentFreshHost']is True and cohort['notRetryOfOtherCohort']is True and cohort['errors']==[],'independent cases')
  for k in ['functionChecksPassed','withinExportIoPathObserved','signalChecksPassed','afterReturnJsHistoryObserved','hostShutdownClean']:need(cohort[k]is True,'cohort '+k)
  need(cohort['afterReturnCleanupStatus']=='js-history-only-no-native-cleanup-proof'and'safetyStop'not in cohort and'discardOwnedServerRequired'not in cohort,'bounded normal reuse')
  h=cohort['host'];need(h['exit']==dict(code=0,signal=None,error=None)and h['shutdownRequested']is True and h['sigintSent']is True and h['forcedCleanup']is False,'actual SIGINT0')
  need(h['command']==[plan['wasmtime']['path'],'serve','--addr','127.0.0.1:'+str(cohort['portLease']['port']),'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','32','--idle-instance-timeout','60s',r['component']['path']],'stock serve/no app mount')
  for k in ['stdout','stderr']:retained(h[k])
  need(h['stdout']['bytes']==0,'host stdout')
  events,host_lines=guest_log(origins[h['stderr']['path']][0]);event_counts[cid]=len(events);host_lines_by_cohort[cid]=host_lines
  need(not any(x['phase']in ['adapter-failed','dispose-failed','io-abort-failed','input-cleanup-failed','response-reader-cancel-failed','handler-reader-cancel-failed-suppressed','response-reader-cancel-failed-suppressed']for x in events),'no typed fatal/unknown cleanup failure')
  first=a['firstHostCase']+'-'+cid+'-healthy-upload';need(cohort['firstLabel']==first,'Root first label')
  expected=['healthy-upload','healthy-output',cid+'-close','inspect'];need([x['kind']for x in cohort['responses']]==expected,'exact four invocations')
  for ordinal,response in enumerate(cohort['responses'],1):
   raw_responses+=1;retained(response['raw']);raw=origins[response['raw']['path']][0]
   need(len(raw)==response['rawBytes']and response['ordinal']==ordinal and response['clientCloseObserved']is True and response['forcedClientCleanup']is False,'whole client observation')
   need('transportOrCollectionError'not in response and'frameDecodeError'not in response,'no discarded capture failure')
   status,headers,body=http(raw,response['kind']=='output-close');need((status,headers)==(response['status'],response['headers'])and body==base64.b64decode(response['decodedBodyBase64'],validate=True)and len(body)==response['decodedBodyBytes'],'whole HTTP/body')
   snapshot=response['diagnosticSnapshot'];need(snapshot['incompleteTail']=='','complete snapshot');snap=snapshot['events'];need(snap==events[:len(snap)],'snapshot actual log prefix')
   own=[x for x in snap if x['label']==response['label']];analysis=response['analysis'];need(analysis['ownEvents']==own and analysis['eventCount']==len(own)and analysis['identityObserved']is True,'actual own events')
   need(all(x['firstLabel']==first and x['ordinal']==ordinal for x in own),'identity/ordinal')
   phases={k:[x for x in own if x['phase']==k]for k in plan['allowedGuestPhases']}
   def one(k):return len(phases[k])==1
   def seq(k):need(one(k),'one '+k);return phases[k][0]['sequence']
   need(one('adapter-enter')and one('handler-enter')and one('adapter-finally-returned'),'entry/finally')
   need(analysis['safeToRequestAgain']is True and analysis['adapterFailureObserved']is False and analysis['adapterFinallyObserved']is True,'explicit safe classified path')
   need(analysis['knownFailedHostTerminal']is False and analysis['hostReadEnteredOrBlockedProved']is False and analysis['afterReturnNativeCleanupProved']is False,'no invented host/native proof')
   created=phases['request-signal-created'];need(len(created)==1 and created[0]['aborted']is False and created[0]['alreadyAbortedBeforeListener']is False,'fresh signal')
   enter=phases['handler-enter'][0];need(enter['signalAborted']is False and enter['requestSignalLinkedToPeer']is True and enter['requestSignalPolicy']=='observed-io-only'and enter['independentPeerDisconnectSignal']is False,'observed-I/O policy')
   if ordinal!=3:
    need(analysis['knownNormalHandlerPath']is True and analysis['knownHandledOutputClosedPath']is False and analysis['freshHealthySignalObserved']is True,'ordinary normal path')
    need(one('handler-finally')and one('outgoing-finish-returned')and not phases['output-write-failed']and not phases['io-abort-invocation-attempt']and not phases['request-signal-abort-event'],'healthy path no abort')
    need(len(phases['output-write-invocation-attempt'])>0 and len(phases['output-write-invocation-attempt'])==len(phases['output-write-returned']),'healthy complete writes')
   else:
    need(analysis['signalPolicyObserved']is True and analysis['ioPathObserved']is True,'I/O abort observed')
    need(seq('io-abort-invocation-attempt')<seq('request-signal-abort-event')<seq('io-abort-returned'),'actual synchronous abort order')
    event=phases['request-signal-abort-event'][0];ret=phases['io-abort-returned'][0]
    need(event['signalAborted']is True and event['reasonMatchesObservedIo']is True and ret['controllerAborted']is True and ret['requestSignalAborted']is True and ret['requestReasonMatchesFirstObservedIo']is True,'same first reason observed')
    need(cohort['disconnectCoverage']==analysis,'whole cohort coverage not projected')
   if response['kind']=='healthy-upload':
    value=json.loads(body);need(status==200 and value['complete']is True and value['received']==8192 and value['readFailure']is None and value['ordinal']==ordinal and value['signalAborted']is False,'healthy upload');need(analysis['functionChecksPassed']is True,'control passed');healthy+=1
   elif response['kind']=='healthy-output':
    need(status==200 and len(body)==32768 and all(body[n*4096:(n+1)*4096]==bytes([65+n])*4096 for n in range(8)),'eight exact output chunks');need(one('producer-close-returned')and analysis['functionChecksPassed']is True,'healthy output');healthy+=1
   elif response['kind']=='upload-close':
    value=json.loads(body);need(status==400 and value['received']==1024 and value['complete']is False and value['signalAborted']is True and'HttpProtocolError'in value['readFailure']['message'],'partial upload actual error')
    milestone=response['synchronizedMilestone'];need(milestone in own and milestone['phase']=='input-read-invocation-attempt'and milestone['inputBytes']==1024 and milestone['hostReadEnteredOrBlockedProved']is False,'read-attempt barrier only')
    need(any(x['error'].get('payloadTag')=='last-operation-failed'for x in phases['input-read-failed']),'actual input category')
    failed=phases['handler-read-failed'];need(len(failed)==1 and failed[0]['signalAborted']is True and failed[0]['reasonMatchesCaught']is True,'handler catches same first reason')
    need(phases['input-read-failed'][-1]['sequence']<seq('io-abort-invocation-attempt')<seq('handler-read-failed')<seq('handler-body-finally'),'input failure/abort/catch order')
    need(analysis['knownNormalHandlerPath']is True and analysis['coverageStatus']=='observed-input-failure-and-io-abort-within-export','normal400 completion')
   elif response['kind']=='inspect':
    value=json.loads(body);need(status==200 and value['signalAborted']is False and value['inspection']['firstLabel']==first and value['inspection']['lastOrdinal']==4 and analysis['afterReturnJsHistoryObserved']is True,'fresh inspect signal/history')
    old=next(x for x in value['inspection']['requests']if x['ordinal']==3);need(old['label'].endswith('-'+cid+'-close'),'disconnected request retained')
    captured=old['events'];need(captured==[x for x in events if x['label']==old['label']],'whole old invocation history')
   else:
    need(status==200 and body==b'A'*4096 and response['firstBodyBeforeClose']is True,'first bytes actually observed');need(any(x['phase']=='client-destroySoon-invocation-attempt'for x in response['socketEvents']),'ordinary client close')
    need(one('output-write-failed')and phases['output-write-failed'][0]['error'].get('payloadTag')=='closed','actual output closed')
    need(len(phases['output-write-invocation-attempt'])==2 and len(phases['output-write-returned'])==1,'second write failure')
    need(seq('output-write-failed')<seq('io-abort-invocation-attempt')<seq('known-output-closed-handling-enter')<seq('producer-cancel-returned')<seq('response-reader-cancel-returned')<seq('response-reader-lock-release-returned')<seq('adapter-finally-returned')<seq('known-output-closed-handled-return'),'actual classified cleanup/return order')
    need(analysis['knownNormalHandlerPath']is False and analysis['knownHandledOutputClosedPath']is True and analysis['handledCloseRequiredOrderObserved']is True and analysis['childBeforeParentDropOrderObserved']is True and analysis['readerCancelReturned']is True and analysis['producerCancelReturned']is True,'specific closed handling')
    drops={x['resource']:x['sequence']for x in phases['dispose-returned']};need(drops['output-stream']<drops['outgoing-body-unfinished']and drops['incoming-body-unfinished']<drops['incoming-request'],'observed child before parent drops')
    for resource in drops:
     attempts=[x for x in phases['dispose-invocation-attempt']if x['resource']==resource];need(len(attempts)==1 and attempts[0]['sequence']<drops[resource],'actual dispose attempt/return')
    final=phases['known-output-closed-handled-return'][0];need(final['requestSignalAborted']is True and final['adapterCleanupCallsReturned']is True and final['nativeResourceCountsOrStoreDeathProved']is False and final['outgoingBodyFinished']is False,'bounded normal return witness')
 need(healthy==4 and raw_responses==8 and r['unknownOrFailedInvocationStops']==[],'exact controls/responses/no unsafe reuse')
 outer=load('runtime-monitor/observation.json');need(outer['rawExitCode']==0 and outer['ownedGroupsClean']is True and outer['protectedInputsPreserved']is True and outer['observationsValid']is True and outer['collectorAccepted']is True and outer['coverageComplete']is True,'actual outer acceptance');need(outer['result']==cap['runtimeResult'],'Root exact result')
 if'--current'in sys.argv:
  refs={x['path']:x for x in cap['externalDescriptors']};refs.update({x['original']['path']:x['original']for x in rows})
  for ref in refs.values():digest(Path(ref['path']).read_bytes(),ref)
 return dict(schemaVersion=1,state='INDEPENDENT_PEER_DISCONNECT_OBSERVED_IO_DATA_REVIEW_PASSED_V3',verifiedPassed=True,
  actualCollectorAccepted=True,actualRawExitCode=0,observationsValid=True,functionChecksPassed=True,withinExportIoPathsObserved=True,signalChecksPassed=True,coverageComplete=True,
  coverageScope='within-export-paths-and-js-history-only',cohorts=2,healthyControls=healthy,rawResponses=raw_responses,cohortGuestEventCounts=event_counts,hostLogLines=host_lines_by_cohort,
  uploadObservedBytes=1024,uploadWasiError='last-operation-failed',uploadHttpStatus=400,uploadObservedIoSignalAndCaughtReasonIdentity=True,uploadJsInspectionOrdinal=4,
  outputFirstObservedBytes=4096,outputLaterWasiWriteError='closed',outputObservedIoSignalAndReaderProducerCancelReturned=True,outputPostFinallyHandledNormalReturn=True,outputJsInspectionOrdinal=4,
  bothInspectSignalsFreshFalse=True,constructorCommandsRaw0=3,constructorParentRaw0=True,emittedImports=len(audit['emittedImports']),allEmittedVersion='0.2.10',
  component=r['component'],engine=r['engine'],nativeMetadata=r['nativeMetadata'],runtimeResult=cap['runtimeResult'],retainedFiles=len(rows),selectedCurrentDescriptors=cap['selectedRowsRehashedBeforeFinal'],
  separateOriginalNodeReferenceRetained=True,nodeWasiEnumOrSignalParityClaimed=False,observedIoRequestSignalImplemented=True,independentIdlePeerSignalProved=False,
  typedHttpErrorCodeOrTrailersCompletionProved=False,nativeDisposalCountsStoreDeathOrGcTeardownProved=False,physicalStoreIdentityProved=False,
  reviewerAuthoredEarlierAlsAndConstructorTooling=True,targetRerun=False,fullNextAcceptance=False,workingFullNext55SignalPolicyChanged=False,adoption=False,protectionScope=cap['independentReviewScope'])
if __name__=='__main__':print(json.dumps(main(),indent=2))
