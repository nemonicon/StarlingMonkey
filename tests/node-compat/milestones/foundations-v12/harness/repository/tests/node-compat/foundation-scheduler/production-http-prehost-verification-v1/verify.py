"""Read existing HTTP component/source evidence. No tool, guest or host call."""
from pathlib import Path
import datetime
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CAP = REPO/'tests/node-compat/foundation-scheduler/production-followon-capability-v3'
ROOT = Path('/tmp/starling-node-compat/production-scheduler-runtime-v1/http')
OUT = ROOT/'http-joint'
FROZEN = Path('/tmp/starling-node-compat/production-scheduler-artifacts-v1/native-freeze')
EXPECTED = ['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:random/random@0.2.10']
EXPORTS = ['wasi:http/incoming-handler@0.2.10']
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
    assert digest is None or digest == value,path
    assert size is None or path.stat().st_size == size,path
    verified[str(path)] = dict(path=str(path),sha256=value,bytes=path.stat().st_size)
    return value


def uint(data,pos):
    value,shift = 0,0
    while True:
        assert pos < len(data) and shift <= 63
        byte = data[pos];pos += 1
        value |= (byte&127)<<shift
        if byte < 128:
            return value,pos
        shift += 7


def string(data,pos):
    size,pos = uint(data,pos)
    assert pos+size <= len(data)
    return data[pos:pos+size].decode(),pos+size


def sections(data,header):
    assert data[:8] == header
    pos = 8
    while pos < len(data):
        kind = data[pos];size,start = uint(data,pos+1);end = start+size
        assert end <= len(data)
        yield kind,data[start:end]
        pos = end
    assert pos == len(data)


def limits(data,pos):
    flags,pos = uint(data,pos)
    _,pos = uint(data,pos)
    if flags&1:
        _,pos = uint(data,pos)
    return pos


def core_imports(data):
    result = []
    for kind,part in sections(data,bytes.fromhex('0061736d01000000')):
        if kind != 2:
            continue
        count,pos = uint(part,0)
        for _ in range(count):
            module,pos = string(part,pos);name,pos = string(part,pos)
            tag = part[pos];pos += 1
            if tag == 0:
                _,pos = uint(part,pos);kind_name = 'function'
            elif tag == 1:
                assert part[pos] in [0x70,0x6f];pos = limits(part,pos+1);kind_name = 'table'
            elif tag == 2:
                pos = limits(part,pos);kind_name = 'memory'
            elif tag == 3:
                pos += 2;kind_name = 'global'
            elif tag == 4:
                pos += 1;_,pos = uint(part,pos);kind_name = 'tag'
            else:
                raise AssertionError(('Unsupported import descriptor',tag))
            result.append(dict(module=module,name=name,kind=kind_name))
        assert pos == len(part)
    return result


component_path = OUT/'native-profile-http.component.wasm'
checked(component_path,'ccc87ae3f9a00195ae243fa1077a07f9cd68e5ad3a8220708400187eee7a2ba6',63639194)
checked(OUT/'component-audit.json','e2d8a4732388c4e930877cb7666aa4ff65f19f6ae10dafecc3ffe7d5e3ca01fe')
checked(OUT/'http.bundle.mjs','7b98c8a62355b341a3a30082938bbb8f3729f9aba637e614169cf35302030625')
checked(ROOT/'http-inputs.json','ca2158472e95b2226ae249c16ac6086a2d8878d62add2c8d3e6a2e60bb3999a1')
checked(ROOT/'observed-http-component-seal.json')
candidate = read(ROOT/'observed-http-component-seal.json')
assert candidate['state'] == 'OBSERVED_HTTP_COMPONENT_SEAL_REQUIRES_REVIEW_NOT_HOST_ADMISSION'
seal = candidate['component']
assert seal['state'] == 'observed-runtime-http-component-not-admitted'
for key,path in [('componentPath',component_path),('auditPath',OUT/'component-audit.json'),('bundlePath',OUT/'http.bundle.mjs'),('inputsPath',ROOT/'http-inputs.json')]:
    assert seal[key] == str(path)
for key,path in [('componentSha256',component_path),('auditSha256',OUT/'component-audit.json'),('applicationBundleSha256',OUT/'http.bundle.mjs'),('inputsSha256',ROOT/'http-inputs.json')]:
    assert seal[key] == sha(path)
