"""Read-only portable DATA reader. No JS/process/oracle/compiler/guest calls."""
from pathlib import Path,PurePosixPath
import base64,codecs,hashlib,json,re,sys,tarfile
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
def checked(ref):
 data=Path(ref['path']).read_bytes();digest(data,ref);return data
def app_guard(inventory,copy_root,root_identity):
 identities=[]
 for kind,root in [('source',Path(inventory['root'])),('copy',copy_root)]:
  assert root.resolve()==root and root.is_dir() and not root.is_symlink()
  st=root.stat();actual=dict(dev=st.st_dev,ino=st.st_ino,nlink=st.st_nlink,mode=st.st_mode&0o777)
  if kind=='source':assert actual==root_identity
  else:assert actual['mode']==0o555 and (st.st_dev,st.st_ino)!=(root_identity['dev'],root_identity['ino'])
  identities.append([kind,'.',st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
  nodes=list(root.rglob('*'));assert not any(p.is_symlink()for p in nodes)
  assert all(p.is_file()or p.is_dir()for p in nodes)
  assert{p.relative_to(root).as_posix()for p in nodes if p.is_file()}=={r['path']for r in inventory['files']}
  assert{p.relative_to(root).as_posix()for p in nodes if p.is_dir()}=={r['path']for r in inventory['directories']}
  assert not(root/'.next/cache').exists()
  for r in inventory['files']:
   p=root/r['path'];checked(dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']));st=p.stat()
   if kind=='source':assert(st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777)==(r['dev'],r['ino'],r['nlink'],r['mode'])
   else:assert st.st_nlink==1 and st.st_mode&0o777==0o444 and(st.st_dev,st.st_ino)!=(r['dev'],r['ino'])
   identities.append([kind,r['path'],st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
  for r in inventory['directories']:
   p=root/r['path'];st=p.stat()
   if kind=='source':assert(st.st_dev,st.st_ino,st.st_mode&0o777)==(r['dev'],r['ino'],r['mode'])
   else:assert st.st_mode&0o777==0o555
   identities.append([kind,r['path'],st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
 cache=copy_root.parent/'cache';st=cache.lstat();assert cache.is_dir() and not cache.is_symlink() and cache.resolve()==cache and st.st_mode&0o777==0o700
 assert list(cache.iterdir())==[]
 identities.append(['separate-cache','.',st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
 return dict(filesPerTree=len(inventory['files']),directoriesExcludingRoot=len(inventory['directories']),directoriesPerTree=1+len(inventory['directories']),bytesPerTree=inventory['bytes'],
  sourceRootIdentity=root_identity,sourceMatchesPublishedIdentity=True,copyByteIdenticalDistinctInodesAndReadOnlyModes=True,
  sourceAndCopyHaveNoCacheMountpoint=True,separateHostCacheReal0700AndEmpty=True,
  combinedIdentitySha256=hashlib.sha256(json.dumps(identities,separators=(',',':')).encode()).hexdigest())
def main():
 if(HERE/'index.json').exists():
  own=json.loads((HERE/'index.json').read_bytes());names=[r['path']for r in own['files']]
  need(len(names)==len(set(names)),'duplicate own member')
  need(set(names)|{'index.json'}=={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()},'own membership')
  need(not any(p.is_symlink()for p in HERE.rglob('*')),'own symlink')
  for r in own['files']:digest((HERE/r['path']).read_bytes(),dict(r,path=r['path']))
 cap=json.loads((HERE/'capsule.json').read_bytes());digest((HERE/'data.tar.gz').read_bytes(),cap['archive'])
 rows=cap['files'];need(len(rows)==cap['retainedFiles'] and len({r['path']for r in rows})==len(rows),'retained membership')
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
 r=load('runtime/result.json');a=readref(r['rootAuthority']);p=load('sources/wasmcloud-cold-candidate-v4/plan.json');contract=load('sources/wasmcloud-cold-candidate-v4/cold-contract.json')
 need(cap['runtimeResult']['sha256']=='6d959823d9f9b54782ecfb0f093c84ee593557cad40851315fc9cef1995271cb','exact failed result')
 need(r['state']=='NEXT_WASMCLOUD_EIGHT_COLD_REQUESTS_PASSED_UNREVIEWED_V1'and r['passed']is True,'actual bounded cold success')
 for k in ['eightCaptured','originalInputsPreserved','readonlyAppPreserved','configVerifiedBeforeDev','contractsPassed','selected13InstantiationDemonstrated','allDirectCliExitsZero']:need(r[k]is True,k)
 for k in ['physicalInstanceIdentityObserved','cacheSequenceExecuted','browserExecuted','retainedContractAcceptance','fullNextAcceptance','adoption','readonlyWasiDescriptorRightsProved']:need(r[k]is False,k)
 need(r['errors']==[],'no hidden collector exception')
 for k in ['sourceIndex','component','componentAudit','engine','nativeMetadata','engineBuildEvidence','constructionResult','inputEntry','inputSourceIndex','wash','applicationInputs']:need(r[k]==a[k],'Root role '+k)
 need(a['state']=='ROOT_NEXT_WASMCLOUD_COLD_AUTHORIZED_V1'and r['worldFamily']==p['worldFamily']['sourceIndex'],'whole world Source selection')
 for k,want in p['expectedArtifacts'].items():need({q:a[k][q]for q in ['sha256','bytes']}==want,'exact selected artifact '+k)
 need(r['engine']['sha256']=='4623640b79b97eb91dc8559b3766fdb430a1807fe90b6ace6c85668a97f13067'and r['component']['sha256']=='1c3108d2fdce72a1bfa8cc64a0e6e0645acd71223b26b6dc11d037d4a95efe83','same prior successful native artifact')
 c=readref(r['constructionResult']);audit=readref(r['componentAudit']);native=readref(r['nativeMetadata']);ctor=readref(c['rootAuthority']);cp=readref(c['plan'])
 need(c['passed']is True and c['entryMode']=='real-next'and c['error']is None and c['finalProtection']['unchanged']is True,'existing construction')
 need(c['callerIndex']==a['constructionCallerIndex']and cp['witDirectory']==str(Path(r['worldFamily']['path']).parent),'actual constructor/world directory')
 for k in ['component','componentAudit','engine','nativeMetadata','inputEntry','inputSourceIndex']:need(c['artifacts'][k]==a[k],'constructor artifact '+k)
 need(native['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'and native['engine']==r['engine'],'genuine incremental metadata')
 need(ctor['metadataExpectedFixedValues']==a['metadataExpectedFixedValues']and ctor['engineBuildEvidence']==r['engineBuildEvidence'],'native Root generation joins')
 for k,v in a['metadataExpectedFixedValues'].items():need(equal(native[k],v),'actual native fixed field '+k)
 need(audit['passed']is True and audit['component']==r['component']and sorted(audit['emittedImports'])==sorted(p['selectedInterfaces'])and len(set(audit['emittedImports']))==13,'artifact exact selected13 set')
 need(audit['exports']==['wasi:http/incoming-handler@0.2.10']and audit['allEmittedVersion']=='0.2.10'and audit['noExternalPreview1OrCustomImports']is True,'artifact standard interface scope')
 for command in c['commands']:
  t=readref(command['terminal']);clean(t)
  for k in ['stdout','stderr']:need(t[k]==command[k],'historic constructor stream');retained(t[k])
 app=readref(r['applicationInputs']);need(app['root']==a['applicationSource']and app['regularFiles']==len(app['files'])==2181 and app['bytes']==48714867 and len(app['directories'])==425,'actual app input inventory')
 need(r['applicationCopy']==dict(files=2181,bytes=48714867,sourceDirectoriesExcludingRoot=425,ownedDirectoriesIncludingRoot=426,ownedAdditionalDirectories=[],byteIdentical=True,independentInodes=True,filesMode='0444',directoryMode='0555'),'application copy scope')
 need(cap['applicationCurrentBeforeFinal']['filesPerTree']==2181 and cap['applicationCurrentBeforeFinal']['copyByteIdenticalDistinctInodesAndReadOnlyModes']is True,'independent current app guard')
 need(app['schemaVersion']==1 and app['symlinks']==[] and all(x['path']!='.'for x in app['directories']),'fresh explicit root-excluded schema')
 need(r['applicationSchema']==p['applicationSchema']and r['sourceRootIdentity']==p['applicationRootIdentity'],'explicit source root and schema joins')
 need(r['applicationSchema']==dict(name='fresh-next-standalone-root-excluded-v1',sourceDirectoriesExcludeRoot=True,files=2181,bytes=48714867,directoriesExcludingRoot=425,additionalDirectories=[],ownedDirectoriesIncludingRoot=426),'cold exact source/copy policy')
 need(r['ownedAdditionalDirectories']==[]and r['cacheInventory']==[],'no additional app directory; empty independent host cache')
 build=readref(r['applicationBuildResult']);need(r['applicationBuildResult']==p['applicationBuildResult'],'fresh actual build selected')
 need(build['passed']is True and build['state']=='NEXT_APP_BUILD_PASSED_UNREVIEWED_V1'and build['errors']==[]and build['originalInputsPreserved']is True,'actual fresh app build success')
 need(build['applicationInventoryDescriptor']==r['applicationInputs']and build['applicationInventory']==app,'whole fresh app build/inventory join')
 need(build['installedVersions']==build['installedVersionsBeforeNextBuild']=={'next':'16.4.5','react':'19.3.1','react-dom':'19.3.1'},'actual unchanged dependency versions')
 need(cap['applicationCurrentBeforeFinal']['directoriesPerTree']==426 and cap['applicationCurrentBeforeFinal']['directoriesExcludingRoot']==425,'current root-inclusive copy accounting')
 need(cap['applicationCurrentBeforeFinal']['sourceAndCopyHaveNoCacheMountpoint']is True and cap['applicationCurrentBeforeFinal']['separateHostCacheReal0700AndEmpty']is True,'actual independent cache and exact app membership')
 world=readref(r['worldFamily']);base=Path(r['worldFamily']['path']).parent
 wit=[x for x in world['files']if x['path'].endswith('.wit')];need(wit==p['fixedWit']['files'],'all eight fixed WIT')
 need(len(r['worldBefore'])==38 and sum(x['kind']=='file'for x in r['worldBefore'])==29,'whole world identity transport')
 need(sorted(x['relativePath']for x in r['worldBefore']if x['kind']=='directory')==p['worldFamily']['directories'],'exact world directory set')
 need(all(x['nlink']==1 for x in r['worldBefore']if x['kind']=='file'),'world no file aliases')
 need([x['label']for x in r['commands']]==['config-show','wash-dev'],'only two actual CLI commands')
 config,dev=r['commands'];need(config['exit']==dict(code=0,signal=None,error=None)and dev['exit']==dict(code=0,signal=None,error=None),'actual config0/dev0')
 for command in r['commands']:
  need(command['timeout']is False and command['forcedCleanup']is False,'no CLI timeout/forced cleanup')
  for k in ['stdout','stderr']:retained(command[k])
 need(dev==r['server']and dev['shutdownRequested']is True and dev['sigintSent']is True,'planned owned SIGINT0')
 output=r['outputRoot'];project=output+'/project';empty=output+'/empty-user-config.json'
 need(config['argv']==[r['wash']['path'],'--user-config',empty,'-C',project,'--output','json','config','show'],'exact config argv')
 need(dev['argv']==[r['wash']['path'],'--user-config',empty,'-C',project,'--log-level','info','--meters','duration','dev'],'exact dev argv')
 configured=r['configured'];effective=r['effectiveConfiguration'];shown=readref(config['stdout']);need(shown['success']is True and shown['data']==effective,'whole effective config output')
 need(configured['version']==effective['version']=='2.11.0'and configured['build']==effective['build'],'same stock config build')
 for k in ['address','command','component_path','service','volumes']:need(configured['dev'][k]==effective['dev'][k],'effective dev '+k)
 need(configured['dev']['service']is False and configured['dev']['volumes']==[dict(host_path=output+'/app',guest_path='/app'),dict(host_path=output+'/cache',guest_path='/app/.next/cache')],'only app and nested cache')
 for k in ['components','plugins','host_plugins']:need(effective['dev'].get(k,[])==[],'no services/plugins')
 for k in ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts']:need(effective['workload'][k]==[],'no egress '+k)
 need(effective['workload']['environment']['config']==dict(STARLING_NEXT_ORIGIN=r['portLease']['origin'],NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1'),'explicit workload environment')
 need(effective['wit']['skip_fetch']is True and r['readiness']['tcpConnect']is True and r['readiness']['workloadRegistered']is True and r['readiness']['extraHttpRequests']==0 and r['readiness']['origin']==r['portLease']['origin'],'post-registration and TCP gate')
 need(r['portLease']['heldThroughConfigInspection']is True and r['portLease']['releasedImmediatelyBeforeSingleDevLaunch']is True and r['portLease']['fallbackAllowed']is False,'single leased port')
 for ref in r['configFiles']:retained(ref)
 need(blobs['runtime/empty-user-config.json']==b'{}\n','empty private user config')
 need([x['id']for x in r['responses']]==[x['id']for x in contract['requests']]and len(r['responses'])==8,'all eight finite attempts')
 for response,request in zip(r['responses'],contract['requests']):
  need(response['complete']is True and response['status']==request['status']==200 and response['method']==request['method']and response['path']==request['path'],'actual complete successful request')
  retained(response['body']);retained(response['chunkRecord']);body=origins[response['body']['path']][0]
  chunks=readref(response['chunkRecord']);need(chunks==response['chunks'],'whole chunk records')
  parts=[];decoder=codecs.getincrementaldecoder('utf8')('strict');text='';shell=ready=-1
  for index,chunk in enumerate(chunks):
   need(set(chunk)=={'base64','bytes'},'chunk fields');part=base64.b64decode(chunk['base64'],validate=True);need(len(part)==chunk['bytes'],'chunk bytes');parts.append(part)
   text+=decoder.decode(part,final=False)
   if shell<0 and'NEXT_STREAM_SHELL'in text:shell=index
   if ready<0 and'NEXT_STREAM_READY'in text:ready=index
  text+=decoder.decode(b'',final=True);need(b''.join(parts)==body and text==body.decode('utf8'),'whole body and strict UTF8')
  need(response['shellChunk']==shell and response['readyChunk']==ready,'actual marker chunk boundaries')
  for marker in request.get('includes',[]):need(marker in text,'expected response marker '+marker)
  if'json'in request:
   value=json.loads(text)
   for k,want in request['json'].items():need(equal(value[k],want),'exact typed JSON contract '+k)
  if request.get('stream'):need(ready>shell>=0,'strict shell before ready in later chunk')
  need(response['wireSha256']is None and response['contract']==dict(passed=True,failures=[]),'decoded bytes and unweakened contract')
 readiness=r['readiness'];need(readiness['workloadRegistered']is True and readiness['tcpConnect']is True and readiness['extraHttpRequests']==0,'combined readiness')
 retained(p['readinessPolicy']['sourceFile']);source=origins[p['readinessPolicy']['sourceFile']['path']][0]
 digest(source,p['readinessPolicy']['sourceFile']);need(readiness['source']==p['readinessPolicy']['sourceFile'],'pinned marker Source')
 need(hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()==p['readinessPolicy']['gitBlobSha1'],'primary Git blob')
 source=source.decode();awaited=source.index('let workload_id = reload_component(host.clone(), &workload, None).await?;');marker=source.index('"listening for HTTP requests"');shutdown=source.index('let shutdown = shutdown.ready();')
 need(awaited<marker<shutdown and'response.workload_status.workload_state != WorkloadState::Running'in source,'await Running before exact marker')
 events=readiness['completionEvents'];need(len(events)==1,'single positive registration marker')
 event=events[0];log=origins[dev[event['stream']]['path']][0].decode();line=log.splitlines()[event['lineNumber']-1]
 need(event['line']==line and' INFO listening for HTTP requests address='+r['portLease']['origin']in line and event['address']==r['portLease']['origin'],'actual exact leased post-registration marker')
 need('no workload registered'not in origins[dev['stderr']['path']][0].decode(),'no premature routing warning in this attempt')
 need(p['readinessPolicy']['extraHttpRequests']==0 and p['readinessPolicy']['capSeconds']==60,'no HTTP retry gate')
 t=load('runtime-monitor/terminal.json');clean(t,0);started=load('runtime-monitor/started.json')
 need(started['authority']==t['authority']==r['rootAuthority']and started['pid']==t['pid']and started['timeoutSeconds']==600,'original600 owner')
 need(started['argv']==[p['node']['path'],str(Path(r['sourceIndex']['path']).parent/'deploy.mjs'),r['rootAuthority']['path']],'exact actor argv')
 for k in ['stdout','stderr','authority']:retained(t[k])
 outer=load('runtime-monitor/observation.json');need(outer['rawExitCode']==0 and outer['ownedGroupsClean']is True and outer['protectedInputsPreserved']is True and outer['passed']is True and outer['result']==cap['runtimeResult'],'actual clean raw0 success')
 events=[load(name)for name in sorted(blobs)if name.startswith('runtime-monitor/owned-')]
 need([x['sequence']for x in events]==list(range(len(events)))and len(events)==len(t['observedProcesses']),'complete observed process event transport')
 need(all(x['process']in t['observedProcesses']for x in events),'owned event/process joins')
 need(outer['terminal']==cap['files'][next(i for i,x in enumerate(cap['files'])if x['path']=='runtime-monitor/terminal.json')]['original'],'outer/terminal descriptor join')
 admission=load('root/launch-admission.json');need(admission['state']=='ROOT_FRESH_NEXT_COLD_V4_START_ADMITTED_V1'and admission['freeBytes']==1521770496 and admission['minimumFreeBytes']==a['rootLaunchMinimumFreeBytes']==1073741824 and admission['freeBytes']>=admission['minimumFreeBytes'],'actual conservative Root start admission')
 need(admission['continuousDiskGuardClaimed']is False,'no continuous disk guard')
 need(admission['argv'][1:]==['-I','-B',str(Path(r['sourceIndex']['path']).parent/'run-owned.py'),r['rootAuthority']['path']],'Root actual owner argv')
 need(blobs['root/first-cli.stderr.log']==b'','Root CLI stderr')
 cli=[json.loads(x)for x in blobs['root/first-cli.stdout.log'].splitlines()];need(cli[-1]==outer and cli[0]['pid']==t['pid']and cli[0]['timeoutSeconds']==600,'complete actual Root CLI stdout frame joins')
 for role,cap_seconds in [('stock',300),('native',600)]:
  pr=load('first-pair/'+role+'/result.json');po=load('first-pair/'+role+'/observation.json');pt=load('first-pair/'+role+'/terminal.json');ps=load('first-pair/'+role+'/started.json');clean(pt)
  need(po['rawExitCode']==0 and po['protectedInputsPreserved']is True and po['ownedGroupsClean']is True and po.get('hostExperimentPassed',po.get('passed'))is True,'prior paired gate '+role)
  need(ps['authority']==pt['authority']and ps['pid']==pt['pid']and ps['timeoutSeconds']==cap_seconds,'prior paired monitor '+role)
  retained(pt['authority'])
  rr=next(x['original']for x in cap['files']if x['path']=='first-pair/'+role+'/result.json');need(po['result']==rr,'prior paired result descriptor '+role)
  if role=='native':
   client=load('first-pair/native/client-result.json');need(pr['passed']is True and pr['originalInputsPreserved']is True and pr['readonlyAppPreserved']is True,'prior native aggregate')
   need(pr['component']==r['component']and pr['constructionResult']==r['constructionResult'],'same native artifact in prior paired gate')
   guard=load('first-pair/native/world-guard.json');need(guard['before']==guard['after']and guard['unchanged']is guard['nativeInputsPreserved']is True and guard['authority']==pt['authority'],'prior paired whole-world receipt')
  else:client=pr;need(pr['originalInputsPreserved']is True,'prior stock source protection')
  need(client['passed']is True and len(client['http'])==24 and all(x['passed']is True for x in client['http']),'prior unchanged 24HTTP '+role)
  need(client['cacheInvalidation']['passed']is True and client['streaming']['complete']is True and client['streaming']['incrementalDeliveryObserved']is True,'prior cache/stream gate '+role)
  browser=client['browser'];need(browser['passed']is True and len(browser['tests'])==2 and all(x['passed']is True for x in browser['tests']),'prior strict browser gate '+role)
  need(client['errors']==[]and client['transportErrors']==[]and browser['errors']==[],'prior strict errors '+role)
 if'--current'in sys.argv:
  refs={x['path']:x for x in cap['externalDescriptors']};refs.update({x['original']['path']:x['original']for x in rows})
  for ref in refs.values():digest(Path(ref['path']).read_bytes(),ref)
  need(app_guard(app,Path(output)/'app',p['applicationRootIdentity'])==cap['applicationCurrentBeforeFinal'],'current source/copied app bookend')
  for identity in r['worldBefore']:
   q=base/identity['relativePath'];s=q.stat();need((s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777)==(identity['dev'],identity['ino'],identity['nlink'],identity['mode']),'current world identity')
 return dict(schemaVersion=1,state='INDEPENDENT_WASMCLOUD_EIGHT_COLD_REQUESTS_DATA_REVIEW_PASSED_V4',verifiedPassed=True,
  actualColdPassed=True,actualRawExitCode=0,ownedGroupsClean=True,protectedInputsPreserved=True,requestsCaptured=8,
  allEightHttp200AndContractsPassed=True,configShowExit=0,washDevExitAfterSigint=0,postRegistrationAndTcpObserved=True,
  extraHttpReadinessRequests=0,strictStreamShellChunk=r['responses'][-1]['shellChunk'],strictStreamReadyChunk=r['responses'][-1]['readyChunk'],
  strictStreamChunks=len(r['responses'][-1]['chunks']),artifactSelectedStandardImports=13,
  sourceAppFiles=2181,copiedAppFiles=2181,currentAppBytesPerTree=48714867,sourceDirectoriesExcludingRoot=425,ownedDirectoriesIncludingRoot=426,appModeScope='physical0444/0555 only; no WASI descriptor rights proof',
  sourceWorldFilesIncludingIndex=29,sourceWorldDirectories=9,worldWitInputs=8,
  component=r['component'],engine=r['engine'],nativeMetadata=r['nativeMetadata'],runtimeResult=cap['runtimeResult'],
  retainedFiles=len(rows),selectedArtifactDescriptors=cap['selectedRowsRehashedBeforeFinal'],
  reviewerPriorV1SourcePassMissedRegistrationGate=True,reviewerAuthoredEarlierAlsConstructorToolingAndAppCli=True,
  worldCurrentBeforeFinalIdentitySha256=cap['worldCurrentBeforeFinalIdentitySha256'],sourceDerivedFreshStorePolicyIsObservedIdentity=False,targetRerun=False,cacheSequenceExecuted=False,browserExecuted=False,
  retained24HttpPlus2BrowserAcceptance=False,fullNodeOrNativeCleanupOrPerformanceProved=False,fullNextAcceptance=False,
  adoption=False,protectionScope=cap['protectionScope'])
if __name__=='__main__':print(json.dumps(main(),indent=2))
