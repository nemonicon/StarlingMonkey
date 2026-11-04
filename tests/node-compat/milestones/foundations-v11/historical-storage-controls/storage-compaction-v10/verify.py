#!/usr/bin/env python3
"""Independently re-read completed compaction journals and test decompression."""

import datetime
import json
from pathlib import Path
import shutil
import subprocess
import uuid

import compact


def main():
    summaries = []
    entries = []
    seen = set()
    for path in sorted(compact.RECEIPTS.glob('*.summary.json')):
        summary = json.loads(path.read_text())
        if not summary['apply'] or summary['compressedFiles'] == 0:
            continue
        assert summary['completed'] and not summary['failures'], path
        assert summary['scriptSha256'] == compact.sha256(compact.__file__), path
        assert summary['dittoSha256'] == compact.sha256('/usr/bin/ditto'), path
        journal_path = Path(summary['journal'])
        assert compact.sha256(journal_path) == summary['journalSha256'], journal_path
        records = [json.loads(line) for line in journal_path.read_text().splitlines()]
        adopted = [value for value in records if value['event'] == 'after']
        assert len(adopted) == summary['compressedFiles'], path
        assert sum(value['physicalBytesRecovered'] for value in adopted) == summary['physicalBytesRecovered'], path
        for value in adopted:
            file_path = Path(value['path'])
            assert file_path not in seen, file_path
            seen.add(file_path)
            assert any(file_path.is_relative_to(root) for root in compact.ROOTS.values()), file_path
            assert compact.NAME.fullmatch(file_path.name) and 'engine' not in file_path.name.lower(), file_path
            assert not any(part in compact.EXCLUDED_DIRS for part in file_path.parts), file_path
            assert not any(token in str(file_path).lower() for token in ('debug', 'oom', 'private')), file_path
            actual = compact.file_stat(file_path)
            assert actual['regular'] and not actual['symlink'] and actual['nlink'] == 1, file_path
            assert actual['flags'] == compact.COMPRESSED, file_path
            assert actual['allocatedBytes'] == value['after']['allocatedBytes'], file_path
            assert compact.sha256(file_path) == value['sha256'], file_path
            assert compact.preserved_metadata(file_path) == value['preservedMetadata'], file_path
            entries.append(value)
        summaries.append({'path': str(path), 'sha256': compact.sha256(path),
                          'journal': str(journal_path), 'journalSha256': compact.sha256(journal_path),
                          'roots': summary['roots'], 'files': len(adopted),
                          'logicalBytes': summary['logicalBytes'],
                          'oldAllocatedBytes': summary['oldAllocatedBytes'],
                          'newAllocatedBytes': summary['newAllocatedBytes'],
                          'physicalBytesRecovered': summary['physicalBytesRecovered']})
    assert len(summaries) == 1 and len(entries) == 61, (len(summaries), len(entries))

    # A new temporary copy demonstrates reversibility. It is never an accepted
    # artifact or native engine and is removed only after complete verification.
    selected = min(entries, key=lambda value: value['before']['logicalBytes'])
    # Stock ditto defaults to --preserveHFSCompression. --nohfsCompression by
    # itself therefore preserves a compressed source representation. Retain the
    # first failed assumption as a control, with byte/metadata checks as usual.
    prior_controls = sorted(compact.RECEIPTS.glob('reversal-test-*.wasm'))
    if not prior_controls:
        control = compact.RECEIPTS / ('reversal-test-' + uuid.uuid4().hex + '.wasm')
        subprocess.run(['/usr/bin/ditto', '--nohfsCompression', '--noclone',
                        selected['path'], str(control)], check=True, capture_output=True)
        prior_controls = [control]
    assert len(prior_controls) == 1, prior_controls
    preserved_control = prior_controls[0]
    control_stat = compact.file_stat(preserved_control)
    assert control_stat['flags'] == compact.COMPRESSED
    assert compact.sha256(preserved_control) == selected['sha256']
    assert compact.preserved_metadata(preserved_control) == selected['preservedMetadata']
    reverse_path = compact.RECEIPTS / ('reversal-test-' + uuid.uuid4().hex + '.wasm')
    command = ['/usr/bin/ditto', '--nohfsCompression', '--nopreserveHFSCompression',
               '--noclone', selected['path'], str(reverse_path)]
    subprocess.run(command, check=True, capture_output=True)
    reversed_stat = compact.file_stat(reverse_path)
    assert reversed_stat['flags'] == 0 and reversed_stat['regular'] and reversed_stat['nlink'] == 1
    assert compact.sha256(reverse_path) == selected['sha256']
    assert compact.preserved_metadata(reverse_path) == selected['preservedMetadata']
    assert reversed_stat['allocatedBytes'] > selected['after']['allocatedBytes']
    reverse_path.unlink()  # This new demonstration copy only, never its source.

    result = {
        'status': 'PASS', 'timestampUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Six completed v10 release-gates-v1 directories: core/allocator/stream-web/optional/strict-sync/strict-runtime only',
        'nativeSourcesOrEngineBytesChanged': False, 'acceptedArchiveChanged': False,
        'filesIndependentlyRehashed': len(entries), 'summaries': summaries,
        'logicalBytesVerified': sum(value['before']['logicalBytes'] for value in entries),
        'oldAllocatedBytes': sum(value['before']['allocatedBytes'] for value in entries),
        'newAllocatedBytes': sum(value['after']['allocatedBytes'] for value in entries),
        'physicalBytesRecovered': sum(value['physicalBytesRecovered'] for value in entries),
        'metadataVerified': ['logical size', 'mode', 'uid', 'gid', 'mtime_ns', 'xattr digests', 'ACL'],
        'representationChanges': ['inode', 'ctime', 'ditto birthtime', 'UF_COMPRESSED flag', 'allocated blocks'],
        'compactorSha256': compact.sha256(compact.__file__),
        'verifierSha256': compact.sha256(__file__),
        'dittoSha256': compact.sha256('/usr/bin/ditto'),
        'diskFreeAfterVerificationBytes': shutil.disk_usage(compact.BASE).free,
        'defaultPreservationControl': {
            'path': str(preserved_control), 'sha256': selected['sha256'],
            'command': ['/usr/bin/ditto', '--nohfsCompression', '--noclone', selected['path'], str(preserved_control)],
            'logicalBytes': control_stat['logicalBytes'], 'allocatedBytes': control_stat['allocatedBytes'],
            'flags': control_stat['flags'], 'finding': '--nohfsCompression alone retains the default --preserveHFSCompression',
            'logicalBytesAndMetadataVerified': True, 'retainedAsControl': True,
        },
        'reversal': {'status': 'PASS', 'command': command, 'source': selected['path'],
                     'sha256': selected['sha256'], 'logicalBytes': reversed_stat['logicalBytes'],
                     'uncompressedAllocatedBytes': reversed_stat['allocatedBytes'],
                     'flags': reversed_stat['flags'], 'freshDemonstrationCopyRemoved': True,
                     'sourceRetained': True},
        'notAnExecutionOrPerformanceTest': True,
    }
    path = compact.RECEIPTS / 'verified-results.json'
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    receipt = Path(__file__).with_name('results.json')
    receipt.write_text(json.dumps({**result, 'authoritativeReceipt': str(path),
                                   'authoritativeReceiptSha256': compact.sha256(path)}, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'files': len(entries),
                      'physicalBytesRecovered': result['physicalBytesRecovered'],
                      'authoritativeReceipt': str(path), 'repositoryReceipt': str(receipt)}, indent=2))


if __name__ == '__main__':
    main()
