// Candidate Node HTTP message semantics over standard Web Request/Response.
// Host tests use Node streams; guest integration must use the real native profile.
import {Readable, Writable} from 'node:stream';
import {EventEmitter} from 'node:events';
import {Buffer} from 'node:buffer';

function failure(code, message) { const error = new Error(message); error.code = code; return error; }

class RequestTransport extends EventEmitter {
  constructor(url) {
    super();
    this.encrypted = url.protocol === 'https:';
    this.remoteAddress = undefined;
    this.remotePort = undefined;
    this.localAddress = undefined;
    this.localPort = Number(url.port || (this.encrypted ? 443 : 80));
    this.destroyed = false;
    this.writable = true;
    this.readable = true;
    this.request = null;
    this.response = null;
  }
  setNoDelay() { return this; } // Advisory transport policy belongs to the host.
  setKeepAlive() { return this; }
  setTimeout(milliseconds, callback) {
    if (callback) this.once('timeout', callback);
    this.timeout = milliseconds;
    return this;
  }
  destroy(error) {
    if (this.destroyed) return this;
    this.destroyed = true;
    this.writable = this.readable = false;
    this.request?.destroy(error);
    this.response?.destroy(error);
    this.emit('close', Boolean(error));
    return this;
  }
  write() { throw failure('ERR_SM_NODE_UNSUPPORTED', 'Raw socket writes are unavailable through WASI HTTP'); }
}

export class BridgeIncomingMessage extends Readable {
  constructor(request) {
    super({autoDestroy: true});
    const url = new URL(request.url);
    this.method = request.method;
    this.url = url.pathname + url.search;
    this.headers = {};
    this.rawHeaders = [];
    for (const [name, value] of request.headers) {
      Object.defineProperty(this.headers, name.toLowerCase(), {value, writable: true, configurable: true, enumerable: true});
      this.rawHeaders.push(name, value);
    }
    this.headers.host ??= url.host;
    this.httpVersion = '1.1';
    this.httpVersionMajor = 1;
    this.httpVersionMinor = 1;
    this.trailers = {};
    this.rawTrailers = [];
    this.complete = false;
    this.aborted = false;
    this.socket = new RequestTransport(url);
    this.connection = this.socket;
    this.socket.request = this;
    this.reader = request.body?.getReader() ?? null;
    this.readPending = false;
    this.abortSignal = request.signal;
    this.onAbort = () => {
      if (this.complete || this.destroyed) return;
      this.aborted = true;
      this.emit('aborted');
      this.socket.destroy(failure('ECONNRESET', 'Request aborted'));
    };
    request.signal?.addEventListener('abort', this.onAbort, {once: true});
    if (request.signal?.aborted) this.onAbort();
  }
  _read() {
    if (this.readPending || this.complete || this.destroyed) return;
    this.readPending = true;
    Promise.resolve().then(async () => {
      const part = this.reader ? await this.reader.read() : {done: true};
      this.readPending = false;
      if (this.destroyed) return;
      if (part.done) {
        this.complete = true;
        this.abortSignal?.removeEventListener('abort', this.onAbort);
        this.push(null);
      } else {
        this.push(Buffer.from(part.value));
      }
    }).catch(error => { this.readPending = false; this.destroy(error); });
  }
  _destroy(error, callback) {
    this.abortSignal?.removeEventListener('abort', this.onAbort);
    if (!this.complete) this.aborted = true;
    Promise.resolve(this.complete ? undefined : this.reader?.cancel(error)).then(
      () => callback(error), () => callback(error));
  }
  setTimeout(milliseconds, callback) { this.socket.setTimeout(milliseconds, callback); return this; }
}

