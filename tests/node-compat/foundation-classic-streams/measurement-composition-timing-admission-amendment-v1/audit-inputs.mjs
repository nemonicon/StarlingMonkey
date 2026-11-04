// Only Node built-ins load before exact amendment/parent/collector authentication.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,relative,isAbsolute,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
const worker=process.argv[2]==='--worker'||process.argv[2]==='--calibrate',ownSha=process.argv[worker?3:2];assert(/^[0-9a-f]{64}$/.test(ownSha??''));
async function check(root,digest){const info=await lstat(join(root,'index.json'));assert(info.isFile()&&!info.isSymbolicLink());const raw=await readFile(join(root,'index.json'));assert.equal(hash(raw),digest);const index=JSON.parse(raw);assert.equal(index.schemaVersion,1);const seen=new Set();for(const row of index.files){const path=resolve(root,row.path),name=relative(root,path);assert(name!==''&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name)&&!seen.has(name));seen.add(name);const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink());const bytes=await readFile(path);assert.equal(hash(bytes),row.sha256);assert.equal(bytes.length,row.bytes);}}
await check(here,ownSha);
await check(resolve(here,'../measurement-execution-activated-v2'),'1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612');
await check(resolve(here,'../measurement-stock-composition-candidate-v1'),'257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da');
await import('./audit-body.mjs');
