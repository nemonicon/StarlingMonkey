"""Independent recorded GC-result reader. No owner modules or tools run."""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
FAMILY=HERE.parent/"component-validation-activated-v2"
FAMILY_SHA="bfb689fe993b9f55abc4848e77930c773597e769a7f08a0f2404914d82227835"
OUTPUT=Path("/tmp/starling-node-compat/consumers355-v2-gc-component-validation-v1")
ENGINE_SHA="b378dea3bafa01d3b85728883d20c1e61a8a22807f2614cb6eceeb615da910e7"
NORMAL_BRIDGE_SHA="e9ea6523942ccd1b1399764301de117b936557eef843c3ef77fbed53a38fe44b"
NODE_SHA="e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0"
WT_SHA="a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c"
verified,cache,checks={},{},[]

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def equal(actual, expected, label):
    def same(a, b):
        if type(a) is not type(b):
            return False
        if isinstance(a, dict):
            return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
        if isinstance(a, list):
            return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
        return a == b
    if not same(actual, expected):
        with (HERE / 'counterexample.json').open('x') as stream:
            json.dump({'label': label, 'actual': actual, 'expected': expected}, stream, ensure_ascii=True)
            stream.write('\n')
        raise AssertionError('Full recorded value mismatch; see counterexample.json: ' + label)

def identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns

