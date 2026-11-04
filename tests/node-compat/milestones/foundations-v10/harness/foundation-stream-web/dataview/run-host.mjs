import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {fixtureRecord} from '../candidate/fixture-record.mjs';
import {createStreamWebModule} from '../candidate/factory.mjs';
import {installDataViewBYOB} from './adapter.mjs';
import {dataViewCases} from './cases.mjs';
import {policyCases,capturedIntrinsicCases} from './policy.mjs';
import {typedViewCases} from '../candidate/typed-view-cases.mjs';
assert.equal(process.version,'v22.14.0');
const fixture=await fixtureRecord();let report;
try{
  const nativeRead=fixture.record.ReadableStreamBYOBReader.prototype.read;
  const web=createStreamWebModule(fixture.record);installDataViewBYOB(fixture.record,nativeRead);
  const actual=await dataViewCases(web,fixture.track),expected=JSON.parse(await readFile(new URL('./node-results.json',import.meta.url))).cases;
  await writeFile(new URL('./host-observations.json',import.meta.url),JSON.stringify(actual,null,2)+'\n');
  assert.deepEqual(JSON.parse(JSON.stringify(actual)),expected);
  const typedViews=await typedViewCases(web,fixture.track);
  assert.deepEqual(typedViews,JSON.parse(await readFile(new URL('../candidate/typed-view-node-results.json',import.meta.url))).cases);
  report={node:process.version,cases:actual.length,nodeExact:true,nativeReaderIdentity:web.ReadableStreamBYOBReader===fixture.record.ReadableStreamBYOBReader,
    typedViews:typedViews.length,policies:await policyCases(web,fixture.track),intrinsics:await capturedIntrinsicCases(web,fixture.track)};
}finally{const restored=fixture.restore();assert(restored);if(report)report.originalDescriptorsRestored=restored;}
await writeFile(new URL('./host-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
