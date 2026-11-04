"""Read-only verification of explicitly completed focused production gates.
Only subprocesses are wasm-tools --version/component wit --json parsers.
No application, guest, compiler, packager, Wasmtime or wasmCloud is executed.
"""
from pathlib import Path
import hashlib,json,os,re,stat,subprocess,sys
BASE=Path(__file__).resolve().parent
PACKETS=BASE.parent
REPO=PACKETS.parents[2]
ROOT=Path('/tmp/starling-node-compat/production-scheduler-runtime-v1')
ROOT_RECORDS=PACKETS/'production-runtime-v1'
TOOL=Path('/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools')
TOOL_SHA='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
RANDOM='wasi:random/random@0.2.10'
GATES={
 'allocator-gc':('502320aaed8c78ace92d8d8d782a355307868beee707b22e03c96f67cd42c833','840e0fa7390b9f860dad9ae387a877a5541df435a33f857aaed3a41ec46965e6'),
 'focused-off':('6e5bc2ca3b3e3f7dccaa887003bc292e8a7abfbc5260691d1cda0114640dae84','d4ba8f9583659d70b7a77d1bbd1737e0533aa617bebc8390a144a30732cef3bb'),
 'focused-runtime':('479821f8eefbc6aacbfe9df8538c5ee0a8745e530a474ecee8cb34251c0a1943','e0f08fc354912fa6e18aba393f8bea9ff0eb29adac8d12d77e3195b1adfb3fc2'),
}
checked_files,copied_files={},[]
def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def check(path, expected=None, size=None):
    path = Path(path)
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and not path.is_symlink(), path
    digest = sha(path)
    if expected is not None:
        assert digest == expected, path
    if size is not None:
        assert info.st_size == size, path
    previous = checked_files.get(str(path))
    row = {'path': str(path), 'sha256': digest, 'bytes': info.st_size}
    if previous:
        assert row == previous
    checked_files[str(path)] = row
    return row

def copy_text(path, target):
    row = check(path)
    data = Path(path).read_bytes()
    data.decode('utf-8')
    assert b'\0' not in data and data[:4] != b'\0asm'
    destination = HERE / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A verifier-only schema correction may leave this packet's earlier exact
    # captures present. Revalidate them against the same pinned complete output;
    # never overwrite a differing file or adopt a prior runtime result as new.
    if destination.exists():
        assert not destination.is_symlink() and destination.read_bytes() == data
    else:
        with destination.open('xb') as stream:
            stream.write(data)
    assert sha(destination) == row['sha256']
    copied_files.append({**row, 'copy': target, 'byteExact': True})

def walk(value, callback, context=''):
    if isinstance(value, dict):
        callback(value, context)
        for key, child in value.items():
            walk(child, callback, context + '/' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, callback, context + '/' + str(index))

def u32(data, position, end):
    result = 0
    for shift in range(0, 35, 7):
        assert position < end
        value = data[position]
        position += 1
        result |= (value & 127) << shift
        if not value & 128:
            assert result <= 0xffffffff
            return result, position
    raise AssertionError('Invalid u32 LEB')

def import_counts(data, begin=0, end=None, depth=0):
    """Header/section-length/import-vector-count inspection only.

    Core sections: import=2. Component: core-module=1, nested-component=4,
    import=10. Source: local wasmparser0.235 parser.rs. No function, type,
    initializer, instance or application instruction is interpreted.
    """
    end = len(data) if end is None else end
    assert depth <= 32 and begin + 8 <= end
    header = data[begin:begin + 8]
    assert header in [b'\0asm\x01\0\0\0', b'\0asm\x0d\0\x01\0']
    component = header[4] == 13
    result = [{'offset': begin, 'bytes': end - begin, 'depth': depth,
               'kind': 'component' if component else 'core-module', 'importEntries': 0}]
    position = begin + 8
    while position < end:
        section = data[position]
        size, payload = u32(data, position + 1, end)
        finish = payload + size
        assert finish <= end
        if section == (10 if component else 2):
            count, _ = u32(data, payload, finish)
            result[0]['importEntries'] += count
        if component and section in [1, 4]:
            nested = import_counts(data, payload, finish, depth + 1)
            assert nested[0]['kind'] == ('core-module' if section == 1 else 'component')
            result.extend(nested)
        position = finish
    assert position == end
    return result

