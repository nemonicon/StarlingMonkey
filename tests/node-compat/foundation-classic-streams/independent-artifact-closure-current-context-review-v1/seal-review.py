"""Seal this bounded independent source/data review only."""
from pathlib import Path
import ast
import hashlib
import json
import stat
HERE=Path(__file__).resolve().parent
cache={}
def describe(path):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 key=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
 if key not in cache:
  h=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
  cache[key]=h.hexdigest()
 after=path.lstat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 return {'sha256':cache[key],'bytes':before.st_size}
def put(name,value):
 with(HERE/name).open('x') as out:json.dump(value,out,indent=2);out.write('\n')
def main():
 assert not(HERE/'index.json').exists()
 refs=json.loads((HERE/'external-references.json').read_bytes())['files']
 for row in refs:assert describe(row['path'])=={k:row[k] for k in ['sha256','bytes']},row['path']
 result=json.loads((HERE/'results.json').read_bytes())
 assert result['state']=='INDEPENDENT_CURRENT_CONTEXT_AMENDMENT_SOURCE_PASSED_PROMOTION_STILL_HELD'
 assert result['pureChecksTotal']==35 and [(r['checks'],r['exitCode']) for r in result['ownedPureChecks']]==[(23,0),(12,0)]
 assert result['sourcePromotionHeld'] and not result['protected17884RehashRepeated']
 for path in HERE.rglob('*'):
  if path.is_file():
   data=path.read_bytes();data.decode('utf-8');assert b'\0' not in data
   assert all(line.rstrip(b' \t')==line for line in data.splitlines()),str(path)
   if path.suffix=='.py':ast.parse(data)
 receipt={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ARTIFACT_CURRENT_CONTEXT_SOURCE_PASS_PROMOTION_HELD','candidateIndexSha256':result['candidateIndexSha256'],'results':describe(HERE/'results.json'),'candidateFiles':35,'candidateReferences':154,'externalPathsFinalRehashed':len(refs),'zlibExactManifests':12,'zlibExactDirectRows':60,'memoryExactDirectRows':5,'zeroDirectProducerPreparationRows':2261,'zeroDirectConsumerSourceRows':506,'future767Approved':False,'snapshotFiles':7,'old24eRecoveredOrUnequallyMapped':False,'originalPlan96bUnchanged':True,'prior4929ProofUnchanged':True,'protected17884AuditRepeated':False,'readerSelectedGenuineDescriptors':9,'ownedPureFixtureSuites':{'reader':23,'context':12,'exitCodes':[0,0],'observedByThisReader':True},'memoryFailure':{'rootReceiptSha256':'e51149e1743030a8c2e13547575731ede0dfed0263c19d951db18aaa1db37ed1','recordedRawExit':1,'workerLaunches':0,'resultsOrCompletion':False,'oldSourcePassNotRuntimeProof':True,'rootTerminalObservedByThisReader':False},'dataOnlyReaderDoesNotRerunHistoricalPrograms':True,'originalDescriptorsProgramsMetadataUnchanged':True,'currentOwnerMigrationCompleted':False,'sourcePromotionHeld':True,'archiveCopiedOrAccepted':False,'ownerNativePreflightGuestHostTimingActions':False,'performanceOrMemoryMeasurementClaim':False}
 put('review-receipt.json',receipt)
 rows=[{'path':str(path.relative_to(HERE)),**describe(path)} for path in sorted(HERE.rglob('*')) if path.is_file() and path.name!='index.json']
 put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_ARTIFACT_CURRENT_CONTEXT_SOURCE_REVIEW_PASS','files':rows,'sourcePromotionHeld':True,'archiveAcceptance':False,'runtimeOrMemoryMeasurementClaim':False})
 print(json.dumps({'state':receipt['state'],'files':len(rows),'indexSha256':describe(HERE/'index.json')['sha256'],'receiptSha256':describe(HERE/'review-receipt.json')['sha256'],'resultsSha256':describe(HERE/'results.json')['sha256'],'externalPathsFinalRehashed':len(refs)}))
if __name__=='__main__':main()
