"""New secret normal-OFF helpers in ORIGINAL tooling context; explicit source/output roles."""
import hashlib,json,os,re,shlex,shutil
from pathlib import Path
if not __debug__:raise RuntimeError('Source checks require assertions')
HERE=Path(__file__).resolve().parent
CONTRACT=json.loads((HERE.parent/'source-contract.json').read_bytes())
assert str(HERE.parent)==CONTRACT['originalToolingRoot']
REPO=Path(CONTRACT['configuredSourceRoot'])
OUTPUT=Path(CONTRACT['freezeRoot'])
RECIPE=CONTRACT['recipe']['sha256']
POLICY=CONTRACT['policy']['sha256']
HELPER=CONTRACT['helper']['sha256']
EMBEDDING='9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205'
ADAPTER='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
LABELS=('normal-off',)
TOOL_PINS_SHA='523f4105a07e375d894a0d07112208b4d5a87ade49a8e2c492e95101352ae237'
SOURCE_POLICY=json.loads(Path(CONTRACT['policy']['path']).read_bytes())
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

def compile_command(command, runtime, source=None, classic=True, gc=False, zlib=True, consumers=True):
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
                ('NODE_COMPAT_STREAM_CONSUMERS', consumers and source.startswith('builtins/node-compat/')),
                ('NODE_COMPAT_ZLIB', zlib and source.startswith('builtins/node-compat/')),
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

def destination(path, output=OUTPUT):
    assert path.is_absolute() and path == Path(os.path.abspath(path))
    assert path.is_relative_to(output)
    cursor = path
    while cursor != output.parent:
        assert not cursor.is_symlink(), cursor
        parent = cursor.parent
        assert parent != cursor
        cursor = parent

def validate_plan(plan, receipt, output=OUTPUT):
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

def execute_plan(plan, output=OUTPUT):
    for row in plan:
        target = row['target']
        destination(target, output)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert row['shared']
            checked(target, row['sha256'])
        else:
            with target.open('xb') as result:
                if row.get('original') is not None:
                    with row['original'].open('rb') as source:
                        shutil.copyfileobj(source, result, 1024 * 1024)
                else:
                    result.write(row['data'])
            checked(target, row['sha256'])
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])
    for row in plan:
        checked(row['target'], row['sha256'])
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])

def classify(metadata,label):
    assert label=='normal-off' and label in LABELS
    assert metadata.get('diagnosticOnly',False)is False and 'internalTickDiagnosticPolicy'not in metadata
    assert metadata.get('syntheticMetadataOnly',False)is False
    assert metadata['buildRecipeSha256']==RECIPE
    assert metadata['sourceManifest']==SOURCE_POLICY['expectedNativeSourceManifest']and len(metadata['sourceManifest'])==355
    assert metadata['cryptoSecretFailureSourcePolicy']==SOURCE_POLICY['cryptoSecretFailureSourcePolicy']
    assert metadata['cryptoKeyOwnershipPolicy']==SOURCE_POLICY['cryptoKeyOwnershipSourcePolicy']
    assert metadata['classicTraceSourcePolicy']==SOURCE_POLICY['classicTraceSourcePolicy']
    for key in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled']:assert metadata[key]is True
    for key in ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled']:assert metadata[key]is False
    assert metadata['entropyPolicy']=='off'
    assert metadata['cryptoSecretFailureBuildEvidence']['currentSourceManifestValidated']is True
    assert metadata['cryptoSecretFailureBuildEvidence']['runtimeValidation']is None
    return False,'off'

def tool_dependencies(repo=REPO):
    assert Path(repo)==REPO
    pins=json.loads(checked(HERE/'tool-pins.json',TOOL_PINS_SHA).read_bytes())
    assert pins['configuredSourceRoot']==str(REPO) and pins['recipeSha256']==RECIPE and pins['sourcePolicySha256']==POLICY and pins['sourceHelperSha256']==HELPER
    rows=pins['toolDependencies'];assert len(rows)==len({r['path']for r in rows})==1424
    for r in rows:
        path=checked_below(REPO,r['path'],r['sha256']);assert path.stat().st_size==r['bytes']
    return rows
