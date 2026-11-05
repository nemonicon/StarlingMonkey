"""Independent source/hash/static models; normalization stays in memory only."""
import ast
import hashlib
import itertools
import json
import os
import re
import stat
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent / 'clock-io-pruning-candidate-v1'
SOURCE_SHA = '55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f'
checks = 0
inputs = {}
cache = {}


def need(condition, label):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(label)


def take(row, role):
    p = Path(row['path'])
    need(p.is_absolute() and not p.is_symlink() and p.is_file(), 'absolute regular input ' + str(p))
    s = p.stat()
    key = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_mode)
    if key not in cache:
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                h.update(data)
        z = p.stat()
        need(key == (z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns, z.st_mode), 'unchanged during hash')
        cache[key] = h.hexdigest()
    need(cache[key] == row['sha256'] and s.st_size == row['bytes'], 'whole source/data hash ' + str(p))
    actual = inputs.setdefault(str(p), dict(path=str(p), sha256=cache[key], bytes=s.st_size,
        identity=list(key), roles=[]))
    need(actual['identity'] == list(key), 'stable actual input')
    if role not in actual['roles']:
        actual['roles'].append(role)
    return actual


def load(row, role):
    take(row, role)
    return json.loads(Path(row['path']).read_bytes())


def own(name):
    p = OWNER / name
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)


def family(row, role):
    data = load(row, role + ' index')
    root = Path(row['path']).parent
    names = {'index.json'}
    for r in data['files']:
        need(not Path(r['path']).is_absolute() and '..' not in Path(r['path']).parts and r['path'] not in names, 'finite index member')
        names.add(r['path'])
        take(dict(r, path=str(root / r['path'])), role + ' member')
    need({str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == names, 'exact family physical members')
    return data


def tree(value, role):
    root = Path(value['root'])
    names = set()
    for r in value['files']:
        take(r['descriptor'], role + ' regular')
        need(r['descriptor']['path'] == str(root / r['relativePath']), 'original tree path context')
        need(stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode) == r['mode'], 'tree mode')
        names.add(r['relativePath'])
    for r in value['symlinks']:
        p = root / r['path']
        need(p.is_symlink() and os.readlink(p) == r['target'] and str(p.resolve()) == r['resolved']['path'], 'declared link boundary')
        take(r['resolved'], role + ' declared real endpoint')
        names.add(r['path'])
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    need(actual == names, 'complete tree inventory')


index = family(dict(path=str(OWNER / 'index.json'), sha256=SOURCE_SHA, bytes=4094), 'reviewed proposal')
need(len(index['files']) == 25, 'actual25 proposal members')
refs = load(own('references.json'), 'original source reference contexts')
cut = load(own('source-cut.json'), 'whole271 source cut')
derivation = load(own('source-derivation.json'), 'exact four source derivations')
tools = load(own('tool-cut-references.json'), 'whole existing tool cut')
declared = load(own('source-inputs.json'), 'all declared input descriptors')
need(len(declared['files']) == 5572, 'actual5572 declared inputs')
for row in declared['files']:
    take(row, 'declared authenticated Source input')
for role in ('provenanceReport', 'independentDesignNotes'):
    family(refs[role]['index'], role + ' DATA not Source authority')
    take(refs[role]['result'], role + ' DATA result')
need(refs['designNotesAreSourceApproval'] is False, 'design notes not projected into Source approval')
need(refs['provenanceReport']['index']['sha256'] == 'dd49f61424b0285a590bc4a5f2ccc765d810b02f12919ed9470f5d3ad3a09433', 'exact adapter provenance')
need(refs['independentDesignNotes']['index']['sha256'] == '8a069abcd6d798bf81098685ad6435e1c2ae3436cf1714faf56dc23310915bb3', 'exact prior design notes')
for key in ('baselineSourceArchive', 'baselineArchiveShaText', 'baselineSourceObservation', 'baselineBuildLog', 'adapter', 'rootPureNormalizerObservation'):
    take(refs[key], key + ' DATA')
