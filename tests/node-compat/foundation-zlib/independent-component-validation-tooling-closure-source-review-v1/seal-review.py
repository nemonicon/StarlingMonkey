"""Seal this source review and rehash stored Root evidence; no project imports."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink();value=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
 assert digest is None or value.hexdigest()==digest,path;assert size is None or path.stat().st_size==size,path
 return{'path':str(path.resolve()),'sha256':value.hexdigest(),'bytes':path.stat().st_size}
assert not(HERE/'index.json').exists()
r=json.loads((HERE/'results.json').read_bytes());assert r['state']=='INDEPENDENT_ZLIB350_TOOLING_CLOSURE_SOURCE_REVIEW_PASSED'
assert r['ownerIndexSha256']=='daa7d28a7105f878a9465c4eb0fea2edaa3ef6329a15baafcabd7ccc28a0fd0c'
assert r['ownerFiles']==15 and r['preparationInputsRehashed']==11015 and r['concreteSourceBlockers']==[]
for value in r['verifiedFiles']:row(value['path'],value['sha256'],value['bytes'])
for name in['component-validation-activated-v7','component-validation-activated-v7.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
root_path=HERE.parent/'component-tool-closure-root-source-results-v1.json';root_row=row(root_path,'8bbcbd290019c9f08e465d8fd23d24407a0676f67ba454fc8bd907bdef64082b');root=json.loads(root_path.read_bytes())
assert root['sourceIndexSha256']==r['ownerIndexSha256']and root['physicalAndSourceChecks']==22 and root['syntaxCommands']==6 and len(root['commands'])==7
assert all(command['rawExitCode']==0 for command in root['commands'])and root['activationExecuted']is root['guestExecuted']is root['operationalAdmission']is False
references=[root_row]
for value in root['references']:references.append(row(value['path'],value['sha256'],value['bytes']))
assert len(references)==17
assert root['references'][-2]['sha256']=='4538ff9f04b940fc587388e0d9d985a3f1fc7b20dc0d495d3902215f996981f6'
supplement={'schemaVersion':1,'state':'STORED_ROOT_SOURCE_CHECK_EVIDENCE_REHASHED','rootReceiptSha256':root_row['sha256'],'sourceIndexSha256':r['ownerIndexSha256'],'reportedPhysicalChecks':22,'reportedSyntaxCommands':6,'reportedCommandExitCodes':[value['rawExitCode']for value in root['commands']],'pastTerminalObservedByThisReader':False,'ownerCodeExecutedByThisReader':False,'verifiedExternalReferences':references}
with(HERE/'root-source-evidence.json').open('x')as stream:json.dump(supplement,stream,indent=2);stream.write('\n')
receipt={key:value for key,value in r.items()if key!='verifiedFiles'}
receipt.update({'state':'INDEPENDENT_ZLIB350_COMPONENT_TOOL_CLOSURE_SOURCE_PASS_NO_ACTIONS','resultsSha256':sha((HERE/'results.json').read_bytes()),'rootSourceEvidenceSha256':sha((HERE/'root-source-evidence.json').read_bytes()),'sourceReadyForRootActivationReview':True,'readerCorrection':'Configured stage and frozen native.sourceRoot are distinct; incorrect draft suggestion was corrected before final review, with no owner source change or reader failure.'})
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8');assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),path
 files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_COMPONENT_TOOL_CLOSURE_SOURCE_PASS','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'sourceReadyForRootActivationReview':True,'operationalAdmission':False,'runtimeAcceptanceClaim':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for value in files:
 raw=(HERE/value['path']).read_bytes();assert sha(raw)==value['sha256']and len(raw)==value['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256'],'verifiedPaths':len(r['verifiedFiles']),'rootExternalReferences':len(references)}))
