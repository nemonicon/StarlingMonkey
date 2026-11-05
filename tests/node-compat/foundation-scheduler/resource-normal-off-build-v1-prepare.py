"""Issue one fresh normal-OFF build phase after actual stage/source reviews."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import sys

S = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler')
SOURCE = S / 'resource-build-controller-candidate-v1'


def row(path):
    raw = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(value):
    assert row(value['path']) == value
    return json.loads(Path(value['path']).read_bytes())


def family(value):
    index = read(value)
    root = Path(value['path']).parent
    names = set()
    for member in index['files']:
        name = member['path']
        assert name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        assert row(root / name) == dict(member, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'}


def write(name, value):
    path = S / name
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
    return row(path)


def main():
    assert __debug__ and sys.dont_write_bytecode
    controller = row(SOURCE / 'index.json')
    assert controller['sha256'] == 'f75104547d0c39fd815101906a9f5f8065b5f486e522fd9fab2370cf01c72bd8'
    family(controller)
    peer_index = row(S / 'independent-resource-build-controller-source-review-v1/index.json')
    assert peer_index['sha256'] == 'de4a0b4351e74e230cff2ac87e1b1479fb4251d45771c8345709ad9b6fdbd18e'
    family(peer_index)
    peer = dict(index=peer_index, result=row(Path(peer_index['path']).parent / 'results.json'))
    result = read(peer['result'])
    assert result['controllerSourceIndexSha256'] == controller['sha256'] and result['sourceReviewPassed'] is True
    references = read(row(SOURCE / 'references.json'))
    root = read(row(SOURCE / 'future-root-authority.template.json'))
    root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_BUILD_V1',
                issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), buildAllowed=True,
                controllerIndex=controller, controllerEntry=row(SOURCE / 'controller.py'),
                controllerIndependentReview=peer, sourceIndependentReview=references['sourceReview'],
                independentStageReview=references['actualStageReview'], actualStageResult=references['actualStageResult'],
                actualStageRootObservation=references['actualStageRootObservation'],
                scope='One new normal-OFF Release342 native build with actual timer installation; no GC reconfiguration/freeze/engine or guest execution')
    spec = importlib.util.spec_from_file_location('genuine_resource_build_phase_data_model', SOURCE / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.validate_root(root, controller)
    guard.validate_peer(result, controller)
    authority = write('resource-normal-off-build-v1-root-authority.json', root)
    config = read(row(SOURCE / 'future-config.template.json'))
    config.update(controllerIndex=controller, rootAuthority=authority)
    config_row = write('resource-normal-off-build-v1-root-config.json', config)
    print(json.dumps(dict(rootAuthority=authority, config=config_row, actualPureRootAndPeerModelsPassed=True)))


if __name__ == '__main__':
    main()