alias = refs['baselineSourceArchiveAlias']
need(Path(alias['path']).is_symlink() and os.readlink(alias['path']) == alias['target'], 'actual archive link text')
need(str(Path(alias['path']).resolve()) == alias['resolved']['path'], 'actual archive real source')
need(Path(refs['baselineArchiveShaText']['path']).read_text().strip() == refs['baselineSourceArchive']['sha256'], 'archive witness not changed tree hash')
tree(cut['baseline'], 'genuine271 baseline')
need(len(cut['baseline']['files']) == len(cut['files']) == cut['sourceFiles'] == 271, 'complete271 baseline/future cut')
need(cut['changedFiles'] == 4 and cut['unchangedFiles'] == 267, '267+4 cut accounting')
need(len(derivation['files']) == 4, 'all four afterimages')


def apply_hunks(source, fragment, reverse=False):
    source_lines = source.splitlines(True)
    patch_lines = fragment.splitlines(True)
    output = []
    cursor = 0
    i = 0
    while i < len(patch_lines):
        match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', patch_lines[i])
        if not match:
            i += 1
            continue
        start = int(match.group(3 if reverse else 1)) - 1
        need(start >= cursor, 'ordered exact hunk')
        output.extend(source_lines[cursor:start])
        cursor = start
        i += 1
        consumed, emitted = 0, 0
        while i < len(patch_lines) and not patch_lines[i].startswith('@@'):
            line = patch_lines[i]
            i += 1
            if line.startswith(('--- ', '+++ ')):
                continue
            need(line[:1] in (' ', '+', '-'), 'finite patch line')
            sign = line[0]
            if reverse:
                sign = {'+': '-', '-': '+', ' ': ' '}[sign]
            text = line[1:]
            if sign != '+':
                need(source_lines[cursor] == text, 'exact existing hunk bytes')
                cursor += 1
                consumed += 1
            if sign != '-':
                output.append(text)
                emitted += 1
        old_count = int(match.group(4 if reverse else 2) or 1)
        new_count = int(match.group(2 if reverse else 4) or 1)
        need(consumed == old_count and emitted == new_count, 'whole declared hunk sizes')
    output.extend(source_lines[cursor:])
    return ''.join(output)


patch = (OWNER / 'io-policy.patch').read_text()
fragments = {p.splitlines()[0][6:]: p for p in re.split(r'(?m)(?=^--- a/)', patch) if p.startswith('--- a/')}
need(len(fragments) == 4, 'exact four patch files')
changes = {}
for r in derivation['files']:
    take(r['before'], 'exact unchanged original donor')
    after = dict(r['after'], path=str(OWNER / r['after']['path']))
    take(after, 'unapplied afterimage')
    before_text = Path(r['before']['path']).read_text()
    after_text = Path(after['path']).read_text()
    need(apply_hunks(before_text, fragments[r['path']]) == after_text, 'complete forward derivation')
    need(apply_hunks(after_text, fragments[r['path']], True) == before_text, 'complete inverse derivation')
    changes[r['path']] = r
for r in cut['files']:
    need(r['futureConfiguredPath'] == str(Path(cut['futureSourceRoot']) / r['path']), 'new explicit source context')
    wanted = changes[r['path']]['after'] if r['path'] in changes else r['baseline']
    need(r['sha256'] == wanted['sha256'] and r['bytes'] == wanted['bytes'], 'exact new cut row')
    need(r['origin'] == ('CORRECTED_AFTERIMAGE' if r['path'] in changes else 'UNCHANGED_BASELINE'), 'truthful row origin')

# A small independent metadata decoder. No instructions or data segments are
# decoded; normalized bytes never leave memory and are never compiled/loaded.
def u32(data, at):
    value = 0
    for shift in range(0, 35, 7):
        need(at < len(data), 'bounded unsigned LEB')
        b = data[at]
        at += 1
        value |= (b & 127) << shift
        if b < 128:
            need(value <= 0xffffffff, 'u32 range')
            return value, at
    raise AssertionError('LEB exceeds u32')


def name(data, at):
    size, at = u32(data, at)
    need(at + size <= len(data), 'bounded metadata name')
    return data[at:at + size].decode(), at + size


