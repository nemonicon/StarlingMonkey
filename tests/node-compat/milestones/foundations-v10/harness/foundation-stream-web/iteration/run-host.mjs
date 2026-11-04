import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {fixtureRecord} from '../candidate/fixture-record.mjs';
import {createStreamWebModule} from '../candidate/factory.mjs';
import {installReadableIteration} from './algorithms.mjs';
import {iterationCases} from './cases.mjs';
import {capturedIntrinsicCases} from './intrinsics.mjs';
assert.equal(process.version,'v22.14.0');
const fixture=await fixtureRecord();let result;
try{
  const web=createStreamWebModule(fixture.record);installReadableIteration(fixture.record);
  const actual=await iterationCases(web),expected=JSON.parse(await readFile(new URL('./node-results.json',import.meta.url))).cases;
  await writeFile(new URL('./host-observations.json',import.meta.url),JSON.stringify(actual,null,2)+'\n');
  assert.deepEqual(JSON.parse(JSON.stringify(actual)),expected);
  result={node:process.version,cases:actual.length,nodeExact:true,nativeConstructorIdentity:web.ReadableStream===fixture.record.ReadableStream,
    intrinsics:await capturedIntrinsicCases(fixture.record)};
}finally{const restored=fixture.restore();assert(restored);if(result)result.originalDescriptorsRestored=restored;}
await writeFile(new URL('./host-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
