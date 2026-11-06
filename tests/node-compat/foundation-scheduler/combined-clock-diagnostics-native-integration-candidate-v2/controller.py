"""Dormant own clock357 stage/build caller. Only stdlib is imported at entry.
No helper, monitor, compiler, or guest is invoked merely by importing this file.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,shlex,shutil,stat,struct,subprocess,sys,time
if not __debug__:raise RuntimeError('Assertions must remain enabled')
sys.dont_write_bytecode=True
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-clock-diagnostics-native-integration-candidate-v2'
SOURCE=Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-source')
WORK=Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-build')
FREEZE=Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-freeze')
STAGE_OUT=Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-stage-external-root')
BUILD_OUT=Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-build-external-root')
BUILD_RESULT=Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-build-result')
JOURNAL=Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-stage.json')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
DOCUMENT_LINKS={'docs/src/ADOPTERS.md':'../../ADOPTERS.md','docs/src/CODE_OF_CONDUCT.md':'../../CODE_OF_CONDUCT.md','docs/src/README.md':'../../README.md'}
START_FREE=2*1024**3
STOP_FREE=800*1024**2
ENV_POLICY={'removePrefixes':['BASH_FUNC_'],'removeExactNames':['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE'],'preserveExactNames':['HOME','home','CODEX_HOME'],'mustRunBeforeFirstControllerOrBash':True,'recordNamesOnly':True}

def clean_environment(original):
    removed=sorted(k for k in original if k.startswith('BASH_FUNC_')or k in ENV_POLICY['removeExactNames'])
    result={k:v for k,v in original.items()if k not in removed}
    for k in ENV_POLICY['preserveExactNames']:assert(k in original)==(k in result)and original.get(k)==result.get(k)
    return result,removed

def safe(name):
    assert type(name)is str and name and not name.startswith('/')and '\\'not in name and '\0'not in name
    assert all(p not in('','.','..')for p in name.split('/'))and name.split('/')[0]!='.git'
    return name

def physical(path):
    path=Path(path);assert path.is_absolute()and '..'not in path.parts
    if str(path).startswith('/tmp/'):
        assert Path('/tmp').is_symlink()and os.readlink('/tmp')=='private/tmp'and Path('/tmp').resolve()==Path('/private/tmp')
        path=Path('/private'+str(path))
    for p in(path,*path.parents):assert not p.is_symlink(),p
    return path

def descriptor(path):
    path=physical(path);before=path.stat();assert stat.S_ISREG(before.st_mode)
    h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    after=path.stat();assert identity(before)==identity(after)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=after.st_size)

def identity(s):return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def checked(row):
    assert set(row)=={'path','sha256','bytes'}and type(row['bytes'])is int and row['bytes']>=0
    assert len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    p=physical(row['path']);assert descriptor(p)==dict(row,path=str(p));return p

def read(row):
    assert row['bytes']<=32*1024**2;return json.loads(checked(row).read_bytes())

def family(row):
    value=read(row);root=Path(row['path']).parent;names={'index.json'};rows=[row]
    for r in value['files']:
        name=safe(r['path']);assert name not in names;names.add(name)
        full=dict(r,path=str(root/name));checked(full);rows.append(full)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    assert actual==names;return rows

def proof(pair,contract=None):
    rows=family(pair['index']);assert pair['result']in rows
    value=read(pair['result'])
    if contract is not None:
        assert contract in rows;k=read(contract)
        assert value['state']==k['requiredReviewState']and value['schemaVersion']==1 and value['verifiedPassed']is True
        for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
            for name,want in k.get(group,{}).items():assert value[name]==want,(group,name)
        if 'requiredCoverage'in k:assert value['coverage']==k['requiredCoverage']
    return value,rows

def capture(frame,row):
    p=checked(row);s=p.stat();key=row['path']
    if key in frame['rows']:assert frame['rows'][key]==row and frame['ids'][key]==identity(s)
    else:frame['rows'][key]=row;frame['ids'][key]=identity(s)

def recheck(frame):
    for r in list(frame['rows'].values()):capture(frame,r)
    for r in frame['families']:family(r)
    if frame.get('staged'):
        targets=set()
        for r in frame['plan']:
            p=checked(dict(path=str(SOURCE/r['path']),sha256=r['sha256'],bytes=r['bytes']));s=p.stat();original=checked(r['origin']).stat()
            assert stat.S_IMODE(s.st_mode)==r['mode']and s.st_nlink==1
            assert(s.st_dev,s.st_ino)!=(original.st_dev,original.st_ino)and(s.st_dev,s.st_ino)not in targets
            targets.add((s.st_dev,s.st_ino))
        assert len(targets)==1583
        for key in ['stagedGitConfig','stagedGitHead','stagedGitShallow']:checked(frame['stage'][key])
        assert git_inventory(SOURCE)==frame['stage']['stagedGitObjects']
        index=index_observation(SOURCE/'.git/index')
        index_stat_only(frame['stage']['gitIndexAfterOverlay'],index)

def load_actual(row,name):
    path=checked(row);spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def root_model(root,own,refs,phase):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CLOCK_DIAGNOSTIC357_PHASE_V2'
    assert phase in('stage','build')and root['phase']==phase
    assert root['sourceIndex']==own and own['path']==str(OWN/'index.json')
    assert root['entry']==refs['controller']and root['contexts']==refs['contexts']
    assert root['nativeSourceFiles']==357 and root['externalEmbeddingSources']==3 and root['selectedWholeManifests']==11 and root['rawMetadataFields']==82
    assert root['sourceStageAllowed']==(phase=='stage')and root['nativeBuildAllowed']==(phase=='build')
    assert root['monitorIndex']==refs['monitorIndex']and root['monitorEntry']==refs['monitorEntry']
    assert root['lifecycleIndex']==refs['lifecycleIndex']and root['lifecycleEntry']==refs['lifecycleEntry']
    assert root['environmentPolicy']==ENV_POLICY and root['cleanEnvironmentRequiredBeforeEntry']is True
    assert root['deadlineSeconds']==(600 if phase=='stage'else 7200)
    assert root['startFreeBytes']==START_FREE and root['stopFreeBytes']==STOP_FREE
    assert root['initialVariant']=='diagnostic-normal-off'and root['releaseOnly']is True and root['allSharedDiagnosticMacrosOn']is True
    assert root['buildEnvironment']==refs['buildEnvironment']and root['cachePlan']==refs['cachePlan']
    for k in ['freezeAllowed','exportAllowed','pinsAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','clockRuntimeAllowed','cryptoAllowed','gcAllowed','oomAllowed','debugAllowed','resetAllowed','normalMutationAllowed','operationalAdmission','sourcePromotionAllowed','allSeventeenGatesAccepted']:assert root[k]is False,k
    for k in ['actualBuild','actualFreeze','actualArtifact','reviewedPins','runtimeAuthority']:assert root[k]is None,k
    if phase=='stage':assert root['actualStageReview']is None and root['actualStageResult']is None
    else:assert root['actualStageReview']is not None and root['actualStageResult']is not None

def peer_model(value,own):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CLOCK_DIAGNOSTIC357_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V2'
    assert value['sourceIndexSha256']==own['sha256']and value['sourceOnly']is value['sourceReviewPassed']is True
    for k in ['ownerActionsInvoked','hostActionsInvoked','nativeBuildOrStageActionsInvoked','runtimeActionsInvoked']:assert value[k]is False
    assert value['nativeSourceFiles']==357 and value['externalEmbeddingSources']==3 and value['rawMetadataFields']==82 and value['selectedWholeManifests']==11

def stage_review_model(value,own,actual):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CLOCK_DIAGNOSTIC357_SOURCE_STAGE_RESULTS_REVIEW_PASSED_V2'and value['verifiedPassed']is True
    assert value['sourceIndexSha256']==own['sha256']and value['actualStageResult']==actual and value['configuredSourceRoot']==str(SOURCE)
    assert value['stageCopies']==1583 and value['nativeSourceFiles']==357 and value['toolCopies']==1226 and value['externalEmbeddingSourcesCopied']==0 and value['externalEmbeddingReferenceSources']==3 and value['selectedWholeManifests']==11
    assert value['rawWorkerExitCode']==0 and value['allObservedOwnedGroupsGone']is True and value['currentOriginalsAndStageCopiesVerified']is True
    for k in ['nativeBuildExecuted','engineExecuted','guestExecuted','operationalAdmission','grantsNativeBuildAuthority']:assert value[k]is False

def authorize(config_row,phase):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
    assert clean_environment(dict(os.environ))[1]==[],'Clean inherited Bash startup controls BEFORE controller entry'
    cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='CLOCK_DIAGNOSTIC357_CONFIG_V2'and cfg['phase']==phase
    root=read(cfg['rootAuthority']);own=root['sourceIndex'];assert own==cfg['sourceIndex']
    own_rows=family(own);refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
    for key in ['controller','recipe','helper','policy','metadataModel','copyPlan','cachePlan','protectedInputs']:assert refs[key]in own_rows
    root_model(root,own,refs,phase)
    frame=dict(root=root,config=cfg,configRow=config_row,own=own,refs=refs,rows={},ids={},families=[own],staged=False)
    for r in [config_row,cfg['rootAuthority'],*own_rows]:capture(frame,r)
    peer,peer_rows=proof(root['sourceReview']);peer_model(peer,own)
    for r in peer_rows:capture(frame,r)
    frame['families'].append(root['sourceReview']['index'])
    for ix in refs['families']:
        for r in family(ix):capture(frame,r)
        frame['families'].append(ix)
    inputs=read(refs['protectedInputs'])
    for ledger in inputs['fileLedgers']:
        capture(frame,ledger)
        for r in read(ledger)['files']:capture(frame,r)
    capture(frame,inputs['frozenCopyInventory'])
    for r in read(inputs['frozenCopyInventory'])['files']:
        capture(frame,r['copy'])
        if r['original']is not None:capture(frame,r['original'])
        assert stat.S_IMODE(checked(r['copy']).stat().st_mode)==r['mode']
    for r in inputs['files']:capture(frame,r)
    for r in inputs['modeRows']:assert stat.S_IMODE(checked(r['file']).stat().st_mode)==r['mode']
    frame['inputModes']=inputs['modeRows']
    for r in inputs['aliases']:assert Path(r['path']).is_symlink()and os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve())==r['resolved']
    frame['aliases']=inputs['aliases']
    frame['hardlinks']=inputs['archiveHardlinks']
    for r in refs['hostTools']:
        assert str(Path(shutil.which(r['name'],path=refs['hostPath'])).resolve())==r['executable']['path']
        capture(frame,r['executable'])
    plan=read(refs['copyPlan'])['files'];assert len(plan)==len({safe(r['path'])for r in plan})==1583
    assert sum(r['role']=='native'for r in plan)==357 and sum(r['role']=='tool'for r in plan)==1226
    frame['plan']=plan
    if phase=='build':
        value,rows=proof(root['actualStageReview']);stage_review_model(value,own,root['actualStageResult'])
        for r in rows:capture(frame,r)
        frame['families'].append(root['actualStageReview']['index'])
        stage=read(root['actualStageResult']);assert stage['state']=='CLOCK_DIAGNOSTIC357_SOURCE_STAGED_NOT_BUILT_V2'and stage['sourceIndex']==own
        assert stage['copiesCompleted']==plan and stage['engineExecuted']is False
        assert stage['allSourceOriginalsPreserved']is stage['finalInputProtectionPassed']is stage['originalGitUnchanged']is stage['originalRepositoryIndexUnchanged']is True
        frame['stage']=stage;frame['staged']=True
        for r in plan:capture(frame,dict(path=str(SOURCE/r['path']),sha256=r['sha256'],bytes=r['bytes']))
        for key in ['stagedGitConfig','stagedGitHead','stagedGitShallow']:capture(frame,stage[key])
    assert checked(refs['pythonExecutable'])==Path(sys.executable).resolve()
    recheck(frame);return frame

def protect_modes_and_aliases(frame):
    for r in frame['inputModes']:assert stat.S_IMODE(checked(r['file']).stat().st_mode)==r['mode']
    for r in frame['aliases']:assert os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve())==r['resolved']
    for r in frame['hardlinks']:
        a=physical(r['path']).stat();b=physical(r['target']).stat()
        assert(a.st_dev,a.st_ino)==(b.st_dev,b.st_ino)

def absent(path):
    for p in(path,*path.parents):assert not p.is_symlink(),p
    assert not path.exists(),path

def fsync_dir(path):
    fd=os.open(str(path),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

def durable(path,data,mode=0o600):
    with Path(path).open('xb')as f:
        os.fchmod(f.fileno(),mode);assert f.write(data)==len(data);f.flush();os.fsync(f.fileno())
    fsync_dir(Path(path).parent);return descriptor(path)

def publish(path,value):return durable(path,(json.dumps(value,indent=2)+'\n').encode())

def copy_regular(origin,target,mode):
    source=checked(origin);before=source.stat();assert stat.S_IMODE(before.st_mode)==mode
    absent(target);target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    for p in(target.parent,*target.parent.parents):assert not p.is_symlink(),p
    with source.open('rb')as src,target.open('xb')as out:
        os.fchmod(out.fileno(),mode)
        for b in iter(lambda:src.read(1024**2),b''):assert out.write(b)==len(b)
        out.flush();os.fsync(out.fileno())
    fsync_dir(target.parent);actual=descriptor(target);after=source.stat();s=target.stat()
    assert identity(before)==identity(after)and(actual['sha256'],actual['bytes'])==(origin['sha256'],origin['bytes'])
    assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==mode and(s.st_dev,s.st_ino)!=(before.st_dev,before.st_ino)
    return actual

def parse_index(raw):
    assert raw[:4]==b'DIRC'and len(raw)>=32 and hashlib.sha1(raw[:-20]).digest()==raw[-20:]
    version,count=struct.unpack('>II',raw[4:12]);assert version==2 and count==742
    pos=12;rows=[];stats=[]
    for _ in range(count):
        start=pos;fields=struct.unpack('>10I',raw[pos:pos+40]);oid=raw[pos+40:pos+60].hex();flags=struct.unpack('>H',raw[pos+60:pos+62])[0]
        end=raw.index(b'\0',pos+62);name=raw[pos+62:end].decode('utf-8','strict');safe(name)
        assert flags&0x3000==0 and flags&0x4000==0
        assert flags==min(len(name.encode()),0xfff)
        assert fields[6]in(0o100644,0o100755,0o120000)
        pos=start+((end+1-start+7)//8)*8;assert raw[end:pos]==b'\0'*(pos-end)
        rows.append(dict(path=name,mode=fields[6],oid=oid,flags=flags));stats.append(list(fields))
    assert len({r['path']for r in rows})==742 and rows==sorted(rows,key=lambda r:r['path'].encode())
    return dict(version=version,entries=rows,extensionsHex=raw[pos:-20].hex(),statFields=stats)

def index_observation(path):
    path=physical(path);s=path.stat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1
    raw=path.read_bytes();assert identity(s)==identity(path.stat())
    return dict(file=descriptor(path),mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,links=s.st_nlink,parsed=parse_index(raw))

def index_stat_only(before,after):
    assert before['mode']==after['mode']and before['device']==after['device']and before['links']==after['links']==1
    a=before['parsed'];b=after['parsed']
    assert a['version']==b['version']==2 and a['entries']==b['entries']and a['extensionsHex']==b['extensionsHex']
    assert before['file']['bytes']==after['file']['bytes']
    return dict(semanticsAndFlagsExtensionsUnchanged=True,statCacheBytesChanged=before['file']['sha256']!=after['file']['sha256'],originalRawBytesPreserved=before['file']['sha256']==after['file']['sha256'],originalIndexInodePreserved=before['inode']==after['inode'],indexModePreserved=True,baselineEntries=742)

def git_policy():
    root=STAGE_OUT/'git-policy'
    return dict(templateRoot=str(root/'empty-template'),hooksRoot=str(root/'disabled-hooks'),cwd=str(root),clientConfig=[['core.hooksPath',str(root/'disabled-hooks')],['core.fsmonitor','false'],['core.attributesFile','/dev/null'],['core.excludesFile','/dev/null'],['index.version','2'],['gc.auto','0'],['gc.autoDetach','false'],['maintenance.auto','false'],['maintenance.autoDetach','false'],['fetch.writeCommitGraph','false'],['submodule.recurse','false'],['protocol.allow','never'],['protocol.file.allow','always'],['init.defaultRefFormat','files']])

def git_prefix(git):
    out=[git,'--no-replace-objects']
    for k,v in git_policy()['clientConfig']:out+=['-c',k+'='+v]
    return out

def git_environment(original):
    env,removed=clean_environment(original);env={k:v for k,v in env.items()if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_CONFIG_COUNT='0',GIT_TERMINAL_PROMPT='0',GIT_OPTIONAL_LOCKS='0',GIT_NO_REPLACE_OBJECTS='1')
    return env

def git_commands(git):
    prefix=git_prefix(git);server=shlex.join(prefix+['-c','uploadpack.allowAnySHA1InWant=true','upload-pack'])
    return [prefix+['init','--template='+git_policy()['templateRoot'],'--object-format=sha1','--initial-branch=stage-baseline',str(SOURCE)],prefix+['-C',str(SOURCE),'fetch','--no-tags','--depth=1','--no-recurse-submodules','--no-auto-maintenance','--no-write-commit-graph','--upload-pack='+server,REPO.as_uri(),BASE],prefix+['-C',str(SOURCE),'checkout','--detach',BASE],prefix+['-C',str(SOURCE),'ls-tree','-r','-z','--full-tree',BASE],prefix+['-C',str(SOURCE),'rev-list','--count','HEAD']]

def git_inventory(root):
    rows=[]
    for p in sorted((root/'.git/objects').rglob('*')):
        assert not p.is_symlink()
        if p.is_file():s=p.stat();rows.append(dict(file=descriptor(p),mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,links=s.st_nlink))
    return rows

def command(argv,folder):
    absent(folder);folder.mkdir(mode=0o700);record=dict(argv=argv,cwd=git_policy()['cwd'],timeoutSeconds=120,returncode=None,timedOut=False);out=err=b''
    try:
        r=subprocess.run(argv,cwd=record['cwd'],env=git_environment(dict(os.environ)),capture_output=True,timeout=120);record['returncode']=r.returncode;out=r.stdout;err=r.stderr
    except subprocess.TimeoutExpired as e:out=e.stdout or b'';err=e.stderr or b'';record['timedOut']=True
    finally:
        record['stdout']=durable(folder/'stdout.log',out);record['stderr']=durable(folder/'stderr.log',err)
        record['terminal']=publish(folder/'terminal.json',record)
    return record

def parse_tree(raw):
    rows={}
    for part in raw.split(b'\0'):
        if not part:continue
        left,name=part.split(b'\t',1);mode,kind,oid=left.decode().split();name=name.decode();safe(name)
        assert kind=='blob'and name not in rows;rows[name]=dict(mode=int(mode,8),oid=oid)
    assert len(rows)==742;return rows

def baseline_tree_files(tree):
    links={};observed=[]
    for name,item in tree.items():
        p=SOURCE/name;s=p.lstat()
        if item['mode']==0o120000:
            assert name in DOCUMENT_LINKS and p.is_symlink()
            text=os.readlink(p);assert text==DOCUMENT_LINKS[name];data=text.encode();links[name]=text
        else:
            assert item['mode']in(0o100644,0o100755)and stat.S_ISREG(s.st_mode)and s.st_nlink==1
            # Git's tracked mode records the executable bit, not the caller's
            # private umask. Capture actual checkout modes without pretending644.
            mode=stat.S_IMODE(s.st_mode);assert mode in((0o700,0o755)if item['mode']==0o100755 else(0o600,0o644))
            data=p.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['oid']
        observed.append(dict(path=name,git=item,actualMode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino))
    assert links==DOCUMENT_LINKS;return observed

def stage_worker(frame):
    for p in [SOURCE,WORK,FREEZE,JOURNAL]:absent(p)
    assert STAGE_OUT.is_dir();os.umask(0o077)
    result=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_SOURCE_STAGE_STARTED_V2',sourceIndex=frame['own'],rootAuthority=frame['config']['rootAuthority'],config=frame['configRow'],configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),baselineRevision=BASE,commands=[],copiesCompleted=[],engineExecuted=False,guestExecuted=False,operationalAdmission=False)
    original_git=git_inventory(REPO);source_ids={(r['device'],r['inode'])for r in original_git}
    original_index=descriptor(REPO/'.git/index')
    original_mode=stat.S_IMODE((REPO/'.git/index').stat().st_mode)
    result['originalRepositoryIndexBeforeGit']=dict(file=original_index,mode=original_mode)
    result['originalRepositoryIndexPreimage']=durable(STAGE_OUT/'original-repository-index-before-git.bin',(REPO/'.git/index').read_bytes())
    try:
        assert shutil.disk_usage(SOURCE.parent).free>=START_FREE
        policy=git_policy();Path(policy['cwd']).mkdir(mode=0o700)
        for k in ['templateRoot','hooksRoot']:Path(policy[k]).mkdir(mode=0o700)
        for argv in git_commands(frame['refs']['git']['path']):
            r=command(argv,STAGE_OUT/('git-'+str(len(result['commands']))));result['commands'].append(r);assert r['returncode']==0 and not r['timedOut']
        assert checked(result['commands'][-1]['stdout']).read_text()=='1\n'
        assert(SOURCE/'.git/HEAD').read_text()==BASE+'\n'and not(SOURCE/'.git/objects/info/alternates').exists()
        SOURCE.chmod(0o700);tree=parse_tree(checked(result['commands'][3]['stdout']).read_bytes())
        result['baselineTreeFilesBeforeOverlay']=baseline_tree_files(tree)
        before=index_observation(SOURCE/'.git/index');assert {r['path']:(r['mode'],r['oid'])for r in before['parsed']['entries']}=={p:(r['mode'],r['oid'])for p,r in tree.items()}
        result['gitIndexBeforeOverlay']=before;result['gitIndexPreimage']=durable(STAGE_OUT/'git-index-before-overlay.bin',(SOURCE/'.git/index').read_bytes())
        result['baselineOverlayPreimages']=[]
        for r in frame['plan']:
            target=SOURCE/r['path'];item=tree.get(r['path'])
            for p in(target,*target.parents):assert not p.is_symlink(),p
            if item:
                assert target.is_file();raw=target.read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['oid']
                mode=stat.S_IMODE(target.stat().st_mode);assert mode in((0o700,0o755)if item['mode']==0o100755 else(0o600,0o644))
                result['baselineOverlayPreimages'].append(dict(path=r['path'],git=item,actual=descriptor(target),actualMode=mode));target.unlink()
            else:absent(target)
            copy_regular(r['origin'],target,r['mode']);result['copiesCompleted'].append(r)
        result['gitIndexAfterOverlay']=index_observation(SOURCE/'.git/index');index_stat_only(before,result['gitIndexAfterOverlay'])
        objects=git_inventory(SOURCE);assert all(r['links']==1 for r in objects)and not source_ids&{(r['device'],r['inode'])for r in objects}
        result['stagedGitObjects']=objects;result['stagedGitConfig']=descriptor(SOURCE/'.git/config');result['stagedGitHead']=descriptor(SOURCE/'.git/HEAD');result['stagedGitShallow']=descriptor(SOURCE/'.git/shallow')
        assert checked(result['stagedGitShallow']).read_text()==BASE+'\n'
        result['baselineHistory']='One reachable BASE only; transient pack bytes are not capped; no source-repo config mutation'
        assert git_inventory(REPO)==original_git
        assert descriptor(REPO/'.git/index')==original_index and stat.S_IMODE((REPO/'.git/index').stat().st_mode)==original_mode
        recheck(frame);protect_modes_and_aliases(frame)
        result.update(state='CLOCK_DIAGNOSTIC357_SOURCE_STAGED_NOT_BUILT_V2',allSourceOriginalsPreserved=True,stageCopies=1583,nativeSources=357,toolCopies=1226,embeddingSourcesCopied=0,embeddingReferenceSources=3)
    except BaseException as e:result.update(state='CLOCK_DIAGNOSTIC357_SOURCE_STAGE_FAILED_V2',error=dict(type=type(e).__name__,message=str(e)));raise
    finally:
        result['originalGitUnchanged']=git_inventory(REPO)==original_git
        result['originalRepositoryIndexUnchanged']=descriptor(REPO/'.git/index')==original_index and stat.S_IMODE((REPO/'.git/index').stat().st_mode)==original_mode
        try:recheck(frame);protect_modes_and_aliases(frame);result['finalInputProtectionPassed']=True
        except BaseException as e:result['finalInputProtectionPassed']=False;result['finalInputError']=dict(type=type(e).__name__,message=str(e))
        publish(JOURNAL,result)
    assert result['state']=='CLOCK_DIAGNOSTIC357_SOURCE_STAGED_NOT_BUILT_V2'and result['finalInputProtectionPassed']is result['originalGitUnchanged']is result['originalRepositoryIndexUnchanged']is True
    return result

def build_environment(original,refs):
    clean,removed=clean_environment(original);assert not removed
    prefixes=('NODE_COMPAT_','STARLINGMONKEY_','COMPONENTIZE_','CPM_','CMAKE_','CORROSION_','RUST','CARGO_','GIT_')
    env={k:v for k,v in clean.items()if not k.startswith(prefixes)and k not in ['CC','CXX','AR','RANLIB','LD','CFLAGS','CXXFLAGS','CPPFLAGS','LDFLAGS','SPIDERMONKEY_BINARIES','HOST_API','BINARYEN_CORES','RAYON_NUM_THREADS','WEVAL','NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH']and not k.startswith('DYLD_')}
    env.update(refs['buildEnvironment']);env.update(git_environment({k:v for k,v in env.items()if k.startswith('GIT_')}))
    for k in ENV_POLICY['preserveExactNames']:assert env.get(k)==original.get(k)and(k in env)==(k in original)
    return env

def validate_build_record(value,policy,refs):
    assert len(value)==82 and value['enginePath']==str(WORK/'artifacts'/refs['artifactBasename'])
    assert value['buildRecipeSha256']==refs['recipe']['sha256']and value['sourceManifest']==policy['expectedNativeSourceManifest']
    assert value['componentizeSourceManifest']==policy['expectedComponentizeSourceManifest']and len(value['selectedModuleManifests'])==11
    assert value['privateRustupBootstrapPolicy']['persistentSetting']=='disable'
    assert value['privateRustupBootstrapPolicy']['privateHomes']==dict(rustup=str(WORK/'rustup-home'),cargo=str(WORK/'cargo-home'))
    checked(value['privateRustupBootstrapPolicy']['beforeInstallRecord']);checked(value['privateRustupBootstrapPolicy']['settingsAtBuildCompletion'])
    sdk=[r for r in value['downloadedArchives']if Path(r['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz']
    assert len(sdk)==1 and sdk[0]['sha256']==refs['sdkArchive']['sha256']
    checked(dict(path=sdk[0]['path'],sha256=sdk[0]['sha256'],bytes=refs['sdkArchive']['bytes']))
    assert value['wasiSdkVersionFiles']and all(r['contents'].startswith('30.0\n')for r in value['wasiSdkVersionFiles'])
    assert value['requestedCMakeOptions']==value['observedCMakeOptions']and value['generatedRustProject']['cargoBuildLocked']is True
    assert value['zlibPolicy']['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)

def build_worker(frame):
    for p in [WORK,FREEZE,BUILD_RESULT]:absent(p)
    os.umask(0o077);refs=frame['refs'];recheck(frame)
    lifecycle=load_actual(refs['lifecycleEntry'],'genuine_clock357_explicit_build_lifecycle')
    assert lifecycle.REQUIRED_START_FREE==START_FREE and lifecycle.MINIMUM_FREE==STOP_FREE
    def free():
        p=WORK if WORK.exists()else WORK.parent;s=os.statvfs(p);return s.f_bavail*s.f_frsize
    before=lifecycle.prepare_output(BUILD_RESULT,free)
    result=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_NORMAL_OFF_NATIVE_BUILD_STARTED_V2',sourceIndex=frame['own'],rootAuthority=frame['config']['rootAuthority'],config=frame['configRow'],actualStageReview=frame['root']['actualStageReview'],actualStageResult=frame['root']['actualStageResult'],configuredSourceRoot=str(SOURCE),workRoot=str(WORK),rawMetadataFields=82,nativeSourceFiles=357,externalEmbeddingSources=3,selectedWholeManifests=11,freeBytesBefore=before,requiredStartFreeBytes=START_FREE,stopBelowFreeBytes=STOP_FREE,externalParentDeadlineSeconds=7200,cacheCopiesCompleted=[],rawChildExitCode=None,engineExecuted=False,guestExecuted=False,clockRuntimeInvoked=False,operationalAdmission=False)
    publish(BUILD_RESULT/'launch.json',result)
    try:
        WORK.mkdir(mode=0o700)
        for r in read(refs['cachePlan'])['copies']:
            assert free()>=START_FREE
            target=copy_regular(r['source'],WORK/safe(r['target']),r['outputMode']);result['cacheCopiesCompleted'].append(dict(source=r['source'],target=target,mode=r['outputMode']))
        for name in ['rustup-home','cargo-home']:(WORK/name).mkdir(mode=0o700)
        assert free()>=START_FREE
        before=index_observation(SOURCE/'.git/index');result['gitIndexBeforeRecipe']=before
        result['gitIndexPreimage']=durable(BUILD_RESULT/'git-index-before-recipe.bin',(SOURCE/'.git/index').read_bytes())
        env=build_environment(dict(os.environ),refs);result['explicitBuildEnvironment']=refs['buildEnvironment']
        with(BUILD_RESULT/'build.log').open('xb')as log:
            result.update(lifecycle.monitor_owned_command([refs['bash']['path'],refs['recipe']['path']],str(SOURCE),env,log,free));log.flush();os.fsync(log.fileno())
        result['gitIndexAfterRecipe']=index_observation(SOURCE/'.git/index');result['gitIndexComparison']=index_stat_only(before,result['gitIndexAfterRecipe'])
        if result['rawChildExitCode']==0:
            engine=WORK/'artifacts'/refs['artifactBasename'];metadata=Path(str(engine)+'.build.json')
            value=read(descriptor(metadata));spec=read(refs['policy']);base=read(spec['basePolicy'])
            model=load_actual(refs['metadataModel'],'genuine_clock357_exact82_model');policy=model.assemble_policy(spec,base)
            validate_build_record(value,policy,refs)
            result['metadataClassification']=model.validate_metadata(value,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
            result['engine']=descriptor(engine);result['metadata']=descriptor(metadata)
    except BaseException as e:result.setdefault('launcherErrors',[]).append(lifecycle.error_record('build-cache-or-metadata',e))
    finally:
        result['freeBytesAfter']=free()
        if(BUILD_RESULT/'build.log').exists():result['buildLog']=descriptor(BUILD_RESULT/'build.log')
        try:recheck(frame);protect_modes_and_aliases(frame);result['allSourceStageOriginalAndCacheInputsPreserved']=True
        except BaseException as e:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('protection',e))
        lifecycle.finalize_status(result);lifecycle.publish_result(BUILD_RESULT,result,writer=lambda p,v:publish(p,v))
    assert result['launcherExitCode']==0;return result

def parent(frame,phase):
    out=STAGE_OUT if phase=='stage'else BUILD_OUT
    absent(out);out.mkdir(mode=0o700)
    monitor=load_actual(frame['refs']['monitorEntry'],'genuine_clock357_owned_monitor')
    argv=[frame['refs']['pythonExecutable']['path'],'-B','-I',str(OWN/'controller.py'),phase+'-worker',json.dumps(frame['configRow'],separators=(',',':'))]
    recheck(frame);protect_modes_and_aliases(frame)
    try:terminal=monitor.monitor(argv,str(REPO),dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),out,600 if phase=='stage'else 7200,frame['config']['rootAuthority'])
    finally:recheck(frame);protect_modes_and_aliases(frame)
    assert terminal['authority']==frame['config']['rootAuthority']and terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is terminal['parentOwnedGroupGone']is True
    assert not terminal['forcedCleanup']and not terminal['timeout']and terminal['signals']==terminal['errors']==terminal['remainingObservedPids']==[]
    actual=descriptor(JOURNAL if phase=='stage'else BUILD_RESULT/'result.json')
    print(json.dumps(dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_PHASE_RAW_ZERO_UNREVIEWED_V2',phase=phase,actualResult=actual,externalParentTerminal=descriptor(out/'terminal.json'),engineExecuted=False,independentActualReviewRequired=True)),flush=True)

def main():
    assert len(sys.argv)==3 and sys.argv[1]in('stage-parent','stage-worker','build-parent','build-worker')
    phase,role=sys.argv[1].split('-');frame=authorize(json.loads(sys.argv[2]),phase)
    try:
        if role=='parent':parent(frame,phase)
        elif phase=='stage':stage_worker(frame)
        else:build_worker(frame)
    finally:recheck(frame);protect_modes_and_aliases(frame)
if __name__=='__main__':main()
