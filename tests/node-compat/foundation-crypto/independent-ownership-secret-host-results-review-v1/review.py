"""Independent actual retained DATA review; no helper, API, engine or host invocation."""
from pathlib import Path
import hashlib,json,os,re,stat,sys,time
OWN=Path(__file__).resolve().parent;K=OWN.parent
OUTPUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-wasmtime-v1')
EXTERNAL=Path(str(OUTPUT)+'-external-root')
SOURCE=K/'ownership-secret-host-candidate-v1'
captured={};identities={};families={};checks=0
TAG='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'
def need(v,label):
 global checks
 assert v,label
 checks+=1
def sig(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):
 need(type(r)is dict and set(r)=={'path','sha256','bytes'},'exact descriptor')
 p=physical(r['path']);need(p.is_absolute()and str(p)==os.path.normpath(str(p)),'canonical absolute evidence')
 for q in(p,*p.parents):need(not q.is_symlink(),'ordinary evidence ancestors')
 s=p.stat();need(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'regular exact-size evidence')
 if r['path']in captured:
  need(captured[r['path']]==r and identities[r['path']]==sig(s),'consistent stable evidence');return p
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(sig(s)==sig(p.stat())and h.hexdigest()==r['sha256'],'stable whole evidence bytes')
 captured[r['path']]=dict(r);identities[r['path']]=sig(s);return p
def data(r):return json.loads(verify(r).read_bytes())
def family(r):
 v=data(r);base=Path(r['path']).parent;names={'index.json'};rows=[r]
 for m in v['files']:
  n=m['path'];need(n not in names and not n.startswith('/')and all(p not in('','.','..')for p in n.split('/')),'confined unique family');names.add(n);row=dict(m,path=str(base/n));verify(row);rows.append(row)
 need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'exact family membership');families[r['path']]=r;return rows
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def wave(raw):
 text=raw.decode('utf8');need(text.endswith('\n')and not text.endswith('\n\n'),'one complete scalar println');text=text[:-1]
 need(text.startswith('"')and text.endswith('"'),'typed whole WAVE string');out=[];at=1
 while at<len(text)-1:
  c=text[at];at+=1
  if c=='\\':
   need(at<len(text)-1,'complete WAVE escape');e=text[at];at+=1
   if e=='u':
    need(text[at]=='{','WAVE scalar braces');end=text.index('}',at+1);digits=text[at+1:end];need(re.fullmatch('[0-9a-fA-F]{1,6}',digits)is not None,'scalar hex');cp=int(digits,16);need(cp<=0x10ffff and not 0xd800<=cp<=0xdfff,'Unicode scalar');out.append(chr(cp));at=end+1
   else:
    escapes={'\\':'\\','"':'"',"'":"'",'n':'\n','r':'\r','t':'\t'};need(e in escapes,'known WAVE escape');out.append(escapes[e])
  else:need(c!='"'and not(ord(c)<32 or 127<=ord(c)<=159),'unescaped scalar content');out.append(c)
 value=''.join(out);need(len(value)<=2097152,'complete bounded wire');return value
def terminal(t,authority=None):
 if authority is not None:
  need(t['rawExitCode']==0 and t['authority']==authority and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True,'outer raw0/groups/auth')
  need(t['forcedCleanup']is t['timeout']is False and all(t[k]==[]for k in('remainingObservedPids','signals','errors','interruptedSignals'))and all(g['alive']is False for g in t['finalGroups']),'outer clean final groups')
 else:
  need(t['status']==0 and t['closed']is t['ownedGroupGone']is t['terminalExitZeroObserved']is True,'inner raw0/closed/group')
  need(t['signal']is t['spawnError']is t['externalSignal']is None and t['timedOut']is t['outputLimitExceeded']is False and t['signalCount']==0 and t['signals']==t['errors']==[],'inner no signal/timeout/overflow/error')
