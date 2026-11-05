"""Independent static/data-only stock-WT result reader; never imports any owner module."""
from pathlib import Path
import hashlib, json, os, re, stat

HERE = Path(__file__).resolve().parent
K = HERE.parent
SOURCE = K / 'ownership-gc-wasmtime-candidate-v1'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-wasmtime-v1')
SOURCE_SHA = 'c5d3ea491e81db5fad6c02e244bcc0cf784c8135a6ab1d5e552326f4f2e1ec35'
ROOT_SHA = '9b9a4108836d0eb51bbec7219f1f8567e030cc04514a5b6aede001664090e310'
COMPONENT = '52d99f4e95860b686d896c88f39b2fa5734eabeb433f48545ba814b2e45ce5f1'
ENGINE = '289df4455b56b50a9598c42a7d924aaa2adca7f5461f96782f5758a979e966c8'
RFC_TAG = 'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'
rows, assertions, leaves = {}, 0, 0

def check(ok, message):
    global assertions
    assertions += 1
    if not ok:
        raise AssertionError(message)

def digest(p):
    p = Path(p)
    a = p.lstat()
    check(stat.S_ISREG(a.st_mode), 'regular leaf: ' + str(p))
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    z = p.lstat()
    check((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns) ==
          (z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns), 'stable bytes')
    return dict(path=str(p), sha256=h.hexdigest(), bytes=z.st_size)

def verify(d, base=None):
    p = Path(d['path'])
    if not p.is_absolute():
        check(base is not None and '..' not in p.parts, 'explicit relative descriptor context')
        p = base / p
    check(p.is_absolute(), 'absolute physical data path')
    actual = rows.get(str(p))
    if actual is None:
        actual = digest(p); rows[str(p)] = actual
    check((actual['sha256'],actual['bytes']) == (d['sha256'],d['bytes']), 'hash/bytes: ' + str(p))
    return p

def unique_pairs(pairs):
    d = {}
    for k,v in pairs:
        check(k not in d, 'no duplicate JSON object key')
        d[k] = v
    return d

