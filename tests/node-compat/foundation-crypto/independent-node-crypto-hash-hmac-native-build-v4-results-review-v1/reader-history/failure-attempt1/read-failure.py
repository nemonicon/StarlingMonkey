"""Independent BUILD4 failure DATA/bookend reader. No owner API or tool calls."""
from pathlib import Path
import hashlib,json,os,stat
P=Path(__file__).resolve().parent;K=P.parent;S=K/'node-crypto-hash-hmac-native-controller-candidate-v3'
files={};identities={};checks=0
def need(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def identity(p):
 s=Path(p).lstat();return[s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def measure(path):
 p=Path(path);a=identity(p);need(stat.S_ISREG(a[2]),'regular bounded file');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(identity(p)==a,'stable read identity');r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[3])
 if str(p)in files:need(files[str(p)]==r and identities[str(p)]==a,'unchanged repeated current input')
 files[str(p)]=r;identities[str(p)]=a;return r
def check(r):v=measure(r['path']);need(v==r,'exact fixed descriptor '+r['path']);return Path(r['path'])
def data(r):return json.loads(check(r).read_bytes())
def family(r):
 p=check(r);v=json.loads(p.read_bytes());names={'index.json'}
 for x in v['files']:
  need(x['path']not in names and not Path(x['path']).is_absolute()and '..'not in Path(x['path']).parts,'unique confined family member');names.add(x['path']);check(dict(x,path=str(p.parent/x['path'])))
 need(names=={q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()}and not any(q.is_symlink()for q in p.parent.rglob('*')),'whole exact family membership');return v
def dump(name,v):(P/name).write_text(json.dumps(v,indent=2)+'\n')
def main():
 rootrow=dict(path=str(K/'node-crypto-hash-hmac-native-build-v4-root-results.json'),sha256='b1b62f951c52f939b424c4c42a4ce89657373df937aa581bcc50a986338491cb',bytes=6810);root=data(rootrow)
 need(root['toolObservation']==dict(sessionId=62405,rawExitCode=1),'original actual failed tool terminal')
 family(root['controllerIndex']);family(root['sourcePeer']['index']);data(root['sourcePeer']['result']);refs=json.loads((S/'references.json').read_bytes());result=data(root['actualBuildResult'])
 for k in ['rootAuthority','config','invocation','observer','integrationSourceIndex','buildLog','actualEngine','actualMetadata','inputRecheck']:check(root[k])
 compiler=json.loads((P/'compile-data-review.json').read_bytes());gitindex=json.loads((P/'git-index-data-review.json').read_bytes())
 need(compiler['compilerAndLinkDataChecksPassed']is True and compiler['engine']==root['actualEngine']and compiler['metadata']==root['actualMetadata']and compiler['actualBuildResult']==root['actualBuildResult'],'whole actual compiler report bindings')
 need(compiler['buildAccepted']is compiler['wholePreservationPassed']is False and root['changedInput']==dict(expected=gitindex['originalExpectedIndex'],actual=gitindex['actualIndex']),'failure/index report exact binding')
 protected=json.loads((S/'source-inputs.json').read_bytes());changed=[]
 for expected in protected['files']:
  actual=measure(expected['path'])
  if actual!=expected:changed.append(dict(expected=expected,actual=actual))
 need(changed==[root['changedInput']],'only known current private index byte exception in declared source inputs')
 configured=json.loads((S/'configured-tree.json').read_bytes())
 for x in configured['files']:need(stat.S_IMODE(Path(x['file']['path']).stat().st_mode)==x['mode'],'actual configured file mode unchanged')
 for x in json.loads((P/'compile-data-input-hashes.json').read_bytes())['files']:check(x)
 groups={};rawcopy=[]
 for key in ['externalParentTerminal','outerTerminal']:
  terminal=data(root[key]);need(terminal['rawExitCode']==1 and terminal['timeout']is terminal['forcedCleanup']is False and terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True,'genuine nonzero clean parent terminal')
  for f in ['interruptedSignals','remainingObservedPids','signals','errors']:need(terminal[f]==[],'no parent interruption/error/remaining processes')
  need(all(x['alive']is False for x in terminal['finalGroups']),'every actual final group absent')
  for stream in ['stdout','stderr']:check(terminal[stream])
  groups[key]=dict(pid=terminal['pid'],rawExitCode=terminal['rawExitCode'],allObservedGroupsGone=True,observedProcesses=len(terminal['observedProcesses']),finalGroups=len(terminal['finalGroups']),operationalElapsedSeconds=terminal['operationalElapsedSeconds'])
 for key in ['externalStdout','externalStderr','outerStdout','outerStderr']:check(root[key])
 external=json.loads(Path(root['externalStdout']['path']).read_bytes());need(external['result']==result,'whole external stdout result envelope equals durable result')
 outer=json.loads(Path(root['outerStdout']['path']).read_bytes());need(outer==dict(pid=groups['externalParentTerminal']['pid'],timeoutSeconds=7200),'actual outer launch-only JSONL')
 stderr=Path(root['externalStderr']['path']).read_text();need(all(s in stderr for s in ['finally:recheck(frame)',"frame['capture'].recheck()",'for r in list(self.files.values()):self.add(r)',"assert sha(p)==r['sha256']and identity(p)==before;return p",'AssertionError']),'actual preservation stack through original checked descriptor')
 need(result['rawChildExitCode']==0 and result['launcherExitCode']==1 and result['lifecycleComplete']is True and result['evidenceComplete']is False and result.get('allSourceStageOriginalAndCacheInputsPreserved')is not True,'wrapper failure remains literal')
 for x in result['cacheCopiesCompleted']:
  a=check(x['source']).stat();b=check(x['target']).stat();need(stat.S_IMODE(a.st_mode)==x['sourceMode']and stat.S_IMODE(b.st_mode)==x['outputMode']and b.st_nlink==1 and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'all4 actual cache bytes/modes/singlelinks/distinctinodes')
 aliases=[]
 for base in [Path(refs['configuredSourceRoot']),Path(refs['workRoot'])/'cache/wasi-sdk']:
  for p in sorted(base.rglob('*')):
   if p.is_symlink():aliases.append(dict(path=str(p),linkText=os.readlink(p),resolved=str(p.resolve(strict=True))))
 for row in aliases:need(os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolved'],'current alias relation')
 # Keep only current finite text evidence; no inherited tree copies.
 for key in ['actualBuildResult','externalParentTerminal','outerTerminal','externalStdout','externalStderr','outerStdout','outerStderr','buildLog','inputRecheck','rootAuthority','config','invocation','observer']:
  r=root[key];src=check(r);dest=P/'raw-evidence'/(key+'-'+src.name);dest.parent.mkdir(exist_ok=True);dest.write_bytes(src.read_bytes());need(hashlib.sha256(dest.read_bytes()).hexdigest()==r['sha256'],'byte exact actual textcopy');rawcopy.append(dict(original=r,copy=dict(path=dest.relative_to(P).as_posix(),sha256=r['sha256'],bytes=r['bytes'])))
 # Current independent before/final hash+identity window, not original-time attestation.
 before=list(files.values());beforeids=dict(identities)
 for r in before:check(r)
 need(identities==beforeids,'whole finite current before/final identity stability')
 for row in aliases:need(os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolved'],'final current alias relation')
 dump('input-hashes.json',dict(schemaVersion=1,scope='Complete finite current independent failure-review boundary: original controller declared files/families, current compiler/link/source witness inputs and actual raw Root/parent files; NOT a full future-freezer distribution ledger',files=sorted(files.values(),key=lambda x:x['path'])))
 dump('reference-aliases.json',dict(schemaVersion=1,scope='Current configured SOURCE and private WORK3 SDK symlink relations only; no global alias attestation',symlinks=aliases,archiveHardlinks=[]))
 dump('index-exception.json',dict(schemaVersion=1,originalExpected=root['changedInput']['expected'],currentActual=root['changedInput']['actual'],originalBytePreservationPassed=False,currentIndexSemanticBaseline742Equal=True,originalIndexPreimageRetained=False,indexStatOnlyDeltaProved=False,exactIndexWriterProved=False,oldResultOrSourceChanged=False))
 dump('raw-copy-map.json',dict(schemaVersion=1,files=rawcopy))
 dump('failure-data-review.json',dict(schemaVersion=1,checks=checks,rootObservation=rootrow,actualBuildResult=root['actualBuildResult'],sourceIndex=root['controllerIndex'],sourcePeer=root['sourcePeer'],recipeRawExitCode=0,parentTerminals=groups,actualChangedInputs=changed,sourceDeclaredRows=len(protected['files']),currentIndependentFiles=len(files),currentIndependentBytes=sum(x['bytes']for x in files.values()),currentBeforeFinalHashIdentityStable=True,currentAliasCount=len(aliases),rawCopies=len(rawcopy),wrapperPreservationFailed=True,compilerAndLinkDataChecksPassed=True,indexSemanticBaselineParity=True,statOnlyIndexDeltaProved=False,exactIndexWriterProved=False,buildAccepted=False,ownerApisOrToolsInvoked=False))
 print(json.dumps(dict(failureDataReviewPassed=True,checks=checks,currentFiles=len(files),aliases=len(aliases),actualExceptionCount=len(changed),rawCopies=len(rawcopy),buildAccepted=False)))
if __name__=='__main__':main()
