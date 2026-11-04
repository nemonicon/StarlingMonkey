"""Read-only capacity inventory of explicit accepted ordinary public outputs.

Writes only a new JSON audit beside this file. No compression/deletion/build/guest.
"""
from pathlib import Path
import collections
import hashlib
import json
import os
import re
import stat
import subprocess

REPO = Path(__file__).resolve().parents[3]
BASE = Path('/tmp/starling-node-compat')
ARCHIVES = REPO / 'tests/node-compat/milestones'
OUTPUT = Path(__file__).with_name('results.json')
NAME = re.compile(r'.+\.(?:component|core\d*)\.wasm\Z')
CORE = re.compile(r'(.+)\.core\d*\.wasm\Z')
MINIMUM = 4 * 1024 * 1024
FORBIDDEN = {'source', 'sources', 'native-freeze', 'componentize-source', 'harness',
             'node_modules', 'project', 'build', 'input', 'inputs'}
TOKENS = ('private', 'debug', 'oom', 'probe', 'candidate', 'benchmark', 'matched', 'diagnostic')


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def normalized(value):
    return str(value).replace('/private/tmp/starling-node-compat/', '/tmp/starling-node-compat/')


reports = {}


def accepted(milestone, name):
    key = milestone + '/' + name
    if key in reports:
        return reports[key]
    directory = ARCHIVES / milestone
    summary_path = directory / 'results.json'
    summary = json.loads(summary_path.read_bytes())
    record, = [row for row in summary['reports'] if row['path'] == name]
    report_path = directory / name
    assert sha(report_path) == record['sha256']
    original = Path(normalized(record['source']))
    assert original.is_file() and not original.is_symlink()
    assert sha(original) == record['sha256'], original
    value = json.loads(report_path.read_bytes())
    proof = {'milestoneSummary': str(summary_path.relative_to(REPO)),
             'milestoneSummarySha256': sha(summary_path),
             'archivedReport': str(report_path.relative_to(REPO)),
             'reportSha256': record['sha256'], 'currentOriginalReport': str(original)}
    reports[key] = (value, proof)
    return value, proof


roots = []


def add(milestone, report, directory, case=None):
    value, proof = accepted(milestone, report)
    path = BASE / directory
    assert path.is_dir() and not path.is_symlink(), path
    assert not any(part in FORBIDDEN or any(token in part.lower() for token in TOKENS)
                   for part in path.relative_to(BASE).parts)
    if case is not None:
        assert case['status'] == 'pass'
        proof = {**proof, 'caseName': case['name'], 'caseStatus': case['status']}
        if 'directory' in case:
            assert normalized(case['directory']) == str(path)
        value = case
    roots.append((path, value, proof))


# Only roots named by immutable accepted report closures. In particular v1 Path
# was explicitly not accepted; neither old duplicate e2e attempt is selected.
for report, directory in [('native.json', 'native'), ('entropy-off.json', 'entropy-off'),
                          ('entropy-runtime.json', 'entropy-runtime'),
                          ('http-off.json', 'http-off'), ('http-runtime.json', 'http-runtime')]:
    add('entropy-v1', report, 'foundations-v1/' + directory)
for report, prefix in [('upstream-builtins-runtime.json', 'upstream-runtime'),
                       ('upstream-builtins-off.json', 'upstream-off')]:
    value, _ = accepted('entropy-v1', report)
    assert value['failed'] == 0 and value['passed'] == len(value['results'])
    for case in value['results']:
        add('entropy-v1', report, 'foundations-v1/' + prefix + '/' + case['name'], case)
for report, directory in [('upstream-e2e.json', 'upstream-runtime-e2e/starling-e2e'),
                          ('upstream-initialization-off.json', 'upstream-off')]:
    value, _ = accepted('entropy-v1', report)
    assert value['failed'] == 0 and value['passed'] == len(value['results'])
    if report == 'upstream-initialization-off.json':
        assert all(case['pass'] is True for case in value['results'])
    else:
        assert all(case['status'] == 'pass' for case in value['results'])
    if report == 'upstream-e2e.json':
        for case in value['results']:
            if 'componentSha256' in case:
                add('entropy-v1', report, 'foundations-v1/' + directory + '/' + case['name'], case)
    else:
        add('entropy-v1', report, 'foundations-v1/' + directory)
for milestone, choices in [
    ('foundations-v3', [('native.json', 'native'), ('path.json', 'path')]),
    ('foundations-v4', [('native.json', 'native'), ('path.json', 'path'),
                        ('events.json', 'events'), ('entropy-runtime.json', 'entropy-runtime'),
                        ('http.json', 'http-joint')])]:
    for report, directory in choices:
        add(milestone, report, milestone + '/' + directory)
for report, directory in [('native.json', 'native'), ('http.json', 'http')]:
    add('allocation-r2', report, 'phase1-validation/allocation-r2/' + directory)


def digests(value):
    output = set()
    if isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value):
        output.add(value)
    elif isinstance(value, dict):
        for key, child in value.items():
            if key not in ('componentizerProvenance', 'engineMetadata', 'metadata'):
                output.update(digests(child))
    elif isinstance(value, list):
        for child in value:
            output.update(digests(child))
    return output


