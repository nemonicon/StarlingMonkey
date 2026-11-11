"""Prepare a fresh constructor request from the genuine current engine context."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RESULTS = HERE.parent / 'next-lifecycle-root-results-v1'
FIXTURE = HERE.parent / 'web-stream-context-component-v1'
WORK = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
GUARD = REPO / 'tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
GUARD_SHA = '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4'
CAPTURE = REPO / 'tests/node-compat/frameworks/nextjs/next-node-fs-atomic-construction-v2/capture.mjs'
ADAPTER = Path('/private/tmp/starling-node-compat/next-preview1-adapter-v1/next-preview1-adapter.wasm')


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    if hashlib.sha256(GUARD.read_bytes()).hexdigest() != GUARD_SHA:
        raise RuntimeError('Genuine current engine guard changed')
    spec = importlib.util.spec_from_file_location('genuine_current_lifecycle_constructor', GUARD)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    state = guard.context()
    compiler_ref = guard.row(RESULTS / 'compiler-selection.json')
    compiler = guard.document(compiler_ref)
    if compiler['state'] != 'FRESH_COMPILER_PACKAGE_SELECTED_V1':
        raise RuntimeError('New compiler selection required')
    for ref in compiler['package']['files']:
        guard.checked({key: ref[key] for key in ('path', 'sha256', 'bytes')})
    adapter = guard.row(ADAPTER)
    if adapter['sha256'] != 'd30ade5b0a146ab1f6cbb878322fa937ec19c4a2b09f7497e9f08e49fb13cfd7':
        raise RuntimeError('Selected standard adapter changed')
    entry = guard.row(FIXTURE / 'guest-entry.mjs')
    fixture_files = [guard.row(path) for path in sorted(FIXTURE.rglob('*')) if path.is_file()]
    inputs = guard.unique(state['buildRefs'] + state['sourceRefs'] +
                          [guard.ENGINE, guard.NATIVE_METADATA, compiler_ref, adapter, guard.row(CAPTURE)] +
                          fixture_files + [guard.row(HERE / name) for name in ('prepare.py', 'componentize.mjs')])
    output = WORK / 'lifecycle-component-first'
    if output.exists():
        raise RuntimeError('Component output already exists; preserve it')
    request = dict(schemaVersion=1, state='ROOT_CURRENT_ENGINE_FRESH_COMPILER_CONSTRUCTION_V1',
                   engine=guard.ENGINE, nativeMetadata=guard.NATIVE_METADATA,
                   metadataKeys=sorted(state['metadata']), engineSelection=guard.row(RESULTS / 'engine-selection.json'),
                   genuineCurrentGuard=guard.row(GUARD), compilerSelection=compiler_ref,
                   entry=entry, capture=guard.row(CAPTURE), adapter=adapter,
                   witDirectory=state['plan']['witDirectory'], output=str(output), inputs=inputs,
                   ordinaryExportsAllowed=False, hostServicesAdded=False,
                   oldCompilerPackageIdentityClaimed=False, productionPromotionAllowed=False)
    guard.protect(state)
    guard.save(RESULTS / 'construction-request.json', request)
    print(json.dumps(dict(request=guard.row(RESULTS / 'construction-request.json'),
                          engineMetadataKeys=len(request['metadataKeys']), protectedInputs=len(inputs))))


if __name__ == '__main__':
    main()
