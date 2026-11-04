// Pure inventory check. No source reads, bundling, provider or scheduler calls.
import assert from 'node:assert/strict';
import {basename,dirname,isAbsolute} from 'node:path';
const names=['entry.mjs','stock-provider.mjs','workload.mjs'];
const sha=/^[0-9a-f]{64}$/;
export function priorStockModules(previous){
 assert(previous&&typeof previous==='object'&&!Array.isArray(previous));
 assert(Array.isArray(previous.modules)&&previous.modules.length===102);
 assert(previous.modules.every(id=>typeof id==='string'));
 assert.equal(new Set(previous.modules).size,102);
 assert(Array.isArray(previous.physicalSources));
 assert(Array.isArray(previous.sourceBeforeAfter)&&previous.sourceBeforeAfter.length===3);
 const rows=previous.sourceBeforeAfter;
 for(const row of rows){
  assert(row&&typeof row==='object'&&!Array.isArray(row));
  assert.deepEqual(Object.keys(row).sort(),['bytes','path','sha256']);
  assert(typeof row.path==='string'&&isAbsolute(row.path)&&!row.path.includes('\0'));
  assert(sha.test(row.sha256)&&Number.isSafeInteger(row.bytes)&&row.bytes>=0);
  assert.equal(previous.modules.filter(id=>id===row.path).length,1);
  const physical=previous.physicalSources.filter(item=>item.path===row.path);
  assert.equal(physical.length,1);assert.deepEqual(physical[0],row);
 }
 assert.deepEqual(rows.map(row=>basename(row.path)).sort(),names);
 assert.equal(new Set(rows.map(row=>dirname(row.path))).size,1);
 const own=new Set(rows.map(row=>row.path));assert.equal(own.size,3);
 const prior=previous.modules.filter(id=>!own.has(id));
 assert.equal(prior.length,99);
 return prior;
}
