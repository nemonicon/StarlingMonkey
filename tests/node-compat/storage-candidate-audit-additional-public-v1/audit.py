"""Read-only additional ordinary public output inventory; never mutates artifacts."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import os
import re
import stat
import subprocess

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/starling-node-compat')
REPO = HERE.parents[2]
roots = []


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def add(directory, report, kind, context=None):
    root, report = BASE / directory, BASE / report
    assert root.is_dir() and not root.is_symlink()
    assert report.is_file() and not report.is_symlink()
    value = read(report)
    proof = {'path': str(report), 'sha256': sha(report), 'kind': kind,
             'releaseAcceptanceClaimed': False, **(context or {})}
    roots.append((root, value, proof))
    return value


for directory in ['foundations-v2/native', 'native-output', 'native-stress-output']:
    value = add(directory, directory + '/results.json', 'final ordinary native public-API report')
    assert len(value['calls']) == 2 and re.fullmatch(r'[0-9a-f]{64}', value['componentSha256'])
for directory in ['foundations-v2/entropy-runtime', 'foundations-v3/entropy-runtime']:
    value = add(directory, directory + '/results.json', 'final ordinary entropy public-API report')
    assert len(value['positive']) == 2 and value['wasmtime']['observed']
value = add('foundations-v2/upstream-off', 'foundations-v2/upstream-off/buffer-ownership-results.json',
            'completed ordinary upstream ownership run')
assert value['passed'] == 2 and value['failed'] == 0
value = add('foundations-v1/upstream-runtime/starling-integration',
            'foundations-v1/upstream-runtime/starling-integration-results.json', 'completed ordinary HTTP integration run')
assert value['passed'] == 10 and value['failed'] == 0

# Preserve the original failure, rather than relabeling duplicate artifacts as
# successful execution. A later accepted component hash may additionally match.
original = BASE / 'foundations-v1/upstream-runtime/starling-e2e-results.json'
old = read(original)
assert old['passed'] == 4 and old['failed'] == 15 and len(old['results']) == 19
accepted_path = REPO / 'tests/node-compat/milestones/entropy-v1/upstream-e2e.json'
accepted = {row['name']: row for row in read(accepted_path)['results']}
for case in old['results']:
    if case.get('status') == 'fail':
        leaf = BASE / ('foundations-v1/upstream-runtime/starling-e2e/' + case['name'])
        files = list(leaf.glob('*.component.wasm')) if leaf.is_dir() else []
        if files:
            assert len(files) == 1
            roots.append((leaf, {'originalCase': case, 'laterAcceptedCase': accepted[case['name']]},
                          {'path': str(original), 'sha256': sha(original), 'kind': 'completed original failed public e2e attempt',
                           'originalPassed': 4, 'originalFailed': 15, 'originalCaseStatus': 'fail',
                           'caseName': case['name'], 'laterAcceptedReport': str(accepted_path),
                           'laterAcceptedReportSha256': sha(accepted_path), 'releaseAcceptanceClaimed': False}))

value = add('component-output', 'component-output/results.json', 'completed initial ordinary JS facade/stub template run')
assert len(value['componentCalls']) == 2 and value['topLevelFailureObserved'] is True
assert value['bufferFacade']['wasmtimeRunPassed'] is True
value = add('wasmcloud-http', 'wasmcloud-http/component-audit.json', 'completed initial ordinary HTTP packaging and host run')
host = BASE / 'wasmcloud-http/wasmtime-results.json'
assert read(host)['componentSha256'] == value['componentSha256']
roots[-1][2]['hostReport'] = {'path': str(host), 'sha256': sha(host)}
value = add('foundations-v3/path-benchmark', 'foundations-v3/path-benchmark/results.json', 'completed ordinary public Path A/B report')
assert len(value['arms']) == 2
value = add('foundations-v3/path-adapter-controls', 'foundations-v3/path-adapter-controls/results.json',
            'completed ordinary public Path adapter/refusal controls')
assert len(value['results']) == 3
for arm in ['native', 'jco-js']:
    value = add('bench-output/' + arm, 'bench-output/build-results.json', 'completed public Buffer benchmark build/correctness report')
    assert len(value['records']) == 2 and {row['arm'] for row in value['records']} == {'native', 'jco-js'}
for replicate in [1, 2, 3]:
    for arm in ['native', 'jco-js']:
        directory = 'bench-clock-v2/replicate-' + str(replicate)
        value = add(directory + '/' + arm, directory + '/build-results.json',
                    'completed ordinary public Buffer benchmark build/correctness report',
                    {'runtimeTimingAcceptanceClaimed': False})
        assert len(value['records']) == 2
for arm in ['native', 'jco-js']:
    value = add('weval-experiment/v5-components/' + arm, 'weval-experiment/v5-components/build-results.json',
                'completed ordinary Release public Buffer A/B build/correctness report')
    assert len(value['records']) == 2
    final = BASE / 'weval-experiment/v5-components/results.json'
    assert read(final)['state'] == 'completed-ordinary-release-weval-native-jco-pair'
    roots[-1][2]['finalReport'] = {'path': str(final), 'sha256': sha(final)}


def digests(value):
    if isinstance(value, str):
        return {value} if re.fullmatch(r'[0-9a-f]{64}', value) else set()
    if isinstance(value, list):
        return set().union(*(digests(child) for child in value)) if value else set()
    if isinstance(value, dict):
        return set().union(*(digests(child) for key, child in value.items()
                             if key not in ['metadata', 'engineMetadata', 'componentizer', 'componentizerProvenance']))
    return set()


rows, skipped, seen = [], [], set()
for root, value, proof in roots:
    allowed = digests(value)
    components = {}
    for path in root.glob('*.component.wasm'):
        if path.is_file() and not path.is_symlink() and sha(path) in allowed:
            components[path.name] = sha(path)
    for path in sorted(root.iterdir()):
        if not re.fullmatch(r'.+\.(?:component|core\d*)\.wasm', path.name):
            continue
        assert not any(token in str(path).lower() for token in ['private', 'debug', 'oom', 'probe', 'candidate', 'diagnostic', 'raw-memory'])
        assert not any(part in path.parts for part in ['source', 'sources', 'native-freeze', 'componentize-source', 'harness', 'SDK', 'node_modules', 'project', 'build', 'inputs', 'input'])
        st = path.lstat()
        if not stat.S_ISREG(st.st_mode) or path.is_symlink() or st.st_nlink != 1 or st.st_flags or st.st_blocks * 512 <= 4 * 1024**2:
            skipped.append({'path': str(path), 'reason': 'not fresh regular uncompressed single-link allocation over4MiB'})
            continue
        digest = sha(path)
        association = {}
        if path.name.endswith('.component.wasm'):
            assert components.get(path.name) == digest, path
            association['componentShaMatchesTerminalReport'] = True
            if 'originalCase' in value:
                association['sameBytesAsLaterAcceptedCase'] = digest == value['laterAcceptedCase']['componentSha256']
        else:
            prefix = re.fullmatch(r'(.+)\.core\d*\.wasm', path.name).group(1)
            pair = prefix + '.component.wasm'
            choices = [pair] if pair in components else list(components) if len(components) == 1 else []
            assert len(choices) == 1, path
            association.update(componentPath=str(root / choices[0]), componentSha256=components[choices[0]])
            if digest in allowed:
                association['coreProof'] = 'explicit terminal packaging/core SHA'
            else:
                js = [f for f in root.glob('*.js') if not f.is_symlink() and path.name in f.read_text()]
                assert js, path
                association['generatedJsReferences'] = [{'path': str(f), 'sha256': sha(f)} for f in js]
        attrs = {}
        for name in subprocess.check_output(['/usr/bin/xattr', str(path)], text=True).splitlines():
            attrs[name] = hashlib.sha256(bytes.fromhex(subprocess.check_output(['/usr/bin/xattr', '-p', '-x', name, str(path)], text=True))).hexdigest()
        acl = subprocess.check_output(['/bin/ls', '-led', str(path)], text=True).splitlines()[1:]
        after = path.lstat()
        assert (after.st_ino, after.st_size, after.st_mtime_ns, after.st_flags, after.st_nlink) == (st.st_ino, st.st_size, st.st_mtime_ns, st.st_flags, st.st_nlink)
        assert str(path) not in seen
        seen.add(str(path))
        rows.append({'path': str(path), 'root': str(root), 'sha256': digest, 'device': st.st_dev, 'inode': st.st_ino,
                     'logicalBytes': st.st_size, 'allocatedBytes': st.st_blocks * 512, 'mode': stat.S_IMODE(st.st_mode),
                     'uid': st.st_uid, 'gid': st.st_gid, 'mtimeNs': st.st_mtime_ns, 'flags': st.st_flags, 'nlink': st.st_nlink,
                     'xattrDigests': attrs, 'acl': acl, 'terminalProof': proof, **association})
report = {'state': 'READ_ONLY_ADDITIONAL_COMPLETED_PUBLIC_OUTPUT_INVENTORY',
          'files': rows, 'eligibleCount': len(rows), 'allocatedBytes': sum(row['allocatedBytes'] for row in rows),
          'logicalBytes': sum(row['logicalBytes'] for row in rows), 'largestOneFileTemporaryLogicalBytes': max(row['logicalBytes'] for row in rows),
          'skipped': skipped, 'releaseAcceptanceOrCompatibilityClaim': False, 'compressionRecoveryMeasured': False,
          'compressionDeletionBuildOrGuestExecuted': False, 'quiescenceStillRequired': True,
          'excluded': ['v2 dynamic diagnostics and partial Path output', 'v1 unaccepted probe/partial Path output',
                       'benchmark diagnostic arm', 'private/debug/OOM/probe/candidate/raw-memory/engine/SDK/source/config paths']}
with (HERE / 'inventory.json').open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({key: report[key] for key in ['eligibleCount', 'allocatedBytes', 'logicalBytes', 'largestOneFileTemporaryLogicalBytes']}))
