"""Independent bounded SOURCE/DATA intake, no operational imports or calls."""
from pathlib import Path
import ast,hashlib,json,os,re,stat,subprocess,time
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-native-runtime-candidate-v2'
EXPECTED='1cda0bd6ae2f0d1a5cde1502bd58842cde06580e3249e9ae94135d6cf8b55f36'
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
rp=OWN.parent/'combined-native-runtime-v2-resource-map-root-results.json';need(descriptor(rp)['sha256']=='a93f01d68c0e6add2f7f78b5dbc5b0a97b952eb8c7cdc2751fce0f9650cd234e','actual Root50606 failure report');root=read(descriptor(rp));direct_roles(root)
need(root['toolObservation']==dict(sessionId=50606,rawExitCode=1)and root['sourceIndex']==ix,'actual original terminal observation/source')
frame=read(root['rootAuthority']);config=read(root['config']);invocation=read(root['invocation']);direct_roles(invocation);need(frame['state']=='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V2'and frame['sourceIndex']==ix and config['sourceIndex']==ix and config['rootAuthority']==root['rootAuthority']and config['phase']==frame['phase']=='map'and config['fixtureId']==frame['fixtureId']=='resource','genuine original map Root/config no runtimephase')
family(frame['sourceIndependentReview']['index']);peer=read(frame['sourceIndependentReview']['result']);need(peer['state']=='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V2'and peer['sourceIndexSha256']==ix['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'actual42ed Source peer unchanged')
need(frame['sourceIndependentReview']['index']['sha256']=='42ed1306e0e23735a4b4c5d0012c64aaac0a92cb0df8968ebdc09d5b1216aa31','actual source peer pin')
need(frame['jcoCompilerHelpersAllowed']is frame['mappingOnlyAllowed']is True and frame['generatedApplicationImportAllowed']is frame['ordinaryGuestExportsAllowed']is frame['stockWasmtimeAllowed']is False,'only mapping compiler action issued')
need(frame['nativeEngine']==refs['nativeEngine']and frame['nativeMetadata']==refs['nativeMetadata']and frame['nativeReadOnlyConfig']==refs['readOnlyConfig']and frame['actualBootstrapReview']==refs['actualBootstrapReview']and frame['actualReadOnlyReview']==refs['actualReadOnlyReview'],'full genuine355 native/API roles unchanged')
need((frame['nativeSourceFiles'],frame['externalEmbeddingSources'],frame['fullMetadataFields'],frame['selectedWholeManifests'])==(355,3,80,11),'new full80/355+3/11 context')
for field in ['actualMappedReview','actualMappedContract']:need(frame[field]is None,'no actual mapped admission proof')
metadata=read(refs['nativeMetadata']);expected_native=read(refs['actualReadOnlyData']);need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11 and expected_native['bootstrap']['metadata']==metadata,'current entire raw native metadata unchanged')
slot=refs['artifactSlots']['resource'];family(slot['actualReview']['index']);artifact=read(slot['actualReview']['result']);ac=read(slot['contract']);need(artifact['state']==ac['requiredReviewState']=='INDEPENDENT_COMBINED355_RESOURCE_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and artifact['artifacts']==ac['artifacts']and artifact['generatedFiles']==ac['generatedFiles'],'actual resource artifact/loadingmap retained')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for k,v in ac[group].items():need(artifact[k]==v,'actual resource percase contract '+k)
direct_roles(artifact['artifacts']);direct_roles(artifact['generatedFiles']);need(frame['actualArtifactReview']==slot['actualReview']and frame['actualArtifactContract']==slot['contract'],'actual Root selected original ce6 resource proof')
base=Path(frame['outputRoot']);need(str(base)=='/private/tmp/starling-node-compat/combined-native-runtime-v2-resource-map'and root['failure']['path']==str(base/'failure.json'),'exact failed output context')
paths={Path(r['path']).relative_to(base).as_posix():r for r in root['allPartialFiles']};need(len(paths)==11,'all11 retained partial files')
need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==set(paths)and not any(p.is_symlink()for p in base.rglob('*')),'exact full failed publication closed set')
for p in [base,*base.rglob('*')]:
 st=p.lstat()
 if p.is_dir():need(stat.S_IMODE(st.st_mode)==0o700,'private failed dir')
 else:need(stat.S_ISREG(st.st_mode)and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1,'private independent partial file')
for n in ['result.json','index.json','completion.json']:need(not(base/n).exists(),'no complete/accepted mapped publication')
need(set(paths)=={'failure.json','inputs.json','transpile-shape.json','mapped-audit.json',*['transpiled/'+n for n in artifact['generatedFiles']]},'whole original7 mappedroles plus4 partialrecords')
mapped={n:paths['transpiled/'+n]for n in artifact['generatedFiles']}
for n,r in mapped.items():
 if not n.endswith('.js'):need(r['sha256']==artifact['generatedFiles'][n]['sha256']and r['bytes']==artifact['generatedFiles'][n]['bytes'],'all mapped core/declarations/package unchanged fullbytes '+n)
need(mapped['combined_resource.js']['sha256']=='a44d99798f59deb9720cbb14b125441c2b604781bd5c7a790be5a84e35847b10','actual whole mappedglue')
inputs=read(root['inputs']);audit=read(root['mappedAudit']);shape=read(root['transpileShape']);failure=read(root['failure']);need(inputs['sourceIndex']==ix and inputs['rootAuthority']==root['rootAuthority']and inputs['config']==root['config']and inputs['actualArtifactReview']==slot['actualReview']and inputs['component']==artifact['artifacts']['component'],'full actual input roles')
need(audit['generatedModuleImported']is audit['actualRuntimeProtocolProved']is False and audit['standardShimVersion']=='0.31.0','Source AST audit passed but notruntimeproof')
need(shape['exports']==[['inspect','function'],['run','function'],['validate','function']]and sorted(shape['fileNames'])==sorted(n for n in artifact['generatedFiles']if n!='package.json'),'all six Jco-return files+separate package')
need(failure==dict(primaryPresent=True,primary=dict(type='object',opaque=True,fullOpaqueValueClaim=False),finalErrors=[],partialEvidenceOnly=True),'whole truthful failure capture no inferred objectfields')
for role,pid in [('externalTerminal',18019),('outerTerminal',17800)]:
 t=read(root[role]);need(t['pid']==pid and t['rawExitCode']==1 and t['authority']==root['rootAuthority'],'genuine actual raw1 owned terminal')
 need(t['timeout']is t['forcedCleanup']is False and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True,'clean owned mapfailure')
 for field in ['signals','errors','interruptedSignals','remainingObservedPids']:need(t[field]==[],'no forced/timeout/cleanup '+field)
 need(all(not g['alive']for g in t['finalGroups']),'every observed group gone');checked(t['stdout']);checked(t['stderr'])
inner=read(root['externalTerminal']);outer=read(root['outerTerminal']);need(any(p['pid']==inner['pid']for p in outer['observedProcesses']),'outer observed genuine innerNode')
need(inner['stdout']['bytes']==0,'no complete mapping return stdout')
err=Path(inner['stderr']['path']).read_text();need('Error: Ordinary acyclic JSON only'in err and 'durable.mjs:11:3'in err and 'at plainJSON'in err and 'at async finish'in err and 'mapping.mjs:23:10'in err,'actual raw publication serializer stack after mapped audit')
lines=[json.loads(x)for x in Path(outer['stdout']['path']).read_text().splitlines()];need(len(lines)==2 and lines[0]==dict(pid=18019,timeoutSeconds=1200),'unmodified two-record parent JSONL launch prefix')
need(lines[1]['terminal']==root['externalTerminal']and lines[1]['rawExitCode']==1 and lines[1]['phase']=='map'and lines[1]['fixtureId']=='resource','original actual outer raw terminal envelope')
need('assert terminal[\'rawExitCode\']==0'in Path(outer['stderr']['path']).read_text(),'outer asserts rawzero and preserves its own error')
# Exact source inference, never an observed post-call options object.
transpile=Path(refs['loaderPackageRoot'])/'node_modules/@bytecodealliance/jco/dist/cmd/transpile.js';jr=next(r for r in package['files']if r['path']==str(transpile));jrow={k:jr[k]for k in ['path','sha256','bytes']};checked(jrow);jt=transpile.read_text();stmt='opts.flagsAsBigInt ??= opts.flagsAsBigint;';need(jt.count(stmt)==1 and 'opts.noComponentErrorWrapping ??= opts.componentErrorWrapping === false;'in jt and 'withDefaultNodeCapabilities(opts);'in jt,'actual pinned prepOpts mutating statements')
need('const options=mappingOptions(f.refs,f.fixture.id)'in(SOURCE/'mapping.mjs').read_text()and'generated=await api.transpile(b,options)'in(SOURCE/'mapping.mjs').read_text()and'mappingOptions:options'in(SOURCE/'mapping.mjs').read_text(),'same calleroptions published after actualAPI seam')
source_inference=dict(schemaVersion=1,jcoSource=jrow,normalizationStatement=stmt,normalizationStatementSha256=hashlib.sha256(stmt.encode()).hexdigest(),normalizationSourceLine=jt[:jt.index(stmt)].count('\n')+1,additionalNormalizations=['opts.noComponentErrorWrapping ??= opts.componentErrorWrapping === false;','withDefaultNodeCapabilities(opts);'],callerSource=descriptor(SOURCE/'mapping.mjs'),observedPostCallOptions=None,actualOptionsFieldAttributionObserved=False,fieldCausality='SOURCE_BASED_INFERENCE_ONLY; actual mutated post-call options were not retained',observedBoundary='rawError plainJSON→DurableOutput.write→output.finish→mapping.run after fullmapped AST audit')
(OWN/'source-causality.json').write_text(json.dumps(source_inference,indent=2)+'\n')
copyrows=[]
chosen=[Path(r['path'])for r in root['allPartialFiles']if not r['path'].endswith('.wasm')]+[rp,*[Path(root[k]['path'])for k in ['rootAuthority','config','invocation','externalTerminal','outerTerminal']],*[Path(t[k]['path'])for t in [inner,outer]for k in ['stdout','stderr']]]
for p in dict.fromkeys(chosen):
 label='actual/'+p.relative_to(base).as_posix()if p.is_relative_to(base)else'external/'+p.parent.name+'/'+p.name;dest=OWN/'raw'/label;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());need(descriptor(dest)['sha256']==descriptor(p)['sha256'],'byteexact finite rawcopy');copyrows.append(dict(original=descriptor(p),copy=descriptor(dest)))