eligible = []
skipped = []
root_counts = []
for root, value, proof in roots:
    permitted = digests(value)
    components = {}
    for path in sorted(root.glob('*.component.wasm')):
        assert path.is_file() and not path.is_symlink()
        digest = sha(path)
        assert digest in permitted, ('Component not authenticated by accepted report', path)
        components[path.name] = digest
    count = 0
    for path in sorted(root.iterdir()):
        if not path.name.endswith('.wasm'):
            continue
        information = path.lstat()
        reason = None
        if not NAME.fullmatch(path.name) or 'engine' in path.name.lower():
            reason = 'not-explicit-component-or-transpiled-core'
        elif not stat.S_ISREG(information.st_mode) or path.is_symlink():
            reason = 'nonregular-or-symlink'
        elif information.st_nlink != 1:
            reason = 'multiple-hardlinks'
        elif information.st_flags & 32:
            reason = 'already-compressed'
        elif information.st_flags:
            reason = 'other-flags'
        elif information.st_blocks * 512 <= MINIMUM:
            reason = 'physical-allocation-not-over-4MiB'
        if reason:
            skipped.append({'path': str(path), 'reason': reason})
            continue
        digest = sha(path)
        association = {'completionProof': proof}
        if path.name.endswith('.component.wasm'):
            assert components[path.name] == digest
            association['acceptedComponentSha256'] = digest
        else:
            core_name = CORE.fullmatch(path.name).group(1)
            paired = core_name + '.component.wasm'
            choices = [paired] if paired in components else list(components) if len(components) == 1 else []
            assert len(choices) == 1, ('Ambiguous transpiled-core closure', path)
            association.update(acceptedComponentPath=str(root / choices[0]),
                               acceptedComponentSha256=components[choices[0]])
            if digest in permitted:
                association.update(coreProof='Explicit core SHA in accepted packaging audit',
                                   acceptedCoreSha256=digest)
            else:
                js = [f for f in root.glob('*.js') if not f.is_symlink()
                      and path.name in f.read_text()]
                assert js, ('No generated JS reference to core', path)
                association.update(coreProof='Generated JS dependency of accepted passed component',
                                   generatedJsReferences=[{'path': str(f), 'sha256': sha(f)} for f in js])
        attr_names = subprocess.check_output(['/usr/bin/xattr', str(path)], text=True).splitlines()
        attrs = {}
        for name in attr_names:
            raw = subprocess.check_output(['/usr/bin/xattr', '-p', '-x', name, str(path)], text=True)
            attrs[name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
        assert 'com.apple.decmpfs' not in attrs
        acl = subprocess.check_output(['/bin/ls', '-led', str(path)], text=True).splitlines()[1:]
        after = path.lstat()
        assert (after.st_ino, after.st_size, after.st_mtime_ns, after.st_flags, after.st_nlink) == (
            information.st_ino, information.st_size, information.st_mtime_ns, information.st_flags, information.st_nlink)
        eligible.append({'path': str(path), 'root': str(root), 'sha256': digest,
                         'logicalBytes': information.st_size, 'allocatedBytes': information.st_blocks * 512,
                         'inode': information.st_ino, 'device': information.st_dev,
                         'mode': stat.S_IMODE(information.st_mode), 'uid': information.st_uid,
                         'gid': information.st_gid, 'mtimeNs': information.st_mtime_ns,
                         'flags': information.st_flags, 'nlink': information.st_nlink,
                         'xattrDigests': attrs, 'acl': acl, **association})
        count += 1
    root_counts.append({'root': str(root), 'eligibleFiles': count, 'completionProof': proof})
assert len({row['path'] for row in eligible}) == len(eligible)
report = {'state': 'READ_ONLY_ACCEPTED_ORDINARY_PUBLIC_OUTPUT_CAPACITY_AUDIT',
          'roots': root_counts, 'files': eligible, 'skipped': skipped,
          'eligibleCount': len(eligible), 'allocatedBytes': sum(row['allocatedBytes'] for row in eligible),
          'logicalBytes': sum(row['logicalBytes'] for row in eligible),
          'largestOneFileTemporaryLogicalBytes': max(row['logicalBytes'] for row in eligible),
          'metadataPreservationFeasibleWithPriorAuditedAlgorithm': True,
          'allCandidatesRegularSingleLinkFlags0': True,
          'allAcceptedComponentsAndCurrentReportBytesAuthenticated': True,
          'transpiledCoreProof': 'Generated JS reference plus authenticated passed component in same exact completed root; current core SHA frozen here',
          'measuredCompressionRecovery': None, 'priorCompressedFilesReselected': False,
          'excluded': ['all v2 outputs without explicit immutable accepted milestone report closure',
                       'v1 Path explicitly not accepted', 'v1 original duplicate e2e attempt',
                       'v3 path benchmarks/adapter controls', 'all private/debug/OOM/probe/candidate/engine/source/SDK/config paths'],
          'compressionDeletionBuildOrGuestExecuted': False}
with OUTPUT.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({key: report[key] for key in ['eligibleCount', 'allocatedBytes', 'logicalBytes',
                                              'largestOneFileTemporaryLogicalBytes']}))
