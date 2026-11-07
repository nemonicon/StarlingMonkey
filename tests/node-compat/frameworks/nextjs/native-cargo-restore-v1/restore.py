#!/usr/bin/env python3
"""Python>=3.11; locked source restoration only. No network, subprocess or Cargo."""
import argparse
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tarfile
import tomllib

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def need(value, message):
    if not value:
        raise ValueError(message)


def rel(value):
    p = PurePosixPath(value)
    need(isinstance(value, str) and value not in ('', '.') and not p.is_absolute()
         and '..' not in p.parts and p.as_posix() == value, 'unsafe relative path: ' + str(value))
    return value


def physical(value, exists=True):
    p = Path(value)
    need(p.is_absolute() and '..' not in p.parts and p.resolve(strict=exists) == p,
         'canonical absolute path without aliases required: ' + str(value))
    return p


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(p):
    s = p.lstat()
    need(not stat.S_ISLNK(s.st_mode), 'symlink: ' + str(p))
    return dict(dev=s.st_dev, ino=s.st_ino, mode=stat.S_IMODE(s.st_mode),
                nlink=s.st_nlink, bytes=s.st_size, mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns)


def read_file(p, expected=None, limit=16 * 1024**2):
    p = physical(p)
    before = identity(p)
    need(p.is_file() and before['nlink'] == 1 and before['bytes'] <= limit, 'regular unaliased bounded file: ' + str(p))
    raw = p.read_bytes()
    need(identity(p) == before, 'input changed while reading: ' + str(p))
    row = dict(path=str(p), sha256=sha(raw), bytes=len(raw), physical=before)
    if expected is not None:
        need(all(row[k] == expected[k] for k in ('sha256', 'bytes')), 'input bytes: ' + str(p))
    return raw, row


def verify_family():
    index_raw, index_row = read_file(HERE / 'index.json')
    index = json.loads(index_raw)
    need(index['state'] == 'NATIVE_CARGO_RESTORE_SOURCE_ONLY_V1', 'family state')
    expected = {rel(r['path']): r for r in index['files']}
    need(len(expected) == len(index['files']), 'duplicate family member')
    need({p.name for p in HERE.iterdir()} == set(expected) | {'index.json'}, 'family membership')
    rows = [index_row]
    for name, row in expected.items():
        need('/' not in name, 'flat family required')
        rows.append(read_file(HERE / name, row)[1])
    return rows


