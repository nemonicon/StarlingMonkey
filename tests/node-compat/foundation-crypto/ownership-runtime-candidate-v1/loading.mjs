// Actual captured crypto_owner ESM/TLA protocol; no generated code at import.
import {dirname,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {descriptor,regular,need} from '../ownership-component-candidate-v1/authority.mjs';
import {NAMES,publicJSExports,parsePublicWit,parsePublicDts,checkTranspileMetadata} from '../ownership-component-candidate-v1/abi.mjs';
import {PARSER} from '../../foundation-zlib/cost-jco-correctness-candidate-v2/parser-tuple.mjs';
export {PARSER};
const ABI=[...NAMES].sort();
function walk(v,visit){if(!v||typeof v!=='object')return;if(Array.isArray(v)){for(const x of v)walk(x,visit);return;}visit(v);for(const[k,x]of Object.entries(v))if(!['loc','range','parent'].includes(k))walk(x,visit);}
export function validateGlue(ast){
 const checked=publicJSExports(ast),imports=[],urls=[],awaits=[];
 for(const n of ast.body){need(n.type!=='ImportDeclaration','No static imports in captured glue');if(n.type==='ExpressionStatement'&&n.expression?.type==='AwaitExpression')awaits.push(n.expression.argument);}
 walk(ast,n=>{if(n.type==='ImportExpression'){need(n.source?.type==='Literal'&&n.source.value==='node:fs/promises','Only observed Node loader import');imports.push(n);}if(n.type==='NewExpression'&&n.callee?.name==='URL')urls.push(n);});
 need(imports.length===1&&urls.length===1,'Exactly one builtin loader and one core URL');const u=urls[0],base=u.arguments?.[1];
 need(u.arguments.length===2&&u.arguments[0]?.type==='Literal'&&u.arguments[0].value==='./crypto_owner.core.wasm','Exact captured core name');
 need(base?.type==='MemberExpression'&&!base.computed&&base.property?.name==='url'&&base.object?.type==='MetaProperty'&&base.object.meta?.name==='import'&&base.object.property?.name==='meta','Actual import.meta.url base');
 need(awaits.length===1&&awaits[0]?.type==='Identifier'&&awaits[0].name==='$init','One real top-level await $init');
 need(JSON.stringify(checked.names)===JSON.stringify([...ABI,'_util'].sort()),'Actual four functions plus empty helper');return checked;
}
export function validateNamespace(ns){
 need(ns!==null&&typeof ns==='object'&&Object.getPrototypeOf(ns)===null,'Actual ESM namespace shape');
 need(JSON.stringify(Object.getOwnPropertyNames(ns).sort())===JSON.stringify([...ABI,'_util'].sort())&&!Object.hasOwn(ns,'then'),'Exact safe namespace names');
 for(const name of ABI)need(typeof ns[name]==='function'&&ns[name].length===(name==='run'?1:0),'Actual scalar function and arity '+name);
 const u=ns._util;need(u&&typeof u==='object'&&Object.getPrototypeOf(u)===Object.prototype&&Reflect.ownKeys(u).length===0,'Only empty ordinary helper');return true;
}
export function scalarArguments(name,args){need(ABI.includes(name)&&Array.isArray(args)&&args.length===(name==='run'?1:0),'Finite public scalar call');if(name==='run')need(Number.isSafeInteger(args[0])&&args[0]>=0&&args[0]<4&&!Object.is(args[0],-0),'Only ordinary case0..3; no coercion');return true;}
export async function auditLoading(rows){
 const r=Object.freeze(Object.fromEntries(['component','glue','core','dts','wit','transpileMetadata','packageJson'].map(k=>[k,descriptor(rows[k])])));
 need(r.glue.path.endsWith('/worker/transpiled/crypto_owner.js')&&r.core.path===join(dirname(r.glue.path),'crypto_owner.core.wasm')&&r.dts.path===join(dirname(r.glue.path),'crypto_owner.d.ts')&&r.packageJson.path===join(dirname(r.glue.path),'package.json'),'Exact actual relative loading tuple');
 const parser=descriptor(PARSER);for(const row of Object.values(r))await regular(row,{maxBytes:64*1024*1024});await regular(parser);
 need(new TextDecoder('utf-8',{fatal:true}).decode(await regular(r.packageJson))==='{\"type\":\"module\"}\n','Actual same-directory package bytes');
 parsePublicWit(new TextDecoder('utf-8',{fatal:true}).decode(await regular(r.wit)));parsePublicDts(new TextDecoder('utf-8',{fatal:true}).decode(await regular(r.dts)));checkTranspileMetadata(JSON.parse(await regular(r.transpileMetadata)));
 const {parse}=await import(pathToFileURL(parser.path));need(typeof parse==='function','Pinned Acorn parser');validateGlue(parse(new TextDecoder('utf-8',{fatal:true}).decode(await regular(r.glue)),{ecmaVersion:'latest',sourceType:'module'}));
 const recheck=async()=>{await regular(parser);for(const row of Object.values(r))await regular(row,{maxBytes:64*1024*1024});};await recheck();return Object.freeze({rows:r,recheck});
}
export async function loadSession(admitted){
 need(admitted?.parentAuditedActualComponent===true,'Actual source/artifact/Root admission before generated import');const captured=await auditLoading(admitted.artifacts);await admitted.recheck();
 const namespace=await import(pathToFileURL(captured.rows.glue.path));validateNamespace(namespace);await captured.recheck();await admitted.recheck();
 return Object.freeze({invoke(name,args){scalarArguments(name,args);return namespace[name](...args);},recheck:captured.recheck,initializationCompletedByModuleTLA:true,guestAsyncScalarExecutionProved:false});
}
