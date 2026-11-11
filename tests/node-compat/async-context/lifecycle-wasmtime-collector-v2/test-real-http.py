"""Root-only real HTTP reference: Content-Length underflow, valid CL and chunked.

No Wasmtime, component, fake HTTPResponse, mocked socket, or test double is used.
The fixed branch calls the actual collector body reader after Source hashing.
"""
from pathlib import Path
import hashlib
import http.client
import importlib.util
import json
import socket
import sys
import threading

HERE = Path(__file__).resolve().parent
COLLECTOR = HERE / 'run-wasmtime.py'
COLLECTOR_SHA = 'bd88a8b280e6a529c6c63e8eb11f3672a1199807364f8455a2ca9bc604c8cedf'


def need(value, message):
    if not value:
        raise AssertionError(message)


class OneResponse:
    def __init__(self, wire):
        self.wire, self.errors, self.closed = wire, [], False
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('127.0.0.1', 0)); self.listener.listen(1); self.listener.settimeout(2)
        self.port = self.listener.getsockname()[1]
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        connection = None
        try:
            connection, _ = self.listener.accept(); connection.settimeout(2)
            request = bytearray()
            while b'\r\n\r\n' not in request:
                block = connection.recv(1024)
                need(block, 'HTTP request headers reached EOF')
                request.extend(block); need(len(request) <= 4096, 'bounded HTTP request headers')
            need(request.startswith(b'GET / HTTP/1.1\r\n'), 'actual explicit GET')
            connection.sendall(self.wire)
            connection.shutdown(socket.SHUT_WR)
        except BaseException as value:
            self.errors.append(dict(name=type(value).__name__, message=str(value)))
        finally:
            if connection is not None:
                connection.close()
            self.listener.close(); self.closed = True

    def close(self):
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            self.listener.close(); self.thread.join(timeout=1)
        need(not self.thread.is_alive() and self.closed, 'owned HTTP reference thread closed')
        need(self.errors == [], 'HTTP reference server errors: ' + repr(self.errors))


def wire(headers, body):
    return b'HTTP/1.1 200 OK\r\nConnection: close\r\n' + headers + b'\r\n' + body


def collect(name, response_bytes, reader):
    server = OneResponse(response_bytes)
    connection = http.client.HTTPConnection('127.0.0.1', server.port, timeout=2)
    primary = None
    try:
        connection.request('GET', '/', headers={'Connection': 'close'})
        response = connection.getresponse(); need(response.status == 200, 'reference HTTP200')
        data, record = bytearray(), dict(complete=False, overflow=False)
        raised = None
        try:
            reader(response, data, record)
        except BaseException as value:
            raised = dict(name=type(value).__name__, message=str(value))
        return dict(case=name, entity=bytes(data), record=record, remaining=response.length,
            chunked=response.chunked, raised=raised)
    except BaseException as value:
        primary = value
        raise
    finally:
        try:
            connection.close(); server.close()
        except BaseException:
            if primary is not None:
                raise primary
            raise


def legacy_sized_read(response, data, record):
    # Intentional real-stdlib reference for the measured V1 admission gap.
    while True:
        block = response.read(4096)
        if not block:
            record['complete'] = True
            break
        data.extend(block)


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use nonoptimized Python -I -B')
    need(len(sys.argv) == 1, 'fixed no-argument reference test')
    original = COLLECTOR.read_bytes()
    need(hashlib.sha256(original).hexdigest() == COLLECTOR_SHA, 'exact collector Source before import')
    spec = importlib.util.spec_from_file_location('lifecycle_v2_body_reader_reference', COLLECTOR)
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)  # Definitions only; main/Wasmtime are not invoked.
    truncated = wire(b'Content-Length: 10\r\n', b'abc')
    old = collect('legacy-underlength-reference', truncated, legacy_sized_read)
    need(old['raised'] is None and old['record']['complete'] is True and old['remaining'] == 7 and old['entity'] == b'abc', 'measured sized-read underlength gap reproduced')
    fixed = collect('v2-underlength-refused', truncated, collector.read_response_body)
    need(fixed['raised'] is not None and fixed['raised']['name'] == 'ValueError', 'V2 refuses truncated Content-Length')
    need(fixed['record']['complete'] is False and fixed['record']['unfulfilledContentLength'] == 7 and fixed['remaining'] == 7 and fixed['entity'] == b'abc', 'bounded partial bytes and remaining length retained')
    valid = collect('v2-valid-content-length', wire(b'Content-Length: 10\r\n', b'abcdefghij'), collector.read_response_body)
    need(valid['raised'] is None and valid['record']['complete'] is True and valid['remaining'] == 0 and valid['entity'] == b'abcdefghij', 'complete Content-Length preserved')
    chunked = collect('v2-valid-chunked', wire(b'Transfer-Encoding: chunked\r\n', b'3\r\nabc\r\n2\r\nde\r\n0\r\n\r\n'), collector.read_response_body)
    need(chunked['raised'] is None and chunked['record']['complete'] is True and chunked['remaining'] is None and chunked['chunked'] is True and chunked['entity'] == b'abcde', 'complete real chunked response preserved')
    need(COLLECTOR.read_bytes() == original, 'collector Source bookend')
    observations = []
    for row in (old, fixed, valid, chunked):
        row['bodyBytes'] = len(row.pop('entity')); observations.append(row)
    print(json.dumps(dict(schemaVersion=1, state='REAL_HTTP_CONTENT_LENGTH_V2_REFERENCE_PASSED_V1',
        passed=True, collector=dict(path=str(COLLECTOR), sha256=COLLECTOR_SHA, bytes=len(original)),
        observations=observations, actualLocalHttpConnections=4, allReferenceServersClosed=True,
        collectorMainInvoked=False, wasmOrGuestOrComponentInvoked=False)))


if __name__ == '__main__':
    main()
