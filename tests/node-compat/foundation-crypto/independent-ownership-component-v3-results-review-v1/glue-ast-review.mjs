// Host parser only. Reads generated source as text; never imports it.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const base='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain';
const sourcePath='/private/tmp/starling-node-compat/crypto-owner355-component-v3/worker/transpiled/crypto_owner.js';
assert.equal(process.version,'v22.14.0');
const req=createRequire(base+'/package.json');
const parserPath=req.resolve('rolldown/parseAst');
const parserRaw=await readFile(parserPath);
const {parseAst}=await import(pathToFileURL(parserPath));
const raw=await readFile(sourcePath);
assert.equal(createHash('sha256').update(raw).digest('hex'),'a85846c12f52f2b995f12269ba7daf811e5d88ec244b333610fa65f251d4b715');
const ast=parseAst(new TextDecoder('utf-8',{fatal:true}).decode(raw),{},'crypto_owner.js');
assert.equal(ast.type,'Program');
const expected={inspect:0,run:1,clear:0,validate:0};
const functions=new Map(),exported=[];let helper=null;
for(const node of ast.body){
 const decl=node.type==='ExportNamedDeclaration'?node.declaration:node;
 if(decl?.type==='FunctionDeclaration'&&Object.hasOwn(expected,decl.id?.name)){
  assert(!functions.has(decl.id.name));assert(!decl.async&&!decl.generator);
  assert.equal(decl.params.length,expected[decl.id.name]);assert(decl.params.every(p=>p.type==='Identifier'));
  functions.set(decl.id.name,decl);
 }
}
for(const node of ast.body){
 assert(!['ImportDeclaration','ExportDefaultDeclaration','ExportAllDeclaration'].includes(node.type));
 if(node.type!=='ExportNamedDeclaration')continue;
 assert(!node.source&&!node.attributes?.length&&!node.assertions?.length);
 for(const e of node.specifiers??[]){
  assert.equal(e.type,'ExportSpecifier');assert.equal(e.local.type,'Identifier');assert.equal(e.exported.type,'Identifier');
  assert.equal(e.local.name,e.exported.name);assert(functions.has(e.local.name));exported.push(e.local.name);
 }
 if(node.declaration){
  const d=node.declaration;assert.equal(d.type,'VariableDeclaration');assert.equal(d.kind,'const');assert.equal(d.declarations.length,1);
  const v=d.declarations[0];assert.equal(v.id.type,'Identifier');assert.equal(v.id.name,'_util');assert.equal(v.init.type,'ObjectExpression');assert.equal(v.init.properties.length,0);
  assert(!helper);assert.equal(node,ast.body.at(-1));helper=node;exported.push('_util');
 }
}
assert.equal(functions.size,4);assert(helper);assert.deepEqual(exported.sort(),['_util','clear','inspect','run','validate']);
function walk(n,fn){if(!n||typeof n!=='object')return;if(Array.isArray(n)){for(const x of n)walk(x,fn);return;}fn(n);for(const[k,v]of Object.entries(n))if(!['loc','range','parent'].includes(k))walk(v,fn);}
const imports=[],urls=[];let count=0;
for(const node of ast.body){
 walk(node,n=>{
  count++;
  if(node!==helper)assert(!(n.type==='Identifier'&&n.name==='_util'));
  if(['AssignmentExpression','UpdateExpression'].includes(n.type))walk(n.left??n.argument,t=>assert(!(t.type==='Identifier'&&Object.hasOwn(expected,t.name))));
  if(n.type==='ImportExpression')imports.push(n.source?.value);
  if(n.type==='NewExpression'&&n.callee?.name==='URL')urls.push(n.arguments?.[0]?.value);
 });
}
assert.deepEqual(imports,['node:fs/promises']);assert.deepEqual(urls,['./crypto_owner.core.wasm']);
const topAwait=ast.body.filter(n=>n.type==='ExpressionStatement'&&n.expression?.type==='AwaitExpression');
assert.equal(topAwait.length,1);assert.equal(topAwait[0].expression.argument.type,'Identifier');assert.equal(topAwait[0].expression.argument.name,'$init');
const init=ast.body.find(n=>n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id?.name==='$init'));
assert(init&&ast.body.indexOf(init)<ast.body.indexOf(topAwait[0]));
const functionsOut=Object.fromEntries([...functions].map(([n,d])=>[n,{arity:d.params.length,async:d.async,generator:d.generator}]));
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_RETAINED_CRYPTO_GLUE_AST_AUDIT_PASSED',
 parserEntry:parserPath,parserEntrySha256:createHash('sha256').update(parserRaw).digest('hex'),sourcePath,
 sourceSha256:createHash('sha256').update(raw).digest('hex'),programSourceType:ast.sourceType,
 publicFunctions:functionsOut,publicJsNames:exported,helper:{name:'_util',terminal:true,literalEmptyObject:true,otherReferences:0},
 dynamicImports:imports,relativeCoreUrls:urls,topLevelAwait:'$init',astObjectNodesVisited:count,
 hostParserLibraryInvoked:true,generatedModuleImported:false,coreCompiledOrInstantiated:false,guestOrKeyExportCalled:false}));
