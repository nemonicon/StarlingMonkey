"""Collect three ordinary lifecycle HTTP calls; semantic comparison is separate.

Root wraps this fixed collector in the original120s owner. No host reentry,
application mount, guest environment forwarding, retries or same-Store claim.
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

OUTPUT = Path('/private/tmp/starling-node-compat/next-lifecycle-runtime-v1-first')
BODY_LIMIT = 128 * 1024
LOG_LIMIT = 512 * 1024
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


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use nonoptimized Python -I -B')
    need(len(sys.argv) == 2, 'usage: run-wasmtime.py ABSOLUTE_REQUEST.json')
    request_ref = row(Path(sys.argv[1])); request = document(request_ref)
    need(request['state'] == 'ROOT_LIFECYCLE_COMPONENT_RUNTIME_REQUEST_V1', 'new Root runtime request')
    need(request['outputRoot'] == str(OUTPUT), 'fixed fresh output')
    need(request['runtimeSource'] == row(Path(__file__).resolve()), 'selected exact collector Source')
    need(type(request['protectedInputs']) is list and 0 < len(request['protectedInputs']) <= 4096, 'finite protected input list')
    protected = [request_ref, request['runtimeSource'], request['component'], request['wasmtime'], request['wasmTools'],
        request['validationStarted'], request['validationTerminal'], request['witStarted'], request['witTerminal'], *request['protectedInputs']]
    def protect():
        for ref in protected:
            checked(ref)
    protect()
    for role, argv in [('validation', [request['wasmTools']['path'], 'validate', request['component']['path']]),
            ('wit', [request['wasmTools']['path'], 'component', 'wit', request['component']['path']])]:
        started, terminal = document(request[role + 'Started']), document(request[role + 'Terminal'])
        need(started['argv'] == argv and started['pid'] == terminal['pid'], 'actual validator/WIT component join')
        need(clean_terminal(terminal), 'actual clean validation/WIT terminal')
        protected.extend([terminal['stdout'], terminal['stderr']])
        if role == 'wit':
            need(terminal['stdout']['bytes'] <= LOG_LIMIT, 'finite actual WIT')
            text = checked(terminal['stdout']).read_text()
            imports = re.findall(r'^\s*import ([^;\n]+);$', text, re.M)
            exports = re.findall(r'^\s*export ([^;\n]+);$', text, re.M)
            need(len(imports) == len(set(imports)) and set(imports) <= SELECTED, 'standard selected13 imports only')
            need(exports == ['wasi:http/incoming-handler@0.2.10'], 'sole incoming handler export')
    protect()
    need(OUTPUT.parent.resolve() == OUTPUT.parent and not OUTPUT.exists() and not OUTPUT.is_symlink(), 'exclusive canonical output')
    OUTPUT.mkdir(mode=0o700)
    result = dict(schemaVersion=1, state='LIFECYCLE_HTTP_COLLECTION_IN_PROGRESS_V1', request=request_ref,
        component=request['component'], wasmtime=request['wasmtime'], selectedInterfaces=sorted(SELECTED),
        emittedImports=imports, exports=exports, bodyLimitBytes=BODY_LIMIT, eachLogLimitBytes=LOG_LIMIT,
        fixedRequests=['/context', '/clone-cancel', '/context'], responses=[], errors=[], secondaryErrors=[],
        collectionClean=False, semanticComparisonPerformed=False, sameStoreIdentityProved=False,
        applicationMounted=False, extraHttpRequests=0, fullNextAccepted=False)
    child = None; captures = []; stop = threading.Event(); primary = None
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lease:
            lease.bind(('127.0.0.1', 0)); port = lease.getsockname()[1]
        argv = [request['wasmtime']['path'], 'serve', '--addr', '127.0.0.1:' + str(port),
            '-S', 'cli=y,tcp=n,udp=n,allow-ip-name-lookup=n', '--max-instance-reuse-count', '32',
            '--idle-instance-timeout', '60s', request['component']['path']]
        env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
        env.update(PATH='/usr/bin:/bin', XDG_CACHE_HOME=str(OUTPUT / 'xdg-cache'),
            XDG_CONFIG_HOME=str(OUTPUT / 'xdg-config'), XDG_DATA_HOME=str(OUTPUT / 'xdg-data'))
        protect()
        child = subprocess.Popen(argv, cwd=str(OUTPUT), env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        result['server'] = dict(argv=argv, pid=child.pid, sameProcessGroup=os.getpgid(child.pid) == os.getpgrp(),
            shutdownRequested=False, forcedCleanup=False, returncode=None)
        for pipe, name in [(child.stdout, 'stdout.log'), (child.stderr, 'stderr.log')]:
            capture = Capture(pipe, OUTPUT / name, stop); captures.append(capture); capture.thread.start()
        origin = 'http://127.0.0.1:' + str(port); result['origin'] = origin
        ready = False; end = time.monotonic() + 20
        while time.monotonic() < end:
            need(child.poll() is None and not stop.is_set(), 'host exited or capture uncertain before readiness')
            log = bytes(captures[0].prefix) + bytes(captures[1].prefix)
            if ('Serving HTTP on ' + origin).encode() in log:
                try:
                    with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                        ready = True; break
                except OSError:
                    pass
            time.sleep(0.02)
        need(ready, 'exact listener log plus TCP readiness deadline')
        result['tcpReady'] = True
        for ordinal, route in enumerate(result['fixedRequests'], 1):
            need(child.poll() is None and not stop.is_set(), 'host/capture uncertain before next fixed request')
            record = dict(ordinal=ordinal, route=route, method='GET', complete=False,
                overflow=False, transportError=None, bodyScope='http.client entity bytes; no HTTP wire/chunk framing')
            result['responses'].append(record)
            connection = http.client.HTTPConnection('127.0.0.1', port, timeout=15)
            raw = bytearray(); transport_primary = None
            try:
                connection.request('GET', route, headers={'Connection': 'close'})
                response = connection.getresponse()
                record.update(status=response.status, reason=response.reason, httpVersion=response.version,
                    headers=response.getheaders())
                need(sum(len(k) + len(v) + 4 for k, v in record['headers']) <= 65536, 'header metadata bound')
                while True:
                    try:
                        block = response.read(min(4096, BODY_LIMIT + 1 - len(raw)))
                    except http.client.IncompleteRead as value:
                        record['overflow'] = len(raw) + len(value.partial) > BODY_LIMIT
                        raw.extend(value.partial[:max(0, BODY_LIMIT - len(raw))])
                        raise
                    if not block:
                        record['complete'] = True; break
                    if len(raw) + len(block) > BODY_LIMIT:
                        record['overflow'] = True
                        raw.extend(block[:max(0, BODY_LIMIT - len(raw))])
                        raise ValueError('HTTP body limit exceeded; bounded prefix retained')
                    raw.extend(block)
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
            # Status/report semantics are retained without being accepted here.
        result['allThreeBodiesCollected'] = len(result['responses']) == 3
    except BaseException as value:
        primary = value; result['errors'].append(error(value))
    finally:
        if child is not None:
            result['server']['shutdownRequested'] = True
            if child.poll() is None:
                try:
                    child.send_signal(signal.SIGINT); result['server']['sigintSent'] = True
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    result['server']['forcedCleanup'] = True
                    try:
                        child.kill(); child.wait(timeout=5)
                    except BaseException as value:
                        result['secondaryErrors'].append(dict(stage='forced-host-shutdown', **error(value)))
                except BaseException as value:
                    result['secondaryErrors'].append(dict(stage='host-shutdown', **error(value)))
            else:
                result['server']['sigintSent'] = False
            result['server']['returncode'] = child.poll()
        for capture in captures:
            capture.thread.join(timeout=5)
        try:
            result['captures'] = [capture.result() for capture in captures]
            need(len(captures) == 2 and all(x['complete'] for x in result['captures']), 'complete bounded stdout and stderr required')
            need(child is not None and result['server']['shutdownRequested'] and result['server']['sigintSent'] and
                not result['server']['forcedCleanup'] and child.returncode == 0, 'normal SIGINT0 shutdown required')
            protect(); result['inputsPreserved'] = True
        except BaseException as value:
            if primary is None:
                primary = value; result['errors'].append(error(value))
            else:
                result['secondaryErrors'].append(dict(stage='final-capture-or-protection', **error(value)))
        result['unattemptedRequests'] = result['fixedRequests'][len(result['responses']):]
        result['collectionClean'] = primary is None and not result['secondaryErrors'] and result.get('allThreeBodiesCollected') is True and result.get('inputsPreserved') is True
        result['state'] = 'LIFECYCLE_HTTP_COLLECTION_CLEAN_UNREVIEWED_V1' if result['collectionClean'] else 'LIFECYCLE_HTTP_COLLECTION_FAILED_RAW_PRESERVED_V1'
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
