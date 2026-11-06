"""Read retained DATA only; no workload, process, compiler or guest invocation."""
from pathlib import Path,PurePosixPath
import hashlib,json,re,sys,tarfile
HERE=Path(__file__).resolve().parent

def need(value,message):
 if not value:raise AssertionError(message)
def digest(data,ref):
 need(len(data)==ref['bytes'] and hashlib.sha256(data).hexdigest()==ref['sha256'],'bytes/hash '+ref['path'])
def equal(a,b):
 if type(a) is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b) and all(equal(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(equal(x,y)for x,y in zip(a,b))
 return a==b
def clean(record):
 need(type(record['rawExitCode'])is int and record['rawExitCode']==0,'raw exit')
 need(record['timeout']is False and record['forcedCleanup']is False,'timeout/cleanup')
 need(record['parentOwnedGroupGone']is True and record['allObservedOwnedGroupsGone']is True,'ownership')
 need(all(record[k]==[]for k in ['signals','errors','interruptedSignals','remainingObservedPids']),'terminal errors/signals')
 need(all(group['alive']is False for group in record['finalGroups']),'remaining group')

def main():
 capsule=json.loads((HERE/'capsule.json').read_bytes());digest((HERE/'data.tar.gz').read_bytes(),capsule['archive'])
 rows=capsule['files'];need(len(rows)==169 and len({r['path']for r in rows})==169,'finite retained membership')
 blobs={};origins={}
 with tarfile.open(HERE/'data.tar.gz','r:gz')as archive:
  members=archive.getmembers();need(sorted(m.name for m in members)==sorted(r['path']for r in rows),'whole tar membership')
  for member in members:
   name=PurePosixPath(member.name);need(member.isfile() and not name.is_absolute() and '..'not in name.parts,'unsafe member')
   blobs[member.name]=archive.extractfile(member).read()
 for record in rows:
  digest(blobs[record['path']],record['original']);origins.setdefault(record['original']['path'],[]).append(blobs[record['path']])
 def retained(ref):
  need(ref['path']in origins,'missing retained '+ref['path'])
  for data in origins[ref['path']]:digest(data,ref)
 def readref(ref):retained(ref);return json.loads(origins[ref['path']][0])
 def load(name):return json.loads(blobs[name])
 for family in capsule['families']:
  index=readref(family['index']);base=Path(family['index']['path']).parent
  need(family['memberDescriptors']==[{**r,'path':str(base/r['path'])}for r in index['files']],'declared family inventory')
  if family['retainedMembers']:
   for ref in family['memberDescriptors']:retained(ref)
 r=load('runtime/result.json');c=load('constructor/result.json');a=readref(r['rootAuthority']);ca=readref(c['rootAuthority'])
 plan=load('sources/native-pipe-wasmtime-collector-v1/plan.json');cp=readref(c['plan']);fixture=load('sources/native-pipe-regression-v1/plan.json')
 need(r['state']=='NATIVE_PIPE_SELECTED_PARITY_OBSERVED_V1' and r['observationsValid']is True and r['nodeSelectedParity']is True and r['selectedDifferences']==[] and r['errors']==[],'actual selected success')
 for key in ('applicationMounted','applicationImported','fullNextAcceptance','adoption'):need(r[key]is False,key)
 need(r['inputsPreserved']is True and r['allThreeCaptureAttemptsComplete']is True and r['comparisonComplete']is True,'capture/protection fences')
 for key in ('component','componentAudit','constructionResult','constructionCallerIndex','engine','nativeMetadata','engineBuildEvidence','nodeOracleStdout','nodeOracleTerminal','nodeOracleStarted','nodeOracleObservation'):
  need(equal(r[key],a[key]),'Root runtime role '+key)
 need(c['passed']is True and c['entryMode']=='pipe-regression' and c['error']is None and c['finalProtection']['unchanged']is True,'actual INIT construction')
 for key in ('ordinaryExportsInvoked','httpServed','appMountedAtInit','metadataFrameProjected','productionProfilePromoted'):need(c[key]is False,'constructor stage scope '+key)
 need(cp['entries']=={'pipe-regression':plan['probeEntry']} and cp['inputSourceIndex']==plan['probeSourceIndex'],'exact fixture roles')
 need(cp['witDirectory']==fixture['witDirectory']==plan['witDirectory']==str(Path(ca['worldSourceIndex']['path']).parent),'actual referenced world path')
 need(ca['worldSourceIndex']==fixture['worldSourceIndex'],'world index join')
 for key,ref in {'component':r['component'],'componentAudit':r['componentAudit'],'engine':r['engine'],'nativeMetadata':r['nativeMetadata'],'inputSourceIndex':plan['probeSourceIndex'],'inputEntry':plan['probeEntry'],'adapter':plan['adapter']}.items():
  need(c['artifacts'][key]==ref,'constructed artifact '+key)
 native=readref(r['nativeMetadata']);need(native['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1','genuine incremental metadata kind')
 need(a['metadataExpectedFixedValues']==ca['metadataExpectedFixedValues'] and a['engineBuildEvidence']==ca['engineBuildEvidence'],'same whole native selection')
 for key,value in a['metadataExpectedFixedValues'].items():need(equal(native[key],value),'native actual fixed field '+key)
 need(native['freshFrontendCompileRows']==1 and native['baselineCompileDatabaseRows']==80 and native['unchangedBaselineCompileDatabaseRows']==79 and native['baselineSeparateEmbeddingRows']==1,'one fresh TU / baseline ancestry')
 need(native['all80FreshCompilationClaimed']is False and native['oldMetadataProjected']is False,'no old-frame adaptation')
 need(r['engine']['sha256']=='4623640b79b97eb91dc8559b3766fdb430a1807fe90b6ace6c85668a97f13067' and r['component']['sha256']=='1c711297ad6c50edd3f1254caff69382aa0ed73bb7848a9f0d2de6a58aaa14bf','exact binary descriptors')
 for prefix in ('runtime-monitor','constructor-monitor'):
  t=load(prefix+'/terminal.json');clean(t)
  for key in ('stdout','stderr','authority'):retained(t[key])
 guard=load('constructor-monitor/world-guard.json');need(guard['unchanged']is True and guard['before']==guard['after'],'construction-time world bookends')
 need(guard['before']==dict(sourceIndex=ca['worldSourceIndex'],members=28,witFiles=8,exactFileAndDirectoryMembership=True,noSymlinkOrHardlinkAliases=True),'whole 8025 world guard receipt')
 world=readref(ca['worldSourceIndex']);wit=[{**item,'path':str(Path(ca['worldSourceIndex']['path']).parent/item['path'])}for item in world['files']if item['path'].endswith('.wit')]
 need(len(wit)==8 and all(ref in ca['newSourceEvidence']for ref in wit),'all eight WIT Root inputs')
 for ref in wit:retained(ref)
 need([row['label']for row in c['commands']]==['componentize-init','component-validate','component-wit'],'three constructor commands')
 for command in c['commands']:
  t=readref(command['terminal']);clean(t);started=load('constructor/'+command['label']+'/started.json')
  need(started['argv']==command['argv'] and started['pid']==t['pid'] and started['timeoutSeconds']==command['capSeconds'],'actual started constructor command')
  need(t['authority']==c['rootAuthority'] and command['rawExitCode']==0 and command['clean']is True,'constructor authority/status')
  for key in ('stdout','stderr'):need(t[key]==command[key],'constructor stream role');retained(t[key])
  need(command['stderr']['bytes']==0,'constructor error stream')
 audit=readref(r['componentAudit']);need(audit['passed']is True and audit['component']==r['component'] and audit['entryMode']=='pipe-regression','actual artifact audit')
 selected=plan['selectedInterfaces'];need(len(selected)==len(set(selected))==13 and audit['selectedInterfaces']==selected,'thirteen selections')
 need(len(audit['emittedImports'])==len(set(audit['emittedImports'])) and set(audit['emittedImports'])<=set(selected) and all(x.endswith('@0.2.10')for x in audit['emittedImports']),'standard emitted subset')
 need(audit['exports']==['wasi:http/incoming-handler@0.2.10'] and audit['noExternalPreview1OrCustomImports']is True and audit['allEmittedVersion']=='0.2.10','standard export/versions')
 wit_text=blobs['constructor/component-wit/stdout.log'].decode();world_text=wit_text.split('world root {',1)[1].split('}',1)[0]
 need(re.findall(r'^  import ([^;]+);$',world_text,re.M)==audit['emittedImports'] and re.findall(r'^  export ([^;]+);$',world_text,re.M)==audit['exports'],'whole raw WIT world')
 need('handle: func(request: incoming-request, response-out: response-outparam);'in wit_text,'resource-typed handler')
 imports=load('constructor/api-return/returned-imports.json');need({x[0]for x in imports}==set(audit['emittedImports']),'actual raw import tuples')
 shape=load('constructor/api-return/returned-own-shape.json');props={x['key']['string']:x for x in shape['properties']}
 need(set(props)=={'component','imports','debug'} and props['debug']['value']=={'type':'undefined'},'API own shape/debug retained')
 value=props['component']['value'];need(value['type']=='Uint8Array' and value['file']==r['component'] and value['byteLength']==r['component']['bytes'] and value['sha256']==r['component']['sha256'],'complete returned component witness')
 oracle=load('node-oracle/terminal.json');clean(oracle);started=load('node-oracle/started.json');observation=load('node-oracle/observation.json')
 need(started['argv']==[plan['node']['path'],plan['nodeOracleSource']['path']] and started['timeoutSeconds']==60 and started['pid']==oracle['pid'] and started['authority']==oracle['authority'],'actual Node oracle command')
 for key in ('stdout','stderr','authority'):retained(oracle[key])
 need(oracle['stdout']==r['nodeOracleStdout'] and oracle['stderr']['bytes']==0,'whole Node stdout/stderr')
 need(observation['passed']is True and observation['sourceInputsPreserved']is True and observation['cleanOwnedShutdown']is True and observation['guestExecuted']is False,'host oracle scope')
 frames=[json.loads(line)for line in blobs['node-oracle/stdout.log'].splitlines()];need(len(frames)==4,'whole four-frame oracle')
 need(frames[0]==r['nodeOracleIdentity'] and frames[0]['node']=='v22.14.0' and frames[0]['candidateInstalled']is False and frames[0]['guestExecuted']is False,'original Node identity')
 need(r['nodeOracleRawStrings']==[frame['value']for frame in frames[1:]],'complete raw oracle strings retained')
 need(blobs['runtime/node-oracle.stdout.jsonl']==blobs['node-oracle/stdout.log'],'oracle transport copy')
 ids=[item['id']for item in load('sources/native-pipe-wasmtime-collector-v1/case-contract.json')['cases']]
 need(ids==fixture['caseIds'] and len(ids)==12,'exact case contract')
 need(len(r['responses'])==3 and len(r['comparisons'])==36,'three complete calls / 36 comparisons')
 for call,record in enumerate(r['responses'],1):
  retained(record['body']);need(record['call']==call and record['status']==200 and record['ordinalValidated']is True and record['rawValueType']=='Uint8Array','actual response ordinal/status')
  actual=readref(record['body']);frame=frames[call];need(frame['call']==call and frame['kind']=='string','Node frame ordinal')
  expected=json.loads(frame['value'])
  need(equal(actual,record['typedPayload']) and equal(actual,expected),'whole typed return to Node')
  need(actual['schemaVersion']==1 and actual['suite']=='NATIVE_SIGNAL_PIPE_REGRESSION_V1' and actual['call']==call and actual['caseCount']==12 and actual['applicationImported']is False and actual['fullNextClaim']is False,'exact observed return schema/scope')
  need([case['id']for case in actual['records']]==ids and all(case['completed']is True for case in actual['records']),'all twelve completed records')
  for i,case in enumerate(actual['records']):
   comparison=r['comparisons'][(call-1)*12+i]
   need(equal(comparison,dict(call=call,id=ids[i],classification='matches-node-selected-semantics',actual=case,node=expected['records'][i])),'whole actual comparison row')
 need(r['server']['command']==[plan['wasmtime']['path'],'serve','--addr','127.0.0.1:'+str(r['portLease']['port']),'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','32','--idle-instance-timeout','60s',r['component']['path']],'stock WT/no app mount command')
 need(r['server']['exit']==dict(code=0,signal=None,error=None) and r['server']['shutdownRequested']is True and r['server']['sigintSent']is True and r['server']['forcedCleanup']is False,'actual owned SIGINT0 shutdown')
 for key in ('stdout','stderr'):retained(r['server'][key])
 outer=load('runtime-monitor/observation.json');need(outer['rawExitCode']==0 and outer['ownedGroupsClean']is True and outer['protectedInputsPreserved']is True and outer['observationsValid']is True and outer['nodeSelectedParity']is True,'outer actual success')
 if '--current'in sys.argv:
  refs={r['path']:r for r in capsule['externalDescriptors']}
  refs.update({r['original']['path']:r['original']for r in rows})
  for ref in refs.values():digest(Path(ref['path']).read_bytes(),ref)
 return dict(schemaVersion=1,state='INDEPENDENT_NATIVE_SIGNAL_PIPE_SELECTED_RUNTIME_DATA_REVIEW_PASSED_V1',verifiedPassed=True,retainedFiles=len(rows),
  constructorCommandsRaw0=3,constructorRootRaw0=True,worldMembers=28,worldWitInputs=8,emittedImports=len(audit['emittedImports']),allEmittedVersion='0.2.10',
  nodeOracleHostCaptures=3,nodeOracleCapturedRecords=36,actualGuestReturns=3,actualNodeGuestRecordComparisons=36,allStrictComparisonsMatch=True,
  engine=r['engine'],nativeMetadata=r['nativeMetadata'],component=r['component'],runtimeResult=capsule['runtimeResult'],
  reviewerAuthoredPipeFacade=True,reviewerTargetRerun=False,full31HostCasesClaimed=False,cppSignalPipeToImplementationProved=False,
  nativeQueueRootOrTeardownProved=False,fullNextAcceptance=False,adoption=False,
  preservationScope=capsule['independentReviewScope'],selectedCurrentRowsAtCollection=capsule['selectedRowsRehashedBeforeFinal'])
if __name__=='__main__':print(json.dumps(main(),indent=2))
