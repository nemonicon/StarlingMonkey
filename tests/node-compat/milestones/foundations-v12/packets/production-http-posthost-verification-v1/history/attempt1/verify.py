"""Read existing post-host HTTP evidence. No tool, guest or host call."""
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
assert read(CAP/'http-component-pins.json')['state'] == 'REVIEWED_REAL_HTTP_COMPONENT_V1'
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

# Executed only as appended read-only verifier source, never a host runner.
import copy

BASE = CAP.parent
PREHOST = BASE/'production-http-prehost-verification-v1'
checked(PREHOST/'index.json','80c31ce1fc1618d5f85f1e75f4bbe6bae12aa7acc945e962229f1246f8edfd41')
for row in read(PREHOST/'index.json')['files']:
    checked(PREHOST/row['path'],row['sha256'],row['bytes'])
checked(PREHOST/'results.json','fe7880ab12e5a7dc326ede5f54013f00e42dfaf3031d5baf98bfc862d1976621')
phase = BASE/'production-http-phase-review-v1'
phase_index = checked(phase/'index.json')
assert phase_index.startswith('0f25af46') and phase_index.endswith('e83c')
for row in read(phase/'index.json')['files']:
    checked(phase/row['path'],row['sha256'],row['bytes'])
checked(phase/'results.json','47bb24ddbd5c66b5f2e7b3d71c28abf81785ab26e3a42129cdac8fe259bd216a')
checked(CAP/'http-component-pins.json','84a92618f415942e8c2afc70cc0734fbe35db284157bc2ddf319f7dc2cdc8aa3')
assert (CAP/'http-component-pins.json').read_bytes() == (phase/'reviewed-http-component-pins.json').read_bytes()
assert read(phase/'previous-null-http-component-pins.json')['component'] is None
pins = read(CAP/'http-component-pins.json')
assert pins['component']['state'] == 'reviewed-real-runtime-http-component'
expected_component = dict(seal)
expected_component.update(state='reviewed-real-runtime-http-component',
    preHostIndependentReviewResultsPath='tests/node-compat/foundation-scheduler/production-http-prehost-verification-v1/results.json',
    preHostIndependentReviewResultsSha256='fe7880ab12e5a7dc326ede5f54013f00e42dfaf3031d5baf98bfc862d1976621',runtimeAcceptanceClaim=False)
assert pins['component'] == expected_component
assert (CAP/'http-component-pins.json').resolve() not in source_map
assert (CAP/'index.json').resolve() not in source_map
checked(CAP/'index.json','c1ba69b0c6845dc453d8205a5e87d61c88c8633147a04d0c53d7966dbdb89c13')
assert len(read(CAP/'index.json')['files']) == 59
for row in read(CAP/'index.json')['files']:
    checked(CAP/row['path'],row['sha256'],row['bytes'])

checked(ROOT/'http-results.json','99a8799a1649285d5d544dc63d9a1dc046fc32e8fb3d90a1a9ee151740b6d1fe')
aggregate = read(ROOT/'http-results.json')
assert aggregate['state'] == 'PRODUCTION306_HTTP_BOTH_UNMODIFIED_HOSTS_PASSED'
assert aggregate['nativeAdmission'] == a['currentProductionAdmission']
assert aggregate['nativeSourceManifest'] == metadata['sourceManifest']
assert aggregate['sourceFilesVerified'] == manifest['inputs']
assert aggregate['component']['sha256'] == seal['componentSha256']
assert aggregate['component']['bytes'] == 63639194
assert aggregate['component']['emittedImports'] == EXPECTED and aggregate['component']['emittedExports'] == EXPORTS
assert aggregate['component']['clockDependency'] == a['clockDependency']
assert aggregate['protectedAbortGroups'] == {'public':16,'nested':4,'receivers':9,'total':29}
assert aggregate['instanceReuseClaim'] is False and aggregate['foundationSchema'] == 5
for row in aggregate['artifacts']:
    checked(row['path'],row['sha256'],row['bytes'])

