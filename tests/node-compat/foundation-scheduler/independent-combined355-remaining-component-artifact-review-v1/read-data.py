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
# Fixed observed Root handoff, not inferred from directory presence.
ROOT_PINS={'clock-snapshot':'f76242ed0aa976dd2b08075fc65d10b300a4e0b607728f2a93504bbdc2dfc80d','surviving-interest':'54c653ef8abf3a5a5f449c481e9aca6bdbce6ae243dab1104121ec993e2ec628','fatal':'70e6f480f91a5a057f3cf0ebcf16bb1c46a79908bff6fc47a1b12d604b0322bb','init-fatal':'9952df0f1c9e65cb1a77c2d68c966919106f8d3a5c3e376a953b4b4495441091'}
metadata=read(refs['nativeMetadata']);expected_data=read(refs['actualReadOnlyData']);catalogue=read(refs['fixtureCatalogue'])
need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3,'new genuine 80/355+3 metadata')
fixtures={r['id']:r for r in catalogue['fixtures']};need(set(fixtures)=={'pure','resource',*ROOT_PINS},'exact six fixture Source catalogue')
for proofkey,contractkey,state in [('actualBootstrapReview','actualBootstrapContract','INDEPENDENT_COMBINED355_NATIVE_BOOTSTRAP_REVIEW_PASSED_V1'),('actualReadOnlyReview','actualReadOnlyContract','INDEPENDENT_COMBINED355_RETAINED_READ_ONLY_REVIEW_PASSED_V1')]:
 proof=refs[proofkey];family(proof['index']);pv=read(proof['result']);cv=read(refs[contractkey]);need(pv['verifiedPassed']is True and pv['state']==cv['requiredReviewState'],'genuine actual native proof state/contract')
 for k,v in cv['requiredFixedValues'].items():need(pv[k]==v,'actual native proof fixed field '+k)
need(expected_data['bootstrap']['metadata']==metadata and len(expected_data['bootstrap']['selectedManifests'])==11,'all raw metadata/whole manifests unchanged')
for row,m in zip(metadata['selectedModuleManifests'],expected_data['bootstrap']['selectedManifests']):
 p=Path(expected_data['bootstrap']['sourceRoot'])/row['path'];checked(dict(path=str(p),sha256=row['sha256'],bytes=p.stat().st_size));need(json.loads(p.read_bytes())==m,'full actual eleven manifest bytes')
# Refer to previous accepted reviews by exact family, never copy history trees.
prior={}
for case,sha in [('pure','0dc8bf11f2cc5d153a7a062131784af84cb3e5f63eddfe26b97437461cd70c2c'),('resource','ce6fb73141c11ed2acd5c1e088dadb53d9428f88a7e5a4a1af19bdd7855b05a0')]:
 base=OWN.parent/f'independent-combined355-{case}-component-artifact-review-v1';rix=descriptor(base/'index.json');need(rix['sha256']==sha,'prior actual per-fixture Source pin');family(rix)
 result=descriptor(base/'results.json');contract=descriptor(base/'result-contract.json');v=read(result);c=read(contract);need(v['state']==c['requiredReviewState'],'prior contract state')
 for k,x in c['requiredFixedValues'].items():need(v[k]==x,'prior exact fixed value '+k)
 need(v['artifacts']==c['artifacts'] and v['generatedFiles']==c['generatedFiles'],'prior artifact maps')
 direct_roles(v['artifacts']);direct_roles(v['generatedFiles']);need(v['artifacts']['fixtureSource']==fixtures[case]['source']and v['artifacts']['fixtureWit']==fixtures[case]['wit'],'prior exact fixtureSource')
 prior[case]=dict(index=rix,result=result,contract=contract)

