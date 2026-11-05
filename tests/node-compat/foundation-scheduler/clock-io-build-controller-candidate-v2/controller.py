"""Dormant fresh tool build: authenticated copies, private vendor cache, owned tools.

No adapter publication/pruning or application engine/component execution.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import urllib.request
import urllib.error

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PROPOSAL = HERE.parent / 'clock-io-pruning-candidate-v1'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
SOURCE = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-source')
WORK = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build')
PACKAGE = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-package')
EXTERNAL = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build-v2-external-root')
SOURCE_SHA = '55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f'
FLOOR = 800 * 1024 * 1024
ORIGINAL = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/clock-io-build-controller-candidate-v2')
MAX_CRATE_BYTES = 128 * 1024 * 1024
MAX_VENDOR_BYTES = 512 * 1024 * 1024
UNIT_FILTERS = (
    'adapter_input_guard_refuses_unknown_payloads_before_parse',
    'pure_and_clock_only_keep_distinct_capabilities',
    'stream_profiles_keep_poll_and_stream_transport',
    'explicitly_selected_world_io_is_retained',
)


def need(value, message):
    if not value:
        raise ValueError(message)


def row(path):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts and not path.is_symlink(), 'ordinary absolute file')
    before = path.stat()
    need(stat.S_ISREG(before.st_mode), 'regular input')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(data)
    after = path.stat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    need(identity(before) == identity(after), 'stable input')
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=after.st_size)


def verify(value):
    need(type(value) is dict and set(value) == {'path', 'sha256', 'bytes'}, 'exact descriptor')
    need(type(value['bytes']) is int and 0 <= value['bytes'] <= 2**40
         and type(value['sha256']) is str and re.fullmatch('[a-f0-9]{64}', value['sha256']) is not None, 'descriptor primitives')
    need(row(value['path']) == value, 'exact current bytes')
    return Path(value['path'])


def read(value):
    need(value['bytes'] <= 32 * 1024 * 1024, 'bounded JSON DATA')
    return json.loads(verify(value).read_bytes())


def family(value):
    index = read(value)
    need(index['schemaVersion'] == 1 and type(index['files']) is list and 0 < len(index['files']) <= 4096, 'finite family')
    base = Path(value['path']).parent
    names = {'index.json'}
    result = [value]
    for item in index['files']:
        name = local(item['path'])
        need(name not in names, 'unique member')
        names.add(name)
        descriptor = dict(item, path=str(base / name))
        verify(descriptor)
        result.append(descriptor)
    need(not any(p.is_symlink() for p in base.rglob('*')), 'no family symlinks')
    need({str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()} == names, 'exact family')
    return result


def local(value):
    need(type(value) is str and value and not value.startswith('/') and '\\' not in value
         and '\0' not in value and all(p not in ('', '.', '..') for p in value.split('/')), 'local member')
    return value


def phase_model(root):
    need(root['schemaVersion'] == 1 and root['state'] == 'ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V2', 'issued Root build')
    need(root['phase'] == 'build-clock-io-tools' and root['sourceIndex']['sha256'] == SOURCE_SHA, 'exact phase/source')
    need(root['sourceRoot'] == str(SOURCE) and root['workRoot'] == str(WORK)
         and root['packageRoot'] == str(PACKAGE) and root['externalRoot'] == str(EXTERNAL), 'fresh exact roots')
    for name in ('stageAllowed', 'privateVendorAllowed', 'downloadThreeLockedArchivesAllowed', 'rustBuildAndUnitTestsAllowed', 'jcoToolPackagingAllowed', 'prunerRefusalUnitTestAllowed'):
        need(root[name] is True, 'explicit phase operation '+name)
    for name in ('adapterPublicationAllowed', 'adapterPruningAllowed', 'validAdapterPruningAllowed', 'nativeEngineBuildAllowed', 'applicationComponentAllowed',
                 'applicationGuestAllowed', 'keyOrCryptoAllowed', 'timingAllowed', 'sourcePromotionAllowed', 'operationalAdmission', 'runtimeAcceptanceClaim'):
        need(root[name] is False, 'no additional action '+name)
    need(root['deadlineSeconds'] == 7200 and root['cargoJobs'] == 1 and root['requiredStartFreeBytes'] == 2 * 1024**3, 'bounded resources')
    need(root['minimumBoundaryFreeBytes'] == FLOOR and root['diskFloorPolicy'] == 'BEFORE_AFTER_COMMANDS_AND_STAGE_BOUNDARIES_ONLY', 'explicit boundary-only disk policy')
    need(root['diskFloorMonitoredDuringCommand'] is False and root['expectedCommandCount'] == 8, 'no continuous disk claim')
    need(root['declaredToolRootMetadataDestination']=='.toolchain-metadata','explicit original tool-root metadata role')


def authorize(config_descriptor):
    need(__debug__ and sys.dont_write_bytecode and sys.flags.isolated, 'isolated assertions')
    need(HERE == ORIGINAL and REPO == Path('/Users/dan/dev/StarlingMonkey'), 'actual original controller context')
    need(not any(os.environ.get(name) for name in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'NODE_OPTIONS', 'NODE_PATH',
         'LD_PRELOAD', 'LD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER',
         'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'NAPI_RS_NATIVE_LIBRARY_PATH', 'NAPI_RS_FORCE_WASI',
         'NAPI_RS_WASI_FLAVOR', 'NAPI_RS_ENFORCE_VERSION_CHECK')), 'no inherited loader/compiler overrides')
    captured = {}
    identities = {}
    families = []
    def capture(value):
        path=verify(value);s=path.stat();identity=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(path.resolve()))
        if value['path'] in captured:
            need(captured[value['path']] == value, 'consistent descriptor')
            need(identities[value['path']]==identity,'same captured physical identity')
        captured[value['path']] = value
        identities[value['path']]=identity
    def capture_family(value):
        entries = family(value)
        for entry in entries:
            capture(entry)
        families.append(value)
        return entries
    capture(config_descriptor);config = read(config_descriptor)
    need(config['schemaVersion']==1 and config['state']=='CLOCK_IO_BUILD_CONTROLLER_CONFIG_V2','new explicit controller config')
    own = config['controllerIndex']
    need(own['path'] == str(HERE / 'index.json'), 'own original context')
    capture_family(own)
    # The own family authenticates this finite manifest; its rows deliberately
    # exclude this manifest/index, avoiding a descriptor cycle. Every external
    # input is captured before any custom import or operation and rechecked.
    fixed = read(row(HERE / 'references.json'))
    capture_family(fixed['predecessorIndex'])
    capture_family(fixed['redirectHoldIndex'])
    capture_family(fixed['sourceReviewData']['index'])
    declared = read(row(HERE / 'source-inputs.json'))
    need(declared['schemaVersion'] == 1 and type(declared['files']) is list
         and 5606 <= len(declared['files']) <= 8192, 'finite complete own Source inputs')
    for entry in declared['files']:
        capture(entry)
    root = read(config['rootAuthority'])
    capture(config['rootAuthority'])
    phase_model(root)
    need(root['controllerIndex'] == own and root['controllerEntry'] == row(Path(__file__).resolve()), 'actual caller bytes')
    need(root['sourceReview'] == fixed['sourceReviewData'], 'exact already-reviewed proposal Source peer')
    source = root['sourceIndex']
    need(source['path'] == str(PROPOSAL / 'index.json'), 'genuine Source context')
    capture_family(source)
    for name, state, key in (
        ('sourceReview', 'INDEPENDENT_SCHEDULER_CLOCK_IO_PRUNING_SOURCE_REVIEW_PASSED_V1', 'sourceIndexSha256'),
        ('controllerReview', 'INDEPENDENT_CLOCK_IO_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V2', 'controllerSourceIndexSha256')):
        pair = root[name]
        entries = capture_family(pair['index'])
        need(pair['result'] in entries, 'peer result indexed in its authenticated family')
        proof = read(pair['result'])
        capture(pair['result'])
        need(proof['schemaVersion'] == 1 and proof['state'] == state and proof['sourceOnly'] is proof['sourceReviewPassed'] is True, 'separate Source peer')
        need(proof[key] == (source['sha256'] if name == 'sourceReview' else own['sha256']), 'exact peer subject')
        need(proof['ownerActionsInvoked'] is False, 'review action-free')
    inputs = read(row(PROPOSAL / 'source-inputs.json'))
    for entry in inputs['files']:
        capture(entry)
    monitor_index = row(MONITOR / 'index.json')
    need(monitor_index['sha256'] == '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b', 'genuine monitor source')
    capture_family(monitor_index)
    context = read(row(HERE / 'host-context.json'))
    for name in ('sdkSettings', 'hostLinkerDriver', 'appleLinker', 'wasmLinker', 'xcodeVersionPlist', 'python'):
        capture(context[name])
    settings = read(context['sdkSettings'])
    need(settings['Version'] == context['sdkVersion'] == '27.0' and settings['CanonicalName'] == context['sdkCanonicalName'], 'selected SDK')
    need(str(Path(sys.executable).resolve())==context['python']['path'],'pinned actual source-controller interpreter')
    frame = dict(config=config, root=root, captured=captured, identities=identities, families=families, context=context,
                 tools=read(row(PROPOSAL / 'tool-cut-references.json')),
                 cut=read(row(PROPOSAL / 'source-cut.json')), plan=read(row(PROPOSAL / 'future-build-plan.json')))
    materialization_plan(frame)
    command_plan(frame)
    for r in frame['cut']['baseline']['files']:
        need(stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode'],'captured original source mode')
    for r in frame['tools']['jsToolchain']['files']:
        need(stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode'],'captured original JS mode')
    recheck(frame)
    return frame


def recheck(frame):
    for value in frame['captured'].values():
        p=verify(value);s=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==frame['identities'][value['path']], 'captured input identity unchanged')
    for index in frame['families']:
        family(index)
    for item in frame['tools']['jsToolchain']['symlinks']:
        path = Path(frame['tools']['jsToolchain']['root']) / item['path']
        need(path.is_symlink() and os.readlink(path) == item['target'] and str(path.resolve()) == item['resolved']['path'], 'unchanged JS alias')
    sdk=Path(frame['context']['sdkRoot']);need(str(sdk.resolve())==frame['context']['sdkRootResolution'],'actual SDK selection unchanged')
    need((os.readlink(sdk)if sdk.is_symlink()else None)==frame['context']['sdkRootLinkText'],'actual SDK lexical alias unchanged')
    cargo_config_guard()


def save(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row(path)


def space():
    free = shutil.disk_usage(WORK.parent).free
    need(free >= FLOOR, '800MiB free-space floor at this boundary')
    return free


def materialization_plan(frame):
    """Pure exact copy/alias plan; no staging or version/metadata projection."""
    tools, cut, plan = frame['tools'], frame['cut'], frame['plan']
    need(cut['futureSourceRoot'] == plan['sourceRoot'] == str(SOURCE)
         and plan['workRoot'] == str(WORK) and plan['packageRoot'] == str(PACKAGE), 'declared fresh roles')
    modes = {r['relativePath']: r['mode'] for r in cut['baseline']['files']}
    need(len(cut['files']) == len(modes) == 271 and not cut['baseline']['symlinks'], 'exact source tree')
    copies, names = [], set()
    for item in cut['files']:
        name = local(item['path']);need(name not in names, 'unique source');names.add(name)
        value = item['baseline'] if item['origin'] == 'UNCHANGED_BASELINE' else dict(path=str(PROPOSAL/'after'/name), sha256=item['sha256'], bytes=item['bytes'])
        need(item['origin'] in ('UNCHANGED_BASELINE', 'CORRECTED_AFTERIMAGE') and value['sha256'] == item['sha256'] and value['bytes'] == item['bytes'], 'declared original/afterimage')
        need(modes[name] in (0o644, 0o755), 'actual source mode')
        copies.append(dict(source=value, path=str(SOURCE/name), mode=modes[name]))
    need(plan['packageSourceFiles'] == ['package.json', 'types.d.ts', 'src/componentize.js', 'src/platform.js', 'src/cli.js'], 'finite package source entries')
    by_name = {r['path']: r for r in cut['files']}
    for name in plan['packageSourceFiles']:
        item=by_name[name];copies.append(dict(source=dict(path=str(SOURCE/name),sha256=item['sha256'],bytes=item['bytes']),path=str(PACKAGE/name),mode=0o600))
    need(len(tools['jsToolchain']['files']) == 4862 and len(tools['jsToolchain']['symlinks']) == 21, 'actual JS tool cut')
    package_names = set(plan['packageSourceFiles'])
    for item in tools['jsToolchain']['files']:
        original_name=local(item['relativePath'])
        # The cut has4860 dependencies plus TWO tool-root metadata files.
        # Those originals are preserved as DATA, never overwrite the new
        # componentize package.json or acquire a Node package-resolution role.
        name=original_name if original_name.startswith('node_modules/')else '.toolchain-metadata/'+original_name
        need(original_name.startswith('node_modules/')or original_name in ('package.json','package-lock.json'),'finite tool-root metadata map')
        need(name not in package_names,'unique declared private copy');package_names.add(name)
        need(item['mode'] in (0o644, 0o755), 'actual JS mode')
        copies.append(dict(source=item['descriptor'],path=str(PACKAGE/name),mode=item['mode']))
    aliases=[]
    for item in tools['jsToolchain']['symlinks']:
        name=local(item['path']);need(name.startswith('node_modules/') and name not in package_names, 'unique declared alias');package_names.add(name)
        need(not Path(item['target']).is_absolute() and '\\'not in item['target'] and '\0'not in item['target'], 'relative alias')
        normalized=os.path.normpath(str(Path(name).parent/item['target']))
        need(normalized in package_names or normalized in {r['relativePath'] for r in tools['jsToolchain']['files']}, 'alias resolves inside declared private files')
        aliases.append(dict(path=str(PACKAGE/name),target=item['target'],resolved=item['resolved']))
    need(len(copies) == 5138 and len({r['path'] for r in copies}) == 5138, '271+5+4862 exact copies')
    need(len(tools['lockedRegistryArchives']) == 118 and len(tools['missingLockedRegistryArchives']) == 3, 'exact locked fetch scope')
    return copies, aliases


def command_plan(frame):
    """Finite derivation from four genuine Source command plans, plus four tests."""
    tools, plan = frame['tools'], frame['plan'];originals=plan['commandPlans'];need(len(originals)==4, 'four original plans')
    need([r['role'] for r in originals]==['HOST_CLI_BUILD','WASM_SPLICER_COMPONENT_BUILD','WASI_COMPONENT_WRAPPER','SPLICER_JS_BINDINGS'], 'unchanged command roles')
    commands=[]
    for index, operation in enumerate(originals):
        need(operation['cwd']==str(SOURCE), 'real configured source cwd');argv=list(operation['argv'])
        if index < 2:
            need(argv[0]==tools['cargo']['path'] and argv[1:5]==['build','--locked','--offline','--release'] and argv[-2:]==['--target-dir',str(WORK/'target')], 'genuine locked Cargo build')
            argv += ['--jobs','1']
        else:
            need(argv[:2]==[tools['node']['path'],tools['jcoEntry']['path']], 'original pinned Node/Jco')
            argv[1]=str(PACKAGE/'node_modules/@bytecodealliance/jco/dist/jco.js')
        commands.append(dict(name=operation['role'].lower(),argv=argv,timeoutSeconds=1800 if index<2 else 600,unitFilter=None))
        if index == 0:
            for test in UNIT_FILTERS:
                argv=[tools['cargo']['path'],'test','--locked','--offline','--release','-p','spidermonkey-embedding-splicer','--lib','--target','aarch64-apple-darwin','--target-dir',str(WORK/'target'),'--jobs','1','clock_io_policy_tests::'+test,'--','--nocapture']
                commands.append(dict(name='unit-'+test,argv=argv,timeoutSeconds=600,unitFilter=test))
    need(len(commands)==8 and sum(r['timeoutSeconds'] for r in commands)==7200, 'eight per-command maxima under one outer7200 cap; not additive extra time')
    return commands


def ensure_directories(root, parent):
    need(root.is_dir() and not root.is_symlink() and parent.is_relative_to(root), 'owned destination root')
    current=root
    for name in parent.relative_to(root).parts:
        current=current/name
        if not current.exists():current.mkdir(mode=0o700)
        need(current.is_dir() and not current.is_symlink() and stat.S_IMODE(current.stat().st_mode)==0o700, 'owned regular directory')


def copy_file(value, destination, mode=0o600):
    space()
    source = verify(value)
    root=next((p for p in (SOURCE,WORK,PACKAGE) if destination.is_relative_to(p)),None)
    need(root is not None, 'copy only into declared fresh roots');ensure_directories(root,destination.parent)
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with source.open('rb') as original, os.fdopen(fd,'wb') as target:
        shutil.copyfileobj(original, target, 4 * 1024 * 1024)
        target.flush()
        os.fsync(target.fileno())
    destination.chmod(mode)
    need(row(destination)==dict(value,path=str(destination)), 'copied exact bytes and length')
    need(destination.stat().st_nlink == 1 and (source.stat().st_dev, source.stat().st_ino) != (destination.stat().st_dev, destination.stat().st_ino), 'independent copy')
    return dict(source=value, destination=row(destination), mode=mode)


def archive_model(item):
    need(re.fullmatch('[A-Za-z0-9_-]+', item['name']) is not None, 'literal crate name')
    need(re.fullmatch('[0-9][A-Za-z0-9.+_-]*', item['version']) is not None, 'literal crate version')
    need(re.fullmatch('[a-f0-9]{64}', item['sha256']) is not None, 'locked checksum')


def archive_member_model(prefix, members):
    """Pure tar metadata guard, shared with actual regular-only extraction."""
    files={};directories=set();total=0
    for member in members:
        name=member['name']
        if member['kind']=='directory' and name.rstrip('/')==prefix:continue
        need(type(name)is str and name.startswith(prefix+'/'), 'one literal crate prefix')
        name=local(name[len(prefix)+1:].rstrip('/') if member['kind']=='directory' else name[len(prefix)+1:])
        need(name!='.cargo-checksum.json' and name not in files, 'no duplicate/generated checksum member')
        need(not any(parent.as_posix() in files for parent in Path(name).parents if parent.as_posix()!='.'),'no file-as-parent')
        if member['kind']=='directory':
            need(name not in directories,'unique explicit directory');directories.add(name);continue
        need(member['kind']=='file' and name not in directories,'regular members only; no links/devices')
        need(not any(n.startswith(name+'/') for n in set(files)|directories),'no file replacing an earlier parent')
        need(type(member['bytes'])is int and 0<=member['bytes']<=32*1024*1024,'bounded regular member')
        total+=member['bytes'];need(total<=MAX_CRATE_BYTES,'bounded uncompressed crate')
        files[name]=member
    need('Cargo.toml'in files,'real crate manifest')
    return files,total


def vendor_archive(archive, item, vendor, remaining=MAX_VENDOR_BYTES):
    archive_model(item)
    need(row(archive)['sha256'] == item['sha256'], 'locked archive checksum')
    prefix = item['name'] + '-' + item['version']
    target = vendor / prefix
    target.mkdir(mode=0o700)
    files = {}
    with tarfile.open(archive, 'r:*') as bundle:
        members=[]
        for member in bundle:
            need(len(members)<16384,'finite archive membership');members.append(member)
        descriptions=[dict(name=m.name,kind='directory' if m.isdir() else ('file' if m.isfile() else 'refused'),bytes=m.size) for m in members]
        expected,unpacked=archive_member_model(prefix,descriptions)
        need(unpacked<=remaining,'remaining total vendor budget before extraction')
        for member in members:
            space()
            if member.isdir() and member.name.rstrip('/')==prefix:continue
            need(member.name.startswith(prefix + '/'), 'one crate prefix')
            name = local(member.name[len(prefix) + 1:].rstrip('/') if member.isdir() else member.name[len(prefix)+1:])
            path = target / name
            if member.isdir():
                ensure_directories(target,path)
                continue
            need(member.isfile() and name not in files and name != '.cargo-checksum.json', 'regular unique crate member')
            ensure_directories(target,path.parent)
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with bundle.extractfile(member) as incoming, os.fdopen(fd,'wb') as outgoing:
                shutil.copyfileobj(incoming, outgoing, 1024 * 1024)
                outgoing.flush();os.fsync(outgoing.fileno())
            need(path.stat().st_size==expected[name]['bytes'],'full uncompressed member')
            path.chmod(0o700 if member.mode&0o111 else 0o600)
            files[name] = row(path)['sha256']
    need('Cargo.toml' in files, 'real crate manifest')
    save(target / '.cargo-checksum.json', dict(files=files, package=item['sha256']))
    need(set(files)==set(expected),'exact extracted files')
    return dict(name=item['name'], version=item['version'], archive=row(archive), files=len(files),unpackedBytes=unpacked)


def inventory(root, aliases=None):
    """Actual fresh tree DATA, never a replacement for original input protection."""
    aliases={} if aliases is None else aliases
    files=[];links=[]
    need(root.is_dir() and not root.is_symlink(),'owned inventory root')
    for p in sorted(root.rglob('*')):
        name=p.relative_to(root).as_posix();s=p.lstat()
        if p.is_symlink():
            need(name in aliases and os.readlink(p)==aliases[name]['target'],'only exact declared aliases')
            need(p.resolve().is_relative_to(root) and row(p.resolve())['sha256']==aliases[name]['resolved']['sha256'],'private alias target')
            links.append(dict(path=name,target=os.readlink(p),resolvedPath=str(p.resolve())))
        elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700,'private directory')
        else:
            need(stat.S_ISREG(s.st_mode) and s.st_nlink==1,'ordinary independently owned file')
            files.append(dict(row(p),relativePath=name,mode=stat.S_IMODE(s.st_mode)))
    need({r['path']for r in links}==set(aliases),'exact alias membership')
    return dict(root=str(root),files=files,links=links)


def tree_model(actual,expected,aliases,allow_lib=False):
    """Pure membership/byte comparison; generated lib is a bounded new DATA set."""
    by_name={r['relativePath']:r for r in actual['files']}
    need(len(by_name)==len(actual['files']),'unique regular inventory')
    need({r['path']for r in actual['links']}==set(aliases),'exact links')
    generated=[]
    for name,value in by_name.items():
        if name in expected:
            need(value['sha256']==expected[name]['sha256'] and value['bytes']==expected[name]['bytes'],'declared private copy exact')
        else:
            need(allow_lib and name.startswith('lib/') and name.endswith(('.js','.wasm','.ts')),'no unlisted private files')
            generated.append(value)
    need(set(expected).issubset(by_name),'all declared private files present')
    need(len(generated)<=128 and sum(r['bytes']for r in generated)<=256*1024*1024,'bounded generated binding family')
    return generated


def check_materialized(frame,complete=False):
    copies,links=materialization_plan(frame)
    source_expected={str(Path(r['path']).relative_to(SOURCE)):r['source'] for r in copies if Path(r['path']).is_relative_to(SOURCE)}
    package_expected={str(Path(r['path']).relative_to(PACKAGE)):r['source'] for r in copies if Path(r['path']).is_relative_to(PACKAGE)}
    aliases={str(Path(r['path']).relative_to(PACKAGE)):r for r in links}
    src=inventory(SOURCE);pkg=inventory(PACKAGE,aliases)
    tree_model(src,source_expected,{});generated=tree_model(pkg,package_expected,aliases,allow_lib=complete)
    if complete:
        names={r['relativePath']for r in generated}
        need('lib/spidermonkey-embedding-splicer.js'in names and any(n.endswith('.wasm')for n in names),'actual new binding JS/core outputs')
    if 'stageInventory'in frame:
        old=frame['stageInventory']
        need(inventory(WORK/'vendor')==old['vendor'],'private vendor immutable including checksums')
        for descriptor in old['archives']+[old['cargoConfig']]:verify(descriptor)
    return dict(source=src,package=pkg,generatedFiles=generated)


def compiler_environment(frame,original):
    """Small explicit tool environment; HOME/CODEX_HOME values are preserved."""
    tools,context=frame['tools'],frame['context']
    environment={k:v for k,v in original.items()if k in ['HOME','CODEX_HOME','USER','LOGNAME','SHELL','LANG','LC_CTYPE','LC_ALL','TZ','TERM']}
    environment.update(PATH=os.pathsep.join([str(Path(tools['cargo']['path']).parent),str(Path(context['hostLinkerDriver']['path']).parent),'/usr/bin','/bin','/usr/sbin','/sbin']),
        RUSTC=tools['rustc']['path'],RUSTDOC=tools['rustdoc']['path'],RUSTUP_TOOLCHAIN='1.96.1-aarch64-apple-darwin',CARGO_HOME=str(WORK/'cargo-home'),
        CARGO_BUILD_JOBS='1',CARGO_INCREMENTAL='0',CARGO_NET_OFFLINE='true',CARGO_TARGET_AARCH64_APPLE_DARWIN_LINKER=context['hostLinkerDriver']['path'],
        CARGO_TARGET_WASM32_WASIP1_LINKER=context['wasmLinker']['path'],SDKROOT=context['sdkRoot'],TMPDIR=str(WORK/'tmp'),BINARYEN_CORES='1',RAYON_NUM_THREADS='1')
    return environment


def cargo_config_guard():
    # Cargo still discovers ancestor configs when CARGO_HOME is private.
    for parent in (SOURCE,*SOURCE.parents):
        for name in ('config','config.toml'):
            p=parent/'.cargo'/name;need(not p.exists()and not p.is_symlink(),'no unindexed ancestor Cargo override')


class RejectDownloadRedirects(urllib.request.HTTPRedirectHandler):
    """Reject every redirect before followup; close the unused response body."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Reject even absent/malformed Location. No target is opened or parsed.
        # Closing here matters: the base handler would close only AFTER this
        # callback, and an exception bypasses its read/close sequence.
        try:
            fp.close()
        finally:
            raise urllib.error.HTTPError(req.full_url, code,
                                         'locked archive redirects refused', headers, None)

    def http_error_302(self, req, fp, code, msg, headers):
        return self.redirect_request(req, fp, code, msg, headers, None)

    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    # Pinned Python3.9 has no default308 alias. Cover it explicitly.
    http_error_308 = http_error_302


