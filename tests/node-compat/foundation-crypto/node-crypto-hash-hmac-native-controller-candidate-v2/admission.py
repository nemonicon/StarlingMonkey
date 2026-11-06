"""Read-only original7c5a new357/83 producer admission. No old355 classifier."""
from pathlib import Path
import importlib.util

def module(row,name,io):
 spec=importlib.util.spec_from_file_location(name,io.checked(row));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def admit(frame,recheck):
 io=frame['io'];refs=frame['refs'];recheck(frame)
 try:
  m=io.read(io.row(Path(refs['enginePath']+'.build.json')));policy=io.read(refs['policy'])
  assert m['enginePath']==refs['enginePath']and len(m)==83 and m['sourceManifest']==policy['expectedNativeSourceManifest']
  assert m['selectedModuleManifests']==policy['selectedModuleManifests']and len(m['selectedModuleManifests'])==12
  assert m['observedCMakeOptions']==m['requestedCMakeOptions']and m['gcStress']is m['oomTesting']is False and m['entropyPolicy']=='off'
  assert m['nodeCryptoHashHmacEnabled']is True and m['nodeCryptoAuditedBorrowEnabled']is False
  for key in ['cmakeCachePath','compileCommandsPath']:assert Path(m[key]).is_relative_to(Path(refs['workRoot']))
  io.checked(io.row(Path(m['cmakeCachePath'])));database=io.read(io.row(Path(m['compileCommandsPath'])));assert len(database)==69
  pure=module(refs['metadataModel'],'genuine_v2_producer_357_83_metadata_shape',io)
  observed=pure.validate_metadata(m,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
  assert observed==dict(state='FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=357,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
  layer=module(refs['helper'],'genuine_v2_357_current_producer',io)
  assert layer.HERE==Path(refs['helper']['path']).parent and layer.REPO==Path(refs['configuredSourceRoot'])and layer.POLICY==policy
  layer.validate_sources(layer.REPO,m['sourceManifest']);native,queue,private=layer.validate_classic_compilation(database,m['actualEmbeddingCompileCommands'],layer.REPO,m)
  assert len(native)==63 and len(queue)==1 and len(private)==7
  selected=[]
  for r in m['selectedModuleManifests']:
   p=layer.REPO/r['path'];v=io.read(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size));assert v['profileVersion']==r['profileVersion'];selected.append(v)
  hash_model=module(refs['hashModel'],'genuine_v2_hash_hmac_commands',io)
  hash_model.validate_hash_hmac_commands(database,m['actualEmbeddingCompileCommands'],layer.REPO,m,policy);hash_model.validate_selected_manifests(m,policy,selected)
  rust=m['privateRustupBootstrapPolicy'];assert rust['persistentSetting']=='disable'and rust['privateHomes']==dict(rustup=refs['workRoot']+'/rustup-home',cargo=refs['workRoot']+'/cargo-home')
  # beforeInstallRecord is historical JSON DATA; never recurse into its stale nested settings descriptor.
  io.checked(rust['beforeInstallRecord']);io.checked(rust['settingsAtBuildCompletion'])
  sdk=[r for r in m['downloadedArchives']if Path(r['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz'];assert len(sdk)==1 and sdk[0]['sha256']==refs['sdkArchive']['sha256']
  io.checked(dict(path=sdk[0]['path'],sha256=sdk[0]['sha256'],bytes=refs['sdkArchive']['bytes']))
  assert m['wasiSdkVersionFiles']and all(r['contents'].startswith('30.0\n')for r in m['wasiSdkVersionFiles'])
  return dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_SOURCE_ADMISSION_DATA_PASSED_V2',controllerSourceIndexSha256=frame['ownIndex']['sha256'],sourceIndexSha256=refs['integrationSourceIndex']['sha256'],configuredSourceRoot=refs['configuredSourceRoot'],genuineLayerRoot=str(layer.HERE),metadata=io.row(Path(refs['enginePath']+'.build.json')),metadataClassifier=observed,nativeSourceFiles=357,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,compileDatabaseRows=69,policyCpp=63,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,selectedManifests=selected,engineExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,liveEvpSnapshotAdmission=False)
 finally:recheck(frame)
