"""Dormant two-CPP SDK frontend driver. No action occurs on import.

Execution requires a separately issued Root descriptor and a real b8a4 Source
peer. Preparation does not authorize compiler, helper, engine or crypto calls.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shlex
import stat
import sys

sys.dont_write_bytecode = True
OWN = Path(__file__).resolve().parent
SOURCE = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
WORK = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build')
OUTPUT = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-init-barrier-sdk-syntax-v1')
SOURCE_SHA = 'b8a4f219df0b5172361045632d1a1a96f068609496ac8ea128e38eb2aedd6b6c'
UNIT_IDS = ['entropy-policy', 'hash-hmac-kernel']


def descriptor(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)


def regular(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    for part in (path, *path.parents):
        assert not part.is_symlink(), part
    assert stat.S_ISREG(path.lstat().st_mode), path
    return path


def identity(path):
    s = Path(path).stat()
    return dict(mode=stat.S_IMODE(s.st_mode), device=s.st_dev, inode=s.st_ino,
                links=s.st_nlink, bytes=s.st_size, mtimeNs=s.st_mtime_ns,
                ctimeNs=s.st_ctime_ns)


class Protection:
    def __init__(self):
        self.files = {}
        self.trees = {}
        self.aliases = {}

    def checked(self, row):
        path = regular(row['path'])
        before = identity(path)
        assert descriptor(path) == {k: row[k] for k in ('path', 'sha256', 'bytes')}, path
        assert identity(path) == before, path
        observed = dict(row={k: row[k] for k in ('path', 'sha256', 'bytes')}, identity=before)
        assert self.files.get(str(path), observed) == observed, path
        self.files[str(path)] = observed
        return path

    def read(self, row):
        assert row['bytes'] <= 32 * 1024**2
        return json.loads(self.checked(row).read_bytes())

    def family(self, row):
        index = self.read(row)
        root = Path(row['path']).parent
        names = [r['path'] for r in index['files']]
        assert len(names) == len(set(names))
        for name in names:
            p = Path(name)
            assert not p.is_absolute() and '..' not in p.parts and name != 'index.json'
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        assert not any(p.is_symlink() for p in root.rglob('*'))
        assert actual == set(names) | {'index.json'}
        for item in index['files']:
            self.checked(dict(item, path=str(root / item['path'])))
        # Compare the same canonical relative string SET on both bookends.
        self.trees[str(root)] = tree_snapshot(root)
        return index

    def tree(self, root, rows, aliases):
        root = Path(root)
        expected = {str(Path(r['path']).relative_to(root)) for r in rows}
        current = tree_snapshot(root)
        assert set(current['files']) == expected, root
        assert set(current['aliases']) == {str(Path(a['path']).relative_to(root)) for a in aliases}
        for row in rows:
            self.checked(row)
        for row in aliases:
            observed = alias_snapshot(row)
            self.aliases[row['path']] = dict(expected=row, observed=observed)
        self.trees[str(root)] = current

    def recheck(self):
        errors = []
        for path, before in self.files.items():
            try:
                self.checked(before['row'])
            except Exception as error:
                errors.append(dict(path=path, error=repr(error)))
        for root, before in self.trees.items():
            try:
                assert tree_snapshot(Path(root)) == before, root
            except Exception as error:
                errors.append(dict(path=root, error=repr(error)))
        for path, before in self.aliases.items():
            try:
                assert alias_snapshot(before['expected']) == before['observed'], path
            except Exception as error:
                errors.append(dict(path=path, error=repr(error)))
        return dict(schemaVersion=1, files=len(self.files), trees=len(self.trees),
                    aliases=len(self.aliases), unchanged=not errors, errors=errors,
                    membershipComparison='sets of relative POSIX strings',
                    fileChecks='SHA256/bytes/mode/device/inode/nlink/mtime/ctime')


def tree_snapshot(root):
    assert root.is_dir() and not root.is_symlink()
    files, aliases, directories = set(), set(), {}
    for path in (root, *root.rglob('*')):
        relative = path.relative_to(root)
        if '.git' in relative.parts:
            continue
        name = relative.as_posix()
        if path.is_symlink():
            aliases.add(name)
        elif path.is_file():
            files.add(name)
        else:
            assert path.is_dir(), path
            s = path.stat()
            directories[name] = dict(mode=stat.S_IMODE(s.st_mode), device=s.st_dev, inode=s.st_ino)
    return dict(files=sorted(files), aliases=sorted(aliases), directories=directories)


def alias_snapshot(row):
    p = Path(row['path'])
    assert p.is_symlink() and os.readlink(p) == row['linkText']
    assert str(p.resolve(strict=True)) == row['resolved']
    s = p.lstat()
    return dict(linkText=os.readlink(p), resolved=row['resolved'],
                mode=stat.S_IMODE(s.st_mode), device=s.st_dev, inode=s.st_ino, links=s.st_nlink)


def clean_arguments(command):
    words = shlex.split(command)
    driver, rest = words[0], words[1:]
    arguments, removed, main = [], [], None
    pair = {'-o', '-MF', '-MT', '-MQ', '-MJ', '--serialize-diagnostics'}
    singleton = {'-MD', '-MMD', '-MP', '-MG', '-M', '-MM', '-fsyntax-only'}
    i = 0
    while i < len(rest):
        token = rest[i]
        if token in pair or token == '-c':
            assert i + 1 < len(rest)
            if token == '-c':
                assert main is None
                main = rest[i + 1]
            removed.append(rest[i:i + 2])
            i += 2
        elif token in singleton:
            removed.append([token])
            i += 1
        else:
            assert not token.startswith(('@', '-Wp,', '-fplugin', '-Xclang'))
            assert not any(token.startswith(p) and token != p for p in pair)
            arguments.append(token)
            i += 1
    assert main and '--target=wasm32-wasi' in arguments
    assert all(x in arguments for x in ('-O3', '-DNDEBUG', '-fno-exceptions', '-DNODE_COMPAT_CRYPTO_HASH_HMAC=1'))
    assert not any(x.startswith(('-DDEBUG', '-DNODE_COMPAT_OOM', '-DNODE_COMPAT_GC_STRESS', '-DNODE_CRYPTO_AUDITED_BORROW')) for x in arguments)
    return driver, arguments, main, removed


def parse_dependencies(text, target):
    logical = text.replace('\\\n', '').replace('\\\r\n', '')
    lhs, separator, rhs = logical.partition(':')
    assert separator and lhs.strip() == target
    names = shlex.split(rhs, comments=False, posix=True)
    assert names and len(names) == len(set(names)), 'Missing or duplicate dependency names'
    assert all('\x00' not in name for name in names)
    return names


def clean_terminal(t):
    return (t['allObservedOwnedGroupsGone'] is True and t['parentOwnedGroupGone'] is True
            and not t['forcedCleanup'] and not t['timeout'] and not t['signals']
            and not t['errors'] and not t['remainingObservedPids'])


def write(path, value):
    path = Path(path)
    assert path.is_relative_to(OUTPUT) and not path.is_symlink()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + '\n').encode() if not isinstance(value, bytes) else value
    with path.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        assert stream.write(raw) == len(raw)
        stream.flush()
        os.fsync(stream.fileno())


def check_authority(a, plan, own_index):
    assert a['schemaVersion'] == 1 and a['state'] == 'ROOT_HASH_HMAC_INIT_BARRIER_TWO_CPP_SYNTAX_AUTHORITY_V1'
    assert a['driverPreparationIndex'] == own_index and a['sourceIndex'] == plan['references']['sourceIndex']
    assert a['outputRoot'] == str(OUTPUT) and a['timeoutSecondsPerUnit'] == 60 and a['units'] == UNIT_IDS
    assert a['syntaxOnlyCompilerAllowed'] is True
    for name in ('objectOrLinkAllowed', 'nativeBuildAllowed', 'helperAllowed', 'engineAllowed',
                 'cryptoAllowed', 'guestAllowed', 'snapshotAllowed', 'adoptionAllowed'):
        assert a[name] is False, name
    assert isinstance(a['sourceReview'], dict)


def authenticate(authority_row):
    assert not sys.flags.optimize, 'Authentication assertions require ordinary Python execution'
    guard = Protection()
    authority = guard.read(authority_row)
    own_index = authority['driverPreparationIndex']
    assert own_index['path'] == str(OWN / 'index.json')
    guard.family(own_index)
    plan = guard.read(descriptor(OWN / 'plan.json'))
    assert plan['state'] == 'PREPARED_UNEXECUTED_TWO_CPP_SDK_SYNTAX_PLAN_V1'
    check_authority(authority, plan, own_index)
    refs = plan['references']
    for key in ('sourceIndex', 'monitorIndex'):
        guard.family(refs[key])
    assert refs['sourceIndex']['sha256'] == SOURCE_SHA
    source_contract = guard.read(descriptor(Path(refs['sourceIndex']['path']).parent / 'future-source-review-contract.json'))
    pair = authority['sourceReview']
    review_index = guard.family(pair['index'])
    assert pair['results']['path'] == str(Path(pair['index']['path']).parent / 'results.json')
    member = next(r for r in review_index['files'] if r['path'] == 'results.json')
    assert {k: pair['results'][k] for k in ('sha256', 'bytes')} == {k: member[k] for k in ('sha256', 'bytes')}
    peer = guard.read(pair['results'])
    assert peer['state'] == source_contract['requiredReviewState'] and peer['sourceIndexSha256'] == SOURCE_SHA
    for key, value in source_contract['requiredFixedValues'].items():
        assert peer[key] == value, key
    for key in ('metadata', 'engine', 'compileDatabase', 'inputLedger', 'aliasInventory',
                'compilerLeaf', 'compilerWrapper', 'python', 'processObserver', 'donorDriver', 'donorDependencySample'):
        guard.checked(refs[key])
    assert Path(sys.executable).resolve() == Path(refs['python']['path']).resolve()
    metadata = guard.read(refs['metadata'])
    assert len(metadata) == 83 and len(metadata['sourceManifest']) == 357 and len(metadata['componentizeSourceManifest']) == 3
    assert metadata['engineSha256'] == refs['engine']['sha256'] and metadata['compileCommandsSha256'] == refs['compileDatabase']['sha256']
    assert metadata['entropyPolicy'] == 'off' and metadata['nodeCryptoHashHmacEnabled'] is True and metadata['nodeCryptoAuditedBorrowEnabled'] is False
    db = guard.read(refs['compileDatabase'])
    for unit in plan['units']:
        matches = [row for row in db if row['file'] == unit['actualCompileRow']['file']]
        assert matches == [unit['actualCompileRow']]
        declared, args, main, removed = clean_arguments(matches[0]['command'])
        assert declared == refs['compilerWrapper']['path'] and main == matches[0]['file']
        assert args == unit['preservedArguments'] and removed == unit['removedOutputArguments']
        assert unit['argv'] == [plan['compilerAlias'], *args, '-ivfsoverlay', str(OUTPUT / 'overlay.json'),
                                '-fsyntax-only', '-MD', '-MF', unit['dependencyFile'], '-MT', unit['dependencyTarget'], unit['privateMainPath']]
        assert unit['cwd'] == matches[0]['directory']
        assert unit['argv'].count('-fsyntax-only') == 1 and '-o' not in unit['argv'] and '-c' not in unit['argv']
    assert refs['compilerLeaf']['path'] == str(Path(plan['compilerAlias']).resolve())
    wrapper = Path(refs['compilerWrapper']['path']).read_text()
    assert plan['compilerAlias'] in wrapper and '"$@"' in wrapper
    ledger = guard.read(refs['inputLedger'])['files']
    indexed = {r['path']: r for r in ledger}
    assert len(indexed) == len(ledger)
    aliases = guard.read(refs['aliasInventory'])['symlinks']
    for tree in plan['protectedTrees']:
        root = Path(tree['path'])
        rows = [r for r in ledger if Path(r['path']).is_relative_to(root)
                and '.git' not in Path(r['path']).relative_to(root).parts]
        links = [r for r in aliases if Path(r['path']).is_relative_to(root)]
        assert len(rows) == tree['regularFiles'] and len(links) == tree['symlinks']
        guard.tree(root, rows, links)
    for r in metadata['sourceManifest']:
        key = str(SOURCE / r['path'])
        assert indexed[key]['sha256'] == r['sha256'] and key in guard.files
    embedding_words = shlex.split(metadata['actualEmbeddingCompileCommands'][0])
    assert embedding_words.count('-c') == 1
    embedding_root = Path(embedding_words[embedding_words.index('-c') + 1]).parents[1]
    expected_external = {str(embedding_root / r['path']): r['sha256'] for r in metadata['componentizeSourceManifest']}
    assert {r['path']: r['sha256'] for r in plan['externalEmbeddingInputs']} == expected_external
    for row in plan['externalEmbeddingInputs']:
        guard.checked(row)
    for change in plan['candidateFiles']:
        guard.checked(change['before'])
        guard.checked(change['after'])
    return guard, plan, authority


def execute(authority_row):
    assert not OUTPUT.exists(), 'First attempt is immutable; no implicit retry'
    guard, plan, authority = authenticate(authority_row)
    os.umask(0o077)
    OUTPUT.mkdir(mode=0o700)
    (OUTPUT / 'tmp').mkdir(mode=0o700)
    outcomes, primary = [], None
    try:
        for item in plan['candidateFiles']:
            destination = Path(item['privatePath'])
            write(destination, Path(item['after']['path']).read_bytes())
            before, after = Path(item['after']['path']).stat(), destination.stat()
            assert (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
            guard.checked(dict(item['after'], path=str(destination)))
        write(OUTPUT / 'overlay.json', plan['overlay'])
        guard.checked(descriptor(OUTPUT / 'overlay.json'))
        write(OUTPUT / 'executed-plan.json', dict(requestedPreparationPlan=plan,
              actualAuthority=authority_row, planCaptureSlotsAreNotOutcomeRecords=True))
        write(OUTPUT / 'protection-before.json', dict(schemaVersion=1, files=guard.files,
              trees=guard.trees, aliases=guard.aliases))
        # Original stdlib-only monitor, authenticated before dynamic custom import.
        spec = importlib.util.spec_from_file_location('authenticated_init_barrier_syntax_monitor',
                 Path(plan['references']['monitorIndex']['path']).parent / 'monitor.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        environment = dict(PATH=str(WORK / 'cache/wasi-sdk/85e6/bin') + ':/usr/bin:/bin',
                           LC_ALL='C', LANG='C', TMPDIR=str(OUTPUT / 'tmp'))
        for name in ('HOME', 'home', 'CODEX_HOME'):
            if name in os.environ:
                environment[name] = os.environ[name]
        for unit in plan['units']:
            out = OUTPUT / 'commands' / unit['id']
            out.mkdir(mode=0o700, parents=True)
            Path(unit['dependencyFile']).parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            terminal, command_error, dependency_error = None, None, None
            dependencies = []
            try:
                terminal = module.monitor(unit['argv'], unit['cwd'], environment, out, 60, authority_row)
            except Exception as error:
                command_error = repr(error)
            finally:
                dep = Path(unit['dependencyFile'])
                if dep.is_file():
                    try:
                        for spelling in parse_dependencies(dep.read_text(), unit['dependencyTarget']):
                            logical = os.path.abspath(os.path.join(unit['cwd'], spelling))
                            mapped = next((r['external-contents'] for r in plan['overlay']['roots'] if r['name'] == logical), logical)
                            physical = str(Path(mapped).resolve(strict=True))
                            before = guard.files.get(physical)
                            record = dict(reportedPath=spelling, normalizedLogicalPath=logical,
                                          physicalPath=physical, authenticatedBeforeFrontend=before is not None)
                            dependencies.append(record)
                            assert before is not None, 'Unobserved compiler input: ' + physical
                            guard.checked(before['row'])
                            record['descriptor'] = before['row']
                        assert any(r['physicalPath'] == unit['privateMainPath'] for r in dependencies)
                    except Exception as error:
                        dependency_error = repr(error)
                else:
                    dependency_error = 'Frontend produced no dependency file; no complete dependency claim'
                raw = {name: descriptor(out / name) for name in ('started.json', 'stdout.log', 'stderr.log', 'terminal.json') if (out / name).is_file()}
                observation = dict(id=unit['id'], monitorReturned=terminal is not None,
                    actualStartedRecordPresent='started.json' in raw, raw=raw,
                    rawExitCode=terminal['rawExitCode'] if terminal else None,
                    ownedGroupsClean=clean_terminal(terminal) if terminal else False,
                    commandError=command_error, dependencyError=dependency_error,
                    dependencies=dependencies, dependencyFile=descriptor(dep) if dep.is_file() else None)
                outcomes.append(observation)
                write(OUTPUT / 'unit-outcomes' / (unit['id'] + '.json'), observation)
            assert terminal is not None and clean_terminal(terminal), 'No further command after failed process cleanup'
    except Exception as error:
        primary = repr(error)
    finally:
        final = guard.recheck()
        write(OUTPUT / 'protection-final.json', final)
        passed = (primary is None and final['unchanged'] and len(outcomes) == 2
                  and all(r['rawExitCode'] == 0 and r['ownedGroupsClean']
                          and r['actualStartedRecordPresent'] and not r['commandError']
                          and not r['dependencyError'] for r in outcomes))
        result = dict(schemaVersion=1, state='INIT_BARRIER_TWO_CPP_FRONTEND_SYNTAX_PASSED_V1' if passed else 'INIT_BARRIER_FRONTEND_FAILURE_PRESERVED_V1',
            sourceIndex=plan['references']['sourceIndex'], rootAuthority=authority_row,
            units=outcomes, currentInputProtection=final, primaryError=primary,
            compilerOnly=True, syntaxOnlyCommandsRequested=2,
            compilerStartedRecordsRetained=sum(r['actualStartedRecordPresent'] for r in outcomes),
            allPlannedCompilerStartsProved=passed,
            objectOrLinkRequested=False, nativeBuildHelperEngineGuestCryptoSnapshotInvoked=False,
            barrierBehaviorLinkOdrRuntimeOrAdoptionProved=False)
        write(OUTPUT / 'result.json', result)
        # Exclude only this root index. Nested monitor evidence is included.
        payloads = []
        for path in sorted(OUTPUT.rglob('*')):
            assert not path.is_symlink(), path
            if path.is_file():
                payloads.append(dict(descriptor(path), path=path.relative_to(OUTPUT).as_posix()))
        write(OUTPUT / 'index.json', dict(schemaVersion=1, state=result['state'], files=payloads))
        assert {p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob('*') if p.is_file()} == {r['path'] for r in payloads} | {'index.json'}
        print(json.dumps(dict(result=descriptor(OUTPUT / 'result.json'), index=descriptor(OUTPUT / 'index.json'), state=result['state'])), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    assert len(sys.argv) == 3 and sys.argv[1] == '--execute-root-authorized-two-frontends'
    sys.exit(execute(json.loads(sys.argv[2])))
