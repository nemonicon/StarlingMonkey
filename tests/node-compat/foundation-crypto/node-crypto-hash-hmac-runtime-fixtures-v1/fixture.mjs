// UNCOMPILED / UNEXECUTED. No crypto operation or native state at module INIT.
import * as nodeCrypto from 'node:crypto';
import * as bareCrypto from 'crypto';
import { Buffer } from 'node:buffer';
let calls = 0;
const HASH_VECTORS = [{"id": "hash-empty", "message": "", "expectedHex": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}, {"id": "hash-ascii-abc", "message": "abc", "expectedHex": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}, {"id": "hash-unicode-eacute", "message": "\u00e9", "expectedHex": "4a99557e4033c3539de2eb65472017cad5f9557f7a0625a09f1c3f6e2ba69c4c"}];
const HMAC_VECTORS = [{"id": "hmac-rfc4231-1", "keyHex": "0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b", "message": "Hi There", "expectedHex": "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"}, {"id": "hmac-rfc4231-2", "keyUtf8": "Jefe", "message": "what do ya want for nothing?", "expectedHex": "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"}, {"id": "hmac-rfc4231-6-long-key", "keyHex": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "message": "Test Using Larger Than Block-Size Key - Hash Key First", "expectedHex": "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"}, {"id": "hmac-rfc4231-7-long-key-data", "keyHex": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "message": "This is a test using a larger than block-size key and a larger than block-size data. The key needs to be hashed before being used by the HMAC algorithm.", "expectedHex": "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2"}];
const EXPECTED_NAMESPACE_NAMES = ["Certificate", "Cipher", "Cipheriv", "Decipher", "Decipheriv", "DiffieHellman", "DiffieHellmanGroup", "ECDH", "Hash", "Hmac", "KeyObject", "Sign", "Verify", "X509Certificate", "checkPrime", "checkPrimeSync", "constants", "createCipheriv", "createDecipheriv", "createDiffieHellman", "createDiffieHellmanGroup", "createECDH", "createHash", "createHmac", "createPrivateKey", "createPublicKey", "createSecretKey", "createSign", "createVerify", "default", "diffieHellman", "generateKey", "generateKeyPair", "generateKeyPairSync", "generateKeySync", "generatePrime", "generatePrimeSync", "getCipherInfo", "getCiphers", "getCurves", "getDiffieHellman", "getFips", "getHashes", "getRandomValues", "hash", "hkdf", "hkdfSync", "pbkdf2", "pbkdf2Sync", "privateDecrypt", "privateEncrypt", "publicDecrypt", "publicEncrypt", "randomBytes", "randomFill", "randomFillSync", "randomInt", "randomUUID", "scrypt", "scryptSync", "secureHeapUsed", "setEngine", "setFips", "sign", "subtle", "timingSafeEqual", "verify", "webcrypto"];

