"""Check retained recovery DATA only; never read original absolute paths."""
import gzip
import hashlib
import json
from pathlib import Path
import stat
import sys

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('Use Python -I -B, without optimization, before payload reads')

ROOT = Path(__file__).resolve().parent / 'recovery-records'
INDEX_SHA = '327afa99295eff21a6156ef57c926e26a01ba8de0afc617d8bbd5fcdb96d23fb'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(relative):
    rel = Path(relative)
    assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == relative
    p = ROOT / rel
    assert p.resolve(strict=True) == p
    before = p.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= 16 * 1024**2
    raw = p.read_bytes()
    after = p.stat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
    return raw


def main():
    assert len(sys.argv) == 1
    raw = local('index.json')
    assert digest(raw) == INDEX_SHA and len(raw) == 426717
    index = json.loads(raw)
    assert index['state'] == 'CLONE_CANCEL_RECOVERY_CLOSED_RECORDS_V1'
    assert (index['payloadFiles'], index['retainedBytes'], index['originalBytes']) == (885, 5698413, 16492171)
    assert not index['nativeEngineBuildIncluded'] and not index['fixedGuestRunIncluded']
    documents = {}; originals = {}; names = set(); total = expanded = 0
    for r in index['files']:
        assert r['path'] not in names; names.add(r['path'])
        payload = local(r['path'])
        assert len(payload) == r['bytes'] and digest(payload) == r['sha256']
        assert r['encoding'] in ('gzip', 'identity') and r['original']['bytes'] <= 16 * 1024**2
        # The compressed payload was authenticated before decompression.
        body = gzip.decompress(payload) if r['encoding'] == 'gzip' else payload
        assert len(body) == r['original']['bytes'] and digest(body) == r['original']['sha256']
        name = r['path'][:-3] if r['encoding'] == 'gzip' else r['path']
        assert name not in documents
        documents[name] = body; originals[name] = r['original']
        total += len(payload); expanded += len(body)
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
    assert not any(p.is_symlink() for p in ROOT.rglob('*'))
    assert actual == names | {'index.json'}
    assert len(names) == 885 and total == 5698413 and expanded == 16492171
    def doc(name):
        return json.loads(documents[name])
    def ref(name):
        return originals[name]
    tools = doc('recovery/tool-recovery-result-v2.json')
    failure = doc('recovery/tool-recovery-result.json')
    assert failure['state'] == 'NATIVE_TOOL_RECOVERY_FAILED_V1' and failure['tools'] == []
    assert failure['inputsPreserved'] and failure['errors'][0]['type'] == 'AssertionError'
    assert tools['state'] == 'NATIVE_TOOL_RECOVERY_MATERIALIZED_AND_INVENTORIED_V2'
    assert tools['inputsPreserved'] and tools['errors'] == tools['secondaryErrors'] == []
    assert tools['priorFailedResult'] == ref('recovery/tool-recovery-result.json')
    assert {t['role'] for t in tools['tools']} == {'wasi-sdk', 'binaryen', 'wasm-tools', 'wasmtime', 'weval', 'openssl'}
    assert sum(t['files'] for t in tools['tools']) == 14793
    assert sum(t['symlinks'] for t in tools['tools']) == 31
    assert sum(t['regularPayloadBytes'] for t in tools['tools']) == 558676040
    for t in tools['tools']:
        assert len(t['rows']) == len({r['relativePath'] for r in t['rows']})
        assert all(r['mode'] == 0o777 for r in t['rows'] if r['kind'] == 'symlink')
    acquisition = doc('recovery/header-acquisition.json')
    assert acquisition['matched'] == 242 and len(acquisition['headers']) == 243
    assert acquisition['unresolved'] == ['include/mozilla/intl/unicode_bidi_ffi_generated.h']
    generated = documents['generated/unicode_bidi_ffi_generated.h']
    assert len(generated) == 3287 and digest(generated) == '51565fa854e09c04d418b39436c9eea683ecdac48b7769d5f07d23840c6fa48b'
    assert generated == documents['recovery/commands/generate-bidi-header/stdout.log']
    sdk = doc('recovery/sdk-materialization.json')
    assert sdk['passed'] and sdk['allHistoricalContentAndModesMatched'] and sdk['selectedLibraryPreserved']
    assert not sdk['vanillaLibrarySelected'] and not sdk['newCIBuildAttestationClaimed']
    assert (sdk['files'], sdk['directories'], sdk['bytes']) == (596, 13, 646760937)
    assert sdk['inventory'] == ref('recovery/selected-sdk-inventory.json')
    sdk_rows = doc('recovery/selected-sdk-inventory.json')['entries']
    assert len(sdk_rows) == 609 and sum(r.get('bytes', 0) for r in sdk_rows) == 646760937
    for role, entries, files in [('rust', 178, 155), ('corrosion', 306, 193)]:
        result = doc('rust-recovery/' + role + '-result.json')
        assert result['state'] == 'PRIVATE_TOOL_SOURCE_RECOVERY_VERIFIED_V1' and result['inputsPreserved']
        assert not result['gitMetadataMaterialized'] and not result['toolCommandsExecuted']
        assert len(result['entries']) == entries and sum(r['kind'] == 'file' for r in result['entries']) == files
    source = doc('build-preparation/source-materialization.json')
    assert (source['nativeCount'], source['supportCount'], source['embeddingCount']) == (435, 387, 3)
    assert len(source['copies']) == 825 and source['inputsUnchanged'] and not source['nativeBuildExecuted']
    changed = [r for r in source['copies'] if r['role'] == 'native' and r['source'] != r['predecessor']]
    assert len(changed) == 1 and changed[0]['relativePath'] == 'builtins/web/fetch/request-response.cpp'
    assert changed[0]['source']['sha256'] == '0431184d4562972c98538494caf46d2b11cdf0280f51d0e7143cd8534526442e'
    generators = doc('build-preparation/generator-checks/result.json')
    assert generators['passed'] and generators['inputsUnchanged'] and len(generators['commands']) == 10
    assert all(r['rawExitCode'] == 0 and r['clean'] and r['stderr']['bytes'] == 0 for r in generators['commands'])
    # Assert original process outcomes without converting collection into conformance.
    terminal_names = [n for n in documents if n.startswith('recovery/commands/') and n.endswith('/terminal.json')]
    failures = {}
    for n in terminal_names:
        t = doc(n)
        assert t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
        assert not t['errors'] and not t['signals'] and not t['interruptedSignals']
        if t['rawExitCode'] != 0:
            failures[n.split('/')[2]] = t['rawExitCode']
    assert failures == {'fetch-sdk-headers': 2, 'materialize-tools': 1, 'query-historical-sdk-artifact': 1}
    node = doc('references/node-followups.json')
    assert node['nodeVersion'] == 'v22.14.0' and node['captureCompleted'] and not node['timedOut']
    cases = node['observation']['cases']
    assert [c['id'] for c in cases] == ['both-reject-false', 'both-reject-object', 'first-cancel-survivor-eof', 'first-cancel-survivor-source-error']
    assert all(c['collectionComplete'] for c in cases)
    for c in cases[:2]:
        assert c['sourceCancelCalls'] == 1 and c['sourceReasons'][0]['length'] == 2
        assert c['sourceReasons'][0]['firstElementIsFirstReason'] and c['sourceReasons'][0]['secondElementIsSecondReason']
        assert c['snapshots'][1]['first']['state'] == c['snapshots'][1]['second']['state'] == 'pending'
        assert all(c['outcomes'][k]['state'] == 'rejected' and c['outcomes'][k]['sameReason'] for k in ('first', 'second'))
    assert cases[0]['rejection'] == {'type': 'boolean', 'value': False}
    for c in cases[2:]:
        assert c['sourceCancelCalls'] == 0 and c['readerReleased']
        assert c['outcomes']['first'] == {'state': 'fulfilled', 'value': {'type': 'undefined'}}
    assert cases[2]['outcomes']['terminalRead']['value']['done']
    assert cases[3]['outcomes']['terminalRead']['state'] == 'rejected' and cases[3]['outcomes']['terminalRead']['sameReason']
    print(json.dumps(dict(savedRecoveryPassed=True, files=len(names), retainedBytes=total,
                         originalFailures=failures, nodeFollowups=4, generatorChecks=10,
                         nativeBuildVerified=False, fixedGuestVerified=False, originalPathsRead=False), sort_keys=True))


if __name__ == '__main__':
    main()
