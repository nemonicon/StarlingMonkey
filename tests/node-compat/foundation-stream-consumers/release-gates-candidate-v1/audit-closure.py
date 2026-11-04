"""Finite pinned-source physical audit, not a general JavaScript parser."""
from pathlib import Path
import hashlib,json,re
H=Path(__file__).resolve().parent;S=H/'snapshot';NC='snapshot/tests/node-compat/';B=NC+'foundation-classic-streams/production-trace-regression-activated-v1/'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
entries=[B+'release/run-release.mjs',B+'common/run-allocator-gc.mjs',B+'capability/run-focused.mjs',B+'capability/run-gc.mjs',B+'capability/run-getter.mjs',
 *[B+'common/run-'+name+'.mjs'for name in ['core','allocator']],*[B+'off/run-'+name+'.mjs'for name in ['stream-web','sync','runtime','late','callbacks']],
 *[B+'release/run-'+name+'.mjs'for name in ['path','events','string-decoder','assert','querystring','util']],
 *[NC+name for name in ['toolchain.mjs','componentizer.mjs','profile-bundler.mjs','foundations/native-scalar-harness.mjs','module-selection.mjs','core-expectations.mjs']],
 'native-preflight.template.mjs','physical.mjs','contracts.mjs','entry.mjs','run-gates.mjs','run-selected.mjs']
pending=list(entries);visited=set();edges=[];urls=[];bare=[];readsites=[]
def local(importer,request,kind):
 target=(H/importer).parent/request;target=target.resolve();assert target.is_relative_to(H),('Escaping local edge',importer,request)
 assert target.is_file()and not target.is_symlink(),('Missing physical module/data',importer,request,str(target))
 name=str(target.relative_to(H));edge={'importer':importer,'request':request,'target':name,'kind':kind}
 if edge not in edges:edges.append(edge)
 if name.endswith(('.mjs','.js','.cjs')):pending.append(name)
 else:visited.add(name)
while pending:
 name=pending.pop(0)
 if name in visited:continue
 visited.add(name);p=H/name;assert p.is_file()and not p.is_symlink();text=p.read_text()
 for pattern in [r'^\s*(?:import|export)\b[^\n;]*?\bfrom\s*([\'\"])([^\'\"]+)\1',r'\bimport\(\s*([\'\"])([^\'\"]+)\1\s*\)']:
  for match in re.finditer(pattern,text,re.M):
   request=match[2]
   if request.startswith('.'):local(name,request,'STATIC_OR_LITERAL_DYNAMIC_IMPORT')
   else:bare.append({'importer':name,'request':request,'kind':'NODE_BUILTIN'if request.startswith('node:')else'PINNED_PACKAGE_OR_VIRTUAL_GUEST_IMPORT'})
 for match in re.finditer(r'new URL\(\s*([\'\"])([^\'\"]+)\1\s*,\s*import\.meta\.url\s*\)',text):
  request=match[2];target=((H/name).parent/request).resolve();assert target.is_relative_to(H)
  if target.is_dir():urls.append({'importer':name,'request':request,'target':str(target.relative_to(H)),'kind':'REPOSITORY_OR_FIXTURE_DIRECTORY_CONTEXT'})
  else:local(name,request,'LITERAL_RELATIVE_DATA_OR_FIXTURE_URL')
 for line_number,line in enumerate(text.splitlines(),1):
  if 'readFile('in line or'readFileSync('in line:readsites.append({'path':name,'line':line_number,'source':line.strip(),'scope':'Pinned finite-source read site; complete local snapshot and explicit external original contexts sealed, dynamic runtime output reads excluded from source authority'})
rows=[]
for name in sorted(visited):
 if name=='native-preflight.mjs':continue # compiled boundary is authenticated by generated index/template
 raw=(H/name).read_bytes();rows.append({'path':name,'sha256':sha(raw),'bytes':len(raw)})
