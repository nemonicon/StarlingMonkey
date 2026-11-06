"""NEW proposed build-time pure functions, not an embedding API or runnable producer.
No metadata file is read, no previous classifier/helper is called, and no action
is performed at import. Full own357 helper/classifier/recipe remain unresolved.
"""
from pathlib import PurePosixPath
import copy
import shlex

MACRO='NODE_COMPAT_LIFECYCLE_DIAGNOSTICS'
NEW_FIELDS=('clockLifecycleDiagnosticSourcePolicy','clockLifecycleDiagnosticBuildEvidence')

def command_words(command, source, diagnostic=True):
    assert type(command) is str
    words=shlex.split(command)
    assert words.count('-c')==1 and words[words.index('-c')+1]==source
    assert '-fsyntax-only' not in words
    assert [x for x in words if x.startswith('-O')]==['-O3']
    assert [x for x in words if x=='-DNDEBUG' or x.startswith('-DNDEBUG=')]==['-DNDEBUG']
    assert '--target=wasm32-wasi' in words and '-fno-exceptions' in words
    found=[x for x in words if x=='-D'+MACRO or x.startswith('-D'+MACRO+'=')]
    if diagnostic:assert found==['-D'+MACRO+'=1'] and '-U'+MACRO not in words
    for forbidden in ['-DDEBUG','-UNDEBUG','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_CRYPTO_HASH_HMAC','-DNODE_CRYPTO_AUDITED_BORROW']:
        assert not any(x==forbidden or x.startswith(forbidden+'=') for x in words)
    return words

def classify_commands(plan, entries, embedding_commands, requested, observed):
    """Checks caller-supplied captured commands only, never runs a compiler."""
    assert requested==observed
    for name in ['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','ENABLE_BUILTIN_WEB_PERFORMANCE']:
        assert observed[name]=='ON'
    root=plan['contexts']['configuredSourceRoot']
    native_paths={r['path'] for r in plan['nativeSources'] if r['path'].endswith('.cpp') and r['path'].startswith(('builtins/','runtime/'))}
    assert len(native_paths)==63
    actual={r['file']:r for r in entries}
    assert len(entries)==len(actual)==69
    native={name:actual[root+'/'+name]['command'] for name in native_paths}
    assert len(native)==63
    for name,command in native.items():command_words(command,root+'/'+name,diagnostic=False)
    others=[r for r in entries if r['file'].startswith(root+'/') and not r['file'].startswith((root+'/builtins/',root+'/runtime/'))]
    generated=[r for r in entries if r['file'].endswith('/starling-raw.wasm/null.cpp')]
    assert len(others)==5 and len(generated)==1
    shared=[]
    for name in plan['sharedNativeTUs']:
        row=actual[root+'/'+name]
        command_words(row['command'],row['file'])
        shared.append(dict(partition='native',source=name,command=row['command']))
    assert len(embedding_commands)==1
    embedding_source=embedding_commands[0]['source']
    assert embedding_source.endswith('/embedding/embedding.cpp')
    assert embedding_source.startswith(plan['contexts']['workRoot']+'/')
    command_words(embedding_commands[0]['command'],embedding_source)
    shared.append(dict(partition='external-embedding',source='embedding/embedding.cpp',command=embedding_commands[0]['command']))
    return dict(kind='PURE_CAPTURED_COMMAND_CLASSIFICATION_ONLY',policyCpp=63,otherConfigured=5,generatedNull=1,
        databaseRows=69,separateEmbedding=1,sharedCommands=shared,engineRead=False,runtimeAccepted=False,
        newNativeBuildProved=False)

def diagnostic_fields(plan, classification, install_witness):
    """Returns ONLY two new fields from NEW actual caller observations in future.
    It cannot accept/project a parent355 or Hash357 metadata frame.
    """
    assert classification['kind']=='PURE_CAPTURED_COMMAND_CLASSIFICATION_ONLY'
    assert len(classification['sharedCommands'])==7
    assert install_witness['namespace']=='NS_DEF(diagnostics::clock_lifecycle)'
    assert install_witness['count']==1 and install_witness['performanceTargetEnabled'] is True
    assert set(plan['newTopLevelMetadataFields'])==set(NEW_FIELDS)
    return {
      NEW_FIELDS[0]:dict(diagnosticOnly=True,nativeSourceFiles=357,retainedParentNativeFiles=349,
        nativeAfterimages=6,newNativePaths=2,externalEmbeddingSources=3,
        publicSelectedWholeManifests=copy.deepcopy(plan['publicWholeManifests']),
        privateModule=plan['privateModuleSeparate'],privateModuleAddedToPublicManifest=False,
        sourceManifest=copy.deepcopy(plan['nativeSources']),externalManifest=copy.deepcopy(plan['externalSources']),
        defaultOff=True,runtimeValidation=None,operationalAdmission=False),
      NEW_FIELDS[1]:dict(diagnosticOnly=True,actualSharedCompileCommands=copy.deepcopy(classification['sharedCommands']),
        actualInstallation=copy.deepcopy(install_witness),proposedNativeCpp=63,proposedDatabaseRows=69,
        actualLinkedInlineStateIdentityProved=False,actualStrongGetterLinkProved=False,
        nativeClockOrSelectorRuntimeInvoked=False,fullSeventeenGateAccepted=False)
    }

def require_complete_wiring(wiring):
    needed=['ownFullHelper','ownFullClassifier','ownFullRecipe','ownPolicyAndDonorLayout','stageController','buildController','sourcePeer','rootAuthority']
    assert all(wiring.get(k) is not None for k in needed),'PARTIAL_SOURCE_ONLY: actual own producer/action wiring is absent'
