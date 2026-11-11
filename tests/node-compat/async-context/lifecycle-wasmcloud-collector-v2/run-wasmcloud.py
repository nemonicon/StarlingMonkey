"""Stock wasmCloud lifecycle collection only; Root supplies the original owner.

No app mounts, guest environment values, outgoing hosts, retries or same-Store claim.
"""
from pathlib import Path
import hashlib
import http.client
import json
import os
import re
import signal
import socket
import stat
import subprocess
import sys
import threading
import time

BODY_LIMIT = 128 * 1024
LOG_LIMIT = 8 * 1024 * 1024
SELECTED = {'wasi:cli/environment@0.2.10', 'wasi:clocks/monotonic-clock@0.2.10',
    'wasi:clocks/wall-clock@0.2.10', 'wasi:random/random@0.2.10',
    'wasi:filesystem/types@0.2.10', 'wasi:filesystem/preopens@0.2.10',
    'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10',
    'wasi:http/types@0.2.10', 'wasi:cli/stdout@0.2.10', 'wasi:cli/stderr@0.2.10',
    'wasi:http/outgoing-handler@0.2.10'}


def need(value, message):
    if not value:
        raise ValueError(message)


def error(value):
    return dict(name=type(value).__name__, message=str(value)[:2048])


def stamp(s):
    return s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def row(value):
    p = Path(value)
    need(p.is_absolute() and p.resolve() == p and not any(q.is_symlink() for q in (p, *p.parents)), 'canonical input')
    before = p.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'regular nlink1 input')
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''):
            h.update(block)
    need(stamp(before) == stamp(p.lstat()), 'input changed during read')
    return dict(path=str(p), sha256=h.hexdigest(), bytes=before.st_size)


def checked(ref):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'}, 'exact descriptor')
    need(type(ref['bytes']) is int and ref['bytes'] >= 0 and row(ref['path']) == ref, 'exact input bytes')
    return Path(ref['path'])


def document(ref):
    need(ref['bytes'] <= 16 * 1024**2, 'finite JSON before read')
    p = checked(ref)
    value = json.loads(p.read_bytes())
    checked(ref)
    return value


