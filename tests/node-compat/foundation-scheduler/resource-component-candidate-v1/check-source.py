"""Finite independent data/source boundary checks. No owner/helper import."""
from pathlib import Path
import ast
import hashlib
import json
import re
OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
assert REPO==Path('/Users/dan/dev/StarlingMonkey')
checks=0
def check(v):
 global checks
 assert v
 checks+=1
def descriptor(p):
 p=Path(p);check(p.is_absolute()and p.is_file()and not p.is_symlink());a=p.stat();h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 z=p.stat();check((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns));return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
manifest=json.loads((OWN/'input-freeze.json').read_bytes());refs=json.loads((OWN/'references.json').read_bytes())
check(len(manifest['files'])==len({r['path']for r in manifest['files']}))
for row in manifest['files']:
 p=Path(row['path']);check(p.is_absolute()and str(p)==row['path']and '..'not in p.parts and '\\'not in row['path']and '\0'not in row['path'])
 check(str(p.parent.resolve())==re.sub(r'^/tmp(?=/|$)','/private/tmp',str(p.parent)))
 check(type(row['bytes'])is int and 0<=row['bytes']<=1024*1024*1024)
 check(descriptor(row['path'])==row)
for fam in refs['families']:
 ix=fam['index'];check(descriptor(ix['path'])==ix);root=Path(ix['path']).parent;names={'index.json'}
 for row in json.loads(Path(ix['path']).read_bytes())['files']:
  check(row['path']not in names);names.add(row['path']);check(descriptor(root/row['path'])==dict(row,path=str(root/row['path'])))
 check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names)
derived=json.loads((OWN/'fixture-derivations.json').read_bytes())
for row in derived['entries']:
 before=Path(row['original']['path']).read_bytes();after=(OWN/row['afterimage']).read_bytes()
 if row['kind'].startswith('BYTE_EXACT'):check(before==after)
 else:check(before.decode().count("const scalarWit='"+row['literal']+"';")==1 and after==(row['literal']+'\n').encode())
for fixture,v in refs['fixtures'].items():
 check(descriptor(v['code']['path'])==v['code']and descriptor(v['wit']['path'])==v['wit'])
 code=Path(v['code']['path']).read_text();imports=re.findall(r"^import .* from '([^']+)';",code,re.M)
 check(imports==(['node:buffer']if fixture in('resource','pure')else[]))
 check('Buffer.from(['not in code)
resource=Path(refs['fixtures']['resource']['code']['path']).read_text()
check('caseId>=0&&caseId<7'in resource and "Buffer.from('c3a92201','hex')"in resource and 'i<8'in resource)
check(resource.index("export async function run")<resource.index('const pressureChecksum=pressure();'))
native=json.loads((OWN/'native-source-data.json').read_bytes());check(len(native['files'])==342 and len(native['allNineManifests'])==9)
frame=json.loads(Path(refs['actualBootstrapWholeFrame']['path']).read_bytes())
check(native['allNineManifests']==frame['selectedManifests']and frame['metadata']['engineSha256']==refs['engine']['sha256'])
check(frame['resourceSourceIndexSha256']==refs['resourceSourceIndex']['sha256']and frame['toolingIndex']==refs['toolingIndex'])
check(frame['metadata']['resourceOwnershipPolicy']['nativeRuntimeValidation']is None)
check(frame['sourceRoot']==refs['frozenSourceRoot']and frame['configuredSourceRoot']==refs['configuredSourceRoot']and frame['sourceRoot']!=frame['configuredSourceRoot'])
pack=json.loads(Path(refs['packagingMap']['path']).read_bytes());check(len(pack['files'])==4934 and len(pack['links'])==22)
for l in pack['links']:
 p=Path(pack['publicationRoot'])/l['destination'];check(p.is_symlink()and p.readlink().as_posix()==l['newLinkText']and p.resolve()==Path(pack['publicationRoot'])/l['mappedTarget'])
