// HOST-ONLY AST inspection. Generated module is read as text, never imported.
import {readFile,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const sha=b=>createHash('sha256').update(b).digest('hex');
const [parserPath,gluePath,manifestPath]=process.argv.slice(2);
assert.equal(process.version,'v22.14.0');assert.equal(process.platform,'darwin');assert.equal(process.arch,'arm64');assert.deepEqual(process.execArgv,[]);
for(const key of Object.keys(process.env))assert(!key.startsWith('NAPI_RS_'));
for(const key of ['NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'])assert(!process.env[key]);
const manifest=JSON.parse(await readFile(manifestPath)),expected=new Map();
for(const r of manifest.files)expected.set(await realpath(r.path),r);
async function pin(path){const actual=await realpath(path),r=expected.get(actual);assert(r,'Authenticated parser closure row: '+actual);const b=await readFile(actual);assert.equal(b.length,r.bytes);assert.equal(sha(b),r.sha256);return{path:actual,sha256:r.sha256,bytes:r.bytes};}
const parser=await pin(parserPath),sourceBytes=await readFile(gluePath);
const {parseAst}=await import(pathToFileURL(parser.path));
const ast=parseAst(sourceBytes.toString('utf8'),{},gluePath);
assert.equal(ast.type,'Program');
const walk=(n,fn)=>{if(!n||typeof n!=='object')return;if(Array.isArray(n)){for(const x of n)walk(x,fn);return;}if(typeof n.type==='string')fn(n);for(const[k,v]of Object.entries(n))if(!['loc','range','parent'].includes(k))walk(v,fn);};
const imports=ast.body.filter(n=>n.type==='ImportDeclaration').map(n=>({source:n.source.value,bindings:n.specifiers.map(s=>({kind:s.type,imported:s.imported?.name??s.imported?.value??null,local:s.local.name}))}));
const functions=new Map(ast.body.filter(n=>n.type==='FunctionDeclaration').map(n=>[n.id.name,n]));
const exports=[];let helper=null;
for(const n of ast.body){
 assert(!['ExportDefaultDeclaration','ExportAllDeclaration'].includes(n.type));if(n.type!=='ExportNamedDeclaration')continue;assert(!n.source);
 for(const s of n.specifiers??[]){assert.equal(s.type,'ExportSpecifier');assert.equal(s.local.name,s.exported.name);const f=functions.get(s.local.name);assert(f&&!f.async&&!f.generator);exports.push({name:s.exported.name,kind:'function',arity:f.params.length});}
 if(n.declaration){const d=n.declaration;assert.equal(d.type,'VariableDeclaration');assert.equal(d.kind,'const');assert.equal(d.declarations.length,1);const x=d.declarations[0];assert.equal(x.id.name,'_util');assert.equal(x.init.type,'ObjectExpression');assert.equal(x.init.properties.length,0);assert.equal(n,ast.body.at(-1));helper=n;exports.push({name:'_util',kind:'terminal-empty-object'});}
}
for(const n of ast.body)if(n!==helper)walk(n,x=>assert(!(x.type==='Identifier'&&x.name==='_util')));
const dynamicImports=[],inlineModules=[],coreUrls=[];
walk(ast,n=>{
 if(n.type==='ImportExpression'){assert.equal(n.source.type,'Literal');dynamicImports.push(n.source.value);}
 if(n.type==='CallExpression'&&n.callee.type==='Identifier'&&n.callee.name==='base64Compile'){assert.equal(n.arguments.length,1);const a=n.arguments[0];assert.equal(a.type,'Literal');const b=Buffer.from(a.value,'base64');inlineModules.push({literalStart:a.start,literalEnd:a.end,sha256:sha(b),bytes:b.length});}
 if(n.type==='NewExpression'&&n.callee.type==='Identifier'&&n.callee.name==='URL'&&n.arguments[0]?.type==='Literal')coreUrls.push(n.arguments[0].value);
 if(n.type==='AssignmentExpression'||n.type==='UpdateExpression')walk(n.left??n.argument,x=>assert(!(x.type==='Identifier'&&x.name==='run')));
});
const awaitNames=ast.body.filter(n=>n.type==='ExpressionStatement'&&n.expression.type==='AwaitExpression').map(n=>n.expression.argument.name??null);
const require=createRequire(pathToFileURL(parser.path)),nativeBindings=[];
for(const path of Object.keys(require.cache))if(path.endsWith('.node'))nativeBindings.push(await pin(path));
process.stdout.write(JSON.stringify({schemaVersion:1,source:{path:gluePath,sha256:sha(sourceBytes),bytes:sourceBytes.length},parser,nativeBindings,parseOnly:true,generatedModuleImported:false,componentOrEngineInstantiated:false,imports,exports,dynamicImports,inlineModules,coreUrls,topLevelAwaitNames:awaitNames})+'\n');
