"""Dormant corrected ALS-only frontend driver. Requires a new explicit Root authority.
No action on import; no producer/helper/engine/guest is called.
"""
from pathlib import Path
import hashlib, importlib.util, json, os, shlex, stat, sys
sys.dont_write_bytecode = True
OWN = Path(__file__).resolve().parent
OUTPUT = Path('/private/tmp/starling-node-compat/native-als-v3-sdk-syntax-v1')
BASE = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')

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
        self.absences = {}

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

    def absent_include(self, policy):
        assert policy['mustRemainAbsent'] is True
        observed = absence_snapshot(Path(policy['path']))
        self.absences[policy['path']] = dict(policy=policy, observed=observed)
        return observed

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
        for path, before in self.absences.items():
            try:
                assert absence_snapshot(Path(path)) == before['observed'], path
            except Exception as error:
                errors.append(dict(path=path, error=repr(error)))
        return dict(schemaVersion=1, files=len(self.files), trees=len(self.trees),
                    aliases=len(self.aliases), absentIncludes=len(self.absences), unchanged=not errors, errors=errors,
                    membershipComparison='sets of relative POSIX strings',
                    fileChecks='SHA256/bytes/mode/device/inode/nlink/mtime/ctime')

def absence_snapshot(path):
    """Absent means no entry, including dangling links; never create the path.

    Visit physical ancestors root-first. Missing intermediate components are
    recorded and must remain missing; every existing ancestor must be a real
    directory with stable device/inode/mode, never an alias.
    """
    assert path.is_absolute() and '..' not in path.parts
    ancestors, missing = {}, []
    for item in reversed((path, *path.parents)):
        try:
            s = item.lstat()
        except FileNotFoundError:
            missing.append(str(item))
            continue
        assert not stat.S_ISLNK(s.st_mode), item
        assert item != path, 'Expected include path must remain absent: ' + str(path)
        assert stat.S_ISDIR(s.st_mode), item
        ancestors[str(item)] = dict(device=s.st_dev, inode=s.st_ino, mode=stat.S_IMODE(s.st_mode))
    assert str(path) in missing
    return dict(path=str(path), missingComponents=missing, physicalAncestors=ancestors)

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
            and t['interruptedSignals'] == []
            and not t['errors'] and not t['remainingObservedPids'])

def write(path, value):
    path = Path(path)
    assert path.is_relative_to(OUTPUT) and not path.is_symlink()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + '\n').encode() if not isinstance(value, bytes) else value
    with path.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        assert stream.write(raw) == len(raw)
        stream.flush(); os.fsync(stream.fileno())

def frontend_passed(primary, final, outcomes):
    return (primary is None and final['unchanged'] and len(outcomes)==13 and
            all(r['terminal'] is not None and r['terminal']['rawExitCode']==0 and clean_terminal(r['terminal']) and
                r['startedArgvMatches'] and len(r['raw'])==4 and not r['commandError'] and not r['dependencyError'] and
                r['protectionBefore']['unchanged'] and r['protectionAfter']['unchanged'] for r in outcomes))

