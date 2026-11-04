import * as querystring from 'node:querystring';
import { Buffer } from 'node:buffer';
import { querystringChecks, prototypeOnlyChecks } from './checks.mjs';
import inspectCommonJS from './native-require.cjs';
const snapshotBytes = querystring.unescapeBuffer('%41%42');
const snapshotView = new Uint8Array(snapshotBytes.buffer, snapshotBytes.byteOffset, snapshotBytes.length);
const snapshotParsed = querystring.parse('a=1&a=2');
let calls = 0;
export async function run() {
  try {
    const id = String.fromCharCode(113, 117, 101, 114, 121, 115, 116, 114, 105, 110, 103);
    const bare = await import(id), again = await import(id);
    const originalParse = querystring.default.parse;
    let sharedMutation;
    try { querystring.default.parse = 19; sharedMutation = bare.default.parse === 19 && querystring.parse === originalParse; }
    finally { querystring.default.parse = originalParse; }
    const originalGlobalBuffer = globalThis.Buffer;
    let privateBuffer;
    try { globalThis.Buffer = undefined; privateBuffer = Buffer.isBuffer(querystring.unescapeBuffer('%41')); }
    finally { globalThis.Buffer = originalGlobalBuffer; }
    const aliases = { names: Object.getOwnPropertyNames(bare).sort(),
      canonicalNamespaceStable: (await import('node:'+id)) === querystring,
      bareCache: bare === again, sharedValues: Object.keys(querystring).every(name => querystring[name] === bare[name]),
      moduleTag: Object.prototype.toString.call(bare), nullNamespacePrototype: Object.getPrototypeOf(bare) === null,
      thenType: typeof bare.then, sharedMutation, privateBuffer };
    ++calls; snapshotView[0]++; snapshotParsed.a.push(String(calls));
    return JSON.stringify({ calls, snapshotByte: snapshotBytes[0], snapshotValues: snapshotParsed.a.length,
      snapshotIdentity: Buffer.isBuffer(snapshotBytes) && Object.getPrototypeOf(snapshotParsed) === null,
      namespaceIdentity: (await Promise.resolve(querystring)) === querystring,
      cases: querystringChecks(querystring), profile: prototypeOnlyChecks(querystring), aliases,
      commonJS: inspectCommonJS(querystring.default) });
  } catch (error) { return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } }); }
}
