// Isolated bounded Node v22.14.0 Assert proposal. Not a registered builtin.
// Semantic references: Node v22.14.0 lib/assert.js and internal/assert/*.
// See README.md for the deliberately smaller diagnostic/matcher contract.
const Apply = Reflect.apply;
const Define = Object.defineProperty;
const Assign = Object.assign;
const Is = Object.is;
const IsNaN = Number.isNaN;
const IsArray = Array.isArray;
const IsPrototypeOf = Object.prototype.isPrototypeOf;
const ErrorCtor = Error;
const TypeErrorCtor = TypeError;
const StringCtor = String;
const RegExpExec = RegExp.prototype.exec;
const RegExpSource = Object.getOwnPropertyDescriptor(RegExp.prototype, 'source').get;

function typedError(code, operation, message) {
  const error = new TypeErrorCtor(message);
  error.code = code;
  error.operation = operation;
  return error;
}
function unsupported(operation) {
  throw typedError('ERR_SM_NODE_UNSUPPORTED', operation, `ERR_SM_NODE_UNSUPPORTED: node:assert ${operation} is deferred in this profile`);
}
function invalid(name, type) {
  throw typedError('ERR_INVALID_ARG_TYPE', name, `The "${name}" argument must be ${type}`);
}
function requirePair(length) {
  if (length < 2) throw typedError('ERR_MISSING_ARGS', 'actual, expected', 'The "actual" and "expected" arguments must be specified');
}
function isRegExp(value) {
  try { Apply(RegExpSource, value, []); return true; } catch { return false; }
}
// Auto diagnostics intentionally do not inspect application objects, invoke
// custom inspection hooks, or traverse cycles. Actual/expected remain references.
function describe(value) {
  if (value === null) return 'null';
  if (typeof value === 'object') return '[object]';
  if (typeof value === 'function') return '[function]';
  if (typeof value === 'string') return `'${value}'`;
  return StringCtor(value);
}
export class AssertionError extends ErrorCtor {
  constructor(options) {
    if (options === null || typeof options !== 'object' || IsArray(options)) invalid('options', 'an object');
    const { message, operator, actual, expected, details } = options;
    if (details !== undefined) unsupported('AssertionError.details');
    super(message == null ? `${describe(actual)} ${typeof operator === 'string' ? operator : '=='} ${describe(expected)}` : StringCtor(message));
    this.generatedMessage = !message;
    Define(this, 'name', { value: 'AssertionError', writable: true, configurable: true });
    this.code = 'ERR_ASSERTION';
    this.actual = actual;
    this.expected = expected;
    this.operator = operator;
  }
  toString() { return `${this.name} [${this.code}]: ${this.message}`; }
}
function failure(actual, expected, operator, message, generated, rethrowErrorMessage = true) {
  if (rethrowErrorMessage && message instanceof ErrorCtor) throw message;
  const error = new AssertionError({ actual, expected, operator, message });
  if (generated !== undefined) error.generatedMessage = generated;
  throw error;
}
function innerOk(length, value, message) {
  if (value) return;
  let generated = false;
  if (length === 0) { message = 'No value argument passed to `assert.ok()`'; generated = true; }
  else if (message == null) generated = true;
  failure(value, true, '==', message, generated);
}
export function ok(...args) { innerOk(args.length, args[0], args[1]); }
export function fail(actual, expected, message, operator, stackStartFn) {
  if (arguments.length > 1) unsupported('fail.legacy-overload');
  let generated;
  if (actual == null) { message = 'Failed'; generated = true; }
  else { message = actual; actual = undefined; }
  failure(actual, undefined, 'fail', message, generated);
}
export function equal(actual, expected, message) {
  requirePair(arguments.length);
  if (actual != expected && (!IsNaN(actual) || !IsNaN(expected))) failure(actual, expected, '==', message);
}
export function notEqual(actual, expected, message) {
  requirePair(arguments.length);
  if (actual == expected || (IsNaN(actual) && IsNaN(expected))) failure(actual, expected, '!=', message);
}
export function strictEqual(actual, expected, message) {
  requirePair(arguments.length);
  if (!Is(actual, expected)) failure(actual, expected, 'strictEqual', message);
}
export function notStrictEqual(actual, expected, message) {
  requirePair(arguments.length);
  if (Is(actual, expected)) failure(actual, expected, 'notStrictEqual', message);
}
export function deepEqual(actual, expected, message) { unsupported('deepEqual'); }
export function notDeepEqual(actual, expected, message) { unsupported('notDeepEqual'); }
export function deepStrictEqual(actual, expected, message) { unsupported('deepStrictEqual'); }
export function notDeepStrictEqual(actual, expected, message) { unsupported('notDeepStrictEqual'); }
export function partialDeepStrictEqual(actual, expected, message) { unsupported('partialDeepStrictEqual'); }
export function rejects(promiseFn, ...args) { unsupported('rejects'); }
export function doesNotReject(promiseFn, ...args) { unsupported('doesNotReject'); }
function deprecated(...args) { unsupported('CallTracker'); }
export { deprecated as CallTracker };

