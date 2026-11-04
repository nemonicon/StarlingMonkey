"""Seal independent timing integrity/provenance; no executable owner imports."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert not(HERE/'index.json').exists()
r=json.loads((HERE/'results.json').read_bytes());assert r['state']=='INDEPENDENT_COMPOSED_TIMING_INTEGRITY_PROVENANCE_PASSED'
assert r['regularOutputFilesRehashed']==1037 and r['pilotsDecoded']==42 and r['timedWorkersDecoded']==126 and r['terminalsIncludingPostAudit']==169
assert r['actualPerBatchCompactValuesRetained']is False and r['independentlyDecodedActualPerBatchChecksumsClaim']is False
for row in r['verifiedFiles']:
 path=Path(row['path']);assert path.is_file()and not path.is_symlink();digest=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
 assert digest.hexdigest()==row['sha256']and path.stat().st_size==row['bytes'],path
source=FAMILY/'measurement-execution-activated-v2';frozen=Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze/source/builtins/node-compat/classic-streams')
assert(source/'classic-core.generated.mjs').read_bytes()==(frozen/'classic-core.generated.mjs').read_bytes()
assert(source/'classic-streams.mjs').read_bytes()==(frozen/'classic-streams.mjs').read_bytes()
assert sha((source/'classic-core.generated.mjs').read_bytes())=='5c0241a73f4cdffc61d7c962bd4d1a1d2015f8fbadef59a4631b7551f9a767b9'
origins={'schemaVersion':1,'sourceFamilyIndexSha256':r['sourceFamilyIndexSha256'],'nativeAndCanonicalCoreSha256':'5c0241a73f4cdffc61d7c962bd4d1a1d2015f8fbadef59a4631b7551f9a767b9','canonicalAndFrozenWrapperByteExact':True,'comparisons':[{'id':'same-engine-binding','scope':'Registered JS classic-stream bindings versus byte-identical bundled JS factory; same ON engine/common native Buffer,EventEmitter,StringDecoder,nextTick/Web-abort/symbol dependencies. Private util stays inside canonical factory; no invented util injection.'},{'id':'whole-profile','scope':'Byte-identical canonical bundle on genuine ON/OFF diagnostic engines.'},{'id':'different-stock-provider','scope':'Canonical provider versus unmodified stock dependency graph/private queueMicrotask FIFO/default imports; stock global Buffer replacement and ambient Web dependency domain are recorded.'}],'cppStateMachineClaim':False,'externalGuestImports':[],'compositionOrigins':r['compositionOrigins'],'quietWindowIsNotBackgroundIsolationProof':True}
with(HERE/'api-origin-ledger.json').open('x')as stream:json.dump(origins,stream,indent=2);stream.write('\n')
output=Path('/tmp/starling-node-compat/production-common-byte-composed-timing-v1')
for path in(output/'processes').glob('*.terminal.json'):
 terminal=json.loads(path.read_bytes());assert terminal['status']==0 and terminal['signal']is terminal['spawnError']is terminal['externalSignal']is None and terminal['timedOut']is terminal['outputLimitExceeded']is False
 assert terminal['closed']is terminal['ownedGroupGone']is terminal['terminalExitZeroObserved']is True and terminal['signals']==terminal['errors']==[]
receipt={key:value for key,value in r.items()if key!='verifiedFiles'}
receipt.update({'state':'INDEPENDENT_COMPOSED_TIMING_INTEGRITY_PROVENANCE_PASS_WITH_RAW_CHECKSUM_RETENTION_LIMIT','resultsSha256':sha((HERE/'results.json').read_bytes()),'workerIntegrityLedgerSha256':sha((HERE/'worker-integrity-ledger.json').read_bytes()),'expectedCompactContractsSha256':sha((HERE/'expected-compact-contracts.json').read_bytes()),'apiOriginLedgerSha256':sha((HERE/'api-origin-ledger.json').read_bytes()),'verifiedExternalPaths':len(r['verifiedFiles']),'rawTimingBatchChecksumsIndependentlyDecoded':False,'numericalInterpretationDeferredToSeparateReview':True,'readerCorrectionsPreserved':True})
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8');assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),path
 files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_COMPOSED_TIMING_INTEGRITY_PROVENANCE_PASS','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'rawTimingBatchChecksumsRetained':False,'numericalInterpretationPerformed':False,'runtimeAcceptanceClaim':False,'performanceSignificanceClaim':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for row in files:
 raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256'],'verifiedPaths':len(r['verifiedFiles'])}))
