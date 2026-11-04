"""Bounded independent source/data review and explicitly pure reader fixtures."""
from pathlib import Path
import ast
import hashlib
import json
import os
import stat
import subprocess
import sys
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
SOURCE=BASE/'production-adoption-v1/artifact-closure-current-context-amendment-v1'
SOURCE_SHA='371132b364486a7b69a1cf9c0aa447959c93d332b54e3e6b07687895880353cb'
REFS={};CACHE={}
def describe(path,expected=None,size=None):
 path=Path(path).absolute();before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 key=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
 if key not in CACHE:
  h=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
  CACHE[key]=h.hexdigest()
 after=path.lstat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value={'path':str(path),'sha256':CACHE[key],'bytes':before.st_size}
 if expected is not None:assert value['sha256']==expected,(str(path),value['sha256'],expected)
 if size is not None:assert value['bytes']==size,str(path)
 assert REFS.setdefault(str(path),value)==value
 return value
def raw(path,expected=None):describe(path,expected);return Path(path).read_bytes()
def load(path,expected=None):return json.loads(raw(path,expected))
def indexed(root,expected=None):
 doc=load(root/'index.json',expected)
 for row in doc['files']:
  name=Path(row['path']);assert not name.is_absolute() and '..' not in name.parts
  describe(root/name,row['sha256'],row['bytes'])
 return doc
def put(name,value):
 with(HERE/name).open('x') as output:json.dump(value,output,indent=2);output.write('\n')
