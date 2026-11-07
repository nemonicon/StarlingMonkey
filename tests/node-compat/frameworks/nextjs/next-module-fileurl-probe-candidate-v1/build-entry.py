"""Source assembly only. Default --check is read-only; --write creates absent text files.
No Node, module import, engine, component constructor, filesystem fixture staging or host action.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent


def descriptor(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def checked(row):
    path = Path(row['path'])
    assert path.is_absolute() and path.resolve(strict=True) == path and path.is_file()
    assert not path.is_symlink() and path.stat().st_nlink == 1
    assert descriptor(path) == row
    return path.read_text()


def family(row):
    index = json.loads(checked(row))
    root = Path(row['path']).parent
    expected = {item['path']: item for item in index['files']}
    assert len(expected) == len(index['files'])
    actual = set()
    for path in root.rglob('*'):
        assert not path.is_symlink() and (path.is_file() or path.is_dir())
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    assert actual == set(expected) | {'index.json'}
    for name, item in expected.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        checked(dict(path=str(root / name), sha256=item['sha256'], bytes=item['bytes']))


def render():
    refs = json.loads((HERE / 'source-references.json').read_text())
    for row in refs['families'].values():
        family(row)
    for row in refs['direct'].values():
        checked(row)
    adapter = checked(refs['direct']['adapter'])
    lifecycle = checked(refs['direct']['lifecycle']).split('export function readRoutingOrigin', 1)[0]
    assert adapter.count('export function ') == 1 and lifecycle.count('export function ') == 1
    cases = (HERE / 'cases.mjs').read_text()
    assert cases.count('export const ') == 3 and cases.count('export async function ') == 1
    tail = (HERE / 'guest-tail.mjs.in').read_text()
    assert tail.count('@MODE@') == 1
    header = """// Generated Source-only loader probe; no fixtures or ordinary imports at INIT.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest, runNeutralServer} from 'starling:node-http';
import * as types from 'wasi:http/types@0.2.10';
"""
    body = (header + adapter.replace('export function ', 'function ') + '\n' +
            lifecycle.replace('export function ', 'function ') + '\n' +
            cases.replace('export const ', 'const ').replace('export async function ', 'async function ') + '\n')
    return {mode: body + tail.replace('@MODE@', mode) for mode in ('guard', 'interop')}


def exclusive(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    texts = render()
    for mode, source in texts.items():
        path = HERE / ('guest-' + mode + '.mjs')
        if args.write:
            exclusive(path, source.encode())
        else:
            assert path.read_text() == source
    result = dict(schemaVersion=1, state='LOADER_PROBE_SOURCE_ASSEMBLY_ONLY_V1',
                  sourceOnly=True, entryEvaluated=False, nodeOrGuestInvoked=False,
                  entries={mode: descriptor(HERE / ('guest-' + mode + '.mjs')) for mode in texts},
                  sourceInputs=[descriptor(HERE / name) for name in
                                ['source-references.json', 'cases.mjs', 'guest-tail.mjs.in', 'build-entry.py']])
    if args.write:
        exclusive(HERE / 'entry-derivation.json', (json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
