"""Read/hash Source preparation only; no tool, oracle, native or guest calls."""
from pathlib import Path
import hashlib,json,os,stat
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[3]
assert not (OWN/'index.json').exists(), 'Sealed Source families are immutable'
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def tree(root):
 root=Path(root);rows=[]
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   p=Path(parent)/name;s=p.lstat();r=dict(path=p.relative_to(root).as_posix(),kind='link'if p.is_symlink()else'directory'if p.is_dir()else'file',mode=stat.S_IMODE(s.st_mode))
   if p.is_symlink():r.update(linkText=os.readlink(p),resolved=str(p.resolve(strict=True)))
   elif p.is_file():r.update(bytes=s.st_size,sha256=row(p)['sha256'])
   rows.append(r)
 rows.sort(key=lambda r:r['path']);data=json.dumps(rows,separators=(',',':'),ensure_ascii=False).encode()
 return dict(root=str(root),rootMode=stat.S_IMODE(root.stat().st_mode),entries=len(rows),sha256=hashlib.sha256(data).hexdigest())
native=read(OWN.parent/'node-crypto-hash-hmac-artifact-revalidation-candidate-v2/references.json')
observed=read(OWN.parent/'node-crypto-hash-hmac-artifact-revalidation-v2-root-results.json')
actual=read(observed['actualRevalidationResult']['path'])
assert actual['rawMetadataFields']==83 and actual['nativeSourceFiles']==357 and actual['selectedWholeManifests']==12
fixture=OWN.parent/'node-crypto-hash-hmac-runtime-fixtures-v2';oracle=OWN.parent/'independent-node-crypto-hash-hmac-node-oracle-results-review-v1'
apis={
 'toolchain':REPO/'tests/node-compat/toolchain.mjs',
 'componentizer':REPO/'tests/node-compat/componentizer.mjs',
 'bundler':REPO/'tests/node-compat/profile-bundler.mjs',
 'moduleSelection':REPO/'tests/node-compat/module-selection.mjs',
 'durable':OWN.parent/'ownership-component-candidate-v1/durable.mjs',
 'durableHost':OWN.parent/'ownership-component-candidate-v1/durable-host.mjs',
 'wholeCapture':REPO/'tests/node-compat/foundation-scheduler/combined-native-component-caller-candidate-v1/io.mjs',
}
dependencies=[
 'tests/node-compat/capability-policy.mjs','tests/node-compat/wasi-0.2.10-interfaces.json',
 'tests/node-compat/private-ticks-admission.mjs','tests/node-compat/classic-streams-admission.mjs',
 'tests/node-compat/legacy-stream-web-receipts.json','builtins/node-compat/validate-manifest.mjs',
 'builtins/node-compat/manifest.schema.json','builtins/node-compat/export-manifest.node-v22.14.0.json',
 'tests/node-compat/abi-fix/componentize-import-i32-v1.patch','tests/node-compat/abi-fix/splicer-Cargo.v1.lock',
 'tests/node-compat/oom/componentize-clock-errno-v2.patch',
 'tests/node-compat/foundation-crypto/ownership-component-candidate-v1/authority.mjs']
packager=Path('/private/tmp/starling-node-compat/import-abi-clock-v2-build/package')
toolchain=Path('/private/tmp/starling-node-compat/toolchain')
tool_roots=[toolchain,packager,Path('/private/tmp/starling-node-compat/native-toolchain-lock/node_modules')]
refs=dict(schemaVersion=1,node=native['producerReferences'],nativeEngine=native['engine'],nativeMetadata=native['metadata'],
 nativeSourceIndex=native['integrationSourceIndex'],producerIndex=native['producerControllerIndex'],
 revalidationSourceIndex=row(OWN.parent/'node-crypto-hash-hmac-artifact-revalidation-candidate-v2/index.json'),
 revalidationResult=observed['actualRevalidationResult'],revalidationRoot=row(OWN.parent/'node-crypto-hash-hmac-artifact-revalidation-v2-root-results.json'),
 revalidationLedger=actual['inputHashes'],tmpAliasPolicy=actual['tmpAliasPolicy'],configuredSourceRoot=native['configuredSourceRoot'],
 fixtureIndex=row(fixture/'index.json'),fixture=row(fixture/'fixture.mjs'),wit=row(fixture/'scalar.wit'),fixtureManifest=row(fixture/'manifest.json'),
 oracleReview=dict(index=row(oracle/'index.json'),result=row(oracle/'results.json')),oracleContract=row(oracle/'result-contract.json'),
 apis={k:row(v)for k,v in apis.items()},apiDependencies=[row(REPO/p)for p in dependencies],
 toolTrees=[tree(p)for p in tool_roots],toolchainRoot=str(toolchain),packagerEntry=str(packager/'src/componentize.js'),
 preview2Adapter=row(REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),
 worldName='validation',selectedInterfaces=[],disableFeatures=['clocks','fetch-event','http','random','stdio'],
 artifactReview=None,artifactContract=None,comparator=None,sourceReview=None,
 outputPrefix='/private/tmp/starling-node-compat/hash-hmac357-experimental-diagnostic-v1')
refs['node']=dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024)
assert row(refs['node']['path'])==refs['node']
save('references.json',refs)
print(json.dumps(dict(sourcePrepared=True,toolTrees=len(tool_roots),artifactReview=None,allActions=False)))
