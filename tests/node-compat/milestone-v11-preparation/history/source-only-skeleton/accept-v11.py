#!/usr/bin/env python3
"""Unexecuted v11 acceptance skeleton. No archive/staging write path is enabled."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/starling-node-compat/foundations-v11')
FREEZE = BASE / 'native-freeze'
RECIPE = '354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754'
CORE = 'sm-node-22.14.0-m0.11'
MACRO = '-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'
HTTP_IMPORTS = sorted(['wasi:http/types@0.2.10', 'wasi:io/error@0.2.10',
                      'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10',
                      'wasi:random/random@0.2.10', 'wasi:clocks/monotonic-clock@0.2.10'])
JOBS = {'core', 'allocator', 'stream-web', 'optional', 'strict-sync',
        'strict-runtime', 'strict-late', 'strict-callbacks'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def pinned_file(entry):
    assert entry and entry.get('path') and entry.get('sha256'), 'Final evidence pin missing'
    path = Path(entry['path'])
    if not path.is_absolute():
        path = REPO / path
    assert path.is_file() and not path.is_symlink()
    assert sha(path) == entry['sha256'], path
    return load(path)


def validate_native(pins):
    """Verify three new configurations; never add historical Events-OFF here."""
    assert set(pins['engines']) == {'off-foundations', 'runtime-foundations', 'gc-foundations'}
    engines = []
    for label, expected in pins['engines'].items():
        path = FREEZE / (label + '.engine.wasm')
        metadata = load(str(path) + '.build.json')
        assert sha(path) == metadata['engineSha256'] == expected['sha256']
        assert sha(str(path) + '.build.json') == expected['metadataSha256']
        assert metadata['buildRecipeSha256'] == sha(REPO / 'tests/node-compat/build-engine.sh') == RECIPE
        assert len(metadata['sourceManifest']) == 304
        assert len(metadata['componentizeSourceManifest']) == 3
        assert metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE'] == 'Release'
        assert metadata['observedCMakeOptions']['WEVAL'] == 'OFF'
        assert metadata['gcStress'] is (label == 'gc-foundations') and not metadata['oomTesting']
        assert metadata['entropyPolicy'] == ('runtime-only' if label == 'runtime-foundations' else 'off')
        assert metadata['protectedAbortListenerEnabled'] and metadata['strictInitialization']
        assert metadata['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3-protected-abort-v2'
        assert metadata['protectedAbortListenerPolicy']['patchSha256'] == '0d314f14e1eba2ed5ff1eed592697d5f6fab2be37d9568281ffec43864e2c3a1'
        assert not metadata['wptSupportEnabled'] and not metadata['debuggerEnabled']
        assert metadata['sourceInputsCapturedBeforeBuild'] and metadata['componentizeSourcesCapturedBeforeBuild']
        assert metadata['buildRecipeCheckedBeforeAndAfterBuild'] and metadata['generatedRustProject']['cargoBuildLocked']
        core = next(item for item in metadata['selectedModuleManifests']
                    if item['path'] == 'builtins/node-compat/export-manifest.node-v22.14.0.json')
        assert core['profileVersion'] == CORE
        for item in metadata['sourceManifest']:
            assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
            assert sha(REPO / item['path']) == sha(FREEZE / 'source' / item['path']) == item['sha256']
        for item in metadata['componentizeSourceManifest']:
            assert sha(FREEZE / 'componentize-source' / item['path']) == item['sha256']
        for path, value in pins['coreSourceSha256'].items():
            assert next(item['sha256'] for item in metadata['sourceManifest'] if item['path'] == path) == value
        assert sha(FREEZE / (label + '-CMakeCache.txt')) == metadata['cmakeCacheSha256']
        assert sha(FREEZE / (label + '-compile_commands.json')) == metadata['compileCommandsSha256']
        commands = load(FREEZE / (label + '-compile_commands.json'))
        cpp = [item['path'] for item in metadata['sourceManifest']
               if item['path'].endswith('.cpp') and item['path'].startswith(('builtins/', 'runtime/'))]
        layout = [item['command'] for item in commands
                  if any(item['file'].endswith('/' + path) for path in cpp)]
        assert len(layout) == 60 and layout == metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
        embedding = metadata['actualEmbeddingCompileCommands']
        assert len(embedding) == 1 and all(MACRO in shlex.split(command) for command in layout + embedding)
        engines.append(metadata)
    assert all(item['sourceManifest'] == engines[0]['sourceManifest'] for item in engines)
    assert all(item['componentizeSourceManifest'] == engines[0]['componentizeSourceManifest'] for item in engines)
    old = load(REPO / 'tests/node-compat/milestones/foundations-v10/off-foundations.engine.wasm.build.json')
    expected = {item['path']: item['sha256'] for item in old['sourceManifest']}
    assert len(pins['nativeChangesFromV10']) == 4
    for item in pins['nativeChangesFromV10']:
        assert expected[item['path']] == item['before']
        expected[item['path']] = item['after']
    assert {item['path']: item['sha256'] for item in engines[0]['sourceManifest']} == expected
    return engines


def validate_release(entry, off_sha):
    report = pinned_file(entry)
    assert report['state'] == 'passed' and len(report['jobs']) == 8
    assert {job['name'] for job in report['jobs']} == JOBS
    for job in report['jobs']:
        assert job['code'] == 0 and job['signal'] is None
        assert sha(job['reportPath']) == job['reportSha256']
        assert sha(job['logPath']) == job['logSha256']
        assert sha(job['runner']) == job['runnerSha256'] and job['emittedImports'] == []
        if job['name'] != 'optional':
            assert load(job['reportPath'])['engineSha256'] == off_sha
    assert sum(job['finalComponentAudits'] for job in report['jobs'] if job['name'].startswith('strict-')) == 24
    # Finalization must also authenticate v3's five reused successful reports,
    # six optional module reports/ten audits, and actual per-job source snapshots.
    return report


def validate_focused(final, pins):
    for name, label in [('focusedOff', 'off-foundations'), ('focusedRuntime', 'runtime-foundations')]:
        report = pinned_file(final[name])
        assert report['state'] == 'M11_ORDINARY_NATIVE_ADD_ABORT_LISTENER_PASSED'
        assert report['engineSha256'] == pins['engines'][label]['sha256']
        assert report['publicNodeGroups']['total'] == 29
        assert len(report['initializers']) == 8 and len(report['fatal']) == 5
        for group in ['main', 'aliases', 'benign']:
            assert [call['calls'] for call in report[group]['calls']] == [1, 2, 3]
    gc = pinned_file(final['focusedGc'])
    assert gc['state'] == 'M11_RELEASE_MOVING_GC_COMBINED_OWNER_GATE_PASSED'
    assert gc['engineSha256'] == pins['engines']['gc-foundations']['sha256']
    gap = pinned_file(final['callbackReturn'])
    assert gap['observationCompleted'] is True and gap['nodeCompatibilityPassed'] is False
    assert gap['node']['observed'] == {'ordinary': 1, 'protectedSignal': 1, 'alreadyAborted': 0}
    assert gap['jco']['observed'] == gap['wasmtime']['observed'] == {'ordinary': 0, 'protectedSignal': 0, 'alreadyAborted': 0}
    # Finalization requires deep 29-group oracle equality, own-error/CJS/snapshot,
    # exact 19 application components (8+8+2+1), imports and fatal/discard checks.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.parse_args()
    pins = load(HERE / 'draft-pins.json')
    assert pins['state'] == 'FINAL_REVIEWED_PINS_AND_COPY_CLOSURE_COMPLETE', (
        'Unfinalized source-only preparation: pending reports, copy closure and root review; no archive writes')
    raise SystemExit('Archive creation remains disabled until reviewed final validation and atomic copy implementation are complete')


if __name__ == '__main__':
    main()