assert len(sys.argv)>=3,'STAGE_LABEL COMPLETED_GATE...; Root confirmation required'
stage_name,*labels=sys.argv[1:]
assert re.fullmatch('[a-z0-9-]+',stage_name) and len(labels)==len(set(labels))
assert all(label in GATES for label in labels)
assert not(BASE/'index.json').exists(),'Do not extend a sealed packet'
HERE=BASE/stage_name
HERE.mkdir(exist_ok=False)
source=Path(__file__).read_bytes()
(HERE/'verify.py').write_bytes(source)
source_seals=[]
for name,digest,count in [('production-regression-candidate-v5','ae37908c99b9043dbfd05a78b61ee7168936b76e4157919e510794f868d7538d',667),('production-followon-capability-v3','d7e4dddef6da2d36aa091001c0d17adf4dbe1d0d07ff743fdd8318853e1a54ad',778)]:
 path=PACKETS/name/'input-freeze.json';check(path,digest);manifest=json.loads(path.read_bytes());assert len(manifest['inputs'])==count
 for row in manifest['inputs']:check(path.parent/row['path'],row['sha256'],row['bytes'])
 source_seals.append({'path':str(path),'sha256':digest,'inputs':count,'postRuntimeBytesRehashed':True})
check(TOOL,TOOL_SHA)
version=subprocess.run([str(TOOL),'--version'],capture_output=True,text=True,timeout=30)
assert version.returncode==0 and version.stdout.startswith('wasm-tools 1.235.0 ')
gates=[]
for label in labels:
 engine,report_sha=GATES[label];directory=ROOT/label
 root_record=ROOT_RECORDS/(label+'-root-results.json');check(root_record)
 observed=json.loads(root_record.read_bytes());assert observed['toolExitCode']==0 and observed['reportSha256']==report_sha and observed['engineSha256']==engine
 report_path=directory/'results.json';check(report_path,report_sha);report=json.loads(report_path.read_bytes());assert report['engineSha256']==engine
 completion=directory/'production-admission-complete.json';check(completion,observed['completionSha256']);seal=json.loads(completion.read_bytes());assert seal['engineSha256']==engine and seal['consumedInputsRecheckedAfterRun'] is True
 expected=[RANDOM]if label=='focused-runtime'else[]
 expected_entropy='runtime-only'if expected else'off'
 expected_gc=label=='allocator-gc'
 assert seal['gcStress']==expected_gc
 if 'entropyPolicy'in seal:assert seal['entropyPolicy']==expected_entropy
 for filename in [label+'-root-results.json',label+'-results.json',label+'-completion.json',label+'.stdout.log',label+'.stderr.log']:
  path=ROOT_RECORDS/filename;copy_text(path,'root-records/'+filename)
 assert sha(ROOT_RECORDS/(label+'-results.json'))==report_sha
 # Report the actual frozen selected engine, not the current mutable build cache.
 pin_document=PACKETS/'production-pin-review-v1/capability-pins.json';check(pin_document,'26b16ba1404c76d04a3ae1a137d37d88a08cc87de4907d14eb3bc028759104f1')
 pin_label='normal-runtime'if expected else'gc-off'if expected_gc else'normal-off'
 pin=json.loads(pin_document.read_bytes())['variants'][pin_label];assert pin['engineSha256']==engine
 check(pin['enginePath'],engine,pin['engineBytes']);check(pin['enginePath']+'.build.json',pin['receiptSha256']);check(pin['freezeReceiptPath'],pin['freezeReceiptSha256'])
 metadata=json.loads(Path(pin['enginePath']+'.build.json').read_bytes());assert metadata['gcStress']==expected_gc and metadata['entropyPolicy']==expected_entropy
 local_components=[];local_cores=[];component_hashes=set()
 for pathdir,dirs,files in os.walk(directory,followlinks=False):
  dirs[:]=[name for name in dirs if not(Path(pathdir)/name).is_symlink()]
  for name in sorted(files):
   path=Path(pathdir)/name
   if path.is_symlink():continue
   row=check(path)
   if path.suffix=='.wasm':
    counts=import_counts(path.read_bytes())
    if counts[0]['kind']=='component':
     assert counts[0]['importEntries']==len(expected)
     parsed=subprocess.run([str(TOOL),'component','wit','--json',str(path)],capture_output=True,text=True,timeout=30)
     assert parsed.returncode==0 and parsed.stderr==''
     wit=json.loads(parsed.stdout);assert len(wit['worlds'])==1 and sorted(wit['worlds'][0]['imports'])==expected
     target=HERE/'component-wit'/label/(name+'.json');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(parsed.stdout)
     local_components.append({**row,'outerImports':expected,'sectionImportCounts':counts,'independentWitPath':str(target.relative_to(HERE)),'independentWitSha256':sha(target),'applicationExecuted':False})
     component_hashes.add(row['sha256'])
    else:local_cores.append({**row,'sectionImportCounts':counts,'notOuterHostImportInventory':True})
   else:copy_text(path,'completed-output/'+label+'/'+path.relative_to(directory).as_posix())
 audits=[]
 def record(value,context):
  if'interfaceAudit'in value:
   audit=value['interfaceAudit'];assert audit['selectedInterfaces']==audit['emittedImports']==expected;assert audit['componentSha256']in component_hashes;audits.append({'context':context,**audit})
  if'componentPath'in value and str(value['componentPath']).startswith(str(directory)+'/'):check(value['componentPath'],value['componentSha256'],value.get('componentBytes'))
  if'componentSha256'in value and'packaging'not in context and'componentizer'not in context:assert value['componentSha256']in component_hashes
 walk(report,record)
 if label=='allocator-gc':
  assert len(local_components)==1 and len(report['calls'])==3
  assert report['wasmtime']['observed']==report['calls'][0]and report['wasmtime']['stderr']==''
  assert'-DNODE_COMPAT_GC_STRESS=1'in report['compileCommand']
  for i,call in enumerate(report['calls'],1):assert call=={'calls':i,'roundtrips':8,'brands':5,'ownedLength':127,'viewOffset':3,'snapshotByte':4+i}
  check(directory/'source.mjs',report['sourceSha256'])
  semantic={'retainedCalls':3,'freshWasmtime':True,'roundtripsPerCall':8,'combinedOwnershipOnly':True,'exclusiveRootingProof':False}
 else:
  assert len(local_components)==8 and report['publicNodeGroups']=={'public':16,'nested':4,'receivers':9,'total':29}
  assert report['capabilityOptions']['selectedInterfaces']==expected
  oracle_path=directory/'source/node-results.json';check(oracle_path,report['nodeOracleSha256']);oracle=json.loads(oracle_path.read_bytes())
  for field,n in [('publicCases',16),('nestedOnceCases',4),('receiverCases',9)]:assert len(oracle[field])==n
  for group in ['main','aliases','benign']:
   value=report[group];assert len(value['calls'])==3 and value['freshWasmtime']['observed']==value['calls'][0]
   assert value['freshWasmtime']['stderr']==''
   for i,call in enumerate(value['calls'],1):assert call['calls']==i
  for call in report['main']['calls']:
   for field in ['publicCases','nestedOnceCases','receiverCases']:assert call[field]==oracle[field]
   assert call['namespace']and call['commonJS']
  assert len(report['initializers'])==8 and len(report['fatal'])==5
  for row in report['sourceFiles']:check(row['path'],row['sha256']);check(row['saved'],row['sha256'])
  for row in report['fatal']:
   assert row['jcoChild']['status']==0 and'EXPECTED_FATAL_DISCARD'in row['jcoChild']['stdout']
   assert row['wasmtime']['status']!=0 and'unreachable'in row['wasmtime']['stderr']
  symbol=report['targetSymbolIdentity'];assert symbol['node']['sameAsNodeRegistry']is True and symbol['target']['sameAsNodeRegistry']is False and symbol['target']['registryKey']is None
  semantic={'publicGroups':29,'groupPartition':[16,4,9],'retainedPositiveCalls':9,'freshWasmtimePositiveControls':3,'initializationFailures':8,'freshFatalCases':5,'targetSymbolRegistryParity':False,'originalFatalCauseIdentityProved':False,'instanceDiscardRequired':True}
 gates.append({'label':label,'engineSha256':engine,'reportSha256':report_sha,'rootReceiptSha256':sha(root_record),'completionSha256':sha(completion),'sourceSeal':seal['inputClosure'],'components':local_components,'cores':local_cores,'interfaceAudits':audits,'semantic':semantic,'knownLimitations':report.get('limits',[report.get('scope')])})
for row in list(checked_files.values()):check(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'PARTIAL_COMPLETED_FOCUSED_GATES_READ_ONLY_VERIFICATION_PASSED_OPEN_PACKET','completedGateLabels':labels,'gates':gates,'sourceSeals':source_seals,'verifiedFiles':list(checked_files.values()),'copiedTextFiles':copied_files,'verifierSourceSha256':hashlib.sha256(source).hexdigest(),'applicationOrNodeOracleOrGuestOrHostExecuted':False,'parserTool':{'path':str(TOOL),'sha256':TOOL_SHA,'version':version.stdout.strip()},'binaryBytesCopied':0,'unlistedActiveGateDirectoriesRead':False,'engineResetALSExclusiveRootingOrCompleteNodeProved':False,'httpIncluded':False,'performanceClaim':False}
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'state':result['state'],'gates':labels,'components':sum(len(x['components'])for x in gates),'copiedTextFiles':len(copied_files)}))
