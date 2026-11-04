import bufferDefault, * as namespace from 'node:buffer';
import { createAllocUnsafeCandidate } from './candidate.mjs';
import { allocationChecks, candidateChecks, preserveCoreUnsupported, temporarilyPatch } from './checks.mjs';
import { demandChecks } from './demand-checks.mjs';
import { createDemandList } from 'node-compat:buffer-list-demand';
import commonJSAllocators from './static-require.cjs';
const { Buffer } = namespace;
const allocate = createAllocUnsafeCandidate(Buffer), List = createDemandList(Buffer);
const snapshot = allocate(2); snapshot[0] = 17;
let calls = 0;
export async function run() {
  try {
    const id = String.fromCharCode(98, 117, 102, 102, 101, 114), bare = await import(id);
    const before = preserveCoreUnsupported(Buffer), original = Object.getOwnPropertyDescriptor(Buffer, 'allocUnsafe');
    let patch, cases, demand;
    temporarilyPatch(Buffer, allocate, () => {
      patch = { canonical: namespace.Buffer.allocUnsafe === allocate, bare: bare.Buffer.allocUnsafe === allocate,
        defaultAlias: bufferDefault.Buffer.allocUnsafe === allocate, global: globalThis.Buffer.allocUnsafe === allocate,
        commonJS: commonJSAllocators().every(value => value === allocate),
        writable: Object.getOwnPropertyDescriptor(Buffer, 'allocUnsafe').writable,
        enumerable: Object.getOwnPropertyDescriptor(Buffer, 'allocUnsafe').enumerable,
        configurable: Object.getOwnPropertyDescriptor(Buffer, 'allocUnsafe').configurable };
      cases = allocationChecks(Buffer, Buffer.allocUnsafe); demand = demandChecks(Buffer, List);
    });
    const restored = Object.getOwnPropertyDescriptor(Buffer, 'allocUnsafe');
    const restore = { sameFunction: restored.value === original.value, writable: restored.writable === original.writable,
      enumerable: restored.enumerable === original.enumerable, configurable: restored.configurable === original.configurable,
      commonJS: commonJSAllocators().every(value => value === original.value) };
    const profile = candidateChecks(Buffer, allocate, createAllocUnsafeCandidate), after = preserveCoreUnsupported(Buffer);
    snapshot[0]++;
    return JSON.stringify({ calls: ++calls, snapshotByte: snapshot[0], snapshotIdentity: Buffer.isBuffer(snapshot),
      namespaceIdentity: (await Promise.resolve(namespace)) === namespace, aliases: bare.Buffer === Buffer && bare.default === bufferDefault,
      before, patch, restore, cases, demand, profile, after, installed: false });
  } catch (error) { return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } }); }
}
