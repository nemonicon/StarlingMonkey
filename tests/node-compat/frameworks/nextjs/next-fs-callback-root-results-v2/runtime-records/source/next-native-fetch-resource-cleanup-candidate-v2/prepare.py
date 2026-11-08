"""Text-only exact three-cast Source successor. Default checks; --write creates absent text.
Never invokes compiler, tools, native APIs, guest, donor copier or process owner.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent

def row(path):
    path = Path(path); data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))

def checked(ref):
    path = Path(ref['path'])
    assert path.is_absolute() and path.resolve(strict=True) == path
    assert not path.is_symlink() and path.is_file() and path.stat().st_nlink == 1
    assert row(path) == ref
    return path.read_text()

def family(ref):
    data = json.loads(checked(ref)); root = Path(ref['path']).parent
    names = [item['path'] for item in data['files']]
    assert len(set(names)) == len(names)
    files = set(); dirs = {'.'}
    for name in names:
        rel = Path(name); assert not rel.is_absolute() and '..' not in rel.parts
        for parent in rel.parents:
            dirs.add(parent.as_posix())
    actual_dirs = {'.'}
    for path in root.rglob('*'):
        assert not path.is_symlink()
        if path.is_dir(): actual_dirs.add(path.relative_to(root).as_posix())
        else:
            assert path.is_file(); files.add(path.relative_to(root).as_posix())
    assert files == set(names) | {'index.json'} and actual_dirs == dirs
    for item in data['files']: checked(dict(item, path=str(root/item['path'])))

def render():
    manifest = json.loads((HERE/'version-manifest.json').read_text())
    family(manifest['parentSourceIndex'])
    parent_images = json.loads(checked(manifest['parentAfterimages']))
    parent_root = Path(manifest['parentSourceIndex']['path']).parent
    selected = [item for item in parent_images['files'] if item['relativePath'] == manifest['relativePath']]
    assert len(selected) == 1
    item = selected[0]['after']
    assert manifest['parentAfterimage'] == dict(item, path=str(parent_root/item['path']))
    expected_inherited = {item['relativePath']: dict(item['after'], path=str(parent_root/item['after']['path']))
                          for item in parent_images['files'] if item['relativePath'] != manifest['relativePath']}
    assert len(expected_inherited) == 5
    assert {item['relativePath']: item['after'] for item in manifest['inheritedAfterimages']} == expected_inherited
    before = checked(manifest['before'])
    assert before == checked(manifest['parentAfterimage'])
    after = before
    for fix in manifest['knownFixes']:
        assert after.count(fix['before']) == 1
        after = after.replace(fix['before'], fix['after'])
    assert len(after.encode()) - len(before.encode()) == manifest['expectedAddedBytes'] == 18
    for ref in manifest['inheritedAfterimages']: checked(ref['after'])
    for key in ['ownershipPlanInherited','normalTestsPlanInherited','apiWitnessesInherited']: checked(manifest[key])
    rel = manifest['relativePath']
    patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                       fromfile='a/'+rel, tofile='b/'+rel))
    return manifest, after, patch

def exclusive(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as stream: stream.write(value.encode()); stream.flush(); os.fsync(stream.fileno())

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--write', action='store_true')
    args = parser.parse_args(); manifest, after, patch = render()
    path = HERE/'after'/manifest['relativePath']
    if args.write:
        exclusive(path, after); exclusive(HERE/'nodiscard.patch', patch)
    else:
        assert path.read_text() == after and (HERE/'nodiscard.patch').read_text() == patch
        assert row(path) == manifest['after']
    print(json.dumps(dict(sourceOnly=True, after=row(path), addedBytes=18,
                         changedFiles=1, inheritedAfterimages=5, compilerOrNativeOrGuestExecuted=False)))

if __name__ == '__main__': main()