def pinned(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    key = (str(path.resolve()), identity(before))
    if key not in cache:
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        assert identity(path.lstat()) == identity(before), str(path)
        cache[key] = h.hexdigest()
    digest = cache[key]
    if expected is not None:
        assert digest == expected, (str(path), digest, expected)
    if size is not None:
        assert before.st_size == size, str(path)
    row = {'path': str(path), 'sha256': digest, 'bytes': before.st_size}
    if str(path) in verified:
        assert verified[str(path)] == row
    verified[str(path)] = row
    return row

def data(path, digest=None, size=None):
    row = pinned(path, digest, size)
    value = Path(path).read_bytes()
    assert sha(value) == row['sha256'] and len(value) == row['bytes']
    return value

def document(path, digest=None, size=None):
    return json.loads(data(path, digest, size))

def descriptor(row):
    return pinned(row['path'], row['sha256'], row['bytes'])

def check(name, condition=True):
    assert condition, name
    checks.append(name)

def indexed(root, digest, count=None):
    value = document(root / 'index.json', digest)
    if count is not None:
        assert len(value['files']) == count
    assert len({r['path'] for r in value['files']}) == len(value['files'])
    for row in value['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        pinned(root / row['path'], row['sha256'], row['bytes'])
    return value

def inventory(root):
    entries = []
    for current, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
            assert kind, str(path)
            entries.append({'path': str(path.relative_to(root)), 'kind': kind})
    return sorted(entries, key=lambda row: row['path'])

def uleb(raw, at):
    value = 0
    for shift in range(0, 35, 7):
        assert at < len(raw)
        byte = raw[at]
        at += 1
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, at
    raise AssertionError('Invalid bounded ULEB')

def sections(raw, version):
    assert raw[:8] == b'\0asm' + version
    at, result = 8, []
    while at < len(raw):
        tag = raw[at]
        size, start = uleb(raw, at + 1)
        end = start + size
        assert end <= len(raw)
        result.append((tag, raw[start:end]))
        at = end
    assert at == len(raw)
    return result

def command_source(command):
    words = shlex.split(command)
    assert words.count('-c') == 1
    return words[words.index('-c') + 1]

def decode_cli_string(raw):
    # Public Wasmtime scalar strings use Rust-debug quoting, including \u{...}.
    # Decode the transport only; never alter or omit the returned JSON value.
    source = raw.decode().strip()
    normalized, at = [], 0
    while at < len(source):
        char = source[at]
        if char != '\\':
            normalized.append(char)
            at += 1
            continue
        assert at + 1 < len(source)
        next_char = source[at + 1]
        if next_char == 'u' and source[at + 2:at + 3] == '{':
            end = source.find('}', at + 3)
            assert end > at + 3 and re.fullmatch('[a-fA-F0-9]+', source[at + 3:end])
            codepoint = int(source[at + 3:end], 16)
            assert 0 <= codepoint <= 0x10ffff
            normalized.append(json.dumps(chr(codepoint), ensure_ascii=True)[1:-1])
            at = end + 1
        elif next_char == "'":
            normalized.append("'")
            at += 2
        elif next_char == '0':
            normalized.append('\\u0000')
            at += 2
        else:
            normalized.append('\\' + next_char)
            at += 2
    value = json.loads(''.join(normalized))
    assert isinstance(value, str)
    return value

ROOT_RECEIPT=HERE.parent/'gc-component-validation-v1-root-results.json'
ROOT_SHA='5c31a47222b1749a5fe200de12e780a600e774d982e071f530afdec591009c1d'
COMPONENT_SHA='ff4c2aaeb4590b206b4c2ec494f06411c3efd377d8e00d358c4675ba6a053421'
root=document(ROOT_RECEIPT,ROOT_SHA,3473)
assert root['state']=='ROOT_CONSUMERS355_COMBINED_OWNER_GC_VALIDATION_RAW_PASS_V1'
assert root['rawExitCode']==0 and root['engineSha256']==ENGINE_SHA
for key in ['authority','reviewedNormalBridge','sourceFamilyIndex','terminal','stdout','stderr','report','completion','outputClosure','component']:
    descriptor(root[key])
authority=document(root['authority']['path'],root['authority']['sha256'])
assert authority['state']=='ROOT_CONSUMERS355_COMBINED_OWNER_GC_VALIDATION_AUTHORITY_V1'
assert authority['variant']=='gc-off' and authority['engineSha256']==ENGINE_SHA
assert authority['ordinaryReleaseGCWithStrongCombinedOwnersOnly']is True
assert authority['isolatedTemporaryRootClaimAllowed']is False and authority['debugOomFaultRawMemoryOrResetAllowed']is False
bridge=document(root['reviewedNormalBridge']['path'],NORMAL_BRIDGE_SHA,2237)
assert bridge['state']=='ROOT_REVIEWED_CONSUMERS355_NORMAL_VALIDATION_V1'
assert bridge['sourceFamilyIndexSha256']==FAMILY_SHA and bridge['driverExitCode']==0 and bridge['namespacePassed']is True
assert bridge['normalEngineSha256']=='661ef79418ab139c9a7bcebb57eb36c17c3c398f67c80bbcd680cb95839f0c79'
for key in ['report','completion','rootActualResults','independentResultReview','independentResultReceipt','independentResultDetails']:
    descriptor(bridge[key])
normal_report=document(bridge['report']['path'],bridge['report']['sha256'])
normal_complete=document(bridge['completion']['path'],bridge['completion']['sha256'])
assert len(normal_report['records'])==190 and normal_report['namespacePassed']is True and normal_complete['reportSha256']==bridge['report']['sha256']
normal_peer=Path(bridge['independentResultReview']['path']).parent
indexed(normal_peer,bridge['independentResultReview']['sha256'],28)
normal_module_row=next(row for row in normal_complete['artifacts']if row['path'].endswith('/0001-module-before.raw.txt'))
normal_module=document(normal_module_row['path'],normal_module_row['sha256'],normal_module_row['bytes'])
check('explicitRootGCauthority and genuine e9 reviewed-normal bridge/report/completion/28fileproof')

indexed(FAMILY,FAMILY_SHA,47)
seal=document(FAMILY/'input-freeze.json','f6bcb9e6703cc03a36b7d4949d3fcb2100caee830c04f6bc6983a625b78edd29')
assert len(seal['inputs'])==7268 and len({row['path']for row in seal['inputs']})==7268
for row in seal['inputs']:
    pinned(FAMILY/row['path'],row['sha256'],row['bytes'])
for tree in seal['toolTrees']:
    assert str(Path(tree['path']).resolve())==tree['realPath']
    equal(inventory(Path(tree['path'])),tree['entries'],'tool-tree-membership')
for row in seal['toolLinks']:
    path=Path(row['path'])
    assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve())==row['resolvedTarget']
    if row['targetKind']=='file':pinned(path.resolve(),row['targetSha256'],row['targetBytes'])
    else:assert row['targetKind']=='directory'and path.resolve().is_dir()
assert len(seal['toolTrees'])==2 and len(seal['toolLinks'])==22
config=document(FAMILY/'activation.json')
assert config['nativeConfiguredSourceRoot']=='/private/tmp/starling-node-compat/consumers-source-v2'
assert config['componentToolRoot']==str(FAMILY/'packaging-tools')and config['operationalAdmission']is False
for row in [config['liveAdapter']]+config['liveWit']:descriptor(row)
assert len(config['liveWit'])==7 and config['liveAdapter']['bytes']==53512
check('full47/7268/twotooltrees22links/LIVE8/currentnative-vs-toolcontext closure')

pins=document(FAMILY/'reviewed-pins.json',config['pinsSha256'])
review=document(FAMILY/'root-review.json',config['rootReviewSha256'])
assert pins['state']=='ROOT_REVIEWED_STREAM_CONSUMERS355_VALIDATION_BOOTSTRAP_V1'
assert review['reviewedPinsSha256']==config['pinsSha256']and review['sourceFiles']==355 and review['operationalAdmission']is False
pin=pins['variants']['gc-off']
for key in ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:
    assert pin[key]==config['actual']['gc-off'][key]
assert pin['engineSha256']==ENGINE_SHA and pin['reviewRequired']is False
for row in pin['frozenFiles']:descriptor(row)
freeze=document(pin['freezeReceiptPath'],pin['freezeReceiptSha256'])
metadata=document(pin['enginePath']+'.build.json',pin['receiptSha256'])
assert len(pin['frozenFiles'])==len(freeze['copies'])==1164
for row in freeze['copies']:descriptor(row)
assert len(metadata['sourceManifest'])==freeze['nativeInputsVerified']==355
assert len(metadata['componentizeSourceManifest'])==freeze['externalEmbeddingInputsVerified']==3
for row in metadata['sourceManifest']:pinned(Path(freeze['sourceRoot'])/row['path'],row['sha256'])
for row in metadata['componentizeSourceManifest']:pinned(Path(freeze['componentizeSourceRoot'])/row['path'],row['sha256'])
assert metadata['gcStress']is True and metadata['oomTesting']is False and metadata['entropyPolicy']=='off'
assert metadata['streamConsumersEnabled']is True and metadata['zlibEnabled']is True
options=metadata['observedCMakeOptions']
for key,value in {'CMAKE_BUILD_TYPE':'Release','NODE_COMPAT_GC_STRESS':'ON','NODE_COMPAT_OOM_TESTING':'OFF','NODE_COMPAT_STREAM_CONSUMERS':'ON','NODE_COMPAT_ZLIB':'ON','ENABLE_BUILTIN_WEB_TEXT_CODEC':'ON'}.items():assert options[key]==value
database=document(pin['commandsPath'],pin['compileCommandsSha256'])
commands=[row['command']for row in database]
layout=metadata['internalTickPolicy']['actualLayoutCompileCommands']
strict=metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']
private=metadata['streamConsumersPolicy']['actualPrivateTargetCompileCommands']
embedding=metadata['actualEmbeddingCompileCommands']
assert [len(layout),len(strict),len(private),len(embedding)]==[62,4,6,1]
assert all(command in commands for command in layout+strict+private)
expected_private={str(Path(config['nativeConfiguredSourceRoot'])/'builtins/node-compat'/name)for name in ['buffer.cpp','register.cpp','entropy-policy.cpp','entropy-bridge.cpp','stream-web-kernel.cpp','zlib/kernel.cpp']}
actual_macros={name:set()for name in ['NODE_COMPAT_GC_STRESS','NODE_COMPAT_STREAM_CONSUMERS']}
for command in commands+embedding:
    words=shlex.split(command)
    assert words.count('-O3')==1 and '-O0'not in words and '-DNDEBUG'in words
    assert not any(word.startswith(('-DNODE_COMPAT_OOM_TESTING','-UNODE_COMPAT_OOM_TESTING'))for word in words)
    for name in actual_macros:
        values=[word for word in words if word.startswith(('-D'+name,'-U'+name))]
        if values:
            assert values==['-D'+name+'=1']
            actual_macros[name].add(str(Path(command_source(command)).resolve()))
assert all(value==expected_private for value in actual_macros.values())
buffer_source=data(Path(freeze['sourceRoot'])/'builtins/node-compat/buffer.cpp').decode()
assert '#ifdef NODE_COMPAT_GC_STRESS'in buffer_source and 'JS::PrepareForFullGC(cx)'in buffer_source
assert 'JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API)'in buffer_source and 'stress_gc(cx)'in buffer_source
installation=metadata['streamConsumersPolicy']['installationOrder']
frozen_install=next(row for row in pin['frozenFiles']if row['sha256']==installation['sha256'])
install_text=data(frozen_install['path'],installation['sha256']).decode()
assert install_text.index('NS_DEF(builtins::web::text_codec)')<install_text.index('NS_DEF(builtins::node_compat)')
assert metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
check('genuine355/frozen1164/native62/strict4/embedding1/exactprivate6GC-consumermacros/Release/noOOM')

report=document(root['report']['path'],root['report']['sha256'],root['report']['bytes'])
complete=document(root['completion']['path'],root['completion']['sha256'],root['completion']['bytes'])
assert report['state']=='CONSUMERS355_COMBINED_OWNER_GC_VALIDATION_PASSED'and report['variant']=='gc-off'
assert report['sourceFamilyIndexSha256']==FAMILY_SHA and report['engineSha256']==ENGINE_SHA and report['nativeSourceFiles']==355
assert report['namespacePassed']is True and len(report['records'])==4 and report['initializerRecords']==[]and report['denials']==[]and report['componentizeCalls']==1
assert complete['reportSha256']==root['report']['sha256']and complete['requiresIndependentExitZero']is True and report['requiresIndependentTerminalExitZero']is True
paths=set()
for row in complete['artifacts']:
    assert row['path']not in paths and Path(row['path']).is_relative_to(OUTPUT)
    paths.add(row['path']);descriptor(row)
assert len(paths)==46
items=inventory(OUTPUT)
regular={str(OUTPUT/row['path'])for row in items if row['kind']=='file'}
links=[str(OUTPUT/row['path'])for row in items if row['kind']=='symlink']
assert regular==paths|{str(OUTPUT/'completion.json')}and len(regular)==47 and links==[str(OUTPUT/'node_modules')]
equal(complete['outputLinks'],root['outputLinks'],'outputlink Root/completion')
for row in complete['outputLinks']:
    assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve())==row['resolvedTarget']
