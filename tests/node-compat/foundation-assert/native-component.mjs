import * as root from 'node:assert';
import * as strict from 'node:assert/strict';
import { assertChecks, prototypeOnlyChecks } from './checks.mjs';
import inspectCommonJS from './native-require.cjs';
const snapshotValue = { count: 0 };
const snapshotError = new root.AssertionError({ actual: snapshotValue, expected: true, operator: 'snapshot', message: 'snapshot' });
root.ok(snapshotValue);
let calls = 0;
export async function run() {
  try {
    // CJS lowering canonicalizes its static aliases. These bare imports stay
    // computed and are first loaded at actual deployed entry, after snapshot.
    const rootId = String.fromCharCode(97, 115, 115, 101, 114, 116);
    const strictId = rootId + String.fromCharCode(47, 115, 116, 114, 105, 99, 116);
    const bare = await import(rootId), bareStrict = await import(strictId), again = await import(rootId);
    const originalEqual = root.default.equal;
    let sharedMutation;
    try { root.default.equal = 19; sharedMutation = bare.default.equal === 19 && root.equal === originalEqual && strict.equal === root.strictEqual; }
    finally { root.default.equal = originalEqual; }
    const aliases = { names: Object.getOwnPropertyNames(bare).sort(), strictNames: Object.getOwnPropertyNames(bareStrict).sort(),
      canonicalNamespaceStable: (await import('node:'+rootId)) === root,
      bareCache: bare === again, rootValues: Object.keys(root).every(name => root[name] === bare[name]),
      strictValues: Object.keys(strict).every(name => strict[name] === bareStrict[name]),
      moduleTag: Object.prototype.toString.call(bare), nullNamespacePrototype: Object.getPrototypeOf(bare) === null,
      thenType: typeof bare.then, sharedMutation };
    snapshotValue.count++;
    return JSON.stringify({ calls: ++calls, snapshotCount: snapshotValue.count,
      snapshotIdentity: snapshotError.actual === snapshotValue && snapshotError instanceof root.AssertionError,
      namespaceIdentity: (await Promise.resolve(root)) === root && (await Promise.resolve(strict)) === strict,
      cases: assertChecks(root, strict), profile: prototypeOnlyChecks(root), aliases,
      commonJS: inspectCommonJS(root.default, strict.default) });
  } catch (error) { return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } }); }
}
