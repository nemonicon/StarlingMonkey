import assert from 'node:assert/strict';
import * as web from 'node:stream/web';
import {writeFile} from 'node:fs/promises';
import {codecCases,cancellationCases,constructorCases} from './codec-cases.mjs';
assert.equal(process.version,'v22.14.0');
const result={node:process.version,constructorCases:constructorCases(web),codecCases:await codecCases(web),cancellationCases:await cancellationCases(web)};
await writeFile(new URL('./codec-node-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({node:process.version,constructors:result.constructorCases.length,codecs:result.codecCases.length,cancellations:result.cancellationCases.length}));
