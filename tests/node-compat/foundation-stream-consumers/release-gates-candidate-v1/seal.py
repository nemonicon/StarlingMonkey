"""Owned source/data seal only. Never runs publisher, bootstrap or runtime code."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return(json.dumps(value,indent=2)+'\n').encode()
def put(name,value):(H/name).write_bytes(encoded(value))
def checked(row):
 p=Path(row['path']);assert p.is_file()and not p.is_symlink();digest=hashlib.sha256();size=0
 with p.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):digest.update(chunk);size+=len(chunk)
 assert digest.hexdigest()==row['sha256']and size==row['bytes'],p
prep=json.loads((H/'source-inputs.preparation.json').read_bytes());assert prep['oldNestedPreparationRowsFollowed']is False
for row in prep['files']:checked(row)
source=json.loads((H/'source-checks.stdout.json').read_bytes());contract=json.loads((H/'contract-checks.stdout.json').read_bytes());syntax=json.loads((H/'syntax-checks.stdout.json').read_bytes())
assert source['state']==contract['state']==syntax['state']=='passed'
live_root=Path('/Users/dan/dev/StarlingMonkey');five=[live_root/name for name in ['builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs']]
direct=[row for row in prep['files']if Path(row['path'])in five];assert direct==[]
tools=json.loads((H/'tool-context.json').read_bytes())
put('input-freeze.json',{'schemaVersion':1,'state':'ORIGINAL_ABSOLUTE_PREPARATION_CONTEXT_ONLY','originalPreparationRoot':str(H),'inputs':[{'path':row['path'],'sha256':row['sha256'],'bytes':row['bytes'],'roles':row['roles']}for row in prep['files']],'toolTrees':tools['toolTrees'],'toolLinks':tools['toolLinks'],'oldNestedPreparationRowsFollowed':False,'liveRootFiveDirectInputs':0,'ownerActionsExecuted':False})
proof=json.loads((H/'afterimage-proof.json').read_bytes());graph=json.loads((H/'selected-closure.json').read_bytes());body=json.loads((H/'inherited-body-audit.json').read_bytes())
put('results.json',{'schemaVersion':1,'state':'SOURCE_IMPLEMENTATION_SEALED_ACTIONS_HELD_FOR_INDEPENDENT_REVIEW','sourceChecks':source['checks'],'pureContractChecks':contract['checks'],'javascriptParseOnly':syntax['javascriptParseOnly'],'pythonAstOnly':syntax['pythonAstOnly'],'snapshotFiles':body['snapshotFiles'],'hostAfterimageEdits':len(proof['edits']),'hostAfterimagePaths':len({row['path']for row in proof['edits']}),'unchangedCaseOracleFixtureFiles':len(body['unchangedCaseOracleFixtureData']),'selectedLocalModuleAndDataFiles':len(graph['localModulesAndData']),'selectedLocalEdges':len(graph['localEdges']),'sourceInputs':len(prep['files']),'nativeSources':355,'nativeSourcesModified':False,'sourcePolicyLineage':[306,342,350,355],'toolTrees':len(tools['toolTrees']),'toolLinks':len(tools['toolLinks']),'historicalControls':6,'liveRootFiveDirectInputs':0,'sourcePublisherExecuted':False,'ownerHelperExecuted':False,'preflightExecuted':False,'nativeOrGuestOrHostExecuted':False,'timingExecuted':False,'operationalAdmission':False,'futureActionAuthority':None,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None}})
put('source-receipt.json',{'schemaVersion':1,'state':'SOURCE_ONLY_PROPOSAL_HELD_FOR_REVIEW','originalPreparationRoot':str(H),'sourceResultsSha256':sha((H/'results.json').read_bytes()),'inputFreezeSha256':sha((H/'input-freeze.json').read_bytes()),'afterimageProofSha256':sha((H/'afterimage-proof.json').read_bytes()),'parentPlanIndexSha256':'24a71405787f98386cf468e903b0e60bb938d1c67f3f6a820b91ace2c6624350','nativeProducerIndexSha256':'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378','currentExternalNativePinsSha256':'93512520ba6f9ddaba096c09936f16f33462b371b5a9df4cf3315e9a43a5d67b','currentExternalNativeReviewSha256':'6359ca0b635bb252643f7082cc0df02d6c7fc83cdec5b4fc94e470c231470ce4','actionsApproved':False,'futureActionAuthority':None,'operationalAdmission':False})
rows=[]
for p in sorted(H.rglob('*')):
 assert not p.is_symlink(),p
 if p.is_file()and p!=H/'index.json':
  name=str(p.relative_to(H));assert all(len(part.encode())<=255 for part in p.relative_to(H).parts)
  raw=p.read_bytes();rows.append({'path':name,'sha256':sha(raw),'bytes':len(raw)})
put('index.json',{'schemaVersion':1,'state':'SOURCE_ONLY_RELEASE_GATES_PROPOSAL_HELD_FOR_INDEPENDENT_REVIEW','files':rows})
for row in rows:assert sha((H/row['path']).read_bytes())==row['sha256']
print(json.dumps({'indexSha256':sha((H/'index.json').read_bytes()),'files':len(rows),'inputs':len(prep['files']),'state':'SOURCE_ONLY_HELD','ownerOrRuntimeActionsExecuted':False}))
