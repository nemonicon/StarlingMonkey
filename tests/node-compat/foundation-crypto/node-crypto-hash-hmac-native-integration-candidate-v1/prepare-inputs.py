"""Finite Source-reference writer; does not create configured SOURCE/WORK/FREEZE."""
import hashlib,json,stat
from pathlib import Path
OWN=Path(__file__).resolve().parent;ROOT=OWN.parents[3]
assert not (OWN/'index.json').exists()
S=ROOT/'tests/node-compat/foundation-scheduler';K=ROOT/'tests/node-compat/foundation-crypto'
p=json.loads((OWN/'policy.json').read_bytes())
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def desc(path):
 path=Path(path).absolute();info=path.stat();assert stat.S_ISREG(path.lstat().st_mode)
 return dict(path=str(path),sha256=digest(path),bytes=info.st_size)
def write(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
frozen=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
base=json.loads((S/'combined-native-build-controller-candidate-v2/policy.json').read_bytes())
before={r['path']:r['sha256']for r in base['expectedNativeSourceManifest']}
rows=[]
for r in p['expectedNativeSourceManifest']:
 changed=r['path'] in {x['path']for x in p['combinedSourcePolicy']['changes']}
 origin=OWN/'native'/r['path'] if changed else frozen/'source'/r['path']
 d=desc(origin);assert d['sha256']==r['sha256']
 rows.append(dict(path=r['path'],original=d['path'],sha256=d['sha256'],bytes=d['bytes'],role='NEW_HASH_HMAC_SOURCE_AFTERIMAGE'if changed else'RETAINED_GENUINE_COMBINED355_FROZEN_SOURCE'))
write('native-origins.json',dict(schemaVersion=1,nativeSourceFiles=357,retainedParentFiles=353,changedParentFiles=2,newSourceFiles=2,files=rows))
embedding=[]
for r in p['expectedComponentizeSourceManifest']:
 d=desc(frozen/'componentize-source'/r['path']);assert d['sha256']==r['sha256'];embedding.append(dict(path=r['path'],**{k:v for k,v in d.items()if k!='path'},original=d['path']))
write('embedding-origins.json',dict(schemaVersion=1,externalEmbeddingSources=3,files=embedding,role='GENUINE_EXPECTED_EMBEDDING_BYTES_REFERENCE_NOT_COPIED_INTO_NATIVE357'))
old=json.loads((S/'combined-native-integration-candidate-v1/tool-origins.json').read_bytes())['files']
tools={r['path']:r for r in old};relative='tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2/policy.json';d=desc(ROOT/relative)
assert relative not in tools;tools[relative]=dict(path=relative,original=d['path'],sha256=d['sha256'],bytes=d['bytes'])
for r in tools.values():assert digest(r['original'])==r['sha256'] and Path(r['original']).stat().st_size==r['bytes']
write('tool-origins.json',dict(schemaVersion=1,files=[tools[k]for k in sorted(tools)],entryContext='Active new recipe/helper remain original OWN context; staged old recipe/helpers are historical DATA unless explicit generic dependency import is named.',activeRecipe=desc(OWN/'build-engine.sh'),activeHelper=desc(OWN/'layer-policy.py'),freezer=None,exporter=None,bootstrap=None))
write('stage-input-plan.json',dict(schemaVersion=1,state='SOURCE_ONLY_FINITE_PLAN_NO_STAGE_CONTROLLER',destination=p['contexts']['configuredSourceRoot'],baselineRevision='54b3329b3ce818fd1f244e871e9c259b63667cda',nativeSourceFiles=357,toolRows=len(tools),files=rows+[tools[k]for k in sorted(tools)],ownSealedFamilyAddedSeparately=True,ownFamilyRole='DATA in configured clone; actual active producer/helper are authentic original OWN files',requiredCopyProperties=dict(regular=True,singleLink=True,distinctOriginalInode=True,fileMode='0600',directoryMode='0700',noGitAlternates=True,noObjectHardlinks=True),workRoot=p['contexts']['workRoot'],freezeRoot=p['contexts']['freezeRoot'],workAndFreezeMustRemainAbsentAtStage=True,stageExecuted=False))
families=[
 K/'node-crypto-hash-hmac-candidate-v1',K/'independent-node-crypto-hash-hmac-source-review-v1',K/'node-crypto-hash-hmac-sdk-syntax-v1',
 S/'combined-native-integration-candidate-v1',S/'combined-native-build-controller-candidate-v2',S/'independent-combined355-native-build-v2-results-review-v1',S/'independent-combined355-native-freeze-v2-results-review-v1']
refs={}
def add(path):
 d=desc(path);old=refs.setdefault(d['path'],d);assert old==d
for r in rows+list(tools.values())+embedding:add(r['original'])
for folder in families:
 add(folder/'index.json');index=json.loads((folder/'index.json').read_bytes())
 index_rows=index.get('files')
 if index_rows is None:raise AssertionError(('Unknown actual family schema',folder,list(index)))
 for row in index_rows:
  file=folder/row['path'];d=desc(file);assert d['sha256']==row['sha256']and d['bytes']==row['bytes'];add(file)
for path in [frozen/'normal-off.engine.wasm',frozen/'normal-off.engine.wasm.build.json',frozen/'normal-off-freeze-receipt.json',ROOT/'builtins/node-compat/manifest.schema.json',ROOT/'builtins/node-compat/validate-manifest.mjs',ROOT/'tests/node-compat/module-selection.mjs',ROOT/'tests/node-compat/profile-bundler.mjs',Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')]:add(path)
write('references.json',dict(schemaVersion=1,nativeParentSourceIndex=desc(S/'combined-native-integration-candidate-v1/index.json'),nativeParentBuildIndex=desc(S/'independent-combined355-native-build-v2-results-review-v1/index.json'),nativeParentFreezeIndex=desc(S/'independent-combined355-native-freeze-v2-results-review-v1/index.json'),hashHmacSourceIndex=desc(K/'node-crypto-hash-hmac-candidate-v1/index.json'),hashHmacSourcePeer=desc(K/'independent-node-crypto-hash-hmac-source-review-v1/index.json'),sdkSyntaxIndex=desc(K/'node-crypto-hash-hmac-sdk-syntax-v1/index.json'),familyIndices=[desc(f/'index.json')for f in families],nativeParentEngine=desc(frozen/'normal-off.engine.wasm'),nativeParentMetadata=desc(frozen/'normal-off.engine.wasm.build.json'),nativeParentFreezeReceipt=desc(frozen/'normal-off-freeze-receipt.json'),node=desc('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'),packagingApi='builtinMap(full12) and bundleProfile({builtinManifests:full12}) only after future genuine357 admission; old selectedManifestsForEngine is deliberately NOT used',buildController=None,stageController=None,freezer=None,pins=None,bootstrap=None,actualNewEngine=None,actualNewMetadata=None))
write('input-hashes.json',dict(schemaVersion=1,scope='Exact current Source boundary only: seven complete indexed families, retained native/tool/embedding origins and actual base artifact descriptors. No recursive claim over unrelated historical receipts or every nested BUILD ledger row.',files=[refs[k]for k in sorted(refs)]))
# Canonical per-top-level policy delta hashes avoid copying a historical policy tree.
sha_value=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
write('policy-delta.json',dict(schemaVersion=1,parent=desc(S/'combined-native-build-controller-candidate-v2/policy.json'),changes=[dict(key=k,beforeCanonicalSha256=sha_value(base[k])if k in base else None,afterCanonicalSha256=sha_value(p[k]))for k in sorted(set(base)|set(p))if base.get(k)!=p.get(k)],derivation=desc(OWN/'derive-source.py'),scope='New Source policy only; never a transformation of actual metadata or an admitted native frame'))
print(json.dumps(dict(state='SOURCE_INPUT_PLAN_ONLY',nativeFiles=len(rows),toolRows=len(tools),externalEmbedding=len(embedding),inputFiles=len(refs),actionsInvoked=False)))
