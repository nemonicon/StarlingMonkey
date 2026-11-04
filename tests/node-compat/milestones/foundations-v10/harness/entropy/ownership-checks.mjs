// Execute against pinned Node22 first, then only an engine with owned-input fix.
// These vectors intentionally detach/resize JS storage from algorithm getters.
export async function ownershipChecks(crypto) {
  const demand = (ok, detail) => { if (!ok) throw new Error(detail); };
  const hex = bytes => Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
  const digest = async (algorithm, bytes) => hex(new Uint8Array(await crypto.subtle.digest(algorithm, bytes)));
  const emptyHash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
  const cases = [];
  for (const mode of ['mutate', 'initial-detached', 'detach-in-getter', 'resize-in-getter']) {
    const backing = new ArrayBuffer(8, { maxByteLength: 16 });
    const input = new Uint8Array(backing); input.set([1, 2, 3, 4, 5, 6, 7, 8]);
    let getterCalls = 0;
    if (mode === 'initial-detached') structuredClone(backing, { transfer: [backing] });
    const algorithm = { get name() {
      getterCalls++;
      // Allocate JS data while normalization holds no borrowed payload pointer.
      const pressure = Array.from({ length: 256 }, (_, i) => ({ i, bytes: new Uint8Array(256) }));
      demand(pressure.length === 256, 'allocation pressure');
      if (mode === 'mutate') input.fill(0);
      if (mode === 'detach-in-getter') structuredClone(backing, { transfer: [backing] });
      if (mode === 'resize-in-getter') backing.resize(4);
      return 'SHA-256';
    } };
    const observed = await digest(algorithm, input);
    const expected = mode.includes('detached') || mode === 'detach-in-getter' ? emptyHash
      : await digest('SHA-256', mode === 'mutate' ? new Uint8Array(8) : new Uint8Array([1, 2, 3, 4]));
    demand(getterCalls === 1 && observed === expected, `${mode} digest/order`);
    cases.push({ name: mode, getterCalls, digest: observed });
  }
  for (const mode of ['invalid-data', 'getter-throw-invalid']) {
    let getterCalls = 0, failure;
    try { await digest({ get name() { getterCalls++; throw new Error('getter must not execute'); } }, {}); }
    catch (error) { failure = error; }
    demand(getterCalls === 0 && failure?.name === 'TypeError', `${mode} validation order`);
    cases.push({ name: mode, getterCalls, errorName: failure.name });
  }
  // The key's JS representation is independent from its owned native bytes.
  const raw = new Uint8Array([1, 2, 3]);
  const key = await crypto.subtle.importKey('raw', raw, {
    get name() { raw.fill(7); return 'HMAC'; }, hash: 'SHA-256'
  }, false, ['sign', 'verify']);
  raw.fill(0xff);
  const expectedKey = await crypto.subtle.importKey('raw', new Uint8Array([7, 7, 7]), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
  const message = new Uint8Array([1, 2, 3]);
  const signature = new Uint8Array(await crypto.subtle.sign({ get name() { message.fill(4); return 'HMAC'; } }, key, message));
  const expectedSignature = new Uint8Array(await crypto.subtle.sign('HMAC', expectedKey, new Uint8Array([4, 4, 4])));
  demand(hex(signature) === hex(expectedSignature), 'sign/input copy and key ownership');
  const verificationData = new Uint8Array([0, 0, 0]);
  const verificationSignature = new Uint8Array(signature.length);
  const verified = await crypto.subtle.verify({ get name() {
    verificationSignature.set(signature); verificationData.fill(4); return 'HMAC';
  } }, key, verificationSignature, verificationData);
  demand(verified, 'verify/signature+data copy after getter');
  cases.push({ name: 'hmac-owned-key-sign-verify', signature: hex(signature), verified });
  // A keyUsages array getter is another untrusted callback before key import.
  // General iterable usages remain an existing StarlingMonkey limitation.
  const iteratedRaw = new Uint8Array([1, 2, 3]);
  const usages = []; Object.defineProperty(usages, 0, { get() { iteratedRaw.fill(7); return 'sign'; } });
  const iteratedKey = await crypto.subtle.importKey('raw', iteratedRaw, { name: 'HMAC', hash: 'SHA-256' }, false, usages);
  const iteratedSignature = new Uint8Array(await crypto.subtle.sign('HMAC', iteratedKey, new Uint8Array([4, 4, 4])));
  demand(hex(iteratedSignature) === hex(expectedSignature), 'keyUsages mutation order');
  cases.push({ name: 'key-usage-array-getter-order', signature: hex(iteratedSignature) });
  return cases;
}
