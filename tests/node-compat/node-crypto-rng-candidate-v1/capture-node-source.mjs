// Source data only; no exported crypto function or workload invocation.
import {writeFile} from 'node:fs/promises';
if(process.version!=='v22.14.0')throw Error('Pinned Node required');
const sources=process.binding('natives');
for(const [key,name]of [['internal/crypto/random','node22-internal-crypto-random.js'],['crypto','node22-crypto.js']])await writeFile(new URL(name,import.meta.url),sources[key],{flag:'wx'});
console.log('Captured actual Node22 RNG primary sources without calling crypto exports');
