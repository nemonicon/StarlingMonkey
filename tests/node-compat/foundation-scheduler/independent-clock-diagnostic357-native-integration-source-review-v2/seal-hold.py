"""Compact static Source HOLD. Evaluates only the exact manifest predicate over DATA."""
from pathlib import Path
import ast,copy,hashlib,json
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-clock-diagnostics-native-integration-candidate-v2'
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
index=desc(SOURCE/'index.json');assert index['sha256']=='a52ee25caa3e026ad8efae1955473bea2a98090811d66cea7be911853b5d7c64'
ix=read(index['path']);assert {r['path']for r in ix['files']}|{'index.json'}=={p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()}
for r in ix['files']:
 p=SOURCE/r['path'];assert not p.is_symlink()and desc(p)==dict(r,path=str(p))
refs=read(SOURCE/'references.json');policy=read(SOURCE/'policy.json');helper=(SOURCE/'layer-policy.py').read_text();recipe=(SOURCE/'build-engine.sh').read_text();tree=ast.parse(helper)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='validate_sources')
condition=next(n for n in ast.walk(fn)if isinstance(n,ast.Assert)).test
text=ast.get_source_segment(helper,condition)
assert text=="sorted(manifest,key=lambda r:r['path'])==actual and all(set(r)=={'path','sha256'}for r in manifest)"
predicate=compile(ast.Expression(condition),'<exact-a52e-validate_sources-predicate>','eval')
manifest=policy['expectedNativeSourceManifest'];canonical=sorted(manifest,key=lambda r:r['path']);assert len(manifest)==len({r['path']for r in manifest})==357 and manifest!=canonical
assert 'rows=POLICY[\'expectedNativeSourceManifest\']'in helper and 'return copy.deepcopy(rows)'in helper
assert 'json.dump(layer.source_manifest(repo),open(sys.argv[2],\'w\'),indent=2)'in recipe
assert 'manifest = layer.source_manifest(repo)'in recipe and 'layer.validate_sources(repo,manifest)'in recipe
assert recipe.index('cmake --build')<recipe.index('layer.validate_sources(repo,manifest)')<recipe.index("with open(artifact + '.build.json', 'x')")
def observe(provided,actual):return eval(predicate,{'__builtins__':{'sorted':sorted,'all':all,'set':set}},dict(manifest=provided,actual=actual))
cases=[]
def case(name,provided,actual,expected):
 observed=observe(provided,actual);assert observed is expected;cases.append(dict(name=name,expected=expected,observed=observed))
