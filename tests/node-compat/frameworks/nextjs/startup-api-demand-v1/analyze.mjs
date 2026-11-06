// DATA/AST only. Never evaluates any of the 406 application input files.
import assert from 'node:assert/strict';
import {readFile,writeFile,realpath,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {dirname,join} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url)),REPO=join(HERE,'../../../../..');
const digest=b=>createHash('sha256').update(b).digest('hex');
const desc=async p=>{const b=await readFile(p);return{path:p,sha256:digest(b),bytes:b.length};};
const save=async(n,v)=>writeFile(join(HERE,n),JSON.stringify(v,null,2)+'\n',{flag:'wx'});
assert.equal(process.version,'v22.14.0');assert.equal(process.platform,'darwin');assert.equal(process.arch,'arm64');
for(const key of Object.keys(process.env))assert(!key.startsWith('NAPI_RS_')&&!['NODE_OPTIONS','NODE_PATH'].includes(key),'Parser override not allowed');
const tool='/private/tmp/starling-node-compat/toolchain/node_modules/rolldown';
const helper=join(REPO,'tests/node-compat/frameworks/package-bundler-bindings-v2/bindings.mjs');
const parserFiles=['package.json','dist/parse-ast-index.mjs','dist/shared/logs-DyTyzzWG.mjs','dist/shared/parse-Bgfg7ZwM.mjs','dist/shared/binding-BXYS21Tf.mjs','dist/shared/rolldown-runtime-DYf_mQCB.mjs'].map(p=>join(tool,p));
parserFiles.push('/private/tmp/starling-node-compat/toolchain/node_modules/@rolldown/binding-darwin-arm64/package.json','/private/tmp/starling-node-compat/toolchain/node_modules/@rolldown/binding-darwin-arm64/rolldown-binding.darwin-arm64.node',helper,process.execPath);
const parserBefore=await Promise.all(parserFiles.map(desc));assert.equal(JSON.parse(await readFile(join(tool,'package.json'),'utf8')).version,'1.2.16');
assert.equal(parserBefore.at(-1).sha256,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
// Pinned Darwin/arm64 branch loads this host parser binding; no fallback/tool
// command, target engine, native compiler or application module is called.
const {parseAst}=await import(pathToFileURL(join(tool,'dist/parse-ast-index.mjs')));
const {findUnboundReferences}=await import(pathToFileURL(helper));
const input=join(HERE,'../http-bridge-candidate-v1/module-results/next-http-bridge-module-v1/result.json');
const reportBefore=await desc(input),report=JSON.parse(await readFile(input,'utf8'));assert(report.passed===true&&report.guestExecuted===false&&report.moduleSnapshot.compiled.length===406);
const TARGETS=new Set(['process','url','os','timers','timers/promises','perf_hooks','http','https','zlib']);
const GLOBALS={process:['process'],URL:['url','URL'],URLSearchParams:['url','URLSearchParams'],performance:['perf_hooks','performance'],setTimeout:['timers','setTimeout'],clearTimeout:['timers','clearTimeout'],setInterval:['timers','setInterval'],clearInterval:['timers','clearInterval'],setImmediate:['timers','setImmediate'],clearImmediate:['timers','clearImmediate'],queueMicrotask:['timers','queueMicrotask']};
const canonical=s=>s.replace(/^node:/,'');
const aggregate=new Map(),inputRows=[],parseErrors=[],unresolved=[];let nodeCount=0;
function children(n){return Object.entries(n).flatMap(([k,v])=>k==='parent'||k==='loc'||k==='range'?[]:Array.isArray(v)?v.filter(x=>x&&typeof x==='object').map(x=>[x,k]):v&&typeof v==='object'?[[v,k]]:[]);}
function analyze(ast,source,path){
 const nodeScope=new WeakMap(),parent=new WeakMap(),ancestors=new WeakMap(),all=[],declarations=[],assignments=[];
 class Scope{constructor(up,kind){this.up=up;this.kind=kind;this.bindings=new Map();}bind(name){if(!this.bindings.has(name))this.bindings.set(name,{name,alias:null,unknown:false});return this.bindings.get(name);}find(name){return this.bindings.get(name)??this.up?.find(name);}varScope(){let s=this;while(!['program','function'].includes(s.kind))s=s.up;return s;}}
 function pattern(node,scope,expr=null,tail=[]){if(!node)return;if(node.type==='Identifier'){const binding=scope.bind(node.name);if(expr)declarations.push({binding,expr,tail});return;}if(node.type==='ObjectPattern')for(const p of node.properties){if(p.type==='Property'&&!p.computed)pattern(p.value,scope,expr,[...tail,p.key.name??p.key.value]);else pattern(p.argument,scope);}else if(node.type==='ArrayPattern')for(const p of node.elements)pattern(p,scope);else if(node.type==='AssignmentPattern')pattern(node.left,scope);else if(node.type==='RestElement')pattern(node.argument,scope);}
 function visit(n,scope,stack=[],p=null,key=''){
  if(!n||!n.type)return;
  if(n.type==='FunctionDeclaration'&&n.id)scope.bind(n.id.name);
  if(/^(FunctionDeclaration|FunctionExpression|ArrowFunctionExpression)$/.test(n.type)){scope=new Scope(scope,'function');if(n.id)scope.bind(n.id.name);for(const p of n.params)pattern(p,scope);}
  else if(n.type==='BlockStatement'||/^For(?:Of|In)?Statement$/.test(n.type)||n.type==='SwitchStatement')scope=new Scope(scope,'block');
  else if(n.type==='CatchClause'){scope=new Scope(scope,'catch');pattern(n.param,scope);}
  if(n.type==='ClassDeclaration'&&n.id)scope.bind(n.id.name);
  nodeScope.set(n,scope);if(p)parent.set(n,{node:p,key});ancestors.set(n,stack);all.push(n);
  if(n.type==='VariableDeclaration')for(const d of n.declarations)pattern(d.id,n.kind==='var'?scope.varScope():scope,d.init);
  if(n.type==='AssignmentExpression'&&n.left.type==='Identifier')assignments.push(n);
  for(const [c,k]of children(n))visit(c,scope,[...stack,n],n,k);
 }
 visit(ast,new Scope(null,'program'));
 const ambient=new Set(findUnboundReferences(ast,[...Object.keys(GLOBALS),'require']).map(n=>n));
 function expr(n){if(!n)return null;if(n.type==='ChainExpression')return expr(n.expression);if(n.type==='SequenceExpression')return expr(n.expressions.at(-1));
  if(n.type==='Identifier'){if(ambient.has(n)&&GLOBALS[n.name])return GLOBALS[n.name];return nodeScope.get(n)?.find(n.name)?.alias??null;}
  if(n.type==='MemberExpression'){const base=expr(n.object),key=n.computed?n.property.type==='Literal'?n.property.value:'*':n.property.name;if(!base)return null;return key==='default'?base:[...base,String(key)];}
  if(n.type==='CallExpression'){
   if(n.callee.type==='Identifier'&&n.callee.name==='require'&&ambient.has(n.callee)&&n.arguments.length===1&&n.arguments[0].type==='Literal'&&typeof n.arguments[0].value==='string'){const id=canonical(n.arguments[0].value);return TARGETS.has(id)?[id]:null;}
   // Explicit common SWC interop wrappers only, not arbitrary call propagation.
   if(n.callee.type==='Identifier'&&/^_interop_require_(?:default|wildcard)$/.test(n.callee.name)&&n.arguments.length>=1)return expr(n.arguments[0]);
  }return null;}
 for(let i=0;i<5;i++)for(const d of declarations){const base=expr(d.expr);if(!base)continue;const alias=[...base,...d.tail];if(d.binding.alias&&JSON.stringify(d.binding.alias)!==JSON.stringify(alias)){d.binding.unknown=true;d.binding.alias=null;}else if(!d.binding.unknown)d.binding.alias=alias;}
 for(const a of assignments){const b=nodeScope.get(a)?.find(a.left.name);if(b)b.alias=null;}
 function context(n){const chain=ancestors.get(n)??[];return{insideFunction:chain.some(x=>/Function/.test(x.type)),conditionalSyntax:chain.filter(x=>['IfStatement','ConditionalExpression','SwitchCase','LogicalExpression'].includes(x.type)).slice(-3).map(x=>({kind:x.type,source:source.slice(x.start,Math.min(x.end,x.start+150)).replace(/\s+/g,' ')}))};}
 function location(n){const prefix=source.slice(0,n.start),line=prefix.split('\n').length,column=n.start-(prefix.lastIndexOf('\n')+1)+1;return{path,line,column,utf16Start:n.start,source:source.slice(n.start,Math.min(n.end,n.start+220)).replace(/\s+/g,' '),...context(n)};}
 const dedup=new Set();
 function add(parts,n,use){if(!parts||!TARGETS.has(parts[0]))return;parts=parts.filter((p,i)=>!(i&&p==='default'));if(parts.length>2&&['call','apply','bind'].includes(parts.at(-1)))parts=parts.slice(0,-1);
  let api=parts.join('.'),detail=null;if(parts[0]==='process'&&parts[1]==='env'){api='process.env';detail=parts.slice(2).join('.')||null;}
  const key=api+'\0'+use+'\0'+n.start;if(dedup.has(key))return;dedup.add(key);
  if(!aggregate.has(api))aggregate.set(api,{api,module:parts[0],staticReferences:0,staticCalls:0,staticConstructs:0,staticWrites:0,staticReads:0,runtimeMethodInvocationsObserved:null,files:new Set(),examples:[],environmentKeys:new Set()});
  const r=aggregate.get(api);r.staticReferences++;r.files.add(path);if(detail)r.environmentKeys.add(detail);if(use==='call')r.staticCalls++;else if(use==='construct')r.staticConstructs++;else if(use==='write')r.staticWrites++;else r.staticReads++;
  if(r.examples.length<5)r.examples.push({...location(n),use});
 }
 for(const n of all){nodeCount++;const p=parent.get(n)?.node;
  if(n.type==='CallExpression'||n.type==='NewExpression'){add(expr(n.callee),n,n.type==='NewExpression'?'construct':'call');}
  if(n.type==='MemberExpression'){
   if(p?.type==='MemberExpression'&&p.object===n||p?.type==='CallExpression'&&p.callee===n||p?.type==='NewExpression'&&p.callee===n)continue;
   add(expr(n),n,p?.type==='AssignmentExpression'&&p.left===n||p?.type==='UpdateExpression'?'write':'read');
  }
  if(n.type==='Identifier'&&ambient.has(n)&&GLOBALS[n.name]&&p?.type!=='MemberExpression'&&!(p?.type==='CallExpression'&&p.callee===n)&&!(p?.type==='NewExpression'&&p.callee===n))add(GLOBALS[n.name],n,p?.type==='UnaryExpression'&&p.operator==='typeof'?'typeof':'read');
 }
}
for(const path of report.moduleSnapshot.compiled){const b=await readFile(path),source=b.toString('utf8');inputRows.push({path,sha256:digest(b),bytes:b.length});try{analyze(parseAst(source,{sourceType:'commonjs'},path),source,path);}catch(e){parseErrors.push({path,message:e.message});}}
const demands=[...aggregate.values()].sort((a,b)=>a.api.localeCompare(b.api)).map(r=>({...r,files:[...r.files].sort(),environmentKeys:[...r.environmentKeys].sort()}));
const require=createRequire(import.meta.url),exports=[];
for(const id of TARGETS){const value=require('node:'+id);const ns=await import('node:'+id);exports.push({specifier:'node:'+id,node:process.version,namedESMExports:Object.keys(ns).sort(),cjsOwnEnumerableKeys:Object.keys(value).sort(),scope:'Host export-shape inventory only; no exported method invoked. Standard implementation availability is not inferred.'});}
for(const r of inputRows)assert.deepEqual(await desc(r.path),r);assert.deepEqual(await desc(input),reportBefore);assert.deepEqual(await Promise.all(parserFiles.map(desc)),parserBefore);
await save('input-hashes.json',{schemaVersion:1,report:reportBefore,compiledInputs:inputRows,parser:parserBefore,scope:'Exact406 retained compilation input files +host parser dependencies. Application sources were parsed, never imported/evaluated by this tool.'});
await save('node22-module-exports.json',{schemaVersion:1,node:process.version,modules:exports,hostOnly:true,exportedMethodsInvoked:false});
await save('ast-demand.json',{schemaVersion:1,state:'RETAINED_NEXT406_SOURCE_API_INVENTORY',report:reportBefore,compiledFiles:406,parsedFiles:406-parseErrors.length,sourceBytes:inputRows.reduce((n,r)=>n+r.bytes,0),astNodesVisited:nodeCount,parseErrors,observedBuiltinLoadSpellings:report.moduleSnapshot.builtins,observedPerMethodCalls:null,demands,qualifications:['Compiled-source membership and builtin loads are actual retained observations; AST call/read/write sites are syntactic demand only, including conditional/deferred code.','Scope-aware variable aliases and explicit SWC interop wrappers are tracked. Arbitrary wrappers, webpack numeric-module dataflow and dynamic properties can be missed; this is not an exhaustive capability/security proof.','No application/server/native compiler/target engine/guest was executed. Host parser native binding was loaded only for parsing.']});
console.log(JSON.stringify({files:406,parsed:406-parseErrors.length,errors:parseErrors.length,apis:demands.length,observedBuiltinLoads:report.moduleSnapshot.builtins.length,sourceOnly:true,applicationExecuted:false}));