closure=document(root['outputClosure']['path'],root['outputClosure']['sha256'])
assert closure['regularFiles']==47 and {row['path']for row in closure['files']}==regular
equal(closure['links'],complete['outputLinks'],'Rootclosurelinks')
for row in closure['files']:descriptor(row)
check('exact46artifacts+completion47regularfiles andoneoutputlink/fullRootclosure')

terminal=document(root['terminal']['path'],root['terminal']['sha256'])
equal(terminal['argv'],authority['argv'],'actualGCcommand')
equal(terminal['selectedEnvironment'],authority['selectedEnvironment'],'actualGCenvironment')
assert terminal['rawExitCode']==0 and terminal['observedByRoot']is True
pinned(terminal['argv'][0],NODE_SHA)
stdout_rows=[json.loads(line)for line in data(root['stdout']['path'],root['stdout']['sha256']).decode().splitlines()]
assert data(root['stderr']['path'],root['stderr']['sha256'])==b''
assert stdout_rows[-1]['state']==report['state']and stdout_rows[-1]['output']==str(OUTPUT)
progress=[document(path)for path in sorted((OUTPUT/'progress').glob('*.json'))]
assert len(progress)==15 and [row['sequence']for row in progress]==list(range(1,16))
compact=[row for row in stdout_rows if row.get('event')=='correctness-progress']
assert len(compact)==15 and len(stdout_rows)==16
for actual,durable in zip(compact,progress):
    assert durable['schemaVersion']==1 and durable['partialObservationOnly']is True and durable['requiresFinalCompletionAndExternalExitZero']is True and durable['runtimeAcceptanceClaim']is False
    detail={k:v for k,v in durable.items()if k not in ['schemaVersion','sequence','event','atUtc','partialObservationOnly','requiresFinalCompletionAndExternalExitZero','runtimeAcceptanceClaim']}
    equal(actual,{'event':'correctness-progress','sequence':durable['sequence'],'eventName':durable['event'],**detail},'explicit compact/durable progress shapes')
