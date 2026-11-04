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
      "builtins/node-compat/factories.generated.h": "cc04376c304ce2c4fe5a6f17eff54256123f02bdfe88555880e1e888babfc869",
      "builtins/node-compat/unsupported.mjs": "013c1934c72a8abfb3e134f29baeb49098a4fda6fad2966df033b5f24ff0957e",
      "builtins/node-compat/buffer.cpp": "7f73ce790e6b23195a9bfa583bacdbf45dfb9fa9aed00489f66952d93ca37cf8"
    }
  },
  "sm-node-22.14.0-m0.11": {
    "allocUnsafePolicy": "zeroed-no-pool-direct-u8-v1",
    "unsupportedStatic": [
      "copyBytesFrom",
      "of",
      "allocUnsafeSlow",
      "compare",
      "concat"
    ],
    "hashes": {
      "builtins/node-compat/buffer-facade.mjs": "8ebfa0253a85bc9b2e91b65391c9f85c26594d107ad0d016cd0351dad89dd235",
      "builtins/node-compat/unsupported.mjs": "8681d64ddf74c42948e0cc99f9808b711618f603dccac09ca25939842731f2cb",
      "builtins/node-compat/export-manifest.node-v22.14.0.json": "abfcc6a07e1b3d2e0877293a7c5fe02bc1ff971a7703c5860d8385b3ad510872",
      "builtins/node-compat/factories.generated.h": "2b6b98b2f5b873c9aff6f0b27cba01c6ad3ef854c49d2ce27ad1f089a9233044",
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
// Guests need only semantic expectations. Compiled-source receipts remain in
// the host audit; embedding their filenames also confuses implementation guards.
export function coreExpectationsForGuest(value) {
  validateCoreExpectations(value);
  return { schema: value.schema, coreVersion: value.coreVersion,
    allocUnsafePolicy: value.allocUnsafePolicy,
    unsupportedStatic: [...value.unsupportedStatic], prototypeRefusals: value.prototypeRefusals };
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

// Host-only checks: source-selected core semantics, never a runtime API toggle.
export function unsupportedMessagePattern(value, module, operation) {
  validateCoreExpectations(value);
  const escape = text => [...text].map(character => "\\^$.*+?()[]{}|".includes(character) ? "\\"+character : character).join('');
  return new RegExp(escape(module+'.'+operation+' is unavailable in '+value.coreVersion)+'(?![A-Za-z0-9.-])');
}
export function validateCoreRuntimeReport(report, value) {
  validateCoreExpectations(value);
  assert.equal(report.coreVersion, value.coreVersion);
  assert.equal(report.allocUnsafePolicy, value.allocUnsafePolicy);
  if (value.allocUnsafePolicy === 'zeroed-no-pool-direct-u8-v1')
    assert.deepEqual(report.allocUnsafePrimordialCalls, {integerCalls:0, finiteCalls:0, truncatedLength:3});
  return report;
}
