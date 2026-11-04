import { Buffer } from 'node:buffer';
const Keys = Object.keys;
const OwnNames = Object.getOwnPropertyNames;
const Proto = Object.getPrototypeOf;
const BufferIsBuffer = Buffer.isBuffer;
const ErrorCtor = Error;
const FromCharCode = String.fromCharCode;
const names = ['decode', 'default', 'encode', 'escape', 'parse', 'stringify', 'unescape', 'unescapeBuffer'];
function must(condition, label) { if (!condition) throw new ErrorCtor(`Querystring check failed: ${label}`); }
function dictionary(value) {
  must(Proto(value) === null, 'parse null prototype');
  return Keys(value).map(key => [key, value[key]]);
}
function outcome(fn) {
  try { return { value: fn() }; }
  catch (error) { return { error: { name: error.name, code: error.code } }; }
}
function hex(bytes) {
  must(BufferIsBuffer(bytes) && bytes instanceof Uint8Array, 'real Buffer output');
  let value = ''; for (const byte of bytes) value += byte.toString(16).padStart(2, '0');
  return value;
}
export function querystringChecks(q) {
  const results = [];
  function check(name, run) { results.push({ name, result: run() }); }
  check('finite exports and aliases', () => {
    must(OwnNames(q).sort().join(',') === names.join(','), 'exact8 exports');
    must(q.encode === q.stringify && q.decode === q.parse, 'named aliases');
    for (const name of names) if (name !== 'default') must(q.default[name] === q[name], `default binding ${name}`);
    must(q.default.encode === q.default.stringify && q.default.decode === q.default.parse, 'default aliases');
    must(q.then === undefined && q.default.then === undefined, 'safe initial then reads');
    return { names, defaultOwnNames: OwnNames(q.default), defaultType: typeof q.default,
      functions: names.filter(name => name !== 'default').map(name => [name, q[name].name, q[name].length]) };
  });
  const parseInputs = ['', 'a', '=', 'a=', '=a', '&&&&', '&=&=', 'a&&b', 'a=a&&b=b', 'a=1&a=2&a=',
    'a=b=c', 'a+b=c+d', 'a%20+=%20+', 'a%3Db=x%26y', 'foo=%zx', '__proto__=1&__proto__=2',
    'constructor=x&prototype=y&hasOwnProperty=z', '10=a&2=b&1=c', '?x=1', 'x=%00',
    'x=%EF%BB%BF', 'x=%C0%AF', 'x=%E2%82', 'x=%F4%90%80%80', 'x=é%', 'x=中%FF',
    'x=\uD800%FF', 'x=\uDC00%ZZ', 'x=rawé&x=raw中', 'a==b===c', 'a::b::c', 'aababxaba', 'a&b&'];
  check('default parser corpus', () => parseInputs.map(input => [input, dictionary(q.parse(input))]));
  check('nonstring parse returns null object', () => [undefined, null, 3, true, {}, ['x'], Symbol('x')].map(input => dictionary(q.parse(input))));
  check('nonstring parse ignores options and separators', () => {
    const poison = { toString() { throw new ErrorCtor('unused separator'); }, get maxKeys() { throw new ErrorCtor('unused maxKeys'); } };
    return dictionary(q.parse(3, poison, poison, poison));
  });
  check('custom separator and equal combinations', () => {
    const out = [];
    for (const sep of ['&', ';', '::', 'aba', 'aa', '💩']) for (const eq of ['=', ':', '==', 'ab', '💥'])
      for (const input of ['a=b&c=d', 'a::b::c', 'aababxaba', 'a==b===c', 'a💥b💩c💥d', 'aaaaa', 'a+b=+%20'])
        out.push([sep, eq, input, dictionary(q.parse(input, sep, eq))]);
    return out;
  });
  check('separator coercion and empty coercion', () => {
    const log = [];
    const sep = { toString() { log.push('sep'); return ';'; } };
    const eq = { toString() { log.push('eq'); return ':'; } };
    return [dictionary(q.parse('a:b;c:d', sep, eq)), log,
      dictionary(q.parse('a=b&c=d', { toString() { return ''; } }, { toString() { return ''; } }))];
  });
  check('maxKeys numeric semantics', () => {
    const out = [];
    for (const maxKeys of [undefined, 0, -1, -Infinity, Infinity, NaN, 1, 2, 1.5, '1', null])
      out.push([String(maxKeys), dictionary(q.parse('&&a=1&a=2&b=3', undefined, undefined, { maxKeys }))]);
    return out;
  });
  check('default maxKeys is1000 segments', () => {
    const input = Array.from({ length: 1002 }, (_, i) => 'k'+i+'=v').join('&');
    const parsed = q.parse(input); return [Keys(parsed).length, parsed.k999, parsed.k1000 === undefined];
  });
  check('maxKeys and decoder getter order', () => {
    const log = [];
    const options = { get maxKeys() { log.push('maxKeys'); return 2; }, get decodeURIComponent() { log.push('decoder'); return input => { log.push(input); return input; }; } };
    return [dictionary(q.parse('a=1&b=2&c=3', undefined, undefined, options)), log];
  });
  check('custom decoder strings plus and empties', () => {
    const log = [];
    const parsed = q.parse('a+b=x+y&=empty&a=&raw&%', undefined, undefined, { decodeURIComponent(input) { log.push(input); return '['+input+']'; } });
    return [dictionary(parsed), log];
  });
  check('decoder callback exceptions fall back', () => {
    const log = [];
    const parsed = q.parse('a+b=x+y&bad=%E2%82&raw=é%', undefined, undefined, { decodeURIComponent(input) { log.push(input); throw new ErrorCtor('fallback'); } });
    return [dictionary(parsed), log];
  });
  check('decoder return primitive types remain values', () => dictionary(q.parse('k=v&k=w', undefined, undefined, { decodeURIComponent(input) { return input === 'k' ? 'k' : undefined; } })));
  check('decoder return object preserves references', () => {
    const value = {}; const parsed = q.parse('k=v', undefined, undefined, { decodeURIComponent(input) { return input === 'k' ? 'k' : value; } });
    return parsed.k === value;
  });
  check('decoder callback receiver is undefined', () => {
    const receivers = []; q.parse('a=b', undefined, undefined, { decodeURIComponent: function(input) { receivers.push(this === undefined); return input; } }); return receivers;
  });
  const escapeInputs = ['plain', "!'-._~()*", ' /+=&?#%', 'é中💩', '\uFEFF', '\u0000', '\uD800', '\uDC00',
    '\uD800a', '\uDC00a', '\uD800\uD800', '\uDFFF\uFFFF', 'x\uD800a\uDC00b', 'x\uD800a\uD800',
    null, undefined, true, false, 42, -0, NaN, Infinity, 12n, Symbol('x')];
  check('escape coercion surrogates and error code', () => escapeInputs.map(input => outcome(() => q.escape(input))));
  check('escape full ASCII alphabet', () => q.escape(Array.from({ length: 128 }, (_, i) => FromCharCode(i)).join('')));
  check('escape object conversion order', () => {
    const log = []; const value = { toString() { log.push('toString'); return 'é'; }, valueOf() { log.push('valueOf'); return 5; } };
    return [q.escape(value), log];
  });
  const byteInputs = ['plain', 'a+b', 'a+b%', '%', '%%2a', '%2sf%2a', '%2%2af%2a', '%GG', '%a', '%aG', '%u4E2D', '%uD800',
    '%00%7F%80%FF', '%C0%AF', '%E2%82', '%ED%A0%80', '%F4%90%80%80', '%EF%BB%BF%', 'é%', '中%FF', '\uD800%FF'];
  check('unescape fast path versus fallback spaces', () => byteInputs.map(input => [input, q.unescape(input), q.unescape(input, true)]));
  check('unescapeBuffer bytes', () => byteInputs.map(input => [input, hex(q.unescapeBuffer(input)), hex(q.unescapeBuffer(input, true))]));
  check('unescapeBuffer fresh owner and view', () => {
    const one = q.unescapeBuffer('%41%42'); const two = q.unescapeBuffer('%41%42');
    const view = new Uint8Array(one.buffer, one.byteOffset, one.length); view[0] = 90;
    return [one.length, one[0], two[0], one !== two, BufferIsBuffer(one)];
  });
  check('all byte values UTF8 and percent fallback', () => {
    const out = [];
    for (let byte = 0; byte < 256; byte++) {
      const escaped = '%'+byte.toString(16).padStart(2, '0');
      for (const prefix of ['', '%EF%BB%BF', '%C2', '%E0%A0', '%F0%90%80', 'é']) {
        const input = prefix + escaped + '%'; out.push([input, q.unescape(input), hex(q.unescapeBuffer(input))]);
      }
    }
    return out;
  });
  check('unescape scalar coercion', () => [undefined, null, true, 4, 12n].map(value => q.unescape(value)));
  check('stringify ordinary fields and arrays', () => {
    const object = { text: 'é中💩', n: 5, bigint: 12n, yes: true, no: false, nan: NaN, inf: Infinity,
      nil: null, undef: undefined, fn() {}, symbol: Symbol('x'), object: {}, arr: ['a', '', 4, null], empty: [] };
    return [q.stringify(object), q.stringify(object, ';', ':'), q.stringify([1, 2])];
  });
  check('stringify nonobjects', () => [undefined, null, 4, true, 'string', Symbol('x'), () => {}].map(value => q.stringify(value)));
  check('stringify inherited symbol and hole behavior', () => {
    const object = Object.create({ inherited: 'skip' }); object.a = [, undefined, 'x']; object[Symbol('skip')] = 'skip'; return q.stringify(object);
  });
  check('stringify custom encoder invocation behavior', () => {
    const log = []; const output = q.stringify({ a: '', n: 3, b: false, z: null, e: [], arr: ['x', 4], big: 1e21 }, '&', '=', { encodeURIComponent(value) { log.push(value); return '['+value+']'; } });
    return [output, log];
  });
  check('stringify default encoder primitive optimization', () => {
    const original = q.default.escape, log = [];
    try { q.default.escape = function(value) { log.push(value); return original(value); }; return [q.stringify({ empty: '', n: 3, b: true, big: 1e21 }), log]; }
    finally { q.default.escape = original; }
  });
  check('stringify encoder getter and receiver', () => {
    const log = []; const options = { get encodeURIComponent() { log.push('get'); return function(value) { log.push(this === undefined); return value; }; } };
    return [q.stringify({ a: 'b' }, undefined, undefined, options), log];
  });
  check('stringify getters and separator coercion order', () => {
    const log = []; const sep = { toString() { log.push('sep'); return ';'; } }, eq = { toString() { log.push('eq'); return ':'; } };
    const input = { get a() { log.push('a'); return []; }, get b() { log.push('b'); return 1; }, get c() { log.push('c'); return [2, 3]; } };
    return [q.stringify(input, sep, eq), log];
  });
  check('default method mutation retains named bindings', () => {
    const original = q.default.escape;
    try { q.default.escape = value => 'x'; return [q.escape === original, q.stringify({ a: 'b' })]; } finally { q.default.escape = original; }
  });
  check('parse mutable default decoder and fallback receiver', () => {
    const original = q.default.unescape, log = [];
    try { q.default.unescape = input => { log.push(input); return input; }; return [dictionary(q.parse('a+b=c+d&raw=x')), log]; } finally { q.default.unescape = original; }
  });
  check('unescape mutable fallback method receiver', () => {
    const original = q.default.unescapeBuffer;
    try { q.default.unescapeBuffer = function(input, spaces) { must(this === q.default, 'fallback method receiver'); return { toString() { return String(input)+':'+spaces; } }; }; return q.unescape('x%', true); }
    finally { q.default.unescapeBuffer = original; }
  });
  return results;
}

