"""Inert Cargo-plan renderer and retained-DATA audit; never executes commands.

Python >=3.11. Root runs each issued Cargo command under its existing monitor.
The merged lock is explicitly an untrusted seed until real Cargo reconciles it.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import sys
import tomllib

COMMIT = '9dab3d6f643e926a340c391ea30968e940390dec'
REV = 'ca612daf1c08c53abe07327cb3e6ef6e0a760f0c'
GIT = 'https://github.com/servo/unicode-bidi'
BASE = {'rust-encoding':'crates/rust-encoding', 'rust-hooks':'crates/rust-hooks',
        'rust-url':'crates/rust-url', 'multipart':'crates/rust-multipart'}
FFI = ('intl/icu_capi', 'intl/icu_segmenter_data',
       'intl/bidi/rust/unicode-bidi-ffi', 'third_party/rust/unicode-bidi')
FEATURES = ['any_provider', 'compiled_data', 'segmenter', 'calendar']

# Explicit Source-reviewed same-compatible-family reconciliation, not a
# general resolver or a claim Cargo accepted the seed. Tuple is (fork, old).
RECONCILIATION = {'displaydoc': ('0.2.4', '0.2.5'), 'proc-macro2': ('1.0.101', '1.0.94'), 'quote': ('1.0.40', '1.0.39'), 'serde': ('1.0.227', '1.0.218'), 'serde_derive': ('1.0.227', '1.0.218'), 'smallvec': ('1.15.1', '1.14.0'), 'syn': ('2.0.106', '2.0.99'), 'unicode-ident': ('1.0.6', '1.0.17'), 'zerofrom': ('0.1.4', '0.1.5'), 'zerofrom-derive': ('0.1.3', '0.1.6')}
REGISTRY = 'registry+https://github.com/rust-lang/crates.io-index'



def digest(path):
    p = Path(path)
    raw = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def physical(value):
    p = Path(value)
    assert p.is_absolute() and '..' not in p.parts
    assert all(not q.is_symlink() for q in (p, *p.parents)), str(p)
    return p


def checked(row):
    p = physical(row['path'])
    assert p.is_file() and digest(p) == row, str(p)
    return p.read_bytes()


def inventory(root, prefixes):
    root = physical(root)
    files = []
    for prefix in prefixes:
        for p in sorted((root/prefix).rglob('*')):
            physical(p)
            if p.is_file():
                r = digest(p)
                r['path'] = str(p.relative_to(root))
                files.append(r)
    return files


def verify_tree(root, rows, prefixes):
    root = physical(root)
    expected = {r['path']:r for r in rows}
    assert len(expected) == len(rows) and rows
    actual = inventory(root, prefixes)
    assert set(expected) == {r['path'] for r in actual}, 'Source tree membership'
    for r in actual:
        assert r['sha256'] == expected[r['path']]['sha256'] and r['bytes'] == expected[r['path']]['bytes'], r['path']
    return actual


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write(raw)
        out.flush()
        os.fchmod(out.fileno(), 0o600)
        os.fsync(out.fileno())
    assert path.stat().st_nlink == 1


def save(path, value):
    write(path, (json.dumps(value, indent=2)+'\n').encode())


def key(row):
    return row['name'], row['version'], row.get('source', '')


def dep_id(row):
    return row['name']+' '+row['version']+(' ('+row['source']+')' if row.get('source') else '')


def normalized_rows(rows):
    by = {}
    for r in rows:
        by.setdefault(r['name'], []).append(r)
    out = []
    for row in rows:
        r = dict(row)
        deps = []
        for dep in r.get('dependencies', []):
            match = re.fullmatch(r'([^ ]+)(?: ([^ ]+))?(?: \((.+)\))?', dep)
            assert match, dep
            name, version, source = match.groups()
            candidates = [p for p in by[name] if (version is None or p['version']==version)
                          and (source is None or p.get('source')==source)]
            assert len(candidates) == 1, dep
            deps.append(dep_id(candidates[0]))
        if deps:
            r['dependencies'] = deps
        out.append(r)
    return out


def merged_seed(old_rows, fork_rows):
    merged = {}
    for r in normalized_rows(old_rows)+normalized_rows(fork_rows):
        k = key(r)
        if k in merged:
            other = merged[k]
            assert other.get('checksum') == r.get('checksum'), k
            other['dependencies'] = sorted(set(other.get('dependencies', [])) | set(r.get('dependencies', [])))
        else:
            merged[k] = dict(r)
    root = next(r for r in merged.values() if r['name']=='rust-staticlib')
    names = [*BASE, 'icu_capi', 'unicode-bidi-ffi']
    root['dependencies'] = [dep_id(next(r for r in merged.values() if r['name']==name and not r.get('source'))) for name in names]
    # Cargo refuses simultaneous compatible locked versions. Prefer each
    # reviewed old pin and redirect only reachable callers to that identity.
    redirects = {}
    for name, (fork_version, old_version) in RECONCILIATION.items():
        before = (name, fork_version, REGISTRY)
        after = (name, old_version, REGISTRY)
        assert before in merged and after in merged, (name, before, after)
        redirects[before] = after
    lookup = {dep_id(r):k for k,r in merged.items()}
    root_key = key(root)
    reachable = {}
    pending = [root_key]
    while pending:
        k = pending.pop()
        if k in reachable:
            continue
        r = dict(merged[k])
        deps = []
        for dependency in r.get('dependencies', []):
            original = lookup[dependency]
            selected = redirects.get(original, original)
            # This exact Serde family cannot be mixed. It should disappear
            # after old serde/derive are selected together. If still reachable,
            # fail rather than redirect serde_core's =1.0.227 edge dishonestly.
            assert not (r['name']=='serde_core' and original!=selected), 'Reachable serde_core exact-version edge requires a new decision'
            deps.append(dep_id(merged[selected]))
            pending.append(selected)
        if deps:
            r['dependencies'] = sorted(set(deps))
        reachable[k] = r
    old_keys = {key(r) for r in old_rows}
    assert old_keys <= set(reachable), 'Reconciliation unexpectedly pruned an old package'
    lines = ['# UNTRUSTED RECONCILED SEED V2: real Cargo resolution and DATA audit required.', 'version = 4', '']
    for r in sorted(reachable.values(), key=key):
        lines.append('[[package]]')
        for name in ('name','version','source','checksum','dependencies'):
            if name in r:
                lines.append(name+' = '+json.dumps(r[name], ensure_ascii=False))
        lines.append('')
    return '\n'.join(lines)+'\n'


def prepare(config, input_config=None):
    own_source = digest(Path(__file__).resolve())
    work = physical(config['work'])
    assert not work.exists()
    ffi_root = physical(config['ffiSourceRoot'])
    manifest = json.loads(checked(config['ffiManifest']))
    assert manifest['commit'] == COMMIT and manifest['state'] == 'EXACT_FOUR_FFI_SOURCE_TREES_FETCHED_AND_HASH_VERIFIED_NO_EXECUTION'
    assert str(ffi_root) == manifest['privateRoot']
    ffi_rows = verify_tree(ffi_root, manifest['files'], FFI)
    assert sum(r['bytes'] for r in ffi_rows) <= 32*1024**2 and len(ffi_rows) <= 20000
    base_root = physical(config['baseSourceRoot'])
    base_manifest = json.loads(checked(config['baseManifest']))
    base_rows = verify_tree(base_root, base_manifest['files'], BASE.values())
    assert sum(r['bytes'] for r in base_rows) <= 32*1024**2 and len(base_rows) <= 20000
    old_raw = checked(config['oldAggregateLock'])
    old = tomllib.loads(old_raw.decode())
    constraints = json.loads(checked(config['forkConstraints']))
    assert constraints['forkCommit'] == COMMIT and constraints['notAResolvedCombinedLock'] is True
    fork = constraints['conservativeUpstreamLockRows']
    for name in ('cargo','rustc'):
        checked(config[name])
        assert Path(config[name]['path']).name == name and os.access(config[name]['path'], os.X_OK)
    assert re.fullmatch(r'[A-Za-z0-9_.@+-]{1,64}', config['locale'])
    for directory in config['path']:
        assert physical(directory).is_dir()
    for ancestor in work.parents:
        assert not any((ancestor/'.cargo'/n).exists() for n in ('config','config.toml')), 'Unexpected ancestor Cargo configuration'
    # No original source is rewritten. Cargo will see only exclusive private copies.
    work.mkdir(mode=0o700)
    for name in ('project','sources','online-cargo','offline-cargo','tmp','target'):
        (work/name).mkdir(mode=0o700)
    for root, rows, target in ((base_root,base_rows,work/'sources/base'), (ffi_root,ffi_rows,work/'sources/firefox')):
        for r in rows:
            source = root/r['path']
            dest = target/r['path']
            write(dest, source.read_bytes())
            assert (source.stat().st_dev,source.stat().st_ino) != (dest.stat().st_dev,dest.stat().st_ino)
    base = work/'sources/base'
    ffi = work/'sources/firefox'
    # Keep one aggregate/profile and exactly the actual four old plus two new dependencies.
    text = '[package]\nname = "rust-staticlib"\nedition = "2021"\nresolver = "2"\n\n[lib]\ncrate-type = ["staticlib"]\npath = "rust-staticlib.rs"\n\n[workspace]\n\n[profile.release]\nlto = true\npanic = "abort"\n\n[profile.dev]\nlto = true\npanic = "abort"\n\n'
    text += '[patch.crates-io]\nicu_capi = { path = '+json.dumps(str(ffi/'intl/icu_capi'))+' }\nicu_segmenter_data = { path = '+json.dumps(str(ffi/'intl/icu_segmenter_data'))+' }\nunicode-bidi = { git = '+json.dumps(GIT)+', rev = '+json.dumps(REV)+' }\n\n[dependencies]\n'
    for name, rel in BASE.items():
        path = base/rel
        assert tomllib.loads((path/'Cargo.toml').read_text())['package']['name'] == name
        features = ['capi','simd'] if name=='multipart' else []
        text += name+' = { path = '+json.dumps(str(path))+', features = '+json.dumps(features)+' }\n'
    text += 'icu_capi = { path = '+json.dumps(str(ffi/'intl/icu_capi'))+', default-features = false, features = '+json.dumps(FEATURES)+' }\n'
    text += 'unicode-bidi-ffi = { path = '+json.dumps(str(ffi/'intl/bidi/rust/unicode-bidi-ffi'))+' }\n'
    write(work/'project/Cargo.toml', text.encode())
    write(work/'project/rust-staticlib.rs', ''.join('pub use '+n.replace('-','_')+';\n' for n in [*BASE,'icu_capi','unicode-bidi-ffi']).encode())
    seed = merged_seed(old['package'], fork)
    write(work/'project/Cargo.lock', seed.encode())
    write(work/'untrusted-seed.lock', seed.encode())
    write(work/'old-aggregate.lock', old_raw)
    save(work/'fork-lock-constraints.json', constraints)
    vendor = work/'vendor'
    offline = '[source.crates-io]\nreplace-with = "intl-vendor"\n\n[source.'+json.dumps('git+'+GIT+'?rev='+REV)+']\ngit = '+json.dumps(GIT)+'\nrev = '+json.dumps(REV)+'\nreplace-with = "intl-vendor"\n\n[source.intl-vendor]\ndirectory = '+json.dumps(str(vendor))+'\n'
    write(work/'offline-cargo/config.toml', offline.encode())
    assert os.environ.get('HOME'), 'Inherited HOME is required and is never reassigned'
    env = dict(PATH=os.pathsep.join(config['path']), HOME=os.environ['HOME'], RUSTC=config['rustc']['path'],
               CARGO_TARGET_DIR=str(work/'target'), CARGO_BUILD_JOBS='1', CARGO_INCREMENTAL='0',
               CARGO_NET_RETRY='2', CARGO_HTTP_TIMEOUT='60', CARGO_NET_GIT_FETCH_WITH_CLI='false',
               TMPDIR=str(work/'tmp'), LANG=config['locale'], LC_ALL=config['locale'],
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    for name in ('home','CODEX_HOME'):
        if name in os.environ:
            env[name] = os.environ[name]
    online = dict(env, CARGO_HOME=str(work/'online-cargo'), CARGO_NET_OFFLINE='false')
    off = dict(env, CARGO_HOME=str(work/'offline-cargo'), CARGO_NET_OFFLINE='true')
    cargo = config['cargo']['path']
    meta = [cargo,'metadata','--manifest-path',str(work/'project/Cargo.toml'),'--format-version','1','--filter-platform','wasm32-wasip1']
    plan = dict(schemaVersion=1,state='CARGO_PLAN_RENDERED_UNEXECUTED_V2',work=str(work),forkCommit=COMMIT,
                seedIsResolvedLock=False, actualCombinedLock=None, actualVendor=None,
                seedReconciliation=[dict(name=n,droppedForkVersion=v[0],selectedOldVersion=v[1]) for n,v in RECONCILIATION.items()],
                unreachableForkPackagesPruned=True,
                rootDependencyNames=[*BASE,'icu_capi','unicode-bidi-ffi'],
                commands=[dict(id='resolve-online',argv=meta,cwd=str(work/'project'),environment=online,stdout='online-metadata.json',stderr='online-metadata.stderr.log',seconds=600),
                          dict(id='vendor-online-after-lock-audit',argv=[cargo,'vendor','--manifest-path',str(work/'project/Cargo.toml'),'--locked','--versioned-dirs',str(vendor)],cwd=str(work/'project'),environment=online,stdout='vendor-config.stdout.toml',stderr='vendor.stderr.log',seconds=600),
                          dict(id='metadata-offline-locked-after-vendor-audit',argv=meta+['--offline','--locked'],cwd=str(work/'project'),environment=off,stdout='offline-metadata.json',stderr='offline-metadata.stderr.log',seconds=300)],
                rootMustMonitorCommands=True, commandsExecuted=False,nativeCompilationAllowed=False,
                requiredDataGates=['resolve-online terminal0 and audit.lockPolicyPassed=true before vendor',
                                   'vendor terminal0 and audit.mozillaPatchedBidiRustAndManifestMatch=true before offline',
                                   'offline terminal0/--locked and audit.offlineLogicalGraphAndFeaturesMatch=true'],
                sourceBytesCopied=sum(r['bytes'] for r in base_rows+ffi_rows), expectedNetworkBytes=None,
                inputConfig=input_config,helperSource=own_source,
                environmentPolicy=dict(HOMEPreserved=True,homeAndCODEX_HOMEPreservedWhenPresent=True,
                                       privateCargoHomes=True,OSHermeticityClaimed=False))
    prepared = [digest(work/'project/Cargo.toml'), digest(work/'project/rust-staticlib.rs'),
                digest(work/'offline-cargo/config.toml'), digest(work/'old-aggregate.lock'),
                digest(work/'fork-lock-constraints.json'), digest(work/'untrusted-seed.lock')]
    save(work/'source-inputs.json', dict(config=config, baseRows=base_rows, ffiRows=ffi_rows,
                                        inputConfig=input_config,helperSource=own_source,prepared=prepared))
    save(work/'plan.json', plan)
    verify_tree(base_root,base_rows,BASE.values()); verify_tree(ffi_root,ffi_rows,FFI)
    checked(own_source)
    return plan


def recheck(work):
    """Hash-only original/copied source/config/tool checks for each Root phase."""
    work = physical(work)
    inputs = json.loads((work/'source-inputs.json').read_text())
    config = inputs['config']
    checked(inputs['helperSource'])
    if inputs['inputConfig'] is not None:
        checked(inputs['inputConfig'])
    for name in ('ffiManifest','baseManifest','oldAggregateLock','forkConstraints','cargo','rustc'):
        checked(config[name])
    for row in inputs['prepared']:
        checked(row)
    for root, rows, prefixes in ((config['baseSourceRoot'],inputs['baseRows'],BASE.values()),
                                  (config['ffiSourceRoot'],inputs['ffiRows'],FFI),
                                  (work/'sources/base',inputs['baseRows'],BASE.values()),
                                  (work/'sources/firefox',inputs['ffiRows'],FFI)):
        verify_tree(root,rows,prefixes)
    return dict(sourceAndPreparedInputsUnchanged=True,originalAndCopiedSourceFiles=2*(len(inputs['baseRows'])+len(inputs['ffiRows'])),
                compilationOrCargoInvoked=False)


def vendor_checks(vendor, rows):
    """Verify the retained whole vendor set against lock/package/file checksums."""
    expected = {key(r):r for r in rows if r.get('source')}
    seen = set()
    file_count = total = 0
    for directory in sorted(physical(vendor).iterdir()):
        physical(directory)
        assert directory.is_dir(), str(directory)
        package = tomllib.loads((directory/'Cargo.toml').read_text())['package']
        sums = json.loads((directory/'.cargo-checksum.json').read_text())
        matches = [k for k,r in expected.items() if k[:2]==(package['name'],package['version'])
                   and r.get('checksum')==sums['package']]
        assert len(matches)==1 and matches[0] not in seen, package
        seen.add(matches[0])
        actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
        assert actual == set(sums['files']) | {'.cargo-checksum.json'}, str(directory)
        for relative, sha in sums['files'].items():
            assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
            path = physical(directory/relative)
            row = digest(path)
            assert row['sha256']==sha, str(path)
            file_count += 1
            total += row['bytes']
            assert file_count<=200000 and total<=512*1024**2, 'Vendor DATA audit bound'
    assert seen==set(expected), 'Vendor/lock source coverage'
    return dict(packages=len(seen),files=file_count,bytes=total,allRecordedChecksumsMatch=True)


def audit(work):
    """Read actual retained Cargo outputs. No command, lock or vendor mutation."""
    work = physical(work)
    source_protection = recheck(work)
    plan = json.loads((work/'plan.json').read_text())
    rows = tomllib.loads((work/'project/Cargo.lock').read_text())['package']
    old = tomllib.loads((work/'old-aggregate.lock').read_text())['package']
    fork = json.loads((work/'fork-lock-constraints.json').read_text())['conservativeUpstreamLockRows']
    allowed = {key(r):r for r in old+fork}
    current = {key(r):r for r in rows}
    unexpected = [r for k,r in current.items() if k not in allowed]
    changed_old = [r for r in old if key(r) not in current and r['name']!='rust-staticlib']
    wrong_shared = [r for r in rows if r['name'] in RECONCILIATION and r['version'] != RECONCILIATION[r['name']][1]]
    for k,r in current.items():
        if k in allowed:
            assert r.get('checksum') == allowed[k].get('checksum'), k
    meta = json.loads((work/'online-metadata.json').read_text())
    packages = {p['id']:p for p in meta['packages']}
    root = packages[meta['resolve']['root']]
    assert root['name']=='rust-staticlib' and {d['name'] for d in root['dependencies']} == set(plan['rootDependencyNames'])
    assert [t['crate_types'] for t in root['targets'] if 'staticlib' in t['crate_types']] == [['staticlib']]
    capi = next(p for p in packages.values() if p['name']=='icu_capi')
    node = next(n for n in meta['resolve']['nodes'] if n['id']==capi['id'])
    assert capi['version']=='2.0.0' and set(node['features']) == set(FEATURES)
    bidi = next(r for r in rows if r['name']=='unicode-bidi')
    assert bidi['version']=='0.3.15' and bidi['source']=='git+'+GIT+'?rev='+REV+'#'+REV
    result = dict(schemaVersion=1,actualLock=digest(work/'project/Cargo.lock'),packageCount=len(rows),
                  unexpectedIdentities=unexpected,oldPackageIdentitiesRemovedOrChanged=changed_old,
                  lockPolicyPassed=not unexpected and not changed_old and not wrong_shared,
                  sharedFamilyReconciliationMismatches=wrong_shared,
                  explicitSharedFamilyReconciliation=plan['seedReconciliation'],
                  sourceProtection=source_protection,rootMustAuthenticateActualCargoTerminals=True,
                  dataConsistencyOnly=True,nativeOrGuestExecuted=False)
    if (work/'vendor').exists():
        result['vendorChecksums'] = vendor_checks(work/'vendor', rows)
        # Cargo's manifest/checksum formatting may differ; require identical Rust
        # source bytes and parsed manifest semantics to the authenticated Mozilla copy.
        expected = work/'sources/firefox/third_party/rust/unicode-bidi'
        target = next(p for p in (work/'vendor').iterdir() if (p/'Cargo.toml').exists() and
                      tomllib.loads((p/'Cargo.toml').read_text())['package']['name']=='unicode-bidi')
        assert tomllib.loads((expected/'Cargo.toml').read_text()) == tomllib.loads((target/'Cargo.toml').read_text()), 'Patched Bidi manifest differs'
        a = inventory(expected, ['src']); b = inventory(target, ['src'])
        assert a==b, 'Patched Bidi Rust sources differ'
        result['mozillaPatchedBidiRustAndManifestMatch'] = True
    if (work/'offline-metadata.json').exists():
        offline = json.loads((work/'offline-metadata.json').read_text())
        def signature(m):
            ps={p['id']:(p['name'],p['version'],p['source']) for p in m['packages']}
            return sorted((ps[n['id']],sorted(n['features']),sorted(ps[d['pkg']] for d in n['deps'])) for n in m['resolve']['nodes'])
        assert signature(meta)==signature(offline), 'Offline graph/feature drift'
        result['offlineLogicalGraphAndFeaturesMatch'] = True
    return result


if __name__ == '__main__':
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert len(sys.argv)==3 and sys.argv[1] in ('--prepare','--audit','--recheck')
    if sys.argv[1]=='--prepare':
        row=digest(physical(sys.argv[2]))
        value=prepare(json.loads(checked(row)),row)
    else:
        value=audit(sys.argv[2]) if sys.argv[1]=='--audit' else recheck(sys.argv[2])
    print(json.dumps(value,indent=2))
    if sys.argv[1]=='--audit' and not value['lockPolicyPassed']:
        raise SystemExit(1)
