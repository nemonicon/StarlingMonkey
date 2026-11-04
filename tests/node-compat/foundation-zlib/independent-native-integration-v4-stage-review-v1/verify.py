"""Independent isolated-stage reader. No source/helper/build/test execution.

The sole subprocess is read-only Git ls-tree with optional locks disabled.
"""
from pathlib import Path
import hashlib,json,os,stat,subprocess
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=HERE.parents[3]
STAGE=Path('/tmp/starling-node-compat/zlib-source-v4')
REL=Path('tests/node-compat/foundation-zlib/native-integration-candidate-v4')
OWNER=REPO/REL;STAGED=STAGE/REL
INDEX='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
ROOT_SHA='9c6b7f9b458197535ee4bda827178a4bcda6227819a80682947740cd0d606443'
HEAD='54b3329b3ce818fd1f244e871e9c259b63667cda'
seen={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path,h=None,size=None):
 p=Path(path);a=p.lstat();assert stat.S_ISREG(a.st_mode)and not p.is_symlink(),p;checksum=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1024*1024),b''):checksum.update(block)
 z=p.lstat()
 assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns),p
 digest=checksum.hexdigest();assert h is None or digest==h,p;assert size is None or z.st_size==size,p
 key=str(p.absolute());row={'path':key,'sha256':digest,'bytes':z.st_size};assert key not in seen or seen[key]==row,p;seen[key]=row
 if z.st_size<=8*1024*1024:
  b=p.read_bytes();assert sha(b)==digest;return b
 return None
def doc(p,h=None):return json.loads(read(p,h))
def below(root,name):
 assert not Path(name).is_absolute()and all(x not in('','.','..')for x in name.split('/'))
 p=root
 for x in name.split('/'):p/=x;assert not p.is_symlink(),p
 return p
def indexed(root,h,count):
 j=doc(root/'index.json',h);assert len(j['files'])==count
 for row in j['files']:read(below(root,row['path']),row['sha256'],row['bytes'])
 return j
assert not(HERE/'results.json').exists()
root=doc(FAMILY/'native-integration-v4-root-stage-results.json',ROOT_SHA)
assert root['sourceIndexSha256']==INDEX and root['sourceRoot']==str(STAGE)
assert len(root['evidence'])==46
for row in root['evidence']:read(row['path'],row['sha256'],row['bytes'])
assert root['sourceCheckRootSession']==34385 and root['mainEightCheckRawExit']==root['linkChainCheckRawExit']==0 and root['sourceCheckCommands']==9
assert root['planApplyVerifyRootSession']==89971 and root['planRawExit']==root['applyRawExit']==root['actualStageVerifyRawExit']==root['actualFactoryCheckRawExit']==root['actualGitHeadRawExit']==0
assert root['nativeBuildStarted']is root['guestExecuted']is root['runtimeAcceptanceClaim']is root['performanceClaim']is False
assert STAGE.is_dir()and not STAGE.is_symlink()and not STAGE.with_name(STAGE.name+'.staging').exists()
assert STAGE.stat().st_ino!=REPO.stat().st_ino
original_index=indexed(OWNER,INDEX,85);staged_index=indexed(STAGED,INDEX,85);assert original_index==staged_index
peer=FAMILY/'independent-native-integration-v4-source-review-v1';indexed(peer,'31d5408eb5567f4e5e925811b33c4e8ec32ad28bb90bc3f844f23c65393145af',12)
receipt=doc(STAGE/'zlib-stage-receipt.json','df7d79194320d48b143e1b9daff67fd9afe1b64bbcbe5e08ab636bf3fdf67be6')
assert receipt['state']=='REVIEWED_SOURCE_STAGE_CREATED_NO_NATIVE_OR_GUEST'and receipt['proposalIndexSha256']==INDEX
assert receipt['originalPreparationRoot']==str(OWNER)and receipt['destination']==str(STAGE)and receipt['gitBase']==HEAD
assert receipt['preparedReferencesRelocatedOrReinterpreted']is receipt['nativeOrGuestExecuted']is False
policy=doc(STAGED/'policy.json');tools=doc(STAGED/'artifact-tools/tool-pins.json');source_receipt=doc(STAGED/'source-receipt.json')
assert len(policy['expectedNativeSourceManifest'])==receipt['actualSourceFiles']==350 and len(tools['toolDependencies'])==632
expected={};copied=[]
for row in policy['expectedNativeSourceManifest']+tools['toolDependencies']:
 n=row['path'];choices=[OWNER/'source'/n]
 if Path(n).is_relative_to(REL):choices.append(OWNER/Path(n).relative_to(REL))
 choices += [Path('/tmp/starling-node-compat/classic-trace-source-v1')/n,REPO/n]
 candidates=[p for p in choices if p.is_file()and not p.is_symlink()and sha(p.read_bytes())==row['sha256']];assert candidates,n
 source=candidates[0];raw=read(source,row['sha256']);entry={'path':n,'source':str(source),'sha256':row['sha256'],'bytes':len(raw)}
 assert n not in expected or expected[n]==entry,n;expected[n]=entry
 target=below(STAGE,n);assert read(target,row['sha256'],len(raw))==raw
 assert (source.stat().st_dev,source.stat().st_ino)!=(target.stat().st_dev,target.stat().st_ino),(n,'hardlink to original')
 assert target.stat().st_nlink==1,(n,'nonexclusive target inode')
