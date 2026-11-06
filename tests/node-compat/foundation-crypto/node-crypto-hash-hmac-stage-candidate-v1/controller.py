"""Dormant genuine Hash/Hmac357 Source stage. No action on module import."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,stat,subprocess,sys
if not __debug__:raise RuntimeError('Stage assertions must remain enabled')
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v1'
SOURCE_FAMILY=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-integration-candidate-v1'
SOURCE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
MONITOR_SHA='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
DEST=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
WORK=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-freeze')
OUT=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-stage-external-root')
JOURNAL=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-stage.json')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
TIMEOUT=600


def safe(name):
    assert isinstance(name,str)and name and not name.startswith('/')and '\\'not in name and '\0'not in name
    assert all(p not in ('','.','..')for p in name.split('/'))and name.split('/')[0]!='.git'
    return name


def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and row['bytes']>=0
    assert isinstance(row['sha256'],str)and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    path=Path(row['path']);assert path.is_absolute()and str(path)==row['path']and '..'not in path.parts and '\\'not in row['path']and '\0'not in row['path']
    # Only the platform's declared /tmp alias is normalized for I/O. The
    # original descriptor strings and preparation manifests are never rewritten.
    if str(path).startswith('/tmp/'):
        assert Path('/tmp').is_symlink()and Path('/tmp').resolve()==Path('/private/tmp')
        path=Path('/private'+str(path))
    for p in (path,*path.parents):assert not p.is_symlink(),p
    before=path.stat();assert stat.S_ISREG(before.st_mode)and before.st_size==row['bytes']
    h=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    after=path.stat()
    assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert h.hexdigest()==row['sha256'];return path


def read(row):
    p=checked(row);assert row['bytes']<=32*1024*1024
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)


def descriptor(path):
    path=Path(path)
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    for p in (path,*path.parents):assert not p.is_symlink()
    assert stat.S_ISREG(path.stat().st_mode)
    h=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(row);return row


def family(row):
    value=read(row);root=Path(row['path']).parent;rows=[row];names=set()
    for item in value['files']:
        name=safe(item['path']);assert name not in names;names.add(name)
        d=dict(path=str(root/name),sha256=item['sha256'],bytes=item['bytes']);checked(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    assert actual==names|{'index.json'};return value,rows


def indexed_result(pair):
    _,rows=family(pair['index']);assert sum(r==pair['result']for r in rows[1:])==1
    return read(pair['result']),rows


def absent(path):
    path=Path(path)
    for p in (path,*path.parents):assert not p.is_symlink(),p
    assert not path.exists(),path


def fsync_directory(path):
    fd=os.open(str(path),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def durable(path,data):
    with Path(path).open('xb')as f:
        assert f.write(data)==len(data);f.flush();os.fchmod(f.fileno(),0o600);os.fsync(f.fileno())
    fsync_directory(Path(path).parent)
    return descriptor(path)


def progress(path,value):
    with Path(path).open('ab')as f:
        data=(json.dumps(value,separators=(',',':'))+'\n').encode();assert f.write(data)==len(data);f.flush();os.fsync(f.fileno())


def git_environment():
    # Only child Git execution overrides are removed. User home variables stay
    # unchanged; no global config or original repository setting is rewritten.
    env={k:v for k,v in os.environ.items()if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_CONFIG_COUNT='0',GIT_TERMINAL_PROMPT='0')
    return env


def command(argv,folder):
    assert not folder.exists();folder.mkdir(mode=0o700)
    record=dict(argv=argv,timeoutSeconds=120,returncode=None,timedOut=False)
    stdout=stderr=b''
    try:
        child=subprocess.run(argv,capture_output=True,timeout=120,env=git_environment())
        stdout,stderr=child.stdout,child.stderr;record['returncode']=child.returncode
    except subprocess.TimeoutExpired as error:
        stdout=error.stdout or b'';stderr=error.stderr or b'';record['timedOut']=True
    finally:
        record['stdout']=durable(folder/'stdout.log',stdout);record['stderr']=durable(folder/'stderr.log',stderr)
        record['terminal']=durable(folder/'terminal.json',(json.dumps({**record,'rawStreamsRetainedBeforeAssertions':True},indent=2)+'\n').encode())
    return record


def terminal_model(value,authority):
    assert value['authority']==authority and value['rawExitCode']==0
    assert value['parentOwnedGroupGone']is True and value['allObservedOwnedGroupsGone']is True
    for key in ['timeout','forcedCleanup']:assert value[key]is False
    for key in ['interruptedSignals','remainingObservedPids','signals','errors']:assert value[key]==[]
    assert value['stderr']['bytes']==0 and value['observedProcesses']and value['finalGroups']
    assert all(g['alive']is False for g in value['finalGroups'])


def copy_safe(name):
    safe(name)
    assert not any(p in ('.git','.cache','.cargo','.rustup','node_modules','target') for p in name.split('/'))
    return name


def merge_rows(rows):
    """Only identical bytes/origin/mode may share one destination, with all roles."""
    merged={}
    for row in rows:
        name=copy_safe(row['path']);assert row['targetMode']==0o600
        if name in merged:
            before=merged[name]
            assert all(before[k]==row[k]for k in ['original','sha256','bytes','sourceMode','targetMode'])
            before['roles']=sorted(set(before['roles']+row['roles']))
        else:merged[name]={**row,'roles':sorted(set(row['roles']))}
    return [merged[name]for name in sorted(merged)]


def source_peer_model(value):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'
    assert value['sourceIndexSha256']==SOURCE_SHA and value['sourceOnly']is value['sourceReviewPassed']is True
    for key in ['ownerActionsInvoked','hostActionsInvoked','nativeBuildActionsInvoked','cryptoOperationsInvoked','operationalAdmission']:assert value[key]is False
    assert (value['nativeSourceFiles'],value['retainedParentNativeFiles'],value['changedParentNativeFiles'],value['newNativeFiles'],value['externalEmbeddingSources'],value['selectedManifestCount'])==(357,353,2,2,3,12)
    assert value['initialVariant']=='normal-off'and value['hashHmacEnabledForInitialExperimentalBuild']is True and value['auditedBorrowEnabled']is False


def stage_peer_model(value,own):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256']==own['sha256']and value['integrationSourceIndexSha256']==SOURCE_SHA and value['genericMonitorSourceIndexSha256']==MONITOR_SHA
    assert value['sourceOnly']is value['sourceReviewPassed']is True
    for key in ['ownerActionsInvoked','hostActionsInvoked','sourceStageActionsInvoked','nativeBuildActionsInvoked','cryptoOperationsInvoked']:assert value[key]is False


def root_model(value,own,refs):
    assert value['schemaVersion']==1 and value['state']=='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_V1'
    assert value['phase']=='source-stage-only'and value['sourceStageAllowed']is True
    assert value['sourceIndex']==refs['integrationIndex']and value['sourceIndex']['sha256']==SOURCE_SHA
    assert value['stageControllerIndex']==own and value['stageControllerEntry']['path']==str(OWN/'controller.py')
    assert value['integrationSourceReview']==refs['actualIntegrationSourceReview']
    assert value['configuredSourceRoot']==str(DEST)and value['workRoot']==str(WORK)and value['freezeRoot']==str(FREEZE)
    assert value['externalOutputRoot']==str(OUT)and value['stageJournal']==str(JOURNAL)
    assert value['baselineRevision']==BASE and value['externalParentDeadlineSeconds']==TIMEOUT
    assert value['nativeSourceFiles']==357 and value['retainedParentNativeFiles']==353 and value['changedParentNativeFiles']==2 and value['newNativeFiles']==2
    assert value['externalEmbeddingSources']==3 and value['selectedManifestCount']==12 and value['initialVariant']=='normal-off'
    assert value['basePlanRows']==1584 and value['integrationFamilyRows']==58 and value['expectedSourceCopies']==1642 and value['expectedEmbeddingDataCopies']==3
    assert value['genericMonitorIndex']==refs['monitorIndex']and value['genericMonitorEntry']==refs['monitorEntry']
    for key in ['nativeBuildAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','keyOperationsAllowed','cryptoOperationsAllowed','guestAllowed','gcAllowed','borrowAllowed','timingAllowed','normalMutationAllowed','metadataProjectionAllowed','privateBackendEvidenceHookEnabled','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:assert value[key]is False
    for key in ['actualStageResult','actualStageReview','actualBuildResult','reviewedNativePins','runtimeAuthority']:assert value[key]is None


def expected_plan(native,tools,source_rows):
    assert len(native)==357 and len(tools)==1227 and len(source_rows)==58
    rows=[]
    for row in native+tools:
        origin=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
        rows.append(dict(path=row['path'],original=row['original'],sha256=row['sha256'],bytes=row['bytes'],sourceMode=stat.S_IMODE(origin.stat().st_mode),targetMode=0o600,roles=[row.get('role','GENUINE_DONOR_TOOL_DATA'),'EXACT_7C5A_STAGE_PLAN_ROW']))
    for row in source_rows:
        origin=checked(row);name=origin.relative_to(REPO).as_posix()
        rows.append(dict(path=name,original=row['path'],sha256=row['sha256'],bytes=row['bytes'],sourceMode=stat.S_IMODE(origin.stat().st_mode),targetMode=0o600,roles=['SEALED_7C5A_FAMILY_STAGED_DATA_ACTIVE_PRODUCER_REMAINS_ORIGINAL']))
    result=merge_rows(rows);assert len(result)==1642
    return result


def stat_identity(path):
    s=Path(path).stat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


def recheck(frame):
    for row in frame['captured']:
        p=checked(row);assert stat_identity(p)==frame['originalStats'][row['path']]
    for row in frame['familyIndices']:family(row)
    for row in frame['copies']+frame['embedding']:
        p=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
        assert stat.S_IMODE(p.stat().st_mode)==row['sourceMode']


def authorize(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
    config=read(config_row);assert config['schemaVersion']==1 and config['state']=='NODE_CRYPTO_HASH_HMAC357_STAGE_CONFIG_V1'
    root=read(config['rootAuthority']);own=root['stageControllerIndex'];assert own['path']==str(OWN/'index.json')
    _,own_rows=family(own);assert root['stageControllerEntry']in own_rows
    refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')));root_model(root,own,refs)
    assert config['sourceIndex']==refs['integrationIndex']and config['controllerIndex']==own
    inputs=read(next(r for r in own_rows if r['path']==str(OWN/'input-hashes.json')))
    captured=[config_row,config['rootAuthority'],*own_rows];indices=[own]
    assert len(inputs['files'])==refs['declaredCurrentInputRows']
    for row in inputs['files']:checked(row)
    captured+=inputs['files']
    for ix in inputs['families']:
        _,rows=family(ix);captured+=rows;indices.append(ix)
    _,source_rows=family(refs['integrationIndex']);assert len(source_rows)==58;captured+=source_rows;indices.append(refs['integrationIndex'])
    declared=read(next(r for r in source_rows if r['path']==str(SOURCE_FAMILY/'input-hashes.json')));assert len(declared['files'])==2622
    for row in declared['files']:checked(row)
    captured+=declared['files']
    for pair,model in [(root['integrationSourceReview'],source_peer_model),(root['stageControllerReview'],lambda value:stage_peer_model(value,own))]:
        value,rows=indexed_result(pair);model(value);captured+=rows;indices.append(pair['index'])
    _,monitor_rows=family(refs['monitorIndex']);assert refs['monitorEntry']in monitor_rows;captured+=monitor_rows;indices.append(refs['monitorIndex'])
    source_data=lambda name:read(next(r for r in source_rows if r['path']==str(SOURCE_FAMILY/name)))
    native=source_data('native-origins.json')['files'];tools=source_data('tool-origins.json')['files']
    plan=read(next(r for r in own_rows if r['path']==str(OWN/'stage-copy-plan.json')))
    assert plan['files']==expected_plan(native,tools,source_rows)
    embedding=source_data('embedding-origins.json')['files'];assert len(embedding)==3
    assert plan['embeddingData']==[dict(row,sourceMode=stat.S_IMODE(checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes'])).stat().st_mode),targetMode=0o600)for row in embedding]
    for row in plan['files']+plan['embeddingData']:captured.append(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
    for key in ['gitBinary','pythonExecutable']:checked(root[key]);captured.append(root[key]);assert checked(root[key]).stat().st_mode&0o111
    assert checked(root['pythonExecutable'])==Path(sys.executable).resolve()
    assert root['gitBinary']['path']==str(checked(root['gitBinary']))and Path(root['gitBinary']['path']).name=='git'
    unique={}
    for row in captured:
        assert row['path']not in unique or unique[row['path']]==row
        unique[row['path']]=row
    captured=list(unique.values());indices=list({r['path']:r for r in indices}.values())
    frame=dict(config=config,root=root,refs=refs,captured=captured,familyIndices=indices,copies=plan['files'],embedding=plan['embeddingData'])
    frame['originalStats']={row['path']:stat_identity(checked(row))for row in captured}
    recheck(frame);return frame


def git_objects(root):
    folder=Path(root)/'.git/objects';assert folder.is_dir()and not folder.is_symlink();rows=[]
    for p in sorted(folder.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            s=p.stat();d=descriptor(p);rows.append(dict(path=p.relative_to(folder).as_posix(),device=s.st_dev,inode=s.st_ino,bytes=s.st_size,mode=stat.S_IMODE(s.st_mode),links=s.st_nlink,sha256=d['sha256']))
    return rows


def parse_tree(raw):
    rows={}
    assert raw.endswith(b'\0')and len(raw)<=32*1024*1024
    for entry in raw.split(b'\0')[:-1]:
        info,path=entry.split(b'\t',1);mode,kind,oid=info.decode('ascii').split(' ');name=path.decode('utf-8');safe(name)
        assert name not in rows and len(oid)==40 and all(c in '0123456789abcdef'for c in oid)
        rows[name]=dict(mode=mode,kind=kind,object=oid)
    return rows


def git_blob_id(data):return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()


def baseline_preimage(path,name,tree,original_ids):
    """Only fresh-clone, Git-byte-identical baseline regular files may be replaced."""
    item=tree.get(name)
    if not path.exists():assert item is None;return None
    assert item is not None and item['kind']=='blob'and item['mode']in ['100644','100755']and not path.is_symlink()
    s=path.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and(s.st_dev,s.st_ino)not in original_ids
    data=path.read_bytes();assert git_blob_id(data)==item['object']
    return dict(path=name,gitTreeEntry=item,actual=descriptor(path),mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,ownedFreshCloneOnly=True)


def private_parents(root,path):
    assert path.is_relative_to(root)
    current=root
    for part in path.relative_to(root).parts:
        current/=part;assert not current.is_symlink()
        if not current.exists():current.mkdir(mode=0o700)
        assert current.is_dir();current.chmod(0o700)


def observe_partial(rows,root):
    result=[]
    for row in rows:
        p=root/row['path']
        if p.is_symlink():result.append(dict(path=row['path'],type='symlink-refused'));continue
        if p.is_file():
            s=p.stat();result.append(dict(path=row['path'],actual=descriptor(p),mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,matchesExpected=descriptor(p)['sha256']==row['sha256']))
    return result


def stage(frame):
    result=dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_STARTED',sourceIndexSha256=SOURCE_SHA,controllerIndex=frame['root']['stageControllerIndex'],rootAuthority=frame['config']['rootAuthority'],configuredSourceRoot=str(DEST),workRoot=str(WORK),freezeRoot=str(FREEZE),baselineRevision=BASE,commands=[],copiesCompleted=[],embeddingDataCompleted=[],baselineOverlayPreimages=[],nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,externalEmbeddingSources=3,selectedManifestCount=12,initialVariant='normal-off',activeProducerOriginal=frame['refs']['activeProducerOriginal'],activeHelperOriginal=frame['refs']['activeHelperOriginal'],stagedSourceFamilyRole='DATA_ONLY',nativeBuildExecuted=False,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,metadataProjected=False,operationalAdmission=False)
    commands=OUT/'stage-commands';progress_path=commands/'progress.jsonl';original_git=None
    try:
        for p in [DEST,WORK,FREEZE,JOURNAL]:absent(p)
        assert OUT.is_dir()and not OUT.is_symlink()and stat.S_IMODE(OUT.stat().st_mode)==0o700
        absent(commands);commands.mkdir(mode=0o700);durable(progress_path,b'');progress(progress_path,dict(event='authenticated-stage-start',sourceIndexSha256=SOURCE_SHA,plannedSourceCopies=1642,embeddingDataCopies=3))
        recheck(frame);result['originalProtection']=durable(commands/'original-protection.json',(json.dumps(frame['originalStats'],indent=2)+'\n').encode());assert shutil.disk_usage(DEST.parent).free>=2*1024**3
        original_git=git_objects(REPO);original_ids={(r['device'],r['inode'])for r in original_git}
        for row in frame['captured']:
            s=checked(row).stat();original_ids.add((s.st_dev,s.st_ino))
        DEST.mkdir(mode=0o700);git=frame['root']['gitBinary']['path']
        def run(argv):
            record=command(argv,commands/str(len(result['commands'])));result['commands'].append(record);progress(progress_path,dict(event='git-command-returned',index=len(result['commands'])-1,record=record));assert record['returncode']==0 and not record['timedOut'];return record
        run([git,'clone','--no-local','--no-checkout',str(REPO),str(DEST)])
        run([git,'-C',str(DEST),'checkout','--detach',BASE])
        assert (DEST/'.git/HEAD').read_text()==BASE+'\n';absent(DEST/'.git/objects/info/alternates');DEST.chmod(0o700)
        staged_git=git_objects(DEST);assert all(r['links']==1 for r in staged_git)and not original_ids&{(r['device'],r['inode'])for r in staged_git}
        tree_record=run([git,'-C',str(DEST),'ls-tree','-r','-z','--full-tree',BASE]);tree=parse_tree(checked(tree_record['stdout']).read_bytes())
        doclinks={name:item for name,item in tree.items()if item['mode']=='120000'};assert set(doclinks)==set(frame['refs']['documentationLinks'])
        result['baselineDocumentationLinks']=[]
        for name,item in sorted(doclinks.items()):
            assert name.startswith('docs/')and not any(row['path']==name or row['path'].startswith(name+'/')for row in frame['copies'])
            record=run([git,'-C',str(DEST),'cat-file','blob',item['object']]);data=checked(record['stdout']).read_bytes();assert git_blob_id(data)==item['object']and data==frame['refs']['documentationLinks'][name].encode()
            p=DEST/name;assert p.is_symlink()and os.readlink(p).encode()==data
            result['baselineDocumentationLinks'].append(dict(path=name,gitObject=item['object'],linkText=data.decode(),gitBlobRaw=record['stdout'],consumedBySourceOrTools=False))
        for row in frame['copies']:
            source=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']));assert stat.S_IMODE(source.stat().st_mode)==row['sourceMode']
            target=DEST/copy_safe(row['path']);private_parents(DEST,target.parent)
            preimage=baseline_preimage(target,row['path'],tree,original_ids)
            if preimage is not None:
                result['baselineOverlayPreimages'].append(preimage);progress(progress_path,dict(event='authorized-baseline-preimage',preimage=preimage));target.unlink()
            absent(target);data=source.read_bytes();assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256']
            durable(target,data);actual=checked(dict(path=str(target),sha256=row['sha256'],bytes=row['bytes']));s=actual.stat()
            assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and(s.st_dev,s.st_ino)not in original_ids
            result['copiesCompleted'].append(row);progress(progress_path,dict(event='source-copy-verified',count=len(result['copiesCompleted']),path=row['path']))
        embedding_root=OUT/'embedding-reference';absent(embedding_root);embedding_root.mkdir(mode=0o700)
        for row in frame['embedding']:
            source=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']));target=embedding_root/safe(row['path']);private_parents(embedding_root,target.parent);absent(target)
            actual=durable(target,source.read_bytes());assert actual['sha256']==row['sha256']and actual['bytes']==row['bytes']
            s=target.stat();assert s.st_nlink==1 and(s.st_dev,s.st_ino)not in original_ids and stat.S_IMODE(s.st_mode)==0o600
            result['embeddingDataCompleted'].append(dict(source=row,target=actual,role='REFERENCE_DATA_NOT_CONFIGURED_EXTERNAL_BUILD_SOURCE'))
        target_ids=[]
        for row in frame['copies']:
            p=checked(dict(path=str(DEST/row['path']),sha256=row['sha256'],bytes=row['bytes']));s=p.stat();assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600;target_ids.append((s.st_dev,s.st_ino))
        for row in result['embeddingDataCompleted']:
            s=checked(row['target']).stat();target_ids.append((s.st_dev,s.st_ino))
        assert len(target_ids)==len(set(target_ids))==1645 and not set(target_ids)&original_ids
        actual_links={str(p.relative_to(DEST)):os.readlink(p)for p in DEST.rglob('*')if p.is_symlink()};assert actual_links==frame['refs']['documentationLinks']
        assert git_objects(REPO)==original_git;recheck(frame);absent(WORK);absent(FREEZE)
        for p in sorted({DEST,*[(DEST/r['path']).parent for r in frame['copies']]},key=lambda p:len(p.parts),reverse=True):fsync_directory(p)
        result.update(state='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGED_NOT_BUILT',copies=frame['copies'],copiedSourceFiles=1642,copiedEmbeddingDataFiles=3,allCopiedHashesModesAndDistinctInodesVerified=True,detachedHead=BASE,gitObjectInodesDisjoint=True,sourceOriginalInputsRechecked=True,originalGitObjectHashesAndIdentityUnchanged=True)
    except BaseException as error:
        result.update(state='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_FAILED_OR_PARTIAL_RETAINED',errorType=type(error).__name__)
        try:result['partialEmbeddingData']=observe_partial(frame['embedding'],OUT/'embedding-reference')
        except BaseException as partial:result['partialEmbeddingObservationError']=type(partial).__name__
        try:result['partialTargets']=observe_partial(frame['copies'],DEST)
        except BaseException as partial:result['partialObservationError']=type(partial).__name__
        try:recheck(frame);result['failureInputRecheckPassed']=True
        except BaseException as check:result['failureInputRecheckPassed']=False;result['failureInputRecheckError']=type(check).__name__
        raise
    finally:
        final_failure=None
        try:recheck(frame);result['finalInputProtectionPassed']=True
        except BaseException as error:result['finalInputProtectionPassed']=False;result['finalInputProtectionError']=type(error).__name__;final_failure=error
        if progress_path.exists():result['progress']=descriptor(progress_path)
        if original_git is not None:
            try:result['finalOriginalGitProtectionPassed']=git_objects(REPO)==original_git
            except BaseException as error:result['finalOriginalGitProtectionPassed']=False;result['finalOriginalGitProtectionError']=type(error).__name__;final_failure=error
            if result.get('finalOriginalGitProtectionPassed')is not True:final_failure=final_failure or RuntimeError('Original Git protection failed')
        if final_failure is not None:result['state']='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_FAILED_OR_PARTIAL_RETAINED'
        durable(JOURNAL,(json.dumps(result,indent=2)+'\n').encode());print(json.dumps(dict(journal=descriptor(JOURNAL),state=result['state'],copiedSourceFiles=len(result['copiesCompleted']),copiedEmbeddingDataFiles=len(result['embeddingDataCompleted']))),flush=True)
        if final_failure is not None:raise final_failure


def journal_model(value,frame):
    assert value['schemaVersion']==1 and value['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGED_NOT_BUILT'and value['sourceIndexSha256']==SOURCE_SHA
    assert value['copies']==value['copiesCompleted']==frame['copies']and value['copiedSourceFiles']==1642 and value['copiedEmbeddingDataFiles']==len(value['embeddingDataCompleted'])==3
    assert value['rootAuthority']==frame['config']['rootAuthority']and value['controllerIndex']==frame['root']['stageControllerIndex']
    for key in ['configuredSourceRoot','workRoot','freezeRoot']:assert value[key]==frame['root'][key]
    assert value['baselineRevision']==value['detachedHead']==BASE
    assert(value['nativeSourceFiles'],value['retainedParentNativeFiles'],value['changedParentNativeFiles'],value['newNativeFiles'],value['externalEmbeddingSources'],value['selectedManifestCount'])==(357,353,2,2,3,12)
    assert value['initialVariant']=='normal-off'and value['activeProducerOriginal']==frame['refs']['activeProducerOriginal']and value['activeHelperOriginal']==frame['refs']['activeHelperOriginal']and value['stagedSourceFamilyRole']=='DATA_ONLY'
    for key in ['nativeBuildExecuted','engineExecuted','guestExecuted','cryptoOperationsInvoked','metadataProjected','operationalAdmission']:assert value[key]is False
    for key in ['allCopiedHashesModesAndDistinctInodesVerified','gitObjectInodesDisjoint','sourceOriginalInputsRechecked','originalGitObjectHashesAndIdentityUnchanged','finalOriginalGitProtectionPassed','finalInputProtectionPassed']:assert value[key]is True
    assert all(r['returncode']==0 and r['timedOut']is False and r['timeoutSeconds']==120 for r in value['commands'])
    git=frame['root']['gitBinary']['path'];expected=[[git,'clone','--no-local','--no-checkout',str(REPO),str(DEST)],[git,'-C',str(DEST),'checkout','--detach',BASE],[git,'-C',str(DEST),'ls-tree','-r','-z','--full-tree',BASE]]
    expected += [[git,'-C',str(DEST),'cat-file','blob',r['gitObject']]for r in value['baselineDocumentationLinks']]
    assert [r['argv']for r in value['commands']]==expected and len(expected)==6


def main(config_row,worker=False):
    frame=authorize(config_row)
    if worker:stage(frame);return
    try:
        for p in [DEST,WORK,FREEZE,OUT,JOURNAL]:absent(p)
        spec=importlib.util.spec_from_file_location('genuine0af_hash_hmac_stage_monitor',checked(frame['root']['genericMonitorEntry']));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);recheck(frame)
        OUT.mkdir(mode=0o700);argv=[str(checked(frame['root']['pythonExecutable'])),'-B','-I',str(OWN/'controller.py'),'--stage-worker',json.dumps(config_row,separators=(',',':'))]
        terminal=module.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['config']['rootAuthority'])
        terminal_model(terminal,frame['config']['rootAuthority']);journal=descriptor(JOURNAL);value=read(journal);journal_model(value,frame)
        worker_stdout=checked(terminal['stdout']).read_bytes();assert json.loads(worker_stdout)==dict(journal=journal,state=value['state'],copiedSourceFiles=1642,copiedEmbeddingDataFiles=3)
        assert read(value['originalProtection'])=={path:list(values)for path,values in frame['originalStats'].items()}
        for record in value['commands']:
            for key in ['stdout','stderr','terminal']:checked(record[key])
            assert read(record['terminal'])=={**{k:v for k,v in record.items()if k!='terminal'},'rawStreamsRetainedBeforeAssertions':True}
        checked(value['progress'])
        for row in frame['copies']:
            p=checked(dict(path=str(DEST/row['path']),sha256=row['sha256'],bytes=row['bytes']));s=p.stat();assert stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
            original=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes'])).stat();assert(s.st_dev,s.st_ino)!=(original.st_dev,original.st_ino)
        for row in value['embeddingDataCompleted']:
            target=checked(row['target']);source=row['source'];origin=checked(dict(path=source['original'],sha256=source['sha256'],bytes=source['bytes']));a=target.stat();b=origin.stat()
            assert a.st_nlink==1 and stat.S_IMODE(a.st_mode)==0o600 and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
            assert row['target']['sha256']==source['sha256']and row['target']['bytes']==source['bytes']
        recheck(frame);absent(WORK);absent(FREEZE)
        print(json.dumps(dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1',sourceIndexSha256=SOURCE_SHA,actualStageResult=journal,externalTerminal=descriptor(OUT/'terminal.json'),copiedSourceFiles=1642,copiedEmbeddingDataFiles=3,nativeSourceFiles=357,independentResultReviewRequired=True,nativeBuildExecuted=False,engineExecuted=False,operationalAdmission=False)),flush=True)
    finally:recheck(frame)


if __name__=='__main__':
    assert len(sys.argv)in[2,3]
    if len(sys.argv)==3:assert sys.argv[1]=='--stage-worker';main(json.loads(sys.argv[2]),True)
    else:main(json.loads(sys.argv[1]))
