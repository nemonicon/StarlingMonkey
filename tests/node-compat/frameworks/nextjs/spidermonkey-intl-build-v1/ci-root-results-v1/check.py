"""Portable, standard-library-only reader for retained CI DATA; executes no tools.

Default mode verifies the complete text bundle. --binary-root additionally
streams the two external tar archives; it never extracts a library to disk.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import io
import json
import re
import tarfile

HEAD = 'dc7bad5c36306368fd8a2816136f02f959aed0ee'
FORK = '9dab3d6f643e926a340c391ea30968e940390dec'
DRIVER_SHA = 'a5486e5011284fcdad6945952b2d088387effb50c49a86395d1fb296af9ae108'
ZIP_SHA = 'ae81c73ecb7b9e93eb08e265d64836e68e3d838d9bbc8bb602ca79a3cbc8342f'
ORIGINAL_EVIDENCE = '/home/runner/work/_temp/spidermonkey-intl/evidence/'
PHASES = ['host-compiler','cmake-version','sdk-download','sdk-extract','rust-install','rust-version','cargo-version','sdk-version','python-version','cbindgen-install','cbindgen-version','configure','source-revision','build','static-members','merged-members','source-clean']


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


def audit_text(data, historic_driver):
    def obj(name):
        return json.loads(data[name])
    def descriptor(ref, name):
        assert ref == dict(path=ORIGINAL_EVIDENCE+name, **digest(data[name])), name
    result = obj('result.json')
    assert result['state'] == 'guest-library-built-engine-and-runtime-pending'
    assert result['forkCommit'] == FORK and result['componentOrEngineExecuted'] is False and result['runtimeAccepted'] is False
    assert result['github'] == dict(GITHUB_SHA=HEAD,GITHUB_RUN_ID='42272037547',GITHUB_RUN_ATTEMPT='1')
    assert [p['name'] for p in result['phases']] == PHASES
    assert digest(historic_driver) == dict(bytes=12953,sha256=DRIVER_SHA)
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
        assert authority['driver'] == dict(path='/home/runner/work/StarlingMonkey/StarlingMonkey/tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/build.py',bytes=12953,sha256=DRIVER_SHA)
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
    assert events == 1247 and samples == 2114
    assert result['startFreeBytes'] == 88822759424 and result['endFreeBytes'] == 77543546880
    assert result['startRequirementBytes'] == 20*1024**3 and result['stopFloorBytes'] == 4*1024**3
    assert result['startFreeBytes'] >= result['startRequirementBytes'] and result['endFreeBytes'] >= result['stopFloorBytes']
    assert data['source-revision/command.log'].decode().strip() == FORK
    assert data['source-clean/command.log'] == b''
    assert obj('source-clean/packet.json')['argv'][-3:] == ['diff','--exit-code','HEAD']
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
    return dict(phases=phases,phaseCount=17,allOriginalRawZeroAndRecordedCleanupClean=True,descriptorJoins=85,
                ownedProcessRecords=events,diskSamples=samples,minimumSampledFreeBytes=minimum,startFreeBytes=result['startFreeBytes'],endFreeBytes=result['endFreeBytes'],
                sampledDiskIsNotMeasuredPeak=True,sourceHead=FORK,trackedSourceDiffEmpty=True,untrackedSourceAbsenceProved=False,
                staticMembers=533,mergedMembers=555,extraMergedObjects=merged[533:],icuCommonObjects=176,icuI18nObjects=191,icuDataObjects=['icu_data.o'],
                generatedIntlHeader=True,generatedIcu4xDefine=True,generatedV8IntlCompileDefine=True,wholeCompilerArgvClosureClaimed=False,
                historicDriverSha256=DRIVER_SHA,engineOrGuestExecuted=False,runtimeAdmission=False)


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


def audit_binary(binary_root,data):
    result=json.loads(data['result.json'])
    binary_root=Path(binary_root)
    summaries=[]
    for name,field,rows,prefix in [
        ('spidermonkey-static-release-intl.tar.gz','distributionArchive',result['distributionFiles'],'/home/runner/work/_temp/spidermonkey-intl/spidermonkey-dist-release-intl/'),
        ('intl-ffi-sources.tar.gz','ffiSourceArchive',result['ffiSourceFiles'],'/home/runner/work/_temp/spidermonkey-intl/project/deps/spidermonkey-source/')]:
        path=binary_root/name
        assert file_digest(path)=={k:result[field][k] for k in ['bytes','sha256']}
        expected={r['path'][len(prefix):]:r for r in rows if r['path'].startswith(prefix)}
        assert len(expected)==len(rows)
        seen=set();directories=[];extras=[];library=None;jsconfig=False;headers=[]
        with tarfile.open(path,'r|gz') as archive:
            all_names=set()
            for member in archive:
                member_name=safe(member.name)
                assert member_name not in all_names;all_names.add(member_name)
                assert member.isdir() or member.isfile(), member.name
                if member.isdir():directories.append(member_name);continue
                logical=member_name
                if field=='distributionArchive':
                    assert logical.startswith('spidermonkey-dist-release-intl/')
                    logical=logical[len('spidermonkey-dist-release-intl/'):]
                stream=HashReader(archive.extractfile(member))
                if logical=='libspidermonkey.a':
                    members=ar_members(stream,member.size)
                    assert members==data['merged-members/command.log'].decode().splitlines()
                    library=dict(bytes=member.size,sha256=stream.hash.hexdigest(),memberCount=len(members),memberListMatchesActualMergedRaw=True)
                elif logical=='include/js-config.h':
                    raw=stream.read(member.size)
                    assert re.search(rb'^#define\s+JS_HAS_INTL_API\s+1\s*$',raw,re.M);jsconfig=True
                else:stream.discard(member.size)
                actual=dict(bytes=stream.bytes,sha256=stream.hash.hexdigest())
                assert stream.bytes==member.size
                if logical in expected:
                    assert actual=={k:expected[logical][k] for k in ['bytes','sha256']};seen.add(logical)
                else:
                    assert field=='ffiSourceArchive' and logical in ['upstream-provenance/Cargo.toml','upstream-provenance/Cargo.lock','upstream-provenance/.cargo/config.toml.in']
                    extras.append(dict(path=logical,**actual))
                headers.append(dict(path=member_name,bytes=member.size,mode=member.mode,type='regular'))
        assert seen==set(expected)
        if field=='distributionArchive':assert library and jsconfig
        else:assert len(extras)==3
        summaries.append(dict(path=name,**file_digest(path),regularFiles=len(headers),directoryHeaders=len(directories),allReportedFileHashesMatch=True,
                              reportedFiles=len(expected),additionalProvenanceFiles=extras,library=library,intlInstalledHeader=jsconfig,tarRegularHeaders=headers))
    return summaries


def check(root,binary_root=None):
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
    assert index['artifactZip']==dict(bytes=227191494,sha256=ZIP_SHA)
    bundle=root/index['textBundle']['path']
    assert file_digest(bundle)=={k:index['textBundle'][k] for k in ['bytes','sha256']}
    expected={r['path']:r for r in index['entries'] if r['role']=='text'}
    assert len(expected)==1374 and len(index['entries'])==1376
    assert {r['path'] for r in index['entries'] if r['role']=='external-binary-reference'}=={'spidermonkey-static-release-intl.tar.gz','intl-ffi-sources.tar.gz'}
    data={}
    with tarfile.open(bundle,'r|gz') as archive:
        for member in archive:
            name=safe(member.name);assert member.isfile() and name not in data and name in expected
            raw=archive.extractfile(member).read();assert digest(raw)=={k:expected[name][k] for k in ['bytes','sha256']}
            raw.decode('utf-8');data[name]=raw
    assert set(data)==set(expected)
    run=json.loads((root/'github-run.json').read_text());artifacts=json.loads((root/'github-artifacts.json').read_text())['artifacts']
    assert run['id']==42272037547 and run['head_sha']==HEAD and run['status']=='completed' and run['conclusion']=='success'
    artifact=next(x for x in artifacts if x['id']==13534080477)
    assert artifact['digest']=='sha256:'+ZIP_SHA and artifact['size_in_bytes']==227191494 and artifact['workflow_run']['head_sha']==HEAD
    summary=audit_text(data,(root/'historic-build-driver.py').read_bytes())
    summary.update(textPayloads=1374,textPayloadBytes=sum(len(b) for b in data.values()),artifactId=13534080477,githubRun=42272037547,
                   binaryArchivesIndependentlyStreamed=binary_root is not None,sourceCodeExecuted=False)
    if binary_root is not None:summary['binaryAudit']=audit_binary(binary_root,data)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data',nargs='?',default=str(Path(__file__).resolve().parent))
    parser.add_argument('--binary-root')
    args=parser.parse_args()
    value=check(args.data,args.binary_root)
    print(json.dumps(value,indent=2))