def load_catalog():
    family = verify_family()
    manifest = json.loads((HERE / 'manifest.json').read_text())
    need(manifest['state'] == 'NATIVE_CARGO_LOCKED_SOURCE_RESTORE_PLAN_V1', 'manifest state')
    refs, docs = [], {}
    for name, row in manifest['sourceRecords'].items():
        raw, record = read_file(REPO / rel(row['path']), row)
        refs.append(record)
        if row['path'].endswith('.json'):
            docs[name] = json.loads(raw)
    index = {r['path']: r for r in docs['cargoIndex']['entries']}
    need(len(index) == len(docs['cargoIndex']['entries']), 'duplicate retained text member')
    bundle = REPO / manifest['sourceRecords']['cargoBundle']['path']
    text = {}
    with tarfile.open(bundle, 'r:gz') as archive:
        members = archive.getmembers()
        need(len(members) == len(index) and {r.name for r in members} == set(index), 'retained text membership')
        need(all(r.isfile() and r.size <= 2 * 1024**2 for r in members) and
             sum(r.size for r in members) <= 16 * 1024**2, 'retained text bounds')
        selected = set(manifest['bundleMembers'].values()) | {
            n for n in index if n.startswith('vendor-checksums/')}
        for name in selected:
            rel(name)
            raw = archive.extractfile(name).read()
            need(len(raw) == index[name]['bytes'] and sha(raw) == index[name]['sha256'], 'retained text hash')
            text[name] = raw
    lock_raw = text[manifest['bundleMembers']['lock']]
    need(sha(lock_raw) == manifest['lockSha256'] and len(lock_raw) == manifest['lockBytes'], 'exact final lock')
    packages = tomllib.loads(lock_raw.decode())['package']
    registry = [r for r in packages if r.get('source', '').startswith('registry+')]
    git = [r for r in packages if r.get('source', '').startswith('git+')]
    need(len(packages) == 84 and len(registry) == 75 and len(git) == 1 and
         git[0]['source'] == manifest['gitSource']['lockSource'], 'exact84 sources')
    recipes = manifest['registryArchives']
    need([(r['name'], r['version'], r['source'], r['sha256']) for r in recipes] ==
         [(r['name'], r['version'], r['source'], r['checksum']) for r in registry], 'exact75 archive pins')
    for r in recipes:
        need(r['fileName'] == r['name'] + '-' + r['version'] + '.crate' and
             r['url'] == 'https://static.crates.io/crates/' + r['name'] + '/' + r['fileName'], 'fixed archive recipe')
    vendor = [dict(path=r['path'], sha256=r['sha256'], bytes=r['bytes'], mode=r['mode'])
              for r in docs['vendorInventory']['entries'] if r['kind'] == 'file']
    vendor_dirs = {r['path']: r['mode'] for r in docs['vendorInventory']['entries'] if r['kind'] == 'directory'}
    by_path = {rel(r['path']): r for r in vendor}
    checksums, covered = {}, set()
    sources = {(p['name'] + '-' + p['version']): p for p in packages if p.get('source')}
    need(len(sources) == 76, 'unique full package identities')
    for directory, p in sources.items():
        name = 'vendor-checksums/' + directory + '.json'
        raw = text[name]
        sums = json.loads(raw)
        need(sums['package'] == p.get('checksum'), 'package checksum identity')
        checksum_path = directory + '/.cargo-checksum.json'
        need(by_path[checksum_path]['sha256'] == sha(raw) and by_path[checksum_path]['bytes'] == len(raw), 'exact checksum JSON')
        checksums[checksum_path] = raw
        covered.add(checksum_path)
        for path, digest in sums['files'].items():
            whole = directory + '/' + rel(path)
            need(by_path[whole]['sha256'] == digest, 'vendor ledger/checksum join')
            covered.add(whole)
    need(covered == set(by_path) and len(vendor) == 2354 and len(vendor_dirs) == 420 and
         sum(r['bytes'] for r in vendor) == 35731921, 'complete vendor ledger')
    ffi = [{k: r[k] for k in ('path', 'sha256', 'bytes')} for r in docs['ffiManifest']['files']]
    ffi_files = {r['path']: r for r in docs['ffiInventory']['entries'] if r['kind'] == 'file'}
    need(set(ffi_files) == {r['path'] for r in ffi} and all(
        all(ffi_files[r['path']][k] == r[k] for k in ('sha256', 'bytes')) for r in ffi), 'FFI ledger join')
    base = docs['baseManifest']['files']
    need(len(ffi) == 1127 and sum(r['bytes'] for r in ffi) == 11364714 and
         len(base) == 21 and sum(r['bytes'] for r in base) == 57188, 'source counts')
    need(manifest['actualCargoMetadata'] is None and manifest['actualNativeBuild'] is None and
         manifest['actualEngine'] is None and manifest['actualRuntime'] is None, 'unexecuted state')
    need(manifest['counts'] == dict(lockPackages=84, registryPackages=75, gitPackages=1, pathPackages=8,
         vendorFiles=2354, vendorSourceFiles=2278, vendorDirectories=420, vendorBytes=35731921,
         ffiFiles=1127, ffiBytes=11364714, baseFiles=21, baseBytes=57188, sourcePayloadBytes=47153823), 'honest source counts')
    need(sum(r['mode'] == 0o644 for r in vendor) == 2351 and
         sum(r['mode'] == 0o755 for r in vendor) == 3 and
         all(mode == 0o755 for mode in vendor_dirs.values()), 'exact vendor modes')
    c = dict(manifest=manifest, text=text, vendor=vendor, vendorDirs=vendor_dirs,
             ffi=ffi, ffiDirs={r['path']: 0o700 for r in docs['ffiInventory']['entries'] if r['kind'] == 'directory'},
             base=base, baseDirs={r: 0o700 for r in manifest['baseDirectories']}, checksums=checksums,
             protected=family + refs)
    # Validate project semantics before allowing any caller path rendering.
    render(c, Path('/source-only-example-not-created'))
    return c


