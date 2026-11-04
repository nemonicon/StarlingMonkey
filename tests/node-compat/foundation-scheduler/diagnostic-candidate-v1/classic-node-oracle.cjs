'use strict';
// Ordinary exact Node22 oracle; no guest, engine or native private-code call.
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
assert.equal(process.version,'v22.14.0');
const source=fs.readFileSync(path.join(__dirname,'classic-bootstrap.fixture.js'),'utf8');
const input="import('starling:test-internal-ticks')";
assert.equal(source.split(input).length,2);
// Only the unavailable diagnostic-module capture is adapted to the actual
// Node public callable; it still resolves during a Promise job in step one.
const adapted=source.replace(input,'Promise.resolve({nextTick:process.nextTick})');
assert.equal(vm.runInThisContext(adapted,{filename:'classic-node-bootstrap.js'}),0);
setImmediate(()=>{
 const completion=vm.runInThisContext('smSeed()',{filename:'classic-node-second-eval.js'});
 assert.equal(typeof completion.run,'function');
 setImmediate(()=>{
  const observed=JSON.parse(completion.run());
  const expected=['tick-first','nested-tick','promise-first','microtask','promise-from-tick','nested-promise','tick-from-promise'];
  assert.deepEqual(observed.trace,expected);assert.deepEqual(observed.globalObjectProperties,[false,false,false]);
  process.stdout.write(JSON.stringify({schemaVersion:1,node:process.version,
   sourceSha256:crypto.createHash('sha256').update(source).digest('hex'),adaptedSha256:crypto.createHash('sha256').update(adapted).digest('hex'),
   observed,expected,scope:'Step-two classic script evaluated synchronously within a real Node task after the step-one capture job drained; not first-ever startup priority',guestExecuted:false})+'\n');
 });
});
