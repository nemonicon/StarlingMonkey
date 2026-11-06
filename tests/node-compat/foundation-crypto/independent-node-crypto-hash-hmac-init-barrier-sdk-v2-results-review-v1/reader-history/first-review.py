"""Retained SDK two-CPP DATA reader; no driver/monitor/compiler/fixture action."""
from pathlib import Path
import hashlib,json,os,stat,ast,shlex
R=Path('/Users/dan/dev/StarlingMonkey');K=R/'tests/node-compat/foundation-crypto';P=Path(__file__).resolve().parent;D=K/'node-crypto-hash-hmac-init-barrier-sdk-syntax-v2';checks=0;seen={};ids={};copies=[]
def yes(v,label='check'):
 global checks
 checks+=1;assert v,label
def identity(p):
 s=Path(p).stat();return dict(mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,links=s.st_nlink,bytes=s.st_size,mtimeNs=s.st_mtime_ns,ctimeNs=s.st_ctime_ns)
def desc(p):
 p=Path(p);yes(p.is_absolute()and '..'not in p.parts)
 for q in [p,*p.parents]:yes(not q.is_symlink(),str(q))
 before=identity(p);yes(stat.S_ISREG(p.lstat().st_mode));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 yes(identity(p)==before,'stable '+str(p));return dict(path=str(p),sha256=h.hexdigest(),bytes=before['bytes'])
def checked(row):
 p=Path(row['path']);yes(set(row)=={'path','sha256','bytes'})
 if str(p)in seen:yes(seen[str(p)]==row and ids[str(p)]==identity(p),'same '+str(p))
 else:yes(desc(p)==row,'hash '+str(p));seen[str(p)]=row;ids[str(p)]=identity(p)
 return p
def read(r):return json.loads(checked(r).read_bytes())
def family(ix):
 value=read(ix);root=Path(ix['path']).parent;names={'index.json'};out=[ix]
 for r in value['files']:
  name=r['path'];yes(name not in names and not Path(name).is_absolute()and all(x not in('','.','..')for x in name.split('/')));names.add(name);r=dict(r,path=str(root/name));checked(r);out.append(r)
 yes(names=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}and not any(p.is_symlink()for p in root.rglob('*')),'closed '+str(root));return out
def copy_text(p,relative):
 p=Path(p);r=desc(p);checked(r);raw=p.read_bytes();raw.decode('utf-8','strict');q=P/relative;yes(not q.exists());q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);yes(q.read_bytes()==raw);copies.append(dict(original=r,copy=desc(q)));return r
def clean(t):
 yes(t['rawExitCode']==0 and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True)
 yes(t['timeout']is t['forcedCleanup']is False and all(t[k]==[]for k in ['signals','interruptedSignals','errors','remainingObservedPids']))
 yes(all(x['alive']is False and x['signalAllowed']is False for x in t['finalGroups']))
rootrow=dict(path=str(K/'node-crypto-hash-hmac-init-barrier-sdk-v2-root-results.json'),sha256='54bef535472bcbe432d0fedf5a2cd2d202bb426a670cffc81382ec69c318451c',bytes=2577);root=read(rootrow);inv=read(root['invocation']);authority=read(root['rootAuthority']);family(root['driverPreparationIndex']);family(root['sourceIndex']);read(root['boundaryAudit']);checked(inv['launcher'])
plan=read(desc(D/'plan.json'));driver=checked(desc(D/'run-sdk-syntax.py')).read_text();yes(root['driverPreparationIndex']['sha256']=='9f0690d3ecd5c96256637718dfe3d1aec4650cab036036a71e680d5223762e9e');yes(root['sourceIndex']['sha256']=='b8a4f219df0b5172361045632d1a1a96f068609496ac8ea128e38eb2aedd6b6c');yes(authority['state']=='ROOT_HASH_HMAC_INIT_BARRIER_TWO_CPP_SYNTAX_AUTHORITY_V2'and authority['sourceReview']==plan['reviewedSourcePair'])
O=Path(plan['outputRoot']);yes(O==Path(root['actualResult']['path']).parent);outputRows=family(root['actualOutputIndex']);result=read(root['actualResult']);yes(result['state']=='INIT_BARRIER_TWO_CPP_FRONTEND_SYNTAX_PASSED_V2'and result['sourceIndex']==root['sourceIndex']and result['rootAuthority']==root['rootAuthority']);yes(root['rawDriverExitCode']==0 and root['syntaxProcessSucceeded']is True)
yes(result['primaryError']is None and result['compilerOnly']is True and result['syntaxOnlyCommandsRequested']==result['compilerStartedRecordsRetained']==2 and result['allPlannedCompilerStartsProved']is True)
yes(all(result[k]is False for k in ['objectOrLinkRequested','nativeBuildHelperEngineGuestCryptoSnapshotInvoked','barrierBehaviorLinkOdrRuntimeOrAdoptionProved']))
for k in ['objectOrLinkInvoked','nativeBuildInvoked','engineInvoked','guestInvoked','cryptoInvoked','snapshotInvoked','phaseBarrierRuntimeBehaviorProved','operationalAdmission']:yes(root[k]is False)
# Only genuine pure parsing and root primitives are extracted, never authenticate/execute/Protection/recheck.
ns={'stat':stat,'shlex':shlex,'os':os}
for name in ['parse_dependencies','tree_snapshot','alias_snapshot','absence_snapshot']:
 node=next(n for n in ast.parse(driver).body if isinstance(n,ast.FunctionDef)and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),str(D/'run-sdk-syntax.py'),'exec'),ns)
