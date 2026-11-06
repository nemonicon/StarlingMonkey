"""Compact Source delta/grammar seal. No full native-ledger replay or producer action."""
from pathlib import Path
import ast,hashlib,json,os,subprocess
OWN=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
refs=read(OWN/'references.json');deriv=read(OWN/'derivations.json');parent=Path(refs['parentProducerIndex']['path']).parent
assert desc(parent/'index.json')==refs['parentProducerIndex']
parent_ix=read(parent/'index.json');parent_rows=[]
for r in parent_ix['files']:
 p=parent/r['path'];assert desc(p)==dict(r,path=str(p));parent_rows.append(dict(r,path=str(p)))
assert {r['path']for r in parent_ix['files']}|{'index.json'}=={p.relative_to(parent).as_posix()for p in parent.rglob('*')if p.is_file()}
hold=Path(refs['manifestOrderHoldIndex']['path']).parent;assert desc(hold/'index.json')==refs['manifestOrderHoldIndex']
for r in read(hold/'index.json')['files']:assert desc(hold/r['path'])==dict(r,path=str(hold/r['path']))
edits=0
for r in deriv['files']:
 assert desc(r['before']['path'])==r['before']and desc(r['after']['path'])==r['after'];before=Path(r['before']['path']).read_text();text=before
 for e in r['edits']:assert text.count(e['before'])==e['count'];text=text.replace(e['before'],e['after']);edits+=1
 assert text==Path(r['after']['path']).read_text()
 for e in reversed(r['edits']):text=text.replace(e['after'],e['before'])
 assert text==before
for name in ['native-admission-model.py','embedding-diagnostic.UNAPPLIED.patch']:assert(OWN/name).read_bytes()==(parent/name).read_bytes()
policy=read(OWN/'policy.json');old=read(parent/'policy.json');assert{**policy,'expectedNativeSourceManifest':old['expectedNativeSourceManifest']}==old
assert policy['expectedNativeSourceManifest']==sorted(old['expectedNativeSourceManifest'],key=lambda r:r['path'])
for key in ['copyPlan','cachePlan','protectedInputs']:assert refs[key]in parent_rows
plan=read(refs['copyPlan']['path'])['files'];assert [dict(path=r['path'],sha256=r['sha256'])for r in plan if r['role']=='native']==policy['expectedNativeSourceManifest']
absence=[]
for key,path in refs['contexts'].items():
 p=Path(path);assert not p.exists()and not p.is_symlink();absence.append(dict(role=key,path=path,absent=True))
