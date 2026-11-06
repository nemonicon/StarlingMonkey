// Guest JS facade over the actual installed native AsyncLocalStorage snapshot.
// Import/installation captures no context and performs no I/O or task creation.
const installed = new WeakMap();
export function installAsyncResourceFacade(asyncHooks) {
  const apply = Reflect.apply, own = Object.getOwnPropertyDescriptor;
  const define = Object.defineProperty, hasOwn = Object.hasOwn;
  const get = Function.call.bind(WeakMap.prototype.get);
  const set = Function.call.bind(WeakMap.prototype.set);
  const prior = get(installed, asyncHooks);
  if (prior) {
    if (asyncHooks.AsyncResource !== prior.constructor)
      throw new TypeError('AsyncResource binding changed after installation');
    return prior.summary;
  }
  if (asyncHooks === null || typeof asyncHooks !== 'object')
    throw new TypeError('Expected mutable node:async_hooks default record');
  const descriptor = own(asyncHooks, 'AsyncResource');
  const ALS = asyncHooks.AsyncLocalStorage;
  if (!descriptor || !hasOwn(descriptor, 'value') || !descriptor.writable || !descriptor.configurable ||
      typeof ALS !== 'function' || typeof ALS.snapshot !== 'function')
    throw new TypeError('Expected original AsyncResource data binding and native ALS snapshot');
  const snapshot = ALS.snapshot;
  const captures = new WeakMap();
  const profile = 'sm-node-22.14.0-async-resource-m0.1';
  function fail(code, operation, message, Ctor = TypeError) {
    const error = new Ctor(message);
    for (const [key, value] of Object.entries({code, module:'node:async_hooks', operation, profile}))
      define(error, key, {value, writable:true, configurable:true, enumerable:true});
    throw error;
  }
  function unsupported(operation) {
    return function () {
      fail('ERR_SM_NODE_UNSUPPORTED', operation, operation + ' is outside this bounded profile', Error);
    };
  }
  class AsyncResource {
    constructor(type, options = undefined) {
      if (typeof type !== 'string') fail('ERR_INVALID_ARG_TYPE', 'AsyncResource', 'type must be a string');
      if (type.length > 4096) fail('ERR_SM_NODE_ASYNC_CONTEXT_LIMIT', 'AsyncResource', 'type exceeds 4096 code units', RangeError);
      if (options !== undefined) fail('ERR_SM_NODE_UNSUPPORTED', 'AsyncResource.options', 'AsyncResource options/trigger IDs are not implemented');
      // The app constructs resources only after deployed bootstrap. This is the
      // real native capture; no JS context stack, Promise patch or fake ID.
      set(captures, this, apply(snapshot, ALS, []));
    }
    runInAsyncScope(fn, thisArg, ...args) {
      const captured = get(captures, this);
      if (!captured) fail('ERR_INVALID_ARG_TYPE', 'AsyncResource.runInAsyncScope', 'Invalid AsyncResource receiver');
      if (typeof fn !== 'function') fail('ERR_INVALID_ARG_TYPE', 'AsyncResource.runInAsyncScope', 'fn must be a function');
      // snapshot's callback is one argument. The same native invoke has a 1024
      // argument cap; reserve that callback slot instead of bypassing the cap.
      if (args.length > 1023) fail('ERR_SM_NODE_ASYNC_CONTEXT_LIMIT', 'AsyncResource.runInAsyncScope', 'Bound argument limit exceeded', RangeError);
      return captured(() => apply(fn, thisArg, args));
    }
  }
  for (const name of ['bind', 'emitDestroy', 'asyncId', 'triggerAsyncId'])
    define(AsyncResource.prototype, name, {value:unsupported('AsyncResource.' + name), writable:true, configurable:true});
  define(AsyncResource, 'bind', {value:unsupported('AsyncResource.bind'), writable:true, configurable:true});
  const summary = Object.freeze({profile, cjsDefaultPatched:true, esmNamedBindingsUpdated:false,
    supported:['new AsyncResource(string)', 'runInAsyncScope'], nativeCapture:'AsyncLocalStorage.snapshot',
    fakeLifecycleIds:false, hooksImplemented:false, nativeGuestExecuted:false});
  define(asyncHooks, 'AsyncResource', {...descriptor, value:AsyncResource});
  set(installed, asyncHooks, {constructor:AsyncResource, summary});
  return summary;
}