def render(c, output):
    m = c['manifest']
    raw = c['text'][m['bundleMembers']['project']].decode()
    project = tomllib.loads(raw)
    need(list(project['dependencies']) == m['rootDependencies'] and project['workspace'] == {} and
         project['lib'] == {'crate-type': ['staticlib'], 'path': 'rust-staticlib.rs'} and
         project['dependencies']['icu_capi']['features'] == m['icuCapiFeatures'] and
         project['dependencies']['icu_capi']['default-features'] is False and
         project['dependencies']['multipart']['features'] == ['capi', 'simd'], 'one aggregate/root features')
    paths = dict(zip(m['rootDependencies'][:4], m['basePrefixes']))
    paths.update({'icu_capi': 'intl/icu_capi', 'unicode-bidi-ffi': 'intl/bidi/rust/unicode-bidi-ffi'})
    expected = copy.deepcopy(project)
    replacements = {}
    for name, row in expected['dependencies'].items():
        target = output / 'sources' / ('base' if name in m['rootDependencies'][:4] else 'firefox') / paths[name]
        replacements[row['path']] = str(target)
        row['path'] = str(target)
    for name in ('icu_capi', 'icu_segmenter_data'):
        row = expected['patch']['crates-io'][name]
        target = str(output / 'sources/firefox/intl' / name)
        replacements[row['path']] = target
        row['path'] = target
    need(project['patch']['crates-io']['unicode-bidi'] == {
        'git': 'https://github.com/servo/unicode-bidi', 'rev': 'ca612daf1c08c53abe07327cb3e6ef6e0a760f0c'}, 'Git patch unchanged')
    need(sum(raw.count(json.dumps(k)) for k in replacements) == 8, 'exact eight project path literals')
    for old, new in replacements.items():
        raw = raw.replace(json.dumps(old), json.dumps(new))
    need(tomllib.loads(raw) == expected, 'only project paths may change')
    config_raw = c['text'][m['bundleMembers']['offlineConfig']].decode()
    config = tomllib.loads(config_raw)
    expected_config = copy.deepcopy(config)
    old = config['source']['intl-vendor']['directory']
    expected_config['source']['intl-vendor']['directory'] = str(output / 'vendor')
    need(config_raw.count(json.dumps(old)) == 1, 'exact config path literal')
    config_raw = config_raw.replace(json.dumps(old), json.dumps(str(output / 'vendor')))
    need(tomllib.loads(config_raw) == expected_config, 'only config directory may change')
    return {'project/Cargo.toml': raw.encode(), 'project/Cargo.lock': c['text'][m['bundleMembers']['lock']],
            'project/rust-staticlib.rs': c['text'][m['bundleMembers']['lib']],
            'offline-cargo/config.toml': config_raw.encode()}


