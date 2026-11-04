"""UNAPPLIED producer validation layer. No build/import side effects; no guest hooks."""
import copy,hashlib,json,pathlib,shlex
HERE=pathlib.Path(__file__).resolve().parent
# Replaced only by prepare-integration.py before the proposal is frozen.
POLICY_SHA256='98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0'
def digest(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def load_policy():
    path=HERE/'policy.json'
    assert digest(path)==POLICY_SHA256,'Unreviewed private scheduler policy'
    return json.loads(path.read_text())
POLICY=load_policy()
def expected(relative,base_expected):
    entry=POLICY['sourceLayer'].get(relative)
    if not entry:return base_expected
    assert entry['beforeSha256']==base_expected,'Policy ancestry mismatch: '+relative
    return entry['afterSha256']
def resolved(source_map):return {p:expected(p,d) for p,d in source_map.items()}
def validate_sources(repo,manifest=None):
    repo=pathlib.Path(repo)
    expected_inputs=POLICY['expectedNativeSourceManifest']
    assert len(expected_inputs)==306 and len({i['path'] for i in expected_inputs})==306
    for entry in expected_inputs:
        path=repo/entry['path']
        assert not path.is_symlink() and path.is_file(),path
        for ancestor in path.relative_to(repo).parents:assert not (repo/ancestor).is_symlink(),path
        assert digest(path)==entry['sha256'],'Unreviewed scheduler source input: '+entry['path']
    if manifest is not None:
        assert all(set(i)=={'path','sha256'} for i in manifest)
        assert len(manifest)==len({i['path'] for i in manifest})==306
        assert sorted(manifest,key=lambda i:i['path'])==expected_inputs,'Unexpected/missing native input'
    return True

def validate_compilation(entries,embedding_commands,enabled,repo):
    assert type(enabled) is bool
    repo=pathlib.Path(repo)
    native=[i['command'] for i in entries if i['file'].endswith('.cpp') and
            any(pathlib.Path(i['file']).as_posix().startswith(str(repo/d)+'/') for d in ['builtins','runtime'])]
    assert native and embedding_commands,'Need actual native AND external embedding compiler observations'
    flag='-DNODE_COMPAT_INTERNAL_TICKS=1'
    for command in native+embedding_commands:
        words=shlex.split(command)
        assert '-c' in words and '-fsyntax-only' not in words,'Need actual engine compile, not syntax proof'
        assert (flag in words)==enabled,'Inconsistent scheduler layout macro'
        assert '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in words
    queue=[i['command'] for i in entries if i['file'].endswith('/runtime/node_tick_queue.cpp')]
    assert len(queue)==int(enabled),'Queue TU must compile exactly once only when selected'
    for suffix in ['/runtime/engine.cpp','/runtime/event_loop.cpp','/builtins/node-compat/register.cpp']:
        assert sum(i['file'].endswith(suffix) for i in entries)==1,'Missing/duplicate layout TU: '+suffix
    return native,queue

def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled):
    assert type(enabled) is bool
    validate_sources(repo,metadata['sourceManifest'])
    assert metadata['requestedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS']==('ON' if enabled else 'OFF')
    assert metadata['observedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS']==('ON' if enabled else 'OFF')
    assert metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'
    assert metadata['oomTesting'] is False
    assert digest(pathlib.Path(source_dir)/'embedding/embedding.cpp')==POLICY['embedding']['afterSha256']
    native,queue=validate_compilation(entries,embedding_commands,enabled,repo)
    strict=metadata['strictEventExceptionPolicy'];protected=metadata['protectedAbortListenerPolicy']
    assert strict['version']==POLICY['parentStrictPolicyVersion']
    assert protected['version']==POLICY['parentProtectedPolicyVersion']
    # Historical ancestry has no invented current compilation observations.
    strict_parent={k:copy.deepcopy(strict[k]) for k in ['version','patchSha256','basePolicy','embeddingBoundaryPatchSha256','nativeSourceSha256']}
    protected_parent={k:copy.deepcopy(protected[k]) for k in ['version','patchSha256','sourceSha256','strictPolicyVersion']}
    strict['parentSourcePolicy']=strict_parent
    strict['version']=POLICY['strictPolicyVersion']
    strict['nativeSourceSha256']=resolved(strict['nativeSourceSha256'])
    for name in ['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h']:
        strict['nativeSourceSha256'][name]=POLICY['sourceLayer'][name]['afterSha256']
    strict['actualNativeCompileCommands']=strict['actualNativeCompileCommands']+queue
    protected['parentSourcePolicy']=protected_parent
    protected['version']=POLICY['protectedPolicyVersion']
    protected['strictPolicyVersion']=strict['version']
    protected['sourceSha256']=resolved(protected['sourceSha256'])
    metadata['internalTicksEnabled']=enabled
    metadata['internalTickPolicy']={
      'version':POLICY['version'],'enabled':enabled,'sourcePolicyInstalled':True,
      'parentRecipeSha256':POLICY['parentRecipeSha256'],
      'parentNativeManifestCanonicalSha256':POLICY['parentNativeManifestCanonicalSha256'],
      'sourceLayer':POLICY['sourceLayer'],'nativePatchSha256':POLICY['nativePatchSha256'],
      'embeddingPatchSha256':POLICY['embedding']['patchSha256'],
      'embeddingBeforeSha256':POLICY['embedding']['beforeSha256'],
      'embeddingAfterSha256':POLICY['embedding']['afterSha256'],
      'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'actualLayoutCompileCommands':native,'actualQueueCompileCommands':queue,
      'actualEmbeddingCompileCommands':embedding_commands,
      'requestedCMake':metadata['requestedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],
      'observedCMake':metadata['observedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],
      'limits':POLICY['limits'],'addsExternalCapabilities':False,'publicProcessModule':False,
      'resetSafeReuse':'OPEN; cancellation and teardown not established',
      'scope':'Private tick source/compile selection only; ordinary component acceptance and ALS integration remain separate'}
    metadata['componentizeJsPatches'].append({
      'name':POLICY['version']+'-boundary','baseRevision':metadata['componentizeJsRevision'],
      'path':str(HERE.parent/'taskqueue-owner-v2/componentize-taskqueue-ticks.UNAPPLIED.patch'),
      'sha256':POLICY['embedding']['patchSha256'],'applied':True,'files':['embedding/embedding.cpp']})
    return metadata

if __name__=='__main__':
    import sys
    assert len(sys.argv)==2,'Source validation only: layer-policy.py REPO'
    validate_sources(sys.argv[1]);print('private scheduler source policy validated')
