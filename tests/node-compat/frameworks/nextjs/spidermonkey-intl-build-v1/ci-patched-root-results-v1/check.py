"""Portable, standard-library-only reader for retained CI DATA; executes no tools.

Default mode verifies the complete text bundle. --artifact-zip additionally
streams the two nested tar archives; it never copies a large binary to disk.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import io
import json
import re
import tarfile
import zipfile

HEAD = 'bb2526b7e862ad7d8f93254beac41dc48b0fa349'
FORK = '9dab3d6f643e926a340c391ea30968e940390dec'
DRIVER_SHA = 'a390f1a6ab88e7513d0ee58f565ed2c18e1a82d1fd8267a280c452494ce6caa3'
ZIP_SHA = 'abbbd37727631187ef20f5b9a2ee1d6d50dbf9ef6c1e5b45f9234f1a2f7c7f74'
ORIGINAL_EVIDENCE = '/home/runner/work/_temp/spidermonkey-intl/evidence/'
PHASES = ['host-compiler','cmake-version','sdk-download','sdk-extract','rust-install','rust-version','cargo-version','sdk-version','python-version','cbindgen-install','cbindgen-version','configure','source-revision','source-prepatch-clean','savedframe-patch-check','savedframe-patch-apply','build','static-members','merged-members','source-final-revision','source-clean','source-patch-diff']


def digest(data):
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def file_digest(path):
    h = hashlib.sha256()
    n = 0
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024**2), b''):
            n += len(block)
            h.update(block)
    return dict(bytes=n, sha256=h.hexdigest())


def safe(name):
    p = PurePosixPath(name)
    assert name and not p.is_absolute() and '..' not in p.parts and '\\' not in name
    assert str(p) == name.rstrip('/'), name
    return str(p)


def audit_patch(data,result):
    prefix='savedframe-patch-source/'
    source=result['sourcePatch'];input=source['input']
    assert result['guestBaseCommit']==FORK and result['savedFrameEvalRequested'] is True and result['savedFrameEvalCapability']==1
    assert result['guestPatchSha256']==input['patch']['sha256']=='1a571a891cffd3b81b463c922212f8a4ab1dd1f42b717da4cac5c401445bc9b1'
    index=data[prefix+'index.json'];assert digest(index)=={k:input['index'][k] for k in ['bytes','sha256']}
    assert input['index']['sha256']=='531bcc7e777b8451d903da23c13bc6e3a005d2a63e90aab1569167d9d25b8a23'
    rows=json.loads(index)['files'];assert len(rows)==input['payloadFiles']==27
    assert {n[len(prefix):] for n in data if n.startswith(prefix)}=={r['path'] for r in rows}|{'index.json'}
    for r in rows:assert digest(data[prefix+safe(r['path'])])=={k:r[k] for k in ['bytes','sha256']}
    assert digest(data[prefix+'saved-frame-is-eval-v1.patch'])=={k:input['patch'][k] for k in ['bytes','sha256']}
    results=json.loads(data[prefix+'results.json'])
    assert results['changedFiles']==4 and results['exactEdits']==21 and results['sourceAndPureChecks']==112
    assert results['sourceOnly'] and results['uncompiled'] and results['actualNativeBuild'] is None
    expected=['js/public/SavedFrameAPI.h','js/src/vm/SavedFrame.h','js/src/vm/SavedStacks.cpp','js/src/vm/StructuredClone.cpp']
    assert source['changedPaths']==expected and source['applied'] and source['sourceCleanValidated']
    before={r['path']:r for r in input['before']};after={r['path']:r for r in input['after']}
    assert set(before)==set(after)==set(expected)
    for field,kind in [('beforeFiles','before'),('afterFiles','after'),('finalFiles','after')]:
        assert len(source[field])==4
        for name,actual in zip(expected,source[field]):
            raw=data[prefix+kind+'/'+name]
            assert actual['descriptor']==dict(path='/home/runner/work/_temp/spidermonkey-intl/project/deps/spidermonkey-source/'+name,**digest(raw))
            assert actual['mode']==0o600
            assert digest(raw)=={k:(before if kind=='before' else after)[name][k] for k in ['bytes','sha256']}
    assert source['afterFiles']==source['finalFiles']
    diff=data['source-patch-diff/command.log']
    assert source['actualDiff']==dict(path=ORIGINAL_EVIDENCE+'source-patch-diff/command.log',**digest(diff))
    blocks=re.split(r'(?m)^diff --git ',diff.decode())[1:];assert len(blocks)==4
    for block,name in zip(blocks,expected):
        lines=block.splitlines(keepends=True);assert lines[0].rstrip()=='a/'+name+' b/'+name
        match=re.search(r'^index ([0-9a-f]{40})\.\.([0-9a-f]{40}) (100644)$',block,re.M);assert match
        old=data[prefix+'before/'+name];new=data[prefix+'after/'+name]
        blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        assert match.group(1)==blob(old)==before[name]['gitBlobSha1'] and match.group(2)==blob(new)
        old_lines=old.decode().splitlines(keepends=True);output=[];cursor=0;i=0
        while i<len(lines):
            hunk=re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
            if not hunk:i+=1;continue
            start=int(hunk[1])-1;old_count=int(hunk[2] or '1');new_count=int(hunk[4] or '1')
            assert start>=cursor;output+=old_lines[cursor:start];cursor=start;used=produced=0;i+=1
            while i<len(lines) and not lines[i].startswith('@@'):
                line=lines[i];assert line[0] in ' +-'
                if line[0] in ' -':assert old_lines[cursor]==line[1:];cursor+=1;used+=1
                if line[0] in ' +':output.append(line[1:]);produced+=1
                i+=1
            assert (used,produced)==(old_count,new_count)
        output+=old_lines[cursor:];assert ''.join(output).encode()==new
    assert data['source-prepatch-clean/command.log']==b''
    assert data['source-revision/command.log'].decode().strip()==data['source-final-revision/command.log'].decode().strip()==FORK
    assert data['source-clean/command.log'].decode().split('\0')==expected+['']
    assert '-z' in json.loads(data['source-clean/packet.json'])['argv']
    assert all(flag in json.loads(data['source-patch-diff/packet.json'])['argv'] for flag in ['--binary','--full-index','--no-ext-diff','--no-textconv','--no-renames'])
    header=data[prefix+'after/js/public/SavedFrameAPI.h']
    assert re.search(rb'^#define JS_HAS_SAVEDFRAME_IS_EVAL 1$',header,re.M) and b'GetSavedFrameIsEval' in header
    return dict(payloadFiles=27,historicalSourcePureChecks=112,sourceChecksRerun=False,actualChangedFiles=4,recordedModesBeforeAfterFinal='0600',
                fullActualGitDiffReconstructed=True,gitIndexModes='100644',exactSourceEditsRecorded=21,capabilityVersion=1,
                sourceBaseCommit=FORK,patchSha256=input['patch']['sha256'],symbolDefinitionFromHeaderClaimed=False)


def audit_text(data, historic_driver):
    def obj(name):
        return json.loads(data[name])
    def descriptor(ref, name):
        assert ref == dict(path=ORIGINAL_EVIDENCE+name, **digest(data[name])), name
    result = obj('result.json')
    assert result['state'] == 'guest-library-built-engine-and-runtime-pending'
    assert result['forkCommit'] == FORK and result['componentOrEngineExecuted'] is False and result['runtimeAccepted'] is False
    assert result['github'] == dict(GITHUB_SHA=HEAD,GITHUB_RUN_ID='42281671898',GITHUB_RUN_ATTEMPT='1')
    assert [p['name'] for p in result['phases']] == PHASES
    assert digest(historic_driver) == dict(bytes=21034,sha256=DRIVER_SHA)
    events = samples = 0
    minimum = result['startFreeBytes']
    phases = []
    for phase in result['phases']:
        name = phase['name']
        terminal_name = name+'/owned-monitor/terminal.json'
        worker_name = name+'/worker-result.json'
        descriptor(phase['terminal'],terminal_name)
        descriptor(phase['worker'],worker_name)
        terminal, worker, started, packet = (obj(n) for n in [terminal_name,worker_name,name+'/owned-monitor/started.json',name+'/packet.json'])
        assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
        assert not terminal['timeout'] and not terminal['forcedCleanup']
        assert all(terminal[k] == [] for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
        assert terminal['finalGroups'] and all(g['alive'] is False for g in terminal['finalGroups'])
        assert worker['rawChildExitCode'] == worker['status'] == 0 and worker['lifecycleComplete'] is True
        assert worker['childStarted'] is True and worker['stoppedForDiskSpace'] is False
        assert worker['stopReason'] is None and worker['sigtermReceived'] == 0 and worker['temporarySigtermHandlerRestored'] is True
        assert worker['launcherErrors'] == []
        cleanup = worker['ownedGroupCleanup']
        assert cleanup['complete'] is True and cleanup['rawChildExitCode'] == 0 and cleanup['events'] == cleanup['errors'] == []
        descriptor(terminal['stdout'],name+'/owned-monitor/stdout.log')
        descriptor(terminal['stderr'],name+'/owned-monitor/stderr.log')
        descriptor(worker['commandLog'],name+'/command.log')
        assert data[name+'/owned-monitor/stdout.log'] == data[name+'/owned-monitor/stderr.log'] == b''
        authority = terminal['authority']
        assert authority == started['authority'] and authority['github'] == result['github']
        assert authority['driver'] == dict(path='/home/runner/work/StarlingMonkey/StarlingMonkey/tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/build.py',bytes=21034,sha256=DRIVER_SHA)
        assert started['argv'][1:3] == ['-B','-I'] and started['argv'][3] == authority['driver']['path']
        assert started['argv'][4:] == ['--worker',ORIGINAL_EVIDENCE+name+'/packet.json']
        assert 0 < started['timeoutSeconds'] <= 5400
        assert packet['environment']['HOME']=='/home/runner'
        for key,value in [('CARGO_BUILD_JOBS','1'),('CARGO_INCREMENTAL','0'),('MAKEFLAGS','-j1'),('CCACHE_DISABLE','1'),('SCCACHE_DISABLE','1')]:
            assert packet['environment'][key]==value
        snapshots = [obj(k) for k in sorted(data) if k.startswith(name+'/owned-monitor/owned-')]
        assert [s['sequence'] for s in snapshots] == list(range(len(snapshots)))
        assert [s['process'] for s in snapshots] == terminal['observedProcesses']
        events += len(snapshots)
        disk = worker['diskSamples']
        assert disk and all(s['freeBytes'] >= result['stopFloorBytes'] for s in disk)
        assert all(a['monotonic'] <= b['monotonic'] for a,b in zip(disk,disk[1:]))
        low = min(s['freeBytes'] for s in disk)
        minimum = min(minimum,low)
        samples += len(disk)
        phases.append(dict(name=name,rawExitCode=0,rawChildExitCode=0,observedProcesses=len(snapshots),diskSamples=len(disk),minimumSampledFreeBytes=low,
                           argv=packet['argv'],terminal=dict(path=terminal_name,**digest(data[terminal_name])),commandLog=dict(path=name+'/command.log',**digest(data[name+'/command.log']))))
    assert events == 1257 and samples == 1772
    assert result['startFreeBytes'] == 88821727232 and result['endFreeBytes'] == 77542973440
    assert result['startRequirementBytes'] == 20*1024**3 and result['stopFloorBytes'] == 4*1024**3
    assert result['startFreeBytes'] >= result['startRequirementBytes'] and result['endFreeBytes'] >= result['stopFloorBytes']
    assert data['source-revision/command.log'].decode().strip() == FORK
    patch_summary=audit_patch(data,result)
    moz = data['mozconfig-release'].decode()
    for flag in ['--with-intl-api','--target=wasm32-unknown-wasi','--disable-debug','--disable-bootstrap','--disable-tests','--disable-js-shell','--enable-lto=thin']:
        assert flag in moz
    assert '--without-intl-api' not in moz
    configure=obj('configure/packet.json')['argv']
    assert '-DSPIDERMONKEY_BUILD_FROM_SOURCE=ON' in configure and '-DSPIDERMONKEY_INTL=ON' in configure and '-DCMAKE_BUILD_TYPE=Release' in configure
    assert re.search(r'^#define\s+JS_HAS_INTL_API\s+1\s*$',data['generated/js/src/js-confdefs.h'].decode(),re.M)
    assert re.search(r'^#define\s+MOZ_ICU4X\s+1\s*$',data['generated/js/src/js-confdefs.h'].decode(),re.M)
    assert '-DV8_INTL_SUPPORT' in data['generated/js/src/irregexp/backend.mk'].decode()
    static = data['static-members/command.log'].decode().splitlines()
    merged = data['merged-members/command.log'].decode().splitlines()
    assert len(static) == 533 and len(merged) == 555 and merged[:533] == static
    assert static.count('icu_data.o') == 1
    backend = data['generated/js/src/build/backend.mk'].decode()
    objects = re.findall(r'(?:^libjs_static\.a:\s*|^\s+)([^\s]+\.o)\s*\\?$',backend,re.M)
    assert collections.Counter(PurePosixPath(p).name for p in objects) == collections.Counter(static)
    common = [p for p in objects if '/icu/common/' in p]
    i18n = [p for p in objects if '/icu/i18n/' in p]
    icudata = [p for p in objects if '/icu/data/' in p]
    assert (len(common),len(i18n),icudata) == (176,191,['../../../config/external/icu/data/icu_data.o'])
    return dict(phases=phases,phaseCount=22,allOriginalRawZeroAndRecordedCleanupClean=True,descriptorJoins=110,
                ownedProcessRecords=events,diskSamples=samples,minimumSampledFreeBytes=minimum,startFreeBytes=result['startFreeBytes'],endFreeBytes=result['endFreeBytes'],
                sampledDiskIsNotMeasuredPeak=True,sourceHead=FORK,trackedSourceDiffExactlyPatch=True,untrackedSourceAbsenceProved=False,
                staticMembers=533,mergedMembers=555,extraMergedObjects=merged[533:],icuCommonObjects=176,icuI18nObjects=191,icuDataObjects=['icu_data.o'],
                generatedIntlHeader=True,generatedIcu4xDefine=True,generatedV8IntlCompileDefine=True,wholeCompilerArgvClosureClaimed=False,
                historicDriverSha256=DRIVER_SHA,sourcePatch=patch_summary,engineOrGuestExecuted=False,runtimeAdmission=False)


class HashReader:
    def __init__(self,stream):
        self.stream,self.hash,self.bytes=stream,hashlib.sha256(),0
    def read(self,n):
        data=self.stream.read(n);self.hash.update(data);self.bytes+=len(data);return data
    def discard(self,n):
        while n:
            data=self.read(min(n,4*1024**2));assert data;n-=len(data)


def ar_members(reader,size):
    assert reader.read(8) == b'!<arch>\n'
    names=[];longnames=b''
    while reader.bytes < size:
        header=reader.read(60)
        assert len(header)==60 and header[58:]==b'`\n'
        raw=header[:16].decode('ascii').rstrip()
        count=int(header[48:58]);remaining=count
        if raw=='//':
            longnames=reader.read(count);remaining=0;name=None
        elif raw in ('/','/SYM64/'):
            name=None
        elif raw.startswith('#1/'):
            length=int(raw[3:]);assert length<=remaining
            name=reader.read(length).rstrip(b'\0').decode();remaining-=length
            if name.startswith('__.SYMDEF'):name=None
        elif raw.startswith('/') and raw[1:].isdigit():
            start=int(raw[1:]);assert start<len(longnames)
            end=longnames.find(b'/\n',start);assert end>=start;name=longnames[start:end].decode()
        else:name=raw.removesuffix('/')
        reader.discard(remaining)
        if count%2:assert reader.read(1)==b'\n'
        if name is not None:names.append(name)
    assert reader.bytes==size
    return names


def audit_zip_binary(zip_path,data):
    result=json.loads(data['result.json']);summaries=[]
    assert file_digest(zip_path)==dict(bytes=227965139,sha256=ZIP_SHA)
    with zipfile.ZipFile(zip_path) as original:
        for name,field,rows,prefix in [
            ('spidermonkey-static-release-intl-savedframe-eval.tar.gz','distributionArchive',result['distributionFiles'],'/home/runner/work/_temp/spidermonkey-intl/spidermonkey-dist-release-intl-savedframe-eval/'),
            ('intl-ffi-sources.tar.gz','ffiSourceArchive',result['ffiSourceFiles'],'/home/runner/work/_temp/spidermonkey-intl/project/deps/spidermonkey-source/')]:
            info=original.getinfo(name);assert info.file_size==result[field]['bytes']
            expected={r['path'][len(prefix):]:r for r in rows if r['path'].startswith(prefix)};assert len(expected)==len(rows)
            seen=set();directories=[];extras=[];library=None;headers=[];installed={}
            with original.open(info) as compressed_stream:
                compressed=HashReader(compressed_stream)
                with tarfile.open(fileobj=compressed,mode='r|gz') as archive:
                    all_names=set()
                    for member in archive:
                        member_name=safe(member.name);assert member_name not in all_names;all_names.add(member_name)
                        assert member.isdir() or member.isfile()
                        if member.isdir():directories.append(member_name);continue
                        logical=member_name
                        if field=='distributionArchive':
                            assert logical.startswith('spidermonkey-dist-release-intl-savedframe-eval/')
                            logical=logical[len('spidermonkey-dist-release-intl-savedframe-eval/'):]
                        stream=HashReader(archive.extractfile(member))
                        if logical=='libspidermonkey.a':
                            members=ar_members(stream,member.size)
                            assert members==data['merged-members/command.log'].decode().splitlines()
                            library=dict(bytes=member.size,sha256=stream.hash.hexdigest(),memberCount=len(members),memberListMatchesActualMergedRaw=True)
                            assert library['sha256']=='ca04fe5e1673676d9085e86c9354b2cce0dd91f0f839f01b5c8eacdfb8b82d75'
                        elif logical in ['include/js-config.h','include/js-confdefs.h','include/js/SavedFrameAPI.h']:
                            installed[logical]=stream.read(member.size)
                        else:stream.discard(member.size)
                        actual=dict(bytes=stream.bytes,sha256=stream.hash.hexdigest());assert stream.bytes==member.size
                        if logical in expected:
                            assert actual=={k:expected[logical][k] for k in ['bytes','sha256']};seen.add(logical)
                        else:
                            assert field=='ffiSourceArchive' and logical in ['upstream-provenance/Cargo.toml','upstream-provenance/Cargo.lock','upstream-provenance/.cargo/config.toml.in']
                            extras.append(dict(path=logical,**actual))
                        headers.append(dict(path=member_name,bytes=member.size,mode=member.mode,type='regular'))
                compressed.discard(info.file_size-compressed.bytes)
                assert dict(bytes=compressed.bytes,sha256=compressed.hash.hexdigest())=={k:result[field][k] for k in ['bytes','sha256']}
            assert seen==set(expected)
            if field=='distributionArchive':
                assert library and installed['include/js/SavedFrameAPI.h']==data['savedframe-patch-source/after/js/public/SavedFrameAPI.h']
                assert installed['include/js-confdefs.h']==data['generated/js/src/js-confdefs.h']
                for h in ['include/js-config.h','include/js-confdefs.h']:
                    assert re.search(rb'^#define\s+JS_HAS_INTL_API\s+1\s*$',installed[h],re.M)
                assert re.search(rb'^#define JS_HAS_SAVEDFRAME_IS_EVAL 1$',installed['include/js/SavedFrameAPI.h'],re.M)
                assert result['installedSavedFrameApiHeader']==dict(path=prefix+'include/js/SavedFrameAPI.h',**digest(installed['include/js/SavedFrameAPI.h']))
            else:assert len(extras)==3
            summaries.append(dict(path=name,bytes=compressed.bytes,sha256=compressed.hash.hexdigest(),regularFiles=len(headers),directoryHeaders=len(directories),
                                  reportedFiles=len(expected),allReportedFileHashesMatch=True,additionalProvenanceFiles=extras,library=library,
                                  installedHeadersMatchActualPatchedSource=field=='distributionArchive',tarRegularHeaders=headers,binaryExtractedToDisk=False))
    return summaries


def audit_symbol(root,data):
    report=json.loads((root/'symbol-review.json').read_text())
    authority=json.loads((root/'symbol-authority.json').read_text())
    assert report['passed'] and report['errors']==[] and report['rawToolExitCode']==0 and report['protectedInputsUnchanged']
    assert report['engineOrGuestExecuted'] is False and report['archiveMembersExecuted'] is False and report['symbolRuntimeSemanticsProved'] is False
    assert digest((root/'symbol-authority.json').read_bytes())=={k:report['authority'][k] for k in ['bytes','sha256']}
    raw={}
    with tarfile.open(root/'symbol-raw.tar.gz','r|gz') as archive:
        for member in archive:
            name=safe(member.name);assert member.isfile() and name not in raw;raw[name]=archive.extractfile(member).read()
    assert digest(raw['terminal.json'])=={k:report['terminal'][k] for k in ['bytes','sha256']}
    terminal=json.loads(raw['terminal.json']);started=json.loads(raw['started.json'])
    assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
    assert not terminal['timeout'] and not terminal['forcedCleanup']
    assert all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
    for stream in ['stdout','stderr']:assert digest(raw[stream+'.log'])=={k:terminal[stream][k] for k in ['bytes','sha256']}
    assert started['argv']==authority['argv'] and started['timeoutSeconds']==authority['timeoutSeconds']==120
    assert all(flag in authority['argv'] for flag in ['--defined-only','--extern-only','--print-file-name','--format=posix'])
    assert authority['nativeCompilationAllowed'] is False and authority['engineOrGuestExecutionAllowed'] is False
    result=json.loads(data['result.json']);library=next(r for r in result['distributionFiles'] if r['path'].endswith('/libspidermonkey.a'))
    assert {k:report['library'][k] for k in ['bytes','sha256']}=={k:library[k] for k in ['bytes','sha256']}
    matches=[line for line in raw['stdout.log'].decode().splitlines() if 'GetSavedFrameIsEval' in line]
    assert matches==report['definedExternalSymbolLines'] and len(matches)==1 and re.search(r'\s[TW]\s',matches[0])
    return dict(definedExternalSymbolMetadataObserved=True,exactDefinedSymbolLine=matches[0],rawToolExitCode=0,
                originalOwnedMonitorSeconds=120,protectedInputsUnchanged=True,engineOrGuestExecuted=False,
                runtimeSemanticsProved=False,sdkBinaryMatchedAuthenticatedArchiveMember=authority['sdkArchiveMemberMatchesCurrentBinary'],
                dynamicSystemLibraryClosureAttestationClaimed=False)




def check(root,artifact_zip=None):
    root=Path(root)
    family=root/'index.json'
    if family.exists():
        files=json.loads(family.read_text())['files']
        assert len({r['path'] for r in files})==len(files)
        assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}=={r['path'] for r in files}|{'index.json'}
        for ref in files:
            name=safe(ref['path'])
            assert file_digest(root/name)=={k:ref[k] for k in ['bytes','sha256']}
    index=json.loads((root/'payload-index.json').read_text())
    assert index['artifactZip']==dict(bytes=227965139,sha256=ZIP_SHA)
    bundle=root/index['textBundle']['path']
    assert file_digest(bundle)=={k:index['textBundle'][k] for k in ['bytes','sha256']}
    expected={r['path']:r for r in index['entries'] if r['role']=='text'}
    assert len(expected)==1447 and len(index['entries'])==1449
    assert {r['path'] for r in index['entries'] if r['role']=='external-binary-reference'}=={'spidermonkey-static-release-intl-savedframe-eval.tar.gz','intl-ffi-sources.tar.gz'}
    data={}
    with tarfile.open(bundle,'r|gz') as archive:
        for member in archive:
            name=safe(member.name);assert member.isfile() and name not in data and name in expected
            raw=archive.extractfile(member).read();assert digest(raw)=={k:expected[name][k] for k in ['bytes','sha256']}
            raw.decode('utf-8');data[name]=raw
    assert set(data)==set(expected)
    run=json.loads((root/'github-run.json').read_text());artifacts=json.loads((root/'github-artifacts.json').read_text())['artifacts']
    assert run['id']==42281671898 and run['head_sha']==HEAD and run['status']=='completed' and run['conclusion']=='success'
    artifact=next(x for x in artifacts if x['id']==13536973897)
    assert artifact['digest']=='sha256:'+ZIP_SHA and artifact['size_in_bytes']==227965139 and artifact['workflow_run']['head_sha']==HEAD
    summary=audit_text(data,(root/'historic-build-driver.py').read_bytes())
    summary.update(textPayloads=1447,textPayloadBytes=sum(len(b) for b in data.values()),artifactId=13536973897,githubRun=42281671898,
                   binaryArchivesIndependentlyStreamed=artifact_zip is not None,sourceCodeExecuted=False)
    if artifact_zip is not None:summary['binaryAudit']=audit_zip_binary(artifact_zip,data)
    summary['symbolMetadata']=audit_symbol(root,data)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data',nargs='?',default=str(Path(__file__).resolve().parent))
    parser.add_argument('--artifact-zip')
    args=parser.parse_args()
    value=check(args.data,args.artifact_zip)
    print(json.dumps(value,indent=2))
