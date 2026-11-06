// Host-only protocol/ownership tests. NO node:crypto or actual hash/HMAC calls.
import assert from 'node:assert/strict';
import { createCryptoModule } from './crypto-facade.mjs';
import { readFileSync } from 'node:fs';
let checks = 0;
function check(value, message) { assert.ok(value, message); checks++; }
function refuses(fn, code) { assert.throws(fn, e => e.code === code); checks++; }
const log = [], handles = [], encodedKeys = [];
const nativeWebCrypto = { existingNativeIdentityModel: 'crypto' };
const nativeSubtle = { existingNativeIdentityModel: 'subtle' };
let failUpdate = false, failDigest = false;
const kernel = {
  constants: JSON.parse(readFileSync(new URL('./constants-policy.json', import.meta.url))).providedHeaderNumericSubset,
  createHash() { const h = { kind: 'hash', bytes: [], live: true }; handles.push(h); return h; },
  createHmac(key) {
    encodedKeys.push(key);
    const h = { kind: 'hmac', key: [...key], bytes: [], live: true };
    handles.push(h); return h;
  },
  update(h, input) {
    log.push({ input, offset: input.byteOffset, length: input.byteLength });
    if (failUpdate) { h.live = false; throw Object.assign(new Error('mock update'), { code: 'MOCK' }); }
    assert.ok(h.live); h.bytes.push(...input);
  },
  digest(h) {
    assert.ok(h.live); h.live = false;
    if (failDigest) throw Object.assign(new Error('mock final'), { code: 'MOCK' });
    // Deliberately not a hash: fixed tagged bytes expose facade transport only.
    return Uint8Array.from({ length: 32 }, (_, i) => (i + h.bytes.length) & 255);
  },
};
const m = createCryptoModule({ kernel, Buffer, webcrypto: nativeWebCrypto, subtle: nativeSubtle });
check(handles.length === 0, 'module install creates no native contexts');
const manifest = JSON.parse(readFileSync(new URL('./node-export-manifest.json', import.meta.url)));
check(JSON.stringify(Object.keys(m).sort()) === JSON.stringify(manifest.esmNamedIncludingDefault.slice().sort()), 'exact static Node namespace keys');
check(JSON.stringify(Object.keys(m)) === JSON.stringify(manifest.esmNamedIncludingDefault), 'official initial export insertion order');
check(JSON.stringify(Object.getOwnPropertyNames(m.default).sort()) === JSON.stringify(manifest.defaultOwnKeys.slice().sort()), 'exact default own keys');
for (const name of manifest.esmNamedIncludingDefault.filter(n => n !== 'default'))
  check(m[name] === m.default[name], `default identity ${name}`);