check('RootexactNode22command/raw0 andall15durableprogressrecords/finalstdout')

component=data(root['component']['path'],COMPONENT_SHA,13118622)
parts=sections(component,b'\x0d\x00\x01\x00')
assert sum(uleb(raw,0)[0]for tag,raw in parts if tag==10)==0
assert sum(uleb(raw,0)[0]for tag,raw in parts if tag==11)==3
wit=data(OUTPUT/'consumer_validation.emitted.wit').decode()
assert wit==report['fixture']['emittedWit']and not re.search(r'\bimport\b',wit)
public_exports=['run: func(index: u32) -> string','module-contract: func() -> string','ordinary-gc: func() -> string']
equal(re.findall(r'export\s+([^;]+);',wit),public_exports,'GCpublic3scalarWIT')
core=data(OUTPUT/'consumer_validation.core.wasm');sections(core,b'\x01\x00\x00\x00')
assert core in component and b'consumer_validation.core.wasm'in data(OUTPUT/'consumer_validation.js')
assert data(OUTPUT/'consumer_validation.d.ts')==data(normal_peer/'evidence/consumer_validation.d.ts')
assert report['fixture']['componentSha256']==COMPONENT_SHA and report['fixture']['componentBytes']==len(component)
assert report['interfaceAudit']['emittedImports']==[]and report['interfaceAudit']['componentSha256']==COMPONENT_SHA
equal(report['bundle'],normal_report['bundle'],'samefullguestbundleasreviewednormal')
assert report['bundle']['code'].encode()==data(OUTPUT/'guest.bundle.mjs')
check('actualGCcomponentouterimports0/public3/core/glue/dts andnormal-identicalfullguestbundle')

