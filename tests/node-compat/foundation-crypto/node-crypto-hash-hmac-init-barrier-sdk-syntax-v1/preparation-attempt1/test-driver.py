"""Synthetic source/argv/dependency tests only; never imports operational code."""
from pathlib import Path
import ast
import hashlib
import json
import os
import shlex

HERE = Path(__file__).resolve().parent
plan = json.loads((HERE / 'plan.json').read_bytes())
tree = ast.parse((HERE / 'run-sdk-syntax.py').read_text())
selected = ['clean_arguments', 'parse_dependencies', 'clean_terminal', 'check_authority']
namespace = dict(Path=Path, shlex=shlex, os=os, OUTPUT=Path(plan['outputRoot']),
                 UNIT_IDS=['entropy-policy', 'hash-hmac-kernel'])
for name in selected:
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'real-driver-pure-' + name, 'exec'), namespace)
checks = []


def check(label, condition):
    assert condition, label
    checks.append(label)


def refuses(label, callback):
    try:
        callback()
    except (AssertionError, ValueError):
        checks.append(label)
    else:
        raise AssertionError(label)


for unit in plan['units']:
    declared, kept, main, removed = namespace['clean_arguments'](unit['actualCompileRow']['command'])
    check(unit['id'] + ': exact original row retained', main == unit['actualCompileRow']['file'])
    check(unit['id'] + ': wrapper not executed', declared == plan['references']['compilerWrapper']['path'])
    check(unit['id'] + ': preserved arguments exact', kept == unit['preservedArguments'])
    check(unit['id'] + ': original -c and -o removed', {part[0] for part in removed} >= {'-c', '-o'})
    check(unit['id'] + ': syntax only', '-c' not in unit['argv'] and '-o' not in unit['argv'] and unit['argv'].count('-fsyntax-only') == 1)
    check(unit['id'] + ': own dependency output', unit['dependencyFile'].startswith(plan['outputRoot'] + '/dependencies/'))
    check(unit['id'] + ': real cwd retained', unit['cwd'] == unit['actualCompileRow']['directory'])
    check(unit['id'] + ': physical main planned', unit['privateMainPath'] == plan['outputRoot'] + '/native/builtins/node-compat/' + unit['id'] + '.cpp')
    for bad in ('-DDEBUG=1', '-DNODE_COMPAT_OOM_TESTING=1', '-DNODE_CRYPTO_AUDITED_BORROW=1', '@response.rsp', '-Xclang'):
        refuses(unit['id'] + ': rejects ' + bad, lambda b=bad: namespace['clean_arguments'](unit['actualCompileRow']['command'] + ' ' + b))

# A real counterexample to the donor's mixed-ordering comparison. Equal
# membership must pass even when Path component order differs from strings.
members = [Path('/scope/foo/a.h'), Path('/scope/foo.cpp')]
path_order = [str(p) for p in sorted(members)]
string_order = sorted(str(p) for p in members)
check('mixed Path/string ordering counterexample exists', path_order != string_order)
check('equal canonical string sets pass', set(path_order) == set(string_order))
check('missing member detected', set(path_order) != set(string_order[:-1]))
check('extra member detected', set(path_order) != set(string_order + ['/scope/extra.h']))

parse = namespace['parse_dependencies']
sample = 'syntax-only-test: ' + chr(92) + '\n /scope/main.cpp ' + chr(92) + '\n /scope/a' + chr(92) + ' b.h /scope/header.h\n'
check('make continuation and escaped space', parse(sample, 'syntax-only-test') == ['/scope/main.cpp', '/scope/a b.h', '/scope/header.h'])
check('CRLF continuation', parse('t: \\\r\n /a.h\n', 't') == ['/a.h'])
refuses('wrong dependency target denied', lambda: parse(sample, 'wrong'))
refuses('empty dependency list denied', lambda: parse('t:', 't'))
refuses('duplicate dependency denied', lambda: parse('t: /a /a', 't'))
refuses('malformed quoting denied', lambda: parse('t: "unfinished', 't'))
check('lexical dot-dot normalizes to pre-observed SDK path', os.path.abspath('/sdk/bin/../share/header.h') == '/sdk/share/header.h')
sample_row = plan['references']['donorDependencySample']
raw_sample = Path(sample_row['path']).read_bytes()
check('actual donor dependency text authenticated', hashlib.sha256(raw_sample).hexdigest() == sample_row['sha256'] and len(raw_sample) == sample_row['bytes'])
old_names = parse(raw_sample.decode(), 'syntax-only-script-loader')
check('actual donor emitted full dependency list parsed', len(old_names) == 1041)
ledger_row = plan['references']['inputLedger']
raw_ledger = Path(ledger_row['path']).read_bytes()
check('dependency comparison ledger authenticated', hashlib.sha256(raw_ledger).hexdigest() == ledger_row['sha256'] and len(raw_ledger) == ledger_row['bytes'])
old_indexed = {r['path'] for r in json.loads(raw_ledger)['files']}
normalized_old = [os.path.abspath(p) for p in old_names]
check('all 1040 non-main donor dependencies have prior provenance', all(p in old_indexed for p in normalized_old[1:]))
mapping = {r['name']: r['external-contents'] for r in plan['overlay']['roots']}
check('overlay has all three changed files', len(mapping) == 3)
check('VFS maps header to genuine private afterimage', mapping[plan['candidateFiles'][0]['before']['path']] == plan['candidateFiles'][0]['privatePath'])
check('no extra external embedding frontend', len(plan['units']) == 2 and plan['separateExternalEmbeddingTranslationUnits'] == 0)

clean = dict(allObservedOwnedGroupsGone=True, parentOwnedGroupGone=True, forcedCleanup=False,
             timeout=False, signals=[], errors=[], remainingObservedPids=[])
check('clean original monitor model accepted', namespace['clean_terminal'](clean))
for name, value in [('allObservedOwnedGroupsGone', False), ('parentOwnedGroupGone', False),
                    ('forcedCleanup', True), ('timeout', True), ('signals', [15]),
                    ('errors', ['snapshot']), ('remainingObservedPids', [123])]:
    check('rejects unclean ' + name, not namespace['clean_terminal'](dict(clean, **{name: value})))

authority = json.loads((HERE / 'root-authority-template.json').read_bytes())
index = dict(path=str(HERE / 'index.json'), sha256='synthetic-only', bytes=1)
grant = dict(authority, driverPreparationIndex=index, sourceReview={'synthetic': True}, syntaxOnlyCompilerAllowed=True)
namespace['check_authority'](grant, plan, index)
check('positive synthetic finite authority shape', True)
refuses('unissued template denied', lambda: namespace['check_authority'](authority, plan, index))
for name, value in [('outputRoot', '/different'), ('timeoutSecondsPerUnit', 61),
                    ('units', ['hash-hmac-kernel']), ('cryptoAllowed', True),
                    ('engineAllowed', True), ('sourceIndex', None), ('sourceReview', None)]:
    refuses('authority refuses ' + name, lambda n=name, v=value: namespace['check_authority'](dict(grant, **{n: v}), plan, index))

check('compiler execution absent from preparation', plan['actualCompilerTranslationUnits'] == 0 and plan['compilerAuthorization'] is None)
check('preflight bookends not falsely reported', plan['currentExecutionInputHashBookendsPerformed'] is False)
check('external output still absent', not Path(plan['outputRoot']).exists())
print(json.dumps(dict(schemaVersion=1, state='SYNTHETIC_DRIVER_CHECKS_PASSED', checks=len(checks),
      cases=checks, compilerHelperMonitorEngineCryptoInvoked=False), indent=2))
