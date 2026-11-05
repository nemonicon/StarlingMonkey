"""Dormant Root-only issuer/outer observer for reviewed v3 normal-OFF export."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE/'ownership-secret-artifact-tooling-candidate-v3'
MONITOR = HERE/'ownership-gc-build-controller-candidate-v1'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3-export-normal-off')
EXTERNAL = Path(str(OUT)+'-external-root')
OBSERVER = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3-export-root-observer')


def row(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(4*1024*1024),b''):
            digest.update(data)
    after = path.stat()
    identity = lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert identity(before)==identity(after)
    return dict(path=str(path),sha256=digest.hexdigest(),bytes=after.st_size)


def read(value):
    assert row(value['path']) == value
    return json.loads(Path(value['path']).read_bytes())


def family(index, expected=None):
    if expected is not None:
        assert index['sha256']==expected
    value=read(index)
    base=Path(index['path']).parent
    names={'index.json'}
    for item in value['files']:
        name=item['path']
        assert name not in names and not Path(name).is_absolute() and '..'not in Path(name).parts
        names.add(name)
        assert row(base/name)==dict(item,path=str(base/name))
    assert not any(path.is_symlink()for path in base.rglob('*'))
    assert {str(path.relative_to(base))for path in base.rglob('*')if path.is_file()}==names
    return value


def save(path,value):
    with path.open('x')as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row(path)


def authenticate(peer):
    source=row(SOURCE/'index.json')
    family(source,'d62b235c0c397ff3b91e098691e3bbe137e761beaf7cd513b132fad7474c52a2')
    index=family(peer['index'])
    assert peer['result']in [dict(item,path=str(Path(peer['index']['path']).parent/item['path']))for item in index['files']]
    value=read(peer['result'])
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V3'
    assert value['toolingSourceIndexSha256']==source['sha256'] and value['sourceOnly']is value['sourceReviewPassed']is True
    assert value['verifierSourceIndexSha256']=='e8726a1c416afc48303faa1fd25dabed6a71872d6a65ae5ac438e2685aceb7ad'
    assert value['nativeSourceIndexSha256']=='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
    for key in ('ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked'):
        assert value[key]is False
    family(row(MONITOR/'index.json'),'0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    return source


def issue(peer):
    source=authenticate(peer)
    for path in (OUT,EXTERNAL,OBSERVER):
        assert not path.exists() and not path.is_symlink()
    root=read(row(SOURCE/'future-root-authority.template.json'))
    assert root['schemaVersion']==3 and root['state']is root['phase']is root['toolingIndex']is None
    assert root['exportAllowed']is root['bootstrapAllowed']is False
    root.update(state='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V3',phase='export',toolingIndex=source,
        sourceIndependentReview=peer,outputRoot=str(OUT),externalOutputRoot=str(EXTERNAL),jsOutputRoot=None,
        exportAllowed=True,rootOuterController=row(Path(__file__).resolve()),rootOuterDeadlineSeconds=1800,
        rootObserverOutput=str(OBSERVER),issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    authority=save(HERE/'ownership-secret-artifact-export-v3-root-authority.json',root)
    config=read(row(SOURCE/'future-config.template.json'))
    config.update(state='SECRET_OWNER355_ARTIFACT_TOOLING_CONFIG_V3',phase='export',toolingIndex=source,rootAuthority=authority)
    print(json.dumps(save(HERE/'ownership-secret-artifact-export-v3-root-config.json',config)))


def run(config_descriptor):
    config=read(config_descriptor)
    root=read(config['rootAuthority'])
    source=authenticate(root['sourceIndependentReview'])
    assert root['rootOuterController']==row(Path(__file__).resolve()) and config['toolingIndex']==source
    assert root['phase']==config['phase']=='export' and root['exportAllowed']is True and root['bootstrapAllowed']is False
    for path in (OUT,EXTERNAL,OBSERVER):
        assert not path.exists() and not path.is_symlink()
    refs=read(row(SOURCE/'references.json'))
    assert row(refs['python']['path'])==refs['python']
    spec=importlib.util.spec_from_file_location('genuine_original_secret355_export_outer_monitor',MONITOR/'monitor.py')
    monitor=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    os.umask(0o077)
    OBSERVER.mkdir(mode=0o700)
    argv=[refs['python']['path'],'-B','-I',str(SOURCE/'artifact_tooling.py'),'parent','export','--config-descriptor',json.dumps(config_descriptor,separators=(',',':'))]
    terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OBSERVER,1800,config['rootAuthority'])
    assert read(row(OBSERVER/'terminal.json'))==terminal
    authenticate(root['sourceIndependentReview'])
    for key in ('stdout','stderr'):
        assert row(terminal[key]['path'])==terminal[key]
    clean=(terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True
        and terminal['timeout']is terminal['forcedCleanup']is False and terminal['signals']==[] and terminal['errors']==[]
        and terminal['interruptedSignals']==[] and terminal['remainingObservedPids']==[])
    result=dict(schemaVersion=3,state='ROOT_OBSERVED_SECRET355_ARTIFACT_EXPORT_PARENT_ZERO_UNREVIEWED_V3'if clean else'ROOT_OBSERVED_SECRET355_ARTIFACT_EXPORT_FAILED_UNACCEPTED_V3',
        toolingIndex=source,sourceReview=root['sourceIndependentReview'],rootAuthority=config['rootAuthority'],config=config_descriptor,
        rawTerminal=row(OBSERVER/'terminal.json'),rawStdout=terminal['stdout'],rawStderr=terminal['stderr'],rawParentExitCode=terminal['rawExitCode'],
        cleanOwnedCleanup=clean,independentExportReview=None,reviewedPins=None,actualBootstrap=None,engineExecuted=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False)
    print(json.dumps(save(OBSERVER/'root-observation.json',result)))
    return 0 if clean else 1


if __name__=='__main__':
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert len(sys.argv)==3 and sys.argv[1]in ('issue','run')
    if sys.argv[1]=='issue':
        issue(json.loads(sys.argv[2]))
    else:
        raise SystemExit(run(json.loads(sys.argv[2])))
