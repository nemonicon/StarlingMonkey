"""Independent isolated-stage reader. No source/helper/build/test execution.

The sole subprocess is read-only Git ls-tree with optional locks disabled.
"""
from pathlib import Path
import hashlib,json,os,stat,subprocess
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=HERE.parents[3]
STAGE=Path('/tmp/starling-node-compat/zlib-source-v3')
REL=Path('tests/node-compat/foundation-zlib/native-integration-candidate-v3')
OWNER=REPO/REL;STAGED=STAGE/REL
INDEX='3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710'
ROOT_SHA='964346f9f468befa48e1b38c97c5852c42f6b80740ce4311db02804c1c18be82'
HEAD='54b3329b3ce818fd1f244e871e9c259b63667cda'
seen={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path,h=None,size=None):
 p=Path(path);a=p.lstat();assert stat.S_ISREG(a.st_mode)and not p.is_symlink(),p;b=p.read_bytes();z=p.lstat()
 assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns),p
 digest=sha(b);assert h is None or digest==h,p;assert size is None or len(b)==size,p
 key=str(p.absolute());row={'path':key,'sha256':digest,'bytes':len(b)};assert key not in seen or seen[key]==row,p;seen[key]=row;return b
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
root=doc(FAMILY/'native-integration-v3-root-stage-results.json',ROOT_SHA)
assert root['sourceIndexSha256']==INDEX and root['sourceRoot']==str(STAGE)
assert len(root['evidence'])==41
for row in root['evidence']:read(row['path'],row['sha256'],row['bytes'])
assert root['sourceCheckRootSession']==76544 and root['sourceCheckRawExit']==0 and root['sourceCheckCommands']==8
assert root['planApplyRootSession']==54392 and root['planRawExit']==root['applyRawExit']==root['actualStageVerifyRawExit']==root['actualFactoryCheckRawExit']==root['actualGitHeadRawExit']==0
assert root['nativeBuildStarted']is root['guestExecuted']is root['runtimeAcceptanceClaim']is root['performanceClaim']is False
assert STAGE.is_dir()and not STAGE.is_symlink()and not STAGE.with_name(STAGE.name+'.staging').exists()
assert STAGE.stat().st_ino!=REPO.stat().st_ino
original_index=indexed(OWNER,INDEX,81);staged_index=indexed(STAGED,INDEX,81);assert original_index==staged_index
peer=FAMILY/'independent-native-integration-v3-source-review-v1';indexed(peer,'f471ec276ce05ef3d80c90af8a30da25933663452dec2b9728ebc111a3a0013e',7)
receipt=doc(STAGE/'zlib-stage-receipt.json','28c1e4454d57affa90d432c284d8382825ca781c57d424bfc7d296a8cea4f893')
assert receipt['state']=='REVIEWED_SOURCE_STAGE_CREATED_NO_NATIVE_OR_GUEST'and receipt['proposalIndexSha256']==INDEX
assert receipt['originalPreparationRoot']==str(OWNER)and receipt['destination']==str(STAGE)and receipt['gitBase']==HEAD
assert receipt['preparedReferencesRelocatedOrReinterpreted']is receipt['nativeOrGuestExecuted']is False
policy=doc(STAGED/'policy.json');tools=doc(STAGED/'artifact-tools/tool-pins.json');source_receipt=doc(STAGED/'source-receipt.json')
assert len(policy['expectedNativeSourceManifest'])==receipt['actualSourceFiles']==350 and len(tools['toolDependencies'])==522
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
copied=receipt['copiedSourceAndToolRows'];assert len(copied)==869 and copied==[expected[k]for k in sorted(expected)]
native={r['path']for r in policy['expectedNativeSourceManifest']};toolset={r['path']for r in tools['toolDependencies']}
assert len(native&toolset)==3 and len(native|toolset)==869
for row in original_index['files']:
 assert read(STAGED/row['path'])==read(OWNER/row['path'])
assert read(STAGED/'input-freeze.json')==read(OWNER/'input-freeze.json')
manifest=doc(OWNER/'input-freeze.json');assert manifest['originalPreparationRoot']==str(OWNER)and manifest['relocatedActionsMustNotReinterpretThesePaths']is True
assert len(manifest['inputs'])==2146
# Follow original-context preparation references from the original packet only.
for row in manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'])
git=STAGE/'.git';assert git.is_dir()and not git.is_symlink()
assert not(git/'commondir').exists()and not(git/'objects/info/alternates').exists()
git_head=read(git/'HEAD').decode().strip();assert git_head=='ref: refs/heads/main'
assert read(git/'refs/heads/main').decode().strip()==HEAD
config=read(git/'config').decode();assert 'url = /Users/dan/dev/StarlingMonkey'in config and 'bare = false'in config
assert (git.stat().st_dev,git.stat().st_ino)!=( (REPO/'.git').stat().st_dev,(REPO/'.git').stat().st_ino)
plan=doc('/tmp/starling-node-compat/zlib-producer-v3-root-stage-v1/plan.stdout.log')
command=plan['gitCommandNotRun'];assert command==['git','-c','core.hooksPath=/dev/null','clone','--no-hardlinks',str(REPO),str(STAGE.with_name(STAGE.name+'.staging'))]
assert plan['sourceRows']==869 and plan['sourcePacketIndexSha256']==INDEX
source_terminal=doc('/tmp/starling-node-compat/zlib-producer-v3-root-source-v1/terminal.json');assert len(source_terminal['commands'])==8 and all(r['returncode']==0 for r in source_terminal['commands'])
for name in ['plan','apply','verify-source','factory','git-head']:
 terminal=doc(Path('/tmp/starling-node-compat/zlib-producer-v3-root-stage-v1')/(name+'.terminal.json'));assert terminal['returncode']==0