def parse(text):
    return json.loads(text, object_pairs_hook=unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON ' + x)))

def decode_wave(raw):
    text = raw.decode('utf-8', errors='strict')
    check(text.endswith('\n') and not text.endswith('\n\n'), 'one println LF')
    literal = text[:-1]
    check(len(literal) >= 2 and literal[0] == literal[-1] == '"', 'one WAVE quoted scalar')
    value, i = [], 1
    escapes = {'"':'"', "'":"'", '\\':'\\', 'n':'\n', 'r':'\r', 't':'\t'}
    while i < len(literal)-1:
        ch = literal[i]; i += 1
        if ch == '\\':
            check(i < len(literal)-1, 'complete WAVE escape')
            escape = literal[i]; i += 1
            if escape == 'u':
                check(i < len(literal)-1 and literal[i] == '{', 'WAVE Unicode braces')
                end = literal.find('}',i+1)
                check(end != -1 and end < len(literal)-1, 'complete Unicode escape')
                digits = literal[i+1:end]
                check(re.fullmatch('[0-9a-fA-F]{1,6}',digits) is not None, 'bounded scalar digits')
                cp = int(digits,16)
                check(cp <= 0x10ffff and not 0xd800 <= cp <= 0xdfff, 'Unicode scalar value')
                value.append(chr(cp)); i = end+1
            else:
                check(escape in escapes, 'known WAVE escape')
                value.append(escapes[escape])
        else:
            cp = ord(ch)
            check(ch != '"' and cp >= 0x20 and not 0x7f <= cp <= 0x9f and not 0xd800 <= cp <= 0xdfff,
                  'no unescaped quote/control/surrogate')
            value.append(ch)
    result = ''.join(value)
    check(len(result.encode('utf-16-le'))//2 <= 2097152, 'whole decoded code-unit bound')
    return result

def load(p):
    p = Path(p); d = digest(p); rows[str(p)] = d
    return parse(p.read_text())

def described(d, base=None):
    return load(verify(d, base))

def family(p, expected, exact=True):
    d = digest(p); check(d['sha256'] == expected, 'expected family SHA')
    ix = load(p); names = [r['path'] for r in ix['files']]
    check(len(names) == len(set(names)), 'unique finite indexed members')
    for r in ix['files']:
        verify(r, p.parent)
    if exact:
        physical = {q.relative_to(p.parent).as_posix() for q in p.parent.rglob('*') if q.is_file()}
        check(physical == set(names) | {'index.json'}, 'exact family membership')
    return ix

def typed_equal(a, b, path=''):
    global leaves
    check(type(a) is type(b), 'exact JSON type at ' + path)
    if isinstance(a, dict):
        check(set(a) == set(b), 'complete object fields at ' + path)
        for k in a:
            typed_equal(a[k], b[k], path + '/' + k)
    elif isinstance(a, list):
        check(len(a) == len(b), 'complete array at ' + path)
        for i,(av,bv) in enumerate(zip(a,b)):
            typed_equal(av,bv,path+'/'+str(i))
    else:
        check(a == b, 'exact whole value at ' + path); leaves += 1

root_path = K / 'ownership-gc-wasmtime-v1-root-results.json'
check(digest(root_path)['sha256'] == ROOT_SHA, 'actual Root report exact SHA')
root = load(root_path)
own = family(SOURCE/'index.json', SOURCE_SHA)
check(len(own['files']) == 60, 'actual source60 members')
freeze = load(SOURCE/'input-freeze.json')
check(len(freeze['files']) == 11279, 'full11279 original-context input rows')
check(len({r['path'] for r in freeze['files']}) == 11279, 'unique full closure paths')
for r in freeze['files']:
    verify(r)
refs = load(SOURCE/'references.json')
authority = described(root['rootAuthority'])
config = described(root['rootConfig'])
check(config['rootAction'] == root['rootAuthority'] and config['sourceIndexSha256'] == SOURCE_SHA, 'actual configuration')
for key in ['sourceIndexSha256','componentSha256','variant','invocation','freshProcesses','workerTimeoutMs','maxPipeBytes']:
    expected = dict(sourceIndexSha256=SOURCE_SHA,componentSha256=COMPONENT,variant='gc-off',invocation='validate()',
                    freshProcesses=3,workerTimeoutMs=600000,maxPipeBytes=16777216)[key]
    typed_equal(authority[key], expected, '/Root/' + key)
for key in ['nodeOracleAllowed','generatedJsAllowed','oomAllowed','resetAllowed','unsafePrototypeProbesAllowed',
            'otherVariantsAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim',
            'nativeGcCountObservedClaim','isolatedRootClaim','nativeFreeOrWipeClaim']:
    check(authority[key] is False, 'closed Root scope ' + key)
verify(authority['externalController']); verify(authority['externalMonitorEntry'])
family(Path(authority['externalMonitorIndex']['path']), authority['externalMonitorIndex']['sha256'])
for pair_key in ['sourceIndependentReview','jcoGcReview']:
    pair = authority[pair_key]
    family(Path(pair['index']['path']), pair['index']['sha256'])
    described(pair['result'])
jco_proof = described(authority['jcoGcReview']['result'])
jco_contract = described(authority['jcoGcContract'])
check(jco_proof['verifiedPassed'] is True and jco_proof['sourceIndexSha256'].startswith('5abe5ed8'), 'actual Jco-v2 peer role')
typed_equal(jco_contract['requiredCoverage'], jco_proof['coverage'])
family(Path(refs['artifactReview']['index']['path']), refs['artifactReview']['index']['sha256'])
artifact = described(refs['artifactReview']['result'])
artifact_contract = described(refs['artifactContract'])
typed_equal(artifact['artifacts'], refs['artifacts'])
typed_equal(artifact_contract['artifacts'], refs['artifacts'])
typed_equal(jco_contract['artifacts'], refs['artifacts'])
for d in refs['artifacts'].values():
    verify(d)
check(artifact['componentSha256'] == COMPONENT and artifact['engineSha256'] == ENGINE, 'actual GC component/native tuple')
check(artifact['emittedImports'] == [] and sorted(artifact['publicAbiFunctions']) == ['clear','inspect','run','validate'],
      'inherited static binary interface proof exact identity')
check(refs['artifacts']['component'] == root['component'], 'same actual component')
verify(root['component']); verify(root['wasmtime']); verify(refs['node'])
check(root['wasmtime'] == refs['wasmtime'] and root['wasmtime']['sha256'] ==
      'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c', 'stock WT42 pin')

actual_index = described(root['actualOutputIndex'])
check(len(actual_index['files']) == 23, 'actual23 indexed files')
for d in actual_index['files']:
    verify(d, OUT)
physical = {p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()}
check(physical == {d['path'] for d in actual_index['files']} | {'index.json','completion.json'}, 'actual25 file membership')
check(not any(p.is_symlink() for p in OUT.rglob('*')), 'no output symlinks')
check(stat.S_IMODE(OUT.stat().st_mode) == stat.S_IMODE((OUT/'processes').stat().st_mode) == 0o700, 'private root/processes')
completion = described(root['actualCompletion'])
verify(completion['index'], OUT); verify(completion['result'], OUT)
parent = described(root['actualParentResult'])
external = described(root['externalParentTerminal'])
for key in ['stdout','stderr','authority']:
    verify(external[key])
check(external['authority'] == root['rootAuthority'], 'observed parent actual Root descriptor')
check(external['rawExitCode'] == 0 and external['timeout'] is False and external['forcedCleanup'] is False,
      'parent terminal0 no timeout/forced cleanup')
check(external['interruptedSignals'] == external['signals'] == external['errors'] == external['remainingObservedPids'] == [],
      'no parent signals/errors/current known PIDs')
check(external['parentOwnedGroupGone'] is True and external['allObservedOwnedGroupsGone'] is True, 'all recorded groups gone')
check(len(external['finalGroups']) == 4 and all(r['alive'] is False for r in external['finalGroups']), 'four groups final gone')
parent_stdout = parse(Path(external['stdout']['path']).read_text())
check(parent_stdout['root'] == str(OUT), 'actual parent stdout output path')
verify(parent_stdout['index'], OUT); verify(parent_stdout['completion'], OUT)
check(Path(external['stderr']['path']).read_bytes() == b'', 'complete empty parent stderr')

oracle = described(root['nodeOracleReference'])
typed_equal(oracle, described(jco_contract['requiredExactDescriptors']['nodeOracle']))
check(oracle['node'] == 'v22.14.0' and oracle['tagHex'] == RFC_TAG, 'actual retained Node/RFC tag')
check(len(oracle['keys']) == 2, 'two retained raw/JWK oracle metadata cases')
node_keys = {r['format']:r for r in oracle['keys']}
wrapper_row = jco_contract['requiredExactDescriptors']['rawWrapper']
check(wrapper_row == root['rawJcoWrapper'], 'actual wrapper exact direct descriptor')
wrapper = described(wrapper_row)
check(wrapper['name'] == 'validate' and wrapper['args'] == [] and wrapper['kind'] == 'return' and
      wrapper['returnedType'] == 'string' and isinstance(wrapper['value'],str), 'actual whole Jco scalar')
jco_record = parse(wrapper['value'])
expected = described(refs['expectedCompleteRecord'])
typed_equal(jco_record, expected)

decoded, sessions, named_tags, sign_returns, bool_returns, pressure_total = [], [], 0, 0, [], 0
per_call = []
for ordinal in range(1,4):
    prefix = 'validate-' + str(ordinal)
    launch = load(OUT/'processes'/ (prefix+'.launch.json'))
    terminal = load(OUT/'processes'/ (prefix+'.terminal.json'))
    argv = load(OUT/(prefix+'-argv.json'))
    expected_args = ['run','--invoke','validate()',root['component']['path']]
    check(launch['args'] == terminal['args'] == argv['args'] == expected_args, 'literal zero-argument real API argv')
    check(launch['executable'] == terminal['executable'] == argv['executable']['path'] == root['wasmtime']['path'], 'actual stock executable')
    check(launch['detachedOwnedSession'] is True and launch['timeoutMs'] == terminal['timeoutMs'] == 600000, 'owned 600s CLI')
    check(terminal['status'] == 0 and terminal['signal'] is None and terminal['spawnError'] is None and
          terminal['timedOut'] is False and terminal['externalSignal'] is None and terminal['outputLimitExceeded'] is False,
          'raw actual child terminal success')
    check(terminal['signals'] == terminal['errors'] == [] and terminal['signalCount'] == 0 and terminal['closed'] is True and
          terminal['ownedGroupGone'] is True, 'clean child no signal/error')
    raw = verify(terminal['stdout']).read_bytes(); stderr = verify(terminal['stderr']).read_bytes()
    check(stderr == b'' and 0 < len(raw) < terminal['maxOutputBytes'] == 16777216, 'full untruncated CLI streams')
    # Strict independent WAVE string lexer consumes all raw bytes. The decoded
    # JSON contains escaped-apostrophe error text, so raw stdout is not JSON.
    value = decode_wave(raw)
    check(isinstance(value,str) and '\x00' not in value, 'one whole scalar string')
    recorded_string = load(OUT/(prefix+'-decoded-string.json'))
    check(recorded_string['value'] == value and recorded_string['ordinal'] == ordinal, 'independent whole decode vs retained scalar')
    verify(recorded_string['rawStdout']); verify(recorded_string['rawStderr']); verify(recorded_string['terminal'])
    check(recorded_string['rawStdout'] == terminal['stdout'] and recorded_string['rawStderr'] == terminal['stderr'], 'scalar raw origin')
    check(value == wrapper['value'], 'whole decoded bytes equal actual Jco string')
    record = parse(value)
    typed_equal(record, load(OUT/(prefix+'-record.json')))
    typed_equal(record, jco_record)
    typed_equal(record, expected)
    check([r['caseId'] for r in record['records']] == [0,1,2,3], 'complete ordered four inner records')
    check(all(v == 0 for v in record['entryCounters'].values()), 'fresh runtime counter origins')
    check(record['entryState']['strongApplicationKeyOwners'] == 0 and record['before']['cryptoOperationsAtSnapshot'] == 0,
          'no snapshot key operation')
    counts = []
    for i,r in enumerate(record['records']):
        check(r['completed'] is True, 'completed inner case')
        pressure = [4,4,8,0][i]
        check(r['gcObservation']['publicGcPressureRequests'] == pressure and r['gcObservation']['publicGcPressureRecords'] == pressure and
              r['gcObservation']['publicGcPressureRequested'] is (pressure > 0), 'scoped per-run pressure4/4/8/0')
        check(r['gcObservation']['actualNativeGcCountObserved'] is False and r['gcObservation']['entropyRequested'] is False, 'no native counter claim')
        expected_counter = [(1,2,2),(2,4,4),(2,8,8),(2,11,10)][i]
        check((r['counters']['keyImportsAttempted'],r['counters']['signCalls'],r['counters']['verifyCalls']) == expected_counter,
              'cumulative imports/sign/verify transitions')
        check(r['counters']['runCalls'] == i+1 and r['counters']['keyImportsFulfilled'] == expected_counter[0], 'run/import fulfillment counter')
        observations = r['observations']
        for observation in observations:
            if observation.get('phase') == 'before':
                check(observation['returned'] == {'type':'undefined'}, 'typed before observation')
            returned = observation.get('returned',{})
            if returned.get('type') == 'ArrayBuffer':
                check(returned['bytes'] == 32 and returned['fullHex'] == RFC_TAG and returned['fullBytesRetained'] is True,
                      'whole32-byte sign return equals Node/RFC')
                sign_returns += 1
            if returned.get('type') == 'boolean':
                check(type(returned['value']) is bool, 'exact verify boolean type'); bool_returns.append(returned['value'])
        operations = []
        if i < 2:
            operations = [(r['result']['format'],r['result']['operations'])]
        elif i == 2:
            operations = [('raw',r['result']['raw']),('jwk',r['result']['jwk'])]
        else:
            check(r['result']['positiveFullSignatureHex'] == RFC_TAG, 'guard-positive full signature'); named_tags += 1
            for refusal in ['signRefusal','verifyRefusal','ordinaryInvalid']:
                error = r['result'][refusal]
                check(error['kind'] == 'native-promise-rejection' and error['error']['typeError'] is True and
                      error['error']['name'] == 'TypeError', 'retained typed key refusal')
            check(all(v == 0 for v in r['result']['signConversionReads'].values()) and
                  all(v == 0 for v in r['result']['verifyConversionReads'].values()), 'zero conversion reads in bounded refusals')
        for fmt,operation in operations:
            key = operation['key']; nk = node_keys[fmt]
            for field in ['type','extractable','algorithm','usages']:
                typed_equal(key[field], nk[field])
            check(operation['firstSignatureHex'] == operation['secondSignatureHex'] == nk['tagHex'] == RFC_TAG, 'full named signature values')
            check(operation['valid'] is nk['valid'] is True and operation['invalid'] is nk['invalid'] is False, 'full verify truth values')
            check(operation['inputBeforeHex'] == operation['inputAfterHex'] == 'a5'*8+'4869205468657265'+'a5'*8, 'complete input sentinel/window bytes')
            typed_equal(operation['inputWindow'], dict(byteOffset=8,byteLength=8,backingBytes=24))
            check(operation['signatureBeforeHex'] == operation['signatureAfterHex'] == 'a5'*8+RFC_TAG+'a5'*8, 'complete signature sentinel/window bytes')
            named_tags += 2
        counts.append(dict(caseId=i,counters=r['counters'],pressureRequests=pressure))
    pressures = record['pressure']['records']
    check(len(pressures) == 16 and record['gcObservation']['publicGcPressureRequests'] == 16, 'all sixteen full public records')
    for i,p in enumerate(pressures):
        check(p['sequence'] == i+1 and p['phase'] == ['before-first-sign','between-signs','before-valid-verify','after-verifies'][i%4], 'pressure ordering')
        check(p['bytes'] == 64 and p['encodedHex'] == p['decodedHex'] == 'a5'*64, 'all64 pressure bytes and hex')
        check(p['forcedGcCounterObserved'] is False and p['isolatedTemporaryRootProved'] is False, 'no native/isolated-root instrumentation')
    pressure_total += len(pressures)
    check(record['released']['applicationReferencesReleased'] is True and record['after']['state']['strongApplicationKeyOwners'] == 0 and
          record['released']['collectionOrNativeFreeOrWipeObserved'] is False, 'application release only')
    check(record['after']['counters']['keyImportsAttempted'] == 2 and record['after']['counters']['signCalls'] == 11 and
          record['after']['counters']['verifyCalls'] == 10, 'full per-process final counters')
    per_call.append(dict(ordinal=ordinal,pid=terminal['pid'],rawStdout=digest(Path(terminal['stdout']['path'])),
                         scalarUtf8Bytes=len(value.encode()),innerRecords=4,counters=counts,fullPressureRecords=16))
    decoded.append(record); sessions.append(terminal)
check(len({s['pid'] for s in sessions}) == 3, 'three genuine fresh CLI PIDs')
check([s['pid'] for s in sessions] == root['wasmtimePids'], 'raw child IDs match recorded actual origins')
check({g['pgid'] for g in external['finalGroups']} == {external['pid']} | {s['pid'] for s in sessions}, 'four actual lifetimes linked')
check(named_tags == sign_returns == 27 and len(bool_returns) == 27 and sum(bool_returns) == 15 and
      len(bool_returns)-sum(bool_returns) == 12 and pressure_total == 48, 'independently derived aggregate values')

# Recheck the genuine finite native/frozen/normal physical closures as DATA.
native_root = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze')
native = load(native_root/'gc-off-freeze-receipt.json')
check(native['engineSha256'] == ENGINE and native['gcStress'] is True, 'genuine frozen GC engine')
check(len(native['copies']) == 1462, 'actual1462 frozen copies')
for d in native['copies']:
    verify(d)
    if d['original'] is not None:
        verify(dict(d,path=d['original']))
null_originals = [d['path'] for d in native['copies'] if d['original'] is None]
check(set(null_originals) == {str(native_root/name) for name in [
      'gc-off-embedding.after.commands.txt','gc-off-source-admission.json','gc-off-freezer-correction-control.json']},
      'exact three generated-data capture rows, no invented physical originals')
check({str(p) for p in native_root.rglob('*') if p.is_file()} ==
      {d['path'] for d in native['copies']} | {str(native_root/'gc-off-freeze-receipt.json')}, 'strict1463 GC freeze membership')
metadata = load(native_root/'gc-off.engine.wasm.build.json')
check(len(metadata['sourceManifest']) == 355 and metadata['engineSha256'] == ENGINE, 'genuine full355 metadata')
normal = load(K/'ownership-gc-native-candidate-v2/normal-protection.json')
check(len(normal['originals']) == 1387, 'normal1387 original reference entries')
for d in normal['originals']:
    verify(d['original']); verify(d['frozen'])
verify(normal['freezeReceipt'])
normal_root = Path(normal['freezeReceipt']['path']).parent
check({p.relative_to(normal_root).as_posix() for p in normal_root.rglob('*') if p.is_file()} ==
      set(normal['requiredNormalFreezeMembership']) and len(normal['requiredNormalFreezeMembership']) == 1391,
      'strict normal1391 membership/protection')
prelaunch = described(root['prelaunchHistory'])
check(prelaunch['prelaunchAttempt']['rawExitCode'] == 1 and prelaunch['actualLaunch']['removedFromTaskEnvironmentOnly'] == ['RUST_LOG'] and
      prelaunch['actualLaunch']['sourceChangedForRetry'] is False, 'retained prelaunch history, no source retry projection')

def save(name, value):
    with (HERE/name).open('x') as f:
        json.dump(value,f,indent=2); f.write('\n')

save('independently-decoded-record.json', decoded[0])
save('data-audit.json', dict(schemaVersion=1,state='INDEPENDENT_STOCK_WT_DATA_RECONSTRUCTION_PASSED_V1',
    assertions=assertions,typedLeavesCompared=leaves,distinctHashedFiles=len(rows),
    distinctHashedBytes=sum(r['bytes'] for r in rows.values()),sourceInputRows=11279,
    decodedWholeScalars=3,innerRecords=12,keyImports=6,signAttempts=33,verifyAttempts=30,
    namedFullSignatures=27,fullSignReturnObservations=27,verifyBooleanObservations=27,verifyTrue=15,verifyFalse=12,
    publicPressureRequests=48,full64BytePressureRecords=48,nativeGcCountObserved=False,
    perCall=per_call,actualIndexedFiles=23,actualFiles=25,normalFrozenMembers=1391,normalOriginalReferences=1387,
    gcFrozenCopies=1462,gcFrozenMembers=1463,gcOriginalReferenceRows=1459,gcNullOriginalGeneratedCaptures=null_originals,
    reviewerOwnerOrRuntimeActionsInvoked=False,
    environmentValuesIndependentlyReconstructed=False,freshBinaryWitDecodePerformed=False))
save('input-hashes.json', dict(schemaVersion=1,files=list(rows.values()),strictOriginalContexts=True,
                             readHashDataOnly=True,ownerHelpersOrRuntimeActionsInvoked=False))
print(json.dumps(dict(dataAudit=digest(HERE/'data-audit.json'),assertions=assertions,typedLeaves=leaves,
                      files=len(rows),rawScalars=3,fullTags=27,pressureRecords=48,ownerActionsInvoked=False)))
