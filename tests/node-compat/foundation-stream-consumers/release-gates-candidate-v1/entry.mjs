// Supported future caller: authenticate every family byte using Node primitives
// BEFORE importing any owned integrity helper, owner preflight or runtime driver.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
const expected=process.env.NODE_COMPAT_RELEASE_FAMILY_INDEX_SHA256;assert(/^[0-9a-f]{64}$/.test(expected??''),'Explicit independent-reviewed generated index required');
const indexPath=join(here,'index.json'),info=await lstat(indexPath);assert(info.isFile()&&!info.isSymbolicLink());
const raw=await readFile(indexPath);assert.equal(hash(raw),expected);const index=JSON.parse(raw),seen=new Set();
for(const row of index.files){assert(typeof row.path==='string'&&!row.path.startsWith('/')&&!row.path.includes('\\')&&!row.path.includes('\0'));assert(row.path.split('/').every(part=>part&&part!=='.'&&part!=='..'&&Buffer.byteLength(part)<=255));assert(!seen.has(row.path));seen.add(row.path);let path=here;for(const part of row.path.split('/')){path=join(path,part);assert(!(await lstat(path)).isSymbolicLink());}const stat=await lstat(path);assert(stat.isFile());const value=await readFile(path);assert.equal(value.length,row.bytes);assert.equal(hash(value),row.sha256,path);}
assert(seen.has('entry.mjs')&&seen.has('native-preflight.mjs')&&seen.has('physical.mjs')&&seen.has('contracts.mjs'));
const mode=process.argv[2];assert(['run','selected','preflight'].includes(mode));process.argv.splice(2,1);
if(mode==='run')await import('./run-gates.mjs');
else if(mode==='selected')await import('./run-selected.mjs');
else{assert.equal(process.argv.length,3);const {validationPreflight}=await import('./native-preflight.mjs');const value=await validationPreflight({variant:process.argv[2]});await value.recheck();console.log(JSON.stringify({state:'READ_ONLY_GENUINE355_PREFLIGHT_PASSED',variant:value.variant,engineSha256:value.pin.engineSha256,sourceFiles:355,operationalAdmission:false,guestExecuted:false}));}
