"""Materialize finite committed Next sources; never execute a donor or build tool.

Default/--check reads only. --output requires a fresh absolute canonical root.
No external workstation artifact is required by this program.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import json
import os
import stat

HERE = Path(__file__).absolute().parent
REL = 'tests/node-compat/frameworks/nextjs/next-native-portable-source-v1'
ROLES = {'native-policy-source': 'source', 'build-support': 'build-support',
         'componentize-embedding': 'componentize-source'}
COUNTS = {'native-policy-source': 435, 'build-support': 387,
          'componentize-embedding': 3}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative(value):
    require(type(value) is str and value and '\\' not in value and '\0' not in value,
            'Invalid relative POSIX path')
    parts = value.split('/')
    require(not any(p in ('', '.', '..') for p in parts), 'Unsafe path component')
    p = PurePosixPath(value)
    require(not p.is_absolute() and p.as_posix() == value, 'Noncanonical path')
    return Path(*parts)


def canonical(path, exists=True):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts,
            'Absolute canonical path required')
    for p in (path, *path.parents):
        require(not p.is_symlink(), 'Symlink refused: ' + str(p))
    require(path.resolve(strict=exists) == path, 'Path alias refused: ' + str(path))
    return path


def descriptor(path, data):
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def read_file(path, expected=None):
    path = canonical(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
            'Unique regular input required: ' + str(path))
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        data = stream.read()
    after = path.lstat()
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_mode', 'st_nlink')
    require(all(getattr(before, k) == getattr(after, k) for k in fields),
            'Input changed while reading: ' + str(path))
    row = descriptor(path, data)
    if expected:
        require(row['sha256'] == expected['sha256'] and row['bytes'] == expected['bytes'],
                'Input bytes/hash differ: ' + str(path))
    return data, row


def fingerprint(rows):
    values = [{k: r[k] for k in ('role', 'path', 'sha256', 'bytes', 'mode')} for r in rows]
    values.sort(key=lambda r: (r['role'], r['path']))
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def selection(repo):
    """Authenticate the genuine finite donor map and exact overlay guards."""
    repo = canonical(repo)
    inputs = {}

    def get(name, expected=None):
        path = repo / relative(name)
        data, row = read_file(path, expected)
        if str(path) in inputs:
            require(inputs[str(path)] == row, 'Conflicting input descriptor')
        inputs[str(path)] = row
        return data

    spec = json.loads(get(REL + '/selection.json'))
    require(spec['schemaVersion'] == 1 and spec['state'] == 'WORKING_NEXT_V7_PLUS_UTF16_PORTABLE_SOURCE_SELECTION_V1', 'Wrong Source selection')
    require(spec['expectedCounts'] == COUNTS and spec['outputDirectories'] == ROLES,
            'Role policy differs')
    require(spec['nativeBuildOrCompilerOrGuestClaimed'] is False, 'Unexpected build claim')
    base = json.loads(get(spec['baselineMap']['repositoryPath'], spec['baselineMap']))
    graft = json.loads(get(spec['v7Mapping']['repositoryPath'], spec['v7Mapping']))
    require(base['state'] == 'EXACT_CURRENT_C2_BASELINE_PORTABLE_SOURCE_MAP_NO_INTL_OR_ERROR_OVERLAY'
            and len(base['files']) == 824, 'Wrong C2 baseline map')
    rows = {}
    for r in base['files']:
        role = r['role']
        require(role in ROLES, 'Unknown role')
        prefix = 'componentize-source/' if role == 'componentize-embedding' else 'native-source/'
        require(r['destination'].startswith(prefix), 'Wrong destination role')
        name = relative(r['destination'][len(prefix):]).as_posix()
        key = (role, name)
        require(key not in rows, 'Duplicate selected input')
        donor = r['repositoryDonor']
        require((donor['sha256'], donor['bytes']) == (r['sha256'], r['bytes']), 'Baseline donor mismatch')
        rows[key] = dict(role=role, path=name, sha256=r['sha256'], bytes=r['bytes'],
                         mode=int(r['copyMode'], 8), repositoryDonor=donor['path'],
                         gitBlobSha1=donor['gitBlobSha1'], origin='committed C2 donor')
    require(len(spec['overlays']) == 6 and len(spec['additions']) == 1
            and len(graft['replacements']) == 5, 'Wrong overlay boundary')
    joined = set()
    for i, edit in enumerate(spec['overlays']):
        key = (edit['role'], relative(edit['path']).as_posix())
        require(key in rows and key not in joined and edit['role'] == 'native-policy-source', 'Invalid replacement')
        joined.add(key)
        old = rows[key]
        require({k: old[k] for k in ('sha256', 'bytes')} == edit['before'], 'Replacement before guard')
        if i < 5:
            g = graft['replacements'][i]
            require(g['target'] == edit['path'] and g['newPath'] is False
                    and {k: g['before'][k] for k in ('sha256', 'bytes')} == edit['before']
                    and all(g['after'][k] == edit['donor'][k] for k in ('sha256', 'bytes')),
                    'V7 mapping join differs')
        else:
            require(edit['path'] == 'builtins/node-compat/module-kernel.cpp', 'Wrong UTF16 target')
        old.update(sha256=edit['donor']['sha256'], bytes=edit['donor']['bytes'], mode=edit['mode'],
                   repositoryDonor=edit['donor']['repositoryPath'], origin=edit['reason'])
        old.pop('gitBlobSha1', None)
    for edit in spec['additions']:
        name = relative(edit['path']).as_posix()
        key = (edit['role'], name)
        require(key not in rows and key == ('build-support', 'runtime/crates/staticlib-template/Cargo.intl.toml.in'), 'Invalid support addition')
        g = graft['extraBuildSupport']
        require(len(g) == 1 and g[0]['relativePath'] == name and g[0]['mode'] == edit['mode']
                and all(g[0]['source'][k] == edit['donor'][k] for k in ('sha256', 'bytes')), 'Extra support join')
        rows[key] = dict(role=edit['role'], path=name, sha256=edit['donor']['sha256'], bytes=edit['donor']['bytes'],
                         mode=edit['mode'], repositoryDonor=edit['donor']['repositoryPath'], origin='V7 extra Intl Cargo support')
    values = sorted(rows.values(), key=lambda r: (r['role'], r['path']))
    require(collections.Counter(r['role'] for r in values) == COUNTS and len(values) == spec['expectedFiles'] == 825,
            'Wrong whole selected role membership')
    require(not {r['path'] for r in values if r['role'] == 'native-policy-source'} &
            {r['path'] for r in values if r['role'] == 'build-support'}, 'Native/support overlap')
    require(sum(r['bytes'] for r in values) == spec['expectedBytes'] == 7530166
            and fingerprint(values) == spec['roleContentSha256'], 'Whole content fingerprint differs')
    for r in values:
        require(r['mode'] in (0o600, 0o644, 0o755), 'Unexpected copy mode')
        data = get(r['repositoryDonor'], r)
        if 'gitBlobSha1' in r:
            require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == r['gitBlobSha1'], 'Git blob differs')
        r['data'] = data
    get(REL + '/materialize.py')
    return spec, values, inputs


def recheck(inputs):
    for r in inputs.values():
        read_file(r['path'], r)


def write_new(path, data, mode=0o600):
    canonical(path.parent)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fchmod(stream.fileno(), mode)
        os.fsync(stream.fileno())


def json_bytes(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def verify_output(output, rows):
    output = canonical(output)
    expected = {ROLES[r['role']] + '/' + r['path']: r for r in rows}
    nodes = list(output.rglob('*'))
    require(not any(p.is_symlink() for p in nodes), 'Output symlink')
    require(all(p.is_file() or p.is_dir() for p in nodes), 'Unexpected output node')
    payloads = {p.relative_to(output).as_posix() for p in nodes if p.is_file()
                and p.relative_to(output).parts[0] in ROLES.values()}
    require(payloads == set(expected), 'Output payload membership differs')
    other = {p.relative_to(output).as_posix() for p in nodes if p.is_file()} - payloads
    require(other <= {'composition.json', 'source-materialization.json'}, 'Unexpected root file')
    dirs = {q.as_posix() for n in expected for q in Path(n).parents if q != Path('.')}
    require({p.relative_to(output).as_posix() for p in nodes if p.is_dir()} == dirs, 'Output directory membership differs')
    for name, r in expected.items():
        path = output / name
        read_file(path, r)
        require(stat.S_IMODE(path.stat().st_mode) == r['mode'], 'Output mode differs')
        require(path.stat().st_ino != Path(r['donorPath']).stat().st_ino
                or path.stat().st_dev != Path(r['donorPath']).stat().st_dev, 'Output aliases donor')


def run(repo, output=None):
    repo = canonical(repo)
    spec, rows, inputs = selection(repo)
    for r in rows:
        r['donorPath'] = str(repo / relative(r['repositoryDonor']))
    summary = dict(schemaVersion=1, state='NEXT_PORTABLE_SOURCE_DONORS_CHECKED_V1', sourceOnly=True,
                   roleCounts=COUNTS, files=len(rows), bytes=sum(r['bytes'] for r in rows),
                   roleContentSha256=fingerprint(rows), compilerOrGuestExecuted=False,
                   generatedBuildMetadataProjected=False, outputRoot=None)
    if output is None:
        recheck(inputs)
        return summary
    output = canonical(output, exists=False)
    require(not output.exists() and output.parent.is_dir(), 'Output must be fresh under existing parent')
    require(output != repo and repo not in output.parents, 'Output must be outside repository')
    output.mkdir(mode=0o700)
    written = []
    try:
        for r in rows:
            path = output / ROLES[r['role']] / relative(r['path'])
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            write_new(path, r['data'], r['mode'])
            written.append(str(path.relative_to(output)))
        verify_output(output, rows)
        recheck(inputs)
        native = [dict(path=r['path'], sha256=r['sha256'], bytes=r['bytes'],
                       origin='repository donor: ' + r['repositoryDonor']) for r in rows if r['role'] == 'native-policy-source']
        composition = dict(schemaVersion=1, state='NEXT_PORTABLE_SOURCE_COMPOSITION_ONLY_V1',
                           sourceRoot=str(output / 'source'), nativeSourceFiles=435, files=native,
                           inputs=list(inputs.values()), engineBuilt=False, guestExecuted=False,
                           legacyMetadataProjected=False, selectedManifestsMustBeDerivedFresh=True)
        composition_path = output / 'composition.json'
        cb = json_bytes(composition)
        write_new(composition_path, cb)
        summary.update(state='NEXT_PORTABLE_SOURCE_MATERIALIZED_V1', outputRoot=str(output),
                       composition=descriptor(composition_path, cb),
                       inputs=list(inputs.values()),
                       filesCopied=[dict(role=r['role'], relativePath=r['path'], mode=r['mode'],
                                         source=descriptor(output / ROLES[r['role']] / r['path'], r['data']),
                                         repositoryDonor=r['repositoryDonor']) for r in rows])
        verify_output(output, rows)
        require({p.name for p in output.iterdir()} == set(ROLES.values()) | {'composition.json'}, 'Unexpected root member')
    except BaseException as error:
        summary.update(state='NEXT_PORTABLE_SOURCE_PARTIAL_FAILURE_PRESERVED_V1', outputRoot=str(output),
                       written=written, error=dict(type=type(error).__name__, message=str(error)))
        raise
    finally:
        write_new(output / 'source-materialization.json', json_bytes(summary))
    verify_output(output, rows)
    recheck(inputs)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true')
    group.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run(HERE.parents[4], args.output)
    print(json.dumps({k: v for k, v in result.items() if k not in ('inputs', 'filesCopied')}, indent=2))


if __name__ == '__main__':
    main()
