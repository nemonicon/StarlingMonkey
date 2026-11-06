// Guest profile initialization; standard native modules, no host shim.
import {addAbortListener as __nextProtectedAbortListener} from 'node:events';
import * as __nextNativeWebStreams from 'node:stream/web';
// Guest-only profile facade. Real stream/AbortSignal objects and protected
// node:events.addAbortListener are required. Installation performs no IO/tasks.
function createSignalPipeTo({
  ReadableStream: RS, WritableStream: WS,
  ReadableStreamDefaultReader: Reader, WritableStreamDefaultWriter: Writer,
  AbortSignal: Signal, Promise: P, addAbortListener,
}) {
  if (typeof addAbortListener !== 'function') throw new TypeError('Protected addAbortListener is required');
  const apply = Reflect.apply;
  const own = Object.getOwnPropertyDescriptor;
  const get = (proto, key) => own(proto, key).get;
  const original = RS.prototype.pipeTo;
  const sourceLocked = get(RS.prototype, 'locked');
  const destLocked = get(WS.prototype, 'locked');
  const getReader = RS.prototype.getReader, getWriter = WS.prototype.getWriter;
  const read = Reader.prototype.read, cancel = Reader.prototype.cancel, releaseReader = Reader.prototype.releaseLock;
  const write = Writer.prototype.write, close = Writer.prototype.close, abort = Writer.prototype.abort, releaseWriter = Writer.prototype.releaseLock;
  const readerClosed = get(Reader.prototype, 'closed'), writerClosed = get(Writer.prototype, 'closed');
  const writerReady = get(Writer.prototype, 'ready'), desiredSize = get(Writer.prototype, 'desiredSize');
  const isAborted = get(Signal.prototype, 'aborted'), reason = get(Signal.prototype, 'reason');
  const then = P.prototype.then;
  const resolve = value => apply(P.resolve, P, [value]);
  const reject = value => apply(P.reject, P, [value]);
  const observe = (promise, fulfilled, rejected) => apply(then, promise, [fulfilled, rejected]);
  const disposeKey = typeof Symbol.dispose === 'symbol' ? Symbol.dispose : Symbol.for('nodejs.dispose');
  return function pipeTo(destination, options = undefined) {
    let reader, writer, signal, preventAbort, preventCancel, preventClose;
    try {
      // Intrinsic getters brand-check without invoking user shadow properties.
      apply(sourceLocked, this, []);
      apply(destLocked, destination, []);
      if (options !== undefined && options !== null && typeof options !== 'object')
        throw new TypeError('pipeTo options must be an object, null or undefined');
      preventAbort = !!options?.preventAbort;
      preventCancel = !!options?.preventCancel;
      preventClose = !!options?.preventClose;
      signal = options?.signal;
      if (signal === undefined) {
        return apply(original, this, [destination, {preventAbort, preventCancel, preventClose}]);
      }
      apply(isAborted, signal, []);
      if (apply(sourceLocked, this, []) || apply(destLocked, destination, [])) throw new TypeError('pipeTo requires unlocked streams');
      reader = apply(getReader, this, []);
      try { writer = apply(getWriter, destination, []); }
      catch (error) { apply(releaseReader, reader, []); throw error; }
    } catch (error) { return reject(error); }
    destination = null; options = undefined;
    let resolveResult, rejectResult;
    const result = new P((yes, no) => { resolveResult = yes; rejectResult = no; });
    let shuttingDown = false, finished = false, sourceClosing = false;
    let sourceState = 'readable', destState = 'writable', disposable;
    let currentWrite = resolve(), currentRead;
    const ignore = () => {};
    function finish(rejected, value) {
      if (finished) return;
      finished = true;
      let cleanupFailed = false, cleanupError;
      for (const action of [
        () => { if (disposable !== undefined) apply(disposable[disposeKey], disposable, []); },
        () => apply(releaseWriter, writer, []),
        () => apply(releaseReader, reader, []),
      ]) {
        try { action(); } catch (error) { if (!cleanupFailed) { cleanupFailed = true; cleanupError = error; } }
      }
      reader = writer = signal = disposable = undefined;
      if (cleanupFailed) rejectResult(cleanupError);
      else if (rejected) rejectResult(value);
      else resolveResult(undefined);
    }
    async function waitWrites() {
      for (;;) {
        const pending = currentWrite;
        await pending;
        if (pending === currentWrite) return;
      }
    }
    function shutdown(action, rejected, value, fromSourceClose = false) {
      if (shuttingDown) return;
      shuttingDown = true; sourceClosing = fromSourceClose;
      // Consume this internal async chain's rejection. The public result is the
      // sole caller-visible completion; release failures are never suppressed.
      observe((async () => {
        try {
          if (fromSourceClose) {
            if (currentRead === undefined) currentRead = apply(read, reader, []); // closed: mark disturbed, no chunk lost
            await currentRead;
          }
          if (destState === 'writable' && apply(desiredSize, writer, []) !== null) await waitWrites();
          if (action !== undefined) await action();
          finish(rejected, value);
        } catch (error) { finish(true, error); }
      })(), ignore, error => finish(true, error));
    }
    const cancelSource = error => sourceState === 'readable' ? apply(cancel, reader, [error]) : resolve();
    const abortDestination = error => destState === 'writable' ? apply(abort, writer, [error]) : resolve();
    function sourceErrored(error) {
      sourceState = 'errored';
      shutdown(preventAbort ? undefined : () => abortDestination(error), true, error);
    }
    function destinationErrored(error) {
      destState = 'errored';
      shutdown(preventCancel ? undefined : () => cancelSource(error), true, error);
    }
    function sourceClosed() {
      sourceState = 'closed';
      shutdown(preventClose ? undefined : () => apply(close, writer, []), false, undefined, true);
    }
    function destinationClosed() {
      destState = 'closed';
      if (shuttingDown) return;
      const error = new TypeError('Destination WritableStream is closed');
      shutdown(preventCancel ? undefined : () => cancelSource(error), true, error);
    }
    function abortPipe() {
      if (shuttingDown) return;
      const error = apply(reason, signal, []);
      shutdown(() => {
        const actions = [];
        if (!preventAbort) actions.push(abortDestination(error));
        if (!preventCancel) actions.push(cancelSource(error));
        return apply(P.all, P, [actions]);
      }, true, error);
    }
    try {
      // Capture both closed promises while locks are still held. Releasing the
      // reader later rejects pending read requests; the pump handles that path.
      observe(apply(readerClosed, reader, []), sourceClosed, sourceErrored);
      observe(apply(writerClosed, writer, []), destinationClosed, destinationErrored);
      if (apply(isAborted, signal, [])) abortPipe();
      else disposable = addAbortListener(signal, abortPipe);
      observe((async () => {
        while (!shuttingDown) {
          await apply(writerReady, writer, []);
          if (shuttingDown) return;
          currentRead = observe(apply(read, reader, []), record => {
            if (record.done) { sourceClosed(); return true; }
            // The public closed promise can settle before read's chunk reaction.
            // A source-close shutdown must forward that already-read final chunk.
            if (shuttingDown && !sourceClosing) return true;
            currentWrite = apply(write, writer, [record.value]);
            observe(currentWrite, ignore, destinationErrored);
            return false;
          }, error => { sourceErrored(error); return true; });
          if (await currentRead) return;
        }
      })(), ignore, destinationErrored);
    } catch (error) {
      shutdown(undefined, true, error);
    }
    return result;
  };
}

function installSignalPipeTo(addAbortListener, target = globalThis, web = target) {
  if (web.ReadableStream !== target.ReadableStream || web.WritableStream !== target.WritableStream)
    throw new TypeError('Profile stream constructors must be the actual global native streams');
  const descriptor = Object.getOwnPropertyDescriptor(target.ReadableStream.prototype, 'pipeTo');
  const pipeTo = createSignalPipeTo({
    ReadableStream: target.ReadableStream, WritableStream: target.WritableStream,
    ReadableStreamDefaultReader: web.ReadableStreamDefaultReader,
    WritableStreamDefaultWriter: web.WritableStreamDefaultWriter,
    AbortSignal: target.AbortSignal, Promise: target.Promise, addAbortListener,
  });
  Object.defineProperty(target.ReadableStream.prototype, 'pipeTo', {...descriptor, value: pipeTo});
  return pipeTo;
}

installSignalPipeTo(__nextProtectedAbortListener,globalThis,__nextNativeWebStreams);
