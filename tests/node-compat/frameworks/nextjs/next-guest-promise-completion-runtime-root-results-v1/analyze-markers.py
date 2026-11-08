"""Bounded offline DATA only. Explicit inputs; no Source imports/eval or original-path I/O."""
import argparse
import collections
import hashlib
import io
import json
from pathlib import Path
import stat

MAX_STDOUT = 8388608
MAX_SOURCE = 131072
MAX_MARKERS = 131072
SAFE = 9007199254740991
KNOWN_MARKERS = {'NEXT_GUEST_RESPONSE_COMPLETION_V1', 'NEXT_GUEST_PROMISE_COMPLETION_V1'}
NORMAL_KEYS = set('marker version sequence lane token method path event phase readBytes readChunks flags caughtType'.split())
LOGGER_KEYS = set('marker version sequence lane token method path event'.split())
CAUGHT_TYPES = {'undefined', 'object', 'boolean', 'number', 'bigint', 'string', 'symbol', 'function', 'null'}
PHASES = {'adapter-enter': '-', 'classic-enter': '-', 'response-finish': '-', 'response-close': '-',
          'adapter-read-eof': 'response-read', 'output-child-dispose-returned': 'output-child-dispose',
          'outgoing-body-finish-returned': 'outgoing-body-finish', 'adapter-post-cleanup': 'post-cleanup',
          'adapter-normal-return-site': 'return-site', 'child-handler-promise-fulfilled': 'handler-await',
          'child-handler-promise-rejected': 'handler-await'}


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