a = read(OUT/'component-audit.json')
assert a['componentSha256'] == seal['componentSha256'] and a['componentBytes'] == seal['componentBytes'] == 63639194
assert a['engineSha256'] == seal['engineSha256'] == '479821f8eefbc6aacbfe9df8538c5ee0a8745e530a474ecee8cb34251c0a1943'
assert seal['engineReceiptSha256'] == 'a89ddb7577528f380eff238b1437c5078c6c1cd266655e5c67902817fcafbcdc'
assert a['engine'] == str(FROZEN/'normal-runtime.engine.wasm')
checked(a['engine'],a['engineSha256'],9766342)
checked(a['engineMetadataPath'],seal['engineReceiptSha256'])
metadata = read(Path(a['engineMetadataPath']))
assert metadata['entropyPolicy'] == 'runtime-only' and metadata['gcStress'] is False
assert a['auditedBaseRevision'] == metadata['auditedBaseRevision'] == metadata['starlingMonkeyRevision']
assert a['componentizeJsRevision'] == metadata['componentizeJsRevision']
f = read(FROZEN/'normal-runtime-freeze-receipt.json')
checked(FROZEN/'normal-runtime-freeze-receipt.json','83be6fe14eaaceb96a446bb5423e9bfcaaa214dde0ac6b5bbe9e4a2d693625d8')
assert len(f['copies']) == 335
for row in f['copies']:
    checked(row['path'],row['sha256'],row['bytes'])

for key in ['selectedInterfaces','allowedImports','emittedImports']:
    assert a[key] == EXPECTED,key
assert a['emittedExports'] == EXPORTS and a['entropyPolicy'] == 'runtime-only'
assert a['applicationBundleExports'] == ['incomingHandler']
assert a['interfaceAudit']['state'] == 'verified-final-component'
assert a['interfaceAudit']['componentSha256'] == seal['componentSha256']
assert a['interfaceAudit']['selectedInterfaces'] == a['interfaceAudit']['emittedImports'] == EXPECTED
assert a['interfaceAudit']['unusedSelectedInterfaces'] == []
wit = (OUT/'emitted.wit').read_text()
checked(OUT/'emitted.wit')
assert wit == a['emittedWit']
assert sorted(re.findall(r'^\s*import ([^;]+);',wit,re.M)) == EXPECTED
assert re.findall(r'^\s*export ([^;]+);',wit,re.M) == EXPORTS
assert (OUT/'wit/profile.wit').read_text() == a['worldSource']
checked(OUT/'wit/profile.wit')

# Narrow, independent binary parsing: root instance imports/exports, actual
# embedded core imports, and the duration-only clock instance type itself.
data = component_path.read_bytes()
imports,exports,cores = [],[],[]
type_cursor = 0;type_definitions = {};clock_found = False
for kind,part in sections(data,bytes.fromhex('0061736d0d000100')):
    if kind == 7 and not clock_found:
        count,pos = uint(part,0)
        assert count == 1
        type_definitions[type_cursor] = part[pos:]
        type_cursor += count
    elif kind == 6 and not clock_found:
        count,pos = uint(part,0)
        for _ in range(count):
            assert part[pos:pos+2] == b'\x03\x00'
            _,pos = uint(part,pos+2)
            _,pos = string(part,pos)
            type_cursor += 1
        assert pos == len(part)
    elif kind == 10:
        count,pos = uint(part,0)
        for _ in range(count):
            assert part[pos] == 0;name,pos = string(part,pos+1)
            assert part[pos] == 5;type_index,pos = uint(part,pos+1)
            imports.append(name)
            if name == 'wasi:clocks/monotonic-clock@0.2.10':
                assert type_index == 5
                # instance{ type u64; export duration: type eq0 }; no function
                # declaration or function export exists in this instance type.
                assert type_definitions[5] == bytes.fromhex('420201770400086475726174696f6e030000')
                clock_found = True
        assert pos == len(part)
    elif kind == 11:
        count,pos = uint(part,0)
        for _ in range(count):
            assert part[pos] == 0;name,pos = string(part,pos+1)
            assert part[pos] == 5;_,pos = uint(part,pos+1)
            assert part[pos] == 0;pos += 1
            exports.append(name)
        assert pos == len(part)
    elif kind == 1:
        cores.append(dict(bytes=len(part),sha256=hashlib.sha256(part).hexdigest(),imports=core_imports(part)))
