"""Read-only exact-byte/JSON/AST checks; no JS, helper, guard or target evaluation."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def read(path):
    return json.loads(path.read_text())


def main():
    count = 0

    def check(value):
        nonlocal count
        assert value
        count += 1

    plan = read(HERE / 'plan.json')
    derivation = read(HERE / 'derivation.json')
    check(set(plan['entries']) == set(plan['variants']) == {'B', 'D'})
    check(plan['variants'] == derivation['variants'])
    for name in ['B', 'D']:
        variant = plan['variants'][name]
        parent_path = Path(variant['parentEntry']['path'])
        entry_path = Path(variant['entry']['path'])
        check(row(parent_path) == variant['parentEntry'])
        check(row(Path(variant['parentSourceIndex']['path'])) == variant['parentSourceIndex'])
        check(row(entry_path) == variant['entry'] == plan['entries'][name])
        check(entry_path.parent == HERE and entry_path.name == 'guest-entry-' + name.lower() + '.mjs')
        parent, entry = parent_path.read_text(), entry_path.read_text()
        before, after = variant['onlyReplacement']['before'], variant['onlyReplacement']['after']
        check(before == '          return handler.handle(incoming,outparam);')
        check(after == '          return await handler.handle(incoming,outparam);')
        check(parent.count(before) == entry.count(after) == 1)
        check(parent.replace(before, after) == entry)
        check(entry.replace(after, before) == parent)
        check(len(entry.encode()) == len(parent.encode()) + 6)
        check(entry.count('await ') == parent.count('await ') + 1)
        check(entry[:entry.index(after)] == parent[:parent.index(before)])
        for token in ['.getReader(', '.getWriter(', '.tee(', 'disposeBeforeEntry(', 'runFreshRequest(']:
            check(entry.count(token) == parent.count(token))
        check('completionHolder' not in entry and 'child-handler-promise-' not in entry)
        check('NEXT_GUEST_PROMISE_COMPLETION_V1' not in entry)
        for key in ['actualConstructor', 'actualComponent', 'actualImportFunctionCount', 'actualRuntime']:
            check(variant[key] is None)
        old_plan = read(Path(variant['parentSourceIndex']['path']).parent / 'plan.json')
        for key in ['worldSourceIndex', 'witDirectory', 'worldName', 'witInputs', 'selectedInterfaces',
                    'componentExports', 'facadeReferences']:
            check(plan[key] == old_plan[key])
    b = (HERE / 'guest-entry-b.mjs').read_text()
    d = (HERE / 'guest-entry-d.mjs').read_text()
    check('NEXT_GUEST_RESPONSE_COMPLETION_V1' not in b)
    parent_d = Path(plan['variants']['D']['parentEntry']['path']).read_text()
    check(d.count('NEXT_GUEST_RESPONSE_COMPLETION_V1') == parent_d.count('NEXT_GUEST_RESPONSE_COMPLETION_V1') == 3)
    logger_start = parent_d.index('let __guestCompletionState;')
    logger_end = parent_d.index('function createWasiHttpHandler(', logger_start)
    check(parent_d[logger_start:logger_end] in d)
    historical = plan['responseLogger']['D']['historicalContract']
    check(row(Path(historical['path'])) == historical)
    check(plan['responseLogger']['D']['currentWholeContractClaim'] is False)
    check(derivation['wholeHistoricalContractAdopted'] is False)
    check(plan['worldSourceIndex']['sha256'] == '802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58')
    check(Path(plan['worldSourceIndex']['path']).parent == Path(plan['witDirectory']))
    check(len(plan['selectedInterfaces']) == len(set(plan['selectedInterfaces'])) == 13)
    check(all(name.endswith('@0.2.10') for name in plan['selectedInterfaces']))
    check(plan['componentExports'] == ['wasi:http/incoming-handler@0.2.10'])
    check(len(plan['witInputs']) == 8 and len(plan['facadeReferences']) == 6)
    for ref in plan['witInputs'] + plan['facadeReferences']:
        check(row(Path(ref['path'])) == ref)
    for key in ['requiredFullNativeBuildReview', 'requiredCleanupSourceIndex', 'requiredCompiledRequestResponse',
                'requiredCompiledModuleLoader', 'requiredCurrentInteropRuntimeReview']:
        check(row(Path(plan[key]['path'])) == plan[key])
    build = read(Path(plan['requiredFullNativeBuildReview']['path']))
    check(build['verifiedPassed'] is True)
    check(plan['requiredEngine'] == build['engine'] and plan['requiredNativeMetadata'] == build['metadata'])
    check(plan['requiredCurrentInteropRuntimeReview']['sha256'] == '55a255e7fd932133b144e32e7c7c26ecb31ad3403a5a0b8112f13c67fef13b17')
    check(plan['oldAsyncReturnAlreadyAdoptedPromise'] is True and plan['missingAwaitFix'] is False)
    check(plan['guaranteedExtraMicrotaskCount'] is None and plan['cd60HolderOrChildPromiseLoggerIncluded'] is False)
    for key in ['actualEngine', 'actualNativeMetadata', 'actualRootAuthority', 'actualConstructor',
                'actualComponent', 'actualImportFunctionCount', 'actualRuntime']:
        check(plan[key] is None)
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
        check(True)
    print(json.dumps(dict(state='EXACT_RETURN_AWAIT_VARIANTS_SOURCE_CHECKS_PASSED_V1', checks=count,
        passed=True, entries=2, byteDeltaPerEntry=6, addedCodeAwaitsPerEntry=1,
        javaScriptOrNodeExecuted=False, helperGuardOrActorExecuted=False,
        targetBinaryPayloadHashed=False, actualConstructorOrRuntime=None)))


if __name__ == '__main__':
    main()
