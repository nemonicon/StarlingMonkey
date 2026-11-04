const Apply = Reflect.apply;
const Construct = Reflect.construct;
const Define = Object.defineProperty;
const Descriptor = Object.getOwnPropertyDescriptor;
const OwnKeys = Reflect.ownKeys;
const Proto = Object.getPrototypeOf;
const ErrorCtor = Error;
const U8 = Uint8Array;
const MAX = 16777216;
function must(value, label) { if (!value) throw new ErrorCtor('allocUnsafe check failed: '+label); }
function code(fn) {
  try { fn(); } catch (error) { return { name: error.name, code: error.code }; }
  throw new ErrorCtor('Missing allocation failure');
}
export function allocationChecks(BufferCtor, allocate) {
  const cases = [];
  function check(name, run) { cases.push({ name, result: run() }); }
  check('function name arity and ordinary prototype', () => ({ name: allocate.name, length: allocate.length,
    callable: typeof allocate, prototypeConstructor: allocate.prototype.constructor === allocate,
    prototypeWritable: Descriptor(allocate, 'prototype').writable, then: typeof allocate.then }));
  check('invalid argument type and no implicit numeric coercion', () => {
    let calls = 0;
    const value = { valueOf() { calls++; return 3; }, toString() { calls++; return '3'; }, [Symbol.toPrimitive]() { calls++; return 3; } };
    const result = [undefined, null, false, true, '3', 3n, Symbol('x'), [], new Number(3), value]
      .map(size => code(() => allocate(size)));
    must(calls === 0, 'no size coercion'); return { result, coercionCalls: calls };
  });
  check('negative NaN and infinity', () => [NaN, Infinity, -Infinity, -1, -0.5, -Number.MIN_VALUE].map(size => code(() => allocate(size))));
  check('integer fraction and signed zero lengths', () => [-0, 0, Number.MIN_VALUE, 0.5, 0.999, 1, 1.9, 7.75, 64].map(size => {
    const bytes = allocate(size); must(BufferCtor.isBuffer(bytes) && bytes instanceof U8, 'owned Buffer brand');
    return { input: String(size), length: bytes.length, byteLength: bytes.byteLength, isBuffer: BufferCtor.isBuffer(bytes) };
  }));
  check('written bytes only differential', () => {
    const bytes = allocate(257);
    // No uninitialized Node byte is read. Initialize the whole visible span.
    for (let i = 0; i < bytes.length; i++) bytes[i] = (i * 17 + 3) & 255;
    return [...bytes];
  });
  check('call this binding and construction', () => {
    const receiver = { get size() { throw new ErrorCtor('this must not be read'); } };
    const lengths = [Apply(allocate, undefined, [3]), Apply(allocate, null, [4]), Apply(allocate, receiver, [5]),
      new allocate(6), Construct(allocate, [7], function Other() {})].map(bytes => {
      must(BufferCtor.isBuffer(bytes), 'new/call returns genuine Buffer');
      must(Proto(bytes) === BufferCtor.prototype, 'new target cannot change returned Buffer prototype');
      return bytes.length;
    });
    return lengths;
  });
  check('construction invalid inputs', () => [code(() => new allocate()), code(() => new allocate('1')), code(() => new allocate(-0.25))]);
  check('bound call extra arguments and derived construction', () => {
    const bound = allocate.bind({ ignored: true });
    class Derived extends allocate {}
    const derived = new Derived(2);
    return { boundLength: bound(3, 'ignored').length, extraLength: allocate(4, 255).length,
      boundConstruct: (new bound(5)).length, derivedBuffer: BufferCtor.isBuffer(derived),
      derivedInstance: derived instanceof Derived, returnedPrototype: Proto(derived) === BufferCtor.prototype };
  });
  check('independent visible allocations', () => {
    const a = allocate(4), b = allocate(4); a[0] = 11; b[0] = 22;
    return { distinct: a !== b, a: a[0], b: b[0], prototype: Proto(a) === BufferCtor.prototype };
  });
  check('shared subarray and backing view', () => {
    const bytes = allocate(6); for (let i = 0; i < bytes.length; i++) bytes[i] = i + 1;
    const slice = bytes.slice(1, 4), subarray = bytes.subarray(2, 5);
    slice[0] = 41; subarray[0] = 42;
    const view = new U8(bytes.buffer, bytes.byteOffset, bytes.byteLength); view[5] = 43;
    return { bytes: [...bytes], slice: [...slice], subarray: [...subarray],
      sliceBrand: BufferCtor.isBuffer(slice), subarrayBrand: BufferCtor.isBuffer(subarray),
      backing: slice.buffer === bytes.buffer && subarray.buffer === bytes.buffer,
      offsetDeltas: [slice.byteOffset - bytes.byteOffset, subarray.byteOffset - bytes.byteOffset] };
  });
  return cases;
}

