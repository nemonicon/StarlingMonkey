// Generated HTTP guest factory v1; all-input digest c8f9b63a52e8c168637343355012b74e3e6e0a0e066fe4d59b61c5918bec8e7a
static constexpr const char kNextHttpFactorySource[]=R"SM_HTTP((function(a){
const {Readable,Writable,EventEmitter,Buffer}=a;
// Candidate Node HTTP message semantics over standard Web Request/Response.
// Host tests use Node streams; guest integration must use the real native profile.

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
    if (!Number.isFinite(milliseconds) || milliseconds < 0) throw failure('ERR_OUT_OF_RANGE', 'Timeout must be a finite nonnegative number');
    if (callback) this.once('timeout', callback);
    this.timeout = milliseconds;
    this.touch();
    return this;
  }
  touch() {
    clearTimeout(this.timeoutHandle);
    if (this.timeout > 0 && !this.destroyed) {
      this.timeoutHandle = setTimeout(() => this.emit('timeout'), this.timeout);
      this.timeoutHandle.unref?.();
    }
  }
  finish() { clearTimeout(this.timeoutHandle); }
  destroy(error) {
    if (this.destroyed) return this;
    this.destroyed = true;
    this.finish();
    this.writable = this.readable = false;
    this.request?.destroy(error);
    this.response?.destroy(error);
    this.emit('close', Boolean(error));
    return this;
  }
  write() { throw failure('ERR_SM_NODE_UNSUPPORTED', 'Raw socket writes are unavailable through WASI HTTP'); }
}

