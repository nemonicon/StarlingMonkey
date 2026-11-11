"""Root DATA checks for the actual V4 probe build; no helper, CLI or host replay."""
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def row(path):
    path = Path(path)
    require(path.is_absolute() and path.resolve() == path and not path.is_symlink(), 'Canonical file')
    before = path.stat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'Independent regular file')
    raw = path.read_bytes()
    require(path.stat() == before, 'Stable read')
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(ref):
    require(row(ref['path']) == ref, 'Current exact descriptor')
    raw = Path(ref['path']).read_bytes()
    require(row(ref['path']) == ref, 'Read bookend')
    return raw


def sections(raw, magic):
    require(raw[:8] == magic, 'Binary header')
    offset, result = 8, []
    while offset < len(raw):
        start, section_id = offset, raw[offset]
        offset += 1
        size = 0
        for shift in range(0, 35, 7):
            require(offset < len(raw), 'Truncated section length')
            byte = raw[offset]
            offset += 1
            require(shift != 28 or byte < 16, 'u32 section length')
            size |= (byte & 127) << shift
            if byte < 128:
                break
        else:
            raise ValueError('Unterminated section length')
        end = offset + size
        require(end <= len(raw), 'Section bound')
        result.append((section_id, start, offset, end))
        offset = end
    require(offset == len(raw), 'Exact binary framing')
    return result


def world(raw):
    text = raw.decode('utf8')
    require(text.startswith('package root:component;\n\nworld root {\n'), 'Actual printed root world')
    block = text.split('world root {\n', 1)[1].split('\n}', 1)[0]
    return {kind: re.findall(r'^  ' + kind + r' ([^;]+);$', block, re.M) for kind in ('import', 'export')}


