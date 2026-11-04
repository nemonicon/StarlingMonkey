import assert from 'node:assert/strict';
import * as web from 'node:stream/web';
import {writeFile} from 'node:fs/promises';
import {observeStreams} from './cases.mjs';
assert.equal(process.version,'v22.14.0');
const exports=Object.keys(web).sort(),names=exports.filter(name=>name!=='default');
const constructors=Object.fromEntries(names.map(name=>[name,{name:web[name].name,length:web[name].length,
  globalIdentity:web[name]===globalThis[name],defaultIdentity:web[name]===web.default[name],
  staticNames:Object.getOwnPropertyNames(web[name]).sort(),prototypeNames:Object.getOwnPropertyNames(web[name].prototype).sort()}]));
const result={node:process.version,exports,defaultNames:Object.keys(web.default).sort(),constructors,
  apiPresence:{from:typeof web.ReadableStream.from,values:typeof web.ReadableStream.prototype.values,
    asyncIterator:typeof web.ReadableStream.prototype[Symbol.asyncIterator]},cases:await observeStreams(web)};
await writeFile(new URL('./node-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({node:process.version,exports:exports.length,cases:result.cases.length,errors:result.cases.filter(value=>value.error)}));
