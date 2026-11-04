"""Independent actual source-copy reader. No Git, owner imports or action calls."""
import hashlib
import json
import stat
from pathlib import Path

P=Path(__file__).resolve().parent
K=P.parent
C=K/'native-integration-candidate-v2'
S=Path('/tmp/starling-node-compat/crypto-owner-source-v2')
Q=K/'independent-crypto-owner355-native-integration-v2-source-review-v1'
ROOT=K/'native-integration-v2-source-stage-root-results.json'
seen={}

def need(value,message):
 if not value:raise AssertionError(message)
def row(path,expected=None):
 path=Path(path);s=path.lstat();need(stat.S_ISREG(s.st_mode),'Ordinary file: '+str(path));h=hashlib.sha256()
 with path.open('rb')as stream:
  for b in iter(lambda:stream.read(1048576),b''):h.update(b)
 r=dict(path=str(path),sha256=h.hexdigest(),bytes=s.st_size)
 if expected:need(all(r[k]==expected[k]for k in ('sha256','bytes')),'Exact tuple '+str(path))
 seen[str(path)]=r;return r
def data(path):return json.loads(Path(path).read_bytes())
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
def indexed(root,pin):
 need(row(root/'index.json')['sha256']==pin,'Exact source/index '+str(root));ix=data(root/'index.json')
 for r in ix['files']:row(root/r['path'],r)
 return ix
