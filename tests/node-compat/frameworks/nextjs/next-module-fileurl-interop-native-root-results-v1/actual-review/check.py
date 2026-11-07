"""Portable failed-build and corrected frontend DATA replay. No producer imports or extraction."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, re, shlex, stat, tarfile, zlib

HERE = Path(__file__).resolve().parent
LIMIT = 128 * 1024**2


def sha(value):
    return hashlib.sha256(value).hexdigest()


def parse(value):
    def unique(items):
        result = {}
        for key, item in items:
            assert key not in result
            result[key] = item
        return result
    return json.loads(value, object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def identity(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def clean(terminal, expected=0):
    assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == expected
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert all(row['alive'] is row['signalAllowed'] is False for row in terminal['finalGroups'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true')
    parser.add_argument('--current', action='store_true', help='Only selected retained text/Source originals, not binaries or omitted trees.')
    args = parser.parse_args()
    final = HERE / 'index.json'
    sealed = final.exists()
    if sealed:
        index = parse(final.read_bytes())
        nodes = list(HERE.rglob('*'))
        assert not any(p.is_symlink() for p in nodes)
        assert {p.relative_to(HERE).as_posix() for p in nodes if p.is_file()} == {r['path'] for r in index['files']} | {'index.json'}
        for row in index['files']:
            path = HERE / row['path']; value = path.read_bytes()
            assert path.resolve(strict=True) == path and path.is_file() and path.stat().st_nlink == 1
            assert (len(value), sha(value)) == (row['bytes'], row['sha256'])
    else:
        assert args.draft, 'Unsealed read requires explicit --draft'
    ix = parse((HERE / 'payload-index.json').read_bytes())
    assert ix['binaryOrComplete825PackageSdkPayloadTreeIncluded'] is ix['recursiveArchivesIncluded'] is False
    assert ix['actorOrNetworkInvoked'] is ix['futureGeneratorOrFutureBuildRecordsIncluded'] is ix['failedBuildAccepted'] is ix['nativeFullBuildOrEngineOrGuestAccepted'] is False
    assert ix['selectedOriginalsBeforeAndFinalHashAndPhysicalBookendsUnchanged'] is ix['syntaxOnlyAccepted'] is True
    compressed = (HERE / ix['bundle']['path']).read_bytes()
    assert (sha(compressed), len(compressed)) == (ix['bundle']['sha256'], ix['bundle']['bytes'])
    unzip = zlib.decompressobj(16 + zlib.MAX_WBITS)
    expanded = unzip.decompress(compressed, LIMIT + 1)
    assert len(expanded) <= LIMIT and unzip.eof and not unzip.unused_data and not unzip.unconsumed_tail
    rows = {row['archivePath']: row for row in ix['files']}
    assert len(rows) == len(ix['files']) == ix['memberCount'] < 5000
    assert len({row['original']['path'] for row in rows.values()}) == len(rows)
    originals = {row['original']['path']: row for row in rows.values()}
    blobs, seen, end = {}, set(), 0
    with tarfile.open(fileobj=io.BytesIO(expanded), mode='r:') as archive:
        for member in archive:
            rel = PurePosixPath(member.name)
            assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts
            assert member.name in rows and member.name not in seen
            assert member.offset == end and member.offset_data == member.offset + 512
            row = rows[member.name]
            assert member.size == row['original']['bytes'] < 8 * 1024**2 and member.mode == row['mode']
            value = archive.extractfile(member).read()
            assert sha(value) == row['original']['sha256']
            value.decode('utf-8'); assert b'\0' not in value
            blobs[row['original']['path']] = value; seen.add(member.name)
            end = member.offset_data + ((member.size + 511) // 512) * 512
    assert set(rows) == seen and len(expanded) - end >= 1024 and not any(expanded[end:])
    assert sum(len(value) for value in blobs.values()) == ix['logicalBytes']

    def data(path):
        return parse(blobs[str(path)])

    def ref(row):
        value = blobs[row['path']]
        assert (sha(value), len(value)) == (row['sha256'], row['bytes'])
        return value

    for source in ix['sourceFamilies']:
        index = parse(ref(source)); root = Path(source['path']).parent
        declared = {str(root / row['path']) for row in index['files']} | {source['path']}
        retained = {path for path in blobs if root in Path(path).parents}
        assert declared == retained
        for row in index['files']:
            rel = PurePosixPath(row['path']); assert not rel.is_absolute() and '..' not in rel.parts
            ref(dict(path=str(root / row['path']), sha256=row['sha256'], bytes=row['bytes']))

    def owner(root, seconds, code=0):
        root = Path(root)
        terminal, started = data(root / 'terminal.json'), data(root / 'started.json')
        clean(terminal, code)
        assert started['pid'] == terminal['pid'] and started['timeoutSeconds'] == seconds
        assert started['authority'] == terminal['authority']; ref(terminal['authority'])
        for key in ['stdout', 'stderr']: ref(terminal[key])
        records = [data(path) for path in sorted(blobs) if path.startswith(str(root) + '/owned-') and path.endswith('.json')]
        assert [row['sequence'] for row in records] == list(range(len(records)))
        assert [row['process'] for row in records] == terminal['observedProcesses']
        return terminal, started

    first = Path(ix['failedBuildRoot']); second = Path(ix['syntaxRoot'])
    root1, root2 = Path(ix['failedRoot']), Path(ix['syntaxRootRecords'])
    r, m = data(first / 'result.json'), data(first / 'metadata.json')
    assert sha(blobs[str(first/'result.json')]) == 'b0b4270b795788db3b75be5619158edabae76c8d8294ee37cb149273d4409207'
    assert sha(blobs[str(first/'metadata.json')]) == 'be397c3c11d699bc5876fdc7b372907e1cbd28d6ab4fa6df75124573d54bb00c'
    assert r['passed'] is False and r['state'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_FAILED_UNACCEPTED_V1'
    assert r['primaryError']['type'] == 'AssertionError' and r['primaryError']['message'] == 'build failed'
    assert r['postCollectionErrors'] == [] and r['engineCandidate'] is None
    assert r['engineOrGuestExecuted'] is r['adoption'] is False
    assert r['inputProtection'] == dict(files=1871, wholeTrees=10, unchanged=True, errors=[], currentBeforeFinalOnly=True)
    assert r['metadata'] == dict(path=str(first/'metadata.json'),sha256=sha(blobs[str(first/'metadata.json')]),bytes=len(blobs[str(first/'metadata.json')]))
    assert m['engine'] is m['actualSeparateEmbeddingCompileRows'] is None
    assert m['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
    assert m['engineExecuted'] is m['guestExecuted'] is m['adoption'] is m['old83MetadataProjected'] is False
    a = data(first/'root-authority.json')
    outer = Path(str(first)+'-root-monitor')
    assert blobs[str(first/'root-authority.json')] == blobs[str(outer/'authority.issued.json')]
    term, start = owner(outer,7200,1)
    assert start['pid'] == term['pid'] == 28790
    assert start['authority']['path']==str(outer/'authority.issued.json')
    assert (start['authority']['sha256'],start['authority']['bytes'])==(m['rootAuthority']['sha256'],m['rootAuthority']['bytes'])
    assert start['argv'] == [a['wrapperPython']['path'],'-B','-I',a['entry']['path'],'--authority',str(outer/'authority.issued.json')]
    assert a['entry'] == m['recipe'] and a['callerIndex']['sha256'] == 'a803c451b1c63f978cfe7b77be8acdeeefda2bafc3b57cccda917b8293ca8bcc'
    ref(a['entry']);ref(a['plan']);ref(a['callerIndex'])
    assert a['buildAllowed'] is a['configureAllowed'] is True
    assert all(a[k] is False for k in ['engineOrGuestExecutionAllowed','networkAllowed','rustupAllowed','freezeAllowed'])
    obs = data(outer/'observation.json')
    assert obs['terminal'] == dict(path=str(outer/'terminal.json'),sha256=sha(blobs[str(outer/'terminal.json')]),bytes=len(blobs[str(outer/'terminal.json')]))
    assert obs['workerResult'] == dict(path=str(first/'result.json'),sha256=sha(blobs[str(first/'result.json')]),bytes=len(blobs[str(first/'result.json')]))
    assert obs['rawExitCode'] == 1 and obs['workerReportedPassed'] is obs['ownedCleanRawZero'] is False
    assert obs['errors'] == [] and obs['originalInputProtection']['unchanged'] is True
    assert obs['workerInputProtection'] == r['inputProtection'] and obs['automaticRetry'] is obs['engineOrGuestExecuted'] is False
    for row in obs['rawFiles'].values(): ref(row)
    assert [p['label']for p in r['phases']] == ['rust-version','cargo-version','rust-sysroot','configure','build','ninja-commands']
    envdoc=data(first/'environment-policy.json'); env=envdoc['environment']
    assert envdoc['HOMEInherited'] is envdoc['privateCargoHome'] is envdoc['offline'] is True and envdoc['rustupInvoked'] is False
    assert env['CARGO_NET_OFFLINE']=='true' and env['CARGO_NET_GIT_FETCH_WITH_CLI']=='false' and env['CARGO_BUILD_JOBS']=='1'
    assert env['TMPDIR']==str(first/'tmp') and env['CARGO_HOME']==str(first/'cargo-home') and env['CARGO_TARGET_DIR']==str(first/'rust-target')
    assert env['RUSTC']==a['rustc']['path'] and 'RUSTUP_TOOLCHAIN'not in env and 'RUSTUP_HOME'not in env
    flags=m['requestedCMake'];assert all(m['observedCMake'][k]['value']==v for k,v in flags.items())
    phase_pids=[];owned_count=len(term['observedProcesses'])
    for row,cap,code in zip(r['phases'],[120,120,120,2400,7200,120],[0,0,0,0,1,0]):
        phase=first/'results'/row['label'];pt,ps=owner(phase/'owned-monitor',cap,code)
        owned_count+=len(pt['observedProcesses']);phase_pids.append(dict(pid=ps['pid'],timeoutSeconds=cap))
        worker,packet=data(phase/'worker-result.json'),data(phase/'packet.json')
        assert data(phase/'phase.json')==row
        assert row['argv']==packet['argv']==worker['argv'] and packet['cwd']==str(first) and packet['environment']==env
        assert row['rawExitCode']==row['outerRawExitCode']==worker['rawChildExitCode']==worker['status']==code
        assert type(row['rawExitCode'])is int and row['innerOwnedClean']is row['ownedGone']is True
        assert row['timeout']is row['forcedCleanup']is False
        assert all(row[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
        assert packet['authority']==ps['authority']==pt['authority']==m['rootAuthority']
        assert ps['argv']==[a['wrapperPython']['path'],'-B','-I',a['entry']['path'],'--worker-packet',str(phase/'packet.json')]
        assert worker['childStarted']is worker['lifecycleComplete']is worker['temporarySigtermHandlerRestored']is True
        assert worker['launcherErrors']==[]and worker['stopReason']is None and worker['stoppedForDiskSpace']is False and worker['sigtermReceived']==0
        cleanup=worker['ownedGroupCleanup'];assert cleanup['complete']is True and cleanup['events']==cleanup['errors']==[]and cleanup['rawChildExitCode']==code
        ref(worker['rawCombinedLog']);ref(row['workerResult']);ref(row['outerTerminal'])
        assert data(phase/'owned-monitor/stdout.log')==worker and pt['stderr']['bytes']==0
        assert all(type(q['bytes'])is int and q['bytes']>=1073741824 for q in worker['diskSamples'])
    frames=[parse(line)for line in blobs[str(outer/'stdout.log')].splitlines()if line.strip()]
    assert len(frames)==7 and frames[:6]==phase_pids
    assert frames[-1]==dict(result=obs['workerResult'],passed=False,engine=None,metadata=r['metadata'])
    assert owned_count==1998
    configure=r['phases'][3]['argv'];assert configure[1:7]==['-S',str(first/'componentize-source'),'-B',str(first/'build'),'-G','Ninja']
    assert configure[7:]==['-D'+k+'='+v for k,v in flags.items()]
    assert r['phases'][4]['argv'][1:]==['--build',str(first/'build'),'--target','starlingmonkey_embedding','--parallel','1','--','-d','keeprsp']
    assert r['phases'][5]['argv'][1:]==['-C',str(first/'build'),'-t','commands']
    db=parse(ref(r['compileDatabase']));assert db==m['actualCompileRows']and len(db)==80
    assert (m['nativePolicyInputCount'],m['buildSupportInputCount'],m['embeddingInputCount'])==(435,387,3)
    composition=parse(ref(r['sourceComposition'])); expected={}
    for q in composition['files']:
        expected[str(first/'native-source'/q['path'])]=(str(Path(composition['sourceRoot'])/q['path']),q['sha256'],q['bytes'],384)
    for q in m['buildSupportInputManifest']:
        expected[str(first/'native-source'/q['relativePath'])]=(q['source']['path'],q['source']['sha256'],q['source']['bytes'],q['mode'])
    for q in m['embeddingInputManifest']:
        expected[str(first/'componentize-source'/q['relativePath'])]=(q['source']['path'],q['source']['sha256'],q['source']['bytes'],q['mode'])
    actual={q['target']['path']:(q['source']['path'],q['source']['sha256'],q['source']['bytes'],q['mode'])for q in r['sourceCopies']}
    assert expected==actual and len(actual)==len(r['sourceCopies'])==825
    assert all(q['singleLink']is q['distinctInode']is True and q['source']['sha256']==q['target']['sha256']and q['source']['bytes']==q['target']['bytes']for q in r['sourceCopies'])
    failurelog=blobs[str(first/'results/build/command.combined.log')].decode()
    assert len(re.findall(r'^.*: error:',failurelog,re.M))==1
    assert "script_loader.cpp:324:35: error: no matching function for call to 'JS_ConcatStrings'"in failurelog
    assert 'JS_ConcatStrings(cx, tag, canonical_url.toString())'in failurelog
    assert "cannot convert argument of incomplete type 'JSString *' to 'JS::Handle<JSString *>' for 3rd argument"in failurelog
    assert '1 error generated.'in failurelog and 'ninja: build stopped: subcommand failed.'in failurelog
    assert '[113/120] Building CXX object'in failurelog
    oldloader=blobs[str(first/'native-source/runtime/script_loader.cpp')]
    assert sha(oldloader)=='25c19d29caf370104f40036df8d20633fdb64396c30f5993a5fe52315e619b28'
    review=data(root1/'actual-build-failure-review.json')
    assert sha(blobs[str(root1/'actual-build-failure-review.json')])=='d2419fe2d12bb1e44ed47afc2d491c7d647476db710b4b1b6ce7d9fd79279ce6'
    assert review['verifiedDataConsistent']is True and review['buildPassed']is review['acceptedForConstruction']is False
    assert review['protectedFileDescriptorsChecked']==1871 and review['copies']['completeExactNativeSupportEmbeddingSourceAndTargetRoleMappingVerified']is True
    assert review['configuredRowsAreNotCompletedCompilationAttestation']is True and review['artifactInventoryDoesNotProveFinalLink']is True
    assert review['engineCandidate']is None and review['engineArtifactExists']is False
    def content(tree):
        return dict(root=tree['root'],rootMode=tree['rootIdentity']['mode'],entries=[{k:v for k,v in q.items()if k not in ['dev','ino','nlink','mtimeNs']}for q in tree['entries']])
    protection=parse(ref(m['initialTreeProtection'])); assert len(protection)==10
    assert sum(len(t['entries'])for t in protection.values())==15766
    for role,t in a['reusedTrees'].items(): assert content(protection[role])==content(parse(ref(t['inventory'])))

    sr=data(second/'result.json');sa=data(second/'authority.json')
    assert sha(blobs[str(second/'result.json')])=='fddb65a86b3a3bcd21fddad28d8a80c3a07bab2fb540b0fa568f28e8956e3f7c'
    assert sha(blobs[str(second/'authority.json')])=='260b0c84f2a678638ea499c313e1d73c552a9d854e3b8ba97bb854880c9265b5'
    assert sr['passed']is sr['ownedClean']is True and sr['primaryError']is None
    assert sr['rawExitCode']==0 and sr['objectOrLinkProduced']is sr['engineOrGuestExecuted']is sr['fullNativeBuildOrInteropAccepted']is False
    st,ss=owner(second/'owned-monitor',180,0)
    assert ss['pid']==st['pid']==52221 and len(st['observedProcesses'])==2
    assert sr['authority']==ss['authority']==st['authority'] and sr['terminal']['sha256']==sha(blobs[str(second/'owned-monitor/terminal.json')])
    si=parse(ref(sa['inputs']));ref(sa['controller']);ref(sa['originalMonitor'])
    assert ss['argv']==sa['argv']==si['argv']and len(ss['argv'])==46
    assert sa['cwd']==si['cwd']==str(second/'cwd')and sa['TMPDIR']==si['TMPDIR']==str(second/'tmp')
    assert st['stdout']['bytes']==st['stderr']['bytes']==0
    assert sa['compilerFrontendOnly']is True and all(sa[k]is False for k in ['originalWorkWritesAllowed','linkAllowed','guestAllowed','fullNativeBuildAccepted'])
    assert sr['guards']==dict(sourceUnchanged=True,toolsUnchanged=True,failedWorkUnchanged=True,treeSnapshotRecordsCtime=False,continuousWriteAttestationClaimed=False)
    oldargv=shlex.split(next(line for line in failurelog.splitlines()if line.startswith(str(first/'build/cxx-wrapper')+' ')))
    derived=[];pos=0
    while pos<len(oldargv):
        arg=oldargv[pos]
        if arg=='-MD':pos+=1;continue
        if arg in ['-MT','-MF','-o']:pos+=2;continue
        if arg.startswith('-I'+str(first/'native-source')):arg=arg.replace(str(first/'native-source'),str(Path(si['argv'][-1]).parents[1]),1)
        elif arg==str(first/'native-source/runtime/script_loader.cpp'):arg=si['argv'][-1]
        if arg=='-c':derived.append('-fsyntax-only')
        derived.append(arg);pos+=1
    assert derived==si['argv']and '-fsyntax-only'in derived and not any(q=='-o'or q.startswith('-M')for q in derived)
    corrected=ref(ix['roles']['selectedCorrectedLoader'])
    assert sha(corrected)=='40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67'
    assert b'JS::RootedString canonical_url_string(cx, canonical_url.toString());'in corrected
    assert b'JS_ConcatStrings(cx, tag, canonical_url_string)'in corrected
    for key in ['source','tools','failed-work']:
        assert blobs[str(second/(key+'-before.json'))]==blobs[str(second/(key+'-after.json'))]
    source=data(second/'source-before.json');selection=parse(ref(sa['sourceInput']))
    assert len(source['physicalRecords'])==825 and len(source['directoryRecords'])==171
    assert source['roleCounts']=={'native-policy-source':435,'build-support':387,'componentize-embedding':3}
    assert all(source[k]==v for k,v in selection.items()if k!='protectedInputs')
    assert len(source['protectedInputs'])==len(selection['protectedInputs'])+1
    assert [q for q in source['protectedInputs']if q!=sa['sourceInput']]==selection['protectedInputs']
    assert source['protectedInputs'].count(sa['sourceInput'])==1
    tools=data(second/'tools-before.json');assert set(tools)=={'wasi-sdk','spidermonkey'}
    for role,t in tools.items():assert content(t)==content(parse(ref(si['completeToolTreeSpecifications'][role]['inventory'])))
    failed=data(second/'failed-work-before.json');assert failed['root']==str(first)and len(failed['entries'])==10272
    rootrows={q['path']:q for q in failed['entries']}
    for name,pinned in [('result.json',si['failedWorkGuard']['originalResult']),('metadata.json',si['failedWorkGuard']['originalFailedMetadata'])]:
        assert rootrows[name]['sha256']==pinned['sha256']and rootrows[name]['bytes']==pinned['bytes'];ref(pinned)
    assert rootrows['native-source/runtime/script_loader.cpp']['sha256']==sha(oldloader)
    syntaxreview=data(root2/'actual-syntax-review.json')
    assert sha(blobs[str(root2/'actual-syntax-review.json')])=='51f52a159d95e5bfea64a0f083d50254291c0b8f80e11f01ce272a9a8412fc98'
    assert syntaxreview['verified']is True and syntaxreview['frontend']['actualRawExitCode']==0
    assert syntaxreview['fullNativeBuildAccepted']is syntaxreview['compilerRerun']is syntaxreview['helperOrAliasExecution']is False
    assert syntaxreview['actualEngine']is syntaxreview['actualComponent']is syntaxreview['actualInteropOrGuest']is None
    current_count=0
    if args.current:
        for row in ix['files']:
            path=Path(row['original']['path']); before=identity(path)
            assert before==row['physicalBefore']and path.resolve(strict=True)==path and path.stat().st_nlink==1
            assert path.read_bytes()==blobs[str(path)]and identity(path)==before
            current_count+=1
    print(json.dumps(dict(portableDataPassed=True,capsuleSealed=sealed,members=len(blobs),logicalBytes=ix['logicalBytes'],currentRetainedOriginalsChecked=current_count,
      failedBuildRetainedAndUnaccepted=True,failedBuildPhaseCodes=[0,0,0,0,1,0],originalGroupsClean=True,
      configuredCompileRowsNotCompletedCompilation=80,failedMetadataRetained=True,engine=None,
      correctedSingleTuFrontendPassed=True,syntaxOnlyNotFullBuildOrLinkOrInterop=True,
      futureGeneratorOrBuildRecordsIncluded=False,actorOrNetworkInvoked=False)))


if __name__=='__main__':main()
