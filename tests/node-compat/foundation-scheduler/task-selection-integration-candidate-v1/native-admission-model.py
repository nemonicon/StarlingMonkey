"""Pure future raw-metadata classifier. No engine/helper/import or authority action."""
def validate_metadata(metadata, policy, policy_sha256, helper_sha256, recipe_sha256, external_sources, variant):
    assert variant == 'normal-off'
    assert metadata.get('diagnosticOnly', False) is False and metadata.get('syntheticMetadataOnly', False) is False
    assert metadata['buildRecipeSha256'] == recipe_sha256
    assert metadata['sourceManifest'] == policy['expectedNativeSourceManifest']
    assert len(metadata['sourceManifest']) == len({r['path'] for r in metadata['sourceManifest']}) == 342
    assert metadata['componentizeSourceManifest'] == external_sources and len(external_sources) == 3
    assert metadata['gcStress'] is (variant == 'gc-off') and metadata['entropyPolicy'] == 'off' and metadata['oomTesting'] is False
    assert metadata['debuggerEnabled'] is False and metadata['wptSupportEnabled'] is False
    for name in ('profileEnabled','internalTicksEnabled','classicStreamsEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled'):
        assert metadata[name] is True
    assert metadata['internalTickPolicy']['version'] == policy['version']
    assert metadata['internalTickPolicy']['policyFileSha256'] == policy_sha256
    assert metadata['internalTickPolicy']['helperSha256'] == helper_sha256
    assert metadata['strictEventExceptionPolicy']['version'] == policy['strictPolicyVersion']
    assert metadata['protectedAbortListenerPolicy']['version'] == policy['protectedPolicyVersion']
    actual = metadata['resourceOwnershipPolicy']
    assert actual['sourcePolicy'] == policy['resourceOwnershipSourcePolicy']
    assert actual['policyFileSha256'] == policy_sha256 and actual['helperSha256'] == helper_sha256
    assert actual['nativeRuntimeValidation'] is None and actual['fullResetOrReuse'] is False
    assert actual['timerInstallation']['webTimersEnabled'] == 'ON'
    for key in ('requestedCMakeOptions','observedCMakeOptions'):
        assert metadata[key]['CMAKE_BUILD_TYPE'] == 'Release'
        assert metadata[key]['ENABLE_BUILTIN_WEB_TIMERS'] == 'ON'
        assert metadata[key]['NODE_COMPAT_GC_STRESS'] == ('ON' if variant == 'gc-off' else 'OFF')
    selected = metadata['taskSelectionPolicy']
    assert selected['sourcePolicy'] == policy['taskSelectionSourcePolicy']
    assert selected['policyFileSha256'] == policy_sha256 and selected['helperSha256'] == helper_sha256
    assert selected['allNativeDependentsRequireRebuild'] is True and selected['nativeAllInvalidRuntimeValidation'] is None and selected['fullResetOrReuse'] is False
    for field in ('actualHostApiCompileCommands','actualEventLoopCompileCommands'):
        assert type(selected[field]) is list and len(selected[field]) == 1 and type(selected[field][0]) is str
    # Actual independent native/freezer proof still must verify each captured
    # file, command, install/library/tool source and the real engine descriptor.
    return dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY', nativeFiles=342,
                engineRead=False, runtimeAccepted=False, grantsAuthority=False)
