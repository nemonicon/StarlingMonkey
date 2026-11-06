"""Independent bounded SOURCE/DATA intake, no operational imports or calls."""
from pathlib import Path
import ast,hashlib,json,os,re,stat,subprocess,time
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-native-runtime-candidate-v3'
EXPECTED='54a70237f27aa9f0d1c0d6d0f7766f1575734031c806478017f304d9a73cd424'
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
reviewConfig=json.loads((OWN/'review-config.json').read_bytes());expectedRoot=reviewConfig['rootObservation'];need(type(expectedRoot)is dict,'Root actual terminal/report tuple must be supplied before DATA audit');rp=OWN.parent/'combined-native-runtime-v3-surviving-interest-map-root-results.json';need(str(rp)==expectedRoot['path'],'own actual Root report path');need(descriptor(rp)==expectedRoot,'actual surviving-interest41448 Root report');root=read(descriptor(rp));direct_roles(root)
need(root['toolObservation']==dict(sessionId=reviewConfig['toolSession'],rawExitCode=0)and root['sourceIndex']==ix,'actual original tool/raw0/currentSource')
auth=read(root['rootAuthority']);cfg=read(root['config']);inv=read(root['invocation']);direct_roles(inv)
need(auth['state']=='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V3'and auth['sourceIndex']==ix and cfg['sourceIndex']==ix and cfg['rootAuthority']==root['rootAuthority']and auth['fixtureId']==cfg['fixtureId']=='surviving-interest'and auth['phase']==cfg['phase']=='map','actual same54a Root/config/map context')
need(auth['mappingOnlyAllowed']is auth['jcoCompilerHelpersAllowed']is True and auth['generatedApplicationImportAllowed']is auth['ordinaryGuestExportsAllowed']is auth['stockWasmtimeAllowed']is False,'compiler-only actual permission, not runtime')
family(auth['sourceIndependentReview']['index']);peer=read(auth['sourceIndependentReview']['result']);need(auth['sourceIndependentReview']['index']['sha256']=='ecd595bc5dc3ad7e0d9130cb7b4b8d3caa45a6cbcb73c0f91f3b3856aaea419b'and peer['state']=='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V3'and peer['sourceIndexSha256']==ix['sha256']and peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'genuine independentSourceecd')
need(auth['nativeEngine']==refs['nativeEngine']and auth['nativeMetadata']==refs['nativeMetadata']and auth['nativeReadOnlyConfig']==refs['readOnlyConfig']and auth['actualBootstrapReview']==refs['actualBootstrapReview']and auth['actualReadOnlyReview']==refs['actualReadOnlyReview'],'genuine current fullnative/API prerequisite roles')
metadata=read(refs['nativeMetadata']);expected=read(refs['actualReadOnlyData']);need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11 and expected['bootstrap']['metadata']==metadata,'full unchanged80/355+3/11 nativeframe')
family(refs['actualMappingFailureReview']['index']);family(refs['mappingFailureOriginalReviewIndex']);failed=read(refs['actualMappingFailureReview']['result']);fc=read(refs['actualMappingFailureContract']);need(failed['state']==fc['requiredReviewState']and failed['sourceIndexSha256']==refs['publicationParentSourceIndex']['sha256']and failed['acceptedMappedOutput']is False and failed['actualPostCallOptionsObserved']is False and failed['optionsFieldCauseInferenceOnly']is True,'real failedV2 lineage remains failed/inferenceonly')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in fc[group].items():need(failed[n]==v,'actual failure contract '+n)
need(failed['coverage']==fc['requiredCoverage']and failed['requiredCorrection']==refs['mappingFailureRequiredCorrection'],'genuine repaired coverage/b926 roles')
for rr in failed['actualPartialFiles']:checked(rr)
slot=refs['artifactSlots']['surviving-interest'];family(slot['actualReview']['index']);a=read(slot['actualReview']['result']);ac=read(slot['contract']);need(a['state']==ac['requiredReviewState']=='INDEPENDENT_COMBINED355_SURVIVING_INTEREST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and a['artifacts']==ac['artifacts']and a['generatedFiles']==ac['generatedFiles'],'real ce6 component/construction loadingproof')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in ac[group].items():need(a[n]==v,'component contract '+n)
familyRows=json.loads(Path(slot['actualReview']['index']['path']).read_bytes())['files'];familyBase=Path(slot['actualReview']['index']['path']).parent
for exactRole in [slot['actualReview']['result'],slot['contract']]:need(sum(dict(r,path=str(familyBase/r['path']))==exactRole for r in familyRows)==1,'artifact result/contract exactly once in same family')
if 'requiredCoverage'in ac:need(a['coverage']==ac['requiredCoverage'],'whole artifact coverage')
direct_roles(a['artifacts']);direct_roles(a['generatedFiles']);need(auth['actualArtifactReview']==slot['actualReview']and auth['actualArtifactContract']==slot['contract']and root['component']==a['artifacts']['component'],'same5599 component selected beforemappedphase')
base=Path(auth['outputRoot']);need(str(base)=='/private/tmp/starling-node-compat/combined-native-runtime-v3-surviving-interest-map','genuine freshV3 output context');index=read(root['actualIndex']);completion=read(root['completion']);result=read(root['mappingResult']);expected_names={'index.json','completion.json'}
for r in index['files']:
 n=r['path'];need(n not in expected_names and n and not n.startswith('/')and all(p not in('','.','..')for p in n.split('/')),'unique confined indexedoutput');expected_names.add(n);checked(dict(r,path=str(base/n)))
need(len(index['files'])==13 and len(expected_names)==15 and {p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==expected_names,'whole13indexed+2 actualpublication')
for p in [base,*base.rglob('*')]:
 st=p.lstat();need(not p.is_symlink(),'no actual outputlinks')
 if p.is_dir():need(stat.S_IMODE(st.st_mode)==0o700,'private actual outputdirectory')
 else:need(stat.S_ISREG(st.st_mode)and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1,'private independent actual outputfile')
need(completion['externalRawZeroAndSeparateReviewRequired']is True and completion['index']==dict(root['actualIndex'],path='index.json')and completion['result']==dict(root['mappingResult'],path='result.json'),'unaltered relative index/completion roles')
need(result['state']=='COMBINED355_MAPPED_OUTPUT_COMPLETE_UNREVIEWED_V3'and result['sourceIndex']==ix and result['rootAuthority']==root['rootAuthority']and result['config']==root['config']and result['fixtureId']=='surviving-interest'and result['component']==a['artifacts']['component'],'whole original unmapped/runtime-unreviewed result')
for n in ['generatedApplicationImported','ordinaryExportsInvoked','operationalAdmission','runtimeAcceptanceClaim']:need(result[n]is False,'actual map scope '+n)
need(result['jcoCompilerHelpersInvoked']is True,'Source-coupled construction-only compiler action')
request=read(root['requestedMappingOptions']);post=read(root['postCallOptionsShape']);need(result['requestedMappingOptions']==root['requestedMappingOptions']and result['postCallOptionsShape']==root['postCallOptionsShape']and result['mappingOptions']==root['mappingOptions']==request,'same wholepristine requestedJSON and exact typedworkrole')
need(result['mappingOptionsMeaning']=='pristine-request-retained-before-Jco-call'and result['postCallOptionsInputWireClaim']is False,'input/workcopy distinction unchanged')
need(set(request)=={'name','wasiShim','map'}and request['name']=='combined_surviving_interest'and request['wasiShim']is False and set(request['map'])=={'wasi:clocks/*','wasi:io/*'}and root['requestedMappingOptions']['bytes']==len((json.dumps(request,indent=2)+'\n').encode()),'exact pristine requestedJSON bytes request keys, not API mutableobject')
need(post['schemaVersion']==1 and post['inputWireClaim']is post['optionsMutatedOrSanitizedByObserver']is False and post['observed']['type']=='object'and post['observed']['fullValueClaim']is False,'actual postcalltyped bounded ownshape, never fullinputwire')
props={r['key']:r for r in post['observed']['properties']};need(set(props)=={'name','wasiShim','map','flagsAsBigInt','noComponentErrorWrapping'},'actual complete postcalltopfieldnames')
need(props['flagsAsBigInt']['kind']=='data'and props['flagsAsBigInt']['observed']==dict(type='undefined')and props['noComponentErrorWrapping']['observed']==dict(type='boolean',value=False),'actual V3 ownundefined/wrapping observedtyped')
postmap={r['key']:r['observed']['value']for r in props['map']['observed']['properties']};need(all(r['kind']=='data'and r['observed']['type']=='string'for r in props['map']['observed']['properties']),'actual postwork stringmap rules')
need(all(postmap[k]==v for k,v in request['map'].items()),'requested2 standardrules preserved in workmap')
unused={k:v for k,v in postmap.items()if k not in request['map']};need(len(unused)>0 and all(k.startswith('jco:node/')or k=='wasi:tls/types@0.2.0-draft'for k in unused),'nonstandard default selectionrules explicitly separate')
need(result['mappedFiles']==root['mappedFiles']and len(root['mappedFiles'])==7 and set(root['mappedFiles'])==set(a['generatedFiles']),'full seven generatedtuple filenames')
for n,r in root['mappedFiles'].items():
 need(r['path']==str(base/'transpiled'/n),'eachactualmappedfile confinedrole');checked(r)
 if not n.endswith('.js'):need(r['sha256']==a['generatedFiles'][n]['sha256']and r['bytes']==a['generatedFiles'][n]['bytes'],'whole nonJS core/declaration/interface/package equaloriginal')
need(root['mappedFiles']['combined_surviving_interest.js']['bytes']>0,'actual surviving-interest generatedglue identity is bound by Root/index/current hashes')
need(result['staticAudit']==read(descriptor(base/'mapped-audit.json'))and result['staticAudit']['generatedModuleImported']is result['staticAudit']['actualRuntimeProtocolProved']is False,'saved whole ASTaudit, no runtimeclaim')
for role in ['externalParentTerminal','outerTerminal']:
 t=read(root[role]);need(t['rawExitCode']==0 and t['authority']==root['rootAuthority']and t['timeout']is t['forcedCleanup']is False and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True,'actual rawzero cleanownership')
 for field in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[field]==[],'no rawcleanup '+field)
 need(all(not g['alive']for g in t['finalGroups']),'all observedgroups gone');checked(t['stdout']);checked(t['stderr']);need(t['stderr']['bytes']==0,'raw empty stderr bothlevels')
inner=read(root['externalParentTerminal']);outer=read(root['outerTerminal']);lines=[json.loads(x)for x in Path(outer['stdout']['path']).read_text().splitlines()];need(len(lines)==2 and lines[0]==dict(pid=inner['pid'],timeoutSeconds=1200)and lines[1]['terminal']==root['externalParentTerminal']and lines[1]['rawExitCode']==0,'raw outerJSONL prefix+terminal unshortened')
need(any(p['pid']==inner['pid']for p in outer['observedProcesses']),'outer observed realNode innerPID')
returned=json.loads(Path(inner['stdout']['path']).read_text());need(returned==dict(root=str(base),index=dict(root['actualIndex'],path='index.json'),completion=dict(root['completion'],path='completion.json'),completeUnreviewed=True),'original relative Nodepublication return, no implicit row rewriting')
# Compact exact actual text only. Core and historical nativeframes stayrefs.
copies=[];chosen=[base/r['path']for r in index['files']if not r['path'].endswith('.wasm')]+[base/'index.json',base/'completion.json',rp,*[Path(root[k]['path'])for k in ['rootAuthority','config','invocation','externalParentTerminal','outerTerminal']],*[Path(t[k]['path'])for t in [inner,outer]for k in ['stdout','stderr']]]
for p in dict.fromkeys(chosen):
 label='actual/'+p.relative_to(base).as_posix()if p.is_relative_to(base)else'external/'+p.parent.name+'/'+p.name;target=OWN/'raw'/label;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());need(descriptor(target)['sha256']==descriptor(p)['sha256'],'exact compact rawcopy');copies.append(dict(original=descriptor(p),copy=descriptor(target)))
