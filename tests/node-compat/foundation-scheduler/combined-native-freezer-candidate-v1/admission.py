"""Genuine current355 configured producer/model APIs; no engine/compiler action."""
import importlib.util
from pathlib import Path

def admit(frame,g):
 g.require_frame(frame);g.recheck(frame);refs=frame['refs'];metadata=frame['metadata'];policy=frame['policy']
 try:
  row=refs['configuredModel'];g.checked(row)
  spec=importlib.util.spec_from_file_location('genuine_combined355_v2_metadata_model',row['path']);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
  result=model.validate_metadata(metadata,policy,refs['policy']['sha256'],refs['layer']['sha256'],refs['recipe']['sha256'],refs['externalSourceManifest'],'normal-off')
  assert result==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
  row=refs['layer'];g.checked(row)
  spec=importlib.util.spec_from_file_location('genuine_combined355_v2_producer_layer',row['path']);layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
  assert layer.HERE==Path(refs['layer']['path']).parent and layer.REPO==g.SOURCE and layer.POLICY==policy
  layer.validate_sources(g.SOURCE,metadata['sourceManifest'])
  native,queue,private=layer.validate_classic_compilation(frame['database'],metadata['actualEmbeddingCompileCommands'],g.SOURCE,metadata)
  assert len(native)==62 and len(queue)==1 and len(private)==6
  selected=[]
  for row in metadata['selectedModuleManifests']:
   path=g.SOURCE/row['path'];value=g.read(dict(path=str(path),sha256=row['sha256'],bytes=path.stat().st_size));assert value['profileVersion']==row['profileVersion'];selected.append(value)
  value=dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_BUILD_SOURCE_ADMISSION_PASSED_V1',variant='normal-off',nativeSourceIndexSha256=g.SOURCE_SHA,freezerSourceIndexSha256=frame['config']['freezerIndex']['sha256'],configuredSourceRoot=str(g.SOURCE),genuineLayerRoot=str(layer.HERE),metadata=refs['metadata'],metadataClassifier=result,sourceManifest=metadata['sourceManifest'],externalSourceManifest=metadata['componentizeSourceManifest'],selectedManifestRows=metadata['selectedModuleManifests'],selectedManifests=selected,sourcePolicies={k:metadata[k] for k in refs['copiedMetadataPolicyKeys']},privateRustupBootstrapPolicy=metadata['privateRustupBootstrapPolicy'],engineHashedAsGuardData=True,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
  value.update(g.COUNTS);return value
 finally:g.recheck(frame)
