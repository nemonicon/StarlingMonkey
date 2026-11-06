// Guest profile extension for Node's classic-readable Request BodyInit.
// Installation is pure. Ordinary calls use the existing selected Readable.toWeb.
export function installClassicRequestBody(Readable, target = globalThis) {
  const NativeRequest = target.Request;
  if (typeof NativeRequest !== 'function' || typeof Readable !== 'function' ||
      typeof Readable.toWeb !== 'function') throw new TypeError('Native Request and selected Readable.toWeb are required');
  const publicDescriptor = Object.getOwnPropertyDescriptor(target, 'Request');
  const constructorDescriptor = Object.getOwnPropertyDescriptor(NativeRequest.prototype, 'constructor');
  if (!publicDescriptor || !Object.hasOwn(publicDescriptor, 'value') || !publicDescriptor.configurable ||
      !constructorDescriptor || !Object.hasOwn(constructorDescriptor, 'value') || !constructorDescriptor.configurable)
    throw new TypeError('Request must have configurable public data bindings');
  const apply = Reflect.apply, construct = Reflect.construct, get = Reflect.get;
  const hasInstance = Function.prototype[Symbol.hasInstance];
  const toWeb = Readable.toWeb;
  const cancel = target.ReadableStream.prototype.cancel;
  const then = target.Promise.prototype.then;
  const reportCleanup = error => { try { console.error('REQUEST_CLASSIC_BODY_CLEANUP_FAILURE', error); } catch {} };
  function initView(init) {
    if (init === null || (typeof init !== 'object' && typeof init !== 'function')) return {value: init};
    let bodyRead = false, body, converted;
    // An empty forwarding target avoids Proxy invariants for frozen/non-writable
    // input dictionaries. Other getters retain their original receiver and order.
    const value = new Proxy(Object.create(null), {
      get(_unused, key) {
        if (key !== 'body') return get(init, key, init);
        if (!bodyRead) {
          body = get(init, key, init);
          if (body !== null && (typeof body === 'object' || typeof body === 'function') &&
              apply(hasInstance, Readable, [body])) converted = body = apply(toWeb, Readable, [body]);
          bodyRead = true;
        }
        return body;
      },
    });
    return {value, retire(reason) {
      if (converted === undefined) return;
      // A synchronous native constructor refusal must not leave a toWeb lease.
      // Preserve its thrown identity; any secondary async cleanup refusal is
      // retained in stderr rather than replacing that primary exception.
      try { apply(then, apply(cancel, converted, [reason]), [undefined, reportCleanup]); }
      catch (error) { reportCleanup(error); }
    }};
  }
  const Request = new Proxy(NativeRequest, {
    construct(native, args, newTarget) {
      if (args.length < 2) return construct(native, args, newTarget);
      const forwarded = args.slice();
      const init = initView(forwarded[1]);
      forwarded[1] = init.value;
      try { return construct(native, forwarded, newTarget); }
      catch (error) { init.retire?.(error); throw error; }
    },
  });
  // Sharing the genuine native prototype preserves native brand checks, clones,
  // public instanceof and NextRequest subclassing. No method is replaced.
  Object.defineProperty(NativeRequest.prototype, 'constructor', {...constructorDescriptor, value: Request});
  try { Object.defineProperty(target, 'Request', {...publicDescriptor, value: Request}); }
  catch (error) {
    Object.defineProperty(NativeRequest.prototype, 'constructor', constructorDescriptor);
    throw error;
  }
  return Object.freeze({
    restore() {
      if (target.Request === Request) Object.defineProperty(target, 'Request', publicDescriptor);
      const current = Object.getOwnPropertyDescriptor(NativeRequest.prototype, 'constructor');
      if (current && Object.hasOwn(current, 'value') && current.value === Request)
        Object.defineProperty(NativeRequest.prototype, 'constructor', constructorDescriptor);
    },
  });
}
