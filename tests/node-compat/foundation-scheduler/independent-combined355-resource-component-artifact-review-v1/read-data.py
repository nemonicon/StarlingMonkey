"""Independent bounded SOURCE/DATA intake, no operational imports or calls."""
from pathlib import Path
import ast,hashlib,json,os,re,stat,subprocess,time
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-native-component-caller-candidate-v1'
EXPECTED='aec12b5c21995f1f080871be2d8fa77ee5aa20fe884e220dd94db7d6573993f1'
rows={};identities={};families={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def digest(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def descriptor(path):return dict(path=str(path),sha256=digest(path),bytes=path.stat().st_size)
def key(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_nlink,s.st_mtime_ns,s.st_ctime_ns)
def checked(r):
 need(type(r)is dict and type(r['path'])is str and Path(r['path']).is_absolute(),'absolute descriptor')
 p=Path(r['path']);s=p.lstat();need(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'regular exact file')
 if str(p)in rows:
  need(rows[str(p)]==r and identities[str(p)]==key(s),'same descriptor/identity');return p
 need(digest(p)==r['sha256']and key(s)==key(p.lstat()),'full stable SHA '+str(p))
 rows[str(p)]=r;identities[str(p)]=key(s);return p
def read(r):return json.loads(checked(r).read_bytes())
def family(ix):
 if ix['path']in families:need(families[ix['path']]==ix,'same family');return
 v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique member')
  names.add(n);checked(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
 paths=list(root.rglob('*'));need(not any(p.is_symlink()for p in paths),'no family symlinks')
 need({p.relative_to(root).as_posix()for p in paths if p.is_file()}==names,'exact whole indexed family')
 families[ix['path']]=ix

CAPS=['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10']
root_result=OWN.parent/'combined-native-component-v1-construct-resource-root-results.json'
need(descriptor(root_result)['sha256']=='6683a3ec6b7cd67c9392e6fa0a60182dc4839fb8d99906ef3c68f3b6f9c1317e','actual Root handoff')
root=read(descriptor(root_result));bundle_root=read(descriptor(OWN.parent/'combined-native-component-v1-bundle-resource-root-results.json'))
ix=descriptor(SOURCE/'index.json');need(ix['sha256']==EXPECTED,'original caller source');family(ix)
source_inputs=json.loads((SOURCE/'source-inputs.json').read_bytes());refs=json.loads((SOURCE/'references.json').read_bytes())
for r in source_inputs['files']:checked(r)
for r in source_inputs['families']:family(r)
for boundary in source_inputs['boundaries']:
 b=read(boundary['manifest']);need(len(b[boundary['field']])==boundary['expectedRows'],'declared current rows')
 for r in b[boundary['field']]:checked(r)
 for r in b.get(boundary['familyField'],[]):family(r)
package=read(refs['packageInventory'])['package'];base=Path(package['root']);names=set();links={r['path']:r for r in package['links']}
need(len(package['files'])==4889 and len(links)==21 and stat.S_IMODE(base.lstat().st_mode)==0o700,'reviewed private package')
for r in package['files']:
 checked({k:r[k]for k in ['path','sha256','bytes']});p=Path(r['path']);need(p==base/r['relativePath']and stat.S_IMODE(p.lstat().st_mode)==r['mode']and p.lstat().st_nlink==1,'package mode/window');names.add(r['relativePath'])
found=set()
for p in base.rglob('*'):
 n=p.relative_to(base).as_posix()
 if p.is_symlink():
  r=links[n];need(os.readlink(p)==r['target']and str(p.resolve(strict=True))==r['resolvedPath']and p.resolve(strict=True).is_relative_to(base),'private alias');found.add(n)
 elif p.is_file():need(n in names,'package member');found.add(n)
need(found==names|set(links),'whole package member set')
def direct_roles(v):
 if type(v)is dict:
  if set(v)=={'path','sha256','bytes'}:checked(v)
  else:
   for x in v.values():direct_roles(x)
 elif type(v)is list:
  for x in v:direct_roles(x)
direct_roles(root);direct_roles(bundle_root)
def publication(ix,completion):
 v=read(ix);base=Path(ix['path']).parent;expected={'index.json','completion.json'}
 for r in v['files']:
  need(r['path']not in expected,'unique producer member');expected.add(r['path']);checked(dict(r,path=str(base/r['path'])))
 for p in base.rglob('*'):
  need(not p.is_symlink(),'private publication has no aliases')
  if p.is_file():need(stat.S_IMODE(p.lstat().st_mode)==0o600 and p.lstat().st_nlink==1,'private single-link output')
 need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==expected,'whole output membership')
 c=read(completion);need(c['state']=='COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED'and c['index']=={**ix,'path':'index.json'},'exact completion publication role')
 checked(dict(c['result'],path=str(base/c['result']['path'])))
 return base,v
construct_base,cindex=publication(root['constructionIndex'],root['constructionCompletion'])
bundle_base,bindex=publication(bundle_root['actualIndex'],bundle_root['actualCompletion'])
constructed=read(root['constructionResult']);bundled=read(root['bundleReport'])
need(root['toolObservation']['sessionId'] is None and 'lost during context compaction' in root['toolObservation']['qualification'],'preserved missing Root tool response; do not reconstruct')
need(bundle_root['toolObservation']['rawExitCode']==0,'observed bundle Root tool exit')
need(constructed['state']=='COMBINED355_COMPONENT_COMPLETE_UNREVIEWED_V1'and bundled['state']=='COMBINED355_BUNDLE_COMPLETE_UNREVIEWED_V1','separate construction/bundle results')
for value in [constructed,bundled]:
 need(value['fixtureId']=='resource'and value['sourceIndex']==ix and value['primaryPresent']is False and value['primary']is None and value['finalProtectionErrors']==[],'clean per-pure phase')
 need(value['nativeSourceFiles']==355 and value['externalEmbeddingSources']==3 and value['fullMetadataFields']==80 and value['selectedWholeManifests']==11,'new combined context')
 for k in ['ordinaryGuestExportsInvoked','generatedApplicationModuleImported','keyOrCryptoWorkloadsInvoked','operationalAdmission','runtimeAcceptanceClaim']:need(value[k]is False,'limited phase '+k)
metadata=read(refs['nativeMetadata']);expected_data=read(refs['actualReadOnlyData'])
native_records=[]
for base in [bundle_base,construct_base]:
 data=json.loads((base/'native-record-data.json').read_bytes());native_records.append(data)
 need(data==expected_data and data['bootstrap']['metadata']==metadata,'whole original full retained record')
 need(list(data)==['schemaVersion','kind','sourceIndex','actualReview','bootstrap','currentVerification'],'six complete DATA fields')
 shape=json.loads((base/'native-record-shape.json').read_bytes());need(list(shape)==list(data)+['recheck']and shape['recheck']==dict(type='function',writable=False,configurable=False,enumerable=True),'own callable-shape not reused serialized callable')
 for k in ['helperInvocations','processesSpawned','filesCreated']:need(data['currentVerification'][k]==0,'read-only current '+k)
 selected=json.loads((base/'selected-whole-manifests.json').read_bytes());need(selected==data['bootstrap']['selectedManifests']and len(selected)==11,'all eleven whole manifests')
 for row,m in zip(metadata['selectedModuleManifests'],selected):
  p=Path(data['bootstrap']['sourceRoot'])/row['path'];need(descriptor(p)['sha256']==row['sha256']and json.loads(p.read_bytes())==m,'actual frozen manifest')
need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3,'full metadata count')
cr=read(root['constructionRootAuthority']);cc=read(root['constructionConfig']);lr=read(root['pairedLoaderRootAuthority']);lc=read(root['pairedLoaderConfig']);br=read(bundle_root['rootAuthority']);bc=read(bundle_root['config'])
for auth,phase in [(cr,'construct'),(br,'bundle')]:
 need(auth['phase']==phase and auth['fixtureId']=='resource'and auth['sourceIndex']==ix and auth['nativeEngine']==refs['nativeEngine']and auth['nativeMetadata']==refs['nativeMetadata'],'actual phase Root')
 family(auth['sourceIndependentReview']['index']);p=read(auth['sourceIndependentReview']['result']);need(p['state']=='INDEPENDENT_COMBINED355_COMPONENT_CALLER_SOURCE_REVIEW_PASSED_V1'and p['componentSourceIndexSha256']==EXPECTED,'Source peer')
 need(sorted(auth['selectedInterfaces'])==CAPS and auth['ordinaryGuestExportsAllowed']is False and auth['generatedModuleImportAllowed']is False,'three exact selected interfaces and no runtime authority')
need(cc['rootAuthority']==root['constructionRootAuthority']and bc['rootAuthority']==bundle_root['rootAuthority']and lc['rootAuthority']==root['pairedLoaderRootAuthority'],'actual configs')
need(cr['bundleReport']==root['bundleReport']and cr['bundle']==root['bundle']and cr['bundleExternalTerminal']==root['bundleExternalTerminal'],'separate actual bundle selected')
for k in ['nativeEngine','nativeMetadata','guestSourceSha256','witWorldSha256','worldName','selectedInterfaces','disableFeatures','privateTemporaryRoot']:need(cr[k]==lr[k],'paired loader role '+k)
need(cr['guestSourceSha256']==root['bundle']['sha256']and lr['sourceIndex']==refs['loaderSourceIndex'],'bundle pinned before loader')
bundle_return=read(bundled['bundleReturn']);need(bundle_return['code'].encode()==Path(root['bundle']['path']).read_bytes()and bundle_return['imports']==['node:buffer'],'whole bundle code and native residual')
need(bundle_return['moduleIds']==[constructed['fixtureSource']['path']]and bundled['allElevenManifestsUsed']is True and bundled['fixtureEvaluated']is False and bundled['packagerLoaded']is False,'one source only/full11/no evaluation')
for base in [bundle_base,construct_base]:need((base/'bundle.mjs').read_bytes()==Path(root['bundle']['path']).read_bytes(),'bundle copies byte exact')
def terminal(row,auth):
 t=read(row);need(t['authority']==auth and type(t['rawExitCode'])is int and t['rawExitCode']==0,'actual raw0 authority')
 for k in ['timeout','forcedCleanup']:need(t[k]is False,'clean '+k)
 for k in ['parentOwnedGroupGone','allObservedOwnedGroupsGone']:need(t[k]is True,'clean '+k)
 for k in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[k]==[],'clean '+k)
 need(all(g['alive']is False for g in t['finalGroups']),'no remaining observed groups')
 checked(t['stdout']);checked(t['stderr']);need(t['stderr']['bytes']==0,'raw empty stderr')
 return t
