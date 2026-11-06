"""Pure new357 metadata-shape gate; never an engine/runtime/adoption API."""
def validate_metadata(metadata, policy, policy_sha256, helper_sha256,
                      recipe_sha256, external_sources, variant):
    assert variant == 'normal-off'
    assert metadata.get('diagnosticOnly', False) is False
    assert metadata.get('syntheticMetadataOnly', False) is False
    assert metadata['buildRecipeSha256'] == recipe_sha256
    assert metadata['sourceManifest'] == policy['expectedNativeSourceManifest']
    assert len(metadata['sourceManifest']) == len({r['path'] for r in metadata['sourceManifest']}) == 357
    assert metadata['componentizeSourceManifest'] == external_sources == policy['expectedComponentizeSourceManifest'] and len(external_sources) == 3
    for field in ('profileEnabled','internalTicksEnabled','classicStreamsEnabled','pathEnabled','eventsEnabled',
                  'stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled',
                  'zlibEnabled','streamConsumersEnabled','abiFixEnabled','bigIntFixEnabled','strictInitialization'):
        assert metadata[field] is True, field
    for field in ('gcStress','oomTesting','debuggerEnabled','wptSupportEnabled'):
        assert metadata[field] is False, field
    assert metadata['entropyPolicy'] == 'off'
    assert metadata['nodeCryptoHashHmacEnabled'] is True
    assert metadata['nodeCryptoAuditedBorrowEnabled'] is False
    assert len(metadata) == policy['expectedRawMetadataFields']
    assert sorted(metadata) == policy['expectedRawMetadataKeys']
    wanted = {'CMAKE_BUILD_TYPE':'Release','WEVAL':'OFF','USE_WASM_OPT':'ON',
              'ENABLE_BUILTIN_NODE_COMPAT':'ON','ENABLE_BUILTIN_WEB_TIMERS':'ON',
              'ENABLE_BUILTIN_WEB_CRYPTO':'ON','ENABLE_BUILTIN_WEB_TEXT_CODEC':'ON',
              'ENABLE_JS_DEBUGGER':'OFF','ENABLE_BUILTIN_WPT_SUPPORT':'OFF',
              'NODE_COMPAT_LOCKED_RUST':'ON','NODE_COMPAT_GC_STRESS':'OFF',
              'NODE_COMPAT_OOM_TESTING':'OFF','NODE_COMPAT_ENTROPY_MODE':'OFF',
              'CMAKE_C_COMPILER_LAUNCHER':'','CMAKE_CXX_COMPILER_LAUNCHER':'',
              'NODE_COMPAT_CRYPTO_HASH_HMAC':'ON','NODE_CRYPTO_AUDITED_BORROW':'OFF'}
    for flag in ('PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB',
                 'INTERNAL_TICKS','CLASSIC_STREAMS','ZLIB','STREAM_CONSUMERS'):
        wanted['NODE_COMPAT_'+flag]='ON'
    for key,value in wanted.items():
        for field in ('requestedCMakeOptions','observedCMakeOptions'):
            assert metadata[field][key] == value, (field,key)
    assert len(metadata['selectedModuleManifests']) == 12
    assert metadata['selectedModuleManifests'] == policy['selectedModuleManifests']
    assert metadata['internalTickPolicy']['version'] == policy['version']
    assert metadata['internalTickPolicy']['policyFileSha256'] == policy_sha256
    assert metadata['internalTickPolicy']['helperSha256'] == helper_sha256
    assert metadata['strictEventExceptionPolicy']['version'] == policy['strictPolicyVersion']
    assert metadata['protectedAbortListenerPolicy']['version'] == policy['protectedPolicyVersion']
    assert len(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']) == 4
    assert len(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands']) == 7
    assert metadata['cryptoKeyOwnershipPolicy'] == policy['cryptoKeyOwnershipSourcePolicy']
    assert metadata['cryptoSecretFailureSourcePolicy'] == policy['cryptoSecretFailureSourcePolicy']
    crypto=metadata['cryptoKeyOwnershipBuildEvidence']
    assert crypto['cryptoBuiltinEnabled'] is True and crypto['installationSource']['count'] == 1
    assert len(crypto['changedNativeCompileCommands']) == 3
    secret=metadata['cryptoSecretFailureBuildEvidence']
    assert secret['cryptoBuiltinEnabled'] is True and len(secret['changedNativeCompileCommands']) == 2
    assert secret['faultInjectionObserved'] is False and secret['runtimeValidation'] is None
    resource=metadata['resourceOwnershipPolicy']
    assert resource['sourcePolicy'] == policy['resourceOwnershipSourcePolicy']
    assert resource['policyFileSha256'] == policy_sha256 and resource['helperSha256'] == helper_sha256
    assert resource['timerInstallation']['webTimersEnabled'] == 'ON'
    assert resource['nativeRuntimeValidation'] is None and resource['fullResetOrReuse'] is False
    task=metadata['taskSelectionPolicy']
    assert task['sourcePolicy'] == policy['taskSelectionSourcePolicy']
    assert task['policyFileSha256'] == policy_sha256 and task['helperSha256'] == helper_sha256
    assert task['allNativeDependentsRequireRebuild'] is True and task['nativeAllInvalidRuntimeValidation'] is None
    assert task['fullResetOrReuse'] is False
    assert len(task['actualHostApiCompileCommands']) == len(task['actualEventLoopCompileCommands']) == 1
    errors=metadata['zlibErrorSemanticsPolicy']
    assert errors['sourcePolicy'] == policy['zlibErrorSemanticsSourcePolicy']
    assert errors['policyFileSha256'] == policy_sha256 and errors['helperSha256'] == helper_sha256
    assert errors['runtimeValidation'] is None and errors['remainingDeviationsApproved'] is False
    assert errors['remainingRecordedDifferences'] == 15
    zlib=metadata['zlibPolicy']
    assert zlib['moduleManifestSha256'] == policy['zlibManifestSha256']
    assert zlib['runtimeBackendProof'] == {'verified':False,'version':None,'vernum':None}
    witness=zlib['codecWitness']
    assert witness['selectedCompileInput'] == metadata['zlibSelectedCodecInput']
    assert witness['runtimeBackendProof'] == {'verified':False,'version':None,'vernum':None}
    assert witness['sourceInputsCheckedBeforeAndAfterBuild'] is True
    assert len(witness['actualKernelCompileCommands']) == 1
    assert metadata['streamConsumersPolicy']['moduleManifestSha256'] == policy['streamConsumersSourcePolicy']['moduleManifestSha256']
    assert metadata['streamConsumersPolicy']['installationOrder']['decoderBeforeNode'] is True
    combined=metadata['combinedNativeSourcePolicy']
    assert combined['sourcePolicy'] == policy['combinedSourcePolicy']
    assert combined['policyFileSha256'] == policy_sha256 and combined['helperSha256'] == helper_sha256
    assert combined['configuredSourceRoot'] == policy['contexts']['configuredSourceRoot']
    assert combined['workRoot'] == policy['contexts']['workRoot']
    assert combined['selectedManifests'] == policy['selectedManifestValues']
    assert combined['sourceManifestCheckedBeforeAndAfterBuild'] is True
    assert combined['actualCompileDatabaseRows'] == 69
    assert len(combined['actualPolicyCppCompileCommands']) == 63
    assert len(combined['actualOtherConfiguredCompileCommands']) == 5
    assert len(combined['actualGeneratedNullCompileCommands']) == 1
    assert len(combined['actualSeparateEmbeddingCompileCommands']) == 1
    commands=combined['actualPolicyCppCompileCommands']
    assert len(set(commands)) == 63
    assert metadata['internalTickPolicy']['actualLayoutCompileCommands'] == commands
    assert combined['actualSeparateEmbeddingCompileCommands'] == metadata['actualEmbeddingCompileCommands']
    assert set(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']) <= set(commands)
    assert set(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands']) <= set(commands)
    assert task['actualEventLoopCompileCommands'][0] in commands
    assert task['actualHostApiCompileCommands'][0] in combined['actualOtherConfiguredCompileCommands']
    assert combined['privateBackendEvidenceHookEnabled'] is False
    fresh=combined['freshAbiEvidence']
    assert fresh['state'] == 'ACTUAL_FRESH_HASH_HMAC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'
    assert fresh['configuredSourceRoot'] == policy['contexts']['configuredSourceRoot']
    assert fresh['workRoot'] == policy['contexts']['workRoot']
    assert fresh['sourceDir'] == combined['externalConfiguredSourceRoot']
    assert fresh['buildDir'] == metadata['cmakeCachePath'].rsplit('/',1)[0]
    assert fresh['artifact'] == metadata['enginePath']
    assert fresh['sourceDirExisted'] is fresh['buildDirExisted'] is fresh['artifactExisted'] is False
    assert fresh['compilerLauncherReuseAllowed'] is False
    assert fresh['rustIncrementalReuseAllowed'] is False
    assert combined['runtimeValidation'] is None and combined['operationalAdmission'] is False
    hash_policy=metadata['nodeCryptoHashHmacPolicy']
    assert hash_policy['sourcePolicy'] == policy['hashHmacSourcePolicy']
    assert hash_policy['enabled'] is True and hash_policy['auditedBorrowEnabled'] is False
    assert len(hash_policy['actualPrivateHashHmacMacroCompileCommands']) == 7
    assert len(hash_policy['actualRegistrationCompileCommands']) == len(hash_policy['actualKernelCompileCommands']) == 1
    assert hash_policy['actualInstallationOrder']['cryptoBeforeNode'] is True
    assert hash_policy['actualNinjaCapture']['rawExitCode'] == 0
    assert hash_policy['actualNinjaCapture']['timeout'] is False
    assert hash_policy['moduleManifest'] == policy['hashHmacSourcePolicy']['packagingManifestInput']
    assert hash_policy['actualNativeAliasIdentityValidated'] is False
    assert hash_policy['runtimeValidation'] is None and hash_policy['operationalAdmission'] is False
    assert hash_policy['borrowRuntimeAuthorized'] is False and hash_policy['algorithmOutputVerified'] is False
    assert metadata['privateRustupBootstrapPolicy']['persistentSetting'] == 'disable'
    return {'state':'FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',
            'nativeFiles':357,'engineRead':False,'runtimeAccepted':False,'grantsAuthority':False}
