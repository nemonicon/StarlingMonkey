// UNAPPLIED factory snapshot; existing EventEmitter algorithms preserved.
import {createAddAbortListener} from './add-abort.mjs';
export function createEventsFacade(resistStopSymbol) {
// Optional bounded node:events semantic facade; installed only when selected.
// Core listener algorithms follow Node.js22.14.0 lib/events.js and events3.3.0.
// Copyright Joyent, Inc. and other Node contributors. MIT; see LICENSE.events.
const apply = Reflect.apply, keys = Reflect.ownKeys, create = Object.create;
const getPrototypeOf = Object.getPrototypeOf, define = Object.defineProperty;
const slice = Function.call.bind(Array.prototype.slice);
const push = Function.call.bind(Array.prototype.push), unshift = Function.call.bind(Array.prototype.unshift);
const splice = Function.call.bind(Array.prototype.splice);
const depths = new WeakMap();
const ErrorCtor = Error, TypeErrorCtor = TypeError, RangeErrorCtor = RangeError;
const numberIsNaN = Number.isNaN, bind = Function.call.bind(Function.prototype.bind);
const depthGet = Function.call.bind(WeakMap.prototype.get), depthSet = Function.call.bind(WeakMap.prototype.set);
const MAX_NAMES = 4096, MAX_LISTENERS = 65536, MAX_DEPTH = 64;
let maxDefault = 10;
const defaultMaxListeners = 10; // Node ESM snapshot; constructor property is mutable.
const captureRejections = false;
const usingDomains = false;
const captureRejectionSymbol = Symbol.for('nodejs.rejection');
const errorMonitor = Symbol('events.errorMonitor');
const kMaxEventTargetListeners = Symbol('events.maxEventTargetListeners');
const kMaxEventTargetListenersWarned = Symbol('events.maxEventTargetListenersWarned');
function failure(code, operation, message, ErrorType = ErrorCtor) {
  const error = new ErrorType(`${code}: ${message}`);
  define(error, 'code', {__proto__:null,value:code,writable:true,configurable:true,enumerable:true});
  define(error, 'module', {__proto__:null,value:'node:events',writable:true,configurable:true,enumerable:true});
  define(error, 'operation', {__proto__:null,value:operation,writable:true,configurable:true,enumerable:true});
  define(error, 'profile', {__proto__:null,value:'sm-node-22.14.0-m0.10',writable:true,configurable:true,enumerable:true});
  return error;
}
function deferred(operation) { throw failure('ERR_SM_NODE_UNSUPPORTED', operation, `node:events.${operation} is deferred by this profile`); }
function limit(operation) { throw failure('ERR_SM_NODE_LIMIT', operation, `node:events.${operation} exceeds the bounded profile limit`, RangeErrorCtor); }
function eventKey(type) {
  if (typeof type !== 'string' && typeof type !== 'symbol') deferred('eventNameCoercion');
  return type;
}
function checkListener(listener) {
  if (typeof listener !== 'function') throw failure('ERR_INVALID_ARG_TYPE', 'listener', 'The listener argument must be a function', TypeErrorCtor);
}
function checkNumber(value, operation) {
  if (typeof value !== 'number') throw failure('ERR_INVALID_ARG_TYPE', operation, 'The argument must be a number', TypeErrorCtor);
  if (numberIsNaN(value) || value < 0) throw failure('ERR_OUT_OF_RANGE', operation, 'The argument must be >= 0', RangeErrorCtor);
}
function init(options) {
  if (this._events === undefined || this._events === getPrototypeOf(this)?._events) {
    this._events = create(null); this._eventsCount = 0;
  }
  this._maxListeners = this._maxListeners || undefined;
  const capture = options?.captureRejections;
  if (capture) {
    if (typeof capture !== 'boolean') throw failure('ERR_INVALID_ARG_TYPE', 'captureRejections', 'captureRejections must be boolean', TypeErrorCtor);
    deferred('captureRejections');
  }
}
function EventEmitter(options) { apply(EventEmitter.init, this, [options]); }
EventEmitter.prototype._events = undefined;
EventEmitter.prototype._eventsCount = 0;
EventEmitter.prototype._maxListeners = undefined;
function add(target, type, listener, prepend) {
  checkListener(listener); eventKey(type);
  let events = target._events;
  if (events === undefined) { events = target._events = create(null); target._eventsCount = 0; }
  else if (events.newListener !== undefined) {
    target.emit('newListener', type, listener.listener || listener);
    events = target._events;
  }
  const existing = events[type];
  if (existing === undefined) {
    if (target._eventsCount >= MAX_NAMES) limit('eventNames');
    events[type] = listener; target._eventsCount++;
  } else {
    const count = typeof existing === 'function' ? 1 : existing.length;
    if (count >= MAX_LISTENERS) limit('addListener');
    if (typeof existing === 'function') events[type] = prepend ? [listener, existing] : [existing, listener];
    else if (prepend) unshift(existing, listener); else push(existing, listener);
    const list = events[type], maximum = maximumFor(target);
    // Node's threshold is advisory, not an insertion cap. Preserve state and
    // warned marker, but process.emitWarning delivery is deliberately deferred.
    if (maximum > 0 && list.length > maximum && !list.warned) list.warned = true;
  }
  return target;
}
EventEmitter.prototype.setMaxListeners = function setMaxListeners(n) { checkNumber(n, 'setMaxListeners'); this._maxListeners = n; return this; };
function maximumFor(target) { return target._maxListeners === undefined ? EventEmitter.defaultMaxListeners : target._maxListeners; }
EventEmitter.prototype.getMaxListeners = function getMaxListeners() { return maximumFor(this); };
EventEmitter.prototype.emit = function emit(type, ...args) {
  eventKey(type);
  const depth = depthGet(depths, this) ?? 0;
  if (depth >= MAX_DEPTH) limit('emit');
  depthSet(depths, this, depth + 1);
  try {
    const events = this._events;
    let unhandled = type === 'error';
    if (events !== undefined) {
      if (unhandled && events[errorMonitor] !== undefined) this.emit(errorMonitor, ...args);
      unhandled = unhandled && events.error === undefined;
    } else if (!unhandled) return false;
    if (unhandled) {
      if (args[0] instanceof ErrorCtor) throw args[0];
      const error = failure('ERR_UNHANDLED_ERROR', 'emit', 'Unhandled error event'); error.context = args[0]; throw error;
    }
    const listener = events[type];
    if (listener === undefined) return false;
    if (typeof listener === 'function') apply(listener, this, args);
    else { const snapshot = slice(listener); for (let i = 0; i < snapshot.length; i++) apply(snapshot[i], this, args); }
    return true;
  } finally { depthSet(depths, this, depth); }
};
EventEmitter.prototype.addListener = function addListener(type, listener) { return add(this, type, listener, false); };
EventEmitter.prototype.on = EventEmitter.prototype.addListener;
EventEmitter.prototype.prependListener = function prependListener(type, listener) { return add(this, type, listener, true); };
function onceWrapper(...args) {
  if (!this.fired) {
    this.target.removeListener(this.type, this.wrapFn); this.fired = true;
    return apply(this.listener, this.target, args);
  }
}
function wrapOnce(target, type, listener) {
  const state = { fired: false, target, type, listener, wrapFn: undefined };
  state.wrapFn = bind(onceWrapper, state); state.wrapFn.listener = listener; return state.wrapFn;
}
EventEmitter.prototype.once = function once(type, listener) { checkListener(listener); eventKey(type); return this.on(type, wrapOnce(this, type, listener)); };
EventEmitter.prototype.prependOnceListener = function prependOnceListener(type, listener) { checkListener(listener); eventKey(type); return this.prependListener(type, wrapOnce(this, type, listener)); };
EventEmitter.prototype.removeListener = function removeListener(type, listener) {
  checkListener(listener); eventKey(type);
  const events = this._events, list = events?.[type];
  if (list === undefined) return this;
  if (list === listener || list.listener === listener) {
    this._eventsCount--;
    if (this._eventsCount === 0) this._events = create(null);
    else { delete events[type]; if (events.removeListener) this.emit('removeListener', type, list.listener || listener); }
  } else if (typeof list !== 'function') {
    let position = -1;
    for (let i = list.length - 1; i >= 0; --i) if (list[i] === listener || list[i].listener === listener) { position = i; break; }
    if (position < 0) return this;
    splice(list, position, 1);
    if (list.length === 1) events[type] = list[0];
    if (events.removeListener !== undefined) this.emit('removeListener', type, listener);
  }
  return this;
};
EventEmitter.prototype.off = EventEmitter.prototype.removeListener;
EventEmitter.prototype.removeAllListeners = function removeAllListeners(type) {
  const events = this._events;
  if (events === undefined) return this;
  if (arguments.length) eventKey(type);
  if (events.removeListener === undefined) {
    if (!arguments.length) { this._events = create(null); this._eventsCount = 0; }
    else if (events[type] !== undefined) { if (--this._eventsCount === 0) this._events = create(null); else delete events[type]; }
    return this;
  }
  if (!arguments.length) {
    const names = keys(events);
    for (let i = 0; i < names.length; i++) if (names[i] !== 'removeListener') this.removeAllListeners(names[i]);
    this.removeAllListeners('removeListener'); this._events = create(null); this._eventsCount = 0; return this;
  }
  const list = events[type];
  if (typeof list === 'function') this.removeListener(type, list);
  else if (list !== undefined) for (let i = list.length - 1; i >= 0; --i) this.removeListener(type, list[i]);
  return this;
};
function listenerArray(target, type, unwrap) {
  eventKey(type); const entry = target._events?.[type];
  const result = entry === undefined ? [] : typeof entry === 'function' ? [entry] : slice(entry);
  if (unwrap) for (let i = 0; i < result.length; i++) result[i] = result[i].listener || result[i];
  return result;
}
EventEmitter.prototype.listeners = function listeners(type) { return listenerArray(this, type, true); };
EventEmitter.prototype.rawListeners = function rawListeners(type) { return listenerArray(this, type, false); };
EventEmitter.prototype.listenerCount = function listenerCount(type, listener) {
  eventKey(type); const entry = this._events?.[type];
  if (entry === undefined) return 0;
  if (listener == null) return typeof entry === 'function' ? 1 : entry.length;
  const list = typeof entry === 'function' ? [entry] : entry; let count = 0;
  for (let i = 0; i < list.length; i++) if (list[i] === listener || list[i].listener === listener) count++;
  return count;
};
EventEmitter.prototype.eventNames = function eventNames() { return this._eventsCount > 0 ? keys(this._events) : []; };
function listenerCount(emitter, type) { return typeof emitter.listenerCount === 'function' ? emitter.listenerCount(type) : apply(EventEmitter.prototype.listenerCount, emitter, [type]); }
function getEventListeners(emitter, type) { if (typeof emitter?.listeners === 'function') return emitter.listeners(type); deferred('getEventListeners.EventTarget'); }
function getMaxListeners(emitter) { if (typeof emitter?.getMaxListeners === 'function') return emitter.getMaxListeners(); deferred('getMaxListeners.EventTarget'); }
function setMaxListeners(n = maxDefault, ...targets) {
  checkNumber(n, 'setMaxListeners');
  if (!targets.length) { maxDefault = n; return; }
  for (let i = 0; i < targets.length; i++) { const target = targets[i]; if (typeof target?.setMaxListeners !== 'function') deferred('setMaxListeners.EventTarget'); target.setMaxListeners(n); }
}
function once(emitter, name, options = undefined) { deferred('once'); }
function on(emitter, event, options = undefined) { deferred('on'); }
const addAbortListener = createAddAbortListener(resistStopSymbol);
function EventEmitterAsyncResource(options = undefined) { deferred('EventEmitterAsyncResource'); }
for (const fn of [init, listenerCount, setMaxListeners]) define(fn, 'name', { value: '', configurable: true });
Object.assign(EventEmitter, { EventEmitter, init, listenerCount, getEventListeners, getMaxListeners, setMaxListeners,
  once, on, addAbortListener, EventEmitterAsyncResource, captureRejectionSymbol, errorMonitor, usingDomains, kMaxEventTargetListeners, kMaxEventTargetListenersWarned });
define(EventEmitter, 'defaultMaxListeners', { enumerable: true, get() { return maxDefault; }, set(n) { checkNumber(n, 'defaultMaxListeners'); maxDefault = n; } });
define(EventEmitter, 'captureRejections', { enumerable: true, get() { return false; }, set(value) {
  if (typeof value !== 'boolean') throw failure('ERR_INVALID_ARG_TYPE', 'captureRejections', 'captureRejections must be boolean', TypeErrorCtor);
  if (value) deferred('captureRejections');
} });

return Object.freeze({EventEmitter, EventEmitterAsyncResource, addAbortListener, captureRejectionSymbol, captureRejections, default: EventEmitter, defaultMaxListeners, errorMonitor, getEventListeners, getMaxListeners, init, listenerCount, on, once, setMaxListeners, usingDomains});
}
