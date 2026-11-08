"""Portable retained-DATA check for ONE stock wasmCloud run; copied paths only, no Source evaluation."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import stat
import zlib

HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = 'dd7c1bb5986b54f88b5f231c9553ee3807b9bfd30a8b56b05d574fed2a385f7c'
MAX_FILE = 20971520
MAX_PAYLOAD = 134217728

def require(value, message):
    if not value:
        raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def decode(data):
    def bad_constant(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=unique_pairs, parse_constant=bad_constant)


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def descriptor_matches(data, descriptor):
    require(type(descriptor) is dict and set(descriptor) == {'path', 'sha256', 'bytes'}, 'Descriptor shape')
    require(type(descriptor['bytes']) is int and descriptor['bytes'] == len(data) and
            descriptor['sha256'] == hashlib.sha256(data).hexdigest(), 'Descriptor bytes/hash mismatch')


def clean_owner(t):
    return (type(t['rawExitCode']) is int and t['timeout'] is False and t['forcedCleanup'] is False and
            t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True and
            all(t[key] == [] for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))


def copied_bytes(relative, size):
    rel = PurePosixPath(relative)
    require(not rel.is_absolute() and '..' not in rel.parts and str(rel) == relative, 'Safe copied relative path')
    path = HERE / relative
    before = stamp(path)
    require(path.resolve() == path and stat.S_ISREG(before[2]) and before[3] == 1 and
            0 <= size <= MAX_FILE and before[4] == size, 'Bounded ordinary independent copy')
    data = path.read_bytes()
    require(len(data) == size and stamp(path) == before, 'Copied file read bookends')
    return data, before


def png_fence(data):
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'PNG signature')
    offset = 8
    seen_end = False
    while offset < len(data):
        require(offset + 12 <= len(data), 'PNG chunk header')
        size = int.from_bytes(data[offset:offset+4], 'big')
        end = offset + 12 + size
        require(end <= len(data), 'PNG chunk length')
        kind = data[offset+4:offset+8]
        require(zlib.crc32(data[offset+4:end-4]) & 0xffffffff == int.from_bytes(data[end-4:end], 'big'), 'PNG CRC')
        offset = end
        if kind == b'IEND':
            require(size == 0 and offset == len(data), 'PNG IEND/tail fence')
            seen_end = True
            break
    require(seen_end, 'PNG IEND required')



def owner_clean(t):
    return (type(t['rawExitCode']) is int and t['timeout'] is False and t['forcedCleanup'] is False and
        t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True and
        all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids']))


def main():
    mp=HERE/'manifest.json';raw,ms=copied_bytes('manifest.json',mp.lstat().st_size)
    require(hashlib.sha256(raw).hexdigest()==MANIFEST_SHA256,'Pinned manifest')
    m=decode(raw);require(m['schemaVersion']==1 and m['primaryAndOwnerReviewsPending'] is False and
        m['maximumFileBytes']==MAX_FILE and m['maximumTotalPayloadBytes']==MAX_PAYLOAD,'Final single-host manifest')
    sizes=[r['copy']['bytes'] for r in m['files']]
    require(type(m['payloadBytes']) is int and all(type(x) is int and 0<=x<=MAX_FILE for x in sizes) and
        sum(sizes)==m['payloadBytes']<=MAX_PAYLOAD and len(sizes)==m['fileCount'],'Aggregate fence before payload reads')
    originals={};paths=set();inodes=set();old_inodes=set();book={};total=pngs=0
    for row in m['files']:
        rel=row['copy']['path'];require(rel.startswith('files/') and rel not in paths and row['original']['path'] not in originals,'Unique copy/original labels')
        data,s=copied_bytes(rel,row['copy']['bytes']);descriptor_matches(data,row['original']);descriptor_matches(data,row['copy'])
        old,copied=row['originalPhysicalBookends'],row['copyPhysicalAtCuration']
        require(old[3]==copied[3]==1 and old[:2]!=copied[:2] and tuple(old[:2]) not in old_inodes and
            s[:2] not in inodes and stat.S_ISREG(old[2]) and stat.S_ISREG(copied[2]) and
            oct(stat.S_IMODE(old[2]))==row['originalMode']==row['copiedModeAtCuration'],'Historical/current alias and mode checks')
        if rel.endswith('.png'):png_fence(data);pngs+=1
        originals[row['original']['path']]=data;paths.add(rel);inodes.add(s[:2]);old_inodes.add(tuple(old[:2]));book[rel]=s;total+=len(data)
    require(total==m['payloadBytes'],'Exact bytes')
    expected_files=paths|{'manifest.json','check.py','README.md'};expected_dirs={'.'}
    for name in expected_files:
        p=PurePosixPath(name).parent
        while str(p)!='.':expected_dirs.add(str(p));p=p.parent
    actual_files=set();actual_dirs={'.'}
    for p in HERE.rglob('*'):
        s=p.lstat();require(not stat.S_ISLNK(s.st_mode),'No corpus symlinks')
        if stat.S_ISREG(s.st_mode):require(s.st_nlink==1,'No corpus hardlinks');actual_files.add(p.relative_to(HERE).as_posix())
        else:require(stat.S_ISDIR(s.st_mode),'No special nodes');actual_dirs.add(p.relative_to(HERE).as_posix())
    require(actual_files==expected_files and actual_dirs==expected_dirs,'Exact corpus membership')
    for ns in m['completeOriginalNamespaces']:
        prefix=ns['originalRoot']+'/'
        require({k[len(prefix):] for k in originals if k.startswith(prefix)}==set(ns['files']) and
            ns['completeOriginalNamespaceAtCopyCut'] is True,'Complete retained monitor/client namespace')
    roles=m['roles']
    def obj(role):return decode(originals[roles[role]])
    def checked(d):
        data=originals[d['path']];descriptor_matches(data,d);return data
    r,a,plan,index=map(obj,['result','authority','actorPlan','actorIndex'])
    primary,owner=map(obj,['primaryReview','ownerReview'])
    require(primary['verifiedDataReviewPassed'] is True and owner['verifiedOwnerConfigBrowserDataPassed'] is True,
        'Genuine held final review DATA flags')
    require(primary['state']=='COORDINATED_STOCK_WASMCLOUD_FULL_CONTRACT_DATA_REVIEW_COMPLETED_UNACCEPTED_V1' and
        owner['state']=='INDEPENDENT_STOCK_WASMCLOUD_FULL_OWNER_CONFIG_BROWSER_DATA_REVIEW_PASSED_V1',
        'Published selected one-host review schema, no aliases')
    checked(primary['actualOwnerBrowserReview'])
    require(primary['actualOwnerBrowserReview']['path']==roles['ownerReview'] and
        primary['rootAuthority']==owner['rootAuthority'] and primary['actorIndex']==owner['actorIndex'],
        'Current primary-to-owner exact role joins')
    for k in ['runtimeAccepted','fullNextAccepted','retainedContractAccepted','nodeParityProved','reliabilityProved','uniqueCauseProved','privateIdentityProved','productionProfilePromoted','priorFailuresReclassified']:
        require(primary[k] is False,'Primary failure/nonacceptance scope preserved')
    checked(primary['actualResult']);checked(owner['actualResult'])
    require(primary['actualResult']==owner['actualResult'] and
        owner['rootAuthority']==r['rootAuthority'],'Final result/authority review roles')
    checked(r['rootAuthority']);checked(r['sourceIndex'])
    require(r['rootAuthority']['path']==roles['authority'] and r['sourceIndex']['path']==roles['actorIndex'] and
        a['plan']['path']==roles['actorPlan'] and a['state']=='ROOT_NEXT_WASMCLOUD_FULL_CONTRACT_AUTHORIZED_V1',
        'Actual stock-host authority/state')
    checked(a['plan'])
    init_review=decode(checked(a['constructionDataReview']))
    require(init_review['state']=='COORDINATED_REAL_NEXT_INTEROP_COMPONENT_INIT_DATA_REVIEW_PASSED_V1' and
        init_review['verifiedPassed'] is init_review['completeReturnedImportAuditVerified'] is True and
        'deployedCompletionDiagnosticObserved' not in init_review and
        init_review['component']==r['component'] and init_review['inputEntry']==r['inputEntry'],
        'Genuine A9256 missing diagnostic field remains absent')
    checked(init_review['complementaryOwnerWorldReview'])
    construction=decode(checked(a['constructionResult']));ctor=decode(checked(construction['rootAuthority']))
    require(len(ctor['metadataExpectedFixedValues'])==31 and len(ctor['engineBuildEvidence'])==39 and
        len(ctor['newSourceEvidence'])==18,'Actual fixed/build/Source metadata role counts, not old projection')
    audit=decode(checked(a['componentAudit']))
    require(audit['passed'] is True and set(audit['emittedImports'])==set(plan['selectedInterfaces']) and
        len(audit['emittedImports'])==len(set(audit['emittedImports']))==13 and
        audit['exports']==['wasi:http/incoming-handler@0.2.10'],'Recorded audited standard13/incoming world')
    actor_root=str(PurePosixPath(roles['actorIndex']).parent)
    for row in index['files']:checked(dict(row,path=actor_root+'/'+row['path']))
    for k in ['coldNextGuestAllowed','localhostServeAllowed','configInspectAllowed','browserAllowed','fullContractClientAllowed']:
        require(a[k] is True,'Exact issued permission')
    for k in ['compilerAllowed','componentConstructionAllowed','externalNetworkAllowed','newServicesAllowed','hostMutationAllowed','retainedContractAcceptanceAllowed','fullNextAcceptanceAllowed','adoptionAllowed']:
        require(a[k] is False,'Preserved false permission')
    require(r['runId']==a['runId'] and r['actualHost']=='stock-wasmCloud-2.11.0' and
        r['passed'] is False and r['retainedContractAcceptance'] is r['fullNextAcceptance'] is r['adoption'] is False,
        'One failed/unaccepted host scope, no baseline/cohort retry')
    s,t,ob=map(obj,['outerStarted','outerTerminal','outerObservation'])
    require(s['pid']==t['pid'] and s['authority']==t['authority']==r['rootAuthority'] and
        s['timeoutSeconds']==600 and owner_clean(t),'Original600 owner/quiescence')
    rootprefix=str(PurePosixPath(roles['outerTerminal']).parent)+'/'
    names=sorted(k for k in originals if k.startswith(rootprefix) and re.fullmatch(r'owned-[0-9]{4}\.json',k[len(rootprefix):]))
    require(len(names)==len(t['observedProcesses']) and
        all(decode(originals[name])['sequence']==i and decode(originals[name])['process']==t['observedProcesses'][i]
            for i,name in enumerate(names)),'All actual owned snapshots')
    checked(t['stdout']);checked(t['stderr']);checked(ob['terminal']);checked(ob['result'])
    require(ob['rawExitCode']==t['rawExitCode'] and ob['ownedGroupsClean'] is ob['protectedInputsPreserved'] is True and
        ob['passed'] is False and t['rawExitCode']==1,'Natural raw1 remains failed despite clean ownership')
    require([c['label'] for c in r['commands']]==['config-show','wash-dev','full-contract-client'],'Exactly three actual direct commands')
    actor_root=str(PurePosixPath(roles['actorIndex']).parent)
    require(s['argv']==[plan['node']['path'],actor_root+'/deploy.mjs',r['rootAuthority']['path']],
        'Original Node actor caller argv')
    empty=r['outputRoot']+'/empty-user-config.json';project=r['outputRoot']+'/project'
    require(r['commands'][0]['argv']==[a['wash']['path'],'--user-config',empty,'-C',project,'--output','json','config','show'] and
        r['commands'][1]['argv']==[a['wash']['path'],'--user-config',empty,'-C',project,'--log-level','info','--meters','duration','dev'] and
        r['commands'][2]['argv']==[plan['node']['path'],plan['clientSource']['path'],a['selfOrigin'],
            r['outputRoot']+'/client',plan['browserTools'],a['runId']], 'Three original direct command argv')
    for c in r['commands']:
        require(c['timeout'] is c['forcedCleanup'] is False and c['exit']['signal'] is c['exit']['error'] is None and
            type(c['exit']['code']) is int,'Original direct-child exit state')
        checked(c['stdout']);checked(c['stderr'])
        require('rawStreamDigestsUnavailable' not in c,'This natural-completion record has actual final direct stream digests')
    require([c['exit']['code'] for c in r['commands']]==[0,0,1] and r['allDirectCliExitsZero'] is False and
        r['server']==r['commands'][1] and r['client']==r['commands'][2] and
        r['server']['shutdownRequested'] is r['server']['sigintSent'] is True and
        'stdoutCapture' not in r['server'],'Direct fd logs are not the Native pump complete-capture schema')
    origin=a['selfOrigin'];match=re.fullmatch(r'http://127\.0\.0\.1:([1-9][0-9]{0,4})',origin)
    require(match is not None and 1<=int(match.group(1))<=65535 and int(match.group(1))!=80,'Canonical exact Root origin')
    require(r['portLease']['origin']==origin and r['portLease']['singleAttempt'] is True and
        r['portLease']['heldThroughConfigInspection'] is True and r['portLease']['fallbackAllowed'] is False and
        r['portLease']['releasedImmediatelyBeforeSingleDevLaunch'] is True,'Actual exact lease boundary')
    selection=obj('portSelection');require(selection['selfOrigin']==origin and selection['selectionBindAttempts']==1 and
        selection['httpRequestsMade']==0 and selection['selectionSocketClosed'] is True,'Documentary original Root port selection')
    for d in r['configFiles']:checked(d)
    configured=r['configured'];effective=r['effectiveConfiguration'];shown=decode(checked(r['commands'][0]['stdout']))
    require(shown['success'] is True and shown['data']==effective and r['configVerifiedBeforeDev'] is True,
        'Actual config-show output before dev')
    require(configured['version']==effective['version']=='2.11.0' and effective['build']==configured['build'],'Selected pinned config version/build')
    for k in ['address','command','component_path','service','volumes']:require(effective['dev'][k]==configured['dev'][k],'Effective selected dev field')
    for k in ['components','plugins','host_plugins']:require(effective['dev'].get(k,[])==[],'No additional service/plugin')
    require(effective['workload']['allowedHosts']==configured['workload']['allowedHosts']==[origin+'/'] and
        effective['workload']['allowedIpNameLookups']==effective['workload']['allowedHostLoopbackPorts']==[] and
        effective['workload']['environment']['config']==configured['workload']['environment']['config']==
            {'STARLING_NEXT_ORIGIN':origin,'NODE_ENV':'production','NEXT_TELEMETRY_DISABLED':'1'} and
        effective['wit']['skip_fetch'] is True,'One normalized self-origin-only config/environment')
    require(r['readiness']['tcpConnect'] is r['readiness']['workloadRegistered'] is True and
        r['readiness']['extraHttpRequests']==0, 'Recorded public workload-registration/TCP readiness only')
    guard=obj('guard');require(guard['unchanged'] is guard['nativeInputsPreserved'] is True and
        guard['before']==guard['after'] and guard['authority']==r['rootAuthority'],'Held whole-world/native receipt documentary')
    require(r['originalInputsPreserved'] is r['readonlyAppPreserved'] is True and
        r['readonlyWasiDescriptorRightsProved'] is False,'Physicalreadonly, not descriptor capability proof')
    client=obj('clientResult');require(r['client']['result']['path']==roles['clientResult'],'Actual full-client result role');checked(r['client']['result'])
    require(client['passed'] is False and len(client['http'])==24 and
        client['portableCacheValidation']['passed'] is True and client['portableCacheValidation']['checks']==52 and
        client['supplementalValidation']['passed'] is True and client['supplementalValidation']['checks']==80,'Preserve recorded profile values')
    rawroot=str(PurePosixPath(roles['clientResult']).parent)
    for response in client['http']:
        body=originals[rawroot+'/responses/'+response['id']+'.txt']
        require(len(body)==response['bodyBytes'] and hashlib.sha256(body).hexdigest()==response['bodySha256'] and
            response['passed'] is True,'All original HTTP body hashes')
    require(client['cacheInvalidation']['passed'] is False and client['browser']['passed'] is False and
        client['browser']['functionalPassed'] is True and client['browser']['browserClosed'] is True and
        type(client['streaming']['chunks']) is int and client['streaming']['chunks']==5 and
        client['streaming']['complete'] is True and client['streaming']['readyChunk']>client['streaming']['shellChunk']>=0,
        'Failedlegacy/strict and positive functional/stream gates remain separate')
    checked(client['browser']['netlog']['file'])
    require(client['browser']['netlog']['completeJson'] is True and client['browser']['netlog']['normalBrowserCloseRequired'] is True,
        'Retained full NetLog; no history-complete or TCP inference')
    require(stamp(mp)==ms and all(stamp(HERE/name)==s for name,s in book.items()),'Final selected copy read bookends')
    print(json.dumps(dict(retainedDataVerified=True,payloadFiles=len(paths),payloadBytes=total,selectedOriginalNamespaces=len(m['completeOriginalNamespaces']),singleHost='stock wasmCloud2.11.0',originalOwnerRawExitCode=t['rawExitCode'],directChildRawExitCodes=[0,0,1],finalDirectStreamFiles=6,clientRawFiles=sum(1 for k in originals if k.startswith(rawroot+'/')),httpBodyHashes=24,pngFiles=pngs,legacyCachePassed=False,strictBrowserPassed=False,functionalBrowserPassed=True,originalAllPassed=False,nativePumpCaptureCompleteClaimed=False,readinessBoundIsLifetimeBound=False,markerAnalysisApplicable=False,originalPathsRead=False,sourceEvaluated=False,helperGuardNodeOrTargetInvoked=False,omittedNativeAppPackagePayloadsRevalidated=False,full52Or80CaseSemanticsReevaluated=False,physicalStorePromiseHostOrCauseProved=False,fullNextAccepted=False,historicalModesDocumentary=True,currentCheckoutModesObservedOnly=True),sort_keys=True))


if __name__=='__main__':
    main()
