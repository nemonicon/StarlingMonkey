// Bundled guest prototype only; native node:assert is NOT installed.
import * as root from './prototype.mjs';
import * as strict from './strict.mjs';
import { assertChecks, prototypeOnlyChecks } from './checks.mjs';
let calls = 0;
export async function run() {
  try {
    return JSON.stringify({ calls: ++calls,
      namespaceIdentity: (await Promise.resolve(root)) === root && (await Promise.resolve(strict)) === strict,
      cases: assertChecks(root, strict), profile: prototypeOnlyChecks(root) });
  } catch (error) {
    return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } });
  }
}
