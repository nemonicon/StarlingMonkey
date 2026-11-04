"""One private PENDING preservation copy. No owner/preflight/runtime imports."""
import argparse,hashlib,importlib.util,json,os,shutil,stat,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
DESTINATION='/tmp/starling-node-compat/classic-artifact-preservation-pending-v1'
SHA=lambda value:type(value)is str and len(value)==64 and all(c in'0123456789abcdef'for c in value)
def need(value,message):
    if not value:raise ValueError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def raw(path,expected,max_bytes=64*1024*1024):
    path=Path(path);info=path.lstat();need(stat.S_ISREG(info.st_mode)and not path.is_symlink()and info.st_size<=max_bytes,'Regular bounded descriptor required')
    value=path.read_bytes();need(digest(value)==expected,'Descriptor hash mismatch');return value
def source_index(expected):
    index=json.loads(raw(HERE/'index.json',expected));need(index['schemaVersion']==1,'Source index schema')
    seen=set()
    for row in index['files']:
        name=row['path'];need(type(name)is str and name not in seen and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/')),'Unsafe source index row');seen.add(name)
        data=raw(HERE/name,row['sha256']);need(len(data)==row['bytes'],'Source index bytes')
    return index
def reviewed_config(value,own_sha,plan_sha):
    need(type(value)is dict and value.get('schemaVersion')==1,'Root config required')
    need(value.get('state')=='ROOT_REVIEWED_CLASSIC_PRIVATE_PRESERVATION_COPY_V1','No Root copy approval')
    need(value.get('candidateIndexSha256')==own_sha and value.get('copyPlanSha256')==plan_sha,'Exact source/plan binding required')
    need(value.get('privateDestination')==DESTINATION,'One fixed private destination')
    need(value.get('copyAllowed')is True and value.get('pendingOnly')is True,'Pending-copy-only approval required')
    need(value.get('archiveAcceptanceAllowed')is False and value.get('sourcePromotionAllowed')is False,'No acceptance or source promotion')
    proof=value.get('lateMemoryIndependentProof');need(type(proof)is dict,'Pending late memory proof refuses before root creation')
    need(proof.get('rootReviewedPassed')is True,'Root must separately review late result proof')
    for key in ['index','result']:
        row=proof.get(key);need(type(row)is dict and type(row.get('path'))is str and Path(row['path']).is_absolute()and SHA(row.get('sha256'))and type(row.get('bytes'))is int and row['bytes']>=0,'Exact late proof descriptors required')
    source_review=value.get('sourceIndependentReview');need(type(source_review)is dict and source_review.get('rootReviewedPassed')is True,'Explicit independent publisher-source review required')
    for key in ['index','result']:
        row=source_review.get(key);need(type(row)is dict and type(row.get('path'))is str and Path(row['path']).is_absolute()and SHA(row.get('sha256'))and type(row.get('bytes'))is int and row['bytes']>=0,'Exact source-review descriptors required')
    decision=value.get('migrationDecision');need(type(decision)is dict and value.get('migrationDecisionReviewed')is True,'Explicit Root-reviewed migration/hold decision required')
    need(type(decision.get('path'))is str and Path(decision['path']).is_absolute()and SHA(decision.get('sha256'))and type(decision.get('bytes'))is int and decision['bytes']>=0,'Exact migration/hold descriptor required')
    return value
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def verify_links(rows):
    for row in rows:
        path=Path(row['path']);need(path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve(strict=True))==row['resolvedTarget'],'Link provenance drift')
def validate_decision(value,plan):
    need(type(value)is dict,'Formal policy document required')
    for key,expected in plan['expectedMigrationPolicyFields'].items():need(value.get(key)==expected,'Formal policy mismatch: '+key)
    need(len(value['acceptedTypedHoldDecisions'])==12,'All twelve typed holds required')
    return True
def validate_omissions(plan):
    rows=plan.get('omissions');need(type(rows)is list and len(rows)==1,'Only one unavailable inspection descriptor')
    row=rows[0];need(row.get('expectedSha256')=='24e4ac4e3edb505e7e1fd6acf342352f5088628f4b966856bf8cce16facfa5ab'and row.get('bytes')==37053 and row.get('archivePath')is None and row.get('oldBytesAvailable')is False,'Unavailable README cannot map to unequal replacement bytes')
    for context in plan['contextMap']['contexts']:
        need(not any(entry['originalPath']==row['originalPath']and entry['expectedSha256']==row['expectedSha256']for entry in context['rows']),'Unavailable README must remain unmapped')
    return True