labels=['0001-module-before','0002-ordinary-GC-1','0003-ordinary-GC-2','0004-ordinary-GC-3','0005-ordinary-GC-module-after','0006-fresh-Wasmtime-ordinary-GC']
assert len(list((OUTPUT/'calls').glob('*.raw.txt')))==6
values,observations={},[]
for label in labels:
    path=OUTPUT/'calls'/(label+'.raw.txt')
    raw=data(path).decode();value=json.loads(raw)
    equal(document(OUTPUT/'calls'/(label+'.observed.json')),value,'complete observed/raw '+label)
    envelope=document(OUTPUT/'calls'/(label+'.transport.json'))
    equal(envelope,{'type':'string','codeUnits':len(raw.encode('utf-16-le',errors='surrogatepass'))//2,'valueStoredSeparatelyAsRawString':True},'typed transport '+label)
    values[label]=value
    observations.append({'id':label,'raw':verified[str(path)],'fullValueDecoded':True,'transportType':'string'})
equal(values[labels[0]],normal_module,'fullGCmodulebefore versusreviewednormalnamespace')
module_after=json.loads(json.dumps(normal_module));module_after['gcCalls']=3
equal(values[labels[4]],module_after,'fullGCmoduleafter onlygcCounter3')
counts=[1,2,3,1]
for label,count,record in zip([labels[1],labels[2],labels[3],labels[5]],counts,report['records']):
    expected={'calls':0,'gcCalls':count,'value':'\u20ac','operations':[f'{i:02x}'for i in range(8)],'ownerHex':'41','applicationStrongOwnerRetained':True,'decoderSpansAwaitAndNativeHex':True,'vmTemporaryRootsIsolated':False,'nativeBlobInvoked':False}
    equal(values[label],expected,'fullGCobservation '+label)
    equal(record['value'],expected,'report fullGCobservation '+label)
    assert record['id']==label
    equal(record['rawFile'],verified[str(OUTPUT/'calls'/(label+'.raw.txt'))],'report/rawdescriptor '+label)
    equal(record['transportFile'],verified[str(OUTPUT/'calls'/(label+'.transport.json'))],'report/typeddescriptor '+label)
check('all6fulltypedrawvalues/2fullnamespaces and4Euro/8hex/owner/counterobservations exact')

wt=document(OUTPUT/'processes/wasmtime-ordinary-gc.terminal.json')
launch=document(OUTPUT/'processes/wasmtime-ordinary-gc.launch.json')
assert wt['args']==['run','--invoke','ordinary-gc()',str(OUTPUT/'consumer_validation.component.wasm')]
assert wt['args']==launch['args']and wt['executable']==launch['executable']
pinned(wt['executable'],WT_SHA)
assert wt['status']==0 and wt['signal']is None and wt['spawnError']is None and wt['timedOut']is False and wt['outputLimitExceeded']is False
assert wt['closed']is True and wt['ownedGroupGone']is True and wt['terminalExitZeroObserved']is True
assert wt['timeoutMs']==launch['timeoutMs']==600000 and wt['maxOutputBytes']==16777216
inner=decode_cli_string(data(wt['stdout']['path'],wt['stdout']['sha256'],wt['stdout']['bytes']))
assert inner==data(OUTPUT/'calls'/(labels[5]+'.raw.txt')).decode()
equal(json.loads(inner),values[labels[5]],'wholeWTouterstring/fullinnerJSON')
assert data(wt['stderr']['path'],wt['stderr']['sha256'],wt['stderr']['bytes'])==b''
check('freshWTwholeRustdebug/nestedreturn exact andraw0/closedownedgroup/no timeout')

assert report['scope']['ordinaryCombinedOwnerGcOnly']is True and report['scope']['normalRecordsExecuted']==0
for key in ['vmTemporaryRootsIsolated','rawGlobalWebPassedToConsumer','nativeBlobInvoked','HTTPBodyCancellationOrReuseInferred','old293Or350RuntimeTransferred','operationalAdmission']:assert report['scope'][key]is False
assert report['scope']['noTiming']is True and root['actualGCCountMeasured']is False and root['combinedStrongOwnersOnly']is True
for row in verified.values():
    h=hashlib.sha256()
    with Path(row['path']).open('rb')as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    assert h.hexdigest()==row['sha256']and Path(row['path']).stat().st_size==row['bytes'],row['path']
check('finalfullsource/native/tool/normalbridge/GCraw/outputbytes unchanged; boundedcoownersclaims')
result={'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_COMBINED_OWNER_GC_ACTUAL_RESULTS_PASSED','rootReceiptSha256':ROOT_SHA,'reviewedNormalBridgeSha256':NORMAL_BRIDGE_SHA,'normalIndependentReviewIndexSha256':bridge['independentResultReview']['sha256'],'sourceFamilyIndexSha256':FAMILY_SHA,'engineSha256':ENGINE_SHA,'componentSha256':COMPONENT_SHA,'componentBytes':len(component),'rawOuterExitCode':0,'reportSha256':root['report']['sha256'],'completionSha256':root['completion']['sha256'],'rawCallsDecoded':6,'gcRecords':4,'retainedGcCalls':[1,2,3],'freshWasmtimeGcCalls':1,'namespaceCounters':{'calls':[0,0],'gcCalls':[0,3]},'ownTypedRefusalsInNamespaceObservations':12,'outputValue':'\u20ac','nativeBufferHexOperationsPerGCRecord':8,'ownerHex':'41','publicWitExports':public_exports,'outerHostImports':[],'completionArtifacts':46,'regularOutputFiles':47,'outputLinks':1,'sourceFamilyFiles':47,'sourceConsumedRows':7268,'toolTrees':2,'toolLinks':22,'frozenCopies':1164,'nativeSources':355,'externalSources':3,'nativeCommands':62,'strictCommands':4,'privateGCMacroCommands':6,'privateConsumerMacroCommands':6,'embeddingCommands':1,'verifiedLexicalPaths':len(verified),'uniquePhysicalVersionsHashed':len(cache),'checks':checks,'passed':len(checks),'concreteResultBlockers':[],'strongApplicationOwnersRetained':True,'decoderSpansAwaitAndNativeHex':True,'actualGCCountMeasured':False,'vmTemporaryRootsIsolated':False,'privateGCExportsOrRawGuestMemoryUsed':False,'normal38CasesRerunUnderGC':False,'disabledGateTransferred':False,'runtimeBackendProofTransferred':False,'operationalAdmission':False,'fullNodeCompatibilityResetReuseHTTPOrPerformanceClaim':False,'reviewerOwnerPreflightBootstrapVerifierFactoryBundlerComponentizerCompilerNodeGuestHostOrBenchmarkActions':False,'limitations':['Four ordinaryGC public observations retain strong application/closure/VM owners; no isolated temporary-root guarantee.','Eight Buffer hex operations are observed; actual GC events/counts are not measured.','The reviewed normal bridge is a prerequisite only, not a new190-record replay underGC.','No DEBUG/OOM/fault/privateGC/rawguestmemory/allocatortrim/reset probe.','Source metadata zlib runtimeBackendProof remainsfalse/null/null; no codec operational proof transferred.','In-process Jco calls retain no independent cancellation/deadline guarantee.']}
for name,value in [('results.json',result),('observations.json',observations),('verified-paths.json',list(verified.values()))]:
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2,ensure_ascii=True);stream.write('\n')
print(json.dumps({'state':result['state'],'passed':len(checks),'rawCalls':6,'gcRecords':4,'verifiedLexicalPaths':len(verified),'reviewerOwnerActions':False}))
