"""Seal source only; hash DATA and inspect syntax evidence, invoke no action."""
from pathlib import Path
import ast
import hashlib
import json
D=Path(__file__).resolve().parent
assert not(D/'index.json').exists()
def row(p):
 p=Path(p);assert p.is_file()and not p.is_symlink();h=hashlib.sha256();a=p.stat()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def save(n,v):
 with(D/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n')
refs=json.loads((D/'references.json').read_bytes());assert refs['actualCalibrationReview']is not None
inputs=json.loads((D/'source-inputs.json').read_bytes())
for r in inputs['files']:assert row(r['path'])==r
checks=json.loads((D/'source-checks.json').read_bytes());assert checks['pilotReviewBound']is True and checks['state']=='V5_TIMING_ONLY_SOURCE_DATA_CHECKS_PASSED'
tests=json.loads((D/'evidence/summary.json').read_bytes());assert tests['preflightWorkerLoaderGuestOrMeasurementCalled']is False and tests['actualPilotIndexRows']==33066 and tests['actualMatchedRows']==120
for p in(D/'evidence').glob('*.terminal.json'):
 t=json.loads(p.read_bytes());assert t['rawExitCode']==0 and row(t['source']['path'])==t['source']and t['operationalEntrypointCalled']is False
asts=[]
for p in D.glob('*.py'):ast.parse(p.read_bytes());asts.append(p.name)
large=[];peer=refs['actualCalibrationReview'];ix=json.loads(Path(peer['index']['path']).read_bytes())
for r in ix['files']:
 if r['bytes']>4*1024*1024:
  assert r['bytes']<=64*1024*1024
  large.append(dict(path=str(Path(peer['index']['path']).parent/r['path']),bytes=r['bytes'],role='EXTERNAL_PROOF_DATA_NOT_SOURCE_FAMILY_MEMBER',reader='existing indexed/regular bounded64MiB'))
for p in D.rglob('*'):
 assert not p.is_symlink()
 if p.is_file():assert p.stat().st_size<=4*1024*1024,'No huge proof in worker own-source inventory'
save('source-vs-proof-bounds.json',dict(schemaVersion=1,ownAndAncestorSourceMemberMaximumBytes=4*1024*1024,externalProofDataMaximumBytes=64*1024*1024,exactPinnedLargeNodeRoleUnchanged=True,largeExternalPilotProofMembers=large,proofDataNotCopiedOrRelabelled=True,pilotIndexRows56894=1536*37+62,timingIndexRows17642=360*49+2))
history=json.loads((D/'preparation-history.json').read_bytes());history.update(currentPreparationState='SOURCE_CHECKS_COMPLETE_SEALED_AFTER_ACTUAL_PILOT_DATA_BINDING',actualPilotReviewBound=True,actualPilotReview=peer,sourceAndPureAndParserActionsOnly=True,operationalEntrypointsOrWorkerLoaderGuestOrMeasurementInvoked=False)
(D/'preparation-history.json').write_text(json.dumps(history,indent=2)+'\n')
result=dict(schemaVersion=1,state='SOURCE_ONLY_ZLIB_COST_TIMING_V5_PREPARED',sourceOnly=True,sourcePreparationPassed=True,sourceIndexSha256=None,sourceIndependentReview=None,originalPilotSourceIndex=refs['originalPilotSourceIndex'],actualCalibrationReview=peer,originalPilotIndex=refs['actualPilotIndex'],originalPilotResults=refs['actualPilotResults'],originalMatchedPlan=refs['actualMatchedPlan'],actualIndexRows=33066,pilotIndexRowBound=56894,timingIndexRowBound=17642,newScope='read-only-plan-and-timing-only',sourceChecks=row(D/'source-checks.json'),pureAndGrammar=row(D/'evidence/summary.json'),pythonAst=asts,preparationInputRows=len(inputs['files']),prospectiveIndependentState='INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1',newRootAuthority=None,actualNewPreparedPlan=None,newPhaseAuthority=None,newQuietWindow=None,newWarmNOrBudgetAuthority=None,operationalEntrypointsCalled=False,preflightOrHelperOrWorkerOrLoaderOrGuestOrMeasurementInvoked=False,oldSourceAndActualRecordsUnchanged=True,oldCalibrationSourceNeverRelabelled=True,operationalAdmission=False,runtimeAcceptanceClaim=False,adoptionAllowed=False,performanceClaim=False)
save('results.json',result)
save('source-receipt.json',dict(schemaVersion=1,state='ZLIB_COST_TIMING_V5_SOURCE_SEALED',sourceOnly=True,results=row(D/'results.json'),sourceChecks=row(D/'source-checks.json'),pureAndGrammar=row(D/'evidence/summary.json'),actualPilotReview=peer,sourceInputManifest=row(D/'source-inputs.json'),allInputsRehashed=True,noOperationalOrGuestActions=True,independentReviewAndFreshRootPlanPhaseWindowRequired=True))
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file():r=row(p);r['path']=p.relative_to(D).as_posix();files.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_TIMING_ONLY_CALIBRATION_ROLE_INDEX_BOUND_SOURCE_V5',files=files,sourceOnly=True,sourceIndependentReview=None,futureRootPhaseAuthority=None,operationalAdmission=False))
print(json.dumps(dict(index=row(D/'index.json'),results=row(D/'results.json'),receipt=row(D/'source-receipt.json'),members=len(files),inputs=len(inputs['files']),actualPilotReview=peer,sourceOnly=True)))
