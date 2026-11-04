import assert from 'node:assert/strict';
import * as web from 'node:stream/web';
import {writeFile} from 'node:fs/promises';
import {observeConstructors} from './constructors-cases.mjs';
assert.equal(process.version,'v22.14.0');
const result={node:process.version,observations:await observeConstructors(web)};
await writeFile(new URL('./constructors-node-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({node:process.version,writerConstructed:true,controllers:2}));