class BridgeIncomingMessage extends Readable {
  constructor(request) {
    a.checkDeployed();
    if (!(request instanceof Request)) throw failure("ERR_SM_NODE_UNSUPPORTED", "IncomingMessage requires this profile Web Request transport");
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
        this.socket.touch();
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

class BridgeServerResponse extends Writable {
  constructor(request, {highWaterMark = 64 * 1024} = {}) {
    a.checkDeployed();
    if (!(request instanceof BridgeIncomingMessage)) throw failure("ERR_SM_NODE_UNSUPPORTED", "ServerResponse requires the paired profile IncomingMessage");
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
      this.socket.touch();
      if (this.req.method === 'HEAD' || [204, 205, 304].includes(this.statusCode)) return callback();
      // Own the bytes before notifying the caller that its input may be reused.
      this.controller.enqueue(new Uint8Array(typeof chunk === 'string' ? Buffer.from(chunk, encoding) : chunk));
      if (this.controller.desiredSize > 0) callback();
      else this.pendingWrite = callback;
    } catch (error) { callback(error); }
  }
  _final(callback) {
    try { this.flushHeaders(); this.socket.finish(); this.bodyClosed = true; this.controller.close(); callback(); }
    catch (error) { callback(error); }
  }
  _destroy(error, callback) {
    this.socket.finish();
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

function createRequestBridge(nextHandler) {
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

// Small guest facade; bridge is supplied from the separately hashed real source.
// No network socket implementation or TLS provider is hidden behind Agent.
function createHttpFacade(a, bridge) {
  const fail = (operation, module = 'node:http') => {
    const error = new Error(`${module}.${operation} is unavailable in the WASI HTTP message profile`);
    Object.assign(error, {code: 'ERR_SM_NODE_UNSUPPORTED', module, operation});
    throw error;
  };
  const stub = (name, id) => ({[name]: function() { return fail(name, id); }})[name];
  const {EventEmitter} = a;
  class Agent extends EventEmitter {
    constructor(options = {}) {
      super();
      if (!options || typeof options !== 'object') throw new TypeError('Agent options must be an object');
      this.options = {...options, noDelay: options.noDelay ?? true, path: null};
      this.defaultPort = 80; this.protocol = 'http:';
      this.requests = Object.create(null); this.sockets = Object.create(null); this.freeSockets = Object.create(null);
      this.keepAliveMsecs = options.keepAliveMsecs ?? 1000; this.keepAlive = options.keepAlive ?? false;
      this.maxSockets = options.maxSockets ?? Infinity; this.maxFreeSockets = options.maxFreeSockets ?? 256;
      this.maxTotalSockets = options.maxTotalSockets ?? Infinity; this.totalSocketCount = 0;
      this.scheduling = options.scheduling ?? 'lifo';
      if (!['fifo', 'lifo'].includes(this.scheduling)) {
        const e = new TypeError('Invalid Agent scheduling'); e.code = 'ERR_INVALID_ARG_VALUE'; throw e;
      }
    }
    // Pure identity formatting only, not an active socket pool.
    getName(options = {}) {
      let name = (options.host || 'localhost') + ':' + (options.port || '') + ':' + (options.localAddress || '');
      if (options.family === 4 || options.family === 6) name += ':' + options.family;
      if (options.socketPath) name += ':' + options.socketPath;
      return name;
    }
    destroy() {} // No resources can be acquired by this configuration object.
    addRequest() { return fail('Agent.addRequest'); }
    createConnection() { return fail('Agent.createConnection'); }
    createSocket() { return fail('Agent.createSocket'); }
    keepSocketAlive() { return fail('Agent.keepSocketAlive'); }
    reuseSocket() { return fail('Agent.reuseSocket'); }
    removeSocket() { return fail('Agent.removeSocket'); }
  }
  class HttpsAgent extends Agent {
    constructor(options) { super(options); this.defaultPort = 443; this.protocol = 'https:'; this.maxCachedSessions = 0; }
    getName(options = {}) {
      if (Object.keys(options).some(key => ['ca','cert','key','pfx','ciphers','servername','rejectUnauthorized','secureProtocol'].includes(key)))
        return fail('Agent.getName(TLS options)', 'node:https');
      return super.getName(options);
    }
  }
  function validateHeaderName(name) {
    if (typeof name !== 'string' || !/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/.test(name)) {
      const e = new TypeError('Invalid HTTP header name'); e.code = 'ERR_INVALID_HTTP_TOKEN'; throw e;
    }
  }
  function validateHeaderValue(name, value) {
    if (value === undefined) { const e = new TypeError('Undefined HTTP header value'); e.code = 'ERR_HTTP_INVALID_HEADER_VALUE'; throw e; }
    if (/[^\t\x20-\x7e\x80-\xff]/.test(String(value))) {
      const e = new TypeError('Invalid HTTP header value'); e.code = 'ERR_INVALID_CHAR'; throw e;
    }
  }
  const overrides = {Agent, IncomingMessage: bridge.BridgeIncomingMessage, ServerResponse: bridge.BridgeServerResponse,
    METHODS: [...a.inventory.METHODS], STATUS_CODES: {...a.inventory.STATUS_CODES}, maxHeaderSize: 16384,
    validateHeaderName, validateHeaderValue};
  function record(id, specific) {
    const values = {};
    for (const name of a.inventory.modules[id].exports) {
      if (name === 'default') continue;
      values[name] = Object.hasOwn(specific, name) ? specific[name]
        : a.inventory.modules[id].types[name] === 'function' ? stub(name, id) : undefined;
    }
    // Mutable CJS default; named exports retain their initial function values.
    return Object.freeze({...values, default: values});
  }
  overrides.globalAgent = new Agent({keepAlive: true, scheduling: 'lifo', timeout: 5000});
  const http = record('node:http', overrides);
  const https = record('node:https', {Agent: HttpsAgent, globalAgent: new HttpsAgent({keepAlive: true, scheduling: 'lifo', timeout: 5000})});
  // No identity fallback: both functions must be actual native context entries.
  if (typeof a.runFreshRequest !== 'function' || typeof a.runNeutralServer !== 'function' || typeof a.checkDeployed !== 'function')
    throw new TypeError('Native HTTP context bindings are required');
  const hosting = Object.freeze({
    runFreshRequest: a.runFreshRequest,
    runNeutralServer: a.runNeutralServer,
    createServerHandler(prepare) {
      a.checkDeployed();
      if (typeof prepare !== 'function') throw new TypeError('prepare must be a function');
      // Allocated at server-neutral scope, never in the first request's owner.
      const ready = a.runNeutralServer(() => Promise.resolve().then(prepare), undefined);
      return async function handle(request) {
        // The mandatory WASI adapter enters runFreshRequest BEFORE it converts
        // incoming resources into Request/body objects. Do not create a second
        // owner here; readiness continuation inherits that same request owner.
        const handler = await ready;
        if (typeof handler !== 'function') throw new TypeError('prepare must return the real Node request handler');
        return bridge.createRequestBridge(handler)(request);
      };
    },
  });
  return {http, https, hosting};
}

a.inventory={"schemaVersion":1,"inventoryVersion":"next-http-node-v22.14.0-v1","node":"v22.14.0","modules":{"node:http":{"exports":["Agent","ClientRequest","CloseEvent","IncomingMessage","METHODS","MessageEvent","OutgoingMessage","STATUS_CODES","Server","ServerResponse","WebSocket","_connectionListener","createServer","default","get","globalAgent","maxHeaderSize","request","setMaxIdleHTTPParsers","validateHeaderName","validateHeaderValue"],"types":{"Agent":"function","ClientRequest":"function","CloseEvent":"function","IncomingMessage":"function","METHODS":"object","MessageEvent":"function","OutgoingMessage":"function","STATUS_CODES":"object","Server":"function","ServerResponse":"function","WebSocket":"function","_connectionListener":"function","createServer":"function","default":"object","get":"function","globalAgent":"object","maxHeaderSize":"number","request":"function","setMaxIdleHTTPParsers":"function","validateHeaderName":"function","validateHeaderValue":"function"}},"node:https":{"exports":["Agent","Server","createServer","default","get","globalAgent","request"],"types":{"Agent":"function","Server":"function","createServer":"function","default":"object","get":"function","globalAgent":"object","request":"function"}}},"METHODS":["ACL","BIND","CHECKOUT","CONNECT","COPY","DELETE","GET","HEAD","LINK","LOCK","M-SEARCH","MERGE","MKACTIVITY","MKCALENDAR","MKCOL","MOVE","NOTIFY","OPTIONS","PATCH","POST","PROPFIND","PROPPATCH","PURGE","PUT","QUERY","REBIND","REPORT","SEARCH","SOURCE","SUBSCRIBE","TRACE","UNBIND","UNLINK","UNLOCK","UNSUBSCRIBE"],"STATUS_CODES":{"100":"Continue","101":"Switching Protocols","102":"Processing","103":"Early Hints","200":"OK","201":"Created","202":"Accepted","203":"Non-Authoritative Information","204":"No Content","205":"Reset Content","206":"Partial Content","207":"Multi-Status","208":"Already Reported","226":"IM Used","300":"Multiple Choices","301":"Moved Permanently","302":"Found","303":"See Other","304":"Not Modified","305":"Use Proxy","307":"Temporary Redirect","308":"Permanent Redirect","400":"Bad Request","401":"Unauthorized","402":"Payment Required","403":"Forbidden","404":"Not Found","405":"Method Not Allowed","406":"Not Acceptable","407":"Proxy Authentication Required","408":"Request Timeout","409":"Conflict","410":"Gone","411":"Length Required","412":"Precondition Failed","413":"Payload Too Large","414":"URI Too Long","415":"Unsupported Media Type","416":"Range Not Satisfiable","417":"Expectation Failed","418":"I'm a Teapot","421":"Misdirected Request","422":"Unprocessable Entity","423":"Locked","424":"Failed Dependency","425":"Too Early","426":"Upgrade Required","428":"Precondition Required","429":"Too Many Requests","431":"Request Header Fields Too Large","451":"Unavailable For Legal Reasons","500":"Internal Server Error","501":"Not Implemented","502":"Bad Gateway","503":"Service Unavailable","504":"Gateway Timeout","505":"HTTP Version Not Supported","506":"Variant Also Negotiates","507":"Insufficient Storage","508":"Loop Detected","509":"Bandwidth Limit Exceeded","510":"Not Extended","511":"Network Authentication Required"},"note":"HTTP protocol constants only; no host sockets, TLS state, handles or environment copied."};
return createHttpFacade(a,{BridgeIncomingMessage,BridgeServerResponse,createRequestBridge});
}))SM_HTTP";
