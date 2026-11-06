"""Read/hash/AST checks only. Never import active layer helper or producer."""
import ast,hashlib,json,os,re,stat
from pathlib import Path
OWN=Path(__file__).resolve().parent;ROOT=OWN.parents[3]
assert not (OWN/'index.json').exists(), 'Sealed family is immutable'
checks=0
def ok(value,label):
 global checks
 assert value,label;checks+=1

def digest(path):
 h=hashlib.sha256()
 with open(path,'rb')as file:
  for chunk in iter(lambda:file.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def read(name):return json.loads((OWN/name).read_bytes())
def current(path):
 path=Path(path);ok(path.is_absolute()and str(path)==os.path.normpath(str(path)),'Canonical absolute input')
 lexical=path
 if str(path).startswith('/tmp/'):
  ok(Path('/tmp').is_symlink()and Path('/tmp').resolve()==Path('/private/tmp'),'Recorded macOS /tmp alias only')
  lexical=Path('/private')/str(path).lstrip('/')
 for part in [lexical,*lexical.parents]:
  ok(not part.is_symlink(),'No additional input symlink: '+str(part))
 info=lexical.lstat();ok(stat.S_ISREG(info.st_mode),'Regular input')
 return dict(path=str(path),sha256=digest(path),bytes=info.st_size,mode=stat.S_IMODE(info.st_mode))
ledger=read('input-hashes.json')['files'];ok(len(ledger)==len({r['path']for r in ledger})==2622,'Finite input ledger')
prior={}
for row in ledger:
 now=current(row['path']);ok({k:now[k]for k in row}==row,'Declared original bytes');prior[row['path']]=now
refs=read('references.json')
for index in refs['familyIndices']:
 folder=Path(index['path']).parent;data=json.loads(Path(index['path']).read_bytes())
 ok(digest(index['path'])==index['sha256'],'Family index')
 members=data['files'];ok(len(members)==len({r['path']for r in members}),'Unique indexed membership')
 for row in members:
  path=folder/row['path'];ok(not Path(row['path']).is_absolute()and'..'not in Path(row['path']).parts,'Relative indexed member')
  actual=prior[str(path)];ok(actual['sha256']==row['sha256']and actual['bytes']==row['bytes'],'Whole named indexed family row')
 # Some historical families have retained unindexed source-receipt DATA; do not claim exact physical membership here.
p=read('policy.json');parent=json.loads((ROOT/'tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2/policy.json').read_bytes())
a={r['path']:r['sha256']for r in p['expectedNativeSourceManifest']};b={r['path']:r['sha256']for r in parent['expectedNativeSourceManifest']}
ok(len(a)==357 and len(b)==355 and set(b)<=set(a),'Actual357 Source arithmetic')
ok(sum(a[k]==b[k]for k in b)==353,'353 exact retained inputs')
changed={k for k in b if a[k]!=b[k]};added=set(a)-set(b)
ok(changed=={'cmake/builtins.cmake','builtins/node-compat/register.cpp'},'Two changed parent rows')
ok(added=={'builtins/node-compat/hash-hmac-kernel.cpp','builtins/node-compat/crypto-factory.generated.h'},'Two new native files')
ok(not any('clock-lifecycle-diagnostics'in k or 'clock_lifecycle_diagnostics'in k for k in a),'No diagnostics variant merge')
for key in ['cryptoKeyOwnershipSourcePolicy','cryptoSecretFailureSourcePolicy','resourceOwnershipSourcePolicy','taskSelectionSourcePolicy','zlibErrorSemanticsSourcePolicy','zlibSourcePolicy','streamConsumersSourcePolicy']:
 ok(p[key]==parent[key],'Exact parent policy ancestry: '+key)
for row in parent['combinedSourcePolicy']['changes']:ok(a[row['path']]==row['afterSha256'],'Seven combined images preserved')
for row in p['cryptoKeyOwnershipSourcePolicy']['changes']:ok(a[row['path']]==b[row['path']],'Five current WebCrypto paths preserved; secret-failure afterimages supersede older ownership bytes')
origins=read('native-origins.json')['files'];ok(len(origins)==357,'357 physical origins')
for row in origins:ok(a[row['path']]==row['sha256']and digest(row['original'])==row['sha256'],'Real proposed357 origin')
afdb=ROOT/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-candidate-v1'
source_map={'cmake/builtins.cmake':afdb/'afterimages/cmake/builtins.cmake','builtins/node-compat/register.cpp':afdb/'afterimages/builtins/node-compat/register.cpp','builtins/node-compat/hash-hmac-kernel.cpp':afdb/'hash-hmac-kernel.cpp','builtins/node-compat/crypto-factory.generated.h':afdb/'crypto-factory.generated.h'}
for relative,original in source_map.items():ok((OWN/'native'/relative).read_bytes()==original.read_bytes(),'Exact afdb afterimage')
ok(p['expectedComponentizeSourceManifest']==parent['expectedComponentizeSourceManifest']and len(p['expectedComponentizeSourceManifest'])==3,'External embedding unchanged3')
ok(sum(k.endswith('.cpp')and k.startswith(('builtins/','runtime/'))for k in a)==63,'63 CPP derived from actual manifest')
ok(len(p['privateTargetCpp'])==7 and p['privateTargetCpp'][:-1]==parent['privateTargetCpp'],'Private7 actual target Source')
ok(p['expectedCompilation']==dict(nativeSourceFiles=357,retainedParentFiles=353,changedParentFiles=2,newSourceFiles=2,policyCpp=63,compileDatabaseRows=69,otherConfiguredRows=5,generatedNullRows=1,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,selectedNativeManifests=11,selectedPackagingManifests=1,totalSelectedManifests=12),'New finite compile contract')
ok(p['selectedModuleManifests'][:-1]==parent['selectedModuleManifests']and p['selectedManifestValues'][:-1]==parent['selectedManifestValues'],'All eleven original manifests retained')
pack=p['hashHmacSourcePolicy']['packagingManifestInput'];ok(pack['path']not in a,'Separate packaging manifest not native358')
ok(p['selectedModuleManifests'][-1]['sha256']==digest(OWN/'crypto-module-manifest.json'),'New schema manifest SHA')
manifest=read('crypto-module-manifest.json');inventory=json.loads((afdb/'node-export-manifest.json').read_bytes())
ok(manifest['modules']['node:crypto']['exports']==inventory['esmNamedIncludingDefault']and len(inventory['esmNamedIncludingDefault'])==68,'Inventory-to-schema exact ESM names')
ok(manifest['modules']['node:crypto']['importOnlyExports']==inventory['unsupportedCallableNamed'],'Unsupported callable inventory exact')
for file,key in [('native-admission-model.py','admissionModelSha256'),('hash-hmac-model.py','hashHmacModelSha256')]:ok(digest(OWN/file)==p[key],'New pure model hash')
derivation=read('tooling-derivations.json');mapping={'helper':'layer-policy.py','recipe':'build-engine.sh','metadata-model':'native-admission-model.py'}
for role,name in mapping.items():
 text=(OWN/name).read_text()
 for edit in reversed([r for r in derivation['edits']if r['role']==role]):
  ok(len(edit['afterPositions'])==edit['count'],'Exact replacement positions '+role)
  for position in reversed(edit['afterPositions']):
   ok(text[position:position+len(edit['after'])]==edit['after'],'Exact reverse span '+role)
   text=text[:position]+edit['before']+text[position+len(edit['after']):]
 donor=ROOT/'tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2'/name
 ok(text==donor.read_text(),'Whole donor reversal '+role)
ok(len(derivation['edits'])==54,'Finite actual edit inventory')
delta=read('policy-delta.json');canon=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
actual_delta={k for k in set(parent)|set(p)if parent.get(k)!=p.get(k)}
ok(actual_delta=={r['key']for r in delta['changes']},'Exact current policy delta field set')
for row in delta['changes']:ok(row['beforeCanonicalSha256']==(canon(parent[row['key']])if row['key']in parent else None)and row['afterCanonicalSha256']==canon(p[row['key']]),'Exact policy field delta hashes')
helper=(OWN/'layer-policy.py').read_text();recipe=(OWN/'build-engine.sh').read_text();model=(OWN/'native-admission-model.py').read_text()
ok(f"HERE==Path('{OWN}')"in helper,'Actual physical helper OWN')
ok(f"REPO=Path('{p['contexts']['configuredSourceRoot']}')"in helper,'Actual new configured Source')
ok('PARENT=json.loads'in helper and "len(before)==355 and len(after)==357"in helper,'Genuine distinct parent355 and own357')
ok('BASE.OWN'not in helper and 'BASE.REPO'not in helper and 'setattr('not in helper,'No donor module rebinding')
ok(helper.index('authenticate_inputs()\nBASE_ROOT=')<helper.index("HASH_MODEL=importlib"),'Donor authentication before custom pure-model import')
ok("assert digest(model_path)==POLICY['hashHmacModelSha256']"in helper,'Pure model before/final hash')
ok("digest(HERE/'policy.json')==POLICY_SHA256"in helper and digest(OWN/'policy.json')in helper,'Actual new policy pin')
ok(digest(OWN/'layer-policy.py')in recipe and digest(OWN/'policy.json')in recipe,'Actual new recipe helper/policy pins')
ok('nodeCryptoHashHmacEnabled' in recipe and 'nodeCryptoAuditedBorrowEnabled' in recipe,'New real metadata booleans')
ok("json.load"not in recipe or 'nativeParentMetadata'not in recipe,'Parent sidecar not producer input')
ok(recipe.index("metadata['privateRustupBootstrapPolicy']")<recipe.index('classification=model.validate_metadata'),'Full raw Rust provenance before new schema gate')
ok('ninja_capture,ninja_text)'in recipe and 'ninja_capture,ninja_text)'in helper,'Real changed API caller/callee')
ok(recipe.index("with open(str(ninja_stem)+'.terminal.json'")<recipe.index('assert ninja_exit==0'),'Complete raw Ninja terminal before status assertion')
ok('-DNODE_COMPAT_CRYPTO_HASH_HMAC=ON -DNODE_CRYPTO_AUDITED_BORROW=OFF'in recipe,'Named future HASH ON COPY-only CMake')
ok('hash_hmac_enabled" == 1'in recipe and 'borrow_enabled" == 0'in recipe,'Experimental recipe requires explicit enable')
ok('CCACHE_DISABLE=1 SCCACHE_DISABLE=1 CARGO_INCREMENTAL=0'in recipe,'Fresh compilation cache policy')
cmake=(OWN/'native/cmake/builtins.cmake').read_text();register=(OWN/'native/builtins/node-compat/register.cpp').read_text()
for line in ['option(NODE_COMPAT_CRYPTO_HASH_HMAC "Experimental SHA256 Hash/Hmac proposal" OFF)','option(NODE_CRYPTO_AUDITED_BORROW "Reviewed fixed-U8 NoGC EVP update borrowing" OFF)','target_sources(builtin_node_compat PRIVATE builtins/node-compat/hash-hmac-kernel.cpp)','target_link_libraries(builtin_node_compat PRIVATE OpenSSL::Crypto builtin_web_crypto)','add_dependencies(builtin_node_compat builtin_web_crypto)']:ok(line in cmake,'Real new CMake integration')
ok('engine->define_builtin_module("node:crypto", module)'in register and 'engine->define_builtin_module("crypto", module)'in register,'Real native alias registration')
plan=read('stage-input-plan.json');ok(plan['nativeSourceFiles']==357 and plan['toolRows']==1227 and len(plan['files'])==1584,'Exact future plan357+1227')
ok(len({r['path']for r in plan['files']})==1584,'Unique future Source copy destinations')
auth=read('donor-inputs.json')['files'];tool={r['path']:r for r in read('tool-origins.json')['files']}
ok(len(auth)==1226 and all(r['path']in tool and r['sha256']==tool[r['path']]['sha256']and r['bytes']==tool[r['path']]['bytes']for r in auth),'Every genuine future-stage helper dependency has actual origin')
for context in p['contexts'].values():ok(not os.path.lexists(context),'No future stage/work/freeze exists')
future=read('future-authority.json')
for key in ['sourcePeer','stageController','stagePhase','actualStage','buildController','buildPhase','actualBuild','freezer','freezePhase','actualFreeze','pins','bootstrap','component','runtime','otherNativeVariants','borrowBuild','allActionAuthority']:ok(future[key]is None,'Closed future action slot '+key)
parsed=0
for path in OWN.glob('*.py'):ast.parse(path.read_text(),filename=str(path));parsed+=1
# Parse every quoted embedded Python block; no shell or Python body is executed.
for match in re.finditer(r"<<'((?:PY)[A-Z]*)'\n",recipe):
 start=match.end();end=recipe.index('\n'+match.group(1)+'\n',start)
 ast.parse(recipe[start:end],filename='build-engine.sh:'+match.group(1));parsed+=1
for name in ['pure-check-results.json','manifest-check-results.json']:ok(read(name)['checks']>0,'Stored pure check evidence')
# Repeat the exact declared original boundary and mode check at the end.
for path,before in prior.items():ok(current(path)==before,'Final unchanged input bytes/modes')
result=dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_SOURCE_CHECKS_PASSED',checks=checks,inputReferences=len(prior),indexedFamilies=len(refs['familyIndices']),pythonAstUnits=parsed,toolingEdits=54,nativeSourceFiles=357,externalEmbeddingSources=3,selectedManifests=12,nativeHelperImported=False,stageActionsInvoked=False,nativeBuildActionsInvoked=False,engineExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False)
(OWN/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
