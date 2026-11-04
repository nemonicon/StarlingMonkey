"""Finite source/data plan construction. No copying, owners or runtime imports."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
ADOPTION=HERE.parent
CLASSIC=ADOPTION.parent
BASE=ADOPTION/'artifact-closure-plan-v1'
AMEND=ADOPTION/'artifact-closure-current-context-amendment-v1'
PLAN_INDEX='96b4536ddb54484d665d93d64b6bc1af794dda977c189f50222238bad73a716e'
AMEND_INDEX='371132b364486a7b69a1cf9c0aa447959c93d332b54e3e6b07687895880353cb'
AMEND_PEER='1c849e619725d1441ee0a716f5e5e71bfb956b25d3f5244b8ef7ea31f5f61c00'
DESTINATION='/tmp/starling-node-compat/classic-artifact-preservation-pending-v1'
LICENSE_SHA='21a82bbee91262a076c2e34533d51d73475d55e889f1c42cf884c86b2a0d5773'
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as source:
        for data in iter(lambda:source.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def descriptor(path):
    path=Path(path);assert path.is_file()and not path.is_symlink();return{'path':str(path),'sha256':digest(path),'bytes':path.stat().st_size}
def load(path,sha=None):
    path=Path(path);raw=path.read_bytes()
    if sha is not None:assert hashlib.sha256(raw).hexdigest()==sha
    return json.loads(raw)
def build():
    physical={};objects={};aliases={};links={};omissions=[];observations=[]
    def add(row,kind='text',role='supplement',asset=None):
        path=Path(row['path']);canonical=str(path.resolve(strict=True));info=path.lstat();assert path.is_file()and not path.is_symlink()
        assert info.st_size==row['bytes']and digest(path)==row['sha256'],str(path)
        if kind=='reference':target=None
        elif asset is not None:target='evidence/source/'+asset
        else:target=('external-wasm/objects/'if kind=='wasm'else'evidence/text/objects/')+row['sha256']+('.wasm'if kind=='wasm'else'.data')
        key=(canonical,row['sha256'],row['bytes']);value=physical.setdefault(key,{'source':canonical,'sha256':row['sha256'],'bytes':row['bytes'],'roles':[],'declaredPaths':[],'kind':kind,'destination':target})
        assert value['destination']==target or target is None or value['destination']is None
        if target is not None:
            previous=objects.setdefault(target,{'source':canonical,'destination':target,'sha256':row['sha256'],'bytes':row['bytes'],'kind':kind});assert(previous['sha256'],previous['bytes'])==(row['sha256'],row['bytes'])
        value['roles'].append(role)
        for declared in [row['path']]+row.get('declaredPaths',[]):
            if declared not in value['declaredPaths']:value['declaredPaths'].append(declared)
            if target is not None:aliases[(declared,row['sha256'],row['bytes'])]=target
        if target is not None:aliases[(canonical,row['sha256'],row['bytes'])]=target
        return target
    def packet(root,expected):
        index=load(root/'index.json',expected);add(descriptor(root/'index.json'),role='sealed-index')
        for row in index['files']:add({'path':str(root/row['path']),**{k:row[k]for k in['sha256','bytes']}},role='indexed-supplement')
    packet(BASE,PLAN_INDEX);packet(AMEND,AMEND_INDEX)
    packet(CLASSIC/'independent-artifact-closure-current-context-review-v1',AMEND_PEER)
    original=load(BASE/'needed-files.json');assert len(original['files'])==17885
    fresh=load(AMEND/'fresh-copy-plan.json');unavailable=fresh['unavailableInspectionOnlyRecords'];assert len(unavailable)==1
    unavailable=unavailable[0];assert unavailable['expectedSha256']=='24e4ac4e3edb505e7e1fd6acf342352f5088628f4b966856bf8cce16facfa5ab'and unavailable['bytes']==37053 and unavailable['oldBytesAvailable']is False
    whitelist=load(BASE/'source-binary-whitelist.json')['paths'];assert len(whitelist)==5
    original_map=[];protected=0
    for row in original['files']:
        if(row['path'],row['sha256'],row['bytes'])==(unavailable['originalPath'],unavailable['expectedSha256'],unavailable['bytes']):
            omissions.append(dict(unavailable));original_map.append({'descriptor':row,'storage':{'kind':'unavailable-inspection-only','archivePath':None}});continue
        protected+=1;classification=row['proposedPreservation'];asset=None
        if classification=='repository-native-source-binary-exception-five-paths-only':
            candidates=[name for name,sha in whitelist.items()if row['path'].endswith('/'+name)and sha==row['sha256']];assert len(candidates)==1;asset=candidates[0];kind='source-binary'
        else:kind={'repository-text-source-evidence-copy':'text','external-binary-preservation-required':'wasm','reference-only-host-sdk-or-dependency-binary':'reference'}[classification]
        target=add(row,kind,'protected-original',asset);storage={'kind':kind,'archivePath':target}
        if kind=='reference'and row['sha256']==LICENSE_SHA and row['bytes']==1076 and Path(row['path']).name=='LICENSE.node':
            raw=Path(row['path']).read_bytes();assert b'\0'not in raw;raw.decode('utf-8','strict')
            # Original classification/identity remains a reference. This exact
            # known text notice receives a separately described legal copy.
            target='evidence/text/objects/'+LICENSE_SHA+'.data';objects.setdefault(target,{'source':str(Path(row['path']).resolve()),'destination':target,'sha256':LICENSE_SHA,'bytes':1076,'kind':'explicit-utf8-node-mit-notice'})
            storage['additionalExactTextLicenseCopy']=target
            for path in [row['path']]+row.get('declaredPaths',[]):aliases[(path,row['sha256'],row['bytes'])]=target
        original_map.append({'descriptor':row,'storage':storage})
    assert protected==17884 and len(omissions)==1
    for row in original['links']:
        path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve(strict=True))==row['resolvedTarget'];links[row['path']]=dict(row)
    snapshots=load(AMEND/'mutable-status-snapshot.json','88fe4e4c63045f75034eb4b961a804173b84bca775d5bd9f9f7cd3fd4441f6f6')
    assert len(snapshots['files'])==7
    for row in snapshots['files']:
        target=add({'path':str(AMEND/row['snapshotPath']),'sha256':row['sha256'],'bytes':row['bytes']},role='separately-captured-status-snapshot');observations.append({**row,'archivePath':target,'historicalOldDescriptorReplacement':False})
    for packet_data in load(AMEND/'late-evidence.json')['packets']:
        for row in packet_data['files']:add(row,role='prior-late-evidence-exact')
    # Exact completed memory-v2 source/authority/raw evidence. The independent
    # result proof is intentionally NOT looked up or auto-selected here.
    packet(CLASSIC/'measurement-memory-probe-candidate-v2','6b0b82df31d13d530ce1541ccedcecb1fa99573f7671aa1b48b97c3bd682def0')
    packet(CLASSIC/'independent-memory-probe-v2-source-review-v1','73fa279b3d5c9b363330716f7bf77d7a0f9360a3144f23f5ecbbcc0fcfa6ca6e')
    memory=ADOPTION/'process-rss-supplement-v2-root-results.json';assert digest(memory)=='203b7e6b7b1bee8675bc52280c7b30fb8b8da82461e4e5b9167535862fd08be5';add(descriptor(memory),role='memory-v2-root-terminal')
    report=load(memory);assert report['rawExitCode']==0 and report['workerCount']==18 and report['retainedPublicReturns']==126
    for row in report['references']:add(row,role='memory-v2-explicit-root-reference')
    closure=report['outputClosure'];add(closure,role='memory-v2-output-closure');assert closure['sha256']=='db26f6492bf230dde6621d32c537faad5728f6f6da5253259ee098f2d7856d99'
    memory_outputs=load(closure['path'],closure['sha256']);assert len(memory_outputs['files'])==599 and memory_outputs['links']==[]
    for row in memory_outputs['files']:add(row,role='memory-v2-output-file')
    memory_peer=CLASSIC/'independent-process-rss-supplement-v2-results-review-v1'
    packet(memory_peer,'14611521cb3f44d5ec0cea7ef61eb8821d8fe7f8d8a53aab197209467bca2fe5')
    assert digest(memory_peer/'review-receipt.json')=='7895d46d6abeed308c3044d72398f7a7cab32ff790a1db68ef58fcb6fa302d7e'
    actual_memory_proof={'index':descriptor(memory_peer/'index.json'),'result':descriptor(memory_peer/'results.json')}
    # The failed v1 receipt is a separate negative observation, never a pass.
    failure=ADOPTION/'process-rss-supplement-v1-preworker-failure-root-results.json';assert digest(failure)=='e51149e1743030a8c2e13547575731ede0dfed0263c19d951db18aaa1db37ed1';add(descriptor(failure),role='failed-memory-v1')
    for row in load(failure)['references']+load(failure)['partialOutputFiles']:add(row,role='failed-memory-v1-raw-reference')
    contexts=[];reference_context_rows=[]
    def context(identity,manifest,selected=None):
        raw=Path(manifest['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==manifest['sha256'];document=json.loads(raw);rows=document['inputs'];manifest_target=add({'path':manifest['path'],'sha256':manifest['sha256'],'bytes':len(raw)},role='exact-context-manifest')
        grouped={}
        for position,row in enumerate(rows):
            if selected is not None and position not in selected:continue
            path=row['path'];key=(path,row['sha256'],row['bytes']);target=aliases.get(key)
            if target is None:
                canonical=str((Path(path)if Path(path).is_absolute()else Path(manifest['path']).parent/path).resolve())
                target=aliases.get((canonical,row['sha256'],row['bytes']))
            if target is None:
                reference=physical.get((canonical,row['sha256'],row['bytes']));assert reference is not None and reference['kind']=='reference','Unknown context descriptor, not an authorized reference'
                reference_context_rows.append({'contextId':identity,'manifestRow':position,'originalPath':path,'canonicalReferencePath':canonical,'sha256':row['sha256'],'bytes':row['bytes'],'mappedAsCopiedBytes':False});continue
            existing=grouped.setdefault(key,{'manifestRows':[],'originalPath':path,'expectedSha256':row['sha256'],'bytes':row['bytes'],'archivePath':target});existing['manifestRows'].append(position)
        assert grouped
        if selected is not None:assert {p for row in grouped.values()for p in row['manifestRows']}==selected
        contexts.append({'contextId':identity,'format':'input-freeze-v1','coverage':'selected-rows','manifest':{'originalPath':manifest['path'],'archivePath':manifest_target,'sha256':manifest['sha256'],'bytes':len(raw)},'rows':list(grouped.values())})
    critical=[row for row in original['inputManifestAndScopeSummaries']if row['kind']=='actual-critical-family-consumed-input'];assert len(critical)==8
    for index,row in enumerate(critical):context('classic-critical-'+str(index),row)
    zlib=load(AMEND/'current-context-migration-or-hold.json');assert len(zlib['zlibFrames'])==12
    for index,frame in enumerate(zlib['zlibFrames']):
        selected={r['row']for r in frame['directOldRootRows']};assert len(selected)==5;context('zlib-old-five-'+str(index),frame['manifest'],selected)
    assert len(contexts)==20
    typed_decisions=[{'role':frame['role'],'manifestSha256':frame['manifest']['sha256'],'decision':frame['decision'],'oldFamilyMayRemainRerunnableAfterPromotion':frame['oldFamilyMayRemainRerunnableAfterPromotion']}for frame in zlib['zlibFrames']]
    assert all(row['oldFamilyMayRemainRerunnableAfterPromotion']is False for row in typed_decisions)
    formal=ADOPTION/'root-source-context-rollforward-policy-v1.json';assert digest(formal)=='20a32c37de8fc1fe3bcbdecaa751377918d921f79ba6bcef91eb8943895eecc6';add(descriptor(formal),role='actual-root-context-policy-not-copy-approval')
    strategy=ADOPTION/'classic-implementation-strategy-root-decision-v2.json';assert digest(strategy)=='bac8c7c01f27460d8756389b1e024216381d20637bfa445310bf56d25e1ce4f4';add(descriptor(strategy),role='late-classic-strategy-decision-not-copy-approval')
    formal_value=load(formal);assert formal_value['acceptedTypedHoldDecisions']==typed_decisions
    expected_policy={'schemaVersion':1,'state':'ROOT_CLASSIC_SOURCE_CONTEXT_ROLLFORWARD_POLICY_V1','sourcePromotionAllowed':False,'archiveAcceptanceAllowed':False,'runtimeAcceptanceClaim':False,
      'preservationPlanIndexSha256':PLAN_INDEX,'contextAmendmentIndexSha256':AMEND_INDEX,'contextReviewIndexSha256':AMEND_PEER,'typedHoldMapSha256':digest(AMEND/'current-context-migration-or-hold.json'),
      'memoryRootReceiptSha256':'203b7e6b7b1bee8675bc52280c7b30fb8b8da82461e4e5b9167535862fd08be5','memoryIndependentProofIndexSha256':'14611521cb3f44d5ec0cea7ef61eb8821d8fe7f8d8a53aab197209467bca2fe5','memoryCompletedUnderOldContext':True,
      'unavailableReadmeSha256':'24e4ac4e3edb505e7e1fd6acf342352f5088628f4b966856bf8cce16facfa5ab','statusSnapshotManifestSha256':'88fe4e4c63045f75034eb4b961a804173b84bca775d5bd9f9f7cd3fd4441f6f6','historicalPreflightRerunAllowed':False,'futureFamiliesRequireNewContextReview':True,'acceptedTypedHoldDecisions':typed_decisions}
    for key,value in expected_policy.items():assert formal_value[key]==value
    return{'schemaVersion':1,'state':'PRIVATE_PENDING_PRESERVATION_COPY_PLAN_SOURCE_ONLY','privateDestination':DESTINATION,'protectedOriginalDescriptors':protected,'originalInventoryDescriptors':17885,'originalMap':original_map,
      'objects':sorted(objects.values(),key=lambda r:r['destination']),'originalInputs':sorted(physical.values(),key=lambda r:(r['source'],r['sha256'])),'links':list(links.values()),'omissions':omissions,'separateStatusSnapshots':observations,
      'contextMap':{'schemaVersion':1,'state':'EXPLICIT_ARCHIVE_CONTEXT_MAP_V1','contexts':contexts},'unmappedContextRows':reference_context_rows,'contextCoverage':'selected-rows only; SDK/host references are not copied-byte claims',
      'lateMemoryIndependentProof':actual_memory_proof,'lateProofRequiredAtExecution':True,'memoryReportSha256':'606346356502ed8824b54677f825cdccec2bc8d48a4e23c34558384e18b8367f','memoryRootReceiptSha256':'203b7e6b7b1bee8675bc52280c7b30fb8b8da82461e4e5b9167535862fd08be5',
      'migrationDecision':descriptor(formal),'expectedMigrationPolicyFields':expected_policy,'futureOwnerMigrationDecisionIssued':True,'fullZlib350OrConsumers355ArchivalClosureClaim':False,'acceptanceIssued':False,'sourcePromotionIssued':False}
