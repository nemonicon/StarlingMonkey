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
                          'outgoing-body-finish-returned']:
        require(frame['flags'] == 0 and frame['caughtType'] == '-', 'Normal terminal fields')
    if frame['event'] == 'adapter-post-cleanup':
        require(frame['flags'] <= 3 and ((frame['flags'] & 1) != 0) ==
                (frame['caughtType'] != '-'), 'Post-cleanup flags/type')
    if frame['event'] == 'adapter-normal-return-site':
        require(frame['flags'] <= 7 and frame['caughtType'] == '-', 'Normal-return flags/type')
    return frame



def analyze_raw(raw, contract, applicable):
    records, errors, ordinary = [], [], []
    events, sequences = collections.Counter(), collections.Counter()
    malformed = foreign = ordinary_count = ordinary_bytes = offset = 0
    for number, line in enumerate(io.BytesIO(raw), 1):
        location = dict(line=number, byteStart=offset, byteEndExclusive=offset + len(line), bytes=len(line))
        offset += len(line)
        response = b'NEXT_GUEST_RESPONSE_COMPLETION_V1' in line
        promise = b'NEXT_GUEST_PROMISE_COMPLETION_V1' in line
        if not response:
            ordinary_count += 1; ordinary_bytes += len(line); foreign += int(promise)
            if len(ordinary) < 16:
                ordinary.append(dict(location, sha256=hashlib.sha256(line).hexdigest()))
            continue
        require(len(records) + malformed < MAX_MARKERS, 'Finite marker aggregate bound; no silent drop')
        try:
            frame = validate_frame(line, contract)
        except (ValueError, KeyError, TypeError) as error:
            malformed += 1
            if len(errors) < 16:
                errors.append(dict(location, error=str(error)[:256], sha256=hashlib.sha256(line).hexdigest()))
            continue
        records.append(dict(location, record=frame))
        events[frame['event']] += 1; sequences[frame['sequence']] += 1
    require(offset == len(raw), 'Whole raw accounting')
    groups = collections.defaultdict(list)
    for row in records:
        f = row['record']
        if f['lane'] != 'logger':
            groups[(f['lane'], f['token'], f['method'], f['path'])].append(row)
    partitions = []
    for key, rows in groups.items():
        counts = collections.Counter(row['record']['event'] for row in rows)
        partitions.append(dict(descriptiveKey=dict(zip(['lane', 'token', 'method', 'path'], key)),
            lineNumbers=[row['line'] for row in rows], eventCounts=dict(sorted(counts.items())),
            repeatedEvents={k:v for k,v in counts.items() if v > 1},
            absentSites=[name for name in contract['lanes'][key[0]]['events'] if name not in counts],
            absentSiteIsNotFailureProof=True, physicalOrCrossInstanceJoinAuthenticated=False,
            sourceTraceOrderProved=False))
    return dict(markerApplicability='selected response schema' if applicable else 'not applicable to selected A/B Source',
        dataParseSucceeded=malformed == foreign == 0 and (applicable or not records),
        markerRecords=len(records), ordinaryLines=ordinary_count, ordinaryBytes=ordinary_bytes,
        ordinarySamples=ordinary, malformedMarkerLines=malformed, foreignPromiseMarkerLines=foreign,
        unexpectedResponseMarkerRecords=0 if applicable else len(records),
        maximumMarkerBytesIncludingLf=max((row['bytes'] for row in records), default=None),
        errors=errors, eventCounts=dict(sorted(events.items())), records=records,
        repeatedSequenceValues={str(k):v for k,v in sequences.items() if v > 1},
        descriptivePartitions=partitions, loggerErrors=events['logger-error'],
        loggerTruncations=events['logger-truncated'], observationCompletenessProved=False,
        numericPartitionsAuthenticateInstance=False, allCallsOrLostRecordsAccountedFor=False)