def publication(ix,completion,failed=False):
 v=read(ix);base=Path(ix['path']).parent;expected={'index.json','completion.json'};dirs={'.':key(base.lstat())}
 need(stat.S_IMODE(base.lstat().st_mode)==0o700,'private publication root')
 for r in v['files']:
  n=r['path'];need(type(n)is str and n not in expected and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique confined producer member')
  expected.add(n);checked(dict(r,path=str(base/n)))
 for p in base.rglob('*'):
  st=p.lstat();need(not p.is_symlink(),'publication no links')
  if p.is_file():need(stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1,'private single-link output')
  elif p.is_dir():need(stat.S_IMODE(st.st_mode)==0o700,'private output dir');dirs[p.relative_to(base).as_posix()]=key(st)
  else:need(False,'ordinary outputs only')
 need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==expected,'whole producer output membership incl nested indices')
 c=read(completion);need(c['state']==('FAILED_UNACCEPTED'if failed else'COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED')and c['index']==dict(ix,path='index.json'),'unaltered completion state and index role')
 checked(dict(c['result'],path=str(base/c['result']['path'])))
 publications.append((base,expected,dirs));return base,v

def terminal(row,auth,exitcode):
 t=read(row);need(t['authority']==auth and type(t['rawExitCode'])is int and t['rawExitCode']==exitcode,'actual terminal exit and authority')
 for k in ['timeout','forcedCleanup']:need(t[k]is False,'no '+k)
 for k in ['parentOwnedGroupGone','allObservedOwnedGroupsGone']:need(t[k]is True,'clean '+k)
 for k in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[k]==[],'no cleanup '+k)
 need(all(g['alive']is False for g in t['finalGroups']),'all final observed groups gone');checked(t['stdout']);checked(t['stderr']);return t

def native_data(base):
 data=json.loads((base/'native-record-data.json').read_bytes());shape=json.loads((base/'native-record-shape.json').read_bytes())
 need(data==expected_data and list(data)==['schemaVersion','kind','sourceIndex','actualReview','bootstrap','currentVerification'],'full genuine unchanged six DATA fields')
 need(list(shape)==list(data)+['recheck']and shape['recheck']==dict(type='function',writable=False,configurable=False,enumerable=True),'real retained API own callable descriptor')
 need(all(data['currentVerification'][k]==0 for k in ['helperInvocations','processesSpawned','filesCreated']),'current read-only API no helper/process/write')
 need(json.loads((base/'selected-whole-manifests.json').read_bytes())==expected_data['bootstrap']['selectedManifests'],'all whole eleven manifests retained')

def raw_copy(case,phase,base,report,inner,outer):
 chosen={base/r['path'] for r in json.loads((base/'index.json').read_text())['files']if r['bytes']<=200000 and r['path']!='selected-whole-manifests.json'}
 chosen|={base/'index.json',base/'completion.json',Path(report),Path(inner['stdout']['path']),Path(inner['stderr']['path']),Path(outer['stdout']['path']),Path(outer['stderr']['path'])}
 chosen|={Path(v['path'])for k,v in json.loads(Path(report).read_text()).items()if type(v)is dict and set(v)=={'path','sha256','bytes'}and k in ['rootAuthority','config','invocation','externalTerminal','outerTerminal','pairedLoaderRootAuthority','pairedLoaderConfig']}
 for p in sorted(chosen):
  # Small actual raw text only, no recursive history or large frame/binary copy.
  if p.suffix=='.wasm' or p.stat().st_size>200000:continue
  checked(descriptor(p));anchor=base if p.is_relative_to(base)else p.parent
  label=('publication/'+p.relative_to(base).as_posix())if p.is_relative_to(base)else ('external/'+p.parent.name+'/'+p.name)
  dest=OWN/'raw'/case/phase/label;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());need(descriptor(dest)['sha256']==descriptor(p)['sha256'],'exact finite raw text copy')
  copies.append(dict(original=descriptor(p),copy=descriptor(dest)))

