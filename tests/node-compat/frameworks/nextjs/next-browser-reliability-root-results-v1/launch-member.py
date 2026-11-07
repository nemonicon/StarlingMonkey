"""Launch exactly one Root-predeclared member; never advance or retry a cohort."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
FRAMEWORK=HERE.parent
REPO=FRAMEWORK.parents[3]
PYTHON='/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
MINIMUM=1073741824
ORDER=['p1-stock','p1-native','p2-native','p2-stock','p3-stock','p3-native']
STOCK=FRAMEWORK/'browser-hydration-matched-host-candidate-v4'
NATIVE=FRAMEWORK/'wasmtime-deployment-candidate-v7'
WRAPPER=FRAMEWORK/'next-app-runtime-root-results-v1/run-full-next-fresh-app.py'
PINS={
 str(STOCK/'index.json'):('1770abb8a4512cf07fe3cf12bffd268731784c19ca7b317e489754df301ea8ac',3890),
 str(STOCK/'plans.json'):('aa171870985ce79810f6d0dd71bf15bf4e7b71b1ec104ebfad51b645ba5f8148',18893),
 str(STOCK/'run-owned.py'):('595d286fde1f98d59305b7403e6c3a63b4a786ccff82c8cbc0229b569ceb4965',4846),
 str(NATIVE/'index.json'):('bd7856486ae75aeb3c44b12670cc54dc22c958f285faf96e3b6ba55f3917caf2',3720),
 str(NATIVE/'plan.json'):('122e269f138281202a76e5f1e6004bbf332108d131874ae22208bb6e1f4569b2',14507),
 str(WRAPPER):('62ec251cdea390c0d05397be09eda46cb6fb73713159605c32f49cf78ad700c4',7933),
 PYTHON:('4a81cbef89c3cded9c9435c2faf747823dfed9ca9a0da82df374834a18c70dc8',102352),
}


def canonical(value):
    assert isinstance(value,str)
    path=Path(value)
    assert path.is_absolute() and '..' not in path.parts and path.resolve()==path
    assert not any(p.is_symlink() for p in (path,*path.parents))
    return path


def row(path):
    path=canonical(str(path));stat=path.stat()
    assert path.is_file() and stat.st_nlink==1
    digest=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(4*1024*1024),b''):digest.update(chunk)
    return dict(path=str(path),sha256=digest.hexdigest(),bytes=stat.st_size)


def verify(ref):
    assert isinstance(ref,dict) and set(ref)=={'path','sha256','bytes'}
    assert re.fullmatch('[0-9a-f]{64}',ref['sha256']) and type(ref['bytes']) is int and ref['bytes']>=0
    assert row(ref['path'])==ref,ref['path']


def read(ref):
    verify(ref)
    return json.loads(Path(ref['path']).read_text())


def family(ref):
    index=read(ref);root=Path(ref['path']).parent;assert Path(ref['path']).name=='index.json'
    names=[r['path'] for r in index['files']];assert len(names)==len(set(names))
    nodes=list(root.rglob('*'));assert all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes)
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_file()}==set(names)|{'index.json'}
    dirs=set()
    for item in index['files']:
        rel=Path(item['path']);assert not rel.is_absolute() and '..' not in rel.parts
        dirs.update(p.as_posix() for p in rel.parents if p!=Path('.'))
        verify(dict(item,path=str(root/rel)))
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_dir()}==dirs


def safe_id(value):
    assert isinstance(value,str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',value)


def pin(path):
    sha,size=PINS[str(path)]
    return dict(path=str(path),sha256=sha,bytes=size)


def member_layout(member,authority,plan):
    """Pure joins to the two reviewed actors, not a new execution API."""
    safe_id(member['id']);safe_id(member['runId'])
    assert authority['runId']==member['runId'] and type(authority['schemaVersion']) is int and authority['schemaVersion']==1
    assert authority['rootLaunchMinimumFreeBytes']==MINIMUM
    assert member['cwd']==str(REPO)
    if member['arm']=='stock':
        assert authority['state']=='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1' and authority['arm']=='stock'
        assert authority['sourceIndex']==pin(STOCK/'index.json') and authority['plans']==pin(STOCK/'plans.json')
        assert authority['localhostServerAllowed'] is authority['browserAllowed'] is True
        for key in ['compilerAllowed','nativeBuildAllowed','guestAllowed','engineAllowed','externalApplicationDeploymentAllowed']:assert authority[key] is False
        assert all(key not in authority for key in ['outputRoot','monitorOutputRoot','argv'])
        assert plan['outputPrefix']=='/private/tmp/starling-node-compat/next-browser-hydration-stock-v4'
        assert plan['arms']['stock']['outputRoot'] is plan['arms']['stock']['monitorOutputRoot'] is plan['arms']['stock']['argv'] is None
        output=plan['outputPrefix']+'-'+member['runId'];monitor=output+'-monitor'
        argv=[PYTHON,'-I','-B',str(STOCK/'run-owned.py'),'stock',member['authority']['path']]
        receipt=None
    else:
        assert member['arm']=='native' and authority['state']=='ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2'
        assert authority['sourceIndex']==pin(NATIVE/'index.json') and authority['plan']==pin(NATIVE/'plan.json')
        for key in ['localhostServeAllowed','actualNextGuestAllowed','browserAllowed']:assert authority[key] is True
        for key in ['compilerAllowed','componentConstructionAllowed','externalDeploymentAllowed','adoptionAllowed']:assert authority[key] is False
        assert plan['outputPrefix']=='/private/tmp/starling-node-compat/next-wasmtime-deployment'
        assert authority['component']['sha256']=='1c3108d2fdce72a1bfa8cc64a0e6e0645acd71223b26b6dc11d037d4a95efe83'
        assert authority['component']['bytes']==37214251
        output=plan['outputPrefix']+'-'+member['runId'];monitor=output+'-external-root'
        argv=[PYTHON,'-I','-B',str(WRAPPER),member['authority']['path']]
        receipt=str(WRAPPER.parent/(member['runId']+'-full-world-guard.json'))
    assert member['outputRoot']==output and member['monitorOutputRoot']==monitor
    assert member['argv']==argv and member['observation']==str(Path(monitor)/'observation.json')
    assert member['worldGuardReceipt']==receipt
    for value in [output,monitor,member['observation']]+([receipt] if receipt else []):canonical(value)


def validate_registry(registry,self_ref,fetch=read):
    assert registry['state']=='ROOT_NEXT_BROWSER_COHORT_PREDECLARED_V1'
    assert registry['launcher']==self_ref and registry['minimumFreeBytes']==MINIMUM
    members=registry['members'];assert [m['id'] for m in members]==ORDER
    assert [m['arm'] for m in members]==['stock','native','native','stock','stock','native']
    assert len({m['runId'] for m in members})==6
    shared=registry['sharedInputs'];paths=[r['path'] for r in shared]
    assert len(paths)==len(set(paths))
    for path in PINS:assert pin(path) in shared,'Missing reviewed actor/tool input: '+path
    destinations=[]
    for member in members:
        authority=fetch(member['authority'])
        plan=fetch(authority['plans'] if member['arm']=='stock' else authority['plan'])
        member_layout(member,authority,plan)
        destinations.extend([member['outputRoot'],member['monitorOutputRoot']])
    assert len(destinations)==len(set(destinations)),'Cohort output/monitor namespaces overlap'
    return members


def prior_status(member,authority,observation,terminal,result,world):
    """Safety/protection gate. A retained functional failure remains failed."""
    code=observation['rawExitCode'];assert type(code) is int and code in (0,1)
    assert type(terminal['schemaVersion']) is int and terminal['schemaVersion']==1 and type(terminal['rawExitCode']) is int and terminal['rawExitCode']==code
    assert terminal['authority']==member['authority']
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    for key in ['errors','signals','interruptedSignals','remainingObservedPids']:assert terminal[key]==[]
    assert observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is True
    assert observation['terminal']['path']==str(Path(member['monitorOutputRoot'])/'terminal.json')
    assert observation['result']['path']==str(Path(member['outputRoot'])/'result.json')
    assert type(result['passed']) is bool and result['passed']==(code==0)
    if member['arm']=='stock':
        assert observation['state']=='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_OBSERVATION_V1' and observation['arm']=='stock'
        assert observation['runId']==member['runId'] and observation['outputRoot']==member['outputRoot']
        assert type(observation['hostExperimentPassed']) is bool and observation['hostExperimentPassed']==result['passed'] and observation['guestOrNativeExecuted'] is False
        assert result['suite']=='FULL_NEXT_STOCK_ORIGINAL_MODULE_BRIDGE_HYDRATION_BROWSER_CONTROL_V1'
        assert result['prepared'] is True and result['originalApplicationInputsPreserved'] is True
        assert result['guestExecuted'] is result['applicationModified'] is False
    else:
        assert observation['state']=='ROOT_NEXT_WASMTIME_DEPLOYMENT_OBSERVATION_V2'
        assert observation['runId']==member['runId'] and observation['outputRoot']==member['outputRoot']
        assert type(observation['passed']) is bool and observation['passed']==result['passed']
        assert result['state']==('NEXT_WASMTIME_DEPLOYMENT_CONTRACTS_PASSED_UNREVIEWED_V2' if code==0 else 'NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2')
        assert result['originalInputsPreserved'] is result['readonlyAppPreserved'] is True
        assert result['rootAuthority']==member['authority'] and result['sourceIndex']==authority['sourceIndex']
        assert result['component']==authority['component'] and result['runId']==member['runId']
        server=result['server'];assert server['shutdownRequested'] is server['sigintSent'] is True and server['forcedCleanup'] is False
        assert type(server['exit']['code']) is int and server['exit']==dict(code=0,signal=None,error=None)
        assert world['before']==world['after'] and world['unchanged'] is world['nativeInputsPreserved'] is True
        assert world['authority']==member['authority'] and world['before']['sourceIndex']==authority['worldSourceIndex']
    return dict(id=member['id'],rawExitCode=code,functionalPassed=result['passed'],safeRecordedCompletion=True)


def prior_cli_status(member,cohort_ref,self_ref,admission,completion,raw_code):
    assert admission['state']=='COHORT_SINGLE_MEMBER_ADMITTED_V1'
    assert admission['cohort']==cohort_ref and admission['launcher']==self_ref and admission['member']==member
    assert admission['oneCommandOnly'] is True and admission['automaticNextOrRetry'] is False
    assert completion['state']=='COHORT_SINGLE_CLI_RETURN_CAPTURED_V1' and completion['memberId']==member['id']
    assert completion['error'] is None and completion['registrySharedAndPriorRecordsPreserved'] is True
    assert completion['automaticNextOrRetry'] is False and completion['functionalPassNotInferred'] is True
    assert type(completion['rawCliExitCode']) is int and completion['rawCliExitCode']==raw_code


def prior_records(member,cohort_ref,self_ref):
    refs=[]
    def grab(path):
        ref=row(path);refs.append(ref);return read(ref)
    authority=read(member['authority']);observation=grab(member['observation'])
    terminal=read(observation['terminal']);result=read(observation['result']);refs.extend([observation['terminal'],observation['result']])
    for key in ['stdout','stderr']:verify(terminal[key]);refs.append(terminal[key])
    world=grab(member['worldGuardReceipt']) if member['arm']=='native' else None
    status=prior_status(member,authority,observation,terminal,result,world)
    logs=HERE/(member['id']+'-launcher')
    admission=grab(logs/'admission.json');completion=grab(logs/'cli-result.json')
    prior_cli_status(member,cohort_ref,self_ref,admission,completion,observation['rawExitCode'])
    for key,name in [('stdout','cli.stdout.log'),('stderr','cli.stderr.log')]:
        assert completion[key]['path']==str(logs/name);verify(completion[key]);refs.append(completion[key])
    return status,refs


def require_fresh(member,exists,free_bytes):
    paths=[member['outputRoot'],member['monitorOutputRoot']]
    if member['worldGuardReceipt'] is not None:paths.append(member['worldGuardReceipt'])
    paths.append(str(HERE/(member['id']+'-launcher')))
    assert not any(exists(path) for path in paths),'Selected outputs/receipt/admission already exist'
    assert free_bytes>=MINIMUM,'At least 1 GiB free required before any launch record/runtime'
    return paths


def durable(path,value):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as handle:
        handle.write(json.dumps(value,indent=2)+'\n');handle.flush();os.fsync(handle.fileno())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort',required=True);parser.add_argument('--sha256',required=True);parser.add_argument('--member',required=True)
    args=parser.parse_args()
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        parser.error('Use Python -I -B without -O')
    cohort=canonical(args.cohort);cohort_ref=row(cohort)
    assert re.fullmatch('[0-9a-f]{64}',args.sha256) and cohort_ref['sha256']==args.sha256
    registry=read(cohort_ref);self_ref=row(Path(__file__).resolve())
    def protect():
        verify(cohort_ref);verify(self_ref);family(registry['prerequisiteReviewIndex'])
        for ref in registry['sharedInputs']:verify(ref)
        return validate_registry(registry,self_ref)
    members=protect();selected=next(m for m in members if m['id']==args.member)
    priors=[];prior_refs=[]
    for member in members[:members.index(selected)]:
        status,refs=prior_records(member,cohort_ref,self_ref);priors.append(status);prior_refs.extend(refs)
    for ref in prior_refs:verify(ref)
    free=shutil.disk_usage(Path(selected['outputRoot']).parent).free
    require_fresh(selected,lambda value:Path(value).exists() or Path(value).is_symlink(),free)
    logs=HERE/(selected['id']+'-launcher');logs.mkdir(mode=0o700)
    admission=dict(schemaVersion=1,state='COHORT_SINGLE_MEMBER_ADMITTED_V1',cohort=cohort_ref,launcher=self_ref,member=selected,
                   preceding=priors,precedingRecords=prior_refs,freeBytesAtAdmission=free,minimumFreeBytes=MINIMUM,
                   oneCommandOnly=True,functionalFailuresNotPromoted=True,automaticNextOrRetry=False)
    durable(logs/'admission.json',admission)
    code=None;error=None;preserved=False
    out_path=logs/'cli.stdout.log';err_path=logs/'cli.stderr.log'
    with os.fdopen(os.open(out_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as out,os.fdopen(os.open(err_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as err:
        try:
            code=subprocess.run(selected['argv'],cwd=selected['cwd'],stdout=out,stderr=err,check=False).returncode
        except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught))
        finally:
            out.flush();err.flush();os.fsync(out.fileno());os.fsync(err.fileno())
    try:
        protect()
        for ref in prior_refs:verify(ref)
        preserved=True
    except BaseException as caught:error=dict(type=type(caught).__name__,message=str(caught))
    record=dict(schemaVersion=1,state='COHORT_SINGLE_CLI_RETURN_CAPTURED_V1',memberId=selected['id'],rawCliExitCode=code,error=error,
                registrySharedAndPriorRecordsPreserved=preserved,stdout=row(out_path),stderr=row(err_path),
                originalMonitorProofRequiredAtNextAdmission=True,functionalPassNotInferred=True,automaticNextOrRetry=False)
    durable(logs/'cli-result.json',record);print(json.dumps(record),flush=True)
    return code if type(code) is int and code in (0,1) and error is None and preserved else 1


if __name__=='__main__':raise SystemExit(main())
