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
        frozen_path = Path(summary['frozenInputs'])
        assert compact.sha256(frozen_path) == summary['frozenInputsSha256']
        frozen = {value['path']: value for value in json.loads(frozen_path.read_text())['files']}

        records = [json.loads(line) for line in journal_path.read_text().splitlines()]
        adopted = [value for value in records if value['event'] == 'after']
        assert len(adopted) == summary['compressedFiles'], path
        assert len(adopted) == len(frozen)
        prepared = [value for value in records if value['event'] == 'prepared']
        assert len(prepared) == len(adopted)
        assert all(not Path(value['rollbackPath']).exists() for value in prepared)
        assert not any(value['event'] in {'failure', 'rolled-back'} for value in records)

        assert sum(value['physicalBytesRecovered'] for value in adopted) == summary['physicalBytesRecovered'], path
        for value in adopted:
            file_path = Path(value['path'])
            assert value['path'] in frozen
            assert value['sha256'] == frozen[value['path']]['sha256']
            assert value['preservedMetadata'] == frozen[value['path']]['metadata']

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
    assert len(summaries) == 1 and len(entries) == 34, (len(summaries), len(entries))

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

    previous_receipts = {
        'tests/node-compat/storage-compaction-v11-pass2/compact.py': '37125bb77b4e35a81e187c1544364ea18638a3650850ba197e2b045e8119a757',
        'tests/node-compat/storage-compaction-v11-pass2/verify.py': 'b98a5acdc31cac6fbb99ff44be14be5b8a72f67a51f2d64b14a8c974742a205f',
        'tests/node-compat/storage-compaction-v11-pass2/README.md': '0ba60c5caba329c2248bffff3360d726a8ba08553f4c15f1a341128942b07733',
        'tests/node-compat/storage-compaction-v11-pass2/results.json': 'e2997f46b0adafaddd60ae462cc5ffb6ce5377828c66d8e5c5e3cb0fc1f59131',
        'tests/node-compat/storage-compaction-v11-pass2/index.json': '95c49a15f478f00a21d415bdc64f3488f35dc31a515bf05cb8087c013e829bc8',
        'tests/node-compat/storage-compaction-v11-pass1/compact.py': 'bdb410e5d49573770f5fa0ed9804a46b231e74f040b13322fa844329a4e18404',
        'tests/node-compat/storage-compaction-v11-pass1/verify.py': '38a7fef171aef0fcb44bccc0b6b68c5654161b345c69001e7285baf864ae856d',
        'tests/node-compat/storage-compaction-v11-pass1/README.md': 'bdf1b04158ac964c79a2417f9de247c830166c9aa41e4f9432191b02474b0d9c',
        'tests/node-compat/storage-compaction-v11-pass1/results.json': '9dc394cac72edc040ada9d6f85dde7e319b1e1df1e7701120eeb322cd494d320',
        'tests/node-compat/storage-compaction-v11-pass1/index.json': '76228b4a2692c2c3e3eaa58156c2cfd861b88dbeb326c413cadd96a652966075',
        'tests/node-compat/storage-compaction-v10-pass3/compact.py': '57376620408d5950d26bc9ce62489a15ee7883cb8ff9573dc28f4a38ee733042',
        'tests/node-compat/storage-compaction-v10-pass3/verify.py': '1fbe5361d84b12abf1d55fd19cc737a9bd20d0d899e3f2eb5c44acd8d2d2c4a6',
        'tests/node-compat/storage-compaction-v10-pass3/README.md': '03cfa59f9160d29f12ba9d46b754d72c2b7bcd5b6504dfd38110c10bd119b1d9',
        'tests/node-compat/storage-compaction-v10-pass3/results.json': 'c1382c32960c243a9da142647645e5c464a6c42d22b1756cff86217b0d8d39f3',
        'tests/node-compat/storage-compaction-v10-pass3/index.json': '2efd622658e3ea10d3811b6f8b8d287c3258434ad04960b1950269424bf0c855',
        'tests/node-compat/storage-compaction/results.json': '9f69c8fea9901834bfe31f6cd3fe361ca95287d6ed780893ad42f212363f34ae',
        'tests/node-compat/storage-compaction-v10/results.json': '6b50c35425ea0136dca10b57ae6eab0e9cd32266240b2f22ae2bbd5a0ab4c4f6',
        'tests/node-compat/storage-compaction/compact.py': 'f62523b7075ad578072f8f1f7d647ade8b1e5eb413c8c6afed077c016a13c939',
        'tests/node-compat/storage-compaction/verify.py': 'd02078bd1c45cd2fa32be8fb08e1195c821fd0eac1db7f822f52e80a1f8786ec',
        'tests/node-compat/storage-compaction/README.md': '8a9a1a8d45835aad5e6c9dfdf623eb7fc9e67e61af5ee176be20e13be481ac76',
        'tests/node-compat/storage-compaction-v10/compact.py': '04a80e033af69f71f71d4b62cca76d72d8c93b81dd65a2cb5ce7d15d782d5a0d',
        'tests/node-compat/storage-compaction-v10/verify.py': '6017cbdb7c5d2c6600ed6b9425a4389d135b3a1b7c72b4c75fa2f09444a73bbf',
        'tests/node-compat/storage-compaction-v10/README.md': '3b1f44387b396473dba930851778bb39b670c350178c5124ea295796966e97fa',
        'tests/node-compat/storage-compaction-v10-pass2/compact.py': 'e340eb560e423100b25d1794f0d9846b57f174487f30c5c19d3745b050758fe6',
        'tests/node-compat/storage-compaction-v10-pass2/verify.py': 'c6ef6d6aa94188fbb0a8d6fd7b0611c19594fe4a5ba245ba6115f13b8fec812e',
        'tests/node-compat/storage-compaction-v10-pass2/README.md': '3024aa12901856ff58dbbb0d1ea408c4875766c5d26df11a4f5f701f178a23bf',
        'tests/node-compat/storage-compaction-v10-pass2/results.json': 'fd264bc4984e4e14d772905f680a883925de19fbc017679b8f4c7c509be6a986',
    }
    for previous, expected in previous_receipts.items():
        assert compact.sha256(previous) == expected
    result = {
        'previousReceiptsUnchanged': previous_receipts,
        'frozenInventoryVerified': True,
        'rollbackLinksReleasedAfterSuccess': True,
        'rollbackFailureBranchExecuted': False,
        'status': 'PASS', 'timestampUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Completed v11 release-v3 strict-runtime/strict-late/strict-callbacks only',
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
