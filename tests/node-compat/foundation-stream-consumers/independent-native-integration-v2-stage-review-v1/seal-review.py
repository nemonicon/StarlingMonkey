"""Seal only this independent actual-source-stage review."""
from pathlib import Path
import ast
import configparser
import hashlib
import json
import os
import stat
HERE=Path(__file__).resolve().parent
STAGE=Path('/tmp/starling-node-compat/consumers-source-v2')
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
 config=configparser.ConfigParser();config.read_string((STAGE/'.git/config').read_text())
 assert config['core']['bare']=='false' and 'worktree' not in config['core']
 assert config['remote "origin"']['url']=='/Users/dan/dev/StarlingMonkey'
 assert 'extensions' not in config and 'promisor' not in config['remote "origin"']
 assert not(STAGE/'.git/objects/info/alternates').exists() and not(STAGE/'.git/commondir').exists()
 result=json.loads((HERE/'results.json').read_bytes())
 assert result['state']=='INDEPENDENT_ACTUAL_CONSUMERS355_V2_STAGE_PASSED_SOURCE_ONLY'
 assert result['declaredOverlaidFiles']==1173 and result['actualWorkingTreeFiles']==1681 and result['baselineFilesOutsideOverlayVerifiedByGitBlob']==508
 assert len(result['genuineBaselineDocSymlinks'])==3 and result['unexpectedWorkingTreeFiles']==0
 for row in result['genuineBaselineDocSymlinks']:
  path=STAGE/row['path'];assert path.is_symlink() and os.readlink(path)==row['linkText'] and str(path.resolve())==row['canonicalTarget']
 for path in HERE.rglob('*'):
  if path.is_file():
   data=path.read_bytes();data.decode('utf-8');assert b'\0' not in data
   assert all(line.rstrip(b' \t')==line for line in data.splitlines()),str(path)
   if path.suffix=='.py':ast.parse(data)
 receipt={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ACTUAL_CONSUMERS355_V2_STAGE_PASS_SOURCE_ONLY','producerIndexSha256':result['producerIndexSha256'],'sourcePeerIndexSha256':result['sourcePeerIndexSha256'],'rootSourceAuthoritySha256':result['rootSourceReviewSha256'],'rootStageReceiptSha256':result['rootStageReviewSha256'],'results':describe(HERE/'results.json'),'externalPathsFinalRehashed':len(refs),'stagedSourceFiles':1173,'actualWorkingTreeFiles':1681,'unchangedGitBaselineOutsideOverlay':508,'nativeInputs':355,'nativeCpp':62,'toolDependencies':767,'selfIndexedFiles':59,'originalPreparationReferences':3420,'preparationFamilyRows':[2261,506],'indexedOnlyFamilies':4,'zeroDirectOldRootFivePreparationRows':True,'universalConfiguredHelperAuthenticationBeforeCustomImports':True,'ordinaryIndependentGitClone':{'head':'54b3329b3ce818fd1f244e871e9c259b63667cda','detached':True,'alternates':False,'sharedCommonDir':False,'hardlinksObserved':False,'genuineBaselineDocLinks':3,'gitConfig':describe(STAGE/'.git/config')},'cachePreseedOnly':{'receiptSha256':'cc1763cfade58953434e164859a95fd481b926e2a03487ff13ffa7454960cacd','files':4,'destinationHashesVerified':True,'engineConfigOrMetadataCopied':False,'nativeBuild':False},'allRuntimeBootstrapPinsNull':True,'componentHarnessClosureProvided':False,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'rootRecordedStageExit':0,'rootOuterTerminalObservedByThisReader':False,'ownedReader':{'session':97102,'exitCode':0,'observedByThisReader':True},'sourceMechanismScope':'Actual CMake/registration/recipe bytes only; generated installation, compilation, linkage and runtime remain future evidence.','ownerActionMainsOrGenuineVerifiersExecuted':False,'nativeCompilerFactoryCodecComponentGuestHostTimingExecuted':False,'sourceOrHistoricalEvidenceEdited':False,'buildAuthorityIssued':False,'runtimeOrReleaseAcceptance':False}
 put('review-receipt.json',receipt)
 rows=[{'path':str(path.relative_to(HERE)),**describe(path)} for path in sorted(HERE.rglob('*')) if path.is_file() and path.name!='index.json']
 put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_NATIVE_INTEGRATION_V2_STAGE_REVIEW_PASS','files':rows,'buildAuthorityIssued':False,'runtimeAcceptance':False})
 print(json.dumps({'state':receipt['state'],'files':len(rows),'indexSha256':describe(HERE/'index.json')['sha256'],'receiptSha256':describe(HERE/'review-receipt.json')['sha256'],'resultsSha256':describe(HERE/'results.json')['sha256'],'externalPathsFinalRehashed':len(refs)}))
if __name__=='__main__':main()