assert sorted(imports) == EXPECTED and exports == EXPORTS and clock_found
assert len(cores) == 3
all_core_imports = [row for core in cores for row in core['imports']]
assert not any(row['module'].startswith('wasi:clocks/') or row['module']=='wasi_snapshot_preview1' for row in all_core_imports)
assert cores[0]['imports'] == a['packagingAudit']['coreImports']
assert sorted({row['module'] for row in cores[0]['imports']}) == a['executableCoreInterfaces']
assert sorted({row['module'] for row in all_core_imports if row['module'].startswith('wasi:')}) == [name for name in EXPECTED if 'clocks/' not in name]
checked(OUT/'native-profile-http.core.wasm',a['packagingAudit']['finalWrapping']['coreSha256'])
raw_core = (OUT/'native-profile-http.core.wasm').read_bytes()
embedded_core = next(part for kind,part in sections(data,bytes.fromhex('0061736d0d000100')) if kind == 1)
core_section_hashes = lambda body:[(kind,hashlib.sha256(part).hexdigest()) for kind,part in sections(body,bytes.fromhex('0061736d01000000')) if kind != 0]
assert core_section_hashes(raw_core) == core_section_hashes(embedded_core)
core_custom_counts = [sum(kind == 0 for kind,_ in sections(body,bytes.fromhex('0061736d01000000'))) for body in [raw_core,embedded_core]]
assert core_custom_counts == [4,3]

checked(OUT/'component-types.json',a['clockDependency']['componentTypeGraph']['sha256'])
graph = read(OUT/'component-types.json')
clock = [(i,v) for i,v in enumerate(graph['interfaces']) if v.get('name')=='monotonic-clock' and graph['packages'][v['package']]['name']=='wasi:clocks@0.2.10']
assert len(clock) == 1
clock_index,clock = clock[0]
assert clock['functions'] == {} and list(clock['types']) == ['duration']
assert graph['types'][clock['types']['duration']]['kind'] == {'type':'u64'}
assert len(graph['worlds']) == 1 and any(v['interface']['id']==clock_index for v in graph['worlds'][0]['imports'].values())
assert len(graph['worlds'][0]['imports']) == 6 and len(graph['worlds'][0]['exports']) == 1
assert a['clockDependency']['typeOnly'] is True
assert a['clockDependency']['coreClockImports'] == a['clockDependency']['callableImports'] == []
checked(a['clockDependency']['tool']['path'],a['clockDependency']['tool']['sha256'])

# Packager/tool bytes and its two passes remain provenance, not rerun commands.
checked(OUT/'packaging-audit.json')
assert read(OUT/'packaging-audit.json') == a['packagingAudit']
pack = a['packagingAudit']
assert pack['initialBindingFeatures'] == pack['finalStubFeatures'] == ['http','random']
assert pack['finalWrapping']['adapters'] == []
prov = a['componentizerProvenance']
assert prov['selection'] == 'patched-import-i32-clock-v2' and prov['packagingVersion'] == 'componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1'
checked(prov['manifestPath'],prov['manifestSha256'])
package = Path(prov['modulePath']).parent.parent
for row in prov['checkedFiles']:
    checked(package/row['path'],row['sha256'])
checked(prov['lock']['path'],prov['lock']['sha256'])
assert a['preview1Adapter']['usedInFinalWrapping'] is False
checked(a['preview1Adapter']['path'],a['preview1Adapter']['sha256'],a['preview1Adapter']['bytes'])

# Rehash the held778 actual source list, including all eight LIVE reopened
# inputs, and bind the recorded pre-copy/post-copy + final admission recheck.
checked(CAP/'input-freeze.json','d7e4dddef6da2d36aa091001c0d17adf4dbe1d0d07ff743fdd8318853e1a54ad')
manifest = read(CAP/'input-freeze.json')
assert len(manifest['inputs']) == 778
source_map = {}
for row in manifest['inputs']:
    path = (CAP/row['path']).resolve()
    checked(path,row['sha256'],row['bytes']);source_map[path] = row
before,after = a['computedLiveInputChecks']['beforeCopy'],a['computedLiveInputChecks']['afterCopy']
assert before == after and before['state'] == 'EXACT_EIGHT_LIVE_HTTP_INPUTS_MATCH_SEAL'
assert before['files'] == 8 and before['witFiles'] == 7 and before['adapterFiles'] == 1
for row in before['inputs']:
    live = (REPO/row['name']).resolve()
    assert source_map[live]['sha256'] == row['sha256']
    checked(live,row['sha256'],row['bytes'])
    if row['name'].endswith('package.wit'):
        copied = OUT/'wit/deps'/Path(row['name']).parent.name/'package.wit'
        checked(copied,row['sha256'],row['bytes'])
