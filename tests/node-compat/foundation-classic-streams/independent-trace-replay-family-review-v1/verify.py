"""Independent read/hash/data verification only; imports no reviewed owner code."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
FAMILY = HERE.parent
STAGE = Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
OUT = STAGE / 'tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1'
PRODUCER = FAMILY / 'trace-replay-activation-candidate-v1'
PARENT = FAMILY / 'production-regression-activated-v3'
RUNTIME = FAMILY / 'production-trace-runtime-activated-v1'
INDEX = 'a08aec2d8a28f6bb91251841b617be20820c23ab085e526d0dc107439b061c6e'
PRODUCER_SHA = '8851e255cb51ac3db02d25946854fef0c8d9e60fac5db7042e180c2b20b2af58'
PARENT_SHA = '577dbad5759ef06f075763c2a793ae278fddc15df8f4f61edc9a7d2de51ecb51'
RUNTIME_SHA = 'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78'
PINS_SHA = '182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb'
REVIEW_SHA = 'ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0'
checks = []
verified = {}

def sha(data): return hashlib.sha256(data).hexdigest()

def regular(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    key = str(path.resolve())
    identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    cached = verified.get(key)
    if cached and cached['identity'] == identity:
        digest = cached['sha256']
    else:
        digest = hashlib.sha256()
        with path.open('rb') as source:
            for block in iter(lambda: source.read(1024 * 1024), b''): digest.update(block)
        digest = digest.hexdigest()
        after = path.lstat()
        assert identity == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
        verified[key] = {'sha256': digest, 'bytes': before.st_size, 'identity': identity}
    if expected is not None: assert digest == expected, (str(path), digest, expected)
    if size is not None: assert before.st_size == size, str(path)
    return digest

def doc(path, expected=None):
    regular(path, expected)
    raw = Path(path).read_bytes()
    if expected is not None: assert sha(raw) == expected
    return json.loads(raw)

def text(path):
    regular(path)
    return Path(path).read_text()

def note(name, **data): checks.append({'name': name, 'passed': True, **data})

def indexed(root, expected, count):
    value = doc(root / 'index.json', expected)
    assert len(value['files']) == count
    seen = set()
    for row in value['files']:
        parts = Path(row['path']).parts
        assert parts and not Path(row['path']).is_absolute() and all(x not in ('', '.', '..') for x in parts)
        assert row['path'] not in seen; seen.add(row['path'])
        current = root
        for part in parts:
            current /= part
            assert not current.is_symlink(), str(current)
        regular(current, row['sha256'], row['bytes'])
    return value

def manifest(path, count):
    value = doc(path)
    assert len(value['inputs']) == count
    rows = {}
    for row in value['inputs']:
        target = Path(os.path.abspath(path.parent / row['path']))
        assert str(target) not in rows
        regular(target, row['sha256'], row['bytes'])
        rows[str(target)] = row
    return value, rows

def main():
    outer = indexed(OUT, INDEX, 83)
    producer = indexed(PRODUCER, PRODUCER_SHA, 124)
    parent = indexed(PARENT, PARENT_SHA, 82)
    runtime = indexed(RUNTIME, RUNTIME_SHA, 26)
    note('four exact indexed source families', generated=83, producer=124, predecessor=82, delegate=26)
    receipt = doc(OUT / 'source-receipt.json')
    assert receipt['runtimeAcceptanceClaim'] is False and receipt['nativePreflightOrGuestOrHostExecuted'] is False
    assert receipt['producerIndexSha256'] == PRODUCER_SHA and receipt['parentIndexSha256'] == PARENT_SHA
    assert receipt['runtimeIndexSha256'] == RUNTIME_SHA
    root, root_rows = manifest(OUT / 'input-freeze.json', 2293)
    cap, cap_rows = manifest(OUT / 'capability/input-freeze.json', 2292)
    assert regular(OUT / 'input-freeze.json') == receipt['inputFreezeSha256']
    assert regular(OUT / 'capability/input-freeze.json') == receipt['capabilityFreezeSha256']
    note('generated root and capability rows rehashed', root=2293, capability=2292)

    pins = doc(OUT / 'runtime-pins.json', PINS_SHA)
    review = doc(OUT / 'root-review-receipt.json', REVIEW_SHA)
    assert (OUT / 'runtime-pins.json').read_bytes() == (RUNTIME / 'runtime-pins.json').read_bytes()
    assert (OUT / 'root-review-receipt.json').read_bytes() == (RUNTIME / 'root-review-receipt.json').read_bytes()
    assert review['reviewedPinsSha256'] == PINS_SHA
    runtime_receipt = doc(RUNTIME / 'source-receipt.json')
    labels = ['normal-off', 'normal-runtime', 'gc-off', 'disabled-off']
    assert sorted(pins['variants']) == sorted(review['variants']) == sorted(labels)
    for label in labels:
        pin = pins['variants'][label]
        assert pin['state'] == 'reviewed-real-classic-trace-production-freeze'
        assert pin['sourceFiles'] == 342 and pin['runtimeAcceptanceClaim'] is False and pin['reviewRequired'] is False
        assert pin['sourceContractVersion'] == 'sm-classic-trace-source-v1'
        assert pin['classicStreamsEnabled'] == (label != 'disabled-off')
        for key in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']:
            assert pin[key] == review['variants'][label][key] == runtime_receipt['actualArtifacts'][label][key]
        for row in pin['frozenFiles']: regular(row['path'], row['sha256'], row['bytes'])
        regular(pin['enginePath'], pin['engineSha256'], pin['engineBytes'])
        metadata = doc(pin['enginePath'] + '.build.json', pin['receiptSha256'])
        frozen = doc(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
        assert len(metadata['sourceManifest']) == 342
        assert len(frozen['copies']) == 474
        assert metadata['gcStress'] == (label == 'gc-off') and metadata.get('diagnosticOnly') is not True
        for row in metadata['sourceManifest']:
            regular(Path(pin['sourceRoot']) / row['path'], row['sha256'])
            regular(STAGE / row['path'], row['sha256'])
    note('four actual native authority tuples and frozen inputs authenticate without executing admission', variants=4, frozenRowsPerVariant=474, sourceRows=342)

    delegated, delegated_rows = manifest(RUNTIME / 'input-freeze.json', 6414)
    assert len(delegated['toolTrees']) == 2 and len(delegated['toolLinks']) == 22
    for tree in delegated['toolTrees']:
        path = Path(tree['path'])
        assert str(path.resolve()) == tree['realPath']
        actual = []
        def walk(directory):
            for item in sorted(directory.iterdir(), key=lambda x: x.name):
                mode = item.lstat().st_mode
                kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file'
                assert kind != 'file' or stat.S_ISREG(mode)
                actual.append({'path': item.relative_to(path).as_posix(), 'kind': kind})
                if kind == 'directory': walk(item)
        walk(path)
        assert sorted(actual, key=lambda x: x['path']) == sorted(tree['entries'], key=lambda x: x['path'])
        for entry in actual:
            if entry['kind'] == 'file':
                target = str((path / entry['path']).absolute())
                assert target in delegated_rows, target
    for row in delegated['toolLinks']:
        path = Path(row['path']); assert path.is_symlink() and os.readlink(path) == row['linkText']
        assert str(path.resolve()) == row['resolvedTarget']
        if row['targetKind'] == 'file': regular(path.resolve(), row['targetSha256'], row['targetBytes'])
        else: assert path.resolve().is_dir()
    note('delegated whole native/tool seal independently rehashed and membership checked', files=6414, toolTrees=2, links=22)

    body_rows = doc(OUT / 'derivations.json')['records']
    assert len(body_rows) == 64 and len(receipt['bodyHashes']) == 64
    changed = []
    for row in body_rows:
        name = row['destinationPath']; raw = (OUT / name).read_bytes()
        assert sha(raw) == receipt['bodyHashes'][name]
        assert raw == (PRODUCER / 'payload' / name).read_bytes()
        if raw != (PARENT / name).read_bytes(): changed.append(name)
    assert set(changed) == {'common/runners/allocator-gc.mjs', 'release/helpers/native-scalar-harness.mjs'}
    transformations = doc(PRODUCER / 'body-transformations.json')['files']
    assert len(transformations) == 3
    for row in transformations:
        raw = Path(row['origin']).read_bytes(); regular(row['origin'], row['beforeSha256'])
        value = raw.decode()
        for edit in row['edits']:
            assert value.count(edit['old']) == edit['count']
            value = value.replace(edit['old'], edit['new'])
        proposed = (PRODUCER / row['path']).read_bytes()
        assert value.encode() == proposed and sha(proposed) == row['afterSha256']
        for edit in reversed(row['edits']):
            assert value.count(edit['new']) == edit['count']
            value = value.replace(edit['new'], edit['old'])
        assert value.encode() == raw
    for path in (PRODUCER / 'payload').rglob('*'):
        if path.is_file(): assert path.read_bytes() == (OUT / path.relative_to(PRODUCER / 'payload')).read_bytes()
    note('complete generated payloads exact with only two finite host guard changes', bodies=64, unchanged=62, completeReversibleDerivations=3)

    policy = doc(FAMILY / 'trace-integration-candidate-v1/policy.json')
    canonical = {row['path']: row['sha256'] for row in policy['expectedNativeSourceManifest']}
    tools = doc(FAMILY / 'trace-integration-candidate-v1/artifact-tools/tool-pins.json')
    canonical.update({row['path']: row['sha256'] for row in tools['toolDependencies']})
    mappings = doc(OUT / 'source-mappings.json')
    for section in ['root', 'capability']:
        assert len(mappings[section]) == 795
        for row in mappings[section]:
            regular(row['beforePath'], row['beforeSha256']); regular(row['afterPath'], row['afterSha256'])
            relative = Path(row['beforePath']).relative_to(REPO)
            assert Path(row['afterPath']) == STAGE / relative
            assert row['afterSha256'] == canonical.get(str(relative), row['beforeSha256'])
    for manifest_name, actual_rows, count in [('input-freeze.json', root_rows, 2055), ('capability/input-freeze.json', cap_rows, 2054)]:
        old = doc(PARENT / manifest_name); assert len(old['inputs']) == count
        for row in old['inputs']:
            original = Path(os.path.abspath((PARENT / manifest_name).parent / row['path']))
            if original.is_relative_to(PARENT):
                relative = original.relative_to(PARENT)
                if str(relative) == 'capability/input-freeze.json': continue
                if (PRODUCER / 'payload' / relative).is_file():
                    target = OUT / relative; digest = regular(target)
                else: target = original; digest = row['sha256']
            elif original.is_relative_to(REPO):
                relative = original.relative_to(REPO); target = STAGE / relative
                digest = canonical.get(str(relative), row['sha256'])
            else: target = original; digest = row['sha256']
            assert str(target) in actual_rows, str(target)
            assert actual_rows[str(target)]['sha256'] == digest
    note('all inherited consumed rows preserved at exact planned afterimages including actual fixtures and oracles', predecessorRoot=2055, predecessorCapability=2054, mappingRowsPerSeal=795)

    live = root['liveComputedInputs']; assert len(live) == 8 and live == cap['liveComputedInputs']
    for name in live:
        target = str(STAGE / name)
        assert target in root_rows and target in cap_rows
        assert (root_rows[target]['sha256'], root_rows[target]['bytes']) == (cap_rows[target]['sha256'], cap_rows[target]['bytes'])
    adapter = STAGE / live[-1]
    regular(adapter, '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0', 53512)
    wit_root = STAGE / 'host-apis/wasi-0.2.10/wit/deps'
    assert sorted(x.name for x in wit_root.iterdir()) == sorted(Path(x).parent.name for x in live[:7])
    for package in wit_root.iterdir():
        assert package.is_dir() and not package.is_symlink()
        assert [x.name for x in package.iterdir()] == ['package.wit']
    note('all eight actually reopened live inputs and seven exact WIT leaf directories sealed', live=8, adapterBytes=53512)

    rendered = text(OUT / 'native-preflight.template.mjs')
    values = {'AUTHORITY_SHA': regular(OUT / 'activation-reference.json'), 'INPUTS_SHA': regular(OUT / 'input-freeze.json'), 'RUNTIME_INDEX_SHA': RUNTIME_SHA, 'RUNTIME_ROOT': str(RUNTIME)}
    for key, value in values.items(): rendered = rendered.replace('@' + key + '@', value)
    assert rendered == text(OUT / 'native-preflight.mjs')
    native = rendered
    assert native.index('await indexedRuntime(),pins=await authority(index)') < native.index('await import(pathToFileURL')
    assert 'const nativeRecheck=native.recheck' in native
    assert 'regular(join(HERE,\'input-freeze.json\'),INPUTS_SHA),document=JSON.parse(raw)' in native
    assert 'await nativeRecheck();const index=await indexedRuntime();await authority(index);await ownSeal();' in native
    common = text(OUT / 'common/preflight.mjs')
    assert common.index('if(expectedSha256!==undefined)assert.equal(sha256,expectedSha256') < common.index('const document=JSON.parse(bytes)')
    assert 'expectedManifest=inputClosure.sha256' in common and 'privateRecheck=production.recheck' in common
    assert "await admission.recheck();await writeFile" in common
    note('four literal delegate parameters reconstruct exactly; hash-before-rows/import and privately captured rechecks retained')

    http_pin = doc(OUT / 'capability/http-component-pins.json')
    assert http_pin['component'] is None
    jobs = text(OUT / 'release/job-plan.mjs')
    for name in ['core', 'allocator', 'stream-web', 'optional', 'sync', 'runtime', 'late', 'callbacks']: assert name in jobs
    serial = text(OUT / 'release/run-release.mjs')
    assert 'assert.equal(jobs.length,8)' in serial and 'reusedResults:0,resumeSupported:false' in serial
    assert "if(entry.code!==0)" in serial and 'seal.consumedInputsRecheckedAfterRun,true' in serial
    assert 'report.modules.length,6' in serial
    capabilities = text(OUT / 'capability/capabilities.mjs')
    assert "wasi:random/random@0.2.10" in capabilities
    assert 'audit.clockDependency.typeOnly,true' in capabilities
    note('fresh serial eight/six-child contracts, interface audits and null later HTTP phase retained')

    # Final source index recheck; no reviewed code or action main is executed.
    indexed(OUT, INDEX, 83); indexed(PRODUCER, PRODUCER_SHA, 124); indexed(RUNTIME, RUNTIME_SHA, 26)
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_ACTUAL_GENERATED_TRACE_REPLAY_SOURCE_REVIEW_PASSED',
              'reviewedIndexSha256': INDEX, 'sourceFamilies': {'generated':83,'producer':124,'predecessor':82,'delegate':26},
              'sourceSeals': {'root':2293,'capability':2292,'delegatedRuntime':6414,'toolTrees':2,'toolLinks':22},
              'checks': checks, 'uniqueRegularPathsRehashed': len(verified),
              'totalUniqueLogicalBytesRead': sum(x['bytes'] for x in verified.values()),
              'noConcreteSourceBlockerFound': True,
              'executed': {'ownerCode':False,'ownerPreflight':False,'producerMain':False,'nodeWorkload':False,'bundle':False,'guest':False,'native':False,'targetHost':False},
              'scope': 'Read-only source/data/hash review only. No new runtime pass, acceptance, performance, queue reset, ALS, VM ownership isolation or request reuse claim.'}
    with (HERE / 'results.json').open('x') as output: json.dump(result, output, indent=2); output.write('\n')
    with (HERE / 'verified-paths.json').open('x') as output:
        json.dump({'schemaVersion':1,'files':[{'path':path,'sha256':row['sha256'],'bytes':row['bytes']} for path,row in sorted(verified.items())]}, output, indent=2); output.write('\n')
    print(json.dumps({'checks':len(checks),'uniquePaths':len(verified),'resultsSha256':regular(HERE/'results.json')}))

if __name__ == '__main__': main()
