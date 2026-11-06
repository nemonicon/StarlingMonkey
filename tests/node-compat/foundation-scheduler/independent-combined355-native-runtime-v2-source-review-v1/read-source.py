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
# Actual immutable V2 derivation and held correction, never old PASS transfer.
derivation=read(descriptor(SOURCE/'source-derivations.json'));family(derivation['heldSourceIndex']);records=derivation['records'];edit_count=0
for r in records:
 before=checked(r['donor']).read_text();after=checked(r['after']).read_text();need(r['after']['path']==str(SOURCE/r['path']),'actual derived Source path')
 cursor=0;built=[];reverse=[];ncursor=0
 for e in r['edits']:
  need(e['oldStart']>=cursor and e['newStart']>=ncursor and before[e['oldStart']:e['oldEnd']]==e['before']and after[e['newStart']:e['newEnd']]==e['after'],'exact complete edit slice')
  built.extend([before[cursor:e['oldStart']],e['after']]);cursor=e['oldEnd'];reverse.extend([after[ncursor:e['newStart']],e['before']]);ncursor=e['newEnd'];edit_count+=1
 built.append(before[cursor:]);reverse.append(after[ncursor:]);need(''.join(built)==after and ''.join(reverse)==before,'exact whole forward/inverse Source image')
need(len(records)==28 and edit_count==70,'exact bounded28/70 Source derivations')
family(refs['previousSourceIndex']);family(refs['previousSourceHold']['index']);held=read(refs['previousSourceHold']['result']);correction=read(refs['requiredCorrection'])
need(held['state']=='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_HELD_V1'and held['sourceReviewPassed']is False and held['sourceIndexSha256']==refs['previousSourceIndex']['sha256']and correction['heldSourceIndex']==refs['previousSourceIndex'],'genuine oldHOLD not SourcePASS')
cat=read(refs['fixtureCatalogue']);need([f['id']for f in cat['fixtures']]==['resource','pure','fatal','init-fatal','clock-snapshot','surviving-interest'],'complete held six fixture Source')
for f in cat['fixtures']:checked(f['source']);checked(f['wit'])
artifact_shapes={}
for case,slot in refs['artifactSlots'].items():
 if case=='init-fatal':continue
 need(slot['actualReview']and slot['contract'],'all5 actual positive artifacts fixed, not pendingwildcard');pair=slot['actualReview'];family(pair['index']);pv=read(pair['result']);cv=read(slot['contract']);need(pv['state']==cv['requiredReviewState']=='INDEPENDENT_COMBINED355_'+case.replace('-','_').upper()+'_COMPONENT_ARTIFACT_REVIEW_PASSED_V1','actual percase state/contract')
 for k,v in cv['requiredFixedValues'].items():need(pv[k]==v,'actual percase fixed value '+k)
 need(pv['artifacts']==cv['artifacts']and pv['generatedFiles']==cv['generatedFiles'],'exact full original artifact loading maps');direct_roles(pv['artifacts']);direct_roles(pv['generatedFiles'])
 f=next(x for x in cat['fixtures']if x['id']==case);need(pv['artifacts']['fixtureSource']==f['source']and pv['artifacts']['fixtureWit']==f['wit']and pv['publicAbiSignatures']==[dict(name=e['name'],params=e['arguments'],result=e['result'])for e in f['exports']],'whole actual scalar ABI/fixture')
 need(pv['nativeSourceFiles']==355 and pv['externalEmbeddingSources']==3 and pv['fullMetadataFields']==80 and pv['selectedWholeManifests']==11 and pv['artifacts']['nativeEngine']==refs['nativeEngine']and pv['artifacts']['nativeMetadata']==refs['nativeMetadata'],'no old metadata generation projection')
 artifact_shapes[case]=dict(review=pair,contract=slot['contract'],component=pv['artifacts']['component'],emittedImports=pv['emittedImports'],publicAbiSignatures=pv['publicAbiSignatures'],generatedFiles=pv['generatedFiles'])
# Children have explicit own89 direct dependencies including the full Node shim
# subtree; their smaller auth is not a claimed native API/admission frame.
child=read(descriptor(SOURCE/'child-inputs.json'));need(child['nativeApiInvocations']==0 and child['nativeFrameReturned']is False,'child API/fabrication distinction')
for r in child['files']:checked(r)
metadata=read(refs['nativeMetadata']);expected=read(refs['actualReadOnlyData']);need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11 and expected['bootstrap']['metadata']==metadata,'full80/355+3/11 actual current raw native frame')
need(refs['originalRoot']==str(SOURCE)and refs['nativeApiSourceIndex']['sha256']=='c365e6089688f62f028580e86b14db80bb434ba7b4ac45ae341e851c11913a7b','real own/runtime/native API contexts')
entry=(SOURCE/'entry.mjs').read_text();external=ast.parse((SOURCE/'external.py').read_text());assignments={}
for n in external.body:
 if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['REPO','OWN']:assignments[n.targets[0].id]=ast.unparse(n.value)
