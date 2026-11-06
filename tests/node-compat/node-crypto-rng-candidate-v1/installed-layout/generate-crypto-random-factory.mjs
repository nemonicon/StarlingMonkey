// Host Source generation only. Never calls a crypto fixture or RNG provider.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validateManifest} from './validate-manifest.mjs';
const names=['crypto-rng.mjs','crypto-facade.mjs','export-manifest.crypto-random.node-v22.14.0.json'],source={};
for(const name of names)source[name]=await readFile(new URL(name,import.meta.url),'utf8');
const manifest=JSON.parse(source[names[2]]);validateManifest(manifest,JSON.parse(await readFile(new URL('manifest.schema.json',import.meta.url),'utf8')));
const random=source[names[0]].replace('export function createRandomOperations','function createRandomOperations');
const facade=source[names[1]].replace("import {createRandomOperations} from './crypto-rng.mjs';\n",'').replace('export function createCryptoModule','function createCryptoModule');
if(/^\s*(?:import|export)\b/m.test(random+'\n'+facade))throw Error('Unexpected factory syntax');
const rendered='(() => {\n'+random+'\n'+facade+'\nreturn createCryptoModule;\n})()';
if(rendered.includes(')SM_NODE_CRYPTO"'))throw Error('Delimiter collision');
const hash=createHash('sha256');for(const name of names)hash.update(name+'\0'+source[name]+'\0');
const output='// Generated canonical Source SHA256 '+hash.digest('hex')+'\n#pragma once\nstatic constexpr const char *kCryptoHashHmacFactorySource = R"SM_NODE_CRYPTO('+rendered+')SM_NODE_CRYPTO";\n';
const dest=new URL('crypto-factory.generated.h',import.meta.url);if(process.argv.includes('--check')){if(await readFile(dest,'utf8')!==output)throw Error('Stale crypto random factory');}else await writeFile(dest,output);
console.log('PASS genuine full-name crypto factory with optional RuntimeOnly RNG');
