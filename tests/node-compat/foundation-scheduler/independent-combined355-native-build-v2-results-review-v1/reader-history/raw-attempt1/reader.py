"""Independent actual combined355 v2 BUILD DATA audit; no owner/tool action."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'combined-native-build-controller-candidate-v2'
SOURCE_SHA = '24584f9686e3c88d935a2d92c376818b462692af9dc68de2703fbf73748fef38'
seen = {}
checks = []
check_count = 0


def need(value, label):
    global check_count
    check_count += 1
    if not value:
        raise AssertionError(label)


def checkpoint(label):
    checks.append(label)


def ident(p):
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'Ordinary non-symlink file: ' + str(p))
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns,
            stat.S_IMODE(s.st_mode), s.st_nlink, str(p.resolve()))


def file(row):
    p = Path(row['path'])
    need(p.is_absolute() and str(p) == row['path'], 'Canonical absolute path')
    need(set(row) == {'path', 'sha256', 'bytes'}, 'Exact three-field descriptor')
    need(type(row['bytes']) is int and row['bytes'] >= 0, 'Actual finite byte count')
    need(re.fullmatch('[a-f0-9]{64}', row['sha256']) is not None, 'SHA256 descriptor')
    before = ident(p)
    if str(p) in seen:
        need(seen[str(p)] == (row, before), 'Repeated row and identity unchanged')
        return row
    h = hashlib.sha256()
    length = 0
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
            length += len(b)
    need(before == ident(p), 'File stable through streamed hash')
    need(length == row['bytes'] and h.hexdigest() == row['sha256'], 'Exact actual file bytes')
    seen[str(p)] = (dict(row), before)
    return row


def row(p):
    p = Path(p)
    b = p.read_bytes()
    return file(dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b)))


def read(d):
    file(d)
    b = Path(d['path']).read_bytes()
    need(len(b) == d['bytes'] and hashlib.sha256(b).hexdigest() == d['sha256'], 'Stable JSON read')
    return json.loads(b)


def tree(p):
    need(p.is_dir() and not p.is_symlink(), 'Ordinary tree root')
    names = []
    for q in p.rglob('*'):
        need(not q.is_symlink(), 'No tree aliases')
        need(q.is_dir() or q.is_file(), 'Ordinary tree entry')
        if q.is_file():
            names.append(q.relative_to(p).as_posix())
    return sorted(names)


def family(d):
    value = read(d)
    need(value['schemaVersion'] == 1 and 0 < len(value['files']) <= 2048, 'Finite indexed family')
    base = Path(d['path']).parent
    names = ['index.json']
    rows = [d]
    for m in value['files']:
        n = m['path']
        need(n and not Path(n).is_absolute() and all(x not in ('', '.', '..') for x in n.split('/')) and '\\' not in n, 'Confined indexed path')
        names.append(n)
        rows.append(file(dict(m, path=str(base / n))))
    need(len(names) == len(set(names)), 'Unique family membership')
    need(tree(base) == sorted(names), 'Complete exact indexed membership')
    return rows


def proof(pair):
    members = family(pair['index'])
    need(sum(d == pair['result'] for d in members) == 1, 'Result indexed exactly once')
    return read(pair['result'])


def descriptors(value):
    if isinstance(value, dict):
        if set(value) == {'path', 'sha256', 'bytes'}:
            yield value
        else:
            for item in value.values():
                yield from descriptors(item)
    elif isinstance(value, list):
        for item in value:
            yield from descriptors(item)


def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def typed_same(a,b):
    if type(a)is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys()and all(typed_same(a[k],b[k])for k in a)
    if isinstance(a,list):return len(a)==len(b)and all(typed_same(x,y)for x,y in zip(a,b))
    return a==b
def main():
    d=read(row(HERE/'audit-data.json'));r=read(d['rootRow']);need(d['rootRow']['sha256']=='36b02cdd40bb7f9cc5e6c93c43c2d1a990189264435d34c68a672adc354bbeb9','Held actual Root result')
    for x in descriptors(r):file(x)
    source=family(r['controllerIndex']);need(r['controllerIndex']['sha256']==SOURCE_SHA,'Actual2458 controller Source');refs=read(row(SOURCE/'references.json'));inputs=read(row(SOURCE/'source-inputs.json'))
    need(len(inputs['files'])==len(inputs['modeRows'])==4515 and len(refs['families'])==12,'Entire finite Source/protection4515/modes/12 families')
    for x in inputs['files']:file(x)
    for x in inputs['modeRows']:file(x['file']);need(ident(Path(x['file']['path']))[5]==x['mode'],'Every source/proof/old artifact mode preserved')
    for x in refs['families']:family(x)
    peer=proof(r['sourcePeer']);need(peer['state']=='INDEPENDENT_COMBINED355_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V2'and peer['controllerSourceIndexSha256']==SOURCE_SHA and peer['sourceOnly']is peer['sourceReviewPassed']is True,'Actual independent0430 Source peer')
    root=read(r['rootAuthority']);config=read(r['rootConfig']);invocation=read(r['invocation']);need(config['controllerIndex']==r['controllerIndex']==root['controllerIndex']and config['sourceIndex']==refs['integrationIndex']==root['sourceIndex'],'Whole actual phase Source/config/controller tuples')
    need(root['state']=='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_BUILD_RETRY_V2'and root['phase']=='native-build-only'and root['variant']=='normal-off'and root['buildAllowed']is True and root['controllerSourceReview']==r['sourcePeer'],'Real new build-only Root authority')
    for k in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOperationsAllowed','gcAllowed','gcReconfigureAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:need(root[k]is False,'No other phase '+k)
    need(r['toolObservation']==dict(sessionId=61477,rawExitCode=0,kind='Real exec-command tool terminal observation; no fabricated outer PID log'),'Root-reported exec tool terminal,not invented independent outer PID record')
    need(r['rawMetadataFields']==80 and r['nativeSourceFiles']==355 and r['externalEmbeddingSources']==3 and r['selectedWholeManifests']==11,'Actual full80-field combined context')
    a=read(r['actualBuildResult']);t=read(r['ownedWorkerTerminal']);need(a['state']=='native-build-completed-runtime-pending'and a['rawChildExitCode']==a['status']==a['launcherExitCode']==0 and a['evidenceComplete']is a['lifecycleComplete']is a['allSourceStageOriginalAndCacheInputsPreserved']is True,'Actual completed native build/lifecycle/protection')
    need(a['controllerIndex']==r['controllerIndex']and a['rootAuthority']==r['rootAuthority']and a['actualStageReview']==refs['actualStageReview']and a['sourceIndexSha256']==refs['integrationIndex']['sha256'],'Whole actual native result roles')
    need(a['command']==[refs['bash']['path'],refs['recipe']['path']]and a['explicitEnvironment']==refs['buildEnvironment']==root['buildEnvironment'],'Exact actual own recipe/environment,not staged donor recipe')
    need(a['engine']==r['engine']and a['metadata']==r['metadata'],'Actual engine/sidecar same build pair')
    need(a['ownedGroupCleanup']==dict(pgid=903,complete=True,events=[],errors=[],rawChildExitCode=0)and a['launcherErrors']==[]and a['sigtermReceived']==0 and a['temporarySigtermHandlerRestored']is True and a['stoppedForDiskSpace']is False and a['stopReason']is None,'Real inner903 natural cleanup/no stop/errors')
    need(t['pid']==795 and t['rawExitCode']==0 and t['authority']==r['rootAuthority']and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['timeout']is t['forcedCleanup']is False,'Actual worker795 raw0 and groups gone')
    for k in ['interruptedSignals','remainingObservedPids','signals','errors']:need(t[k]==[],'No monitor lifecycle issue '+k)
    external=Path(r['ownedWorkerTerminal']['path']).parent;events=[read(row(q))for q in sorted(external.glob('owned-*.json'))]
    need(len(events)==707 and [x['sequence']for x in events]==list(range(707))and[x['process']for x in events]==t['observedProcesses'],'All707 actual ownership records entireobjects/order')
    need(len(t['finalGroups'])==80 and all(g['alive']is g['signalAllowed']is False for g in t['finalGroups'])and{795,903}<={g['pgid']for g in t['finalGroups']},'All80 actual owned groups gone without signals')
    need(tree(external)==sorted(['started.json','terminal.json','stdout.log','stderr.log']+['owned-%04d.json'%i for i in range(707)]),'Whole711-file external actual inventory')
    started=read(row(external/'started.json'));need(started['pid']==795 and started['timeoutSeconds']==7200 and started['authority']==r['rootAuthority']and started['argv']==[refs['pythonExecutable']['path'],'-B','-I',str(SOURCE/'controller.py'),'worker',json.dumps(r['rootConfig'],separators=(',',':'))],'Whole started worker argv/authority/config/deadline')
    stdout=Path(t['stdout']['path']).read_bytes();need(t['stderr']['bytes']==0 and len(stdout.splitlines())==1 and typed_same(json.loads(stdout),dict(output=str(Path(r['actualBuildResult']['path']).parent),result=a)),'Whole worker raw stdout result frame and empty stderr')
    parentlines=Path(r['parentStdout']['path']).read_bytes().splitlines();need(len(parentlines)==2 and typed_same(json.loads(parentlines[0]),r['monitorLaunch'])and typed_same(json.loads(parentlines[1]),r['actualReturnEnvelope'])and r['parentStderr']['bytes']==0,'Entire parent raw two-record JSONL,never one JSON object')
    need(r['actualReturnEnvelope']['actualBuildResult']==r['actualBuildResult']and r['actualReturnEnvelope']['externalParentTerminal']==r['ownedWorkerTerminal'],'Raw parent actual descriptor bindings')
    observer=Path('/private/tmp/starling-node-compat/combined-native355-v2-build-root-observer');pre=read(row(observer/'preentry-environment.json'));need(pre['rootAuthority']==r['rootAuthority']and pre['controllerIndex']==r['controllerIndex']and pre['policy']==peer['requiredRootEnvironmentPolicy']==root['rootEnvironmentPolicy']and pre['removedVariableNames']==[]and pre['requiredEntriesAbsent']is pre['hostHomeValuesPreserved']is True and pre['environmentValuesRecorded']is False,'Actual clean-entry record names-only policy,not environment values attestation')
    samples=a['diskFreeSamplesDuringBuildCommand'];need(len(samples)==398 and all(x['freeBytes']>=838860800 for x in samples)and all(x['monotonicSeconds']<y['monotonicSeconds']for x,y in zip(samples,samples[1:])),'All398 actual ordered build floor samples')
    for k in ['freeBytesBefore','freeBytesBeforeCacheCopies','freeBytesAfterCacheCopies']:need(a[k]>=2147483648,'Actual boundary2GiB '+k)
    plan=read(refs['cachePlan']);need(len(plan['copies'])==len(a['cacheCopiesCompleted'])==4,'Four exact owned archive/tool cache copies')
    for x,y in zip(plan['copies'],a['cacheCopiesCompleted']):
        file(x['source']);file(y['target']);need(y['source']==x['source']and y['target']['path']==str(Path(d['workRoot'])/x['target'])and y['target']['sha256']==x['source']['sha256']and y['target']['bytes']==x['source']['bytes'],'Exact cache source/target bytes')
        u,v=ident(Path(x['source']['path'])),ident(Path(y['target']['path']));need(u[:2]!=v[:2]and v[6]==1 and u[5]==x['sourceMode']and v[5]==x['outputMode'],'Independent cache copy inode/modes')
    out=Path(r['actualBuildResult']['path']).parent;need(tree(out)==sorted(['build.log','launch.json','result.json']+['cache-copy-%d.json'%i for i in range(1,5)]),'Exact seven-file inner lifecycle output')
    launch=read(row(out/'launch.json'));need(launch['rawChildExitCode']is None and launch['state']=='COMBINED355_NORMAL_OFF_NATIVE_BUILD_STARTED','Actual pre-action launch remains historical')
    for k in ['configuredSourceRoot','workRoot','freezeRoot','command','explicitEnvironment','controllerIndex','rootAuthority']:need(launch[k]==a[k],'Same before/after native build role '+k)
    file(a['buildLog']);log=Path(a['buildLog']['path']).read_text();steps=[(int(x),int(y))for x,y in re.findall(r'^\[(\d+)/(\d+)\]',log,re.M)];need(steps[-1]==(108,108)and all(y==108 for x,y in steps)and 'Finished `release` profile'in log,'Actual complete108-stage Ninja/control-flow log')
    need('auto-self-update mode set to disable'in log and 'installed - rustc 1.88.0'in log and 'unchanged - rustc 1.88.0'in log,'Actual private disable/install/CMake-repeat log sequence succeeds')
    checkpoint('WholeRoot/Source4515+modes/12,actual795/903 raw0,707records80groups,711+7 inventories,complete parent2JSONL/workerwholeframe,4cache copies/398disk/108Ninja log independently verified')
    m=read(r['metadata']);need(len(m)==80 and m['enginePath']==r['engine']['path']and m['engineSha256']==r['engine']['sha256']and m['engineBytes']==r['engine']['bytes'],'Exact unmodified80-field native sidecar/engine')
    need(m['buildRecipeSha256']==refs['recipe']['sha256']and m['combinedNativeSourcePolicy']['helperSha256']==refs['helper']['sha256']and m['combinedNativeSourcePolicy']['policyFileSha256']==refs['policy']['sha256'],'Actual own recipe/helper/policy identity')
    rp=m['privateRustupBootstrapPolicy'];need(rp==r['privateRustupBootstrapPolicy']and rp['persistentSetting']=='disable'and rp['oldFailedWorkResumed']is False,'Genuine actual private Rustup provenance')
    before=read(rp['beforeInstallRecord']);file(rp['settingsAtBuildCompletion']);need(before['settings']['bytes']==57 and before['settings']['sha256']=='c199d646911907e3bf8b419c59b0dedf08d1a133d6d69e1e01e7d733be995437'and before['persistentSetting']=='disable'and before['installedToolchainClaim']is False,'Historical57B preinstall digest/control-flow record,not current file descriptor')
    need(Path(rp['settingsAtBuildCompletion']['path']).read_bytes()==b'version = "12"\ndefault_toolchain = "1.88.0-aarch64-apple-darwin"\nauto_self_update = "disable"\n\n[overrides]\n','Actual107B postbuild private settings')
    dump('raw-source-review.json',dict(schemaVersion=1,passed=True,root=d['rootRow'],actualBuildResult=r['actualBuildResult'],engine=r['engine'],metadata=r['metadata'],rawMetadataFields=80,processRecords=707,groups=80,externalFiles=711,innerFiles=7,diskSamples=398,minimumBuildFreeBytes=min(x['freeBytes']for x in samples),rawNinjaSteps=steps,rootToolExitCodeReported=0,ownedWorkerExitCode=0,recipeExitCode=0,privateSettingsBeforeHistoricalDescriptor=before['settings'],privateSettingsAfter=rp['settingsAtBuildCompletion'],noStandaloneCompilerTerminalClaim=True))
    dump('raw-inputs.json',dict(schemaVersion=1,files=[x[0]for name,x in sorted(seen.items())]))
    print(json.dumps(dict(rawSourceAuditPassed=True,checks=check_count,files=len(seen))))
if __name__=='__main__':main()