def metadata(data):
    need(data[:8] == b'\0asm\1\0\0\0', 'exact core header')
    at = 8
    sections, imports, types, exports = [], [], [], []
    import_entries = []
    import_location = None
    while at < len(data):
        start = at
        section_id = data[at]
        size, payload_at = u32(data, at + 1)
        end = payload_at + size
        need(end <= len(data), 'bounded core section')
        sections.append((section_id, data[start:end]))
        payload = data[payload_at:end]
        if section_id == 1:
            count, p = u32(payload, 0)
            for _ in range(count):
                need(payload[p] == 0x60, 'ordinary function type')
                p += 1
                n, p = u32(payload, p)
                params = list(payload[p:p + n]); p += n
                n, p = u32(payload, p)
                results = list(payload[p:p + n]); p += n
                types.append(dict(params=params, results=results))
            need(p == len(payload), 'complete type section')
        elif section_id == 2:
            need(import_location is None, 'one import section')
            import_location = (start, payload_at, end)
            count, p = u32(payload, 0)
            functions = 0
            for i in range(count):
                entry_start = p
                module, p = name(payload, p)
                field, p = name(payload, p)
                kind = payload[p]; p += 1
                row = dict(importIndex=i, module=module, name=field, kind=kind)
                if kind == 0:
                    type_index, p = u32(payload, p)
                    need(type_index < len(types), 'actual function type exists')
                    row.update(functionIndex=functions, typeIndex=type_index)
                    functions += 1
                elif kind == 2:
                    flags, p = u32(payload, p)
                    minimum, p = u32(payload, p)
                    need(flags == 0, 'pinned unshared memory32 without max')
                    row['limits'] = dict(flags=flags, min=minimum)
                else:
                    raise AssertionError('unknown pinned import kind')
                imports.append(row)
                import_entries.append(payload[entry_start:p])
            need(p == len(payload), 'complete import section')
        elif section_id == 7:
            count, p = u32(payload, 0)
            for _ in range(count):
                field, p = name(payload, p)
                kind = payload[p]; p += 1
                index, p = u32(payload, p)
                exports.append(dict(name=field, kind=kind, index=index))
            need(p == len(payload), 'complete export section')
        at = end
    return dict(sections=sections, imports=imports, types=types, exports=exports,
                importEntries=import_entries, importLocation=import_location)


