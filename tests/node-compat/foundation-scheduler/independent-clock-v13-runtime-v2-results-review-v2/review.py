"""Independent finished clock DATA review; no application/helper/API/host execution."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys,time
OWN=Path(__file__).resolve().parent;S=OWN.parent
SOURCE=S/'clock-v13-runtime-candidate-v2'
OUTPUT=Path('/private/tmp/starling-node-compat/clock-v13-runtime-v2')
EXTERNAL=Path(str(OUTPUT)+'-external-root')
ROOT_SHA='8badaeea36187aa7e15432e41d229567c907b1dc921a4af677692eb7fcb65811'
captured={};identities={};families={};checks=0
def need(v,label):
 global checks
 assert v,label
 checks+=1
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
def sig(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def verify(r):
 need(type(r)is dict and set(r)=={'path','sha256','bytes'},'exact descriptor')
 p=physical(r['path']);need(p.is_absolute()and str(p)==os.path.normpath(str(p)),'canonical evidence')
 for q in(p,*p.parents):need(not q.is_symlink(),'ordinary evidence path')
 a=p.stat();need(stat.S_ISREG(a.st_mode)and a.st_size==r['bytes'],'regular exact bytes')
 if r['path']in captured:need(captured[r['path']]==r and identities[r['path']]==sig(a),'stable repeated original');return p
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(sig(a)==sig(p.stat())and h.hexdigest()==r['sha256'],'stable whole evidence SHA');captured[r['path']]=dict(r);identities[r['path']]=sig(a);return p
def data(r):return json.loads(verify(r).read_bytes())
def family(r):
 v=data(r);base=Path(r['path']).parent;names={'index.json'};rows=[r]
 for m in v['files']:
  n=m['path'];need(n not in names and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/')),'unique confined family');names.add(n);q=dict(m,path=str(base/n));verify(q);rows.append(q)
 need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'exact family membership');families[r['path']]=r;return rows
def confined(root,r):
 n=r['path'];need(not n.startswith('/')and all(p not in('','.','..')for p in n.split('/')),'relative publication unchanged/confined');q=dict(r,path=str(root/n));verify(q);return q
def publication(root,ixrow,completionrow,resultrow=None):
 ix=data(ixrow);completion=data(completionrow);names={'index.json','completion.json'}
 need(completion['index']==dict(ixrow,path='index.json'),'relative index descriptor exact')
 if resultrow is not None:need(completion['result']==dict(resultrow,path=resultrow['path'].split('/')[-1]),'relative result descriptor exact')
 for m in ix['files']:need(m['path']not in names,'unique output row');names.add(m['path']);confined(root,m)
 need(not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names,'actual exact output membership')
 return ix,completion,names
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 global checks
 need(OWN.name=='independent-clock-v13-runtime-v2-results-review-v2'and OWN==Path(__file__).resolve().parent,'genuine corrected-publication reader context');started=time.monotonic();rootrow=desc(S/'clock-v13-runtime-v2-root-results.json');need(rootrow['sha256']==ROOT_SHA and rootrow['bytes']==5157,'explicit terminal Root tuple');root=data(rootrow)
 need(root['toolObservation']==dict(sessionId=33981,rawExitCode=0,kind='Actual exec-command terminal observation'),'Root raw0 tool observation, no invented log')
 srcrows=family(root['sourceIndex']);peerrows=family(root['sourcePeer']['index']);need(root['sourcePeer']['result']in peerrows,'actual Source peer indexed')
 peer=data(root['sourcePeer']['result']);need(peer['state']=='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V2'and peer['sourceIndexSha256']==root['sourceIndex']['sha256']and peer['sourceReviewPassed']is True,'correct V2 Source peer')
 refs=data(next(r for r in srcrows if r['path']==str(SOURCE/'references.json')));inputs=data(next(r for r in srcrows if r['path']==str(SOURCE/'source-inputs.json')))
 need(len(inputs['files'])==12079 and len(inputs['families'])==18,'fixed declared protection; no recursive growth')
 for r in inputs['files']:verify(r)
 for r in inputs['families']:family(r)
 # Own standard-only pure DATA decoder; no operational producer code imported.
 spec=importlib.util.spec_from_file_location('clock_retained_data_primitives',OWN/'data_reader.py');primitive=importlib.util.module_from_spec(spec);spec.loader.exec_module(primitive)
 authority=data(root['rootAuthority']);config=data(root['rootConfig']);invocation=data(root['invocation']);verify(invocation['rootLauncher'])
 need(authority['sourceIndex']==config['sourceIndex']==root['sourceIndex']and authority['sourceIndependentReview']==root['sourcePeer']and config['rootAuthority']==root['rootAuthority'],'exact Root/config/Source joins')
 need(authority['phase']=='runtime-differential'and authority['mappedTranspileAllowed']is authority['jcoCompilerWasmHelpersAllowed']is False,'no mapping rerun in runtime phase')
 need(authority['generatedApplicationImportAllowed']is authority['ordinaryRunAllowed']is authority['stockWasmtimeAllowed']is True,'bounded actual runtime permission')
 need(authority['actualMappedOutputReview']==root['actualMappedOutputReview'],'exact separately reviewed mapped output')
 mapped=data(root['actualMappedOutputReview']);mapped_peer=data(mapped['independentActualMappedOutputReview']['result']);mapped_rows=family(mapped['independentActualMappedOutputReview']['index']);need(mapped['independentActualMappedOutputReview']['result']in mapped_rows and mapped['independentActualMappedOutputContract']in mapped_rows,'indexed actual mapping peer/contract')
 mapped_contract=data(mapped['independentActualMappedOutputContract'])
 for group in('requiredFixedValues','requiredExactDescriptors'):
  for k,v in mapped_contract[group].items():need(mapped_peer[k]==v,'whole actual mapping contract '+k)
 need(mapped_peer['coverage']==mapped_contract['requiredCoverage']and mapped['sourceIndexSha256']==root['sourceIndex']['sha256']and mapped['component']==refs['component']and mapped['mappingOptions']==refs['mappingOptions'],'whole mapping proof and same component')
 mapresult=data(mapped['mappingResult']);mapix,mapcompletion,mapnames=publication(Path(refs['mappedOutputRoot']),mapped['index'],mapped['completion'])
 need(mapcompletion['mappingResult']==mapped['mappingResult']and mapresult['sourceIndex']==root['sourceIndex']and mapresult['component']==refs['component'],'actual mapping result/relative publication')
 for r in mapresult['mappedFiles'].values():verify(r)
 need(mapresult['mappedFiles']['clock_v13.core.wasm']['sha256']==refs['generatedFiles']['clock_v13.core.wasm']['sha256']and mapped['allFourActualCoreBytesUnchanged']is True,'unchanged full engine plus inline core proof')
 # Current declared package membership and aliases, without importing any shim.
 pkg=data(refs['packageInventory'])['package'];pbase=Path(pkg['root']);files={r['relativePath']:r for r in pkg['files']};links={r['path']:r for r in pkg['links']};names=set()
 need(len(files)==4889 and len(links)==21 and not pbase.is_symlink(),'actual fixed package roles')
 for p in pbase.rglob('*'):
  n=p.relative_to(pbase).as_posix();s=p.lstat()
  if p.is_symlink():r=links[n];need(os.readlink(p)==r['target']and str(p.resolve())==r['resolvedPath']and p.resolve().is_relative_to(pbase),'current literal package alias');names.add(n)
  elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700,'private package directory')
  else:r=files[n];need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'],'regular private package file');verify({k:r[k]for k in('path','sha256','bytes')});names.add(n)
 need(names==set(files)|set(links),'full current package membership')
 oracle=data(refs['oracleEvidence']['command']['stdout']);need(oracle['status']=='passed'and oracle['value']==refs['oracleValue'],'original whole retained Node oracle');primitive.scalar(oracle['value'],refs['oracleValue'])
 parent=data(root['externalParentTerminal']);primitive.check_outer_terminal(parent,root['rootAuthority']);need(verify(parent['stderr']).read_bytes()==b'','outer stderr empty')
 start=data(desc(EXTERNAL/'started.json'));need(start['pid']==parent['pid']and start['timeoutSeconds']==1200 and start['authority']==root['rootAuthority'],'actual owned parent start')
 cfgarg=json.dumps(root['rootConfig'],separators=(',',':'));need(start['argv']==[refs['node']['path'],str(SOURCE/'entry.mjs'),'runtime',cfgarg],'actual original Node argv/plain runtime path')
 parent_lines=[json.loads(line)for line in verify(root['parentStdout']).read_text().splitlines()];need(len(parent_lines)==2 and parent_lines[0]==dict(pid=parent['pid'],timeoutSeconds=1200)and parent_lines[1]==root['actualReturnEnvelope'],'complete parent launch+envelope JSONL');need(verify(root['parentStderr']).read_bytes()==b'','parent stderr empty');verify(root['environmentPolicy'])
 result=data(root['actualResult']);ix,completion,actualnames=publication(OUTPUT,root['actualIndex'],root['actualCompletion'],root['actualResult'])
 need(result['state']=='CLOCK_V13_REACTDOM_DIFFERENTIAL_COMPLETE_UNREVIEWED_V2'and result['sourceIndex']==root['sourceIndex']and result['component']==refs['component']and result['rootAuthority']==root['rootAuthority'],'actual result source/component/Root')
 envelope=json.loads(verify(parent['stdout']).read_bytes());need(envelope==dict(root=str(OUTPUT),index=completion['index'],completion=dict(root['actualCompletion'],path='completion.json')),'whole Node relative publication')
 native_frame=data(refs['artifacts']['nativeFrameData']);metadata=data(refs['nativeMetadata']);frames=[]
 for lane in('','retained','fresh'):
  d=desc(OUTPUT/lane/'native-frame-data.json');shape_row=desc(OUTPUT/lane/'native-frame-shape.json');f=data(d);shape=data(shape_row)
  need(f==native_frame and f['metadata']==metadata and len(metadata)==64 and len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==9,'full unchanged actual native frame342/3/64/9')
  need(list(f)==['enginePath','sourceRoot','metadata','pin','variant']and list(shape)==list(f)+['recheck'],'complete DATA and callable-descriptor roles')
  need(all(shape[k]==dict(type='object'if k in('metadata','pin')else'function'if k=='recheck'else'string',writable=False,configurable=False,enumerable=True)for k in shape),'actual readonly frame shape; callable is DATA only')
  frames.append(dict(scenario=lane or'parent',data=d,shape=shape_row))
 retained_oracle=data(desc(OUTPUT/'retained-node-oracle.json'));need(retained_oracle==dict(value=refs['oracleValue'],source=refs['oracleEvidence'],rerun=False),'retained oracle role exact')
 returns=[];pids=[]
 need(len(result['sessions'])==5,'exact five child sessions')
 for session in result['sessions']:
  t=data(session['terminal']);primitive.check_inner_terminal(t);pids.append(t['pid']);need(t['timeoutMs']==180000 and t['maxOutputBytes']==16777216,'owned180s/16MiB bounds');need(verify(t['stderr']).read_bytes()==b'','all inner stderr empty')
  if session['host']=='jco-standard-wasi-shim':
   scenario=session['scenario'];need(scenario in('retained','fresh')and t['executable']==refs['node']['path']and t['args']==[str(SOURCE/'entry.mjs'),'jco-worker',cfgarg,scenario],'actual fresh Jco worker Source/config argv')
   lane=OUTPUT/scenario;sr=desc(lane/'result.json');ci=desc(lane/'index.json');cc=desc(lane/'completion.json');si,sc,sn=publication(lane,ci,cc,sr);sresult=data(sr);count=3 if scenario=='retained'else 1
   need(sresult['scenario']==scenario and sresult['rawAttempts']==sresult['rawWritten']==count and sresult['sourceIndex']==root['sourceIndex']and sresult['component']==refs['component'],'retained/fresh actual schedule/source/result')
   need({r['path']for r in si['files']if r['path'].startswith('raw/')}=={'raw/'+str(n).zfill(3)+'.json'for n in range(1,count+1)},'all exact typed raw rows')
   worker_publication=json.loads(verify(t['stdout']).read_bytes());need(worker_publication==dict(root=str(lane),index=sc['index'],completion=dict(cc,path='completion.json')),'complete worker relative publication')
   for n in range(1,count+1):
    r=desc(lane/'raw'/(str(n).zfill(3)+'.json'));v=data(r);need(list(v)==['schemaVersion','name','args','kind','observed']and v['schemaVersion']==1 and v['name']=='run'and v['args']==[]and v['kind']=='return'and v['observed']['type']=='string','full typed raw scalar before assertion');primitive.scalar(v['observed']['value'],refs['oracleValue']);returns.append(dict(host='jco',scenario=scenario,ordinal=n,raw=r,value=v['observed']['value'],terminal=session['terminal']))
  else:
   need(session['host']=='stock-wasmtime42'and session['fresh']is True and t['executable']==refs['wasmtime']['path']and t['args']==['run','--invoke','run()',refs['component']['path']],'stock Wasmtime same component actual argv')
   raw=verify(t['stdout']).read_bytes();value=primitive.parse_wave(raw);primitive.scalar(value,refs['oracleValue']);name=t['name'];decoded=data(desc(OUTPUT/(name+'.decoded.json')));need(decoded==dict(returnedType='string',value=value,rawStdout=t['stdout']),'complete raw-WAVE/decoded join');returns.append(dict(host='stock-wasmtime42',scenario='fresh',raw=t['stdout'],stderr=t['stderr'],terminal=session['terminal'],value=value))
 need(len(returns)==7 and sum(r['host']=='jco'and r['scenario']=='retained'for r in returns)==3 and sum(r['host']=='jco'and r['scenario']=='fresh'for r in returns)==1,'all seven strings in exact3+1+3 schedule')
 need(len(pids)==len(set(pids))==5 and set(pids)|{parent['pid']}=={r['pid']for r in parent['observedProcesses']},'five fresh child PIDs plus actual parent')
 need(all(r['ppid']==parent['pid']and r['pgid']==r['pid']for r in parent['observedProcesses']if r['pid']in pids)and len(parent['finalGroups'])==6,'exact owned parent/child groups')
 for k,v in dict(jcoRetainedWholeStrings=3,jcoFreshWholeStrings=1,stockWasmtimeFreshWholeStrings=3,allWholeStringsEqualRetainedNode=True,hostCallCountsObserved=False,fullClockProfileAcceptance=False,resourceDateSnapshotTimerTeardownSevenCaseGateComplete=False,operationalAdmission=False,runtimeAcceptanceClaim=False).items():need(result[k]==v,'bounded actual result claim '+k)
 copies=[]
 for lane,base in [('actual',OUTPUT),('external',EXTERNAL)]:
  need(not base.is_symlink()and stat.S_IMODE(base.stat().st_mode)==0o700,'private actual output root')
  for p in sorted(base.rglob('*')):
   need(not p.is_symlink(),'actual evidence no links')
   if p.is_dir():need(stat.S_IMODE(p.stat().st_mode)==0o700,'private actual subdir');continue
   r=desc(p);verify(r);need(p.stat().st_nlink==1,'actual ordinary single-link raw');target=OWN/'evidence'/lane/p.relative_to(base);target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb')as f:f.write(verify(r).read_bytes());f.flush();os.fsync(f.fileno())
   os.chmod(target,0o600);need(desc(target)['sha256']==r['sha256'],'complete exact actual text copy');copies.append(dict(original=r,copy=desc(target)))
 for lane,r in [('root-results',rootrow),('invocation',root['invocation']),('authority',root['rootAuthority']),('config',root['rootConfig']),('parent-stdout',root['parentStdout']),('parent-stderr',root['parentStderr']),('environment-policy',root['environmentPolicy'])]:
  target=OWN/'evidence'/(lane+'.json'if lane not in('parent-stdout','parent-stderr')else lane+'.log')
  with target.open('xb')as f:f.write(verify(r).read_bytes());f.flush();os.fsync(f.fileno())
  os.chmod(target,0o600);copies.append(dict(original=r,copy=desc(target)))
 for p in captured:need(identities[p]==sig(physical(p).stat()),'all current evidence/source physical identities stable')
 for r in srcrows:need(desc(Path(r['path']))==r,'Source135d stable across review')
 save('raw-evidence.json',dict(schemaVersion=1,copies=copies,inheritedTreesCopied=False))
 save('checks.json',dict(schemaVersion=1,passed=True,checks=checks,currentDeclaredInputs=12079,currentDeclaredFamilies=18,allAuthenticatedFamilies=len(families),uniqueReadHashInputs=len(captured),uniqueLogicalBytes=sum(r['bytes']for r in captured.values()),actualIndexedFiles=len(ix['files']),actualFiles=len(actualnames),actualExternalFiles=len([p for p in EXTERNAL.rglob('*')if p.is_file()]),actualTextCopies=len(copies),jcoRetainedStrings=3,jcoFreshStrings=1,stockWasmtimeFreshStrings=3,fullHtmlUtf8Bytes=45,freshChildPids=pids,outerNodePid=parent['pid'],ownedGroups=6,allWholeStringsEqualNode=True,completeNativeFrames=3,nativeSourceFiles=342,externalEmbeddingSources=3,fullMetadataFields=64,selectedManifestCount=9,currentPackageFiles=4889,currentPackageAliases=21,currentPhysicalIdentitiesStable=True,actualTimeProtectionEvidence='Successful authenticated Source control flow and raw0 plus independent current hashes; no separately retained per-read historical snapshots',ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,elapsedDataReadSeconds=time.monotonic()-started))
 save('references.json',dict(schemaVersion=1,rootResult=rootrow,sourceIndex=root['sourceIndex'],sourcePeer=root['sourcePeer'],rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],invocation=root['invocation'],actualIndex=root['actualIndex'],actualResult=root['actualResult'],actualCompletion=root['actualCompletion'],externalParentTerminal=root['externalParentTerminal'],parentStdout=root['parentStdout'],parentStderr=root['parentStderr'],actualMappedOutputReview=root['actualMappedOutputReview'],actualMappedIndependentReview=mapped['independentActualMappedOutputReview'],actualMappedIndependentContract=mapped['independentActualMappedOutputContract'],component=refs['component'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativeFrameDataAndShape=frames,wholeRawReturnsAndTerminals=returns,retainedNodeOracle=desc(OUTPUT/'retained-node-oracle.json'),originalNodeOracle=refs['oracleEvidence'],selectedInterfaces=refs['selectedInterfaces'],mappingOptions=refs['mappingOptions'],sourceProtection=desc(SOURCE/'source-inputs.json'),futureResultsContract=desc(SOURCE/'future-results-review-contract.json')))
 print(json.dumps(dict(passed=True,checks=checks,strings=7,actualTextCopies=len(copies),actions=False)),flush=True)
if __name__=='__main__':
 assert sys.dont_write_bytecode
 try:main()
 except BaseException as error:save('reader-failure-'+str(time.time_ns())+'.json',dict(schemaVersion=1,name=type(error).__name__,message=str(error),checksCompleted=checks,actionsInvoked=False));raise
