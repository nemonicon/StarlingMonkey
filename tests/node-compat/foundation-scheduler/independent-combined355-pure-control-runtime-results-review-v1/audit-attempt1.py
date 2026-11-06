"""Independent actual DATA only: stdlib hash/JSON/WAVE; no provider/process calls."""
from pathlib import Path
import json,hashlib,stat
P=Path(__file__).resolve().parent;S=P.parent
OBS=dict(path=str(S/'combined-native-pure-runtime-control-v1-root-results.json'),sha256='ea851b44d9b54bff81a32f4598807355ad109db21f620b3ff9580e9ead7586c7',bytes=5928)
checks=0;files={};families={};copies=[]
def check(v,m):
 global checks
 assert v,m;checks+=1

def row(p):
 p=Path(p);a=p.lstat();check(stat.S_ISREG(a.st_mode),'ordinary file '+str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.lstat();check((a.st_dev,a.st_ino,a.st_size,a.st_mode,a.st_nlink,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mode,z.st_nlink,z.st_mtime_ns,z.st_ctime_ns),'stable file '+str(p));d=dict(path=str(p),sha256=h.hexdigest(),bytes=a.st_size);files[str(p)]=d;return d

def verify(d):check(row(d['path'])==d,'whole pinned descriptor '+d['path']);return Path(d['path'])
def read(d):return json.loads(verify(d).read_bytes())
def family(d):
 v=read(d);base=Path(d['path']).parent;names={'index.json'};rows=[d]
 for x in v['files']:
  n=x['path'];check(n and n not in names and not n.startswith('/')and '\\'not in n and all(q not in('','.','..')for q in n.split('/')),'unique finite family member');names.add(n);r=dict(x,path=str(base/n));verify(r);rows.append(r)
 check(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'exact family membership '+str(base));families[d['path']]=d;return rows

def proof(pair):check(pair['result']in family(pair['index']),'proof result indexed');return read(pair['result'])
def publication(root,index,completion,result,state,expected_rows):
 check(index['path']==str(root/'index.json')and completion['path']==str(root/'completion.json')and result['path']==str(root/'result.json'),'actual publication paths');ix=read(index);done=read(completion);r=read(result);check(ix['schemaVersion']==1 and len(ix['files'])==expected_rows,'finite actual row count');names={'index.json','completion.json'}
 for x in ix['files']:
  n=x['path'];check(n not in names and n and not n.startswith('/')and '\\'not in n and all(q not in('','.','..')for q in n.split('/')),'confined publication row');names.add(n);f=verify(dict(x,path=str(root/n)));st=f.lstat();check(st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o600,'independent private actual file')
 check({f.relative_to(root).as_posix()for f in root.rglob('*')if f.is_file()}==names and not any(f.is_symlink()for f in root.rglob('*')),'closed actual publication membership');check(r['schemaVersion']==1 and r['state']==state,'actual completed result state');check(done['index']==dict(index,path='index.json')and done['result']==dict(result,path='result.json'),'whole completion descriptors');return r,done

def child_terminal(d):
 t=read(d);check(t['schemaVersion']==1 and t['closed']is True and type(t['status'])is int and t['status']==0 and t['signal']is None and t['spawnError']is None and t['timedOut']is False and t['externalSignal']is None and t['outputLimitExceeded']is False and t['ownedGroupGone']is True and t['terminalExitZeroObserved']is True and t['signalCount']==0 and t['errors']==t['signals']==[],'strict owned raw0/no signalling/errors/overflow');check(t['timeoutMs']==60000 and t['maxOutputBytes']==16777216,'actual command caps');verify(t['stdout']);verify(t['stderr']);check(t['stderr']['bytes']==0,'whole empty child stderr');return t

def outer_terminal(d,authority):
 t=read(d);check(t['rawExitCode']==0 and type(t['rawExitCode'])is int and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['timeout']is t['forcedCleanup']is False,'actual parent raw0 clean');check(t['signals']==t['errors']==t['interruptedSignals']==t['remainingObservedPids']==[]and t['authority']==authority,'no parent signal/error/remaining processes');check(t['finalGroups']and all(g['alive']is False for g in t['finalGroups']),'all final groups observed gone');verify(t['stdout']);verify(t['stderr']);check(t['stderr']['bytes']==0,'parent stderr empty');return t

def wave(raw):
 text=raw.decode('utf-8','strict');check(text.endswith('\n')and not text.endswith('\n\n'),'one WAVE println LF');text=text[:-1];check(len(text)>=2 and text[0]==text[-1]=='"','one typed WAVE string');out='';i=1
 while i<len(text)-1:
  ch=text[i]
  if ch=='\\':
   i+=1;check(i<len(text)-1,'complete WAVE escape');e=text[i]
   if e=='u':
    i+=1;check(text[i]=='{','WAVE scalar escape braces');end=text.find('}',i+1);digits=text[i+1:end];check(end>i and end<len(text)-1 and 1<=len(digits)<=6 and all(c in '0123456789abcdefABCDEF'for c in digits),'whole WAVE Unicode escape');cp=int(digits,16);check(cp<=0x10ffff and not 0xd800<=cp<=0xdfff,'Unicode scalar');out+=chr(cp);i=end
   else:
    esc={'\\':'\\','"':'"',"'":"'",'t':'\t','n':'\n','r':'\r'};check(e in esc,'known WAVE escape');out+=esc[e]
  else:check(ch!='"'and ord(ch)>31 and not 0x7f<=ord(ch)<=0x9f and not 0xd800<=ord(ch)<=0xdfff,'no raw control/extraquote/malformed scalar');out+=ch
  i+=1
 return out

def scalar(value,ordinal):
 check(type(value)is str,'actual string primitive');v=json.loads(value);check(list(v)==['schemaVersion','initial','calls','hex','timerRequested'],'whole original key order');check(type(v['schemaVersion'])is int and v['schemaVersion']==1 and type(v['initial'])is int and v['initial']==0 and type(v['calls'])is int and v['calls']==ordinal and v['hex']=='c3a92201'and v['timerRequested']is False,'all typed values/counters/bytes');return value

obs=read(OBS);check(obs['state']=='ROOT_OBSERVED_COMBINED355_PRELIMINARY_PURE_CONTROL_ZERO_UNREVIEWED_V1'and obs['toolObservation']==dict(sessionId=62153,rawExitCode=0),'actual Root tool observation');source=obs['sourceIndex'];source_rows=family(source);source_dir=Path(source['path']).parent;refs=read(next(x for x in source_rows if x['path']==str(source_dir/'references.json')));inputs=read(next(x for x in source_rows if x['path']==str(source_dir/'source-inputs.json')));peer=proof(obs['sourceIndependentReview']);check(peer['state']=='INDEPENDENT_COMBINED355_PURE_RUNTIME_CONTROL_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==source['sha256']and peer['sourceReviewPassed']is peer['sourceOnly']is True,'genuine current Source/peer')
for r in inputs['files']:verify(r)
for r in inputs['families']:family(r)
boundary=read(inputs['parentOnlyBoundary'])
for r in boundary['files']:verify(r)
for r in boundary['families']:
 if r['path']not in families:family(r)
for b in boundary['boundaries']:
 v=read(b['manifest']);check(len(v[b['field']])==b['expectedRows'],'finite known original boundary')
 for d in v[b['field']]:
  if d['path']not in files:verify(d)
 for d in v.get(b['familyField'],[]):
  if d['path']not in families:family(d)
# Private package is preserved input only; no package or module/API import.
pkg=read(refs['packageInventory'])['package'];base=Path(refs['loaderPackageRoot']);names=set();aliases=set();check(pkg['root']==str(base)and len(pkg['files'])==4889 and len(pkg['links'])==21,'actual package identity')
for d in pkg['files']:
 names.add(d['relativePath']);verify({k:d[k]for k in ['path','sha256','bytes']});st=Path(d['path']).lstat();check(st.st_nlink==1 and stat.S_IMODE(st.st_mode)==d['mode'],'actual package mode/inode')
for d in pkg['links']:
 f=base/d['path'];check(f.is_symlink()and f.readlink().as_posix()==d['target']and str(f.resolve())==d['resolvedPath']and f.resolve().is_relative_to(base),'actual package confined alias');aliases.add(d['path'])
check({f.relative_to(base).as_posix()for f in base.rglob('*')if f.is_file()or f.is_symlink()}==names|aliases,'current whole package membership')
root=read(obs['rootAuthority']);config=read(obs['config']);invocation=read(obs['invocation']);verify(invocation['launcher']);check(config==dict(schemaVersion=1,state='COMBINED355_PURE_CONTROL_CONFIG_V1',sourceIndex=source,rootAuthority=obs['rootAuthority']),'whole genuine config');check(root['state']=='ROOT_REVIEWED_COMBINED355_PRELIMINARY_PURE_CONTROL_V1'and root['sourceIndex']==source and root['sourceIndependentReview']==obs['sourceIndependentReview'],'own Root source/peer');check(root['entry']in source_rows and root['externalController']in source_rows,'actual original entry/controller')
for k in ['actualPureReview','actualPureContract','component','fixtureSource','readOnlyConfig']:check(root[k]==refs[k],'same exact Source/Root role '+k)
for k in ['parentNativeReadOnlyApiAllowed','nodeFixtureOracleAllowed','pureGeneratedImportAllowed','pureRunAllowed','stockWasmtimeAllowed']:check(root[k]is True,'separate actual Root permission '+k)
for k in ['resourceRuntimeAllowed','otherGuestAllowed','componentConstructionAllowed','transpileOrMappingAllowed','nativeBuildAllowed','nativeFreezeAllowed','keyOrCryptoAllowed','gcOrOomOrFaultAllowed','unsafeResetOrReuseAllowed','allSixFixtureGateComplete','fullSeventeenGateComplete','fullNextCompatibility','deploymentAccepted','adoptionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:check(root[k]is False,'no wider Root grant '+k)
check([root[k]for k in ['parentNativeApiCalls','childNativeApiCalls','nodeOracleCalls','retainedJcoCalls','freshJcoCalls','freshWasmtimeCalls','componentValues','totalValues']]==[1,0,3,3,1,3,7,10],'whole Root schedule')
p=proof(refs['actualPureReview']);k=read(refs['actualPureContract']);check(p['artifacts']==k['artifacts']and p['generatedFiles']==k['generatedFiles']==refs['generated']and p['emittedImports']==[]and p['publicAbiSignatures']==[dict(name='run',params=[],result='string')],'actual pure original graph and loading tuple');check(p['componentSha256']==refs['component']['sha256']and refs['component']==obs['component']and refs['fixtureSource']==obs['fixtureSource'],'exact actual component/source')
base=Path(root['outputRoot']);result,done=publication(base,obs['runtimeIndex'],obs['runtimeCompletion'],obs['runtimeResult'],'COMBINED355_PRELIMINARY_PURE_CONTROL_COMPLETE_UNREVIEWED_V1',53);check(done['externalParentRawZeroAndIndependentReviewRequired']is True,'actual unreviewed completion');check(result['sourceIndex']==source and result['rootAuthority']==obs['rootAuthority']and result['component']==refs['component']and result['fixtureSource']==refs['fixtureSource'],'whole result source/native roles');check(len(result['sessions'])==6,'six actual commands/sessions')
values={};raw_descriptors=[];command_pids=[]
for mode,count in [('oracle',3),('retained',3),('fresh',1)]:
 session=next(x for x in result['sessions']if x['mode']==mode);d=base/'sessions'/mode;ix=row(d/'index.json');co=row(d/'completion.json');r,cd=publication(d,ix,co,session['result'],'COMBINED355_PURE_CHILD_COMPLETE_UNREVIEWED_V1',count+3);check(cd['externalRawZeroAndReviewRequired']is True and r['sourceIndex']==source and r['rootAuthority']==obs['rootAuthority']and r['mode']==mode and r['rawAttempts']==r['rawWritten']==r['values']==count and r['childNativeApiInvocations']==0,'complete actual child context/count');check(r['componentImported']is(mode!='oracle')and r['nodeFixtureOracleInvoked']is(mode=='oracle'),'real Node versus component role');vs=read(session['values']);check(vs['schemaVersion']==1 and vs['mode']==mode and len(vs['values'])==count,'whole ordinal value array');values[mode]=[]
 t=child_terminal(session['terminal']);command_pids.append(t['pid']);check(t['executable']==refs['node']['path']and t['args']==[str(source_dir/'entry.mjs'),mode,json.dumps(obs['config'],separators=(',',':'))],'actual plain pinned Node argv');launch=json.loads((base/'processes'/('node-'+mode+'.launch.json')).read_text());check(launch['executable']==t['executable']and launch['args']==t['args']and launch['timeoutMs']==60000 and launch['detachedOwnedSession']is True,'whole launch/terminal argv binding')
 for i in range(count):
  f=d/'raw'/('%03d.json'%(i+1));r=json.loads(f.read_text());check(list(r)==['schemaVersion','name','args','kind','observed']and r['schemaVersion']==1 and r['name']=='run'and r['args']==[]and r['kind']=='return'and set(r['observed'])=={'type','value'}and r['observed']['type']=='string','whole actual typed raw return');value=scalar(r['observed']['value'],i+1);check(value==vs['values'][i],'whole value equals raw string');values[mode].append(value);raw_descriptors.append(row(f))
for i,v in enumerate(values['retained']):check(v==values['oracle'][i]and v.encode()==values['oracle'][i].encode(),'Jco retained whole Node ordinal equality')
check(values['fresh'][0]==values['oracle'][0],'fresh Jco counter1 and full Node first string');values['wasmtime']=[]
for n in range(3):
 session=result['sessions'][n+3];check(session['mode']=='wasmtime-fresh'and session['count']==1,'fresh WT session role');t=child_terminal(session['terminal']);command_pids.append(t['pid']);check(t['executable']==refs['wasmtime']['path']and t['args']==['run','--invoke','run()',refs['component']['path']],'actual stock WT42 exact literal argv');launch=json.loads((base/'processes'/('wasmtime-'+str(n)+'.launch.json')).read_text());check(launch['executable']==t['executable']and launch['args']==t['args']and launch['timeoutMs']==60000,'exact WT launch/terminal');decoded=read(session['decoded']);value=scalar(wave(verify(t['stdout']).read_bytes()),1);check(decoded==dict(schemaVersion=1,host='stock-wasmtime42',fresh=True,name='run',args=[],kind='return',observed=dict(type='string',value=value),ordinal=1,rawStdout=t['stdout']),'entire strict WAVE decoded record');check(value==values['oracle'][0]and value.encode()==values['oracle'][0].encode(),'whole fresh WT byte equality to actual Node first');values['wasmtime'].append(value);raw_descriptors.append(t['stdout'])
check(len(set(command_pids))==6,'six distinct actual command PIDs');outer=outer_terminal(obs['outerTerminal'],obs['rootAuthority']);inner=outer_terminal(obs['externalTerminal'],obs['rootAuthority']);check(outer['pid']!=inner['pid']and outer['pid']not in command_pids and inner['pid']not in command_pids,'two actual separate parents')
for d,t,deadline,argv in [(Path(obs['outerTerminal']['path']).parent,outer,1800,invocation['actualArgv']),(Path(obs['externalTerminal']['path']).parent,inner,1200,[refs['node']['path'],str(source_dir/'entry.mjs'),'parent',json.dumps(obs['config'],separators=(',',':'))])]:
 start=json.loads((d/'started.json').read_text());check(start['pid']==t['pid']and start['timeoutSeconds']==deadline and start['argv']==argv and start['authority']==obs['rootAuthority'],'complete actual parent start/argv/cap');verify(row(d/'started.json'))
lines=[json.loads(x)for x in verify(outer['stdout']).read_text().splitlines()];check(len(lines)==2 and lines[0]==dict(pid=inner['pid'],timeoutSeconds=1200)and lines[1]['terminal']==obs['externalTerminal']and lines[1]['rawExitCode']==0 and lines[1]['requiresIndependentActualReview']is True,'whole actual outer JSONL2 records');v=json.loads(verify(inner['stdout']).read_bytes());check(v==dict(root=str(base),index=dict(obs['runtimeIndex'],path='index.json'),completion=dict(obs['runtimeCompletion'],path='completion.json')),'whole exact inner publication return')
# Transport qualification: body writes expected DATA only after genuine fresh
# record model equality; shape comes from the fresh returned own descriptors.
native=read(obs['nativeRecordData']);expected=read(refs['actualReadOnlyData']);metadata=read(refs['nativeMetadata']);check(native==expected and obs['nativeRecordData']['sha256']==refs['actualReadOnlyData']['sha256'],'whole reviewed DATA transport byte equality');check(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11 and native['bootstrap']['metadata']==metadata and len(native['bootstrap']['selectedManifests'])==11,'full actual80/355+3/11, no smaller adaptation');check(native['bootstrap']['engine']==refs['nativeEngine']and native['bootstrap']['freezeReceipt']==refs['freezeReceipt'],'real frozen engine/receipt');check(native['bootstrap']['nativeFrame']['verificationCapsule']['state']=='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1','historical NOT_ACCEPTED capsule unchanged');check(native['bootstrap']['currentFrozenVerifierCalls']==1,'historical one verifier call remains DATA');check(all(native['currentVerification'][n]==0 for n in ['helperInvocations','processesSpawned','filesCreated']),'current retained API zero helper/process/write scope');shape=json.loads((base/'native-record-shape.json').read_text());check(list(shape)==['schemaVersion','kind','sourceIndex','actualReview','bootstrap','currentVerification','recheck']and shape['recheck']==dict(type='function',writable=False,configurable=False,enumerable=True),'whole actual own callable shape, not serialized callable');check(all(d['writable']is d['configurable']is False and d['enumerable']is True for d in shape.values()),'frozen own shape metadata')
for n in ['nativeSourceFiles','externalEmbeddingSources','fullMetadataFields','selectedWholeManifests']:check(result[n]==root[n], 'current context count '+n)
for n in ['resourceRuntimeExercised','allSixFixtureGateComplete','fullSeventeenGateComplete','fullNextCompatibility','deploymentAccepted','adoptionAllowed','operationalAdmission','runtimeAcceptanceClaim']:check(result[n]is False,'literal limited actual scope '+n)
check(result['nodeOracleStrings']==3 and result['jcoRetainedStrings']==3 and result['jcoFreshStrings']==1 and result['wasmtimeFreshStrings']==3 and result['componentStrings']==7 and result['totalSuccessfulCapturedValues']==10 and result['parentNativeReadOnlyApiInvocations']==1 and result['childNativeApiInvocations']==0 and result['generatedModuleImported']is result['ordinaryPureRunInvoked']is result['preliminaryPureControlOnly']is True,'all actual typed coverage/Source-coupled call counts')
# Compact actual text copies only. No native DATA/engine/core/old history copy.
for f in sorted(base.rglob('*')):
 if f.is_file()and f.name!='native-record-data.json':
  destination=P/'raw'/'runtime'/f.relative_to(base);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(f.read_bytes());copies.append(dict(original=row(f),copy=str(destination.relative_to(P))))
monitor_inventory=[]
for label,d in [('outer',Path(obs['outerTerminal']['path']).parent),('inner',Path(obs['externalTerminal']['path']).parent)]:
 for f in sorted(d.iterdir()):
  check(f.is_file()and not f.is_symlink(),'actual monitor regular inventory');monitor_inventory.append(row(f))
  if f.name in ['started.json','terminal.json','stdout.log','stderr.log']:
   destination=P/'raw'/label/f.name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(f.read_bytes());copies.append(dict(original=row(f),copy=str(destination.relative_to(P))))
for name,d in [('root-observation.json',OBS),('root-authority.json',obs['rootAuthority']),('config.json',obs['config']),('invocation.json',obs['invocation'])]:
 destination=P/'raw'/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(verify(d).read_bytes());copies.append(dict(original=d,copy=str(destination.relative_to(P))))
(P/'monitor-inventory.json').write_text(json.dumps(dict(schemaVersion=1,files=monitor_inventory,scope='Actual completed monitor DATA only; no invented original monitor index or runtime timing attestation'),indent=2)+'\n')
(P/'values.json').write_text(json.dumps(dict(schemaVersion=1,values=values,nodeOracleStrings=3,jcoStrings=4,wasmtimeStrings=3,componentStrings=7,totalStrings=10,wholeStringsAndUtf8EqualByOrdinal=True),indent=2)+'\n')
(P/'raw-copy-map.json').write_text(json.dumps(dict(schemaVersion=1,files=copies,nativeDataCopied=False,historyTreesCopied=False),indent=2)+'\n')
(P/'audit-results.json').write_text(json.dumps(dict(schemaVersion=1,checks=checks,currentUniqueInputFiles=len(files),sourceFamilies=len(families),actualRuntimePayloadRows=53,actualRuntimeFiles=55,actualMonitorFiles=len(monitor_inventory),actualCopiedTextFiles=len(copies),actualCommandPids=command_pids,parentPids=[outer['pid'],inner['pid']],sourceIndex=source,rootObservation=OBS,runtimeIndex=obs['runtimeIndex'],runtimeResult=obs['runtimeResult'],runtimeCompletion=obs['runtimeCompletion'],nodeOracle=row(base/'sessions/oracle/values.json'),rawTypedRecords=raw_descriptors,nativeDataDescriptor=obs['nativeRecordData'],nativeRecordShape=row(base/'native-record-shape.json'),proofCoverage=dict(nodeOracleStrings=3,jcoRetainedStrings=3,jcoFreshStrings=1,wasmtimeFreshStrings=3,componentStrings=7,totalSuccessfulCapturedValues=10),reviewerOperationalActionsInvoked=False),indent=2)+'\n')
print(json.dumps(dict(checks=checks,currentUniqueInputFiles=len(files),families=len(families),runtimeRows=53,runtimeFiles=55,copiedTextFiles=len(copies),monitorFiles=len(monitor_inventory),whole10ValuesPassed=True)))
