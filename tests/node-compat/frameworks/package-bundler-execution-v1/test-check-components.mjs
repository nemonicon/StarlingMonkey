// Synthetic counterexamples mutate retained DATA in memory only. No suite runs.
// node test-check-components.mjs [COMPLETE_MATRIX_RESULTS]
import assert from 'node:assert/strict';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadMatrix,auditMatrices,comparisonExitCode} from './check-components.mjs';

export async function runTests(input){
const path=resolve(input??join(dirname(fileURLToPath(import.meta.url)),'results-post-push-v2/results.json'));
const actual=await loadMatrix(path),tests=[];
assert.equal(comparisonExitCode(auditMatrices(actual.report,actual.report,{baseline:actual.evidence,current:actual.evidence})),0,'Actual retained DATA must be a complete baseline');
function sync(x,id){
  const row=x.report.cases.find(r=>r.id===id);
  x.evidence.cases[id].worker=structuredClone(row.worker);
  x.evidence.commands['wasm-'+id].stdoutValue={case:id,stage:row.worker.stage,status:row.worker.status,output:row.worker.output};
}
function test(name,mutate,expected,kind){
  const before=structuredClone(actual),after=structuredClone(actual);mutate(after);
  const result=auditMatrices(before.report,after.report,{baseline:before.evidence,current:after.evidence});
  assert.equal(comparisonExitCode(result),expected,name);
  if(kind)assert(result.regressions.some(r=>r.kind===kind)||result.changedBlockers.some(r=>r.kind===kind)||result.improvements.some(r=>r.kind===kind),name+' expected classification '+kind);
  tests.push({name,expectedExitCode:expected,passed:true});
}
test('unchanged complete matrix retains seven guest blockers',()=>{},0);
test('missing case rejects',x=>x.report.cases.pop(),1,'exact-ten-case-coverage-required');
test('duplicate case rejects',x=>x.report.cases[9]=structuredClone(x.report.cases[8]),1,'unknown-or-duplicate-case');
test('unknown added case rejects',x=>x.report.cases.push({id:'unbaselined'}),1,'unknown-or-duplicate-case');
test('Node version mismatch rejects',x=>x.report.node='v24.0.0',1,'suite-schema-or-recorded-version-mismatch');
test('bundler mismatch rejects',x=>x.report.bundler='packages-v1',1,'bundler-mismatch');
test('selected interface widening rejects',x=>x.report.selectedInterfaces=['wasi:clocks/monotonic-clock@0.2.10'],1,'interface-or-profile-scope-mismatch');
test('missing executed source capture rejects',x=>x.evidence.sourcesVerified=false,1,'missing-executed-source-copies');
test('missing raw evidence rejects',x=>delete x.evidence.cases['react-element'].jcoRaw,1,'typed-or-parsed-return-mismatch');
test('missing second retained string rejects',x=>x.evidence.cases['react-element'].jcoStrings.pop(),1,'missing-or-different-whole-return');
test('changed retained whole string rejects',x=>x.evidence.cases['react-element'].jcoStrings[1]+=' ',1,'missing-or-different-whole-return');
test('fresh WAVE decode disagreement rejects',x=>x.evidence.cases['react-element'].waveDecoded+=' ',1,'missing-or-different-whole-return');
test('Node/guest return disagreement rejects',x=>{const r=x.report.cases[2];r.nodeControl.value='{"different":true}';x.evidence.commands['node-react-element'].stdoutValue=structuredClone(r.nodeControl);},1,'complete-node-jco-wasmtime-differential-mismatch');
test('unclean owned terminal rejects',x=>{const t=x.report.commands.find(r=>r.name==='wasm-react-element');t.ownedGroupGone=false;x.evidence.commands[t.name].terminal=structuredClone(t);},1,'unclean-or-inconsistent-outer-terminal');
test('missing command rejects',x=>x.report.commands.pop(),1,'exact-seventeen-commands-required');
test('unknown command rejects',x=>x.report.commands.push({name:'other'}),1,'unknown-or-duplicate-command');
test('copied worker mismatch rejects',x=>x.evidence.cases['react-element'].worker.status='failed',1,'missing-or-inconsistent-worker-report');
test('unknown emitted import rejects',x=>x.evidence.cases['react-element'].audit.emittedImports=['wasi:io/streams@0.2.10'],1,'recorded-component-interface-mismatch');
test('different WIT arity rejects',x=>x.evidence.cases['react-element'].wit='package root:component; world root { export run: func(input: string) -> string; }',1,'recorded-component-interface-mismatch');
test('different transpile export rejects',x=>x.evidence.cases['react-element'].transpile.exports.push(['extra','function']),1,'recorded-component-interface-mismatch');
test('recorded native identity mismatch rejects',x=>{x.report.cases[2].worker.engine.sha256='0'.repeat(64);sync(x,'react-element');},1,'accepted-engine-or-metadata-mismatch');
test('recorded tool identity mismatch rejects',x=>x.evidence.cases['react-element'].tooling.packages.rolldown.sha256='0'.repeat(64),1,'recorded-node-or-tool-package-mismatch');
test('legacy extensionless Node resolution is incomplete',x=>{const r=x.report.cases.find(r=>r.id==='next-server');r.nodeControl={status:'threw',name:'Error',code:'ERR_MODULE_NOT_FOUND',message:'Cannot find next/server'};x.evidence.commands['node-next-server'].stdoutValue=structuredClone(r.nodeControl);delete r.nodeControlResolution;},1,'node-control-resolution-failed');
test('changed guest blocker requires review',x=>{const r=x.report.cases.find(r=>r.id==='next-server');r.worker.failures[0].message='different unsupported operation';sync(x,r.id);},2,'worker-blocker-changed');
test('changed failure is not success even with finished observations',x=>{const r=x.report.cases.find(r=>r.id==='react-dom-edge');r.worker.failures[0].message='another trap';sync(x,r.id);},2,'worker-blocker-changed');
test('arbitrary stable Node refusal is not the required oracle',x=>{const r=x.report.cases.find(r=>r.id==='next-headers');r.nodeControl.message='different outside-request error';x.evidence.commands['node-next-headers'].stdoutValue=structuredClone(r.nodeControl);},1,'finite-node-control-outcome-mismatch');
test('lost positive is a regression',x=>{
  const r=x.report.cases[2],c=x.evidence.cases[r.id];r.worker.status='failed';r.worker.jco.passed=false;r.worker.failures=[{stage:'jco-runtime',message:'synthetic failure'}];sync(x,r.id);x.report.requiredPositivePassed=false;
},1,'successful-case-regressed');
test('true former blocker success is improvement after complete evidence',x=>{
  const r=x.report.cases.find(r=>r.id==='react-dom-edge'),c=x.evidence.cases[r.id],value=r.nodeControl.value,parsed=JSON.parse(value);
  r.worker.status='passed';r.worker.failures=[];r.worker.jco={passed:true,retainedCalls:3};r.worker.wasmtime={status:0,signal:null,timedOut:false,ownedGroupGone:true,passed:true};
  c.wtTerminal.status=0;c.wtTerminal.terminalExitZeroObserved=true;c.jcoStrings=[value,value,value];c.jcoRaw=c.jcoStrings.map(value=>({type:'string',value}));c.jcoParsed=[parsed,parsed,parsed];c.wtString=value;c.waveDecoded=value;c.wtParsed=parsed;r.differential={fullStringEqual:true,guestValue:parsed};sync(x,r.id);
},0,'previous-worker-blocker-now-passed');
test('adding a new output-root diagnostic still requires review',x=>{
  const r=x.report.cases.find(r=>r.id==='next-standalone');r.worker.failures[0].message+=' '+x.report.output;sync(x,r.id);
  // This is a real diagnostic change: merely being a path does not erase it.
},2,'worker-blocker-changed');
test('changed failure stderr requires review despite generic same trap',x=>x.evidence.cases['react-dom-edge'].wtStderr+='different stack frame\n',2,'worker-blocker-changed');
test('missing failure stderr rejects',x=>delete x.evidence.cases['react-dom-edge'].wtStderr,1,'missing-wasmtime-failure-streams');
test('same recorded source identities can relocate',x=>{
  for(const id of x.report.cases.map(r=>r.id)){
    const c=x.evidence.cases[id],old=c.native.sourceRoot;c.native.sourceRoot='/relocated/accepted-source';
    c.native.sourceInputs.forEach(r=>{r.path=c.native.sourceRoot+r.path.slice(old.length);});
    const t=x.report.commands.find(r=>r.name==='wasm-'+id);t.args[10]=c.native.sourceRoot;x.evidence.commands[t.name].terminal=structuredClone(t);
  }
},0);
test('unrecorded source argument alias refuses',x=>{const t=x.report.commands.find(r=>r.name==='wasm-react-element');t.args[10]='/unrelated/source';x.evidence.commands[t.name].terminal=structuredClone(t);},1,'worker-argv-mismatch');
test('changed recorded source identity refuses',x=>x.evidence.cases['react-element'].native.sourceInputs[0].sha256='0'.repeat(64),1,'recorded-native-closure-changed');
test('relative report output rejects',x=>x.report.output='relative-output',1,'absolute-report-roots-required');
test('relative report application rejects',x=>x.report.application='relative-application',1,'absolute-report-roots-required');
test('worker output must belong to the declared case root',x=>{
  const r=x.report.cases.find(r=>r.id==='react-element');r.worker.output+='.different';sync(x,r.id);
  const t=x.report.commands.find(command=>command.name==='wasm-'+r.id);t.args[6]=r.worker.output;x.evidence.commands[t.name].terminal=structuredClone(t);
},1,'worker-output-root-mismatch');
test('missing generated fixture is incomplete',x=>{const r=x.report.cases.find(r=>r.id==='next-page');r.worker.status='missing-fixture';r.worker.stage='fixture';r.worker.reason='GENERATED_NEXT_FIXTURE_NOT_FOUND';r.worker.failures=[];sync(x,r.id);},1,'required-generated-fixture-missing');
test('stable throw on a required passing Node control rejects',x=>{const r=x.report.cases.find(r=>r.id==='react-dom-string');r.nodeControl={status:'threw',name:'Error',message:'arbitrary'};x.evidence.commands['node-'+r.id].stdoutValue=structuredClone(r.nodeControl);},1,'finite-node-control-outcome-mismatch');
test('new guest success without a Node oracle does not count as improvement',x=>{
  const r=x.report.cases.find(r=>r.id==='next-page'),c=x.evidence.cases[r.id],donor=x.evidence.cases['react-element'];
  const output=r.worker.output;Object.assign(c,structuredClone(donor));r.worker=structuredClone(x.report.cases[2].worker);r.worker.case=r.id;r.worker.output=output;c.worker=structuredClone(r.worker);r.differential=null;
  // Keep complete component evidence internally consistent for the synthetic
  // case; the intentionally absent Node oracle alone prevents success.
  c.wtTerminal.args[3]=r.worker.component.path;sync(x,r.id);
},1,'new-guest-success-without-passing-node-oracle');
return {schemaVersion:1,syntheticDataMutations:tests.length,passed:true,tests,applicationExecuted:false,guestExecuted:false,childProcessesSpawned:false};
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url)console.log(JSON.stringify(await runTests(process.argv[2]),null,2));