copied=receipt['copiedSourceAndToolRows'];assert len(copied)==979 and copied==[expected[k]for k in sorted(expected)]
native={r['path']for r in policy['expectedNativeSourceManifest']};toolset={r['path']for r in tools['toolDependencies']}
assert len(native&toolset)==3 and len(native|toolset)==979
for row in original_index['files']:
 assert read(STAGED/row['path'])==read(OWNER/row['path'])
assert read(STAGED/'input-freeze.json')==read(OWNER/'input-freeze.json')
manifest=doc(OWNER/'input-freeze.json');assert manifest['originalPreparationRoot']==str(OWNER)and manifest['relocatedActionsMustNotReinterpretThesePaths']is True
assert len(manifest['inputs'])==2261
# Follow original-context preparation references from the original packet only.
for row in manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'])
git=STAGE/'.git';assert git.is_dir()and not git.is_symlink()
assert not(git/'commondir').exists()and not(git/'objects/info/alternates').exists()
git_head=read(git/'HEAD').decode().strip();assert git_head=='ref: refs/heads/main'
assert read(git/'refs/heads/main').decode().strip()==HEAD
config=read(git/'config').decode();assert 'url = /Users/dan/dev/StarlingMonkey'in config and 'bare = false'in config
assert (git.stat().st_dev,git.stat().st_ino)!=( (REPO/'.git').stat().st_dev,(REPO/'.git').stat().st_ino)
plan=doc('/tmp/starling-node-compat/zlib-producer-v4-root-stage-v1/plan.stdout.log')
command=plan['gitCommandNotRun'];assert command==['git','-c','core.hooksPath=/dev/null','clone','--no-hardlinks',str(REPO),str(STAGE.with_name(STAGE.name+'.staging'))]
assert plan['sourceRows']==979 and plan['sourcePacketIndexSha256']==INDEX
source_terminal=doc('/tmp/starling-node-compat/zlib-producer-v4-root-source-v1/terminal.json');assert len(source_terminal['commands'])==8 and all(r['returncode']==0 for r in source_terminal['commands'])
assert doc('/tmp/starling-node-compat/zlib-producer-v4-root-source-v1/link-chain.terminal.json')['returncode']==0
for name in ['plan','apply','verify-source','factory','git-head']:
 terminal=doc(Path('/tmp/starling-node-compat/zlib-producer-v4-root-stage-v1')/(name+'.terminal.json'));assert terminal['returncode']==0
assert read('/tmp/starling-node-compat/zlib-producer-v4-root-stage-v1/git-head.stdout.log').decode().strip()==HEAD
checks={'policy':73,'source-js':49,'command-data-py':15,'command-data-js':74,'after-contract':7,'bootstrap-py':16,'bootstrap-js':8,'link-chain':26}
for name,count in checks.items():
 report=doc(Path('/tmp/starling-node-compat/zlib-producer-v4-root-source-v1')/name/'results.json');assert report.get('count',report.get('passed'))==count,(name,report.keys())
