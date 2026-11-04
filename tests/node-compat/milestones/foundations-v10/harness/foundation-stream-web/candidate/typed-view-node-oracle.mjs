import assert from 'node:assert/strict';
import * as web from 'node:stream/web';
import {writeFile} from 'node:fs/promises';
import {typedViewCases} from './typed-view-cases.mjs';
assert.equal(process.version,'v22.14.0');
const result={node:process.version,cases:await typedViewCases(web)};
await writeFile(new URL('./typed-view-node-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({node:process.version,cases:result.cases.length}));