def capture_complete(server, raw):
    descriptor_matches(raw, server['stdout'])
    require(server['command'][1:3] == ['serve', '--no-logging-prefix'], 'Standard explicit no-prefix capture')
    require(server['exit'] == {'code':0, 'signal':None, 'error':None}, 'Original server natural SIGINT cleanup result')
    c = server['stdoutCapture']
    require(c['state'] == 'RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1' and
        c['path'] == server['stdout']['path'] and c['limitBytes'] == MAX_STDOUT and
        c['completeWriteBytes'] == c['lastReservedWriteCeiling'] == c['fileBytes'] == len(raw) and
        all(c[k] is True for k in ['pipeEof','fileClosed','fileBoundVerified','finalized','complete']) and
        all(c[k] is False for k in ['overflow','partialWritePossible','unretainedBytesUnknown']) and
        c['errors'] == [] and c['rejectedWholeChunkBytes'] is None and
        server['stdoutCaptureScope'] == 'complete raw stream', 'Complete finalized raw capture required before parse')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['cohort', 'authority', 'plan', 'outer-terminal', 'contract']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--arm', nargs=4, action='append', metavar=('ARM','ACTOR_INDEX','ENTRY_INDEX','ENTRY'), required=True)
    parser.add_argument('--trial', nargs=4, action='append', metavar=('SEQUENCE','RESULT','TERMINAL','STDOUT'), default=[])
    args = parser.parse_args()
    explicit = {}
    for name in ['cohort','authority','plan','outer_terminal','contract']:
        explicit[name] = (getattr(args,name), MAX_SOURCE if name == 'contract' else 8388608)
    arms, trials = {}, {}
    for arm, actor_index, entry_index, entry in args.arm:
        require(arm in 'abcd' and len(arm) == 1 and arm not in arms, 'Exact unique arm CLI')
        arms[arm] = (actor_index, entry_index, entry)
        for name, path in zip(['actor_index','entry_index','entry'], arms[arm]):
            explicit[arm + '_' + name] = (path, MAX_SOURCE)
    require(set(arms) == set('abcd'), 'Exactly four frozen Source arms')
    for sequence, result, terminal, stdout in args.trial:
        require(sequence.isascii() and sequence.isdecimal(), 'Numeric sequence CLI')
        n = int(sequence); require(1 <= n <= 10 and n not in trials and ORDER[n-1] != 'stock', 'Unique native trial CLI')
        trials[n] = (result, terminal, stdout)
        for name, path in zip(['result','terminal','stdout'], trials[n]):
            explicit[str(n) + '_' + name] = (path, MAX_STDOUT if name == 'stdout' else 8388608)
    require(sum(Path(path).lstat().st_size for path, _ in explicit.values()) <= MAX_TOTAL_INPUT,
        'Finite total explicit input budget before reads')
    inputs = {name:read_bounded(path,limit) for name,(path,limit) in explicit.items()}
    objs = {name:decode(data) for name,(_,data,_) in inputs.items() if not name.endswith(('_stdout','_entry'))}
    cohort, authority, plan, outer, contract = (objs[name] for name in ['cohort','authority','plan','outer_terminal','contract'])
    descriptor_matches(inputs['authority'][1], cohort['cohortAuthority'])
    descriptor_matches(inputs['plan'][1], cohort['comparisonPlan'])
    require(outer['rawExitCode'] == 0 and clean_owner(outer) and outer['authority'] == cohort['cohortAuthority'] and
        outer['pid'] == cohort['controllerPid'], 'Original cohort terminal/authority identity before intake')
    require(authority['comparisonPlan'] == cohort['comparisonPlan'] and
        cohort['automaticRetry'] is cohort['replacementTrials'] is False, 'Frozen no-retry cohort roles')
    require(len(cohort['trials']) == len(plan['trials']) == len(authority['trials']) == 10 and
        [x['arm'] for x in cohort['trials']] == ORDER and
        [x['sequence'] for x in cohort['trials']] == list(range(1,11)), 'Complete fixed ten-row order')
    require(contract['marker'] == 'NEXT_GUEST_RESPONSE_COMPLETION_V1' and
        contract['limits']['bytesPerRecordIncludingNewline'] == 512 and
        contract['limits']['recordsPerComponentInstanceIncludingErrorOrTruncation'] == 256 and
        contract['limits']['ASCIIOnly'] is True, 'Historical response record schema only')
    source = {}
    for arm in 'abcd':
        actor, index = objs[arm+'_actor_index'], objs[arm+'_entry_index']
        descriptor_matches(inputs[arm+'_actor_index'][1], authority['actorBindings'][arm])
        descriptor_matches(inputs[arm+'_entry_index'][1], actor['inputSourceIndex'])
        descriptor_matches(inputs[arm+'_entry'][1], actor['inputEntry'])
        name = Path(actor['inputEntry']['path']).name
        member = [row for row in index['files'] if row['path'] == name]
        require(len(member) == 1, 'Exact selected indexed entry')
        descriptor_matches(inputs[arm+'_entry'][1], dict(member[0],path=name))
        source[arm] = inputs[arm+'_entry'][1]
        require((b'NEXT_GUEST_RESPONSE_COMPLETION_V1' in source[arm]) == (arm in 'cd') and
            b'NEXT_GUEST_PROMISE_COMPLETION_V1' not in source[arm] and
            b'completionHolder' not in source[arm], 'No cd60 holder/child observer projected')
    old=b'          return handler.handle(incoming,outparam);'
    new=b'          return await handler.handle(incoming,outparam);'
    require(source['a'].count(old)==source['c'].count(old)==1 and
        source['b']==source['a'].replace(old,new,1) and source['d']==source['c'].replace(old,new,1),
        'Only B/D six-byte await variants, Source text not execution')
    schema_members=[row for row in objs['c_entry_index']['files'] if row['path']=='marker-contract.json']
    require(len(schema_members)==1, 'C indexed historical response schema')
    descriptor_matches(inputs['contract'][1],dict(schema_members[0],path='marker-contract.json'))
    output_rows=[]; used=set(); total_records=0
    for position, trial in enumerate(cohort['trials']):
        scheduled=plan['trials'][position];issued=authority['trials'][position]
        require(all(trial[k]==scheduled[k] for k in ['sequence','arm','runId']) and
            issued['trial']==scheduled and issued['authority']==trial['authority'], 'Fixed issued trial/order join')
        outcome=trial.get('outcome')
        row={k:trial[k] for k in ['sequence','arm','runId','status']}
        row['originalOutcomeDocumentary']=outcome
        if trial['arm']=='stock':
            row['markerApplicability']='not applicable: Node control, no guest capture invented'
        elif type(outcome) is not dict or not all(type(outcome.get(k)) is dict for k in ['result','terminal']):
            require(trial['sequence'] not in trials,'No invented raw inputs for unobserved trial')
            row['markerObservation']='unobserved; no completed native result/terminal'
        else:
            sequence=trial['sequence'];require(sequence in trials,'Explicit complete native trial inputs required')
            used.add(sequence);key=str(sequence);result,terminal=objs[key+'_result'],objs[key+'_terminal']
            descriptor_matches(inputs[key+'_result'][1],outcome['result'])
            descriptor_matches(inputs[key+'_terminal'][1],outcome['terminal'])
            require(clean_owner(terminal) and terminal['authority']==result['rootAuthority']==trial['authority'],
                'Clean original native terminal/result/authority join')
            arm=trial['arm'];actor=objs[arm+'_actor_index']
            require(result['sourceIndex']==authority['actorBindings'][arm] and
                result['inputSourceIndex']==actor['inputSourceIndex'] and result['inputEntry']==actor['inputEntry'] and
                result['runId']==trial['runId'] and type(result['passed']) is bool,
                'Actual per-trial selected Source and namespace')
            raw=inputs[key+'_stdout'][1];capture_complete(result['server'],raw)
            require(outcome['stdoutCapture']==result['server']['stdoutCapture'], 'Cohort actual capture metadata equality')
            analysis=analyze_raw(raw,contract,arm in 'cd');total_records+=analysis['markerRecords']
            require(total_records<=MAX_MARKERS,'Finite cohort record count; no silent truncation')
            row.update(originalOwnerRawExitCode=terminal['rawExitCode'],applicationPassed=result['passed'],
                component=result['component'],inputEntry=result['inputEntry'],sourceIndex=result['sourceIndex'],
                rawCaptureComplete=True,rawStdout=result['server']['stdout'],markerAnalysis=analysis)
        output_rows.append(row)
    require(used==set(trials),'No extra unassociated CLI trial inputs')
    for path,_,before in inputs.values():require(stamp(path)==before,'Final selected input read bookend')
    output=dict(schemaVersion=1,state='FIXED_FOUR_ARM_RESPONSE_MARKER_DATA_ANALYSIS_V1',
        dataParseSucceeded=all(row.get('markerAnalysis',{}).get('dataParseSucceeded',True) for row in output_rows),
        fixedOrder=ORDER,trials=output_rows,markerRecords=total_records,
        inputDescriptors={name:dict(argument=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
            for name,(path,data,_) in inputs.items()},
        sourceTextByteVariantsVerified=True,DHistoricalContractScope='Inherited response record schema only; no current whole-entry/no-added-await claim.',
        countsOrErrorAbsenceAssumed=False,numericPartitionsAuthenticatePhysicalInstance=False,
        childNeutralOrExportPromiseSettlementObserved=False,nativeLoopPostCallOrHostTaskObserved=False,
        hostTcpEofProved=False,classicAdapterOrOuterInnerJoinProved=False,privateIdentityOrUniqueCauseProved=False,
        fullNextAccepted=False,priorFailedGatesAccepted=False,reliabilityProved=False,
        sourceEvaluated=False,helperGuardNodeOrActorInvoked=False,embeddedDescriptorPathsOpened=False,
        interpretation='A/B absent logger is not a completion test. C/D positive records prove only their sealed public Source sites; read counts are not written/peer bytes. Missing, malformed, logger-error, truncation and collided/interleaved data remain unobserved. Numeric partitions are descriptive, never physical. No child-holder observer is selected; no Promise/native/host/cause acceptance.')
    print(json.dumps(output,indent=2))
    return 0 if output['dataParseSucceeded'] else 1


if __name__=='__main__':
    raise SystemExit(main())
