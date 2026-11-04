// Production integration vectors. No policy is emulated in JavaScript.
// Execute only with the selected policy engine and validated packaging receipt.
// The caller must supply the actual selected installed native globals.
function demand(condition, message) { if (!condition) throw new Error(message); }
function codedFailure(callback, code) {
  let error;
  try { callback(); } catch (failure) { error = failure; }
  demand(error && error.code === code, `Expected ${code}, got ${error?.code ?? error}`);
  return { code: error.code, message: error.message };
}
const hex = bytes => Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');

export async function entropyChecks(policy) {
  const input = new Uint8Array(32).fill(0xaa);
  const result = { policy };
  if (policy === 'off') {
    result.getRandomValues = codedFailure(() => crypto.getRandomValues(input), 'ERR_SM_ENTROPY_DISABLED');
    result.randomUUID = codedFailure(() => crypto.randomUUID(), 'ERR_SM_ENTROPY_DISABLED');
    result.objectURL = codedFailure(() => URL.createObjectURL(new Blob(['x'])), 'ERR_SM_ENTROPY_DISABLED');
    result.multipart = codedFailure(() => { const form = new FormData(); form.append('x', 'y'); return new Response(form); }, 'ERR_SM_ENTROPY_DISABLED');
    demand(input.every(byte => byte === 0xaa), 'Disabled entropy mutated caller bytes');
  } else {
    demand(policy === 'runtime-only', 'Unknown policy');
    demand(crypto.getRandomValues(input) === input, 'getRandomValues must preserve object identity');
    result.bytes = hex(input);
    result.uuid = crypto.randomUUID();
    const objectURL = URL.createObjectURL(new Blob(['x']));
    demand(objectURL.startsWith('blob:'), 'Object URL generated from fresh secure token');
    URL.revokeObjectURL(objectURL);
    const form = new FormData(); form.append('x', 'y');
    const response = new Response(form);
    result.multipartContentType = response.headers.get('content-type');
    demand(result.multipartContentType.startsWith('multipart/form-data; boundary='), 'Multipart boundary');
    demand(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(result.uuid), 'UUID format/version/variant');
  }
  // Pure hashing must work in OFF without selecting entropy. Native WebCrypto
  // is reused; no node:crypto module/export support is claimed by this fixture.
  const digest = await crypto.subtle.digest('SHA-256', new Uint8Array([97, 98, 99]));
  result.hash = hex(new Uint8Array(digest));
  demand(result.hash === 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', 'SHA256 abc');
  return result;
}

export async function digestCopyCheck() {
  // Safe mutation-only regression; ownership-checks.mjs adds detach/resize
  // vectors after the native owned-input fix.
  const input = new Uint8Array([1, 2, 3]);
  const algorithm = { get name() { input.fill(0); return 'SHA-256'; } };
  const digest = await crypto.subtle.digest(algorithm, input);
  const actual = hex(new Uint8Array(digest));
  demand(actual === '709e80c88487a2411e1ee4dfb9f22a861492d20c4765150c0c794abd70f8147c',
    'Pinned Node22 observes algorithm-getter mutation before digest input copy');
  return actual;
}
