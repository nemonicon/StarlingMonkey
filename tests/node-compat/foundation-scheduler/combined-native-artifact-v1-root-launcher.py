"""Root observer for separately issued combined355 export/bootstrap phases.

The candidate controller owns the 600-second worker monitor. The original
owned monitor bounds the whole parent at 1,200 seconds, including its input
checks. Both layers retain complete streams; neither invokes an engine/guest.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
SOURCE=S/'combined-native-artifact-tooling-candidate-v1'
PEER=S/'independent-combined355-native-artifact-tooling-source-review-v1'
BASE=Path('/private/tmp/starling-node-compat/combined-native355-artifact-tooling-v1')
PYTHON=Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
SOURCE_SHA='c365e6089688f62f028580e86b14db80bb434ba7b4ac45ae341e851c11913a7b'
def descriptor(path):
    path=Path(path);assert path.is_file() and not path.is_symlink()
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)
def write(path,value):
    with Path(path).open('x') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def family(path):
    path=Path(path);index=json.loads(path.read_bytes());names={'index.json'}
    for row in index['files']:
        name=row['path'];assert name and not name.startswith('/') and '\\' not in name and all(v not in ('','.','..') for v in name.split('/')) and name not in names
        names.add(name);actual=descriptor(path.parent/name)
        assert actual['sha256']==row['sha256'] and actual['bytes']==row['bytes']
    assert not any(p.is_symlink() for p in path.parent.rglob('*'))
    assert {p.relative_to(path.parent).as_posix() for p in path.parent.rglob('*') if p.is_file()}==names
    return descriptor(path)
def main():
    assert len(sys.argv)==2 and sys.argv[1] in ('export','bootstrap')
    phase=sys.argv[1];own=family(SOURCE/'index.json');assert own['sha256']==SOURCE_SHA
    proof_index=family(PEER/'index.json');proof=json.loads((PEER/'results.json').read_bytes())
    contract=json.loads((SOURCE/'future-source-review-contract.json').read_bytes())
    assert proof['state']==contract['requiredState'] and proof['toolingSourceIndexSha256']==SOURCE_SHA
    for key,value in contract['requiredFixedValues'].items():assert type(proof[key]) is type(value) and proof[key]==value
    refs=json.loads((SOURCE/'references.json').read_bytes())
    monitor_index=family(Path(refs['monitorIndex']['path']));assert monitor_index==refs['monitorIndex']
    assert descriptor(refs['monitorEntry']['path'])==refs['monitorEntry']
    root=json.loads((SOURCE/'future-root-authority.template.json').read_bytes());root.pop('requiredIssuedState')
    out=Path(str(BASE)+'-'+phase+'-normal-off');external=Path(str(out)+'-external-root');caller=Path(str(out)+'-root-caller')
    for path in (out,external,caller):assert not path.exists() and not path.is_symlink()
    root.update(state='ROOT_REVIEWED_COMBINED355_NATIVE_ARTIFACT_PHASE_V1',phase=phase,toolingIndex=own,sourceIndependentReview=dict(index=proof_index,result=descriptor(PEER/'results.json')),exportAllowed=phase=='export',bootstrapAllowed=phase=='bootstrap',frozenReadOnlyVerifierAllowed=True,outputRoot=str(out),externalOutputRoot=str(external))
    if phase=='bootstrap':
        inputs=json.loads((S/'combined-native355-artifact-v1-bootstrap-inputs.json').read_bytes())
        assert set(inputs)=={'actualExportCandidate','independentExportReview','reviewedPins','rootPinReview'}
        root.update(inputs)
    prefix=S/('combined-native355-artifact-v1-'+phase+'-root')
    authority=Path(str(prefix)+'-authority.json');write(authority,root)
    config=json.loads((SOURCE/'future-config.template.json').read_bytes());config.update(phase=phase,toolingIndex=own,rootAuthority=descriptor(authority))
    config_path=Path(str(prefix)+'-config.json');write(config_path,config)
    argv=[str(PYTHON),'-B','-I',str(SOURCE/'artifact_tooling.py'),'parent',phase,'--config-descriptor',json.dumps(descriptor(config_path),separators=(',',':'))]
    invocation=Path(str(prefix)+'-invocation.json')
    write(invocation,dict(schemaVersion=1,phase=phase,toolingIndex=own,sourcePeer=root['sourceIndependentReview'],rootAuthority=descriptor(authority),rootConfig=descriptor(config_path),rootLauncher=descriptor(Path(__file__).resolve()),python=descriptor(PYTHON),entry=descriptor(SOURCE/'artifact_tooling.py'),actualArgv=argv,ownedWorkerDeadlineSeconds=600,observerHasSeparateHardDeadline=True,outerParentDeadlineSeconds=1200,engineOrGuestExecutionAllowed=False,operationalAdmission=False))
    caller.mkdir(mode=0o700)
    env={k:os.environ[k] for k in ['HOME','USER','LOGNAME','TMPDIR'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin',PYTHONDONTWRITEBYTECODE='1')
    write(caller/'environment-policy.json',dict(schemaVersion=1,keys=sorted(env),valuesRetained=False))
    print(json.dumps(dict(event='combined-native-root-launch',phase=phase,invocation=descriptor(invocation))),flush=True)
    assert descriptor(refs['monitorEntry']['path'])==refs['monitorEntry']
    spec=importlib.util.spec_from_file_location('genuine0af_root_combined_artifact_monitor',refs['monitorEntry']['path']);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    terminal=monitor.monitor(argv,str(REPO),env,caller,1200,descriptor(authority))
    write(caller/'root-child-return.json',dict(schemaVersion=1,rawExitCode=terminal['rawExitCode'],terminal=descriptor(caller/'terminal.json')))
    clean=terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False and all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
    print(json.dumps(dict(event='combined-native-root-terminal',phase=phase,rawExitCode=terminal['rawExitCode'],outerTerminal=descriptor(caller/'terminal.json'),stdout=descriptor(caller/'stdout.log'),stderr=descriptor(caller/'stderr.log'),outerCleanupPassed=clean)),flush=True)
    raise SystemExit(0 if clean else 1)
if __name__=='__main__':main()
