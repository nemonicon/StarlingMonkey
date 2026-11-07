"""Acquire exact official Node22.14 archive and extract npm only; execute nothing."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import posixpath
import shutil
import stat
import tarfile
import time
import urllib.parse
import urllib.request

BASE = 'https://nodejs.org/download/release/v22.14.0/'
NAME = 'node-v22.14.0-darwin-arm64.tar.xz'
SHA = '4e845cb71b4e897289312743b2e31c405a8a48720655404d82a4dce23fc43527'
TOP = 'node-v22.14.0-darwin-arm64'
NPM = TOP + '/lib/node_modules/npm'
MIN_FREE = 1024**3
ARCHIVE_MAX = 64 * 1024**2
NPM_MAX = 64 * 1024**2
TOTAL_MAX = 128 * 1024**2


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(p, exists=True):
    p = Path(p)
    need(p.is_absolute() and '..' not in p.parts and not any(x.is_symlink() for x in (p, *p.parents)), 'Canonical real path required')
    need(p.resolve(strict=exists) == p, 'Path alias refused')
    return p


def descriptor(p):
    p = canonical(p)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024**2), b''):
            h.update(b)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=p.stat().st_size)


def identity(p):
    s = p.stat()
    return dict(dev=s.st_dev, ino=s.st_ino, nlink=s.st_nlink, mode=stat.S_IMODE(s.st_mode),
                bytes=s.st_size, mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns)


def save(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def free():
    n = shutil.disk_usage('/private/tmp').free
    need(n >= MIN_FREE, 'Below separate1GiB tool-acquisition floor')
    return n


def fetch(url, path, maximum):
    start = time.monotonic()
    request = urllib.request.Request(url, headers={'User-Agent': 'StarlingMonkey-pinned-tool-acquisition'})
    with urllib.request.urlopen(request, timeout=30) as response, path.open('xb') as output:
        actual = urllib.parse.urlsplit(response.geturl())
        need(actual.scheme == 'https' and actual.hostname == 'nodejs.org', 'Unapproved redirect')
        length = response.headers.get('Content-Length')
        if length:
            need(0 < int(length) <= maximum, 'HTTP length exceeds bound')
        size = 0
        while True:
            need(time.monotonic() - start < 180, 'Download operational budget exceeded')
            b = response.read(min(1024**2, maximum - size + 1))
            if not b:
                break
            size += len(b)
            need(size <= maximum, 'Download byte bound exceeded')
            output.write(b)
            free()
        need(not length or size == int(length), 'Incomplete HTTP entity')
        output.flush()
        os.fsync(output.fileno())
        return dict(requestedUrl=url, finalUrl=response.geturl(), status=response.status,
                    headers=dict(response.headers.items()), bytes=size)


def member_path(name):
    name = name.rstrip('/')
    need(name and '\\' not in name and '\0' not in name and not any(x in ('', '.', '..') for x in name.split('/')), 'Unsafe archive path')
    p = PurePosixPath(name)
    need(not p.is_absolute() and p.parts[0] == TOP, 'Unexpected archive prefix')
    return name


def extract_npm(archive, root):
    prefix = root / 'lib/node_modules/npm'
    selected, names, links = [], set(), []
    npm_bytes = 0
    node = None
    with tarfile.open(archive, 'r|xz') as tar:
        for item in tar:
            name = member_path(item.name)
            need(name not in names, 'Duplicate archive member')
            names.add(name)
            if name == TOP + '/bin/node':
                need(item.isfile() and item.size <= 128 * 1024**2 and node is None, 'Invalid official Node entry')
                h = hashlib.sha256()
                size = 0
                with tar.extractfile(item) as stream:
                    for b in iter(lambda: stream.read(1024**2), b''):
                        h.update(b)
                        size += len(b)
                need(size == item.size, 'Short Node stream')
                node = dict(archiveMember=name, sha256=h.hexdigest(), bytes=size, extracted=False)
            if name != NPM and not name.startswith(NPM + '/'):
                continue
            rel = name[len(NPM):].lstrip('/')
            path = prefix / rel
            mode = item.mode & 0o777
            need(item.mode == mode and not item.islnk(), 'Special modes/hardlinks refused')
            need(item.isdir() or item.isfile() or item.issym(), 'Unsupported npm member type')
            row = dict(path=rel or '.', archiveMember=name, mode=mode)
            if item.isdir():
                path.mkdir(mode=0o700, parents=True, exist_ok=True)
                row['kind'] = 'directory'
            elif item.isfile():
                need(0 <= item.size <= 8 * 1024**2, 'Oversized npm file')
                npm_bytes += item.size
                need(npm_bytes <= NPM_MAX, 'npm expansion bound')
                path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                canonical(path.parent)
                h = hashlib.sha256()
                size = 0
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
                with os.fdopen(fd, 'wb') as output, tar.extractfile(item) as stream:
                    for b in iter(lambda: stream.read(1024**2), b''):
                        size += len(b)
                        output.write(b)
                        h.update(b)
                    need(size == item.size, 'Short npm stream')
                    output.flush()
                    os.fchmod(output.fileno(), mode)
                    os.fsync(output.fileno())
                row.update(kind='file', sha256=h.hexdigest(), bytes=size)
            else:
                target = item.linkname
                need(target and not PurePosixPath(target).is_absolute() and '\\' not in target and '\0' not in target, 'Invalid npm link')
                normalized = posixpath.normpath(posixpath.join(posixpath.dirname(rel), target))
                need(normalized != '..' and not normalized.startswith('../'), 'Escaping npm link')
                links.append((path, target))
                row.update(kind='symlink', target=target)
            selected.append(row)
            need(len(selected) <= 20000, 'npm member count bound')
            if len(selected) % 128 == 0:
                free()
    need(node is not None and selected, 'Required archive members absent')
    for path, target in links:
        canonical(path.parent)
        path.symlink_to(target)
    for path, target in links:
        resolved = path.resolve(strict=True)
        need(prefix in resolved.parents and (resolved.is_file() or resolved.is_dir()), 'Link target not inside npm tree')
    for row in sorted(selected, key=lambda r: len(Path(r['path']).parts), reverse=True):
        if row['kind'] == 'directory':
            (prefix / row['path']).chmod(row['mode'])
    verify(prefix, selected)
    return prefix, selected, node, len(names)


def verify(prefix, rows):
    prefix = canonical(prefix)
    need({'.'} | {p.relative_to(prefix).as_posix() for p in prefix.rglob('*')} == {r['path'] for r in rows}, 'npm exact tree membership')
    for r in rows:
        p = prefix / r['path']
        s = p.lstat()
        if r['kind'] == 'symlink':
            need(p.is_symlink() and os.readlink(p) == r['target'] and prefix in p.resolve(strict=True).parents, 'npm link differs')
        else:
            canonical(p)
            need(stat.S_IMODE(s.st_mode) == r['mode'], 'npm mode differs')
            if r['kind'] == 'file':
                need(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'npm unique regular file')
                need({k: descriptor(p)[k] for k in ('sha256', 'bytes')} == {k: r[k] for k in ('sha256', 'bytes')}, 'npm file differs')
            else:
                need(p.is_dir(), 'npm directory differs')


def acquire(output, existing_node):
    output = canonical(output, exists=False)
    existing_node = canonical(existing_node)
    need(not output.exists() and output.parent.is_dir(), 'Fresh private output required')
    need(stat.S_ISREG(existing_node.lstat().st_mode) and existing_node.stat().st_nlink == 1, 'Existing unique Node required')
    before, node_identity = descriptor(existing_node), identity(existing_node)
    start_free = free()
    output.mkdir(mode=0o700)
    result = dict(schemaVersion=1, state='APP_NPM_TOOL_ACQUISITION_FAILED_PARTIAL_PRESERVED_V1', passed=False,
                  outputRoot=str(output), officialOrigin='https://nodejs.org', nodeOrNpmExecuted=False,
                  existingNode=before, existingNodeBeforeIdentity=node_identity, startFreeBytes=start_free,
                  publishedArchiveSha256=SHA, signatureVerified=False, signatureScope='Official HTTPS published SHASUMS comparison; no OpenPGP verification claimed')
    try:
        sums = output / 'SHASUMS256.txt'
        result['shasumsHttp'] = fetch(BASE + 'SHASUMS256.txt', sums, 64 * 1024)
        matches = [line.split() for line in sums.read_text().splitlines() if line.split()[1:] == [NAME]]
        need(matches == [[SHA, NAME]], 'Published exact archive SHA differs')
        archive = output / NAME
        result['archiveHttp'] = fetch(BASE + NAME, archive, ARCHIVE_MAX)
        archive_row = descriptor(archive)
        need(archive_row['sha256'] == SHA, 'Official archive checksum mismatch')
        prefix, rows, archive_node, total_members = extract_npm(archive, output)
        package = json.loads((prefix / 'package.json').read_text())
        need(package['name'] == 'npm' and package['version'] == '10.9.2', 'Wrong bundled npm version')
        need({k: archive_node[k] for k in ('sha256', 'bytes')} == {k: before[k] for k in ('sha256', 'bytes')}, 'Existing Node differs from official archive Node entry')
        inventory_path = output / 'npm-inventory.json'
        save(inventory_path, dict(schemaVersion=1, root=str(prefix), entries=rows))
        verify(prefix, rows)
        result.update(state='APP_NPM_TOOL_ACQUISITION_PASSED_UNEXECUTED_V1', passed=True,
                      shasums=descriptor(sums), archive=archive_row, npmRoot=str(prefix), npmVersion=package['version'],
                      npmEngines=package.get('engines'), npmCli=descriptor(prefix / 'bin/npm-cli.js'),
                      npmPackage=descriptor(prefix / 'package.json'), npmInventory=descriptor(inventory_path),
                      npmFiles=sum(r['kind'] == 'file' for r in rows), npmDirectories=sum(r['kind'] == 'directory' for r in rows),
                      npmSymlinks=sum(r['kind'] == 'symlink' for r in rows), npmBytes=sum(r.get('bytes', 0) for r in rows),
                      fullArchiveMembersRead=total_members, officialNodeMember=archive_node,
                      existingNodeMatchesOfficialArchive=True)
    except BaseException as error:
        result['error'] = dict(type=type(error).__name__, message=str(error))
    finally:
        result['endFreeBytes'] = shutil.disk_usage('/private/tmp').free
        result['endCapacityFloorPassed'] = result['endFreeBytes'] >= MIN_FREE
        try:
            result['existingNodeUnchanged'] = descriptor(existing_node) == before and identity(existing_node) == node_identity
        except BaseException as error:
            result['existingNodeUnchanged'] = False
            result['finalNodeCheckError'] = dict(type=type(error).__name__, message=str(error))
        result['privateRegularBytes'] = sum(p.stat().st_size for p in output.rglob('*') if p.is_file() and not p.is_symlink())
        result['passed'] = result['passed'] and result['existingNodeUnchanged'] and result['endCapacityFloorPassed'] and result['privateRegularBytes'] <= TOTAL_MAX
        if not result['passed']:
            result['state'] = 'APP_NPM_TOOL_ACQUISITION_FAILED_PARTIAL_PRESERVED_V1'
        save(output / 'result.json', result)
    return result


def main():
    os.umask(0o077)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path)
    p.add_argument('--existing-node', type=Path)
    args = p.parse_args()
    if not args.output:
        print(json.dumps(dict(sourceOnlyPlan=True, archiveUrl=BASE + NAME, publishedSha256=SHA,
                              npmOnly=True, nodeOrNpmExecutionAllowed=False), indent=2))
        return 0
    need(args.existing_node is not None, 'Explicit existing Node required')
    result = acquire(args.output, args.existing_node)
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
