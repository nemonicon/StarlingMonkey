"""Review actual constructor/validator outputs before any ordinary guest call."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
REPO = HERE.parents[3]
GUARD = REPO / 'tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    if hashlib.sha256(GUARD.read_bytes()).hexdigest() != '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4':
        raise RuntimeError('Genuine current engine guard changed')
    spec = importlib.util.spec_from_file_location('current_engine_final_review', GUARD)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    context = guard.context()
    request = json.loads((HERE / 'construction-request.json').read_bytes())
    for ref in request['inputs']:
        guard.checked(ref)
    terminals = {}
    for name in ('componentize', 'validate-component', 'component-wit'):
        path = WORK / 'commands' / name / 'terminal.json'
        terminal = guard.document(guard.row(path))
        guard.require(terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and
                      not any(terminal[key] for key in ('remainingObservedPids', 'timeout', 'forcedCleanup',
                                                       'signals', 'interruptedSignals', 'errors')), 'Clean original tool: ' + name)
        for key in ('stdout', 'stderr'):
            guard.checked(terminal[key])
        terminals[name] = guard.row(path)
    output = Path(request['output'])
    result = guard.document(guard.row(output / 'result.json'))
    guard.require(result['state'] == 'FRESH_LIFECYCLE_COMPONENT_CAPTURED_UNREVIEWED_V1' and
                  result['engine'] == guard.ENGINE and result['nativeMetadata'] == guard.NATIVE_METADATA and
                  result['compilerSelection'] == request['compilerSelection'] and
                  result['inputEntry'] == request['entry'] and result['ordinaryExportInvoked'] is False,
                  'Actual constructor result roles')
    for ref in result['artifacts'].values():
        guard.checked(ref)
    wit_path = WORK / 'commands/component-wit/stdout.log'
    wit = wit_path.read_text()
    match = re.match(r'package root:component;\n\nworld root \{\n([^{}]*)\}\n', wit)
    guard.require(match is not None, 'Explicit top-level WIT world')
    imports, exports = [], []
    for line in match[1].splitlines():
        if not line.strip():
            continue
        declaration = re.fullmatch(r'  (import|export) ([a-z0-9:/@.-]+);', line)
        guard.require(declaration is not None, 'Only named selected standard interfaces')
        (imports if declaration[1] == 'import' else exports).append(declaration[2])
    expected = context['plan']['selectedInterfaces']
    guard.require(len(imports) == len(set(imports)) == 13 and set(imports) == set(expected), 'Exact selected thirteen imports')
    guard.require(exports == ['wasi:http/incoming-handler@0.2.10'], 'Sole standard incoming-handler export')
    returned = guard.document(result['artifacts']['returnedImports'])
    guard.require(all(type(pair) is list and len(pair) == 2 and all(type(value) is str for value in pair)
                      for pair in returned) and set(pair[0] for pair in returned) == set(imports), 'Complete API import groups')
    guard.require(len({tuple(pair) for pair in returned}) == len(returned), 'Unique returned import functions')
    preopens = json.loads((output / 'final-preopens.json').read_bytes())
    guard.require(preopens == [request['witDirectory']], 'Only selected parser preopen')
    guard.protect(context)
    review = dict(schemaVersion=1, state='ACTUAL_LIFECYCLE_COMPONENT_CONSTRUCTION_REVIEW_PASSED_V1',
                  passed=True, actualResult=guard.row(output / 'result.json'), artifacts=result['artifacts'],
                  engine=guard.ENGINE, nativeMetadata=guard.NATIVE_METADATA,
                  compilerSelection=request['compilerSelection'], guestSource=request['entry'],
                  constructorRequest=guard.row(HERE / 'construction-request.json'), terminals=terminals,
                  emittedWit=guard.row(wit_path), emittedImports=imports, emittedExports=exports,
                  returnedImportFunctions=len(returned), metadataKeys=len(context['metadata']),
                  genuineCurrentContextRechecked=True, ordinaryGuestExecuted=False,
                  freshCompilerValidatedForThisConstruction=True, originalCompilerByteIdentityClaimed=False,
                  productionProfilePromoted=False)
    guard.save(HERE / 'construction-review.json', review)
    print(json.dumps(dict(review=guard.row(HERE / 'construction-review.json'),
                          component=result['artifacts']['component'], interfaces=len(imports), importFunctions=len(returned))))


if __name__ == '__main__':
    main()