publications=[];copies=[];outcomes={}
for case,pin in ROOT_PINS.items():
 out=OWN/case;out.mkdir(exist_ok=True);rp=OWN.parent/f'combined-native-component-v1-construct-{case}-root-results.json';brp=OWN.parent/f'combined-native-component-v1-bundle-{case}-root-results.json';need(descriptor(rp)['sha256']==pin,'exact observed Root handoff')
 root=read(descriptor(rp));bundle_root=read(descriptor(brp));direct_roles(root);direct_roles(bundle_root)
 failed=case=='init-fatal';exitcode=int(failed)
 need(root['toolObservation']==dict(sessionId={'clock-snapshot':26228,'surviving-interest':86269,'fatal':37335,'init-fatal':26507}[case],rawExitCode=exitcode),'retained Root tool observation')
 need(bundle_root['toolObservation']['rawExitCode']==0,'bundle Root tool raw0')
 cb,ci=publication(root['phaseIndex'],root['phaseCompletion'],failed);bb,bi=publication(bundle_root['phaseIndex'],bundle_root['phaseCompletion'])
 constructed=read(root['phaseResult']);bundled=read(root['bundleReport'])
 need(constructed['state']==('COMBINED355_CALLER_PHASE_FAILED_UNACCEPTED_V1'if failed else'COMBINED355_COMPONENT_COMPLETE_UNREVIEWED_V1')and bundled['state']=='COMBINED355_BUNDLE_COMPLETE_UNREVIEWED_V1','separate true phase states')
 for value in [constructed,bundled]:
  need(value['fixtureId']==case and value['sourceIndex']==ix and value['primaryPresent']is(value is constructed and failed)and value['finalProtectionErrors']==[],'actual phase final error/protection state')
  if not(value is constructed and failed):need(value['primary']is None,'no primary on successful actual phase')
  for k,n in [('nativeSourceFiles',355),('externalEmbeddingSources',3),('fullMetadataFields',80),('selectedWholeManifests',11)]:need(value[k]==n,'actual new context '+k)
  for k in ['ordinaryGuestExportsInvoked','generatedApplicationModuleImported','keyOrCryptoWorkloadsInvoked','operationalAdmission','runtimeAcceptanceClaim']:need(value[k]is False,'construction scope '+k)
 need(constructed['fixtureSource']==fixtures[case]['source']and constructed['fixtureWit']==fixtures[case]['wit'],'exact unchanged lifecycle fixture')
 for b in [cb,bb]:native_data(b);need((b/'bundle.mjs').read_bytes()==Path(root['bundle']['path']).read_bytes(),'same bundle bytes in both phases')
 cr=read(root['rootAuthority']);cc=read(root['config']);lr=read(root['pairedLoaderRootAuthority']);lc=read(root['pairedLoaderConfig']);br=read(bundle_root['rootAuthority']);bc=read(bundle_root['config'])
 for auth,phase in [(cr,'construct'),(br,'bundle')]:
  need(auth['phase']==phase and auth['fixtureId']==case and auth['sourceIndex']==ix and auth['nativeEngine']==refs['nativeEngine']and auth['nativeMetadata']==refs['nativeMetadata'],'actual context/phase Root')
  family(auth['sourceIndependentReview']['index']);peer=read(auth['sourceIndependentReview']['result']);need(peer['state']=='INDEPENDENT_COMBINED355_COMPONENT_CALLER_SOURCE_REVIEW_PASSED_V1'and peer['componentSourceIndexSha256']==EXPECTED,'actual caller Source peer')
  need(sorted(auth['selectedInterfaces'])==CAPS and auth['ordinaryGuestExportsAllowed']is False and auth['generatedModuleImportAllowed']is False,'literal three-interface construction authority; no runtime')
 need(cc['rootAuthority']==root['rootAuthority']and bc['rootAuthority']==bundle_root['rootAuthority']and lc['rootAuthority']==root['pairedLoaderRootAuthority'],'original actual config roles')
 need(cr['bundleReport']==root['bundleReport']and cr['bundle']==root['bundle']and cr['bundleExternalTerminal']==root['bundleExternalTerminal'],'separate actual bundle input')
 for k in ['nativeEngine','nativeMetadata','guestSourceSha256','witWorldSha256','worldName','selectedInterfaces','disableFeatures','privateTemporaryRoot']:need(cr[k]==lr[k],'paired pre-load authority '+k)
 need(cr['guestSourceSha256']==root['bundle']['sha256']and lr['sourceIndex']==refs['loaderSourceIndex'],'actual bundle SHA fixed before loader')
 bv=read(bundled['bundleReturn']);need(bv['code'].encode()==Path(root['bundle']['path']).read_bytes()and bv['imports']==fixtures[case]['expectedNativeResidualImports'],'full actual bundle/native residual')
 need(bv['moduleIds']==[fixtures[case]['source']['path']]and bundled['allElevenManifestsUsed']is True and bundled['fixtureEvaluated']is False and bundled['packagerLoaded']is False,'one literal source/full11/no evaluation')
 process={}
 for phase,ir,orr,auth,base,ec,report in [('bundle',root['bundleExternalTerminal'],bundle_root['outerTerminal'],bundle_root['rootAuthority'],bb,0,brp),('construct',root['externalTerminal'],root['outerTerminal'],root['rootAuthority'],cb,exitcode,rp)]:
  inner=terminal(ir,auth,ec);outer=terminal(orr,auth,ec);need(inner['stderr']['bytes']==0,'inner retained stderr empty')
  if ec==0:need(outer['stderr']['bytes']==0,'successful outer retained stderr empty')
  lines=[json.loads(s)for s in Path(outer['stdout']['path']).read_text().splitlines()];need(len(lines)==2 and lines[0]['pid']==inner['pid']and lines[0]['timeoutSeconds']==(1200 if phase=='bundle'else 2400),'original two-record owned parent JSONL')
  need(lines[1]['terminal']==ir and lines[1]['rawExitCode']==ec and lines[1]['phase']==phase,'actual parent final envelope/raw exit')
  v=json.loads(Path(inner['stdout']['path']).read_text());need(v['completeUnreviewed']is(not ec)and v['root']==str(base)and v['index']==descriptor(base/'index.json')and v['completion']==descriptor(base/'completion.json')and v['result']==descriptor(base/'result.json'),'inner true publication descriptor and completeness role')
  need(outer['pid']!=inner['pid']and any(p['pid']==inner['pid']for p in outer['observedProcesses']),'separate observed Node child')
  process[phase]=dict(parentPid=outer['pid'],nodePid=inner['pid'],innerTerminal=ir,outerTerminal=orr,rawExitCode=ec,innerObserved=inner['observedProcesses'],outerObservedRows=len(outer['observedProcesses']))
  raw_copy(case,phase,base,report,inner,outer)
 need(process['bundle']['nodePid']!=process['construct']['nodePid'],'fresh single-use construction Node')
 artifact={k:root[k]for k in ['bundle','bundleReport','bundleExternalTerminal','pairedLoaderRootAuthority','pairedLoaderConfig','outerTerminal']}
 artifact.update(constructionRootAuthority=root['rootAuthority'],constructionConfig=root['config'],constructionResult=root['phaseResult'],constructionIndex=root['phaseIndex'],constructionCompletion=root['phaseCompletion'],constructionExternalTerminal=root['externalTerminal'],fixtureSource=constructed['fixtureSource'],fixtureWit=constructed['fixtureWit'],actualNativeBootstrapReview=refs['actualBootstrapReview'],actualRetainedReadOnlyReview=refs['actualReadOnlyReview'],rootResult=descriptor(rp),bundleRootResult=descriptor(brp),nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],freezeReceipt=refs['freezeReceipt'])
 if failed:
  need(constructed['component']is None and constructed['componentizationAttempted']is True and constructed['componentBytesReturned']is False and constructed['noUnavailableBytesClaimed']is True,'no accepted/init component or unavailable-byte claim')
  need(root['component']is None and root['allGeneratedFiles']==[] and not any(p.suffix=='.wasm'for p in cb.rglob('*'))and not(cb/'transpiled').exists(),'no actual component/glue/core emitted')
  msg=constructed['primary']['ownData']['message'];need(constructed['primary']==root['failure'],'full actual captured primary identity DATA')
  need('TypeError: setTimeout can only be used during request handling, not during initialization'in msg and 'source.js:2:11'in msg and 'Failed to initialize component (wizer ('in msg,'exact identified Wizer INIT timer refusal')
  need(b'setTimeout'in Path(constructed['fixtureSource']['path']).read_bytes(),'literal init timer fixture')
  outer_stderr=Path(read(root['outerTerminal'])['stderr']['path']).read_text();need('clean_terminal(terminal)'in outer_stderr and 'rawExitCode' in outer_stderr and outer_stderr.endswith('AssertionError\n'),'outer caller retains its raw-zero cleanup assertion; target diagnostic is in full failed result')
  classify=OWN.parent/'combined-native-component-v1-init-fatal-root-classification.json';need(descriptor(classify)['sha256']=='37d04b3411e00ae80353f78f1d2d3acc72111bd6a024c65d39ce66d35103f552','actual Root classification pin')
  classification=read(descriptor(classify));need(classification['rootObservation']==descriptor(rp)and classification['phaseResult']==root['phaseResult']and classification['observedDiagnostic']==msg and classification['acceptedComponent']is False and classification['noComponentReturned']is True,'Root diagnostic classification matches actual whole failure');artifact['rootClassification']=descriptor(classify)
  outcomes[case]=dict(acceptedComponent=False,identifiedExpectedRefusal=True,rawExitCode=1,component=None,artifacts=artifact,diagnostic=constructed['primary'],processes=process,bundleIndexedFiles=len(bi['files']),constructionIndexedFiles=len(ci['files']))
 else:
  need(constructed['component']==root['component']and constructed['emittedImports']==CAPS and constructed['guestInitializationExecuted']is True,'literal actual successful artifact/init not ordinarycall')
  artifact.update({k:root[k]for k in ['component','emittedWit','interfaceAudit','transpileMetadata','allGeneratedFiles']})
  wit=Path(root['emittedWit']['path']).read_text();need(sorted(re.findall(r'import ([^;]+);',wit))==CAPS and re.findall(r'export ([a-z]+): func\(([^)]*)\) -> string;',wit)==[('run','')],'full WIT exact3 and scalar run0')
  tv=read(root['transpileMetadata']);need(tv['imports']==[x.split('@')[0]for x in CAPS]and tv['exports']==[['run','function']],'actual Jco metadata exact ABI')
  need(Path(next(r['path']for r in root['allGeneratedFiles']if r['path'].endswith('.d.ts')and '/interfaces/'not in r['path'])).read_text().endswith('export function run(): string;\n'),'actual d.ts scalar run0')
  need(Path(next(r['path']for r in root['allGeneratedFiles']if r['path'].endswith('/package.json'))).read_bytes()==b'{"type":"module"}\n','literal ESM package')
  outcomes[case]=dict(acceptedComponent=True,rawExitCode=0,artifacts=artifact,processes=process,bundleIndexedFiles=len(bi['files']),constructionIndexedFiles=len(ci['files']))