original = Path(refs['adapter']['path']).read_bytes()
need(len(original) == 53512 and hashlib.sha256(original).hexdigest() == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0', 'actual repository adapter, not npm fallback')
a = metadata(original)
need([r['kind'] for r in a['imports']] == [2] + [0] * 63, 'original memory-first hazard layout')
need(a['imports'][0] == dict(importIndex=0, module='env', name='memory', kind=2, limits=dict(flags=0, min=0)), 'exact sole imported memory')
start, payload_at, end = a['importLocation']
need(original[payload_at] == 64, 'canonical single-byte count64')
normalized_payload = bytes([64]) + b''.join(a['importEntries'][1:] + a['importEntries'][:1])
normalized = original[:payload_at] + normalized_payload + original[end:]
need(len(normalized) == 53512 and hashlib.sha256(normalized).hexdigest() == '667907826ed62123beb0c1817969dcf32527a02b4bcbbbb10dc1dcafaba12ecc', 'independent actual normalization only in memory')
b = metadata(normalized)
need(a['types'] == b['types'] and a['exports'] == b['exports'], 'types/exports exact index invariance')
need(len(a['sections']) == len(b['sections']), 'all section count preserved')
for x, y in zip(a['sections'], b['sections']):
    need(x[0] == y[0] and (x[0] == 2 or x[1] == y[1]), 'all non-import sections byte-identical')
af = [r for r in a['imports'] if r['kind'] == 0]
bf = [r for r in b['imports'] if r['kind'] == 0]
for old, new in zip(af, bf):
    need({k:v for k,v in old.items() if k != 'importIndex'} == {k:v for k,v in new.items() if k != 'importIndex'}, 'full imported function index/type sequence preserved')
    need(old['importIndex'] == old['functionIndex'] + 1 and new['importIndex'] == new['functionIndex'], 'actual hazard closed by function-first entries')
need(b['imports'][-1] == dict(a['imports'][0], importIndex=63), 'memory index-space unchanged, entry63')
model = load(own('adapter-metadata-model.json'), 'author metadata DATA independently checked')
need(model['functionTypes'] == a['types'] and model['exports'] == a['exports'] and model['originalImports'] == a['imports'], 'whole independently decoded original metadata equality')
need(model['normalizedInMemoryImports'] == b['imports'], 'whole normalized metadata equality')


def rust_function(text, key):
    match = re.search(r'(?m)^(?:pub )?fn ' + re.escape(key) + r'\b', text)
    need(match is not None, 'actual named Rust function ' + key)
    next_match = re.search(r'(?m)^(?:pub )?fn ', text[match.start() + 1:])
    return text[match.start():match.start() + 1 + next_match.start()] if next_match else text[match.start():]


rust = (OWNER / 'after/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs').read_text()
baseline = Path(derivation['baselinePath']).read_text()
calls = lambda t: re.findall(r'stub_wasi_imports\(\s*module,\s*"([^"]+)",\s*"([^"]+)"', t)
old_targets = calls(rust_function(baseline, 'stub_io'))
poll_targets = calls(rust_function(rust, 'stub_io_poll'))
stream_targets = calls(rust_function(rust, 'stub_io_streams'))
need(len(set(old_targets)) == 23 and len(poll_targets) == 4 and len(stream_targets) == 19, 'exact old23 split4+19')
need(sorted(old_targets) == sorted(poll_targets + stream_targets), 'no dropped/widened original stub target')
pruner = rust_function(rust, 'prune_clock_adapter_io')
need(pruner.index('wasm.len() != 53512') < pruner.index('Module::parse') and '667907826ed62123beb0c1817969dcf32527a02b4bcbbbb10dc1dcafaba12ecc' in pruner, 'exact size+SHA preparse guard')
need(re.findall(r'(?m)^    (stub_\w+)\(&mut module\)\?;', pruner) == ['stub_stdio','stub_io_streams'], 'only intended two helpers')
for forbidden in ('stub_wasi', 'stub_random', 'stub_clocks', 'stub_preview1', 'stub_filesystem', 'stub_cli', 'stub_io_poll'):
    need(forbidden + '(' not in pruner, 'narrow entry excludes ' + forbidden)
need(pruner.index('stub_stdio(&mut module)?') < pruner.index('stub_io_streams(&mut module)?') < pruner.index('module.encode()'), 'actual helper/encode ordering')
clock = [r for r in bf if r['module'].startswith('wasi:clocks/')]
poll = [r for r in bf if (r['module'].split('@')[0],r['name']) in poll_targets]
streams = [r for r in bf if (r['module'].split('@')[0],r['name']) in stream_targets]
stdio = [r for r in bf if r['module'] in ('wasi:cli/stdin@0.2.0','wasi:cli/stdout@0.2.0','wasi:cli/stderr@0.2.0')]
need(len(clock) == 6 and len(poll) == 2 and len(streams) == 11 and len(stdio) == 3, 'actual six clocks/two poll/fourteen pruning matches')
need(clock == model['sixClockImports'] and poll == model['twoPollImports'], 'all retained clock/poll signatures and indices exact')
need(streams == model['elevenPresentStreamErrorTargets'] and stdio == model['threePresentStdioTargets'], 'all actual14 replacement candidates exact')
need(not any(r['module'] == 'wasi_snapshot_preview1' for r in bf), 'stdio preview1 import attempts are absent no-ops')
need({'fd_write','fd_fdstat_get'} <= {r['name'] for r in a['exports']}, 'preview1 names are exports, not imports')
need(not {'cabi_realloc','get-random-u64'} & {r['name'] for r in a['exports'] + a['imports']}, 'generic random engine path not usable on this adapter')

# Read actual locked wirm code AND its immutable registry archive as DATA.
wirm = next(r for r in tools['lockedRegistryArchives'] if r['name'] == 'wirm' and r['version'] == '5.0.0')
registry = Path('/Users/dan/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/wirm-5.0.0')
with tarfile.open(wirm['descriptor']['path'], 'r:gz') as archive:
    for relative in ('src/ir/function.rs','src/ir/module/module_imports.rs','src/ir/module/module_functions.rs','src/ir/module/mod.rs'):
        path = registry / relative
        need(archive.extractfile('wirm-5.0.0/' + relative).read() == path.read_bytes(), 'actual cached wirm source equals pinned crate')
wf = (registry / 'src/ir/function.rs').read_text()
wm = (registry / 'src/ir/module/mod.rs').read_text()
need('FunctionID(*import_id)' in wf and 'FunctionID(imp_fn_id)' in wm and 'MemoryID(imp_mem_id)' in wm, 'actual function hazard and separate dense memory IDs')
need('let fid: FunctionID = FunctionID(*iid);' in rust, 'existing helper shares actual wirm hazard')

# One direct exact locked edge, with all registry inputs/checksums accounted.
before_lock = Path(derivation['files'][3]['before']['path']).read_text()
after_lock = (OWNER / 'after/Cargo.lock').read_text()
need(after_lock.replace(' "sha2",\n', '', 1) == before_lock, 'only direct locked sha2 edge changed')
sha2_block = next(x for x in re.split(r'(?m)^\[\[package\]\]\n', after_lock) if x.startswith('name = "sha2"\n'))
need('version = "0.10.9"' in sha2_block, 'existing exact sha2 version locked')
cargo = (OWNER / 'after/crates/spidermonkey-embedding-splicer/Cargo.toml').read_text()
need('sha2 = { version = "=0.10.9", default-features = false }' in cargo, 'direct exact declared Rust dependency')
need(len(tools['rustBinAndLibFiles']) == 270 and len(tools['jsToolchain']['files']) == 4862 and len(tools['lockedRegistryArchives']) == 118, 'complete declared tool counts')
for row in tools['rustBinAndLibFiles']:
    take(row, 'installed Rust1.96.1 tool DATA not compiler invocation')
tree(tools['jsToolchain'], 'existing complete JS tool cut DATA')
need(len(tools['jsToolchain']['symlinks']) == 21, 'all21 actual JS tool links')
take(tools['node'], 'pinned Node DATA not execution')
for row in tools['lockedRegistryArchives']:
    take(row['descriptor'], 'actual locked cached archive')
    block = next(x for x in re.split(r'(?m)^\[\[package\]\]\n', after_lock) if x.startswith('name = ' + json.dumps(row['name']) + '\n') and '\nversion = ' + json.dumps(row['version']) + '\n' in x)
    need('checksum = ' + json.dumps(row['descriptor']['sha256']) in block, 'archive exact locked checksum')
missing = tools['missingLockedRegistryArchives']
need({(r['name'],r['version']) for r in missing} == {('anstyle-wincon','3.0.7'),('once_cell','1.21.0'),('winapi-util','0.1.9')}, 'three explicit absent archive identities')
for row in missing:
    need(not Path(row['expectedPath']).exists(), 'declared cache absence remains true at review')
status = tools['missingArchiveStatus']
for witness in status['directWindowsEdges']:
    take(witness['archive'], 'actual cfg(windows) manifest archive witness')
    with tarfile.open(witness['archive']['path'], 'r:gz') as archive:
        data = archive.extractfile(witness['member']).read()
    need(hashlib.sha256(data).hexdigest() == witness['memberSha256'] and len(data) == witness['memberBytes'], 'whole actual manifest witness')
    need(witness['exactManifestHeading'].encode() in data and witness['targetPredicate'] == 'cfg(windows)', 'actual direct Windows edge; not target activation evaluation')
need(status['activationEvaluated'] is False and status['offlineReadinessProved'] is False and status['globalSourceBlocker'] is False, 'availability vs readiness correctly scoped')

# Independently model finite policy formula; these are not real WIT/Rust calls.
policy = rust_function(rust, 'io_requirements')
retained_names = set(re.findall(r'"(wasi:[^"]+)"', rust_function(rust, 'target_world_requires_io')))
names = set(re.findall(r'"(wasi:[^"]+)"', policy))
stream_names = names - {'wasi:io/poll@0.2'}
policy_cases = []
for bits in itertools.product((False,True), repeat=5):
    features = {f for f,b in zip(('Clocks','Stdio','Http','FetchEvent','Random'),bits) if b}
    for world in [set()] + [{n} for n in sorted(names | retained_names)]:
        has_streams = bool(features & {'Stdio','Http','FetchEvent'} or world & (stream_names | retained_names))
        has_poll = has_streams or 'Clocks' in features or 'wasi:io/poll@0.2' in world
        need(not has_streams or has_poll, 'stream retention always includes poll')
        if features == {'Clocks'} and not world:
            need(has_poll and not has_streams, 'clock-only source distinction')
        if features & {'Stdio','Http','FetchEvent'} or world & retained_names:
            need(has_streams and has_poll, 'wider declared IO preservation')
        policy_cases.append(dict(features=sorted(features), world=sorted(world), poll=has_poll, streams=has_streams))
need(len(policy_cases) == 672 and rust.count('#[test]') == 4, '672 pure Boolean cases/four UNRUN Rust definitions')
need('resolve.name_canonicalized_world_key(key)' in rust, 'real WIT canonicalization API used; alias/dependency tests still open')

normalizer_text = (OWNER / 'normalize-adapter.py').read_text()
normalizer_ast = ast.parse(normalizer_text)
writer = next(n for n in normalizer_ast.body if isinstance(n,ast.FunctionDef) and n.name == 'write_normalized')
need(isinstance(writer.body[-1], ast.Return), 'writer success result only after completion')
tries = [n for n in writer.body if isinstance(n,ast.Try)]
need(len(tries) == 1 and len(tries[0].finalbody) == 1 and ast.unparse(tries[0].finalbody[0]) == 'os.close(descriptor)', 'one final owner closes fd on wrapper/write/fsync failure')
need('closefd=False' in normalizer_text and 'os.O_EXCL' in normalizer_text and '0o600' in normalizer_text and '== 0o700' in normalizer_text, 'dormant private exclusive writer semantics')
need(normalizer_text.index('stream.write(data) == len(data)') < normalizer_text.index('stream.flush()') < normalizer_text.index('os.fsync(stream.fileno())'), 'full write/flush/fsync ordering')
need(not tries[0].handlers, 'writer failures propagate and no partial-success return')
need('unlink(' not in normalizer_text, 'failed partial outputs retained, not silently replaced')
cli = (OWNER / 'after/crates/spidermonkey-embedding-splicer/src/bin/splicer.rs').read_text()
branch = cli.split('Commands::PruneClockAdapterIo { input, output } => {',1)[1].split('Commands::StubWasi',1)[0]
need('create_new(true)' in branch and 'options.mode(0o600)' in branch and '#[cfg(unix)]' in branch, 'new CLI Unix exclusive private request')
need(branch.index('prune_clock_adapter_io(wasm)?') < branch.index('options.open(&output)') < branch.index('file.write_all(&result)?') < branch.index('file.sync_all()?'), 'CLI transforms before exclusive output; complete write and sync')
pure = load(own('pure-results.json'), 'retained author pure/injected model evidence only')
need(len(pure['cases']) == 27 and all(r['passed'] for r in pure['cases']) and pure['rustUnitTestsExecuted'] is False, 'authentic stored27 pure cases not Rust/runtime proof')
need(pure['writerSeamsMemoryOnly'] is True, 'stored writer cases are memory models only')
plan = load(own('future-build-plan.json'), 'dormant concrete build API plan')
need(plan['controllerImplemented'] is False and plan['allActionsAllowed'] is False, 'no owned build/action implementation admitted')
need(plan['futureEnvironment']['CARGO_HOME'] is None and plan['futureEnvironment']['hostLinkerAndSdk'] is None, 'cache/linker/SDK seams explicitly open')
need(plan['selectedEngineMechanism'].startswith('Existing componentize options.engine') and plan['adapterSelectionMechanism'].startswith('Existing componentize options.preview2Adapter'), 'actual selected engine/adapter APIs no projection')
for field in ('sourceIndependentReview','rootAuthority','stageAction','buildAction','normalizationPublication','pruningAction','actualPackage','actualPrunedAdapter','componentAction','runtimeAction'):
    need(refs[field] is None, 'closed Source action slot ' + field)

compiled_gates = [
    'Independent owned stage/build/publication caller and Root phase with exact whole source/tool closure before/final/failure, finite budgets/deadlines/raw collection, private protected input/output directories; all current slots are null.',
    'Actual locked host and wasm builds with selected linker/SDK/private Cargo cache and registry/target activation review. The3 missing Windows-linked archives do not prove a global Source blocker or offline readiness.',
    'Compile and run all4 Rust tests plus actual WIT WorldKey::Name aliases/canonical/version/dependency elaboration and profile-preservation regressions. Boolean672 source models do not elaborate WIT or prove these behaviors.',
    'Publish only fresh actual normalized/pruned adapters under new authority. Verify actual encoded references, all exports/type/index spaces, exact14 replacements and expected49-function/one-memory inventory, and exact6clock+2poll signatures. Expected output is not an observed artifact.',
    'New real splicer JS/package artifacts and dependency closure through existing engine/preview2Adapter selectors, never installed-tool mutation or old metadata/state/source projection.',
    'New component binary/type/core/adapter import graph and independent admission, preserving full declared wider stdio/streams/error/poll/HTTP/filesystem/socket/terminal and WIT dependency requirements. Do not widen strict2 or accept all6 blindly.',
    'Independent actual guest/runtime preservation of Date/monotonic/timers/poll and failure paths; no entropy, reset, unsafe probes, resource-lifetime, security or adoption claim follows from this Source proof.',
    'Future CLI/caller must authenticate input53512-byte path/hash before fs::read, keep private parents and inputs stable, and independently check output modes/membership/hash. Source-only writer models are not filesystem-race, crash-durability or owned-lifecycle evidence.'
]
result = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_CLOCK_IO_PRUNING_SOURCE_REVIEW_PASSED_V1',
    sourceIndexSha256=SOURCE_SHA, sourceOnly=True, sourceReviewPassed=True,
    ownerActionsInvoked=False, rustCompilerInvoked=False, adapterArtifactPublished=False,
    adapterPrunerExecuted=False, guestExecuted=False, nodeExecuted=False, sourceStaged=False,
    sourceFiles=271, unchangedSourceFiles=267, changedSourceFiles=4, declaredInputs=5572,
    exactFourForwardAndInverseDerivations=True, actualOriginalAdapter=refs['adapter'],
    originalAdapterSha256=refs['adapter']['sha256'], normalizedInMemorySha256=hashlib.sha256(normalized).hexdigest(),
    normalizedInMemoryBytes=len(normalized), allNonImportSectionsByteIdentical=True,
    completeTypesAndExportsIdentical=True, functionIndexAndMemoryIndexSpacesPreserved=True,
    memoryIndexDenseZeroWithImportEntry63=True, wirmActualApiHazardVerified=True,
    narrowRustPrunerGuardBeforeParse=True, narrowPrunerOnlyStdioAndStreams=True,
    originalIoTargets=23, pollTargets=4, streamErrorTargets=19, actualInputClockImports=6,
    actualInputPollImports=2, presentPruneTargets=14, expectedPostPruneFunctions=49,
    actualPrunedOutputObserved=False, rustUnitTestDefinitions=4, rustUnitTestsExecuted=False,
    independentBooleanPolicyCases=672, writerRealFilesystemExecuted=False,
    completeRustToolFiles=270, completeJsToolFiles=4862, jsToolSymlinks=21,
    cachedLockedArchives=118, missingLockedArchives=missing,
    offlineReadinessProved=False, missingArchivesAreGlobalSourceBlocker=False,
    provenanceAndDesignAreDataNotSourceApproval=True, requiredFutureGates=compiled_gates,
    checks=checks, physicalInputsRead=len(inputs), sourceIndependentReview=None,
    rootAuthority=None, actualNewPackage=None, actualPrunedAdapter=None,
    operationalAdmission=False, runtimeAcceptanceClaim=False, issuesAnyActionAuthority=False)
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
(HERE/'result-contract.json').write_text(json.dumps(dict(schemaVersion=1,
    state='BOUNDED_CLOCK_IO_PRUNING_SOURCE_RESULT_CONTRACT_V1', requiredState=result['state'],
    sourceIndex=own('index.json'), requiredFixedValues={k:result[k] for k in ('schemaVersion','sourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','rustCompilerInvoked','adapterArtifactPublished','adapterPrunerExecuted','guestExecuted')},
    futureGates=compiled_gates, sourceOrActionAuthorityGranted=False),indent=2)+'\n')
(HERE/'normalization-and-policy-audit.json').write_text(json.dumps(dict(schemaVersion=1,
    originalAdapter=refs['adapter'], normalizedSha256=hashlib.sha256(normalized).hexdigest(),
    originalImports=a['imports'], normalizedImports=b['imports'], functionTypes=a['types'], exports=a['exports'],
    sections=[dict(id=i,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for i,raw in a['sections']],
    unchangedNonImportSections=True, instructionsDecoded=False, binaryPublished=False,
    clocks=clock,poll=poll,streams=streams,stdio=stdio,booleanPolicyModels=policy_cases,
    rawWitElaborationOrRustExecution=False),indent=2)+'\n')
(HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(inputs.values(),key=lambda r:r['path']),
    sourceInputDescriptors5572Authenticated=True,ownerModulesImported=False),indent=2)+'\n')
print(json.dumps(dict(state=result['state'],checks=checks,physicalInputsRead=len(inputs),
    normalizedInMemorySha256=result['normalizedInMemorySha256'],adapterArtifactPublished=False)))
