"""Materialize finite committed Next sources; never execute a donor or build tool.

Default/--check reads only. --output requires a fresh absolute canonical root.
No external workstation artifact is required by this program.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import importlib.util
import json
import os
import stat
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).absolute().parent
REL = 'tests/node-compat/frameworks/nextjs/next-native-portable-source-v5'
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


EDIT_PATHS = {
    'include/host_api.h', 'host-apis/wasi-0.2.0/handles.h',
    'host-apis/wasi-0.2.0/host_api.cpp', 'builtins/web/fetch/request-response.h',
    'builtins/web/fetch/fetch-api.cpp', 'builtins/web/fetch/request-response.cpp',
}


def apply_overlays(spec, manifest, rows, source_root, members, get):
    """Apply exactly the six indexed afterimages to exact parent payload bytes."""
    require(manifest['schemaVersion'] == 1 and manifest['state'] ==
            'UNCOMPILED_SOURCE_DRAFT_NO_BUILD_OR_RUNTIME', 'Original Source-cut manifest')
    require(manifest['inheritedInteropLoaderSha256'] == spec['inheritedInteropLoader']['sha256']
            and manifest['futureSelectedCountsUnchangedIntended'] is True, 'Inherited loader/counts')
    for key in ('actualBuild', 'actualComponent', 'actualGuest', 'futureMaterialization',
                'futureGenerators', 'futureNativeBuild', 'futureComponent',
                'futureReturnedImportFunctionCount', 'futureNormalRuntime'):
        require(manifest[key] is None, 'No actual cleanup result may be projected')
    declared = manifest['files']
    edits = spec['postOverlays']
    require(len(declared) == len(edits) == 6 and
            {r['relativePath'] for r in declared} == EDIT_PATHS and
            {r['path'] for r in edits} == EDIT_PATHS, 'Exactly six declared paths')
    records = {r['relativePath']: r for r in declared}
    selected = {(r['role'], r['path']): r for r in rows}
    require(len(selected) == len(rows) == 825, 'Unique parent selection')
    for edit in edits:
        path = edit['path']
        require(edit['role'] == 'native-policy-source' and type(edit['mode']) is int
                and edit['mode'] == 0o600, 'Exact native overlay role/mode')
        record = records[path]
        before_name, after_name = 'before/' + path, 'after/' + path
        require(record['before']['path'] == before_name and record['after']['path'] == after_name,
                'Exact relative before/after paths')
        row = selected[(edit['role'], path)]
        require(all(row[k] == edit['before'][k] == record['before'][k] ==
                    members[before_name][k] for k in ('sha256', 'bytes')),
                'Indexed exact before-image')
        require(get((source_root / before_name).as_posix(), record['before']) == row['data'],
                'Parent/before payload equality')
        donor = edit['donor']
        require(donor['repositoryPath'] == (source_root / after_name).as_posix() and
                all(donor[k] == record['after'][k] == members[after_name][k]
                    for k in ('sha256', 'bytes')), 'Indexed exact after-image')
        data = get(donor['repositoryPath'], donor)
        row.update(sha256=donor['sha256'], bytes=donor['bytes'], mode=edit['mode'],
                   repositoryDonor=donor['repositoryPath'],
                   origin='Sealed read-based Fetch resource cleanup Source; uncompiled', data=data)
    loader = selected[('native-policy-source', 'runtime/script_loader.cpp')]
    require(spec['inheritedInteropLoader']['path'] == 'runtime/script_loader.cpp' and
            all(loader[k] == spec['inheritedInteropLoader'][k] for k in ('sha256', 'bytes')),
            'Inherited rooted file-URL loader unchanged')


def selection(repo):
    """Authenticate sealed Mat4 and one closed, six-file cleanup Source family."""
    repo = canonical(repo)
    inputs = {}

    def get(name, expected=None):
        data, ref = read_file(repo / relative(name), expected)
        require(ref['path'] not in inputs or inputs[ref['path']] == ref, 'Conflicting Source input')
        inputs[ref['path']] = ref
        return data

    def family(ref):
        index = json.loads(get(ref['repositoryPath'], ref))
        root = relative(ref['repositoryPath']).parent
        members = {r['path']: r for r in index['files']}
        require(len(members) == len(index['files']) and 'index.json' not in members,
                'Unique indexed Source members')
        nodes = list((repo / root).rglob('*'))
        require(not any(p.is_symlink() for p in nodes) and all(p.is_file() or p.is_dir() for p in nodes),
                'Source aliases/specials refused')
        require({p.relative_to(repo / root).as_posix() for p in nodes if p.is_file()} ==
                {'index.json', *members}, 'Closed Source membership')
        dirs = {p.as_posix() for n in members for p in relative(n).parents if p != Path('.')}
        require({p.relative_to(repo / root).as_posix() for p in nodes if p.is_dir()} == dirs,
                'Closed Source directory membership')
        for name, member in members.items():
            get((root / relative(name)).as_posix(), member)
        return index, root, members

    spec = json.loads(get(REL + '/selection.json'))
    require(type(spec['schemaVersion']) is int and spec['schemaVersion'] == 1 and spec['state'] ==
            'NATIVE_FETCH_READ_RESOURCE_CLEANUP_PORTABLE_SOURCE_SELECTION_V5', 'Wrong Source recipe')
    require(spec['expectedCounts'] == COUNTS and spec['outputDirectories'] == ROLES
            and spec['nativeBuildOrCompilerOrGuestClaimed'] is False, 'Role/action policy')
    parent_index, parent_root, parent_members = family(spec['parentMaterializerIndex'])
    require(parent_index['state'] == 'HELD_NEXT_PORTABLE_NATIVE_SOURCE_MATERIALIZER_V4', 'Sealed Mat4 parent')
    for key, name in [('parentMaterializerModule', 'materialize.py'),
                      ('parentMaterializerSelection', 'selection.json')]:
        ref = spec[key]
        require(ref['repositoryPath'] == (parent_root / name).as_posix() and
                all(parent_members[name][k] == ref[k] for k in ('sha256', 'bytes')), 'Indexed parent role')
    module_path = repo / relative(spec['parentMaterializerModule']['repositoryPath'])
    module_spec = importlib.util.spec_from_file_location('sealed_mat4_parent_recipe', module_path)
    parent = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(parent)
    parent_spec, rows, parent_inputs = parent.selection(repo)
    require(parent_spec == json.loads(get(spec['parentMaterializerSelection']['repositoryPath'],
                                         spec['parentMaterializerSelection'])), 'Exact parent recipe')
    require(parent.fingerprint(rows) == spec['parentRoleContentSha256'], 'Parent content fingerprint')
    before = {(r['role'], r['path']): (r['sha256'], r['bytes'], r['mode'], r['data']) for r in rows}
    for path, ref in parent_inputs.items():
        require(path not in inputs or inputs[path] == ref, 'Parent provenance conflict')
        inputs[path] = ref
    index, source_root, members = family(spec['cleanupSourceIndex'])
    require(index['state'] == 'NATIVE_FETCH_READ_BASED_RESOURCE_CLEANUP_SOURCE_HELD_V1'
            and len(members) == 22 and index['sourceOnly'] is True
            and index['cppCompiledOrTypechecked'] is False and index['beforeAfterFiles'] == 6
            and index['oldImportFunctionCountProjected'] is False, 'Sealed uncompiled cleanup Source')
    require(all(index[k] is None for k in ('actualBuild', 'actualComponent', 'actualGuest')),
            'No cleanup execution claim')
    manifest_ref = spec['cleanupAfterimages']
    require(manifest_ref['repositoryPath'] == (source_root / 'afterimages.json').as_posix()
            and all(manifest_ref[k] == members['afterimages.json'][k] for k in ('sha256', 'bytes')),
            'Indexed cleanup manifest')
    apply_overlays(spec, json.loads(get(manifest_ref['repositoryPath'], manifest_ref)),
                   rows, source_root, members, get)
    unchanged = [r for r in rows if r['path'] not in EDIT_PATHS or r['role'] != 'native-policy-source']
    require(len(unchanged) == 819 and all(before[(r['role'], r['path'])] ==
            (r['sha256'], r['bytes'], r['mode'], r['data']) for r in unchanged), 'All 819 other payloads unchanged')
    require(collections.Counter(r['role'] for r in rows) == COUNTS and len(rows) == spec['expectedFiles'] == 825,
            'Whole selected role membership')
    require(sum(r['bytes'] for r in rows) == spec['expectedBytes'] == 7554682
            and fingerprint(rows) == spec['roleContentSha256'], 'Six-overlay content fingerprint')
    get(REL + '/materialize.py')
    return spec, rows, inputs

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
