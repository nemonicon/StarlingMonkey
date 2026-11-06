"""Source/data preparation only. No Git, stage, authorize or monitor calls."""
import ast,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent;V1=OWN.parent/'node-crypto-hash-hmac-stage-candidate-v1';ROOT=OWN.parents[3];assert not(OWN/'index.json').exists()
PEER=OWN.parent/'independent-node-crypto-hash-hmac-stage-source-review-v1';SOURCE=OWN.parent/'node-crypto-hash-hmac-native-integration-candidate-v1'
def d(p):p=Path(p).absolute();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def j(p):return json.loads(Path(p).read_bytes())
def w(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('actual_v2_inert_source_only',OWN/'controller.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);assert m.OWN==OWN
(OWN/'stage-copy-plan.json').write_bytes((V1/'stage-copy-plan.json').read_bytes())
refs=j(V1/'references.json');refs.update(baselineGitPolicy=m.git_policy(),externalOutputRoot=str(m.OUT),stageJournal=str(m.JOURNAL),predecessorControllerIndex=d(V1/'index.json'),predecessorControllerReview=dict(index=d(PEER/'index.json'),result=d(PEER/'results.json')),predecessorRole='Immutable qualified V1 Source only; never an actual V2 action or Source peer',stageControllerReview=None,rootAuthority=None,actualStage=None,actualStageReview=None)
rows={r['path']:r for r in j(V1/'input-hashes.json')['files']};families={r['path']:r for r in j(V1/'input-hashes.json')['families']}
for folder in [V1,PEER]:
 ix=d(folder/'index.json');families[ix['path']]=ix;rows[ix['path']]=ix
 for row in j(folder/'index.json')['files']:
  value=dict(row,path=str(folder/row['path']));assert d(value['path'])==value;rows[value['path']]=value
config=d(ROOT/'.git/config');rows[config['path']]=config
# Record all actual native-source history-query matches, never run them.
evidence=[];native=j(SOURCE/'native-origins.json')['files']
for row in native:
 path=Path(row['original']);assert d(path)['sha256']==row['sha256']
 if row['path'].startswith(('cmake/','runtime/','crates/'))or row['path']=='CMakeLists.txt':
  for n,line in enumerate(path.read_text(errors='replace').splitlines(),1):
   if re.search(r'\bgit\b|GIT_EXECUTABLE|git_version|GIT_COMMIT',line,re.I):evidence.append(dict(sourcePath=row['path'],original=d(path),line=n,text=line))
recipe=SOURCE/'build-engine.sh';recipe_lines=[]
for n,line in enumerate(recipe.read_text().splitlines(),1):
 if re.search(r"['\"]git['\"]|SPIDERMONKEY_BINARIES|cmake -S",line):recipe_lines.append(dict(line=n,text=line))
external=Path('/private/tmp/starling-node-compat/combined-native355-v2-build/componentize-abi-fixed-bigint-v1-combined355-v2.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1/CMakeLists.txt');rows[str(external)]=d(external)
assert d(external)['sha256']==next(x['sha256']for x in j(SOURCE/'policy.json')['expectedComponentizeSourceManifest']if x['path']=='CMakeLists.txt')
keys=[];section=''
for line in Path(config['path']).read_text().splitlines():
 text=line.strip()
 if text.startswith('['):section=text
 elif text and not text.startswith(('#',';')):keys.append(dict(section=section,key=text.split('=',1)[0].strip()))
w('history-and-git-isolation-evidence.json',dict(schemaVersion=1,scope='Exact7c5a recipe/357-source project graph and unchanged external ComponentizeJS CMake; not universal third-party build code attestation',nativeSourceFilesInspected=357,projectMatches=evidence,recipe=d(recipe),recipeMatches=recipe_lines,externalCMake=d(external),externalCMakeGitQueries=[],rootRepositoryHistoryRequiredByInspectedCode=False,rootProvenanceGitOperations=['diff --binary HEAD','rev-parse HEAD'],separateFirefoxTagCode='manage-git-source.cmake operates on separate Firefox source repo; selected recipe exports pinned SPIDERMONKEY_BINARIES and takes prebuilt SM_LIB_DIR branch',originalRepositoryConfig=config,configurationKeysOnly=keys,configurationValuesRecorded=False,originalRepositoryAlternatesPresent=(ROOT/'.git/objects/info/alternates').exists(),runtimeGitInvoked=False,buildInvoked=False))
refs['declaredCurrentInputRows']=len(rows);w('references.json',refs);w('input-hashes.json',dict(schemaVersion=1,scope='Unchanged2723 V1 Source boundary plus complete immutable V1/qualified-peer ancestry, actual current config descriptor and exact external CMake evidence; no history recopies',files=[rows[k]for k in sorted(rows)],families=[families[k]for k in sorted(families)]))
root=j(V1/'root-authority.template.json');root.update(state='UNISSUED_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_V2',requiredIssuedState='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_V2',externalOutputRoot=str(m.OUT),stageJournal=str(m.JOURNAL),baselineGitPolicy=m.git_policy());w('root-authority.template.json',root)
cfg=j(V1/'config.template.json');cfg.update(state='UNISSUED_NODE_CRYPTO_HASH_HMAC357_STAGE_CONFIG_V2',requiredIssuedState='NODE_CRYPTO_HASH_HMAC357_STAGE_CONFIG_V2');w('config.template.json',cfg)
contract=j(V1/'future-source-review-contract.json');contract['requiredState']='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V2';w('future-source-review-contract.json',contract)
# Adapt only the Source-local test context/protocol; native7c5a peer remains V1.
s=(V1/'test-pure.py').read_text().replace('INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V1','INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V2')
s=s.replace("result=dict(schemaVersion=1,state='HASH_HMAC357_STAGE_PURE_MODELS_PASSED'",(OWN/'extra-tests.py.txt').read_text()+"\nresult=dict(schemaVersion=1,state='HASH_HMAC357_STAGE_V2_PURE_MODELS_PASSED'")
(OWN/'test-pure.py').write_text(s)
print(json.dumps(dict(state='SOURCE_PREPARATION_ONLY',currentRows=len(rows),families=len(families),nativeInputs357=True,copyPlanByteIdentical=d(OWN/'stage-copy-plan.json')['sha256']==d(V1/'stage-copy-plan.json')['sha256'],gitInvoked=False)))