const noException = {};
function getActual(fn) {
  if (typeof fn !== 'function') invalid('fn', 'a function');
  try { fn(); } catch (error) { return error; }
  return noException;
}
function matcherResult(actual, expected, operation) {
  if (typeof expected !== 'function') {
    if (isRegExp(expected)) return Apply(RegExpExec, expected, [StringCtor(actual)]) !== null;
    if (expected !== null && typeof expected === 'object') unsupported(`${operation}.validation-object`);
    invalid('error', 'a function or RegExp');
  }
  // Match ordinary constructors before treating a function as a predicate,
  // including custom Symbol.hasInstance semantics as in the reference runtime.
  if (expected.prototype !== undefined && actual instanceof expected) return true;
  if (Apply(IsPrototypeOf, ErrorCtor, [expected])) return false;
  return Apply(expected, {}, [actual]) === true;
}
export function throws(fn, ...args) {
  const actual = getActual(fn);
  let [expected, message] = args;
  if (typeof expected === 'string') {
    if (args.length > 1) invalid('error', 'a function or RegExp');
    if ((actual !== null && typeof actual === 'object' && actual.message === expected) || actual === expected)
      throw typedError('ERR_AMBIGUOUS_ARGUMENT', 'error/message', 'The error and message are identical');
    message = expected; expected = undefined;
  } else if (expected != null && typeof expected !== 'object' && typeof expected !== 'function') invalid('error', 'a function or RegExp');
  if (actual === noException) {
    if (expected !== null && typeof expected === 'object' && !isRegExp(expected)) unsupported('throws.validation-object');
    failure(undefined, expected, 'throws', message ? `Missing expected exception: ${StringCtor(message)}` : 'Missing expected exception.', false);
  }
  if (!expected) return;
  if (!matcherResult(actual, expected, 'throws')) failure(actual, expected, 'throws', message || 'The thrown value did not match the expected exception', !message, false);
}
export function doesNotThrow(fn, ...args) {
  const actual = getActual(fn);
  if (actual === noException) return;
  let [expected, message] = args;
  if (typeof expected === 'string') { message = expected; expected = undefined; }
  if (!expected || matcherResult(actual, expected, 'doesNotThrow')) {
    // No object inspection/message getter is required for the smaller diagnostic contract.
    failure(actual, expected, 'doesNotThrow', message ? `Got unwanted exception: ${StringCtor(message)}` : 'Got unwanted exception.', false);
  }
  throw actual;
}
export function ifError(error) {
  if (error != null) failure(error, null, 'ifError', 'ifError got unwanted exception', false);
}
function internalMatch(string, regexp, message, operation) {
  if (!isRegExp(regexp)) invalid('regexp', 'a RegExp');
  if (typeof string !== 'string' || (Apply(RegExpExec, regexp, [string]) !== null) !== (operation === 'match'))
    failure(string, regexp, operation, message || 'The input did not satisfy the regular expression assertion', !message);
}
export function match(string, regexp, message) { internalMatch(string, regexp, message, 'match'); }
export function doesNotMatch(string, regexp, message) { internalMatch(string, regexp, message, 'doesNotMatch'); }

export function strict(...args) { innerOk(args.length, args[0], args[1]); }
// SpiderMonkey can materialize these ordinary function properties lazily. Give
// them Node's observable insertion order before installing enumerable methods.
for (const [fn, name] of [[ok, 'ok'], [strict, 'strict']]) {
  Define(fn, 'length', { value: 0, writable: false, enumerable: false, configurable: true });
  Define(fn, 'name', { value: name, writable: false, enumerable: false, configurable: true });
  Define(fn, 'prototype', { value: fn.prototype, writable: true, enumerable: false, configurable: false });
}
Assign(ok, { fail, AssertionError, ok, equal, notEqual, deepEqual, notDeepEqual,
  deepStrictEqual, notDeepStrictEqual, strictEqual, notStrictEqual, partialDeepStrictEqual,
  throws, rejects, doesNotThrow, doesNotReject, ifError, match, doesNotMatch, CallTracker: deprecated, strict });
Assign(strict, ok, { equal: strictEqual, notEqual: notStrictEqual,
  deepEqual: deepStrictEqual, notDeepEqual: notDeepStrictEqual, strict });
export default ok;
