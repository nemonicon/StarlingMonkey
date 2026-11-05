"""Dormant owned external caller for the two selected-clock differential phases."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/clock-v13-runtime-candidate-v2'
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

def load_actual(row,name):
    spec=importlib.util.spec_from_file_location(name,checked(row));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def package_context(refs):
    v=read(refs['packageInventory'])['package'];root=Path(v['root']);s=root.stat();assert str(root)==refs['loaderPackageRoot']and not root.is_symlink()and stat.S_IMODE(s.st_mode)==0o700
    files={r['relativePath']:r for r in v['files']};links={r['path']:r for r in v['links']};assert len(files)==4889 and len(links)==21
    actual=set()
    for p in root.rglob('*'):
        n=p.relative_to(root).as_posix();s=p.lstat()
        if p.is_symlink():
            r=links[n];assert os.readlink(p)==r['target']and str(p.resolve())==r['resolvedPath']and p.resolve().is_relative_to(root);actual.add(n)
        elif p.is_dir():assert stat.S_IMODE(s.st_mode)==0o700
        else:
            r=files[n];assert r['path']==str(p)and stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'];checked(dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']));actual.add(n)
    assert actual==set(files)|set(links)


def run(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
    for k in ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK']:assert not os.environ.get(k)
    captured=[config_row];indices=[];refs=None
    def recheck():
        for r in captured:checked(r)
        for r in indices:family(r)
        if refs:package_context(refs)
    try:
        cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='CLOCK_V13_REACTDOM_CONFIG_V2';own=cfg['sourceIndex'];assert own['path']==str(OWN/'index.json')
        rows=family(own);captured+=rows;indices.append(own);refs=read(next(r for r in rows if r['path']==str(OWN/'references.json')));inputs=read(next(r for r in rows if r['path']==str(OWN/'source-inputs.json')))
        assert 11581<=len(inputs['files'])<=25000
        for r in inputs['files']:checked(r);captured.append(r)
        for r in inputs['families']:captured+=family(r);indices.append(r)
        root_row=cfg['rootAuthority'];root=read(root_row);captured.append(root_row);phase=root['phase'];assert phase in ['mapped-transpile','runtime-differential']
        assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CLOCK_V13_REACTDOM_DIFFERENTIAL_V2'and root['sourceIndex']==own and root['entry']in rows and root['externalController']in rows
        assert root['actualArtifactReview']==refs['actualArtifactReview']and root['actualArtifactContract']==refs['actualArtifactContract']and root['componentSha256']==refs['component']['sha256']and root['selectedInterfaces']==refs['selectedInterfaces']and root['mappingOptions']==refs['mappingOptions']
        mapping=phase=='mapped-transpile';assert root['mappedTranspileAllowed']is mapping and root['jcoCompilerWasmHelpersAllowed']is mapping
        for k in ['generatedApplicationImportAllowed','ordinaryRunAllowed','stockWasmtimeAllowed']:assert root[k]is(not mapping)
        assert root['nativeReadOnlyPreflightAllowed']is root['standardShimWorkerThreadsAllowed']is True and root['ownedWorkerDeadlineMs']==180000 and root['requiredExternalParentDeadlineSeconds']==1200
        for k in ['customHostServicesAllowed','componentConstructionAllowed','nativeBuildAllowed','engineReplacementAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','otherGuestAllowed','resourceSevenCaseProfileAccepted','clockProfilePromotionAllowed','dateTimerSnapshotTeardownAccepted','resetOrReuseAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:assert root[k]is False
        assert root['outputRoot']==(refs['mappedOutputRoot']if mapping else refs['runtimeOutputRoot'])
        assert root['externalOutputRoot']==root['outputRoot']+'-external-root'and root['monitorIndex']==refs['monitorIndex']and root['monitorEntry']==refs['monitorEntry']
        assert root['actualMappedOutputReview']is None if mapping else type(root['actualMappedOutputReview'])is dict
        peer,rs=indexed_result(root['sourceIndependentReview']);captured+=rs;indices.append(root['sourceIndependentReview']['index']);assert peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V2'and peer['sourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True
        for k in ['ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked']:assert peer[k]is False
        proof,rs=indexed_result(refs['actualArtifactReview']);captured+=rs;indices.append(refs['actualArtifactReview']['index']);assert refs['actualArtifactContract']in rs
        assert proof['state']=='INDEPENDENT_CLOCK_V13_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and proof['verifiedPassed']is True and proof['componentSha256']==refs['component']['sha256']and proof['componentSourceIndexSha256']==refs['componentSourceIndex']['sha256']
        assert proof['artifacts']==read(refs['actualArtifactContract'])['artifacts']==refs['artifacts']and proof['nativeSourceFiles']==342 and proof['fullMetadataFields']==64 and proof['selectedManifestCount']==9 and proof['externalEmbeddingSources']==3
        assert sorted(proof['emittedImports'])==sorted(refs['selectedInterfaces'])and proof['publicAbiFunctions']==['run']and proof['generatedModuleImported']is proof['ordinaryGuestExportsInvoked']is False
        if not mapping:read(root['actualMappedOutputReview']);captured.append(root['actualMappedOutputReview'])
        assert checked(refs['pythonExecutable'])==Path(sys.executable).resolve()and refs['monitorEntry']in captured and refs['node']in captured
        recheck();out=Path(root['externalOutputRoot']);assert not out.exists()and not out.is_symlink();assert not Path(root['outputRoot']).exists()
        monitor=load_actual(refs['monitorEntry'],'genuine_clock_scalar_owned_monitor');recheck();out.mkdir(mode=0o700)
        env={k:v for k,v in os.environ.items()if not k.startswith('NODE_COMPAT_')};env.update(refs['requiredNativeReadOnlyEnvironment']);env['PYTHONDONTWRITEBYTECODE']='1'
        for k in ['HOME','home','CODEX_HOME']:assert env.get(k)==os.environ.get(k)
        argv=[refs['node']['path'],str(OWN/'entry.mjs'),'map'if mapping else'runtime',json.dumps(config_row,separators=(',',':'))]
        terminal=monitor.monitor(argv,str(REPO),env,out,1200,root_row);recheck();validate_terminal(terminal,root_row)
        print(json.dumps(dict(schemaVersion=1,state='CLOCK_V13_SLICE_EXTERNAL_RAW_ZERO_UNREVIEWED_V2',phase=phase,rootAuthority=root_row,sourceIndex=own,terminal=descriptor(out/'terminal.json'),requiresActualResultsReview=True,fullClockProfileAcceptance=False)),flush=True)
    finally:recheck()


if __name__=='__main__':
    assert len(sys.argv)==2
    run(json.loads(sys.argv[1]))