def download_opener():
    # Local opener only: no install_opener/global mutation. An empty proxy
    # map disables environment/system proxy discovery for these three URLs.
    return urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                       RejectDownloadRedirects())


def stage(frame):
    need(shutil.disk_usage(WORK.parent).free >= 2 * 1024**3, 'start at2GiB before creation/copies')
    cargo_config_guard()
    for path in (SOURCE, WORK, PACKAGE):
        need(not path.exists() and not path.is_symlink(), 'fresh output')
        path.mkdir(mode=0o700)
    need(shutil.disk_usage(WORK).free >= 2 * 1024**3, 'start at2GiB')
    tools, cut = frame['tools'], frame['cut']
    plan,aliases=materialization_plan(frame);copies=[]
    for item in plan:copies.append(copy_file(item['source'],Path(item['path']),item['mode']))
    for item in aliases:
        destination=Path(item['path']);ensure_directories(PACKAGE,destination.parent);destination.symlink_to(item['target'])
        need(destination.resolve().is_relative_to(PACKAGE) and row(destination.resolve())['sha256']==item['resolved']['sha256'],'private internal alias')
    vendor = WORK / 'vendor'
    vendor.mkdir(mode=0o700)
    downloads = WORK / 'locked-archives'
    downloads.mkdir(mode=0o700)
    archives = []
    for item in tools['lockedRegistryArchives']:
        value = item['descriptor']
        copy = downloads / (item['name'] + '-' + item['version'] + '.crate')
        copies.append(copy_file(value, copy))
        archives.append(dict(name=item['name'], version=item['version'], sha256=value['sha256'], path=copy))
    client = download_opener()
    for item in tools['missingLockedRegistryArchives']:
        archive_model(item)
        url = 'https://static.crates.io/crates/{0}/{0}-{1}.crate'.format(item['name'], item['version'])
        path = downloads / (item['name'] + '-' + item['version'] + '.crate')
        with client.open(url, timeout=60) as response, path.open('xb') as target:
            need(response.geturl()==url,'no unknown download redirect');started=time.monotonic()
            total = 0
            for block in iter(lambda: response.read(1024 * 1024), b''):
                space();need(time.monotonic()-started<=60,'bounded download read loop')
                total += len(block)
                need(total <= 16 * 1024 * 1024, 'bounded locked archive download')
                target.write(block)
            target.flush()
            os.fsync(target.fileno())
        need(row(path)['sha256'] == item['sha256'], 'exact downloaded locked crate')
        archives.append(dict(item, path=path, url=url))
    need(len(archives) == 121, '118cached plus3locked downloads')
    vendored=[];unpacked=0
    for item in archives:
        record=vendor_archive(item['path'],item,vendor,MAX_VENDOR_BYTES-unpacked);vendored.append(record);unpacked+=record['unpackedBytes']
    need(sum(r['unpackedBytes']for r in vendored)<=MAX_VENDOR_BYTES,'finite total vendor content')
    cargo_home = WORK / 'cargo-home'
    cargo_home.mkdir(mode=0o700)
    config_text = '[source.crates-io]\nreplace-with = "private-vendor"\n[source.private-vendor]\ndirectory = ' + json.dumps(str(vendor)) + '\n[net]\noffline = true\n'
    with (cargo_home / 'config.toml').open('x') as stream:
        stream.write(config_text)
        stream.flush();os.fsync(stream.fileno())
    (WORK/'tmp').mkdir(mode=0o700)
    # Cargo discovers ancestor .cargo configs even with a private CARGO_HOME.
    # No unindexed ancestor config may contribute hidden build settings.
    cargo_config_guard()
    frame['stageInventory']=dict(vendor=inventory(vendor),archives=[row(r['path'])for r in archives],cargoConfig=row(cargo_home/'config.toml'))
    check_materialized(frame)
    return save(WORK / 'stage-receipt.json', dict(schemaVersion=1, sourceIndex=frame['root']['sourceIndex'], copies=copies,
                sources=271, jsToolFiles=4862, jsAliases=21, vendored=vendored, privateCargoHome=str(cargo_home),
                stageInventory=frame['stageInventory'],originalSourceOrCacheModified=False, allOutputsFresh=True, adapterPublished=False))


