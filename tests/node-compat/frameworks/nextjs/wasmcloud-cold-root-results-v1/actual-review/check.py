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
def app_guard(inventory,copy_root):
 identities=[]
 for kind,root in [('source',Path(inventory['root'])),('copy',copy_root)]:
  nodes=list(root.rglob('*'));assert not any(p.is_symlink()for p in nodes)
  assert{p.relative_to(root).as_posix()for p in nodes if p.is_file()}=={r['path']for r in inventory['files']}
  assert{'.'}|{p.relative_to(root).as_posix()for p in nodes if p.is_dir()}=={r['path']for r in inventory['directories']}
  for r in inventory['files']:
   p=root/r['path'];digest(p.read_bytes(),dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']));s=p.stat()
   if kind=='source':assert(s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777)==(r['dev'],r['ino'],r['nlink'],r['mode'])
   else:assert s.st_nlink==1 and s.st_mode&0o777==0o444 and(s.st_dev,s.st_ino)!=(r['dev'],r['ino'])
   identities.append([kind,r['path'],s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777])
  for r in inventory['directories']:
   p=root/r['path'];s=p.stat()
   if kind=='source':assert(s.st_dev,s.st_ino,s.st_mode&0o777)==(r['dev'],r['ino'],r['mode'])
   else:assert s.st_mode&0o777==0o555
   identities.append([kind,r['path'],s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777])
 return dict(filesPerTree=len(inventory['files']),directoriesPerTree=len(inventory['directories']),bytesPerTree=inventory['bytes'],
  sourceMatchesPublishedIdentity=True,copyByteIdenticalDistinctInodesAndReadOnlyModes=True,
  combinedIdentitySha256=hashlib.sha256(json.dumps(identities,separators=(',',':')).encode()).hexdigest())
def main():
 if(HERE/'index.json').exists():
  own=json.loads((HERE/'index.json').read_bytes());names=[r['path']for r in own['files']]
  need(len(names)==len(set(names)),'duplicate own member')
  need(set(names)|{'index.json'}=={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()},'own membership')
  need(not any(p.is_symlink()for p in HERE.rglob('*')),'own symlink')
  for r in own['files']:digest((HERE/r['path']).read_bytes(),dict(r,path=r['path']))
 cap=json.loads((HERE/'capsule.json').read_bytes());digest((HERE/'data.tar.gz').read_bytes(),cap['archive'])
 rows=cap['files'];need(len(rows)==101 and len({r['path']for r in rows})==101,'retained membership')
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
 r=load('runtime/result.json');a=readref(r['rootAuthority']);p=load('sources/wasmcloud-cold-candidate-v1/plan.json');contract=load('sources/wasmcloud-cold-candidate-v1/cold-contract.json')
 need(cap['runtimeResult']['sha256']=='1c691de2fbf12cf62b56df9d7f40a29a0e5877d53868283756ec82ce90833fb4','exact failed result')
 need(r['state']=='NEXT_WASMCLOUD_COLD_FAILED_UNACCEPTED_V1'and r['passed']is False,'preserve actual failure')
 for k in ['eightCaptured','originalInputsPreserved','readonlyAppPreserved','configVerifiedBeforeDev']:need(r[k]is True,k)
 for k in ['contractsPassed','selected13InstantiationDemonstrated','allDirectCliExitsZero','physicalInstanceIdentityObserved','cacheSequenceExecuted','browserExecuted','retainedContractAcceptance','fullNextAcceptance','adoption','readonlyWasiDescriptorRightsProved']:need(r[k]is False,k)
 need(r['errors']==[],'no hidden collector exception')
 for k in ['sourceIndex','component','componentAudit','engine','nativeMetadata','engineBuildEvidence','constructionResult','inputEntry','inputSourceIndex','wash','applicationInputs']:need(r[k]==a[k],'Root role '+k)
 need(a['state']=='ROOT_NEXT_WASMCLOUD_COLD_AUTHORIZED_V1'and r['worldFamily']==p['worldFamily']['sourceIndex']==a['inputSourceIndex'],'whole world Source selection')
 for k,want in p['expectedArtifacts'].items():need({q:a[k][q]for q in ['sha256','bytes']}==want,'exact selected artifact '+k)
 need(r['engine']['sha256']=='4623640b79b97eb91dc8559b3766fdb430a1807fe90b6ace6c85668a97f13067'and r['component']['sha256']=='55f05e3d75b199c6a9e2afa54c7bfe3e2ba6d506324cb896b4d6c4c122f09f70','same prior successful native artifact')
 c=readref(r['constructionResult']);audit=readref(r['componentAudit']);native=readref(r['nativeMetadata']);ctor=readref(c['rootAuthority']);cp=readref(c['plan'])
 need(c['passed']is True and c['entryMode']=='real-next'and c['error']is None and c['finalProtection']['unchanged']is True,'existing construction')
 need(c['callerIndex']==a['constructionCallerIndex']and cp['witDirectory']==str(Path(a['inputSourceIndex']['path']).parent),'actual constructor/world directory')
 for k in ['component','componentAudit','engine','nativeMetadata','inputEntry','inputSourceIndex']:need(c['artifacts'][k]==a[k],'constructor artifact '+k)
 need(native['metadataKind']=='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'and native['engine']==r['engine'],'genuine incremental metadata')
 need(ctor['metadataExpectedFixedValues']==a['metadataExpectedFixedValues']and ctor['engineBuildEvidence']==r['engineBuildEvidence'],'native Root generation joins')
 for k,v in a['metadataExpectedFixedValues'].items():need(equal(native[k],v),'actual native fixed field '+k)
 need(audit['passed']is True and audit['component']==r['component']and sorted(audit['emittedImports'])==sorted(p['selectedInterfaces'])and len(set(audit['emittedImports']))==13,'artifact exact selected13 set')
 need(audit['exports']==['wasi:http/incoming-handler@0.2.10']and audit['allEmittedVersion']=='0.2.10'and audit['noExternalPreview1OrCustomImports']is True,'artifact standard interface scope')
 for command in c['commands']:
  t=readref(command['terminal']);clean(t)
  for k in ['stdout','stderr']:need(t[k]==command[k],'historic constructor stream');retained(t[k])
 app=readref(r['applicationInputs']);need(app['root']==a['applicationSource']and app['regularFiles']==len(app['files'])==2218 and app['bytes']==48808299 and len(app['directories'])==455,'actual app input inventory')
 need(r['applicationCopy']==dict(files=2218,bytes=48808299,byteIdentical=True,independentInodes=True,filesMode='0444',directoryMode='0555'),'application copy scope')
 need(cap['applicationCurrentBeforeFinal']['filesPerTree']==2218 and cap['applicationCurrentBeforeFinal']['copyByteIdenticalDistinctInodesAndReadOnlyModes']is True,'independent current app guard')
 world=readref(a['inputSourceIndex']);base=Path(a['inputSourceIndex']['path']).parent
 wit=[x for x in world['files']if x['path'].endswith('.wit')];need(wit==p['fixedWit']['files'],'all eight fixed WIT')
 need(len(r['worldBefore'])==26 and sum(x['kind']=='file'for x in r['worldBefore'])==17,'whole world identity transport')
 need(sorted(x['relativePath']for x in r['worldBefore']if x['kind']=='directory')==p['worldFamily']['directories'],'exact world directory set')
 need(all(x['nlink']==1 for x in r['worldBefore']if x['kind']=='file'),'world no file aliases')
 need([x['label']for x in r['commands']]==['config-show','wash-dev'],'only two actual CLI commands')
 config,dev=r['commands'];need(config['exit']==dict(code=0,signal=None,error=None)and dev['exit']==dict(code=130,signal=None,error=None),'actual config0/dev130')
 for command in r['commands']:
  need(command['timeout']is False and command['forcedCleanup']is False,'no CLI timeout/forced cleanup')
  for k in ['stdout','stderr']:retained(command[k])
 need(dev==r['server']and dev['shutdownRequested']is True and dev['sigintSent']is True,'planned SIGINT during readiness race')
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
 need(effective['wit']['skip_fetch']is True and r['readiness']==dict(tcpConnect=True,extraHttpRequests=0,origin=r['portLease']['origin']),'actual inadequate TCP-only gate')
 need(r['portLease']['heldThroughConfigInspection']is True and r['portLease']['releasedImmediatelyBeforeSingleDevLaunch']is True and r['portLease']['fallbackAllowed']is False,'single leased port')
 for ref in r['configFiles']:retained(ref)
 need(blobs['runtime/empty-user-config.json']==b'{}\n','empty private user config')
 need([x['id']for x in r['responses']]==[x['id']for x in contract['requests']]and len(r['responses'])==8,'all eight finite attempts')
 for response,request in zip(r['responses'],contract['requests']):
  need(response['complete']is True and response['status']==404 and response['method']==request['method']and response['path']==request['path'],'actual empty404 request')
  retained(response['body']);retained(response['chunkRecord'])
  need(origins[response['body']['path']][0]==b''and readref(response['chunkRecord'])==response['chunks']==[],'whole empty body/chunks')
  need(response['body']['bytes']==0 and response['wireSha256']is None and response['contract']['passed']is False and response['contract']['failures'][0]=='status 404 != 200','no false body/wire/contract claim')
  need(response['shellChunk']==response['readyChunk']==-1,'no stream markers')
 log=origins[dev['stderr']['path']][0].decode();need('HTTP server listening'in log and'development session started, building and deploying component'in log,'early startup log order')
 need(log.index('HTTP server listening')<log.index('development session started, building and deploying component'),'listener before workload build')
 need('failed to route incoming request err=no workload registered'in log and'listening for HTTP requests'not in log,'routing failure/no positive registration marker observed')
 t=load('runtime-monitor/terminal.json');clean(t,1);started=load('runtime-monitor/started.json')
 need(started['authority']==t['authority']==r['rootAuthority']and started['pid']==t['pid']and started['timeoutSeconds']==600,'original600 owner')
 need(started['argv']==[p['node']['path'],str(Path(r['sourceIndex']['path']).parent/'deploy.mjs'),r['rootAuthority']['path']],'exact actor argv')
 for k in ['stdout','stderr','authority']:retained(t[k])
 outer=load('runtime-monitor/observation.json');need(outer['rawExitCode']==1 and outer['ownedGroupsClean']is True and outer['protectedInputsPreserved']is True and outer['passed']is False and outer['result']==cap['runtimeResult'],'preserve clean raw1 failure')
 if'--current'in sys.argv:
  refs={x['path']:x for x in cap['externalDescriptors']};refs.update({x['original']['path']:x['original']for x in rows})
  for ref in refs.values():digest(Path(ref['path']).read_bytes(),ref)
  need(app_guard(app,Path(output)/'app')==cap['applicationCurrentBeforeFinal'],'current source/copied app bookend')
  for identity in r['worldBefore']:
   q=base/identity['relativePath'];s=q.stat();need((s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777)==(identity['dev'],identity['ino'],identity['nlink'],identity['mode']),'current world identity')
 return dict(schemaVersion=1,state='INDEPENDENT_WASMCLOUD_COLD_READINESS_FAILURE_DATA_REVIEW_PASSED_V1',verifiedPassed=True,
  actualColdPassed=False,actualRawExitCode=1,ownedGroupsClean=True,protectedInputsPreserved=True,requestsCaptured=8,
  completeEmpty404Responses=8,configShowExit=0,washDevExitAfterSigint=130,componentRegistrationObserved=False,
  nextRouteExecutionOrInstantiationDemonstrated=False,artifactSelectedStandardImports=13,
  sourceAppFiles=2218,copiedAppFiles=2218,currentAppBytesPerTree=48808299,appModeScope='physical0444/0555 only; no WASI descriptor rights proof',
  sourceWorldFilesIncludingIndex=17,sourceWorldDirectories=9,worldWitInputs=8,
  component=r['component'],engine=r['engine'],nativeMetadata=r['nativeMetadata'],runtimeResult=cap['runtimeResult'],
  retainedFiles=len(rows),selectedArtifactDescriptors=cap['selectedRowsRehashedBeforeFinal'],
  reviewerPreviousSourcePassMissedWorkloadRegistrationGate=True,reviewerAuthoredEarlierAlsAndConstructorTooling=True,
  sourceDerivedFreshStorePolicyIsObservedIdentity=False,targetRerun=False,retainedContractAcceptance=False,
  fullNextAcceptance=False,adoption=False,protectionScope=cap['protectionScope'])
if __name__=='__main__':print(json.dumps(main(),indent=2))
