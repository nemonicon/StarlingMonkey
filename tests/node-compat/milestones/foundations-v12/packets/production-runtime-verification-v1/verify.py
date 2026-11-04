"""Read completed OFF serial8 evidence; never execute application Wasm/JS.

Only external process: pinned wasm-tools --version / component wit --json.
Section inspection below counts import entries; it is not a general decoder.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess

HERE = Path(__file__).resolve().parent
PACKETS = HERE.parent
REPO = PACKETS.parents[2]
ROOT = Path('/tmp/starling-node-compat/production-scheduler-runtime-v1/off-release')
ENGINE = '6e5bc2ca3b3e3f7dccaa887003bc292e8a7abfbc5260691d1cda0114640dae84'
ROOT_SHA = 'f7ff117d4c4ecdaa720a76caef6d8f5df42f433641ea42413c2a20a0e7c7e6af'
TOOL = Path('/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools')
TOOL_SHA = 'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
EXPECTED_JOBS = ['core', 'allocator', 'stream-web', 'optional', 'strict-sync', 'strict-runtime', 'strict-late', 'strict-callbacks']
SOURCE_PACKETS = [('production-regression-candidate-v5', '0a65a102b89eaa68f583246c7a95d2dd6b5826b80931a6b59b9926a0c719b2cd', 667),
                  ('production-followon-off-v3', '6354d57c9dc0a5161b0910a56c98886480d343e1aed8642c15debf1367081efd', 755),
                  ('production-release-runner-v3', '70e60105aded35a37e9a53027dab4397824f9e6c5bb60039266bf02a988f9ed7', 1442)]
checked_files, copied_files, components, cores, jobs = {}, [], [], [], []


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def check(path, expected=None, size=None):
    path = Path(path)
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and not path.is_symlink(), path
    digest = sha(path)
    if expected is not None:
        assert digest == expected, path
    if size is not None:
        assert info.st_size == size, path
    previous = checked_files.get(str(path))
    row = {'path': str(path), 'sha256': digest, 'bytes': info.st_size}
    if previous:
        assert row == previous
    checked_files[str(path)] = row
    return row


def read_json(path, expected=None):
    check(path, expected)
    return json.loads(Path(path).read_bytes())


def copy_text(path, target):
    row = check(path)
    data = Path(path).read_bytes()
    data.decode('utf-8')
    assert b'\0' not in data and data[:4] != b'\0asm'
    destination = HERE / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A verifier-only schema correction may leave this packet's earlier exact
    # captures present. Revalidate them against the same pinned complete output;
    # never overwrite a differing file or adopt a prior runtime result as new.
    if destination.exists():
        assert not destination.is_symlink() and destination.read_bytes() == data
    else:
        with destination.open('xb') as stream:
            stream.write(data)
    assert sha(destination) == row['sha256']
    copied_files.append({**row, 'copy': target, 'byteExact': True})


def walk(value, callback, context=''):
    if isinstance(value, dict):
        callback(value, context)
        for key, child in value.items():
            walk(child, callback, context + '/' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, callback, context + '/' + str(index))


def u32(data, position, end):
    result = 0
    for shift in range(0, 35, 7):
        assert position < end
        value = data[position]
        position += 1
        result |= (value & 127) << shift
        if not value & 128:
            assert result <= 0xffffffff
            return result, position
    raise AssertionError('Invalid u32 LEB')


def import_counts(data, begin=0, end=None, depth=0):
    """Header/section-length/import-vector-count inspection only.

    Core sections: import=2. Component: core-module=1, nested-component=4,
    import=10. Source: local wasmparser0.235 parser.rs. No function, type,
    initializer, instance or application instruction is interpreted.
    """
    end = len(data) if end is None else end
    assert depth <= 32 and begin + 8 <= end
    header = data[begin:begin + 8]
    assert header in [b'\0asm\x01\0\0\0', b'\0asm\x0d\0\x01\0']
    component = header[4] == 13
    result = [{'offset': begin, 'bytes': end - begin, 'depth': depth,
               'kind': 'component' if component else 'core-module', 'importEntries': 0}]
    position = begin + 8
    while position < end:
        section = data[position]
        size, payload = u32(data, position + 1, end)
        finish = payload + size
        assert finish <= end
        if section == (10 if component else 2):
            count, _ = u32(data, payload, finish)
            result[0]['importEntries'] += count
        if component and section in [1, 4]:
            nested = import_counts(data, payload, finish, depth + 1)
            assert nested[0]['kind'] == ('core-module' if section == 1 else 'component')
            result.extend(nested)
        position = finish
    assert position == end
    return result


assert not (HERE / 'results.json').exists(), 'Exclusive verification; preserve prior results'
source_seals = []
for name, expected_index, count in SOURCE_PACKETS:
    base = PACKETS / name
    index = read_json(base / 'index.json', expected_index)
    for row in index['files']:
        check(base / row['path'], row['sha256'], row['bytes'])
    manifest_pin = next(row['sha256'] for row in index['files'] if row['path'] == 'input-freeze.json')
    manifest = read_json(base / 'input-freeze.json', manifest_pin)
    assert len(manifest['inputs']) == count
    for row in manifest['inputs']:
        check(base / row['path'], row['sha256'], row['bytes'])
    live = [row for row in manifest['inputs'] if (base / row['path']).resolve() ==
            (REPO / 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm').resolve()]
    assert len(live) == 1 and live[0]['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
    source_seals.append({'packet': name, 'indexSha256': expected_index, 'manifestSha256': manifest_pin,
                         'inputs': count, 'postRunBytesIndependentlyRehashed': True})

root = read_json(ROOT / 'results.json', ROOT_SHA)
assert root['state'] == 'passed' and root['engineSha256'] == ENGINE
assert root['sourceFiles'] == 306 and root['reusedResults'] == 0 and root['resumeSupported'] is False
assert [job['name'] for job in root['jobs']] == EXPECTED_JOBS
release_seal = read_json(ROOT / 'release-admission-complete.json')
assert release_seal['reportSha256'] == ROOT_SHA and release_seal['jobs'] == 8
assert release_seal['consumedInputsRecheckedAfterRun'] is True
copy_text(ROOT / 'results.json', 'reports/serial8-results.json')
copy_text(ROOT / 'release-admission-complete.json', 'reports/serial8-completion.json')

all_reports = {}
for job in root['jobs']:
    assert job['code'] == 0 and job['signal'] is None
    check(job['runner'], job['runnerSha256'])
    report = read_json(job['reportPath'], job['reportSha256'])
    seal = read_json(job['completionPath'], job['completionSha256'])
    check(job['logPath'], job['logSha256'])
    assert report['engineSha256'] == ENGINE and seal['consumedInputsRecheckedAfterRun'] is True
    assert seal.get('production', seal)['engineSha256'] == ENGINE
    all_reports[job['name']] = report
    jobs.append({**job, 'reportAndCompletionAndLogIndependentlyRehashed': True})
    copy_text(Path(job['logPath']), 'logs/' + job['name'] + '.log')
optional = all_reports['optional']
assert optional['state'] == 'passed'
assert [entry['name'] for entry in optional['modules']] == ['path', 'events', 'string-decoder', 'assert', 'querystring', 'util']
for entry in optional['modules']:
    assert entry['code'] == 0 and entry['signal'] is None
    check(entry['runner'], entry['runnerSha256'])
    check(entry['logPath'], entry['logSha256'])
    report = read_json(entry['reportPath'], entry['reportSha256'])
    completion = read_json(entry['completionPath'], entry['completionSha256'])
    assert report['engineSha256'] == completion['production']['engineSha256'] == ENGINE
    assert completion['consumedInputsRecheckedAfterRun'] is True
    all_reports['optional/' + entry['name']] = report

# Inventory/copy only the complete OFF release tree; never sibling GC/focused/HTTP.
binary_by_sha = {}
for directory, dirs, files in os.walk(ROOT, followlinks=False):
    dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
    for name in sorted(files):
        path = Path(directory) / name
        if path.is_symlink():
            continue
        row = check(path)
        if path.suffix == '.wasm':
            data = path.read_bytes()
            counts = import_counts(data)
            if counts[0]['kind'] == 'component':
                assert counts[0]['importEntries'] == 0
                binary_by_sha[row['sha256']] = row
                components.append({**row, 'sectionImportCounts': counts, 'outerHostImports': [],
                                   'binaryBytesCopied': False})
            else:
                cores.append({**row, 'sectionImportCounts': counts,
                              'notAnOuterComponentCapabilityInventory': True, 'binaryBytesCopied': False})
        else:
            copy_text(path, 'completed-off-output/' + path.relative_to(ROOT).as_posix())
assert len(components) == 40
assert sum('/strict-' in row['path'] for row in components) == 24

audits = []
inline_sources = []
def validate_record(value, context):
    if 'componentSha256' in value and 'componentizer' not in context.lower():
        digest = value['componentSha256']
        assert digest in binary_by_sha, context
        if 'componentBytes' in value:
            assert value['componentBytes'] == binary_by_sha[digest]['bytes']
    if 'interfaceAudit' in value:
        audit = value['interfaceAudit']
        assert audit['selectedInterfaces'] == audit['emittedImports'] == []
        assert audit['entropyPolicy'] == 'off' and audit['componentSha256'] in binary_by_sha
        audits.append({'context': context, **audit})
    if 'emittedWit' in value:
        assert not re.search(r'^\s*import\s', value['emittedWit'], re.M)
    if 'source' in value and isinstance(value['source'], str) and 'sourceSha256' in value:
        assert hashlib.sha256(value['source'].encode()).hexdigest() == value['sourceSha256']
        inline_sources.append({'context': context, 'sha256': value['sourceSha256']})
    if 'componentPath' in value and str(value['componentPath']).startswith(str(ROOT) + '/'):
        if 'componentSha256' in value:
            check(value['componentPath'], value['componentSha256'], value.get('componentBytes'))
        else:
            assert context == 'optional/path/aliases', context
            check(value['componentPath'], value['sha256'], value['bytes'])
    if str(value.get('path', '')).startswith(str(ROOT) + '/') and str(value.get('path', '')).endswith('.wasm') and 'sha256' in value:
        check(value['path'], value['sha256'], value.get('bytes'))
    if 'sourcePath' in value and str(value['sourcePath']).startswith(str(ROOT) + '/') and 'sourceSha256' in value:
        check(value['sourcePath'], value['sourceSha256'])
for name, report in all_reports.items():
    walk(report, validate_record, name)

core = all_reports['core']
assert len(core['calls']) == 2 and core['wasmtimeReport'] == core['calls'][0]
corpus = read_json(ROOT / 'core/oracle-corpus.json')
assert len(corpus['strings']) == 381 and len(corpus['bytes']) == 250
for index, call in enumerate(core['calls'], 1):
    assert call['calls'] == index and call['strings'] == 381 and call['bytes'] == 250
    assert call['stubCalls'] == call['stubConstructors'] == 9 and call['unavailableMethods'] == 91
    assert call['globalBufferIdentity'] and call['staticCommonJS']
assert len(core['initializationFailures']) == 4 and all(row['expectedFailure'] for row in core['initializationFailures'])
assert 'native registry aliases, dynamic imports and per-specifier caching passed' in core['rawAliasFixture']['wasmtimeStdout']

allocator = all_reports['allocator']
oracle_path = REPO / 'tests/node-compat/foundation-alloc-unsafe/node-results.json'
oracle = read_json(oracle_path, allocator['oracleSha256'])
assert len(allocator['calls']) == 2 and allocator['wasmtime']['observed'] == allocator['calls'][0]
for count, call in enumerate(allocator['calls'], 1):
    assert call['calls'] == count and call['cases'] == oracle['cases'] and call['demand'] == oracle['callerDemand']
    assert len(call['profile']) == 5 and len(call['numericHooks']) == 6
    assert all(row['hookCalls'] == 0 for row in call['numericHooks'])
    assert call['refusals']['operations'] == 240 and call['refusals']['prototypeFunctions'] == 91
    assert call['snapshot'] == {'first': 17 + count, 'shared': True, 'viewValue': count, 'byteOffset': 1, 'backingBytes': 3}
    assert call['actualNativeModule'] and not call['allocatorReplaced']
assert len(allocator['initialization']) == 11 and len(allocator['oldControl']['initialization']) == 2
assert allocator['oldControl']['sourceFilesVerified'] == 293 and allocator['delegatedControl']['sourceFilesVerified'] == 304
for row in allocator['sourceFiles']:
    check(ROOT / 'allocator/source' / row['name'], row['sha256'])

web = all_reports['stream-web']
assert len(web['calls']) == 3 and web['wasmtimeReport'] == web['calls'][0]
for count, call in enumerate(web['calls'], 1):
    assert call['calls'] == count and call['passed'] and call['snapshotResumption']
    for key, expected in {'constructors': 41, 'codecs': 250, 'cancellations': 4, 'guards': 24,
                          'views': 12, 'controllers': 6, 'iterations': 67, 'data': 26}.items():
        assert call[key] == expected
    assert call['ownErrors'] == {'checks': 9, 'inheritedGets': 0, 'inheritedSets': 0}
assert [x['calls'] for x in web['aliases']['calls']] == [1, 2] and web['aliases']['wasmtimeReport']['calls'] == 1
assert len(web['topLevelFailures']) == 7 and all(row['failed'] for row in web['topLevelFailures'])
for row in web['topLevelFailures']:
    assert row['expected'].strip('/') in row['message']
for row in web['sourceManifest']:
    check(REPO / 'tests/node-compat/foundation-stream-web/production-candidate' / row['path'], row['sha256'])

for name, count, failures in [('path', 3, 2), ('events', 2, 7), ('string-decoder', 3, 3),
                              ('assert', 2, 9), ('querystring', 2, 8), ('util', 2, 8)]:
    report = all_reports['optional/' + name]
    assert len(report['calls']) == count
    assert len(report.get('topLevelFailures', report.get('initialization', []))) == failures
assert all_reports['optional/path']['globReport']['differences'] == []
assert all_reports['optional/assert']['primitiveEqualityComparisons'] == 784
assert all_reports['optional/querystring']['customSeparatorVectors'] == 210
assert all_reports['optional/querystring']['byteFallbackVectors'] == 1536

sync, runtime, late, callback = [all_reports[name] for name in EXPECTED_JOBS[-4:]]
assert len(sync['initialization']) == 16 and sum(x['rejected'] for x in sync['initialization']) == 13
assert len(sync['successfulReuse']['calls']) == 3 and len(sync['deployed']) == 3
assert len(runtime['fatal']) == 5 and len(runtime['controls']) == 4
assert len(late['cases']) == 6 and sum(x['rejected'] for x in late['cases']) == 3
assert len(callback['initialization']) == 8 and all(x['rejected'] for x in callback['initialization'])
assert len(callback['controls']) == 5
for entry in sync['deployed'] + runtime['fatal']:
    assert entry['jcoChild']['status'] == 0 and 'EXPECTED_FATAL_EXPORT' in entry['jcoChild']['stdout']
    assert entry['wasmtime']['status'] != 0 and 'unreachable' in entry['wasmtime']['stderr']
for entry in runtime['controls'] + callback['controls']:
    assert [x['calls'] for x in entry['calls']] == [1, 2, 3]

# Independent parse only. The component is never instantiated or executed.
check(TOOL, TOOL_SHA)
version = subprocess.run([str(TOOL), '--version'], capture_output=True, text=True, timeout=30)
assert version.returncode == 0 and version.stdout.startswith('wasm-tools 1.235.0 ')
for component in components:
    path = Path(component['path'])
    command = [str(TOOL), 'component', 'wit', '--json', str(path)]
    parsed = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert parsed.returncode == 0 and parsed.stderr == ''
    document = json.loads(parsed.stdout)
    worlds = document['worlds']
    assert len(worlds) == 1 and worlds[0]['imports'] == {}
    relative = path.relative_to(ROOT).as_posix()
    destination = HERE / 'component-wit' / (relative + '.json')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x') as stream:
        stream.write(parsed.stdout)
    component['independentWit'] = {'command': command, 'exit': 0, 'stderr': '',
                                 'copy': destination.relative_to(HERE).as_posix(), 'sha256': sha(destination),
                                 'outerWorldImports': [], 'exports': list(worlds[0]['exports'])}

# The delegated numeric-hook component is deliberately built with the actual
# historical m0.8 engine. Do not count that preserved control as production306.
legacy_component = allocator['delegatedControl']['componentSha256']
assert sum(row['sha256'] == legacy_component for row in components) == 1
for row in components:
    historical = row['sha256'] == legacy_component
    row['reportedEngineSha256'] = allocator['delegatedControl']['engineSha256'] if historical else ENGINE
    row['engineAssociation'] = 'historical-m08-delegated-control' if historical else 'current-production306'

for row in list(checked_files.values()):
    check(row['path'], row['sha256'], row['bytes'])
summary = {'schemaVersion': 1, 'state': 'INDEPENDENT_READ_ONLY_PRODUCTION_OFF_SERIAL8_VERIFICATION_PASSED',
           'rootReportSha256': ROOT_SHA, 'engineSha256': ENGINE, 'jobs': jobs,
           'sourceSeals': source_seals, 'optionalModules': 6, 'actualComponents': len(components),
           'currentProductionEngineComponents': 39, 'historicalM08ControlComponents': 1,
           'strictComponents': 24, 'reportedInterfaceAuditsChecked': len(audits),
           'allActualOuterComponentImportsEmpty': True, 'components': components,
           'transpiledCoreModules': cores, 'checkedInlineSourceBodies': inline_sources,
           'binaryAndTextReferences': list(checked_files.values()), 'copiedCompletedTextFiles': copied_files,
           'parserTool': {'path': str(TOOL), 'sha256': TOOL_SHA, 'version': version.stdout.strip()},
           'nestedCoreImportCountsAreNotOuterHostServices': True,
           'sourcePostRunHashChecks': True, 'completionSealsRecordSourcePrePostChecks': True,
           'independentRuntimeReexecution': False, 'nodeOracleReexecuted': False,
           'gcStressGateIncluded': False, 'focusedOrHTTPIncluded': False,
           'fatalOriginalCauseIdentityProved': False, 'safeReuseAfterFatalProved': False,
           'engineResetOrALSProved': False, 'performanceClaim': False, 'binaryBytesCopied': 0}
with (HERE / 'results.json').open('x') as stream:
    json.dump(summary, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': summary['state'], 'jobs': len(jobs), 'optionalModules': 6,
                  'components': len(components), 'strictComponents': 24,
                  'interfaceAudits': len(audits), 'referencedFiles': len(checked_files),
                  'copiedTextFiles': len(copied_files), 'guestOrHostExecuted': False}))
