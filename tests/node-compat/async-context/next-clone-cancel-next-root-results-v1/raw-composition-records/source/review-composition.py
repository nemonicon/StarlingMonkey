"""Self-contained closed DATA composition review. No tools/helpers/host replay."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-next-observer-v1-first')
CONSTRUCTION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/async-context/next-clone-cancel-next-root-results-v1/construction-review.json', 'sha256': '30ae9607b5d2b115e7dfd742c14c1071ab646dc5e14ef4510763a2926f773c49', 'bytes': 7868016}
OBSERVER_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-v4-composition-review.json', 'sha256': '214c1d9bcfd1858666d460afe72811b858fc8018e9f5e4bfb9519d8ddbe04224', 'bytes': 11140}
METADATA_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-metadata-runtime-review.json', 'sha256': '61bb6690df9cf8fef3c455314352a95816a20bc01920909b75632bf5333c47c8', 'bytes': 7272}
WAC = dict(path='/private/tmp/starling-node-compat/next-standard-handler-wac-build-v1-first/target/debug/wac', sha256='6577e5eedeb0644025a8454c3d600ecad14a3788432c48e8d40b7ba56d271f5f', bytes=30168152)
WASM_TOOLS = dict(path='/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/tools-v2/wasm-tools/wasm-tools', sha256='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d', bytes=17556208)
OBSERVER = dict(path='/private/tmp/starling-node-compat/next-standard-handler-observer-build-v4-first/observer.wasm', sha256='3534089e3a28ef109cffef9bc2c6b9bebf1e7ab7c90d1781c91272d01ac3092f', bytes=5771)
INPUTS = {}
STAMPS = {}
CHARGED = 0
DRIVER = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/async-context/next-clone-cancel-next-root-results-v1/compose-observer.py', 'sha256': '08e3698535ee448a028cef57d276447f55fc7712d86ab8fa53a548c0d677b6b4', 'bytes': 15749}
OWNER = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/clone-next-compose-observer')
PYTHON = '/opt/homebrew/Cellar/python@3.11/3.11.10/Frameworks/Python.framework/Versions/3.11/bin/python3.11'

def need(value, message):
    if not value:
        raise RuntimeError(message)


def stamp(value):
    return tuple(getattr(value, name) for name in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))


def row(path):
    p = Path(path)
    need(p.is_absolute() and p.resolve(strict=True) == p, 'canonical regular input')
    before = p.lstat()
    need(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= 2 * 1024**3, 'file kind/declared bound')
    h = hashlib.sha256()
    with p.open('rb') as f:
        need(stamp(os.fstat(f.fileno())) == stamp(before), 'changed before open')
        remaining = before.st_size
        while remaining:
            block = f.read(min(1024**2, remaining))
            need(bool(block), 'short input read')
            h.update(block)
            remaining -= len(block)
        need(f.read(1) == b'' and stamp(os.fstat(f.fileno())) == stamp(before), 'changed during read')
    need(stamp(p.lstat()) == stamp(before), 'file read bookend')
    return dict(path=str(p), sha256=h.hexdigest(), bytes=before.st_size)


def checked(ref):
    global CHARGED
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'} and
         type(ref['bytes']) is int and 0 <= ref['bytes'] <= 2 * 1024**3 and
         type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}', ref['sha256']) is not None, 'typed descriptor')
    old = INPUTS.get(ref['path'])
    need(old is None or old == ref, 'conflicting input descriptor')
    p = Path(ref['path'])
    if old is None:
        CHARGED += ref['bytes']
        need(len(INPUTS) < 100000 and CHARGED <= 96 * 1024**3, 'input count/aggregate declaration bound')
        need(row(p) == ref, 'input payload mismatch')
        INPUTS[ref['path']] = ref
        STAMPS[ref['path']] = stamp(p.lstat())
    else:
        need(stamp(p.lstat()) == STAMPS[ref['path']], 'input physical bookend')
    return p


def raw(ref, limit=32 * 1024**2):
    need(ref['bytes'] <= limit, 'bounded raw input')
    p = checked(ref)
    with p.open('rb') as f:
        data = f.read(limit + 1)
    need(len(data) == ref['bytes'] and len(data) <= limit and hashlib.sha256(data).hexdigest() == ref['sha256'], 'raw readback')
    need(stamp(p.lstat()) == STAMPS[ref['path']], 'raw input bookend')
    return data


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def doc(ref):
    return json.loads(raw(ref), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(RuntimeError('nonfinite JSON')))


def protect(full=False):
    for path, ref in list(INPUTS.items()):
        need(stamp(Path(path).lstat()) == STAMPS[path], 'protected input changed')
        if full:
            need(row(path) == ref, 'protected final payload changed')


def save(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    need(len(data) <= 32 * 1024**2, 'publication bound')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    primary = None
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            need(n > 0, 'short publication')
            view = view[n:]
        os.fsync(fd)
    except BaseException as error:
        primary = error
    try:
        os.close(fd)
    except BaseException:
        if primary is not None:
            raise primary
        raise
    if primary is not None:
        raise primary
    need(Path(path).read_bytes() == data, 'publication readback')
    return row(path)


def prerequisites():
    construction = doc(CONSTRUCTION_REVIEW)
    need(construction['state'] == 'CLONE_CANCEL_NEXT_COMPONENT_CONSTRUCTION_REVIEW_PASSED_V1', 'actual new Next construction review')
    for key in ('passed', 'verifiedPassed', 'completeReturnedImportAuditVerified', 'allImportTuplesUniqueAndTyped',
                'componentTypedArrayBytesMatch', 'completeActualMetadataReviewed', 'allThreeCommandsRawZeroClean', 'allCurrentInputsPreserved'):
        need(construction[key] is True, 'new construction proof: ' + key)
    for key in ('oldMetadataProjected', 'ordinaryGuestExecuted', 'appMountedAtInit', 'observerComposed', 'runtimeAccepted', 'fullNextAccepted'):
        need(construction[key] is False, 'new construction scope: ' + key)
    need(construction['component']['sha256'] == 'bfb106fe77874a8e4d2d24ec446c83a301af82346f782cee95dd219b336a943b' and
         construction['component']['bytes'] == 37274386, 'actual selected new inner')
    need(construction['originalDriverPassed'] is False and construction['originalOuterRawExitCode'] == 1, 'old native failure preserved')
    request = doc(construction['constructorRequest'])
    need(request['state'] == 'ROOT_CLONE_CANCEL_NEXT_ENGINE_CONSTRUCTION_V1' and
         request['engineAdmission'] == construction['engineAdmission'] and request['engine'] == construction['engine'] and
         request['nativeMetadata'] == construction['nativeMetadata'] and request['entry'] == construction['inputEntry'], 'actual new request roles')
    need(request['ordinaryExportsAllowed'] is False and request['oldFixedGuardInvoked'] is False, 'new request scope')
    admission = doc(construction['engineAdmission'])
    need(admission['state'] == 'CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1' and
         admission['passed'] is admission['completeActualMetadataReviewed'] is admission['nativeBuildPassed'] is True and
         admission['engine'] == construction['engine'] and admission['nativeMetadata'] == construction['nativeMetadata'] and
         admission['oldMetadataProjected'] is admission['guestExecuted'] is False, 'actual new engine admission')
    metadata = doc(construction['nativeMetadata'])
    need(sorted(metadata) == admission['metadataKeys'] == admission['metadataFieldsVerified'] == construction['metadataKeys'] and
         metadata['engine'] == construction['engine'], 'whole actual native metadata')
    for ref in construction['protectedInputs'] + request['inputs'] + admission['protectedBuildInputs'] + admission['protectedSourceInputs']:
        checked(ref)
    for ref in construction['artifacts'].values():
        checked(ref)
    for key in ('component', 'constructorRequest', 'engine', 'nativeMetadata', 'engineAdmission', 'inputEntry',
                'inputSourceIndex', 'constructorSourceIndex', 'selectionPolicy', 'constructorTerminal', 'validationTerminal', 'witTerminal'):
        checked(construction[key])
    observer = doc(OBSERVER_REVIEW)
    need(observer['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_DATA_REVIEW_PASSED_V1', 'actual observer construction ancestry')
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'rawChildBytesVerified', 'siblingDefiningInstancesVerified',
                'sharedNominalResourceAliasesVerified', 'fieldsNominalResourceAliasesVerified', 'metadataGetterCanonicalOptionsVerified',
                'synchronousLiftLowerWithInnerPostReturnVerified', 'innerExplicitPostReturnPreserved', 'observerManualPostReturnAbsent',
                'observerNoMarkerBeforeInnerCallSourceVerified', 'normalFieldsChildDropBeforeOwnForwardSourceVerified',
                'correlationSnapshotIndependentOfMethodAndPathSourceVerified', 'allSevenRequestedToolStepsRawZero', 'allSevenToolStderrEmpty'):
        need(observer[key] is True, 'observer ancestry proof: ' + key)
    need(observer['observerBinary'] == OBSERVER and observer['runtimeAccepted'] is observer['actualMetadataBehaviorProved'] is False,
         'observer Source/binary scope')
    metadata_review = doc(METADATA_REVIEW)
    need(metadata_review['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_METADATA_DATA_REVIEW_PASSED_V1', 'actual seven-case metadata ancestry')
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'allCollectionsCompletedCleanly', 'actualMetadataBehaviorProved',
                'runtimeAccepted', 'cleanOwner', 'finalInputsPreserved'):
        need(metadata_review[key] is True, 'metadata ancestry proof: ' + key)
    need(metadata_review['metadataCasesPassed'] == len(metadata_review['caseResults']) == 7 and
         all(r['passed'] is True for r in metadata_review['caseResults']) and metadata_review['rawExitCode'] == 0 and
         metadata_review['originalOwnerSeconds'] == 900 and metadata_review['compositionReview'] == OBSERVER_REVIEW and
         metadata_review['observerBinary'] == OBSERVER and metadata_review['nextWorkloadExecuted'] is metadata_review['fullNextAccepted'] is False,
         'metadata accepted roles and scope')
    for key in ('observerSource', 'observerManifest', 'observerProtocol'):
        checked(observer[key])
    checked(OBSERVER); checked(WAC); checked(WASM_TOOLS)
    return construction, request, observer

def owner():
    started_ref, terminal_ref = row(OWNER / 'started.json'), row(OWNER / 'terminal.json')
    started, terminal = doc(started_ref), doc(terminal_ref)
    argv = [PYTHON, '-I', '-B', DRIVER['path']]
    need(started['argv'] == argv and started['pid'] == terminal['pid'] and started['timeoutSeconds'] == 900 and
         started['authority'] == terminal['authority'], 'actual original composition owner start')
    authority = doc(terminal['authority'])
    need(authority['argv'] == argv and authority['seconds'] == 900 and DRIVER in authority['inputs'], 'actual composition owner authority')
    for ref in authority['inputs']:
        checked(ref)
    need(terminal['rawExitCode'] == 0 and terminal['timeout'] is terminal['forcedCleanup'] is False and
         terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
         all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')) and
         terminal['finalGroups'] and all(r['alive'] is False for r in terminal['finalGroups']), 'actual composition owner raw0 clean')
    checked(terminal['stdout']); checked(terminal['stderr'])
    return started_ref, terminal_ref


def sections(data, magic):
    need(len(data) <= 128 * 1024**2 and data[:8] == magic, 'bounded Wasm header')
    offset, result = 8, []
    while offset < len(data):
        start, kind = offset, data[offset]
        offset += 1
        size = 0
        for shift in range(0, 35, 7):
            need(offset < len(data), 'truncated section length')
            byte = data[offset]; offset += 1
            need(shift != 28 or byte < 16, 'u32 section length')
            size |= (byte & 127) << shift
            if byte < 128:
                break
        else:
            raise RuntimeError('unterminated section length')
        end = offset + size
        need(end <= len(data) and len(result) < 4096, 'section size/count bound')
        result.append((kind, start, offset, end)); offset = end
    need(offset == len(data), 'exact binary framing')
    return result


def world(ref):
    text = raw(ref).decode('utf8')
    match = re.match(r'package root:component;\n\nworld root \{\n([^{}]*)\}\n', text)
    need(match is not None, 'actual printed external world')
    result = dict(imports=[], exports=[])
    for line in match[1].splitlines():
        if line.strip():
            declaration = re.fullmatch(r'  (import|export) ([a-z0-9:/@.-]+);', line)
            need(declaration is not None, 'actual root world declaration')
            result['imports' if declaration[1] == 'import' else 'exports'].append(declaration[2])
    return result


def structure(ref):
    original = raw(ref).decode().splitlines()
    lines = [re.sub(r'^\(;@[0-9a-f]+\s*;\)', '', line) for line in original]
    facts = {}
    def unique_fact(name, pattern, candidates=None):
        selected = range(len(lines)) if candidates is None else candidates
        matches = [(i, re.search(pattern, lines[i])) for i in selected]
        matches = [(i, m) for i, m in matches if m is not None]
        need(len(matches) == 1, 'unique skeleton fact: ' + name)
        i, match = matches[0]
        facts[name] = dict(lineOneBased=i+1, literal=original[i])
        return i, match
    def block(index):
        end = next((i for i in range(index+1, len(lines)) if re.match(r'^  \([A-Za-z]', lines[i])), len(lines)-1)
        return range(index, end)
    roots = {}
    for i, line in enumerate(lines):
        match = re.fullmatch(r'  \(import "([^"]+)" \(instance \(;(\d+);\) \(type \d+\)\)\)', line)
        if match:
            need(match[1] not in roots, 'duplicate root import')
            roots[match[1]] = int(match[2])
    need(len(roots) == 13, 'actual root import instance map')
    component0, _ = unique_fact('innerComponentDefinition', r'^  \(component \(;0;\)$')
    component1, _ = unique_fact('observerComponentDefinition', r'^  \(component \(;1;\)$')
    inner_at, im = unique_fact('innerInstantiation', r'^  \(instance \(;(\d+);\) \(instantiate 0$')
    observer_at, om = unique_fact('observerInstantiation', r'^  \(instance \(;(\d+);\) \(instantiate 1$')
    inner_instance, observer_instance = int(im[1]), int(om[1])
    need(inner_instance != observer_instance and component0 < inner_at < component1 < observer_at, 'sibling root defining instances')
    alias_at, am = unique_fact('innerHandlerAlias', r'^  \(alias export '+str(inner_instance)+r' "wasi:http/incoming-handler@0\.2\.10" \(instance \(;(\d+);\)\)\)$')
    outer_at, xm = unique_fact('observerHandlerAlias', r'^  \(alias export '+str(observer_instance)+r' "wasi:http/incoming-handler@0\.2\.10" \(instance \(;(\d+);\)\)\)$')
    inner_alias, outer_alias = int(am[1]), int(xm[1])
    _, em = unique_fact('externalHandlerExport', r'^  \(export \(;(\d+);\) "wasi:http/incoming-handler@0\.2\.10" \(instance '+str(outer_alias)+r'\)\)$')
    need(inner_at < alias_at < observer_at < outer_at and inner_alias != outer_alias, 'actual handler alias order')
    inner_block, observer_block = list(block(inner_at)), list(block(observer_at))
    for interface in ('wasi:http/types@0.2.10', 'wasi:io/error@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:cli/stdout@0.2.10'):
        literal = '(with "'+interface+'" (instance '+str(roots[interface])+'))'
        need(sum(literal in lines[i] for i in inner_block) == sum(literal in lines[i] for i in observer_block) == 1,
             'shared nominal root resource instance: ' + interface)
    need(sum('(with "wasi:http/incoming-handler@0.2.10" (instance '+str(inner_alias)+'))' in lines[i] for i in observer_block) == 1,
         'observer internal handler bound to actual new inner alias')
    child0, child1 = list(block(component0)), list(block(component1))
    lift_at, _ = unique_fact('innerSynchronousHandlerLiftWithPostReturn',
        r'\(canon lift \(core func [^)]*wasi:http/incoming-handler@0\.2\.10#handle\) \(post-return [^)]*wasi:http/incoming-handler@0\.2\.10#handle\)\)', child0)
    need('async' not in lines[lift_at] and 'callback' not in lines[lift_at], 'actual synchronous inner lift options')
    literals = {
        'observerSynchronousLower': '(core func $lower-inner-handler (;1;) (canon lower (func $inner-handler)))',
        'observerSynchronousLift': '(func $handle (;7;) (type $handle-type) (canon lift (core func $handle-core)))',
        'sharedFieldsAlias': '(alias export $http "fields" (type $fields (;3;)))',
        'fieldsDrop': '(core func $drop-fields (;0;) (canon resource.drop $fields))',
        'methodLowerOptions': '(core func $lower-get-method (;7;) (canon lower (func $get-method) (memory $memory) (realloc $realloc) string-encoding=utf8))',
        'pathLowerOptions': '(core func $lower-get-path (;8;) (canon lower (func $get-path) (memory $memory) (realloc $realloc) string-encoding=utf8))',
        'fieldLowerOptions': '(core func $lower-get-field (;10;) (canon lower (func $get-field) (memory $memory) (realloc $realloc) string-encoding=utf8))',
        'headersLowerOptions': '(core func $lower-get-headers (;9;) (canon lower (func $get-headers)))'}
    for name, literal in literals.items():
        unique_fact(name, re.escape(literal), child1)
    need(not any('post-return' in lines[i] for i in child1), 'observer has no manual postreturn hook')
    return roots, dict(innerRootInstance=inner_instance, innerHandlerAlias=inner_alias,
        observerRootInstance=observer_instance, observerHandlerAlias=outer_alias, externalExportIndex=int(em[1]),
        sharedHttpTypesInstance=roots['wasi:http/types@0.2.10'], sharedIoErrorInstance=roots['wasi:io/error@0.2.10'],
        sharedStreamsInstance=roots['wasi:io/streams@0.2.10'], sharedStdoutInstance=roots['wasi:cli/stdout@0.2.10']), facts


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode or len(sys.argv) != 2 or re.fullmatch('[0-9a-f]{64}', sys.argv[1]) is None:
        raise RuntimeError('Root supplies exact closed composition result SHA under unoptimized Python -I -B')
    output = HERE / 'composition-review.json'
    need(not os.path.lexists(output), 'new exclusive composition review')
    construction, request, observer = prerequisites()
    checked(DRIVER)
    expected_input_closure = sorted(INPUTS.values(), key=lambda r: r['path'])
    owner_started, owner_terminal = owner()
    result_ref = row(HERE / 'composition-result.json')
    need(result_ref['sha256'] == sys.argv[1], 'actual closed result pin')
    build = doc(result_ref)
    need(build['state'] == 'CLONE_CANCEL_NEXT_V4_COMPOSITION_COMPLETED_UNREVIEWED_V1' and
         build['controller'] == DRIVER and build['error'] is None and build['finalizationErrors'] == [] and
         build['allFourRequestedToolStepsRawZero'] is build['finalInputsPreserved'] is True and
         build['runtimeInvoked'] is build['fullNextAccepted'] is False, 'actual completed composition state')
    need(build['protectedInputs'] == expected_input_closure, 'complete actual composition input closure')
    for key, value in dict(innerConstructionReview=CONSTRUCTION_REVIEW, innerConstructionRequest=construction['constructorRequest'],
            engineAdmission=construction['engineAdmission'], engine=construction['engine'], nativeMetadata=construction['nativeMetadata'],
            innerComponent=construction['component'], observerBinary=OBSERVER, observerCompositionReview=OBSERVER_REVIEW,
            metadataRuntimeReview=METADATA_REVIEW, observerSource=observer['observerSource'], observerManifest=observer['observerManifest'],
            observerProtocol=observer['observerProtocol']).items():
        need(build[key] == value, 'actual composition role: ' + key)
    steps = [('compose', [WAC['path'], 'plug', '--plug', build['innerComponent']['path'], OBSERVER['path'], '-o', str(WORK / 'next-with-observer.wasm')]),
             ('validate', [WASM_TOOLS['path'], 'validate', str(WORK / 'next-with-observer.wasm')]),
             ('wit', [WASM_TOOLS['path'], 'component', 'wit', str(WORK / 'next-with-observer.wasm')]),
             ('skeleton', [WASM_TOOLS['path'], 'print', '--skeleton', '--print-offsets', str(WORK / 'next-with-observer.wasm'), '-o', str(WORK / 'envelope.skeleton.wat')])]
    need(len(build['commands']) == 4, 'four exact requested tool steps')
    for command, (label, argv) in zip(build['commands'], steps):
        need(command['label'] == label and command['argv'] == argv and command['rawExitCode'] == 0 and
             command['timeout'] is False and command['error'] is None, 'actual requested tool command')
        for key in ('stdout', 'stderr'):
            need(command[key]['path'] == str(WORK / (label+'.'+key+'.log')), 'actual command capture path')
            raw(command[key])
        need(raw(command['stderr']) == b'', 'all four tool stderr captures empty')
    need(build['externalWit'] == build['commands'][2]['stdout'] and build['envelope']['path'] == str(WORK / 'next-with-observer.wasm') and
         build['actualSkeleton']['path'] == str(WORK / 'envelope.skeleton.wat'), 'actual output role paths')
    names = {label+'.'+key+'.log' for label, _ in steps for key in ('stdout', 'stderr')} | {'next-with-observer.wasm', 'envelope.skeleton.wat'}
    need({p.name for p in WORK.iterdir()} == names and all(p.is_file() and not p.is_symlink() for p in WORK.iterdir()), 'closed tool output namespace')
    magic, core_magic = b'\x00asm\x0d\x00\x01\x00', b'\x00asm\x01\x00\x00\x00'
    envelope = raw(build['envelope'], 128 * 1024**2)
    inner = raw(build['innerComponent'], 128 * 1024**2)
    binary = raw(OBSERVER)
    children = [s for s in sections(envelope, magic) if s[0] == 4]
    need(len(children) == 2, 'exactly two top-level raw child components')
    child_rows = []
    for index, (section, expected, role) in enumerate(zip(children, (inner, binary), ('innerComponent', 'observerBinary'))):
        _, start, payload, end = section
        need(envelope[payload:end] == expected, 'exact raw child input equality: ' + role)
        child_rows.append(dict(role=role, componentIndex=index, offset=start, payloadOffset=payload, end=end,
                               descriptor=build[role], rawBytesExactlyEqualInput=True))
    core_modules = []
    def inspect(data, depth=0):
        need(depth <= 16, 'observer component nesting bound')
        for kind, start, payload, end in sections(data, magic):
            need(kind != 9, 'observer component start absent')
            if kind == 1:
                need(all(s[0] != 8 for s in sections(data[payload:end], core_magic)), 'observer core start absent')
                core_modules.append(dict(bytes=end-payload, startSectionAbsent=True))
            if kind == 4:
                inspect(data[payload:end], depth+1)
    inspect(binary)
    need(len(core_modules) == 2, 'unchanged observer two core modules')
    external = world(build['externalWit'])
    need(set(external['imports']) == set(construction['emittedImports']) and len(external['imports']) == len(set(external['imports'])) == 13 and
         external['exports'] == construction['emittedExports'] == ['wasi:http/incoming-handler@0.2.10'], 'actual standard13 external world')
    roots, topology, facts = structure(build['actualSkeleton'])
    need(set(roots) == set(external['imports']), 'actual printed nominal import roots equal external world')
    wat = raw(observer['observerSource']).decode()
    handle = wat.split('(func (export "handle")', 1)[1].split('  (core instance $host-functions', 1)[0]
    calls = ['(call $reset)', '(call $get-method ', '(call $get-path ', '(call $get-headers ',
             '(call $get-field ', '(call $drop-fields ', '(call $inner-handler ', '(call $emit-metadata ']
    positions = [handle.index(call) for call in calls]
    need(positions == sorted(positions) and all(handle.count(call) == 1 for call in calls), 'pinned observer Source getter/drop/forward/emit order')
    need('(local.get $request)' not in handle.split('(call $inner-handler (local.get $request) (local.get $out))', 1)[1] and
         ';; Header classification is independent of method/path' in handle, 'normal own-forward and independent public-header snapshot Source')
    protocol = doc(observer['observerProtocol'])
    need(protocol['version'] == 4 and protocol['limits']['pythonModelMaximumAdmittedRecordBytes'] == 314, 'unchanged V4 protocol')
    self_ref = row(Path(__file__).resolve()); checked(self_ref)
    protect(full=True)
    proof = dict(schemaVersion=1, state='CLONE_CANCEL_NEXT_V4_OBSERVER_COMPOSITION_REVIEW_PASSED_V1',
        passed=True, verifiedPassed=True, verifiedDataReviewPassed=True, actualCompositionResult=result_ref,
        compositionOwnerStarted=owner_started, compositionOwnerTerminal=owner_terminal,
        innerConstructionReview=CONSTRUCTION_REVIEW, innerConstructionRequest=construction['constructorRequest'],
        innerComponent=construction['component'], engineAdmission=construction['engineAdmission'], engine=construction['engine'],
        nativeMetadata=construction['nativeMetadata'], innerComponentValidation=construction['validationTerminal'],
        envelope=build['envelope'], observerBinary=OBSERVER, observerCompositionReview=OBSERVER_REVIEW,
        metadataRuntimeReview=METADATA_REVIEW, observerSource=observer['observerSource'], observerManifest=observer['observerManifest'],
        observerProtocol=observer['observerProtocol'], actualSkeleton=build['actualSkeleton'],
        selectedImports=external['imports'], selectedExports=external['exports'], selectedStandardVersion='0.2.10',
        externalWorld=dict(wit=build['externalWit'], imports=external['imports'], exports=external['exports'], standardVersion='0.2.10'),
        rawChildSections=child_rows, observerCoreModules=core_modules, topology=topology, selectedSkeletonFacts=facts,
        rawChildBytesVerified=True, siblingDefiningInstancesVerified=True, sharedNominalResourceAliasesVerified=True,
        fieldsNominalResourceAliasesVerified=True, metadataGetterCanonicalOptionsVerified=True,
        synchronousLiftLowerWithInnerPostReturnVerified=True, innerExplicitPostReturnPreserved=True,
        observerManualPostReturnAbsent=True, internalIncomingHandlerImportComposedAway=True,
        allFourRequestedToolStepsRawZero=True, allFourToolStderrEmpty=True, originalOwnerRawZeroClean=True,
        observerNoMarkerBeforeInnerCallSourceVerified=True, normalFieldsChildDropBeforeOwnForwardSourceVerified=True,
        correlationSnapshotIndependentOfMethodAndPathSourceVerified=True, finalInputsPreserved=True,
        originalDriverPassed=False, originalOuterRawExitCode=1, oldMetadataProjected=False,
        protectedInputs=sorted(INPUTS.values(), key=lambda r: r['path']), reviewerSource=self_ref,
        bodyInstructionOrderScope='Skeleton elides core bodies. Pinned observer Source order is tied to tested3534 through214c ancestry and actual raw child equality; no independent instruction decode/runtime observation is claimed.',
        witnessScope='Future normal observer row can witness successful metadata snapshot and code after synchronous inner canonical call/postreturn; never observer own return, host/React/network EOF, private identity or cause.',
        allocatorScope='Unchanged64KiB and Source models do not prove arbitrary-input/OOM/getter-trap cleanup. Canonical lowering may trap before forwarding with borrowed child live.',
        priorObserverBehaviorScope='Seven accepted61bb cases exercise the unchanged observer/probe ancestry; no new Next runtime is inferred from that proof.',
        runtimeInvoked=False, runtimeAccepted=False, fullNextAccepted=False, oldV3JoinUpgraded=False,
        authorship='B authored new driver/reviewer and thin Next constructor. All Source/DATA checks here are self-contained; no old fixed-engine admission/helper/guard is imported or replayed.')
    receipt = save(output, proof)
    print(json.dumps(dict(review=receipt, innerComponent=construction['component'], envelope=build['envelope'], runtimeInvoked=False)), flush=True)


if __name__ == '__main__':
    main()
