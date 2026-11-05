"""Dormant normal-OFF freezer parent/worker. No action during source preparation."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import types

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-freezer-candidate-v1'
SOURCE='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source'
WORK='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build'
FROZEN='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze'
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze-external-root')
NATIVE_SHA='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
COMMON_RELATIVE='tests/node-compat/foundation-crypto/ownership-secret-freezer-candidate-v1/artifact-tools/artifact_common.py'
TIMEOUT=2400


def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    p=Path(row['path']);assert p.is_absolute()and '..'not in p.parts
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    for q in (p,*p.parents):assert not q.is_symlink(),q
    a=p.stat();assert stat.S_ISREG(a.st_mode)and type(row['bytes'])is int and a.st_size==row['bytes'];h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    assert h.hexdigest()==row['sha256'];return p


def read(row):
    p=checked(row);assert row['bytes']<=32*1024*1024
    b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==row['sha256'];return json.loads(b)


def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(row);return row


def write(path,value):
    with Path(path).open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())


def family(row):
    value=read(row);root=Path(row['path']).parent;names=set();rows=[row]
    for r in value['files']:
        name=r['path'];assert name and name not in names and not name.startswith('/')and '\\'not in name and all(x not in ('','.','..')for x in name.split('/'))
        names.add(name);d=dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==names|{'index.json'};return rows


def proof(pair):
    rows=family(pair['index']);assert sum(r==pair['result']for r in rows[1:])==1
    return read(pair['result']),rows


def select_common(rows,root_row):
    """Exact complete repository-relative role; never a suffix or first match."""
    path=str(REPO/COMMON_RELATIVE)
    hits=[r for r in rows if r['path']==path]
    assert len(hits)==1 and hits[0]==root_row
    assert Path(root_row['path']).relative_to(REPO).as_posix()==COMMON_RELATIVE
    return hits[0]


def validate_root(root,index,contract,refs):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_NORMAL_OFF_FREEZE_V1'
    assert root['phase']=='freeze'and root['variant']=='normal-off'and root['freezeAllowed']is True
    assert root['freezerIndex']==index and index['path']==str(OWN/'index.json')
    assert root['nativeSourceIndex']==contract['nativeSourceIndex']and root['nativeSourceIndex']['sha256']==NATIVE_SHA
    assert root['configuredSourceRoot']==SOURCE and root['workRoot']==WORK and root['freezeRoot']==FROZEN
    assert root['originalToolingRoot']==str(OWN)and root['externalOutputRoot']==str(OUT)
    assert root['entry']['path']==str(OWN/'freeze.py')and root['workerMode']=='worker'
    assert root['commonHelper']['path']==str(REPO/COMMON_RELATIVE)
    assert root['engine']==contract['engine']and root['metadata']==contract['metadata']
    assert root['actualBuildReview']==contract['actualBuildReview']and contract['actualBuildReview']is not None
    assert root['actualBuildContract']==contract['actualBuildContract']and root['buildReferenceLedger']==contract['buildReferenceLedger']
    assert root['buildRootObservation']==contract['actualBuildRootObservation']
    assert root['nativeSourceFiles']==355 and root['externalEmbeddingSources']==3 and root['selectedManifestCount']==11
    assert root['externalParentDeadlineSeconds']==TIMEOUT and root['genericMonitorIndex']==refs['monitorIndex']
    for k in ['buildAllowed','exportAllowed','bootstrapAllowed','gcAllowed','normalMutationAllowed','metadataProjectionAllowed',
              'engineExecutionAllowed','componentAllowed','guestAllowed','keyOrCryptoAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:
        assert root[k]is False
    for k in ['actualFreezeReceipt','independentFrozenArtifactReview','reviewedNativePins','runtimeAuthority']:assert root[k]is None
    return True


def validate_source_peer(value,index,contract):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_FREEZER_SOURCE_REVIEW_PASSED_V1'
    assert value['sourceIndexSha256']==index['sha256']and value['nativeSourceIndexSha256']==NATIVE_SHA
    assert value['actualBuildReviewIndexSha256']==contract['actualBuildReview']['index']['sha256']
    assert value['sourceOnly']is True and value['sourceReviewPassed']is True
    for k in ['ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked']:assert value[k]is False


def validate_build(value,contract):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V1'and value['verifiedPassed']is True
    assert value['sourceIndexSha256']==NATIVE_SHA and value['controllerSourceIndexSha256']=='c9573e416c76350a6ab169b0d5ddb2938883e9698620759b4285ee7a2fde3643'and value['variant']=='normal-off'
    assert value['unchangedParentNativeFiles']==352 and value['changedNativeFiles']==3 and value['selectedManifestCount']==11
    assert value['nativeSourceFiles']==355 and value['externalEmbeddingSources']==3
    assert value['engine']==contract['engine']and value['metadata']==contract['metadata']and value['rootBuildObservation']==contract['actualBuildRootObservation']
    assert value['inputHashes']==contract['buildReferenceLedger']
    assert value['configuredSourceRoot']==SOURCE and value['workRoot']==WORK
    assert value['engineSha256']==contract['engine']['sha256']and value['metadataSha256']==contract['metadata']['sha256']
    for k in ['actualFreezeVerified','engineExecuted','operationalAdmission','runtimeAcceptanceClaim']:assert value[k]is False
    return True


def normal_protection(row):
    value=read(row);assert value['originalReferenceEntries']==1387 and len(value['requiredNormalFreezeMembership'])==1391
    rows=[row,value['freezeReceipt']]
    rows += [{k:r[k]for k in ['path','sha256','bytes']}for r in value['frozenCopyEntries']]
    for r in value['originals']:rows.extend([r['original'],r['frozen']])
    for r in rows:checked(r)
    root=Path(value['freezeReceipt']['path']).parent;actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==set(value['requiredNormalFreezeMembership']);return rows


def recheck(frame):
    for r in frame['captured']:checked(r)
    for r in frame['families']:family(r)
    normal_protection(frame['normalProtection'])
    for r in frame['stageCopies']:
        a=checked(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
        b=checked(dict(path=str(Path(SOURCE)/r['path']),sha256=r['sha256'],bytes=r['bytes']))
        assert stat.S_IMODE(a.stat().st_mode)==stat.S_IMODE(b.stat().st_mode)==r['sourceMode']


def authorize(config_row):
    config=read(config_row);assert config['schemaVersion']==1 and config['state']=='SECRET_NORMAL_OFF_FREEZER_CONFIG_V1'
    index=config['freezerIndex'];assert index['path']==str(OWN/'index.json')
    own_rows=family(index);contract=read(next(r for r in own_rows if r['path']==str(OWN/'source-contract.json')))
    refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
    assert config['nativeSourceIndex']==contract['nativeSourceIndex']
    root=read(config['rootAuthority']);validate_root(root,index,contract,refs)
    assert root['entry']in own_rows
    selected=select_common(own_rows,root['commonHelper'])
    captured=[config_row,config['rootAuthority'],*own_rows];indices=[index]
    for item in refs['families']:
        captured+=family(item['index']);indices.append(item['index'])
    for row in refs['files']:checked(row);captured.append(row)
    native=family(config['nativeSourceIndex']);captured+=native;indices.append(config['nativeSourceIndex'])
    ir=read(next(r for r in native if r['path']==str(Path(contract['nativeSourceIndex']['path']).parent/'references.json')))
    for item in ir['families']:
        captured+=family(item['index']);indices.append(item['index'])
    data,rows=proof(root['independentSourceReview']);validate_source_peer(data,index,contract)
    source_peer_rows=rows
    captured+=rows;indices.append(root['independentSourceReview']['index'])
    data,rows=proof(contract['actualBuildReview']);validate_build(data,contract)
    captured+=rows;indices.append(contract['actualBuildReview']['index'])
    assert contract['actualBuildContract']in rows and contract['buildReferenceLedger']in rows
    build_contract=read(contract['actualBuildContract'])
    assert all(data[k]==v for k,v in build_contract.items())
    ledger=read(contract['buildReferenceLedger']);assert ledger['schemaVersion']==1 and len(ledger['files'])==25594 and len({r['path']for r in ledger['files']})==25594
    for row in ledger['files']:checked(row);captured.append(row)
    normal=ir['normalProtection'];captured+=normal_protection(normal)
    stage=read(refs['actualStageJournal']);assert len(stage['copies'])==1424
    for row in stage['copies']:
        captured += [dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']),dict(path=str(Path(SOURCE)/row['path']),sha256=row['sha256'],bytes=row['bytes'])]
    for row in [contract['policy'],contract['helper'],contract['recipe'],contract['buildAdmission'],contract['engine'],contract['metadata'],refs['node'],refs['monitorEntry']]:checked(row);captured.append(row)
    frame=dict(config=config,root=root,contract=contract,refs=refs,captured=captured,families=indices,normalProtection=normal,stageCopies=stage['copies'],
        freezeRoot=FROZEN,configuredSourceRoot=SOURCE,originalToolingRoot=str(OWN),entryPath=str(OWN/'freeze.py'),guardPath=str(OWN/'freeze.py'),
        enginePath=contract['engine']['path'],label='normal-off',sourceIndex=index,nativeSourceIndex=contract['nativeSourceIndex'],
        rootAuthority=config['rootAuthority'],sourcePeer=root['independentSourceReview'],actualBuildReview=contract['actualBuildReview'],buildReferenceLedger=contract['buildReferenceLedger'],
        active=root['entry'],donor=refs['donorBody'],ownCapsule=own_rows,proofCapsules=[config_row,config['rootAuthority'],*source_peer_rows,*rows],commandRecords=[],
        selectedCommonHelper=selected,configuredPolicy=contract['policy'],configuredHelper=contract['helper'])
    recheck(frame);return frame


def capture_command(frame,role,argv):
    """Real future helper call: retain complete raw streams/status before assertions."""
    assert role in ('source-admission','embedding-after')and role not in {r['role']for r in frame['commandRecords']}
    if role=='source-admission':
        assert argv==[frame['refs']['node']['path'],str(OWN/'artifact-tools/metadata-admission.mjs'),frame['contract']['metadata']['path'],'normal-off',SOURCE]
    else:
        metadata=read(frame['contract']['metadata'])
        assert argv==[frame['refs']['ninja']['path'],'-C',str(Path(metadata['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding']
    root=OUT/'helper-calls';assert OUT.is_dir()and not OUT.is_symlink()
    root.mkdir(mode=0o700,exist_ok=True);output=root/role;output.mkdir(mode=0o700)
    status=None;stdout=b'';stderr=b'';timed_out=False;error=None
    try:
        result=subprocess.run(argv,cwd=SOURCE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180 if role=='source-admission'else 60,check=False)
        status=result.returncode;stdout=result.stdout;stderr=result.stderr
    except subprocess.TimeoutExpired as failure:
        stdout=failure.stdout or b'';stderr=failure.stderr or b'';timed_out=True;error=type(failure).__name__
    except BaseException as failure:error=type(failure).__name__
    finally:
        for name,data in [('stdout.log',stdout),('stderr.log',stderr)]:
            with (output/name).open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
        terminal=dict(schemaVersion=1,role=role,argv=argv,cwd=SOURCE,rawExitCode=status,timeout=timed_out,error=error,
            stdout=descriptor(output/'stdout.log'),stderr=descriptor(output/'stderr.log'),engineExecuted=False)
        write(output/'terminal.json',terminal)
        frame['commandRecords'].append(dict(role=role,stdout=terminal['stdout'],stderr=terminal['stderr'],terminal=descriptor(output/'terminal.json')))
    assert status==0 and not timed_out and error is None
    assert stderr==b''
    return types.SimpleNamespace(returncode=status,stdout=stdout,stderr=stderr)


def validate_admission(frame,value):
    c=frame['contract']
    assert value['state']==c['sourceAdmissionState']and value['label']=='normal-off'and value['sourceRoot']==SOURCE
    assert value['sourceFiles']==355 and value['selectedManifestCount']==11 and value['engineBytesRead']is False and value['guestExecuted']is False
    assert value['policySha256']==c['policy']['sha256']and value['admissionSourceSha256']==c['buildAdmission']['sha256']
    assert value['classicSourceAdmission']['cryptoSecretFailureSourcePolicy']==read(c['policy'])['cryptoSecretFailureSourcePolicy']
    assert value['validationBootstrapOnly']is True and value['operationalAdmission']is False


def validate_receipt_roles(frame,receipt,active_sha,donor_sha):
    assert receipt['state']==frame['contract']['frozenReceiptState']and receipt['label']=='normal-off'
    assert receipt['nativeSourceIndexed']==frame['nativeSourceIndex']and receipt['freezerSourceIndexed']==frame['sourceIndex']
    assert receipt['cryptoSecretFailureSourcePolicy']==read(frame['contract']['policy'])['cryptoSecretFailureSourcePolicy']
    assert receipt['helperSha256']==active_sha==frame['active']['sha256']
    assert receipt['activeFreezerTooling']['original']==frame['entryPath']and receipt['activeFreezerTooling']['sha256']==active_sha
    assert receipt['donorFreezerTooling']['original']==frame['donor']['path']and receipt['donorFreezerTooling']['sha256']==donor_sha
    assert receipt['configuredSourceRoot']==SOURCE and receipt['originalToolingRoot']==str(OWN)
    assert receipt['sourceRoot']==FROZEN+'/source'and receipt['componentizeSourceRoot']==FROZEN+'/componentize-source'
    assert receipt['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)



def validate_output(plan,receipt_path):
    """Before receipt publication: exact inventory, bytes, private modes, separate inodes."""
    root=Path(FROZEN);expected={str(r['target'].relative_to(root))for r in plan};actual=set()
    assert not receipt_path.exists()and not receipt_path.is_symlink()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==expected
    for row in plan:
        target=checked(descriptor(row['target']))
        assert descriptor(target)['sha256']==row['sha256']
        assert stat.S_IMODE(target.stat().st_mode)==0o600
        with target.open('r+b')as stream:os.fsync(stream.fileno())
        if row.get('original')is not None:
            original=checked(descriptor(row['original']))
            assert descriptor(original)['sha256']==row['sha256']
            assert (original.stat().st_dev,original.stat().st_ino)!=(target.stat().st_dev,target.stat().st_ino)
    return True


def load_actual(row,name):
    spec=importlib.util.spec_from_file_location(name,checked(row));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def validate_terminal(t,authority):
    assert t['rawExitCode']==0 and t['authority']==authority
    assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
    for k in ['timeout','forcedCleanup']:assert t[k]is False
    for k in ['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]
    assert t['stderr']['bytes']==0


def parent(frame):
    assert not OUT.exists()and not OUT.is_symlink()and not Path(FROZEN).exists()
    monitor=load_actual(frame['refs']['monitorEntry'],'genuine_secret_freeze_owned_monitor');recheck(frame)
    OUT.mkdir(mode=0o700)
    argv=[sys.executable,'-B','-I',str(OWN/'freeze.py'),'worker',json.dumps(frame['configDescriptor'],separators=(',',':'))]
    try:t=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['rootAuthority'])
    finally:recheck(frame)
    validate_terminal(t,frame['rootAuthority']);print(json.dumps(t),flush=True)


def worker(frame):
    assert not Path(FROZEN).exists()and not Path(FROZEN).is_symlink()
    # Private output modes belong only to this newly launched worker process.
    os.umask(0o077)
    common=load_actual(frame['selectedCommonHelper'],'actual_secret_normal_common')
    assert str(common.HERE)==str(OWN/'artifact-tools')and str(common.REPO)==SOURCE and str(common.OUTPUT)==FROZEN
    body_row=next(r for r in frame['ownCapsule']if r['path']==str(OWN/'freezer-body.py'))
    body=load_actual(body_row,'actual_secret_normal_freezer_body');recheck(frame)
    guard=types.SimpleNamespace(recheck=recheck,validate_admission=validate_admission,validate_receipt_roles=validate_receipt_roles,capture_command=capture_command,validate_output=validate_output)
    return body.freeze(frame,common,guard)


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv)==3 and sys.argv[1]in ('parent','worker')
    assert not any(os.environ.get(k)for k in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH'])
    config_row=json.loads(sys.argv[2]);frame=authorize(config_row);frame['configDescriptor']=config_row
    try:
        if sys.argv[1]=='parent':parent(frame)
        else:worker(frame)
    finally:recheck(frame)


if __name__=='__main__':main()
