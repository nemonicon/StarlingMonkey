"""UNSEALED DATA-reader preparation; no actual Root result is bound yet.
This file has no publication main and invokes no Source adapter/admission/archive
reader, monitor, compiler, Git, engine or crypto operation.
"""
from pathlib import Path
import hashlib
import json
import os
import stat

SOURCE_INDEX_SHA256 = '559d600d9bedec4e319a415bcd30b984f445cfed7df2322dee25a86cba253172'
ACTUAL_ROOT_RESULT = {'path':'/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-v2-root-results.json','sha256':'f7a73f20118d53f007fec13f16e9cbd7d781ada3f499d9e35d8f30901cf89bee','bytes':3729}
ACTUAL_TERMINAL = {'path':'/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-artifact-revalidation-v2-external-root/terminal.json','sha256':'a2b800efb74046f4e7dcb598b62f7c0332c276228cf09445f7b1dcdbbb8989e3','bytes':1563}
SELECTED_TMP_DESCRIPTORS = {
 '/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/classic-streams-admission.mjs',
 '/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/zlib-admission.mjs',
}

def descriptor(path):
    p = Path(path)
    if str(p).startswith('/tmp/'):
        assert str(p) in SELECTED_TMP_DESCRIPTORS
        assert Path('/tmp').is_symlink() and os.readlink('/tmp') == 'private/tmp'
        assert str(Path('/tmp').resolve(strict=True)) == '/private/tmp'
        physical = Path('/private' + str(p))
    else:
        physical = p
    assert p.is_absolute() and '..' not in p.parts and str(p) == str(path)
    assert not any(q.is_symlink() for q in (physical, *physical.parents))
    before = physical.stat()
    assert stat.S_ISREG(before.st_mode)
    h = hashlib.sha256()
    with physical.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4194304), b''):
            h.update(chunk)
    after = physical.stat()
    attrs = lambda s: (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert attrs(before) == attrs(after)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=before.st_size)

def verified(row):
    assert set(row) == {'path','sha256','bytes'}
    assert type(row['bytes']) is int and row['bytes'] >= 0
    assert descriptor(row['path']) == row
    return Path(row['path'])

def parse_json(raw):
    def pairs(items):
        out = {}
        for k,v in items:
            assert k not in out
            out[k] = v
        return out
    def invalid(value):
        raise AssertionError('Nonfinite JSON constant: ' + value)
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)

def read(row):
    assert row['bytes'] <= 32 * 1024 * 1024
    return parse_json(verified(row).read_bytes())

