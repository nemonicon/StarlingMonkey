// Pure scalar/profile/mapping checks. No shim, generated module, or process import.
import {isDeepStrictEqual as same} from 'node:util';
import {createHash} from 'node:crypto';
const need=(v,m)=>{if(!v)throw new Error(m);};
export const INTERFACES=Object.freeze(['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10']);
export function artifactModel(p,contract,refs){
 need(p?.schemaVersion===1&&p.state==='INDEPENDENT_CLOCK_V13_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'&&p.verifiedPassed===true,'Actual clock-selected artifact proof');
 need(p.componentSourceIndexSha256===refs.componentSourceIndex.sha256&&p.componentSha256===refs.component.sha256&&p.engineSha256===refs.nativeEngine.sha256,'Actual original component/native/source identities');
 need(p.nativeSourceFiles===342&&p.externalEmbeddingSources===3&&p.fullMetadataFields===64&&p.selectedManifestCount===9,'Whole accepted native342+3/64/9 only');
 need(same([...p.emittedImports].sort(),[...INTERFACES].sort())&&same(p.publicAbiFunctions,['run']),'Exactly three standard callable0.2.10 interfaces and sole run');
 for(const k of ['ordinaryGuestExportsInvoked','generatedModuleImported','runtimeAcceptanceClaim','operationalAdmission'])need(p[k]===false,'Construction scope only '+k);
 need(contract?.schemaVersion===1&&same(contract.artifacts,p.artifacts)&&same(p.artifacts,refs.artifacts),'Whole exact actual artifact contract/map');return true;
}
export function phaseModel(root,own,refs,phase){
 need(root?.schemaVersion===1&&root.state==='ROOT_REVIEWED_CLOCK_V13_REACTDOM_DIFFERENTIAL_V2'&&root.phase===phase&&same(root.sourceIndex,own),'New own Root phase/source');
 need(['mapped-transpile','runtime-differential'].includes(phase)&&root.variant==='normal-off'&&same(root.actualArtifactReview,refs.actualArtifactReview)&&same(root.actualArtifactContract,refs.actualArtifactContract),'Exact actual proof, distinct finite phases');
 need(root.componentSha256===refs.component.sha256&&root.outputRoot===(phase==='mapped-transpile'?refs.mappedOutputRoot:refs.runtimeOutputRoot),'Same reviewed component and fixed fresh output');
 need(same(root.selectedInterfaces,INTERFACES)&&same(root.mappingOptions,refs.mappingOptions),'Unchanged actual selected interfaces/standard mapping');
 need(root.mappedTranspileAllowed===(phase==='mapped-transpile')&&root.jcoCompilerWasmHelpersAllowed===(phase==='mapped-transpile'),'No implicit compilation action');
 need(root.generatedApplicationImportAllowed===(phase==='runtime-differential')&&root.ordinaryRunAllowed===(phase==='runtime-differential')&&root.stockWasmtimeAllowed===(phase==='runtime-differential'),'No application work during mapping');
 need(root.nativeReadOnlyPreflightAllowed===true,'Genuine original native read-only API explicitly allowed');
 need(root.externalOutputRoot===root.outputRoot+'-external-root'&&same(root.monitorIndex,refs.monitorIndex)&&same(root.monitorEntry,refs.monitorEntry),'Genuine owned external monitor/context');
 need(root.standardShimWorkerThreadsAllowed===true&&root.ownedWorkerDeadlineMs===180000&&root.requiredExternalParentDeadlineSeconds===1200,'Real standard worker shim and external deadlines');
 for(const k of ['customHostServicesAllowed','componentConstructionAllowed','nativeBuildAllowed','engineReplacementAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','otherGuestAllowed','resourceSevenCaseProfileAccepted','clockProfilePromotionAllowed','dateTimerSnapshotTeardownAccepted','resetOrReuseAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'])need(root[k]===false,'Slice does not grant '+k);
 if(phase==='runtime-differential')need(root.actualMappedOutputReview&&root.actualMappedOutputReview.path,'Separate actual mapped-output proof required');
 else need(root.actualMappedOutputReview===null,'No mapped proof invented in advance');return true;
}
export function scalarRunArguments(name,args){need(name==='run'&&Array.isArray(args)&&args.length===0,'Sole real run()->string ABI');return true;}
export function htmlResult(value,expected){
 need(typeof value==='string'&&value.length<=2097152,'Whole bounded ordinary scalar string');need(value===expected,'Whole public string equals actual retained Node oracle');
 const v=JSON.parse(value);need(same(Object.keys(v),['library','html','bytes'])&&v.library==='react-dom/server.edge'&&v.html==='<p id="wasm-ssr">Hello from real ReactDOM</p>'&&v.bytes===45&&new TextEncoder().encode(v.html).length===v.bytes,'Full HTML and UTF8 bytes, no normalization');return v;
}
function walk(v,visit){if(!v||typeof v!=='object')return;if(Array.isArray(v)){for(const x of v)walk(x,visit);return;}visit(v);for(const[k,x]of Object.entries(v))if(!['parent','loc','range'].includes(k))walk(x,visit);}
export function mappedGlueModel(ast,refs){
 need(ast?.type==='Program'&&Array.isArray(ast.body),'Actual mapped-source AST');const sources=new Map([[refs.shimClocksUrl,new Set(['monotonicClock','wallClock'])],[refs.shimIoUrl,new Set(['poll'])]]),used=new Map(),publicNames=[],functions=new Map();let helper=false,tla=0,nodeFs=0;const coreUrls=[],inline=[];
 for(const node of ast.body){
  if(node.type==='ImportDeclaration'){
   const names=sources.get(node.source?.value);need(names,'Only exact pinned standard clock/io shim module URLs');const set=used.get(node.source.value)||new Set();
   for(const s of node.specifiers){need(s.type==='ImportSpecifier'&&s.imported?.type==='Identifier'&&names.has(s.imported.name)&&!set.has(s.imported.name),'Only actual standard interface object bindings');set.add(s.imported.name);}used.set(node.source.value,set);
  }
  const d=node.type==='ExportNamedDeclaration'?node.declaration:node;
  if(d?.type==='FunctionDeclaration'&&d.id?.name==='run'){need(!d.async&&!d.generator&&d.params.length===0&&!functions.has('run'),'Sync scalar binding, no guessed await');functions.set('run',d);}
  need(!['ExportDefaultDeclaration','ExportAllDeclaration'].includes(node.type),'No default/star public exports');
  if(node.type==='ExportNamedDeclaration'){
   need(!node.source,'No reexports');for(const s of node.specifiers??[]){need(s.type==='ExportSpecifier'&&s.local?.name==='run'&&s.exported?.name==='run','Only actual same-name run export');publicNames.push('run');}
   if(d?.type==='FunctionDeclaration'){need(d.id.name==='run','No extra public functions');publicNames.push('run');}
   else if(d){need(!helper&&node===ast.body.at(-1)&&d.type==='VariableDeclaration'&&d.kind==='const'&&d.declarations.length===1&&d.declarations[0].id?.name==='_util'&&d.declarations[0].init?.type==='ObjectExpression'&&d.declarations[0].init.properties.length===0,'Only terminal empty Jco helper');helper=true;publicNames.push('_util');}
  }
  if(node.type==='ExpressionStatement'&&node.expression?.type==='AwaitExpression'){need(node.expression.argument?.type==='Identifier'&&node.expression.argument.name==='$init','Actual top-level await init');tla++;}
 }
 for(const[url,names]of sources)need(used.has(url)&&same([...used.get(url)].sort(),[...names].sort()),'Every exact required standard interface binding');
 walk(ast,n=>{
  if(n.type==='CallExpression'&&n.callee?.type==='Identifier'&&n.callee.name==='base64Compile'){const s=n.arguments?.[0];need(n.arguments.length===1&&s?.type==='Literal'&&typeof s.value==='string'&&/^[A-Za-z0-9+/]*={0,2}$/.test(s.value),'Whole literal inline core');const bytes=Buffer.from(s.value,'base64');const canonical=bytes.toString('base64');need(s.value===canonical||s.value===canonical.replace(/=+$/,''),'Canonical padded or actual Jco unpadded full base64');inline.push({sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length});}
  if(n.type==='ImportExpression'){need(n.source?.type==='Literal'&&n.source.value==='node:fs/promises','Only generated Node file loader dynamic import');nodeFs++;}
  if(n.type==='NewExpression'&&n.callee?.name==='URL'){need(n.arguments?.length===2&&n.arguments[0]?.type==='Literal'&&n.arguments[0].value==='./clock_v13.core.wasm','Actual relative external core only');const b=n.arguments[1];need(b?.type==='MemberExpression'&&!b.computed&&b.property?.name==='url'&&b.object?.type==='MetaProperty'&&b.object.meta?.name==='import'&&b.object.property?.name==='meta','Real import.meta.url');coreUrls.push(n.arguments[0].value);}
 });
 need(same(inline,refs.inlineCoreModules),'All three inline core bytes unchanged');
 need(functions.size===1&&same(publicNames.sort(),['run','_util'].sort())&&tla===1&&nodeFs===1&&coreUrls.length===1,'Exact mapped generated scalar/TLA/core protocol');return{shimModuleUrls:[...used.keys()].sort(),standardInterfaces:[...INTERFACES],publicExports:publicNames,topLevelAwait:true,inlineCoreModules:inline,generatedApplicationImported:false};
}
export function namespaceModel(ns){
 need(ns!==null&&typeof ns==='object'&&Object.getPrototypeOf(ns)===null&&same(Object.getOwnPropertyNames(ns).sort(),['_util','run']),'Exact ESM namespace names before reading then');
 need(typeof ns.run==='function'&&ns.run.length===0,'Actual sole scalar export');const h=ns._util;need(h&&typeof h==='object'&&Object.getPrototypeOf(h)===Object.prototype&&Reflect.ownKeys(h).length===0,'Empty helper only');return true;
}
