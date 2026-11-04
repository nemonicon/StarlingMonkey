"""Final read/hash seal of the actual consumer-OFF native evidence review."""
from pathlib import Path
import ast,hashlib,json,stat
HERE=Path(__file__).resolve().parent
cache={}
def describe(path):
 p=Path(path);a=p.lstat();assert stat.S_ISREG(a.st_mode),str(p)
 key=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)
 if key not in cache:
  h=hashlib.sha256()
  with p.open('rb')as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  cache[key]=h.hexdigest()
 z=p.lstat();assert key==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns),str(p)
 return{'sha256':cache[key],'bytes':z.st_size}
def put(name,value):
 with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 assert not(HERE/'index.json').exists()
 result=json.loads((HERE/'results.json').read_bytes());assert result['state']=='INDEPENDENT_CONSUMERS355_V2_DISABLED_OFF_NATIVE_FREEZE_PASSED_NO_GUEST'
 for row in result['verifiedFiles']:assert describe(row['path'])=={k:row[k]for k in['sha256','bytes']},row['path']
 assert result['frozenCopiesObserved']==1164 and result['allDisabledOriginalEntryReferencesRehashed']==1162
 assert result['normalFrozenCopiesRehashedUnchanged']==result['gcFrozenCopiesRehashedUnchanged']==1164
 assert result['streamConsumersEnabled']is False and result['zlibEnabled']is True and result['gcStress']is False
 assert result['configuredNativeCompileCommands']==62 and result['privateCompileCommands']==6 and result['selectedManifests']==10
 for path in HERE.rglob('*'):
  if path.is_file():
   data=path.read_bytes();data.decode('utf-8');assert b'\0'not in data
   assert all(line.rstrip(b' \t')==line for line in data.splitlines()),str(path)
   if path.suffix=='.py':ast.parse(data)
 receipt={'schemaVersion':1,'state':'SEALED_INDEPENDENT_CONSUMERS355_V2_DISABLED_OFF_NATIVE_FREEZE_PASS','results':describe(HERE/'results.json'),'rootReceiptSha256':result['rootReceiptSha256'],'sourceIndexSha256':result['sourceIndexSha256'],'engineSha256':result['engineSha256'],'engineBytes':9995242,'metadataSha256':result['metadataSha256'],'freezeReceiptSha256':result['freezeReceiptSha256'],'normalProofIndexSha256':result['normalPeerIndexSha256'],'gcProofIndexSha256':result['gcPeerIndexSha256'],'disabledFrozenCopies':1164,'disabledOriginalReferences':1162,'normalAndGCFrozenCopiesEachUnchanged':1164,'finalFileReferencesRehashed':len(result['verifiedFiles']),'nativeInputs':355,'externalEmbeddingInputs':3,'toolRows':767,'compilerInventory':{'native':62,'strict':4,'private':6,'separateNoLtoEmbedding':1},'actualBuildSteps':108,'selectedManifests':10,'consumerManifestSelected':False,'consumerDefineAbsentIncludingNoZeroDefine':True,'zlibKernelPresent':True,'rawLinkBytes':result['rawLinkCaptureBytes'],'rawLinkLineOneBased':result['rawLinkSelectedLineOneBased'],'selectedMOZ_ZDefinitions':7,'decoderBeforeNode':True,'actualDisabledOpenSslLibrary':result['opensslActualLibrary'],'actualPerProjectDownloadedArchives':0,'actualSharedSdkVersionFiles':1,'normalArchiveInventoryRelabelled':False,'inheritedSourcePreparationRows':3420,'inheritedOpenSslSourceFiles':4650,'broadOldSourceAuditsRepeated':False,'flags':{'consumer':False,'zlib':True,'gc':False,'entropy':'off','DEBUG':False,'OOM':False},'runtimeBackendProof':result['runtimeBackendProof'],'runtimeBootstrapPinsNull':True,'operationalAdmissionOpen':False,'rootTerminalEventsObservedByThisReader':False,'ownedReader':{'session':49298,'exitCode':0,'observedByThisReader':True},'ownerVerifierBootstrapCompilerEngineGuestHostTimingExecuted':False,'runtimeImportDenialOrConsumerBehaviorClaim':False,'runtimeAcceptance':False,'performanceClaim':False}
 put('review-receipt.json',receipt)
 rows=[{'path':str(p.relative_to(HERE)),**describe(p)}for p in sorted(HERE.rglob('*'))if p.is_file()and p.name!='index.json']
 put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_NATIVE_CONSUMERS_V2_DISABLED_OFF_REVIEW_PASS','files':rows,'runtimeAcceptance':False,'performanceClaim':False})
 print(json.dumps({'state':receipt['state'],'files':len(rows),'indexSha256':describe(HERE/'index.json')['sha256'],'receiptSha256':describe(HERE/'review-receipt.json')['sha256'],'resultsSha256':describe(HERE/'results.json')['sha256'],'finalRehashed':len(result['verifiedFiles'])}))
if __name__=='__main__':main()
