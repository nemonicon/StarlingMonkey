// Authorized host-only syntax/AST inspection. Never imports the generated JS.
import { readFileSync, realpathSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';
const here=dirname(fileURLToPath(import.meta.url));
const source=join(here,'../combined-native-component-caller-candidate-v1');
const refs=JSON.parse(readFileSync(join(source,'references.json')));
const sha=b=>createHash('sha256').update(b).digest('hex');
const node=refs.node,actualNode=readFileSync(process.execPath);
assert.equal(realpathSync(process.execPath),node.path);
assert.equal(actualNode.length,node.bytes);assert.equal(sha(actualNode),node.sha256);
const inventory=JSON.parse(readFileSync(refs.packageInventory.path));
assert.equal(sha(readFileSync(refs.packageInventory.path)),refs.packageInventory.sha256);
const require=createRequire(join(refs.loaderPackageRoot,'package.json'));
const parser=require.resolve('acorn');
const pin=inventory.package.files.find(r=>r.path===parser);
assert(pin,'Parser is a member of the already fully authenticated private package');
const parserBytes=readFileSync(parser);assert.equal(parserBytes.length,pin.bytes);assert.equal(sha(parserBytes),pin.sha256);
const {parse}=require('acorn');
const root=JSON.parse(readFileSync(join(here,'../combined-native-component-v1-construct-resource-root-results.json')));
const glue=root.allGeneratedFiles.find(r=>r.path.endsWith('/combined_resource.js'));
const bytes=readFileSync(glue.path);assert.equal(bytes.length,glue.bytes);assert.equal(sha(bytes),glue.sha256);
const ast=parse(bytes.toString('utf8'),{ecmaVersion:'latest',sourceType:'module'});
const imports=[],bindings=[],dynamic=[],urls=[],functions=[],exports=[],inline=[];
function visit(n){
 if(!n||typeof n!=='object')return;
 if(n.type==='ImportDeclaration'){imports.push(n.source.value);bindings.push({source:n.source.value,names:n.specifiers.map(s=>({imported:s.imported.name,local:s.local.name}))});}
 if(n.type==='ImportExpression')dynamic.push(n.source.value);
 if(n.type==='CallExpression'&&n.callee.type==='Identifier'&&n.callee.name==='base64Compile'){assert.equal(n.arguments.length,1);const b=Buffer.from(n.arguments[0].value,'base64');inline.push({bytes:b.length,sha256:sha(b)});}
 if(n.type==='NewExpression'&&n.callee.type==='Identifier'&&n.callee.name==='URL')urls.push(n.arguments[0]?.value);
 if(n.type==='FunctionDeclaration'&&['inspect','run','validate'].includes(n.id?.name))functions.push({name:n.id.name,params:n.params.length,async:n.async,generator:n.generator});
 if(n.type==='ExportNamedDeclaration'){
  for(const s of n.specifiers)exports.push({name:s.exported.name,local:s.local.name,kind:'specifier'});
  if(n.declaration){assert.equal(n.declaration.type,'VariableDeclaration');for(const d of n.declaration.declarations){assert.equal(d.id.name,'_util');assert.equal(d.init.type,'ObjectExpression');assert.deepEqual(d.init.properties,[]);exports.push({name:d.id.name,kind:'exact-empty-helper'});}}
 }
 for(const value of Object.values(n)){
  if(Array.isArray(value)){for(const x of value)visit(x);}
  else if(value&&typeof value==='object')visit(value);
 }
}
visit(ast);
assert.deepEqual(imports,['wasi:clocks/monotonic-clock','wasi:clocks/wall-clock','wasi:io/poll']);assert.deepEqual(dynamic,['node:fs/promises']);
assert.deepEqual(urls,['./combined_resource.core.wasm']);
assert.deepEqual(functions,[{name:'inspect',params:0,async:false,generator:false},{name:'run',params:1,async:false,generator:false},{name:'validate',params:0,async:false,generator:false}]);
assert.deepEqual(exports,[{name:'inspect',local:'inspect',kind:'specifier'},{name:'run',local:'run',kind:'specifier'},{name:'validate',local:'validate',kind:'specifier'},{name:'_util',kind:'exact-empty-helper'}]);
const graph=JSON.parse(readFileSync(join(here,'binary-graph.json')));assert.deepEqual(inline,graph.nestedCores.slice(1).map(m=>({bytes:m.moduleBytes,sha256:m.moduleSha256})));
assert.deepEqual(bindings,[{source:imports[0],names:[{imported:'now',local:'now'},{imported:'subscribeDuration',local:'subscribeDuration'},{imported:'subscribeInstant',local:'subscribeInstant'}]},{source:imports[1],names:[{imported:'now',local:'now$1'}]},{source:imports[2],names:[{imported:'Pollable',local:'Pollable'},{imported:'poll',local:'poll'}]}]);
const awaitInit=ast.body.filter(n=>n.type==='ExpressionStatement'&&n.expression.type==='AwaitExpression'&&n.expression.argument.type==='Identifier'&&n.expression.argument.name==='$init');
assert.equal(awaitInit.length,1);
console.log(JSON.stringify({schemaVersion:1,state:'RESOURCE_GENERATED_GLUE_HOST_AST_PASSED',parser:{path:parser,sha256:pin.sha256,bytes:pin.bytes},glue,staticImports:imports,staticImportBindings:bindings,inlineWasm: inline,dynamicHostLoaderImports:dynamic,relativeCoreUrls:urls,publicFunctions:functions,jsExports:exports,topLevelAwaitInit:true,generatedModuleImported:false,guestInstantiatedOrInvoked:false}));