def read_bounded(path, limit):
    # Only explicit CLI paths are read. Embedded descriptor paths are labels, never opened.
    path = Path(path).absolute()
    before = stamp(path)
    require(path.resolve() == path and stat.S_ISREG(before[2]) and before[3] == 1,
            'Canonical ordinary unique file required')
    require(0 <= before[4] <= limit, 'Input exceeds finite byte bound')
    data = path.read_bytes()
    require(len(data) == before[4] and stamp(path) == before, 'Input read bookend changed')
    return path, data, before


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
                          'outgoing-body-finish-returned', 'child-handler-promise-fulfilled']:
        require(frame['flags'] == 0 and frame['caughtType'] == '-', 'Normal terminal fields')
    if frame['event'] == 'adapter-post-cleanup':
        require(frame['flags'] <= 3 and ((frame['flags'] & 1) != 0) ==
                (frame['caughtType'] != '-'), 'Post-cleanup flags/type')
    if frame['event'] == 'adapter-normal-return-site':
        require(frame['flags'] <= 7 and frame['caughtType'] == '-', 'Normal-return flags/type')
    if frame['event'] == 'child-handler-promise-rejected':
        require(frame['flags'] == 0 and frame['caughtType'] in CAUGHT_TYPES, 'Child rejection fields')
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['stdout', 'result', 'terminal', 'contract', 'entry', 'entry-index']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    inputs = {}
    for name, limit in [('stdout', MAX_STDOUT), ('result', 2097152), ('terminal', 8388608),
                        ('contract', MAX_SOURCE), ('entry', MAX_SOURCE), ('entry_index', MAX_SOURCE)]:
        inputs[name] = read_bounded(getattr(args, name), limit)
    raw = inputs['stdout'][1]
    result, terminal, contract, index = (decode(inputs[name][1]) for name in ['result', 'terminal', 'contract', 'entry_index'])
    require(clean_owner(terminal), 'Original owner must be terminal and clean before marker interpretation')
    require(terminal['authority'] == result['rootAuthority'], 'Original owner/result authority join')
    require(type(result['passed']) is bool, 'Runtime result boolean')
    server = result['server']
    descriptor_matches(raw, server['stdout'])
    require(server['command'][1:3] == ['serve', '--no-logging-prefix'], 'Explicit standard no-prefix capture')
    require(server['exit'] == {'code': 0, 'signal': None, 'error': None}, 'Reaped natural server stop')
    capture = server['stdoutCapture']
    require(capture['state'] == 'RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1' and
            capture['path'] == server['stdout']['path'] and capture['limitBytes'] == MAX_STDOUT and
            capture['completeWriteBytes'] == capture['lastReservedWriteCeiling'] == capture['fileBytes'] == len(raw) and
            all(capture[k] is True for k in ['pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized', 'complete']) and
            all(capture[k] is False for k in ['overflow', 'partialWritePossible', 'unretainedBytesUnknown']) and
            capture['errors'] == [] and capture['rejectedWholeChunkBytes'] is None and
            server['stdoutCaptureScope'] == 'complete raw stream', 'Raw stdout must finalize before interpretation')
    descriptor_matches(inputs['entry_index'][1], result['inputSourceIndex'])
    descriptor_matches(inputs['entry'][1], result['inputEntry'])
    for name, role in [('guest-entry.mjs', 'entry'), ('marker-contract.json', 'contract')]:
        members = [row for row in index['files'] if row['path'] == name]
        require(len(members) == 1, 'Exactly one selected indexed Source member')
        descriptor_matches(inputs[role][1], dict(members[0], path=name))
    require(contract['marker'] in KNOWN_MARKERS and contract['limits']['ASCIIOnly'] is True and
            contract['limits']['bytesPerRecordIncludingNewline'] == 512 and
            contract['limits']['recordsPerComponentInstanceIncludingErrorOrTruncation'] == 256,
            'Known versioned marker contract')
    source = inputs['entry'][1].decode('utf8')  # Text witness only, never evaluated.
    is_promise = contract['marker'] == 'NEXT_GUEST_PROMISE_COMPLETION_V1'
    holder_witness = all(text in source for text in ['completionHolder={trace:undefined};',
        'completionHolder.trace=completionTrace;', 'return handleResources(...args,completionHolder);',
        'const value=await handler.handle(incoming,outparam,completionHolder);'])
    require(not is_promise or holder_witness, 'Indexed actual-holder Source witness')
    records, ordinary_samples, errors = [], [], []
    event_counts, sequences = collections.Counter(), collections.Counter()
    ordinary_count = ordinary_bytes = foreign_count = malformed = offset = 0
    marker = contract['marker'].encode('ascii')
    for number, line in enumerate(io.BytesIO(raw), 1):
        location = dict(line=number, byteStart=offset, byteEndExclusive=offset + len(line), bytes=len(line))
        offset += len(line)
        if marker not in line:
            ordinary_count += 1; ordinary_bytes += len(line)
            foreign_count += int(any(other.encode('ascii') in line for other in KNOWN_MARKERS if other != contract['marker']))
            if len(ordinary_samples) < 16:
                ordinary_samples.append(dict(location, sha256=hashlib.sha256(line).hexdigest()))
            continue
        require(len(records) < MAX_MARKERS, 'Finite aggregate marker bound; no silent truncation')
        try:
            frame = validate_frame(line, contract)
        except (ValueError, KeyError, TypeError) as error:
            malformed += 1
            if len(errors) < 16:
                errors.append(dict(location, error=str(error)[:256], sha256=hashlib.sha256(line).hexdigest()))
            continue
        records.append(dict(location, record=frame))
        event_counts[frame['event']] += 1; sequences[frame['sequence']] += 1
    require(offset == len(raw), 'Whole raw byte accounting')
    groups = collections.defaultdict(list)
    for row in records:
        frame = row['record']
        if frame['lane'] != 'logger':
            groups[(frame['lane'], frame['token'], frame['method'], frame['path'])].append(row)
    partitions = []
    for key, rows in groups.items():
        events = collections.Counter(row['record']['event'] for row in rows)
        seq = collections.Counter(row['record']['sequence'] for row in rows)
        expected = contract['lanes'][key[0]]['events']
        partitions.append(dict(descriptiveKey=dict(zip(['lane', 'token', 'method', 'path'], key)),
            records=rows, duplicateEventCounts={k:v for k,v in events.items() if v > 1},
            repeatedSequenceCounts={str(k):v for k,v in seq.items() if v > 1},
            sequenceIncreasingInThisFileSubset=all(a['record']['sequence'] < b['record']['sequence'] for a,b in zip(rows, rows[1:])),
            sitesAbsentFromThisDescriptiveSubset=[name for name in expected if name not in events],
            absentSiteIsNotFailureProof=True, physicalOrCrossInstanceJoinAuthenticated=False))
    for path, _, before in inputs.values():
        require(stamp(path) == before, 'Final selected input read bookend')
    output = dict(schemaVersion=1, state='BOUNDED_GUEST_COMPLETION_MARKER_DATA_ANALYSIS_V1',
        dataParseSucceeded=malformed == foreign_count == 0, rawCaptureReportedComplete=True,
        inputDescriptors={name:dict(argument=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
                          for name,(path,data,_) in inputs.items()},
        originalOwnerRawExitCode=terminal['rawExitCode'], applicationPassed=result['passed'],
        marker=contract['marker'], markerRecords=len(records), newMarkerObserved=bool(records),
        ordinaryLines=ordinary_count, ordinaryBytes=ordinary_bytes, ordinarySamples=ordinary_samples,
        malformedMarkerLines=malformed, foreignKnownMarkerLines=foreign_count, errors=errors,
        maximumMarkerBytesIncludingLf=max((row['bytes'] for row in records), default=None),
        eventCounts=dict(sorted(event_counts.items())), records=records,
        repeatedSequenceValues={str(k):v for k,v in sequences.items() if v > 1},
        descriptivePartitions=partitions,
        explicitHolderSourceReferenceWitnessPresent=holder_witness if is_promise else None,
        sourceReferenceScope='The indexed Source shares the actual trace object through a per-call holder. Raw serialized numbers still do not authenticate physical/cross-instance/cross-lane identity.',
        interpretation='Site records are positive evidence only for their sealed public Source sites. Child fulfillment follows the awaited child call, not whole neutral/export/native/host completion. Rejection may also cover synchronous invocation failure. Read bytes are not written/peer bytes. Missing/error/truncated/colliding or unlogged data remain unobserved.',
        loggerErrors=event_counts['logger-error'], loggerTruncations=event_counts['logger-truncated'],
        noAssumedRouteOrRecordCounts=True, noAssumedFulfillmentOrNoRejection=True,
        allCallsOrLostRecordsAccountedFor=False, physicalHandleOrStoreIdentityProved=False,
        classicAdapterOrOuterInnerJoinProved=False, wholeNeutralOrExportSettledProved=False,
        nativeLoopOrPostCallProved=False, hostTaskOrTcpEofProved=False, uniqueCauseProved=False,
        fullNextAccepted=False, priorFailedGatesAccepted=False, sourceEvaluated=False,
        helperGuardNodeOrActorInvoked=False, embeddedOriginalDescriptorPathsOpened=False)
    print(json.dumps(output, indent=2))
    return 0 if output['dataParseSucceeded'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