def record_model(w,oracle):
 need(w['schemaVersion']==1 and w['kind']=='crypto-owner-within-export-validation-v1'and w['withinOneOuterExport']is True and w['separateHostCallInterleavingProved']is w['finalizerOrWipeObserved']is False,'wrapper scope')
 zero=dict(inspectCalls=0,runCalls=0,clearCalls=0,validateCalls=0,keyImportsAttempted=0,keyImportsFulfilled=0,signCalls=0,verifyCalls=0)
 need(w['entryCounters']==zero and w['entryState']==dict(rawRetained=False,jwkRetained=False,strongApplicationKeyOwners=0,pendingOperationsInstrumented=False,finalizersOrWipesObserved=False),'fresh empty snapshot state')
 expected=dict(zero,inspectCalls=1,validateCalls=1);need(w['before']['counters']==expected and w['before']['cryptoOperationsAtSnapshot']==0,'initial inspect')
 tags=truth=falsity=imports=0
 need(len(w['records'])==4,'all four guarded cases')
 for case,r in enumerate(w['records']):
  need(r['caseId']==case and r['completed']is True and r['kind']=='crypto-owner-run-v1','ordered completed cases0..3')
  expected['runCalls']+=1
  if case<2:expected['keyImportsAttempted']+=1;expected['keyImportsFulfilled']+=1;expected['signCalls']+=2;expected['verifyCalls']+=2
  elif case==2:expected['signCalls']+=4;expected['verifyCalls']+=4
  else:expected['signCalls']+=3;expected['verifyCalls']+=2
  need(r['counters']==expected,'independent exact cumulative counters')
  need(r['state']==dict(rawRetained=True,jwkRetained=case!=0,strongApplicationKeyOwners=1 if case==0 else 2,pendingOperationsInstrumented=False,finalizersOrWipesObserved=False),'public retained-key state')
  need(r['gcOrEntropyRequested']is r['finalizerCountOrWipeProof']is False,'no GC/erasure inference')
  for obs in r['observations']:
   if obs['phase']!='returned':continue
   v=obs.get('returned',{})
   if obs['operation']=='sign':need(v==dict(type='ArrayBuffer',bytes=32,fullHex=TAG,fullBytesRetained=True),'complete successful32-byte tag');tags+=1
   elif obs['operation']=='verify':need(v['type']=='boolean'and type(v['value'])is bool,'typed whole verify');truth+=int(v['value']);falsity+=int(not v['value'])
   elif obs['operation']=='importKey':need(v==dict(type='object',opaque=True,fullOpaqueValueClaim=False),'opaque key return scope');imports+=1
  result=r['result']
  ops=[result['operations']]if case<2 else [result['raw'],result['jwk']]if case==2 else []
  for op in ops:
   need(op['firstSignatureHex']==op['secondSignatureHex']==oracle['tagHex']==TAG and op['valid']is True and op['invalid']is False,'full expected bytes and true/false')
   need(all(op[k]is True for k in('priorFullBytesStable','independentNonemptyBacking','mutationRestored')),'public successive-signature stability observations')
   need(op['inputBeforeHex']==op['inputAfterHex']=='a5'*8+'4869205468657265'+'a5'*8 and op['inputWindow']==dict(byteOffset=8,byteLength=8,backingBytes=24),'full input window and sentinels')
   need(op['signatureBeforeHex']==op['signatureAfterHex']=='a5'*8+TAG+'a5'*8,'full signature window and sentinels')
  if case==3:
   for key in('signRefusal','verifyRefusal','ordinaryInvalid'):need(result[key]['kind']=='native-promise-rejection'and result[key]['error']['typeError']is True,'guarded TypeError refusals')
   need(all(v==0 for k in('signConversionReads','verifyConversionReads')for v in result[k].values())and result['positiveAlgorithmReads']==result['positiveVerifyAlgorithmReads']==1,'refusal before conversion plus positive getters')
   need(result['positiveFullSignatureHex']==TAG and result['onlyNewGuardedArtifactAllowed']is True and result['uniqueNativeErrorCauseInferred']is False,'guarded positive fulltag/no unique cause')
   need([x['name']for x in result['getters']]==['algorithm','extractable','type','usages']and all(x['error']['typeError']is True for x in result['getters'])and result['constructorError']['typeError']is True,'prototype getters and constructor refuse')
 expected['clearCalls']=1;need(w['released']['counters']==expected and w['released']['applicationReferencesReleased']is True and w['released']['collectionOrNativeFreeOrWipeObserved']is False,'clear releases application references only')
 expected['inspectCalls']=2;need(w['after']['counters']==expected and w['after']['state']==w['entryState'],'final empty application state')
 need((tags,truth,falsity,imports)==(9,5,4,2),'independent one-wrapper coverage');return(tags,truth,falsity,imports)
