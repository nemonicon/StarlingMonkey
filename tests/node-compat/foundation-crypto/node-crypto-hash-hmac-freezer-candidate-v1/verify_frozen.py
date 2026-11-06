"""Frozen-only357/83 DATA verification. Opens no original producer/work paths.
The caller authenticates this active Source before import; every payload/model
read here is an explicit frozen physical role. No helper/API/engine is called.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,posixpath,re,shlex,stat,sys
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze')
NATIVE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
PRODUCER_SHA='2ebed6b8c0f9787c07ef00036e8b903f4a39cfa70f916da45e895743d097969c'

def checked(d):
    assert type(d)is dict and set(d)=={'path','sha256','bytes'}and type(d['bytes'])is int and d['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',d['sha256'])
    p=Path(d['path']);assert p.is_absolute()and str(p)==d['path']and p.is_relative_to(FREEZE)and '..'not in p.parts and '\\'not in d['path']and not d['path'].startswith('//')
    for q in(p,*p.parents):assert not q.is_symlink()
    a=p.stat();assert stat.S_ISREG(a.st_mode)and a.st_nlink==1 and stat.S_IMODE(a.st_mode)==0o600
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4194304),b''):h.update(b)
    z=p.stat();assert(a.st_dev,a.st_ino,a.st_mode,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    assert a.st_size==d['bytes']and h.hexdigest()==d['sha256'];return p

def read(d):assert d['bytes']<=32*1024**2;return json.loads(checked(d).read_bytes())

def fixed_contract(value,contract):
    assert value['schemaVersion']==1 and value['verifiedPassed']is True and value['state']==contract['requiredReviewState']
    for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
        for key,want in contract.get(group,{}).items():assert value[key]==want
    if 'requiredCoverage'in contract:assert value['coverage']==contract['requiredCoverage']

def lexical_link_archives(command,build):
    return [w if w.startswith('/')else posixpath.normpath(build+'/'+w)for w in command if w.endswith('.a')]

def verify_frozen(receipt_row,expected_source):
    assert __debug__ and sys.dont_write_bytecode and re.fullmatch('[a-f0-9]{64}',expected_source)
    assert receipt_row['path']==str(FREEZE/'normal-off-freeze-receipt.json');r=read(receipt_row)
    assert r['schemaVersion']==1 and r['state']=='HASH_HMAC357_NORMAL_OFF_REVALIDATED_FREEZE_COMPLETE_UNREVIEWED_V1'and r['variant']=='normal-off'
    assert r['freezerSourceIndex']['sha256']==expected_source and r['producerIndex']['sha256']==PRODUCER_SHA and r['integrationIndex']['sha256']==NATIVE_SHA
    for key,want in dict(rawMetadataFields=83,nativeSourceFiles=357,externalEmbeddingSources=3,stagedSourceAndToolFiles=1642,stagedEmbeddingReferences=3,selectedWholeManifests=12,compileDatabaseRows=69,policyCpp=63,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,historicalCurrentLedgerFiles=21451,referenceTrees=11,freshProducerAdmissionCalls=1,originalRecipeExitCode=0,originalParentExitCodes=[1,1]).items():assert r[key]==want
    for key in ['originalBuildPreservationPassed','originalBuildAccepted','originalNinjaCommandReexecuted','originalCompilerRawExitProofClaim','liveEvpSnapshotAdmission','engineExecuted','guestExecuted','cryptoOperationsInvoked','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted']:assert r[key]is False
    for key in ['fullCurrentReferenceClosureChecked','referencesNotAllPhysicallyCopied','rawMetadataUnchanged','rawMetadataOriginalPathsPreserved']:assert r[key]is True
    assert r['freezeRoot']==str(FREEZE)and r['sourceRoot']==str(FREEZE/'source')and r['componentizeSourceRoot']==str(FREEZE/'componentize-source')
    initial=FREEZE.stat();assert stat.S_IMODE(initial.st_mode)==0o700
    owner=r['rootOwnership'];assert(owner['device'],owner['inode'])==(initial.st_dev,initial.st_ino)and owner['mode']==0o700 and owner['exclusiveRootCreated']is owner['rootHandleNoFollow']is True
    copies={};ids=set()
    for item in r['copies']:
        d={k:item[k]for k in ['path','sha256','bytes']};p=checked(d);name=p.relative_to(FREEZE).as_posix();s=p.stat()
        assert name not in copies and name!='normal-off-freeze-receipt.json'and(s.st_dev,s.st_ino)not in ids
        copies[name]=item;ids.add((s.st_dev,s.st_ino))
    actual=set()
    for p in FREEZE.rglob('*'):
        s=p.lstat();assert not p.is_symlink()
        if stat.S_ISDIR(s.st_mode):assert stat.S_IMODE(s.st_mode)==0o700
        else:assert stat.S_ISREG(s.st_mode);actual.add(p.relative_to(FREEZE).as_posix())
    assert actual==set(copies)|{'normal-off-freeze-receipt.json'}
    rs=checked(receipt_row).stat();assert(rs.st_dev,rs.st_ino)not in ids
    def row(name):return{k:copies[name][k]for k in ['path','sha256','bytes']}
    def complete_family(prefix,original_index):
        ix=row(prefix+'/index.json');assert(ix['sha256'],ix['bytes'])==(original_index['sha256'],original_index['bytes'])
        v=read(ix);names={'index.json'}
        for d in v['files']:
            name=d['path'];assert name and not name.startswith('/')and all(x not in('','.','..')for x in name.split('/'))and '\\'not in name and name not in names;names.add(name)
            saved=row(prefix+'/'+name);assert(saved['sha256'],saved['bytes'])==(d['sha256'],d['bytes'])
        assert{n[len(prefix)+1:]for n in copies if n.startswith(prefix+'/')}==names
        return v
    own_index=complete_family('artifact-tools/source',r['freezerSourceIndex'])
    refs=read(row('artifact-tools/source/references.json'))
    assert r['artifactReview']==refs['artifactReview']and r['artifactContract']==refs['artifactContract']and r['producerIndex']==refs['producerIndex']
    artifact_index=complete_family('artifact-review',r['artifactReview']['index'])
    peer_index=complete_family('freezer-source-review',r['sourceReview']['index'])
    def original_role(d):
        choices=[name for name,item in copies.items()if item['original']==d]
        assert choices,'Missing frozen physical role for '+d['path'];return row(choices[0])
    proof=read(original_role(refs['artifactReview']['result']));contract=read(original_role(refs['artifactContract']));fixed_contract(proof,contract)
    assert proof['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_READ_ONLY_REVALIDATED_ARTIFACT_REVIEW_PASSED_V1'and proof['publicationVersion']==2
    assert proof['originalRecipeExitCode']==0 and proof['originalParentExitCodes']==[1,1]and proof['originalBuildPreservationPassed']is proof['originalBuildAccepted']is False
    assert proof['indexException']==r['indexException']and proof['engine']==refs['engine']and proof['metadata']==refs['metadata']
    old_result=read(row('original-failure-data/buildResult.json'));old_root=read(row('original-failure-data/rootObservation.json'));old_review=read(row('original-failure-data/reviewResult.json'));old_contract=read(row('original-failure-data/reviewContract.json'));fixed_contract(old_review,old_contract)
    assert old_result['rawChildExitCode']==0 and old_result['launcherExitCode']==1 and old_result['evidenceComplete']is False
    assert old_result.get('allSourceStageOriginalAndCacheInputsPreserved')is not True
    assert old_root['recipeRawExitCode']==0 and old_root['wrapperRawExitCode']==1 and old_root['wrapperSourcePreservationClaimPassed']is False
    assert old_review['recipeRawExitCode']==0 and old_review['externalParentExitCode']==old_review['outerParentExitCode']==1
    assert old_review['originalSourcePreservationPassed']is old_review['phaseSucceeded']is old_review['buildAcceptanceClaim']is False
    assert r['engine']['sha256']==proof['engine']['sha256']and r['metadata']['sha256']==proof['metadata']['sha256']
    assert checked(r['engine'])==FREEZE/'normal-off.engine.wasm'
    metadata=read(r['metadata']);assert len(metadata)==83 and metadata['enginePath']==proof['engine']['path']
    assert r['metadata']['sha256']==row('revalidation-data/rawMetadata.json')['sha256']==proof['rawMetadata']['sha256']
    def pure(name):
        d=row('artifact-tools/source/'+name);source=next(x for x in own_index['files']if x['path']==name);assert(d['sha256'],d['bytes'])==(source['sha256'],source['bytes'])
        s=importlib.util.spec_from_file_location('frozen_357_'+name.replace('.','_'),checked(d));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    policy=read(row('producer-source/policy.json'));producer=read(row('producer-source/references.json'))
    assert producer==read(original_role(refs['producerReferences'])) # same frozen role, not an original read
    model=pure('metadata_model.py');observed=model.validate_metadata(metadata,policy,producer['policy']['sha256'],producer['helper']['sha256'],producer['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
    assert observed==dict(state='FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=357,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
    for key,prefix,count in [('sourceManifest','source',357),('componentizeSourceManifest','componentize-source',3)]:
        assert len(metadata[key])==count
        for d in metadata[key]:assert row(prefix+'/'+d['path'])['sha256']==d['sha256']
    assert sum(n.startswith('source/')for n in copies)==1642 and sum(n.startswith('componentize-source/')for n in copies)==3 and sum(n.startswith('stage-embedding-reference/')for n in copies)==3
    selected=[]
    for d in metadata['selectedModuleManifests']:
        saved=row('source/'+d['path']);assert saved['sha256']==d['sha256'];value=read(saved);assert value['profileVersion']==d['profileVersion'];selected.append(value)
    hm=pure('hash_model.py');hm.validate_selected_manifests(metadata,policy,selected)
    def by_original_path(path):
        ds=[item['original']for item in copies.values()if item['original']is not None and item['original']['path']==path];assert ds;assert all(x==ds[0]for x in ds);return original_role(ds[0])
    database=read(by_original_path(metadata['compileCommandsPath']));assert len(database)==69
    hm.validate_hash_hmac_commands(database,metadata['actualEmbeddingCompileCommands'],Path(producer['configuredSourceRoot']),metadata,policy)
    # No Path.resolve/original file lookup: original command paths remain lexical
    # DATA; every .a argument maps to a verified frozen copy by original role.
    link=metadata['nodeCryptoHashHmacPolicy']['actualLinkEvidence'];archives=lexical_link_archives(link['linkArgv'],str(Path(metadata['cmakeCachePath']).parent))
    for path in archives:checked(by_original_path(path))
    ninja=metadata['nodeCryptoHashHmacPolicy']['actualNinjaCapture'];assert ninja['rawExitCode']==0 and ninja['timeout']is False
    ninja_text=checked(original_role(ninja['stdout'])).read_text();assert link['completeNinjaLine']in ninja_text.splitlines();checked(original_role(ninja['stderr']))
    segments=[];current=[]
    for token in shlex.split(link['completeNinjaLine']):
        if token=='&&':segments.append(current);current=[]
        else:current.append(token)
    segments.append(current);assert segments.count(link['linkArgv'])==1
    assert link['guestOpenSSLArchiveArguments']==[w for w in link['linkArgv']if Path(w).name=='libcrypto.a']and link['guestOpenSSLArchiveArguments']
    init=metadata['nodeCryptoHashHmacPolicy']['actualInstallationOrder'];install=checked(original_role(init['source'])).read_text();assert install.count(init['cryptoNamespace'])==install.count(init['nodeNamespace'])==1 and install.index(init['cryptoNamespace'])<install.index(init['nodeNamespace'])
    for d in [metadata['privateRustupBootstrapPolicy']['beforeInstallRecord'],metadata['privateRustupBootstrapPolicy']['settingsAtBuildCompletion']]:checked(original_role(d))
    # Full historical ledger/tree DATA is retained, but its original absolute
    # paths are NEVER opened by this frozen-only verifier.
    ledger=read(row('revalidation-data/inputHashes.json'));assert len(ledger['files'])==21451 and row('revalidation-data/inputHashes.json')['sha256']==proof['inputHashes']['sha256']
    tree_data=read(row('reference-closure/artifact-trees.json'));assert len(tree_data['trees'])==11
    additions=read(row('reference-closure/additions.json'));known={d['path']for d in ledger['files']}|{d['path']for d in additions['files']}
    for tree in tree_data['trees']:
        for item in tree['entries']:
            if item['kind']=='file':assert str(Path(tree['root'])/item['path'])in known
    actual_revalidation=read(row('revalidation-data/result.json'));historical_admit=read(row('revalidation-data/producerAdmission.json'));fresh_admit=read(r['freshProducerAdmission'])
    assert fresh_admit==historical_admit==actual_revalidation['producerAdmission']
    assert fresh_admit['controllerSourceIndexSha256']==PRODUCER_SHA and fresh_admit['sourceIndexSha256']==NATIVE_SHA and fresh_admit['metadata']==proof['metadata']
    plan=read(r['copyPlan']);assert plan['referencesNotAllPhysicallyCopied']is True
    for d in plan['copies']:
        saved=copies[d['destination']];assert saved['original']==d['source']and saved['role']==d['role']and(saved['sha256'],saved['bytes'])==(d['source']['sha256'],d['source']['bytes'])
    config=read(row('provenance/config.json'));authority=read(row('provenance/root-authority.json'));assert config['rootAuthority']==r['rootAuthority']and authority['freezerIndex']==r['freezerSourceIndex']and authority['artifactReview']==r['artifactReview']
    peer=read(original_role(r['sourceReview']['result']));peer_contract=read(original_role(authority['sourceReviewContract']));fixed_contract(peer,peer_contract)
    assert peer['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_FREEZER_SOURCE_REVIEW_PASSED_V1'and peer['freezerSourceIndexSha256']==expected_source
    control=read(r['control']);assert control['freshProducerAdmissionCalls']==1 and control['artifactReview']==r['artifactReview']and control['originalBuildAccepted']is False
    assert(FREEZE.stat().st_dev,FREEZE.stat().st_ino)==(initial.st_dev,initial.st_ino);checked(receipt_row)
    return dict(schemaVersion=1,state='HASH_HMAC357_FROZEN_ONLY_CAPSULE_VERIFIED_NOT_ADOPTED_V1',receipt=receipt_row,engine=r['engine'],metadata=r['metadata'],copies=len(copies),nativeSourceFiles=357,externalEmbeddingSources=3,selectedWholeManifests=12,rawMetadataFields=83,originalRecipeExitCode=0,originalParentExitCodes=[1,1],originalBuildPreservationPassed=False,originalBuildAccepted=False,originalProducerOrWorkPathsOpened=False,currentLiveReferenceReverificationPerformed=False,frozenCopyRolesVerified=True,referencesNotAllPhysicallyCopied=True,helperOrAdmissionReexecuted=False,independentActualFreezeReviewRequired=True,liveEvpSnapshotAdmission=False,engineExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False)

if __name__=='__main__':
    assert len(sys.argv)==3;print(json.dumps(verify_frozen(json.loads(sys.argv[2]),sys.argv[1])),flush=True)
