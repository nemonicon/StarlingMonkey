"""Actual extracted guard/wrapper AST with in-memory I/O/import seams only.
No owner module is imported, no action main/helper/native/engine is executed.
"""
from pathlib import Path,PurePosixPath
from types import SimpleNamespace
import ast,copy,hashlib,json
HERE=Path(__file__).resolve().parent

def actual_function(filename,name):
 tree=ast.parse((HERE/filename).read_text());f=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
 return ast.Module(body=[f],type_ignores=[])
def define(module,namespace):exec(compile(ast.fix_missing_locations(module),'<source-ast-pure-seam>','exec'),namespace);return namespace
# Extract only pure constants/functions; no owner imports or top-level actions.
cns={'PurePosixPath':PurePosixPath}
ctree=ast.parse((HERE/'context.py').read_text())
define(ast.Module(body=[n for n in ctree.body if isinstance(n,(ast.Assign,ast.FunctionDef))],type_ignores=[]),cns)
C=SimpleNamespace(**{k:v for k,v in cns.items()if not k.startswith('__')})
SHA='1'*64

def desc(path,tag='2',size=19):return dict(path=path,sha256=tag*64,bytes=size)
def clone(v):return copy.deepcopy(v)
# Path seam models only read-only source membership and absent future freeze root.
class VPath:
 def __init__(self,path):self.path=str(path)
 def __str__(self):return self.path
 def __truediv__(self,name):return VPath(self.path+'/'+str(name))
 @property
 def parent(self):return VPath(str(PurePosixPath(self.path).parent))
 def resolve(self):return self
 def exists(self):return False
 def is_symlink(self):return False
 def is_file(self):return True
 def relative_to(self,other):return VPath(str(PurePosixPath(self.path).relative_to(PurePosixPath(str(other)))))
 def as_posix(self):return self.path
 def rglob(self,pattern):return[VPath(C.OWN+'/'+n)for n in ['index.json','stage-inputs.json','normal-protection.json','references.json']]
 def __eq__(self,other):return str(self)==str(other)

