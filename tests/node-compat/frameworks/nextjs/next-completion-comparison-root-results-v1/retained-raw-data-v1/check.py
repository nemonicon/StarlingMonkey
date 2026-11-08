"""Portable copied-DATA reader. No arguments, original paths, Source imports/eval or target actions."""
import collections
import hashlib
import io
import json
from pathlib import Path
import stat
from pathlib import PurePosixPath
import zlib

MAX_STDOUT = 8388608
MAX_SOURCE = 131072
MAX_MARKERS = 131072
MAX_TOTAL_INPUT = 134217728
ORDER = ['stock', 'a', 'b', 'c', 'd', 'stock', 'd', 'c', 'b', 'a']
SAFE = 9007199254740991
KNOWN_MARKERS = {'NEXT_GUEST_RESPONSE_COMPLETION_V1', 'NEXT_GUEST_PROMISE_COMPLETION_V1'}
NORMAL_KEYS = set('marker version sequence lane token method path event phase readBytes readChunks flags caughtType'.split())
LOGGER_KEYS = set('marker version sequence lane token method path event'.split())
CAUGHT_TYPES = {'undefined', 'object', 'boolean', 'number', 'bigint', 'string', 'symbol', 'function', 'null'}
PHASES = {'adapter-enter': '-', 'classic-enter': '-', 'response-finish': '-', 'response-close': '-',
          'adapter-read-eof': 'response-read', 'output-child-dispose-returned': 'output-child-dispose',
          'outgoing-body-finish-returned': 'outgoing-body-finish', 'adapter-post-cleanup': 'post-cleanup',
          'adapter-normal-return-site': 'return-site'}


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


def validate_frame(line, contract):
    require(line.endswith(b'\n') and len(line) <= 512, 'Marker LF/512-byte fence')
    require(all(32 <= byte <= 126 for byte in line[:-1]), 'Marker must be printable ASCII JSON')
    frame = decode(line[:-1].decode('ascii'))
    require(type(frame) is dict and frame['marker'] == contract['marker'], 'Marker identity')
    require(type(frame['version']) is int and frame['version'] == 1, 'Marker version')
    require(type(frame['sequence']) is int and 1 <= frame['sequence'] <= 256, 'Per-instance sequence bound')
    if frame['lane'] == 'logger':
        require(set(frame) == LOGGER_KEYS and type(frame['token']) is int and frame['token'] == 0 and
                frame['method'] == frame['path'] == '-' and
                frame['event'] in ['logger-error', 'logger-truncated'], 'Logger record schema')
        require(frame['event'] != 'logger-truncated' or frame['sequence'] == 256,
                'Truncation uses the reserved final attempt')
        return frame
    require(set(frame) == NORMAL_KEYS and frame['lane'] in ['adapter', 'classic'], 'Normal record schema')
    require(frame['sequence'] <= 255, 'Normal records leave the reserved final attempt')
    require(type(frame['token']) is int and 1 <= frame['token'] <= SAFE, 'Local token')
    require((frame['method'], frame['path']) in
            {(row['method'], row['pathname']) for row in contract['routeAdmissions']}, 'Selected route')
    require(frame['event'] in contract['lanes'][frame['lane']]['events'], 'Lane event')
    for key in ['readBytes', 'readChunks', 'flags']:
        require(type(frame[key]) is int and 0 <= frame[key] <= SAFE, 'Exact nonnegative integer field')
    require(frame['caughtType'] in CAUGHT_TYPES | {'-'}, 'Caught type only')
    if frame['event'] == 'adapter-catch':
        require(frame['phase'] in ['request', 'web-handler', 'response-setup', 'response-outparam',
                'response-read', 'output-child-dispose', 'outgoing-body-finish'] and
                frame['flags'] <= 7 and frame['caughtType'] in CAUGHT_TYPES, 'Adapter catch fields')
    else:
        require(frame['phase'] == PHASES[frame['event']], 'Source phase')
    if frame['lane'] == 'classic' or frame['event'] == 'adapter-enter':
        require(frame['readBytes'] == frame['readChunks'] == frame['flags'] == 0 and
                frame['caughtType'] == '-', 'Entry/classic scalar fields')
    if frame['event'] in ['adapter-read-eof', 'output-child-dispose-returned',
                          'outgoing-body-finish-returned']:
        require(frame['flags'] == 0 and frame['caughtType'] == '-', 'Normal terminal fields')
    if frame['event'] == 'adapter-post-cleanup':
        require(frame['flags'] <= 3 and ((frame['flags'] & 1) != 0) ==
                (frame['caughtType'] != '-'), 'Post-cleanup flags/type')
    if frame['event'] == 'adapter-normal-return-site':
        require(frame['flags'] <= 7 and frame['caughtType'] == '-', 'Normal-return flags/type')
    return frame



HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = '0f6f8a502f641c829387320374d51e7838749cc80515f0185cc30d286da70d6f'
MAX_FILE = 20971520
MAX_PAYLOAD = 134217728


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


def capture_complete(server, raw):
    descriptor_matches(raw, server['stdout'])
    c = server['stdoutCapture']
    require(server['command'][1:3] == ['serve','--no-logging-prefix'] and
            server['exit'] == {'code':0,'signal':None,'error':None} and
            c['state'] == 'RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1' and
            c['limitBytes'] == MAX_STDOUT and c['path'] == server['stdout']['path'] and
            c['completeWriteBytes'] == c['lastReservedWriteCeiling'] == c['fileBytes'] == len(raw) and
            all(c[k] is True for k in ['pipeEof','fileClosed','fileBoundVerified','finalized','complete']) and
            all(c[k] is False for k in ['overflow','partialWritePossible','unretainedBytesUnknown']) and
            c['errors'] == [] and c['rejectedWholeChunkBytes'] is None and
            server['stdoutCaptureScope'] == 'complete raw stream', 'Complete capture before parsing')


def main():
    manifest_path = HERE / 'manifest.json'
    raw, manifest_stamp = copied_bytes('manifest.json', manifest_path.lstat().st_size)
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, 'Pinned manifest SHA256')
    manifest = decode(raw)
    require(manifest['schemaVersion'] == 1 and manifest['maximumFileBytes'] == MAX_FILE and
            manifest['maximumTotalPayloadBytes'] == MAX_PAYLOAD and
            manifest['payloadBytes'] <= MAX_PAYLOAD, 'Finite copied corpus budget')
    sizes = [row['copy']['bytes'] for row in manifest['files']]
    require(type(manifest['payloadBytes']) is int and
            all(type(size) is int and 0 <= size <= MAX_FILE for size in sizes) and
            sum(sizes) == manifest['payloadBytes'] <= MAX_PAYLOAD and
            len(sizes) == manifest['fileCount'], 'Aggregate declared payload fence before payload reads')
    originals, current, paths, inodes, old_inodes = {}, {}, set(), set(), set()
    total = pngs = 0
    for row in manifest['files']:
        rel = row['copy']['path']
        require(rel.startswith('files/') and rel not in paths and row['original']['path'] not in originals,
                'Unique copy and documentary original labels')
        data, s = copied_bytes(rel, row['copy']['bytes'])
        descriptor_matches(data, row['original']); descriptor_matches(data, row['copy'])
        old, copied = row['originalPhysicalBookends'], row['copyPhysicalAtCuration']
        require(old[3] == copied[3] == 1 and old[:2] != copied[:2] and
                tuple(old[:2]) not in old_inodes and s[:2] not in inodes and
                stat.S_ISREG(old[2]) and stat.S_ISREG(copied[2]) and
                oct(stat.S_IMODE(old[2])) == row['originalMode'] == row['copiedModeAtCuration'],
                'Historical independent identities/modes, current no aliases')
        if rel.endswith('.png'): png_fence(data); pngs += 1
        originals[row['original']['path']] = data
        old_inodes.add(tuple(old[:2]));inodes.add(s[:2]);current[rel]=s;paths.add(rel);total+=len(data)
    require(total == manifest['payloadBytes'] and len(paths) == manifest['fileCount'], 'Exact payload totals')
    expected_files = paths | {'manifest.json','check.py','README.md'}
    expected_dirs = {'.'}
    for name in expected_files:
        p = PurePosixPath(name).parent
        while str(p) != '.': expected_dirs.add(str(p));p=p.parent
    actual_files,actual_dirs=set(),{'.'}
    for p in HERE.rglob('*'):
        s=p.lstat();require(not stat.S_ISLNK(s.st_mode),'No corpus symlinks')
        if stat.S_ISREG(s.st_mode):require(s.st_nlink==1,'No corpus hardlinks');actual_files.add(p.relative_to(HERE).as_posix())
        else:require(stat.S_ISDIR(s.st_mode),'No corpus special files');actual_dirs.add(p.relative_to(HERE).as_posix())
    require(actual_files==expected_files and actual_dirs==expected_dirs,'Exact current file/directory membership')
    for namespace in manifest['completeOriginalNamespaces']:
        prefix=namespace['originalRoot']+'/'
        selected={name[len(prefix):] for name in originals if name.startswith(prefix) and
                  not any(name[len(prefix):]==x or name[len(prefix):].startswith(x+'/')
                          for x in namespace['excludedDirectoryPrefixes'])}
        require(selected==set(namespace['files']) and namespace['completeSelectedNamespaceAtCopyCut'] is True,
                'Complete retained original selected namespace')
    roles=manifest['roles']
    def content(role):return originals[roles[role]]
    def obj(role):return decode(content(role))
    def checked(descriptor):
        data=originals[descriptor['path']];descriptor_matches(data,descriptor);return data
    cohort,authority,plan=map(obj,['cohortResult','cohortAuthority','cohortPlan'])
    primary,owner,marker=map(obj,['primaryReview','ownerReview','markerReview'])
    descriptor_matches(content('cohortAuthority'),cohort['cohortAuthority'])
    descriptor_matches(content('cohortPlan'),cohort['comparisonPlan'])
    require(primary['verifiedDataReviewPassed'] is owner['verifiedOwnerBrowserCaptureDataPassed'] is True and
            marker['verifiedMarkerSchemaAndInputJoinsPassed'] is True and
            primary['cohortResult']==owner['cohortResult']==marker['cohortResult'], 'Three final DATA review roles')
    checked(primary['cohortResult']);checked(primary['complementaryOwnerBrowserCaptureReview']);checked(primary['complementaryMarkerReview'])
    require(primary['complementaryOwnerBrowserCaptureReview']['path']==roles['ownerReview'] and
            primary['complementaryMarkerReview']['path']==roles['markerReview'], 'Coordinated final reviews')
    for d in cohort['driverSourceProofs']:checked(d)
    require([t['arm'] for t in cohort['trials']]==ORDER and
            [t['sequence'] for t in cohort['trials']]==list(range(1,11)) and
            len(plan['trials'])==len(authority['trials'])==len(manifest['trials'])==10, 'Fixed complete ten-trial order')
    require(cohort['automaticRetry'] is cohort['replacementTrials'] is False and
            cohort['fullNextAccepted'] is primary['fullNextAccepted'] is False, 'No retry/replacement or acceptance waiver')
    def original_owner(started_path,terminal_path):
        s,t=decode(originals[started_path]),decode(originals[terminal_path])
        require(s['pid']==t['pid'] and s['authority']==t['authority'] and clean_owner(t),'Original terminal clean')
        prefix=str(PurePosixPath(terminal_path).parent)+'/'
        snapshots=sorted(name for name in originals if name.startswith(prefix) and
                         '/' not in name[len(prefix):] and re_owned(name[len(prefix):]))
        require(len(snapshots)==len(t['observedProcesses']) and
                all(decode(originals[name])['sequence']==i and decode(originals[name])['process']==t['observedProcesses'][i]
                    for i,name in enumerate(snapshots)), 'Complete original owned snapshots')
        checked(t['stdout']);checked(t['stderr']);return s,t
    outer_s,outer_t=original_owner(roles['outerStarted'],roles['outerTerminal'])
    require(outer_t['rawExitCode']==0 and outer_s['timeoutSeconds']==7200 and
            outer_t['authority']==cohort['cohortAuthority'] and outer_t['pid']==cohort['controllerPid'], 'Original cohort owner')
    analysis,observation=obj('markerAnalysis'),obj('markerObservation')
    checked(observation['argv']);checked(observation['source']);checked(observation['stdout']);checked(observation['stderr'])
    require(observation['rawExitCode']==0 and len(checked(observation['stderr']))==0 and
            marker['analysisStdout']==observation['stdout'] and
            marker['analyzer']==observation['source'], 'Retained offline analysis exit and exact output')
    for d in analysis['inputDescriptors'].values():
        descriptor_matches(originals[d['argument']],dict(path=d['argument'],sha256=d['sha256'],bytes=d['bytes']))
    contract=obj('responseSchema');require(contract['marker']=='NEXT_GUEST_RESPONSE_COMPLETION_V1','C/D schema identity only')
    accepted=[];strict_failed=[];marker_total=0;raw_clients=0;http_bodies=0;native_caps=0;summary=[]
    for position,record in enumerate(manifest['trials']):
        trial=cohort['trials'][position];scheduled=plan['trials'][position];issued=authority['trials'][position]
        require(all(trial[k]==record[k]==scheduled[k] for k in ['sequence','arm','runId']) and
                issued['trial']==scheduled and issued['authority']==trial['authority'], 'Exact issued fixed trial roles')
        outcome=trial['outcome'];require(trial['status']=='completed-valid-profile' and outcome['valid'] is True,'Actual completed profile remains recorded')
        for key in ['terminal','observation','result','client']:checked(outcome[key])
        a=decode(originals[record['authority']]);descriptor_matches(originals[record['authority']],trial['authority'])
        s,t=original_owner(record['monitorRoot']+'/started.json',record['terminal'])
        require(s['timeoutSeconds']==record['ownerSeconds'] and t['rawExitCode']==outcome['rawExitCode'] and
                t['authority']==trial['authority'],'Original per-trial owner/cap/raw')
        result=decode(originals[record['result']]);client=decode(originals[record['clientResult']]);obs=decode(originals[record['observation']])
        require(obs['rawExitCode']==t['rawExitCode'] and obs['terminal']==outcome['terminal'] and
                obs['result']==outcome['result'] and obs['ownedGroupsClean'] is True and
                obs['protectedInputsPreserved'] is True,'Original observation joins')
        predicate=obs['hostExperimentPassed'] if trial['arm']=='stock' else obs['passed']
        original_pass=t['rawExitCode']==0 and predicate is True and result['passed'] is True
        require(outcome['originalAllPassed'] is original_pass,'Rawzero plus genuine observation/result acceptance')
        if original_pass:accepted.append(trial['sequence'])
        require(len(client['http'])==24 and client['portableCacheValidation']['passed'] is True and
                client['portableCacheValidation']['checks']==52 and
                client['supplementalValidation']['passed'] is True and client['supplementalValidation']['checks']==80,
                'Recorded original/new profile booleans/counts')
        for response in client['http']:
            body=originals[record['rawRoot']+'/responses/'+response['id']+'.txt']
            require(len(body)==response['bodyBytes'] and hashlib.sha256(body).hexdigest()==response['bodySha256'] and
                    response['passed'] is True,'All retained original HTTP bodies')
            http_bodies+=1
        require(outcome['legacyCacheInvalidation']==client['cacheInvalidation'] and
                outcome['browserStrictPassed']==client['browser']['passed'] and
                outcome['browserFunctionalPassed']==client['browser']['functionalPassed'], 'Preserved current legacy/browser gates')
        if not client['browser']['passed']:strict_failed.append(trial['sequence'])
        require(client['browser']['browserClosed'] is True and client['streaming']['complete'] is True and
                client['streaming']['readyChunk']>client['streaming']['shellChunk']>=0 and
                type(client['streaming']['chunks']) is int and client['streaming']['chunks']==5,'Closed browser and complete incremental stream gate')
        raw_clients+=record['rawFiles']
        marker_row=analysis['trials'][position]
        require(marker_row['sequence']==trial['sequence'] and marker_row['originalOutcomeDocumentary']==outcome,
                'Marker analysis ordered outcomes preserved')
        if trial['arm']!='stock':
            native_caps+=1;require(result['rootAuthority']==trial['authority'] and
                    result['sourceIndex']==authority['actorBindings'][trial['arm']],'Actual native artifact Source roles')
            actor=decode(checked(result['sourceIndex']));require(result['inputEntry']==actor['inputEntry'] and
                    result['inputSourceIndex']==actor['inputSourceIndex'],'Actual selected input, no artifact retarget')
            checked(result['inputEntry']);checked(result['inputSourceIndex']);review=decode(checked(actor['acceptedConstructionReview']))
            require(review['inputEntry']==result['inputEntry'] and review['component']==result['component'],'Genuine selected INIT artifact')
            if trial['arm']=='a':require('deployedCompletionDiagnosticObserved' not in review,'A missing review field remains missing')
            else:require(review['deployedCompletionDiagnosticObserved'] is False,'Genuine present INIT flag')
            guard=decode(originals[record['fullWorldGuard']]);require(guard['unchanged'] is guard['nativeInputsPreserved'] is True and
                    guard['before']==guard['after'] and guard['authority']==trial['authority'],'Documentary native/world final receipt')
            raw=originals[record['rawStdout']];capture_complete(result['server'],raw)
            require(outcome['stdoutCapture']==result['server']['stdoutCapture'],'Final capture metadata equality')
            parsed=[];events=collections.Counter();seqs=collections.Counter();offset=ordinary=0
            for number,line in enumerate(io.BytesIO(raw),1):
                at=offset;offset+=len(line)
                require(b'NEXT_GUEST_PROMISE_COMPLETION_V1' not in line,'No projected child logger')
                if b'NEXT_GUEST_RESPONSE_COMPLETION_V1' not in line:ordinary+=1;continue
                frame=validate_frame(line,contract);parsed.append(dict(line=number,byteStart=at,byteEndExclusive=offset,bytes=len(line),record=frame));events[frame['event']]+=1;seqs[frame['sequence']]+=1
            require(offset==len(raw),'Full retained raw byte accounting')
            derived=marker_row['markerAnalysis'];require(parsed==derived['records'] and dict(sorted(events.items()))==derived['eventCounts'] and
                    len(parsed)==derived['markerRecords'] and ordinary==derived['ordinaryLines'] and
                    {str(k):v for k,v in seqs.items() if v>1}==derived['repeatedSequenceValues'],'Independent copied-byte marker derivation')
            require((trial['arm'] in 'cd') or not parsed,'A/B no-response-logger applicability')
            marker_total+=len(parsed)
        summary.append(dict(sequence=trial['sequence'],arm=trial['arm'],originalPassed=original_pass,strictBrowserPassed=client['browser']['passed'],legacyCachePassed=client['cacheInvalidation']['passed']))
    require(primary['originalAcceptedTrialSequences']==accepted and primary['strictBrowserFailedTrialSequences']==strict_failed and
            cohort['originalAllPassed'] is all(x['originalPassed'] for x in summary) and
            marker_total==analysis['markerRecords']==marker['aggregate']['CDResponseMarkerRecords'], 'Final qualified summary joins')
    require(stamp(manifest_path)==manifest_stamp and all(stamp(HERE/name)==s for name,s in current.items()), 'Final current copy read bookends')
    print(json.dumps(dict(retainedDataVerified=True,payloadFiles=len(paths),payloadBytes=total,completeSelectedNamespaces=len(manifest['completeOriginalNamespaces']),trialRows=10,nativeCompleteCaptures=native_caps,rawClientFiles=raw_clients,httpBodyHashes=http_bodies,pngFiles=pngs,markerRecords=marker_total,originalAcceptedTrialSequences=accepted,strictBrowserFailedTrialSequences=strict_failed,originalAllPassed=cohort['originalAllPassed'],originalPathsRead=False,sourceEvaluated=False,helperGuardNodeOrTargetInvoked=False,omittedNativeApplicationPackagePayloadsRevalidated=False,full52Or80CaseSemanticsReevaluated=False,markerPartitionsAuthenticateInstance=False,promiseNativeHostOrCauseProved=False,fullNextAccepted=False,historicalModesDocumentary=True,currentCheckoutModesObservedOnly=True),sort_keys=True))


def re_owned(name):
    return len(name)==15 and name.startswith('owned-') and name.endswith('.json') and name[6:10].isdigit()


if __name__=='__main__':
    main()
