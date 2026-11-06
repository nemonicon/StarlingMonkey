import crypto, { constants, createHash, createHmac } from 'node:crypto';
// INIT imports and metadata only; no EVP-backed operation.
export function run() {
  return JSON.stringify({ constantsObject: typeof constants === 'object',
    namedDefaultIdentity: crypto.createHash === createHash && crypto.createHmac === createHmac });
}
