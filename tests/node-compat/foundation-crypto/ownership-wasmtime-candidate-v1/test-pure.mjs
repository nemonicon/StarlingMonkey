// Pure transport/counterexample/data only. No process helper or guest is called.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateArgv,parseScalarStringOutput,checkWholeRecord,checkOracle,argvAudit} from './protocol.mjs';
import {waveString} from '../../foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs';
import {authorityModel,environment} from './guard.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));let checks=0;
const ck=(v,m)=>{assert(v,m);checks++;},refuse=fn=>{assert.throws(fn);checks++;};
const refs=JSON.parse(await readFile(join(HERE,'references.json'))),wrapper=JSON.parse(await readFile(refs.normalWrapper.path)),oracle=JSON.parse(await readFile(refs.nodeOracle.path)),record=JSON.parse(wrapper.value);
ck(checkOracle(oracle),'Actual retained Node oracle only');ck(checkWholeRecord(record,oracle,wrapper),'Actual complete normal fresh-wrapper data only');
const argv=validateArgv(refs.artifacts.component);assert.deepEqual(argv,['run','--invoke','validate()',refs.artifacts.component.path]);checks++;
ck(!argv.includes('validate')&&!argv.some(a=>a.includes('validate([])')),'literal zero-argument WAVE invocation; no codec arity helper');
const raw=new TextEncoder().encode(waveString(wrapper.value)+'\n');ck(parseScalarStringOutput({stdoutBytes:raw,rawDurablyRetained:true})===wrapper.value,'Full existing wrapper pure WAVE roundtrip without normalization');
for(const value of ['0\n','{}\n','("x", "y")\n','"x"','"x"\n\n','"\\u0000"\n','\uFEFF"x"\n'])refuse(()=>parseScalarStringOutput({stdoutBytes:new TextEncoder().encode(value),rawDurablyRetained:true}));
refuse(()=>parseScalarStringOutput({stdoutBytes:raw,rawDurablyRetained:false}));
refuse(()=>parseScalarStringOutput({stdoutBytes:new Uint8Array([34,0xff,34,10]),rawDurablyRetained:true}));
for(const edit of [r=>r.records.pop(),r=>r.records[0].result.operations.firstSignatureHex='00'.repeat(32),r=>r.records[2].result.jwk.inputAfterHex='00'.repeat(24),r=>r.records[3].result.signConversionReads.algorithmName=1,r=>r.after.state.rawRetained=true,r=>r.records[0].counters.keyImportsFulfilled=0,r=>r.records[3].result.signRefusal.error.message='changed']){
 const r=structuredClone(record);edit(r);refuse(()=>checkWholeRecord(r,oracle,wrapper));
}
for(const edit of [r=>r.tagHex='00'.repeat(32),r=>r.keys[0].extractable=true,r=>r.keys[1].invalid=true]){const r=structuredClone(oracle);edit(r);refuse(()=>checkWholeRecord(record,r,wrapper));}
refuse(()=>validateArgv({...refs.artifacts.component,sha256:'a'.repeat(64)}));refuse(()=>validateArgv({...refs.artifacts.component,bytes:0}));
ck(argvAudit(refs.wasmtime.path,argv,{PATH:'/usr/bin:/bin'}).strictlyBelowArgMax,'Small actual final argv arithmetic, no spawn proof');
ck(environment({}),'No override domain');for(const key of ['WASMTIME_CONFIG_FILE','RUST_LOG','NODE_OPTIONS','DYLD_INSERT_LIBRARIES'])refuse(()=>environment({[key]:'unreviewed'}));
const template=JSON.parse(await readFile(join(HERE,'future-root-authority.template.json')));refuse(()=>authorityModel(template,'a'.repeat(64)));ck(template.wasmtimeValidateAllowed===false&&template.sourceIndexSha256===null&&template.sourceIndependentReview===null&&template.externalController===null,'Source peer/action/controller remain unissued');
const run=await readFile(join(HERE,'run.mjs'),'utf8');ck(run.indexOf('checkOwnedTerminal(terminal)')<run.indexOf('parseScalarStringOutput(')&&run.indexOf('parseScalarStringOutput(')<run.indexOf('JSON.parse(value)'),'Existing full raw+terminal gate before WAVE and JSON checks');
ck(run.indexOf("mkdir(join(out.root,'processes')")<run.indexOf('await runOwnedCommand('),'required output directory before untouched lifecycle');
ck(!run.includes('nodeOracle(')&&!run.includes('loadSession(')&&!run.includes('invocation('),'No new oracle/generated loader/codec invocation action');
console.log(JSON.stringify({schemaVersion:1,state:'CRYPTO_STOCK_WT_PURE_DATA_TRANSPORT_CHECKS_PASSED',checks,actualNormalDataOnly:true,wasmtimeProcessHelperGuestCryptoActionsInvoked:false}));
