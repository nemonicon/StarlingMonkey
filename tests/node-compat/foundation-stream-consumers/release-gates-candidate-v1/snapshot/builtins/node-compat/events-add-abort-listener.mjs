// UNAPPLIED source template. A guest EventTarget supplies the unique Symbol;
// this factory is internal and is not a new node:events export.
export function createAddAbortListener(resistStopSymbol) {
  const TypeErrorCtor = TypeError;
  const define = Object.defineProperty;
  const enqueue = globalThis.queueMicrotask;
  const symbolFor = Symbol.for;
  const disposeSymbol = typeof Symbol.dispose === 'symbol' ? Symbol.dispose : symbolFor('nodejs.dispose');
  function invalid(name, description) {
    const error = new TypeErrorCtor(`The "${name}" argument must be ${description}.`);
    define(error, 'code', { __proto__: null, value: 'ERR_INVALID_ARG_TYPE', writable: true, configurable: true, enumerable: true });
    define(error, 'module', { __proto__: null, value: 'node:events', writable: true, configurable: true, enumerable: true });
    define(error, 'operation', { __proto__: null, value: 'addAbortListener', writable: true, configurable: true, enumerable: true });
    define(error, 'profile', { __proto__: null, value: 'sm-node-22.14.0-m0.10', writable: true, configurable: true, enumerable: true });
    return error;
  }
  if (typeof resistStopSymbol !== 'symbol' || typeof enqueue !== 'function') {
    throw new TypeErrorCtor('Unconfigured protected AbortListener guest factory');
  }
  return function addAbortListener(signal, listener) {
    // Match the pinned structural validator and its order; preserve user Proxy
    // has/get exceptions rather than replacing them with a native brand check.
    if (signal === undefined || signal === null || typeof signal !== 'object' || !('aborted' in signal)) {
      throw invalid('signal', 'an instance of AbortSignal');
    }
    if (typeof listener !== 'function') throw invalid('listener', 'of type function');
    let removeEventListener;
    if (signal.aborted) {
      // Drop the result: Starling queueMicrotask uses a Promise reaction while
      // Node's native microtask callback ignores returned arbitrary thenables.
      enqueue(() => { listener(); });
    } else {
      // Keep the original identity, duplicate tuple and dynamic public calls.
      signal.addEventListener('abort', listener, { __proto__: null, once: true, [resistStopSymbol]: true });
      removeEventListener = () => { signal.removeEventListener('abort', listener); };
    }
    return {
      __proto__: null,
      [disposeSymbol]() { removeEventListener?.(); },
    };
  };
}
