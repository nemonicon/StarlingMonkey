// Finite future artifact contract. Synthetic source models never satisfy it.
import assert from 'node:assert/strict';
import {isAbsolute,resolve,join} from 'node:path';
const SHA=/^[0-9a-f]{64}$/;
export const variants=Object.freeze(['normal-off','normal-runtime','gc-off','disabled-off']);
export function selectClassicPin(document,{variant='normal-off',recipeSha256}={}){
  assert(variants.includes(variant),'Unknown classic engine variant');
  assert.equal(document.schemaVersion,1);
  assert.equal(document.state,'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1','Classic engine pins remain unconfigured');
  assert.deepEqual(Object.keys(document.variants).sort(),[...variants].sort());
  const pin=document.variants[variant];assert(pin&&typeof pin==='object','No reviewed actual classic engine artifact');
  assert.equal(pin.state,'reviewed-real-classic-production-freeze');
  assert.equal(pin.variant,variant);assert.equal(pin.sourceFiles,342);assert.equal(pin.recipeSha256,recipeSha256);
  assert.equal(pin.gcStress,variant==='gc-off');assert.equal(pin.entropyPolicy,variant==='normal-runtime'?'runtime-only':'off');
  assert.equal(pin.classicStreamsEnabled,variant!=='disabled-off');
  for(const name of ['engineSha256','receiptSha256','cmakeCacheSha256','compileCommandsSha256','freezeReceiptSha256','parentEmbeddingCommandSha256'])assert(SHA.test(pin[name]),name);
  assert(Number.isSafeInteger(pin.engineBytes)&&pin.engineBytes>0);
  for(const key of ['freezeRoot','enginePath','sourceRoot','componentizeSourceRoot','cachePath','commandsPath','recipePath','freezeReceiptPath','parentEmbeddingCommandPath']){
    assert(typeof pin[key]==='string'&&!pin[key].includes('\0')&&isAbsolute(pin[key])&&resolve(pin[key])===pin[key],key);
  }
  assert.equal(pin.sourceRoot,join(pin.freezeRoot,'source'));assert.equal(pin.componentizeSourceRoot,join(pin.freezeRoot,'componentize-source'));
  const seen=new Set();assert(Array.isArray(pin.frozenFiles)&&pin.frozenFiles.length>=350);
  for(const row of pin.frozenFiles){assert(typeof row.path==='string'&&isAbsolute(row.path)&&resolve(row.path)===row.path&&!row.path.includes('\0'));assert(!seen.has(row.path));seen.add(row.path);assert(SHA.test(row.sha256)&&Number.isSafeInteger(row.bytes)&&row.bytes>=0);}
  for(const key of ['enginePath','cachePath','commandsPath','recipePath','parentEmbeddingCommandPath'])assert(seen.has(pin[key]),key+' is absent from frozen inventory');
  assert(seen.has(pin.enginePath+'.build.json'));
  return Object.freeze(structuredClone(pin));
}
