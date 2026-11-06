"""Read/hash-only intake. Does not import fixtures, crypto modules or action code."""
import hashlib
import json
import pathlib
import stat

OWN = pathlib.Path(__file__).resolve().parent


def main():
    refs = json.loads((OWN / 'references.json').read_text())
    inputs = {}
    checks = 0

    def checked(row):
        nonlocal checks
        path = pathlib.Path(row['path'])
        info = path.lstat()
        assert stat.S_ISREG(info.st_mode), str(path)
        raw = path.read_bytes()
        assert len(raw) == row['bytes'], str(path)
        assert hashlib.sha256(raw).hexdigest() == row['sha256'], str(path)
        prior = inputs.setdefault(str(path), row)
        assert prior == row
        checks += 4
        return raw

    def walk(value):
        if isinstance(value, dict):
            if set(('path', 'sha256', 'bytes')) <= set(value):
                checked({key: value[key] for key in ('path', 'sha256', 'bytes')})
            else:
                for child in value.values():
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(refs)
    families = []
    for row in (refs['fixtureIndex'], refs['nodeOracleReview']['index']):
        root = pathlib.Path(row['path']).parent
        index = json.loads(checked(row))
        names = []
        for member in index['files']:
            name = member['path']
            assert name not in names and not pathlib.PurePosixPath(name).is_absolute()
            assert '..' not in pathlib.PurePosixPath(name).parts
            names.append(name)
            checked({**member, 'path': str(root / name)})
        actual = sorted(str(q.relative_to(root)) for q in root.rglob('*') if q.is_file())
        assert actual == sorted(names + ['index.json']), str(root)
        families.append({'index': row, 'indexedMembers': len(names), 'actualFiles': len(actual)})

    frames = [json.loads(line) for line in checked(refs['nodeOracleStdout']).decode().splitlines()]
    assert len(frames) == 4 and frames[0]['kind'] == 'host-node-identity'
    assert frames[0]['version'] == 'v22.14.0' and frames[0]['guestProviderProof'] is False
    for ordinal, (frame, row) in enumerate(zip(frames[1:], refs['nodeOracleRawReturns']), 1):
        assert frame['sequence'] == ordinal and frame['name'] == 'run' and frame['kind'] == 'return'
        assert frame['observed']['type'] == 'string'
        raw = frame['observed']['value'].encode()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
        assert row['sequence'] == ordinal and row['jsonlLine'] == ordinal + 1
        checks += 7
    review = json.loads(checked(refs['nodeOracleReview']['result']))
    assert review['state'] == 'INDEPENDENT_NODE_CRYPTO_HASH_HMAC_NODE22_ORACLE_RESULTS_REVIEW_PASSED_V1'
    assert review['verifiedPassed'] is True
    first = json.loads(frames[1]['observed']['value'])
    assert first['nodeComparable'] == review['acceptedOracleRecords']
    assert first['profilePolicy'] == review['separateObservedNodePolicyRecords']
    checks += 4
    assert refs['actualGuestStrings'] is None and refs['actualComponentProof'] is None and refs['runtimeRootAuthority'] is None
    return {'schemaVersion': 1, 'passed': True, 'checks': checks, 'files': sorted(inputs.values(), key=lambda r: r['path']), 'families': families, 'actualGuestStrings': None, 'newOracleOrCryptoOrFixtureExecution': False}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