files={str(Path(pack['publicationRoot'])/r['path']):r for r in pack['files']}
for path in [refs['jcoEntry']['path'],str(Path(pack['packagingRoot'])/'tests/node-compat/profile-bundler.mjs'),str(Path(pack['packagingRoot'])/'tests/node-compat/toolchain.mjs'),str(Path(pack['packagingRoot'])/'tests/node-compat/componentizer.mjs')]:check(path in files)
adapter=next(r for r in pack['files']if r['path'].endswith('/preview1-adapter-release/wasi_snapshot_preview1.wasm'));check(adapter['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'and adapter['bytes']==53512)

# Actual physical packaging graph: literal local module/data paths. This is
# finite pinned-source inspection; lazy Python/helper functions are not called.
graph=[];data=[];directories=[]
for name in [r['path']for r in pack['files']if r['path'].startswith('packaging/')and r['path'].endswith('.mjs')]:
 path=Path(pack['publicationRoot'])/name;text=path.read_text()
 for match in re.finditer(r"(?:from\s*|import\s*\(|new URL\s*\()(['\"])(\.[^'\"]+)\1",text):
  spec=match[2];target=(path.parent/spec).resolve()
  if target.is_dir():
   check(spec=='../../'and str(target)==pack['packagingRoot']);directories.append(dict(source=str(path),specifier=spec,target=str(target),role='DECLARED_REPOSITORY_DIRECTORY_NOT_FILE'));continue
  check(str(target)in files)
  (graph if target.suffix=='.mjs'else data).append(dict(source=str(path),specifier=spec,target=str(target)))
selection=Path(pack['packagingRoot'])/'tests/node-compat/module-selection.mjs'
catalog=re.findall(r"export const ([A-Z_]+_MANIFEST) = '([^']+)';",selection.read_text())
check(len(catalog)==10)
for symbol,relative in catalog:
 target=Path(pack['packagingRoot'])/relative;check(str(target)in files);data.append(dict(source=str(selection),symbol=symbol,target=str(target),role='INDEXED_MANIFEST_CATALOG_DATA_NOT_AN_OLD_ENGINE_ADMISSION_CALL'))

entry=(OWN/'entry.mjs').read_text();worker=(OWN/'build-worker.mjs').read_text();parent=(OWN/'build.mjs').read_text();bundle=(OWN/'bundle.mjs').read_text()
static_specs=re.findall(r"^import .* from '([^']+)';",entry,re.M);check(all(s.startswith('node:')for s in static_specs))
first_import=entry.index('await import(pathToFileURL(source.refs.bootstrapEntry.path))')
check(entry.index("for(const r of manifest.files)await streamHash(r)")<first_import)
check(entry.index('await packagingPhysical(refs.packagingMap)')<first_import)
check(entry.index("await peer(root.sourceIndependentReview")<first_import)
check(entry.index('const fixture=authorityModel(root,sourceSha)')<first_import)
models=(OWN/'models.mjs').read_text()
for name in('fixtureModel','authorityModel'):
 start=models.index('export function '+name+'(');end=models.index('\n}',start)+2
 check(models[start:end].replace('export function ','function ',1)in entry)
check('resourceBootstrapPreflight({configDescriptor:source.refs.bootstrapConfig})'in entry)
check('isDeepStrictEqual(comparison,expected)'in entry and 'delete comparison.recheck'in entry and 'delete native.'not in entry)
check('constructionFrames.has(v)'in entry and 'workerFrames.has(v)'in entry)
check('requireConstructionFrame(frame)'in parent and 'requireWorkerFrame(frame)'in worker)
check("await mkdir(join(output.root,'processes'),{mode:0o700})"in parent)
check(parent.index('checkOwnedTerminal(outcome)')>parent.index('await runOwnedCommand('))
check('root.workerTimeoutMs'in parent and '2*1024*1024*1024'in parent and '800*1024*1024'in parent)
check('adapter:packaging.adapter'in worker and 'preview2Adapter'not in worker)
check(worker.index("componentRow=await output.write('component.wasm'")<worker.index('const emitted=await componentWit(result.component)')<worker.index('return result.component;'))
check('await selected.componentize(bundled.code,options)'in worker and 'checkInterfaces(built.interfaceAudit,d.fixture)'in worker)
check("need(threw&&!captured"in worker)
check('for(const[name,bytes]of Object.entries(generated.files))'in worker)
check('generatedModuleImported:false'in worker and 'loadingProtocolReviewRequired:true'in worker)
check("await import(pathToFileURL(jcoPath))"in worker and 'wasiShim:true'in worker)
check('nativeBufferExternal:'in bundle and 'builtinManifests:selectedManifests'in bundle)
check('virtualModuleIds:[]'in bundle and 'Unobserved virtual source refuses'in bundle)
check('selectedManifestsForEngine'not in entry+bundle+worker+parent)
check('process.env.HOME='not in entry+bundle+worker+parent and 'process.env.CODEX_HOME='not in entry+bundle+worker+parent)
for file in OWN.glob('*.mjs'):
 if file.name=='entry.mjs':continue
 for spec in re.findall(r"^import .* from '([^']+)';",file.read_text(),re.M):
  if spec.startswith('.'):
   target=(file.parent/spec).resolve();check(target.is_file())
   check(target.is_relative_to(OWN)or str(target)in {r['path']for r in manifest['files']})
future=json.loads((OWN/'future-root-authority.template.json').read_bytes())
for name in('state','sourceIndexSha256','phase','fixture','outputRoot','sourceIndependentReview','bootstrapConfig','bootstrapRootObservation','reviewedPins','rootPinReview'):check(future[name]is None)
for name in('componentConstructionAllowed','nativeBuildAllowed','nativeFreezeAllowed','ordinaryExportsAllowed','timerRuntimeAllowed','guestLoadingAllowed','hostRequestsAllowed','gcAllowed','keyOrCryptoAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed'):check(future[name]is False)
for fixture in refs['fixtures']:check(not Path('/private/tmp/starling-node-compat/scheduler-resource-component-v1-'+fixture).exists())
asts=[]
for p in OWN.glob('*.py'):ast.parse(p.read_bytes());asts.append(p.name)
result=dict(schemaVersion=1,state='RESOURCE342_COMPONENT_SOURCE_DATA_CHECKS_PASSED_V1',checks=checks,preparationRows=len(manifest['files']),nativeSources=342,selectedManifests=9,packagingAndToolFiles=4934,toolLinks=22,exactFixtureCopies=5,exactScalarWitLiteral=1,packagingLocalModuleEdges=graph,packagingLiteralDataEdges=data,packagingDirectoryEdges=directories,pythonAst=asts,ownerHelperOrBootstrapOrPackagingOrGuestInvoked=False,sourceOnly=True)
with(OWN/'source-check-results.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in result.items()if k not in('packagingLocalModuleEdges','packagingLiteralDataEdges')}))
