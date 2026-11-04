"""Independent finite actual-stage reader. No owner helper/action execution."""
from pathlib import Path
import ast
import collections
import hashlib
import json
import os
import stat
import subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
OWN=HERE.parent/'native-integration-candidate-v2'
REL=str(OWN.relative_to(REPO))
STAGE=Path('/tmp/starling-node-compat/consumers-source-v2')
BASE=Path('/tmp/starling-node-compat/zlib-source-v4')
PARENT=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
CONSUMER=HERE.parent/'production-text-json-candidate-v2'
COMMIT='54b3329b3ce818fd1f244e871e9c259b63667cda'
INDEX_SHA='9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
FIVE=['builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs']
REFS={};CACHE={}
def describe(path,expected=None,size=None):
 path=Path(path).absolute();before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 key=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
 if key not in CACHE:
  h=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
  CACHE[key]=h.hexdigest()
 after=path.lstat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value={'path':str(path),'sha256':CACHE[key],'bytes':before.st_size}
 if expected is not None:assert value['sha256']==expected,(str(path),value['sha256'],expected)
 if size is not None:assert value['bytes']==size,str(path)
 assert REFS.setdefault(str(path),value)==value
 return value
def raw(path,expected=None):describe(path,expected);return Path(path).read_bytes()
def load(path,expected=None):return json.loads(raw(path,expected))
def put(name,value):
 with(HERE/name).open('x') as out:json.dump(value,out,indent=2);out.write('\n')
def indexed(root,expected):
 d=load(root/'index.json',expected)
 for row in d['files']:
  name=Path(row['path']);assert not name.is_absolute() and '..' not in name.parts
  describe(root/name,row['sha256'],row['bytes'])
 return d
def git(*args):
 command=['git','-C',str(STAGE),*args]
 result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1','GIT_NO_REPLACE_OBJECTS':'1'})
 assert result.returncode==0,(command,result.stderr.decode())
 return result.stdout
def data_expr(node,names):
 if isinstance(node,ast.Constant):return node.value
 if isinstance(node,ast.Name):return names[node.id]
 if isinstance(node,(ast.List,ast.Tuple)):return [data_expr(n,names) for n in node.elts]
 if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div):return data_expr(node.left,names)/data_expr(node.right,names)
 raise AssertionError(ast.dump(node))