def raw_step(frame, name, argv, environment, timeout):
    before=None;before_error=None
    try:before=shutil.disk_usage(WORK.parent).free
    except BaseException as caught:before_error=dict(type=type(caught).__name__)
    folder = WORK / 'commands' / local(name)
    folder.mkdir(parents=True, mode=0o700)
    start = time.monotonic()
    terminal=None;failure=None;after=None;post_error=None;streams={}
    try:
        need(before is not None and before>=FLOOR,'800MiB command-start floor')
        terminal=frame['monitor'].monitor(argv,str(SOURCE),environment,folder,timeout,frame['config']['rootAuthority'])
    except BaseException as caught:failure=dict(type=type(caught).__name__,stage='owned-command-call')
    finally:
        # An actual post-command observation precedes the summary and semantic
        # checks on EVERY path; unavailable space is represented as unavailable.
        try:after=shutil.disk_usage(WORK.parent).free
        except BaseException as caught:post_error=dict(type=type(caught).__name__)
        for key in ('stdout','stderr'):
            path=folder/(key+'.log')
            if path.is_file()and not path.is_symlink():
                fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
                try:os.fsync(fd)
                finally:os.close(fd)
                streams[key]=row(path)
    monitor_row=row(folder/'terminal.json')if(folder/'terminal.json').is_file()else None
    summary=dict(schemaVersion=1,argv=argv,cwd=str(SOURCE),monitorTerminal=monitor_row,
        rawExitCode=None if terminal is None else terminal['rawExitCode'],timeout=None if terminal is None else terminal['timeout'],
        timeoutSeconds=timeout,operationalSeconds=time.monotonic()-start,streams=streams,streamsClipped=False,
        availableStreamsFsynced=True,rawMonitorCallReturned=terminal is not None,callFailure=failure,
        beforeFreeBytes=before,afterFreeBytes=after,preSpaceObservationError=before_error,postSpaceObservationError=post_error,
        diskFloorCheckedBeforeAndAfter=before is not None and after is not None,diskFloorMonitoredDuringCommand=False,
        beforeFloorPassed=before is not None and before>=FLOOR,afterFloorPassed=after is not None and after>=FLOOR)
    summary_row=save(folder/'command-summary.json',summary)
    need(failure is None and terminal is not None and monitor_row is not None,'actual owned command returned')
    need(read(monitor_row)==terminal,'raw owned terminal equals actual return')
    need(terminal['authority']==frame['config']['rootAuthority']and terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['forcedCleanup']is False
         and terminal['allObservedOwnedGroupsGone']is True and terminal['parentOwnedGroupGone']is True
         and terminal['signals']==[] and terminal['errors']==[] and terminal['interruptedSignals']==[]
         and terminal['remainingObservedPids']==[] and terminal['finalGroups']and all(g['alive']is False for g in terminal['finalGroups']), 'owned command clean-zero '+name)
    need(after is not None and after>=FLOOR,'actual command-end floor '+name)
    return summary_row