for path,ident in identities.items():need(key(Path(path).lstat())==ident,'final fullSource/native/package/actual identitybookend')
for path in families:
 b=Path(path).parent;need({p.relative_to(b).as_posix()for p in b.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in json.loads(Path(path).read_bytes())['files']]},'final family exactmembership')
need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==set(paths),'final exact11 partialmembers')
summary=dict(schemaVersion=1,state='INDEPENDENT_RESOURCE_MAP_V2_FAILURE_READ_ONLY_INTAKE_PASSED',checks=checks,currentFullHashFiles=len(rows),currentLogicalBytes=sum(r['bytes']for r in rows.values()),currentFamilies=len(families),sourceIndex=ix,sourcePeer=frame['sourceIndependentReview'],rootResult=descriptor(rp),rootAuthority=root['rootAuthority'],config=root['config'],invocation=root['invocation'],externalTerminal=root['externalTerminal'],outerTerminal=root['outerTerminal'],rawExitCodes=[1,1],actualPartialRoot=str(base),actualPartialFiles=root['allPartialFiles'],mappedFiles=mapped,mappedAudit=root['mappedAudit'],transpileShape=root['transpileShape'],inputs=root['inputs'],failure=root['failure'],resourceArtifactReview=slot['actualReview'],resourceArtifactContract=slot['contract'],component=artifact['artifacts']['component'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],freezeReceipt=refs['freezeReceipt'],fullMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,sourceCausality=descriptor(OWN/'source-causality.json'),observedFailureBoundary='strict JSON result serialization after saved mapped AST audit',postCallOptionsObserved=False,indexPublished=False,resultPublished=False,completionPublished=False,acceptedMappedOutput=False,generatedApplicationImported=False,ordinaryGuestExportsInvoked=False,reviewerOperationalActionsInvoked=False,actualTimeProtectionQualification='Source-coupled failure.finalErrors[] and original owned rawterminals plus current complete declared read/hash identity/membership intake; no independent actual-time per-file readtrace')
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(OWN/'raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=copyrows),indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','currentFullHashFiles','currentLogicalBytes','currentFamilies','actualPartialRoot','rawExitCodes']}))