def main():
 own=indexed(OWN,INDEX_SHA);staged=indexed(STAGE/REL,INDEX_SHA);assert own==staged and len(own['files'])==59
 peer=indexed(HERE.parent/'independent-native-integration-v2-source-review-v1','283008266ff55471723d1aff05bc66c5d48663346f1d4bc90752c4278f827811');assert len(peer['files'])==8
 authority=load(HERE.parent/'native-integration-v2-root-source-review.json','d166859727e559a8ead79e0bfe0d2b1820e469fce932c3c59783eeb447d59435')
 root=load(HERE.parent/'native-integration-v2-root-stage-results.json','58737a8a9363b41741f8d76db4c595eb3f41e00e0a84d64311b73b6efc4d5c12')
 for row in root['references']:describe(row['path'],row['sha256'],row['bytes'])
 publication=load('/tmp/starling-node-compat/consumers-source-v2-publication.json','c0e93a9c01a53770ba9fa906bdbd3d027f527a0384e4ecc11fd36cd6e5372491')
 terminal=load('/tmp/starling-node-compat/consumers355-v2-source-publication-v1.terminal.json','f33d8bbe27798f6758a617a080a53772be9a732fd3103b1d005ca8c3ef6b85e1')
 assert authority['stagingAllowed'] and not authority['nativeBuildAllowedByThisReceipt']
 assert root['rawExitCode']==terminal['rawExitCode']==0 and terminal['sourceIndexSha256']==INDEX_SHA and terminal['rootReviewSha256']==describe(HERE.parent/'native-integration-v2-root-source-review.json')['sha256']
 assert publication['genuineHead']==COMMIT and publication['files']==1173 and publication['nativeRows']==355 and publication['toolRows']==767
 assert publication['sourceCommands'][0]['argv']==['git','clone','--no-local','--no-checkout',str(REPO),str(STAGE)]
 assert publication['sourceCommands'][1]['argv']==['git','-C',str(STAGE),'checkout','--detach',COMMIT]
 assert all(row['status']==0 for row in publication['sourceCommands'])
 assert json.loads(raw('/tmp/starling-node-compat/consumers355-v2-source-publication-v1.stdout.log'))==publication
 assert raw('/tmp/starling-node-compat/consumers355-v2-source-publication-v1.stderr.log')==b''
 manifest=load(OWN/'input-freeze.json');assert len(manifest['inputs'])==3420 and manifest['originalPreparationRoot']==str(OWN)
 assert manifest['originalPrepRowsMustNeverBeReinterpretedInStagedActionHelpers'] is True
 roles=collections.Counter()
 for row in manifest['inputs']:
  assert Path(row['path']).is_absolute();describe(row['path'],row['sha256'],row['bytes']);assert str(Path(row['path']).resolve())==row['realpath']
  roles.update(row['roles'])
 # Reconstruct collect() from data, never import the publisher or its helpers.
 source_ast=ast.parse(raw(OWN/'stage.py'))
 family_node=next(n.value for n in source_ast.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FAMILIES' for t in n.targets))
 families=data_expr(family_node,{'ORIGINAL':REPO,'PARENT':PARENT,'CONSUMERS':CONSUMER})
 family_results=[];prep_hits=[]
 for family,expected,role,filename,key in families:
  doc=indexed(family,expected);count=0
  if role=='PREPARATION':
   content=load(family/filename)
   for row in content[key]:
    path=Path(row['path']);path=path if path.is_absolute() else family/path
    describe(path,row['sha256'],row['bytes']);count+=1
    if str(path.resolve()) in {str((REPO/p).resolve()) for p in FIVE}:prep_hits.append(str(path))
  else:assert role=='INDEXED_ONLY' and filename is None and key is None
  family_results.append({'root':str(family),'indexSha256':expected,'role':role,'indexedFiles':len(doc['files']),'preparationRows':count})
 assert [r['preparationRows'] for r in family_results]==[2261,506,0,0,0,0] and not prep_hits
 rows={}
 def add(relative,origin,digest,size,role):
  assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
  describe(origin,digest,size)
  if relative in rows:assert rows[relative]['sha256']==digest and rows[relative]['bytes']==size;rows[relative]['roles'].append(role)
  else:rows[relative]={'path':relative,'original':str(origin),'sha256':digest,'bytes':size,'roles':[role]}
 policy=load(OWN/'policy.json');native=policy['expectedNativeSourceManifest'];assert len(native)==355
 edits=load(CONSUMER/'native-derivations.json');proposed=set(edits['addedSources']+[r['path'] for r in edits['changes']])
 assert len(proposed)==7
 for row in native:
  origin=CONSUMER/'proposed'/row['path'] if row['path'] in proposed else BASE/row['path']
  size=describe(origin,row['sha256'])['bytes'];add(row['path'],origin,row['sha256'],size,'ACTUAL_NATIVE355')
 pins=load(OWN/'artifact-tools/tool-pins.json','7ee0303e21e32da5b85bb7a6f2476a20f74a91c3cfef988274acc26f8fc5d9fe')
 origins=load(OWN/'tool-origins.json')['files'];assert len(origins)==len(pins['toolDependencies'])==767
 assert {r['path']:(r['sha256'],r['bytes']) for r in origins}=={r['path']:(r['sha256'],r['bytes']) for r in pins['toolDependencies']}
 for row in origins:add(row['path'],Path(row['original']),row['sha256'],row['bytes'],'FINITE_BUILD_TOOL_DEPENDENCY')
 own_desc=describe(OWN/'index.json',INDEX_SHA);add(REL+'/index.json',OWN/'index.json',INDEX_SHA,own_desc['bytes'],'SELF_SEALED_SOURCE')
 for row in own['files']:add(REL+'/'+row['path'],OWN/row['path'],row['sha256'],row['bytes'],'SELF_SEALED_SOURCE')
 assert len(rows)==1173
 aliases=[]
 for row in rows.values():
  path=STAGE/row['path'];cursor=STAGE
  for piece in Path(row['path']).parts:cursor/=piece;assert not cursor.is_symlink()
  describe(path,row['sha256'],row['bytes']);target_stat=path.stat();origin_stat=Path(row['original']).stat()
  assert target_stat.st_nlink==1 and (target_stat.st_dev,target_stat.st_ino)!=(origin_stat.st_dev,origin_stat.st_ino),str(path)
 for name in FIVE:
  row=rows[name];assert Path(row['original']).resolve()!=(REPO/name).resolve()
  aliases.append({'path':name,'origin':row['original'],'sha256':row['sha256'],'liveRootFiveOriginalReadByStagedBuild':False})
 assert git('rev-parse','HEAD').decode().strip()==COMMIT
 assert raw(STAGE/'.git/HEAD').decode().strip()==COMMIT
 assert (STAGE/'.git').is_dir() and not (STAGE/'.git').is_symlink()
 assert not(STAGE/'.git/commondir').exists() and not(STAGE/'.git/objects/info/alternates').exists() and not(STAGE/'.git/refs/replace').exists()
 git_files=[]
 for parent,dirs,names in os.walk(STAGE/'.git',followlinks=False):
  for name in dirs+names:assert not(Path(parent)/name).is_symlink()
  for name in names:
   path=Path(parent)/name;assert path.stat().st_nlink==1;git_files.append(str(path.relative_to(STAGE)))
 baseline={}
 for entry in git('ls-tree','-r','-z','HEAD').split(b'\0'):
  if not entry:continue
  header,name=entry.split(b'\t',1);mode,kind,oid=header.decode().split();baseline[name.decode()]={'mode':mode,'kind':kind,'oid':oid}
 actual={};links=[]
 for parent,dirs,names in os.walk(STAGE,followlinks=False):
  dirs[:]=[n for n in dirs if not(Path(parent)==STAGE and n=='.git')]
  for name in list(dirs):
   path=Path(parent)/name
   if path.is_symlink():links.append(str(path.relative_to(STAGE)));dirs.remove(name)
  for name in names:
   path=Path(parent)/name;relative=str(path.relative_to(STAGE));actual[relative]=path
   if path.is_symlink():links.append(relative)
 expected_paths=set(rows)|{name for name,item in baseline.items() if item['kind']=='blob'}
 assert set(actual)==expected_paths,{'extra':sorted(set(actual)-expected_paths),'missing':sorted(expected_paths-set(actual))}
 baseline_unmodified=0
 for name,path in actual.items():
  assert path.lstat().st_nlink==1
  if name not in rows:
   item=baseline[name];data=os.readlink(path).encode() if path.is_symlink() else raw(path)
   assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['oid'],name
   baseline_unmodified+=1
 link_ledger=[]
 for name in links:
  path=STAGE/name
  assert name not in rows and baseline[name]['mode']=='120000' and path.resolve().is_relative_to(STAGE.resolve())
  link_ledger.append({'path':name,'linkText':os.readlink(path),'canonicalTarget':str(path.resolve()),'genuineGitBlob':baseline[name]['oid'],'consumedOverlayInput':False})
 assert sorted(links)==['docs/src/ADOPTERS.md','docs/src/CODE_OF_CONDUCT.md','docs/src/README.md']
 staged_common=raw(STAGE/REL/'artifact-tools/artifact_common.py').decode();function=next(n for n in ast.parse(staged_common).body if isinstance(n,ast.FunctionDef) and n.name=='verify_frozen_variant')
 assert isinstance(function.body[0],ast.Assert) and ast.unparse(function.body[1])=='tool_dependencies(REPO)'
 all_import_positions=[node.lineno for node in ast.walk(function) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ['spec_from_file_location','exec_module']]
 assert all(line>function.body[1].lineno for line in all_import_positions)
 assert "TOOL_PINS_SHA = '7ee0303e21e32da5b85bb7a6f2476a20f74a91c3cfef988274acc26f8fc5d9fe'" in staged_common
 assert "path = checked_below(repo, row['path'], row['sha256'])" in staged_common
 assert 'input-freeze' not in staged_common
 recipe=raw(STAGE/'tests/node-compat/build-engine.sh','3a5fa8cd58d3948c373b59ff486eae5792ae7ec1b51ed47f43f4edc5b39b4c68').decode()
 assert 'repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"' in recipe
 assert '-DNODE_COMPAT_STREAM_CONSUMERS="$consumers_flag" -DENABLE_BUILTIN_WEB_TEXT_CODEC=ON' in recipe
 cmake=raw(STAGE/'cmake/builtins.cmake').decode();register=raw(STAGE/'builtins/node-compat/register.cpp').decode()
 assert 'target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_STREAM_CONSUMERS=1)' in cmake
 assert 'add_dependencies(builtin_node_compat builtin_web_text_codec)' in cmake and 'target_link_libraries(builtin_node_compat PRIVATE builtin_web_text_codec)' in cmake
 assert 'file(APPEND $CACHE{INSTALL_BUILTINS} "NS_DEF(${NS})\\n")' in raw(STAGE/'cmake/add_builtin.cmake').decode()
 assert 'JSAutoRealm realm(cx, engine->global());' in register and 'JS::RootedObject argument(cx, JS_NewPlainObject(cx));' in register
 assert 'engine->define_builtin_module("node:stream/consumers", module)' in register and 'engine->define_builtin_module("stream/consumers", module)' in register
 cpp=[r['path'] for r in native if r['path'].endswith('.cpp') and r['path'].startswith(('builtins/','runtime/'))];assert len(cpp)==62
 for name in ['runtime-pins.json','bootstrap-pins.json']:
  null=load(STAGE/REL/name);assert all(v is None for v in null['variants'].values()) and null['operationalAdmission'] is False and null['runtimeAcceptanceClaim'] is False
 assert load(STAGE/REL/'admission-pins.json')['reviewedFutureEnginePins'] is None
 contract=load(STAGE/REL/'bootstrap-contract.json');assert contract['componentHarnessRoot'] is None and contract['componentHarnessClosureComplete'] is False and contract['operationalAdmission'] is False
 assert contract['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
 cache_receipt=load(HERE.parent/'native-integration-v2-cache-preseed-attempt2-root-results.json','cc1763cfade58953434e164859a95fd481b926e2a03487ff13ffa7454960cacd')
 assert len(cache_receipt['files'])==4 and cache_receipt['buildPerformed'] is False and cache_receipt['engineOrMetadataOrCodecEvidenceCopied'] is False
 cache_root=Path(cache_receipt['destinationRoot']);actual_cache={str(p) for p in cache_root.rglob('*') if p.is_file()}
 assert actual_cache=={r['destination'] for r in cache_receipt['files']}
 for row in cache_receipt['files']:
  describe(row['destination'],row['sha256'],row['bytes']);a=Path(row['source']).stat();b=Path(row['destination']).stat();assert(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
 absent={str(Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze')):not Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze').exists()};assert all(absent.values())
 result={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_CONSUMERS355_V2_STAGE_PASSED_SOURCE_ONLY','producerIndexSha256':INDEX_SHA,'sourcePeerIndexSha256':'283008266ff55471723d1aff05bc66c5d48663346f1d4bc90752c4278f827811','rootSourceReviewSha256':describe(HERE.parent/'native-integration-v2-root-source-review.json')['sha256'],'rootStageReviewSha256':describe(HERE.parent/'native-integration-v2-root-stage-results.json')['sha256'],'rootRecordedExit':0,'rootTerminalObservedByThisReader':False,'stage':str(STAGE),'canonicalStage':str(STAGE.resolve()),'genuineGitHead':COMMIT,'independentNoLocalCloneRecord':True,'gitMetadataOrdinaryDirectory':True,'alternatesOrCommonDir':False,'gitRegularFilesLinkCountOne':len(git_files),'declaredOverlaidFiles':1173,'actualWorkingTreeFiles':len(actual),'baselineFilesOutsideOverlayVerifiedByGitBlob':baseline_unmodified,'unexpectedWorkingTreeFiles':0,'genuineBaselineDocSymlinks':link_ledger,'nativeSources':355,'nativeCpp':62,'toolDependencies':767,'selfSourceFiles':59,'selfIndexAdditional':1,'originalPreparationRows':3420,'originalPreparationRoleCounts':dict(roles),'families':family_results,'oldRootFivePreparationHits':0,'fivePathRouting':aliases,'universalHelperBarrierBeforeCustomImports':True,'componentHarnessClosureProvided':False,'nullRuntimeAndBootstrapPins':True,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'freezePathAbsentAtReview':absent,'externalWorkRootCacheOnly':{'rootReceiptSha256':'cc1763cfade58953434e164859a95fd481b926e2a03487ff13ffa7454960cacd','files':cache_receipt['files'],'fourDestinationHashesChecked':True,'nativeBuildPerformed':False},'sourceMechanismOnly':['Existing CMake Node target/private consumer define/TextCodec prerequisite and link dependency present.','Registration remains CONTENT realm, rooted JSAPI arguments and existing factory evaluation; no new C++ translation unit.','Generated install order, actual compile flags, link/codec/engine artifacts and runtime behavior remain future build/validation evidence.'],'noOwnerHelpersVerifiersBootstrapNativeGuestOrTimingExecuted':True,'buildAuthorizedByThisReview':False,'runtimeAcceptanceClaim':False}
 put('results.json',result);put('stage-row-ledger.json',{'files':[rows[name] for name in sorted(rows)],'copyBytesExact':True});put('git-membership.json',{'head':COMMIT,'physicalFiles':sorted(actual),'baseline':baseline,'gitRegularFiles':git_files,'noAlternates':True,'noHardlinksObserved':True,'genuineBaselineDocLinks':link_ledger});put('external-references.json',{'files':sorted(REFS.values(),key=lambda r:r['path']),'oldRuntimeOutputTreesEnumerated':False})
 print(json.dumps({'state':result['state'],'stageRows':1173,'workingTreeFiles':len(actual),'native':355,'tools':767,'prepRows':3420,'externalPaths':len(REFS),'buildOrGuestActions':False}))
if __name__=='__main__':main()
