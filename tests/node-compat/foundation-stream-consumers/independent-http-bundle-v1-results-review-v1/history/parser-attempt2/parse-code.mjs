// Host source parser only. Never imports/evaluates the generated bundle.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
const HERE=dirname(fileURLToPath(import.meta.url));
const ROOT='/private/tmp/starling-node-compat/consumers355-http-bundle-v1/worker';
const parser='/private/tmp/starling-node-compat/native-toolchain-lock/node_modules/acorn/dist/acorn.mjs';
const parserBytes=await readFile(parser);assert.equal(createHash('sha256').update(parserBytes).digest('hex'),'1cbcbf252a5800e496dc505c706f309a9dd4e1789392e12963c77ae9497ff6f7');assert.equal(process.version,'v22.14.0');
const {parse}=await import(pathToFileURL(parser));
const raw=await readFile(join(ROOT,'http.bundle.mjs'));assert.equal(createHash('sha256').update(raw).digest('hex'),'ef1922514543fb6cb3dcc0aac7b2f98226357864a37b0c6bece35fcedc9b25a5');
const source=raw.toString('utf8'),ast=parse(source,{ecmaVersion:'latest',sourceType:'module'}),graph=JSON.parse(await readFile(join(ROOT,'bundle-graph.json')));
const imports=[],exports=[],nativeDefaults=new Map();
for(const n of ast.body){
 if(n.type==='ImportDeclaration'){
  if(!imports.includes(n.source.value))imports.push(n.source.value);
  for(const s of n.specifiers)if(s.type==='ImportDefaultSpecifier')nativeDefaults.set(s.local.name,n.source.value);
 }
 assert(!['ExportDefaultDeclaration','ExportAllDeclaration'].includes(n.type));
 if(n.type==='ExportNamedDeclaration'){assert(!n.source&&!n.declaration);for(const s of n.specifiers){assert.equal(s.local.name,s.exported.name);exports.push(s.exported.name);}}
}
assert.deepEqual(imports,graph.imports);assert.deepEqual(exports,['incomingHandler']);
assert(imports.every(s=>s.startsWith('node:')||s==='wasi:http/types@0.2.10'));
const funcs=new Map(ast.body.filter(n=>n.type==='FunctionDeclaration').map(n=>[n.id.name,n]));
for(const name of ['runConsumerHttpProbe','runClassic19','runJointChecks','createIncomingHandler'])assert(funcs.has(name));
const consumer=funcs.get('runConsumerHttpProbe');assert(consumer.async&&!consumer.generator&&consumer.params.length===0);
const generators=consumer.body.body.filter(n=>n.type==='FunctionDeclaration');assert.deepEqual(generators.map(n=>n.id.name),['utf8Chunks','jsonChunks']);assert(generators.every(n=>n.async&&n.generator&&n.params.length===0));
const yieldArg=n=>{assert.equal(n.type,'ExpressionStatement');assert.equal(n.expression.type,'YieldExpression');return n.expression.argument;};
const bytes=generators[0].body.body.map(n=>{const a=yieldArg(n);assert.equal(a.type,'NewExpression');assert.equal(a.callee.name,'Uint8Array');assert.equal(a.arguments.length,1);return a.arguments[0].elements.map(x=>x.value);});assert.deepEqual(bytes,[[226],[130,172]]);
assert.deepEqual(generators[1].body.body.map(n=>yieldArg(n).value),['{"consumer":','true}']);
const returned=consumer.body.body.at(-1);assert.equal(returned.type,'ReturnStatement');assert.equal(returned.argument.type,'ObjectExpression');
for(const name of ['text','json']){const prop=returned.argument.properties.find(p=>p.key.name===name);assert.equal(prop.value.type,'AwaitExpression');assert.equal(prop.value.argument.callee.name,name);}
const incoming=ast.body.flatMap(n=>n.type==='VariableDeclaration'?n.declarations:[]).find(n=>n.id.name==='incomingHandler');assert(incoming);assert.equal(incoming.init.callee.name,'createIncomingHandler');assert.equal(incoming.init.arguments.length,1);assert.equal(incoming.init.arguments[0].name,'runJointChecks');
function clean(n,{origin=false,rename={}}={}){
 if(Array.isArray(n))return n.map(v=>clean(v,{origin,rename}));if(!n||typeof n!=='object')return n;
 if(origin&&n.type==='CallExpression'&&n.callee.type==='Identifier'&&n.callee.name==='require')return{type:'NativeBuiltinReference',name:n.arguments[0].value.startsWith('node:')?n.arguments[0].value:'node:'+n.arguments[0].value};
 if(!origin&&n.type==='Identifier'&&nativeDefaults.has(n.name))return{type:'NativeBuiltinReference',name:nativeDefaults.get(n.name)};
 const o={};for(const[k,v]of Object.entries(n)){
  if(['start','end','loc','range','raw','sourceFile'].includes(k))continue;
  if(k==='value'&&n.regex)continue;
  o[k]=k==='name'&&n.type==='Identifier'&&Object.hasOwn(rename,v)?rename[v]:clean(v,{origin,rename});
 }return o;
}
const composerSource=await readFile(join(HERE,'derived-composer-data.mjs.txt'),'utf8');const comp=parse(composerSource,{ecmaVersion:'latest',sourceType:'module'}).body.find(n=>n.type==='ExportNamedDeclaration').declaration;
const actualComposer=funcs.get('createIncomingHandler');const originalName=actualComposer.body.body[0].argument.callee.name;
assert.deepEqual(clean(actualComposer),clean(comp,{rename:{original:originalName}}));
const cjsIds=graph.modules.filter(s=>s.endsWith('.cjs.native-profile.mjs'));
const cjsBodies=ast.body.filter(n=>n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'&&n.expression.callee.type==='MemberExpression'&&n.expression.callee.property.name==='call'&&n.expression.callee.object.type==='FunctionExpression'&&n.expression.callee.object.params.map(x=>x.name).join(',')==='module,exports');
assert.equal(cjsIds.length,9);assert.equal(cjsBodies.length,9);const cjs=[];
for(let i=0;i<9;i++){
 const original=cjsIds[i].slice(0,-'.native-profile.mjs'.length),bytes=await readFile(original),program=parse(bytes.toString('utf8'),{ecmaVersion:'latest',sourceType:'script'});
 assert.deepEqual(clean(cjsBodies[i].expression.callee.object.body.body),clean(program.body,{origin:true}));
 cjs.push({id:cjsIds[i],original,originalSha256:createHash('sha256').update(bytes).digest('hex'),bodyMatchesAfterLiteralNativeRequireLowering:true});
}
const dynamic=[];let astNodes=0;
function walk(n){if(!n||typeof n!=='object')return;if(Array.isArray(n)){for(const v of n)walk(v);return;}if(typeof n.type==='string')astNodes++;if(n.type==='ImportExpression')dynamic.push(n.source.type==='Literal'?{kind:'literal',source:n.source.value}:{kind:n.source.type,name:n.source.name??null});for(const[k,v]of Object.entries(n))if(!['loc','range','parent'].includes(k))walk(v);}
walk(ast);assert(dynamic.some(v=>v.kind==='Identifier'&&v.name==='id'));
assert(!/reference-kernel|buffer-facade|createBufferModule|hexEncode|hexDecode|__require/.test(source));
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_HTTP_WHOLE_BUNDLE_AST_PARSE_PASSED',parser,parserSha256:createHash('sha256').update(parserBytes).digest('hex'),bundleSha256:createHash('sha256').update(raw).digest('hex'),imports,exports,astNodes,dynamicImports:dynamic,
 consumerFixtureExactYieldsAndAwaitedNativeCalls:true,composerFullAstMatchesDerivedPinnedSource:true,cjsBodies:cjs,handlerRoutesWholeJointChecks:true,
 hostParserInvoked:true,generatedBundleImported:false,guestOrHostRequestsInvoked:false}));
