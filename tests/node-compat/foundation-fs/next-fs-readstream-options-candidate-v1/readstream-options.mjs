// Pure guest JS. Import/installation performs no IO. Calls delegate to the
// original profile ReadStream, including its deployed-phase and ownership guards.
const accepted = ['flags','encoding','fd','fs','mode','autoClose','emitClose','start','end','highWaterMark','signal'];
const sendOnly = ['root','acceptRanges','cacheControl','etag','dotfiles','hidden','extensions','immutable','index','lastModified','maxAge','maxage','from'];

export function normalizeReadStreamOptions(value) {
  function fail(code, operation) {
    const e = new TypeError(code === 'ERR_SM_NODE_UNSUPPORTED' ? 'node:fs.' + operation + ' is outside this bounded profile' : operation);
    e.code = code; e.module = 'node:fs'; e.operation = operation; throw e;
  }
  if (value === undefined || value === null) return {};
  if (typeof value === 'string') return {encoding:value};
  if (typeof value !== 'object' || Array.isArray(value)) fail('ERR_INVALID_ARG_TYPE','options');
  // Retain the existing bounded policy for symbols and unknown own keys.
  for (const key of Reflect.ownKeys(value)) {
    if (typeof key !== 'string' || (!accepted.includes(key) && !sendOnly.includes(key))) fail('ERR_SM_NODE_UNSUPPORTED','createReadStream.' + String(key));
  }
  const result = Object.create(null);
  // Node22 copyObject and send both use for-in: inherited enumerable options
  // and getters matter. Read each accepted value once, preserving original
  // thrown values. A null-prototype target avoids any __proto__ setter.
  for (const key in value) {
    if (!accepted.includes(key) && !sendOnly.includes(key)) fail('ERR_SM_NODE_UNSUPPORTED','createReadStream.' + key);
    const entry = value[key];
    if (accepted.includes(key)) result[key] = entry;
  }
  return result;
}

const installed = new WeakMap();
export function installReadStreamOptionsFacade(fs) {
  const prior = installed.get(fs);
  if (prior) {
    if (fs.createReadStream !== prior.createReadStream || fs.ReadStream !== prior.ReadStream || fs.FileReadStream !== prior.ReadStream) throw new Error('ReadStream options facade was replaced after installation');
    return prior.summary;
  }
  if (fs === null || typeof fs !== 'object') throw new TypeError('Expected mutable node:fs default record');
  const original = fs.ReadStream;
  if (typeof original !== 'function' || fs.FileReadStream !== original || typeof fs.createReadStream !== 'function') throw new TypeError('Expected original profile ReadStream aliases');
  const names = ['createReadStream','ReadStream','FileReadStream'];
  const descriptors = names.map(name => Object.getOwnPropertyDescriptor(fs,name));
  if (descriptors.some(d => !d || !Object.hasOwn(d,'value') || !d.writable || !d.configurable)) throw new TypeError('Expected writable configurable node:fs data bindings');
  function ReadStream(path, options) {
    if (!new.target) return new ReadStream(path,options);
    const target = new.target;
    const stream = Reflect.construct(original,[path,normalizeReadStreamOptions(options)],target);
    // The current profile's function constructor explicitly returns its real
    // ReadStreamImpl instance. Give that object the genuine derived prototype;
    // its Readable state and native-handle WeakMap remain on the same instance.
    if (Object.getPrototypeOf(stream) !== target.prototype) Object.setPrototypeOf(stream,target.prototype);
    return stream;
  }
  ReadStream.prototype = Object.create(original.prototype,{constructor:{value:ReadStream,writable:true,configurable:true}});
  Object.setPrototypeOf(ReadStream,original);
  function createReadStream(path,options) { return new ReadStream(path,options); }
  const values = [createReadStream,ReadStream,ReadStream];
  for (let i=0;i<names.length;i++) Object.defineProperty(fs,names[i],{...descriptors[i],value:values[i]});
  const summary = Object.freeze({kind:'bounded-readstream-send-options-v1',cjsDefaultPatched:true,esmNamedBindingsUpdated:false,additionalHostInterfaces:false});
  installed.set(fs,{createReadStream,ReadStream,summary});
  return summary;
}