def tree(root, rows, directories, prefixes=None, exact_modes=False):
    root = physical(root)
    need(root.is_dir(), 'donor directory')
    expected = {rel(r['path']): r for r in rows}
    expected_dirs = set(directories)
    records, seen, seen_dirs = [], set(), set()
    if prefixes is not None:
        records.append(dict(path=str(root), kind='directory', physical=identity(root)))
    scope = list(prefixes) if prefixes is not None else ['']
    # Parent directories above selected prefixes are included when declared;
    # unrelated siblings outside the four selected crates are never traversed.
    for name in expected_dirs:
        if prefixes is not None and not any(name == p or name.startswith(p + '/') for p in prefixes):
            p = physical(root / name)
            need(p.is_dir(), 'declared source parent')
            records.append(dict(path=str(p), kind='directory', physical=identity(p)))
            seen_dirs.add(name)
    for prefix in scope:
        start = physical(root / prefix)
        todo = [start]
        while todo:
            p = todo.pop()
            name = p.relative_to(root).as_posix()
            if p.is_dir():
                if name != '.':
                    need(name in expected_dirs and name not in seen_dirs, 'unexpected/duplicate donor directory: ' + name)
                    if exact_modes:
                        need(identity(p)['mode'] == directories[name], 'donor directory mode')
                    seen_dirs.add(name)
                records.append(dict(path=str(p), kind='directory', physical=identity(p)))
                children = sorted(p.iterdir(), reverse=True)
                for child in children:
                    physical(child)
                todo.extend(children)
            else:
                need(name in expected and name not in seen, 'unexpected/duplicate donor file: ' + name)
                _, row = read_file(p, expected[name])
                if exact_modes:
                    need(row['physical']['mode'] == expected[name]['mode'], 'donor file mode')
                seen.add(name)
                records.append(dict(row, kind='file'))
    need(seen == set(expected) and seen_dirs == expected_dirs, 'donor membership')
    return sorted(records, key=lambda r: r['path'])


def archive_files(path, recipe, selected, policy, consume=None):
    raw, record = read_file(path, limit=policy['maximumArchiveBytes'])
    need(sha(raw) == recipe['sha256'], 'registry archive lock checksum')
    prefix = recipe['name'] + '-' + recipe['version']
    seen, required, excluded = set(), set(), []
    expanded = 0
    # No extract/extractall: only safe whitelisted regular bytes are passed to
    # a writer, after the complete published archive hash was checked.
    import io
    unpacked = bytearray()
    # Bound the gzip/TAR byte stream before tarfile parses PAX/long headers;
    # compressed size or regular-member sizes alone cannot bound that parser.
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        while True:
            block = stream.read(min(1024**2, policy['maximumArchiveExpandedBytes'] + 1 - len(unpacked)))
            if not block:
                break
            unpacked.extend(block)
            need(len(unpacked) <= policy['maximumArchiveExpandedBytes'], 'uncompressed TAR byte cap')
    with tarfile.open(fileobj=io.BytesIO(unpacked), mode='r:') as archive:
        for number, member in enumerate(archive, 1):
            need(number <= policy['maximumArchiveEntries'], 'archive entry cap')
            name = member.name.rstrip('/') if member.isdir() else member.name
            rel(name)
            need(name == prefix or name.startswith(prefix + '/'), 'archive root confinement')
            need(name != prefix or member.isdir(), 'archive root is a directory')
            need(name not in seen and name.casefold() not in {n.casefold() for n in seen}, 'archive duplicate/case alias')
            seen.add(name)
            need(member.isdir() or member.isfile(), 'archive links/specials forbidden')
            if member.isdir():
                continue
            need(0 <= member.size <= policy['maximumFileBytes'], 'archive file cap')
            expanded += member.size
            need(expanded <= policy['maximumArchiveExpandedBytes'], 'archive expanded cap')
            relative = name[len(prefix) + 1:]
            if relative not in selected:
                excluded.append(relative)
                continue
            expected = selected[relative]
            body = archive.extractfile(member).read()
            need(len(body) == expected['bytes'] and sha(body) == expected['sha256'], 'selected archive bytes')
            required.add(relative)
            if consume is not None:
                consume(prefix + '/' + relative, body, expected['mode'])
    need(required == set(selected), 'archive missing selected vendor files')
    return dict(input=record, expandedBytes=expanded, uncompressedTarBytes=len(unpacked), excludedSafeMembers=excluded,
                selectedFiles=len(required), archiveEntries=len(seen))