function errorRecord(e) {
  if (e === null || (typeof e !== 'object' && typeof e !== 'function'))
    return { type: e === null ? 'null' : typeof e, value: e === undefined ? null : e, originalIdentityClaim: false };
  return { type: 'object', name: typeof e.name === 'string' ? e.name : null,
    code: typeof e.code === 'string' ? e.code : null,
    message: typeof e.message === 'string' ? e.message : null, originalIdentityClaim: false };
}
function hex(v) {
  let out = '';
  for (let i = 0; i < v.byteLength; i++) out += v[i].toString(16).padStart(2, '0');
  return out;
}
function fromHex(v) {
  const out = new Uint8Array(v.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(v.slice(i * 2, i * 2 + 2), 16);
  return out;
}
function returned(v) {
  if (typeof v === 'string') return { type: 'string', value: v };
  if (v instanceof Uint8Array) return { type: Buffer.isBuffer(v) ? 'Buffer' : 'Uint8Array', bytes: v.byteLength, hex: hex(v) };
  if (v === undefined || v === null || typeof v === 'boolean' || typeof v === 'number')
    return { type: v === null ? 'null' : typeof v, value: v === undefined ? null : v };
  return { type: typeof v, opaque: true, fullOpaqueValueClaim: false };
}
function attempt(fn) {
  try { return { kind: 'return', observed: returned(fn()) }; }
  catch (error) { return { kind: 'throw', error: errorRecord(error) }; }
}
// Every returned context is driven to digest within the ordinary call, including
// cleanup after non-consuming refusals. This is not finalizer/erasure proof.
function withContext(factory, operation) {
  let context, consumed = false, outcome, cleanup = { attempted: false };
  const markConsumed = () => { consumed = true; };
  try {
    context = factory();
    outcome = { kind: 'return', observed: returned(operation(context, markConsumed)) };
  } catch (error) { outcome = { kind: 'throw', error: errorRecord(error) }; }
  finally {
    if (context && !consumed) cleanup = { attempted: true, ...attempt(() => context.digest('hex')) };
  }
  return { outcome, cleanup };
}
function hashHex(parts, algorithm = 'sha256') {
  return withContext(() => nodeCrypto.createHash(algorithm), (c, consumed) => {
    for (const part of parts) c.update(part);
    const out = c.digest('hex'); consumed(); return out;
  });
}
function hmacHex(key, parts) {
  return withContext(() => nodeCrypto.createHmac('sha256', key), (c, consumed) => {
    for (const part of parts) c.update(part);
    const out = c.digest('hex'); consumed(); return out;
  });
}
function dataValue(v) {
  if (v === null || ['undefined', 'boolean', 'number', 'string'].includes(typeof v))
    return { type: v === null ? 'null' : typeof v, value: v === undefined ? null : v };
  return { type: typeof v, functionName: typeof v === 'function' ? v.name : null, opaque: true, fullOpaqueValueClaim: false };
}
function descriptors(v) {
  const all = Object.getOwnPropertyDescriptors(v);
  return Reflect.ownKeys(all).map(key => {
    const d = all[key];
    return { key: typeof key === 'symbol' ? { type: 'symbol', description: key.description ?? null } : { type: 'string', value: key },
      kind: Object.hasOwn(d, 'value') ? 'data' : 'accessor', enumerable: d.enumerable, configurable: d.configurable,
      writable: Object.hasOwn(d, 'writable') ? d.writable : null,
      value: Object.hasOwn(d, 'value') ? dataValue(d.value) : null,
      getter: typeof d.get, setter: typeof d.set };
  });
}
export function run() {
  calls++;
  const nodeComparable = [], profilePolicy = [];
  function row(id, fn) {
    try { nodeComparable.push({ id, value: fn() }); }
    catch (error) { nodeComparable.push({ id, unexpectedFixtureThrow: errorRecord(error) }); }
  }
  for (const v of HASH_VECTORS)
    row(v.id, () => ({ messageUtf8Hex: hex(Buffer.from(v.message, 'utf8')), expectedHex: v.expectedHex, actual: hashHex([v.message]) }));
  row('hash-unicode-surrogate', () => ({ messageUtf8Hex: hex(Buffer.from('\u00e9\ud834\udd1e\ud800', 'utf8')),
    expectedUtf8Hex: 'c3a9f09d849eefbfbd', actual: hashHex(['\u00e9\ud834\udd1e\ud800']), expectedDigest: null }));
  row('hash-partition-abc', () => ({ expectedHex: HASH_VECTORS[1].expectedHex, actual: hashHex(['a', '', 'b', 'c'], 'SHA256') }));
  for (const n of [55, 56, 63, 64, 65]) row('hash-block-' + n, () => {
    const bytes = new Uint8Array(n);
    for (let i = 0; i < bytes.length; i++) bytes[i] = (i * 17 + 3) & 255;
    return { messageHex: hex(bytes), whole: hashHex([bytes]), partitioned: hashHex([bytes.subarray(0, 1), bytes.subarray(1, 17), bytes.subarray(17)]) };
  });
  row('hash-nonzero-window-copy', () => {
    const backing = Uint8Array.of(0xd1, 97, 98, 99, 0xe2), view = backing.subarray(1, 4);
    let sameReceiver = false;
    const actual = withContext(() => nodeCrypto.createHash('sha256'), (c, consumed) => {
      sameReceiver = c.update(view) === c; view.fill(120);
      const out = c.digest('hex'); consumed(); return out;
    });
    const bufferBacking = Buffer.from([0xd1, 97, 98, 99, 0xe2]), bufferView = bufferBacking.subarray(1, 4);
    let bufferSameReceiver = false;
    const bufferWindow = withContext(() => nodeCrypto.createHash('sha256'), (c, consumed) => {
      bufferSameReceiver = c.update(bufferView) === c; bufferView.fill(120);
      const out = c.digest('hex'); consumed(); return out;
    });
    return { expectedMessageHex: '616263', expectedHex: HASH_VECTORS[1].expectedHex, sameReceiver, actual,
      afterCallerMutationHex: hex(backing), sentinelsPreserved: backing[0] === 0xd1 && backing[4] === 0xe2,
      bufferWindow, bufferInputIsBuffer: Buffer.isBuffer(bufferView), bufferSameReceiver,
      bufferAfterCallerMutationHex: hex(bufferBacking), bufferSentinelsPreserved: bufferBacking[0] === 0xd1 && bufferBacking[4] === 0xe2 };
  });
  row('hash-output-ownership', () => {
    let first, second;
    const a = withContext(() => nodeCrypto.createHash('sha256'), (c, done) => { first = c.update('abc').digest(); done(); return first; });
    const before = first instanceof Uint8Array ? hex(first) : null;
    const b = withContext(() => nodeCrypto.createHash('sha256'), (c, done) => { second = c.digest(); done(); return second; });
    const priorStableAfterSecond = first instanceof Uint8Array && hex(first) === before;
    const otherBefore = second instanceof Uint8Array ? hex(second) : null;
    if (first instanceof Uint8Array) first[0] ^= 255;
    return { first: a, second: b, priorStableAfterSecond, secondStableAfterFirstMutation: second instanceof Uint8Array && hex(second) === otherBefore,
      expectedFirstHex: HASH_VECTORS[1].expectedHex, expectedSecondHex: HASH_VECTORS[0].expectedHex };
  });
  for (const v of HMAC_VECTORS) row(v.id, () => ({ expectedHex: v.expectedHex,
    keyHex: v.keyHex ?? null, keyUtf8: v.keyUtf8 ?? null,
    actual: hmacHex(v.keyHex ? fromHex(v.keyHex) : v.keyUtf8, [v.message]) }));
  row('hmac-empty', () => ({ actual: hmacHex(new Uint8Array(0), ['']), expectedDigest: null }));
  row('hmac-key-window-snapshot', () => {
    const backing = new Uint8Array(22); backing.fill(0x0b); backing[0] = 0xd1; backing[21] = 0xe2;
    const view = backing.subarray(1, 21); let callerUnchangedAfterCreate = false;
    const actual = withContext(() => {
      const c = nodeCrypto.createHmac('sha256', view); callerUnchangedAfterCreate = hex(view) === '0b'.repeat(20); return c;
    }, (c, done) => { view.fill(0); c.update('Hi There'); const out = c.digest('hex'); done(); return out; });
    return { actual, expectedHex: HMAC_VECTORS[0].expectedHex, callerUnchangedAfterCreate,
      sentinelsPreserved: backing[0] === 0xd1 && backing[21] === 0xe2, callerAfterMutationHex: hex(view) };
  });
  row('terminal-hash', () => {
    let terminal;
    const actual = withContext(() => nodeCrypto.createHash('sha256'), (c, done) => {
      const first = c.update('abc').digest('hex'); done();
      terminal = { first, repeated: attempt(() => c.digest('hex')), updateAfter: attempt(() => c.update('x')) }; return first;
    });
    return { actual, terminal: terminal ?? null, expectedFinalizedErrorCode: 'ERR_CRYPTO_HASH_FINALIZED' };
  });
  row('terminal-hmac', () => {
    let terminal;
    const actual = withContext(() => nodeCrypto.createHmac('sha256', 'Jefe'), (c, done) => {
      const first = c.update('what do ya want for nothing?').digest('hex'); done();
      terminal = { first, repeatedHex: attempt(() => c.digest('hex')), repeatedBuffer: attempt(() => c.digest()), updateAfter: attempt(() => c.update('x')) }; return first;
    });
    return { actual, terminal: terminal ?? null, expectedFirstHex: HMAC_VECTORS[1].expectedHex,
      expectedRepeatedHex: '', expectedRepeatedBufferBytes: 0, expectedFinalizedErrorCode: 'ERR_CRYPTO_HASH_FINALIZED' };
  });
  function policy(id, expectedProfileErrorCode, factory, operation) {
    profilePolicy.push({ id, expectedProfileErrorCode, actual: withContext(factory, operation), nodeParityRequired: false });
  }
  const finish = (c, done) => { const out = c.digest('hex'); done(); return out; };
  policy('unsupported-hash-constructor', 'ERR_SM_NODE_UNSUPPORTED', () => new nodeCrypto.Hash('sha256'), finish);
  policy('unsupported-hmac-constructor', 'ERR_SM_NODE_UNSUPPORTED', () => new nodeCrypto.Hmac('sha256', 'public-test-key'), finish);
  policy('unsupported-sha1', 'ERR_SM_NODE_UNSUPPORTED', () => nodeCrypto.createHash('sha1'), finish);
  policy('unsupported-options', 'ERR_SM_NODE_UNSUPPORTED', () => nodeCrypto.createHash('sha256', {}), finish);
  policy('unsupported-input-encoding-hex', 'ERR_SM_NODE_UNSUPPORTED', () => nodeCrypto.createHash('sha256'), c => { c.update('61', 'hex'); return 'update-returned'; });
  policy('unsupported-output-encoding-base64', 'ERR_SM_NODE_UNSUPPORTED', () => nodeCrypto.createHash('sha256'), (c, done) => { const out = c.digest('base64'); done(); return out; });
  let algorithmConversions = 0;
  profilePolicy.push({ id: 'invalid-algorithm-type', expectedProfileErrorCode: 'ERR_INVALID_ARG_TYPE',
    actual: withContext(() => nodeCrypto.createHash({ toString() { algorithmConversions++; return 'sha256'; } }), finish), algorithmConversions, nodeParityRequired: false });
  profilePolicy.push({ id: 'invalid-receiver', expectedProfileErrorCode: 'ERR_INVALID_THIS',
    actual: attempt(() => nodeCrypto.Hash.prototype.update.call({}, 'x')), nodeParityRequired: false });
  const namespaceNames = Object.getOwnPropertyNames(nodeCrypto).sort();
  const aliases = { namedDefaultHashSame: nodeCrypto.createHash === nodeCrypto.default.createHash,
    namedDefaultHmacSame: nodeCrypto.createHmac === nodeCrypto.default.createHmac,
    bareNamedHashSame: bareCrypto.createHash === nodeCrypto.createHash, bareNamedHmacSame: bareCrypto.createHmac === nodeCrypto.createHmac,
    bareDefaultObjectSame: bareCrypto.default === nodeCrypto.default,
    diffieHellmanAliasSame: nodeCrypto.getDiffieHellman === nodeCrypto.createDiffieHellmanGroup,
    prngAliasSame: nodeCrypto.default.prng === nodeCrypto.randomBytes,
    rngAliasSame: nodeCrypto.default.rng === nodeCrypto.randomBytes,
    pseudoRandomBytesAliasSame: nodeCrypto.default.pseudoRandomBytes === nodeCrypto.randomBytes,
    defaultWebcryptoSame: nodeCrypto.default.webcrypto === nodeCrypto.webcrypto,
    defaultSubtleSame: nodeCrypto.default.subtle === nodeCrypto.subtle,
    webcryptoGlobalSame: nodeCrypto.webcrypto === globalThis.crypto, subtleSame: nodeCrypto.subtle === nodeCrypto.webcrypto.subtle };
  return JSON.stringify({ schemaVersion: 1, kind: 'node-sha256-hash-hmac-ordinary-v1', calls, nodeComparable, aliases, profilePolicy,
    namespaceInspection: { actualNames: namespaceNames, expectedInitialNames: EXPECTED_NAMESPACE_NAMES,
      nativeAndNodeNamespaceObjectIdentityNotRequired: true, namespaceObjectsSame: nodeCrypto === bareCrypto,
      namespaceDescriptors: descriptors(nodeCrypto), defaultDescriptors: descriptors(nodeCrypto.default),
      defaultFrozen: Object.isFrozen(nodeCrypto.default), namespaceExtensible: Object.isExtensible(nodeCrypto) },
    providerAndConstants: { constantsType: typeof nodeCrypto.constants, ownDescriptors: descriptors(nodeCrypto.constants),
      nativeSubsetExpectedNames: ['OPENSSL_VERSION_NUMBER','RSA_PKCS1_PADDING','RSA_NO_PADDING','RSA_PKCS1_OAEP_PADDING','RSA_X931_PADDING','RSA_PKCS1_PSS_PADDING','RSA_PSS_SALTLEN_DIGEST','RSA_PSS_SALTLEN_MAX_SIGN','RSA_PSS_SALTLEN_AUTO'],
      constantsNodeParityRequired: false, headerNumberIsRuntimeBackendProof: false, providerRuntimeIdentityObserved: false,
      opensslVersionNumber: dataValue(nodeCrypto.constants.OPENSSL_VERSION_NUMBER) },
    limits: { moduleInitCryptoCalls: 0, stateCreationOnlyInsideOrdinaryRun: true, everyReturnedContextDrivenToDigest: true,
      nativeFinalizationOrZeroizationProved: false, liveEvpSnapshotAdmission: false, gcPressureInvoked: false,
      borrowVariantInvoked: false, cryptoKeyOrKeyObjectUsed: false, entropyOperationInvoked: false, resetInvoked: false,
      streamInheritanceOrFullNodeCryptoProved: false, fullNextCompatibilityProved: false, runtimeAcceptanceClaim: false } });
}
