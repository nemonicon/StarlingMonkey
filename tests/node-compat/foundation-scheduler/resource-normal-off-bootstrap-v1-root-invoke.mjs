// Genuine read-only harness API plus an explicit full-frame recheck.
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const descriptor=JSON.parse(process.argv[2]);
const bytes=await readFile(descriptor.path);
if(bytes.length!==descriptor.bytes||createHash('sha256').update(bytes).digest('hex')!==descriptor.sha256)throw Error('Root config changed');
const {resourceBootstrapPreflight}=await import('./resource-pin-tooling-candidate-v1/bootstrap.mjs');
const actual=await resourceBootstrapPreflight({configDescriptor:descriptor});
await actual.recheck();
const {recheck,...wholeDataFrame}=actual;
if(typeof recheck!=='function')throw Error('Missing captured recheck');
if(!(await readFile(descriptor.path)).equals(bytes))throw Error('Root config changed after bootstrap');
console.log(JSON.stringify(wholeDataFrame));