assert read('/tmp/starling-node-compat/zlib-producer-v3-root-stage-v1/git-head.stdout.log').decode().strip()==HEAD
checks={'policy':73,'source-js':49,'command-data-py':15,'command-data-js':74,'after-contract':7,'bootstrap-py':16,'bootstrap-js':8}
for name,count in checks.items():
 report=doc(Path('/tmp/starling-node-compat/zlib-producer-v3-root-source-v1')/name/'results.json');assert report.get('count',report.get('passed'))==count,(name,report.keys())
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
assert read(STAGED/'codec-evidence.py')==read(FAMILY/'descriptor-shadow-amendment-v1/codec-evidence.after.py')
assert read(STAGED/'compile-input.mjs')==read(FAMILY/'native-integration-candidate-v2/compile-input.mjs')
assert source_receipt['recipeSha256']==sha(read(STAGE/'tests/node-compat/build-engine.sh'))=='b8b26474682c4236a6f1b02337f7b100a3a79adab5c95c2c7a96a0d0176b546e'
assert len([n for n in native if n.endswith('.cpp')and n.startswith(('runtime/','builtins/'))])==62 and len(policy['privateTargetCpp'])==6
for name in ['bootstrap-pins.json','runtime-pins.json']:assert all(v is None for v in doc(STAGED/name)['variants'].values())
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_ZLIB350_V3_ISOLATED_STAGE_REVIEW_PASSED_NO_NATIVE',
 'rootReceiptSha256':ROOT_SHA,'sourceIndexSha256':INDEX,'stageReceiptSha256':'28c1e4454d57affa90d432c284d8382825ca781c57d424bfc7d296a8cea4f893',
 'stageRoot':str(STAGE),'rootEvidenceReferences':41,'nativeSources':350,'toolRows':522,'nativeToolOverlap':3,'exactCopiedUniquePlanRows':869,
 'indexedProposalFiles':81,'stagedProposalIndexByteExact':True,'originalPreparationInputsRehashed':2146,'preparationReferencesRelocatedOrReinterpreted':False,
 'allSourceOriginalsAndStageCopiesRehashed':True,'stageCopiesIndependentInodesFromOriginals':True,'gitBase':HEAD,'gitOrdinaryCloneNotWorktree':True,
 'gitReadOnlyTreeRows':len(git_rows),'inheritedGitEntriesUnchanged':unchanged,'trackedEntriesOverlaidBySealedPlan':overlay_tracked,'physicalMembershipExact':True,
 'cppCounts':{'on':62,'off':61},'privateTargetCpp':{'on':6,'off':5},'nativeApi40Unchanged':True,'c92DescriptorFixAndIncludeGrammarByteExact':True,
 'rootRecordedSourceChecksAuthenticatedNotRerun':checks,'rootRecordedFactoryChecksAuthenticatedNotRerun':2,
 'rootReportedRawTerminals':{'sourceSession':76544,'sourceExit':0,'planApplySession':54392,'planExit':0,'applyExit':0,'stageVerifyChunk':'f9ed2e','verifyExit':0,'observedByThisReader':False},
 'reviewerActions':['owned Python file/hash/source/data reader','read-only /usr/bin/git ls-tree with GIT_OPTIONAL_LOCKS=0'],
 'ownerHelperOrStageMainOrFactoryOrTestsOrNativeVerifierOrBootstrapOrBuildOrCompilerOrGuestOrHostExecuted':False,
 'nativeBuildOrRuntimeProof':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteSourceStageBlockers':[],
 'limitations':['This authenticates actual isolated source staging and saved Root checks only; no native build/freezer/bootstrap/guest or empirical new link/backend/GC/cross-decode proof.',
 'Original-context2146-row preparation seal is read from the original packet; relocated actions must use actual staged350/tool inventories.',
 'Historical3ff/dafaff/c65/1d0c/89bc and all runtime pins remain unchanged. Future actual engine/backend pins are null.'],
 'verifiedPathStrings':len(seen),'verifiedFiles':sorted(seen.values(),key=lambda r:r['path'])}
for name,value in [('results.json',result),('git-tree.json',{'schemaVersion':1,'gitBase':HEAD,'entries':git_rows})]:
 with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'state':result['state'],'copiedRows':869,'sourceFiles':350,'toolRows':522,'gitBaseRows':len(git_rows),'unchangedInheritedGitEntries':unchanged,'paths':len(seen)}))
