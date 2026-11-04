// Pure metadata/text guard checks. Never import nativeHarness or a package tool.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyClassicRegistrarOracle} from './guard-source.mjs';
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../../..');
assert.equal(process.version,'v22.14.0');
const output=process.env.NODE_COMPAT_REGISTRAR_ORACLE_TEST_OUTPUT;
assert(output,'Fresh explicit output required');
const hash=x=>createHash('sha256').update(x).digest('hex');
const freeze='/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze';
const metadata=JSON.parse(await readFile(join(freeze,'normal-off.engine.wasm.build.json')));
const registrar=await readFile(join(freeze,'source/builtins/node-compat/register.cpp'),'utf8');
const common={
 tickPolicyBytes:await readFile(join(repository,'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json')),
 tickPatchBytes:await readFile(join(repository,'tests/node-compat/foundation-scheduler/taskqueue-owner-v2/starling-taskqueue-ticks.UNAPPLIED.patch')),
 classicPolicyBytes:await readFile(join(repository,'tests/node-compat/foundation-classic-streams/integration-candidate-v1/policy.json')),
 classicPatchBytes:await readFile(join(repository,'tests/node-compat/foundation-classic-streams/implementation-candidate-v1-allocation-order-amendment/native-integration.corrected.UNAPPLIED.patch'))
};
const cases=[],actual=[];
function check(name,run){run();cases.push(name);}
for(const kind of ['assert','querystring','util']){
 const oraclePath=join(repository,'tests/node-compat/foundation-'+kind+'/native-node-results.json');
 const oracleBytes=await readFile(oraclePath),oracle=JSON.parse(oracleBytes);
 const requiredNames=kind==='assert'?['assert.mjs','assert-strict.mjs','assert-factories.generated.h','export-manifest.assert.node-v22.14.0.json']:
  kind==='querystring'?['querystring.mjs','querystring-factories.generated.h','export-manifest.querystring.node-v22.14.0.json']:Object.keys(oracle.sources).filter(x=>x!=='LICENSE.util');
 const value={kind,oracle,requiredNames,registrar,metadata,proof:{...common,oracleBytes}};
 check('actual frozen342 and unchanged '+kind+' oracle',()=>actual.push(verifyClassicRegistrarOracle(value)));
 const reject=(name,mutate)=>check(kind+': '+name,()=>{const copy=structuredClone(value);mutate(copy);assert.throws(()=>verifyClassicRegistrarOracle(copy));});
 reject('changed oracle raw bytes',x=>x.proof.oracleBytes=Buffer.from('not JSON; digest must reject first'));
 reject('caller oracle registrar normalization',x=>x.oracle.registrarSha256=hash(registrar));
 reject('unknown oracle kind',x=>x.kind='other');
 reject('missing facade check',x=>x.requiredNames=x.requiredNames.slice(1));
 reject('changed captured registrar',x=>x.registrar+='\n');
 reject('wrong actual metadata registrar',x=>x.metadata.sourceManifest.find(x=>x.path==='builtins/node-compat/register.cpp').sha256=oracle.registrarSha256);
 reject('old306 manifest',x=>x.metadata.sourceManifest=x.metadata.sourceManifest.slice(0,306));
 reject('unrecognized facade source',x=>x.metadata.sourceManifest.find(x=>x.path==='builtins/node-compat/'+Object.keys(oracle.sources)[0]).sha256='0'.repeat(64));
 reject('unreviewed recipe',x=>x.metadata.buildRecipeSha256='0'.repeat(64));
 reject('diagnostic metadata',x=>x.metadata.diagnosticOnly=true);
 reject('synthetic metadata',x=>x.metadata.syntheticMetadataOnly=true);
 for(const field of ['tickPolicyBytes','tickPatchBytes','classicPolicyBytes','classicPatchBytes'])
  reject('tampered '+field,x=>x.proof[field]=Buffer.from('not valid pinned input'));
}
const report={schemaVersion:1,state:'FINITE_REGISTRAR_ANCESTRY_ACTUAL_DATA_AND_NEGATIVES_PASSED',node:process.version,passed:cases.length,failures:0,cases,
 actualDataOnly:actual,metadataPath:join(freeze,'normal-off.engine.wasm.build.json'),metadataSha256:hash(await readFile(join(freeze,'normal-off.engine.wasm.build.json'))),
 actualEngineBytesRead:false,guestOrHostOrComponentizerExecuted:false,scope:'Only exact guard source, frozen metadata/source and original three Node oracle documents. Mutated clones are negative models; no artifact admission or engine projection.'};
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,passed:report.passed}));