assert root['sourceChecks']==checks
# Independently verify every inherited Git blob outside the sealed overlays.
# ls-tree only reads Git objects and runs no source hook/helper/entrypoint.
env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'}
tree=subprocess.run(['/usr/bin/git','-C',str(STAGE),'ls-tree','-r','-z',HEAD],env=env,capture_output=True,check=True);assert tree.stderr==b''
overlays=set(expected)|{str(REL/row['path'])for row in original_index['files']}|{str(REL/'index.json')}
git_rows=[];unchanged=0;overlay_tracked=0
for entry in tree.stdout.split(b'\0'):
 if not entry:continue
 meta,name=entry.split(b'\t',1);mode,kind,oid=meta.decode().split();n=name.decode();p=STAGE/n
 if n in overlays:overlay_tracked+=1
 elif mode=='160000':assert p.is_dir()
 elif mode=='120000':assert p.is_symlink();raw=os.readlink(p).encode();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid;unchanged+=1
 else:
  assert mode in ['100644','100755']and kind=='blob';raw=read(p);assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid,n;unchanged+=1
 git_rows.append({'path':n,'mode':mode,'kind':kind,'gitObjectId':oid,'sealedOverlay':n in overlays})
actual_files=[]
for directory,dirs,files in os.walk(STAGE,followlinks=False):
 if Path(directory)==STAGE:dirs[:]=[x for x in dirs if x!='.git']
 for n in files:actual_files.append(str((Path(directory)/n).relative_to(STAGE)))