def exact_family(row):
    root = verified(row).parent
    data = read(row)
    names = {'index.json'}
    for item in data['files']:
        name = item['path']
        assert name and not name.startswith('/') and '\\' not in name
        assert all(x not in ('','.','..') for x in name.split('/'))
        assert name not in names
        names.add(name)
        verified(dict(item,path=str(root/name)))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert names == {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    return data

def exact_trees(trees):
    for tree in trees:
        base = Path(tree['root'])
        assert base.is_dir() and not base.is_symlink()
        entries = []
        for parent,dirs,files in os.walk(base,followlinks=False):
            for name in dirs + files:
                p = Path(parent)/name
                kind = 'symlink' if p.is_symlink() else 'directory' if p.is_dir() else 'file'
                entries.append(dict(path=p.relative_to(base).as_posix(),kind=kind,mode=stat.S_IMODE(p.lstat().st_mode)))
        assert sorted(entries,key=lambda x:x['path']) == tree['entries']

def whole_saved_payload(result, raw_stdout, admission_bytes, raw_metadata, metadata_descriptor):
    frames = [parse_json(line) for line in raw_stdout.splitlines()]
    assert frames == [result]  # Source child prints exactly its complete result.
    assert parse_json(admission_bytes) == result['producerAdmission']
    assert len(parse_json(raw_metadata)) == 83
    assert len(raw_metadata) == metadata_descriptor['bytes']
    assert hashlib.sha256(raw_metadata).hexdigest() == metadata_descriptor['sha256']
    assert result['argumentContextKind'] == 'NEW_READ_ONLY_ARGUMENT_CONTEXT_ORIGINAL_P3_OWNER_V1'
    assert result['originalBootstrapFrameClaimed'] is False
    assert (result['originalRecipeExitCode'],result['originalParentExitCodes']) == (0,[1,1])
    assert result['originalBuildPreservationPassed'] is result['originalBuildAccepted'] is False
    assert result['rawMetadataFields'] == 83 and result['nativeSourceFiles'] == 357
    assert result['externalEmbeddingSources'] == 3 and result['selectedWholeManifests'] == 12
    assert result['producerAdmission']['state'] == 'NODE_CRYPTO_HASH_HMAC357_SOURCE_ADMISSION_DATA_PASSED_V3'
    assert result['currentInputBookendsPassed'] is True
    for key in ['engineExecuted','guestExecuted','cryptoOperationsInvoked','freezeInvoked',
                'operationalAdmission','runtimeAcceptanceClaim','originalResultRewritten',
                'grantsAnyActionAuthority']:
        assert result[key] is False

def require_actual_handoff():
    assert ACTUAL_ROOT_RESULT is not None and ACTUAL_TERMINAL is not None, (
        'Await Root original terminal0 and exact final Root/result descriptors. '
        'No acceptance or publication may be inferred from output existence.')


def decode_index(index, tree):
    import struct
    assert index[:4]==b'DIRC' and struct.unpack('>II',index[4:12])==(2,742)
    assert hashlib.sha1(index[:-20]).digest()==index[-20:]
    assert tree.endswith(b'\0')
    baseline={}
    for record in tree.split(b'\0')[:-1]:
        head,name=record.split(b'\t',1);mode,kind,oid=head.decode().split()
        assert kind=='blob' and name not in baseline
        baseline[name]=(int(mode,8),oid,0)
    pos=12;actual={};names=[]
    for unused in range(742):
        begin=pos;mode=struct.unpack('>I',index[pos+24:pos+28])[0]
        oid=index[pos+40:pos+60].hex();flags=struct.unpack('>H',index[pos+60:pos+62])[0]
        pos+=62;end=index.index(b'\0',pos,len(index)-20);name=index[pos:end]
        assert flags & 0xf000==0 and flags & 0xfff==min(len(name),4095)
        pos=end+1
        while (pos-begin)%8:assert index[pos]==0;pos+=1
        assert name not in actual and not name.startswith(b'/') and b'..' not in name.split(b'/')
        actual[name]=(mode,oid,0);names.append(name)
    assert actual==baseline and names==sorted(names)
    extensions=[]
    while pos<len(index)-20:
        sig=index[pos:pos+4];size=struct.unpack('>I',index[pos+4:pos+8])[0];pos+=8
        assert len(sig)==4 and 65<=sig[0]<=90 and pos+size<=len(index)-20
        extensions.append(dict(signature=sig.decode(),bytes=size,sha256=hashlib.sha256(index[pos:pos+size]).hexdigest()));pos+=size
    assert pos==len(index)-20
    return dict(schemaVersion=1,indexVersion=2,entries=742,pathModeOidStageEqualBaseline=True,
        extensions=extensions,originalIndexPreimageRetained=False,indexStatOnlyDeltaProved=False,exactIndexWriterProved=False)

def main():
    import ast
    import copy
    here=Path(__file__).resolve().parent
    k=here.parent
    source=k/'node-crypto-hash-hmac-artifact-revalidation-candidate-v2'
    require_actual_handoff()
    root=read(ACTUAL_ROOT_RESULT);terminal=read(ACTUAL_TERMINAL)
    assert root['state']=='ROOT_OBSERVED_READ_ONLY_ARTIFACT_REVALIDATION_COMPLETE_V2'
    assert root['ownedTerminal']==ACTUAL_TERMINAL
    assert root['adapterSourceIndex']['sha256']==SOURCE_INDEX_SHA256
    exact_family(root['adapterSourceIndex']);exact_family(root['sourceReviewIndex'])
    refs=read(descriptor(source/'references.json'))
    future=read(descriptor(source/'future-artifact-review-contract.json'))
    authority=read(root['rootAuthority']);config=read(root['rootConfig']);invocation=read(root['invocation'])
    assert invocation['rootAuthority']==root['rootAuthority']==config['rootAuthority']
    assert invocation['rootConfig']==root['rootConfig']
    assert authority['adapterIndex']==config['adapterIndex']==root['adapterSourceIndex']==invocation['sourceIndex']
    assert authority['state']=='ROOT_REVIEWED_HASH_HMAC357_READ_ONLY_ARTIFACT_REVALIDATION_V2'
    assert authority['sourceReview']['index']==root['sourceReviewIndex']==invocation['sourceReviewIndex']
    peer=read(authority['sourceReview']['result'])
    assert peer['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_ARTIFACT_REVALIDATION_SOURCE_REVIEW_PASSED_V2'
    assert peer['sourceIndexSha256']==SOURCE_INDEX_SHA256 and peer['sourceOnly'] is peer['sourceReviewPassed'] is True
    assert authority['readOnlySourceAdmissionAllowed'] is authority['ownedEvidencePublicationAllowed'] is True
    for key in ['nativeBuildAllowed','recipeAllowed','compilerAllowed','ninjaAllowed','gitAllowed','engineExecutionAllowed','guestAllowed','cryptoAllowed','componentAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','gcAllowed','oomAllowed','debugAllowed','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim']:
        assert authority[key] is False
    assert authority['actualRevalidationResult'] is authority['actualIndependentArtifactReview'] is authority['futureFreezeAuthority'] is None
    assert authority['tmpAliasPolicy']==refs['tmpAliasPolicy']==future['tmpAliasPolicy']==peer['tmpAliasPolicy']
    assert authority['deadlineSeconds']==invocation['deadlineSeconds']==600
    for key in ['launcher','python','monitorEntry']:
        verified(invocation[key])
    exact_family(invocation['monitorIndex'])
    assert invocation['monitorEntry']==refs['monitorEntry'] and invocation['monitorIndex']==refs['monitorIndex']
    assert invocation['actualArgv'][:4]==[refs['python']['path'],'-B','-I',refs['entry']['path']]
    assert len(invocation['actualArgv'])==5 and parse_json(invocation['actualArgv'][4])==root['rootConfig']
    verified(refs['entry'])
    assert terminal['rawExitCode']==root['rawParentExitCode']==0
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is root['allOwnedGroupsGone'] is True
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    for key in ['signals','errors','interruptedSignals','remainingObservedPids']:assert terminal[key]==[]
    assert terminal['authority']==root['rootAuthority']
    external=Path(refs['externalOutputRoot']);payload=Path(refs['outputRoot'])
    assert set(p.name for p in payload.iterdir())=={'result.json','raw-metadata.json','producer-admission-return.json','distribution-data.json','current-input-hashes.json','reference-aliases.json'}
    assert set(p.name for p in external.iterdir())=={'started.json','owned-0000.json','stdout.log','stderr.log','terminal.json'}
    started=read(descriptor(external/'started.json'));owned=read(descriptor(external/'owned-0000.json'))
    assert started['argv']==invocation['actualArgv'] and started['authority']==root['rootAuthority'] and started['timeoutSeconds']==600
    assert started['pid']==terminal['pid']==owned['process']['pid']==20222
    assert terminal['observedProcesses']==[owned['process']]
    assert terminal['finalGroups']==[dict(pgid=20222,alive=False,signalAllowed=False)]
    for directory in [payload,external]:
        assert stat.S_IMODE(directory.stat().st_mode)==0o700 and not directory.is_symlink()
        for f in directory.iterdir():assert f.is_file() and not f.is_symlink() and f.stat().st_nlink==1
    actual=read(root['actualRevalidationResult'])
    assert root['actualRevalidationResult']['sha256']=='e55c5de6f920427743bde7e7d5a5d0fbfb02e1dee840b28a992832d1728e6579'
    stdout=verified(terminal['stdout']).read_bytes();stderr=verified(terminal['stderr']).read_bytes();assert stderr==b''
    raw_metadata=(payload/'raw-metadata.json').read_bytes()
    whole_saved_payload(actual,stdout,(payload/'producer-admission-return.json').read_bytes(),raw_metadata,refs['metadata'])
    assert actual['adapterSourceIndex']==root['adapterSourceIndex'] and actual['rootAuthority']==root['rootAuthority']
    assert actual['state']=='NODE_CRYPTO_HASH_HMAC357_READ_ONLY_ARTIFACT_REVALIDATED_UNREVIEWED_V2'
    assert actual['indexException']==future['indexException']==refs['indexException']==authority['indexException']
    assert actual['failedReadOnlyRootObservation']==refs['failedReadOnlyRootObservation']==future['failedReadOnlyRootObservation']
    assert actual['originalFailureReview']==future['originalFailureReview']==root['originalFailureReview']
    assert actual['engine']==root['engine']==refs['engine']==future['engine']
    assert actual['metadata']==root['metadata']==refs['metadata']==future['metadata']
    meta=parse_json(raw_metadata);assert verified(refs['metadata']).read_bytes()==raw_metadata
    verified(refs['engine'])
    assert (meta['enginePath'],meta['engineSha256'],meta['engineBytes'])==(refs['engine']['path'],refs['engine']['sha256'],refs['engine']['bytes'])
    assert meta['nodeCryptoHashHmacEnabled'] is True and meta['nodeCryptoAuditedBorrowEnabled'] is False
    assert meta['gcStress'] is meta['oomTesting'] is meta['debuggerEnabled'] is False and meta['entropyPolicy']=='off'
    assert meta['observedCMakeOptions']==meta['requestedCMakeOptions']
    assert len(meta['sourceManifest'])==357 and len({r['path'] for r in meta['sourceManifest']})==357
    assert len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==12
    product=read(refs['producerReferences']);policy=read(product['policy'])
    assert meta['sourceManifest']==policy['expectedNativeSourceManifest'] and meta['componentizeSourceManifest']==policy['expectedComponentizeSourceManifest']
    assert meta['selectedModuleManifests']==policy['selectedModuleManifests']
    configured=Path(refs['configuredSourceRoot']);external_root=Path(meta['combinedNativeSourcePolicy']['externalConfiguredSourceRoot'])
    for rows,base in [(meta['sourceManifest'],configured),(meta['componentizeSourceManifest'],external_root)]:
        for r in rows:
            d=descriptor(base/r['path']);assert d['sha256']==r['sha256']
    selected=[]
    for r in meta['selectedModuleManifests']:
        d=descriptor(configured/r['path']);assert d['sha256']==r['sha256']
        value=read(d);assert value['profileVersion']==r['profileVersion'];selected.append(value)
    admit=actual['producerAdmission']
    assert admit['selectedManifests']==selected
    assert admit['controllerSourceIndexSha256']==refs['producerControllerIndex']['sha256']
    assert admit['sourceIndexSha256']==refs['integrationSourceIndex']['sha256']
    assert admit['genuineLayerRoot']==str(Path(product['helper']['path']).parent)
    assert admit['configuredSourceRoot']==refs['configuredSourceRoot'] and admit['metadata']==refs['metadata']
    for key,expected in [('nativeSourceFiles',357),('externalEmbeddingSources',3),('selectedManifestCount',12),('rawMetadataFields',83),('compileDatabaseRows',69),('policyCpp',63),('strictCpp',4),('privateCpp',7),('separateEmbeddingCpp',1)]:
        assert admit[key]==expected
    db=read(descriptor(meta['compileCommandsPath']));assert len(db)==69
    assert descriptor(meta['compileCommandsPath'])['sha256']==meta['compileCommandsSha256']
    assert descriptor(meta['cmakeCachePath'])['sha256']==meta['cmakeCacheSha256']
    hash_policy=meta['nodeCryptoHashHmacPolicy']
    private_commands=hash_policy['actualPrivateHashHmacMacroCompileCommands']
    assert len(private_commands)==7 and len(hash_policy['actualKernelCompileCommands'])==1 and len(hash_policy['actualRegistrationCompileCommands'])==1
    for command in private_commands:
        assert '-DNODE_COMPAT_CRYPTO_HASH_HMAC=1' in command
        assert '-DNODE_CRYPTO_AUDITED_BORROW' not in command and '-DNDEBUG' in command and '-O3' in command
    # The separately compiled generic embedding is not a private crypto TU.
    # Preserve its real flags; do not invent propagation of the kernel macro.
    assert len(meta['actualEmbeddingCompileCommands'])==1
    for command in meta['actualEmbeddingCompileCommands']:
        for flag in ['--target=wasm32-wasi','-DNODE_COMPAT_ENTROPY_POLICY=1','-DNDEBUG','-O3','-fno-exceptions']:
            assert flag in command
        assert '-DNODE_CRYPTO_AUDITED_BORROW' not in command
    failure=read(refs['originalFailureReview']['result']);failure_contract=read(refs['originalFailureContract'])
    exact_family(refs['originalFailureReview']['index'])
    assert failure['state']==failure_contract['requiredReviewState']
    for group in ['requiredFixedValues','requiredExactDescriptors']:
        for key,value in failure_contract[group].items():assert failure[key]==value
    assert failure['coverage']==failure_contract['requiredCoverage']
    assert failure['phaseSucceeded'] is failure['buildAcceptanceClaim'] is failure['originalSourcePreservationPassed'] is False
    assert actual['originalBuildResult']==refs['originalBuildResult']
    verified(refs['originalBuildResult']);verified(refs['failedReadOnlyRootObservation'])
    failed_readonly=read(refs['failedReadOnlyRootObservation'])
    assert not Path(refs['failedReadOnlyOutputRoot']).exists() and not Path(refs['freezeRoot']).exists()
    original_payloads={q.name:descriptor(q) for q in payload.iterdir()}
    source_inputs=read(refs['baseSourceInputs'])
    additional=read(descriptor(source/'source-inputs.json'))
    family_rows={r['path']:r for r in source_inputs['families']+additional['families']+[root['adapterSourceIndex'],root['sourceReviewIndex'],refs['originalFailureReview']['index']]}
    for r in family_rows.values():exact_family(r)
    ledger=read(actual['inputHashes'])['files']
    assert len(ledger)==21451 and len({r['path'] for r in ledger})==len(ledger)
    assert ledger==sorted(ledger,key=lambda r:r['path'])
    identities={};total_bytes=0
    for n,r in enumerate(ledger,1):
        p=verified(r);s=p.stat();total_bytes+=s.st_size
        identities[r['path']]=(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        if n%5000==0:print(json.dumps(dict(stage='current-ledger',checked=n,total=len(ledger))),flush=True)
    tree_data=read(refs['baseArtifactTrees'])['trees'];assert len(tree_data)==11;exact_trees(tree_data)
    aliases=read(actual['referenceAliases']);assert len(aliases['symlinks'])==35
    for a in aliases['symlinks']:
        p=Path(a['path']);assert p.is_symlink() and os.readlink(p)==a['linkText'] and str(p.resolve(strict=True))==a['resolved']
    for a in aliases['archiveHardlinks']:
        p,q=Path(a['path']),Path(a['target']);x,y=p.stat(),q.stat()
        assert (x.st_dev,x.st_ino)==(y.st_dev,y.st_ino)==(a['device'],a['inode'])
    exception=refs['indexException'];index_path=verified(exception['currentActual'])
    assert stat.S_IMODE(index_path.stat().st_mode)==0o600
    semantics=decode_index(index_path.read_bytes(),verified(refs['baselineTreeTransport']).read_bytes())
    assert semantics==actual['currentIndexSemantics']
    distributions=read(descriptor(payload/'distribution-data.json'));assert distributions==actual['distributionAudit']
    assert len(distributions['distributions'])==7 and [r['entries'] for r in distributions['distributions']]==[10688,364,361,20,5,4,3]
    assert distributions['opensslSources']==4650 and distributions['wholeCurrentDistributionBytesAndMembershipVerified'] is True and distributions['toolsOrNativeCodeInvoked'] is False
    for distribution in distributions['distributions']:
        verified(distribution['archive']);assert distribution['wholeMembershipVerified'] is True
        root_path=Path(distribution['root']);names=set()
        for parent,dirs,files in os.walk(root_path,followlinks=False):
            for name in dirs+files:names.add((Path(parent)/name).relative_to(root_path).as_posix())
        assert len(names)==distribution['entries']
    assert aliases['archiveHardlinks']==distributions['archiveHardlinks']
    for a in distributions['referenceAliases']:assert a in aliases['symlinks']
    # Distribution correspondence is Source-coupled to the reviewed seven archive
    # readers; do not rerun those readers/admission/helper APIs. Current archives,
    # extracted-file hashes, complete eleven memberships/modes and aliases are
    # independently checked above against the retained shared ledger.
    copy_index=descriptor(k/'node-crypto-hash-hmac-artifact-revalidation-v2-root-evidence/index.json')
    assert copy_index['sha256']=='40c9d46cd178e948d106c62145136f45409c4af411421ef7f042d2d59e57667d'
    copied=exact_family(copy_index);assert len(copied['files'])==11
    for r in copied['files']:
        folder,name=r['path'].split('/',1);original=payload/name if folder=='payload' else external/name
        d=descriptor(original);assert (d['sha256'],d['bytes'])==(r['sha256'],r['bytes'])
    for r in ledger:
        verified(r);s=Path(r['path']).stat()
        assert identities[r['path']]==(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    exact_trees(tree_data)
    mutations=[]
    def reject(name, edit):
        v=copy.deepcopy(actual);edit(v)
        try:whole_saved_payload(v,(json.dumps(v)+'\n').encode(),(payload/'producer-admission-return.json').read_bytes(),raw_metadata,refs['metadata'])
        except (AssertionError,KeyError,TypeError):mutations.append(dict(name=name,refused=True));return
        raise AssertionError('Mutation accepted:'+name)
    for name,key,value in [('original parents relabeled','originalParentExitCodes',[0,0]),('old preservation repaired','originalBuildPreservationPassed',True),('old build accepted','originalBuildAccepted',True),('engine execution claimed','engineExecuted',True),('native count cast','nativeSourceFiles',355),('metadata count cast','rawMetadataFields',80),('manifest shortening','selectedWholeManifests',11),('fake bootstrap frame','originalBootstrapFrameClaimed',True)]:
        reject(name,lambda v,k=key,x=value:v.update({k:x}))
    audit=meta['openssl']['completeSourceAudit'];ssl_root=Path(audit['sourceDirectory'])
    ssl_rows=[dict(path=str(Path(d['path']).relative_to(ssl_root)),sha256=d['sha256']) for d in ledger if Path(d['path']).is_relative_to(ssl_root)]
    ssl_rows.sort(key=lambda d:d['path']);assert len(ssl_rows)==4650
    ssl_canonical=hashlib.sha256(json.dumps(ssl_rows,separators=(',',':')).encode()).hexdigest()
    assert ssl_canonical==audit['sourceManifestSha256']
    with Path(refs['engine']['path']).open('rb') as engine_stream:assert engine_stream.read(8)==b'\\0asm\\1\\0\\0\\0'
    result=dict(future['requiredFixedValues'],state=future['requiredReviewState'],sourceIndexSha256=SOURCE_INDEX_SHA256,
        adapterSourceIndex=root['adapterSourceIndex'],sourceReview=authority['sourceReview'],actualRevalidationResult=root['actualRevalidationResult'],rootObservation=ACTUAL_ROOT_RESULT,rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],ownedTerminal=ACTUAL_TERMINAL,
        engine=refs['engine'],metadata=refs['metadata'],inputHashes=actual['inputHashes'],referenceAliases=actual['referenceAliases'],originalFailureReview=refs['originalFailureReview'],
        originalFailureContract=refs['originalFailureContract'],originalFailureOutcomeRetained=True,failedReadOnlyRootObservation=refs['failedReadOnlyRootObservation'],indexException=exception,currentIndexSemantics=semantics,
        producerControllerIndex=refs['producerControllerIndex'],integrationSourceIndex=refs['integrationSourceIndex'],originalArgumentContextPreserved=True,originalBootstrapFrameClaimed=False,
        producerAdmissionReturn=descriptor(payload/'producer-admission-return.json'),rawMetadata=descriptor(payload/'raw-metadata.json'),distributionData=descriptor(payload/'distribution-data.json'),
        wholeProducerAdmissionEqualsSavedAndResult=True,wholeRawMetadataByteEqualOriginal=True,allTwelveWholeManifestsEqualActualFiles=True,completeNativeAndExternalSourceRows=360,compileDatabaseRows=69,policyCpp=63,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,
        allSixOriginalPayloads=original_payloads,rawStdout=terminal['stdout'],rawStderr=terminal['stderr'],started=descriptor(external/'started.json'),ownedObservation=descriptor(external/'owned-0000.json'),invocation=root['invocation'],
        sharedRetainedDataIndex=copy_index,sharedOriginalCurrentLedgerFiles=21451,independentlyHashedCurrentBytes=total_bytes,exactCurrentTrees=11,symlinkAliases=35,selectedTmpAliasDescriptors=2,archiveHardlinks=len(aliases['archiveHardlinks']),currentDeclaredFamilyCount=len(family_rows),
        distributionCounts=[r['entries'] for r in distributions['distributions']],opensslSources=4650,
        currentFileHashesAndIdentitiesBookendedByReviewer=True,currentTreeMembershipAndModesChecked=True,sourceCoupledArchiveCorrespondence=True,archiveVerifierOrAdmissionOrAdapterRerunByReviewer=False,
        pureRetainedDataMutations=mutations,reviewerEngineGuestCryptoCompilerGitExecuted=False,
        opensslCurrentCanonicalManifestSha256=ssl_canonical,opensslCurrentManifestRows=4650,opensslCurrentCanonicalManifestMatchesRaw83=True,engineCoreHeaderDecodedAsDataOnly=True,
        qualifications=['Distinct actual read-only artifact revalidation, not acceptance or repair of original BUILD4 wrappers/preservation.',
        'Full shared ledger/distributions/eleven tree current hashes and modes are independently read; reviewed Source archive-correspondence/readers are not re-executed.',
        'Whole P3 admission return and raw83 bytes are retained under original contexts; no old355 metadata or successful-BUILD frame projection.',
        'Current bfbb/0600 index742 matches baseline path/mode/OID/stage. Original index bytes/writer/stat-only delta remain unknown and original preservation stays false.',
        'Original Root54289 raw0 is tool observation; actual child20222 owned terminal0 and whole stdout are retained. No separate outer OS terminal is fabricated.',
        'Source-coupled actual-time rechecks plus independent current bookends do not reconstruct past unrecorded filesystem states.',
        'No engine/guest/crypto/compiler/Git/freeze/pin/bootstrap/component/runtime action or operational adoption follows.'])
    for key,value in future['requiredFixedValues'].items():assert result[key]==value
    for role in future['requiredDescriptorRoles']:assert role in result
    (here/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(state=result['state'],currentFiles=21451,bytes=total_bytes,trees=11,sourceFamilies=len(family_rows),wholeMetadataFields=83,rawReadOnlyExitCode=0,reviewerOwnerActions=False)),flush=True)

if __name__=='__main__':main()