export function candidateChecks(BufferCtor, candidate, makeCandidate) {
  const cases = [];
  function check(name, run) { cases.push({ name, result: run() }); }
  check('zeroed fresh no-pool allocations', () => {
    const result = [];
    for (const size of [0, 0.5, 1, 17, 1024]) {
      const a = candidate(size), b = candidate(size);
      must(a.byteOffset === 0 && a.buffer.byteLength === a.length, 'exact owned backing');
      must(a.buffer !== b.buffer, 'independent backing even for zero length');
      must([...a].every(byte => byte === 0), 'all candidate bytes zero');
      result.push({ size, length: a.length, offset: a.byteOffset, backing: a.buffer.byteLength, zero: true });
    }
    return result;
  });
  check('inclusive maximum and raw-size cap', () => {
    const max = candidate(MAX);
    must(max.length === MAX && max.buffer.byteLength === MAX && max.byteOffset === 0, 'inclusive maximum');
    must(max[0] === 0 && max[MAX >> 1] === 0 && max[MAX - 1] === 0, 'maximum zero samples');
    return { maximum: MAX, samples: [max[0], max[MAX >> 1], max[MAX - 1]],
      failures: [MAX + 0.25, MAX + 1, Number.MAX_SAFE_INTEGER].map(size => code(() => candidate(size))) };
  });
  check('captured allocator and intrinsic references', () => {
    const savedAlloc = BufferCtor.alloc, savedTrunc = Math.trunc, savedApply = Reflect.apply;
    try {
      const captured = makeCandidate(BufferCtor);
      const poisoned = () => { throw new ErrorCtor('mutable public producer must not run'); };
      BufferCtor.alloc = poisoned; Math.trunc = poisoned; Reflect.apply = poisoned;
      const bytes = captured(3.75); must(bytes.length === 3 && BufferCtor.isBuffer(bytes), 'private captured allocation');
      return { length: bytes.length, zero: bytes[0] === 0 && bytes[2] === 0 };
    } finally { BufferCtor.alloc = savedAlloc; Math.trunc = savedTrunc; Reflect.apply = savedApply; }
  });
  check('allocator failure propagates with no fallback', () => {
    const sentinel = new ErrorCtor('owned allocation failed');
    const allocate = makeCandidate({ alloc() { throw sentinel; } }); let same = false;
    try { allocate(1); } catch (error) { same = error === sentinel; }
    must(same, 'original allocation failure'); return same;
  });
  check('public pool setting does not create a slab', () => {
    const previous = BufferCtor.poolSize;
    try {
      BufferCtor.poolSize = 8192;
      const bytes = candidate(3); must(bytes.buffer.byteLength === 3 && bytes.byteOffset === 0, 'no pool');
      return { independentOfPoolSize: true, parentMatchesBacking: bytes.parent === bytes.buffer, offset: bytes.offset };
    } finally { BufferCtor.poolSize = previous; }
  });
  return cases;
}

export function preserveCoreUnsupported(BufferCtor) {
  const value = BufferCtor.alloc(1), supported = new Set(['constructor', 'toString', 'slice', 'subarray']);
  let methods = 0;
  for (const name of OwnKeys(BufferCtor.prototype)) {
    const descriptor = Descriptor(BufferCtor.prototype, name);
    if (typeof descriptor.value !== 'function' || supported.has(name)) continue;
    const result = code(() => Apply(descriptor.value, value, []));
    must(result.code === 'ERR_SM_NODE_UNSUPPORTED', 'existing prototype refusal'); methods++;
  }
  must(methods === 91, 'preserved91-method core gate');
  for (const name of ['allocUnsafe', 'allocUnsafeSlow']) {
    must(code(() => BufferCtor[name](1)).code === 'ERR_SM_NODE_UNSUPPORTED', 'original static refusal');
    must(code(() => new BufferCtor[name](1)).code === 'ERR_SM_NODE_UNSUPPORTED', 'original static new refusal');
  }
  return { methods, allocUnsafe: 'ERR_SM_NODE_UNSUPPORTED', allocUnsafeSlow: 'ERR_SM_NODE_UNSUPPORTED' };
}

export function temporarilyPatch(BufferCtor, candidate, run) {
  const previous = Descriptor(BufferCtor, 'allocUnsafe');
  try { Define(BufferCtor, 'allocUnsafe', { ...previous, value: candidate }); return run(); }
  finally { Define(BufferCtor, 'allocUnsafe', previous); }
}
