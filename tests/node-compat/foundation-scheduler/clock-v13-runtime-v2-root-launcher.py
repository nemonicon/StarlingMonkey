"""Root observer for two separately authorized selected-clock test phases.

The reviewed candidate's external controller owns process deadlines and final
source/native/package checks. This observer retains its actual raw return.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
SOURCE=S/'clock-v13-runtime-candidate-v2'
PEER=S/'independent-clock-v13-runtime-v2-source-review-v1'
PYTHON='/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
def descriptor(path):
    path=Path(path);data=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def write(path,value):
    with Path(path).open('x') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
    assert sys.argv[1:] in [['map'],['runtime']]
    mapping=sys.argv[1]=='map';name='map' if mapping else 'runtime'
    own=descriptor(SOURCE/'index.json')
    assert own['sha256']=='135d1e45ea4214a99e2a835cfab0b212c92519ea6600a7c802336e7a323be384'
    proof=json.loads((PEER/'results.json').read_bytes())
    assert proof['state']=='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V2'
    assert proof['sourceIndexSha256']==own['sha256'] and proof['sourceOnly'] is proof['sourceReviewPassed'] is True
    assert proof['ownerActionsInvoked'] is proof['hostActionsInvoked'] is proof['runtimeActionsInvoked'] is False
    refs=json.loads((SOURCE/'references.json').read_bytes())
    root=json.loads((SOURCE/'future-root-authority.template.json').read_bytes())
    root.update(state='ROOT_REVIEWED_CLOCK_V13_REACTDOM_DIFFERENTIAL_V2',phase='mapped-transpile' if mapping else 'runtime-differential',sourceIndex=own,entry=descriptor(SOURCE/'entry.mjs'),externalController=descriptor(SOURCE/'external.py'),sourceIndependentReview=dict(index=descriptor(PEER/'index.json'),result=descriptor(PEER/'results.json')),outputRoot=refs['mappedOutputRoot'] if mapping else refs['runtimeOutputRoot'],mappedTranspileAllowed=mapping,jcoCompilerWasmHelpersAllowed=mapping,generatedApplicationImportAllowed=not mapping,ordinaryRunAllowed=not mapping,stockWasmtimeAllowed=not mapping,nativeReadOnlyPreflightAllowed=True,standardShimWorkerThreadsAllowed=True)
    root['externalOutputRoot']=root['outputRoot']+'-external-root'
    if not mapping:
        review=S/'clock-v13-mapped-output-v2-root-review.json'
        actual=json.loads(review.read_bytes());assert actual['state']=='ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V2' and actual['verifiedPassed'] is True
        root['actualMappedOutputReview']=descriptor(review)
    for path in [Path(root['outputRoot']),Path(root['externalOutputRoot'])]:assert not path.exists() and not path.is_symlink()
    prefix=S/('clock-v13-'+name+'-v2-root')
    authority=Path(str(prefix)+'-authority.json');write(authority,root)
    config=json.loads((SOURCE/'future-config.template.json').read_bytes());config.update(sourceIndex=own,rootAuthority=descriptor(authority))
    config_path=Path(str(prefix)+'-config.json');write(config_path,config)
    argv=[PYTHON,'-B','-I',str(SOURCE/'external.py'),json.dumps(descriptor(config_path),separators=(',',':'))]
    invocation=Path(str(prefix)+'-invocation.json')
    write(invocation,dict(schemaVersion=1,sourceIndex=own,sourcePeer=root['sourceIndependentReview'],rootAuthority=descriptor(authority),rootConfig=descriptor(config_path),rootLauncher=descriptor(Path(__file__).resolve()),entry=descriptor(SOURCE/'external.py'),python=descriptor(PYTHON),actualArgv=argv,externalParentDeadlineSeconds=1200,mappingOnly=mapping,ordinaryApplicationExportAllowed=not mapping,fullClockProfileAcceptance=False))
    out=Path(root['outputRoot']+'-root-caller');out.mkdir(mode=0o700)
    env={k:os.environ[k] for k in ['HOME','USER','LOGNAME','TMPDIR'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin',PYTHONDONTWRITEBYTECODE='1')
    write(out/'environment-policy.json',dict(schemaVersion=1,keys=sorted(env),valuesRetained=False,requiredNativeReadOnlyEnvironmentSetByReviewedExternalController=True))
    print(json.dumps(dict(event='clock-root-launch',phase=root['phase'],invocation=descriptor(invocation))),flush=True)
    with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
        result=subprocess.run(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr)
    write(out/'root-tool-child-return.json',dict(schemaVersion=1,rawExitCode=result.returncode))
    print(json.dumps(dict(event='clock-root-terminal',rawExitCode=result.returncode,stdout=descriptor(out/'stdout.log'),stderr=descriptor(out/'stderr.log'))),flush=True)
    raise SystemExit(result.returncode)
if __name__=='__main__':main()