def unit_result_model(text, selected):
    need(re.findall(r'^running 1 test$',text,re.M)==['running 1 test'],'one actual Rust test selected')
    need(len(re.findall(r'^test .*clock_io_policy_tests::'+re.escape(selected)+r' \.\.\. ok$',text,re.M))==1,'exact actual selected test passed')
    need(re.search(r'^test result: ok\. 1 passed; 0 failed; 0 ignored;',text,re.M)is not None,'zero-test/ignored/failed unit result refuses')


def worker(frame):
    os.umask(0o077)
    steps = []
    error = None
    stage_receipt = None
    pruner_refusal_test=None
    protection_error=None
    protected=False;private_complete=False;artifacts=[]
    try:
        frame['monitor']=load_monitor(frame)
        stage_receipt = stage(frame)
        recheck(frame)
        environment=compiler_environment(frame,os.environ)
        for operation in command_plan(frame):
            steps.append(raw_step(frame,operation['name'],operation['argv'],environment,operation['timeoutSeconds']))
            if operation['unitFilter']is not None:
                summary=read(steps[-1]);terminal=read(summary['monitorTerminal']);text=verify(terminal['stdout']).read_text()
                unit_result_model(text,operation['unitFilter'])
                if operation['unitFilter']=='adapter_input_guard_refuses_unknown_payloads_before_parse':pruner_refusal_test=True
            recheck(frame)
            check_materialized(frame,complete=operation['name']=='splicer_js_bindings')
        private=check_materialized(frame,complete=True);save(WORK/'private-package-inventory.json',private);private_complete=True
        artifacts = [row(WORK/'target/aarch64-apple-darwin/release/splicer'), row(WORK/'target/wasm32-wasip1/release/splicer_component.wasm'), row(WORK/'splicer.wasm')]
        artifacts.extend(row(p) for p in sorted((PACKAGE/'lib').rglob('*')) if p.is_file())
    except BaseException as caught:
        error = dict(type=type(caught).__name__, detail=str(caught), availablePartialFilesMayExist=True,fullPartialEvidenceClaim=False)
        artifacts = []
    finally:
        try:
            recheck(frame)
            protected = True
        except BaseException as caught:
            protected = False
            protection_error = dict(type=type(caught).__name__, detail='Final input protection failed: '+str(caught))
    # Even a failure before WORK creation has a durable record under the already
    # fresh owned external root. An authorize failure is instead retained by the
    # parent's raw worker streams; it does not fabricate a worker result.
    result = dict(schemaVersion=1, state='CLOCK_IO_TOOLS_BUILD_COMPLETE_UNREVIEWED_V2' if error is None and protected else 'CLOCK_IO_TOOLS_BUILD_FAILED_UNACCEPTED_V2',
        sourceIndex=frame['root']['sourceIndex'], rootAuthority=frame['config']['rootAuthority'], stageReceipt=stage_receipt, commandTerminals=steps,
        artifacts=artifacts, error=error, finalProtectionError=protection_error,protectedInputsRechecked=protected,privatePackageMembershipVerified=private_complete,
        diskFloorMonitoredDuringCommand=False, adapterArtifactPublished=False,validAdapterPruningRun=False,adapterCliPruneCommandInvoked=False,
        prunerFunctionInvokedByRefusalUnitTest=pruner_refusal_test,
        nativeEngineBuiltOrExecuted=False, applicationComponentConstructed=False, applicationGuestExecuted=False,
        independentArtifactReview=None, operationalAdmission=False, runtimeAcceptanceClaim=False)
    destination=WORK/'result.json' if WORK.is_dir()and not WORK.is_symlink()else EXTERNAL/'worker-prework-failure.json'
    print(json.dumps(save(destination,result)),flush=True)
    return 0 if error is None and protected else 1