check(m.getDiffieHellman === m.createDiffieHellmanGroup, 'alias identity');
check(m.default.rng === m.randomBytes && m.default.prng === m.randomBytes, 'default-only random aliases');
check(!Object.keys(m.default).includes('fips') && !Object.keys(m).includes('fips'), 'nonenumerable Node default-only names');
check(m.webcrypto === nativeWebCrypto && m.subtle === nativeSubtle, 'existing native identity bindings retained in model');
check(m.default.webcrypto === nativeWebCrypto && m.default.subtle === nativeSubtle, 'named and default WebCrypto aliases');
check(typeof m.constants === 'object' && Object.keys(m.constants).length === 9, 'meaningful finite constants object');
check(Object.values(m.constants).every(Number.isSafeInteger) && m.constants.RSA_PKCS1_PADDING === 1 && m.constants.RSA_PSS_SALTLEN_DIGEST === -1, 'typed guest-header constant values');
check(Object.isFrozen(m.constants) && !Object.isFrozen(nativeWebCrypto), 'constant freeze does not freeze native WebCrypto');
refuses(() => createCryptoModule({ kernel, Buffer }), 'ERR_SM_NODE_PROFILE_INITIALIZATION');
refuses(() => m.default.fips, 'ERR_SM_NODE_UNSUPPORTED');
for (const name of manifest.unsupportedCallableNamed) refuses(() => m[name](), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => new m.Hash('sha256'), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => new m.Hmac('sha256', 'key'), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => m.createHash('sha1'), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => m.createHash('sha256', {}), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => m.createHash({ toString() { throw 17; } }), 'ERR_INVALID_ARG_TYPE');
const h = m.createHash('sha256');
check(h instanceof m.Hash && !(h instanceof m.Hmac), 'public factory prototype branding');
const backing = Uint8Array.of(99, 1, 2, 3, 88), window = backing.subarray(1, 4);
check(h.update(window) === h, 'chaining identity');
check(log.at(-1).input === window && log.at(-1).offset === 1 && log.at(-1).length === 3, 'pass exact U8 window, no JS message copy');
backing[2] = 77;
check(JSON.stringify(handles.at(-1).bytes) === '[1,2,3]', 'mock consumed data synchronously');
h.update('').update(new Uint8Array(0)).update('é');
check(JSON.stringify(handles.at(-1).bytes) === '[1,2,3,195,169]', 'one real UTF8 path and empty updates');
refuses(() => h.update(new Uint16Array([1])), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => h.update(new DataView(new ArrayBuffer(4))), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => h.update(new ArrayBuffer(4)), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => h.update([1]), 'ERR_SM_NODE_UNSUPPORTED');
let conversions = 0;
refuses(() => h.update({ get buffer() { conversions++; }, toString() { conversions++; } }), 'ERR_SM_NODE_UNSUPPORTED');
check(conversions === 0, 'invalid input invokes no user conversion or property getter');
refuses(() => h.update(new Proxy(window, {})), 'ERR_SM_NODE_UNSUPPORTED');
if (typeof SharedArrayBuffer === 'function') refuses(() => h.update(new Uint8Array(new SharedArrayBuffer(2))), 'ERR_SM_NODE_UNSUPPORTED');
if (Object.getOwnPropertyDescriptor(ArrayBuffer.prototype, 'resizable')) {
  refuses(() => h.update(new Uint8Array(new ArrayBuffer(2, { maxByteLength: 4 }))), 'ERR_SM_NODE_UNSUPPORTED');
}
const detached = new ArrayBuffer(3), detachedView = new Uint8Array(detached);
structuredClone(detached, { transfer: [detached] });
refuses(() => h.update(detachedView), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => h.update('abc', 'hex'), 'ERR_SM_NODE_UNSUPPORTED');
refuses(() => h.digest('base64'), 'ERR_SM_NODE_UNSUPPORTED');
check(handles.at(-1).live, 'unsupported output encoding does not consume state');
const out = h.digest();
check(Buffer.isBuffer(out) && out.length === 32 && !handles.at(-1).live, 'fresh owned Buffer result');
refuses(() => h.digest(), 'ERR_CRYPTO_HASH_FINALIZED');
refuses(() => h.update('a'), 'ERR_CRYPTO_HASH_FINALIZED');
refuses(() => m.Hash.prototype.update.call({}, 'x'), 'ERR_INVALID_THIS');
const callerKey = Uint8Array.of(9, 10), mac = m.createHmac('SHA256', callerKey);
callerKey[0] = 200;
check(handles.at(-1).key[0] === 9 && callerKey[0] === 200, 'key snapshot contract without mutating caller key');
check(m.Hmac.prototype.update === m.Hash.prototype.update, 'shared update identity');
mac.update(Buffer.from([4, 5]));
const hex = mac.digest('hex');
check(hex.length === 64 && mac.digest('hex') === '' && mac.digest().length === 0, 'Hmac repeated digest returns empty');
refuses(() => mac.update('x'), 'ERR_CRYPTO_HASH_FINALIZED');
m.createHmac('sha256', 'secret');
check(encodedKeys.at(-1).every(x => x === 0), 'owned JS UTF8 key staging wiped after init');
check(handles.at(-1).key.length === 6 && handles.at(-1).key[0] === 115, 'native mock owns key before JS staging wipe');
const emptyMac = m.createHmac('sha256', new Uint8Array(0));
check(handles.at(-1).key.length === 0 && emptyMac.digest().length === 32, 'empty key accepted');
const bufKey = Buffer.from([5, 6]); m.createHmac('sha256', bufKey);
check(bufKey[0] === 5 && bufKey[1] === 6, 'caller Buffer key not wiped');
refuses(() => m.createHmac('sha256', new Uint8Array(1024 * 1024 + 1)), 'ERR_OUT_OF_RANGE');
refuses(() => m.createHash('sha256').update(new Uint8Array(16 * 1024 * 1024 + 1)), 'ERR_OUT_OF_RANGE');
failUpdate = true;
const failedUpdate = m.createHash('sha256');
refuses(() => failedUpdate.update('x'), 'MOCK');
refuses(() => failedUpdate.update('x'), 'ERR_CRYPTO_HASH_FINALIZED');
failUpdate = false; failDigest = true;
const failedDigest = m.createHash('sha256');
refuses(() => failedDigest.digest(), 'MOCK');
refuses(() => failedDigest.digest(), 'ERR_CRYPTO_HASH_FINALIZED');
failDigest = false;
const oldFrom = Buffer.from, oldUpdate = kernel.update;
try {
  Buffer.from = () => { throw 19; };
  kernel.update = () => { throw 20; };
  check(m.createHash('sha256').update('x').digest('hex').length === 64, 'captured trusted methods survive later mutation');
} finally { Buffer.from = oldFrom; kernel.update = oldUpdate; }
console.log(JSON.stringify({ state: 'HOST_PURE_FACADE_MODELS_PASSED', checks, actualCodecCalls: 0,
  nativeKernelCompiled: false, mockKernelOnly: true }));
