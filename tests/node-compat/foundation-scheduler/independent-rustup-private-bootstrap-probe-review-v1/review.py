"""Independent retained private Rustup probe DATA audit; no owner code evaluated."""
from pathlib import Path
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
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


def dump(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2)+'\n')

def main():
    s=HERE.parent
    authority_row=row(s/'rustup-private-bootstrap-probe-v1-root-authority.json')
    root_row=row(s/'rustup-private-bootstrap-probe-v1-root-results.json')
    need(authority_row['sha256']=='b501591d13809510c023a706e3569162afc28a2d6533f81b26dd4657c83d5d90' and authority_row['bytes']==2396,'Held Root authority')
    need(root_row['sha256']=='734659a7d92424c86015e6b2b0fcc5f64b51315cda7f6d0e368f53f373026ab3' and root_row['bytes']==2759,'Held Root unreviewed result')
    auth,root=read(authority_row),read(root_row)
    private=Path('/private/tmp/starling-node-compat/rustup-private-bootstrap-probe-v1')
    need(root==read(row(private/'result.json')) and (private/'result.json').read_bytes()==Path(root_row['path']).read_bytes(),'Entire actual/retained Root result byte equality')
    need(auth['schemaVersion']==root['schemaVersion']==1 and auth['state']=='ROOT_PRIVATE_RUSTUP_BOOTSTRAP_DIAGNOSTIC_V1' and root['state']=='ROOT_PRIVATE_RUSTUP_BOOTSTRAP_PROBE_PASSED_UNREVIEWED_V1','Exact diagnostic states')
    need(root['authority']==authority_row and root['error'] is None,'Actual authority and no probe error')
    need(auth['freshRoot']==str(private) and auth['privateRustupHome']==str(private/'rustup-home') and auth['privateCargoHome']==str(private/'cargo-home'),'Literal fresh private roles')
    need(auth['removedVariableNames']==[] and auth['environmentValuesRecorded'] is False and auth['hostHomeValuesPreserved'] is True,'Root-reported home/environment provenance')
    need(auth['networkAndPrebuiltToolchainInstallationAllowed'] is True,'Explicit Root prebuilt installation authorization')
    for k in ['cmakeOrGuestCompilationAllowed','engineOrGuestAllowed','oldFailedRootsMutationAllowed']:need(auth[k] is False,'Scope withheld '+k)
    for k in ['oldBuildResumed','cmakeOrGuestCompilationExecuted','engineOrGuestExecuted','operationalAdmission']:need(root[k] is False,'Root actual scope '+k)
    for k in ['managerInputUnchanged','failedBuildObservationUnchanged','requiresIndependentActualReview']:need(root[k] is True,'Literal actual result '+k)
    file(auth['manager']);need(auth['manager']['sha256']=='63752a1919a3a4793173ec70f8f212621a7ce38ba6a246095984482f4de20f9f' and auth['manager']['bytes']==11408656,'Pinned manager unchanged')
    cargo=Path(auth['cargoProxyPath']);need(cargo.is_symlink() and str(cargo.readlink())=='rustup' and cargo.resolve()==Path(auth['manager']['path']),'Actual host cargo alias resolves exact pinned manager')
    manager=auth['manager']['path'];toolchain=private/'rustup-home/toolchains/1.88.0-aarch64-apple-darwin'
    specs=[('disable-self-update',[manager,'set','auto-self-update','disable'],30,88059),('first-install',[manager,'toolchain','install','1.88.0','--profile','minimal'],300,88064),('target-add',[manager,'target','add','--toolchain','1.88.0','wasm32-wasip1'],180,88264),('repeat-install',[manager,'toolchain','install','1.88.0','--profile','minimal'],180,88352),('manager-version',[manager,'--version'],30,88359),('cargo-proxy-version',[str(cargo),'--version'],30,88365)]
    expected={
      'disable-self-update':('',"info: auto-self-update mode set to disable\nwarn: no toolchain installed and no default toolchain set\nhelp: run 'rustup default stable' to download the latest stable release of Rust and set it as your default toolchain.\n"),
      'first-install':('\n  1.88.0-aarch64-apple-darwin installed - rustc 1.88.0 (6b00bc388 2025-06-23)\n\n','info: syncing channel updates for 1.88.0-aarch64-apple-darwin\ninfo: latest update on 2025-06-26 for version 1.88.0 (6b00bc388 2025-06-23)\ninfo: downloading 3 components\ninfo: default toolchain set to 1.88.0-aarch64-apple-darwin\n'),
      'target-add':('','info: downloading component rust-std\n'),
      'repeat-install':('\n  1.88.0-aarch64-apple-darwin unchanged - rustc 1.88.0 (6b00bc388 2025-06-23)\n\n','info: syncing channel updates for 1.88.0-aarch64-apple-darwin\n'),
      'manager-version':('rustup 1.29.3 (edbc831ce 2026-11-02)\n','info: This is the version for the rustup toolchain manager, not the rustc compiler.\ninfo: the currently active `rustc` version is `rustc 1.88.0 (6b00bc388 2025-06-23)`\n'),
      'cargo-proxy-version':('cargo 1.88.0 (873a06493 2025-05-10)\n','')}
    need(auth['commands']==[dict(name=n,argv=a,deadlineSeconds=d)for n,a,d,p in specs],'All six complete authorized argv/deadlines')
    need([x['name']for x in root['commands']]==[x[0]for x in specs],'All six actual command roles and order')
    commands=[];raw_names=[];processes=[];started_times=[]
    for spec,actual in zip(specs,root['commands']):
        name,argv,deadline,pid=spec;directory=private/'commands'/name
        terminal=read(actual['terminal']);started_row=row(directory/'started.json');started=read(started_row)
        need(actual['terminal']['path']==str(directory/'terminal.json'),'Actual terminal physical role')
        need(started['schemaVersion']==terminal['schemaVersion']==1 and started['pid']==terminal['pid']==pid and started['argv']==argv and started['timeoutSeconds']==deadline,'Complete raw argv/pid/deadline')
        need(started['authority']==terminal['authority']==authority_row,'Raw command same authority')
        need(terminal['rawExitCode']==0 and type(terminal['rawExitCode']) is int,'Each actual raw exit zero')
        for k in ['timeout','forcedCleanup']:need(terminal[k] is False,'No actual '+k)
        for k in ['interruptedSignals','remainingObservedPids','signals','errors']:need(terminal[k]==[],'Empty actual lifecycle '+k)
        for k in ['parentOwnedGroupGone','allObservedOwnedGroupsGone','acceptanceRequiresRawZeroNoSignalsNoTimeoutAndIndependentResultReview']:need(terminal[k] is True,'Complete actual cleanup '+k)
        need(terminal['finalGroups']==[dict(pgid=pid,alive=False,signalAllowed=False)],'Only actual owned command group and gone')
        need(type(terminal['operationalElapsedSeconds']) in (int,float) and 0<terminal['operationalElapsedSeconds']<deadline,'Operational duration only, bounded')
        events=[read(row(p))for p in sorted(directory.glob('owned-*.json'))]
        need([x['sequence']for x in events]==list(range(len(events))) and [x['process']for x in events]==terminal['observedProcesses'],'Whole ownership events equal terminal')
        need(len(events)==(2 if name=='first-install' else 1) and all(x['process']['pgid']==pid for x in events),'Finite exact ownership scope')
        need(events[0]['process']['pid']==pid and events[0]['process']['ppid']==88057,'Actual Root parent and fresh PID')
        for k,value in zip(['stdout','stderr'],expected[name]):
            d=terminal[k];file(d);need(d['path']==str(directory/(k+'.log')) and Path(d['path']).read_bytes()==value.encode(),'Whole exact raw '+name+' '+k)
        names=tree(directory);need(names==sorted(['started.json','terminal.json','stdout.log','stderr.log']+['owned-%04d.json'%i for i in range(len(events))]),'Complete actual command evidence membership')
        raw_names.extend('commands/'+name+'/'+n for n in names);processes.extend(terminal['observedProcesses']);started_times.append(started['startedAtUtc'])
        commands.append(dict(name=name,argv=argv,deadlineSeconds=deadline,pid=pid,started=started_row,terminal=actual['terminal'],stdout=terminal['stdout'],stderr=terminal['stderr'],rawExitCode=0,ownedGroupGone=True,observedProcesses=len(events),operationalElapsedSeconds=terminal['operationalElapsedSeconds']))
    need(started_times==sorted(started_times) and len(set(started_times))==6 and len(raw_names)==31 and len(processes)==7,'All six fresh commands sequential; seven observed processes,31 raw files')
    need(any(x['pid']==88250 and x['ppid']==88064 and x['command']==str(toolchain/'bin/rustc')for x in processes),'Private installed rustc observed, not a compilation claim')
    need(processes[-1]['pid']==88365 and processes[-1]['command']==str(toolchain/'bin/cargo'),'Host cargo proxy actually execs private installed cargo')
    checkpoint('Six full argv/start/ownership/raw streams/terminal records, seven observed processes and six naturally cleaned owned groups; first install,targetadd,identical repeat install,manager and cargo proxy raw0')
    settings=read(root_row)['settings'];file(settings)
    need(settings['path']==str(private/'rustup-home/settings.toml') and Path(settings['path']).read_bytes()==b'version = "12"\ndefault_toolchain = "1.88.0-aarch64-apple-darwin"\nauto_self_update = "disable"\n\n[overrides]\n','Exact persistent private auto-self-update disable')
    components=row(toolchain/'lib/rustlib/components')
    need(Path(components['path']).read_text().splitlines()==['cargo-aarch64-apple-darwin','rust-std-aarch64-apple-darwin','rustc-aarch64-apple-darwin','rust-std-wasm32-wasip1'],'Actual host and wasm32-wasip1 installed component manifests')
    target=toolchain/'lib/rustlib/wasm32-wasip1/lib';need(len(list(target.glob('*.rlib')))==28,'Actual target28 rlib files retained, not compiler invocation')
    need(root['cargoHomeBinExists'] is False and tree(private/'cargo-home')==[] and not(private/'cargo-home/bin').exists(),'Private Cargo home empty; no proxy seeding required for tested command')
    private_names=tree(private);need(len(private_names)==189,'Whole finite private diagnostic tree membership')
    private_rows=[]
    for name in private_names:
        d=row(private/name);private_rows.append(dict(d,path=name,mode=stat.S_IMODE((private/name).lstat().st_mode)))
    dump('probe-inventory.json',dict(schemaVersion=1,root=str(private),files=private_rows,prebuiltToolchainDataOnly=True,compilerBuildOrAdoptionGranted=False))
    checkpoint('All189 actual private files read/hashed; exact107B persistent disable, four installed components,28 wasm32-wasip1 rlibs and empty private Cargo home')
    old=s/'independent-combined355-native-build-bootstrap-failure-review-v1'
    old_index=row(old/'index.json');need(old_index['sha256']=='188878b478a6165b1b1d51716ef5a8c6230685562d03e14f640dbf78b0fe2d1d','Held original failure-review family')
    family(old_index);old_result=row(old/'results.json');need(old_result['sha256']=='9832b4caed3be7cab3edc0ad299014ed7cc847bc111e1bf84db01ee81c607262','Original failed-build review unchanged')
    ledger=read(row(old/'input-hashes.json'));need(len(ledger['files'])==4253,'Exact prior finite protection4253')
    for d in ledger['files']:file(d)
    failed=read(row(old/'failed-work-inventory.json'));failed_root=Path(failed['root'])
    need(len(failed['files'])==755 and tree(failed_root)==sorted(x['path']for x in failed['files']),'Whole failed-v1 work755 membership unchanged')
    for m in failed['files']:
        file(dict(path=str(failed_root/m['path']),sha256=m['sha256'],bytes=m['bytes']));need(stat.S_IMODE((failed_root/m['path']).lstat().st_mode)==m['mode'],'Every retained failed-v1 file mode unchanged')
    file(auth['failedBuildRootObservation']);need(auth['failedBuildRootObservation']['sha256']=='282d46aee7bcee35cffe08126a91f96dd6e870da4da0b0a476fac1bfc06b03c6','Root original failed observation unchanged')
    need(not Path('/private/tmp/starling-node-compat/combined-native355-v1-freeze').exists(),'Old frozen root still absent')
    checkpoint('All4253 prior failure-reader inputs and entire755-file failed-v1 work bytes/modes/membership rehashed; pinned manager and original Root failure unchanged; no old build resumed')
    copies=[]
    for name,original in [('root-authority.json',Path(authority_row['path'])),('root-results.json',Path(root_row['path'])),('settings.toml',Path(settings['path'])),('components',Path(components['path']))]+[(n,private/n)for n in raw_names]:
        d=row(original);copy=HERE/'raw'/name;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(original.read_bytes());q=row(copy)
        need(d['sha256']==q['sha256'] and d['bytes']==q['bytes'] and ident(original)[:2]!=ident(copy)[:2],'Whole retained raw copy and independent inode')
        copies.append(dict(original=d,copy=q))
    dump('raw-copy-map.json',dict(schemaVersion=1,files=copies))
    for name,before in list(seen.items()):need(ident(Path(name))==before[1],'Final identity of every authenticated input unchanged')
    need(tree(private)==private_names and tree(failed_root)==sorted(x['path']for x in failed['files']),'Final probe and old-failure membership unchanged')
    result=dict(schemaVersion=1,state='INDEPENDENT_RUSTUP_PRIVATE_BOOTSTRAP_PROBE_REVIEW_PASSED_V1',verifiedPassed=True,dataReviewOnly=True,
      rootObservation=root_row,rootAuthority=authority_row,priorFailureReview=dict(index=old_index,result=old_result),manager=auth['manager'],settings=settings,components=components,commands=commands,
      rawCommandCount=6,allRawExitCodesZero=True,allObservedOwnedGroupsGone=True,privateAutoSelfUpdateDisabled=True,wasm32Wasip1Installed=True,repeatedInstallPassed=True,cargoProxyPassed=True,cargoHomeBinExists=False,pinnedManagerUnchanged=True,failedBuildEvidenceUnchanged=True,oldBuildResumed=False,
      coverage=dict(commandCount=6,rawCommandFiles=31,observedProcesses=7,ownedGroups=6,rawCopies=35,privateRegularFiles=189,wasmTargetRlibs=28,priorProtectedInputs=4253,failedWorkFiles=755),
      reviewerOwnerHelpersInvoked=False,reviewerToolOrRustupInvoked=False,reviewerNetworkOrInstallationInvoked=False,reviewerEngineOrGuestInvoked=False,rootExecutedPrebuiltToolchainInstallation=True,rootExecutedManagerVersionAndCargoProxy=True,nativeBuildAuthorityGranted=False,cmakeOrGuestCompilationExecuted=False,engineOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
      limitations=['Per-command argv and streams are retained; process environment values are not. Private Cargo/home environment selection and host-home preservation are Root-authority/result provenance, not an independent environment snapshot. Private Rustup storage is corroborated by actual settings,installed files and observed executable paths.','This finite host diagnostic proves the tested manager/target/repeated-install/proxy sequence. It neither completes a native build nor proves later CMake/Cargo compilation, hermeticity,all future network behavior,performance or guest correctness.','Original failed v1 remains failed; fresh private diagnostic success does not authorize resuming,retargeting or mutating its roots.','Seven observed processes and six groups are finite retained monitor evidence,not general OS process attestation.'],
      recommendation='A genuine new source/context successor may persistently disable private Rustup auto-self-update before the same pinned install/target steps,retain original native355 semantics and use fresh source/work/freeze/output roots. Keep old failure immutable. Root must separately review/authorize any build; this proof grants none.')
    dump('results.json',result)
    fixed={k:v for k,v in result.items()if k not in ['commands','limitations','recommendation','rootObservation','rootAuthority','priorFailureReview','manager','settings','components','coverage']}
    dump('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],requiredFixedValues=fixed,requiredCoverage=result['coverage'],requiredExactDescriptors={k:result[k]for k in ['rootObservation','rootAuthority','manager','settings','components']},requiredPriorFailureReview=result['priorFailureReview'],requiredCommands=commands,nativeBuildAuthorityGranted=False))
    dump('input-hashes.json',dict(schemaVersion=1,files=[x[0]for _,x in sorted(seen.items())if not Path(x[0]['path']).is_relative_to(HERE)],observedDataOnly=True))
    dump('audit-results.json',dict(schemaVersion=1,passed=True,checks=check_count,uniqueFilesHashed=len(seen),observedBytes=sum(x[0]['bytes']for x in seen.values()),checkpoints=checks,ownerOrToolCodeExecuted=False))
    print(json.dumps(dict(passed=True,checks=check_count,uniqueFilesHashed=len(seen),rawCopies=len(copies))))

if __name__=='__main__':
    main()
