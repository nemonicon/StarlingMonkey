import assert from 'node:assert/strict';
import * as web from 'node:stream/web';
import {writeFile} from 'node:fs/promises';
import {iterationCases} from './cases.mjs';
assert.equal(process.version,'v22.14.0');
const cases=await iterationCases(web);
await writeFile(new URL('./node-results.json',import.meta.url),JSON.stringify({node:process.version,cases},null,2)+'\n');
console.log(JSON.stringify({node:process.version,cases:cases.length}));