case('actual emitted unsorted357 refuses its own actual source rows',manifest,manifest,False)
case('caller-only sorting cannot repair unsorted actual policy rows',canonical,manifest,False)
case('prospective source canonical policy/manifest consistency',canonical,canonical,True)
bad=copy.deepcopy(canonical);bad[0]['sha256']='0'*64;case('changed source hash refused',bad,canonical,False)
case('duplicate source row refused',canonical+[canonical[0]],canonical,False)
bad=copy.deepcopy(canonical);bad[0]['extra']=True;case('extra row field refused',bad,canonical,False)
plan=read(SOURCE/'stage-copy-plan.json')['files'];native=[dict(path=r['path'],sha256=r['sha256'])for r in plan if r['role']=='native']
assert {r['path']:r['sha256']for r in native}=={r['path']:r['sha256']for r in manifest}
evidence=dict(schemaVersion=1,state='ACTUAL_SOURCE_MANIFEST_ORDER_JOIN_BLOCKER_CONFIRMED',sourceIndex=index,policy=refs['policy'],helper=refs['helper'],recipe=refs['recipe'],exactExtractedPredicate=text,sourceRowCount=357,declaredSourceRowsAlreadyCanonical=False,stageAndPolicyPathHashMapsEqual=True,lastDeclaredRows=manifest[-2:],cases=cases,helperOrRecipeOrStageOrCompilerOrGuestInvoked=False,scope='Pure evaluation of exact helper AST predicate over authenticated actual source-policy rows; no helper function or source_manifest invocation.')
save('counterexample.json',evidence)
save('required-correction-contract.json',dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_NATIVE_SOURCE_MANIFEST_ORDER_CORRECTION_REQUIRED_V1',sourceIndex=index,requiredCorrection=['Genuine immutable successor must join declared357 source order, source_manifest return, retained prebuild input_manifest, postbuild validate_sources predicate and whole metadata/model sourceManifest equality.','Canonicalize declared source-policy rows genuinely before hashing the new policy/helper/recipe; update every resulting active guard, reference and Root template. An order-insensitive alternative must still preserve the full exact357 path/hash set and explicit raw ordering contract.','Add exact actual source_manifest/validate_sources predicate regression using current unsorted357 DATA (old must refuse) and successor DATA (new must pass), plus hash/duplicate/shape negatives.','Keep native diagnostic CPP/header/embedding bytes and357/3/11/82 arithmetic unchanged unless separately justified; no source count/metadata facade projection.'],currentBuildOrStageActionAdmitted=False,actualRuntimeOrNativeFailureObserved=False))
save('results.json',dict(schemaVersion=1,state='INDEPENDENT_CLOCK_DIAGNOSTIC357_NATIVE_INTEGRATION_SOURCE_REVIEW_HELD_V2',sourceIndexSha256=index['sha256'],sourceIndex=index,sourceOnly=True,sourceReviewPassed=False,verifiedPassed=False,sourceHold=True,concreteBlockers=1,blocker='M1: emitted357 manifest cannot satisfy real sorted-manifest/unsorted-policy helper join',nativeSourceFiles=357,externalEmbeddingSources=3,rawMetadataFields=82,selectedWholeManifests=11,sourceFamilyMembersAuthenticated=len(ix['files'])+1,counterexample=desc(OWN/'counterexample.json'),requiredCorrectionContract=desc(OWN/'required-correction-contract.json'),ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildOrStageActionsInvoked=False,runtimeActionsInvoked=False,actualNativeOrRuntimeFailureObserved=False,reviewerRelationship='Reviewer authored diagnostic payload90ef. This review independently examines B-authored producer/controller wiring; it does not self-certify the payload or grant native/link/runtime authority.',completedReads=['All current Source members authenticated and inspected; real source_manifest return, prebuild capture and postbuild validate_sources call joined.','Reviewer attempt1 traversed declared input families/ledgers and hashed regular rows before its own overly order-sensitive plan comparison refused; that attempt is retained without claiming a completed intake PASS.','A separate read-only reviewer authenticated the active seven helper/policy guards, helper/model pins, own paths and final82 emitter gate; no guard-slot mismatch found.'],remainingReview='Full producer/controller review and final current-boundary PASS are withheld pending a genuine correction; no stage/build may consume this as Source PASS.',qualifications=['This is a Source-level deterministic refusal, not an observed native build or guest failure.','The earliest real refusal is the post-build emitter layer.validate_sources(repo,manifest), before sidecar publication; decorate repeats the same validation later.','Existing macro/link/ODR/natural-loop/epoch/Store-death/fatal/full17 lifecycle gates remain open.','Root pre-entry Bash startup cleaning, SDK post-command hash qualification, depth1 non-byte-capped Git history and narrow stat-cache-only index semantics remain explicit obligations.']))
save('source-receipt.json',dict(schemaVersion=1,results=desc(OWN/'results.json'),counterexample=desc(OWN/'counterexample.json'),correctionContract=desc(OWN/'required-correction-contract.json'),sourceIndex=index,operationalActionsInvoked=False))
assert desc(SOURCE/'index.json')==index
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():r=desc(p);r['path']=p.relative_to(OWN).as_posix();rows.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_SOURCE_HOLD_NO_ACTION_AUTHORITY_V1',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for name in ['index.json','results.json','required-correction-contract.json']:print(json.dumps(desc(OWN/name)))
