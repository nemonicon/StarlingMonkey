// Finite parent-index data only. This module reads no files and admits no engine.
import assert from 'node:assert/strict';
export function selectDependencyIndex(document,key){
  assert(document&&typeof document==='object'&&!Array.isArray(document));
  assert.equal(document.schemaVersion,1);
  assert.equal(document.state,'REVIEWED_SEALED_PARENT_INDICES_V1','Parent packet indices are not reviewed/sealed');
  assert(['commonIndexSha256','offIndexSha256'].includes(key));
  const value=document[key];
  assert(typeof value==='string'&&/^[a-f0-9]{64}$/.test(value)&&!/^0+$/.test(value),'Missing exact sealed parent index: '+key);
  return value;
}
