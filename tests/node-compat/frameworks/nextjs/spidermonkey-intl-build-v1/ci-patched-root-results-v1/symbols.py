"""One authorized SDK llvm-nm metadata query. Never executes archive members."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
import tarfile
import traceback

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[5]
ROOT=Path('/private/tmp/starling-node-compat/next-intl-ci-run42281671898-v1')
SDK=Path('/private/tmp/starling-node-compat/next-native-build-v5/extracted-wasi-sdk/wasi-sdk-30.0-arm64-macos')
ARCHIVE=Path('/private/tmp/starling-node-compat/next-native-build-v5/archives/wasi-sdk-30.0-arm64-macos.tar.gz')
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    path=Path(path)
    for p in (path,*path.parents):assert not p.is_symlink()
    s=path.stat();assert stat.S_ISREG(s.st_mode)
    h=hashlib.sha256();n=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024**2),b''):h.update(block);n+=len(block)
    t=path.stat();assert (s.st_ino,s.st_dev,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_ino,t.st_dev,t.st_size,t.st_mtime_ns,t.st_ctime_ns)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=n)


def save(path,value):
    with Path(path).open('x') as out:json.dump(value,out,indent=2);out.write('\n')


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    work=ROOT/'symbol-metadata-v1';assert not work.exists()
    report=dict(schemaVersion=1,state='PATCHED_INTL_LIBRARY_DEFINED_SYMBOL_METADATA_V1',passed=False,errors=[],engineOrGuestExecuted=False,archiveMembersExecuted=False)
    protected=[]
    try:
        root_review=json.loads((ROOT/'root-review.json').read_text())
        library=Path(root_review['smLibrary']['path']);assert row(library)==root_review['smLibrary']
        nm=SDK/'bin/llvm-nm';nmr=row(nm)
        assert nmr['sha256']=='0f0dfccb3778ec756b3bcbfe69574cdddfb2a6da2ae92c5bc1df1d1d6d3a591c' and nmr['bytes']==152040
        archive_ref=row(ARCHIVE);assert archive_ref['sha256']=='2c2ed99296857e60fd14c3f40fe226231f296409502491094704089c31a16740'
        matched=False
        with tarfile.open(ARCHIVE,'r|gz') as archive:
            for member in archive:
                if member.name=='wasi-sdk-30.0-arm64-macos/bin/llvm-nm':
                    assert member.isfile();b=archive.extractfile(member).read()
                    assert len(b)==nmr['bytes'] and hashlib.sha256(b).hexdigest()==nmr['sha256'];matched=True;break
        assert matched
        monitor_ref=row(MONITOR);assert monitor_ref['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
        protected=[row(Path(__file__).resolve()),row(ROOT/'root-review.json'),root_review['smLibrary'],nmr,archive_ref,monitor_ref]
        protected += [root_review[k] for k in ['smSavedFrameHeader','smConfigHeader','smConfdefsHeader']]
        for ref in protected:assert row(ref['path'])==ref
        work.mkdir(mode=0o700);(work/'owned-monitor').mkdir(mode=0o700)
        argv=[str(nm),'--defined-only','--extern-only','--print-file-name','--format=posix',str(library)]
        env={k:os.environ[k] for k in ['HOME','home','CODEX_HOME','USER','LOGNAME'] if k in os.environ}
        env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C')
        authority=dict(schemaVersion=1,scope='Parent Root task explicitly authorizes one SDK llvm-nm read-only metadata query under original0af120s; no engine/native/guest execution',
                       argv=argv,cwd=str(work),environment=env,timeoutSeconds=120,protectedInputs=protected,sdkArchiveMemberMatchesCurrentBinary=True,
                       nativeCompilationAllowed=False,engineOrGuestExecutionAllowed=False,dynamicSystemLibraryClosureAttestationClaimed=False)
        save(HERE/'symbol-authority.json',authority);ar=row(HERE/'symbol-authority.json')
        spec=importlib.util.spec_from_file_location('actual_original_symbol_monitor',MONITOR);monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
        terminal=monitor.monitor(argv,str(work),env,work/'owned-monitor',120,ar)
        report['terminal']=row(work/'owned-monitor/terminal.json');report['authority']=ar
        assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
        assert not terminal['timeout'] and not terminal['forcedCleanup']
        assert all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
        lines=(work/'owned-monitor/stdout.log').read_text().splitlines()
        matches=[line for line in lines if 'GetSavedFrameIsEval' in line]
        assert len(matches)==1 and re.search(r'\s[TW]\s',matches[0]),matches
        report.update(rawToolExitCode=0,definedExternalSymbolLines=matches,tool=nm.as_posix(),library=root_review['smLibrary'],
                      symbolDefinitionMetadataObserved=True,symbolRuntimeSemanticsProved=False,ciOriginalPhasesUnaffected=True)
    except BaseException as error:
        report['errors'].append(dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    finally:
        try:
            assert protected
            for ref in protected:assert row(ref['path'])==ref
            report['protectedInputsUnchanged']=True
        except BaseException as error:report['errors'].append(dict(stage='final-protection',type=type(error).__name__,message=str(error)))
        report['passed']=report.get('symbolDefinitionMetadataObserved') is True and not report['errors'] and report.get('protectedInputsUnchanged') is True
        save(HERE/'symbol-review.json',report)
        if (work/'owned-monitor').exists():
            with (HERE/'symbol-raw.tar.gz').open('xb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz,tarfile.open(fileobj=gz,mode='w|') as tar:
                for p in sorted((work/'owned-monitor').iterdir()):
                    assert p.is_file();tar.add(p,arcname=p.name,recursive=False)
        print(json.dumps(report),flush=True)
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