before=read(desc(O/'protection-before.json'));final=read(desc(O/'protection-final.json'));yes(final==result['currentInputProtection']);yes(final['unchanged']is True and final['errors']==[]and final['files']==len(before['files'])==12864 and final['trees']==len(before['trees'])==9 and final['aliases']==len(before['aliases'])==34 and final['absentIncludes']==len(before['absentIncludes'])==1)
# Match current bytes and exact actual mode/device/inode/nlink/mtime/ctime to the original pre-frontend capture.
for path,observation in before['files'].items():
 yes(observation['row']['path']==path);p=checked(observation['row']);yes(identity(p)==observation['identity'],'pre/current identity '+path)
for path,snapshot in before['trees'].items():yes(ns['tree_snapshot'](Path(path))==snapshot,'tree '+path)
for path,a in before['aliases'].items():yes(a['expected']['path']==path and ns['alias_snapshot'](a['expected'])==a['observed'],'alias '+path)
for path,a in before['absentIncludes'].items():yes(a['policy']['path']==path and a['policy']['mustRemainAbsent']is True and a['policy']['missingPathMayBeCreated']is False);yes(ns['absence_snapshot'](Path(path))==a['observed'],'absence '+path)
yes(len(plan['protectedTrees'])==4 and sum(x['regularFiles']for x in plan['protectedTrees'])==12748);yes(sum(x['symlinks']for x in plan['protectedTrees'])==34)
for tree in plan['protectedTrees']:
 prefix=tree['path']+'/';selected=[r for path,r in before['files'].items()if path.startswith(prefix)];yes(len(selected)==tree['regularFiles']);yes(before['trees'][tree['path']]['files']==sorted(str(Path(r['row']['path']).relative_to(tree['path']))for r in selected))
executed=read(desc(O/'executed-plan.json'));yes(executed['requestedPreparationPlan']==plan and executed['actualAuthority']==root['rootAuthority']and executed['planCaptureSlotsAreNotOutcomeRecords']is True);yes(read(desc(O/'overlay.json'))==plan['overlay'])
# Three private physical afterimages are real pre-observed inputs, not modified native source.
for r in plan['candidateFiles']:
 p=checked(dict(r['after'],path=r['privatePath']));yes(p.read_bytes()==checked(r['after']).read_bytes());s=p.stat();a=Path(r['after']['path']).stat();yes(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and(s.st_dev,s.st_ino)!=(a.st_dev,a.st_ino));checked(r['before'])