def main():
 root=row(ROOT,dict(sha256='a0654a8ec71fc293644d69942db0b7444227132b48cd5c770c121a402225d101',bytes=717806));r=data(ROOT)
 need(r['state']=='ROOT_OBSERVED_NEW_CRYPTO_OWNER355_V2_SOURCE_STAGE_RAW_ZERO'and r['destination']==str(S),'Actual Root source-only stage record')
 for key in ('sourceIndex','rootAuthority','externalTerminal','externalLaunchSource','publicationJournal'):
  d=r[key];row(d['path'],d)
 for d in r['sourceIndependentReview'].values():row(d['path'],d)
 source_pin='68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'
 own=indexed(C,source_pin)
 indexed(Q,'ebbfda800fc288ea249b9c2e3af2f77a6a0ae1153bc9586b9aab91999a060dac')
 need(data(Q/'results.json')['sourceReviewPassed']is True,'Prior exact source review passed')
 authority=data(r['rootAuthority']['path'])
 need(authority['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_SOURCE_STAGE_V2'and authority['sourceIndexSha256']==source_pin and authority['destination']==str(S),'Root authority exact source/destination')
 need(authority['sourceStageAllowed']is True and authority['nativeBuildOrRuntimeAllowed']is False,'Root authority permits copy only')
 need(authority['independentSourceReview']==r['sourceIndependentReview'],'Root authority points to exact indexed independent source result')
 terminal=data(r['externalTerminal']['path'])
 need(terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['pid']==50423,'Retained Root terminal raw0/no timeout/PID50423; not directly observed by this reader')
 for key in ('stdout','stderr'):row(terminal[key]['path'],terminal[key])
 need(Path(terminal['stderr']['path']).stat().st_size==0,'Actual stage stderr empty')
 journal=data(r['publicationJournal']['path']);stdout=data(terminal['stdout']['path'])
 need(stdout==journal,'Exact stdout publication state equals retained journal')
 need(journal['state']=='NEW_CRYPTO_OWNER355_SOURCE_STAGED_NOT_BUILT'and journal['sourceIndexSha256']==source_pin,'Source staged, not built')
 need(journal['metadataProjected']is False and journal['preparationManifestsInterpreted']is False and journal['nativeBuildOrCryptoOrGuestExecuted']is False,'No metadata projection/prep rebasing/native/crypto/guest claim')
 expected_commands=[['git','clone','--no-local','--no-checkout','/Users/dan/dev/StarlingMonkey',str(S)],['git','-C',str(S),'checkout','--detach','54b3329b3ce818fd1f244e871e9c259b63667cda']]
 need([x['argv']for x in journal['commands']]==expected_commands and all(x['returncode']==0 for x in journal['commands']),'Root retained fresh ordinary clone54b command records both0; no reviewer Git invocation')
 need(S.is_dir()and not S.is_symlink()and(S/'.git').is_dir()and not(S/'.git').is_symlink(),'Actual isolated directory with ordinary .git directory')
 need((S/'.git/HEAD').read_text().strip()=='54b3329b3ce818fd1f244e871e9c259b63667cda','Actual detached HEAD54b read as data')
 need(not(S/'.git/objects/info/alternates').exists()and not(S/'.git/objects/info/alternates').is_symlink(),'No Git alternates file or link')
 row(S/'.git/HEAD');row(S/'.git/config')
 # All copied native/tool/self rows are reconstructed from the original source
 # contexts, never by treating staged input-freeze relative to the stage.
 expected={}
 def add(name,original,sha,size,role):
  need(not Path(name).is_absolute()and all(x not in ('','.','..')for x in name.split('/')),'Safe copied path')
  if name in expected:
   need(expected[name]['sha256']==sha and expected[name]['bytes']==size,'Only equal-byte staged overlap');expected[name]['roles'].append(role)
  else:expected[name]=dict(path=name,original=str(original),sha256=sha,bytes=size,roles=[role])
 policy=data(C/'policy.json');manifest={x['path']:x['sha256']for x in policy['expectedNativeSourceManifest']}
 origins=data(C/'native-origins.json')['files'];tools=data(C/'tool-origins.json')['files'];pins=data(C/'artifact-tools/tool-pins.json')
 need(len(origins)==355 and len(tools)==922 and {x['path']:(x['sha256'],x['bytes'])for x in tools}=={x['path']:(x['sha256'],x['bytes'])for x in pins['toolDependencies']},'Actual full355 and922 origin/tool contracts')
 for x in origins:
  need(manifest[x['path']]==x['sha256'],'Native origin exactly full new355 manifest')
  add(x['path'],x['original'],x['sha256'],Path(x['original']).stat().st_size,'EXACT_NEW_NATIVE355')
 for x in tools:add(x['path'],x['original'],x['sha256'],x['bytes'],'PINNED_BUILD_TOOL_OR_SOURCE_ANCESTRY')
 prefix='tests/node-compat/foundation-crypto/native-integration-candidate-v2'
 add(prefix+'/index.json',C/'index.json',source_pin,(C/'index.json').stat().st_size,'OWN_SOURCE_SEAL')
 for x in own['files']:add(prefix+'/'+x['path'],C/x['path'],x['sha256'],x['bytes'],'OWN_SOURCE_SEAL')
 need(len(expected)==1311 and len(r['files'])==len({x['path']for x in r['files']})==1311,'Exact1311 unique declared actual copies')
 actual={x['path']:x for x in r['files']};need(set(actual)==set(expected),'Actual copied membership equals independently assembled native/tool/self closure')
 copies=[]
 for name in sorted(expected):
  e=expected[name];a=actual[name]
  need(all(a[k]==e[k]for k in ('path','original','sha256','bytes','roles')),'Actual descriptor matches independent origin/context '+name)
  src=Path(e['original']);dst=S
  for part in name.split('/'):
   dst/=part;need(not dst.is_symlink(),'No symlink in staged copied path '+name)
  row(src,e);row(dst,e)
  s=src.lstat();d=dst.lstat();sm=stat.S_IMODE(s.st_mode);dm=stat.S_IMODE(d.st_mode)
  need(sm==dm==a['sourceMode']==a['outputMode'],'Exact original/staged modes '+name)
  need((s.st_dev,s.st_ino)!=(d.st_dev,d.st_ino)and a['distinctSourceAndDestinationInodes']is True,'Distinct original/staged inode '+name)
  copies.append(dict(**e,sourceMode=sm,outputMode=dm,distinctSourceAndDestinationInodes=True))
 staged_source=S/prefix
 need(row(staged_source/'index.json')['sha256']==source_pin,'Staged immutable44+index exact original seal')
 for x in own['files']:row(staged_source/x['path'],x)
 for x in policy['cryptoKeyOwnershipSourcePolicy']['changes']:
  need(row(S/x['path'])['sha256']==x['afterSha256'],'Actual new crypto ownership/prototype payload staged '+x['path'])
 # Ordinary --no-local clone objects must not share inode with original repo.
 original_objects=Path('/Users/dan/dev/StarlingMonkey/.git/objects')
 source_inodes={(x.stat().st_dev,x.stat().st_ino)for x in original_objects.rglob('*')if x.is_file()}
 object_files=[x for x in (S/'.git/objects').rglob('*')if x.is_file()]
 for f in object_files:
  need(not f.is_symlink()and(f.stat().st_dev,f.stat().st_ino)not in source_inodes,'Independent clone Git object inode')
 # The checked-in preparation manifest stays in its original context.  Its
 # bytes are copied, but no owner prep interpretation is executed by reviewer.
 need(data(staged_source/'input-freeze.json')==data(C/'input-freeze.json'),'Original1323 preparation bytes preserved without relocation interpretation')
 contract=data(C/'bootstrap-contract.json')
 need(not Path(contract['nativeBuildRoot']).exists()and not Path(contract['freezeRoot']).exists(),'New build/freeze namespaces absent at this stage observation')
 for name in ('runtime-pins.json','bootstrap-pins.json'):
  need(all(v is None for v in data(staged_source/name)['variants'].values()),'Staged four future pins remain null')
 # Extract only the static literal environment for the existing launcher,
 # supplemented by the source's explicit normal-off conditionals.
 env={
  'NODE_COMPAT_NODE':'/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
  'NODE_COMPAT_JOBS':'1','BINARYEN_CORES':'1','RAYON_NUM_THREADS':'1','CARGO_BUILD_JOBS':'1',
  'NODE_COMPAT_BUILD_TYPE':'Release','NODE_COMPAT_OOM_TESTING':'0','NODE_COMPAT_BUILD_ROOT':contract['nativeBuildRoot'],
  'NODE_COMPAT_ABI_FIX':'1','NODE_COMPAT_BIGINT_FIX':'1','NODE_COMPAT_INTERNAL_TICKS':'1','NODE_COMPAT_CLASSIC_STREAMS':'1',
  'NODE_COMPAT_ZLIB':'1','NODE_COMPAT_STREAM_CONSUMERS':'1','NODE_COMPAT_ENTROPY_MODE':'OFF','NODE_COMPAT_GC_STRESS':'0',
  'NODE_COMPAT_ARTIFACT_TAG':'ko355v2',
  **{'NODE_COMPAT_'+n:'1'for n in ('PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB')}}
 suffix='keyowner-v2.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1'
 artifact='starlingmonkey_embedding.abi-i32-i64-v1.'+suffix+'.ko355v2.wasm'
 recommendation=dict(schemaVersion=1,state='EXISTING_SOURCE_REVIEWED_NORMAL_OFF_BUILD_ENTRY_NOT_EXECUTED',
  argv=['/usr/bin/python3',str(staged_source/'artifact-tools/build-one.py'),'normal-off'],cwd=str(S),
  outerEnvironment=dict(PYTHONDONTWRITEBYTECODE='1'),outerEnvironmentUnset=['PYTHONOPTIMIZE','PYTHONPATH','NODE_OPTIONS','NODE_PATH'],
  launcherManagedChildEnvironment=env,launcherManagedChildEnvironmentRule='Remove inherited NODE_COMPAT_* and CMAKE_PROJECT_* plus NODE_OPTIONS, then use the existing literal environment in build-one.py.',
  recipePath=str(S/'tests/node-compat/build-engine.sh'),recipeSha256=pins['recipeSha256'],
  configuredRoot=str(S),workRoot=contract['nativeBuildRoot'],sourceProject=str(Path(contract['nativeBuildRoot'])/('componentize-abi-fixed-bigint-v1-'+suffix)),cmakeProject=str(Path(contract['nativeBuildRoot'])/('engine-abi-fixed-bigint-v1-'+suffix)),
  engineArtifact=str(Path(contract['nativeBuildRoot'])/'artifacts'/artifact),sidecarArtifact=str(Path(contract['nativeBuildRoot'])/'artifacts'/(artifact+'.build.json')),
  launcherOutput=str(Path(contract['freezeRoot']).parent/'builds/normal-off'),futureFreezeRoot=contract['freezeRoot'],
  requiredStartFreeBytes=2*1024**3,stopBelowFreeBytes=800*1024**2,parallelBuilds=1,
  authorityDisposition='Requires separate explicit Root native-build authorization; stage copy authority forbids build/runtime. No runtime or operational authority supplied here.',
  sourceCitations=[dict(path=str(staged_source/'artifact-tools/build-one.py'),line=229),dict(path=str(staged_source/'artifact-tools/build-one.py'),line=247),dict(path=str(staged_source/'artifact-tools/build-one.py'),line=284),dict(path=str(S/'tests/node-compat/build-engine.sh'),line=118)],actionExecuted=False)
 result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_V2_ACTUAL_SOURCE_STAGE_VERIFIED_V1',sourceOnly=True,actualSourceStageReviewPassed=True,
  sourceIndexSha256=source_pin,rootStageResult=root,sourceReviewIndexSha256=row(Q/'index.json')['sha256'],destination=str(S),
  copiedPathsVerified=1311,nativeSourcePathsVerified=355,toolPathsVerified=922,ownIndexedFilesVerified=44,ownIndexCopied=True,cryptoChangedPayloadsVerified=5,
  exactModesVerified=True,distinctOriginalAndCopiedInodesVerified=True,allDeclaredSourceOriginsAndDestinationBytesRehashed=True,uniqueFileTuplesRehashed=len(seen),
  git=dict(baseCommit='54b3329b3ce818fd1f244e871e9c259b63667cda',detachedHeadReadAsData=True,ordinaryDotGitDirectory=True,alternatesPresent=False,cloneObjectFilesChecked=len(object_files),gitObjectInodesDistinctFromOriginal=True,reviewerGitInvoked=False),
  originalPreparationContextPreserved=True,preparationManifestReinterpreted=False,
  rootReportedProcess=dict(sessionId=91711,pid=terminal['pid'],rawExitCode=terminal['rawExitCode'],timeout=terminal['timeout'],elapsedSeconds=terminal['elapsedSeconds'],observedByThisReader=False,provenance='Authenticated retained Root terminal and exact journal/stdout, not a new execution.'),
  actualNativeBuildExecuted=False,newNativeArtifactAccepted=False,ownerHelpersOrGitOrSdkOrCompilerOrKeyCryptoGcComponentGuestHostActionsInvokedByThisReader=False,
  operationalAdmission=False,runtimeAcceptanceClaim=False,runtimeBackendProof=contract['runtimeBackendProof'],futureEnginePins=None,
  remainingFollowons=policy['cryptoKeyOwnershipSourcePolicy']['remainingFollowons'])
 write('verified-copies.json',copies);write('normal-off-build-entry.json',recommendation)
 write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('results.json',result)
 print(json.dumps(dict(state=result['state'],copies=1311,inputs=len(seen),gitObjects=len(object_files))))
if __name__=='__main__':main()
