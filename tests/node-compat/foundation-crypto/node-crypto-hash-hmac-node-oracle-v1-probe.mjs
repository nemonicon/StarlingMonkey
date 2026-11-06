// Host-only pinned Node oracle. Imports execute no guest or component code.
import { realpath } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

if (process.version !== 'v22.14.0' || process.execArgv.length !== 0 || process.argv.length !== 3)
  throw new Error('Exact plain Node22.14 oracle invocation required');
const input = JSON.parse(process.argv[2]);
if (await realpath(process.execPath) !== input.node.path) throw new Error('Pinned Node path');
const ns = await import(pathToFileURL(input.fixture.path));
if (Object.getPrototypeOf(ns) !== null || Object.getOwnPropertyNames(ns).join() !== 'run' || typeof ns.run !== 'function')
  throw new Error('Exact fixture module namespace');
process.stdout.write(JSON.stringify({ kind: 'host-node-identity', version: process.version,
  execPath: process.execPath, openssl: process.versions.openssl,
  hostProviderOnly: true, guestProviderProof: false }) + '\n');
for (let sequence = 1; sequence <= 3; sequence++) {
  try {
    const value = ns.run();
    if (typeof value !== 'string') throw new TypeError('Scalar string required');
    process.stdout.write(JSON.stringify({ sequence, name: 'run', kind: 'return',
      observed: { type: 'string', value } }) + '\n');
  } catch (error) {
    process.stdout.write(JSON.stringify({ sequence, name: 'run', kind: 'throw',
      error: { name: error?.name ?? null, message: error?.message ?? null, code: error?.code ?? null } }) + '\n');
    process.exitCode = 1;
    break;
  }
}