assert set(actual_files)=={r['path']for r in git_rows if r['mode']!='160000'}|overlays|{'zlib-stage-receipt.json'}
assert read(STAGED/'codec-evidence.py')==read(FAMILY/'compound-link-parser-amendment-v1/codec-evidence.after.py')
assert read(STAGED/'compile-input.mjs')==read(FAMILY/'native-integration-candidate-v2/compile-input.mjs')
assert source_receipt['recipeSha256']==sha(read(STAGE/'tests/node-compat/build-engine.sh'))=='4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2'
assert len([n for n in native if n.endswith('.cpp')and n.startswith(('runtime/','builtins/'))])==62 and len(policy['privateTargetCpp'])==6
for name in ['bootstrap-pins.json','runtime-pins.json']:assert all(v is None for v in doc(STAGED/name)['variants'].values())
# Existing v3 source, stage/failure evidence and its raw engine remain exact.
# These reads do not transfer any raw engine or old result into the new stage.
old=FAMILY/'native-integration-candidate-v3';indexed(old,'3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710',81)
old_stage_root=doc(FAMILY/'native-integration-v3-root-stage-results.json','964346f9f468befa48e1b38c97c5852c42f6b80740ce4311db02804c1c18be82')
for row in old_stage_root['evidence']:read(row['path'],row['sha256'],row['bytes'])
failure=doc(FAMILY/'native-integration-v3-build-attempt1-failure-root-results.json','accf4b054401f214fae62feba67bacce0ead71ac3eead31187830c26550c9875')
for row in failure['evidence']:read(row['path'],row['sha256'],row['bytes'])
assert failure['rawOuterExit']==failure['rawRecipeExit']==1 and failure['rawEngineAdmitted']is failure['metadataSidecarProduced']is failure['nativeFreezeProduced']is failure['runtimeBackendProof']is False
old_peer=FAMILY/'independent-native-zlib-v3-build-failure-review-v1';old_peer_index=doc(old_peer/'index.json','c319335168016fcc40ec2b04548e82a3fd171972dcc3a488f30bbb0ffcecb4ce')
indexed(old_peer,'c319335168016fcc40ec2b04548e82a3fd171972dcc3a488f30bbb0ffcecb4ce',len(old_peer_index['files']))
preseed=doc(FAMILY/'native-integration-v4-cache-preseed-root-results.json','47668bda4ca3baa0f1f918a21a30cc6f61dc0224dd618402564c732601351a0c')
cache=Path(preseed['destinationRoot']);assert cache==Path('/tmp/starling-node-compat/zlib-v4-build')and not cache.is_symlink()
assert len(preseed['files'])==4 and preseed['nativeOrComponentSourcesCopied']is preseed['engineOrMetadataOrCodecEvidenceCopied']is preseed['buildPerformed']is preseed['artifactAdmission']is False
cache_members={str(p)for p in cache.rglob('*')if p.is_file()or p.is_symlink()}
assert cache_members=={row['destination']for row in preseed['files']}
for row in preseed['files']:
 read(row['source'],row['sha256'],row['bytes']);read(row['destination'],row['sha256'],row['bytes'])
 assert (Path(row['source']).stat().st_dev,Path(row['source']).stat().st_ino)!=(Path(row['destination']).stat().st_dev,Path(row['destination']).stat().st_ino)
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_ZLIB350_V4_ISOLATED_STAGE_REVIEW_PASSED_NO_NATIVE',
 'rootReceiptSha256':ROOT_SHA,'sourceIndexSha256':INDEX,'stageReceiptSha256':'df7d79194320d48b143e1b9daff67fd9afe1b64bbcbe5e08ab636bf3fdf67be6',
 'stageRoot':str(STAGE),'rootEvidenceReferences':46,'nativeSources':350,'toolRows':632,'nativeToolOverlap':3,'exactCopiedUniquePlanRows':979,
 'indexedProposalFiles':85,'stagedProposalIndexByteExact':True,'originalPreparationInputsRehashed':2261,'preparationReferencesRelocatedOrReinterpreted':False,
 'allSourceOriginalsAndStageCopiesRehashed':True,'stageCopiesIndependentInodesFromOriginals':True,'gitBase':HEAD,'gitOrdinaryCloneNotWorktree':True,
 'gitReadOnlyTreeRows':len(git_rows),'inheritedGitEntriesUnchanged':unchanged,'trackedEntriesOverlaidBySealedPlan':overlay_tracked,'physicalMembershipExact':True,
 'cppCounts':{'on':62,'off':61},'privateTargetCpp':{'on':6,'off':5},'nativeApi40Unchanged':True,'compoundParserDescriptorFixAndIncludeGrammarByteExact':True,
 'rootRecordedSourceChecksAuthenticatedNotRerun':checks,'rootRecordedFactoryChecksAuthenticatedNotRerun':2,
 'rootReportedRawTerminals':{'sourceSession':34385,'sourceExit':0,'planApplySession':89971,'planExit':0,'applyExit':0,'linkChainChunk':'42f14b','linkChainExit':0,'verifyExit':0,'observedByThisReader':False},
 'reviewerActions':['owned Python file/hash/source/data reader','read-only /usr/bin/git ls-tree with GIT_OPTIONAL_LOCKS=0'],
 'ownerHelperOrStageMainOrFactoryOrTestsOrNativeVerifierOrBootstrapOrBuildOrCompilerOrGuestOrHostExecuted':False,
 'oldV3SourceStageFailureEvidenceAndRawEngineRehashedUnchanged':True,'oldV3FailureRawEngineAdmitted':False,
 'v4BuildRootPhysicalFilesCacheOnly':4,'v4CachePreseedTransferredNativeEngineOrMetadataOrProof':False,
 'nativeBuildOrRuntimeProof':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteSourceStageBlockers':[],
 'limitations':['This authenticates actual isolated source staging and saved Root checks only; no native build/freezer/bootstrap/guest or empirical new link/backend/GC/cross-decode proof.',
 'Original-context2261-row preparation seal is read from the original packet; relocated actions must use actual staged350/tool inventories.',
 'Historical3ff/dafaff/c65/1d0c/89bc and all runtime pins remain unchanged. Future actual engine/backend pins are null.'],
 'verifiedPathStrings':len(seen),'verifiedFiles':sorted(seen.values(),key=lambda r:r['path'])}
for name,value in [('results.json',result),('git-tree.json',{'schemaVersion':1,'gitBase':HEAD,'entries':git_rows})]:
 with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'state':result['state'],'copiedRows':979,'sourceFiles':350,'toolRows':632,'gitBaseRows':len(git_rows),'unchangedInheritedGitEntries':unchanged,'paths':len(seen)}))
