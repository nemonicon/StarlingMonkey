"""Owned tiny filesystem/data tests only; no real publisher or owner action."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,tempfile
from copy_primitives import PrivateRoot,check_source
import copy_primitives
import publisher
HERE=Path(__file__).resolve().parent
arguments=argparse.ArgumentParser(description=__doc__);arguments.add_argument('--output',type=Path,default=HERE/'scratch-results.json');args=arguments.parse_args()
def sha(data):return hashlib.sha256(data).hexdigest()
def module(path):
    spec=importlib.util.spec_from_file_location('reviewed_reader_scratch',path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
checks=[]
def passed(name):checks.append(name)
def rejected(name,call):
    try:call()
    except(ValueError,OSError,AssertionError,KeyError):passed(name)
    else:raise AssertionError('Expected refusal: '+name)
with tempfile.TemporaryDirectory(prefix='classic-preservation-scratch-',dir='/tmp/starling-node-compat')as temporary:
    base=Path(temporary).resolve();source=base/'original.txt';source.write_bytes(b'owned source\n');row={'source':str(source),'destination':'objects/item.data','sha256':sha(source.read_bytes()),'bytes':source.stat().st_size}
    original_inode=source.stat().st_ino
    with PrivateRoot(base/'clean')as root:
        root.copy(row);root.check(row);assert(source.stat().st_ino,source.stat().st_nlink)==(original_inode,1);assert(root.parent/root.path.name/'objects/item.data').read_bytes()==b'owned source\n';passed('exclusiveCopyAndOriginalRetained')
        assert set(root.files())=={'objects/item.data'};passed('actualClosureMatchesRecordedWrites')
        rejected('existingTargetNotOverwritten',lambda:root.copy(row))
        (base/'clean/objects/item.data').write_bytes(b'owned change\n');rejected('targetHashDriftRefuses',lambda:root.check(row))
    bad=copy.deepcopy(row);bad['sha256']='0'*64
    rejected('sourceHashDriftRefuses',lambda:check_source(bad))
    with PrivateRoot(base/'changed-source')as root:
        rejected('sourceAfterCopyDriftRefuses',lambda:root.copy(row,lambda:source.write_bytes(b'changed after\n')))
        assert(base/'changed-source/objects/item.data').exists()and not(base/'changed-source/completion.json').exists();passed('partialOwnedCopyRetainedWithoutCompletion')
    source.write_bytes(b'owned source\n')
    existing=base/'raced-destination';existing.mkdir();(existing/'untouched').write_text('own prior data')
    rejected('racedExistingRootRefuses',lambda:PrivateRoot(existing));assert(existing/'untouched').read_text()=='own prior data'
    (base/'root-link').symlink_to(existing,target_is_directory=True);rejected('symlinkRootRefuses',lambda:PrivateRoot(base/'root-link'))
    (base/'source-link').symlink_to(source);rejected('sourceSymlinkRefuses',lambda:check_source({**row,'source':str(base/'source-link')}))
    directory=base/'source-dir';directory.mkdir();(directory/'text').write_bytes(b'owned source\n');(base/'dir-link').symlink_to(directory,target_is_directory=True)
    rejected('sourceAncestorSymlinkRefuses',lambda:check_source({**row,'source':str(base/'dir-link/text')}))
    with PrivateRoot(base/'target-link')as root:
        (base/'target-link/objects').symlink_to(existing,target_is_directory=True);rejected('targetAncestorSymlinkRefuses',lambda:root.copy(row));assert(existing/'untouched').read_text()=='own prior data'
    with PrivateRoot(base/'root-replaced')as root:
        root.copy(row);(base/'root-replaced').rename(base/'retained-partial');(base/'root-replaced').mkdir()
        rejected('rootReplacementRefusesBeforeCompletion',lambda:root.json('completion.json',{'success':True},success_marker=True));assert not(base/'retained-partial/completion.json').exists()and not(base/'root-replaced/completion.json').exists()
    with PrivateRoot(base/'marker-race')as root:
        original_check=root.check_identity;calls=[0]
        def replace_during_marker():
            calls[0]+=1
            if calls[0]==2:(base/'marker-race').rename(base/'marker-race-retained');(base/'marker-race').mkdir()
            return original_check()
        root.check_identity=replace_during_marker
        rejected('rootReplacedDuringMarkerRemovesOnlyOwnedMarker',lambda:root.json('completion.json',{'state':'PENDING'},success_marker=True));assert not(base/'marker-race-retained/completion.json').exists()and not(base/'marker-race/completion.json').exists()
    with PrivateRoot(base/'foreign-file')as root:
        root.write('known.txt',b'known');(base/'foreign-file/foreign.txt').write_text('unrecorded')
        rejected('unrecordedFileCannotSealClosure',lambda:publisher.need(root.files()==sorted(root.written),'Unknown file'));assert not(base/'foreign-file/completion.json').exists()
    with PrivateRoot(base/'hardlink')as root:
        root.copy(row);os.link(base/'hardlink/objects/item.data',base/'hardlink/extra-link');rejected('outputHardlinkRefusesClosure',lambda:root.files());assert source.stat().st_nlink==1
    with PrivateRoot(base/'reader')as root:
        payload=b'original owned bytes\n';original_path='../historical/literal.mjs';target=root.write('objects/source.data',payload)
        manifest={'inputs':[{'path':original_path,'sha256':sha(payload),'bytes':len(payload)}]};manifest_file=root.json('objects/manifest.json',manifest)
        mapping={'schemaVersion':1,'state':'EXPLICIT_ARCHIVE_CONTEXT_MAP_V1','contexts':[{'contextId':'owned','format':'input-freeze-v1','coverage':'selected-rows','manifest':{'originalPath':'/never-open-this/manifest.json','archivePath':'objects/manifest.json','sha256':manifest_file['sha256'],'bytes':manifest_file['bytes']},'rows':[{'manifestRows':[0],'originalPath':original_path,'expectedSha256':sha(payload),'bytes':len(payload),'archivePath':'objects/source.data'}]}]}
        map_file=root.json('maps/map.json',mapping);reader=module(HERE/'archive-context-reader.py')
        with reader.ArchiveContextReader(str(base/'reader'),'maps/map.json',map_file['sha256'])as archive:
            assert archive.verify('owned',original_path,sha(payload))['originalFilesystemOpened']is False;passed('reviewedReaderVerifiesCopiedBytesNotOriginalPath')
            rejected('unknownContextTupleRefuses',lambda:archive.verify('unknown',original_path,sha(payload)))
        index=root.json('index.json',{'files':list(root.written.values())});completion=root.json('completion.json',{'state':'PENDING_INDEPENDENT_REVIEW','accepted':False,'index':index},success_marker=True)
        root.check_identity();assert completion['path']=='completion.json';passed('ownedTinyPendingIndexAndCompletionOnly')
    omission={'originalPath':'/unavailable/README.md','expectedSha256':'24e4ac4e3edb505e7e1fd6acf342352f5088628f4b966856bf8cce16facfa5ab','bytes':37053,'archivePath':None,'oldBytesAvailable':False}
    omission_plan={'omissions':[omission],'contextMap':{'contexts':[]}};assert publisher.validate_omissions(omission_plan);passed('oneExactUnavailableInspectionTupleAllowedAsUnmappedData')
    bad=copy.deepcopy(omission_plan);bad['omissions'][0]['archivePath']='objects/new-readme.data';rejected('unequalFreshReadmeCannotReplaceUnavailableBytes',lambda:publisher.validate_omissions(bad))
    bad=copy.deepcopy(omission_plan);bad['omissions'].append(copy.deepcopy(omission));rejected('secondUnavailableExceptionRefuses',lambda:publisher.validate_omissions(bad))
    cfg={'schemaVersion':1,'state':'ROOT_REVIEWED_CLASSIC_PRIVATE_PRESERVATION_COPY_V1','candidateIndexSha256':'1'*64,'copyPlanSha256':'2'*64,'privateDestination':publisher.DESTINATION,'copyAllowed':True,'pendingOnly':True,'archiveAcceptanceAllowed':False,'sourcePromotionAllowed':False,'lateMemoryIndependentProof':None}
    rejected('lateProofNullRefusesBeforeAnyRootCreation',lambda:publisher.reviewed_config(cfg,'1'*64,'2'*64))
    cfg['lateMemoryIndependentProof']={'rootReviewedPassed':True,'index':{'path':'/owned-synthetic/index.json','sha256':'3'*64,'bytes':1},'result':{'path':'/owned-synthetic/results.json','sha256':'4'*64,'bytes':1}}
    rejected('sourceReviewNullRefusesBeforeAnyRootCreation',lambda:publisher.reviewed_config(cfg,'1'*64,'2'*64))
    future=json.loads((HERE/'future-root-config.json').read_bytes());rejected('checkedInRootAuthorityRemainsClosed',lambda:publisher.reviewed_config(future,'1'*64,'2'*64))
    policy_path=HERE.parent/'root-source-context-rollforward-policy-v1.json';policy_raw=policy_path.read_bytes();assert sha(policy_raw)=='20a32c37de8fc1fe3bcbdecaa751377918d921f79ba6bcef91eb8943895eecc6';policy=json.loads(policy_raw)
    expected={k:policy[k]for k in ['schemaVersion','state','sourcePromotionAllowed','archiveAcceptanceAllowed','runtimeAcceptanceClaim','preservationPlanIndexSha256','contextAmendmentIndexSha256','contextReviewIndexSha256','typedHoldMapSha256','memoryRootReceiptSha256','memoryIndependentProofIndexSha256','memoryCompletedUnderOldContext','unavailableReadmeSha256','statusSnapshotManifestSha256','historicalPreflightRerunAllowed','futureFamiliesRequireNewContextReview','acceptedTypedHoldDecisions']}
    assert publisher.validate_decision(policy,{'expectedMigrationPolicyFields':expected});passed('genuinePinnedFormalRootPolicyFieldsAcceptedAsData')
    for field,value in [('sourcePromotionAllowed',True),('archiveAcceptanceAllowed',True),('historicalPreflightRerunAllowed',True),('typedHoldMapSha256','0'*64),('state','UNREVIEWED')]:
        bad=copy.deepcopy(policy);bad[field]=value;rejected('formalPolicyRefuses:'+field,lambda bad=bad:publisher.validate_decision(bad,{'expectedMigrationPolicyFields':expected}))
    bad=copy.deepcopy(policy);bad['acceptedTypedHoldDecisions'].pop();rejected('allTwelveTypedDecisionsRequired',lambda:publisher.validate_decision(bad,{'expectedMigrationPolicyFields':expected}))
    peer={'schemaVersion':1,'state':'INDEPENDENT_CLASSIC_PRESERVATION_PUBLISHER_SOURCE_REVIEW_PASSED','publisherSourceIndexSha256':'1'*64,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'archiveCopyExecuted':False,'sourcePromotionIssued':False,'runtimeAcceptanceClaim':False}
    assert publisher.source_review_result(peer,'1'*64);passed('sourceReviewShapeOnlyModelAcceptedNoAuthorityIssued')
    for key,value in [('publisherSourceIndexSha256','0'*64),('sourceOnly',False),('sourceReviewPassed',False),('ownerActionsInvoked',True),('archiveCopyExecuted',True),('sourcePromotionIssued',True),('runtimeAcceptanceClaim',True)]:
        bad=copy.deepcopy(peer);bad[key]=value;rejected('sourceReviewResultRefuses:'+key,lambda bad=bad:publisher.source_review_result(bad,'1'*64))
    reviewdir=base/'owned-synthetic-source-review';reviewdir.mkdir();resultfile=reviewdir/'result.json';indexfile=reviewdir/'index.json'
    resultfile.write_text(json.dumps(peer)+'\n');record={'path':'result.json','sha256':sha(resultfile.read_bytes()),'bytes':resultfile.stat().st_size};indexfile.write_text(json.dumps({'schemaVersion':1,'files':[record]})+'\n')
    review_config={'sourceIndependentReview':{'index':{'path':str(indexfile),'sha256':sha(indexfile.read_bytes()),'bytes':indexfile.stat().st_size},'result':{'path':str(resultfile),'sha256':record['sha256'],'bytes':record['bytes']},'rootReviewedPassed':True}}
    assert len(publisher.source_review_capsule(review_config,'1'*64,copy_primitives))==2;passed('ownedSyntheticIndexedSourceReviewCapsuleOnly')
    resultfile.write_text('changed owned review\n');rejected('indexedSourceReviewHashDriftRefuses',lambda:publisher.source_review_capsule(review_config,'1'*64,copy_primitives));resultfile.write_text(json.dumps(peer)+'\n')
    wrong=copy.deepcopy(review_config);wrong['sourceIndependentReview']['result']['path']=str(reviewdir/'unindexed.json');rejected('unindexedSourceReviewResultRefuses',lambda:publisher.source_review_capsule(wrong,'1'*64,copy_primitives))
    binary=reviewdir/'binary.data';binary.write_bytes(b'owned\0binary');indexfile.write_text(json.dumps({'schemaVersion':1,'files':[record,{'path':'binary.data','sha256':sha(binary.read_bytes()),'bytes':binary.stat().st_size}]})+'\n');bad=copy.deepcopy(review_config);bad['sourceIndependentReview']['index']={'path':str(indexfile),'sha256':sha(indexfile.read_bytes()),'bytes':indexfile.stat().st_size};rejected('indexedSourceReviewMustBeTextOnly',lambda:publisher.source_review_capsule(bad,'1'*64,copy_primitives))
result={'schemaVersion':1,'state':'OWNED_TINY_COPY_AND_DATA_GUARD_CHECKS_PASSED','checks':checks,'passed':len(checks),'actualArchiveOrOwnerActionsExecuted':False,'scratchScope':'Only owned temporary text fixtures and copied reviewed data-only reader; no protected source/real artifact was written or copied.'}
with args.output.open('x')as output:json.dump(result,output,indent=2);output.write('\n')
print(json.dumps({'state':result['state'],'passed':len(checks),'actualArchiveExecuted':False}))