# Exact outer original monitor argv/transport, with all raw records retained.
outerRoot=Path(root['ownedTerminal']['path']).parent;outer=read(root['ownedTerminal']);clean(outer);start=read(desc(outerRoot/'started.json'));yes(start['argv']==inv['actualArgv']and start['timeoutSeconds']==inv['outerDeadlineSeconds']==300 and start['authority']==root['rootAuthority']);yes(outer['authority']==root['rootAuthority']);yes(checked(outer['stderr']).read_bytes()==b'')
outerFrames=[json.loads(x)for x in checked(outer['stdout']).read_text().splitlines()];yes(len(outerFrames)==3);yes(outerFrames[-1]==dict(result=root['actualResult'],index=root['actualOutputIndex'],state=result['state']))
units=[];allDependencyPaths=set();mapping={r['name']:r['external-contents']for r in plan['overlay']['roots']};header=plan['candidateFiles'][0]
yes([x['id']for x in result['units']]==[x['id']for x in plan['units']])
for n,(u,v)in enumerate(zip(plan['units'],result['units'])):
 yes(v==read(desc(O/'unit-outcomes'/(u['id']+'.json'))));yes(v['monitorReturned']is v['actualStartedRecordPresent']is v['ownedGroupsClean']is True and v['rawExitCode']==0 and v['commandError']is v['dependencyError']is None)
 terminal=read(v['raw']['terminal.json']);clean(terminal);started=read(v['raw']['started.json']);yes(started['argv']==u['argv']and started['timeoutSeconds']==60 and started['authority']==root['rootAuthority']);yes(terminal['pid']==started['pid']and terminal['authority']==root['rootAuthority']);yes(outerFrames[n]==dict(pid=started['pid'],timeoutSeconds=60))
 yes(checked(v['raw']['stdout.log']).read_bytes()==checked(v['raw']['stderr.log']).read_bytes()==b'');yes(terminal['stdout']==v['raw']['stdout.log']and terminal['stderr']==v['raw']['stderr.log'])
 words=started['argv'];yes(words.count('-fsyntax-only')==1 and '-c'not in words and '-o'not in words and words[-1]==u['privateMainPath']);yes('-DNODE_COMPAT_CRYPTO_HASH_HMAC=1'in words and '-DNODE_COMPAT_STRICT_INITIALIZATION=1'in words and '-O3'in words and '-DNDEBUG'in words);yes(not any(x.startswith(('-DDEBUG','-DNODE_CRYPTO_AUDITED_BORROW','-DNODE_COMPAT_OOM','-DNODE_COMPAT_GC_STRESS'))for x in words))
 dependencyText=checked(v['dependencyFile']).read_text();names=ns['parse_dependencies'](dependencyText,u['dependencyTarget']);yes(names==[x['reportedPath']for x in v['dependencies']]);roles=collections.Counter()if False else {}
 for name,row in zip(names,v['dependencies']):
  logical=os.path.abspath(os.path.join(u['cwd'],name));physical=str(Path(mapping.get(logical,logical)).resolve(strict=True));yes(row['normalizedLogicalPath']==logical and row['physicalPath']==physical and row['authenticatedBeforeFrontend']is True);prior=before['files'].get(physical);yes(prior is not None and row['descriptor']==prior['row']);checked(row['descriptor']);allDependencyPaths.add(physical)
  kind='private-afterimage'if physical.startswith(str(O)+'/native/')else'preauthenticated-original';roles[kind]=roles.get(kind,0)+1
 yes(any(row['physicalPath']==u['privateMainPath']for row in v['dependencies']));yes(any(row['physicalPath']==header['privatePath']and row['normalizedLogicalPath']==header['before']['path']for row in v['dependencies']),'changed header VFS role')
 units.append(dict(id=u['id'],actualStarted=v['raw']['started.json'],actualTerminal=v['raw']['terminal.json'],actualArgv=started['argv'],rawExitCode=0,timeoutSeconds=60,stdoutBytes=0,stderrBytes=0,interruptions=[],dependencyFile=v['dependencyFile'],dependencyOccurrences=len(names),dependencyRoles=roles,changedHeaderObservedViaVfs=True))
yes([u['dependencyOccurrences']for u in units]==[1021,1052]);yes(len(outputRows)==23)
# Repeat the full current captured files/root membership/absence; no external guard helper invoked.
for path,observation in before['files'].items():yes(desc(path)==observation['row']and identity(path)==observation['identity'],'final current '+path)
for path,snapshot in before['trees'].items():yes(ns['tree_snapshot'](Path(path))==snapshot)
for path,a in before['aliases'].items():yes(ns['alias_snapshot'](a['expected'])==a['observed'])
for path,a in before['absentIncludes'].items():yes(ns['absence_snapshot'](Path(path))==a['observed'])
family(root['actualOutputIndex']);family(root['driverPreparationIndex']);family(root['sourceIndex'])
# Portable byte-exact text capsule. Its nested original index.json is included in our final root index.
for r in outputRows:
 p=Path(r['path']);copy_text(p,Path('capsule/sdk-output')/p.relative_to(O))
for p in sorted(outerRoot.rglob('*')):
 if p.is_file():copy_text(p,Path('capsule/root-monitor')/p.relative_to(outerRoot))
for name,row in [('root-results.json',rootrow),('root-invocation.json',root['invocation']),('root-authority.json',root['rootAuthority']),('driver.py',desc(D/'run-sdk-syntax.py')),('prepared-plan.json',desc(D/'plan.json'))]:copy_text(row['path'],Path('capsule/context')/name)
for r in seen.values():yes(desc(r['path'])==r,'sealed observed '+r['path'])
summary=dict(schemaVersion=1,passed=True,checks=checks,currentCapturedInputs=12864,requiredTreeInputs=12748,requiredTrees=4,totalCapturedTrees=9,capturedAliases=34,capturedAbsentIncludes=1,currentOriginalIdentityAndBytesMatchActualBefore=True,originalFinalProtectionPassed=True,actualFrontends=2,rawDriverExitCode=0,allOwnedGroupsGone=True,unitResults=units,distinctPhysicalDependencyFiles=len(allDependencyPaths),actualSdkPayloadFilesCopied=0,actualOutputPayloads=22,actualOutputFilesIncludingOriginalIndex=23,portableTextFiles=len(copies),reviewerCompilerOrDriverMonitorHelperFixtureEngineCryptoInvoked=False)
(P/'data-check-results.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'capsule-copy-map.json').write_text(json.dumps(dict(schemaVersion=1,files=copies,originalPathsAndFramesRewritten=False),indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='unitResults'}))
