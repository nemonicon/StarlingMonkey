"""Seal only this independent text packet; final rehash of stable data refs."""
from pathlib import Path
import ast
import hashlib
import json
import stat

HERE=Path(__file__).resolve().parent
cache={}
def digest(path):
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
 for row in refs:
  assert digest(row['path'])=={k:row[k] for k in ['sha256','bytes']},row['path']
 results=json.loads((HERE/'results.json').read_bytes())
 findings=json.loads((HERE/'source-findings.json').read_bytes())
 assert results['state']=='SOURCE_REVIEW_HOLD_CURRENT_CONTEXT_AND_MUTABLE_SNAPSHOT_GAPS'
 assert [row['id'] for row in results['blockers']]==['ART-CLOSURE-M1','ART-CLOSURE-M2']
 assert len(results['inventoryRehashMismatches'])==1
 assert findings['mutableStatusSnapshot']['classification'].startswith('Expected mutable status drift')
 assert not findings['draftObservation']['stableReviewInput']
 for path in HERE.rglob('*'):
  if path.is_file():
   data=path.read_bytes();data.decode('utf-8');assert b'\0' not in data,str(path)
   if path.suffix=='.py':ast.parse(data)
   assert not any(line.rstrip(b' \t')!=line for line in data.splitlines()),str(path)
 receipt={
  'schemaVersion':1,'state':'SEALED_INDEPENDENT_SOURCE_REVIEW_HOLD_PROMOTION_AND_EXACT_SNAPSHOT_COPY',
  'reviewedPlanIndexSha256':results['planIndexSha256'],'results':digest(HERE/'results.json'),
  'findings':digest(HERE/'source-findings.json'),'externalStableReferencePathsFinalRehashed':len(refs),
  'inventory':{'files':17885,'matchingFiles':17884,'mutableStatusDrift':1,'links':47,'freezeInventories':6,'criticalManifests':8,'classicPacketIndexes':129,'stagedPacketIndexes':2,'terminalRoots':9},
  'fiveFilePatchExact':True,'native342Delta':{'unchanged':339,'changed':3},'moduleSelectionUnchanged':True,
  'expandedNonclassicDirectImpact':{'manifests':12,'rows':60,'currentV8':5,'currentDisabled':5,'currentPublisher':5,'native350Preparation2261DirectRows':0,'consumerSource506DirectRows':0},
  'draft767Approved':False,'unsealedDraftDescriptorsExcludedFromStableRehash':True,
  'resolutionBeforeLiveRollforward':['Explicit current owner migration-or-hold map, including memory-probe completion against currentRoot5 or a fresh archive-aware source revision.','New preservation producer/read-only descriptor mapper review; protected closure stays strict, original descriptors stay unchanged.','Separate atomic fresh capture of mutable status text; preserve24e as historical snapshot unless authenticold bytes located, never substitute3e under24e.'],
  'readerTerminal':{'session':82678,'exitCode':0,'observedByThisReader':True},
  'rootRuntimeTerminalsObservedByThisReader':False,
  'ownerImportsOrHelpersExecuted':False,'nativeGuestHostBenchmarkActions':False,
  'liveSourceOrSealedParentEdits':False,'archiveCreated':False,'sourceAdoption':False,'acceptance':False,'performanceClaim':False
 }
 put('review-receipt.json',receipt)
 files=[]
 for path in sorted(HERE.rglob('*')):
  if path.is_file() and path.name!='index.json':files.append({'path':str(path.relative_to(HERE)),**digest(path)})
 put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_ARTIFACT_CLOSURE_PLAN_REVIEW_HOLD','files':files,'sourceAdoption':False,'archiveAcceptance':False,'runtimeAcceptance':False})
 print(json.dumps({'state':receipt['state'],'indexSha256':digest(HERE/'index.json')['sha256'],'files':len(files),'receiptSha256':digest(HERE/'review-receipt.json')['sha256'],'resultsSha256':digest(HERE/'results.json')['sha256'],'stablePathsFinalRehashed':len(refs)}))
if __name__=='__main__':main()
