"""Source-only checks; never executes JavaScript, a fixture, import, constructor or host."""
from pathlib import Path
import ast
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def main():
    count = 0

    def need(value, why):
        nonlocal count
        assert value is True, why
        count += 1

    spec = importlib.util.spec_from_file_location('pure_probe_text_assembly', HERE / 'build-entry.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    rendered = builder.render()
    plan = json.loads((HERE / 'plan.json').read_text())
    cases = (HERE / 'cases.mjs').read_text()
    tail = (HERE / 'guest-tail.mjs.in').read_text()
    need(plan['actionsAllowed'] is False, 'No Source action permission')
    for key in ['actualNativeBuild', 'actualEngine', 'actualNativeMetadata', 'actualConstructor',
                'actualComponent', 'actualNodeControl', 'actualGuestProbe', 'actualRuntime',
                'constructionPlan', 'rootAuthority']:
        need(plan[key] is None, 'No actual role: ' + key)
    need(plan['plannedNodeReference']['executed'] is False and
         plan['plannedNodeReference']['actualResult'] is None, 'No invented Node oracle')
    need(plan['modes']['guard']['expectedCases'] == len(plan['modes']['guard']['caseIds']) == 2,
         'Finite guard contract')
    need(plan['modes']['interop']['expectedCases'] == len(plan['modes']['interop']['caseIds']) == 16,
         'Finite interop contract')
    need(plan['modes']['guard']['guardRefusalIsNodeCompatibilityPass'] is False,
         'Guard refusal is an explicit compatibility gap')
    need(plan['request'] == {'method': 'GET', 'path': '/probe', 'query': '', 'requestsPerComponent': 1,
         'readiness': 'TCP-only future host readiness; no HTTP warmup consumes the single probe',
         'runtimeModeSelection': 'literal Source entry, never request/env', 'bodyDelaysOrTimers': False},
         'One predeclared GET; no environment mode or HTTP retry')
    need(plan['worldSourceIndex']['sha256'] == '802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58' and
         plan['worldName'] == 'next-http' and len(set(plan['selectedInterfaces'])) == 13,
         'Existing complete standard world')
    need(all(x.endswith('@0.2.10') for x in plan['selectedInterfaces']), 'Exact standard interface version')
    need(plan['fixturePolicy']['stagingPerformed'] is False and plan['fixturePolicy']['writesByGuest'] is False,
         'No private fixture staging or guest writes')
    need(plan['fixturePolicy']['physicalModesAreNotProofOfReadOnlyWasiRights'] is True,
         'Physical mode scope honest')
    expected = ['class.cjs', 'driver.cjs', 'nan.cjs', 'negative-zero.cjs', 'target.cjs',
                'thenable.cjs', 'throw-null.cjs', 'undefined.cjs']
    need([x['relativePath'] for x in plan['fixtureFiles']] == expected, 'Exact eight Source fixtures')
    need(sorted(p.name for p in (HERE / 'fixtures').iterdir()) == expected, 'No extra fixture payload')
    for row in plan['fixtureFiles']:
        need(builder.descriptor(HERE / 'fixtures' / row['relativePath']) == row['source'], 'Fixture bytes')
        need(row['guestPath'] == '/probe/' + row['relativePath'], 'Declared future guest path')
    need((HERE / 'fixtures/driver.cjs').read_text().count('return import(specifier)') == 1,
         'Natural CJS dynamic import expression, compiled by genuine loader later')
    need('await import(\'node:module\')' in cases and 'const require = createRequire(\'/probe/driver.cjs\')' in cases,
         'Installed Module only inside deployed collector')
    need(cases.index('export async function collectFileUrlProbe') < cases.index("await import('node:module')") <
         cases.index("require('/probe/driver.cjs')"), 'No top-level require or fixture read')
    need('ERR_SM_MODULE_IMPORT_REFERRER' in cases and "'module_load_hook', targetUrl" in cases,
         'Actual guard diagnostic contract')
    need('ERR_SM_MODULE_FILE_URL_UNSUPPORTED' in cases and "'module_file_url', url" in cases,
         'Actual interop refusal contract')
    need("sameJoin = namespace.join === builtin.join" in cases, 'Builtin path checks actual function identity')
    need("Object.is(namespace.default, expected)" in cases and
         "Object.getOwnPropertyNames(namespace)" in cases and "names[0] === 'default'" in cases,
         'Namespace default identity and own namespace surface')
    need('Object.getOwnPropertyNames(expected)' not in cases and 'Object.keys(expected)' not in cases,
         'No enumeration of export object')
    need('await namespace.default' not in cases and 'return namespace.default' not in cases and
         '.then(ns =>' not in cases and 'Promise.resolve(namespace.default)' not in cases,
         'Tester never assimilates default export')
    need('value.inspectThenReads()' in cases and 'thenReads === 0' in cases,
         'Actual then getter side-effect counter is observed as a scalar')
    need("new namespace.default(7)" in cases and 'Constructor.prototype' in cases,
         'Class default genuine construction checks')
    need('Number.isNaN(value)' in cases and 'Object.is(value, -0)' in cases and 'value === undefined' in cases,
         'Primitive semantics use actual JS operations')
    need('result.value === null' in cases and "!Object.hasOwn(require.cache, path)" in cases,
         'Falsy throw and real failed-load cache outcome')
    for key in ['query-refusal', 'fragment-refusal', 'encoded-separator-refusal', 'uppercase-scheme-refusal',
                'extension-refusal', 'url-byte-limit-refusal', 'decoded-path-limit-refusal']:
        need(key in cases and key in plan['modes']['interop']['caseIds'], 'Selected profile refusal: ' + key)
    need("'x'.repeat(12297)" in cases and "'x'.repeat(4096)" in cases,
         'Finite declared native URL/path bounds, no namespace-cap loop')
    need('bootstrap();' in tail and tail.index('async function prepareFileUrlProbe') < tail.index('bootstrap();'),
         'Bootstrap ordinary-only')
    need("if (++calls !== 1)" in tail and "request.method !== 'GET'" in tail and "url.search !== ''" in tail,
         'Single exact request path and no second collection')
    need('setTimeout' not in cases + tail and 'fetch(' not in cases + tail and 'Math.random' not in cases + tail,
         'No probe timers/network/entropy')
    need('ScriptPrivate' not in cases + tail and 'eval(' not in cases + tail and 'new Function' not in cases + tail,
         'No private metadata mutation or Function fallback')
    for mode, text in rendered.items():
        need((HERE / ('guest-' + mode + '.mjs')).read_text() == text, 'Exact actual text assembly ' + mode)
        need(text.count('function disposeBeforeEntry(') == 1 and text.count('function probeOwnData(') == 1,
             'No helper name collision ' + mode)
        need(text.count('export const incomingHandler') == 1 and text.count('@MODE@') == 0,
             'Only actual standard incoming handler export ' + mode)
    need(rendered['guard'].replace("const fileUrlProbeMode = 'guard';", "const fileUrlProbeMode = 'interop';") ==
         rendered['interop'], 'Only literal mode differs between entries')
    for path in HERE.glob('*.py'):
        tree = ast.parse(path.read_text())
        need(not any(isinstance(node, (ast.Import, ast.ImportFrom)) and
                     any(name.name in ['subprocess', 'socket'] for name in node.names) for node in ast.walk(tree)),
             'Source helpers have no actor imports ' + path.name)
    print(json.dumps(dict(sourceOnly=True, passed=True, checks=count,
                         sourceAssemblyChecked=True, javascriptParsedOrExecuted=False,
                         fixturesStaged=False, actualNodeControl=None, actualGuestProbe=None,
                         compilerConstructorEngineHostOrImportInvoked=False)))


if __name__ == '__main__':
    main()