phase_processes={}
for phase,inner_row,outer_row,auth in [('bundle',root['bundleExternalTerminal'],bundle_root['outerTerminal'],bundle_root['rootAuthority']),('construct',root['constructionExternalTerminal'],root['outerTerminal'],root['constructionRootAuthority'])]:
 inner=terminal(inner_row,auth);outer=terminal(outer_row,auth);lines=[json.loads(s)for s in Path(outer['stdout']['path']).read_text().splitlines()]
 need(len(lines)==2 and lines[0]['pid']==inner['pid']and lines[0]['timeoutSeconds']==(1200 if phase=='bundle'else 2400),'original parent launch prefix')
 need(lines[1]['terminal']==inner_row and lines[1]['rawExitCode']==0 and lines[1]['phase']==phase,'parent final envelope')
 value=json.loads(Path(inner['stdout']['path']).read_text());base=bundle_base if phase=='bundle'else construct_base
 need(value['completeUnreviewed']is True and value['root']==str(base)and value['index']==descriptor(base/'index.json')and value['completion']==descriptor(base/'completion.json')and value['result']==descriptor(base/'result.json'),'inner complete publication')
 need(outer['pid']!=inner['pid']and any(p['pid']==inner['pid']for p in outer['observedProcesses']),'observed genuine separate owned Node')
 phase_processes[phase]={'parentPid':outer['pid'],'nodePid':inner['pid'],'innerObserved':inner['observedProcesses'],'outerObservedRows':len(outer['observedProcesses']),'innerTerminal':inner_row,'outerTerminal':outer_row}