def main():
 proposal=indexed(SOURCE,SOURCE_SHA);assert len(proposal['files'])==35
 source_inputs=load(SOURCE/'source-inputs.json');assert len(source_inputs['files'])==154
 for row in source_inputs['files']:describe(row['path'],row['sha256'],row['bytes'])
 old_root=BASE/'independent-artifact-closure-plan-review-v1'
 prior=indexed(old_root,'4929aae96f34e4cba93c3d035f23e3f0db395ca4822f20c80f5105a86086c42c')
 original=indexed(BASE/'production-adoption-v1/artifact-closure-plan-v1','96b4536ddb54484d665d93d64b6bc1af794dda977c189f50222238bad73a716e')
 assert len(prior['files'])==16 and len(original['files'])==20
 old_map=load(old_root/'all-discovered-direct-dependencies.json')['nonclassic']
 mapping=load(SOURCE/'current-context-migration-or-hold.json')
 assert len(mapping['zlibFrames'])==12 and mapping['zlibDirectOldRootRows']==60
 expected={row['manifest']:{(r['row'],r['recordedPath'],r['expectedSha256'],r['bytes']) for r in row['directOldRootRows']} for row in old_map}
 observed={};roles={}
 for frame in mapping['zlibFrames']:
  md=frame['manifest'];doc=load(md['path'],md['sha256']);describe(md['path'],md['sha256'],md['bytes']);assert len(doc['inputs'])==frame['manifestRows']
  rows=set()
  for row in frame['directOldRootRows']:
   actual=doc['inputs'][row['row']]
   assert (actual['path'],actual['sha256'],actual['bytes'])==(row['recordedPath'],row['expectedSha256'],row['bytes'])
   describe(row['beforeimageWitness'],row['expectedSha256'],row['bytes'])
   rows.add((row['row'],row['recordedPath'],row['expectedSha256'],row['bytes']))
  assert len(rows)==5 and frame['oldFamilyMayRemainRerunnableAfterPromotion'] is False
  assert 'migrationRequirement' in frame and 'originalSourceBytesCurrentlyMatch' in frame['directOldRootRows'][0]
  observed[md['path']]=rows
  if frame['role']!='historical-zlib-source-context':roles[frame['role']]=frame['decision']
 assert observed==expected
 assert roles=={'zlib-current-runtime':'FINISH_CURRENT_AUTHORIZED_WORK_THEN_HOLD_FOR_ANY_RERUN','zlib-disabled-validation':'PRESERVE_COMPLETED_EVIDENCE_HOLD_RERUN_AFTER_PROMOTION','zlib-current-source-publisher':'HOLD_PUBLICATION_AFTER_PROMOTION_UNTIL_CONTEXT_AWARE_SUCCESSOR'}
 repo=HERE.parents[3]
 five={'builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs'}
 targets={str((repo/name).resolve()) for name in five}
 for frame in mapping['zeroDirectSourceOwners']:
  md=frame['manifest'];doc=load(md['path'],md['sha256']);rows=doc.get('inputs',doc.get('files'))
  assert len(rows)==frame['rows'] and frame['directOldRootFiveRows']==0 and frame['runtimeAdmissionImplied'] is False
  assert not any(str((Path(r['path']) if Path(r['path']).is_absolute() else Path(md['path']).parent/r['path']).resolve()) in targets for r in rows)
 assert [(r['rows'],r['ownerIndex']['indexedFiles']) for r in mapping['zeroDirectSourceOwners']]==[(2261,85),(506,39)]
 draft=mapping['unsealedConsumerDraft'];assert draft['toolRows']==767 and draft['stableApprovedInput'] is False and draft['currentDraftBytesRead'] is False
 memory=mapping['memorySupplement'];md=memory['manifest'];doc=load(md['path'],md['sha256']);assert len(doc['inputs'])==memory['rows']==10295
 assert [r['row'] for r in memory['directOldRootRows']]==[11,16,19,344,345]
 for row in memory['directOldRootRows']:
  actual=doc['inputs'][row['row']];assert (actual['path'],actual['sha256'],actual['bytes'])==(row['originalPath'],row['sha256'],row['bytes'])
 assert memory['futureAuthorityIssuedByThisMap'] is False and memory['actualRunOrResultClaim'] is False
 assert memory['futureV2Candidate']=='Not sealed/reviewed/included at this amendment checkpoint; separately bind genuine successor before use.'
 failure_row=memory['RootReportedAttempt']['RootFailureReceipt'];failure=load(failure_row['path'],failure_row['sha256']);assert failure_row['sha256']=='e51149e1743030a8c2e13547575731ede0dfed0263c19d951db18aaa1db37ed1'
 assert failure['rawExitCode']==1 and failure['completedMeasuredWorkers']==failure['observedWorkerLaunches']==0
 assert all(failure[name] is False for name in ['guestExecutionDuringAttempt','wasmCompileInstantiateDuringAttempt','postOperationSourceAuditPublished','resultPublished','completionPublished','memoryObservationOrSavingsClaim','runtimeAcceptanceClaim'])
 for row in failure['references']+failure['partialOutputFiles']:describe(row['path'],row['sha256'],row['bytes'])
 terminal=load(failure['references'][0]['path']);assert terminal['returncode']==1
 partial=Path(failure['partialOutputFiles'][0]['path']).parent
 assert sorted(p.name for p in partial.iterdir())==['worker-self-manifest.json','workers'] and not list((partial/'workers').iterdir())
 snapshots=load(SOURCE/'mutable-status-snapshot.json');assert len(snapshots['files'])==7
 for row in snapshots['files']:describe(SOURCE/row['snapshotPath'],row['sha256'],row['bytes'])
 assert not(set(row['originalPath'] for row in snapshots['files']) & set(row['path'] for row in source_inputs['files']))
 assert snapshots['oldBytesAvailable'] is False and snapshots['oldHashMayMapToCurrentBytes'] is False and snapshots['zeroMismatchOld17885CopyClaim'] is False
 assert snapshots['oldAdoptionReadmeSha256']=='24e4ac4e3edb505e7e1fd6acf342352f5088628f4b966856bf8cce16facfa5ab'
 assert snapshots['files'][-1]['sha256']=='3e5992df46f39b472a3cda2fa1e2901aea6ec4be0df4c94bf3fa4248317e8d02'
 plan=load(SOURCE/'fresh-copy-plan.json');assert plan['protectedOriginalDescriptors']==17884 and len(plan['unavailableInspectionOnlyRecords'])==1
 missing=plan['unavailableInspectionOnlyRecords'][0];assert missing['archivePath'] is None and missing['oldBytesAvailable'] is False and missing['expectedSha256']==snapshots['oldAdoptionReadmeSha256']
 assert plan['freshStatusSnapshots']==snapshots['files'] and not any(plan[k] for k in ['sourcePromotionIssued','bulkCopyExecuted','archiveAcceptanceIssued','historicalProgramsOrMetadataMayBeRewritten'])
 fixtures=load(SOURCE/'actual-reader-fixtures.json');archive=Path(fixtures['archiveRoot']);fixture_map=load(archive/fixtures['mapPath'],fixtures['mapSha256']);assert len(fixture_map['contexts'])==3
 actual_descriptors=[]
 formats={'input-freeze-v1':('inputs','path'),'v11-copied-evidence-v1':('copiedEvidence','original'),'sealed-files-v1':('files','path')}
 for context in fixture_map['contexts']:
  assert context['coverage']=='selected-rows';m=context['manifest'];copied=load(archive/m['archivePath'],m['sha256']);describe(m['originalPath'],m['sha256'],m['bytes'])
  field,path_key=formats[context['format']]
  for row in context['rows']:
   assert not Path(row['archivePath']).is_absolute() and '..' not in Path(row['archivePath']).parts
   for pos in row['manifestRows']:
    r=copied[field][pos];assert (r[path_key],r['sha256'],r['bytes'])==(row['originalPath'],row['expectedSha256'],row['bytes'])
   describe(archive/row['archivePath'],row['expectedSha256'],row['bytes']);actual_descriptors.append({'contextId':context['contextId'],**row})
 assert len(actual_descriptors)==9 and fixtures['fullArchiveCopyOrAcceptanceClaim'] is False
 reader=raw(SOURCE/'archive-context-reader.py').decode();tree=ast.parse(reader)
 assert not any(isinstance(node,(ast.ImportFrom,)) and node.module and not node.module.split('.')[0] in {'pathlib'} for node in ast.walk(tree))
 assert 'os.O_DIRECTORY|os.O_NOFOLLOW' in reader and 'os.O_RDONLY|os.O_NOFOLLOW' in reader
 assert "key=(identity,original,digest)" in reader and "key=(text(context_id),text(original_path),sha_text(expected_sha256))" in reader
 assert "document=self._json(manifest['archivePath'],manifest['sha256'],manifest['bytes'])" in reader
 assert "record.get(path_key)==original" in reader and "covered==set(range(len(records)))" in reader
 assert 'originalPath' not in ''.join(ast.unparse(node) for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ['open','read_bytes','read_text'])
 # Two authenticated owned-data tests import only this archive reader, and
 # exercise selected text fixtures/temp-owned data. No owner/runtime helper.
 pure=[]
 for name,count in [('test-reader.py',23),('test-context-map.py',12)]:
  ast.parse(raw(SOURCE/name));command=[sys.executable,str(SOURCE/name)]
  process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  for stream,data in [('stdout',process.stdout),('stderr',process.stderr)]:
   with(HERE/(name+'.'+stream+'.log')).open('xb') as out:out.write(data)
  assert process.returncode==0,(name,process.stderr.decode())
  output=json.loads(process.stdout);assert output['passed']==count
  pure.append({'argv':command,'exitCode':process.returncode,'observedByThisReader':True,'checks':count,'stdout':describe(HERE/(name+'.stdout.log')),'stderr':describe(HERE/(name+'.stderr.log'))})
 for row in proposal['files']:describe(SOURCE/row['path'],row['sha256'],row['bytes'])
 result={'schemaVersion':1,'state':'INDEPENDENT_CURRENT_CONTEXT_AMENDMENT_SOURCE_PASSED_PROMOTION_STILL_HELD','candidateIndexSha256':SOURCE_SHA,'candidateFiles':35,'candidateReferences':154,'originalPlanIndexSha256':'96b4536ddb54484d665d93d64b6bc1af794dda977c189f50222238bad73a716e','originalHoldReviewIndexSha256':'4929aae96f34e4cba93c3d035f23e3f0db395ca4822f20c80f5105a86086c42c','zlibManifests':12,'zlibExactDirectRows':60,'currentDecisions':roles,'memoryExactDirectRows':5,'memoryAttempt':{'receiptSha256':failure_row['sha256'],'rootReportedOuterExit':1,'workerLaunches':0,'completedWorkers':0,'newMeasurementClaim':False,'ownPreviousSourceReviewMissAcknowledged':True,'rootOuterTerminalObservedByThisReader':False,'futureV2UnsealedUnreviewedAtCheckpoint':True},'zeroDirectNativeProducerRows':2261,'zeroDirectConsumerSourceRows':506,'unsealed767SnapshotOnly':True,'freshStatusSnapshots':7,'old24eBytesRecovered':False,'unequalOldToNewMapping':False,'protected17884RehashRepeated':False,'priorProtectedProofRetainedByHash':True,'actualSelectedReaderDescriptors':9,'readerScope':'Pinned map + pinned copied original manifest + exact context/literalPath/hash/size/row -> normalized no-follow archive-relative target; original paths remain data only.','ownedPureChecks':pure,'pureChecksTotal':35,'sourcePromotionHeld':True,'currentOwnerMigrationCompleted':False,'newArchiveCreated':False,'runtimeOrMemoryOrAcceptanceClaim':False,'ownerNativeRuntimePreflightGuestHostTimingHelpersExecuted':False,'historicalDescriptorsProgramsOrNativeMetadataEdited':False}
 put('results.json',result);put('selected-descriptor-ledger.json',{'records':actual_descriptors,'selectedOnly':True,'fullArchiveClaim':False});put('external-references.json',{'files':[r for r in sorted(REFS.values(),key=lambda row:row['path']) if not Path(r['path']).is_relative_to(HERE)],'fullProtectedAuditRepeated':False})
 print(json.dumps({'state':result['state'],'candidateFiles':35,'references':154,'pureChecks':35,'selectedReaderDescriptors':9,'promotionHeld':True}))
if __name__=='__main__':main()
