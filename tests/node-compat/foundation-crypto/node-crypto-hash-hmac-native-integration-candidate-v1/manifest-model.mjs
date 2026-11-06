// Pure full-manifest validation. This does not admit an engine or invoke a bundler.
import { validateManifest } from '../../../../builtins/node-compat/validate-manifest.mjs';
export function validateHashHmacSelectedManifests(values, policy, schema) {
  if (values.length !== 12 || JSON.stringify(values) !== JSON.stringify(policy.selectedManifestValues))
    throw new Error('Exact eleven native plus one crypto packaging manifest required');
  const ids = new Set(), aliases = new Set();
  for (const value of values) {
    validateManifest(value, schema);
    for (const [id, module] of Object.entries(value.modules)) {
      if (!id.startsWith('node:') || ids.has(id) || aliases.has(id)) throw new Error('Duplicate or noncanonical module');
      ids.add(id);
      for (const alias of module.aliases) {
        if (aliases.has(alias) || ids.has(alias) || alias !== id.slice(5)) throw new Error('Duplicate/noncanonical native alias');
        aliases.add(alias);
      }
    }
  }
  const crypto = values.at(-1).modules['node:crypto'];
  if (!crypto || JSON.stringify(crypto.exports) !== JSON.stringify(policy.hashHmacSourcePolicy.esmNamedIncludingDefault))
    throw new Error('Exact crypto ESM inventory required');
  if (crypto.exports.length !== 68 || crypto.exports.includes('then')) throw new Error('Wrong crypto scalar namespace');
  return Object.freeze({ validated: true, manifests: 12, nativeManifestRows: 11,
    separatePackagingManifestRows: 1, cryptoEsmNames: 68, grantsNativeOrRuntimeAuthority: false });
}