wt_path = OUT/'wasmtime-v1/wasmtime-results.json'
wc_path = ROOT/'http-joint-wasmcloud-results.json'
checked(wt_path,'8856c0389de6bea514245cc8f5600356a341723c78b68cde1bc1b877b9648169')
checked(wc_path,'4215f60c2ee5060362afa657204df5b44f83e6ecba8f061053053bf677a87f0e')
wt,wc = read(wt_path),read(wc_path)
wt_binary = Path(wt['command'][0])
checked(wt_binary,'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')
assert wt['wasmtime'] == 'wasmtime 42.0.1 (6844a83b5 2026-02-25)'
assert wt['command'] == [str(wt_binary),'serve','--addr','127.0.0.1:0',str(component_path)]
assert wt['componentSha256'] == seal['componentSha256'] and wt['componentBytes'] == 63639194
assert wt['emittedImports'] == EXPECTED and wt['emittedExports'] == EXPORTS
assert wt['address'].startswith('http://127.0.0.1:')
wash = wc['host']
assert wash['unmodifiedOfficialBinary'] is True and wash['version'] == '2.11.0'
assert wash['sourceCommit'] == 'bc5acfb8e15f7d6d199ca940354d82e590c2d5ff'
assert wash['embeddedWasmtimeVersion'] == '48.0.7'
assert wash['binarySha256'] == '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954'
checked(wash['binaryPath'],wash['binarySha256'])
assert wc['component']['sha256'] == seal['componentSha256'] and wc['component']['bytes'] == 63639194
checked(wc['component']['deployedPath'],seal['componentSha256'],63639194)
assert wc['componentAudit'] == a
assert wc['component']['emittedImports'] == wc['component']['allowedImports'] == EXPECTED
assert wc['hostInspection']['success'] is True
assert wc['hostInspection']['emittedImports'] == EXPECTED and wc['hostInspection']['emittedExports'] == EXPORTS
assert wc['hostInspection']['emittedWit'] == wit
assert wc['command'][0] == wash['binaryPath'] and wc['command'][-1] == 'dev'
assert wc['configuration'] == read(Path(wc['configPath']))
checked(wc['configPath'])
assert wc['configuration']['wit']['skip_fetch'] is True
for key in ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts']:
    assert wc['configuration']['workload'][key] == wc['effectiveConfiguration']['workload'][key] == []
for key in ['plugins','host_plugins','components','volumes']:
    assert wc['configuration']['dev'][key] == []
assert wc['effectiveConfiguration']['dev']['service'] is False
assert wc['effectiveConfiguration']['dev']['wasi_otel'] is False and wc['effectiveConfiguration']['dev']['wasi_webgpu'] is False
assert wc['effectiveConfiguration']['dev']['wasm_proposals'] == []
isolation = wc['isolation']
assert isolation['publicListener'] is False and isolation['globalInstallationModified'] is False
assert isolation['userConfigOverridden'] is True and isolation['isolatedXdgDirectories'] is True
assert isolation['dockerUsed'] is False and isolation['natsUsed'] is False
for key in ['outgoingHostAllowlist','ipNameLookupAllowlist','hostLoopbackPortAllowlist','customHostPlugins','sidecars','volumes']:
    assert isolation[key] == []
assert isolation['address'] == wc['effectiveConfiguration']['dev']['address']
assert isolation['address'].startswith('127.0.0.1:')
user_config = Path(wc['command'][wc['command'].index('--user-config')+1])
checked(user_config)
assert read(user_config) == {}
assert wc['configInspectionCommand'][:5] == wc['command'][:5]
run_root = user_config.parent
checked(run_root/'host-results.json',sha(wc_path))
for host in [wt,wc]:
    assert host['process']['stopped'] is True and host['process']['exitStatus'] == {'code':0,'signal':None}
    checked(host['process']['logPath'])
    assert len(host['responses']) == 3 and host['retainedStateObserved'] is False

def normalized_body(body):
    body = copy.deepcopy(body)
    body.pop('requestTag')
    secure = body['native']['entropyIntegration']['secure']
    for key in ['bytes','uuid','multipartContentType']:
        secure.pop(key)
    return body

baseline = normalized_body(wt['responses'][0]['body'])
secure_bytes,secure_uuids = [],[]
host_summaries = []
for product,host in [('stock-wasmtime42',wt),('official-wash2.11',wc)]:
    counters = []
    for request,response in enumerate(host['responses'],1):
        assert response['status'] == 200
        body = response['body'];tag = '/node-compat?request='+str(request)
        assert body['requestTag'] == response.get('requestTag',response.get('request')) == tag
        assert body['schema'] == 1 and body['componentInstanceRequestCount'] == 1
        counters.append(body['componentInstanceRequestCount'])
        assert body['snapshotMarker'] == 'HTTP module initialized during componentization'
        assert normalized_body(body) == baseline
        native = body['native']
        assert native['coreVersion'] == 'sm-node-22.14.0-m0.11' and native['allocUnsafePolicy'] == 'zeroed-no-pool-direct-u8-v1'
        assert native['calls'] == 1 and native['strings'] == 381 and native['bytes'] == 250
        assert native['unavailableMethods'] == 91 and native['stubCalls'] == native['stubConstructors'] == 9
        assert native['globalBufferIdentity'] is True and native['staticCommonJS'] is True
        for key in ['unsupported','unsupportedConstructor']:
            failure = body[key]
            assert set(failure) == {'code','module','operation','profile'}
            assert failure['code'] == 'ERR_SM_NODE_UNSUPPORTED' and failure['module'] == 'node:child_process'
            assert failure['profile'] == 'sm-node-22.14.0-m0.11'
        entropy = native['entropyIntegration']
        assert entropy['policy'] == entropy['secure']['policy'] == 'runtime-only'
        assert len(entropy['snapshot']) == 4 and all(row['code']=='ERR_SM_ENTROPY_INITIALIZATION' for row in entropy['snapshot'])
        assert entropy['snapshotRsa']['succeeded'] is False
        assert entropy['rsa']['algorithm'] == 'RSASSA-PKCS1-v1_5' and entropy['rsa']['modulusLength'] == 2048
        assert re.fullmatch('[0-9a-f]{64}',entropy['secure']['bytes'])
        assert re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',entropy['secure']['uuid'])
        assert entropy['secure']['multipartContentType'].startswith('multipart/form-data; boundary=--StarlingMonkeyFormBoundary')
        secure_bytes.append(entropy['secure']['bytes']);secure_uuids.append(entropy['secure']['uuid'])
        foundation = native['foundations']
        assert foundation['schema'] == 5 and foundation['calls'] == 1
        assert foundation['aliases']['firstDeployedCall'] is True and len(foundation['aliases']['computedBareImports']) == 14
        for key in ['publicCases','nestedOnceCases','receiverCases']:
            assert foundation['protectedAbort'][key] == a['foundationOracles']['protectedAbort'][key]
        assert [len(foundation['protectedAbort'][key]) for key in ['publicCases','nestedOnceCases','receiverCases']] == [16,4,9]
        assert foundation['stringDecoder']['passed'] is True and foundation['streamWeb']['passed'] is True
    assert counters == [1,1,1]
    host_summaries.append(dict(product=product,requests=3,statuses=[200]*3,counters=counters,stopped=True,exitStatus={'code':0,'signal':None}))
