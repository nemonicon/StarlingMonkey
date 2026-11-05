"""Explicit342 source/compile layer; parent306 data is ancestry, never projection."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Source policy checks require assertions')
HERE=Path(__file__).resolve().parent
POLICY_SHA256='1f9d7de1115955c2fca5c171197eb85f5298f135dd9ea3bb5703412074aac842'
PARENT_POLICY_SHA256='98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0'
PARENT_HELPER_SHA256='78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert digest(HERE/'policy.json')==POLICY_SHA256
POLICY=json.loads((HERE/'policy.json').read_bytes())

# Exact previous342 source ancestry is data, never an engine metadata adapter.
def verify_resource_ancestry():
    previous=HERE.parents[1]/'foundation-classic-streams/trace-integration-candidate-v1'
    source=POLICY['resourceOwnershipSourcePolicy']
    assert digest(previous/'policy.json')==source['parentPolicySha256']
    assert digest(previous/'layer-policy.py')==source['parentHelperSha256']
    old=json.loads((previous/'policy.json').read_bytes())
    before={r['path']:r['sha256']for r in old['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in POLICY['expectedNativeSourceManifest']}
    assert len(before)==len(after)==342 and set(before)==set(after)
    assert sum(before[p]==after[p]for p in before)==340
    assert {r['path']for r in source['changes']}=={'builtins/web/timers.cpp','runtime/event_loop.cpp'}
    for r in source['changes']:assert before[r['path']]==r['beforeSha256']and after[r['path']]==r['afterSha256']
    assert POLICY['classicTraceSourcePolicy']==old['classicTraceSourcePolicy']
    assert POLICY['embedding']==old['embedding']and POLICY['nativePatchSha256']==old['nativePatchSha256']
    proposal=HERE.parent/'resource-ownership-candidate-v1'
    assert digest(proposal/'index.json')==source['sourceCandidateIndexSha256']
    for r in json.loads((proposal/'index.json').read_bytes())['files']:
        path=proposal/r['path'];assert not path.is_symlink()and path.stat().st_size==r['bytes']and digest(path)==r['sha256']
    peer=HERE.parent/'independent-resource-ownership-source-review-v1'
    assert digest(peer/'index.json')==source['sourceReviewIndexSha256']
    for r in json.loads((peer/'index.json').read_bytes())['files']:
        path=peer/r['path'];assert not path.is_symlink()and path.stat().st_size==r['bytes']and digest(path)==r['sha256']
    reviewed=json.loads((peer/'results.json').read_bytes())
    assert reviewed['state']=='INDEPENDENT_SCHEDULER_RESOURCE_OWNERSHIP_SOURCE_REVIEW_PASSED_V1'and reviewed['sourceIndexSha256']==source['sourceCandidateIndexSha256']and reviewed['sourceOnly']is True and reviewed['sourceReviewPassed']is True and reviewed['ownerActionsInvoked']is False
    return True
verify_resource_ancestry()
PARENT_ROOT=HERE.parent/'integration-candidate-v1'
assert digest(PARENT_ROOT/'policy.json')==PARENT_POLICY_SHA256
assert digest(PARENT_ROOT/'layer-policy.py')==PARENT_HELPER_SHA256
_spec=importlib.util.spec_from_file_location('classic_source_parent306',PARENT_ROOT/'layer-policy.py')
PARENT=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(PARENT)
assert POLICY['parentExpectedNativeSourceManifest']==PARENT.POLICY['expectedNativeSourceManifest']
def expected(relative,base_expected):
    parent=PARENT.expected(relative,base_expected)
    entry=POLICY['sourceLayer'].get(relative)
    if entry is None:return parent
    assert entry['beforeSha256']==parent,'Immediate306 ancestry mismatch: '+relative
    return entry['afterSha256']
def resolved(mapping):return{path:expected(path,value)for path,value in mapping.items()}
def source_manifest(repo):
    repo=Path(repo);rows=POLICY['expectedNativeSourceManifest']
    assert len(rows)==len({row['path']for row in rows})==342
    for row in rows:
        path=repo
        for part in row['path'].split('/'):
            assert part and part not in('.','..');path/=part;assert not path.is_symlink(),path
        assert path.is_file() and digest(path)==row['sha256'],'Unreviewed342 source: '+row['path']
    return copy.deepcopy(rows)
def validate_sources(repo,manifest=None):
    actual=source_manifest(repo)
    if manifest is not None:
        assert all(set(row)=={'path','sha256'}for row in manifest)
        assert sorted(manifest,key=lambda row:row['path'])==actual
    return True
def _macro(words,name,enabled):
    assert '-D'not in words and '-U'not in words,'Need joined captured macro arguments'
    values=[word for word in words if word=='-D'+name or word.startswith('-D'+name+'=')]
    assert values==(['-D'+name+'=1']if enabled else[]),'Conflicting/missing '+name
    assert '-U'+name not in words
def _release(words):
    assert [word for word in words if word.startswith('-O')]==['-O3'],'Exactly one Release optimization flag required'
    assert [word for word in words if word=='-DNDEBUG'or word.startswith('-DNDEBUG=')]==['-DNDEBUG'],'Exact NDEBUG definition required'
    assert '-UNDEBUG'not in words and '-UDEBUG'not in words and not any(word.startswith('-DDEBUG')for word in words)
    assert not any(word=='-DNODE_COMPAT_OOM_TESTING'or word.startswith('-DNODE_COMPAT_OOM_TESTING=')for word in words)
    assert '-UNODE_COMPAT_OOM_TESTING'not in words
def validate_classic_compilation(entries,embedding,repo,metadata):
    ticks=metadata['internalTicksEnabled'];classic=metadata['classicStreamsEnabled'];web=metadata['streamWebEnabled']
    assert all(type(value)is bool for value in[ticks,classic,web,metadata['eventsEnabled'],metadata['stringDecoderEnabled']])
    assert not(metadata['gcStress'] and metadata['entropyPolicy']=='runtime-only'),'RuntimeOnly+GC is outside this finite producer'
    if classic:assert ticks and metadata['eventsEnabled'] and metadata['stringDecoderEnabled']
    native,queue=PARENT.validate_compilation(entries,embedding,ticks,repo)
    cpp=[row['path']for row in POLICY['expectedNativeSourceManifest']if row['path'].endswith('.cpp')and row['path'].startswith(('builtins/','runtime/'))]
    active=[name for name in cpp if(ticks or name!='runtime/node_tick_queue.cpp')and(web or name!='builtins/node-compat/stream-web-kernel.cpp')]
    assert len(cpp)==61
    rows=[row for row in entries if row['file'].endswith('.cpp')and any(Path(row['file']).as_posix().startswith(str(Path(repo)/base)+'/')for base in['builtins','runtime'])]
    mapped={}
    private=[]
    for row in rows:
        names=[name for name in cpp if row['file']==str(Path(repo)/name)]
        assert len(names)==1 and names[0]not in mapped,'Unknown/duplicate native TU'
        name=names[0];mapped[name]=row['command'];words=shlex.split(row['command'])
        assert words.count('-c')==1 and '-fsyntax-only'not in words
        _release(words)
        _macro(words,'NODE_COMPAT_STRICT_INITIALIZATION',True)
        _macro(words,'NODE_COMPAT_INTERNAL_TICKS',ticks)
        _macro(words,'NODE_COMPAT_CLASSIC_STREAMS',classic and name in POLICY['privateTargetCpp'])
        _macro(words,'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER',metadata['eventsEnabled'])
        _macro(words,'NODE_COMPAT_STREAM_WEB',web and name.startswith('builtins/node-compat/'))
        _macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',metadata['entropyPolicy']=='runtime-only')
        _macro(words,'NODE_COMPAT_ENTROPY_POLICY',True)
        _macro(words,'NODE_COMPAT_GC_STRESS',metadata['gcStress'] and name in POLICY['privateTargetCpp'])
        if name in POLICY['privateTargetCpp']:private.append(row['command'])
    assert sorted(mapped)==sorted(active)
    for command in embedding:
        words=shlex.split(command);assert words.count('-c')==1 and '-fsyntax-only'not in words
        _release(words)
        _macro(words,'NODE_COMPAT_STRICT_INITIALIZATION',True)
        _macro(words,'NODE_COMPAT_INTERNAL_TICKS',ticks)
        _macro(words,'NODE_COMPAT_CLASSIC_STREAMS',False)
        _macro(words,'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER',metadata['eventsEnabled'])
        _macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',metadata['entropyPolicy']=='runtime-only')
        _macro(words,'NODE_COMPAT_ENTROPY_POLICY',True)
        _macro(words,'NODE_COMPAT_GC_STRESS',False)
    assert len(embedding)==1 and len(private)==(5 if web else 4)
    return native,queue,private
def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled):
    validate_sources(repo,metadata['sourceManifest'])
    assert type(enabled)is bool and metadata['internalTicksEnabled']is enabled
    choice='ON'if metadata['classicStreamsEnabled']else'OFF'
    for field in['requestedCMakeOptions','observedCMakeOptions']:
        assert metadata[field]['NODE_COMPAT_CLASSIC_STREAMS']==choice
    assert metadata['oomTesting']is False and metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'
    assert digest(Path(source_dir)/'embedding/embedding.cpp')==POLICY['embedding']['afterSha256']
    native,queue,private=validate_classic_compilation(entries,embedding_commands,repo,metadata)
    strict=metadata['strictEventExceptionPolicy'];protected=metadata['protectedAbortListenerPolicy']
    assert strict['version']==PARENT.POLICY['parentStrictPolicyVersion']
    assert protected['version']==PARENT.POLICY['parentProtectedPolicyVersion']
    strict['parentSourcePolicy']={key:copy.deepcopy(strict[key])for key in['version','patchSha256','basePolicy','embeddingBoundaryPatchSha256','nativeSourceSha256']}
    protected['parentSourcePolicy']={key:copy.deepcopy(protected[key])for key in['version','patchSha256','sourceSha256','strictPolicyVersion']}
    strict['version']=POLICY['strictPolicyVersion'];strict['nativeSourceSha256']=resolved(strict['nativeSourceSha256'])
    for name in['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h']:strict['nativeSourceSha256'][name]=PARENT.POLICY['sourceLayer'][name]['afterSha256']
    strict['actualNativeCompileCommands']+=queue
    protected['version']=POLICY['protectedPolicyVersion'];protected['strictPolicyVersion']=strict['version'];protected['sourceSha256']=resolved(protected['sourceSha256'])
    metadata['internalTickPolicy']={
      'version':POLICY['version'],'enabled':enabled,'sourcePolicyInstalled':True,
      'parentRecipeSha256':POLICY['parentRecipeSha256'],'parentNativeManifestCanonicalSha256':POLICY['parentNativeManifestCanonicalSha256'],
      'parentPrivateTickPolicyFileSha256':PARENT_POLICY_SHA256,'parentPrivateTickHelperSha256':PARENT_HELPER_SHA256,
      'sourceLayer':POLICY['sourceLayer'],'nativePatchSha256':POLICY['nativePatchSha256'],
      'embeddingPatchSha256':POLICY['embedding']['patchSha256'],'embeddingBeforeSha256':POLICY['embedding']['beforeSha256'],'embeddingAfterSha256':POLICY['embedding']['afterSha256'],
      'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'actualLayoutCompileCommands':native,'actualQueueCompileCommands':queue,'actualEmbeddingCompileCommands':embedding_commands,
      'requestedCMake':metadata['requestedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],'observedCMake':metadata['observedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],
      'limits':PARENT.POLICY['limits'],'addsExternalCapabilities':False,'publicProcessModule':False,
      'resetSafeReuse':'OPEN; cancellation and teardown not established',
      'scope':'Actual342 source/command observations; parent306 is immutable source ancestry, not projected engine metadata.'}
    metadata['classicTraceSourcePolicy']=copy.deepcopy(POLICY['classicTraceSourcePolicy'])
    cache=Path(metadata['cmakeCachePath']);values={}
    for line in cache.read_text().splitlines():
        key,sep,rest=line.partition(':')
        if sep and '='in rest:values[key]=rest.partition('=')[2]
    assert values['ENABLE_BUILTIN_WEB_TIMERS']=='ON'
    install=Path(values['INSTALL_BUILTINS']);text=install.read_text()
    assert text.count('NS_DEF(builtins::web::timers)')==1
    metadata['resourceOwnershipPolicy']={'sourcePolicy':copy.deepcopy(POLICY['resourceOwnershipSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'timerInstallation':{'path':str(install),'sha256':digest(install),'webTimersEnabled':'ON'},'nativeRuntimeValidation':None,'fullResetOrReuse':False}
    metadata['classicStreamsPolicy']={
      'version':POLICY['classicPolicyVersion'],'enabled':metadata['classicStreamsEnabled'],'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'parentRecipeSha256':POLICY['parentRecipeSha256'],'parentSourceManifestCanonicalSha256':POLICY['parentNativeManifestCanonicalSha256'],
      'nativePatchSha256':POLICY['nativePatchSha256'],'addedSourcePaths':POLICY['addedSourcePaths'],
      'actualPrivateTargetCompileCommands':private,'actualRegistrationCompileCommands':metadata['actualRegistrationCompileCommands'],
      'requestedCMake':choice,'observedCMake':choice,'addsExternalCapabilities':False,'publicProcessModule':False,
      'moduleManifest':POLICY['classicManifest'],'apiScope':'Large captured guest JS state machines over existing native byte primitives; partial Node22 contract; no performance claim.'}
    metadata['componentizeJsPatches'].append({'name':PARENT.POLICY['version']+'-boundary','baseRevision':metadata['componentizeJsRevision'],
       'path':str(PARENT_ROOT.parent/'taskqueue-owner-v2/componentize-taskqueue-ticks.UNAPPLIED.patch'),
       'sha256':POLICY['embedding']['patchSha256'],'applied':True,'files':['embedding/embedding.cpp']})
    return metadata
if __name__=='__main__':
    assert len(sys.argv)==2;validate_sources(sys.argv[1]);print('Exact342 classic source policy verified; no compiler or guest ran')