need(phase_processes['bundle']['nodePid']!=phase_processes['construct']['nodePid'],'fresh construction Node')
need(constructed['component']==root['component']and constructed['emittedImports']==CAPS and constructed['guestInitializationExecuted']is True,'actual construction artifact/no ordinary invocation')
wit=Path(root['emittedWit']['path']).read_text()
need(sorted(re.findall(r'import ([^;]+);',wit))==CAPS,'exact three standard imports in full WIT')
need(re.findall(r'export ([a-z]+): func\(([^)]*)\) -> string;',wit)==[('inspect',''),('run','case-id: u32'),('validate','')],'exact three string scalar WIT signatures')
transpile=read(root['transpileMetadata']);need(transpile['imports']==[x.split('@')[0]for x in CAPS]and transpile['exports']==[['inspect','function'],['run','function'],['validate','function']],'Jco ABI metadata')
dts=Path(root['allGeneratedFiles'][1]['path']).read_text();need('export function inspect(): string;'in dts and 'export function run(caseId: number): string;'in dts and 'export function validate(): string;'in dts,'d.ts three scalar signatures')
need(Path(next(r['path']for r in root['allGeneratedFiles']if r['path'].endswith('/package.json'))).read_bytes()==b'{"type":"module"}\n','exact ESM package')
# Authenticate a previously inspected metadata-only decoder before its inert
# import. Its __main__ path never runs; graph() reads only the supplied binary.
parser=OWN.parent.parent/'foundation-crypto/independent-ownership-secret-component-v2-results-review-v1/binary-graph.py'
parser_ix=parser.parent/'index.json';need(descriptor(parser_ix)['sha256']=='28bc2f472ae5422dc92386a7f496b26cd3919602cde15b7a01e04d78ab6b0c29','bounded parser source family pin')
pr=next(r for r in json.loads(parser_ix.read_bytes())['files']if r['path']=='binary-graph.py');checked(dict(pr,path=str(parser)))
import importlib.util
spec=importlib.util.spec_from_file_location('independent_pure_component_metadata_decoder',parser);decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
g=decoder.graph(root['component']['path'])
need(sorted(i['name']for i in g['rootImports'])==CAPS,'fresh exact binary root imports')
need([e['name']for e in g['exports']]==['inspect','run','validate']and all(e['sort']==[1]for e in g['exports']),'three actual root function exports')
signatures=[]
for export in g['exports']:
 f=g['componentFunctions'][export['index']];t=g['componentTypes'][f['typeIndex']]
 need(f['kind']=='lift'and t['kind']=='function'and t['results']==[-13],'binary canonical string result')
 need(t['params']==([{'name':'case-id','type':-7}]if export['name']=='run'else []),'binary zero or u32 parameter')
 signatures.append({'name':export['name'],'params':t['params'],'results':t['results']})
