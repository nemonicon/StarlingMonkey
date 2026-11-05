// Read-only regression comparator; never loads an application, component or tool.
// node check-components.mjs BASELINE_RESULTS CURRENT_RESULTS
// Exit 0: no regression/change; 1: invalid/incomplete/regressed; 2: changed blocker.
import {readFile,lstat} from 'node:fs/promises';
import {dirname,join,resolve,basename,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {canonicalRolldownMessage} from '../nextjs/check-results.mjs';
import {parseScalarStringOutput} from '../../foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs';

export const CASES=Object.freeze(['native-cjs-interop','native-modules','react-element','react-dom-edge','react-dom-string','next-server','next-headers','next-standalone','next-page','next-route']);
export const REQUIRED_POSITIVES=Object.freeze(CASES.slice(0,3));
const NODE_CASES=CASES.slice(0,7),STATUSES=new Set(['passed','failed','refused','missing-fixture']);
const HEADERS_ERROR={status:'threw',name:'Error',message:'`headers` was called outside a request scope. Read more: https://nextjs.org/docs/messages/next-dynamic-api-wrong-context'};
const WIT='package root:component; world root { export run: func() -> string; }';
const ENGINE='d54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92';
const META='bfaec95ee0058edf587ebbf1cb020d7871759e896aa0d809e1af788a300531d6';
const WT='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c';
const TOOL_PACKAGES={'@bytecodealliance/jco':'ef0d7bf54e101a50bf2d242513c2fd64e6454ca7d2b42d8aead7669d91117f82',rolldown:'525884560d75c4eecb362453e6bbf92b1618d2261ddfbb1a806f164be0813f84'};
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const canonical=x=>Array.isArray(x)?'['+x.map(canonical).join(',')+']':object(x)?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}':JSON.stringify(x);
const same=(a,b)=>canonical(a)===canonical(b);
const sha=b=>createHash('sha256').update(b).digest('hex');
const descriptor=x=>object(x)&&typeof x.path==='string'&&/^[0-9a-f]{64}$/.test(x.sha256)&&Number.isSafeInteger(x.bytes)&&x.bytes>=0;
const empty=x=>Array.isArray(x)&&x.length===0;

// Only the exact roots declared by this result are replaced. No path patterns,
// generated names, wording, values, exception codes or semantic data are erased.
function normalize(value,report){
  const roots=[[report.output,'<RUN>'],[report.application,'<APPLICATION>']].filter(([x])=>typeof x==='string'&&x.startsWith('/')&&x.length>1).sort((a,b)=>b[0].length-a[0].length);
  if(typeof value==='string')return roots.reduce((s,[a,b])=>s.split(a).join(b),value);
  if(Array.isArray(value))return value.map(x=>normalize(x,report));
  if(object(value))return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,normalize(v,report)]));
  return value;
}
function blocker(worker,report,evidence){
  const diagnostics={};
  if(worker.wasmtime?.passed===false)diagnostics.wasmtime={stdout:evidence?.wtStdout,stderr:evidence?.wtStderr};
  if(worker.componentizer&&worker.componentizer.status!==0)diagnostics.componentizer={stdout:evidence?.componentStdout,stderr:evidence?.componentStderr};
  const value=normalize({status:worker.status,stage:worker.stage,reason:worker.reason??null,failures:worker.failures,candidates:worker.candidates??null,failedProcessDiagnostics:diagnostics},report);
  for(const f of value.failures??[])if(f.stage==='bundling'&&typeof f.message==='string')f.message=canonicalRolldownMessage(f.message);
  return value;
}
function nodeObservation(value,report){return value?.status==='threw'?normalize(value,report):value;}
function clean(t,status=0){
  return object(t)&&t.schemaVersion===1&&t.status===status&&t.signal===null&&t.spawnError===null&&t.timedOut===false
    &&t.externalSignal===null&&t.signalCount===0&&t.outputLimitExceeded===false&&t.closed===true&&t.ownedGroupGone===true
    &&empty(t.signals)&&empty(t.errors)&&(status===0?t.terminalExitZeroObserved===true:t.terminalExitZeroObserved===false);
}
const terminalSummary=t=>({status:t?.status,signal:t?.signal,timedOut:t?.timedOut,ownedGroupGone:t?.ownedGroupGone});
const absoluteRoot=x=>typeof x==='string'&&isAbsolute(x)&&x.length>1&&!x.split('/').includes('..');
// This is solely the observed macOS /tmp alias relationship between an argv
// string and its retained preflight root; it does not reopen either location.
const sameSourceArgument=(a,b)=>absoluteRoot(a)&&absoluteRoot(b)&&(a===b||(a.startsWith('/tmp/')&&b==='/private'+a)||(b.startsWith('/tmp/')&&a==='/private'+b));
function nativeClosure(native){
  return {sources:native.sourceInputs.map(r=>({path:r.path.slice(native.sourceRoot.length+1),sha256:r.sha256,bytes:r.bytes})).sort((a,b)=>a.path.localeCompare(b.path)),manifests:native.selectedModuleManifests};
}