def donors(c, value):
    need(set(value) == {'baseRoot', 'ffiRoot', 'vendor'}, 'exact donor config keys')
    v = value['vendor']
    need(v.get('kind') in ('tree', 'archives') and set(v) == {'kind', 'root'}, 'explicit vendor tree or archive pool')
    m = c['manifest']
    roots = {k: physical(value[k]) for k in ('baseRoot', 'ffiRoot')}
    roots['vendor'] = physical(v['root'])
    records = tree(roots['baseRoot'], c['base'], c['baseDirs'], m['basePrefixes'])
    records += tree(roots['ffiRoot'], c['ffi'], c['ffiDirs'])
    archive_rows = []
    if v['kind'] == 'tree':
        records += tree(roots['vendor'], c['vendor'], c['vendorDirs'], exact_modes=True)
    else:
        need(roots['vendor'].is_dir(), 'archive pool directory')
        records.append(dict(path=str(roots['vendor']), kind='directory', physical=identity(roots['vendor'])))
        expanded = compressed = 0
        for recipe in m['registryArchives']:
            prefix = recipe['name'] + '-' + recipe['version'] + '/'
            selected = {r['path'][len(prefix):]: r for r in c['vendor']
                        if r['path'].startswith(prefix) and not r['path'].endswith('/.cargo-checksum.json')}
            report = archive_files(roots['vendor'] / recipe['fileName'], recipe, selected, m['policy'])
            archive_rows.append(report)
            records.append(report['input'])
            expanded += report['uncompressedTarBytes']
            compressed += report['input']['bytes']
            need(expanded <= m['policy']['maximumAllArchiveExpandedBytes'] and
                 compressed <= m['policy']['maximumAllArchiveBytes'], 'all-archive cap')
        # The mandatory FFI donor is the exact Mozilla Git-bidi vendor tree,
        # including its original checksum. Never generate replacement hashes.
        ffi = {r['path']: r for r in c['ffi']}
        for row in c['vendor']:
            if row['path'].startswith('unicode-bidi-0.3.15/'):
                key = 'third_party/rust/unicode-bidi/' + row['path'].split('/', 1)[1]
                need(all(ffi[key][k] == row[k] for k in ('bytes', 'sha256')), 'exact Mozilla bidi donor')
    return dict(value=value, roots=roots, records=records, archiveReports=archive_rows)


def guard_sources(records):
    for row in records:
        p = physical(row['path'])
        need(identity(p) == row['physical'], 'input identity/mode changed: ' + str(p))
        if row.get('kind') != 'directory':
            read_file(p, row)


def capacity(path, floor, samples):
    free = shutil.disk_usage(path).free
    samples.append(dict(freeBytes=free, requiredBytes=floor))
    need(free >= floor, 'source-only restoration disk floor')


def payload_layout(c, output):
    dirs = {'sources': 0o700, 'sources/base': 0o700, 'sources/firefox': 0o700,
            'vendor': 0o755, 'project': 0o700, 'offline-cargo': 0o700}
    dirs.update({'sources/base/' + p: 0o700 for p in c['baseDirs']})
    dirs.update({'sources/firefox/' + p: 0o700 for p in c['ffiDirs']})
    dirs.update({'vendor/' + p: mode for p, mode in c['vendorDirs'].items()})
    generated = render(c, output)
    rows = [dict(r, path='vendor/' + r['path']) for r in c['vendor']]
    rows += [dict(r, path='sources/base/' + r['path'], mode=0o600) for r in c['base']]
    rows += [dict(r, path='sources/firefox/' + r['path'], mode=0o600) for r in c['ffi']]
    rows += [dict(path=name, sha256=sha(raw), bytes=len(raw), mode=0o600) for name, raw in generated.items()]
    return dirs, rows, generated


def plain_descriptor(row):
    return {k: row[k] for k in ('path', 'sha256', 'bytes')}


