// New read-only API. Importing this module launches nothing. No generated code.
import assert from 'node:assert/strict';
import {readFile,lstat,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url)),run=promisify(execFile),sha=b=>createHash('sha256').update(b).digest('hex');
const NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',NODE_SHA='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0';
async function parentNode(){assert.equal(await realpath(process.execPath),NODE);const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(NODE)){h.update(b);bytes+=b.length;}assert.equal(bytes,108619024);assert.equal(h.digest('hex'),NODE_SHA);}
function deepFreeze(v){if(v&&typeof v==='object'){for(const x of Object.values(v))deepFreeze(x);Object.freeze(v);}return v;}
async function regular(row){assert(row&&typeof row.path==='string'&&/^[a-f0-9]{64}$/.test(row.sha256)&&Number.isSafeInteger(row.bytes));const s=await lstat(row.path);assert(s.isFile()&&!s.isSymbolicLink());const b=await readFile(row.path);assert.equal(b.length,row.bytes);assert.equal(sha(b),row.sha256);return b;}
export async function cryptoOwnerGcBootstrapPreflight({configDescriptor}={}){
 // NULL refuses before a helper, pin, native artifact or output is touched.
 const captured=Object.freeze({...configDescriptor});const config=JSON.parse(await regular(captured));
 const ix=Object.freeze({...config.sourceIndex});assert.equal(ix.path,join(HERE,'index.json'));const index=JSON.parse(await regular(ix));
 const rows=index.files.map(r=>Object.freeze({path:join(HERE,r.path),sha256:r.sha256,bytes:r.bytes}));
 const root=Object.freeze({...config.rootAuthority});assert(root.path);await regular(root);
 async function own(){await regular(captured);await regular(ix);await regular(root);for(const r of rows)await regular(r);await parentNode();}
 async function execute(){await own();assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE'])assert(!process.env[k]);const child=await run('python3',[join(HERE,'bootstrap.py'),JSON.stringify(captured)],{timeout:120000,maxBuffer:16*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});const v=JSON.parse(child.stdout);assert.equal(v.state,'ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_PASSED_V1');assert.equal(v.sourceIndexSha256,ix.sha256);assert.equal(v.variant,'gc-off');assert.equal(v.metadata.gcStress,true);assert.equal(v.configuredSourceRoot,'/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source');assert.equal(v.sourceRoot,'/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze/source');assert.equal(v.operationalAdmission,false);assert.equal(v.guestExecuted,false);return v;}
 const actual=await execute();const stable=JSON.stringify(actual);
 async function recheck(){assert.equal(JSON.stringify(await execute()),stable,'Actual full GC native frame changed');await own();}
 await recheck();return Object.freeze({...deepFreeze(actual),recheck});
}
