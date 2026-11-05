"""Dormant external caller; authenticate all DATA before original owned monitor import."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v3'
OUTPUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v3')
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v3-external-root')
def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and row['bytes']>=0
    assert isinstance(row['sha256'],str)and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    p=Path(row['path']);assert p.is_absolute()and '..'not in p.parts
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    for parent in (p,*p.parents):assert not parent.is_symlink(),parent
    before=p.stat();assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert before.st_size==row['bytes']and h.hexdigest()==row['sha256'];return p


def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(row);return row


def read(row):
    p=checked(row);assert row['bytes']<=32*1024*1024
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)


def family(row):
    value=read(row);root=Path(row['path']).parent;rows=[row];seen=set()
    for r in value['files']:
        name=r['path'];assert isinstance(name,str)and name and name not in seen and '\\'not in name and '\0'not in name
        assert not name.startswith('/')and all(p not in ('','.','..')for p in name.split('/'))
        seen.add(name);d=dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==seen|{'index.json'};return rows


def indexed_result(pair):
    rows=family(pair['index']);assert sum(r==pair['result']for r in rows[1:])==1
    return read(pair['result']),rows


def validate_terminal(value,authority):
    assert value['schemaVersion']==1 and value['authority']==authority and value['rawExitCode']==0
    assert value['parentOwnedGroupGone']is True and value['allObservedOwnedGroupsGone']is True
    for k in ['forcedCleanup','timeout']:assert value[k]is False
    for k in ['remainingObservedPids','signals','errors','interruptedSignals']:assert value[k]==[]
    assert value['observedProcesses']and value['finalGroups']and all(g['alive']is False for g in value['finalGroups'])
    return True


def write(path,value):
    with Path(path).open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())


def load_actual(row,name):
    spec=importlib.util.spec_from_file_location(name,checked(row));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def package_context(refs):
    m=read(refs['packagingMap']);root=Path(m['publicationRoot']);s=root.stat()
    assert m['state']=='EXACT_EXISTING_PACKAGING_PHYSICAL_ROLES_NOT_NATIVE_AUTHORITY'and m['originalZlibNativeFactsConsumed']is m['costActionStatesReused']is False
    assert not root.is_symlink()and stat.S_IMODE(s.st_mode)==0o700 and(s.st_dev,s.st_ino)==(m['rootIdentity']['device'],m['rootIdentity']['inode'])
    expected={r['path']:r for r in m['files']};links={r['destination']:r for r in m['links']};files=set();seenlinks=set()
    assert len(expected)==4934 and len(links)==22
    def walk(path):
        for p in path.iterdir():
            name=p.relative_to(root).as_posix();s=p.lstat()
            if p.is_symlink():
                r=links[name];assert os.readlink(p)==r['newLinkText']and p.resolve()==root/r['mappedTarget'];seenlinks.add(name)
            elif p.is_dir():assert stat.S_IMODE(s.st_mode)==0o700;walk(p)
            else:
                r=expected[name];assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'];checked(dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']));files.add(name)
    for prefix in m['roleRoots']:
        p=root/prefix;assert p.is_dir()and not p.is_symlink();walk(p)
    assert files==set(expected)and seenlinks==set(links)


def root_model(v,own,refs):
    assert v['schemaVersion']==1 and v['state']=='ROOT_REVIEWED_SECRET355_NORMAL_RUNTIME_V3'and v['phase']=='guarded-normal-runtime'
    assert v['sourceIndex']==own and own['path']==str(OWN/'index.json')and v['entry']['path']==str(OWN/'entry.mjs')and v['externalController']['path']==str(OWN/'external.py')
    for k in ['runtimeWorkloadAllowed','nodeOracleAllowed','retainedReadOnlyApiAllowed','guardedPrototypeCase3Allowed']:assert v[k]is True
    assert v['variant']=='normal-off'and v['nativeSourceFiles']==355 and v['externalEmbeddingSources']==3 and v['selectedManifestCount']==11 and v['fullMetadataFields']==75
    assert v['engineSha256']==refs['engine']['sha256']and v['componentSha256']==refs['artifacts']['component']['sha256']
    assert v['actualArtifactReview']==refs['actualArtifactReview']and v['actualArtifactContract']==refs['actualArtifactContract']and v['componentSourceIndex']==refs['componentSourceIndex']
    assert v['outputRoot']==str(OUTPUT)and v['externalOutputRoot']==str(OUT)and v['externalParentDeadlineSeconds']==2400 and v['workerTimeoutMs']==600000
    assert v['scenarios']==['retained','fresh','wrapper']and v['monitorIndex']==refs['monitorIndex']and v['monitorEntry']==refs['monitorEntry']
    for k in ['originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','nativeBuildAllowed','nativeFreezeAllowed','componentBuildAllowed','gcAllowed','gcPressureAllowed','oomAllowed','faultInjectionAllowed','unsafeResetAllowed','wasmtimeAllowed','otherVariantsAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:assert v[k]is False
    assert v['actualRuntimeReview']is None


def run(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
    for k in ['NODE_OPTIONS','NODE_PATH','JCO_DEBUG','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK']:assert not os.environ.get(k)
    captured=[config_row];indices=[];refs=None;inputs=None
    def recheck():
        for r in captured:checked(r)
        for ix in indices:family(ix)
        if inputs:
            for r in inputs['modeRows']:assert stat.S_IMODE(checked(r['file']).stat().st_mode)==r['mode']
            for t in inputs['historicalDonorTrees']:
                root=Path(t['root']);assert not any(p.is_symlink()for p in root.rglob('*'))
                assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(t['names'])
        if refs:package_context(refs)
    try:
        cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='SECRET355_NORMAL_RUNTIME_CONFIG_V3'
        own=cfg['sourceIndex'];assert own['path']==str(OWN/'index.json');rows=family(own);captured+=rows;indices.append(own)
        refs=read(next(r for r in rows if r['path']==str(OWN/'references.json')));inputs=read(next(r for r in rows if r['path']==str(OWN/'source-inputs.json')))
        assert 33364<=len(inputs['files'])<=45000
        for r in inputs['files']:checked(r);captured.append(r)
        for r in inputs['families']:captured+=family(r);indices.append(r)
        root_row=cfg['rootAuthority'];root=read(root_row);root_model(root,own,refs);captured.append(root_row)
        assert root['entry']in rows and root['externalController']in rows
        peer,peerrows=indexed_result(root['sourceIndependentReview']);captured+=peerrows;indices.append(root['sourceIndependentReview']['index'])
        assert peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_PASSED_V3'and peer['sourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True
        assert peer['ownerActionsInvoked']is peer['hostActionsInvoked']is peer['runtimeActionsInvoked']is False
        proof,proofrows=indexed_result(refs['actualArtifactReview']);captured+=proofrows;indices.append(refs['actualArtifactReview']['index']);assert refs['actualArtifactContract']in proofrows
        contract=read(refs['actualArtifactContract']);assert proof['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_V2_ARTIFACT_REVIEW_PASSED_V1'and proof['verifiedPassed']is True and proof['componentSourceIndexSha256']==refs['componentSourceIndex']['sha256']
        assert proof['componentSha256']==refs['artifacts']['component']['sha256']and proof['engineSha256']==refs['engine']['sha256']and proof['nativeSourceFiles']==355 and proof['externalEmbeddingSources']==3 and proof['selectedManifestCount']==11 and proof['fullMetadataFields']==75
        assert proof['emittedImports']==[]and sorted(proof['publicAbiFunctions'])==['clear','inspect','run','validate']and contract['artifacts']==proof['artifacts']==refs['artifacts']
        for k in ['generatedModuleImported','ordinaryGuestExportsInvoked','keyOperationsInvoked','asyncScalarRuntimeProof']:assert proof[k]is False
        ro=read(root['retainedConfig']);assert ro['sourceIndex']==refs['retainedSourceIndex'];read(ro['rootAuthority']);captured+=[root['retainedConfig'],ro['rootAuthority']]
        assert checked(refs['pythonExecutable'])==Path(sys.executable).resolve()
        assert refs['monitorEntry']in captured and refs['node']in captured
        recheck()
        for path in [OUTPUT,OUT]:
            for p in(path,*path.parents):assert not p.is_symlink()
            assert not path.exists()
        monitor=load_actual(refs['monitorEntry'],'genuine_secret355_ordinary_runtime_owned_monitor')
        recheck();OUT.mkdir(mode=0o700)
        argv=[refs['node']['path'],str(OWN/'entry.mjs'),'parent',json.dumps(config_row,separators=(',',':'))]
        terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,2400,root_row)
        recheck();validate_terminal(terminal,root_row)
        print(json.dumps(dict(schemaVersion=1,state='SECRET355_NORMAL_RUNTIME_PARENT_RAW_ZERO_UNREVIEWED_V3',terminal=descriptor(OUT/'terminal.json'),actualRuntimeIndex=descriptor(OUTPUT/'index.json'),actualRuntimeCompletion=descriptor(OUTPUT/'completion.json'),rootAuthority=root_row,sourceIndex=own,requiresIndependentResultsReview=True,operationalAdmission=False)),flush=True)
    finally:recheck()


if __name__=='__main__':
    assert len(sys.argv)==2
    run(json.loads(sys.argv[1]))
