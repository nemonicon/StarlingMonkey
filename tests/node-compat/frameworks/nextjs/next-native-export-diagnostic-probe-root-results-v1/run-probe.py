"""Unbound Root controller: prepare, then collect exactly seventeen owned probe cases."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import traceback

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[4]
ACTOR_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-probe-runtime-v1/index.json', 'sha256': '72eb6fe422a64f42f083b9c2841c00e22702c03f85f75b6c724bdcadce756b89', 'bytes': 8138}
ACTOR_PLAN = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-probe-runtime-v1/plan.json', 'sha256': '8b8f6b53511a0885f6b5b3b7274d7f340e36b990ade1dfcf8fe32218cc1e3b28', 'bytes': 8414}
CONSTRUCTION_PREPARER = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-probe-root-results-v1/prepare-construction.py', 'sha256': '62142edc1a76bd7c47bc482737c16faa2364cde898ffb790aebf8a8ebf0859ef', 'bytes': 17890}
CONSTRUCTION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-probe-root-results-v1/actual-construction-review.json', 'sha256': '163eb782152b11c62be41165a5ea6a2130a70795b6d7490b477b0004b4646bca', 'bytes': 21317}
PYTHON = dict(path='/opt/homebrew/Cellar/python@3.11/3.11.10/Frameworks/Python.framework/Versions/3.11/bin/python3.11',
    sha256='b76df9b72b06c2592c34e234c10fb51a587fa4aaf3d57fd98325ea2774f4f758', bytes=52640)
AUTHORITY = HERE / 'diagnostic-probe-runtime-authority.json'
ORIGIN = 'http://127.0.0.1:61927'
RUN_ID = 'probe-237c-first'


def need(value, message):
    if not value:
        raise ValueError(message)


def row(value):
    p = Path(value)
    need(p.is_absolute() and p.resolve() == p and not any(q.is_symlink() for q in (p, *p.parents)), 'Canonical file')
    before = p.stat()
    need(p.is_file() and before.st_nlink == 1, 'Independent regular file')
    digest = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024**2), b''):
            digest.update(block)
    after = p.stat()
    need(all(getattr(before, k) == getattr(after, k) for k in
        ['st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns']), 'File read changed')
    return dict(path=str(p), sha256=digest.hexdigest(), bytes=before.st_size)


def checked(ref):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'} and
         type(ref['bytes']) is int and row(ref['path']) == ref, 'Exact descriptor')
    return Path(ref['path'])


def pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, 'Duplicate JSON key')
        out[key] = value
    return out


def document(ref):
    need(type(ref['bytes']) is int and 0 <= ref['bytes'] <= 16 * 1024**2, 'Finite JSON')
    p = checked(ref)
    value = json.loads(p.read_bytes(), object_pairs_hook=pairs)
    checked(ref)
    return value


def save(path, value):
    with path.open('x') as f:
        os.fchmod(f.fileno(), 0o600)
        f.write(json.dumps(value, indent=2) + '\n')
        f.flush()
        os.fsync(f.fileno())
    return row(path)


def module(ref, name):
    source = checked(ref)
    spec = importlib.util.spec_from_file_location(name, source)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    checked(ref)
    return value


def context():
    need(all(type(x) is dict for x in [ACTOR_INDEX, ACTOR_PLAN, CONSTRUCTION_PREPARER, CONSTRUCTION_REVIEW]),
         'Unbound runtime Source: no imports, reads or actions')
    need(__debug__ and sys.flags.isolated and sys.dont_write_bytecode and row(Path(sys.executable).resolve()) == PYTHON,
         'Pinned Python -I -B, no -O')
    prep = module(CONSTRUCTION_PREPARER, 'genuine_completed_probe_constructor_admission')
    prep.family(ACTOR_INDEX)
    p = document(ACTOR_PLAN)
    need(ACTOR_INDEX['path'] == str(BASE / 'next-native-export-diagnostic-probe-runtime-v1/index.json') and
         ACTOR_PLAN['path'] == str(Path(ACTOR_INDEX['path']).with_name('plan.json')), 'Exact actor roles')
    need(p['prospectiveArtifactBindingsPending'] is False and p['perCaseOwnerSeconds'] == 90 and
         p['outerOwnerSeconds'] == 1800 and p['minimumFreeBytes'] == 1024**3, 'Bound original runtime limits')
    review = document(CONSTRUCTION_REVIEW)
    need(review['state'] == p['expectedConstructorReviewState'] and
         review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True, 'Complete independent INIT review')
    bindings = p['expectedBindings']
    need(bindings['constructionDataReview'] == CONSTRUCTION_REVIEW, 'Actual constructor review role')
    for ref in bindings.values():
        checked(ref)
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata']:
        need(review[key] == bindings[key], 'Reviewed artifact role')
    need(review['actualResult'] == bindings['constructionResult'] and
         review['fullBuildReview'] == bindings['fullNativeBuildReview'], 'Reviewed construction/build join')
    constructor = document(bindings['constructionResult'])
    need(constructor['passed'] is True and constructor['callerIndex'] == bindings['constructionCallerIndex'] and
         constructor['plan'] == bindings['constructionPlan'] and
         constructor['rootAuthority'] == bindings['constructionRootAuthority'], 'Genuine constructor roles')
    need(constructor['artifacts']['component'] == bindings['component'] and
         constructor['artifacts']['componentAudit'] == bindings['componentAudit'], 'Actual component artifacts')
    constructor_authority = document(bindings['constructionRootAuthority'])
    before = prep.admit(constructor_authority)
    source = prep.context()
    need(source['plan']['inputSourceIndex'] == p['inputSourceIndex'] and
         source['plan']['entries']['real-next'] == p['inputEntry'] and
         source['plan']['worldSourceIndex'] == p['worldSourceIndex'] and
         source['plan']['selectedInterfaces'] == p['selectedInterfaces'], 'Actual fixture/world')
    for key, value in source['fullRoles'].items():
        need(bindings[key] == value, 'Fresh seven-role full build wire')
    audit = document(bindings['componentAudit'])
    need(audit['passed'] is True and audit['component'] == bindings['component'] and
         set(audit['emittedImports']) <= set(p['selectedInterfaces']) and
         audit['exports'] == ['wasi:http/incoming-handler@0.2.10'], 'Actual standard component world')
    need(len(p['selectedInterfaces']) == 13 and all(x.endswith('@0.2.10') for x in p['selectedInterfaces']), 'Same selected interfaces')
    need(len(p['fixedCaseIds']) == len(set(p['fixedCaseIds'])) == 17 and p['fixedCaseIds'][0] == 'none', 'Fixed schedule')
    for ref in [p['node'], p['wasmtime'], p['monitor'], p['caseContract'], PYTHON]:
        checked(ref)
    contract = document(p['caseContract'])
    need([x['id'] for x in contract['cases']] == p['fixedCaseIds'], 'Actual case contract')
    return dict(prep=prep, plan=p, bindings=bindings, contract=contract,
        constructorAuthority=constructor_authority, worldBefore=before,
        monitor=module(p['monitor'], 'genuine_original_seventeen_case_monitor'))


def authority(s):
    p = s['plan']
    return dict(schemaVersion=1, state='ROOT_NATIVE_EXPORT_DIAGNOSTIC_PROBE_RUNTIME_AUTHORIZED_V1', unissued=False,
        perCaseCollectionAllowed=True, nativeBuildAllowed=False, constructorAllowed=False, browserAllowed=False,
        applicationMountAllowed=False, guestEnvironmentAllowed=False, outgoingHttpWorkloadSelected=False,
        automaticRetryAllowed=False, sourceIndex=ACTOR_INDEX, plan=ACTOR_PLAN, caseIds=p['fixedCaseIds'],
        runId=RUN_ID, origin=ORIGIN, node=p['node'], wasmtime=p['wasmtime'], controller=row(Path(__file__).resolve()),
        **s['bindings'])


def protect(s, ar):
    need(document(ar) == authority(s), 'Authority/controller changed')
    s['prep'].family(ACTOR_INDEX)
    checked(ACTOR_PLAN)
    checked(CONSTRUCTION_PREPARER)
    checked(CONSTRUCTION_REVIEW)
    need(s['prep'].admit(s['constructorAuthority']) == s['worldBefore'], 'Native/source/world changed')


def clean(t):
    return type(t['rawExitCode']) is int and t['rawExitCode'] == 0 and \
        t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True and \
        t['timeout'] is t['forcedCleanup'] is False and all(t[k] == [] for k in
        ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']) and \
        all(g['alive'] is False for g in t['finalGroups'])


def equals(actual, expected):
    return type(actual) is type(expected) and actual == expected


def analyze(case, raw, folder, origin, contract):
    """Final DATA only, after the original owner has finalized its terminal/groups."""
    errors = []
    def check(value, message):
        if not value:
            errors.append(message)
    check(raw['collectionCompleted'] is True and raw['semanticValidationInvoked'] is False, 'Incomplete collection')
    check(raw['errors'] == [], 'Collection errors')
    capture = raw['stdoutCapture']
    check(capture['complete'] is capture['pipeEof'] is capture['fileClosed'] is capture['finalized'] is True and
          capture['fileBoundVerified'] is True and capture['errors'] == [] and capture['overflow'] is False and
          capture['partialWritePossible'] is capture['unretainedBytesUnknown'] is False, 'Incomplete stdout')
    stdout = checked(raw['stdout']).read_bytes()
    check(len(stdout) == capture['fileBytes'] == capture['completeWriteBytes'] <= 8388608, 'Stdout size')
    response = raw['http']
    check(response['error'] is None and response['complete'] is True and response['overflow'] is False and
          response['status'] == case['expectedHttpStatus'], 'HTTP failure')
    body_bytes = checked(response['body']).read_bytes()
    check(len(body_bytes) == response['bodyBytes'] <= 4096, 'HTTP size')
    body = json.loads(body_bytes.decode('ascii'), object_pairs_hook=pairs)
    expected_body = dict(contract['responseCommon'], case='/' + case['id'],
        allocatedBytes=524288 if case['id'] == 'after-observe-allocation' else 0,
        constructedStringExpression=case['id'] == 'rope')
    check(set(body) == set(expected_body) and all(equals(body.get(k), v) for k, v in expected_body.items()), 'Response semantics')
    lines = stdout.decode('ascii').splitlines()
    records = []
    for line in lines:
        if not line:
            continue
        if line == 'Serving HTTP on ' + origin:
            continue
        value = json.loads(line, object_pairs_hook=pairs)
        check(type(value) is dict and value.get('marker') == 'NEXT_NATIVE_EXPORT_PUBLIC_CORRELATION_V1', 'Unexpected stdout')
        records.append(value)
    expected = case['expectedNativeRecord']
    check(len(records) == (1 if expected['required'] else 0), 'Native record count')
    if expected['required'] and len(records) == 1:
        value = records[0]
        check(set(value) == {'marker', 'version', 'event', 'status', 'observations', 'method', 'path', 'reason', 'corrCount', 'corr'}, 'Native field set')
        check(equals(value.get('version'), 1), 'Native version')
        wanted = {k: v for k, v in expected.items() if k not in ['required', 'allowedRecords']}
        check(all(equals(value.get(k), v) for k, v in wanted.items()), 'Native contract fields')
        if 'allowedRecords' in expected:
            check(any(all(equals(value.get(k), v) for k, v in option.items())
                      for option in expected['allowedRecords']), 'Rope alternatives')
        # These are static observe arguments in indexed c06d, not incoming GET metadata.
        route = ('POST', '/actions')
        if case['id'] in ['missing', 'duplicate']:
            route = ('GET', '/actions')
        elif case['id'] == 'invalid':
            route = ('GET', '/action-result')
        elif case['id'] in ['wrong-enum-string', 'wrong-enum-object', 'wrong-arity', 'repeated-same', 'repeated-different']:
            route = ('-', '-')
        check((value.get('method'), value.get('path')) == route, 'Static native route snapshot')
        check(raw['markerPresenceControl']['observed'] is True and
              raw['markerPresenceControl']['deadlineReached'] is False, 'Marker control deadline')
    return dict(caseId=case['id'], passed=not errors, errors=errors, rawResult=row(folder / 'data/case-result.json'),
        stdout=raw['stdout'], stderr=row(folder / 'data/wasmtime.stderr.log'), body=response['body'],
        nativeRecords=records, response=body, absenceIsBoundedObservationOnly=not expected['required'],
        gcOrRopeRepresentationOrPrivateIdentityOrHostCompletionProved=False)


def environment():
    env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    return dict(env, PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')


def worker(s, ar, output):
    p = s['plan']
    need(not output.exists() and not output.is_symlink(), 'Fresh collection root')
    output.mkdir(mode=0o700)
    result = dict(schemaVersion=1, state='DIAGNOSTIC_PROBE_COLLECTION_FAILED_UNACCEPTED_V1', rootAuthority=ar,
        cases=[], error=None, finalProtection=None, collectionCompleted=False, allCasesPassed=False,
        unattemptedCaseIds=list(p['fixedCaseIds']),
        fullNextAccepted=False, nativeExportOrHostCompletionProved=False)
    try:
        protect(s, ar)
        for index, case in enumerate(s['contract']['cases']):
            s['prep'].family(ACTOR_INDEX)
            checked(ar)
            folder = output / ('case-' + str(index).zfill(2) + '-' + case['id'])
            folder.mkdir(mode=0o700)
            argv = [p['node']['path'], str(Path(ACTOR_INDEX['path']).with_name('run-case.mjs')),
                    '--authority', ar['path'], '--case', str(index)]
            record = dict(caseId=case['id'], ownerInvocationAttempted=True, terminal=None,
                          cleanOwner=False, ownerError=None, analysis=None)
            result['cases'].append(record)
            result['unattemptedCaseIds'] = p['fixedCaseIds'][index + 1:]
            try:
                terminal = s['monitor'].monitor(argv, str(REPO), environment(), folder, p['perCaseOwnerSeconds'], ar)
                record.update(terminal=row(folder / 'terminal.json'), cleanOwner=clean(terminal))
            except BaseException as error:
                record['ownerError'] = dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc())
                raise
            need(clean(terminal), 'Case owner failed; remaining cases unattempted')
            raw = document(row(folder / 'data/case-result.json'))
            need(raw['collectionCompleted'] is True, 'Collection failed; remaining cases unattempted')
            try:
                record['analysis'] = analyze(case, raw, folder, ORIGIN, s['contract'])
            except BaseException as error:
                record['analysis'] = dict(caseId=case['id'], passed=False, error=repr(error), stack=traceback.format_exc())
            save(folder / 'analysis.json', record['analysis'])
        result['collectionCompleted'] = len(result['cases']) == 17
        result['allCasesPassed'] = result['collectionCompleted'] and all(x['analysis']['passed'] is True for x in result['cases'])
    except BaseException as error:
        result['error'] = dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc())
    finally:
        try:
            protect(s, ar)
            result['finalProtection'] = dict(unchanged=True)
        except BaseException as error:
            result['finalProtection'] = dict(unchanged=False, error=repr(error), stack=traceback.format_exc())
        result['passed'] = result['allCasesPassed'] and result['error'] is None and result['finalProtection']['unchanged'] is True
        if result['passed']:
            result['state'] = 'DIAGNOSTIC_PROBE_SEVENTEEN_CASES_PASSED_UNREVIEWED_V1'
        save(output / 'result.json', result)
    print(json.dumps(dict(result=row(output / 'result.json'), passed=result['passed'])), flush=True)
    return 0 if result['passed'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true')
    group.add_argument('--run', action='store_true')
    group.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    s = context()
    a = authority(s)
    output = Path(s['plan']['outputPrefix'] + '-' + RUN_ID)
    outer = Path(str(output) + '-external-root')
    need(shutil.disk_usage(output.parent).free >= 1024**3, 'Original 1 GiB admission')
    if args.write:
        need(not output.exists() and not outer.exists() and not AUTHORITY.exists(), 'Fresh authority and output paths')
        print(json.dumps(dict(authority=save(AUTHORITY, a), targetsInvoked=False)), flush=True)
        return 0
    if not args.run and not args.worker:
        print(json.dumps(dict(sourceOnly=True, authorityIssued=False, targetsInvoked=False, proposedOutput=str(output))))
        return 0
    ar = row(AUTHORITY)
    need(document(ar) == a, 'Exact prepared authority')
    if args.worker:
        return worker(s, ar, output)
    need(not output.exists() and not outer.exists(), 'Fresh original owner namespaces')
    outer.mkdir(mode=0o700)
    terminal = None
    owner_error = None
    protection = None
    try:
        protect(s, ar)
        terminal = s['monitor'].monitor([PYTHON['path'], '-I', '-B', str(Path(__file__).resolve()), '--worker'],
            str(REPO), environment(), outer, s['plan']['outerOwnerSeconds'], ar)
    except BaseException as error:
        owner_error = dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc())
    finally:
        try:
            protect(s, ar)
            protection = dict(unchanged=True, sourceAndNativeAndWorldReadmitted=True)
        except BaseException as error:
            protection = dict(unchanged=False, error=repr(error), stack=traceback.format_exc())
        save(outer / 'root-protection.json', protection)
    terminal_ref = row(outer / 'terminal.json') if (outer / 'terminal.json').exists() else None
    if terminal is None and terminal_ref is not None:
        terminal = document(terminal_ref)
    final = dict(rootAuthority=ar, terminal=terminal_ref, cleanOwner=clean(terminal) if terminal else False,
        ownerError=owner_error, finalProtection=protection,
        workerResult=row(output / 'result.json') if (output / 'result.json').exists() else None,
        fullNextAccepted=False, independentRuntimeDataReviewRequired=True)
    final['passed'] = final['cleanOwner'] and owner_error is None and protection['unchanged'] is True and \
        final['workerResult'] is not None and document(final['workerResult'])['passed'] is True
    save(outer / 'observation.json', final)
    print(json.dumps(final), flush=True)
    return 0 if final['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
