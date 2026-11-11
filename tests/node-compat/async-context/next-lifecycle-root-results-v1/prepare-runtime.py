"""Bind the real validated component to the finite Wasmtime collector."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
OUTPUT = Path('/private/tmp/starling-node-compat/next-lifecycle-runtime-v1-first')


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    review_ref = row(HERE / 'construction-review.json')
    if review_ref['sha256'] != '8c6174c7454cdcc5f906fe6f8cd566a6b9e37c015e40970cea2e7a94e72f191f':
        raise RuntimeError('Original construction review changed')
    review = json.loads((HERE / 'construction-review.json').read_bytes())
    component = review['artifacts']['component']
    if row(component['path']) != component or review['passed'] is not True:
        raise RuntimeError('Reviewed component changed')
    runtime_source = row(HERE / 'run-wasmtime.py')
    if runtime_source['sha256'] != '9e70d5098ca196e348a4bebaac6170baebabffc1c5ba4aafdf6f27a4df39cbba':
        raise RuntimeError('Frozen runtime collector changed')
    wasmtime = row(Path('/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime'))
    if wasmtime['sha256'] != 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c':
        raise RuntimeError('Pinned Wasmtime changed')
    wasm_tools = row(Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/cache/wasm-tools/1448/wasm-tools'))
    if wasm_tools['sha256'] != 'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d':
        raise RuntimeError('Pinned wasm-tools changed')
    if OUTPUT.exists():
        raise RuntimeError('Preserve existing runtime output')
    protected = [review_ref, review['actualResult'], review['engine'], review['nativeMetadata'],
                 review['compilerSelection'], review['guestSource'], review['constructorRequest'],
                 row(HERE / 'compare-results.mjs'), row(HERE / 'prepare-runtime.py'),
                 row(HERE.parent / 'web-stream-context-component-v1/compare.mjs'),
                 row(Path('/private/tmp/starling-node-compat/web-stream-context-candidate-v2-node-first/result.json')),
                 row(Path('/private/tmp/starling-node-compat/response-clone-cancel-candidate-v1-node-first/result.json'))]
    request = dict(schemaVersion=1, state='ROOT_LIFECYCLE_COMPONENT_RUNTIME_REQUEST_V1',
                   component=component, wasmtime=wasmtime, wasmTools=wasm_tools,
                   runtimeSource=runtime_source, protectedInputs=protected, outputRoot=str(OUTPUT))
    for role, directory in [('validation', 'validate-component'), ('wit', 'component-wit')]:
        for suffix, file in [('Started', 'started.json'), ('Terminal', 'terminal.json')]:
            request[role + suffix] = row(WORK / 'commands' / directory / file)
    with (HERE / 'runtime-request.json').open('x') as handle:
        json.dump(request, handle, indent=2)
        handle.write('\n')
    print(json.dumps(row(HERE / 'runtime-request.json')))


if __name__ == '__main__':
    main()