inputs = read(ROOT/'http-inputs.json')
assert inputs['state'] == 'PRODUCTION306_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING'
assert inputs['sourceInputClosure'] == a['currentProductionAdmission']['inputClosure']
assert inputs['nativeAdmission'] == a['currentProductionAdmission']
checked(OUT/'production-admission-complete.json')
complete = read(OUT/'production-admission-complete.json')
assert complete['consumedInputsRecheckedAfterRun'] is True
assert complete['engineSha256'] == a['engineSha256'] and complete['inputClosure'] == inputs['sourceInputClosure']
assert read(CAP/'http-component-pins.json')['component'] is None and not (CAP/'index.json').exists()
assert a['applicationBundleSha256'] == sha(OUT/'http.bundle.mjs')
bundle = (OUT/'http.bundle.mjs').read_text()
assert not re.search(r'createBufferModule|createEventsFacade|reference-kernel|node_modules/(?:buffer|unenv)',bundle)
assert len(a['bundledModules']) == 49 and not any('/run-' in p or 'fatal' in p for p in a['bundledModules'])
for name in a['bundledModules']:
    if name.startswith('\0'):
        continue
    path = Path(name.removesuffix('.native-profile.mjs'))
    assert path.resolve() in source_map,path
assert a['foundationOracles']['protectedAbort']['counts'] == {'public':16,'nested':4,'receivers':9,'total':29}
assert len(a['foundationOracles']['dynamicBareAliases']) == 14
for name,digest in a['foundationOracles']['protectedAbort']['sources'].items():
    checked(REPO/'tests/node-compat/foundation-add-abort/production-native-m0.10'/name,digest)
for row in list(verified.values()):
    checked(row['path'],row['sha256'],row['bytes'])
result = dict(schemaVersion=1,state='INDEPENDENT_HTTP_COMPONENT_PREHOST_ARTIFACT_REVIEW_PASSED',verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    componentSha256=seal['componentSha256'],componentBytes=63639194,auditSha256=sha(OUT/'component-audit.json'),bundleSha256=sha(OUT/'http.bundle.mjs'),inputsSha256=sha(ROOT/'http-inputs.json'),
    actualEngineSha256=a['engineSha256'],frozenEngineCopiesRehashed=335,heldSourceInputsRehashed=778,bundleModules=49,
    binaryRootImports=sorted(imports),binaryRootExports=exports,binaryClockInstanceTypeIndex=5,binaryClockDurationOnlyTypeHex='420201770400086475726174696f6e030000',
    rawCoreInputSha256=a['packagingAudit']['finalWrapping']['coreSha256'],embeddedNativeCoreSha256=cores[0]['sha256'],allElevenNonCustomCoreSectionPayloadsIdentical=True,rawAndEmbeddedCoreCustomSectionCounts=core_custom_counts,firstVerifierAssumptionFailurePreserved=True,
    typeGraphClockOnlyU64Duration=True,clockCallableImports=[],clockCoreImports=[],embeddedCoreModules=cores,
    recordedLiveComputedInputsBeforeAfterIdentical=True,liveComputedInputsCurrentlyRehashed=8,finalAdmissionRecheckRecorded=True,
    protectedOrdinaryGroups=29,firstDeployedBareAliasChecksInFixture=14,httpComponentPinStillNull=True,capabilityFinalIndexAbsent=True,
    noConcretePrehostArtifactBlockerFound=True,verifiedFiles=list(verified.values()),
    limitations=['This is read-only structural/provenance review before host execution, not a successful HTTP request or runtime compatibility result.',
                'The independent parser checks concrete root import/export encodings, embedded core imports and the exact duration-only clock instance type; it does not repeat full Component Model validation or execute wasm-tools.',
                'Packager pre/post facts are bound recorded evidence; current source/binary hashes and copied WIT are independently rehashed without reproducing historical packaging.',
                'HTTP type constructors do not grant outgoing-handler, DNS, socket, TLS, filesystem, CLI/environment or clock operations; only the six selected standard0.2.10 interfaces are admitted.',
                'Known callback-return getter counts Node1/1/0 versus guest0/0/0, Symbol.dispose registry identity difference and GC co-ownership limitations are not closed by the positive29 corpus.',
                'Observed counters establish neither instance reuse nor request isolation. Reset/ALS/request cleanup and full Node HTTP remain open.',
                'Root must review/adopt the excluded HTTP phase pin and seal the final capability index before serial same-byte stock Wasmtime/wasmCloud host gates.'],
    nativeGuestHostNinjaPackagerOrValidationToolExecutedByVerifier=False,existingSourceOrArtifactModified=False)
with (HERE/'results.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(dict(state=result['state'],resultSha256=sha(HERE/'results.json'),verifiedPaths=len(verified),componentSha256=seal['componentSha256'])))