# Only an authenticated inert binary metadata decoder is imported. It never
# compiles/evaluates/instantiates bytes. Its operational __main__ is not invoked.
parser=OWN.parent.parent/'foundation-crypto/independent-ownership-secret-component-v2-results-review-v1/binary-graph.py';pix=descriptor(parser.parent/'index.json');need(pix['sha256']=='28bc2f472ae5422dc92386a7f496b26cd3919602cde15b7a01e04d78ab6b0c29','known metadata decoder index')
pr=next(r for r in read(pix)['files']if r['path']=='binary-graph.py');checked(dict(pr,path=str(parser)))
import importlib.util
spec=importlib.util.spec_from_file_location('combined_remaining_metadata_decoder',parser);decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
for case,ov in outcomes.items():
 if not ov['acceptedComponent']:continue
 a=ov['artifacts'];g=decoder.graph(a['component']['path']);need(sorted(i['name']for i in g['rootImports'])==CAPS,'fresh binary exact3 roots')
 need([e['name']for e in g['exports']]==['run']and g['exports'][0]['sort']==[1],'actual binary run function only')
 f=g['componentFunctions'][g['exports'][0]['index']];t=g['componentTypes'][f['typeIndex']];need(f['kind']=='lift'and t['kind']=='function'and t['params']==[]and t['results']==[-13],'fresh binary run0 string')
 functions={i['name']:i['functions']for i in g['rootImports']};need(functions[CAPS[0]]==['now','subscribe-instant','subscribe-duration']and functions[CAPS[1]]==['now']and functions[CAPS[2]]==['poll'],'five callables; no type-only claim')
 cg=decoder.core(Path(a['allGeneratedFiles'][0]['path']).read_bytes(),{'role':'physical-generated-core'});need(len(g['modules'])==4,'4 actual cores')
 need(cg['moduleSha256']==g['modules'][0]['moduleSha256'],'full main physical/nested core equal')
 out=OWN/case;(out/'binary-type-core-graph.json').write_text(json.dumps(g,indent=2)+'\n')
 graph=dict(schemaVersion=1,component=a['component'],rootImports=g['rootImports'],exports=g['exports'],functionSignatures=[dict(name='run',params=[],result='string')],componentSections=g['componentSections'],nestedCores=[{k:m[k]for k in ['moduleSha256','moduleBytes','imports','customSections','sections']}for m in g['modules']],physicalCore=a['allGeneratedFiles'][0],wholeCoreByteEqual=True,allNoncustomCoreSectionsByteEqual=True,compiledOrInstantiatedByReviewer=False,decoderSource=descriptor(parser),decoderSourceIndex=pix)
 (out/'binary-graph.json').write_text(json.dumps(graph,indent=2)+'\n');ov['binaryGraph']=descriptor(out/'binary-graph.json');ov['fullBinaryTypeCoreGraph']=descriptor(out/'binary-type-core-graph.json')
