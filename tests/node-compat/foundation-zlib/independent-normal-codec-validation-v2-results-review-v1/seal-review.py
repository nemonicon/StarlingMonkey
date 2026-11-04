"""Final independent normal data/source rehash and textual review seal."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert not(HERE/'index.json').exists()
r=json.loads((HERE/'results.json').read_bytes());s=json.loads((HERE/'source-closure-results.json').read_bytes())
assert r['state']=='INDEPENDENT_ZLIB350_NORMAL_CODEC_V2_BOUNDED_RESULTS_PASSED'and r['decodedCodecObservations']==283 and r['freshWasmtimeFullNestedReturnsDecoded']==61
assert s['generatedIndexSha256']==r['actualSourceFamilyIndexSha256']=='8af9a2137b93802ae2f09e30219ad416675a9b10fdac1cdbcc18e48e937a9e56'and s['consumedRowsIndependentlyReconstructedAndRehashed']==11107
assert r['labels']=={'retained-0':61,'retained-1':50,'retained-2':50,'fresh-Jco':61,'fresh-Wasmtime':61}
verified={}
for value in s['verifiedFiles']+r['verifiedFiles']:
 key=value['path'];assert key not in verified or verified[key]==value;verified[key]=value
for value in verified.values():
 path=Path(value['path']);assert path.is_file()and not path.is_symlink();digest=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
 assert digest.hexdigest()==value['sha256']and path.stat().st_size==value['bytes'],path
wit=(HERE/'fresh-component.wit').read_text();exports=set(re.findall(r'export\s+([\w-]+):\s*(func\([^;]+);',wit))
assert exports=={('run','func(index: u32) -> string'),('module-contract','func() -> string'),('refusals','func() -> string'),('ownership','func() -> string'),('ordinary-gc','func() -> string')}
output=Path('/tmp/starling-node-compat/production-zlib-v4-normal-off-codec-validation-v2');pids=[]
for i in range(61):
 terminal=json.loads((output/f'processes/wasmtime-{i}.terminal.json').read_bytes());pids.append(terminal['pid']);assert terminal['status']==0 and terminal['ownedGroupGone']is True
assert len(set(pids))==61
node_path=HERE.parent/'component-validation-activated-v8/node-results.json';node=json.loads(node_path.read_bytes());module_path=output/'module-observation.json';module=json.loads(module_path.read_bytes())
constants=[]
for name,value in module['value']['constants'].items():
 expected=node['inventory']['constants'][name]
 if value!=expected:constants.append({'name':name,'nodeAsRecorded':expected,'profileAsObserved':value,'interpretation':'Source-coupled header/runtime-equality inference only; not a returned private backend version.','citations':{'node':{'path':str(node_path),'jsonPointer':'/inventory/constants/'+name},'profile':{'path':str(module_path),'jsonPointer':'/value/constants/'+name},'sourceHeaderInference':{'path':str(module_path),'jsonPointer':'/sourceCoupledBackendInference'}}})
assert len(constants)==1 and constants[0]['name']=='ZLIB_VERNUM'
with(HERE/'constant-difference-ledger.json').open('x')as stream:json.dump({'schemaVersion':1,'differences':constants,'otherTypedConstantsEqual':106,'privateBackendObserved':False},stream,indent=2);stream.write('\n')
with(HERE/'verified-closure.json').open('x')as stream:json.dump({'schemaVersion':1,'files':sorted(verified.values(),key=lambda value:value['path'])},stream,indent=2);stream.write('\n')
receipt={key:value for key,value in r.items()if key!='verifiedFiles'}
receipt.update({'state':'INDEPENDENT_ZLIB350_NORMAL_V2_BOUNDED_RESULTS_PASS','resultsSha256':sha((HERE/'results.json').read_bytes()),'sourceClosureResultsSha256':sha((HERE/'source-closure-results.json').read_bytes()),'nodeProfileDifferenceLedgerSha256':sha((HERE/'node-profile-difference-ledger.json').read_bytes()),'constantDifferenceLedgerSha256':sha((HERE/'constant-difference-ledger.json').read_bytes()),'verifiedClosureSha256':sha((HERE/'verified-closure.json').read_bytes()),'verifiedExternalPaths':len(verified),'sourceNativeToolClosureFreshlyRehashed':True,'freshWasmtimeDistinctRecordedPids':61,'readerCorrectionsPreserved':True})
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8');assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),path
 files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_NORMAL_CODEC_V2_BOUNDED_RESULTS_PASS','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'nodeParityClaim':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for value in files:
 raw=(HERE/value['path']).read_bytes();assert sha(raw)==value['sha256']and len(raw)==value['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256'],'verifiedExternalPaths':len(verified),'ledgerSha256':receipt['nodeProfileDifferenceLedgerSha256']}))
