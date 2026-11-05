"""Read/authenticate existing source DATA and prepare a dormant copy plan only."""
from pathlib import Path
import hashlib,json,stat
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
SOURCE=REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
seen={}
def row(p):
 p=Path(p).absolute();b=p.read_bytes();r=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));assert seen.get(str(p),r)==r;seen[str(p)]=r;return r
def verify(r):
 got=row(r['path']);assert got==r
def load(p):row(p);return json.loads(Path(p).read_bytes())
def write(name,v):(HERE/name).write_text(json.dumps(v,indent=2)+'\n')
def family(root,expected):
 index=row(root/'index.json');assert index['sha256']==expected;data=load(root/'index.json');rows=[index]
 for r in data['files']:
  p=root/r['path'];got=row(p);assert(got['sha256'],got['bytes'])==(r['sha256'],r['bytes']);rows.append(got)
 assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}=={r['path']for r in data['files']}|{'index.json'}
 return rows
source_rows=family(SOURCE,'08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65');assert len(source_rows)==32
monitor_rows=family(MONITOR,'0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
policy=load(SOURCE/'policy.json');declared=load(SOURCE/'input-hashes.json')['files'];assert len(declared)==1590
for r in declared:verify(r)
base=load(SOURCE/'stage-input-plan.json');assert len(base['files'])==1581
rows=[]
for r in base['files']:
 d=dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']);verify(d)
 mode=stat.S_IMODE(Path(r['original']).stat().st_mode)
 rows.append(dict(path=r['path'],original=r['original'],sha256=r['sha256'],bytes=r['bytes'],sourceMode=mode,roles=[r.get('role','AUTHENTICATED_COMBINED_BUILD_TOOL_OR_ANCESTRY'),'EXACT_08BF_STAGE_INPUT_PLAN_ROW']))
for r in source_rows:
 rows.append(dict(path=Path(r['path']).relative_to(REPO).as_posix(),original=r['path'],sha256=r['sha256'],bytes=r['bytes'],sourceMode=stat.S_IMODE(Path(r['path']).stat().st_mode),roles=['EXACT_COMBINED_INTEGRATION_SEALED_FAMILY_DATA']))
rows.sort(key=lambda r:r['path']);assert len(rows)==len({r['path']for r in rows})==1613
write('stage-copy-plan.json',dict(schemaVersion=1,state='DORMANT_COMBINED355_EXACT_SOURCE_COPY_PLAN_V1',sourceIndex=source_rows[0],configuredSourceRoot=policy['contexts']['configuredSourceRoot'],workRoot=policy['contexts']['workRoot'],freezeRoot=policy['contexts']['freezeRoot'],nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,externalEmbeddingSources=3,selectedManifestCount=11,basePlanRows=1581,integrationFamilyRows=32,copiedFiles=1613,files=rows,controllerFamilyCopied=False,baselineGitFilesAreAdditional=True,originalPreparationRowsRebased=False,sourceStageExecuted=False))
apis=[row(REPO/p)for p in['tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/stage.py','tests/node-compat/foundation-crypto/native-integration-candidate-v2/stage.py','tests/node-compat/foundation-crypto/ownership-secret-stage-controller-candidate-v1/controller.py']]
write('references.json',dict(schemaVersion=1,integrationIndex=source_rows[0],monitorIndex=monitor_rows[0],monitorEntry=next(r for r in monitor_rows if r['path']==str(MONITOR/'monitor.py')),publishMechanismSourceData=apis,monitorApi='monitor(argv,cwd,environment,output,timeout_seconds,authority)',deadlineSeconds=600,actualIntegrationSourceReview=None,actualStageControllerReview=None,rootStageAuthority=None,stageExecuted=False,buildAllowed=False,operationalAdmission=False))
root=dict(schemaVersion=1,state='UNISSUED_COMBINED355_SOURCE_STAGE_ROOT_AUTHORITY_V1',phase=None,sourceStageAllowed=False,sourceIndex=source_rows[0],stageControllerIndex=None,stageControllerEntry=None,integrationSourceReview=None,stageControllerReview=None,genericMonitorIndex=monitor_rows[0],genericMonitorEntry=next(r for r in monitor_rows if r['path']==str(MONITOR/'monitor.py')),pythonExecutable=None,gitBinary=None,configuredSourceRoot=policy['contexts']['configuredSourceRoot'],workRoot=policy['contexts']['workRoot'],freezeRoot=policy['contexts']['freezeRoot'],externalOutputRoot='/private/tmp/starling-node-compat/combined-native355-v1-stage-external-root',stageJournal='/private/tmp/starling-node-compat/combined-native355-v1-stage.json',baselineRevision='54b3329b3ce818fd1f244e871e9c259b63667cda',externalParentDeadlineSeconds=600,nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,externalEmbeddingSources=3,selectedManifestCount=11,initialVariant='normal-off',basePlanRows=1581,integrationFamilyRows=32,expectedStageCopies=1613)
for key in ['nativeBuildAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','timingAllowed','normalMutationAllowed','metadataProjectionAllowed','privateBackendEvidenceHookEnabled','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:root[key]=False
for key in ['actualStageResult','actualStageReview','actualBuildResult','reviewedNativePins','runtimeAuthority']:root[key]=None
write('root-authority.template.json',root)
write('config.template.json',dict(schemaVersion=1,state='UNISSUED_COMBINED355_SOURCE_STAGE_CONFIG_V1',rootAuthority=None,sourceIndex=source_rows[0],controllerIndex=None))
write('input-hashes.json',dict(schemaVersion=1,role='ORIGINAL_SOURCE_DATA_ONLY_NOT_STAGED_PREPARATION_REINTERPRETATION',files=sorted(seen.values(),key=lambda r:r['path']),sourceOriginalInputRows=1590,allInputHashesChecked=True,actualStageExecuted=False))
print(json.dumps(dict(state='COMBINED355_STAGE_SOURCE_DATA_PREPARED_NO_ACTION',stageRows=len(rows),inputs=len(seen),sourceFamilyRows=len(source_rows),monitorFamilyRows=len(monitor_rows))))