# Genuine source-row payloads, read as DATA before any function compilation/use.
stage_inputs=json.loads((HERE/'stage-inputs.json').read_bytes());refs=json.loads((HERE/'references.json').read_bytes());normal=json.loads((HERE/'normal-protection.json').read_bytes())
assert len(stage_inputs['files'])==1311
ownrow=desc(C.OWN+'/index.json','1');configrow=desc('/synthetic-data-only/config.json','3');rootrow=desc('/synthetic-data-only/root-freeze.json','4')
peer_index=desc('/synthetic-data-only/peer/index.json','5');peer_result=desc('/synthetic-data-only/peer/results.json','6')
stage_result=desc('/synthetic-data-only/stage.json','7');stage_peer_ix=desc('/synthetic-data-only/stage-peer/index.json','8');stage_peer_result=desc('/synthetic-data-only/stage-peer/results.json','9')
build_result=desc(C.BUILD_OUTPUT+'/result.json','a');build_terminal=desc('/synthetic-data-only/build-terminal.json','b');build_authority=desc('/synthetic-data-only/root-build.json','c')
engine=desc(C.WORK+'/artifacts/synthetic-engine.wasm','d',8);metadata_row=desc(engine['path']+'.build.json','e',100)
own_rows=[desc(C.OWN+'/'+n,str(i+2))for i,n in enumerate(['stage-inputs.json','normal-protection.json','references.json'])]
own=dict(schemaVersion=1,sourceOnly=True,files=[dict(r,path=Path(r['path']).name)for r in own_rows])
root=dict(schemaVersion=1,state=C.AUTHORITY_STATE,phase='freeze',sourceIndexSha256=SHA,variant='gc-off',configuredSourceRoot=C.SOURCE,artifactToolsRoot=C.TOOLS,workRoot=C.WORK,freezeRoot=C.FREEZE,nativeSourceFiles=355,externalEmbeddingSources=3,independentSourceReview=dict(index=peer_index,result=peer_result),actualStageResult=stage_result,independentStageReview=dict(index=stage_peer_ix,result=stage_peer_result),actualBuildResult=build_result,actualBuildExternalTerminal=build_terminal,engine=engine,metadata=metadata_row)
for p in C.PHASES:root[p+'Allowed']=p=='freeze'
for p in ['guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:root[p]=False
metadata=dict(gcStress=True,entropyPolicy='off',oomTesting=False,buildRecipeSha256=C.RECIPE_SHA,sourceManifest=[dict(path='synthetic/native/'+str(i))for i in range(355)],componentizeSourceManifest=[{}]*3,cryptoKeyOwnershipPolicy=dict(sourceFiles=355,runtimeValidation=None),cmakeCachePath=C.WORK+'/synthetic/CMakeCache.txt',compileCommandsPath=C.WORK+'/synthetic/compile_commands.json',engineSha256=engine['sha256'],engineBytes=8)
config=dict(sourceIndex=ownrow,rootAuthority=rootrow)
docs={configrow['path']:config,rootrow['path']:root,own_rows[0]['path']:stage_inputs,own_rows[1]['path']:normal,own_rows[2]['path']:refs,peer_result['path']:dict(state=C.PEER_STATE,sourceIndexSha256=SHA,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False),stage_result['path']:dict(state='CRYPTO_OWNER355_GC_SOURCE_STAGE_COMPLETE_UNREVIEWED_V1',sourceIndexSha256=SHA,destination=C.SOURCE),stage_peer_result['path']:dict(state='INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_STAGE_REVIEW_PASSED_V1',verifiedPassed=True,actualStageResult=stage_result,sourceIndexSha256=SHA,configuredSourceRoot=C.SOURCE),build_result['path']:dict(sourceIndexSha256=SHA,state='native-build-completed-runtime-pending',rawChildExitCode=0,lifecycleComplete=True,ownedGroupCleanup=dict(complete=True),allOriginalNormalAndStageBytesPreserved=True,rootAuthority=build_authority),build_terminal['path']:dict(rawExitCode=0,timeout=False,parentOwnedGroupGone=True,authority=build_authority,stdout=desc('/synthetic-data-only/build.stdout','f',0),stderr=desc('/synthetic-data-only/build.stderr','f',0)),metadata_row['path']:metadata}
known={r['path']:r for r in [configrow,rootrow,ownrow,*own_rows,peer_index,peer_result,stage_result,stage_peer_ix,stage_peer_result,build_result,build_terminal,metadata_row]}
counts={};last_frame=None;wrapper_module_imports=0

def regular(r):
 assert set(r)=={'path','sha256','bytes'} and type(r['bytes'])is int and r['bytes']>=0 and len(r['sha256'])==64
 if r['path']in known:assert r==known[r['path']]
 counts['regular']=counts.get('regular',0)+1;return VPath(r['path'])
def read(r):regular(r);return clone(docs[r['path']])
def indexed(r):
 regular(r)
 if r==ownrow:return clone(own),clone(own_rows)
 if r==peer_index:return dict(schemaVersion=1,files=[]),[clone(peer_result)]
 if r==stage_peer_ix:return dict(schemaVersion=1,files=[]),[clone(stage_peer_result)]
 raise AssertionError('unknown synthetic index')
def safe(n):assert not n.startswith('/')and all(x not in ('','.','..')for x in n.split('/'))
def protect(n):assert n==normal;counts['normalProtectionCalls']=counts.get('normalProtectionCalls',0)+1
ns=dict(Path=VPath,C=C,read=read,regular=regular,indexed=indexed,safe=safe,protection=protect)
define(actual_function('guard.py','recheck'),ns);define(actual_function('guard.py','authorize'),ns)
recheck=ns['recheck'];authorize=ns['authorize']
# Every actual body context read must be supplied by this actual guard/wrapper.
bodytree=ast.parse((HERE/'freezer-body.py').read_text())
bodyreads=sorted({n.slice.value for n in ast.walk(bodytree)if isinstance(n,ast.Subscript)and isinstance(n.value,ast.Name)and n.value.id=='context'and isinstance(n.slice,ast.Constant)and isinstance(n.slice.value,str)})
proofnode=next(n.value for n in ast.walk(bodytree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='correction_proof'for t in n.targets))
oldtree=ast.parse((HERE.parent/'ownership-gc-native-candidate-v1/freezer-body.py').read_text())
oldproof=next(n.value for n in ast.walk(oldtree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='correction_proof'for t in n.targets))
common=SimpleNamespace(REPO=VPath(C.SOURCE),HERE=VPath(C.TOOLS))

def project_body(frame,common,guard):
 global last_frame
 recheck(frame);assert set(bodyreads)<=set(frame);last_frame=clone(frame)
 result=eval(compile(ast.Expression(proofnode),'<actual-correction-proof-expression>','eval'),dict(context=frame,source_guard=guard,configured_root=common.REPO,artifact_tools=common.HERE,output_root=VPath(C.FREEZE),correction_copies=[]))
 assert result['rootAuthority']==docs[configrow['path']]['rootAuthority']==frame['captured'][1]
 return result

def load_common(frame):recheck(frame);counts['commonSeamCalls']=counts.get('commonSeamCalls',0)+1;return common
body=SimpleNamespace(freeze=project_body)
class Loader:
 def exec_module(self,module):
  global wrapper_module_imports
  assert module is body;wrapper_module_imports+=1
util=SimpleNamespace(spec_from_file_location=lambda name,path:SimpleNamespace(loader=Loader()),module_from_spec=lambda spec:body)
guard=SimpleNamespace(authorize=authorize,load_common=load_common,recheck=recheck,DONOR_SHA=C.DONOR_SHA)
wns=dict(Path=VPath,C=C,guard=guard,read=read,descriptor=lambda p:desc(str(p),'0',100),importlib=SimpleNamespace(util=util),__file__=C.OWN+'/freeze.py')
define(actual_function('freeze.py','freeze'),wns);freeze=wns['freeze']
passed=[]
proof=freeze(clone(configrow));assert proof['rootAuthority']==rootrow and last_frame['rootAuthority']==rootrow and 'authority'not in last_frame;passed.append('actual authorize plus actual freeze wrapper provides all body keys and exact Root descriptor')
assert set(bodyreads)<=set(last_frame);passed.append('every actual freezer body context read is provided')
assert metadata_row in last_frame['captured'];passed.append('wrapper appends expected metadata before common seam')
assert proof['configuredSourceRoot']==C.SOURCE and proof['freezeRoot']==C.FREEZE;passed.append('proof retains actual fresh configured/freeze contexts')
try:eval(compile(ast.Expression(oldproof),'<held-original-proof-expression>','eval'),dict(context=last_frame,source_guard=guard,configured_root=common.REPO,artifact_tools=common.HERE,output_root=VPath(C.FREEZE),correction_copies=[]))
except KeyError as e:assert e.args==('authority',);passed.append('held actual old proof reproduces missing authority key against full actual frame')
else:raise AssertionError('old bug not reproduced')

def reject_frame(name,mutate):
 frame=authorize(clone(configrow),'freeze');mutate(frame);original=guard.authorize;guard.authorize=lambda config,phase:frame
 before=counts.get('commonSeamCalls',0)
 try:
  try:freeze(clone(configrow))
  except (AssertionError,KeyError):assert counts.get('commonSeamCalls',0)==before;passed.append(name)
  else:raise RuntimeError('negative accepted '+name)
 finally:guard.authorize=original
reject_frame('missing rootAuthority rejects before common/import seam',lambda f:f.pop('rootAuthority'))
reject_frame('legacy authority alias alone rejects before common/import seam',lambda f:f.update(authority=f.pop('rootAuthority')))
for field,value in [('path','/synthetic-data-only/wrong-root.json'),('sha256','9'*64),('bytes',20)]:
 reject_frame('changed authority '+field+' rejects before common/import seam',lambda f,field=field,value=value:f.update(rootAuthority={**f['rootAuthority'],field:value}))
reject_frame('captured Root row mismatch rejects',lambda f:f['captured'].__setitem__(1,desc('/synthetic-data-only/other.json','7')))
frame=authorize(clone(configrow),'freeze');saved=docs[configrow['path']];docs[configrow['path']]={**saved,'rootAuthority':desc('/synthetic-data-only/other.json','7')}
try:
 try:recheck(frame)
 except AssertionError:passed.append('authenticated config Root descriptor mismatch rejects')
 else:raise AssertionError('config mismatch accepted')
finally:docs[configrow['path']]=saved
# Full source derivations (including unchanged copied bytes) are reversible.
deriv=json.loads((HERE/'donor-derivations.json').read_bytes())
for r in deriv['files']:
 old=Path(r['source']['path']).read_text();new=(HERE/r['afterimage']).read_text();f=old
 for e in r['edits']:assert f.count(e['before'])==e['count'];f=f.replace(e['before'],e['after'])
 assert f==new
 for e in reversed(r['edits']):assert new.count(e['after'])==e['count'];new=new.replace(e['after'],e['before'])
 assert new==old
passed.append('all18 operational/template/support afterimages reverse exactly')
# Existing explicit-output APIs and active-wrapper identity remain literal source.
text=(HERE/'freezer-body.py').read_text();assert 'validate_plan(plan, receipt_path, output=output_root)'in text and 'execute_plan(plan, output=output_root)'in text and "'helperSha256': sha(active_entry)"in text
assert "context['authority']"not in text and 'common.OUTPUT ='not in text and 'common.REPO ='not in text and 'common.HERE ='not in text
passed.append('explicit output and active-wrapper helper identity unchanged, no globals rebound')
result=dict(schemaVersion=1,state='PURE_ACTUAL_GUARD_WRAPPER_BODY_CONTEXT_REGRESSION_PASSED_V2',checks=len(passed),passed=passed,actualGuardAuthorizeAstExecuted=True,actualGuardRecheckAstExecuted=True,actualFreezeWrapperAstExecuted=True,actualBodyProofExpressionEvaluated=True,actualBodyContextReadKeys=bodyreads,actualProvidedFrameKeys=sorted(last_frame),exactAuthorityDescriptor=rootrow,descriptorIsSyntheticDataOnly=True,syntheticStageRows=len(stage_inputs['files']),allIOImportsCommonNativeFreezerAndActionSeamsStubbed=True,ownerModulesImported=False,actualHelperOrActionInvoked=False,sandboxDirectoriesCreated=False,commonSeamCalls=counts.get('commonSeamCalls',0),mockedBodyImportCalls=wrapper_module_imports)
(HERE/'context-regression-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(pureChecks=len(passed),oldMissingKeyReproduced=True,allWrongOrMissingRootCasesRejected=True,ownerActionsInvoked=False)))
