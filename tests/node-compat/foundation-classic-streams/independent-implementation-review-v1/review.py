"""Independent source/byte and Node-host evidence review; no native or guest."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent/'implementation-candidate-v1'
REPO = HERE.parents[3]
HOST = Path('/tmp/starling-node-compat/independent-classic-implementation-host-v1')
verified = {}


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            value.update(chunk)
    return value.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def checked(path,digest=None,size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(),path
    value = sha(path)
    assert digest is None or value == digest,path
    assert size is None or path.stat().st_size == size,path
    verified[str(path)] = dict(path=str(path),sha256=value,bytes=path.stat().st_size)
    return value


assert sys.argv[1:] in [['before'],['after']]
phase = sys.argv[1]
checked(SOURCE/'index.json','743037e278438d7947c871f17b8b9195dc26088ddc054a2293d1e6c4ef2f72f8')
index = read(SOURCE/'index.json')
assert len(index['files']) == 223 and index['bytes'] == 3594506
for row in index['files']:
    checked(SOURCE/row['path'],row['sha256'],row['bytes'])
checked(SOURCE/'source-receipt.json','a62bec02a53ca7cbe82bfe1408bc39c3693635771d2fffd622f9d1d1d7b40e46')
checked(SOURCE/'input-freeze.json','38aa03039f7f8097af1e9d5411a3085fac3d9f1595cbb33faa727e38e1abc555')
inputs = read(SOURCE/'input-freeze.json')['files']
assert len(inputs) == len({row['path'] for row in inputs}) == 342
for row in inputs:
    path = Path(row['path'])
    checked(path if path.is_absolute() else REPO/path,row['sha256'],row['bytes'])
receipt = read(SOURCE/'source-receipt.json')
assert receipt['ancestorNative306Checked'] is True
assert receipt['upstreamVendorFiles'] == receipt['transformedFiles'] == 24
assert receipt['rootNamespaceExports'] == 24 and receipt['promiseNamespaceExports'] == 3
assert receipt['nativeIntegrationApplied'] is False and receipt['nativeCompilerExecuted'] is False
assert receipt['componentOrGuestExecuted'] is False and receipt['guestSchedulerExecuted'] is False
assert receipt['enginePins'] is None and receipt['newNativeSourceCount'] is None
checked(SOURCE/'factories.generated.h','f8503c92d87d6ad0bb6f5961c3eac2c8e2eab2e76224867c6363dc9bbfc7404e')
checked(SOURCE/'native-integration.UNAPPLIED.patch','e13a6563551dd5047f4793307a79eea84928d2503b847493de0c1fa1be12a414')
transform = read(SOURCE/'transformation-receipt.json')
assert len(transform['rawSources']) == len(transform['transformations']) == 24
for row in transform['rawSources']:
    checked(SOURCE/'vendor'/row['path'],row['sha256'],row['bytes'])
for row in transform['transformations']:
    checked(SOURCE/'source'/row['path'],row['afterSha256'])
checked(SOURCE/'classic-core.generated.mjs',transform['generatedSha256'])
manifest = read(SOURCE/'export-manifest.classic-streams.node-v22.14.0.json')
assert manifest['profileVersion'] == 'sm-node-22.14.0-m0.12'
assert set(manifest['modules']) == {'node:stream','node:stream/promises'}
assert manifest['requiredHostInterfaces'] == []
assert manifest['modules']['node:stream']['aliases'] == ['stream']
assert manifest['modules']['node:stream/promises']['aliases'] == ['stream/promises']
facade = (SOURCE/'classic-streams.mjs').read_text()
assert "('readable'in value&&'writable'in value)" in facade
assert 'get(){return promises[name]}' in facade
assert "value:'ERR_SM_NODE_UNSUPPORTED'" in facade and "value:'node:stream'" in facade
assert 'isUint8ArrayBrand(value)' in (SOURCE/'source/readable-stream/lib/stream.js').read_text()
patch = (SOURCE/'native-integration.UNAPPLIED.patch').read_text()
assert 'core::EventLoop::create_internal_next_tick(cx)' in patch
assert 'JS::RootedValue events_module(cx)' in patch and 'JS::RootedValue decoder_module(cx)' in patch
assert 'JS::RootedObject argument(cx, JS_NewPlainObject(cx));' in patch
assert patch.index('JS::RootedObject argument(cx, JS_NewPlainObject(cx));') < patch.index('JS::RootedObject next_tick(cx, core::EventLoop::create_internal_next_tick(cx));') < patch.index('if (!argument || !next_tick) return false;')
for row in read(SOURCE/'native-integration-pins.json')['before'].items():
    checked(REPO/row[0],row[1])

if phase == 'before':
    result = dict(state='CLASSIC_SEALED_SOURCE_VERIFIED_BEFORE_HOST_REPLAY',verifiedFiles=list(verified.values()))
    with (HERE/'before.json').open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(phase=phase,indexedFiles=223,inputFiles=342,readPaths=len(verified))))
else:
    for row in read(HERE/'before.json')['verifiedFiles']:
        checked(row['path'],row['sha256'],row['bytes'])
    checked(HOST/'node-results.json')
    observed = read(HOST/'node-results.json')
    original = read(SOURCE/'node-final-acceptance-results.json')
    assert observed == original
    assert (HOST/'node-results.json').read_bytes() == (SOURCE/'node-final-acceptance-results.json').read_bytes()
    assert observed['groups'] == 19 and len(observed['unsupportedChecks']) == 48
    assert len(observed['unsupportedOverloadChecks']) == 17 and len(observed['customPromisifyDefaultMutation']) == 4
    for name in ['node.stdout','node.stderr','generate.stdout','generate.stderr']:
        checked(HOST/name)
    assert (HOST/'node.stderr').read_bytes() == (HOST/'generate.stderr').read_bytes() == b''
    amendment = HERE.parent/'implementation-candidate-v1-allocation-order-amendment'
    checked(amendment/'index.json','f723d0c997bb59bfcbbe6f82fcc5797ab45e82fa7ac416bd8367d4f73fd0db72')
    for row in read(amendment/'index.json')['files']:
        checked(amendment/row['path'],row['sha256'],row['bytes'])
    corrected = (amendment/'register.cpp').read_text()
    parent = (SOURCE/'integration/builtins/node-compat/register.cpp').read_text()
    original_block = '  JS::RootedObject argument(cx, JS_NewPlainObject(cx));\n  JS::RootedObject next_tick(cx, core::EventLoop::create_internal_next_tick(cx));\n  if (!argument || !next_tick) return false;'
    corrected_block = '  JS::RootedObject argument(cx, JS_NewPlainObject(cx));\n  if (!argument) return false;\n  JS::RootedObject next_tick(cx, core::EventLoop::create_internal_next_tick(cx));\n  if (!next_tick) return false;'
    assert parent.count(original_block) == 1 and corrected.count(corrected_block) == 1
    assert parent.replace(original_block,corrected_block) == corrected
    am = read(amendment/'source-receipt.json')
    assert am['parentIndexSha256'] == sha(SOURCE/'index.json')
    assert am['sameFactoryHeaderSha256'] == sha(SOURCE/'factories.generated.h')
    assert am['sameNodeHostReportSha256'] == sha(SOURCE/'node-final-acceptance-results.json')
    assert am['allocationFailurePathTested'] is False and am['nativeCompilerExecuted'] is False
    result = dict(schemaVersion=1,state='INDEPENDENT_CLASSIC_SOURCE_HOST_AND_ALLOCATION_AMENDMENT_REVIEW_PASSED',
        reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceIndexSha256=sha(SOURCE/'index.json'),indexedTextFilesVerified=223,
        inputFreezeSha256=sha(SOURCE/'input-freeze.json'),inputFilesVerified=342,rawSources=24,transformedSources=24,rootExports=24,promiseExports=3,
        native306Unchanged=True,nativePatchUnapplied=True,nativeCompilerOrGuestExecuted=False,
        hostDifferentialGroups=19,hostDependencyArms=2,deferredCallConstructChecks=48,unsupportedOverloadChecks=17,defaultMutationChecks=4,
        freshHostReportByteIdentical=True,generatedFactoryCheckPassed=True,
        resolvedFindings=[
            dict(area='Web Transform/pair overload',resolution='Final facade rejects ordinary readable/writable pair shapes before private pipeline Web dispatch;17 ordinary overload refusals cover the path.'),
            dict(area='Mutable promises/default graph',resolution='Custom-promisify getters now read current promises[name]; four pinned-Node/candidate mutation observations confirm aliases while named bindings remain snapshots.'),
            dict(area='Byte helper named recursion',resolution='Owner-preserved earlier valid-host failure is corrected by the distinct isUint8ArrayBrand helper; fresh ordinary group covers it.')],
        sourceFindings=[
            'Finite private CJS loader caches before execution and exposes no public require/process;24 original modules and explicit transformed deltas are hash-bound.',
            'Byte conversion retains JS-owned ArrayBuffer windows using captured installed Buffer.from; BufferList aggregation uses captured Uint8Array.set and bounded allocUnsafe, no new native span or allocator transfer.',
            'Proposed bridge uses actual evaluate_factory/define_builtin_module/create_internal_next_tick APIs. Retained Events/Decoder, dependency object, nextTick, graph and module values are Rooted across allocating calls.',
            'Queued JavaScript callback/argument/state objects would rely on the existing TaskQueue trace; this source review does not prove candidate guest callback/GC ownership.',
            'Default-OFF CMake option has explicit core/Events/StringDecoder/ticks/native Abort prerequisites; selected interfaces[] is a proposal, not emitted-import evidence.'],
        originalNativeAllocationFinding=dict(status='RESOLVED_BY_SEPARATELY_REVIEWED_AMENDMENT',amendmentIndexSha256=sha(amendment/'index.json'),correctedNativePatchSha256=am['completeNativePatchSha256'],source='native-integration.UNAPPLIED.patch',issue='Checks argument allocation only after the second allocating create_internal_next_tick call.',requiredIntegration='Use the separately reviewed full corrected0574 patch, which returns immediately on failed argument creation. Original sealedv1 remains unchanged; native compilation/admission is still a separate future gate.',evidence='Source fallibility reasoning only; no genuine OOM, fault, DEBUG or unsafe path executed.'),
        verifiedFiles=list(verified.values()),limitations=[
            'Host scheduler is Node process.nextTick, one dependency arm uses a JS reference hex kernel and host Node codecs, and the abort option symbol is not native guest resistance proof.',
            'No native classic module, component, guest scheduler, moving-GC, initializer, retained/fresh host or same-byte target-host acceptance is established.',
            'A corrected registration proposal, new finite source/producer/admission policy and actual feature/command receipts are required before building/selecting this feature.',
            'Snapshot/GC callback retention, unsupported call/new initialization, encoding/queue limits, cancellation/handled and fatal scheduling, namespace/alias/static-CJS and final import audits remain future component gates.',
            'Getter/Symbol.dispose/captureRejections/ALS/reset/request teardown/first-classic and full reflection limitations remain; no performance or memory benefit is inferred.'])
    with (HERE/'results.json').open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(state=result['state'],resultSha256=sha(HERE/'results.json'),hostGroups=19,allocationOrderAmendmentReviewed=True,nativeIntegrationUncompiled=True)))