def authenticate(authority_row):
    assert not sys.flags.optimize
    guard = Protection()
    authority = guard.read(authority_row)
    assert authority['schemaVersion'] == 1 and authority['state'] == 'ROOT_NATIVE_ALS_V3_SDK_FRONTEND_AUTHORITY_V1'
    assert authority['sourceReviewedForFrontend'] is True and authority['syntaxOnlyCompilerAllowed'] is True
    for key in ['nativeBuildAllowed', 'objectOrLinkAllowed', 'helperAllowed', 'engineAllowed',
                'guestAllowed', 'cryptoAllowed', 'gcPressureAllowed', 'oomAllowed', 'resetAllowed', 'adoptionAllowed']:
        assert authority[key] is False, key
    own_index = authority['sourceIndex']
    assert own_index['path'] == str(OWN / 'index.json')
    guard.family(own_index)
    assert authority['outputRoot'] == str(OUTPUT) and authority['timeoutSecondsPerUnit'] == 60
    plan_row = descriptor(OWN / 'sdk-plan.json')
    assert authority['plan'] == plan_row
    plan = guard.read(plan_row)
    assert plan['state'] == 'DORMANT_NATIVE_ALS_V3_SDK_SYNTAX_PLAN_V1'
    assert plan['outputRoot'] == str(OUTPUT) and len(plan['units']) == 13
    assert authority['units'] == [r['id'] for r in plan['units']]
    for reference in plan['references'].values(): guard.checked(reference)
    guard.family(plan['references']['monitorIndex'])
    guard.family(plan['references']['parentAlsIndex'])
    assert Path(sys.executable).resolve() == Path(plan['references']['python']['path']).resolve()
    ledger = guard.read(plan['references']['inputLedger'])['files']
    aliases = guard.read(plan['references']['aliasInventory'])['symlinks']
    for tree in plan['protectedTrees']:
        root = Path(tree['path'])
        rows = [r for r in ledger if Path(r['path']).is_relative_to(root)
                and '.git' not in Path(r['path']).relative_to(root).parts]
        links = [r for r in aliases if Path(r['path']).is_relative_to(root)]
        assert len(rows) == tree['regularFiles'] and len(links) == tree['symlinks']
        guard.tree(root, rows, links)
    for policy in plan['absentIncludePolicies']:
        assert any(policy['literalCompileArgument'] in u['preservedArguments'] for u in plan['units'])
        guard.absent_include(policy)
    for row in plan['externalEmbeddingInputs']: guard.checked(row)
    virtual = {}
    for row in plan['candidateFiles']:
        guard.checked(row['source'])
        assert row['privatePath'] == str(OUTPUT / 'native' / row['relativePath'])
        assert row['logicalPath'] == str(BASE / row['relativePath'])
        virtual[row['logicalPath']] = row['privatePath']
    assert len(virtual) == len(plan['candidateFiles']) == 24
    assert plan['overlay'] == {'version':0,'case-sensitive':True,'use-external-names':False,
        'roots':[{'type':'file','name':r['logicalPath'],'external-contents':r['privatePath']}
                 for r in plan['candidateFiles']]}
    db = guard.read(plan['references']['compileDatabase'])
    metadata = guard.read(plan['references']['metadata'])
    assert len(metadata) == 83 and len(metadata['sourceManifest']) == 357
    assert metadata['engineSha256'] == plan['references']['engine']['sha256']
    assert metadata['compileCommandsSha256'] == plan['references']['compileDatabase']['sha256']
    assert len(metadata['componentizeSourceManifest']) == 3
    # This83-field frame is authenticated BASE provenance, not an ALS frame.
    assert plan['baseMetadataIsNewAlsMetadata'] is False
    for unit in plan['units']:
        if 'actualCompileRow' in unit: assert unit['actualCompileRow'] in db
        else: assert unit['actualCompileCommand'] in metadata['actualEmbeddingCompileCommands']
        argv = unit['argv']
        assert argv.count('-DNODE_COMPAT_ASYNC_LOCAL_STORAGE=1') == 1
        assert argv.count('-fsyntax-only') == 1 and '-c' not in argv and '-o' not in argv
        assert '--target=wasm32-wasi' in argv and '-DNDEBUG' in argv
        assert unit['timeoutSeconds'] == 60 and not unit['executionStarted']
        if 'privateMainPath' in unit:
            assert argv[-1] == unit['privateMainPath']
            assert ['-iquote', unit['addedQuotedIncludeDirectory']] == argv[argv.index('-iquote'):argv.index('-iquote')+2]
            assert unit['addedQuotedIncludeDirectory'] == str(Path(unit['logicalMainPath']).parent)
        assert not any(x.startswith(('-DDEBUG', '-DENABLE_JS_DEBUGGER', '-DNODE_COMPAT_GC_STRESS', '-DNODE_COMPAT_OOM')) for x in argv)
    return guard, plan

