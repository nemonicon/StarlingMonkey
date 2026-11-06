"""Pure own357/82 diagnostic metadata-shape gate; never an engine/runtime/adoption API."""
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
    wanted = {'CMAKE_BUILD_TYPE':'Release','WEVAL':'OFF','USE_WASM_OPT':'ON',
              'ENABLE_BUILTIN_NODE_COMPAT':'ON','ENABLE_BUILTIN_WEB_TIMERS':'ON',
              'ENABLE_BUILTIN_WEB_CRYPTO':'ON','ENABLE_BUILTIN_WEB_TEXT_CODEC':'ON',
              'ENABLE_JS_DEBUGGER':'OFF','ENABLE_BUILTIN_WPT_SUPPORT':'OFF',
              'NODE_COMPAT_LOCKED_RUST':'ON','NODE_COMPAT_GC_STRESS':'OFF',
              'NODE_COMPAT_OOM_TESTING':'OFF','NODE_COMPAT_ENTROPY_MODE':'OFF',
              'CMAKE_C_COMPILER_LAUNCHER':'','CMAKE_CXX_COMPILER_LAUNCHER':''}
    for flag in ('PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB',
                 'INTERNAL_TICKS','CLASSIC_STREAMS','ZLIB','STREAM_CONSUMERS'):
        wanted['NODE_COMPAT_'+flag]='ON'
    for key,value in wanted.items():
        for field in ('requestedCMakeOptions','observedCMakeOptions'):
            assert metadata[field][key] == value, (field,key)
    assert len(metadata['selectedModuleManifests']) == 11
    assert metadata['selectedModuleManifests'] == policy['selectedModuleManifests']
    assert metadata['internalTickPolicy']['version'] == policy['version']
    assert metadata['internalTickPolicy']['policyFileSha256'] == policy_sha256
    assert metadata['internalTickPolicy']['helperSha256'] == helper_sha256
    assert metadata['strictEventExceptionPolicy']['version'] == policy['strictPolicyVersion']
    assert metadata['protectedAbortListenerPolicy']['version'] == policy['protectedPolicyVersion']
    assert len(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']) == 4
    assert len(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands']) == 6
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
    assert fresh['state'] == 'ACTUAL_FRESH_CLOCK_DIAGNOSTIC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V2'
    assert fresh['configuredSourceRoot'] == policy['contexts']['configuredSourceRoot']
    assert fresh['workRoot'] == policy['contexts']['workRoot']
    assert fresh['sourceDir'] == combined['externalConfiguredSourceRoot']
    assert fresh['buildDir'] == metadata['cmakeCachePath'].rsplit('/',1)[0]
    assert fresh['artifact'] == metadata['enginePath']
    assert fresh['sourceDirExisted'] is fresh['buildDirExisted'] is fresh['artifactExisted'] is False
    assert fresh['compilerLauncherReuseAllowed'] is False
    assert fresh['rustIncrementalReuseAllowed'] is False
    assert combined['runtimeValidation'] is None and combined['operationalAdmission'] is False
    validate_diagnostic_fields(metadata,policy)
    assert set(metadata)==set(policy['expectedRawMetadataFields']) and len(metadata)==82
    return {'state':'FINITE_CLOCK_DIAGNOSTIC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V2',
            'nativeFiles':357,'rawMetadataFields':82,'engineRead':False,'runtimeAccepted':False,'grantsAuthority':False}

# Own pure source-policy assembly. Accepts SOURCE policy data, never metadata.
def assemble_policy(spec,base):
    import copy
    assert spec['state']=='CLOCK_DIAGNOSTIC357_OWN_SOURCE_POLICY_V2'
    assert len(base['expectedNativeSourceManifest'])==355
    diagnostic=spec['diagnosticSourcePolicy']
    assert diagnostic['parentExpectedNativeSourceManifest']==base['expectedNativeSourceManifest']
    before={r['path']:r['sha256']for r in base['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in spec['expectedNativeSourceManifest']}
    assert len(after)==357 and len(after.keys()-before.keys())==2
    assert sum(before[p]==after[p]for p in before)==349
    assert len(diagnostic['changes'])==6 and len(diagnostic['added'])==2
    for r in diagnostic['changes']:assert before[r['path']]==r['beforeSha256']and after[r['path']]==r['afterSha256']
    for r in diagnostic['added']:assert r['path']not in before and after[r['path']]==r['sha256']
    assert diagnostic['publicSelectedWholeManifests']==base['selectedModuleManifests']and len(base['selectedModuleManifests'])==11
    assert len(spec['expectedComponentizeSourceManifest'])==3
    value=copy.deepcopy(base)
    for key in ['contexts','expectedNativeSourceManifest','expectedComponentizeSourceManifest','admissionModelSha256','expectedRawMetadataFields','diagnosticSourcePolicy']:value[key]=copy.deepcopy(spec[key])
    value['combinedSourcePolicy']={'version':'sm-combined-clock-diagnostic357-v2','parentCombined355Policy':copy.deepcopy(base['combinedSourcePolicy']),'diagnosticSourcePolicy':copy.deepcopy(diagnostic)}
    return value

def classify_diagnostic_commands(policy,entries,embedding,requested,observed):
    import shlex
    assert requested==observed
    for k in ['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','ENABLE_BUILTIN_WEB_PERFORMANCE']:assert observed[k]=='ON'
    root=policy['contexts']['configuredSourceRoot'];work=policy['contexts']['workRoot']
    by_file={r['file']:r['command']for r in entries};assert len(by_file)==len(entries)==69
    native=[r['path']for r in policy['expectedNativeSourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))]
    assert len(native)==63 and all(root+'/'+p in by_file for p in native)
    names=policy['diagnosticSourcePolicy']['sharedNativeTUs'];assert len(names)==len(set(names))==6
    assert len(embedding)==1
    commands=[dict(partition='native',source=p,command=by_file[root+'/'+p])for p in names]
    words=shlex.split(embedding[0]);assert words.count('-c')==1
    external=words[words.index('-c')+1];assert external.startswith(work+'/')and external.endswith('/embedding/embedding.cpp')
    assert '-I'+root+'/include'in words
    commands.append(dict(partition='external-embedding',source='embedding/embedding.cpp',command=embedding[0]))
    for r in commands:
        words=shlex.split(r['command']);source=root+'/'+r['source']if r['partition']=='native'else external
        assert words.count('-c')==1 and words[words.index('-c')+1]==source and '-fsyntax-only'not in words
        assert '--target=wasm32-wasi'in words and '-fno-exceptions'in words
        assert [x for x in words if x.startswith('-O')]==['-O3']and words.count('-DNDEBUG')==1
        macro='NODE_COMPAT_LIFECYCLE_DIAGNOSTICS'
        assert [x for x in words if x=='-D'+macro or x.startswith('-D'+macro+'=')]==['-D'+macro+'=1']and '-U'+macro not in words
        for m in ['DEBUG','NODE_COMPAT_GC_STRESS','NODE_COMPAT_OOM_TESTING','NODE_COMPAT_CRYPTO_HASH_HMAC','NODE_CRYPTO_AUDITED_BORROW']:
            assert not any(x=='-D'+m or x.startswith('-D'+m+'=')for x in words)
        assert '-UNDEBUG'not in words
    return commands

def validate_diagnostic_fields(metadata,policy):
    source=metadata['clockLifecycleDiagnosticSourcePolicy'];evidence=metadata['clockLifecycleDiagnosticBuildEvidence']
    assert source==policy['diagnosticSourcePolicy']and source['diagnosticOnly']is True
    assert source['sourceDefaultsOff']is source['namedBuildDiagnosticsOn']is True
    assert source['privateModuleAddedToPublicManifest']is False
    assert source['runtimeValidation']is None and source['operationalAdmission']is False
    assert len(evidence['actualSharedCompileCommands'])==7
    commands=metadata['combinedNativeSourcePolicy']['actualPolicyCppCompileCommands']+metadata['combinedNativeSourcePolicy']['actualOtherConfiguredCompileCommands']+metadata['actualEmbeddingCompileCommands']
    assert all(r['command']in commands for r in evidence['actualSharedCompileCommands'])
    import shlex
    database=metadata['combinedNativeSourcePolicy']['actualPolicyCppCompileCommands']+metadata['combinedNativeSourcePolicy']['actualOtherConfiguredCompileCommands']+metadata['combinedNativeSourcePolicy']['actualGeneratedNullCompileCommands']
    entries=[]
    for command in database:
        words=shlex.split(command);assert words.count('-c')==1
        entries.append(dict(file=words[words.index('-c')+1],command=command))
    assert evidence['actualSharedCompileCommands']==classify_diagnostic_commands(policy,entries,metadata['actualEmbeddingCompileCommands'],metadata['requestedCMakeOptions'],metadata['observedCMakeOptions'])
    assert evidence['actualPolicyCpp']==63 and evidence['actualDatabaseRows']==69 and evidence['actualNodePrivateCpp']==6 and evidence['actualSeparateEmbeddingCpp']==1
    install=evidence['actualInstallation'];assert install['namespace']=='NS_DEF(diagnostics::clock_lifecycle)'and install['count']==1 and install['performanceTargetEnabled']is True
    for k in ['actualLinkedInlineStateIdentityProved','actualStrongGetterLinkProved','nativeClockOrSelectorRuntimeInvoked','fullSeventeenGateAccepted','operationalAdmission']:assert evidence[k]is False
    assert evidence['runtimeValidation']is None