# Current end-bookend: every original file identity, every private publication
# member/directory and package/family membership. All payloads hashed above.
for p,i in identities.items():need(key(Path(p).lstat())==i,'final current full intake identity')
for base,names,dirs in publications:
 need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'final exact publication membership')
 for n,ident in dirs.items():need(key((base if n=='.'else base/n).lstat())==ident,'final private directory identity')
for path,ixrow in families.items():
 root=Path(path).parent;need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in json.loads(Path(path).read_text())['files']]},'final whole family membership')
summary=dict(schemaVersion=1,state='REMAINING_FOUR_CONSTRUCTION_OUTCOMES_READ_ONLY_INTAKE_PASSED',checks=checks,currentFullHashFiles=len(rows),currentLogicalBytes=sum(r['bytes']for r in rows.values()),currentFamilies=len(families),sourceIndex=ix,priorReviews=prior,outcomes=outcomes,decoderSource=descriptor(parser),actualTimeProtectionQualification='Source-coupled successful final/failure guards and original raw terminals plus current full hash/identity/membership intake; no actual-time per-file read trace claimed',reviewerOperationalActionsInvoked=False)
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(OWN/'raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=copies),indent=2)+'\n')
(OWN/'input-boundaries.json').write_text(json.dumps(dict(schemaVersion=1,sourceIndex=ix,declaredSourceInputs=descriptor(SOURCE/'source-inputs.json'),declaredBoundaries=source_inputs['boundaries'],packageInventory=refs['packageInventory'],familyIndices=list(families.values()),fullCurrentHashFileCount=len(rows),fullCurrentLogicalBytes=sum(r['bytes']for r in rows.values()),identityBookendPassed=True,scope='Complete current expanded declared closure hashed; descriptors referenced without recursively copying historical inventories'),indent=2)+'\n')
print(json.dumps({k:summary[k]for k in ['state','checks','currentFullHashFiles','currentLogicalBytes','currentFamilies']}))
