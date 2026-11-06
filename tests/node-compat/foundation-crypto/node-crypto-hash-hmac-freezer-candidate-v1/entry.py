"""Revalidated357 artifact freezer; no original successful-BUILD wire is used.
Stdlib authentication precedes every custom module import or operational call.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,re,stat,sys
if not __debug__:raise RuntimeError('Assertions must remain enabled')
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/node-crypto-hash-hmac-freezer-candidate-v1')
REPO=OWN.parents[3]
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze')
TMP_POLICY={'schemaVersion':1,'aliasPath':'/tmp','linkText':'private/tmp','resolved':'/private/tmp','selectedDescriptorPaths':['/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/classic-streams-admission.mjs','/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/zlib-admission.mjs'],'otherSymlinkAncestorsAllowed':False,'descriptorPathRewriting':False}

def physical(path):
    p=Path(path);assert p.is_absolute()and str(p)==path and not path.startswith('//')and '..'not in p.parts and '\\'not in path and '\0'not in path
    if path.startswith('/tmp/'):
        assert path in TMP_POLICY['selectedDescriptorPaths']
        assert Path('/tmp').is_symlink()and os.readlink('/tmp')=='private/tmp'and Path('/tmp').resolve()==Path('/private/tmp')
        p=Path('/private'+path)
    for q in(p,*p.parents):assert not q.is_symlink(),q
    return p

def identity(p):
    s=p.stat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def checked(r):
    assert type(r)is dict and set(r)=={'path','sha256','bytes'}and type(r['bytes'])is int and r['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',r['sha256'])
    p=physical(r['path']);a=identity(p);assert stat.S_ISREG(a[2])and a[4]==r['bytes'];h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4194304),b''):h.update(b)
    assert identity(p)==a and h.hexdigest()==r['sha256'];return p

def row(path):
    p=physical(str(path));a=identity(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4194304),b''):h.update(b)
    assert identity(p)==a;return dict(path=str(p),sha256=h.hexdigest(),bytes=a[4])

def read(r):assert r['bytes']<=32*1024**2;return json.loads(checked(r).read_bytes())

def safe(name):
    assert type(name)is str and name and not name.startswith('/')and '\\'not in name and '\0'not in name and all(p not in('','.','..')for p in name.split('/'));return name

def family(r):
    root=Path(r['path']).parent;v=read(r);names={'index.json'};rows=[r]
    for f in v['files']:
        name=safe(f['path']);assert name not in names;names.add(name);d=dict(f,path=str(root/name));checked(d);rows.append(d)
    assert not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names
    return rows

def load(r,name):
    s=importlib.util.spec_from_file_location(name,checked(r));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def whole_proof(pair,contract):
    rows=family(pair['index']);assert pair['result']in rows and contract in rows
    p=read(pair['result']);k=read(contract);assert p['schemaVersion']==1 and p['verifiedPassed']is True and p['state']==k['requiredReviewState']
    for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
        for key,value in k.get(group,{}).items():assert p[key]==value,(group,key)
    if 'requiredCoverage'in k:assert p['coverage']==k['requiredCoverage']
    return p,k,rows

def root_model(root,own,refs):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_HASH_HMAC357_REVALIDATED_FREEZE_PHASE_V1'
    assert root['phase']=='freeze-only'and root['freezerIndex']==own and root['entry']==refs['entry']
    assert root['artifactReview']==refs['artifactReview']and root['artifactContract']==refs['artifactContract']
    assert root['producerIndex']==refs['producerIndex']and root['engine']==refs['engine']and root['metadata']==refs['metadata']
    for key in ['configuredSourceRoot','workRoot','freezeRoot','externalRoot']:assert root[key]==refs[key]
    assert root['nativeSourceFiles']==357 and root['externalEmbeddingSources']==3 and root['selectedWholeManifests']==12 and root['rawMetadataFields']==83
    assert root['freezeAllowed']is root['readOnlyProducerAdmissionAllowed']is root['frozenOnlyVerificationAllowed']is root['ownedCopiesAllowed']is True
    assert root['originalRecipeExitCode']==0 and root['originalParentExitCodes']==[1,1]and root['originalBuildPreservationPassed']is root['originalBuildAccepted']is False
    assert root['tmpAliasPolicy']==refs['tmpAliasPolicy']==TMP_POLICY
    assert root['deadlineSeconds']==1800 and root['startFreeBytes']==2147483648 and root['stopFreeBytes']==838860800
    for k in ['nativeBuildAllowed','recipeAllowed','compilerAllowed','ninjaAllowed','gitAllowed','engineExecutionAllowed','guestAllowed','cryptoAllowed','gcAllowed','oomAllowed','debugAllowed','resetAllowed','exportAllowed','pinsAllowed','bootstrapAllowed','componentAllowed','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim']:assert root[k]is False,k
    for k in ['actualFreeze','actualFrozenReview','reviewedPins','runtimeAuthority']:assert root[k]is None

def artifact_model(p,refs):
    assert p['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_READ_ONLY_REVALIDATED_ARTIFACT_REVIEW_PASSED_V1'and p['publicationVersion']==2
    assert p['engine']==refs['engine']and p['metadata']==refs['metadata']and p['inputHashes']==refs['artifactLedger']
    assert p['originalRecipeExitCode']==0 and p['originalParentExitCodes']==[1,1]and p['originalBuildPreservationPassed']is p['originalBuildAccepted']is False
    assert p['currentInputBookendsPassed']is True and p['readOnlyParentRawExitCode']==0 and p['allOwnedGroupsGone']is True
    assert p['producerControllerIndex']==refs['producerIndex']and p['indexException']==refs['indexException']
    assert p['nativeSourceFiles']==357 and p['externalEmbeddingSources']==3 and p['rawMetadataFields']==83 and p['selectedWholeManifests']==12
    assert p['coverage']['currentLedgerFiles']==21451 and p['coverage']['currentTrees']==11
    for k in ['engineExecuted','guestExecuted','cryptoOperationsInvoked','operationalAdmission','runtimeAcceptanceClaim','grantsAnyActionAuthority']:assert p[k]is False

def trees(values,known):
    for t in values:
        base=Path(t['root']);assert not base.is_symlink();actual=[]
        for parent,dirs,files in os.walk(base,followlinks=False):
            for name in dirs+files:
                p=Path(parent)/name;kind='symlink'if p.is_symlink()else'directory'if p.is_dir()else'file'
                actual.append(dict(path=p.relative_to(base).as_posix(),kind=kind,mode=stat.S_IMODE(p.lstat().st_mode)))
                if kind=='file':assert str(p)in known,'Every distribution regular file must have a checked descriptor'
        assert sorted(actual,key=lambda r:r['path'])==t['entries']

def recheck(frame):
    for d in list(frame['captured'].values()):
        p=checked(d);assert identity(p)==frame['identities'][d['path']]
    for ix in frame['families'].values():family(ix)
    trees(frame['trees'],frame['captured'])
    for a in frame['aliases']['symlinks']:assert Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve(strict=True))==a['resolved']
    for a in frame['aliases']['archiveHardlinks']:
        x=Path(a['path']).stat();y=Path(a['target']).stat();assert(x.st_dev,x.st_ino)==(y.st_dev,y.st_ino)
    e=frame['refs']['indexException'];assert stat.S_IMODE(checked(e['currentActual']).stat().st_mode)==0o600
    frame['indexModel'].decode(checked(e['currentActual']).read_bytes(),checked(frame['refs']['baselineTreeTransport']).read_bytes())
    if frame.get('freezeHandle')is not None:
        s=FREEZE.lstat();held=os.fstat(frame['freezeHandle']);assert stat.S_ISDIR(s.st_mode)and stat.S_IMODE(s.st_mode)==0o700 and(s.st_dev,s.st_ino)==frame['freezeIdentity']==(held.st_dev,held.st_ino)
    elif not frame.get('creationAllowed',False):assert not FREEZE.exists()and not FREEZE.is_symlink()
    elif FREEZE.exists():assert not FREEZE.is_symlink()and FREEZE.is_dir()and stat.S_IMODE(FREEZE.stat().st_mode)==0o700

def bootstrap(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
    cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='HASH_HMAC357_REVALIDATED_FREEZE_CONFIG_V1'
    root=read(cfg['rootAuthority']);own=cfg['freezerIndex'];assert root['freezerIndex']==own and own['path']==str(OWN/'index.json')
    own_rows=family(own);byname={Path(r['path']).relative_to(OWN).as_posix():r for r in own_rows[1:]};refs=read(byname['references.json'])
    assert refs['entry']==byname['entry.py'];root_model(root,own,refs)
    captured={};families={};identities={}
    def add(d):
        p=checked(d);assert d['path']not in captured or captured[d['path']]==d
        captured[d['path']]=d
        if d['path']in identities:assert identities[d['path']]==identity(p)
        else:identities[d['path']]=identity(p)
    def indexed(ix):
        for d in family(ix):add(d)
        families[ix['path']]=ix
    for d in [config_row,cfg['rootAuthority'],*own_rows]:add(d)
    families[own['path']]=own
    p,k,proof_rows=whole_proof(refs['artifactReview'],refs['artifactContract']);artifact_model(p,refs)
    for d in proof_rows:add(d)
    families[refs['artifactReview']['index']['path']]=refs['artifactReview']['index']
    peer,_,peer_rows=whole_proof(root['sourceReview'],root['sourceReviewContract'])
    assert peer['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_FREEZER_SOURCE_REVIEW_PASSED_V1'and peer['freezerSourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True
    assert peer['artifactReviewIndexSha256']==refs['artifactReview']['index']['sha256']and peer['producerSourceIndexSha256']==refs['producerIndex']['sha256']
    assert peer['nativeSourceFiles']==357 and peer['externalEmbeddingSources']==3 and peer['rawMetadataFields']==83 and peer['selectedWholeManifests']==12
    for key in ['ownerActionsInvoked','hostActionsInvoked','nativeFreezeOrAdmissionActionsInvoked','engineOrGuestOrCryptoActionsInvoked']:assert peer[key]is False
    for d in peer_rows:add(d)
    families[root['sourceReview']['index']['path']]=root['sourceReview']['index']
    inputs=read(refs['sourceInputs'])
    for d in inputs['files']:add(d)
    for ix in inputs['families']:indexed(ix)
    for d in read(refs['artifactLedger'])['files']:add(d)
    for d in read(refs['referenceAdditions'])['files']:add(d)
    tree_data=read(refs['artifactTrees'])['trees'];trees(tree_data,captured)
    alias_data=read(refs['referenceAliases'])
    for a in alias_data['symlinks']:assert Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve(strict=True))==a['resolved']
    assert not FREEZE.exists()and not FREEZE.is_symlink()
    assert checked(refs['python'])==Path(sys.executable).resolve()
    # All source/proof/current ledger/distribution bytes precede custom imports.
    io=load(refs['producerIo'],'genuine_P3_357_io_for_new_freeze_phase')
    index_model=load(refs['indexModel'],'original_current_index_decoder_DATA_only')
    frame=dict(config=cfg,configRow=config_row,root=root,own=own,ownRows=own_rows,ownByName=byname,refs=refs,proof=p,contract=k,captured=captured,identities=identities,families=families,trees=tree_data,aliases=alias_data,io=io,indexModel=index_model,freezeHandle=None,creationAllowed=False)
    recheck(frame);return frame

def parent(frame):
    out=Path(frame['refs']['externalRoot']);assert not out.exists()and not out.is_symlink();os.umask(0o077);out.mkdir(mode=0o700)
    monitor=load(frame['refs']['monitorEntry'],'genuine_original0af_hash357_freeze_monitor')
    recheck(frame);frame['creationAllowed']=True
    args=[frame['refs']['python']['path'],'-B','-I',str(OWN/'entry.py'),'worker',json.dumps(frame['configRow'],separators=(',',':'))]
    try:t=monitor.monitor(args,str(REPO),dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),out,1800,frame['config']['rootAuthority'])
    finally:recheck(frame)
    assert t['authority']==frame['config']['rootAuthority']and t['rawExitCode']==0 and t['allObservedOwnedGroupsGone']is t['parentOwnedGroupGone']is True
    assert not t['forcedCleanup']and not t['timeout']and t['signals']==t['errors']==t['remainingObservedPids']==[]
    receipt=row(FREEZE/'normal-off-freeze-receipt.json');r=read(receipt);assert r['rootAuthority']==frame['config']['rootAuthority']and r['freezerSourceIndex']==frame['own']
    print(json.dumps(dict(schemaVersion=1,state='HASH_HMAC357_REVALIDATED_ARTIFACT_FREEZE_RAW_ZERO_UNREVIEWED_V1',receipt=receipt,externalParentTerminal=row(out/'terminal.json'),engineExecuted=False,cryptoOperationsInvoked=False,independentActualFreezeReviewRequired=True)),flush=True)

def main():
    assert len(sys.argv)==3 and sys.argv[1]in('parent','worker')
    f=bootstrap(json.loads(sys.argv[2]))
    try:
        if sys.argv[1]=='parent':parent(f)
        else:load(f['ownByName']['freeze.py'],'own_revalidated_hash357_freeze_body').run(f,recheck)
    finally:recheck(f)
if __name__=='__main__':main()
