"""Prepare exact dormant frontend argv/VFS data; never execute a compiler."""
from pathlib import Path
import hashlib
import json
import shlex

OWN = Path(__file__).resolve().parent
REPO = OWN.parents[3]
BASE = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
OUT = Path('/private/tmp/starling-node-compat/native-als-v2-sdk-syntax-v1')
DONOR = REPO / 'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-sdk-syntax-v2/plan.json'

def row(path):
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

def stripped(words):
    result = []
    i = 1
    while i < len(words):
        if words[i] in ['-o', '-c', '-MF', '-MT', '-MQ']:
            i += 2
        elif words[i] in ['-MD', '-MMD', '-MP']:
            i += 1
        else:
            result.append(words[i]); i += 1
    return result

def main():
    assert not OUT.exists(), 'No old frontend output may be resumed'
    donor = json.loads(DONOR.read_text())
    db_row = donor['references']['compileDatabase']
    assert row(Path(db_row['path'])) == db_row
    db = json.loads(Path(db_row['path']).read_text())
    metadata_row = donor['references']['metadata']
    assert row(Path(metadata_row['path'])) == metadata_row
    metadata = json.loads(Path(metadata_row['path']).read_text())
    assert len(metadata) == 83  # BASE provenance only, never a new ALS frame.
    compiler = donor['compilerAlias']
    files = []
    for source in sorted((OWN / 'after').rglob('*')):
        if not source.is_file(): continue
        name = str(source.relative_to(OWN / 'after'))
        files.append({'relativePath': name, 'source': row(source),
                      'privatePath': str(OUT / 'native' / name),
                      'logicalPath': str(BASE / name)})
    overlay = {'version': 0, 'case-sensitive': True, 'use-external-names': False,
               'roots': [{'type': 'file', 'name': f['logicalPath'],
                          'external-contents': f['privatePath']} for f in files]}
    units = []
    for file in files:
        name = file['relativePath']
        if not name.endswith('.cpp'): continue
        if name.startswith('runtime/async_context_'):
            actual = next(r for r in db if r['file'] == str(BASE / 'runtime/engine.cpp'))
            role = 'new ALS runtime unit, derived from actual engine compile flags'
        else:
            actual = next(r for r in db if r['file'] == file['logicalPath'])
            role = 'actual existing translation-unit flags'
        flags = stripped(shlex.split(actual['command']))
        assert '-DNODE_COMPAT_ASYNC_LOCAL_STORAGE=1' not in flags
        assert not any(x.startswith('-DENABLE_JS_DEBUGGER') for x in flags)
        flags.append('-DNODE_COMPAT_ASYNC_LOCAL_STORAGE=1')
        unit_id = name.removesuffix('.cpp').replace('/', '-')
        # Give the driver an existing private main file, including for NEW CPPs.
        # Preserve original quoted-header lookup explicitly after its directory.
        argv = [compiler, *flags, '-iquote', str(Path(file['logicalPath']).parent),
                '-ivfsoverlay', str(OUT / 'overlay.json'), '-fsyntax-only',
                '-MD', '-MF', str(OUT / 'dependencies' / (unit_id + '.d')),
                '-MT', 'syntax-only-' + unit_id, file['privatePath']]
        units.append({'id': unit_id, 'role': role, 'actualCompileRow': actual,
                      'preservedArguments': flags[:-1], 'addedDefinition': flags[-1],
                      'logicalMainPath': file['logicalPath'], 'privateMainPath': file['privatePath'],
                      'addedQuotedIncludeDirectory': str(Path(file['logicalPath']).parent),
                      'argv': argv, 'cwd': actual['directory'], 'timeoutSeconds': 60,
                      'dependencyFile': str(OUT / 'dependencies' / (unit_id + '.d')),
                      'dependencyTarget': 'syntax-only-' + unit_id,
                      'executionStarted': False, 'actualTerminal': None})
    # The extension-api Task layout must match the actual external embedding.
    command = metadata['actualEmbeddingCompileCommands']
    assert len(command) == 1
    words = shlex.split(command[0]); main_path = words[words.index('-c') + 1]
    flags = stripped(words)
    assert not any(x.startswith('-DENABLE_JS_DEBUGGER') for x in flags)
    flags.append('-DNODE_COMPAT_ASYNC_LOCAL_STORAGE=1')
    unit_id = 'separate-componentize-embedding'
    units.append({'id': unit_id, 'role': 'separate external embedding header/ABI frontend only',
                  'actualCompileCommand': command[0], 'preservedArguments': flags[:-1],
                  'addedDefinition': flags[-1],
                  'argv': [compiler, *flags, '-ivfsoverlay', str(OUT / 'overlay.json'), '-fsyntax-only',
                           '-MD', '-MF', str(OUT / 'dependencies' / (unit_id + '.d')),
                           '-MT', 'syntax-only-' + unit_id, main_path],
                  'cwd': str(Path(main_path).parents[1]), 'timeoutSeconds': 60,
                  'dependencyFile': str(OUT / 'dependencies' / (unit_id + '.d')),
                  'dependencyTarget': 'syntax-only-' + unit_id,
                  'executionStarted': False, 'actualTerminal': None})
    assert len(units) == 13
    reference_names = ['compileDatabase', 'metadata', 'engine', 'inputLedger', 'aliasInventory',
                       'compilerLeaf', 'compilerWrapper', 'monitorIndex', 'python', 'processObserver']
    plan = {'schemaVersion': 1, 'state': 'DORMANT_NATIVE_ALS_V2_SDK_SYNTAX_PLAN_V1',
            'references': {**{k: donor['references'][k] for k in reference_names}, 'donorPlan': row(DONOR)},
            'baseRawMetadataFields': 83, 'baseMetadataIsNewAlsMetadata': False,
            'candidateFiles': files, 'overlay': overlay, 'units': units,
            'outputRoot': str(OUT), 'protectedTrees': donor['protectedTrees'],
            'absentIncludePolicies': donor['absentIncludePolicies'],
            'externalEmbeddingInputs': donor['externalEmbeddingInputs'],
            'requiredBeforeAndFinal': ['own source/plan/Root descriptors and identities',
                'four complete existing SDK/SM/Source/OpenSSL trees excluding original Source .git',
                'exact unused absent textcodec include path and physical ancestors',
                'all selected aliases; all candidate private copies; external embedding3',
                'each actual .d dependency resolves to a preauthenticated virtual or physical input'],
            'successRequires': ['all13 actual started argv equal this plan',
                'all13 raw0/no signals/interruptedSignals/timeouts/errors/remainingPids and groups gone',
                'complete stdout/stderr for every attempted command, including failures',
                'all13 dependency files parsed and all protection bookends passed'],
            'rootAuthority': None, 'sourceReview': None, 'compilerAuthorization': None,
            'actualOutput': None, 'compilerExecuted': False,
            'objectLinkBuildEngineGuestCryptoGcOomResetActionsAllowed': False,
            'scope': 'ALS delta on real9aec Source; final whole Next composition requires its own generated profile'}
    (OWN / 'sdk-plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    print(json.dumps({'units': len(units), 'virtualSourceFiles': len(files),
                      'compilerExecuted': False, 'outputExists': OUT.exists()}))

if __name__ == '__main__': main()
