// Additional mutable-public-API and retained-primordial checks for the native
// optional facade. Keep the original isolated prototype corpus immutable.
export function nativeEventsChecks(events) {
  const E = events.EventEmitter, result = [];
  {
    const original = E.init, trace = [];
    try {
      E.init = function(options) { trace.push(options.value); return Reflect.apply(original, this, [options]); };
      const e = new E({ value: 7 }); e.on('x', () => {});
      result.push({ name: 'mutable-init-with-named-snapshot', trace, count: e.listenerCount('x'), namedUnchanged: events.init === original });
    } finally { E.init = original; }
  }
  {
    const descriptor = Object.getOwnPropertyDescriptor(E, 'defaultMaxListeners'); let errorName;
    try { Object.defineProperty(E, 'defaultMaxListeners', { configurable: true, get() { return 17; } }); }
    catch (error) { errorName = error.name; }
    result.push({ name: 'protected-default-threshold-descriptor', configurable: descriptor.configurable, errorName, value: new E().getMaxListeners(), namedSnapshot: events.defaultMaxListeners });
  }
  {
    const e = new E(); let called = 0;
    e.getMaxListeners = () => { called++; throw new Error('internal insertion must not call public method'); };
    e.on('x', () => {}).on('x', () => {});
    result.push({ name: 'internal-threshold-does-not-call-public-override', count: e.listenerCount('x'), called });
  }
  {
    const saved = { apply: Reflect.apply, keys: Reflect.ownKeys, create: Object.create, bind: Function.prototype.bind,
      slice: Array.prototype.slice, push: Array.prototype.push, unshift: Array.prototype.unshift, splice: Array.prototype.splice,
      iterator: Array.prototype[Symbol.iterator], nan: Number.isNaN, error: globalThis.Error };
    const a = new E(), expected = new Error('same'), trace = { calls: 0, sameError: false, max: null };
    const callback = () => { trace.calls++; }; a.on('x', callback).on('x', callback); a.once('y', callback);
    const OriginalError = globalThis.Error;
    function poison() { throw new OriginalError('public intrinsic replacement must not run'); }
    try {
      Reflect.apply = poison; Reflect.ownKeys = poison; Object.create = poison; Function.prototype.bind = poison;
      Array.prototype.slice = poison; Array.prototype.push = poison; Array.prototype.unshift = poison; Array.prototype.splice = poison;
      Array.prototype[Symbol.iterator] = poison; Number.isNaN = () => false; globalThis.Error = function ChangedError() {};
      a.emit('x'); a.removeListener('x', callback); a.emit('y');
      a.setMaxListeners(0); trace.max = a.getMaxListeners();
      try { a.emit('error', expected); } catch (error) { trace.sameError = error === expected; }
      trace.names = a.eventNames().length; a.removeAllListeners(); trace.remaining = a.eventNames().length;
    } finally {
      Reflect.apply = saved.apply; Reflect.ownKeys = saved.keys; Object.create = saved.create; Function.prototype.bind = saved.bind;
      Array.prototype.slice = saved.slice; Array.prototype.push = saved.push; Array.prototype.unshift = saved.unshift; Array.prototype.splice = saved.splice;
      Array.prototype[Symbol.iterator] = saved.iterator; Number.isNaN = saved.nan; globalThis.Error = saved.error;
    }
    result.push({ name: 'retained-language-primordials', ...trace });
  }
  return result;
}