def execute(authority_row):
    assert not OUTPUT.exists(), 'Fresh absent output required; no implicit retry'
    guard, plan = authenticate(authority_row)
    os.umask(0o077); OUTPUT.mkdir(mode=0o700); (OUTPUT / 'tmp').mkdir(mode=0o700)
    outcomes, primary = [], None
    try:
        for row in plan['candidateFiles']:
            target = Path(row['privatePath']); write(target, Path(row['source']['path']).read_bytes())
            assert (target.stat().st_dev, target.stat().st_ino) != (Path(row['source']['path']).stat().st_dev, Path(row['source']['path']).stat().st_ino)
            guard.checked(dict(row['source'], path=str(target)))
        write(OUTPUT / 'overlay.json', plan['overlay']); guard.checked(descriptor(OUTPUT / 'overlay.json'))
        write(OUTPUT / 'requested-plan.json', plan)
        write(OUTPUT / 'protection-before.json', {'files':guard.files,'trees':guard.trees,
              'aliases':guard.aliases,'absentIncludes':guard.absences})
        # Genuine unchanged0af API, authenticated before its first custom import.
        path = Path(plan['references']['monitorIndex']['path']).parent / 'monitor.py'
        spec = importlib.util.spec_from_file_location('authenticated_als_sdk_monitor', path)
        monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
        env = {'PATH':str(Path(plan['units'][0]['argv'][0]).parent)+':/usr/bin:/bin',
               'LC_ALL':'C','LANG':'C','TMPDIR':str(OUTPUT / 'tmp')}
        for key in ['HOME','home','CODEX_HOME']:
            if key in os.environ: env[key]=os.environ[key]
        for unit in plan['units']:
            before = guard.recheck(); assert before['unchanged'], before
            out = OUTPUT / 'commands' / unit['id']; out.mkdir(mode=0o700,parents=True)
            dep = Path(unit['dependencyFile']); dep.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            terminal, command_error, dependency_error, dependencies = None, None, None, []
            try:
                terminal = monitor.monitor(unit['argv'],unit['cwd'],env,out,60,authority_row)
            except Exception as error: command_error=repr(error)
            finally:
                if dep.is_file():
                    try:
                        for spelling in parse_dependencies(dep.read_text(), unit['dependencyTarget']):
                            logical = os.path.abspath(os.path.join(unit['cwd'],spelling))
                            physical = next((r['external-contents'] for r in plan['overlay']['roots'] if r['name']==logical),logical)
                            physical = str(Path(physical).resolve(strict=True))
                            prior = guard.files.get(physical)
                            observed = {'reportedPath':spelling,'logicalPath':logical,'physicalPath':physical,
                                        'authenticatedBeforeFrontend':prior is not None}
                            dependencies.append(observed)
                            assert prior is not None, 'Unobserved compiler dependency: '+physical
                            guard.checked(prior['row']); observed['descriptor']=prior['row']
                        expected_main=next((r['external-contents'] for r in plan['overlay']['roots'] if r['name']==unit['argv'][-1]),unit['argv'][-1])
                        assert any(r['physicalPath']==expected_main for r in dependencies)
                    except Exception as error: dependency_error=repr(error)
                else: dependency_error='No dependency file retained'
                raw = {name:descriptor(out/name) for name in ['started.json','stdout.log','stderr.log','terminal.json'] if (out/name).is_file()}
                started = json.loads((out/'started.json').read_text()) if (out/'started.json').is_file() else None
                record = {'id':unit['id'],'terminal':terminal,'raw':raw,'startedArgvMatches':started is not None and started['argv']==unit['argv'],
                          'commandError':command_error,'dependencyError':dependency_error,'dependencies':dependencies,
                          'dependencyFile':descriptor(dep) if dep.is_file() else None,'protectionBefore':before,
                          'protectionAfter':guard.recheck()}
                outcomes.append(record); write(OUTPUT/'unit-outcomes'/(unit['id']+'.json'),record)
            assert terminal is not None and clean_terminal(terminal), 'Stop after incomplete command ownership'
            assert outcomes[-1]['protectionAfter']['unchanged'], 'Stop after changed compiler input'
    except Exception as error: primary=repr(error)
    finally:
        final=guard.recheck()
        passed=frontend_passed(primary,final,outcomes)
        result={'schemaVersion':1,'state':'NATIVE_ALS_V3_THIRTEEN_FRONTEND_SYNTAX_PASSED' if passed else 'NATIVE_ALS_V3_FRONTEND_FAILURE_PRESERVED',
                'passed':passed,'rootAuthority':authority_row,'sourceIndex':json.loads(Path(authority_row['path']).read_text())['sourceIndex'],
                'units':outcomes,'primaryError':primary,'currentInputProtection':final,'syntaxOnly':True,
                'baseMetadataIsNewAlsFrame':False,'objectLinkNativeBuildEngineGuestCryptoGcOomResetInvoked':False,
                'asyncPropagationOrFinalNextCompositionProved':False}
        write(OUTPUT/'result.json',result)
        files=[]
        for path in sorted(OUTPUT.rglob('*')):
            assert not path.is_symlink()
            if path.is_file(): files.append(dict(descriptor(path),path=path.relative_to(OUTPUT).as_posix()))
        write(OUTPUT/'index.json',{'schemaVersion':1,'state':result['state'],'files':files})
        print(json.dumps({'result':descriptor(OUTPUT/'result.json'),'index':descriptor(OUTPUT/'index.json'),'passed':passed}),flush=True)
    return 0 if passed else 1

if __name__ == '__main__':
    assert len(sys.argv)==3 and sys.argv[1]=='--execute-root-authorized-frontends'
    sys.exit(execute(json.loads(sys.argv[2])))

