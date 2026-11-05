"""Source/data manifest assembly only. No CLI/helper/process/crypto calls."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;K=P.parent;Z=K.parent/'foundation-zlib'
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def data(p):return json.loads(Path(p).read_bytes())
def save(n,v):
 with (P/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n')
normal=K/'independent-ownership-runtime-v1-results-review-v1';artifact=K/'independent-ownership-component-v3-results-review-v1';transport=Z/'cost-wasmtime-transport-candidate-v1'
assert row(normal/'index.json')['sha256']=='abcb6da340ab7ffb53189d64f51c2e4c8b1ca4fb1cd50f2cc035235818a32c42'
assert row(normal/'result-contract.json')['sha256']=='859649edac081ae8dff0a34b100d130faade6b0a20776062e572394d94527e4f'
assert row(artifact/'index.json')['sha256']=='8be6c70b212922b201ed4e4439f903b01aad53f2d7b31999e0e0a3d31ff82200'
assert row(artifact/'result-contract.json')['sha256']=='47ea76aabd722336ab694040fa5f7a20fddc5634bc6f43537e6bce794b0cbd97'
nc=data(normal/'result-contract.json');ac=data(artifact/'result-contract.json');assert nc['artifacts']==ac['artifacts']
out_ix=nc['requiredExactDescriptors']['actualIndex'];out=data(out_ix['path']);wrapper=next(r for r in out['files']if r['path']=='wrapper/raw/001.json');wrapper={**wrapper,'path':str(Path(out_ix['path']).parent/wrapper['path'])}
refs=dict(schemaVersion=1,state='ACTUAL_NORMAL_AND_ARTIFACT_PREREQUISITES_NOT_WT_AUTHORITY',normalReview=dict(index=row(normal/'index.json'),result=row(normal/'results.json')),normalContract=row(normal/'result-contract.json'),
 artifactReview=dict(index=row(artifact/'index.json'),result=row(artifact/'results.json')),artifactContract=row(artifact/'result-contract.json'),artifacts=ac['artifacts'],
 normalOutputIndex=out_ix,normalWrapper=wrapper,nodeOracle=nc['requiredExactDescriptors']['nodeOracle'],node=data(K/'ownership-runtime-candidate-v1/references.json')['node'],
 wasmtime=data(transport/'future-proof.template.json')['wasmtime'],transportSourceIndex=row(transport/'index.json'),transportDecoder=row(transport/'scalar-transport.mjs'),
 approvedRuntimeSourceIndex=row(K/'ownership-runtime-candidate-v1/index.json'),approvedChecks=row(K/'ownership-runtime-candidate-v1/checks.mjs'),approvedOracleChecks=row(K/'ownership-runtime-candidate-v1/oracle.mjs'))
save('references.json',refs)
inputs={}
def add(r,role):
 actual=row(r['path']);assert all(actual[k]==r[k]for k in ['path','sha256','bytes']),r['path'];old=inputs.get(r['path']);assert old is None or all(old[k]==r[k]for k in ['path','sha256','bytes'])
 inputs[r['path']]={**actual,'role':role}
for r in data(normal/'rehashed-inputs.json')['files']:add(r,'actual-normal-full-source-native-artifact-closure')
for family in [normal,artifact,transport]:
 add(row(family/'index.json'),'immutable-prerequisite-index')
 for r in data(family/'index.json')['files']:add(dict(path=str(family/r['path']),sha256=r['sha256'],bytes=r['bytes']),'immutable-prerequisite-member')
for r in data(transport/'input-freeze.json')['files']:add(r,'transport-primary-source-and-tool-data')
for r in [refs['wasmtime'],refs['node'],refs['normalWrapper'],refs['nodeOracle'],refs['approvedRuntimeSourceIndex'],refs['approvedChecks'],refs['approvedOracleChecks']]:add(r,'exact-public-ABI-decoder-or-normal-data')
# Follow the finite literal relative source graph, without importing any module.
import re
visited=set()
def visit(path):
 path=Path(path).resolve()
 if path in visited:return
 visited.add(path)
 if path.parent!=P:add(row(path),'actual-literal-local-module')
 for spec in re.findall(r'(?:from\s*|import\s*)[\'\"]([^\'\"]+)[\'\"]',path.read_text()):
  if spec.startswith('.'):visit(path.parent/spec)
for p in P.glob('*.mjs'):visit(p)
save('input-freeze.json',dict(schemaVersion=1,state='CRYPTO_STOCK_WT_ORIGINAL_CONTEXT_SOURCE_NATIVE_ARTIFACT_TOOL_INPUTS',files=list(inputs.values()),
 originalPathsNeverRelocated=True,normalAndArtifactProofsRemainUnchanged=True,wasmtimeOrProcessGuestCryptoActionsInvoked=False))
template=dict(schemaVersion=1,state='ROOT_REVIEWED_CRYPTO_OWNER355_STOCK_WASMTIME_V1',action='stock-wasmtime-validate',sourceIndexSha256=None,
 wasmtimeValidateAllowed=False,variant='normal-off',componentSha256=ac['artifacts']['component']['sha256'],outputRoot='/private/tmp/starling-node-compat/crypto-owner355-wasmtime-v1',
 freshProcesses=3,invocation='validate()',workerTimeoutMs=600000,maxPipeBytes=16777216,externalParentDeadlineSeconds=2400,externalController=None,
 sourceIndependentReview=None,normalReview=refs['normalReview'],normalContract=refs['normalContract'],artifactReview=refs['artifactReview'],artifactContract=refs['artifactContract'])
for key in ['nodeOracleAllowed','generatedJsAllowed','gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim']:template[key]=False
save('future-root-authority.template.json',template);save('future-config.template.json',dict(sourceIndexSha256=None,rootAction=None))
print(json.dumps(dict(sourceInputs=len(inputs),literalModules=len(visited),wasmtimeOrGuestActions=0)))