def extra_proof(config,primitive):
    proof=config['lateMemoryIndependentProof'];index_row=proof['index'];index_raw=primitive.check_source({'source':index_row['path'],'sha256':index_row['sha256'],'bytes':index_row['bytes']},True);index=json.loads(index_raw)
    need(index.get('schemaVersion')==1 and type(index.get('files'))is list,'Proof index required')
    rows=[{'source':index_row['path'],'destination':'evidence/late-memory-proof/index.json','sha256':index_row['sha256'],'bytes':index_row['bytes'],'kind':'late-proof-text'}];found=0;seen=set()
    for row in index['files']:
        name=row['path'];need(type(name)is str and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'))and name not in seen,'Unsafe proof row');seen.add(name)
        path=Path(index_row['path']).parent/name;source={'source':str(path),'destination':'evidence/late-memory-proof/'+name,'sha256':row['sha256'],'bytes':row['bytes'],'kind':'late-proof-text'}
        text=primitive.check_source(source,True);need(b'\0'not in text,'Proof is text only');text.decode('utf-8','strict');rows.append(source)
        if str(path)==proof['result']['path']:need(row['sha256']==proof['result']['sha256']and row['bytes']==proof['result']['bytes'],'Result proof differs from index');found+=1
    need(found==1,'Root-reviewed result must be indexed exactly once');return rows
def source_review_result(value,own_sha):
    expected={'schemaVersion':1,'state':'INDEPENDENT_CLASSIC_PRESERVATION_PUBLISHER_SOURCE_REVIEW_PASSED','publisherSourceIndexSha256':own_sha,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'archiveCopyExecuted':False,'sourcePromotionIssued':False,'runtimeAcceptanceClaim':False}
    need(type(value)is dict,'Independent source result required')
    for key,want in expected.items():need(type(value.get(key))is type(want)and value.get(key)==want,'Independent source result mismatch: '+key)
    return True
def source_review_capsule(config,own_sha,primitive):
    proof=config['sourceIndependentReview'];row=proof['index'];need(row['bytes']<=1024*1024,'Finite source-review index bound')
    value=primitive.check_source({'source':row['path'],'sha256':row['sha256'],'bytes':row['bytes']},True);index=json.loads(value)
    need(index.get('schemaVersion')==1 and type(index.get('files'))is list and 0<len(index['files'])<=256,'Finite indexed source review required')
    rows=[{'source':row['path'],'destination':'evidence/publisher-source-review/index.json','sha256':row['sha256'],'bytes':row['bytes'],'kind':'source-review-text'}];seen=set();found=0
    for entry in index['files']:
        name=entry['path'];need(type(name)is str and '\\'not in name and '\0'not in name and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'))and name not in seen,'Unsafe source-review name');seen.add(name)
        need(type(entry['bytes'])is int and 0<=entry['bytes']<=64*1024*1024,'Finite text source-review member required')
        path=Path(row['path']).parent/name;copy={'source':str(path),'destination':'evidence/publisher-source-review/'+name,'sha256':entry['sha256'],'bytes':entry['bytes'],'kind':'source-review-text'}
        data=primitive.check_source(copy,True);need(b'\0'not in data,'Source review is text only');data.decode('utf-8','strict');rows.append(copy)
        if str(path)==proof['result']['path']:
            need(entry['sha256']==proof['result']['sha256']and entry['bytes']==proof['result']['bytes'],'Source result differs from index');source_review_result(json.loads(data),own_sha);found+=1
    need(found==1,'Independent source result must be indexed exactly once');return rows
def perform(plan,config,authority_bytes,own_sha,index,primitive,after_copy=None,authority_source=None):
    validate_omissions(plan)
    for key in ['index','result']:need(config['lateMemoryIndependentProof'][key]==plan['lateMemoryIndependentProof'][key],'Only explicitly planned actual memory proof is allowed')
    proof_rows=extra_proof(config,primitive);source_review_rows=source_review_capsule(config,own_sha,primitive)
    own_rows=[{'source':str(HERE/'index.json'),'destination':'metadata/publisher-source/index.json','sha256':own_sha,'bytes':(HERE/'index.json').stat().st_size}]+[{'source':str(HERE/row['path']),'destination':'metadata/publisher-source/'+row['path'],'sha256':row['sha256'],'bytes':row['bytes']}for row in index['files']]
    objects=plan['objects']+proof_rows+source_review_rows+own_rows;need(len({row['destination']for row in objects})==len(objects),'Copy target collision')
    inputs=plan['originalInputs']+proof_rows+source_review_rows+own_rows
    decision=config['migrationDecision'];decision_row={'source':decision['path'],'destination':'metadata/root-context-migration-or-hold-decision.json','sha256':decision['sha256'],'bytes':decision['bytes'],'kind':'root-decision-text'}
    need(decision==plan['migrationDecision'],'Only exact planned formal Root policy allowed')
    decision_bytes=primitive.check_source(decision_row,True);need(b'\0'not in decision_bytes,'Decision is text data');validate_decision(json.loads(decision_bytes),plan);objects.append(decision_row);inputs.append(decision_row)
    if authority_source is not None:inputs.append(authority_source)
    for row in inputs:primitive.check_source(row)
    verify_links(plan['links'])
    logical=sum(row['bytes']for row in objects);required=2*logical+1024**3
    need(shutil.disk_usage(Path(DESTINATION).parent).free>=required,'Two logical copies plus1GiB reserve required')
    root=None;completion=None
    try:
        root=primitive.PrivateRoot(DESTINATION);root.json('journal/000000-start.json',{'state':'PRIVATE_PENDING_COPY_STARTED','accepted':False,'candidateIndexSha256':own_sha,'copyPlanSha256':config['copyPlanSha256'],'logicalCopyBytes':logical,'initialRequiredFreeBytes':required})
        copied=[];remaining=logical
        for position,row in enumerate(objects):
            need(shutil.disk_usage(Path(DESTINATION).parent).free>=remaining+1024**3,'Remaining logical bytes plus1GiB reserve required')
            root.copy(row,(lambda:after_copy(root,position))if after_copy else None);remaining-=row['bytes'];copied.append({**row,'original':row['source']})
            root.json('journal/'+str(position+1).zfill(6)+'.json',{'state':'OBJECT_COPIED_PARTIAL_ONLY','path':row['destination'],'sha256':row['sha256'],'bytes':row['bytes']})
        for row in inputs:primitive.check_source(row)
        for row in objects:root.check(row)
        verify_links(plan['links']);root.check_identity()
        context_file=root.json('maps/context-map.json',plan['contextMap']);root.json('maps/original-paths.json',plan['originalMap']);root.json('maps/reference-context-rows.json',plan['unmappedContextRows']);root.json('maps/link-provenance.json',plan['links']);root.json('maps/unavailable-inspection-only.json',plan['omissions']);root.json('maps/separate-status-snapshots.json',plan['separateStatusSnapshots'])
        root.write('metadata/root-copy-authorization.json',authority_bytes)
        reader=module('reviewed_data_only_archive_reader',HERE/'archive-context-reader.py')
        with reader.ArchiveContextReader(str(root.parent/root.path.name),'maps/context-map.json',context_file['sha256'])as data_reader:
            mapped=data_reader.verify_all();need(len(data_reader.contexts)==20,'Eight classic+twelve selected zlib contexts required')
        result={'schemaVersion':1,'state':'PENDING_INDEPENDENT_REVIEW','accepted':False,'candidateIndexSha256':own_sha,'copyPlanSha256':config['copyPlanSha256'],'rootAuthorizationSha256':digest(authority_bytes),'protectedOriginalDescriptors':17884,'unavailableHistoricalDescriptors':plan['omissions'],'copiedObjects':copied,'externalReferences':[row for row in plan['originalInputs']if row['kind']=='reference'],'contextRowsVerified':len(mapped),'contextCoverage':'selected-rows','linksRechecked':len(plan['links']),'lateMemoryIndependentProof':config['lateMemoryIndependentProof'],'rootIdentity':{'device':root.root_id.st_dev,'inode':root.root_id.st_ino},'fullZlib350OrConsumers355ArchiveClaim':False,'sourcePromotionPerformed':False,'archiveAcceptanceIssued':False,'ownerRuntimeExecuted':False}
        result_file=root.json('results.json',result)
        root.json('README.json',{'state':'PRIVATE_PENDING_INDEPENDENT_REVIEW','accepted':False,'historicalProgramsRerunnableClaim':False,'SDKHostBinariesCopied':False,'sourcePromotionAllowed':False,'knownScope':'Classic bounded artifacts +late memory evidence.350/355 remain separate. OldREADME24e unavailable. Status snapshots are distinct captures.'})
        root.check_identity()
        need(root.files()==sorted(root.written),'Unexpected unowned archive member')
        archive_rows=[root.written[name]for name in sorted(root.written)]
        for row in archive_rows:root.check({'destination':row['path'],'sha256':row['sha256'],'bytes':row['bytes']})
        archive_index=root.json('index.json',{'schemaVersion':1,'state':'PRIVATE_PENDING_PRESERVATION_INDEX','accepted':False,'files':archive_rows,'externalReferencesRemainReferences':True})
        # Captured primitive authority/source/index hashes are rechecked at the
        # final boundary, not recomputed from publicly returned mutable records.
        boundary_rows=[own_rows[0],next(r for r in own_rows if r['destination']=='metadata/publisher-source/copy-plan.json'),proof_rows[0],source_review_rows[0],decision_row]
        if authority_source is not None:boundary_rows.append(authority_source)
        for row in boundary_rows:primitive.check_source(row)
        # This is an exclusive private completion marker, not directory rename,
        # publication acceptance or permission to promote the live five files.
        completion=root.json('completion.json',{'schemaVersion':1,'state':'PENDING_INDEPENDENT_REVIEW','accepted':False,'result':result_file,'index':archive_index,'candidateIndexSha256':own_sha,'copyPlanSha256':config['copyPlanSha256'],'rootIdentity':result['rootIdentity'],'requiresActualExternalExitZeroAndIndependentValidation':True},success_marker=True)
        root.check_identity();need(root.files()==sorted(root.written),'Unexpected final archive member');return result,completion
    except BaseException as error:
        if root is not None:
            root.discard_owned_success_marker('completion.json')
            try:root.json('journal/failure.json',{'state':'FAILED_OR_PARTIAL_PRIVATE_COPY','error':{'type':type(error).__name__,'message':str(error)},'accepted':False,'partialOwnedFilesRetained':True})
            except BaseException:pass
        raise
    finally:
        if root is not None:root.close()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('index_sha');parser.add_argument('--root-config');parser.add_argument('--root-config-sha');args=parser.parse_args()
    need(SHA(args.index_sha),'Exact candidate index SHA required');index=source_index(args.index_sha)
    plan_row=next(row for row in index['files']if row['path']=='copy-plan.json');plan=json.loads(raw(HERE/'copy-plan.json',plan_row['sha256']));need(plan['protectedOriginalDescriptors']==17884 and type(plan['lateMemoryIndependentProof'])is dict,'Finite strict plan with actual late proof required')
    if args.root_config is None:
        print(json.dumps({'state':'SOURCE_COPY_PLAN_ONLY_ACTION_BLOCKED','copyPlanSha256':plan_row['sha256'],'lateMemoryIndependentProof':plan['lateMemoryIndependentProof'],'RootArchiveAuthority':None,'privateRootCreated':False}));return
    need(SHA(args.root_config_sha),'Explicit Root config SHA required');authority=raw(args.root_config,args.root_config_sha);config=reviewed_config(json.loads(authority),args.index_sha,plan_row['sha256'])
    primitive=module('private_pending_copy_primitives',HERE/'copy_primitives.py');authority_source={'source':str(Path(args.root_config).resolve(strict=True)),'sha256':args.root_config_sha,'bytes':len(authority)};result,completion=perform(plan,config,authority,args.index_sha,index,primitive,authority_source=authority_source)
    print(json.dumps({'state':result['state'],'privateRoot':DESTINATION,'completion':completion,'accepted':False}))
if __name__=='__main__':main()
