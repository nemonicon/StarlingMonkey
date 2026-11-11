"""Review the new constructor's closed outputs and prepare a four-call test.

Reads the actual new-engine admission. No predecessor fixed-engine guard, tools,
or guest exports are invoked. Constructor/tool commands must have closed first.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-component-v1-first')
COMMANDS = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands')
RUNTIME = Path('/private/tmp/starling-node-compat/next-lifecycle-runtime-v3-clone-cancel-first')
TOOLS = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/tools-v2')
SELECTED = {'wasi:cli/environment@0.2.10', 'wasi:cli/stdout@0.2.10', 'wasi:cli/stderr@0.2.10',
    'wasi:clocks/monotonic-clock@0.2.10', 'wasi:clocks/wall-clock@0.2.10', 'wasi:random/random@0.2.10',
    'wasi:filesystem/types@0.2.10', 'wasi:filesystem/preopens@0.2.10',
    'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10',
    'wasi:http/types@0.2.10', 'wasi:http/outgoing-handler@0.2.10'}
INPUTS = {}


def row(path):
    p = Path(path)
    assert p.is_absolute() and p.resolve(strict=True) == p and p.is_file()
    before = p.stat()
    h = hashlib.sha256()
    with p.open('rb') as handle:
        for block in iter(lambda: handle.read(1024**2), b''):
            h.update(block)
    after = p.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == \
           (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=after.st_size)


def checked(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(ref['path']) == ref
    assert ref['path'] not in INPUTS or INPUTS[ref['path']] == ref
    INPUTS[ref['path']] = ref
    return Path(ref['path'])


def doc(ref):
    assert ref['bytes'] <= 32 * 1024**2
    p = checked(ref)
    value = json.loads(p.read_bytes())
    checked(ref)
    return value


def save(path, value):
    with path.open('x') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    return row(path)


def command(name, argv):
    folder = COMMANDS / name
    started_ref, terminal_ref = row(folder / 'started.json'), row(folder / 'terminal.json')
    started, terminal = doc(started_ref), doc(terminal_ref)
    assert started['argv'] == argv and started['pid'] == terminal['pid']
    assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is True
    assert terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is False
    assert terminal['forcedCleanup'] is False
    assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
    checked(terminal['stdout']); checked(terminal['stderr'])
    return started_ref, terminal_ref, terminal


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B without optimization')
    assert len(sys.argv) == 2, 'Supply the exact actual construction request SHA256'
    request_ref = row(HERE / 'construction-request.json')
    assert request_ref['sha256'] == sys.argv[1]
    request = doc(request_ref)
    assert request['state'] == 'ROOT_CLONE_CANCEL_ENGINE_CONSTRUCTION_V1'
    assert request['output'] == str(WORK) and request['ordinaryExportsAllowed'] is False
    for ref in request['inputs']:
        checked(ref)
    admission = doc(request['engineAdmission'])
    assert admission['state'] == 'CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1'
    assert admission['passed'] is admission['completeActualMetadataReviewed'] is admission['nativeBuildPassed'] is True
    assert admission['oldMetadataProjected'] is admission['guestExecuted'] is False
    assert admission['engine'] == request['engine']
    assert admission['nativeMetadata'] == request['nativeMetadata']
    metadata = doc(request['nativeMetadata'])
    assert sorted(metadata) == admission['metadataKeys'] == request['metadataKeys']
    assert metadata['engine'] == request['engine']
    node = '/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
    caller = BASE / 'clone-cancel-component-construction-v1/componentize.mjs'
    _, constructor_terminal, _ = command('clone-componentize', [node, str(caller), request_ref['path'], request_ref['sha256']])
    result_ref = row(WORK / 'result.json'); result = doc(result_ref)
    assert result['state'] == 'CLONE_CANCEL_LIFECYCLE_COMPONENT_CAPTURED_UNREVIEWED_V1'
    for key in ('engine', 'nativeMetadata', 'engineAdmission', 'compilerSelection'):
        assert result[key] == request[key]
    assert result['inputEntry'] == request['entry'] and result['ordinaryExportInvoked'] is False
    for ref in result['artifacts'].values():
        checked(ref)
    component = result['artifacts']['component']
    wasm_tools = row(TOOLS / 'wasm-tools/wasm-tools')
    assert wasm_tools['sha256'] == 'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
    validation_started, validation_terminal, _ = command('clone-validate-component', [wasm_tools['path'], 'validate', component['path']])
    wit_started, wit_terminal, wit_run = command('clone-component-wit', [wasm_tools['path'], 'component', 'wit', component['path']])
    wit = checked(wit_run['stdout']).read_text()
    match = re.match(r'package root:component;\n\nworld root \{\n([^{}]*)\}\n', wit)
    assert match is not None
    imports, exports = [], []
    for line in match[1].splitlines():
        if not line.strip():
            continue
        declaration = re.fullmatch(r'  (import|export) ([a-z0-9:/@.-]+);', line)
        assert declaration is not None
        (imports if declaration[1] == 'import' else exports).append(declaration[2])
    assert len(imports) == len(set(imports)) == 13 and set(imports) == SELECTED
    assert exports == ['wasi:http/incoming-handler@0.2.10']
    returned = doc(result['artifacts']['returnedImports'])
    assert all(type(pair) is list and len(pair) == 2 and all(type(v) is str for v in pair) for pair in returned)
    assert len({tuple(pair) for pair in returned}) == len(returned)
    assert {pair[0] for pair in returned} == set(imports)
    assert doc(row(WORK / 'final-preopens.json')) == [request['witDirectory']]
    collector = row(BASE / 'lifecycle-wasmtime-collector-v3/run-wasmtime.py')
    assert collector['sha256'] == '42c4939251a9f10bc33464493ed47c405f82d790dd7f742acf67997633c6d1cd'
    wasmtime = row(TOOLS / 'wasmtime/wasmtime')
    assert wasmtime['sha256'] == 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'
    references = [row(Path('/private/tmp/starling-node-compat') / name / 'result.json') for name in (
        'web-stream-context-candidate-v2-node-first', 'response-clone-cancel-candidate-v1-node-first',
        'response-clone-cancel-followup-candidate-v1-node-first')]
    protected = [request_ref, result_ref, request['engineAdmission'], request['engine'], request['nativeMetadata'],
        request['compilerSelection'], request['entry'], row(Path(__file__).resolve()), row(HERE / 'compare-results.mjs'),
        row(BASE / 'web-stream-context-component-v1/compare.mjs'), *references]
    for ref in protected:
        checked(ref)
    for ref in list(INPUTS.values()):
        checked(ref)
    assert not RUNTIME.exists()
    review = dict(schemaVersion=1, state='CLONE_CANCEL_COMPONENT_CONSTRUCTION_REVIEW_PASSED_V1',
        passed=True, actualResult=result_ref, artifacts=result['artifacts'], engine=request['engine'],
        nativeMetadata=request['nativeMetadata'], engineAdmission=request['engineAdmission'],
        compilerSelection=request['compilerSelection'], guestSource=request['entry'], constructorRequest=request_ref,
        constructorTerminal=constructor_terminal, validationTerminal=validation_terminal, witTerminal=wit_terminal,
        emittedWit=wit_run['stdout'], emittedImports=imports, emittedExports=exports,
        returnedImportFunctions=len(returned), metadataKeys=sorted(metadata), protectedInputsChecked=len(INPUTS),
        ordinaryGuestExecuted=False, oldMetadataProjected=False, productionProfilePromoted=False)
    review_ref = save(HERE / 'construction-review.json', review)
    runtime_request = dict(schemaVersion=1, state='ROOT_LIFECYCLE_COMPONENT_RUNTIME_REQUEST_V3',
        component=component, wasmtime=wasmtime, wasmTools=wasm_tools, runtimeSource=collector,
        protectedInputs=[review_ref, *protected], outputRoot=str(RUNTIME),
        validationStarted=validation_started, validationTerminal=validation_terminal,
        witStarted=wit_started, witTerminal=wit_terminal)
    runtime_ref = save(HERE / 'runtime-request.json', runtime_request)
    print(json.dumps(dict(review=review_ref, runtimeRequest=runtime_ref, component=component,
                         imports=len(imports), returnedImportFunctions=len(returned))))


if __name__ == '__main__':
    main()