def recorded_bookends(c, value):
    config_raw, config_row = read_file(value['inputConfig']['path'], value['inputConfig'])
    need(json.dumps(config_row, sort_keys=True) == json.dumps(value['inputConfig'], sort_keys=True), 'original config identity')
    admitted = donors(c, json.loads(config_raw))
    protected = c['protected'] + [config_row]
    recorded = value['sourceProtection']
    need(json.dumps(protected, sort_keys=True) == json.dumps(recorded['protectedMetadataRecords'], sort_keys=True),
         'complete original metadata/config bookends')
    need(json.dumps(admitted['records'], sort_keys=True) == json.dumps(recorded['donorPhysicalRecords'], sort_keys=True),
         'complete original donor bookends')
    return protected + admitted['records']


def admit_restore(receipt_ref):
    """Read-only current DATA admission; no claim of actual process/Cargo proof.

    The caller must separately bind any actual stage/process Root evidence.
    All output paths/physical rows are freshly observed, never retargeted old
    metadata. No producer or tool action is triggered by this function.
    """
    c = load_catalog()
    raw, receipt_row = read_file(receipt_ref['path'], receipt_ref)
    value = json.loads(raw)
    need(value['schemaVersion'] == 1 and value['state'] ==
         'LOCKED_CARGO_SOURCES_RESTORED_UNCHECKED_BY_CARGO_V1' and value['passed'] is True and
         value['sourceOnly'] is True and value['cargoOrCompilerOrNetworkOrGuestExecuted'] is False and
         value['error'] is None and value['finalProtectionError'] is None and
         value.get('publicationError') is None and value['sourceProtection']['unchanged'] is True,
         'successful source-only receipt required')
    need(all(value[k] is None for k in ('actualCargoMetadata', 'actualNativeBuild', 'actualEngine', 'actualRuntime')),
         'source receipt cannot claim Cargo/build/runtime')
    output = physical(value['outputRoot'])
    need(output / 'restore-result.json' == Path(receipt_ref['path']) and
         value['sourceIndex'] == plain_descriptor(c['protected'][0]), 'receipt producer/root binding')
    dirs, rows, generated = payload_layout(c, output)
    rows.append(dict(path='restore-result.json', sha256=sha(raw), bytes=len(raw), mode=0o600))
    current = tree(output, rows, dirs, exact_modes=True)
    fresh = [r for r in current if r['path'] not in (str(output), str(output / 'restore-result.json'))]
    need(json.dumps(fresh, sort_keys=True) == json.dumps(value['freshPhysicalRecords'], sort_keys=True),
         'fresh physical identity/mode/content records')
    root = next(r for r in current if r['path'] == str(output))
    need(root['physical']['mode'] == 0o700 and
         {k: root['physical'][k] for k in ('dev', 'ino', 'mode', 'nlink')} == value['ownedRootIdentity'], 'owned root identity')
    need(value['sourcePayloadFiles'] == 3502 and value['generatedFiles'] == 4 and
         value['lockSha256'] == c['manifest']['lockSha256'] and
         value['logicalPayloadBytes'] == sum(r['bytes'] for r in rows if r['path'] != 'restore-result.json') and
         sum(r['bytes'] for r in rows) <= c['manifest']['policy']['maximumAcceptedOutputBytes'], 'receipt counts/cap')
    original_bookends = recorded_bookends(c, value)
    current_files = {r['path']: r for r in current if r.get('kind') == 'file'}
    lock_descriptor = plain_descriptor(current_files[str(output / 'project/Cargo.lock')])
    config_descriptor = plain_descriptor(current_files[str(output / 'offline-cargo/config.toml')])
    # No file reads occur after this final bookend. Returned descriptors are
    # taken from the current payload rows already checked above.
    guard_sources(current + original_bookends + c['protected'] + [receipt_row])
    return dict(schemaVersion=1, state='RESTORED_CARGO_SOURCE_DATA_CONSISTENT_V1', dataConsistent=True,
                sourceIndex=value['sourceIndex'], receipt=plain_descriptor(receipt_row), root=str(output),
                intlLockfile=lock_descriptor, offlineCargoConfig=config_descriptor,
                baseRoot=str(output / 'sources/base'), firefoxRoot=str(output / 'sources/firefox'),
                vendorRoot=str(output / 'vendor'), physicalRecords=current,
                actualCargoMetadata=None, nativeBuildOrGuestExecutionProved=False,
                sourceProcessExecutionAttested=False)