def load_monitor(frame):
    entry=MONITOR/'monitor.py';need(str(entry)in frame['captured'],'monitor entry in authenticated full family');verify(frame['captured'][str(entry)])
    recheck(frame)
    spec=importlib.util.spec_from_file_location('genuine_original_clock_build_monitor',entry)
    monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    return monitor


def partial_roots():
    """Bounded names/sizes only: honest failure DATA, not a full hash/copy proof."""
    result=[]
    for root in (SOURCE,WORK,PACKAGE):
        record=dict(root=str(root),exists=root.exists(),entries=[],allBytesHashed=False,inventoryComplete=False)
        if root.is_dir()and not root.is_symlink():
            for p in root.rglob('*'):
                need(len(record['entries'])<100000,'bounded partial observation')
                s=p.lstat();record['entries'].append(dict(path=p.relative_to(root).as_posix(),bytes=s.st_size,mode=stat.S_IMODE(s.st_mode),symlink=p.is_symlink(),directory=p.is_dir()and not p.is_symlink()))
            record['inventoryComplete']=True
        result.append(record)
    return result


def parent(frame, config_descriptor):
    for path in (SOURCE, WORK, PACKAGE, EXTERNAL):
        need(not path.exists() and not path.is_symlink(), 'fresh operation roots')
    monitor=load_monitor(frame)
    os.umask(0o077)
    EXTERNAL.mkdir(mode=0o700)
    argv = [frame['context']['python']['path'], '-B', '-I', str(HERE/'controller.py'), 'worker', json.dumps(config_descriptor,separators=(',',':'))]
    terminal=None;errors=[];protected=False;observation=None
    try:
        terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},EXTERNAL,7200,frame['config']['rootAuthority'])
        need(read(row(EXTERNAL/'terminal.json'))==terminal,'durable genuine terminal')
        for key in ('stdout','stderr'):verify(terminal[key])
        need(terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is True and terminal['parentOwnedGroupGone']is True
             and terminal['timeout']is terminal['forcedCleanup']is False and terminal['signals']==[] and terminal['interruptedSignals']==[]
             and terminal['errors']==[] and terminal['remainingObservedPids']==[],'clean owned build')
        result=read(row(WORK/'result.json'));need(result['state']=='CLOCK_IO_TOOLS_BUILD_COMPLETE_UNREVIEWED_V2'and result['error']is None
             and result['protectedInputsRechecked']is True and result['privatePackageMembershipVerified']is True,'whole actual worker result')
        # The worker stdout also contains exact inner-monitor PID notices. Keep
        # all raw lines and compare only the explicitly final result descriptor.
        raw=verify(terminal['stdout']).read_bytes();need(len(raw)<=16*1024*1024,'bounded worker JSONL')
        lines=[json.loads(line)for line in raw.splitlines()if line]
        need(len(lines)==9 and all(set(v)=={'pid','timeoutSeconds'}for v in lines[:-1])and lines[-1]==row(WORK/'result.json'),'eight real tool notices plus final result; no prefix relabel')
        need(result['prunerFunctionInvokedByRefusalUnitTest']is True and result['validAdapterPruningRun']is False
             and result['adapterCliPruneCommandInvoked']is False and result['adapterArtifactPublished']is False,'invalid-input pruner unit invocation is separate from valid adapter operation')
        observation=dict(workerResult=row(WORK/'result.json'),rawWorkerStdout=terminal['stdout'],rawWorkerStderr=terminal['stderr'],rawWorkerJsonlLines=9,prunerFunctionInvokedByRefusalUnitTest=True)
    except BaseException as caught:errors.append(dict(stage='owned-build-or-whole-result',type=type(caught).__name__))
    finally:
        try:recheck(frame);protected=True
        except BaseException as caught:errors.append(dict(stage='final-input-protection',type=type(caught).__name__))
    success=observation is not None and protected and not errors
    partial=None
    if not success:
        try:partial=save(EXTERNAL/'partial-output-observation.json',dict(schemaVersion=1,roots=partial_roots(),allBytesHashed=False))
        except BaseException as caught:errors.append(dict(stage='partial-observation-writer',type=type(caught).__name__))
    result=dict(schemaVersion=1,state='CLOCK_IO_BUILD_CONTROLLER_COMPLETE_UNREVIEWED_V2'if success else'CLOCK_IO_BUILD_CONTROLLER_FAILED_UNACCEPTED_V2',
        controllerIndex=frame['config']['controllerIndex'],sourceIndex=frame['root']['sourceIndex'],rootAuthority=frame['config']['rootAuthority'],
        rawTerminal=row(EXTERNAL/'terminal.json')if(EXTERNAL/'terminal.json').is_file()else None,workerObservation=observation,
        partialOutputObservation=partial,protectedInputsRechecked=protected,errors=errors,independentArtifactReview=None,
        adapterPublished=False,validAdapterPruningRun=False,adapterCliPruneCommandInvoked=False,
        prunerFunctionInvokedByRefusalUnitTest=True if observation is not None else None,
        applicationEngineOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    descriptor=save(EXTERNAL/'parent-observation.json',result);print(json.dumps(dict(observation=descriptor,completeUnreviewed=success)),flush=True)
    return 0 if success else 1


def main():
    need(len(sys.argv) == 3 and sys.argv[1] in ('parent','worker'), 'exact CLI')
    descriptor = json.loads(sys.argv[2])
    frame = authorize(descriptor)
    try:
        return parent(frame,descriptor) if sys.argv[1] == 'parent' else worker(frame)
    finally:
        recheck(frame)


if __name__ == '__main__':
    raise SystemExit(main())