/** Pure audit over parsed DATA. loadMatrix supplies relative retained evidence;
 * missing evidence is an error, never a successful comparison by omission. */
export function auditMatrices(baseline,current,evidence={baseline:{},current:{}}){
  const regressions=[],improvements=[],changedBlockers=[],outstandingKnownFailures=[];
  const coverage={complete:true,cases:CASES.length,requiredPositives:[...REQUIRED_POSITIVES],successfulReturns:[],constructedInterfaces:[]};
  const fail=(label,id,kind,detail={})=>regressions.push({label,id,kind,...detail});
  const incomplete=(label,id,kind,detail={})=>{coverage.complete=false;fail(label,id,kind,detail);};
  const states={};
  for(const [label,report]of[['baseline',baseline],['current',current]]){
    const data=evidence[label]??{},map=new Map();states[label]=map;
    if(!object(report)){incomplete(label,null,'results-not-object');continue;}
    if(report.schemaVersion!==1||report.suite!=='production-package-components-v1'||report.node!=='v22.14.0'||report.nodeEnvironment!=='production')incomplete(label,null,'suite-schema-or-recorded-version-mismatch');
    if(!absoluteRoot(report.output)||!absoluteRoot(report.application))incomplete(label,null,'absolute-report-roots-required');
    if(!['packages-v1','packages-v2'].includes(report.bundler))incomplete(label,null,'unknown-bundler');
    if(!empty(report.selectedInterfaces)||report.nativeProfileChanged!==false||report.legacyBundlerChanged!==false||report.frameworkCompatible!==false)incomplete(label,null,'interface-or-profile-scope-mismatch');
    if(report.observationsComplete!==true||!empty(report.errors)||typeof report.finished!=='string')incomplete(label,null,'incomplete-observations-or-suite-errors');
    if(!Array.isArray(report.cases)){incomplete(label,null,'missing-case-list');continue;}
    for(const row of report.cases){
      if(!object(row)||!CASES.includes(row.id)||map.has(row.id)){incomplete(label,row?.id??null,'unknown-or-duplicate-case');continue;}
      map.set(row.id,row);
    }
    if(report.cases.length!==10||CASES.some(id=>!map.has(id)))incomplete(label,null,'exact-ten-case-coverage-required');
    for(const issue of data.errors??[])incomplete(label,issue.id??null,'retained-evidence-unavailable',{evidence:issue});
    const expectedCommands=CASES.map(id=>'wasm-'+id).concat(NODE_CASES.map(id=>'node-'+id));
    const commandMap=new Map();
    for(const t of report.commands??[]){
      if(!object(t)||!expectedCommands.includes(t.name)||commandMap.has(t.name)){incomplete(label,t?.name??null,'unknown-or-duplicate-command');continue;}
      commandMap.set(t.name,t);const retained=data.commands?.[t.name];
      if(!retained||!same(t,retained.terminal)||!clean(t)||t.timeoutMs!==(t.name.startsWith('node-')?30000:240000))incomplete(label,t.name,'unclean-or-inconsistent-outer-terminal');
    }
    if(commandMap.size!==17||expectedCommands.some(id=>!commandMap.has(id)))incomplete(label,null,'exact-seventeen-commands-required');
    if(data.sourcesVerified!==true)incomplete(label,null,'missing-executed-source-copies');
    for(const id of CASES){
      const row=map.get(id);if(!row)continue;const w=row.worker,c=data.cases?.[id];
      if(row.collectorError!==undefined&&row.collectorError!==null)incomplete(label,id,'collector-error',{error:row.collectorError});
      if(!object(w)||!c||!same(w,c.worker)){incomplete(label,id,'missing-or-inconsistent-worker-report');continue;}
      if(w.schemaVersion!==1||w.case!==id||!STATUSES.has(w.status)||typeof w.stage!=='string'||typeof w.finishedAtUtc!=='string'||!Array.isArray(w.failures)||!w.failures.every(object))incomplete(label,id,'partial-or-invalid-worker-report');
      if(!absoluteRoot(report.output)||w.output!==join(report.output,'wasm',id))incomplete(label,id,'worker-output-root-mismatch');
      if(w.status==='missing-fixture')incomplete(label,id,'required-generated-fixture-missing');
      if(w.bundler!==report.bundler||!empty(w.selectedInterfaces)||w.experimentalEngineUsed!==false||w.builtinAdaptersUsed!==false||w.fullNextServerClaim!==false||w.postNativeRecheck!==true)incomplete(label,id,'worker-policy-or-post-recheck-mismatch');
      if(!descriptor(w.engine)||w.engine.sha256!==ENGINE||w.engine.bytes!==9973355||!descriptor(w.metadata)||w.metadata.sha256!==META||w.metadata.bytes!==290222)incomplete(label,id,'accepted-engine-or-metadata-mismatch');
      if(!same(c.native?.engine,w.engine)||!same(c.native?.metadata,w.metadata)||!absoluteRoot(c.native?.sourceRoot)||c.native?.sourceInputs?.length!==342||new Set(c.native?.sourceInputs?.map(r=>r.path)).size!==342||!c.native.sourceInputs.every(r=>descriptor(r)&&r.path.startsWith(c.native.sourceRoot+'/'))||!Array.isArray(c.native?.selectedModuleManifests)||c.native.selectedModuleManifests.length!==9||new Set(c.native.selectedModuleManifests.map(r=>r.path)).size!==9)incomplete(label,id,'recorded-native-frame-mismatch');
      if(c.tooling?.node?.sha256!=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'||Object.entries(TOOL_PACKAGES).some(([name,h])=>c.tooling?.packages?.[name]?.sha256!==h))incomplete(label,id,'recorded-node-or-tool-package-mismatch');
      const outer=data.commands?.['wasm-'+id];
      if(!same(outer?.stdoutValue,{case:id,stage:w.stage,status:w.status,output:w.output}))incomplete(label,id,'worker-stdout-envelope-mismatch');
      const args=outer?.terminal?.args;
      if(!Array.isArray(args)||args[1]!=='--case'||args[2]!==id||args[3]!=='--application'||args[4]!==report.application||args[5]!=='--output'||args[6]!==w.output||args[7]!=='--engine'||args[8]!==w.engine?.path||args[9]!=='--source-root'||!sameSourceArgument(args[10],c.native?.sourceRoot)||args[11]!=='--bundler'||args[12]!==report.bundler||args.length!==13||outer?.terminal.executable!==c.tooling?.node?.path)incomplete(label,id,'worker-argv-mismatch');
      const node=row.nodeControl;
      if(NODE_CASES.includes(id)){
        if(!object(node)||!['passed','threw'].includes(node.status)||!same(node,data.commands?.['node-'+id]?.stdoutValue))incomplete(label,id,'missing-or-inconsistent-node-control');
        else if(node.status==='passed'&&typeof node.value!=='string'||node.status==='threw'&&(typeof node.name!=='string'||typeof node.message!=='string'))incomplete(label,id,'invalid-node-control-value');
        if(node?.code==='ERR_MODULE_NOT_FOUND')incomplete(label,id,'node-control-resolution-failed');
        if(id==='next-headers'?!same(node,HEADERS_ERROR):node?.status!=='passed')incomplete(label,id,'finite-node-control-outcome-mismatch');
        if(data.commands?.['node-'+id]?.terminal.executable!==c.tooling?.node?.path)incomplete(label,id,'node-control-executable-mismatch');
        if(['next-server','next-headers'].includes(id)){
          const resolution=row.nodeControlResolution,specifier=id==='next-server'?'next/server':'next/headers';
          if(resolution?.specifier!==specifier||!descriptor(resolution?.resolvedEntry)||!resolution.resolvedEntry.path.startsWith(report.application+'/node_modules/next/')||!resolution.resolvedEntry.path.endsWith('/'+specifier.split('/')[1]+'.js'))incomplete(label,id,'missing-real-next-node-control-entry');
        }
      }else if(node!==null)incomplete(label,id,'unexpected-node-control');
      if(w.componentizer){
        if(!same(terminalSummary(c.componentTerminal),w.componentizer)||!clean(c.componentTerminal,w.componentizer.status)||c.componentTerminal.timeoutMs!==120000)incomplete(label,id,'component-child-terminal-mismatch');
        if(w.componentizer.status!==0&&(typeof c.componentStderr!=='string'||typeof c.componentStdout!=='string'))incomplete(label,id,'missing-component-failure-streams');
      }
      if(w.component){
        if(!descriptor(w.component)||c.child?.status!=='passed'||c.child?.stage!=='componentization'||!same(c.child.component,w.component)||!empty(c.child.imports)
          ||c.audit?.state!=='verified-final-component'||c.audit.componentSha256!==w.component.sha256||!empty(c.audit.emittedImports)||!empty(c.audit.selectedInterfaces)
          ||typeof c.wit!=='string'||c.wit.replace(/\s+/g,' ').trim()!==WIT||!empty(c.transpile?.imports)||!same(c.transpile?.exports,[['run','function']]))incomplete(label,id,'recorded-component-interface-mismatch');
        coverage.constructedInterfaces.push({label,id,emittedImports:[],wit:'run: func() -> string',binaryIndependentlyDecoded:false});
      }
      if(w.wasmtime){
        if(!descriptor(w.wasmtimeBinary)||w.wasmtimeBinary.sha256!==WT||w.wasmtimeBinary.bytes!==50820352||!clean(c.versionTerminal)||c.versionTerminal.timeoutMs!==10000||!/^wasmtime 42\.0\.1\b/.test(c.versionStdout??'')||c.versionTerminal.executable!==w.wasmtimeBinary.path||c.wtTerminal?.executable!==w.wasmtimeBinary.path)incomplete(label,id,'stock-wasmtime-version-mismatch');
        if(!same(terminalSummary(c.wtTerminal),Object.fromEntries(Object.entries(w.wasmtime).filter(([k])=>k!=='passed')))||!clean(c.wtTerminal,w.wasmtime.status)||c.wtTerminal.timeoutMs!==60000||!same(c.wtTerminal.args,['run','--invoke','run()',w.component?.path]))incomplete(label,id,'wasmtime-terminal-or-invocation-mismatch');
        if(w.wasmtime.passed===false&&(typeof c.wtStderr!=='string'||typeof c.wtStdout!=='string'))incomplete(label,id,'missing-wasmtime-failure-streams');
      }
      if(w.status==='passed'){
        if(node?.status!=='passed')incomplete(label,id,'new-guest-success-without-passing-node-oracle');
        if(w.stage!=='complete'||!empty(w.failures)||w.jco?.passed!==true||w.jco.retainedCalls!==3||w.wasmtime?.passed!==true||w.componentizer?.status!==0||!w.component)incomplete(label,id,'inconsistent-success');
        const strings=c.jcoStrings;
        if(!Array.isArray(strings)||strings.length!==3||strings.some(s=>typeof s!=='string')||!strings.every(s=>s===strings[0])||c.wtString!==strings[0]||c.waveDecoded!==strings[0])incomplete(label,id,'missing-or-different-whole-return');
        else{
          try{
            const parsed=JSON.parse(strings[0]);
            if(!Array.isArray(c.jcoRaw)||c.jcoRaw.length!==3||c.jcoRaw.some((r,i)=>!same(r,{type:'string',value:strings[i]}))||!same(c.jcoParsed,[parsed,parsed,parsed])||!same(c.wtParsed,parsed))incomplete(label,id,'typed-or-parsed-return-mismatch');
            if(node?.status==='passed'&&(node.value!==strings[0]||row.differential?.fullStringEqual!==true||!same(row.differential.guestValue,parsed)))fail(label,id,'complete-node-jco-wasmtime-differential-mismatch');
            coverage.successfulReturns.push({label,id,retainedJcoCalls:3,freshWasmtimeCalls:1,nodeCompared:node?.status==='passed'});
          }catch{incomplete(label,id,'invalid-complete-return-json');}
        }
      }else if(w.failures.length===0&&w.status!=='missing-fixture')incomplete(label,id,'failure-without-diagnostic');
    }
    const positive=REQUIRED_POSITIVES.every(id=>map.get(id)?.worker?.status==='passed'&&map.get(id)?.nodeControl?.status==='passed'&&map.get(id)?.differential?.fullStringEqual===true);
    if(report.requiredPositivePassed!==positive||!positive)fail(label,null,'required-three-positive-differentials-not-passed');
    const nativeFrames=CASES.map(id=>data.cases?.[id]?.native);
    if(nativeFrames.every(n=>n?.sourceInputs?.length===342&&Array.isArray(n.selectedModuleManifests))&&!nativeFrames.every(n=>same(nativeClosure(n),nativeClosure(nativeFrames[0]))))incomplete(label,null,'inconsistent-recorded-native-closure');
  }
  if(object(baseline)&&object(current)){
    if(baseline.bundler!==current.bundler)incomplete('comparison',null,'bundler-mismatch');
    for(const suffix of [baseline.bundler==='packages-v2'?'framework-package-bundler-v2.mjs':'framework-package-bundler.mjs',...(baseline.bundler==='packages-v2'?['package-environment-guards.mjs','bindings.mjs']:[])]){
      const get=r=>r.sources?.filter(s=>basename(s.path??'')===suffix);
      const a=get(baseline),b=get(current);
      if(a?.length!==1||b?.length!==1||a[0].sha256!==b[0].sha256||a[0].bytes!==b[0].bytes)incomplete('comparison',suffix,'bundler-or-policy-source-mismatch');
    }
    for(const id of CASES){
      const a=states.baseline?.get(id),b=states.current?.get(id);if(!a?.worker||!b?.worker)continue;
      if(a.worker.originalSource&&b.worker.originalSource&&(a.worker.originalSource.sha256!==b.worker.originalSource.sha256||a.worker.originalSource.bytes!==b.worker.originalSource.bytes))incomplete('comparison',id,'probe-source-mismatch');
      const passed=x=>x.worker.status==='passed';
      const oldEvidence=evidence.baseline?.cases?.[id],newEvidence=evidence.current?.cases?.[id];
      if(oldEvidence?.native?.sourceInputs?.length===342&&newEvidence?.native?.sourceInputs?.length===342&&!same(nativeClosure(oldEvidence.native),nativeClosure(newEvidence.native)))incomplete('comparison',id,'recorded-native-closure-changed');
      if(passed(a)&&!passed(b))fail('comparison',id,'successful-case-regressed',{before:blocker(a.worker,baseline,oldEvidence),after:blocker(b.worker,current,newEvidence)});
      else if(!passed(a)&&passed(b)){
        if(b.nodeControl?.status==='passed')improvements.push({id,kind:'previous-worker-blocker-now-passed'});
        else changedBlockers.push({id,kind:'unoracled-guest-success-requires-review',disposition:'New return is not a verified improvement; no passing Node oracle exists.'});
      }
      else if(!passed(a)){
        const before=blocker(a.worker,baseline,oldEvidence),after=blocker(b.worker,current,newEvidence);
        if(same(before,after))outstandingKnownFailures.push({id,...after,stillFailed:true});
        else changedBlockers.push({id,kind:'worker-blocker-changed',before,after,disposition:'Review required; a different failure is not success.'});
      }else{
        const before=evidence.baseline?.cases?.[id]?.jcoStrings?.[0],after=evidence.current?.cases?.[id]?.jcoStrings?.[0];
        if(typeof before!=='string'||typeof after!=='string'||before!==after)fail('comparison',id,'successful-whole-return-changed');
      }
      const before=nodeObservation(a.nodeControl,baseline),after=nodeObservation(b.nodeControl,current);
      if(!same(before,after)){
        if(a.nodeControl?.status==='threw'&&b.nodeControl?.status==='passed')improvements.push({id,kind:'node-control-now-passed'});
        else if(a.nodeControl?.status==='passed')fail('comparison',id,'node-control-result-regressed-or-changed',{before,after});
        else changedBlockers.push({id,kind:'node-control-blocker-changed',before,after,disposition:'Review required.'});
      }
    }
  }
  return {schemaVersion:1,suite:'package-component-regression-comparison-v1',coverage,regressions,improvements,changedBlockers,outstandingKnownFailures,
    frameworkCompatible:false,interpretation:'No-regression comparison only. Known failures remain failures; improvements do not establish general package/framework support.',
    limits:['Only recorded Node22/bundler/Wasmtime/native identities are enforced; installed Next/React package versions are absent from this matrix schema.',
      'Checks retained WIT/audit/transpile records, not an independent decode of component binaries (not copied into the repository results).',
      'Does not rehash external engine/tool/source trees, rerun applications, or approve changed harness code.',
      'Finite Node controls require six passes and the exact headers outside-request-scope error. Generated-entry successes need a future oracle contract; missing fixtures are incomplete.'],
    harnessSources:{baseline:baseline?.sources??null,current:current?.sources??null}};
}
export const comparisonExitCode=a=>a.regressions.length||!a.coverage.complete?1:a.changedBlockers.length?2:0;

/** Reads copied evidence next to results.json. Descriptor paths are provenance
 * strings only: no external runtime/application path is opened. */
export async function loadMatrix(path){
  path=resolve(path);const root=dirname(path),decoder=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true});
  async function raw(relative,max=32*1024*1024){const p=join(root,relative),s=await lstat(p);if(!s.isFile()||s.size>max)throw new Error('Missing/nonregular/oversized retained file: '+relative);return readFile(p);}
  const text=async relative=>decoder.decode(await raw(relative));
  const json=async relative=>JSON.parse(await text(relative));
  const report=JSON.parse(decoder.decode(await raw(basename(path))));
  const data={commands:{},cases:{},errors:[],sourcesVerified:true};
  async function attempt(id,action){try{return await action();}catch(e){data.errors.push({id,message:e.message,code:e.code??null});return undefined;}}
  function verify(bytes,d){if(!descriptor(d)||bytes.length!==d.bytes||sha(bytes)!==d.sha256)throw new Error('Retained stream/source descriptor mismatch');}
  async function terminal(prefix){
    const t=await json(prefix+'.terminal.json');
    const stdout=await raw(prefix+'.stdout.log'),stderr=await raw(prefix+'.stderr.log');verify(stdout,t.stdout);verify(stderr,t.stderr);
    return {terminal:t,stdout:decoder.decode(stdout),stderr:decoder.decode(stderr),stdoutBytes:stdout};
  }
  const names=CASES.map(id=>'wasm-'+id).concat(NODE_CASES.map(id=>'node-'+id));
  for(const name of names)await attempt(name,async()=>{const x=await terminal(name);x.stdoutValue=JSON.parse(x.stdout);data.commands[name]=x;});
  const sourceNames=new Set();
  if(!Array.isArray(report.sources)||report.sources.length<3)data.sourcesVerified=false;
  for(const s of report.sources??[])await attempt('executed-source',async()=>{
    if(!descriptor(s)||sourceNames.has(basename(s.path)))throw new Error('Invalid or duplicate executed source');sourceNames.add(basename(s.path));verify(await raw('executed-harness/'+basename(s.path)),s);
  });
  if(data.errors.some(e=>e.id==='executed-source'))data.sourcesVerified=false;
  for(const id of CASES)await attempt(id,async()=>{
    const base='wasm/'+id+'/',worker=await json(base+'result.json'),c={worker};data.cases[id]=c;
    c.native=await json(base+'native-preflight.json');c.tooling=await json(base+'tooling-preflight.json');
    if(worker.bundle)verify(await raw(base+'bundle.mjs'),worker.bundle);
    if(worker.componentizer){const x=await terminal(base+'componentize');c.componentTerminal=x.terminal;c.componentStdout=x.stdout;c.componentStderr=x.stderr;}
    if(worker.component){c.child=await json(base+'component-child-result.json');c.audit=await json(base+'interface-audit.json');c.wit=await text(base+'emitted.wit');c.transpile=await json(base+'transpile-metadata.json');}
    if(worker.wasmtime){
      const version=await terminal(base+'wasmtime-version'),wt=await terminal(base+'wasmtime-run');c.versionTerminal=version.terminal;c.versionStdout=version.stdout;c.wtTerminal=wt.terminal;c.wtStdout=wt.stdout;c.wtStderr=wt.stderr;
      if(worker.status==='passed')c.waveDecoded=parseScalarStringOutput({stdoutBytes:wt.stdoutBytes,rawDurablyRetained:true});
    }
    if(worker.status==='passed'){
      c.jcoStrings=await Promise.all([0,1,2].map(i=>text(base+`jco-${i}.string.txt`)));c.jcoRaw=await Promise.all([0,1,2].map(i=>json(base+`jco-${i}.raw.json`)));c.jcoParsed=await Promise.all([0,1,2].map(i=>json(base+`jco-${i}.parsed.json`)));c.wtString=await text(base+'wasmtime.string.txt');c.wtParsed=await json(base+'wasmtime.parsed.json');
    }
  });
  return {report,evidence:data};
}
async function main(args){
  if(args.length===1&&args[0]==='--self-test'){const {runTests}=await import('./test-check-components.mjs');process.stdout.write(JSON.stringify(await runTests(),null,2)+'\n');return;}
  if(args.length!==2)throw new Error('Usage: check-components.mjs BASELINE_RESULTS CURRENT_RESULTS');
  const [a,b]=await Promise.all(args.map(loadMatrix));const result=auditMatrices(a.report,b.report,{baseline:a.evidence,current:b.evidence});
  process.stdout.write(JSON.stringify(result,null,2)+'\n');process.exitCode=comparisonExitCode(result);
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url)main(process.argv.slice(2)).catch(e=>{
  process.stdout.write(JSON.stringify({schemaVersion:1,coverage:{complete:false},regressions:[{kind:'input-read-error',message:e.message}],changedBlockers:[],improvements:[],frameworkCompatible:false},null,2)+'\n');process.exitCode=1;
});
