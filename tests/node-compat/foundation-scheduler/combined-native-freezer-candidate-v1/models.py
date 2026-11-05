"""Finite combined355-v2 freezer DATA contracts; no import/action side effects."""
from pathlib import Path
import shlex
SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
ENGINE_SHA='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'
META_SHA='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'
COUNTS=dict(nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,rawMetadataFields=80,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredSourceRows=5,generatedNullCppRows=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6)

def metadata(metadata,policy,refs):
 assert len(metadata)==80 and metadata['engineSha256']==ENGINE_SHA and metadata['enginePath']==refs['engine']['path'] and metadata['engineBytes']==refs['engine']['bytes']
 assert metadata['buildRecipeSha256']==refs['recipe']['sha256']
 assert metadata['sourceManifest']==policy['expectedNativeSourceManifest'] and len({r['path'] for r in metadata['sourceManifest']})==355
 assert metadata['componentizeSourceManifest']==refs['externalSourceManifest']==policy['expectedComponentizeSourceManifest'] and len(refs['externalSourceManifest'])==3
 assert metadata['selectedModuleManifests']==refs['selectedManifests']==policy['selectedModuleManifests'] and len(refs['selectedManifests'])==11
 for name in ('resourceOwnershipPolicy','taskSelectionPolicy','zlibErrorSemanticsPolicy','combinedNativeSourcePolicy'):
  assert metadata[name]['policyFileSha256']==refs['policy']['sha256'] and metadata[name]['helperSha256']==refs['layer']['sha256']
 assert metadata['combinedNativeSourcePolicy']['configuredSourceRoot']==refs['configuredSourceRoot']
 assert metadata['combinedNativeSourcePolicy']['workRoot']==refs['workRoot']
 assert metadata['privateRustupBootstrapPolicy']==refs['privateRustupBootstrapPolicy']
 rust=metadata['privateRustupBootstrapPolicy'];assert rust['persistentSetting']=='disable' and rust['oldFailedWorkResumed'] is False
 assert rust['privateHomes']==dict(rustup=refs['workRoot']+'/rustup-home',cargo=refs['workRoot']+'/cargo-home')
 # beforeInstallRecord's nested settings descriptor is historical DATA, not a live path.
 assert rust['beforeInstallRecord']==refs['rustupBeforeRecord'] and rust['settingsAtBuildCompletion']==refs['rustupCurrentSettings']
 assert refs['rustupBeforeRecord']['bytes']==368 and refs['rustupCurrentSettings']['bytes']==107
 assert metadata['gcStress'] is metadata['oomTesting'] is metadata['debuggerEnabled'] is metadata['wptSupportEnabled'] is False
 assert metadata['entropyPolicy']=='off' and not metadata.get('diagnosticOnly',False) and not metadata.get('syntheticMetadataOnly',False)

