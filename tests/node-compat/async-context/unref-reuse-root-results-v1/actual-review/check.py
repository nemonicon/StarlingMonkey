"""Read-only portable DATA reader. No JS/process/oracle/compiler/guest calls."""
from pathlib import Path,PurePosixPath
import hashlib,json,re,sys,tarfile
HERE=Path(__file__).resolve().parent
def need(ok,message):
 if not ok:raise AssertionError(message)
def equal(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(equal(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(equal(x,y)for x,y in zip(a,b))
 return a==b
def digest(data,ref):need(len(data)==ref['bytes']and hashlib.sha256(data).hexdigest()==ref['sha256'],'bytes/hash '+ref['path'])
def clean(t):
 need(type(t['rawExitCode'])is int and t['rawExitCode']==0,'raw0')
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
 rows=cap['files'];need(len(rows)==162 and len({r['path']for r in rows})==162,'retained membership')
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
 plan=load('sources/unref-reuse-wasmtime-collector-v1/plan.json');fixture=load('sources/unref-reuse-candidate-v1/plan.json');cp=readref(c['plan'])
 contract=readref(plan['runtimeContract'])
 need(cap['runtimeResult']['sha256']=='88b54313e8b4b89ba165dd328f2f0b617f7687c0fc37cb8da2fe72663b528300','exact runtime result')
 need(r['state']=='UNREF_REUSE_SELECTED_PARITY_OBSERVED_V1'and r['observationsValid']is True and r['nodeSelectedParity']is True and r['nodePublicProjectionParity']is True,'actual selected success')
 need(r['errors']==[]and r['selectedDifferences']==[]and'safetyStop'not in r,'no expected gaps or failed-state reuse')
 for k in ['applicationMounted','applicationImported','fullNextAcceptance','adoption','nativeBoundaryParityClaimed','nativeOwnerIdentityOrTeardownProved']:need(r[k]is False,k)
 for k in ['inputsPreserved','allThreeCaptureAttemptsComplete','allThreePassingResponsesCaptured','comparisonComplete']:need(r[k]is True,k)
 for k in ['component','componentAudit','constructionResult','constructionCallerIndex','engine','nativeMetadata','engineBuildEvidence','nodeOracleStdout','nodeOracleTerminal','nodeOracleStarted','nodeOracleHostChecks']:need(equal(r[k],a[k]),'Root runtime role '+k)
 need(a['state']=='ROOT_UNREF_REUSE_HTTP_PROBE_AUTHORIZED_V1'and a['firstHostCase']==r['firstHostCase']=='unref-'+r['runId'],'exact Root case')
 need(c['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'and c['passed']is True and c['entryMode']=='unref-reuse'and c['error']is None and c['finalProtection']['unchanged']is True,'actual construction')
 for k in ['ordinaryExportsInvoked','httpServed','appMountedAtInit','metadataFrameProjected','productionProfilePromoted']:need(c[k]is False,'construction scope '+k)
 need(ca['state']=='ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2'and ca['entryMode']=='unref-reuse'and ca['callerIndex']==r['constructionCallerIndex'],'constructor authority')
 need(cp['entries']=={'unref-reuse':plan['probeEntry']}and cp['inputSourceIndex']==plan['probeSourceIndex']==r['probeSourceIndex'],'exact Source/entry')
 need(cp['witDirectory']==fixture['witDirectory']==plan['witDirectory']==str(Path(ca['worldSourceIndex']['path']).parent),'world directory')
 need(ca['worldSourceIndex']==fixture['worldSourceIndex'],'world index')
 for k,v in {'component':r['component'],'componentAudit':r['componentAudit'],'engine':r['engine'],'nativeMetadata':r['nativeMetadata'],'inputSourceIndex':plan['probeSourceIndex'],'inputEntry':plan['probeEntry'],'adapter':plan['adapter']}.items():need(c['artifacts'][k]==v,'constructed artifact '+k)
 native=readref(r['nativeMetadata']);need(native['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1','genuine native generation')
 need(equal(a['metadataExpectedFixedValues'],ca['metadataExpectedFixedValues'])and a['engineBuildEvidence']==ca['engineBuildEvidence'],'same native selection')
 for k,v in a['metadataExpectedFixedValues'].items():need(equal(native[k],v),'actual native fixed field '+k)
 need(native['freshFrontendCompileRows']==1 and native['baselineCompileDatabaseRows']==80 and native['unchangedBaselineCompileDatabaseRows']==79 and native['baselineSeparateEmbeddingRows']==1,'incremental provenance')
 need(native['all80FreshCompilationClaimed']is False and native['oldMetadataProjected']is False,'no old-frame or fresh80 claim')
 need(r['component']['sha256']=='29722cfbac49dd14a74e6f659f162288649fdc5ab60b2a77002be2250a1c846d'and r['engine']['sha256']=='4623640b79b97eb91dc8559b3766fdb430a1807fe90b6ace6c85668a97f13067','binary descriptors')
 for prefix in ['runtime-monitor','constructor-monitor']:
  t=load(prefix+'/terminal.json');clean(t)
  for k in ['stdout','stderr','authority']:retained(t[k])
  need(t['stderr']['bytes']==0,'outer stderr')
  s=load(prefix+'/started.json');need(s['authority']==t['authority']and s['pid']==t['pid'],'outer started/authority')
  need(t['authority']==(r['rootAuthority']if prefix=='runtime-monitor'else c['rootAuthority']),'exact outer Root authority')
 need(load('runtime-monitor/started.json')['timeoutSeconds']==180,'runtime monitor budget')
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
 need(len(init)==1 and init[0]['state']=='NEXT_NATIVE_COMPONENT_API_CAPTURE_COMPLETE_V1'and init[0]['entryMode']=='unref-reuse','whole API capture frame')
 for k in ['component','returnedImports','returnedOwnShape']:need(init[0]['artifacts'][k]==c['artifacts'][k],'API capture artifact '+k)
 outer=[json.loads(x)for x in blobs['constructor-monitor/stdout.log'].splitlines()]
 need(len(outer)==4 and outer[-1]['result']==cap['constructionResult']and outer[-1]['passed']is True and outer[-1]['error']is None,'whole constructor parent JSONL')
 need([x['timeoutSeconds']for x in outer[:3]]==[1800,120,120],'actual child budgets')
 audit=readref(r['componentAudit']);need(audit['passed']is True and audit['entryMode']=='unref-reuse'and audit['component']==r['component'],'actual typed audit')
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
 nt=load('node-oracle/terminal.json');clean(nt);ns=load('node-oracle/started.json')
 need(ns['argv']==[plan['node']['path'],plan['nodeOracleSource']['path']]and ns['timeoutSeconds']==120 and ns['pid']==nt['pid']and ns['authority']==nt['authority'],'original Node command')
 for k in ['stdout','stderr','authority']:retained(nt[k])
 need(nt['stdout']==r['nodeOracleStdout']and nt['stderr']['bytes']==0,'whole Node streams')
 host=readref(r['nodeOracleHostChecks']);phase=next(x for x in host['phases']if x['name']=='node-oracle')
 need(host['hostOnly']is True and host['passed']is True and host['sourceProtectionPassed']is True and host['guestOrEngineOrCompilerOrNetworkExecuted']is False,'host reference scope')
 need(phase['terminal']==r['nodeOracleTerminal']and phase['stdout']==r['nodeOracleStdout']and phase['argv']==ns['argv'],'host phase roles')
 frames=[json.loads(x)for x in blobs['node-oracle/stdout.log'].splitlines()];need(len(frames)==5,'complete Node frames')
 identity=frames[0];need(identity['kind']=='identity'and identity['version']=='v22.14.0'and identity['execArgv']==[]and identity['nativeOrGuestOrEngineExecuted']is False,'original Node identity')
 need(blobs['runtime/node-oracle.stdout.jsonl']==blobs['node-oracle/stdout.log'],'oracle transport')
 need(r['nodeOracleSummary']==frames[4]==host['summary']and r['nodeOracleOriginalCollections']==[x['observed']for x in frames[1:4]],'whole Node collection/summary')
 def validate(value,call,case,mode):
  phase=['A','B','C'][call-1];ctl=contract['controls'][phase]
  need(set(value)==set(contract['requiredKeys'])|({'finalCleanup'}if phase=='C'else set()),'exact collection fields')
  for k,x in contract['requiredConstants'].items():need(equal(value[k],x),'Source constant '+k)
  need(value['phase']==phase and type(value['ordinal'])is int and value['ordinal']==call,'phase/ordinal')
  need(value['firstHostCase']==value['requestedHostCase']==case and value['boundaryMode']==mode,'case/boundary')
  for field in ['checks','callbackChecks']:
   need([x['id']for x in value[field]]==ctl[field+'Ids'],'exact '+field+' IDs')
   need(all(set(x)=={'id','passed'}and x['passed']is True for x in value[field]),'literal checks')
  need(equal(value['counts'],ctl['counts'])and equal(value['plannedHandles'],ctl['plannedHandles']),'counts/local accounting')
  need(len(value['observations'])==len(ctl['observations']),'observation inventory')
  for observed,want in zip(value['observations'],ctl['observations']):
   need(set(observed)==set(want)|{'firstIdentity','secondIdentity'},'observation fields')
   need(observed['firstIdentity']is True and observed['secondIdentity']is True,'actual marker identity')
   for k,x in want.items():need(equal(observed[k],x),'observation '+k)
  if phase=='C':need(equal(value['finalCleanup'],contract['finalCleanup']),'explicit final cleanup')
 def projection(v):return dict(schemaVersion=1,phase=v['phase'],ordinal=v['ordinal'],policy=v['policy'],checks=sorted(v['checks'],key=lambda x:x['id']),callbackChecks=sorted(v['callbackChecks'],key=lambda x:x['id']),counts=v['counts'],observations=v['observations'],delays=v['delays'],plannedPending=v['plannedHandles']['pending'],plannedPeak=v['plannedHandles']['peak'])
 need(len(r['responses'])==len(r['comparisons'])==3,'three whole ordinary returns/comparisons')
 for call,record in enumerate(r['responses'],1):
  value=readref(record['body']);need(value==record['typedPayload']==record['safety']['envelope'],'whole native raw/typed/safety records')
  need(set(value)=={'schemaVersion','marker','call','method','collection'}and type(value['call'])is int and value['call']==call and value['schemaVersion']==1 and value['marker']=='NEXT_NATIVE_UNREF_REUSE_V1'and value['method']=='GET','strict envelope')
  need(record['call']==call and record['status']==200 and record['rawValueType']=='Uint8Array'and record['ordinalValidated']is True and record['safety']['safeToReuse']is True,'safe captured response')
  need(record['safety']['reason']=='strict-native-envelope-and-collection-validated','strict admission')
  actual=value['collection'];node=frames[call]['observed'];need(frames[call]['phase']==['A','B','C'][call-1]and frames[call]['ordinal']==call,'Node whole ordinal')
  validate(actual,call,r['firstHostCase'],'actual-native-private-boundaries');validate(node,call,identity['hostCase'],'node-public-empty-store-projection')
  ap=projection(actual);np=projection(node);need(equal(ap,np),'whole public projection')
  need(equal(r['comparisons'][call-1],dict(call=call,phase=['A','B','C'][call-1],classification='matches-node-public-projection',actualProjection=ap,nodeProjection=np,actualWholeCollection=actual,nodeOriginalWholeCollection=node)),'entire comparison row')
  need(record['callChecksVerified']==len(actual['checks'])and record['cumulativeCallbackChecksVerified']==len(actual['callbackChecks']),'verified counts')
 need(sum(x['callChecksVerified']for x in r['responses'])==r['nativeCallChecksVerified']==r['nodeHostCallChecksVerified']==51,'51 total call checks')
 need([x['cumulativeCallbackChecksVerified']for x in r['responses']]==[0,7,9]and r['nativeDistinctCallbackChecksVerified']==r['nodeHostDistinctCallbackChecksVerified']==9 and r['callbackInventoriesAreCumulativeNotSummed']is True,'nine distinct cumulative callback checks')
 need(r['server']['command']==[plan['wasmtime']['path'],'serve','--addr','127.0.0.1:'+str(r['portLease']['port']),'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','32','--idle-instance-timeout','60s',r['component']['path']],'stock WT/no application mount')
 need(r['server']['exit']==dict(code=0,signal=None,error=None)and r['server']['shutdownRequested']is True and r['server']['sigintSent']is True and r['server']['forcedCleanup']is False,'owned shutdown')
 for k in ['stdout','stderr']:retained(r['server'][k])
 outer=load('runtime-monitor/observation.json');need(outer['rawExitCode']==0 and outer['ownedGroupsClean']is True and outer['protectedInputsPreserved']is True and outer['observationsValid']is True and outer['nodeSelectedParity']is True,'Root actual observation')
 need(outer['result']==cap['runtimeResult'],'Root exact result descriptor')
 if'--current'in sys.argv:
  refs={x['path']:x for x in cap['externalDescriptors']};refs.update({x['original']['path']:x['original']for x in rows})
  for ref in refs.values():digest(Path(ref['path']).read_bytes(),ref)
 return dict(schemaVersion=1,state='INDEPENDENT_UNREF_REUSE_SELECTED_RUNTIME_DATA_REVIEW_PASSED_V1',verifiedPassed=True,
  retainedFiles=len(rows),constructorCommandsRaw0=3,constructorParentRaw0=True,runtimeParentRaw0=True,worldMembers=28,worldWitInputs=8,
  emittedImports=len(audit['emittedImports']),allEmittedVersion='0.2.10',actualGuestCalls=3,originalNodeCalls=3,
  totalCallChecks=51,distinctCumulativeCallbackChecks=9,cumulativeCallbackInventoryLengths=[0,7,9],allPublicProjectionsMatch=True,
  oldACallbackDuringBWithOriginalMarkers=True,cancelCandidateObservedCallbacks=0,explicitLocalPendingAfterClear=0,
  engine=r['engine'],nativeMetadata=r['nativeMetadata'],component=r['component'],runtimeResult=cap['runtimeResult'],
  reviewerAuthoredOriginalAlsAndConstructorTooling=True,targetRerun=False,nativeQueueOrCountsProved=False,
  physicalStoreOrNativeOwnerIdentityProved=False,gcRootReleaseOrTeardownProved=False,permanentCancellationOrTimerAccuracyProved=False,
  fullNextAcceptance=False,adoption=False,protectionScope=cap['independentReviewScope'],selectedCurrentDescriptors=cap['selectedRowsRehashedBeforeFinal'])
if __name__=='__main__':print(json.dumps(main(),indent=2))