def save(path, value):
    raw = (json.dumps(value, indent=2) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return row(path)


def clean_terminal(value):
    return value['rawExitCode'] == 0 and value['timeout'] is False and value['forcedCleanup'] is False and \
        value['parentOwnedGroupGone'] is True and value['allObservedOwnedGroupsGone'] is True and \
        all(value[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))


class Capture:
    def __init__(self, pipe, path, stop):
        self.pipe, self.path, self.stop = pipe, path, stop
        self.observed = self.retained = 0
        self.eof = self.closed = self.synced = self.overflow = False
        self.errors = []
        self.prefix = bytearray()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        try:
            with self.path.open('xb', buffering=0) as output:
                try:
                    while True:
                        block = self.pipe.read(4096)
                        if not block:
                            self.eof = True
                            break
                        self.observed += len(block)
                        if self.observed <= LOG_LIMIT and not self.overflow:
                            view = memoryview(block)
                            while view:
                                count = output.write(view)
                                if count is None or count <= 0:
                                    raise OSError('incomplete raw log write')
                                view = view[count:]
                                self.retained += count
                            self.prefix.extend(block)
                        else:
                            self.overflow = True; self.stop.set()
                    output.flush(); os.fsync(output.fileno()); self.synced = True
                finally:
                    self.pipe.close()
            self.closed = True
        except BaseException as value:
            self.errors.append(error(value)); self.stop.set()

    def result(self):
        alive = self.thread.is_alive()
        descriptor = row(self.path) if self.path.is_file() and not alive else None
        complete = not alive and self.eof and self.closed and self.synced and not self.overflow and not self.errors and \
            self.observed == self.retained and descriptor is not None and descriptor['bytes'] == self.retained
        return dict(path=str(self.path), limitBytes=LOG_LIMIT, observedBytes=self.observed,
            retainedBytes=self.retained, pipeEof=self.eof, fsynced=self.synced, closed=self.closed,
            overflow=self.overflow, errors=self.errors, readerStillRunning=alive,
            complete=complete, file=descriptor)


def read_response_body(response, raw, record):
    while True:
        try:
            block = response.read(min(4096, BODY_LIMIT + 1 - len(raw)))
        except http.client.IncompleteRead as value:
            record['overflow'] = len(raw) + len(value.partial) > BODY_LIMIT
            raw.extend(value.partial[:max(0, BODY_LIMIT - len(raw))])
            raise
        if not block:
            # Sized http.client reads can reach socket EOF without consuming declared Content-Length.
            # Only None (no length / chunked) or zero remaining permits complete collection.
            remaining = response.length
            if remaining is not None and remaining != 0:
                record['unfulfilledContentLength'] = remaining
                raise ValueError('HTTP EOF before declared Content-Length was fulfilled')
            record['complete'] = True; break
        if len(raw) + len(block) > BODY_LIMIT:
            record['overflow'] = True
            raw.extend(block[:max(0, BODY_LIMIT - len(raw))])
            raise ValueError('HTTP body limit exceeded; bounded prefix retained')
        raw.extend(block)


def configuration(component, origin):
    match = re.fullmatch(r'http://127\.0\.0\.1:([1-9][0-9]{0,4})', origin)
    need(match is not None and int(match[1]) <= 65535, 'literal loopback origin with valid port')
    command = 'test -f "$WASH_COMPONENT_PATH"'
    return dict(version='2.11.0', build=dict(command=command, component_path=component),
        dev=dict(address='127.0.0.1:' + match[1], command=command, component_path=component,
                 service=False, components=[], plugins=[], host_plugins=[], volumes=[]),
        workload=dict(allowedHosts=[], allowedIpNameLookups=[], allowedHostLoopbackPorts=[],
                      config={}, environment=dict(config={})), wit=dict(skip_fetch=True))


def effective_configuration(actual, wanted):
    need(actual['version'] == wanted['version'] and actual['build'] == wanted['build'], 'effective build configuration')
    for key in ('address', 'command', 'component_path', 'service'):
        need(actual['dev'][key] == wanted['dev'][key], 'effective dev field: ' + key)
    need(actual['dev'].get('volumes', []) == [], 'no dev volumes; empty serde omission permitted')
    for key in ('components', 'plugins', 'host_plugins'):
        need(actual['dev'].get(key, []) == [], 'no extra dev workloads/plugins')
    for key in ('allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts'):
        need(actual['workload'][key] == [], 'zero outgoing allowlist')
    environment = actual['workload']['environment']
    need(type(environment) is dict and set(environment) <= {'config'} and
         environment.get('config', {}) == {}, 'zero guest environment; no configFrom/secretFrom or extra fields')
    need(actual['workload'].get('config', {}) == {} and actual['wit']['skip_fetch'] is True,
         'zero guest config; no WIT network fetch')


def registration(captures, origin):
    events = []
    for capture, stream in zip(captures, ('stdout', 'stderr')):
        lines = bytes(capture.prefix).decode('utf-8', 'replace').split('\n')[:-1]
        for index, raw in enumerate(lines):
            line = re.sub(r'\x1b\[[0-9;]*m', '', raw.rstrip('\r'))
            if not re.search(r'\bINFO\s+listening for HTTP requests\b', line):
                continue
            address = re.search(r'(?:^|\s)address=(?:"([^"]+)"|(\S+))(?:\s|$)', line)
            if address is None:
                continue
            value = address[1] if address[1] is not None else address[2]
            need(value == origin, 'unexpected stock post-registration origin; no fallback')
            events.append(dict(stream=stream, lineNumber=index + 1, line=raw, address=value))
    return events


def stop_process(item, secondary, reason):
    child, record = item['child'], item['record']
    if record['shutdownRequested']:
        return
    record['shutdownRequested'] = True
    record['shutdownReason'] = reason
    if child.poll() is None:
        try:
            child.send_signal(signal.SIGINT)
            record['sigintSent'] = True
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            record['forcedCleanup'] = True
            try:
                child.kill(); child.wait(timeout=5)
            except BaseException as value:
                secondary.append(dict(stage='forced-' + record['label'] + '-stop', **error(value)))
        except BaseException as value:
            secondary.append(dict(stage=record['label'] + '-stop', **error(value)))
    record['returncode'] = child.poll()


def finalize(item):
    for capture in item['captures']:
        capture.thread.join(timeout=5)
    item['record']['returncode'] = item['child'].poll()
    item['record']['captures'] = [c.result() for c in item['captures']]
    need(len(item['captures']) == 2 and all(r['complete'] for r in item['record']['captures']),
         'both stock command pipe captures must reach complete EOF/sync/close')


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use nonoptimized Python -I -B')
    need(len(sys.argv) == 2, 'usage: run-wasmcloud.py ABSOLUTE_REQUEST.json')
    request_ref = row(Path(sys.argv[1])); request = document(request_ref)
    need(request['state'] == 'ROOT_LIFECYCLE_WASMCLOUD_RUNTIME_REQUEST_V2', 'fresh Root cloud runtime request')
    need(type(request['outputRoot']) is str and re.fullmatch(
        r'/private/tmp/starling-node-compat/next-lifecycle-wasmcloud-v2-[a-z0-9][a-z0-9-]{0,47}',
        request['outputRoot']) is not None, 'fresh cloud output namespace')
    OUTPUT = Path(request['outputRoot'])
    need(OUTPUT.resolve() == OUTPUT and OUTPUT.parent.is_dir() and not os.path.lexists(OUTPUT), 'exclusive canonical output')
    need(request['runtimeSource'] == row(Path(__file__).resolve()), 'selected exact cloud collector Source')
    need(request['wash']['sha256'] == '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954' and
         request['wash']['bytes'] == 101947952, 'selected stock wash2.11.0 bytes')
    wanted = configuration(request['component']['path'], request['selfOrigin'])
    port = int(request['selfOrigin'].rsplit(':', 1)[1])
    need(type(request['protectedInputs']) is list and 0 < len(request['protectedInputs']) <= 4096, 'finite protected list')
    protected = [request_ref, request['runtimeSource'], request['component'], request['wash'], request['wasmTools'],
        request['validationStarted'], request['validationTerminal'], request['witStarted'], request['witTerminal'], *request['protectedInputs']]
    def protect():
        for ref in protected:
            checked(ref)
    protect()
    for role, argv in [('validation', [request['wasmTools']['path'], 'validate', request['component']['path']]),
                       ('wit', [request['wasmTools']['path'], 'component', 'wit', request['component']['path']])]:
        started, terminal = document(request[role + 'Started']), document(request[role + 'Terminal'])
        need(started['argv'] == argv and started['pid'] == terminal['pid'], 'actual validator/WIT component join')
        need(clean_terminal(terminal), 'closed clean actual validation/WIT owner')
        protected.extend([terminal['stdout'], terminal['stderr']])
        if role == 'wit':
            need(terminal['stdout']['bytes'] <= LOG_LIMIT, 'bounded actual component WIT')
            text = checked(terminal['stdout']).read_text()
            imports = re.findall(r'^\s*import ([^;\n]+);$', text, re.M)
            exports = re.findall(r'^\s*export ([^;\n]+);$', text, re.M)
            need(len(imports) == len(set(imports)) == 13 and set(imports) == SELECTED, 'exact selected standard13 imports')
            need(exports == ['wasi:http/incoming-handler@0.2.10'], 'sole incoming handler export')
    protect()
    os.umask(0o077)
    OUTPUT.mkdir(mode=0o700)
    result = dict(schemaVersion=1, state='LIFECYCLE_WASMCLOUD_COLLECTION_IN_PROGRESS_V2', request=request_ref,
        component=request['component'], wash=request['wash'], selectedInterfaces=sorted(SELECTED),
        emittedImports=imports, exports=exports, actualHost='stock-wasmCloud-2.11.0',
        configured=wanted, bodyLimitBytes=BODY_LIMIT, eachLogLimitBytes=LOG_LIMIT,
        fixedRequests=['/context', '/clone-cancel', '/clone-cancel-followups', '/context'],
        responses=[], commands=[], errors=[], secondaryErrors=[], collectionClean=False,
        semanticComparisonPerformed=False, sameStoreIdentityProved=False, applicationMounted=False,
        guestEnvironmentConfigured=False, outgoingHostsAllowed=False, extraHttpRequests=0,
        fullNextAccepted=False, originalExternalOwnerRequired=True)
    children = []; host = None; lease = None; primary = None
    def launch(args, label):
        env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
        env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C', XDG_CACHE_HOME=str(OUTPUT / 'xdg-cache'),
                   XDG_CONFIG_HOME=str(OUTPUT / 'xdg-config'), XDG_DATA_HOME=str(OUTPUT / 'xdg-data'))
        argv = [request['wash']['path'], *args]
        child = subprocess.Popen(argv, cwd=str(OUTPUT / 'project'), env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        stop = threading.Event()
        record = dict(label=label, argv=argv, pid=child.pid,
            sameProcessGroup=os.getpgid(child.pid) == os.getpgrp(), timeout=False,
            shutdownRequested=False, sigintSent=False, forcedCleanup=False, returncode=None)
        item = dict(child=child, record=record, captures=[], stop=stop)
        children.append(item); result['commands'].append(record)
        for pipe, suffix in ((child.stdout, 'stdout.log'), (child.stderr, 'stderr.log')):
            capture = Capture(pipe, OUTPUT / (label + '.' + suffix), stop)
            item['captures'].append(capture); capture.thread.start()
        return item
    try:
        (OUTPUT / 'project/.wash').mkdir(parents=True, mode=0o700)
        config_ref = save(OUTPUT / 'project/.wash/config.json', wanted)
        empty_ref = save(OUTPUT / 'empty-user-config.json', {})
        protected.extend([config_ref, empty_ref]); result['configFiles'] = [config_ref, empty_ref]
        lease = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lease.bind(('127.0.0.1', port))
        result['portLease'] = dict(origin=request['selfOrigin'], literalPort=port, heldThroughConfigInspection=True,
                                   singleAttempt=True, fallbackAllowed=False)
        protect()
        show = launch(['--user-config', empty_ref['path'], '-C', str(OUTPUT / 'project'), '--output', 'json', 'config', 'show'], 'config-show')
        try:
            show['child'].wait(timeout=30)
        except subprocess.TimeoutExpired:
            show['record']['timeout'] = True
            stop_process(show, result['secondaryErrors'], 'config-timeout')
            raise
        finalize(show)
        need(show['record']['returncode'] == 0 and not show['record']['timeout'], 'stock config-show raw0')
        shown = document(show['record']['captures'][0]['file'])
        need(shown['success'] is True, 'stock config-show success wrapper')
        effective_configuration(shown['data'], wanted)
        result['effectiveConfiguration'] = shown['data']; result['configVerifiedBeforeDev'] = True
        protect()
        lease.close(); lease = None
        result['portLease']['releasedImmediatelyBeforeSingleDevLaunch'] = True
        host = launch(['--user-config', empty_ref['path'], '-C', str(OUTPUT / 'project'), '--log-level', 'info', '--meters', 'duration', 'dev'], 'wash-dev')
        result['server'] = host['record']; result['origin'] = request['selfOrigin']
        ready = False; end = time.monotonic() + 60
        while time.monotonic() < end:
            need(host['child'].poll() is None and not host['stop'].is_set(), 'stock host/capture uncertain before readiness')
            events = registration(host['captures'], request['selfOrigin'])
            if events:
                try:
                    with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                        ready = True
                    result['readiness'] = dict(postRegistrationEvents=events, tcpReady=True, httpWarmupRequests=0)
                    break
                except OSError:
                    pass
            time.sleep(0.05)
        need(ready, 'exact post-registration log plus TCP readiness')
        for ordinal, route in enumerate(result['fixedRequests'], 1):
            need(host['child'].poll() is None and not host['stop'].is_set(), 'host/capture uncertain before next fixed request')
            record = dict(ordinal=ordinal, route=route, method='GET', complete=False,
                overflow=False, transportError=None, bodyScope='http.client entity bytes; no HTTP wire/chunk framing')
            result['responses'].append(record)
            connection = http.client.HTTPConnection('127.0.0.1', port, timeout=15)
            raw = bytearray(); transport_primary = None
            try:
                connection.request('GET', route, headers={'Connection': 'close'})
                response = connection.getresponse()
                record.update(status=response.status, reason=response.reason, httpVersion=response.version, headers=response.getheaders())
                need(sum(len(k) + len(v) + 4 for k, v in record['headers']) <= 65536, 'header metadata bound')
                read_response_body(response, raw, record)
            except BaseException as value:
                transport_primary = value; record['transportError'] = error(value)
            finally:
                try:
                    connection.close(); record['connectionClosed'] = True
                except BaseException as value:
                    record['connectionClosed'] = False; record['closeError'] = error(value)
                body = OUTPUT / ('response-' + str(ordinal) + '.body')
                try:
                    with body.open('xb') as stream:
                        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                    record['body'] = row(body)
                except BaseException as value:
                    record['bodyPublicationError'] = error(value)
                    if transport_primary is not None:
                        raise transport_primary
                    raise
            if record['transportError'] is not None or not record['complete'] or not record['connectionClosed']:
                if transport_primary is not None:
                    raise transport_primary
                raise RuntimeError('HTTP collection uncertain; fixed remaining suffix unattempted')
        result['allFourBodiesCollected'] = len(result['responses']) == 4
    except BaseException as value:
        primary = value; result['errors'].append(error(value))
    finally:
        if lease is not None:
            try:
                lease.close()
            except BaseException as value:
                result['secondaryErrors'].append(dict(stage='lease-close', **error(value)))
        for item in children:
            if item is host or item['child'].poll() is None:
                stop_process(item, result['secondaryErrors'], 'four-fixed-calls-collected' if item is host else 'final-cleanup')
            try:
                finalize(item)
            except BaseException as value:
                result['secondaryErrors'].append(dict(stage=item['record']['label'] + '-capture-finalization', **error(value)))
        try:
            need(host is not None and len(children) == 2 and result.get('configVerifiedBeforeDev') is True,
                 'exactly one closed config-show and one dev required')
            result['captures'] = host['record']['captures']
            need(all(len(item['record']['captures']) == 2 and all(c['complete'] for c in item['record']['captures'])
                     and item['record']['returncode'] == 0 and not item['record']['timeout'] and not item['record']['forcedCleanup']
                     for item in children), 'all stock commands raw0 and both captures complete')
            need(host['record']['shutdownRequested'] and host['record']['sigintSent'] and not host['record']['forcedCleanup']
                 and host['record']['returncode'] == 0, 'normal stock SIGINT0 shutdown')
            protect(); result['inputsPreserved'] = True
        except BaseException as value:
            if primary is None:
                primary = value; result['errors'].append(error(value))
            else:
                result['secondaryErrors'].append(dict(stage='final-capture-or-protection', **error(value)))
        result['unattemptedRequests'] = result['fixedRequests'][len(result['responses']):]
        result['collectionClean'] = primary is None and not result['secondaryErrors'] and result.get('allFourBodiesCollected') is True and result.get('inputsPreserved') is True
        result['state'] = 'LIFECYCLE_WASMCLOUD_COLLECTION_CLEAN_UNREVIEWED_V2' if result['collectionClean'] else 'LIFECYCLE_WASMCLOUD_COLLECTION_FAILED_RAW_PRESERVED_V2'
        try:
            descriptor = save(OUTPUT / 'result.json', result)
            print(json.dumps(dict(result=descriptor, collectionClean=result['collectionClean'], semanticComparisonPerformed=False)), flush=True)
        except BaseException as value:
            if primary is not None:
                raise primary
            raise value
    return 0 if result['collectionClean'] else 1


if __name__ == '__main__':
    sys.exit(main())