def compilation(database,metadata,policy,refs):
 source=Path(refs['configuredSourceRoot']);work=Path(refs['workRoot'])
 cpp={str(source/r['path']) for r in policy['expectedNativeSourceManifest'] if r['path'].endswith('.cpp') and r['path'].startswith(('builtins/','runtime/'))};assert len(cpp)==62
 other={str(source/p) for p in ('host-apis/wasi-0.2.0/host_api.cpp','host-apis/wasi-0.2.0/host_call.cpp','host-apis/wasi-0.2.3/sockets.cpp','host-apis/wasi-0.2.10/bindings/bindings.c','crates/rust-hooks/src/wrappers.cpp')}
 null=str(Path(metadata['cmakeCachePath']).parent/'starling-raw.wasm/null.cpp')
 assert len(database)==len({r['file'] for r in database})==68 and {r['file'] for r in database}==cpp|other|{null}
 commands={r['file']:r['command'] for r in database};combined=metadata['combinedNativeSourcePolicy']
 assert set(combined['actualPolicyCppCompileCommands'])=={commands[p] for p in cpp}
 assert set(combined['actualOtherConfiguredCompileCommands'])=={commands[p] for p in other}
 assert combined['actualGeneratedNullCompileCommands']==[commands[null]]
 for name,count in (('strictEventExceptionPolicy',4),('classicStreamsPolicy',6)):
  key='actualNativeCompileCommands' if name=='strictEventExceptionPolicy' else 'actualPrivateTargetCompileCommands'
  assert len(metadata[name][key])==count and set(metadata[name][key]) <= {commands[p] for p in cpp}
 for field,name in (('actualHostApiCompileCommands','host-apis/wasi-0.2.0/host_api.cpp'),('actualEventLoopCompileCommands','runtime/event_loop.cpp')):
  assert metadata['taskSelectionPolicy'][field]==[commands[str(source/name)]]
 assert len(metadata['actualEmbeddingCompileCommands'])==1 and metadata['actualEmbeddingCompileCommands']==combined['actualSeparateEmbeddingCompileCommands']
 for row in database:
  words=shlex.split(row['command']);assert words.count('-c')==words.count('-o')==1 and words[words.index('-c')+1]==row['file'] and '-fsyntax-only' not in words
  assert [w for w in words if w.startswith('-O')]==['-O3'] and '-DNDEBUG' in words
  assert not any(w.startswith(('-DDEBUG','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY','@')) for w in words)
  expected_include=0 if row['file']==null else 1;assert words.count('-include')==expected_include
  if expected_include:assert words[words.index('-include')+1]==str(work/'spidermonkey-dist-release/include/js-confdefs.h')

def source_peer(value,own):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1'
 assert value['freezerSourceIndexSha256']==own['sha256'] and value['nativeSourceIndexSha256']==SOURCE_SHA
 assert value['sourceOnly'] is value['sourceReviewPassed'] is True
 for name in ('ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked'):assert value[name] is False

def root(value,own,refs):
 assert value['schemaVersion']==1 and value['state']=='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_FREEZE_V1' and value['phase']=='freeze' and value['variant']=='normal-off'
 assert value['nativeSourceIndexSha256']==SOURCE_SHA and value['freezerIndex']==own
 for key in ('configuredSourceRoot','workRoot','freezeRoot','externalOutputRoot'):assert value[key]==refs[key]
 for key,n in COUNTS.items():assert value[key]==n
 assert value['freezeAllowed'] is value['readOnlySourceAdmissionAllowed'] is value['postBuildNinjaCommandsAllowed'] is True
 assert value['externalParentDeadlineSeconds']==2400 and value['requiredStartFreeBytes']==2147483648 and value['gcStress'] is False and value['entropyMode']=='OFF'
 for key in ('buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):assert value[key] is False
 for key in ('actualFreezeResult','independentFreezeReview','reviewedEnginePins','runtimeAuthority'):assert value[key] is None
 for key in ('actualBuildReview','actualBuildContract','actualBuildResult','actualBuildRootObservation','engine','metadata'):assert value[key]==refs[key]

def admission(value,metadata,refs,own_sha):
 assert value['schemaVersion']==1 and value['state']=='COMBINED355_NORMAL_OFF_BUILD_SOURCE_ADMISSION_PASSED_V1' and value['variant']=='normal-off'
 assert value['nativeSourceIndexSha256']==SOURCE_SHA and value['freezerSourceIndexSha256']==own_sha
 assert value['configuredSourceRoot']==refs['configuredSourceRoot'] and value['genuineLayerRoot']==str(Path(refs['layer']['path']).parent)
 assert value['metadata']==refs['metadata'] and value['sourceManifest']==metadata['sourceManifest'] and value['externalSourceManifest']==metadata['componentizeSourceManifest']
 assert value['selectedManifestRows']==metadata['selectedModuleManifests'] and value['selectedManifests']==refs['selectedManifestValues']
 assert value['sourcePolicies']=={k:metadata[k] for k in refs['copiedMetadataPolicyKeys']}
 assert value['privateRustupBootstrapPolicy']==refs['privateRustupBootstrapPolicy']
 assert value['metadataClassifier']==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
 for key,n in COUNTS.items():assert value[key]==n
 assert value['engineHashedAsGuardData'] is True and value['engineExecuted'] is value['operationalAdmission'] is value['runtimeAcceptanceClaim'] is False
