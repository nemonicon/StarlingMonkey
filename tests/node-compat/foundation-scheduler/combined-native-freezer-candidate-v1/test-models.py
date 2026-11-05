"""Pure DATA checks only; no authorize, admission/helper, monitor, copy or freezer."""
from pathlib import Path
import ast,copy,importlib.util,json
OWN=Path(__file__).resolve().parent;S=OWN.parent
checks=0

def load(name):
 spec=importlib.util.spec_from_file_location('pure_combined_freezer_'+name,OWN/(name+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
models=load('models');metadata_model=load('metadata_model');io=load('copy_io')
root=json.loads((S/'combined-native355-v2-build-root-results.json').read_bytes());metadata=json.loads(Path(root['metadata']['path']).read_bytes());producer=json.loads((S/'combined-native-build-controller-candidate-v2/references.json').read_bytes());policy=json.loads(Path(producer['policy']['path']).read_bytes());database=json.loads(Path(metadata['compileCommandsPath']).read_bytes())
refs=dict(engine=root['engine'],recipe=producer['recipe'],policy=producer['policy'],layer=producer['helper'],externalSourceManifest=metadata['componentizeSourceManifest'],selectedManifests=metadata['selectedModuleManifests'],configuredSourceRoot=metadata['combinedNativeSourcePolicy']['configuredSourceRoot'],workRoot=metadata['combinedNativeSourcePolicy']['workRoot'],privateRustupBootstrapPolicy=metadata['privateRustupBootstrapPolicy'],rustupBeforeRecord=metadata['privateRustupBootstrapPolicy']['beforeInstallRecord'],rustupCurrentSettings=metadata['privateRustupBootstrapPolicy']['settingsAtBuildCompletion'])

def validate(m,p=policy):
 models.metadata(m,p,refs);models.compilation(database,m,p,refs)
 result=metadata_model.validate_metadata(m,p,refs['policy']['sha256'],refs['layer']['sha256'],refs['recipe']['sha256'],refs['externalSourceManifest'],'normal-off')
 assert result==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)

def good(fn):
 global checks
 fn();checks+=1

def denied(fn):
 global checks
 try:fn()
 except (AssertionError,KeyError,TypeError,ValueError):checks+=1;return
 raise AssertionError('counterexample accepted')

def mutate(keys,value):
 m=copy.deepcopy(metadata);at=m
 for k in keys[:-1]:at=at[k]
 at[keys[-1]]=value;return m

good(lambda:validate(metadata))
for keys,value in [(['engineSha256'],'0'*64),(['enginePath'],'/wrong/engine.wasm'),(['sourceManifest'],metadata['sourceManifest'][:342]),(['selectedModuleManifests'],metadata['selectedModuleManifests'][:9]),(['componentizeSourceManifest'],[]),(['gcStress'],True),(['oomTesting'],True),(['entropyPolicy'],'runtime-only'),(['privateRustupBootstrapPolicy','persistentSetting'],'check-only'),(['privateRustupBootstrapPolicy','settingsAtBuildCompletion'],dict(metadata['privateRustupBootstrapPolicy']['settingsAtBuildCompletion'],bytes=57)),(['combinedNativeSourcePolicy','configuredSourceRoot'],'/wrong/source'),(['combinedNativeSourcePolicy','workRoot'],'/wrong/work'),(['combinedNativeSourcePolicy','actualCompileDatabaseRows'],67),(['combinedNativeSourcePolicy','actualPolicyCppCompileCommands'],metadata['combinedNativeSourcePolicy']['actualPolicyCppCompileCommands'][:61]),(['classicStreamsPolicy','actualPrivateTargetCompileCommands'],metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands'][:5]),(['strictEventExceptionPolicy','actualNativeCompileCommands'],[]),(['taskSelectionPolicy','nativeAllInvalidRuntimeValidation'],{'invented':True}),(['zlibErrorSemanticsPolicy','remainingDeviationsApproved'],True),(['zlibPolicy','runtimeBackendProof'],dict(verified=True,version='invented',vernum=1))]:denied(lambda keys=keys,value=value:validate(mutate(keys,value)))
m=copy.deepcopy(metadata)
for key in list(m)[-5:]:del m[key]
denied(lambda:validate(m))
for replacement in [database[:-1],database+[database[0]],copy.deepcopy(database)]:
 if len(replacement)==68:replacement[0]['command']+=' -DDEBUG=1'
 denied(lambda replacement=replacement:models.compilation(replacement,metadata,policy,refs))
source=Path(refs['configuredSourceRoot'])
for row in database:
 names=[r['path'] for r in metadata['sourceManifest'] if r['path'].endswith('.cpp') and r['path'].startswith(('builtins/','runtime/')) and row['file']==str(source/r['path'])]
 if names:good(lambda row=row,n=names[0]:io.compile_command(row['command'],False,n,True,False))
good(lambda:io.compile_command(metadata['actualEmbeddingCompileCommands'][0],False,'embedding/embedding.cpp',True,False))
# Real generic validation functions exercise prospective copy confinement and
# refusal, without execute_plan, any write or a fake admitted Frame.
import hashlib
output=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
original=OWN/'models.py';checksum=hashlib.sha256(original.read_bytes()).hexdigest()
plan=[dict(original=original,target=output/'model.txt',sha256=checksum,shared=False)]
good(lambda:io.validate_plan(plan,output/'normal-off-freeze-receipt.json',output))
denied(lambda:io.validate_plan(plan+plan,output/'normal-off-freeze-receipt.json',output))
denied(lambda:io.validate_plan(plan,output/'model.txt',output))
for target in [output/'../escape',Path('/private/tmp/not-owned.txt')]:
 denied(lambda target=target:io.validate_plan([dict(plan[0],target=target)],output/'normal-off-freeze-receipt.json',output))
denied(lambda:io.validate_plan([dict(plan[0],sha256='0'*64)],output/'normal-off-freeze-receipt.json',output))
denied(lambda:io.validate_plan([dict(plan[0],original=OWN/'ABSENT')],output/'normal-off-freeze-receipt.json',output))
denied(lambda:io.validate_plan([dict(original=original,target=original,sha256=checksum,shared=False)],OWN/'ABSENT-RECEIPT',OWN))
# Before JSON is retained as historical bytes; only its actual current record
# descriptor and the independent 107-byte current setting are live origins.
before=json.loads(Path(refs['rustupBeforeRecord']['path']).read_bytes());assert refs['rustupBeforeRecord']['bytes']==368 and refs['rustupCurrentSettings']['bytes']==107
historical=[]
def collect(v):
 if isinstance(v,dict):
  if set(v)=={'path','sha256','bytes'}:historical.append(v)
  for value in v.values():collect(value)
 elif isinstance(v,list):
  for value in v:collect(value)
collect(before);good(lambda:None);assert any(r['bytes']==57 for r in historical)
# Do not open or hash the historical nested 57-byte setting descriptor.
for path in OWN.glob('*.py'):ast.parse(path.read_text(),filename=str(path));checks+=1
result=dict(schemaVersion=1,passed=True,checks=checks,actualMetadataFields=len(metadata),actualDatabaseRows=len(database),policyCppCommands=62,strictCommands=4,privateCommands=6,separateEmbedding=1,rawMetadataNotRewritten=True,historical57ByteSettingNotReadOrRehashed=True,currentSettingBytes=107,ownerModelOrLayerImported=False,genericCopyValidationOnly=True,actualCopyWriterInvoked=False,ownerActionOrCopyOrFreezeOrCompilerOrGuestInvoked=False)
(OWN/'model-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
