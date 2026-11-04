"""Seal only this owned source review, with fresh final byte rechecks."""
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
 with(HERE/name).open('x') as output:json.dump(value,output,indent=2);output.write('\n')
def main():
 assert not(HERE/'index.json').exists()
 refs=json.loads((HERE/'external-references.json').read_bytes())['files']
 for row in refs:assert describe(row['path'])=={key:row[key] for key in ['sha256','bytes']},row['path']
 result=json.loads((HERE/'results.json').read_bytes())
 assert result['state']=='INDEPENDENT_MEMORY_PROBE_SOURCE_STRUCTURE_AND_CLOSURE_PASSED'
 assert result['consumedInputs']==10295 and result['manifestReconstructionExact'] is True
 assert result['plannedProcesses']==18 and result['actualProbeReturnsObserved']==0
 assert result['descriptorMaxPrettyBytes']==3412 and result['selfManifestBytes']==911
 assert result['noBlockerFound'] is True
 for path in HERE.rglob('*'):
  if path.is_file():
   data=path.read_bytes();data.decode('utf-8');assert b'\0' not in data
   assert all(line.rstrip(b' \t')==line for line in data.splitlines()),str(path)
   if path.suffix=='.py':ast.parse(data)
 receipt={'schemaVersion':1,'state':'SEALED_INDEPENDENT_MEMORY_PROBE_SOURCE_PASS',
  'candidateIndexSha256':result['candidateIndexSha256'],'results':describe(HERE/'results.json'),
  'candidateFiles':20,'consumedInputs':10295,'stablePathsFinalRehashed':len(refs),'fullManifestReconstructionExact':True,
  'originalLoaderSha256':'0b9d3cee8d40160a9fa0c56165e60d6a8ef57e10a9c722069f30d5f162c3492b','originalLoaderBytes':646,
  'componentTuples':4,'diagnosticNativeFreezes':2,'frozenCopiesEach':525,'originalToolTrees':2,'originalToolLinks':22,
  'largestDescriptorPrettyBytes':3412,'descriptorLimitBytes':16384,'selfManifestBytes':911,'selfManifestLimitBytes':4096,
  'plannedWorkers':18,'publicReturnsPerWorker':7,'plannedCases':[1,5],'iterationsPerCase':1,'plannedOrder':'AB/BA/AB; small before large',
  'sourceChecks':{'ownedReaderSession':65963,'ownedReaderExitCode':0,'observedByThisReader':True,'ownerStoredPureChecks':35,'ownerStoredSyntaxChecks':4,'ownerOriginalTerminalsObservedByThisReader':False},
  'authority':{'checkedInNull':True,'separateCallerHashedRootOverlaySupported':True,'sealedSourceEditsNeeded':False,'rootAuthorityIssuedByThisReader':False,'executionApprovedByThisReview':False},
  'currentContextCondition':'All five oldRoot preimages remain required by this unchanged candidate. Complete execution before promotion or derive/review a fresh explicitly context-aware successor; no hash/metadata projection.',
  'limitations':['Whole-process public RSS/maxRSS only; no guest heap/capacity/grow/unique-physical claims.','Compilation and binding import combined; no cold physical startup claim.','Small then large on one instance and AB/BA/AB order confound; n3 and shared-machine/parent pressure.','600s is an operational bound, not universal adequacy.','No new RSS, operational timings or actual raw probe returns exist yet.'],
  'ownerParentWorkerPreflightNativeGuestHostBenchmarkActions':False,'sealedSourceOrArtifactEdits':False,'runtimeAcceptance':False,'performanceConclusion':False}
 put('review-receipt.json',receipt)
 rows=[]
 for path in sorted(HERE.rglob('*')):
  if path.is_file() and path.name!='index.json':rows.append({'path':str(path.relative_to(HERE)),**describe(path)})
 put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_MEMORY_PROBE_SOURCE_REVIEW_PASS','files':rows,'runtimeAcceptance':False,'executionAuthorityIssued':False,'measurementsObserved':False})
 print(json.dumps({'state':receipt['state'],'files':len(rows),'indexSha256':describe(HERE/'index.json')['sha256'],'receiptSha256':describe(HERE/'review-receipt.json')['sha256'],'resultsSha256':describe(HERE/'results.json')['sha256'],'stablePathsFinalRehashed':len(refs)}))
if __name__=='__main__':main()