def restore(c, config_path, output):
    output = physical(output, exists=False)
    need(not output.exists() and output.parent.is_dir() and not output.is_relative_to(REPO), 'fresh output outside repository')
    policy = c['manifest']['policy']
    samples = []
    capacity(output.parent, policy['minimumStartFreeBytes'], samples)
    config_raw, config_row = read_file(config_path)
    admitted = donors(c, json.loads(config_raw))
    need(all(not output.is_relative_to(p) and not p.is_relative_to(output)
             for p in admitted['roots'].values()), 'output/donor separation')
    capacity(output.parent, policy['minimumStartFreeBytes'], samples)
    protected = c['protected'] + [config_row]
    result = dict(schemaVersion=1, state='LOCKED_CARGO_SOURCES_RESTORING_V1', passed=False,
                  sourceOnly=True, cargoOrCompilerOrNetworkOrGuestExecuted=False,
                  actualCargoMetadata=None, actualNativeBuild=None, actualEngine=None, actualRuntime=None,
                  inputConfig=config_row, sourceProtection=None, error=None, finalProtectionError=None,
                  sourceIndex=plain_descriptor(c['protected'][0]),
                  diskSamples=samples, diskSamplesAreBoundaryOnly=True, outputRoot=str(output),
                  outputCapBytes=policy['maximumAcceptedOutputBytes'], archiveReports=admitted['archiveReports'])
    total = 0
    output.mkdir(mode=0o700)
    os.chmod(output, 0o700)

    def write(name, body, mode):
        nonlocal total
        rel(name)
        capacity(output, policy['minimumCopyBoundaryFreeBytes'], samples)
        total += len(body)
        need(total <= policy['maximumAcceptedOutputBytes'], 'accepted output logical cap')
        destination = output / name
        physical(destination.parent)
        fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, mode)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(body)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        need(destination.stat().st_nlink == 1, 'new file alias')
        capacity(output, policy['minimumCopyBoundaryFreeBytes'], samples)

    try:
        dirs, all_rows, generated = payload_layout(c, output)
        for name, mode in sorted(dirs.items(), key=lambda r: (r[0].count('/'), r[0])):
            (output / name).mkdir(mode=mode)
            os.chmod(output / name, mode)
        for kind, rows in [('base', c['base']), ('firefox', c['ffi'])]:
            root = admitted['roots']['baseRoot' if kind == 'base' else 'ffiRoot']
            for row in rows:
                write('sources/' + kind + '/' + row['path'], read_file(root / row['path'], row)[0], 0o600)
        if admitted['value']['vendor']['kind'] == 'tree':
            for row in c['vendor']:
                write('vendor/' + row['path'], read_file(admitted['roots']['vendor'] / row['path'], row)[0], row['mode'])
        else:
            for recipe in c['manifest']['registryArchives']:
                prefix = recipe['name'] + '-' + recipe['version'] + '/'
                selected = {r['path'][len(prefix):]: r for r in c['vendor']
                            if r['path'].startswith(prefix) and not r['path'].endswith('/.cargo-checksum.json')}
                archive_files(admitted['roots']['vendor'] / recipe['fileName'], recipe, selected, policy,
                              lambda name, raw, mode: write('vendor/' + name, raw, mode))
            for row in c['vendor']:
                if row['path'].endswith('/.cargo-checksum.json'):
                    write('vendor/' + row['path'], c['checksums'][row['path']], row['mode'])
                elif row['path'].startswith('unicode-bidi-0.3.15/'):
                    source = admitted['roots']['ffiRoot'] / 'third_party/rust/unicode-bidi' / row['path'].split('/', 1)[1]
                    write('vendor/' + row['path'], read_file(source, row)[0], row['mode'])
        for name, raw in generated.items():
            write(name, raw, 0o600)
        fresh = tree(output, all_rows, dirs, exact_modes=True)
        root_row = next(r for r in fresh if r['path'] == str(output))
        result['freshPhysicalRecords'] = [r for r in fresh if r['path'] != str(output)]
        result['ownedRootIdentity'] = {k: root_row['physical'][k] for k in ('dev', 'ino', 'mode', 'nlink')}
        result['payloadPhysicalRecordScope'] = '3506 payload files and all child directories; this receipt is excluded from its own inventory. Root timestamps change on receipt publication and are not claimed.'
        result['sourcePayloadFiles'] = 3502
        result['generatedFiles'] = 4
        result['lockSha256'] = sha(generated['project/Cargo.lock'])
        result['logicalPayloadBytes'] = total
        result['relocationOnlyNoCargoGraphProof'] = True
        result['state'] = 'LOCKED_CARGO_SOURCES_RESTORED_UNCHECKED_BY_CARGO_V1'
        result['passed'] = True
    except BaseException as error:
        result['error'] = dict(type=type(error).__name__, message=str(error))
        result['passed'] = False
    finally:
        try:
            guard_sources(protected + admitted['records'])
            # Re-enumeration detects additions/removals, not only changed old rows.
            after = donors(c, admitted['value'])
            need(after['records'] == admitted['records'], 'donor membership/identity changed')
            load_catalog()
            result['sourceProtection'] = dict(unchanged=True, donorPhysicalRecords=admitted['records'],
                                            protectedMetadataRecords=protected)
            capacity(output, policy['minimumCopyBoundaryFreeBytes'], samples)
        except BaseException as error:
            result['finalProtectionError'] = dict(type=type(error).__name__, message=str(error))
            result['passed'] = False
        if not result['passed']:
            result['state'] = 'LOCKED_CARGO_SOURCE_RESTORATION_FAILED_V1'
        # Receipt publication is metadata, outside the payload-copy sampling
        # loop. Its bytes still count toward the same accepted logical cap.
        # A caller must also retain the actual process exit; a receipt alone
        # never proves publication/fsync or later Cargo validation succeeded.
        encoded = (json.dumps(result, indent=2) + '\n').encode()
        try:
            need(total + len(encoded) <= policy['maximumAcceptedOutputBytes'], 'receipt/output logical cap')
            fd = os.open(output / 'restore-result.json', os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(encoded)
                stream.flush()
                os.fchmod(stream.fileno(), 0o600)
                os.fsync(stream.fileno())
        except BaseException as error:
            result['passed'] = False
            result['publicationError'] = dict(type=type(error).__name__, message=str(error))
            print(json.dumps(result))
            raise
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true', help='read-only default; metadata only')
    parser.add_argument('--donors', type=Path, help='explicit owned donor config, no implicit paths')
    parser.add_argument('--output', type=Path, help='exclusive fresh source-only restoration')
    args = parser.parse_args()
    need(not (args.plan and args.output), '--plan cannot create output')
    c = load_catalog()
    if args.output is None:
        need(args.donors is None, '--donors requires explicit --output; default never walks private donor roots')
        print(json.dumps(dict(state=c['manifest']['state'], sourceRestored=False,
                              counts=c['manifest']['counts'], policy=c['manifest']['policy'],
                              actualCargoMetadata=None, actualNativeBuild=None, actualEngine=None, actualRuntime=None), indent=2))
        return 0
    need(args.donors is not None, 'explicit donor config required')
    result = restore(c, args.donors, args.output)
    print(json.dumps({k: result[k] for k in ('state', 'passed', 'outputRoot', 'error', 'finalProtectionError',
                                           'actualCargoMetadata', 'actualNativeBuild', 'actualEngine', 'actualRuntime')}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
