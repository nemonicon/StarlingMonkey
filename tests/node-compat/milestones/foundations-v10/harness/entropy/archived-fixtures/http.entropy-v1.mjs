import { run as runNativeChecks } from '../fixtures/component.mjs';
import { createIncomingHandler } from '../wasmcloud/http.mjs';
import { entropyChecks, digestCopyCheck } from './guest-checks.mjs';
import { ownershipChecks } from './ownership-checks.mjs';
import { rsaBridgeCheck } from './rsa-bridge-check.mjs';
import policy from 'node-compat:entropy-policy';

// All work here occurs during componentization. The selected mode is supplied
// by the engine-receipt-aware builder, not a guest runtime toggle.
const expectedCode = policy === 'off' ? 'ERR_SM_ENTROPY_DISABLED' : 'ERR_SM_ENTROPY_INITIALIZATION';
const snapshot = [];
for (const [operation, callback] of [
  ['getRandomValues', () => crypto.getRandomValues(new Uint8Array(16))],
  ['randomUUID', () => crypto.randomUUID()],
  ['objectURL', () => URL.createObjectURL(new Blob(['x']))],
  ['multipart', () => { const form = new FormData(); form.append('x', 'y'); return new Response(form); }],
]) {
  let failure;
  try { callback(); } catch (error) { failure = error; }
  if (failure?.code !== expectedCode) throw failure ?? new Error(`Snapshot entropy succeeded: ${operation}`);
  snapshot.push({ operation, code: failure.code });
}
// Hashing must remain a snapshot-safe, entropy-free operation in both modes.
const snapshotHash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new Uint8Array([97, 98, 99]))), byte => byte.toString(16).padStart(2, '0')).join('');
if (snapshotHash !== 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad') throw new Error('Snapshot SHA256');
let snapshotRsa;
if (policy === 'runtime-only') {
  try { await rsaBridgeCheck(crypto); snapshotRsa = { succeeded: true }; }
  catch (error) { snapshotRsa = { succeeded: false, name: error.name, code: error.code, message: error.message }; }
}

async function runChecks() {
  const report = JSON.parse(await runNativeChecks());
  report.entropyIntegration = {
    policy, snapshot, snapshotHash, snapshotRsa,
    secure: await entropyChecks(policy), digestCopy: await digestCopyCheck(),
    ownership: await ownershipChecks(crypto),
    // OFF makes no claim that entropy-dependent provider operations work.
    rsa: policy === 'runtime-only' ? await rsaBridgeCheck(crypto) : { executed: false, reason: 'Runtime entropy not selected' },
  };
  return JSON.stringify(report);
}
export const incomingHandler = createIncomingHandler(runChecks);