export class BridgeServerResponse extends Writable {
  constructor(request, {highWaterMark = 64 * 1024} = {}) {
    super({highWaterMark, autoDestroy: true});
    this.req = request;
    this.socket = request.socket;
    this.connection = this.socket;
    this.socket.response = this;
    this.statusCode = 200;
    this.statusMessage = undefined;
    this.sendDate = true;
    this.strictContentLength = false;
    this.headerFields = new Map();
    this.sent = false;
    this._header = null;
    this._headerSent = false;
    this.pendingWrite = null;
    this.responsePublished = false;
    this.bodyClosed = false;
    this.response = new Promise((resolve, reject) => { this.resolveResponse = resolve; this.rejectResponse = reject; });
    this.body = new ReadableStream({
      start: controller => { this.controller = controller; },
      pull: () => { this.releaseWrite(); },
      cancel: reason => { this.destroy(reason instanceof Error ? reason : failure('ECONNRESET', 'Response cancelled')); },
    }, {highWaterMark, size: chunk => chunk.byteLength});
    this.on('error', error => { if (!this.responsePublished) this.rejectResponse(error); });
  }
  get headersSent() { return this.sent; }
  get finished() { return this.writableEnded; }
  setHeader(name, value) {
    if (this.sent) throw failure('ERR_HTTP_HEADERS_SENT', 'Cannot set headers after they are sent');
    if (!/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/.test(name)) throw failure('ERR_INVALID_HTTP_TOKEN', 'Invalid header name');
    const values = (Array.isArray(value) ? value : [value]).map(item => {
      if (item === undefined) throw failure('ERR_HTTP_INVALID_HEADER_VALUE', 'Undefined header value');
      const text = String(item);
      if (/[\r\n]/.test(text)) throw failure('ERR_INVALID_CHAR', 'Invalid header value');
      return text;
    });
    this.headerFields.set(name.toLowerCase(), {name, values});
    return this;
  }
  appendHeader(name, value) {
    const old = this.getHeader(name);
    return this.setHeader(name, [...(Array.isArray(old) ? old : old === undefined ? [] : [old]), ...(Array.isArray(value) ? value : [value])]);
  }
  getHeader(name) {
    const row = this.headerFields.get(name.toLowerCase());
    if (!row) return undefined;
    return row.values.length === 1 ? row.values[0] : [...row.values];
  }
  getHeaders() { return Object.assign(Object.create(null), Object.fromEntries([...this.headerFields].map(([name]) => [name, this.getHeader(name)]))); }
  getHeaderNames() { return [...this.headerFields.keys()]; }
  getRawHeaderNames() { return [...this.headerFields.values()].map(row => row.name); }
  hasHeader(name) { return this.headerFields.has(name.toLowerCase()); }
  removeHeader(name) {
    if (this.sent) throw failure('ERR_HTTP_HEADERS_SENT', 'Cannot remove headers after they are sent');
    this.headerFields.delete(name.toLowerCase());
  }
  writeHead(status, statusMessage, headers) {
    this.statusCode = status;
    if (typeof statusMessage === 'string') this.statusMessage = statusMessage;
    else headers = statusMessage;
    if (headers) {
      if (Array.isArray(headers)) for (let i = 0; i < headers.length; i += 2) this.appendHeader(headers[i], headers[i + 1]);
      else for (const [name, value] of Object.entries(headers)) this.setHeader(name, value);
    }
    this.commitHeaders();
    return this;
  }
  _implicitHeader() { this.writeHead(this.statusCode); }
  flushHeaders() {
    if (!this.sent) this._implicitHeader();
  }
  commitHeaders() {
    if (this.sent) return;
    const headers = new Headers();
    for (const row of this.headerFields.values()) for (const value of row.values) headers.append(row.name, value);
    const emptyBody = this.req.method === 'HEAD' || [204, 205, 304].includes(this.statusCode);
    const response = new Response(emptyBody ? null : this.body, {status: this.statusCode, headers,
      ...(this.statusMessage === undefined ? {} : {statusText: this.statusMessage})});
    this._header = 'HTTP/1.1 ' + this.statusCode + ' ' + (this.statusMessage ?? '') + '\r\n'
      + [...this.headerFields.values()].flatMap(row => row.values.map(value => row.name + ': ' + value + '\r\n')).join('') + '\r\n';
    this._headerSent = true;
    this.sent = true;
    this.responsePublished = true;
    this.resolveResponse(response);
  }
  releaseWrite() {
    if (this.pendingWrite && this.controller.desiredSize > 0) {
      const callback = this.pendingWrite;
      this.pendingWrite = null;
      callback();
    }
  }
  _write(chunk, encoding, callback) {
    try {
      this.flushHeaders();
      if (this.req.method === 'HEAD' || [204, 205, 304].includes(this.statusCode)) return callback();
      // Own the bytes before notifying the caller that its input may be reused.
      this.controller.enqueue(new Uint8Array(typeof chunk === 'string' ? Buffer.from(chunk, encoding) : chunk));
      if (this.controller.desiredSize > 0) callback();
      else this.pendingWrite = callback;
    } catch (error) { callback(error); }
  }
  _final(callback) {
    try { this.flushHeaders(); this.bodyClosed = true; this.controller.close(); callback(); }
    catch (error) { callback(error); }
  }
  _destroy(error, callback) {
    const pending = this.pendingWrite;
    this.pendingWrite = null;
    if (pending) pending(error || failure('ECONNRESET', 'Response destroyed'));
    if (!this.bodyClosed) {
      this.bodyClosed = true;
      this.controller.error(error || failure('ECONNRESET', 'Response destroyed'));
    }
    callback(error);
  }
  setTimeout(milliseconds, callback) { this.socket.setTimeout(milliseconds, callback); return this; }
}

export function createRequestBridge(nextHandler) {
  return function handle(request) {
    const incoming = new BridgeIncomingMessage(request);
    const outgoing = new BridgeServerResponse(incoming);
    incoming.on('error', error => outgoing.destroy(error));
    // Handler lifetime continues while the host consumes the returned body.
    Promise.resolve().then(() => nextHandler(incoming, outgoing)).catch(value => {
      const error = value instanceof Error ? value : failure('ERR_SM_HTTP_HANDLER', 'Request handler threw a non-Error value');
      if (error !== value) error.cause = value;
      outgoing.destroy(error);
    });
    return outgoing.response;
  };
}
