"""Accepted342 source/hash/command/copy functions, with explicit output arguments only."""
import hashlib,json,os,re,shlex,shutil
from pathlib import Path

def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def checked(path, expected):
    path = Path(path)
    assert isinstance(expected, str) and re.fullmatch(r'[a-f0-9]{64}', expected)
    assert path.is_file() and not path.is_symlink(), path
    assert sha(path) == expected, path
    return path

def checked_below(root, relative, expected):
    root = Path(root)
    assert root.is_absolute() and not root.is_symlink() and root.is_dir()
    assert isinstance(relative, str) and '\0' not in relative and '\\' not in relative
    assert not Path(relative).is_absolute() and all(part not in ('', '.', '..') for part in relative.split('/'))
    path = root
    for part in relative.split('/'):
        path /= part
        assert not path.is_symlink(), path
    return checked(path, expected)

def capture_regular(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    checksum = digest(data)
    checked(path, checksum)
    return data, checksum

def manifest(rows, count):
    assert isinstance(rows, list) and len(rows) == count
    seen = set()
    for row in rows:
        assert set(row) == {'path', 'sha256'}
        name = row['path']
        assert isinstance(name, str) and name and '\0' not in name and '\\' not in name
        assert not Path(name).is_absolute() and all(p not in ('', '.', '..') for p in name.split('/'))
        assert name not in seen and re.fullmatch(r'[a-f0-9]{64}', row['sha256'])
        seen.add(name)
    return rows

def exact_release(words):
    assert [word for word in words if word.startswith('-O')]==['-O3'],'Exactly one Release optimization flag required'
    assert [word for word in words if word=='-DNDEBUG'or word.startswith('-DNDEBUG=')]==['-DNDEBUG'],'Exact NDEBUG definition required'
    assert '-UNDEBUG'not in words and '-UDEBUG'not in words and not any(word.startswith('-DDEBUG')for word in words)
    assert not any(word=='-DNODE_COMPAT_OOM_TESTING'or word.startswith('-DNODE_COMPAT_OOM_TESTING=')for word in words)
    assert '-UNODE_COMPAT_OOM_TESTING'not in words

def compile_command(command, runtime, source=None, classic=True, gc=False):
    args = shlex.split(command)
    assert args.count('-c') == 1 and '-fsyntax-only' not in args
    assert '-D' not in args and '-U' not in args, 'Need captured joined macro arguments'
    exact_release(args)
    for flag in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY'):
        definitions = [x for x in args if x == '-D' + flag or x.startswith('-D' + flag + '=')]
        assert definitions == ['-D' + flag + '=1'], flag
        assert '-U' + flag not in args, flag
    runtime_definitions = [x for x in args if x == '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY' or x.startswith('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=')]
    assert runtime_definitions == (['-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1'] if runtime else [])
    assert '-UNODE_COMPAT_ENTROPY_RUNTIME_ONLY' not in args
    if source is not None:
        assert args[args.index('-c') + 1].endswith('/' + source), 'Compiler input disagrees with recorded native source'
        for flag, enabled in (
                ('NODE_COMPAT_CLASSIC_STREAMS', classic and source.startswith('builtins/node-compat/')),
                ('NODE_COMPAT_STREAM_WEB', source.startswith('builtins/node-compat/')),
                ('NODE_COMPAT_GC_STRESS', gc and source.startswith('builtins/node-compat/'))):
            definitions = [x for x in args if x == '-D' + flag or x.startswith('-D' + flag + '=')]
            assert definitions == (['-D' + flag + '=1'] if enabled else []), flag
            assert '-U' + flag not in args, flag
    return args

def embedding_command(raw, source):
    selected = []
    for line in raw.decode('utf-8').splitlines():
        if ' -c ' not in line:
            continue
        args = shlex.split(line)
        if args.count('-c') == 1 and args[args.index('-c') + 1] == source:
            selected.append(line)
    assert len(selected) == 1, 'Need exactly one actual parent embedding compile command'
    return selected

def destination(path, output):
    assert path.is_absolute() and path == Path(os.path.abspath(path))
    assert path.is_relative_to(output)
    cursor = path
    while cursor != output.parent:
        assert not cursor.is_symlink(), cursor
        parent = cursor.parent
        assert parent != cursor
        cursor = parent

def validate_plan(plan, receipt, output):
    assert len({row['target'] for row in plan}) == len(plan)
    assert receipt not in {row['target'] for row in plan}
    destination(receipt, output)
    assert not receipt.exists() and not receipt.is_symlink(), 'Never overwrite a frozen receipt'
    for row in plan:
        destination(row['target'], output)
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])
        else:
            assert digest(row['data']) == row['sha256']
        if row['target'].exists():
            assert row['shared'], 'Never overwrite a frozen variant'
            checked(row['target'], row['sha256'])

def execute_plan(plan, output):
    for row in plan:
        space = os.statvfs(output)
        assert space.f_bavail * space.f_frsize >= 800 * 1024 * 1024, 'Freeze stops below the operational 800MiB floor'
        target = row['target']
        destination(target, output)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert row['shared']
            checked(target, row['sha256'])
        else:
            with target.open('xb') as result:
                os.fchmod(result.fileno(), 0o600)
                if row.get('original') is not None:
                    with row['original'].open('rb') as source:
                        shutil.copyfileobj(source, result, 1024 * 1024)
                else:
                    result.write(row['data'])
                result.flush()
                os.fsync(result.fileno())
            checked(target, row['sha256'])
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])
    for row in plan:
        checked(row['target'], row['sha256'])
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])
