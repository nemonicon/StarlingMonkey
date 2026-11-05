"""Issue one reviewed read-only verifier phase; never invoke the verifier here."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'ownership-secret-verifier-controller-candidate-v1'
PEER = HERE / 'independent-ownership-secret-verifier-controller-source-review-v1'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1')
EXTERNAL = Path(str(OUT) + '-external-root')


def row(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def family(path, expected):
    descriptor = row(path)
    assert descriptor['sha256'] == expected
    index = json.loads(path.read_bytes())
    names = {'index.json'}
    for item in index['files']:
        name = item['path']
        assert name not in names and not Path(name).is_absolute() and '..' not in Path(name).parts
        names.add(name)
        assert row(path.parent / name) == dict(item, path=str(path.parent / name))
    assert {str(p.relative_to(path.parent)) for p in path.parent.rglob('*') if p.is_file()} == names
    return descriptor


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    return row(path)


def main():
    assert not OUT.exists() and not OUT.is_symlink() and not EXTERNAL.exists() and not EXTERNAL.is_symlink()
    source = family(SOURCE / 'index.json', '0fc0082da7d9842bf9bd9e46a28760e2cea5f698eec62880f0150c572d94a78f')
    peer = family(PEER / 'index.json', 'a219119659f8a3cf0da2b0be0eceba9bf6d3d6ff2b453c4c2da50dcaa4348e7b')
    peer_result = json.loads((PEER / 'results.json').read_bytes())
    assert peer_result['state'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_VERIFIER_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert peer_result['controllerSourceIndexSha256'] == source['sha256']
    assert peer_result['sourceOnly'] is peer_result['sourceReviewPassed'] is True
    for key in ('ownerActionsInvoked', 'hostActionsInvoked', 'verifierActionsInvoked'):
        assert peer_result[key] is False
    root = json.loads((SOURCE / 'future-root-authority.template.json').read_bytes())
    assert root['state'] is root['controllerIndex'] is root['controllerEntry'] is root['controllerIndependentReview'] is None
    assert root['verifierReadOnlyAllowed'] is False
    root.update(state='ROOT_REVIEWED_SECRET_OWNER355_FROZEN_VERIFIER_READ_ONLY_V1',
                controllerIndex=source, controllerEntry=row(SOURCE / 'controller.py'),
                controllerIndependentReview=dict(index=peer, result=row(PEER / 'results.json')),
                verifierReadOnlyAllowed=True, issuerSource=row(Path(__file__).resolve()),
                issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                precedingGitCheckpoint='23c40067')
    authority = save(HERE / 'ownership-secret-frozen-verifier-v1-root-authority.json', root)
    config = dict(schemaVersion=1, state='SECRET_OWNER355_VERIFIER_CONTROLLER_CONFIG_V1',
                  controllerIndex=source, rootAuthority=authority)
    descriptor = save(HERE / 'ownership-secret-frozen-verifier-v1-root-config.json', config)
    print(json.dumps(descriptor))


if __name__ == '__main__':
    main()
