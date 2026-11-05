"""Issue a distinct normal-only freeze phase after actual build/source reviews."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import sys

S = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler')
SOURCE = S / 'resource-freezer-candidate-v1'


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
    own = row(SOURCE / 'index.json')
    assert own['sha256'] == 'f88db73e4541e72bf37fa1c2a684257a737fde1dc685a34f00335ebc0705b072'
    family(own)
    peer_dir = S / 'independent-resource-freezer-source-review-v1'
    peer_index = row(peer_dir / 'index.json')
    assert peer_index['sha256'] == '4724fa4a4ae3151f5235c2082967dd1ce25090ad1ccd0e3664d1103a56db348c'
    family(peer_index)
    peer = dict(index=peer_index, result=row(peer_dir / 'results.json'))
    passed = read(peer['result'])
    refs = read(row(SOURCE / 'references.json'))
    family(refs['actualBuildReview']['index'])
    build = read(refs['actualBuildReview']['result'])
    assert build['verifiedPassed'] is True and build['engineSha256'] == 'fec7a900f0c04815e3609d2f9a5ed94056d854bd1a8f241bf74cb5f3f475a704'
    root = read(row(SOURCE / 'future-root-authority.template.json'))
    root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_FREEZE_V1',
                issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), freezerIndex=own,
                freezerEntry=row(SOURCE / 'freeze.py'), sourceIndependentReview=peer,
                actualBuildReview=refs['actualBuildReview'], actualBuildContract=refs['actualBuildContract'],
                actualBuildResult=build['actualBuildResult'], actualBuildRootObservation=build['rootObservation'],
                engine=refs['engine'], metadata=refs['metadata'], freezeAllowed=True, postBuildNinjaCommandsAllowed=True,
                scope='Fresh normal-OFF342 freeze and post-build Ninja command listing only; preserve raw metadata/source/context and all original build inputs')
    spec = importlib.util.spec_from_file_location('genuine_resource_freeze_phase_models', SOURCE / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.root_model(root, own)
    guard.peer_model(passed, own)
    authority = write('resource-normal-off-freeze-v1-root-authority.json', root)
    config = read(row(SOURCE / 'future-config.template.json'))
    config.update(freezerIndex=own, rootAuthority=authority)
    config_row = write('resource-normal-off-freeze-v1-root-config.json', config)
    print(json.dumps(dict(rootAuthority=authority, config=config_row, actualPurePhaseModelsPassed=True)))


if __name__ == '__main__':
    main()
