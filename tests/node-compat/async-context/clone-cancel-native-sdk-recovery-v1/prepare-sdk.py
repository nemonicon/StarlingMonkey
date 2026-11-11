"""Root-owned exact selected SDK recovery; no compiler, network or old-tree writes."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tarfile

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('requires unoptimized Python -I -B before any input IO')

HERE = Path(__file__).resolve().parent
MAP = HERE / 'donor-map.json'
MAP_SHA256 = '15781d2edf76d69e69f19b11b2de2cc19b21db614a33b6847b948ef4e21b360b'
MAP_BYTES = 236077
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first')
OUTPUT = WORK / 'spidermonkey-selected-sdk'
INVENTORY = WORK / 'selected-sdk-inventory.json'
RECEIPT = WORK / 'sdk-materialization.json'
MAX_HEADER = 2 * 1024 * 1024
MAX_SDK = 1024 * 1024 * 1024
inputs = {}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def stamp(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def row(path, data):
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def safe_relative(value):
    need(isinstance(value, str), 'relative path must be text')
    p = PurePosixPath(value)
    need(value == p.as_posix() and not p.is_absolute() and p.parts and
         all(part not in ('', '.', '..') for part in p.parts), 'noncanonical relative path')
    return p


def verify_file(reference, read=False, limit=MAX_SDK):
    path = Path(reference['path'])
    need(path.is_absolute() and path.resolve(strict=True) == path, 'noncanonical input path')
    size = reference['bytes']
    need(type(size) is int and 0 <= size <= limit and
         isinstance(reference['sha256'], str) and len(reference['sha256']) == 64, 'invalid file descriptor')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size == size,
         'input kind/link/size mismatch: ' + str(path))
    digest = hashlib.sha256()
    chunks = []
    with path.open('rb') as stream:
        need(stamp(os.fstat(stream.fileno())) == stamp(before), 'input changed before open')
        remaining = size
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            need(bool(chunk), 'short input')
            digest.update(chunk)
            if read:
                chunks.append(chunk)
            remaining -= len(chunk)
        need(stream.read(1) == b'', 'input grew')
        need(stamp(os.fstat(stream.fileno())) == stamp(before), 'input changed during read')
    need(stamp(path.lstat()) == stamp(before) and digest.hexdigest() == reference['sha256'],
         'input hash/bookend mismatch: ' + str(path))
    previous = inputs.get(str(path))
    need(previous is None or previous == (reference, stamp(before)), 'conflicting input descriptor')
    inputs[str(path)] = (reference, stamp(before))
    return b''.join(chunks) if read else None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def document(reference, limit):
    data = verify_file(reference, read=True, limit=limit)
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(RuntimeError('nonfinite JSON')))


def header_archive(reference, prefix, expected_members=None):
    """Read bounded regular header bytes; turn confined hardlink aliases into byte references."""
    verify_file(reference)
    data, kinds, aliases = {}, {}, {}
    total = 0
    with tarfile.open(reference['path'], 'r|gz') as archive:
        for member in archive:
            need(len(kinds) < 2048, 'tar member limit')
            relative = safe_relative(member.name)
            if prefix:
                need(relative.parts[0] == prefix and len(relative.parts) > 1, 'tar namespace')
                name = '/'.join(relative.parts[1:])
            else:
                name = relative.as_posix()
            need(name not in kinds and member.size >= 0, 'duplicate/invalid tar member')
            total += member.size
            need(total <= MAX_SDK, 'tar aggregate declaration limit')
            if member.isdir():
                kinds[name] = 'directory'
            elif member.islnk():
                need(bool(prefix), 'unexpected retained-text hardlink')
                target = safe_relative(member.linkname)
                need(target.parts[0] == prefix and len(target.parts) > 1, 'tar hardlink namespace')
                aliases[name] = '/'.join(target.parts[1:])
                kinds[name] = 'hardlink'
            else:
                need(member.isfile(), 'tar special or symbolic link refused')
                kinds[name] = 'file'
                if prefix and name == 'libspidermonkey.a':
                    # This donor library is never copied, hashed as a selected library, or linked.
                    need(member.size == 538170426, 'unexpected donor library size')
                    continue
                need(member.size <= (MAX_HEADER if prefix else 4 * 1024 * 1024), 'tar file bound')
                selected = member.name in ('generated/js/src/js-confdefs.h', 'generated/config.status')
                if prefix or selected:
                    payload = archive.extractfile(member).read(member.size + 1)
                    need(len(payload) == member.size, 'short tar payload')
                    data[member.name] = payload
    if expected_members is not None:
        need(len(kinds) == expected_members, 'tar membership count')
    for name, target in aliases.items():
        need(kinds.get(target) == 'file' and prefix + '/' + target in data,
             'hardlink must name a regular header in the same archive')
    return data


def preflight():
    need(len(sys.argv) == 1, 'fixed no-argument recovery entry')
    need(WORK.is_dir() and WORK.resolve() == WORK, 'fresh recovery parent absent/noncanonical')
    for path in (OUTPUT, INVENTORY, RECEIPT):
        need(not path.exists() and not path.is_symlink(), 'refuse existing output: ' + str(path))
    spec = document(dict(path=str(MAP), sha256=MAP_SHA256, bytes=MAP_BYTES), 512 * 1024)
    need(spec['state'] == 'SELECTED_SPIDERMONKEY_SDK_EXACT_DONOR_MAP_V1' and
         spec['outputRoot'] == str(OUTPUT), 'map state/output')
    historical = document(spec['historicalInventory'], 256 * 1024)
    entries = spec['entries']
    need(len(entries) == len(historical['entries']) == 609, 'whole selected entry count')
    old = {r['path']: r for r in historical['entries']}
    need(len(old) == 609 and len({r['path'] for r in entries}) == 609, 'entry uniqueness')
    need(sum(r.get('bytes', 0) for r in entries) == 646760937 and
         sum(r['kind'] == 'file' for r in entries) == 596 and
         sum(r['kind'] == 'directory' for r in entries) == 13, 'SDK count/byte declarations')
    base = header_archive(spec['baseArchive'], spec['archivePrefix'], 363)
    archives = {}
    resolved = {}
    unresolved = []
    for entry in entries:
        relative = safe_relative(entry['path'])
        keys = ('path', 'kind', 'mode') if entry['kind'] == 'directory' else ('path', 'kind', 'mode', 'bytes', 'sha256')
        need(entry['kind'] in ('file', 'directory') and
             all(entry[key] == old[entry['path']][key] for key in keys), 'historical content-map join')
        resolution = entry['resolution']
        if entry['kind'] == 'directory':
            need(resolution == dict(kind='create-directory'), 'directory resolution')
            continue
        kind = resolution['kind']
        try:
            if kind in ('selected-existing', 'additional-exact-file', 'retained-exact-file'):
                reference = resolution.get('source') or dict(path=resolution['path'], bytes=entry['bytes'], sha256=entry['sha256'])
                need(reference['bytes'] == entry['bytes'] and reference['sha256'] == entry['sha256'], 'file map descriptor join')
                if kind == 'selected-existing':
                    need(Path(reference['path']) == Path(spec['selectedOriginalRoot']) / relative, 'selected source path')
                if kind == 'additional-exact-file':
                    need(Path(reference['path']) == Path(spec['additionalExactRoot']) / relative and
                         entry['path'].startswith(('include/unicode/', 'include/mozilla/intl/')), 'additional header path')
                verify_file(reference)
                resolved[entry['path']] = ('file', reference)
                continue
            if kind == 'exact-base-tar-member':
                need(entry['path'] not in ('libspidermonkey.a', 'include/js-config.h', 'include/js-confdefs.h', 'include/js/SavedFrameAPI.h'), 'protected selected file cannot use vanilla donor')
                payload = base[resolution['member']]
            elif kind == 'retained-tar-member':
                ref = resolution['archive']
                key = ref['path']
                if key not in archives:
                    archives[key] = header_archive(ref, None)
                payload = archives[key][resolution['member']]
            elif kind == 'exact-config-template-recovery':
                need(entry['path'] == 'include/js-config.h', 'only selected config template recovery')
                ref = resolution['configuredValueProofArchive']
                key = ref['path']
                if key not in archives:
                    archives[key] = header_archive(ref, None)
                proof = archives[key][resolution['configuredValueProofMember']]
                need(len(proof) == resolution['configuredValueProofBytes'] and
                     hashlib.sha256(proof).hexdigest() == resolution['configuredValueProofSha256'] and
                     resolution['configuredValueProofLiteral'].encode() in proof, 'recorded actual Intl definition proof')
                template = base[resolution['member']]
                before, after = resolution['replaceBefore'].encode(), resolution['replaceAfter'].encode()
                need(before == b'/* #undef JS_HAS_INTL_API */' and after == b'#define JS_HAS_INTL_API 1' and
                     template.count(before) == resolution['requiredOccurrences'] == 1, 'exact configured template operation')
                payload = template.replace(before, after)
            else:
                raise RuntimeError('unknown SDK resolution')
            need(len(payload) == entry['bytes'] and hashlib.sha256(payload).hexdigest() == entry['sha256'], 'resolved header bytes mismatch')
            resolved[entry['path']] = ('bytes', payload)
        except (OSError, KeyError, RuntimeError) as error:
            unresolved.append(dict(path=entry['path'], errorType=type(error).__name__, message=str(error)))
    need(not unresolved, 'unresolved selected SDK inputs BEFORE OUTPUT: ' + json.dumps(unresolved, separators=(',', ':')))
    need(len(resolved) == 596, 'resolved whole SDK file count')
    for path, (_, expected) in inputs.items():
        need(stamp(Path(path).lstat()) == expected, 'preflight final bookend: ' + path)
    return spec, entries, resolved


def write_exclusive(path, payload, mode):
    with path.open('xb') as stream:
        os.fchmod(stream.fileno(), mode)
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def materialize(spec, entries, resolved):
    # This is the first output operation; preflight has resolved every required byte.
    OUTPUT.mkdir(mode=0o700)
    for entry in sorted((r for r in entries if r['kind'] == 'directory'), key=lambda r: (len(PurePosixPath(r['path']).parts), r['path'])):
        (OUTPUT / entry['path']).mkdir(mode=entry['mode'])
        os.chmod(OUTPUT / entry['path'], entry['mode'])
    for entry in (r for r in entries if r['kind'] == 'file'):
        kind, source = resolved[entry['path']]
        target = OUTPUT / entry['path']
        if kind == 'bytes':
            write_exclusive(target, source, entry['mode'])
        else:
            original = Path(source['path'])
            expected = inputs[str(original)][1]
            need(stamp(original.lstat()) == expected, 'source changed before copy')
            digest = hashlib.sha256()
            with original.open('rb') as incoming, target.open('xb') as outgoing:
                need(stamp(os.fstat(incoming.fileno())) == expected, 'copy source replaced')
                os.fchmod(outgoing.fileno(), entry['mode'])
                remaining = entry['bytes']
                while remaining:
                    chunk = incoming.read(min(1024 * 1024, remaining))
                    need(bool(chunk), 'copy source short')
                    digest.update(chunk)
                    outgoing.write(chunk)
                    remaining -= len(chunk)
                need(incoming.read(1) == b'' and digest.hexdigest() == entry['sha256'], 'copy source size/hash')
                outgoing.flush()
                os.fsync(outgoing.fileno())
                need(stamp(os.fstat(incoming.fileno())) == expected, 'source changed during copy')
    physical = []
    for path in sorted(OUTPUT.rglob('*')):
        state = path.lstat()
        relative = path.relative_to(OUTPUT).as_posix()
        entry = dict(path=relative, mode=stat.S_IMODE(state.st_mode), dev=state.st_dev,
                     ino=state.st_ino, nlink=state.st_nlink, mtimeNs=state.st_mtime_ns)
        if stat.S_ISDIR(state.st_mode):
            entry['kind'] = 'directory'
        else:
            need(stat.S_ISREG(state.st_mode) and state.st_nlink == 1, 'output special/link refused')
            entry.update(kind='file', bytes=state.st_size)
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            need(stamp(path.lstat()) == stamp(state), 'output readback changed')
            entry['sha256'] = digest.hexdigest()
        physical.append(entry)
    content_keys = ('path', 'kind', 'mode', 'bytes', 'sha256')
    project = lambda records: sorted([{k: r[k] for k in content_keys if k in r} for r in records], key=lambda r: r['path'])
    need(project(physical) == project(entries), 'complete output membership/content mismatch')
    need(len({r['ino'] for r in physical if r['kind'] == 'file'}) == 596, 'output unique file inodes')
    for path, (_, expected) in inputs.items():
        need(stamp(Path(path).lstat()) == expected, 'final input bookend: ' + path)
    root = OUTPUT.stat()
    inventory = dict(root=str(OUTPUT), rootIdentity=dict(mode=stat.S_IMODE(root.st_mode), dev=root.st_dev,
        ino=root.st_ino, nlink=root.st_nlink, mtimeNs=root.st_mtime_ns), entries=physical)
    inventory_bytes = (json.dumps(inventory, indent=2) + '\n').encode()
    write_exclusive(INVENTORY, inventory_bytes, 0o600)
    receipt = dict(schemaVersion=1, state='EXACT_SELECTED_SPIDERMONKEY_SDK_RECOVERED_DATA_V1',
        passed=True, inventory=row(INVENTORY, inventory_bytes), donorMap=dict(path=str(MAP), sha256=MAP_SHA256, bytes=MAP_BYTES),
        root=str(OUTPUT), files=596, directories=13, bytes=646760937,
        allHistoricalContentAndModesMatched=True, selectedLibraryPreserved=True,
        selectedConfigsRecoveredExactly=True, vanillaLibrarySelected=False,
        newCIBuildAttestationClaimed=False, originalPathsWritten=False,
        sourceInputs=[reference for reference, _ in inputs.values()],
        nativeEngineBuilt=False, engineExecuted=False, guestExecuted=False)
    payload = (json.dumps(receipt, indent=2) + '\n').encode()
    write_exclusive(RECEIPT, payload, 0o600)
    print(json.dumps(dict(receipt=row(RECEIPT, payload), passed=True)), flush=True)


if __name__ == '__main__':
    materialize(*preflight())
