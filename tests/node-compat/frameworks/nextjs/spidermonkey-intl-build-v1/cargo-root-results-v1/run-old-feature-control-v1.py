"""One Root-authorized offline Cargo metadata control. Never compiles Rust."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import sys
import tomllib
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
WORK = Path('/private/tmp/starling-node-compat/next-intl-old-feature-control-v1')
COMBINED = Path('/private/tmp/starling-node-compat/next-intl-cargo-resolution-v2')
OLD = Path('/private/tmp/starling-node-compat/next-native-build-v5/build/starling-raw.wasm')
HELPER = HERE.parent / 'resolve-aggregate-v2.py'
HELPER_SHA = '954edc4dfdc87961370de43fee8dbc3d730d2561e80db09a4b33bdc2ee5f41be'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
MONITOR_SHA = '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
GRANT = """RootAUTHORIZES one actual OLD4offline featurecontrol now: vendor+offline actualboth0clean; finalaudit-offline-v2.json passesall76/2278/35.5MB checksums,patchedBidi exact,offlinegraphsame. Freshprivate /private/tmp/starling-node-compat/next-intl-old-feature-control-v1 ONLY; exactold908Bmanifest/412Brs +old49lock, replaceonly4pathliterals toprotectedWORKv2basecrates; freshCARGO_HOME(configpointingvalidatedv2vendor),target/tmp; HOMEinherited. DirectCargo/Rustc1.88 checked; actual `cargo metadata --offline --locked --filter-platform wasm32-wasip1 --format-version1` nocompile/network, original0afcap300 ordinarysafe; boundarydisk>=3GiBbefore/>=2GiBafter adequatebecauseoffline metadataonly(noperiodicdiskguardclaim). R2helper.recheckWORKv2 before/after +owncontrolmanifest/lock/config/toolbookends. RetainRootgrantscopeexactthismessage+actualargv/env/source rows inauthorityJSONunderexistingcargo-root-results-v1. Compareactualcontrolvsnewresolve.nodes features/packageids, identifyinactiveoldserde separately, no sourcechanges/Roothelperedits. Returnallrawreceipt+portabletextDATA,sourcemutationunknownrefuse. No furthercommandsneeded."""


def row(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    for p in (path, *path.parents):
        assert not p.is_symlink(), str(p)
    before = path.stat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1, str(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def protected(path):
    value = row(path)
    s = Path(path).stat()
    return dict(descriptor=value, mode=stat.S_IMODE(s.st_mode), inode=s.st_ino, device=s.st_dev, links=s.st_nlink)


def save(path, value):
    with Path(path).open('x') as out:
        json.dump(value, out, indent=2)
        out.write('\n')
        out.flush()
        os.fsync(out.fileno())


def load(path, sha, name):
    assert row(path)['sha256'] == sha
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def create(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    assert Path(path).stat().st_nlink == 1


def normalized(metadata):
    packages = {p['id']: p for p in metadata['packages']}
    def key(identifier):
        p = packages[identifier]
        return (p['name'], p['version'], p['source'])
    result = {}
    for node in metadata['resolve']['nodes']:
        k = key(node['id'])
        assert k not in result
        result[k] = dict(features=sorted(node['features']), dependencies=sorted(key(d['pkg']) for d in node['deps']))
    return result


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert not WORK.exists()
    result = dict(schemaVersion=1, state='OLD_FOUR_DEPENDENCY_OFFLINE_FEATURE_CONTROL_V1', passed=False,
                  readOnlyMetadata=True, nativeCompilation=False, guestExecution=False, networkAllowed=False,
                  errors=[], periodicDiskGuardClaimed=False, authority=None, terminal=None)
    helper = None
    before = []
    before_vendor = []
    try:
        plan = json.loads((COMBINED / 'plan.json').read_text())
        audit = json.loads((HERE / 'audit-offline-v2.json').read_text())
        assert audit['lockPolicyPassed'] and audit['mozillaPatchedBidiRustAndManifestMatch'] and audit['offlineLogicalGraphAndFeaturesMatch']
        assert audit['vendorChecksums']['allRecordedChecksumsMatch']
        assert audit['vendorChecksums']['packages'] == 76 and audit['vendorChecksums']['files'] == 2278
        command = plan['commands'][2]
        environment = dict(command['environment'])
        assert environment['HOME'] == os.environ['HOME']
        cargo = Path(command['argv'][0])
        rustc = Path(environment['RUSTC'])
        assert row(cargo)['sha256'] == '1e871156aaf10cf58364b6fd4c824859d5d178f227b963a81a58ade2442ac744'
        assert row(rustc)['sha256'] == '6efc19b5cef1e23df77a75d94ce8b75ed9e8929f0dee0618154c88fd6d82c3e1'
        assert row(OLD / 'Cargo.toml')['sha256'] == '1461261363726c8a5857307d5fc181a4ff4101db1b6a581defb8c74624b81757'
        assert row(OLD / 'rust-staticlib.rs')['sha256'] == 'd65aa984618b35d8326da7af5c69154bc47e5c207ce49e99567ff010bad1bc5c'
        assert row(COMBINED / 'old-aggregate.lock')['sha256'] == '46a469ce88f8334da3cd64872191b927eb969c84f8c08b58c8ec2501b205b30a'
        originals = [Path(__file__).resolve(), HELPER, MONITOR, cargo, rustc, OLD/'Cargo.toml', OLD/'rust-staticlib.rs',
                     COMBINED/'old-aggregate.lock', COMBINED/'project/Cargo.lock', COMBINED/'online-metadata.json',
                     COMBINED/'offline-metadata.json', COMBINED/'plan.json', COMBINED/'source-inputs.json', HERE/'audit-offline-v2.json']
        before = [protected(p) for p in originals]
        before_vendor = [row(p) for p in sorted((COMBINED/'vendor').rglob('*')) if p.is_file()]
        assert len(before_vendor) == 2278 + 76
        result['diskBytesBefore'] = shutil.disk_usage(COMBINED).free
        assert result['diskBytesBefore'] >= 3 * 1024**3
        helper = load(HELPER, HELPER_SHA, 'old4_control_held_resolver')
        result['beforeSourceProtection'] = helper.recheck(COMBINED)
        WORK.mkdir(mode=0o700)
        for name in ('project', 'cargo-home', 'target', 'tmp', 'owned-monitor'):
            (WORK/name).mkdir(mode=0o700)
        for ancestor in (WORK, *WORK.parents):
            assert not (ancestor/'.cargo/config').exists() and not (ancestor/'.cargo/config.toml').exists()
        manifest = (OLD/'Cargo.toml').read_text()
        old_prefix = '/private/tmp/starling-node-compat/next-native-build-v5/native-source/crates/'
        new_prefix = str(COMBINED/'sources/base/crates') + '/'
        assert manifest.count(old_prefix) == 4
        manifest = manifest.replace(old_prefix, new_prefix)
        create(WORK/'project/Cargo.toml', manifest.encode())
        create(WORK/'project/rust-staticlib.rs', (OLD/'rust-staticlib.rs').read_bytes())
        create(WORK/'project/Cargo.lock', (COMBINED/'old-aggregate.lock').read_bytes())
        create(WORK/'cargo-home/config.toml', ('[source.crates-io]\nreplace-with = "validated-vendor"\n\n[source.validated-vendor]\ndirectory = ' + json.dumps(str(COMBINED/'vendor')) + '\n').encode())
        own_inputs = [WORK/'project/Cargo.toml', WORK/'project/rust-staticlib.rs', WORK/'project/Cargo.lock', WORK/'cargo-home/config.toml']
        before.extend(protected(p) for p in own_inputs)
        environment.update(CARGO_HOME=str(WORK/'cargo-home'), CARGO_TARGET_DIR=str(WORK/'target'), TMPDIR=str(WORK/'tmp'), CARGO_NET_OFFLINE='true')
        argv = [str(cargo), 'metadata', '--manifest-path', str(WORK/'project/Cargo.toml'), '--offline', '--locked', '--filter-platform', 'wasm32-wasip1', '--format-version', '1']
        authority = dict(schemaVersion=1, state='ROOT_AUTHORIZED_OLD4_OFFLINE_FEATURE_CONTROL_V1', grantSender='/root', grantText=GRANT,
                         caller=row(Path(__file__).resolve()), helper=row(HELPER), monitor=row(MONITOR), argv=argv, cwd=str(WORK/'project'),
                         environment=environment, protectedInputs=before, validatedVendorInputRows=before_vendor,
                         validatedVendorAudit=row(HERE/'audit-offline-v2.json'), outerOperationalSeconds=300, nativeCompilationAllowed=False,
                         networkAllowed=False, guestExecutionAllowed=False, inheritedHOMEPreserved=True, periodicDiskGuardClaimed=False)
        save(HERE/'old-feature-control-v1-authority.json', authority)
        result['authority'] = row(HERE/'old-feature-control-v1-authority.json')
        monitor = load(MONITOR, MONITOR_SHA, 'old4_control_original_owned_monitor')
        terminal = monitor.monitor(argv, str(WORK/'project'), environment, WORK/'owned-monitor', 300, result['authority'])
        result['terminal'] = row(WORK/'owned-monitor/terminal.json')
        assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
        assert not terminal['timeout'] and not terminal['forcedCleanup']
        assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        control = json.loads((WORK/'owned-monitor/stdout.log').read_text())
        combined = json.loads((COMBINED/'offline-metadata.json').read_text())
        old_graph, new_graph = normalized(control), normalized(combined)
        lock_keys = {(p['name'], p['version'], p.get('source')) for p in tomllib.loads((COMBINED/'old-aggregate.lock').read_text())['package']}
        assert set(old_graph) == lock_keys and set(old_graph) <= set(new_graph)
        changes = []
        for key in sorted(old_graph):
            old, new = old_graph[key], new_graph[key]
            added = sorted(set(new['features']) - set(old['features']))
            removed = sorted(set(old['features']) - set(new['features']))
            if added or removed:
                changes.append(dict(name=key[0], version=key[1], source=key[2], oldFeatures=old['features'], newFeatures=new['features'], added=added, removed=removed))
        result.update(controlMetadata=row(WORK/'owned-monitor/stdout.log'), combinedOfflineMetadata=row(COMBINED/'offline-metadata.json'),
                      oldPackages=len(old_graph), combinedPackages=len(new_graph), newPackages=len(set(new_graph)-set(old_graph)), featureChanges=changes,
                      featureSetsUnchanged=len(old_graph)-len(changes), exactPathIdsComparedLiterally=False,
                      pathIdentityPolicy='Path dependencies matched by exact name/version/source-null; physical source roots intentionally differ',
                      serdeControl=[dict(name=k[0], oldFeatures=old_graph[k]['features'], combinedFeatures=new_graph[k]['features']) for k in old_graph if k[0] in ('serde','serde_derive')])
        result['operationPassed'] = True
    except BaseException as error:
        result['errors'].append(dict(stage='operation-or-collection', type=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
    finally:
        try:
            assert helper is not None
            result['finalSourceProtection'] = helper.recheck(COMBINED)
            assert [protected(x['descriptor']['path']) for x in before] == before
            assert [row(p) for p in sorted((COMBINED/'vendor').rglob('*')) if p.is_file()] == before_vendor
            result['protectedInputsAndVendorUnchanged'] = True
            result['diskBytesAfter'] = shutil.disk_usage(COMBINED).free
            assert result['diskBytesAfter'] >= 2 * 1024**3
            if result['authority'] is not None:
                assert row(result['authority']['path']) == result['authority']
        except BaseException as error:
            result['errors'].append(dict(stage='final-protection', type=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
        result['passed'] = bool(result.get('operationPassed')) and not result['errors'] and result.get('protectedInputsAndVendorUnchanged') is True
        for key, path in [('stdout', WORK/'owned-monitor/stdout.log'), ('stderr', WORK/'owned-monitor/stderr.log'), ('terminal', WORK/'owned-monitor/terminal.json')]:
            if path.exists():
                result[key] = row(path)
        save(HERE/'old-feature-control-v1-result.json', result)
        for name in ('stdout.log', 'stderr.log', 'terminal.json', 'started.json'):
            path = WORK/'owned-monitor'/name
            if path.exists():
                create(HERE/('old-feature-control-v1-'+name+'.gz'), gzip.compress(path.read_bytes(), mtime=0))
        print(json.dumps(result), flush=True)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
