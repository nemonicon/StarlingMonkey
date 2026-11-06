"""Read retained metadata/protection only; never executes Cargo or helpers."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import stat
import tomllib

HERE = Path(__file__).resolve().parent
CONTROL = Path('/private/tmp/starling-node-compat/next-intl-old-feature-control-v1')
COMBINED = Path('/private/tmp/starling-node-compat/next-intl-cargo-resolution-v2')


def row(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    for p in (path, *path.parents):
        assert not p.is_symlink()
    s = path.stat()
    assert stat.S_ISREG(s.st_mode) and s.st_nlink == 1
    b = path.read_bytes()
    t = path.stat()
    assert (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns) == (t.st_dev, t.st_ino, t.st_size, t.st_mtime_ns, t.st_ctime_ns)
    return dict(path=str(path), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def pinned(path, sha):
    r = row(path)
    assert r['sha256'] == sha
    return r


def read(ref):
    assert row(ref['path']) == ref
    return json.loads(Path(ref['path']).read_text())


def graph(m):
    packages = {p['id']: p for p in m['packages']}
    def identity(identifier):
        p = packages[identifier]
        return (p['name'], p['version'], p['source'])
    return {identity(n['id']): dict(features=sorted(n['features']), node=n, package=packages[n['id']]) for n in m['resolve']['nodes']}


def main():
    authority_ref = pinned(HERE/'old-feature-control-v1-authority.json', '6d988648f7bb7095bb4b8c9ee0741c9a8ffa1bbd7aa88ce91f4ab553a7e89161')
    authority = read(authority_ref)
    collector_ref = row(HERE/'old-feature-control-v1-result.json')
    collector = read(collector_ref)
    assert collector['passed'] is False
    assert len(collector['errors']) == 1 and collector['errors'][0]['type'] == 'AssertionError'
    assert 'set(old_graph) == lock_keys' in collector['errors'][0]['traceback']
    terminal_ref = pinned(CONTROL/'owned-monitor/terminal.json', '8f23932ae988c5b3d492be22fd75bfafc93a954a3f25acb198e9729dcd680727')
    terminal = read(terminal_ref)
    assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
    assert not terminal['timeout'] and not terminal['forcedCleanup']
    assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
    assert collector['beforeSourceProtection'] == collector['finalSourceProtection']
    assert collector['finalSourceProtection']['sourceAndPreparedInputsUnchanged'] is True
    assert collector['finalSourceProtection']['originalAndCopiedSourceFiles'] == 2296
    assert collector['protectedInputsAndVendorUnchanged'] is True
    for p in authority['protectedInputs']:
        assert row(p['descriptor']['path']) == p['descriptor']
        s = Path(p['descriptor']['path']).stat()
        assert (stat.S_IMODE(s.st_mode), s.st_ino, s.st_dev, s.st_nlink) == (p['mode'], p['inode'], p['device'], p['links'])
    actual_vendor = [row(p) for p in sorted((COMBINED/'vendor').rglob('*')) if p.is_file()]
    assert actual_vendor == authority['validatedVendorInputRows']
    control_ref = pinned(CONTROL/'owned-monitor/stdout.log', 'a3bbae45c0ac3deca1d7fce4831109a5398bfb9b31fa76f29c138c82cf4b4f0c')
    old_meta = read(control_ref)
    combined_ref = row(COMBINED/'offline-metadata.json')
    new_meta = read(combined_ref)
    old, new = graph(old_meta), graph(new_meta)
    old_lock_ref = pinned(COMBINED/'old-aggregate.lock', '46a469ce88f8334da3cd64872191b927eb969c84f8c08b58c8ec2501b205b30a')
    new_lock_ref = pinned(COMBINED/'project/Cargo.lock', 'dc098f33febee6952974705077140ff543ca37eb1cedad2e0b07496646c3bd61')
    identity = lambda p: (p['name'], p['version'], p.get('source'))
    old_lock = {identity(p) for p in tomllib.loads(Path(old_lock_ref['path']).read_text())['package']}
    new_lock = {identity(p) for p in tomllib.loads(Path(new_lock_ref['path']).read_text())['package']}
    missing = old_lock-set(old)
    serde_derive = ('serde_derive','1.0.218','registry+https://github.com/rust-lang/crates.io-index')
    assert missing == {serde_derive} and set(old) <= old_lock and old_lock <= new_lock
    assert len(old_lock) == 49 and len(new_lock) == 84 and len(old) == 48 and len(new) == 84
    assert set(old) <= set(new)
    changes = []
    for key in sorted(old):
        a, b = set(old[key]['features']), set(new[key]['features'])
        if a != b:
            changes.append(dict(name=key[0], version=key[1], source=key[2], oldFeatures=sorted(a), combinedFeatures=sorted(b), added=sorted(b-a), removed=sorted(a-b)))
    assert {c['name']:c['added'] for c in changes} == {'serde':['derive','serde_derive'], 'smallvec':['union'], 'syn':['full']}
    assert all(c['removed'] == [] for c in changes)
    source_requests = []
    for package_name, version, dependency, feature in [('unicode-bidi','0.3.15','smallvec','union'), ('diplomat','0.11.0','syn','full'), ('diplomat_core','0.11.0','syn','full'), ('diplomat_core','0.11.0','serde','derive')]:
        p = next(p for p in new_meta['packages'] if p['name'] == package_name and p['version'] == version)
        d = next(d for d in p['dependencies'] if d['name'] == dependency and feature in d['features'] and d['kind'] is None)
        ref = row(p['manifest_path'])
        parsed = tomllib.loads(Path(ref['path']).read_text())
        assert feature in parsed['dependencies'][dependency]['features']
        source_requests.append(dict(parent=package_name, version=version, dependency=dependency, requestedFeatures=d['features'], usesDefaultFeatures=d['uses_default_features'], manifest=ref,
                                    procMacroManifest=any('proc-macro' in t['kind'] for t in p['targets'])))
    fingerprint_root = Path('/private/tmp/starling-node-compat/next-native-build-v5/build/cargo/build')
    fingerprint_rows = []
    fingerprint_names = set()
    for p in sorted(fingerprint_root.rglob('*.json')):
        if '.fingerprint' not in p.parts or not p.name.startswith('lib-'):
            continue
        name = p.parent.name.rsplit('-',1)[0]
        if name not in {k[0] for k in old_lock}:
            continue
        value = json.loads(p.read_text())
        features = json.loads(value['features'])
        key = next(k for k in old_lock if k[0] == name)
        assert features == old[key]['features'], name
        fingerprint_rows.append(dict(name=name, version=key[1], target='wasm32-wasip1' if 'wasm32-wasip1' in p.parts else 'host', features=features, descriptor=row(p)))
        fingerprint_names.add(name)
    assert len(fingerprint_rows) == 47 and {k[0] for k in old_lock}-fingerprint_names == {'serde','serde_derive'}
    report = dict(schemaVersion=1, state='RETAINED_OLD4_OFFLINE_FEATURE_CONTROL_DATA_RECONCILED_V1', verifiedPassed=True,
                  collectorResult=collector_ref, originalCollectorPassed=False, originalCollectorFailurePreserved=True,
                  collectorFailure='Invalid author assumption: a49-entry lock must yield49 default metadata nodes. Actual graph has48; serde_derive is not selected.',
                  actualCargoRawExitCode=0, originalTerminal=terminal_ref, authority=authority_ref, controlMetadata=control_ref,
                  combinedOfflineMetadata=combined_ref, oldLock=old_lock_ref, combinedLock=new_lock_ref,
                  lockPackages=dict(old=49, combined=84, preservedOld=49, new=35, removed=0),
                  metadataNodes=dict(old=48, combined=84, preservedOld=48, new=36, removed=0),
                  oldLockEntriesNotInOldMetadata=[dict(name=k[0],version=k[1],source=k[2]) for k in sorted(missing)],
                  oldMetadataFeatureSetsUnchanged=45, sharedFeatureChanges=changes, oldMetadataFeaturesRemoved=0,
                  serde=dict(oldMetadataFeatures=old[('serde','1.0.218',serde_derive[2])]['features'], oldBuildFingerprintAbsent=True,
                             combinedFeatures=new[('serde','1.0.218',serde_derive[2])]['features']),
                  serdeDerive=dict(alreadyInOldLock=True, oldMetadataNodePresent=False, oldBuildFingerprintAbsent=True,
                                   newMetadataNodePresent=True, newFeatures=new[serde_derive]['features'], procMacro=True,
                                   newlySelectedInMetadata=True, newCompilationObserved=False),
                  featureRequestSources=source_requests, oldBuildFingerprintRows=fingerprint_rows,
                  targetHostQualification='Metadata resolve.features unifies logical package features and is not a compiled unit graph. Existing fingerprints corroborate old target smallvec and host syn; source edges request union through target unicode-bidi-ffi and full/serde derive through host Diplomat proc macros. No new Rust compilation observed.',
                  identityPolicy='Registry/Git identities match exact name/version/source; five path-package identities match name/version/source-null and authenticated unchanged source bytes, not literal root-dependent package IDs.',
                  sourceProtection=collector['finalSourceProtection'], protectedInputsAndVendorUnchanged=True,
                  protectedControlAndOriginalRows=len(authority['protectedInputs']), vendorRowsRehashed=len(actual_vendor),
                  diskBytesBefore=collector['diskBytesBefore'], diskBytesAfter=collector['diskBytesAfter'], periodicDiskGuardClaimed=False,
                  dataReaderExecutesCargoOrHelpers=False, newNativeCompilation=False, newGuestExecution=False, networkUsed=False,
                  operationalAcceptanceClaim=False, noIntlEngineAdmissionClaim=True)
    with (HERE/'old-feature-control-v1-data-review.json').open('x') as out:
        json.dump(report,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
    copies = []
    for p in sorted((CONTROL/'owned-monitor').glob('owned-*.json')):
        target = HERE/('old-feature-control-v1-'+p.name+'.gz')
        with target.open('xb') as out:
            out.write(gzip.compress(p.read_bytes(),mtime=0))
        copies.append(dict(original=row(p),retained=row(target)))
    for name in ('stdout.log','stderr.log','terminal.json','started.json'):
        p = CONTROL/'owned-monitor'/name
        copy = HERE/('old-feature-control-v1-'+name+'.gz')
        assert gzip.decompress(copy.read_bytes()) == p.read_bytes()
        copies.append(dict(original=row(p),retained=row(copy)))
    with (HERE/'old-feature-control-v1-raw-copy-map.json').open('x') as out:
        json.dump(dict(schemaVersion=1,copies=copies),out,indent=2);out.write('\n')
    print(json.dumps(dict(dataReview=row(HERE/'old-feature-control-v1-data-review.json'), originalCollector=collector_ref,
                          controlMetadata=control_ref, rawCopyMap=row(HERE/'old-feature-control-v1-raw-copy-map.json'), featureChanges=changes,
                          serdeDeriveNewlySelected=True, rawCargoExitCode=0, noCommandRerun=True)),flush=True)


if __name__ == '__main__':
    main()