functions={i['name']:i['functions']for i in g['rootImports']}
need(functions[CAPS[0]]==['now','subscribe-instant','subscribe-duration']and functions[CAPS[1]]==['now']and functions[CAPS[2]]==['poll'],'five actual imported functions, no type-only clock substitution')
core_path=Path(root['allGeneratedFiles'][0]['path']);cg=decoder.core(core_path.read_bytes(),{'role':'physical-generated-core'});need(len(g['modules'])==4,'one physical plus three inline cores')
semantic=lambda m:[(x['id'],x['bytes'],x['sha256'])for x in m['sections']if x['id']!=0]
need(semantic(cg)==semantic(g['modules'][0]),'main noncustom core sections exactly match')
(OWN/'binary-type-core-graph.json').write_text(json.dumps(g,indent=2)+'\n')
graph={'schemaVersion':1,'component':root['component'],'rootImports':g['rootImports'],'exports':g['exports'],'functionSignatures':signatures,
 'componentSections':g['componentSections'],'nestedCores':[{k:m[k]for k in ['moduleSha256','moduleBytes','imports','customSections','sections']}for m in g['modules']],
 'physicalCore':root['allGeneratedFiles'][0],'physicalCoreCustomSections':cg['customSections'],'wholeCoreByteEqual':cg['moduleSha256']==g['modules'][0]['moduleSha256'],
 'allNoncustomCoreSectionsByteEqual':True,'compiledOrInstantiatedByReviewer':False,'decoderSource':descriptor(parser),'decoderSourceIndex':descriptor(parser_ix)}
(OWN/'binary-graph.json').write_text(json.dumps(graph,indent=2)+'\n')
for p,i in identities.items():need(key(Path(p).lstat())==i,'final current intake identity')
summary={'schemaVersion':1,'state':'RESOURCE_ARTIFACT_READ_ONLY_INTAKE_PASSED','checks':checks,'currentFullHashFiles':len(rows),'currentLogicalBytes':sum(r['bytes']for r in rows.values()),'currentFamilies':len(families),
 'bundleIndexedFiles':len(bindex['files']),'bundleActualFiles':len(bindex['files'])+2,'constructionIndexedFiles':len(cindex['files']),'constructionActualFiles':len(cindex['files'])+2,
 'processes':phase_processes,'rootResult':descriptor(root_result),'bundleRootResult':descriptor(OWN.parent/'combined-native-component-v1-bundle-resource-root-results.json'),
 'sourceIndex':ix,'artifacts':{k:root[k]for k in ['bundle','bundleReport','bundleExternalTerminal','constructionRootAuthority','constructionConfig','pairedLoaderRootAuthority','pairedLoaderConfig','constructionResult','constructionIndex','constructionCompletion','constructionExternalTerminal','outerTerminal','component','emittedWit','interfaceAudit','transpileMetadata','allGeneratedFiles']},
 'fixtureSource':constructed['fixtureSource'],'fixtureWit':constructed['fixtureWit'],'actualNativeBootstrapReview':refs['actualBootstrapReview'],'actualRetainedReadOnlyReview':refs['actualReadOnlyReview'],
 'metadata':refs['nativeMetadata'],'engine':refs['nativeEngine'],'freezeReceipt':refs['freezeReceipt'],'nativeMetadataFields':80,'nativeSourceFiles':355,'externalEmbeddingSources':3,'selectedWholeManifests':11,
 'actualTimeProtectionQualification':'Source-coupled successful guards/raw0 plus current full intake; no per-read trace claimed','reviewerOperationalActionsInvoked':False}
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k]for k in ['state','checks','currentFullHashFiles','currentLogicalBytes','currentFamilies','bundleIndexedFiles','constructionIndexedFiles']}))
