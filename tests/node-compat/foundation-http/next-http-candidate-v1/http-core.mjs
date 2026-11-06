// Small guest facade; bridge is supplied from the separately hashed real source.
// No network socket implementation or TLS provider is hidden behind Agent.
export function createHttpFacade(a, bridge) {
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
