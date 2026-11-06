// UNCOMPILED RNG successor of reviewed SHA256 profile. No install/INIT entropy.
import {createRandomOperations} from './crypto-rng.mjs';
export function createCryptoModule({ kernel, rng, nextTick, Buffer, webcrypto, subtle }, web = globalThis) {
  const Apply = Reflect.apply;
  const Create = Object.create;
  const Freeze = Object.freeze;
  const Define = Object.defineProperty;
  const Keys = Object.keys;
  const ErrorCtor = Error;
  const TypeErrorCtor = TypeError;
  const Weak = WeakMap;
  const weakGet = Weak.prototype.get;
  const weakSet = Weak.prototype.set;
  const U8 = web.Uint8Array;
  const typed = Object.getPrototypeOf(U8.prototype);
  const bufferGet = Object.getOwnPropertyDescriptor(typed, 'buffer').get;
  const lengthGet = Object.getOwnPropertyDescriptor(typed, 'byteLength').get;
  const tagGet = Object.getOwnPropertyDescriptor(typed, Symbol.toStringTag).get;
  const fill = U8.prototype.fill;
  const abLength = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'byteLength').get;
  const abResizable = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'resizable')?.get;
  const abDetached = Object.getOwnPropertyDescriptor(web.ArrayBuffer.prototype, 'detached')?.get;
  const bufferFrom = Buffer.from;
  const bufferString = Buffer.prototype.toString;
  const records = new Weak();
  const MAX_MESSAGE = 16 * 1024 * 1024;
  const MAX_KEY = 1024 * 1024;
  const MAX_SOURCE = 1024 * 1024;
  const MAX_TOTAL = 64 * 1024 * 1024;
  // Private native methods are captured once, never dispatched through a public object.
  const kh = kernel.createHash, km = kernel.createHmac, ku = kernel.update, kd = kernel.digest;

  function fail(code, message, type = false) {
    const e = new (type ? TypeErrorCtor : ErrorCtor)(message);
    Define(e, 'code', { value: code, enumerable: true });
    throw e;
  }
  function unsupported(name) {
    return function unavailableCryptoOperation() {
      fail('ERR_SM_NODE_UNSUPPORTED', `node:crypto.${name} is unavailable in sha256-proposal-v1`);
    };
  }
  // These are trusted installation-time objects, not arbitrary caller values.
  // Existing native WebCrypto objects are reused, never replaced or frozen.
  if (!webcrypto || typeof webcrypto !== 'object' || !subtle || typeof subtle !== 'object' ||
      !kernel.constants || typeof kernel.constants !== 'object' || Keys(kernel.constants).length === 0)
    fail('ERR_SM_NODE_PROFILE_INITIALIZATION', 'Native crypto value bindings are required');
  function encoding(e, output = false) {
    if (output) {
      if (e === undefined || e === 'buffer') return 'buffer';
      if (e === 'hex') return e;
    } else if (e === undefined || e === 'utf8' || e === 'utf-8') return 'utf8';
    fail('ERR_SM_NODE_UNSUPPORTED', 'Unsupported crypto encoding');
  }
  function bytes(input, enc, max, key = false) {
    if (typeof input === 'string') {
      encoding(enc);
      if (input.length > MAX_SOURCE) fail('ERR_OUT_OF_RANGE', 'Crypto source exceeds limit');
      // Exactly one real UTF-8 conversion through the installed Buffer facade.
      const out = Apply(bufferFrom, Buffer, [input, 'utf8']);
      if (Apply(lengthGet, out, []) > max) {
        if (key) Apply(fill, out, [0]);
        fail('ERR_OUT_OF_RANGE', 'Crypto bytes exceed limit');
      }
      return { value: out, ownedKey: key, length: Apply(lengthGet, out, []) };
    }
    // No user conversion/getter is consulted. This brand check rejects proxies,
    // DataView, non-U8 typed arrays and ordinary Array/ArrayBuffer inputs.
    let backing, length;
    try {
      if (Apply(tagGet, input, []) !== 'Uint8Array') throw 0;
      backing = Apply(bufferGet, input, []);
      Apply(abLength, backing, []); // SharedArrayBuffer fails the real AB brand.
      if ((abResizable && Apply(abResizable, backing, [])) ||
          (abDetached && Apply(abDetached, backing, []))) throw 0;
      length = Apply(lengthGet, input, []);
    } catch {
      fail('ERR_SM_NODE_UNSUPPORTED', 'Crypto requires a fixed, nonshared Uint8Array or Buffer', true);
    }
    if (length > max) fail('ERR_OUT_OF_RANGE', 'Crypto bytes exceed limit');
    // inputEncoding is ignored for byte inputs, as in Node's Hash.update.
    return { value: input, ownedKey: false, length };
  }
  function algorithm(a, options) {
    if (typeof a !== 'string') fail('ERR_INVALID_ARG_TYPE', 'algorithm must be a string', true);
    if (a !== 'sha256' && a !== 'SHA256') fail('ERR_SM_NODE_UNSUPPORTED', 'Only SHA256 is proposed');
    if (options !== undefined) fail('ERR_SM_NODE_UNSUPPORTED', 'Crypto options are unsupported');
  }
  function record(receiver) {
    const r = Apply(weakGet, records, [receiver]);
    if (!r) fail('ERR_INVALID_THIS', 'Incompatible Hash/Hmac receiver', true);
    return r;
  }
  const Hash = unsupported('Hash constructor');
  const Hmac = unsupported('Hmac constructor');
  function update(input, inputEncoding) {
    const r = record(this);
    if (r.finalized) fail('ERR_CRYPTO_HASH_FINALIZED', 'Digest already called');
    const b = bytes(input, inputEncoding, MAX_MESSAGE);
    if (r.total > MAX_TOTAL - b.length) fail('ERR_OUT_OF_RANGE', 'Crypto cumulative bytes exceed limit');
    try { Apply(ku, undefined, [r.handle, b.value]); }
    catch (e) { r.finalized = true; r.handle = undefined; throw e; }
    r.total += b.length;
    return this;
  }
  function digest(outputEncoding) {
    const r = record(this);
    const e = encoding(outputEncoding, true); // refuse before consuming the state
    if (r.finalized) {
      if (r.kind === 'hash') fail('ERR_CRYPTO_HASH_FINALIZED', 'Digest already called');
      return e === 'hex' ? '' : Apply(bufferFrom, Buffer, [new U8(0)]);
    }
    // The native contract consumes/releases the state on success AND failure.
    // Even a later Buffer allocation failure cannot expose a reusable context.
    const h = r.handle;
    r.finalized = true;
    r.handle = undefined;
    const raw = Apply(kd, undefined, [h]);
    const out = Apply(bufferFrom, Buffer, [raw]); // bounded 32-byte ownership copy
    return e === 'hex' ? Apply(bufferString, out, ['hex']) : out;
  }
  for (const C of [Hash, Hmac]) {
    Define(C.prototype, 'update', { value: update });
    Define(C.prototype, 'digest', { value: digest });
    for (const name of ['copy', 'pipe', 'write', 'end', 'on', 'once', 'read', 'destroy'])
      Define(C.prototype, name, { value: unsupported(`${C === Hash ? 'Hash' : 'Hmac'}.${name}`) });
    Freeze(C.prototype);
  }
  function wrap(kind, handle) {
    const out = Create(kind === 'hash' ? Hash.prototype : Hmac.prototype);
    Apply(weakSet, records, [out, { kind, handle, finalized: false, total: 0 }]);
    return out;
  }
  function createHash(a, options) {
    algorithm(a, options);
    return wrap('hash', Apply(kh, undefined, []));
  }
  function createHmac(a, key, options) {
    algorithm(a, options);
    const b = bytes(key, undefined, MAX_KEY, true);
    try { return wrap('hmac', Apply(km, undefined, [b.value])); }
    finally { if (b.ownedKey) Apply(fill, b.value, [0]); }
  }

  // Exact initial enumerable Node v22.14.0 crypto keys, statically derived from
  // the captured official crypto.js. Presence is not an implementation claim.
  const callableNames = [
    'checkPrime','checkPrimeSync','createCipheriv','createDecipheriv','createDiffieHellman',
    'createDiffieHellmanGroup','createECDH','createHash','createHmac','createPrivateKey',
    'createPublicKey','createSecretKey','createSign','createVerify','diffieHellman',
    'generatePrime','generatePrimeSync','getCiphers','getCipherInfo','getCurves',
    'getDiffieHellman','getHashes','hkdf','hkdfSync','pbkdf2','pbkdf2Sync','generateKeyPair',
    'generateKeyPairSync','generateKey','generateKeySync','privateDecrypt','privateEncrypt',
    'publicDecrypt','publicEncrypt','randomBytes','randomFill','randomFillSync','randomInt',
    'randomUUID','scrypt','scryptSync','sign','setEngine','timingSafeEqual','getFips','setFips',
    'verify','hash','Certificate','Cipher','Cipheriv','Decipher','Decipheriv','DiffieHellman',
    'DiffieHellmanGroup','ECDH','Hash','Hmac','KeyObject','Sign','Verify','X509Certificate',
    'secureHeapUsed',
  ];
  const named = Create(null);
  for (const name of callableNames) named[name] = unsupported(name);
  named.createHash = createHash; named.createHmac = createHmac;
  named.Hash = Hash; named.Hmac = Hmac;
  named.getDiffieHellman = named.createDiffieHellmanGroup;
  // Finite numeric guest-header constants; full Node TLS/cipher constants are
  // deliberately not fabricated. The private native object contains no keys.
  named.constants = Freeze(kernel.constants);
  named.webcrypto = webcrypto;
  named.subtle = subtle;
  named.getRandomValues = unsupported('getRandomValues');
  if(rng!==undefined){if(typeof nextTick!=='function')fail('ERR_SM_NODE_PROFILE_INITIALIZATION','Genuine private nextTick required');const random=createRandomOperations({rng,Buffer,webcrypto,nextTick},web);for(const name of Keys(random))named[name]=random[name];}
  const defaultExport = Create(null);
  for (const name of Keys(named)) defaultExport[name] = named[name];
  for (const name of ['prng', 'pseudoRandomBytes', 'rng'])
    Define(defaultExport, name, { value: named.randomBytes, enumerable: false });
  Define(defaultExport, 'fips', { get: unsupported('fips'), enumerable: false });
  // Next installs real wrappers on its CJS crypto object; ESM names remain the
  // initial record, with later syncBuiltinESMExports behavior still deferred.
  if(rng===undefined)Freeze(defaultExport);
  named.default = defaultExport;
  return Freeze(named);
}
