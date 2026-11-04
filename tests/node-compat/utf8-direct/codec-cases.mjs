// Dependency-free, bounded UTF-8 semantics shared by the exact Node oracle and
// private guest codec experiments. This is deliberately not a complete Web API
// or Buffer conformance suite. Optional gc() runs only at JavaScript boundaries.
export function runCodecCases({ TextEncoder, Buffer, gc }) {
  const U8 = Uint8Array, AB = ArrayBuffer;
  const encoder = new TextEncoder();
  const encode = encoder.encode.bind(encoder);
  const encodeInto = encoder.encodeInto.bind(encoder);
  const cases = [];
  let assertionCount = 0, gcBoundaryCalls = 0;
  function assert(condition, message) {
    assertionCount++;
    if (!condition) {
      const error = new Error(message || 'UTF-8 codec assertion failed');
      error.code = 'ERR_UTF8_CODEC_ASSERTION';
      throw error;
    }
  }
  function equal(actual, expected, message) {
    assert(Object.is(actual, expected), message || 'Expected identical values');
  }
  function bytes(actual, expected, message) {
    equal(actual.length, expected.length, `${message}: length`);
    for (let i = 0; i < expected.length; ++i) equal(actual[i], expected[i], `${message}: byte ${i}`);
  }
  function ascii(value) {
    const result = [];
    for (let i = 0; i < value.length; ++i) {
      assert(value.charCodeAt(i) < 128, 'ASCII oracle input');
      result.push(value.charCodeAt(i));
    }
    return result;
  }
  function collect(action) {
    try { action(); }
    catch (error) { return error; }
    throw new Error('Expected codec operation to throw');
  }
  function boundary() {
    if (gc) { gcBoundaryCalls++; gc(); }
  }
  function test(name, action) {
    const before = assertionCount;
    const observations = action() || [];
    cases.push({ name, passed: true, assertionCount: assertionCount - before, observations });
  }
  function checkOutput(output, expected, label) {
    equal(Object.getPrototypeOf(output), U8.prototype, `${label}: Uint8Array prototype`);
    assert(output instanceof U8, `${label}: Uint8Array instance`);
    equal(output.BYTES_PER_ELEMENT, 1, `${label}: element width`);
    bytes(output, expected, label);
    equal(output.byteLength, expected.length, `${label}: byte length`);
    equal(output.byteOffset, 0, `${label}: zero offset`);
    const backing = output.buffer;
    assert(backing instanceof AB, `${label}: ordinary ArrayBuffer`);
    equal(backing.byteLength, expected.length, `${label}: exact ArrayBuffer size`);
    if ('resizable' in AB.prototype) equal(backing.resizable, false, `${label}: fixed backing`);
    equal(new U8(backing, output.byteOffset, output.byteLength).length, expected.length, `${label}: valid view`);
  }

  test('default and primitive input conversion', () => {
    const inputs = [
      ['omitted', [], ''], ['undefined', [undefined], ''], ['null', [null], 'null'],
      ['false', [false], 'false'], ['true', [true], 'true'], ['zero', [0], '0'],
      ['negative zero', [-0], '0'], ['negative integer', [-123], '-123'],
      ['fraction', [1.25], '1.25'], ['NaN', [NaN], 'NaN'],
      ['positive infinity', [Infinity], 'Infinity'], ['negative infinity', [-Infinity], '-Infinity'],
      ['BigInt', [123456789012345678901234567890n], '123456789012345678901234567890'],
    ];
    const observations = [];
    for (const [label, args, expected] of inputs) {
      const result = encode(...args);
      checkOutput(result, ascii(expected), label);
      observations.push({ label, byteLength: result.length });
    }
    const error = collect(() => encode(Symbol('must not stringify')));
    assert(error instanceof TypeError, 'Symbol input throws TypeError');
    observations.push({ label: 'Symbol', errorName: error.name });
    return observations;
  });

  test('ToString hook order, hint and original exceptions', () => {
    const events = [];
    const primitive = {
      get [Symbol.toPrimitive]() {
        events.push('get @@toPrimitive');
        return function(hint) {
          equal(this, primitive, 'primitive hook receiver');
          events.push(`call @@toPrimitive:${hint}`);
          boundary();
          return 'hook';
        };
      },
      get toString() { throw new Error('unexpected toString read'); },
      get valueOf() { throw new Error('unexpected valueOf read'); },
    };
    bytes(encode(primitive), ascii('hook'), 'primitive hook result');
    equal(events.join('|'), 'get @@toPrimitive|call @@toPrimitive:string', 'primitive hook order');
    const fallbackEvents = [];
    const fallback = {
      get [Symbol.toPrimitive]() { fallbackEvents.push('get @@toPrimitive'); return undefined; },
      get toString() {
        fallbackEvents.push('get toString');
        return function() { equal(this, fallback, 'toString receiver'); fallbackEvents.push('call toString'); return {}; };
      },
      get valueOf() {
        fallbackEvents.push('get valueOf');
        return function() { equal(this, fallback, 'valueOf receiver'); fallbackEvents.push('call valueOf'); return 37; };
      },
    };
    bytes(encode(fallback), ascii('37'), 'fallback conversion result');
    equal(fallbackEvents.join('|'), 'get @@toPrimitive|get toString|call toString|get valueOf|call valueOf', 'fallback conversion order');
    const marker = { sentinel: 'original exception identity' };
    for (const stage of ['get primitive', 'call primitive', 'get toString', 'call toString', 'get valueOf', 'call valueOf']) {
      const value = stage === 'get primitive' ? { get [Symbol.toPrimitive]() { throw marker; } }
        : stage === 'call primitive' ? { [Symbol.toPrimitive]() { throw marker; } }
        : stage === 'get toString' ? { get toString() { throw marker; } }
        : stage === 'call toString' ? { toString() { throw marker; } }
        : stage === 'get valueOf' ? { toString() { return {}; }, get valueOf() { throw marker; } }
        : { toString() { return {}; }, valueOf() { throw marker; } };
      equal(collect(() => encode(value)), marker, `${stage}: preserve thrown value`);
    }
    assert(collect(() => encode({ [Symbol.toPrimitive]() { return {}; } })) instanceof TypeError,
      'nonprimitive conversion result rejected');
    assert(collect(() => encode({ [Symbol.toPrimitive]() { return Symbol(); } })) instanceof TypeError,
      'Symbol returned from conversion rejected');
    return [{ primitiveHookOrder: events, fallbackHookOrder: fallbackEvents, sentinelStages: 6 }];
  });

  const replacement = [239, 191, 189];
  const vectors = [
    ['empty', '', []], ['ASCII', 'Az09 ~', [65, 122, 48, 57, 32, 126]],
    ['embedded NUL', '\0A\0', [0, 65, 0]], ['leading BOM', '\ufeffX', [239, 187, 191, 88]],
    ['Latin1 boundaries', '\u007f\u0080\u00ff', [127, 194, 128, 195, 191]],
    ['BMP width boundaries', '\u07ff\u0800', [223, 191, 224, 160, 128]],
    ['BMP around surrogate range', '\ud7ff\ue000\uffff', [237, 159, 191, 238, 128, 128, 239, 191, 191]],
    ['supplementary pairs', '\ud83d\ude00\ud834\udd1e', [240, 159, 152, 128, 240, 157, 132, 158]],
    ['largest scalar', '\udbff\udfff', [244, 143, 191, 191]],
    ['lone high surrogate', '\ud800', replacement], ['lone low surrogate', '\udfff', replacement],
    ['separated surrogates', '\ud800A\udc00', [...replacement, 65, ...replacement]],
    ['high-high-low-low', '\ud800\ud800\udc00\udc00', [...replacement, 240, 144, 128, 128, ...replacement]],
    ['low-high pair', '\udc00\ud83d\ude00', [...replacement, 240, 159, 152, 128]],
  ];
  test('hand-written UTF-16 scalar and replacement byte vectors', () => {
    const observations = [];
    for (const [label, source, expected] of vectors) {
      boundary();
      checkOutput(encode(source), expected, label);
      observations.push({ label, codeUnits: source.length, expectedBytes: expected });
    }
    return observations;
  });

  const allocationSizes = [0, 1, 7, 8, 15, 16, 31, 32, 47, 48, 63, 64, 65,
    95, 96, 97, 127, 128, 129, 255, 256, 257, 1023, 1024, 1025, 4095, 4096, 4097];
  test('fresh exact-length outputs around small allocation boundaries', () => {
    const observations = [];
    for (const length of allocationSizes) {
      const source = 'a'.repeat(length), expected = ascii(source);
      const first = encode(source);
      boundary();
      const second = encode(source);
      checkOutput(first, expected, `${length}: first`);
      checkOutput(second, expected, `${length}: second`);
      assert(first !== second, `${length}: distinct result objects`);
      assert(first.buffer !== second.buffer, `${length}: distinct backing objects`);
      if (length) {
        const firstView = new U8(first.buffer, first.byteOffset, first.length);
        first[0] = 17;
        equal(firstView[0], 17, `${length}: shared backing view observes mutation`);
        equal(second[0], 97, `${length}: second result remains independent`);
        firstView[length - 1] = 23;
        equal(first[length - 1], 23, `${length}: result observes backing view mutation`);
      }
      boundary();
      bytes(second, expected, `${length}: survives safe-boundary GC`);
      equal(source, 'a'.repeat(length), `${length}: source value remains unchanged`);
      observations.push({ byteLength: length, freshObject: true, independentBacking: true });
    }
    return observations;
  });

  test('concatenation, sliced strings and surrogate pairs across concatenations', () => {
    const pieces = ['a', '\u00e9', '\u20ac', '\ud83d', '\ude00', '\0'];
    const expectedUnit = [97, 195, 169, 226, 130, 172, 240, 159, 152, 128, 0];
    let source = '';
    const expected = [];
    for (let i = 0; i < 257; ++i) {
      for (const piece of pieces) source += piece;
      expected.push(...expectedUnit);
    }
    boundary();
    checkOutput(encode(source), expected, 'concatenated string');
    const sliced = ('prefix' + source + 'suffix').slice(6, -6);
    boundary();
    checkOutput(encode(sliced), expected, 'sliced string');
    equal(source, sliced, 'logical source content preserved');
    return [{ repetitions: 257, codeUnits: source.length, byteLength: expected.length,
      representationScope: 'Logical concatenation/slice inputs; no assertion of engine-private rope layout.' }];
  });

  test('encodeInto complete scalar boundaries, offsets and untouched sentinels', () => {
    const sources = [
      ['', []], ['ABC', [[1, [65]], [1, [66]], [1, [67]]]],
      ['A\u00e9\ud83d\ude00Z', [[1, [65]], [1, [195, 169]], [2, [240, 159, 152, 128]], [1, [90]]]],
      ['\ud800X\udc00', [[1, replacement], [1, [88]], [1, replacement]]],
      ['\ufeff\u20ac', [[1, [239, 187, 191]], [1, [226, 130, 172]]]],
    ];
    const observations = [];
    for (const [source, chunks] of sources) {
      const maximum = chunks.reduce((sum, chunk) => sum + chunk[1].length, 0);
      const matrix = [];
      for (const offset of [0, 1, 3]) for (let capacity = 0; capacity <= maximum + 2; ++capacity) {
        const storage = new U8(offset + capacity + 3);
        storage.fill(165);
        const destination = new U8(storage.buffer, offset, capacity);
        let read = 0;
        const expected = [];
        for (const [units, encoded] of chunks) {
          if (expected.length + encoded.length > capacity) break;
          read += units; expected.push(...encoded);
        }
        boundary();
        const result = encodeInto(source, destination);
        equal(result.read, read, 'encodeInto code units read');
        equal(result.written, expected.length, 'encodeInto bytes written');
        equal(Object.keys(result).sort().join('|'), 'read|written', 'encodeInto result fields');
        for (let i = 0; i < storage.length; ++i) {
          equal(storage[i], i >= offset && i < offset + expected.length ? expected[i - offset] : 165,
            'encodeInto writes only complete scalars in supplied destination');
        }
        equal(destination.byteOffset, offset, 'encodeInto preserves destination offset');
        equal(destination.byteLength, capacity, 'encodeInto preserves destination length');
        matrix.push([offset, capacity, read, expected.length]);
      }
      observations.push({ sourceCodeUnits: source.length, columns: ['offset', 'capacity', 'read', 'written'], matrix });
    }
    return observations;
  });

  test('captured encoder methods survive public prototype replacement', () => {
    const encodeDescriptor = Object.getOwnPropertyDescriptor(TextEncoder.prototype, 'encode');
    const intoDescriptor = Object.getOwnPropertyDescriptor(TextEncoder.prototype, 'encodeInto');
    const globalU8Descriptor = Object.getOwnPropertyDescriptor(globalThis, 'Uint8Array');
    const setDescriptor = Object.getOwnPropertyDescriptor(U8.prototype, 'set');
    const fillDescriptor = Object.getOwnPropertyDescriptor(U8.prototype, 'fill');
    const marker = { sentinel: 'poisoned public method' };
    let replacedCalls = 0;
    try {
      TextEncoder.prototype.encode = function() { replacedCalls++; throw marker; };
      TextEncoder.prototype.encodeInto = function() { replacedCalls++; throw marker; };
      globalThis.Uint8Array = function() { replacedCalls++; throw marker; };
      U8.prototype.set = function() { replacedCalls++; throw marker; };
      U8.prototype.fill = function() { replacedCalls++; throw marker; };
      bytes(encode('\u00e9\ud83d\ude00'), [195, 169, 240, 159, 152, 128], 'captured encode');
      const destination = new U8(3);
      const result = encodeInto('A\u00e9', destination);
      equal(result.read, 2, 'captured encodeInto read');
      equal(result.written, 3, 'captured encodeInto written');
      bytes(destination, [65, 195, 169], 'captured encodeInto bytes');
      if (Buffer) {
        bytes(Buffer.from('A\u00e9', 'utf8'), [65, 195, 169], 'Buffer codec capture');
        equal(Buffer.byteLength('A\u00e9', 'utf8'), 3, 'Buffer byteLength codec capture');
      }
      equal(replacedCalls, 0, 'captured methods bypass public replacements');
    } finally {
      Object.defineProperty(TextEncoder.prototype, 'encode', encodeDescriptor);
      Object.defineProperty(TextEncoder.prototype, 'encodeInto', intoDescriptor);
      Object.defineProperty(globalThis, 'Uint8Array', globalU8Descriptor);
      if (setDescriptor) Object.defineProperty(U8.prototype, 'set', setDescriptor);
      else delete U8.prototype.set;
      if (fillDescriptor) Object.defineProperty(U8.prototype, 'fill', fillDescriptor);
      else delete U8.prototype.fill;
    }
    return [{ replacedCalls, bufferCaptureChecked: Boolean(Buffer) }];
  });

  if (Buffer) test('bounded Buffer UTF-8 bytes, lengths and backing relationships', () => {
    const observations = [];
    for (const [label, source, expected] of vectors) {
      const output = Buffer.from(source, 'utf8');
      const independent = Buffer.from(source, 'utf-8');
      assert(Buffer.isBuffer(output), `${label}: Buffer brand`);
      assert(output instanceof U8, `${label}: Buffer is Uint8Array`);
      bytes(output, expected, `${label}: Buffer bytes`);
      bytes(independent, expected, `${label}: UTF-8 alias`);
      equal(Buffer.byteLength(source, 'utf8'), expected.length, `${label}: Buffer byteLength`);
      assert(output !== independent, `${label}: fresh Buffer object`);
      assert(output.buffer instanceof AB, `${label}: ordinary Buffer backing`);
      assert(output.byteOffset + output.byteLength <= output.buffer.byteLength, `${label}: valid Buffer view range`);
      const backingView = new U8(output.buffer, output.byteOffset, output.byteLength);
      bytes(backingView, expected, `${label}: backing view bytes`);
      if (expected.length) {
        output[0] ^= 255;
        equal(backingView[0], expected[0] ^ 255, `${label}: Buffer/backing shared view`);
        equal(independent[0], expected[0], `${label}: independent Buffer visible bytes`);
      }
      boundary();
      bytes(independent, expected, `${label}: Buffer survives safe-boundary GC`);
      observations.push({ label, byteLength: expected.length, visibleBytesIndependent: true,
        backingScope: 'Offsets/pooling intentionally unrestricted; backing view must cover the visible bytes.' });
    }
    return observations;
  });

  return { schemaVersion: 1, cases, caseCount: cases.length, assertionCount,
    observationCount: cases.reduce((sum, item) => sum + item.observations.length, 0),
    bufferChecked: Boolean(Buffer), gcBoundaryCalls,
    scope: 'Bounded UTF-8 TextEncoder and optional Buffer tests; not complete Web API or Buffer conformance.',
    allocationSizes, unicodeVectorCount: vectors.length };
}
