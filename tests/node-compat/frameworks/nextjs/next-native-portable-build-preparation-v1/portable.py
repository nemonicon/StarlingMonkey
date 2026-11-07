"""Read-only portable source admission. No donor import or build/tool invocation."""
from pathlib import Path
import collections
import hashlib
import json
import os
import stat


def require(value, message):
    if not value:
        raise ValueError(message)


def relative(name):
    require(type(name) is str and name and '\\' not in name and '\0' not in name,
            'Invalid relative path')
    require(not name.startswith('/') and all(x not in ('', '.', '..') for x in name.split('/')),
            'Unsafe relative path')
    return Path(*name.split('/'))


def canonical(path):
    p = Path(path)
    require(p.is_absolute() and '..' not in p.parts, 'Canonical absolute path required')
    for q in (p, *p.parents):
        require(not q.is_symlink(), 'Symlink/alias refused: ' + str(q))
    require(p.resolve(strict=True) == p, 'Physical alias refused')
    return p


def file_row(path, expected=None):
    p = canonical(path)
    s = p.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'Unique regular file required')
    h = hashlib.sha256()
    n = 0
    with os.fdopen(os.open(p, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)), 'rb') as f:
        opened = os.fstat(f.fileno())
        require((opened.st_dev, opened.st_ino) == (s.st_dev, s.st_ino), 'Input replaced before open')
        while b := f.read(1024**2):
            h.update(b)
            n += len(b)
    t = p.lstat()
    fields = ('st_dev', 'st_ino', 'st_nlink', 'st_mode', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    require(all(getattr(s, k) == getattr(t, k) for k in fields), 'Input changed during read')
    row = dict(path=str(p), sha256=h.hexdigest(), bytes=n)
    if expected is not None:
        require(row == expected, 'Descriptor differs: ' + str(p))
    physical = dict(path=str(p), dev=s.st_dev, ino=s.st_ino, nlink=s.st_nlink,
                    mode=stat.S_IMODE(s.st_mode), bytes=n, mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns)
    return row, physical


def document(ref):
    file_row(ref['path'], ref)
    require(ref['bytes'] < 4 * 1024**2, 'Oversized JSON input')
    return json.loads(Path(ref['path']).read_bytes())


def fingerprint(rows):
    values = [{k: r[k] for k in ('role', 'path', 'sha256', 'bytes', 'mode')} for r in rows]
    values.sort(key=lambda r: (r['role'], r['path']))
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def authenticate_policy(policy, repo):
    repo = canonical(repo)
    refs = []
    for key in ['materializerIndex', 'materializerSelection']:
        r = policy[key]
        ref = dict(path=str(repo / relative(r['repositoryPath'])), sha256=r['sha256'], bytes=r['bytes'])
        file_row(ref['path'], ref)
        refs.append(ref)
    index = document(refs[0])
    base = Path(refs[0]['path']).parent
    expected = {'index.json', *[r['path'] for r in index['files']]}
    require({str(q.relative_to(base)) for q in base.rglob('*') if q.is_file()} == expected,
            'Materializer family membership differs')
    require(not any(q.is_symlink() for q in base.rglob('*')), 'Materializer family alias')
    for r in index['files']:
        ref = dict(path=str(base / relative(r['path'])), sha256=r['sha256'], bytes=r['bytes'])
        file_row(ref['path'], ref)
        refs.append(ref)
    selected = document(refs[1])
    require(selected['expectedCounts'] == policy['expectedCounts']
            and selected['outputDirectories'] == policy['roleDirectories']
            and selected['expectedFiles'] == policy['expectedFiles']
            and selected['expectedBytes'] == policy['expectedBytes']
            and selected['roleContentSha256'] == policy['roleContentSha256'], 'Pinned selection policy differs')
    return refs


def inspect_layout(summary_ref, policy, provenance_refs=()):
    """Authenticate a materializer result, including every role/path/mode/byte.

    policy is Source-pinned by the real admission caller. Tiny policies are used
    only by inert filesystem tests; runtime authority cannot replace plan.json.
    """
    summary = document(summary_ref)
    require(summary['schemaVersion'] == 1 and summary['state'] == 'NEXT_PORTABLE_SOURCE_MATERIALIZED_V1',
            'Not a successful source materialization')
    require(summary['sourceOnly'] is True and summary['compilerOrGuestExecuted'] is False
            and summary['generatedBuildMetadataProjected'] is False, 'Unexpected compiled/runtime claim')
    root = canonical(summary['outputRoot'])
    require(Path(summary_ref['path']) == root / 'source-materialization.json', 'Summary root mismatch')
    require(summary['roleCounts'] == policy['expectedCounts'] and summary['files'] == policy['expectedFiles']
            and summary['bytes'] == policy['expectedBytes'], 'Role counts differ')
    composition_ref = summary['composition']
    require(composition_ref['path'] == str(root / 'composition.json'), 'Composition root mismatch')
    composition = document(composition_ref)
    require(composition['schemaVersion'] == 1 and composition['state'] == 'NEXT_PORTABLE_SOURCE_COMPOSITION_ONLY_V1',
            'Not a fresh Source-only composition')
    require(composition['engineBuilt'] is composition['guestExecuted'] is composition['legacyMetadataProjected'] is False,
            'Unexpected composition build claim')
    require(composition['selectedManifestsMustBeDerivedFresh'] is True
            and composition['sourceRoot'] == str(root / 'source'), 'Composition Source policy mismatch')
    rows = []
    protected = [summary_ref, composition_ref, *provenance_refs]
    physical = []
    names = set()
    for copied in summary['filesCopied']:
        role = copied['role']
        require(role in policy['roleDirectories'], 'Unknown role')
        name = relative(copied['relativePath']).as_posix()
        key = (role, name)
        require(key not in names, 'Duplicate role/path')
        names.add(key)
        ref = copied['source']
        require(ref['path'] == str(root / policy['roleDirectories'][role] / name), 'Cross-root payload path')
        r, identity = file_row(ref['path'], ref)
        require(identity['mode'] == copied['mode'], 'Copied file mode differs')
        require(type(copied['mode']) is int and copied['mode'] in (0o600, 0o644, 0o755), 'Invalid source mode')
        rows.append(dict(role=role, path=name, sha256=r['sha256'], bytes=r['bytes'], mode=copied['mode']))
        protected.append(ref)
        physical.append(identity)
    require(collections.Counter(r['role'] for r in rows) == policy['expectedCounts']
            and len(rows) == policy['expectedFiles'] and sum(r['bytes'] for r in rows) == policy['expectedBytes'],
            'Whole role membership differs')
    require(fingerprint(rows) == summary['roleContentSha256'] == policy['roleContentSha256'],
            'Whole content/mode fingerprint differs')
    native = [r for r in rows if r['role'] == 'native-policy-source']
    require(composition['nativeSourceFiles'] == len(native) == len(composition['files']), 'Native count differs')
    require(sorted((r['path'], r['sha256'], r['bytes']) for r in composition['files']) ==
            sorted((r['path'], r['sha256'], r['bytes']) for r in native), 'Composition/native membership differs')
    payload_names = {policy['roleDirectories'][r['role']] + '/' + r['path'] for r in rows}
    expected_files = payload_names | {'composition.json', 'source-materialization.json'}
    all_nodes = list(root.rglob('*'))
    require(not any(p.is_symlink() for p in all_nodes), 'Payload alias')
    require(all(p.is_dir() or p.is_file() for p in all_nodes), 'Special payload node')
    require({p.relative_to(root).as_posix() for p in all_nodes if p.is_file()} == expected_files,
            'Unexpected materialized file membership')
    expected_dirs = {p.as_posix() for n in payload_names for p in Path(n).parents if p != Path('.')}
    require({p.relative_to(root).as_posix() for p in all_nodes if p.is_dir()} == expected_dirs,
            'Unexpected materialized directory membership')
    directories = []
    for path in sorted([root, *[p for p in all_nodes if p.is_dir()]]):
        s = path.lstat()
        directories.append(dict(path=str(path), mode=stat.S_IMODE(s.st_mode),
                                dev=s.st_dev, ino=s.st_ino, nlink=s.st_nlink,
                                mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns))
    require(summary['inputs'] == composition['inputs'], 'Donor provenance differs')
    protected.extend(summary['inputs'])
    seen = {}
    for ref in protected:
        require(ref['path'] not in seen or seen[ref['path']] == ref, 'Conflicting input provenance')
        seen[ref['path']] = ref
        file_row(ref['path'], ref)
    # Preserve donor provenance unchanged; this is a new current physical read,
    # not a claim to have observed the materializer's earlier creation sequence.
    return dict(schemaVersion=1, state='AUTHENTICATED_PORTABLE_BUILD_SOURCE_SELECTION_V1',
                sourceOnly=True, sourceMaterialization=summary_ref, composition=composition_ref,
                sourceRoot=str(root / 'source'), roleCounts=policy['expectedCounts'],
                roleContentSha256=fingerprint(rows), files=rows, physicalRecords=physical,
                directoryRecords=directories,
                protectedInputs=list(seen.values()), engineBuilt=False, guestExecuted=False,
                historicalMetadataProjected=False, priorCopySequenceObservedByPreparer=False)


def role_copies(selection, role):
    roots = {'native-policy-source': selection['sourceRoot'],
             'build-support': str(Path(selection['sourceRoot']).parent / 'build-support'),
             'componentize-embedding': str(Path(selection['sourceRoot']).parent / 'componentize-source')}
    return [dict(relativePath=r['path'], mode=r['mode'],
                 source=dict(path=roots[role] + '/' + r['path'], sha256=r['sha256'], bytes=r['bytes']))
            for r in selection['files'] if r['role'] == role]


def admit(selection_ref, policy, repo):
    refs = authenticate_policy(policy, repo)
    recorded = document(selection_ref)
    actual = inspect_layout(recorded['sourceMaterialization'], policy, refs)
    require(actual == recorded, 'Prepared selection/physical records changed')
    actual['protectedInputs'] = [selection_ref, *actual['protectedInputs']]
    return actual


def generator_argv(policy, source, node):
    result = []
    for command in policy['generatorCommands']:
        result.append([node['path'], str(Path(source) / relative(command[0])),
                       *[source if x == '$SOURCE' else x for x in command[1:]]])
    return result


def validate_generators(generated, selection, node, policy):
    require(all(node[k] == policy['node'][k] for k in ['sha256', 'bytes']), 'Wrong generator Node')
    require(generated['schemaVersion'] == 1 and generated['state'] == 'ACTUAL_PORTABLE_NEXT_INSTALLED_GENERATORS_CHECKED_V1',
            'Fresh generator receipt required')
    require(generated['passed'] is generated['sourceBeforeAfterUnchanged'] is True
            and generated['nativeOrGuestExecuted'] is False, 'Failed generator receipt')
    require(generated['composition'] == selection['composition'] and generated['node'] == node,
            'Generator composition/Node mismatch')
    require(generated['sourceRoot'] == selection['sourceRoot']
            and generated['materializationSummary'] == selection['sourceMaterialization']
            and generated['roleContentSha256'] == selection['roleContentSha256']
            and generated['portableInputsPreserved'] is True, 'Generator portable input mismatch')
    require(generated['wholePortableBefore'] == generated['wholePortableAfter'] == selection['physicalRecords'],
            'Generator whole portable physical bookends differ')
    require(generated['portableDirectoriesBefore'] == generated['portableDirectoriesAfter'] == selection['directoryRecords'],
            'Generator portable directory bookends differ')
    native = [r['source'] for r in role_copies(selection, 'native-policy-source')]
    require(generated['sourceBefore'] == generated['sourceAfter'] == native,
            'Generator full native bookends differ')
    require(generated['sourceFiles'] == len(native), 'Generator source count differs')
    commands = generated['commands']
    require([r['argv'] for r in commands] == generator_argv(policy, selection['sourceRoot'], node),
            'Generator commands target another root or protocol')
    require(all(type(r['rawExitCode']) is int and r['rawExitCode'] == 0
                and r['stderrSha256'] == hashlib.sha256(b'').hexdigest() for r in commands),
            'Generator failed or stderr not empty')
    refs = [generated[k] for k in ['rootAuthority', 'sourceIndex', 'plan']]
    generator_plan = document(generated['plan'])
    require(generator_plan['perCommandSeconds'] == 30 and generator_plan['outerSeconds'] == 900,
            'Generator plan command/outer cap differs')
    for command in commands:
        require(command['cwd'] == selection['sourceRoot'] and command['ownedGroupsClean'] is True,
                'Generator cwd/cleanup mismatch')
        started = document(command['started'])
        terminal = document(command['terminal'])
        require(started['argv'] == command['argv'] and started['timeoutSeconds'] == 30
                and started['pid'] == terminal['pid']
                and started['authority'] == terminal['authority'] == generated['rootAuthority'],
                'Generator original started/terminal mismatch')
        require(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
                and terminal['timeout'] is terminal['forcedCleanup'] is False
                and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
                and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
                and all(g['alive'] is False for g in terminal['finalGroups']), 'Generator original terminal not clean')
        require(terminal['stdout'] == command['stdout'] and terminal['stderr'] == command['stderr'],
                'Generator raw streams differ')
        require(command['stdout']['sha256'] == command['stdoutSha256']
                and command['stderr']['sha256'] == command['stderrSha256']
                and command['stderr']['bytes'] == 0, 'Generator stream hashes differ')
        refs.extend(command[k] for k in ['started', 'terminal', 'stdout', 'stderr'])
    require(generated['primaryError'] is generated['finalProtectionError'] is generated['outerOwnerError'] is None,
            'Generator producer/owner error')
    require(generated['outerOwnedGroupsClean'] is generated['outerInputsPreserved'] is generated['outputCapSatisfied'] is True,
            'Generator outer protection/cap failed')
    require(generated['byteCapsArePostCaptureAdmissionNotContinuousLimits'] is True,
            'Generator byte cap scope differs')
    body = document(generated['bodyResult'])
    require(all(k in body for k in ['schemaVersion', 'state', 'passed', 'commands', 'composition',
                                  'sourceBefore', 'sourceAfter', 'wholePortableBefore', 'wholePortableAfter']),
            'Missing generator body fields')
    require(all(generated[k] == v for k, v in body.items()), 'Generator body/final result mismatch')
    outer_started = document(generated['outerStarted'])
    outer_terminal = document(generated['outerTerminal'])
    expected_worker = [generator_plan['python']['path'], '-I', '-B',
                       str(Path(generated['sourceIndex']['path']).parent / 'run.py'),
                       '--worker-authority', generated['rootAuthority']['path']]
    require(outer_started['argv'] == expected_worker and outer_started['timeoutSeconds'] == 900
            and outer_started['pid'] == outer_terminal['pid']
            and outer_started['authority'] == outer_terminal['authority'] == generated['rootAuthority'],
            'Generator original outer started/terminal mismatch')
    require(type(outer_terminal['rawExitCode']) is int and outer_terminal['rawExitCode'] == 0
            and outer_terminal['timeout'] is outer_terminal['forcedCleanup'] is False
            and outer_terminal['parentOwnedGroupGone'] is outer_terminal['allObservedOwnedGroupsGone'] is True
            and all(outer_terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
            and all(g['alive'] is False for g in outer_terminal['finalGroups']), 'Generator outer not clean')
    require(outer_terminal['stdout'] == generated['outerStdout']
            and outer_terminal['stderr'] == generated['outerStderr'], 'Generator outer streams differ')
    refs.extend(generated[k] for k in ['bodyResult', 'outerStarted', 'outerTerminal', 'outerStdout', 'outerStderr'])
    refs.append(generator_plan['python'])
    for ref in refs:
        file_row(ref['path'], ref)
    return refs