for path,i in identities.items():need(key(Path(path).lstat())==i,'full declared source/native/package/actual finalidentity')
for path in families:
 b=Path(path).parent;need({p.relative_to(b).as_posix()for p in b.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in json.loads(Path(path).read_bytes())['files']]},'final wholefamily membership')
need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==expected_names,'finalexact publicationmembers')
summary=dict(schemaVersion=1,state='INDEPENDENT_V3_SURVIVING_INTEREST_MAPPED_OUTPUT_READ_ONLY_INTAKE_PASSED',checks=checks,currentFullHashFiles=len(rows),currentLogicalBytes=sum(r['bytes']for r in rows.values()),currentFamilies=len(families),sourceIndex=ix,sourcePeer=auth['sourceIndependentReview'],rootResult=descriptor(rp),mappingRootAuthority=root['rootAuthority'],mappingConfig=root['config'],invocation=root['invocation'],mappingResult=root['mappingResult'],actualIndex=root['actualIndex'],completion=root['completion'],externalParentTerminal=root['externalParentTerminal'],outerTerminal=root['outerTerminal'],innerNodePid=inner['pid'],outerParentPid=outer['pid'],actualRoot=str(base),actualFiles=[dict(r,path=str(base/r['path']))for r in index['files']]+[root['actualIndex'],root['completion']],mappedFiles=root['mappedFiles'],component=root['component'],mappingOptions=request,requestedMappingOptions=root['requestedMappingOptions'],postCallOptionsShape=root['postCallOptionsShape'],staticAudit=descriptor(base/'mapped-audit.json'),originalComponentArtifactReview=slot['actualReview'],originalComponentArtifactContract=slot['contract'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],freezeReceipt=refs['freezeReceipt'],actualFailureReview=refs['actualMappingFailureReview'],historicalV2ActualOptionsObjectObserved=False,actualV3PostCallOwnUndefinedObserved=True,unusedNonstandardMappingRules=unused,unusedMapRulesNotImportsOrCapabilities=True,currentFullHostTlsImplementationClaim=False,generatedApplicationImported=False,ordinaryExportsInvoked=False,reviewerOperationalActionsInvoked=False,actualTimeProtectionQualification='Original Source-coupled successful guards/raw0 and parentnativeAPI bookends plus current full read/hash/identity/membership intake; no per-file actual-time readtrace or newly retained nativeframe invented')
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(OWN/'raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=copies),indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','currentFullHashFiles','currentLogicalBytes','currentFamilies','innerNodePid','outerParentPid']}))
