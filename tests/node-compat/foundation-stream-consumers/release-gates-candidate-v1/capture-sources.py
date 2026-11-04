"""Pure source/data snapshot preparation. Never import or execute owner code."""
from pathlib import Path
import hashlib,json,os

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
NATIVE_ROOT=Path('/private/tmp/starling-node-compat/consumers-source-v2')
CLASSIC_ROOT=Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
REL=Path('tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1')
BASE=CLASSIC_ROOT/REL
NATIVE_REL=Path('tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2')
NATIVE=NATIVE_ROOT/NATIVE_REL
SNAPSHOT=HERE/'snapshot'
origins={};references={};hints=[]

def sha(data):return hashlib.sha256(data).hexdigest()
def read(path,expected=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink(),path
 raw=path.read_bytes();assert expected is None or sha(raw)==expected,path;assert size is None or len(raw)==size,path
 return raw
def source_reference(path,raw,role):
 path=Path(path);key=str(path)
 row={'path':key,'canonicalPath':str(path.resolve()),'sha256':sha(raw),'bytes':len(raw)}
 if key in references:
  assert all(references[key][k]==v for k,v in row.items())
  if role not in references[key]['roles']:references[key]['roles'].append(role)
 else:references[key]={**row,'roles':[role]}
def copy(relative,origin,role,expected=None,size=None,priority=False):
 relative=str(relative);assert not Path(relative).is_absolute()and'..'not in Path(relative).parts
 raw=read(origin,expected,size)
 if relative in origins:
  if origins[relative]['sha256']!=sha(raw):
   assert not priority,'The authoritative355 overlay was already installed'
   hints.append({'relativePath':relative,'notSelectedOrigin':str(origin),'notSelectedSha256':sha(raw),
      'selectedOrigin':origins[relative]['originalPath'],'selectedSha256':origins[relative]['sha256'],
      'reason':'Fresh genuine355 native/tool source overlay; old source hint is not new metadata or source authority'})
  return
 target=SNAPSHOT/relative;target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('xb')as stream:stream.write(raw)
 source_reference(origin,raw,role)
 origins[relative]={'relativePath':relative,'originalPath':str(origin),'canonicalOriginalPath':str(Path(origin).resolve()),
    'sha256':sha(raw),'bytes':len(raw),'role':role}

assert not SNAPSHOT.exists()
native_index=json.loads(read(NATIVE/'index.json','9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'))
base_index=json.loads(read(BASE/'index.json','a08aec2d8a28f6bb91251841b617be20820c23ab085e526d0dc107439b061c6e'))
policy=json.loads(read(NATIVE/'policy.json'));tools=json.loads(read(NATIVE/'artifact-tools/tool-pins.json'))
assert len(policy['expectedNativeSourceManifest'])==355 and len(tools['toolDependencies'])==767
for row in policy['expectedNativeSourceManifest']:
 copy(row['path'],NATIVE_ROOT/row['path'],'GENUINE355_NATIVE_SOURCE_SNAPSHOT_NOT_CONFIGURED_ROOT',row['sha256'],priority=True)
for row in tools['toolDependencies']:
 copy(row['path'],NATIVE_ROOT/row['path'],'GENUINE355_NATIVE_TOOL_SNAPSHOT_NOT_PACKAGING_AUTHORITY',row['sha256'],row['bytes'],priority=True)
for row in native_index['files']:
 copy(NATIVE_REL/row['path'],NATIVE/row['path'],'NATIVE_PRODUCER_INDEXED_SOURCE_DATA_ONLY',row['sha256'],row['bytes'],priority=True)
copy(NATIVE_REL/'index.json',NATIVE/'index.json','NATIVE_PRODUCER_INDEX_BYTES_DATA_ONLY',priority=True)

# The old source seal is a dependency-name hint only. We do not reinterpret its
# original contexts, execute an old preflight, or promote its342 native rows.
old=json.loads(read(BASE/'input-freeze.json'))
source_reference(BASE/'index.json',read(BASE/'index.json'),'OLD_SOURCE_FAMILY_INDEX_BYTES_ONLY')
source_reference(BASE/'input-freeze.json',read(BASE/'input-freeze.json'),'OLD_DEPENDENCY_HINT_DATA_ONLY_NO_AUTHORITY')
excluded_http_prefixes=['capability/hosts/','capability/runners/http-build.mjs']
excluded_http_names={'capability/prepare-http.mjs','capability/build-http.mjs','capability/seal-http-component.mjs',
 'capability/http-component.mjs','capability/http-contract.mjs','capability/http-component-pins.json',
 'capability/run-http-wasmtime.mjs','capability/run-http-wash.mjs','capability/audit-http.mjs','capability/computed-inputs.mjs'}
excluded_legacy_authority={'native-preflight.mjs','native-preflight.template.mjs','runtime-pins.json','root-review-receipt.json',
 'activation-reference.json','source-receipt.json','input-freeze.json','capability/input-freeze.json','source-mappings.json','index.json'}
def wanted(relative):
 if relative.startswith(str(REL)+'/'):
  local=str(Path(relative).relative_to(REL))
  if local in excluded_http_names or any(local.startswith(p)for p in excluded_http_prefixes):return False
  if local in excluded_legacy_authority:return False
 return True
for row in old['inputs']:
 path=Path(os.path.abspath(BASE/row['path']))
 try:relative=str(path.relative_to(CLASSIC_ROOT))
 except ValueError:continue
 if wanted(relative):copy(relative,path,'SEALED_CLASSIC_SOURCE_DEPENDENCY_BODY',row['sha256'],row['bytes'])
for row in base_index['files']:
 relative=str(REL/row['path'])
 if wanted(relative):copy(relative,BASE/row['path'],'SEALED_CLASSIC_RELEASE_FOLLOWON_BODY',row['sha256'],row['bytes'])

# Explicit genuine old control origins remain external, immutable controls.
controls=json.loads(read(BASE/'release/historical-controls.json'))
control_rows=list(controls['modules'].values())
control_rows.append({'engine':'/tmp/starling-node-compat/foundations-v7/native-freeze/off-foundations.engine.wasm',
 'sourceRoot':'/tmp/starling-node-compat/foundations-v7/native-freeze/source',
 'engineSha256':'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09','sourceFiles':293,'enabledField':'allocator-old-core','optional':False})
historical=[]
for control in control_rows:
 engine=Path(control['engine']);raw=read(engine,control['engineSha256']);source_reference(engine,raw,'EXACT_HISTORICAL_CONTROL_ENGINE_NOT355_EVIDENCE')
 metadata_path=Path(str(engine)+'.build.json');metadata_raw=read(metadata_path,control.get('receiptSha256'));source_reference(metadata_path,metadata_raw,'EXACT_HISTORICAL_CONTROL_METADATA_NOT_REWRITTEN')
 metadata=json.loads(metadata_raw);assert metadata['engineSha256']==control['engineSha256']and len(metadata['sourceManifest'])==control['sourceFiles']
 for row in metadata['sourceManifest']:
  path=Path(control['sourceRoot'])/row['path'];source_reference(path,read(path,row['sha256']),'EXACT_HISTORICAL_CONTROL_ORIGINAL_SOURCE')
 historical.append({**control,'receiptSha256':sha(metadata_raw),'metadata':metadata})

# Preserve an oracle's embedded absolute source pointer rather than rewriting it.
allocator=CLASSIC_ROOT/'tests/node-compat/foundation-alloc-unsafe/node-results.json'
data=json.loads(read(allocator));demand=data['demandSource'];path=Path(demand['path'])
source_reference(path,read(path,demand['sha256']),'EXACT_ABSOLUTE_NODE_ORACLE_SOURCE_CONTEXT')

context=ROOT/'tests/node-compat/foundation-stream-consumers/component-validation-candidate-v2/tool-context.json'
tool_context=json.loads(read(context));source_reference(context,read(context),'CURRENT_PINNED_TOOL_TREES_LINKS_INVOCATION_CONTEXT')
assert len(tool_context['toolTrees'])==2 and len(tool_context['toolLinks'])==22 and len(tool_context['inputs'])==4892
for row in tool_context['inputs']:source_reference(row['path'],read(row['path'],row['sha256'],row['bytes']),'PHYSICAL_PACKAGE_TREE_OR_INVOCATION_BINARY')

def put(name,value):
 with(HERE/name).open('x')as stream:stream.write(json.dumps(value,indent=2)+'\n')
put('snapshot-origins.json',{'schemaVersion':1,'state':'FRESH_355_AND_HISTORICAL_BODY_SOURCE_SNAPSHOT_NOT_EXECUTED',
 'files':[origins[k]for k in sorted(origins)],'nativeSourceSnapshotDoesNotReplaceConfiguredOrFrozenRoot':True,
 'legacy342DependencyHintsNotAuthority':True,'native355OverridesOldSourceHints':hints,'httpAfterimagesImplemented':False})
put('source-inputs.preparation.json',{'schemaVersion':1,'state':'ORIGINAL_PREPARATION_CONTEXT_ONLY',
 'originalPreparationRoot':str(HERE),'nativeConfiguredSourceRoot':str(NATIVE_ROOT),'historicalSourceBodyRoot':str(CLASSIC_ROOT),
 'files':[references[k]for k in sorted(references)],'oldNestedPreparationRowsFollowed':False,'actionsExecuted':False})
put('historical-controls.sealed.json',{'schemaVersion':1,'state':'EXACT_HISTORICAL_CONTROL_METADATA_AND_SOURCE_CONTEXT_NOT_NEW355_PASSES',
 'controls':historical,'originalDocument':controls,'sourceMetadataRewritten':False})
put('tool-context.json',tool_context)
print(json.dumps({'snapshotFiles':len(origins),'sourceReferences':len(references),'nativeOverrides':len(hints),
 'historicalControlRecords':len(historical),'toolTrees':2,'toolLinks':22,'ownerActionsExecuted':False}))
