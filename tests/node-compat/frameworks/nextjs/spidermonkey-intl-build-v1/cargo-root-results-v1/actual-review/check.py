"""Portable Cargo DATA reader. No Cargo, native helper, or payload execution."""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import json
import tarfile
import tomllib


def digest(data):
    return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def safe(name):
    p=PurePosixPath(name)
    assert name and not p.is_absolute() and '..' not in p.parts and '\\' not in name and str(p)==name
    return name


def graph(metadata):
    packages={p['id']:p for p in metadata['packages']}
    def key(identifier):
        p=packages[identifier]
        return (p['name'],p['version'],p['source'])
    return {key(n['id']):dict(features=sorted(n['features']),dependencies=sorted(key(d['pkg']) for d in n['deps'])) for n in metadata['resolve']['nodes']}


def verify(root):
    root=Path(root)
    if (root/'index.json').exists():
        family=json.loads((root/'index.json').read_text())['files']
        assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}=={r['path'] for r in family}|{'index.json'}
        for r in family:assert digest((root/safe(r['path'])).read_bytes())=={k:r[k] for k in ['bytes','sha256']}
    index=json.loads((root/'payload-index.json').read_text())
    assert digest((root/'data.tar.gz').read_bytes())=={k:index['bundle'][k] for k in ['bytes','sha256']}
    entries={r['path']:r for r in index['entries']};assert len(entries)==len(index['entries'])
    data={}
    with tarfile.open(root/'data.tar.gz','r|gz') as archive:
        for member in archive:
            name=safe(member.name)
            assert member.isfile() and name not in data and name in entries
            value=archive.extractfile(member).read();value.decode('utf-8')
            assert digest(value)=={k:entries[name][k] for k in ['bytes','sha256']}
            data[name]=value
    assert set(data)==set(entries)
    origins={r['originalPath']:r['path'] for r in index['entries'] if r.get('originalPath')}
    def obj(name):return json.loads(data[name])
    def ref(row):
        name=origins[row['path']]
        assert digest(data[name])=={k:row[k] for k in ['bytes','sha256']}
        return name
    phase_summaries=[];observed=0
    for version,name,authority_name,expected_cargo,expected_wrapper in [
        (1,'resolve-online','resolve-online-authority.json',101,1),
        (2,'resolve-online','resolve-online-v2-authority.json',0,0),
        (2,'vendor-online','vendor-v2-authority.json',0,0),
        (2,'metadata-offline','offline-v2-authority.json',0,0)]:
        base=f'v{version}/phases/{name}/'
        result=obj(base+'result.json');terminal=obj(ref(result['terminal']));authority=obj(ref(result['authority']))
        assert ref(result['authority'])=='root/'+authority_name
        assert authority['state']=='ROOT_CARGO_METADATA_VENDOR_PHASE_V1'
        assert authority['nativeCompilationAllowed'] is False and authority['guestExecutionAllowed'] is False
        plan=obj(ref(authority['plan']));ref(authority['helper']);ref(authority['caller'])
        packet=obj(base+'packet.json');command=packet['command'];started=obj(base+'owned-monitor/started.json');worker=obj(base+'worker-result.json')
        assert packet['authority']==result['authority'] and packet['command']==next(c for c in plan['commands'] if c['id']==authority['phase'])
        assert result['rawCargoExitCode']==obj(base+'cargo-status.json')['rawCargoExitCode']==expected_cargo
        assert terminal['rawExitCode']==worker['rawChildExitCode']==expected_wrapper
        assert result['passed'] is (version==2) and result['nativeOrGuestExecuted'] is False
        protection=result['sourceProtection']
        assert protection==dict(sourceAndPreparedInputsUnchanged=True,originalAndCopiedSourceFiles=2296,compilationOrCargoInvoked=False)
        assert terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup'] and not terminal['timeout']
        assert all(terminal[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
        assert worker['lifecycleComplete'] and not worker['stopReason'] and not worker['sigtermReceived'] and worker['launcherErrors']==[]
        cleanup=worker['ownedGroupCleanup'];assert cleanup['complete'] and cleanup['events']==cleanup['errors']==[]
        assert cleanup['rawChildExitCode']==expected_wrapper
        ref(terminal['stdout']);ref(terminal['stderr']);ref(result['stdout']);ref(result['stderr'])
        assert started['authority']==result['authority'] and started['argv'][3]==authority['caller']['path']
        assert '--worker' in started['argv'] and started['argv'][-1]==str(Path(authority['output'])/'packet.json')
        assert terminal['authority']==result['authority']
        assert command['argv'][1] in ['metadata','vendor'] and command['environment']['HOME']=='/Users/dan'
        events=[obj(k) for k in sorted(data) if k.startswith(base+'owned-monitor/owned-')]
        assert [e['sequence'] for e in events]==list(range(len(events)))
        assert [e['process'] for e in events]==terminal['observedProcesses'];observed+=len(events)
        if version==2:
            assert result['errors']==[] and result['beforeSourceProtection']==protection
            assert result['callerAuthorityPlanHelperUnchanged'] and result['finalSourceProtectionAttempted']
            ref(result['workerResult']);ref(result['cargoStatus'])
            assert started['timeoutSeconds']==command['seconds']==result['timeoutPolicy']['outerOperationalSeconds']
        else:
            assert started['timeoutSeconds']==command['seconds']+60
            assert data[ref(result['stdout'])]==b'' and b'smallvec' in data[ref(result['stderr'])]
            assert b'1.14.0' in data[ref(result['stderr'])] and b'1.15.1' in data[ref(result['stderr'])]
        phase_summaries.append(dict(version=version,phase=name,rawCargoExitCode=expected_cargo,rawWrapperExitCode=expected_wrapper,
                                   originalPassed=result['passed'],ownedGroupsClean=True,recordedSourceFilesUnchanged=2296,
                                   rawStdout=digest(data[ref(result['stdout'])]),rawStderr=digest(data[ref(result['stderr'])]),observedProcesses=len(events),
                                   operationalSeconds=started['timeoutSeconds']))
    parse=lambda name:tomllib.loads(data[name].decode())
    key=lambda p:(p['name'],p['version'],p.get('source'))
    old_rows=parse('v2/old-aggregate.lock')['package'];actual_rows=parse('v2/project/Cargo.lock')['package']
    old={key(p):p for p in old_rows};actual={key(p):p for p in actual_rows}
    assert len(old)==49 and len(actual)==84 and set(old)<=set(actual)
    assert digest(data['v2/project/Cargo.lock'])==dict(bytes=20626,sha256='dc098f33febee6952974705077140ff543ca37eb1cedad2e0b07496646c3bd61')
    for k,p in old.items():
        assert actual[k].get('checksum')==p.get('checksum')
    constraints=obj('v2/fork-lock-constraints.json')['conservativeUpstreamLockRows']
    assert set(actual)<=set(old)|{key(p) for p in constraints}|{('icu_capi','2.0.0',None),('unicode-bidi-ffi','0.1.0',None),('icu_segmenter_data','2.0.0',None)}
    plan=obj('v2/plan.json');redirects=plan['seedReconciliation'];assert len(redirects)==10
    for r in redirects:
        assert any(k[0]==r['name'] and k[1]==r['selectedOldVersion'] for k in actual)
        assert not any(k[0]==r['name'] and k[1]==r['droppedForkVersion'] for k in actual)
    online=obj('v2/online-metadata.json');offline=obj('v2/offline-metadata.json')
    assert graph(online)==graph(offline) and len(graph(online))==84
    manifest=parse('v2/project/Cargo.toml')
    assert manifest['lib']=={'crate-type':['staticlib'],'path':'rust-staticlib.rs'}
    names=['rust-encoding','rust-hooks','rust-url','multipart','icu_capi','unicode-bidi-ffi']
    assert set(manifest['dependencies'])==set(names)
    assert manifest['dependencies']['icu_capi']['default-features'] is False
    assert manifest['dependencies']['icu_capi']['features']==['any_provider','compiled_data','segmenter','calendar']
    assert manifest['dependencies']['multipart']['features']==['capi','simd']
    assert data['v2/project/rust-staticlib.rs'].decode().splitlines()==['pub use '+n.replace('-','_')+';' for n in names]
    for p in online['packages']:
        if p['name']=='icu_capi':
            node=next(n for n in online['resolve']['nodes'] if n['id']==p['id'])
            assert set(node['features'])=={'any_provider','compiled_data','segmenter','calendar'}
    for n in ['audit-online-v2.json','audit-vendor-v2.json','audit-offline-v2.json']:
        a=obj('root/'+n);assert a['lockPolicyPassed'] and a['unexpectedIdentities']==a['oldPackageIdentitiesRemovedOrChanged']==a['sharedFamilyReconciliationMismatches']==[]
        assert a['actualLock']==dict(path='/private/tmp/starling-node-compat/next-intl-cargo-resolution-v2/project/Cargo.lock',**digest(data['v2/project/Cargo.lock']))
    final=obj('root/audit-offline-v2.json');assert final['mozillaPatchedBidiRustAndManifestMatch'] and final['offlineLogicalGraphAndFeaturesMatch']
    assert final['vendorChecksums']==dict(packages=76,files=2278,bytes=35510599,allRecordedChecksumsMatch=True)
    # Reuse the already-retained old-control ledger, never duplicate its payloads.
    refs=json.loads((root/'references.json').read_text())
    for r in refs['files']:
        p=root/r['relativePath'];assert digest(p.read_bytes())=={k:r[k] for k in ['bytes','sha256']}
    old_index=json.loads((root/'../old-feature-control-v1-retained-index.json').read_text())
    for r in old_index['files']:assert digest((root/'..'/safe(r['path'])).read_bytes())=={k:r[k] for k in ['bytes','sha256']}
    ledger=json.loads((root/'../old-feature-control-v1-authority.json').read_text())['validatedVendorInputRows']
    ledger={r['path']:r for r in ledger};assert len(ledger)==2354
    vendor=obj('vendor-checksum-evidence.json');assert len(vendor['packages'])==76
    covered=set();source_bytes=0;source_files=0
    for p in vendor['packages']:
        sums=obj(p['retainedChecksumPath']);identity=(p['name'],p['version'],p['source'])
        assert identity in actual and identity not in covered;covered.add(identity)
        assert sums['package']==actual[identity].get('checksum')
        directory='/private/tmp/starling-node-compat/next-intl-cargo-resolution-v2/vendor/'+p['directory']+'/'
        checksum_ref=ledger[directory+'.cargo-checksum.json']
        assert digest(data[p['retainedChecksumPath']])=={k:checksum_ref[k] for k in ['bytes','sha256']}
        assert {x for x in ledger if x.startswith(directory)}=={directory+n for n in sums['files']}|{directory+'.cargo-checksum.json'}
        for name,sha in sums['files'].items():
            r=ledger[directory+safe(name)];assert r['sha256']==sha;source_bytes+=r['bytes'];source_files+=1
    assert covered=={k for k in actual if k[2] is not None}
    assert (source_files,source_bytes)==(2278,35510599)
    assert vendor['sourceFilesRehashedDuringCuration']==2354 and vendor['allActualFileHashesMatchedRetainedLedger'] is True
    assert vendor['bidiParsedManifestMatch'] is True and vendor['bidiRustSourceFilesMatch'] is True
    assert vendor['bidiMozillaManifestCanonicalSha256']==vendor['bidiVendorManifestCanonicalSha256']
    assert vendor['bidiMozillaRustRows']==vendor['bidiVendorRustRows']
    feature_review=json.loads((root/'../old-feature-control-v1-data-review.json').read_text())
    assert feature_review['originalCollectorPassed'] is False and feature_review['verifiedPassed'] is True
    return dict(schemaVersion=1,state='COMBINED_INTL_CARGO_RETAINED_DATA_REVIEW_PASSED_V1',verifiedPassed=True,phases=phase_summaries,
                firstUnderlyingResultPassed=False,firstCargoRawExitCode=101,successorCargoRawExitCodes=[0,0,0],recordedSourcePreservationFilesPerPhase=2296,
                oldLockPackages=49,combinedLockPackages=84,preservedOldIdentities=49,newPackageIdentities=35,explicitSharedFamilyReconciliations=10,
                onlineOfflineLogicalGraphAndFeaturesMatch=True,icuCapiFeatures=['any_provider','compiled_data','segmenter','calendar'],
                rootStaticlibCount=1,rootDirectDependencies=6,vendorPackages=76,vendorSourceFiles=2278,vendorAllRecordedFiles=2354,vendorSourceBytes=35510599,
                vendorChecksumEvidenceOnlyNoPayloadsCopied=True,bidiAlignmentRecordedAndHashJoined=True,ownedProcessRecords=observed,
                oldFeatureControlReferencedNotDuplicated=True,sharedOldFeatureChanges=feature_review['sharedFeatureChanges'],
                serdeDeriveNewlySelectedInMetadata=True,noNewCargoExecuted=True,noHelperOrHistoricSourceCodeExecuted=True,
                nativeCompilationAccepted=False,engineRelinkAccepted=False,guestOrRuntimeAccepted=False,
                v1CollectorExceptionGapQualified='V1 monitor/status collection could skip final checks on an unexpected exception; actual Cargo101 returned normally and retained successful final source protection.',
                v1TimeoutQualification='V1 allowed600+60 operational seconds before monitor cleanup; V2 bounds600/600/300 including worker startup, cleanup additional.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('data',nargs='?',default=str(Path(__file__).resolve().parent))
    args=parser.parse_args();print(json.dumps(verify(args.data),indent=2))