def main():
 global checks
 start=time.monotonic();rootrow=desc(K/'ownership-secret-host-v1-root-results.json');need(rootrow['sha256'].startswith('a50922')and rootrow['bytes']==5402,'Root terminal report pin');root=data(rootrow)
 need(root['toolObservation']==dict(sessionId=49701,rawExitCode=0,kind='Actual exec-command terminal observation'),'Root tool observation retained, no invented process log')
 source_rows=family(root['sourceIndex']);peer_rows=family(root['sourcePeer']['index']);need(root['sourcePeer']['result']in peer_rows,'Source peer indexed')
 peer=data(root['sourcePeer']['result']);need(peer['sourceIndexSha256']==root['sourceIndex']['sha256']and peer['sourceReviewPassed']is True,'exact passed Source8513 peer')
 refs=data(next(r for r in source_rows if r['path']==str(SOURCE/'references.json')));inputs=data(next(r for r in source_rows if r['path']==str(SOURCE/'source-inputs.json')))
 need(len(inputs['files'])==34403 and len(inputs['families'])==38,'fixed protection manifest, no recursive expansion')
 for r in inputs['files']:verify(r)
 for r in inputs['families']:family(r)
 for r in inputs['modeRows']:need(stat.S_IMODE(verify(r['file']).stat().st_mode)==r['mode'],'current original mode protection')
 authority=data(root['rootAuthority']);config=data(root['rootConfig']);invocation=data(root['invocation']);need(authority['sourceIndex']==root['sourceIndex']==config['sourceIndex']and config['rootAuthority']==root['rootAuthority']and authority['sourceIndependentReview']==root['sourcePeer'],'actual Root/config/Source roles')
 need(authority['wasmtimeValidateAllowed']is authority['guardedPrototypeCase3Allowed']is True and authority['generatedJsAllowed']is authority['gcAllowed']is authority['runtimeAcceptanceClaim']is False,'new bounded host permission only')
 need(invocation['sourceIndex']==root['sourceIndex']and invocation['sourcePeer']==root['sourcePeer']and invocation['rootAuthority']==root['rootAuthority']and invocation['rootConfig']==root['rootConfig'],'original invocation joins')
 parent=data(root['ownedNodeTerminal']);terminal(parent,root['rootAuthority']);verify(parent['stdout']);verify(parent['stderr']);need(parent['stderr']['bytes']==0,'empty outer stderr')
 started=data(desc(EXTERNAL/'started.json'));need(started['pid']==parent['pid']and started['timeoutSeconds']==2400 and started['authority']==root['rootAuthority'],'actual started Node session')
 need(started['argv']==[refs['node']['path'],str(SOURCE/'entry.mjs'),json.dumps(root['rootConfig'],separators=(',',':'))],'plain original Node argv/no flags')
 parent_lines=[json.loads(line)for line in verify(root['parentStdout']).read_text().splitlines()];need(len(parent_lines)==2 and parent_lines[0]==dict(pid=parent['pid'],timeoutSeconds=2400)and parent_lines[1]==root['actualReturnEnvelope'],'whole parent launch/final JSONL')
 need(verify(root['parentStderr']).read_bytes()==b'','empty parent stderr');verify(root['environmentPolicy'])
 index=data(root['actualIndex']);completion=data(root['actualCompletion']);result=data(root['actualHostResult']);names={'index.json','completion.json'}
 for r in index['files']:
  need(r['path']not in names,'unique actual publication row');names.add(r['path']);verify(dict(r,path=str(OUTPUT/r['path'])))
 need({p.relative_to(OUTPUT).as_posix()for p in OUTPUT.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in OUTPUT.rglob('*')),'complete actual output inventory')
 need(completion['index']==dict(root['actualIndex'],path='index.json')and completion['result']==dict(root['actualHostResult'],path='results.json'),'original relative publication descriptors with confined absolute bindings')
 published=json.loads(verify(parent['stdout']).read_bytes());need(published==dict(root=str(OUTPUT),index=completion['index'],completion=dict(root['actualCompletion'],path='completion.json')),'whole Node publication envelope')
 runtime_contract=data(refs['actualRuntimeContract']);runtime_proof=data(refs['actualRuntimeReview']['result']);need(runtime_contract['requiredExactDescriptors']['rawWrapper']==runtime_proof['rawWrapper'],'actual independent Jco whole-wrapper role')
 wrapper=data(runtime_proof['rawWrapper']);oracle=data(runtime_proof['nodeOracle']);need(data(desc(OUTPUT/'node-oracle-reference.json'))==oracle,'unchanged retained Node oracle DATA')
 need(data(runtime_contract['requiredExactDescriptors']['rootAuthority'])['wasmtimeAllowed']is False,'original Jco host permission remains false')
 totals=[0,0,0,0];pids=[];rawrows=[]
 for n,session in enumerate(result['sessions'],1):
  need(session['ordinal']==n,'ordered three sessions');t=data(session['terminal']);terminal(t);pids.append(t['pid']);need(session['pid']==t['pid'],'actual inner PID')
  need(t['executable']==refs['wasmtime']['path']and t['args']==['run','--invoke','validate()',refs['artifacts']['component']['path']]and t['timeoutMs']==600000 and t['maxOutputBytes']==16777216,'literal actual stock Wasmtime argv/bounds')
  launch=data(desc(OUTPUT/'processes'/('validate-'+str(n)+'.launch.json')));need(launch['executable']==t['executable']and launch['args']==t['args']and launch['detachedOwnedSession']is True,'actual direct owned launch')
  raw=verify(t['stdout']).read_bytes();need(verify(t['stderr']).read_bytes()==b'','empty retained WT stderr');value=wave(raw)
  decodedrow=dict(session['decodedString'],path=str(OUTPUT/session['decodedString']['path']));decoded=data(decodedrow);record=data(session['record'])
  need(value==wrapper['observed']['value']==decoded['value']and json.loads(value)==record,'three whole WAVE/Jco/retained-record strings, no projection')
  need(decoded['rawStdout']==t['stdout']and decoded['rawStderr']==t['stderr']and decoded['terminal']==session['terminal'],'raw/decoded/terminal joins')
  counts=record_model(record,oracle);totals=[a+b for a,b in zip(totals,counts)];rawrows.append(dict(ordinal=n,pid=t['pid'],rawStdout=t['stdout'],rawStderr=t['stderr'],terminal=session['terminal'],decodedString=decodedrow,record=session['record']))
 need(len(pids)==len(set(pids))==3 and set(pids)|{parent['pid']}=={r['pid']for r in parent['observedProcesses']},'three fresh sampled WT processes plus exact Node parent')
 need(all(r['ppid']==parent['pid']and r['pgid']==r['pid']for r in parent['observedProcesses']if r['pid']in pids),'fresh owned WT groups under actual parent')
 need(totals==[27,15,12,6],'aggregate actual tags/booleans/imports')
 for k,v in dict(outerPublicStrings=3,withinExportRunRecords=12,guestKeyImports=6,guestSignAttempts=33,guestVerifyAttempts=30,successfulFullTagsCompared=27,fullVerifyBooleans=27,verifyTrue=15,verifyFalse=12).items():need(result[k]==v,'producer result count matches independent DATA '+k)
 need(result['sourceIndexSha256']==root['sourceIndex']['sha256']and result['component']==refs['artifacts']['component']and result['wasmtime']==refs['wasmtime']and result['rootAction']==root['rootAuthority'],'exact actual result source/native/tool identities')
 for p in OUTPUT.rglob('*'):
  s=p.lstat();need(not p.is_symlink()and(stat.S_ISDIR(s.st_mode)and stat.S_IMODE(s.st_mode)==0o700 or stat.S_ISREG(s.st_mode)and s.st_nlink==1),'private directories/regular independent actual files')
 # Capture actual raw text only. Inherited source/proof/package trees remain refs.
 copies=[]
 for lane,path in [('actual',OUTPUT),('external',EXTERNAL)]:
  for p in sorted(path.rglob('*')):
   if not p.is_file():continue
   r=desc(p);verify(r);target=OWN/'evidence'/lane/p.relative_to(path);target.parent.mkdir(parents=True,exist_ok=True);raw=verify(r).read_bytes()
   with target.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
   os.chmod(target,0o600);need(desc(target)['sha256']==r['sha256'],'exact retained raw text copy');copies.append(dict(original=r,copy=desc(target)))
 for lane,r in [('root-results',rootrow),('invocation',root['invocation']),('authority',root['rootAuthority']),('config',root['rootConfig']),('parent-stdout',root['parentStdout']),('parent-stderr',root['parentStderr']),('environment-policy',root['environmentPolicy'])]:
  b=verify(r).read_bytes();target=OWN/'evidence'/(lane+'.json'if lane not in('parent-stdout','parent-stderr')else lane+'.log')
  with target.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
  os.chmod(target,0o600);copies.append(dict(original=r,copy=desc(target)))
 for key in captured:need(identities[key]==sig(physical(key).stat()),'all captured current identities/modes stable')
 for row in source_rows:need(desc(Path(row['path']))==row,'source8513 byte-exact at completion')
 save('raw-evidence.json',dict(schemaVersion=1,copies=copies,inheritedTreesCopied=False))
 save('checks.json',dict(schemaVersion=1,passed=True,checks=checks,fixedCurrentProtectedInputs=34403,fixedInheritedFamilies=38,allFamiliesAuthenticated=len(families),currentUniqueReadHashInputs=len(captured),currentLogicalBytes=sum(r['bytes']for r in captured.values()),actualIndexedFiles=len(index['files']),actualFiles=len(names),actualExternalFiles=len([p for p in EXTERNAL.rglob('*')if p.is_file()]),actualRawTextCopies=len(copies),freshStockWasmtimePids=pids,outerNodePid=parent['pid'],wholeWaveStrings=3,innerCaseRecords=12,fullTags=27,verifyTrue=15,verifyFalse=12,keyImports=6,guestSignAttempts=33,guestVerifyAttempts=30,wholeStringsExactlyEqualJco=True,currentOriginalJcoWasmtimePermissionFalse=True,allCurrentProtectedInputIdentitiesStable=True,actualTimeProtectionEvidence='Successful exact authenticated Source control flow and raw0; independent current hashes, not separately persisted historical recheck samples',ownerActionsInvoked=False,hostActionsInvoked=False,helperApiOrEngineInvoked=False,elapsedDataReadSeconds=time.monotonic()-start))
 save('references.json',dict(schemaVersion=1,rootResult=rootrow,sourceIndex=root['sourceIndex'],sourcePeer=root['sourcePeer'],rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],invocation=root['invocation'],actualIndex=root['actualIndex'],actualResults=root['actualHostResult'],actualCompletion=root['actualCompletion'],outerTerminal=root['ownedNodeTerminal'],parentStdout=root['parentStdout'],parentStderr=root['parentStderr'],actualJcoReview=refs['actualRuntimeReview'],actualJcoContract=refs['actualRuntimeContract'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],component=refs['artifacts']['component'],engine=refs['engine'],metadata=refs['metadata'],wasmtime=refs['wasmtime'],sourceProtection=desc(SOURCE/'source-inputs.json'),futureResultsContract=desc(SOURCE/'future-results-review-contract.json'),rawReturns=rawrows))
 print(json.dumps(dict(passed=True,checks=checks,actualFiles=len(names),rawTextCopies=len(copies),tags=27,ownerActions=False)),flush=True)
if __name__=='__main__':
 assert sys.dont_write_bytecode
 try:main()
 except BaseException as error:save('reader-failure-'+str(time.time_ns())+'.json',dict(schemaVersion=1,name=type(error).__name__,message=str(error),checksCompleted=checks,actionsInvoked=False));raise
