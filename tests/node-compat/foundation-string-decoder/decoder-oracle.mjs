import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {decoderCases} from './decoder-cases.mjs';
assert.equal(process.version,'v22.14.0');
const results=decoderCases();
assert(results.length>=40);
await writeFile(new URL('./decoder-oracle-results.json',import.meta.url),JSON.stringify({node:process.version,
  scope:'SAFE Node-only ordinary API oracle; no old-native decoder execution',results},null,2)+'\n');
console.log(JSON.stringify({node:process.version,cases:results.length}));