assert len(set(secure_bytes)) == len(set(secure_uuids)) == 6
assert [host['counters'] for host in aggregate['hosts']] == [[1,1,1],[1,1,1]]
assert any('then-getter' in value and '1/1/0' in value and '0/0/0' in value for value in aggregate['limitations'])
for path in ROOT.glob('*.log'):
    checked(path)
for row in list(verified.values()):
    checked(row['path'],row['sha256'],row['bytes'])
result = dict(schemaVersion=1,state='INDEPENDENT_PRODUCTION_HTTP_POSTHOST_VERIFICATION_PASSED',verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    aggregateResultsSha256=sha(ROOT/'http-results.json'),componentSha256=seal['componentSha256'],componentBytes=63639194,
    engineSha256=a['engineSha256'],prehostReviewIndexSha256=sha(PREHOST/'index.json'),phaseReviewIndexSha256=phase_index,
    httpPhasePinSha256=sha(CAP/'http-component-pins.json'),capabilityFinalIndexSha256=sha(CAP/'index.json'),capabilityIndexedFiles=59,
    sourceInputsUnchanged=778,nativeSources=306,frozenEngineCopiesRehashed=335,liveComputedInputsRehashed=8,
    binaryImports=sorted(imports),binaryExports=exports,clockBinaryAndTypeGraphDurationOnlyU64=True,clockCallableImports=[],clockCoreImports=[],
    rawAndEmbeddedCoreNoncustomSectionsIdentical=True,priorCoreCustomSectionExplanationPreserved=True,
    hosts=host_summaries,washOfficialBinarySha256=wash['binarySha256'],stockWasmtimeSha256=sha(wt_binary),washEffectiveAllowlistsEmpty=True,
    noCustomPluginsSidecarsVolumes=True,sameComponentBytesOnBothHosts=True,allSixResponseBodiesMatchExceptRequestTagAndThreeExplicitRandomFields=True,
    observedDistinctSecureByteStrings=6,observedDistinctUuids=6,protectedAbortGroupsPerResponse=29,firstDeployedBareAliasesPerResponse=14,
    observedInstanceCounters=[1,1,1],instanceReuseOrRequestIsolationClaim=False,phaseChangeExcludedFromSourceSeal=True,
    verifiedFiles=list(verified.values()),limitations=[
        'This independently reads and validates recorded host execution, not a rerun of either host, guest, packager, Node oracle or source test.',
        'Normalized complete response equality removes only requestTag and secure bytes/UUID/multipart boundary; distinct samples are observations, not an entropy-quality or general isolation proof.',
        'Binary parsing rechecks root imports/exports, exact duration-only clock type and embedded core imports; complete Component Model validation is not rerun.',
        'Known callback-return getter Node1/1/0 versus guest0/0/0, Symbol.dispose identity and GC co-ownership limits remain.',
        'Full Node HTTP/process/stream compatibility, explicit reset, ALS/request teardown and performance/memory advantages are not established.',
        'Latest milestone acceptance/archive is Root-owned; these bounded HTTP host results alone do not close the full roadmap.'],
    hostGuestNativeNinjaNodeOraclePackagerOrValidationToolExecuted=False,existingSourceArtifactsConfigsOrResultsModified=False)
with (HERE/'results.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(dict(state=result['state'],resultSha256=sha(HERE/'results.json'),verifiedPaths=len(verified),hostRequests=6)))