def main():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1):
        raise RuntimeError('Use Python -I -B without -O and no arguments')
    result_ref = row(HERE / 'observer-v4-build-result.json')
    require(result_ref['sha256'] == '8fbdfc64b9e9a0b5937e333717c9ccde0a489dcbd9ae4aa6c2da886309b359fc', 'Actual completed build')
    build = json.loads(read(result_ref))
    require(build['allRequestedToolStepsPassed'] and build['finalInputsPreserved'] and
        build['constructorGuardBefore'] == build['constructorGuardAfter'] and
        build['error'] is None and not build['finalizationErrors'] and not build['runtimeInvoked'], 'Actual build state')
    commands = build['commands']
    require([x['label'] for x in commands] == ['parse', 'observer-validate', 'observer-wit', 'compose',
        'envelope-validate', 'envelope-wit', 'skeleton'], 'Seven selected steps')
    for command in commands:
        require(command['rawExitCode'] == 0 and not command['timeout'] and command['error'] is None, 'Raw tool success')
        read(command['stdout'])
        require(read(command['stderr']) == b'', 'Empty tool stderr')
    wasm_tools = dict(path='/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/cache/wasm-tools/1448/wasm-tools',
        sha256='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d', bytes=17556208)
    wac = dict(path='/private/tmp/starling-node-compat/next-standard-handler-wac-build-v1-first/target/debug/wac',
        sha256='6577e5eedeb0644025a8454c3d600ecad14a3788432c48e8d40b7ba56d271f5f', bytes=30168152)
    read(wasm_tools)
    read(wac)
    require(commands[0]['argv'] == [wasm_tools['path'], 'parse', build['observerSource']['path'],
        '-o', build['observerBinary']['path']], 'Actual selected parse input/output')
    require(commands[3]['argv'] == [wac['path'], 'plug', '--plug', build['innerComponent']['path'],
        build['observerBinary']['path'], '-o', build['envelope']['path']], 'Actual selected composition roles')
    inner_review = json.loads(read(build['innerConstructionReview']))
    require(inner_review['component'] == build['innerComponent'] and
        inner_review['rootAuthority'] == build['innerConstructionAuthority'] and
        inner_review['verifiedPassed'] and inner_review['completeReturnedImportAuditVerified'], 'Unchanged genuine probe inner')
    read(inner_review['componentAudit'])
    read(build['controller'])
    component_magic, module_magic = b'\0asm\x0d\0\x01\0', b'\0asm\x01\0\0\0'
    envelope, observer, inner = [read(build[k]) for k in ('envelope', 'observerBinary', 'innerComponent')]
    envelope_sections = sections(envelope, component_magic)
    children = [s for s in envelope_sections if s[0] == 4]
    require(len(children) == 2, 'Exactly two raw child components')
    child_rows = []
    for index, (section, expected, name) in enumerate(zip(children, (inner, observer), ('inner', 'observer'))):
        _, start, payload, end = section
        require(envelope[payload:end] == expected, 'Exact raw child equality: ' + name)
        child_rows.append(dict(kind=name, componentIndex=index, offset=start, payloadOffset=payload,
            end=end, bytes=end-payload, sha256=hashlib.sha256(expected).hexdigest(), rawBytesExactlyEqualInput=True))
    core_modules = []

    def inspect_component(raw):
        for kind, start, payload, end in sections(raw, component_magic):
            require(kind != 9, 'No observer component start')
            if kind == 1:
                core = sections(raw[payload:end], module_magic)
                require(all(x[0] != 8 for x in core), 'No observer core start')
                core_modules.append(dict(bytes=end-payload, startSectionAbsent=True))
            if kind == 4:
                inspect_component(raw[payload:end])

    inspect_component(observer)
    require(len(core_modules) == 2, 'Observer storage and implementation modules')
    selected_imports = ['wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10',
        'wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10', 'wasi:cli/stdout@0.2.10',
        'wasi:cli/environment@0.2.10', 'wasi:clocks/wall-clock@0.2.10', 'wasi:random/random@0.2.10',
        'wasi:filesystem/types@0.2.10', 'wasi:filesystem/preopens@0.2.10', 'wasi:cli/stderr@0.2.10',
        'wasi:http/outgoing-handler@0.2.10']
    selected_exports = ['wasi:http/incoming-handler@0.2.10']
    external = world(read(build['externalWit']))
    require(external == {'import': selected_imports, 'export': selected_exports}, 'Exact standard external world')
    standalone = world(read(build['observerWit']))
    require(standalone == {'import': ['wasi:http/types@0.2.10', 'wasi:http/incoming-handler@0.2.10',
        'wasi:io/error@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:cli/stdout@0.2.10'], 'export': selected_exports}, 'Exact standalone world')
    lines = read(build['actualSkeleton']).decode().splitlines()
    facts = {}

    def fact(name, literal):
        found = [(i+1, line) for i, line in enumerate(lines) if literal in line]
        require(len(found) == 1, 'Unique skeleton fact: ' + name)
        facts[name] = dict(lineOneBased=found[0][0], literal=found[0][1])
        return found[0][0]

    fact('innerLift', '(func $"#func143 handle" (@name "handle") (;143;) (type 58) (canon lift (core func $wasi:http/incoming-handler@0.2.10#handle) (post-return $cabi_post_wasi:http/incoming-handler@0.2.10#handle)))')
    inner_at = fact('innerInstantiate', '  (instance (;13;) (instantiate 0')
    alias_at = fact('innerExportAlias', '  (alias export 13 "wasi:http/incoming-handler@0.2.10" (instance (;14;)))')
    fact('observerLower', '(core func $lower-inner-handler (;1;) (canon lower (func $inner-handler)))')
    fact('observerLift', '(func $handle (;7;) (type $handle-type) (canon lift (core func $handle-core)))')
    observer_at = fact('observerInstantiate', '  (instance (;15;) (instantiate 1')
    external_at = fact('externalAlias', '  (alias export 15 "wasi:http/incoming-handler@0.2.10" (instance (;16;)))')
    fact('externalExport', '  (export (;17;) "wasi:http/incoming-handler@0.2.10" (instance 16))')
    for interface, instance in [('wasi:http/types@0.2.10', 4), ('wasi:io/error@0.2.10', 0),
            ('wasi:io/streams@0.2.10', 2), ('wasi:cli/stdout@0.2.10', 5)]:
        literal = '(with "' + interface + '" (instance ' + str(instance) + '))'
        require(sum(literal in line for line in lines[inner_at-1:alias_at-1]) == 1, 'Shared inner resource instance')
        require(sum(literal in line for line in lines[observer_at-1:external_at-1]) == 1, 'Shared observer resource instance')
    require('(with "wasi:http/incoming-handler@0.2.10" (instance 14))' in '\n'.join(lines[observer_at-1:external_at-1]), 'Internal handler binding')
    for name, literal in [('fieldsAlias', '(alias export $http "fields" (type $fields (;3;)))'),
            ('dropFields', '(core func $drop-fields (;0;) (canon resource.drop $fields))')]:
        fact(name, literal)
    for name, index in [('method', 7), ('path', 8), ('field', 10)]:
        target = {'method':'method', 'path':'path', 'field':'field'}[name]
        fact('metadataLower:'+name, f'(core func $lower-get-{target} (;{index};) (canon lower (func $get-{target}) (memory $memory) (realloc $realloc) string-encoding=utf8))')
    fact('metadataLower:headers', '(core func $lower-get-headers (;9;) (canon lower (func $get-headers)))')
    wat = read(build['observerSource']).decode()
    handle = wat.split('(func (export "handle")', 1)[1].split('  (core instance $host-functions', 1)[0]
    calls = ['(call $reset)', '(call $get-method ', '(call $get-path ', '(call $get-headers ',
        '(call $get-field ', '(call $drop-fields ', '(call $inner-handler ', '(call $emit-metadata ']
    positions = [handle.index(x) for x in calls]
    require(positions == sorted(positions) and all(handle.count(x) == 1 for x in calls), 'Source getter/drop/forward/emit order')
    require('(local.get $request)' not in handle.split('(call $inner-handler (local.get $request) (local.get $out))', 1)[1], 'No post-transfer request use')
    require('(local.set $count (i32.const 3))' not in handle and
        ';; Header classification is independent of method/path' in handle, 'No V3 correlation clearing')
    read(build['observerManifest'])
    protocol = json.loads(read(build['observerProtocol']))
    require(protocol['version'] == 4 and protocol['limits']['pythonModelMaximumAdmittedRecordBytes'] == 314, 'Selected V4 wire')
    proof = dict(schemaVersion=1, state='COORDINATED_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_DATA_REVIEW_PASSED_V1',
        verifiedPassed=True, verifiedDataReviewPassed=True, actualBuildResult=result_ref,
        **{key:build[key] for key in ('envelope', 'observerBinary', 'innerComponent', 'innerConstructionReview',
            'innerConstructionAuthority', 'observerSource', 'observerManifest', 'observerProtocol', 'actualSkeleton')},
        innerComponentAudit=inner_review['componentAudit'], selectedImports=selected_imports,
        selectedExports=selected_exports, selectedStandardVersion='0.2.10',
        externalWorld=dict(wit=build['externalWit'], imports=selected_imports, exports=selected_exports, standardVersion='0.2.10'),
        observerWorld=dict(wit=build['observerWit'], **standalone), rawChildSections=child_rows,
        selectedSkeletonFacts=facts, observerCoreModules=core_modules, checker=row(Path(__file__).resolve()),
        selectedTools=dict(wasmTools=wasm_tools, wac=wac),
        topology=dict(innerRootInstance=13, innerHandlerAlias=14, observerRootInstance=15, observerHandlerAlias=16,
            externalExportInstance=17, sharedHttpTypesInstance=4, sharedIoErrorInstance=0, sharedStreamsInstance=2, sharedStdoutInstance=5),
        bodyInstructionOrderScope='Printed skeleton elides core bodies. Source ordering plus actual parse argv and raw observer child equality ties the reviewed Source to this artifact; no independent core-body decode or runtime observation is claimed.',
        allocatorScope='Fixed guest64KiB is not a host allocation bound. Metadata lowering can trap before forwarding with fields child live. Inert models do not prove allocator/None/trapped cleanup behavior.',
        positiveWitnessScope='Future normal row witnesses successful snapshot and ordinary code after exact synchronous inner import returns; not observer return, host EOF, React EOF, identity or cause.',
        runtimeInvoked=False, runtimeAccepted=False, metadataCasesExecuted=False, actualMetadataBehaviorProved=False,
        fullNextAccepted=False, oldV3JoinUpgraded=False)
    for name in ['rawChildBytesVerified', 'siblingDefiningInstancesVerified', 'sharedNominalResourceAliasesVerified',
            'fieldsNominalResourceAliasesVerified', 'metadataGetterCanonicalOptionsVerified',
            'synchronousLiftLowerWithInnerPostReturnVerified', 'innerExplicitPostReturnPreserved',
            'observerManualPostReturnAbsent', 'internalIncomingHandlerImportComposedAway',
            'allSevenRequestedToolStepsRawZero', 'allSevenToolStderrEmpty',
            'observerNoMarkerBeforeInnerCallSourceVerified', 'normalFieldsChildDropBeforeOwnForwardSourceVerified',
            'correlationSnapshotIndependentOfMethodAndPathSourceVerified']:
        proof[name] = True
    with (HERE / 'actual-v4-composition-review.json').open('x') as handle:
        json.dump(proof, handle, indent=2)
        handle.write('\n')
    print(json.dumps(dict(review=row(HERE / 'actual-v4-composition-review.json'), observerBytes=len(observer),
        unchangedInnerBytes=len(inner), externalImports=len(selected_imports), runtimeInvoked=False)))


if __name__ == '__main__':
    main()