need("const ORIGINAL='"+str(SOURCE)+"';"in entry and assignments['OWN'].endswith("'tests/node-compat/foundation-scheduler/combined-native-runtime-candidate-v2'"),'actual own JS/Python constants; no injected namespace')
for p in SOURCE.glob('*.py'):ast.parse(p.read_text());checks+=1
# Exact failure classification and contract text joins; behavior is tested using
# the actual exported pure functions only after this complete hash intake.
model=(SOURCE/'models.mjs').read_text();body=(SOURCE/'runtime.mjs').read_text();contract=read(descriptor(SOURCE/'future-runtime-review-contract.template.json'));facts=read(descriptor(SOURCE/'source-facts.json'));prepared=read(descriptor(SOURCE/'results.json'))
need(contract['fatalGateReviewPassedState']is None and 'fatal'not in contract['perFixtureRequiredStates']and contract['expectedCallbackDiagnosticProof']is None,'no fatalGate PASS contract exposed')
need(contract['fatalObservationRequiredFixedValues']['expectedCallbackFailureProved']is False and contract['fatalObservationRequiredFixedValues']['fatalCallbackGateSatisfied']is False and contract['fatalObservationRequiredFixedValues']['callbackCause']=='inconclusive','contract observes failure not callbackcause')
need("state:'COMBINED355_FATAL_OBSERVATION_CAUSE_INCONCLUSIVE_UNACCEPTED_V2'"in body or "fatal?'COMBINED355_FATAL_OBSERVATION_CAUSE_INCONCLUSIVE_UNACCEPTED_V2'"in body,'realparent unaccepted observation state')
need("stderr.includes('RESOURCE_UNHANDLED_TIMER_CALLBACK')"in body and '!/unknown import|failed to instantiate|no export/i.test(stderr)'in body,'unchanged WT source marker/no generictrap acceptance')
for k in ['expectedCallbackFailureProved','fatalCallbackGateSatisfied','current355NativeCallbackDiagnosticAvailable','ownerActionsInvoked','operationalAdmission','runtimeAcceptanceClaim']:
 need(prepared[k]is False,'Source preparation limit '+k)
need(prepared['failureReceiptBestEffort']is True and prepared['completeFailedIndexGuaranteed']is False and prepared['failedPositiveChildParentRegistrationMayBeIncomplete']is True,'truthful inherited failure output limit')
need(facts['resourceCoverage']==dict(innerRecords=49,callbacks=98,newIds=322,publicStrings=35),'actual Source fact35/49/98/322 fields');need(contract['resourceRequiredCoverage']==dict(rawPublicStrings=35,runRecords=49,callbackObservations=98,newIds=322,retainedJcoRotations=3,freshJcoRotations=1,freshWasmtimeWithinExportRotations=3),'preserved positive coverage consumer contract')
for p,i in identities.items():need(key(Path(p).lstat())==i,'final own/import/current boundary identity')
for path in families:
 base=Path(path).parent;v=json.loads(Path(path).read_bytes());need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in v['files']]},'final exact family membership')
summary=dict(schemaVersion=1,state='INDEPENDENT_FULLRUNTIME_V2_SOURCE_READ_HASH_AST_INTAKE_PASSED',checks=checks,currentFullHashFiles=len(rows),currentLogicalBytes=sum(r['bytes']for r in rows.values()),currentFamilies=len(families),sourceIndex=ix,sourceInputs=descriptor(SOURCE/'source-inputs.json'),declaredBoundaries=source_inputs['boundaries'],familyIndices=list(families.values()),artifactShapes=artifact_shapes,childDirectFiles=len(child['files']),derivationFiles=len(records),exactForwardInverseEdits=edit_count,sourceParentMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,packageRegularFiles=4889,packageLinks=21,ownConstants=assignments,operationalActionsInvoked=False,selfWritingAuthorCheckerInvoked=False)
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','currentFullHashFiles','currentLogicalBytes','currentFamilies','derivationFiles','exactForwardInverseEdits']}))