export function prototypeOnlyChecks(q) {
  const results = [];
  function fails(name, run, expected) {
    let failure; try { run(); } catch (error) { failure = error; }
    must(failure?.code === expected, name); results.push({ name, code: failure.code, operation: failure.operation });
  }
  for (const construct of [false, true]) fails('unescapeBuffer nonstring '+construct,
    () => construct ? new q.unescapeBuffer({ length: 1 }) : q.unescapeBuffer({ length: 1 }), 'ERR_SM_NODE_UNSUPPORTED');
  for (const method of ['parse', 'escape', 'unescape', 'unescapeBuffer']) fails(method+' input cap', () => q[method]('x'.repeat(1048577)), 'ERR_SM_NODE_LIMIT');
  fails('parse separator cap', () => q.parse('a=b', '&'.repeat(1048577)), 'ERR_SM_NODE_LIMIT');
  fails('parse pair cap cannot be disabled', () => q.parse('&'.repeat(65537), undefined, undefined, { maxKeys: 0 }), 'ERR_SM_NODE_LIMIT');
  fails('stringify array field cap', () => q.stringify({ x: Array(65537) }), 'ERR_SM_NODE_LIMIT');
  fails('stringify output cap', () => q.stringify({ x: ['x', 'x'] }, '&', '=', { encodeURIComponent: () => 'x'.repeat(8388608) }), 'ERR_SM_NODE_LIMIT');
  const encode = globalThis.encodeURIComponent, decode = globalThis.decodeURIComponent, alloc = Buffer.alloc;
  const charCode = String.prototype.charCodeAt, slice = String.prototype.slice;
  const isArray = Array.isArray, keys = Object.keys;
  try {
    const poison = () => { throw new ErrorCtor('mutated primordial'); };
    globalThis.encodeURIComponent = globalThis.decodeURIComponent = Buffer.alloc = String.prototype.charCodeAt = String.prototype.slice = Array.isArray = Object.keys = poison;
    must(q.escape('é') === '%C3%A9', 'captured encode');
    must(q.unescape('%C3%A9') === 'é', 'captured decode');
    must(q.unescape('é%') === '\uFFFD%', 'captured byte fallback');
    must(q.parse('a=x').a === 'x' && q.stringify({ a: ['x'] }) === 'a=x', 'captured state machine');
  } finally {
    globalThis.encodeURIComponent = encode; globalThis.decodeURIComponent = decode; Buffer.alloc = alloc;
    String.prototype.charCodeAt = charCode; String.prototype.slice = slice; Array.isArray = isArray; Object.keys = keys;
  }
  results.push({ name: 'captured intrinsic and byte allocator mutation', passed: true });
  return results;
}
