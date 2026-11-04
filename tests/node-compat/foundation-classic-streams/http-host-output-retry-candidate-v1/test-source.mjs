// Pure source/options/reverse checks. No host wrapper/body is imported.
import assert from 'node:assert/strict';
import {readFile,writeFile,lstat,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {requireSupportedFixtureOptions} from './verify-retry.mjs';
const here=dirname(fileURLToPath(import.meta.url)),old=resolve(here,'../classic-http-candidate-v1'),hash=b=>createHash('sha256').update(b).digest('hex');
const checks=[];const pass=name=>checks.push(name);
for(const value of [undefined,'','0','true']){requireSupportedFixtureOptions({NODE_COMPAT_HTTP_REQUIRE_INTRINSICS:value});pass('fixture option '+String(value)+' retains original optional-assertion behavior');}
assert.throws(()=>requireSupportedFixtureOptions({NODE_COMPAT_HTTP_REQUIRE_INTRINSICS:'1'}),/no optional intrinsics report/);pass('incompatible extra assertion rejected by pure function');
const entry=await readFile(join(here,'run-http-wasmtime.mjs'),'utf8');
assert(entry.indexOf('requireSupportedFixtureOptions(process.env);')<entry.indexOf("await import('./run-http-wasmtime-body.mjs')"));
assert(entry.indexOf('await verifyRetrySource()')<entry.indexOf("await import('./run-http-wasmtime-body.mjs')"));
assert(entry.includes('await source.recheck();'));pass('approved entry rejects flag and authenticates source before any host body import; source rechecked after');
const proof=JSON.parse(await readFile(join(here,'transformation-proof.json')));
assert.equal(proof.records.length,2);
for(const row of proof.records){const before=await readFile(join(old,row.original)),after=await readFile(join(here,row.target));assert.equal(hash(before),row.beforeSha256);assert.equal(hash(after),row.afterSha256);let text=after.toString();
  for(const edit of [...row.edits].reverse()){assert.equal(text.split(edit.new).length-1,edit.occurrences);text=text.replaceAll(edit.new,edit.old);}assert.equal(text,before.toString());pass(row.target+' reverses exactly; checks unchanged');}
const host=await readFile(join(here,'run-http-wasmtime-body.mjs'),'utf8');assert(host.includes("'http-joint/wasmtime-v2'"));assert(!host.includes('wasmtime-v1'));assert(host.includes('../classic-http-candidate-v1/capability/hosts/test-wasmtime-http.mjs'));pass('fresh fixed Wasmtime-v2 directory and unchanged original host implementation');
const audit=await readFile(join(here,'audit-http-body.mjs'),'utf8');assert.equal(audit.split('http-joint/wasmtime-v2/').length-1,2);assert(!audit.includes('wasmtime-v1'));assert(audit.includes('validateCombinedHosts({audit:ready.audit,wasmtime,wash})'));pass('audit uses v2 report and completion paths with original full validators');
const phase=await readFile(resolve(here,'../production-adoption-v1/http-component-phase-root-review-v1.json'));assert.equal(hash(phase),'eb1caa1168f57f135c1b38c924ef1ce99305aa34688419edd5847e242a5f9c29');assert.equal(JSON.parse(phase).component.componentSha256,'25eb1a1c7343519318ffc5a4519bc1dbd4cc1c23755a6b8fcc3bab479ffb6c7d');pass('original reviewed phase and component tuple unchanged');
assert.equal(JSON.parse(await readFile(join(old,'capability/component-pins.json'))).component,null);pass('original local null component pin remains unchanged');
const manifest=await readFile(join(here,'input-freeze.json')),compiled=await readFile(join(here,'verify-retry.mjs'),'utf8');assert(compiled.includes("INPUTS_SHA='"+hash(manifest)+"'"));assert(compiled.indexOf("assert.equal(hash(raw),INPUTS_SHA")<compiled.indexOf('JSON.parse(raw)'));pass('own source seal digest fixed before parsing rows');
const output=resolve(process.env.NODE_COMPAT_HTTP_RETRY_SOURCE_TEST_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Choose a fresh source test output');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(dirname(output),{recursive:true});const result={schemaVersion:1,state:'HTTP_FRESH_OUTPUT_RETRY_SOURCE_CHECKS_PASSED',checks:checks.length,passed:checks.length,observations:checks,
  componentOrGuestOrHostExecuted:false,bodyOrPreflightImported:false,reviewedPhaseSha256:hash(phase),ownManifestSha256:hash(manifest)};
await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,checks:checks.length,output}));
