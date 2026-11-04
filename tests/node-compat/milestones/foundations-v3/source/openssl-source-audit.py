"""Compare every source file with the pinned archive and two reviewed patches.

Read-only audit. This is a guest dependency proof, not a host modification.
The build receipt identifies the actually selected source/cache/library.
"""
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ARCHIVE_SHA256 = 'dfdd77e4ea1b57ff3a6dbde6b0bdc3f31db5ac99e7fdd4eaf9e1fbb6ec2db8ce'
PATCHED = {
    'crypto/uid.c': '86b53aecb1046e81dfbfe74d779704b408cbaa70abfb9a7d1cc98211bdc8ba08',
    'crypto/rand/rand_lib.c': 'e8c853b5d609b5b13f3a63ddcd88047a37fb75afa59e88d1950907c5a85bcd95',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit(build_directory):
    build = Path(build_directory).resolve()
    receipt_path = build / 'openssl-profile-receipt.txt'
    receipt = dict(line.split('=', 1) for line in receipt_path.read_text().splitlines())
    source = Path(receipt['sourceDir'])
    archives = list((build / '_deps').rglob('openssl-3.0.17.tar.gz'))
    assert len(archives) == 1, 'Need exact downloaded archive from this configure'
    archive = archives[0]
    assert digest(archive.read_bytes()) == ARCHIVE_SHA256
    expected = {}
    with tarfile.open(archive) as contents:
        for member in contents.getmembers():
            if not member.isfile():
                assert member.isdir(), f'Unexpected archive resource: {member.name}'
                continue
            prefix, separator, name = member.name.partition('/')
            assert separator and prefix == 'openssl-3.0.17' and '..' not in Path(name).parts
            expected[name] = PATCHED.get(name) or digest(contents.extractfile(member).read())
    actual = {}
    for path in sorted(source.rglob('*')):
        assert not path.is_symlink(), f'Unexpected source symlink: {path}'
        if path.is_file():
            actual[str(path.relative_to(source))] = digest(path.read_bytes())
    assert actual == expected, 'Dependency source differs from exact archive plus reviewed two-file patch'
    manifest = [{'path': name, 'sha256': value} for name, value in sorted(actual.items())]
    return {
        'schemaVersion': 1, 'state': 'verified-complete-source',
        'buildDirectory': str(build), 'sourceDirectory': str(source),
        'archivePath': str(archive), 'archiveSha256': ARCHIVE_SHA256,
        'receiptSha256': digest(receipt_path.read_bytes()),
        'sourceFilesVerified': len(manifest), 'unexpectedFiles': [], 'missingFiles': [],
        'patchedSources': PATCHED,
        'sourceManifestSha256': digest(json.dumps(manifest, separators=(',', ':')).encode()),
        'auditScriptSha256': digest(Path(__file__).read_bytes()),
        'scope': 'Every regular source file and exact file set; out-of-tree generated build files are separate receipts',
    }


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1]), indent=2))
