// TEST EXPECTATIONS ONLY. No guest API or runtime feature toggle.
// Select solely from an exact recognized core source receipt, after engine-byte verification.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { CORE_MANIFEST, selectedManifestsForEngine } from './module-selection.mjs';
const known = {
  "sm-node-22.14.0-m0.1": {
    "allocUnsafePolicy": "deferred",
    "unsupportedStatic": [
      "copyBytesFrom",
      "of",
      "allocUnsafe",
      "allocUnsafeSlow",
      "compare",
      "concat"
    ],
    "hashes": {
      "builtins/node-compat/buffer-facade.mjs": "b1a8b671e4ebf71ed300b56afb1d60986ef37be1716f55bf00b35151a4a00f16",
      "builtins/node-compat/export-manifest.node-v22.14.0.json": "fbc2f85596eab0cd9614fcd12281212fce55a3c925da731650a4cfa2927809e3",
      "builtins/node-compat/factories.generated.h": "7de6c1e35dec100894bb7fe6f904b491ef5497df5ae8fe3ce6494742bc91b84e",
      "builtins/node-compat/unsupported.mjs": "412b869a321421f3930e25ba2c0d4bac4dac9effbbb1e4d84eaf636599d38ea8",
      "builtins/node-compat/buffer.cpp": "7f73ce790e6b23195a9bfa583bacdbf45dfb9fa9aed00489f66952d93ca37cf8"
    }
  },
  "sm-node-22.14.0-m0.8": {
    "allocUnsafePolicy": "zeroed-no-pool-v1",
    "unsupportedStatic": [
      "copyBytesFrom",
      "of",
      "allocUnsafeSlow",
      "compare",
      "concat"
    ],
    "hashes": {
      "builtins/node-compat/buffer-facade.mjs": "4af877ca8ebb0273c71d5289fc2e60084623ef57ff10b0a6735181e65af8452d",
      "builtins/node-compat/export-manifest.node-v22.14.0.json": "0e482334c46240f1cc4a20e97530a2339e14339f29dc14c27e025f1e6d218439",
      "builtins/node-compat/factories.generated.h": "e6463dbf6c5f741b0b41c952add2ee4ea1129c8950a614b49c4f2f806f51309c",
      "builtins/node-compat/unsupported.mjs": "aaac55f7e67a5861624ddb38e8ca83fc8b5ef8216789fff18ded772ebbf12f67",
      "builtins/node-compat/buffer.cpp": "7f73ce790e6b23195a9bfa583bacdbf45dfb9fa9aed00489f66952d93ca37cf8"
    }
  }
};
const hash = value => createHash('sha256').update(value).digest('hex');
function expected(version) {
  const core = known[version]; assert(core && Object.hasOwn(known, version), 'Unrecognized core compatibility version');
  return { schema: 1, coreVersion: version, allocUnsafePolicy: core.allocUnsafePolicy,
    unsupportedStatic: [...core.unsupportedStatic], prototypeRefusals: 91,
    manifestSha256: core.hashes[CORE_MANIFEST], sourceHashes: { ...core.hashes } };
}
export function validateCoreExpectations(value) {
  assert(value && typeof value === 'object' && !Array.isArray(value), 'Missing core expectations');
  assert.deepEqual(value, expected(value.coreVersion), 'Core expectation fields disagree with the recognized source contract');
  return value;
}
export function selectCoreExpectations(metadata, { sourceRoot }) {
  assert(typeof sourceRoot === 'string' && sourceRoot.length, 'Core policy requires explicit sourceRoot');
  const root = resolve(sourceRoot);
  const manifests = selectedManifestsForEngine(metadata, { sourceRoot: root });
  const manifest = manifests.find(item => Object.hasOwn(item.modules, 'node:buffer'));
  assert(manifest, 'Core manifest must contain Buffer'); const version = manifest.profileVersion;
  const value = expected(version), sources = new Map();
  for (const entry of metadata.sourceManifest) {
    assert(entry && typeof entry.path === 'string' && typeof entry.sha256 === 'string' && /^[0-9a-f]{64}$/.test(entry.sha256), 'Malformed source receipt');
    assert(!sources.has(entry.path), 'Duplicate compiled input path'); sources.set(entry.path, entry.sha256);
  }
  for (const [path, digest] of Object.entries(value.sourceHashes)) {
    assert.equal(sources.get(path), digest, 'Core source receipt does not match selected profile: '+path);
    const absolute = resolve(root, path); assert(absolute.startsWith(root+'/'), 'Core source escapes selected root');
    assert.equal(hash(readFileSync(absolute)), digest, 'Core source bytes do not match selected profile: '+path);
  }
  assert.deepEqual(manifest.modules['node:buffer'].unsupportedStatic, value.unsupportedStatic);
  return Object.freeze({ ...value, unsupportedStatic: Object.freeze(value.unsupportedStatic), sourceHashes: Object.freeze(value.sourceHashes) });
}
