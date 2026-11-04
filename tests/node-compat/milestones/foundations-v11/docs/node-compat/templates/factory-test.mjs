// Check generated C++ string expressions before compiling the embedding.
// Usage: pinned-node factory-test.mjs /absolute/node-profile-factories.generated.h
import { readFile } from 'node:fs/promises';
import { runInThisContext } from 'node:vm';
import assert from 'node:assert/strict';
import * as kernel from './reference-kernel.mjs';
assert.equal(process.version, 'v22.14.0');
const text = await readFile(process.argv[2], 'utf8');
function factory(name) {
  const line = text.split('\n').find(line => line.startsWith(`static constexpr const char ${name}[] = `));
  assert.ok(line, `missing ${name}`);
  const literal = line.slice(line.indexOf(' = ') + 3, -1);
  return runInThisContext(JSON.parse(literal));
}
const buffer = factory('kBufferFactorySource')(kernel);
assert.equal(buffer.Buffer.from('hello').toString('hex'), '68656c6c6f');
assert.equal(buffer.Buffer, buffer.default.Buffer);
const child = factory('kChildProcessFactorySource')();
assert.equal(child.spawn, child.default.spawn);
assert.throws(() => child.spawn(), { code: 'ERR_SM_NODE_UNSUPPORTED' });
console.log('PASS generated Buffer/child-process factory expressions (native C++ uncompiled)');