test=read(OWN/'test-results.json');assert test['oldFailNewPass']and test['checks']>=50 and not test['helperOrStageOrBuildOrCompilerOrGuestInvoked']
assert(OWN/'test.stderr.log').read_bytes()==b''
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
bash=refs['bash'];assert desc(bash['path'])==bash
env={k:v for k,v in os.environ.items()if not k.startswith('BASH_FUNC_')and k not in ['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE']}
argv=[bash['path'],'-n',str(OWN/'build-engine.sh')];r=subprocess.run(argv,env=env,capture_output=True,timeout=30)
(OWN/'bash-grammar.stdout.log').write_bytes(r.stdout);(OWN/'bash-grammar.stderr.log').write_bytes(r.stderr);assert r.returncode==0 and r.stdout==r.stderr==b''
save('grammar-results.json',dict(schemaVersion=1,argv=argv,rawExitCode=r.returncode,stdout=desc(OWN/'bash-grammar.stdout.log'),stderr=desc(OWN/'bash-grammar.stderr.log'),activePythonAsts=len(list(OWN.glob('*.py'))),grammarOnly=True,recipeExecuted=False))
root=read(OWN/'root-authority.template.json');assert root['entry']==refs['controller']and root['sourceIndex']is root['sourceReview']is root['sourceStageAllowed']is root['nativeBuildAllowed']is None
hist=read(OWN/'preparation-history.json');hist['state']='SEALED_UNEXECUTED_CANONICAL_MANIFEST_SOURCE_CORRECTION_V3';hist['authoringChecksRetained']=['authoring-attempt1.json','authoring-test-attempt1.json'];save('preparation-history.json',hist)
save('results.json',dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_NATIVE_PRODUCER_SOURCE_READY_FOR_INDEPENDENT_REVIEW_V3',sourceOnly=True,sourceChecksPassed=True,manifestOrderingCorrected=True,actualSourceAstOldFailNewPass=True,sourceExpressionPureChecks=test['checks'],sevenActiveHashGuardsAndSelfPinsJoined=True,parentProducerIndex=refs['parentProducerIndex'],manifestOrderHoldIndex=refs['manifestOrderHoldIndex'],newHelper=refs['helper'],newPolicy=refs['policy'],newRecipe=refs['recipe'],newController=refs['controller'],nativeSourceFiles=357,retainedParentNativeFiles=349,changedNativeFiles=6,newNativeFiles=2,externalEmbeddingSources=3,externalEmbeddingChanges=1,selectedWholeManifests=11,prospectiveRawMetadataFields=82,prospectivePolicyCpp=63,prospectiveDatabaseRows=69,prospectiveNodePrivateCpp=6,prospectiveSeparateEmbeddingCpp=1,nativeOrEmbeddingPayloadChanged=False,direct82ModelByteIdentical=True,sharedDataDescriptors={k:refs[k]for k in ['copyPlan','cachePlan','protectedInputs']},sharedDataAuthenticatedByParentIndex=True,fullNativeLedgerOrTooltreeAuthoringReplay=False,parentCurrentIntakeRetainedAsAncestryOnly=True,futurePathAbsenceObservations=absence,exactReversibleSourceEditGroups=edits,sourcePeer=None,rootAuthority=None,actualStage=None,actualBuild=None,actualArtifact=None,runtimeAuthority=None,stageActionsInvoked=False,nativeBuildActionsInvoked=False,producerOrHelperInvoked=False,compilerActionsInvoked=False,engineOrGuestOrClockRuntimeInvoked=False,operationalAdmission=False,fullSeventeenGatesAccepted=False,qualifications=['Prior Source and HOLD remain unchanged; prior current-input audit is ancestry and is not projected as a newly completed V3 24528-row audit.','New runtime/Source protocol identity V3 retains the never-created v2 paths; operational parent/worker perform original full-boundary checks and require separate issued Root phase.','Shared stage plan activeProducerContext is historical DATA; V3 refs and future stage receipt bind actual original V3 producer context.','Metadata/source policy structure and exact82 classifier state remain V2 schema, with no metadata cast or native source/version substitution.','New Source has no stage/build authority. SDK post-command digest qualification, private environment cleaning, Git index restrictions and all link/runtime/fatal/natural-loop/Storedeath gates remain unchanged.']))
save('source-receipt.json',dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_RUNNABLE_NATIVE_PRODUCER_SOURCE_SEALED_V3',result=desc(OWN/'results.json'),tests=desc(OWN/'test-results.json'),testStdout=desc(OWN/'test.stdout.json'),testStderr=desc(OWN/'test.stderr.log'),grammar=desc(OWN/'grammar-results.json'),derivations=desc(OWN/'derivations.json'),references=desc(OWN/'references.json'),sourceContract=desc(OWN/'future-source-review-contract.json'),nativeSourceFiles=357,prospectiveRawMetadataFields=82,allFutureActionAuthoritiesNull=True,operationalActionsInvoked=False))
assert desc(parent/'index.json')==refs['parentProducerIndex']and desc(hold/'index.json')==refs['manifestOrderHoldIndex']
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():r=desc(p);r['path']=p.relative_to(OWN).as_posix();rows.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_CLOCK_DIAGNOSTIC357_NATIVE_INTEGRATION_V3',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for n in ['index.json','results.json','source-receipt.json']:print(json.dumps(desc(OWN/n)))
