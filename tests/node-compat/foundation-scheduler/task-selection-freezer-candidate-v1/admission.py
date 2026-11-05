"""Explicit342 build-source/compile admission; genuine configured APIs, no engine call."""
import importlib.util

def admit(frame,g):
 g.require_frame(frame);g.recheck(frame);refs=frame['refs'];metadata=frame['metadata'];policy=frame['policy']
 try:
  row=refs['configuredModel'];g.checked(row)
  spec=importlib.util.spec_from_file_location('genuine_task_selection342_metadata_model',row['path']);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
  result=model.validate_metadata(metadata,policy,refs['policySha256'],refs['helperSha256'],refs['recipeSha256'],refs['externalSourceManifest'],'normal-off')
  assert result==dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY',nativeFiles=342,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
  row=refs['configuredLayer'];g.checked(row)
  spec=importlib.util.spec_from_file_location('genuine_configured_task_selection342_layer',row['path']);layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
  assert layer.HERE==g.SOURCE/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'
  layer.validate_sources(g.SOURCE,metadata['sourceManifest'])
  native,queue,private=layer.validate_classic_compilation(frame['database'],metadata['actualEmbeddingCompileCommands'],g.SOURCE,metadata)
  assert len(native)==61 and len(queue)==1 and len(private)==5
  selected=[]
  for row in metadata['selectedModuleManifests']:
   path=g.SOURCE/row['path'];value=g.read(dict(path=str(path),sha256=row['sha256'],bytes=path.stat().st_size));assert value['profileVersion']==row['profileVersion'];selected.append(value)
  return dict(schemaVersion=1,state='TASK_SELECTION342_NORMAL_OFF_BUILD_SOURCE_ADMISSION_PASSED_V1',variant='normal-off',taskSelectionSourceIndexSha256=g.SOURCE_SHA,freezerSourceIndexSha256=frame['config']['freezerIndex']['sha256'],configuredSourceRoot=str(g.SOURCE),configuredLayerRoot=str(layer.HERE),metadata=refs['metadata'],metadataClassifier=result,sourceManifest=metadata['sourceManifest'],externalSourceManifest=metadata['componentizeSourceManifest'],selectedManifestRows=metadata['selectedModuleManifests'],selectedManifests=selected,taskSelectionPolicy=metadata['taskSelectionPolicy'],resourceOwnershipPolicy=metadata['resourceOwnershipPolicy'],sourceFiles=342,externalSources=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=5,engineHashedAsGuardData=True,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
 finally:g.recheck(frame)