# The four real packaging loaders, their selected ABI/clock data and repository
# adapter are mandatory beyond the767 native-tool rows. New355 admission modules
# are physical transitive dependencies, not an old342 source projection.
required=[NC+name for name in ['toolchain.mjs','componentizer.mjs','profile-bundler.mjs','foundations/native-scalar-harness.mjs','private-ticks-admission.mjs','classic-streams-admission.mjs','zlib-admission.mjs','stream-consumers-admission.mjs']]
assert set(required)<=visited
selected_data=[NC+'wasi-0.2.10-interfaces.json',NC+'abi-fix/componentize-import-i32-v1.patch',NC+'abi-fix/splicer-Cargo.v1.lock',NC+'oom/componentize-clock-errno-v2.patch','snapshot/builtins/node-compat/manifest.schema.json','snapshot/builtins/node-compat/export-manifest.node-v22.14.0.json',NC+'legacy-stream-web-receipts.json','snapshot/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']
for name in selected_data:
 raw=(H/name).read_bytes()
 if name not in visited:rows.append({'path':name,'sha256':sha(raw),'bytes':len(raw)})
origins=json.loads((H/'snapshot-origins.json').read_bytes())['files'];proof=json.loads((H/'afterimage-proof.json').read_bytes());changed={row['path']for row in proof['edits']}
unchanged=[];cases=[]
for row in origins:
 p=S/row['relativePath'];raw=p.read_bytes()
 if row['relativePath']not in changed:assert sha(raw)==row['sha256'];unchanged.append(row['relativePath'])
 if re.search(r'(?:cases|corpus|oracle|node-results|component|fixture|semantic|glob|native-checks|native-policies)',row['relativePath'])and p.suffix in ['.mjs','.js','.cjs','.json']and row['relativePath']not in changed:cases.append({'path':row['relativePath'],'sha256':sha(raw),'bytes':len(raw)})
native=json.loads((H/'lineage.json').read_bytes())['native355']
for row in native:assert sha((S/row['path']).read_bytes())==row['sha256'],row['path']
put('selected-closure.json',{'schemaVersion':1,'state':'FINITE_PINNED_SELECTED_MODULE_DATA_PHYSICAL_CLOSURE','entries':entries,'localModulesAndData':sorted(rows,key=lambda r:r['path']),'compiledBoundaryModules':['native-preflight.mjs'],'localEdges':sorted(edges,key=lambda r:(r['importer'],r['request'],r['kind'])),'directoryContexts':urls,'bareImports':bare,'dataReadSites':readsites,'scope':'Finite regex audit of pinned sources plus complete snapshot membership; not a general JavaScript parser or proof of new runtime success','ownerModulesImported':False,'packageAlgorithmsLoaded':False})
put('inherited-body-audit.json',{'schemaVersion':1,'state':'ALL_NATIVE355_AND_UNCHANGED_SOURCE_BODIES_HASH_EXACT','snapshotFiles':len(origins),'unchangedFiles':len(unchanged),'hostAfterimagePaths':sorted(changed),'nativeSourceFiles':355,'nativeSourcesModified':False,'unchangedCaseOracleFixtureData':cases,'safeNodeOracleSourcesRetained':True,'sourceResultsAdopted':False,'historicalControlsNotNew355Evidence':True})
payload=[*['snapshot/'+str(p.relative_to(S))for p in S.rglob('*')if p.is_file()],*['contracts.mjs','physical.mjs','native-preflight.template.mjs','entry.mjs','run-gates.mjs','run-selected.mjs','lineage.json','tool-context.json','package-endpoints.json','selected-closure.json','historical-controls.sealed.json','afterimage-proof.json','inherited-body-audit.json','runtime-authority.template.json','prerequisites.json','reviewed-consumer-validation.json','snapshot-origins.json'],*['preimages/'+str(p.relative_to(H/'preimages'))for p in(H/'preimages').rglob('*')if p.is_file()]]
payload.extend(['integration-bindings.json','future-actions.template.json'])
assert len(payload)==len(set(payload));assert'native-preflight.mjs'not in payload
put('payload-files.json',{'schemaVersion':1,'state':'FUTURE_PUBLISHED_SOURCE_PAYLOAD_ONLY','files':sorted(payload),'compiledBoundaryCreatedOnlyByPublisher':['activation.json','native-preflight.mjs','input-freeze.json','source-receipt.json','index.json'],'actionsExecuted':False})
print(json.dumps({'selectedModuleAndDataFiles':len(rows),'localEdges':len(edges),'selectedDataMandatory':len(selected_data),'snapshotFiles':len(origins),'unchangedCaseOracleFixtureData':len(cases),'payloadFiles':len(payload),'nativeSources':355,'actionsExecuted':False}))
