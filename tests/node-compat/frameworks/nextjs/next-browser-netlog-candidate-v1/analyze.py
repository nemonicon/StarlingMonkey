"""Read-only NetLog DATA classification. No browser, network or producer imports."""
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import stat
from urllib.parse import urlsplit

MAX_BYTES = 20 * 1024 * 1024
MAX_EVENTS = 250000
MAX_SELECTED_EVENTS = 5000


def reverse(constants, key):
    table = constants.get(key)
    if not isinstance(table, dict) or not table:
        raise ValueError('Missing NetLog constants: ' + key)
    result = {}
    for name, value in table.items():
        if not isinstance(name, str) or type(value) is not int or value in result:
            raise ValueError('Ambiguous NetLog constant: ' + key)
        result[value] = name
    return result


def source(value):
    if not isinstance(value, dict) or type(value.get('id')) is not int or type(value.get('type')) is not int:
        raise ValueError('NetLog source id/type must be integers')
    return value['id'], value['type']


def dependencies(value, depth=0):
    if depth > 24:
        raise ValueError('NetLog parameter nesting exceeds24')
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'source_dependency':
                found.append(source(item))
            else:
                found.extend(dependencies(item, depth + 1))
    elif isinstance(value, list):
        for item in value:
            found.extend(dependencies(item, depth + 1))
    return found


def classify(document, origin):
    url = urlsplit(origin)
    if url.scheme != 'http' or url.hostname != '127.0.0.1' or not url.port or url.path or url.query or url.fragment or url.username or url.password:
        raise ValueError('Exact canonical leased loopback origin required')
    if origin != 'http://127.0.0.1:' + str(url.port):
        raise ValueError('Noncanonical origin')
    if not isinstance(document, dict) or not isinstance(document.get('constants'), dict) or not isinstance(document.get('events'), list):
        raise ValueError('Complete constants/events JSON required')
    events = document['events']
    if len(events) > MAX_EVENTS:
        raise ValueError('NetLog event count exceeds finite analyser bound')
    constants = document['constants']
    event_names = reverse(constants, 'logEventTypes')
    source_names = reverse(constants, 'logSourceType')
    phase_names = reverse(constants, 'logEventPhase')
    error_names = reverse(constants, 'netError')
    by_source, candidates, edges = {}, {}, []
    for index, event in enumerate(events):
        if not isinstance(event, dict) or type(event.get('type')) is not int or type(event.get('phase')) is not int:
            raise ValueError('Malformed NetLog event')
        identity = source(event.get('source'))
        time = event.get('time')
        if not isinstance(time, str):
            raise ValueError('NetLog time string required')
        try:
            if not Decimal(time).is_finite():
                raise ValueError('Nonfinite NetLog time')
        except InvalidOperation as error:
            raise ValueError('Invalid NetLog time') from error
        params = event.get('params', {})
        if not isinstance(params, dict):
            raise ValueError('NetLog params must be an object')
        record = dict(index=index, time=time, eventTypeId=event['type'],
            eventType=event_names.get(event['type'], 'UNKNOWN_EVENT'),
            phaseId=event['phase'], phase=phase_names.get(event['phase'], 'UNKNOWN_PHASE'),
            sourceId=identity[0], sourceTypeId=identity[1],
            sourceType=source_names.get(identity[1], 'UNKNOWN_SOURCE'), params=params)
        by_source.setdefault(identity, []).append(record)
        if record['sourceType'] == 'URL_REQUEST' and params.get('url') == origin + '/actions' and params.get('method') == 'POST':
            candidates.setdefault(identity, []).append(index)
        for dependent in dependencies(params):
            edges.append(dict(eventIndex=index, sourceId=identity[0], sourceTypeId=identity[1],
                dependencySourceId=dependent[0], dependencySourceTypeId=dependent[1]))
    selected = set(candidates)
    # One explicit dependency hop in either direction. No inferred ownership.
    related_edges = [edge for edge in edges if (edge['sourceId'], edge['sourceTypeId']) in selected or
        (edge['dependencySourceId'], edge['dependencySourceTypeId']) in selected]
    for edge in related_edges:
        selected.add((edge['sourceId'], edge['sourceTypeId']))
        selected.add((edge['dependencySourceId'], edge['dependencySourceTypeId']))
    selected_events = sorted((event for identity in selected for event in by_source.get(identity, [])), key=lambda event: event['index'])
    if len(selected_events) > MAX_SELECTED_EVENTS:
        raise ValueError('Selected source events exceed5000; raw file remains intact')
    errors = []
    for event in selected_events:
        code = event['params'].get('net_error')
        if code is not None:
            if type(code) is not int:
                raise ValueError('net_error must be integer')
            errors.append(dict(eventIndex=event['index'], sourceId=event['sourceId'],
                sourceTypeId=event['sourceTypeId'], eventType=event['eventType'],
                time=event['time'], code=code, name=error_names.get(code, 'UNKNOWN_NET_ERROR'),
                isNegativeCode=code < 0))
    return dict(schemaVersion=1, state='NETLOG_DATA_CLASSIFICATION_ONLY_V1',
        completeJsonDocument=True, circularCaptureConfigured=True,
        historyCompleteProved=False, evictionStatus='not determined from this format; capped circular logging may omit earlier events',
        totalEvents=len(events), targetUrl=origin + '/actions', targetMethod='POST',
        candidateCount=len(candidates), postObservation='present' if candidates else 'not observed in retained events',
        candidates=[dict(sourceId=identity[0], sourceTypeId=identity[1], witnessEventIndexes=indices)
            for identity, indices in candidates.items()],
        matchPolicy='Same event explicitly records URL_REQUEST, exact leased /actions URL and method POST. Missing/redacted/evicted evidence is unobserved, never successful or failed by inference.',
        explicitDependencyEdges=related_edges, dependencyHopLimit=1,
        selectedEvents=selected_events, explicitNetErrors=errors,
        negativeNetErrorObserved=any(error['isNegativeCode'] for error in errors),
        ordering='Original JSON event indexes and NetLog time strings retained. NetLog ticks are not Node/PW/CDP clock values; no cross-clock alignment or root-cause inference.',
        completeRequestLifecycleProved=False, browserStrictGateAccepted=False,
        netlogSourceIdIsNativeStoreIdentity=False, uniqueCauseProved=False,
        fullNextAcceptance=False, authorizesFutureAction=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--origin', required=True)
    args = parser.parse_args()
    path = Path(args.input)
    if not path.is_absolute() or path.resolve() != path or path.is_symlink():
        raise ValueError('Canonical ordinary input required')
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 0 < before.st_size <= MAX_BYTES:
        raise ValueError('Regular unique NetLog within20MiB required before read')
    data = path.read_bytes()
    fields = ['st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns']
    after = path.lstat()
    if any(getattr(before, key) != getattr(after, key) for key in fields) or len(data) != before.st_size:
        raise ValueError('NetLog changed while reading')
    report = classify(json.loads(data.decode('utf-8')), args.origin)
    report['input'] = dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
