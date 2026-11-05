// Actual observed ESM/TLA protocol. Never imported/evaluated generated glue here
// until a future admitted worker explicitly calls loadReviewedSession.
import {dirname,join} from 'node:path';
import {nValue} from './planner.mjs';
import {pathToFileURL} from 'node:url';
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {need} from '../cost-jco-correctness-candidate-v2/transport.mjs';
import {NAMES,publicJSExports,parsePublicDts,parsePublicWit,checkTranspileMetadata} from '../cost-jco-correctness-candidate-v2/glue-policy.mjs';
import {PARSER} from '../cost-jco-correctness-candidate-v2/parser-tuple.mjs';
export {PARSER};
export const ABI_NAMES=Object.freeze([...NAMES].sort());
function walk(v,visit){if(!v||typeof v!=='object')return;if(Array.isArray(v)){for(const item of v)walk(item,visit);return;}visit(v);for(const[k,item]of Object.entries(v))if(!['loc','range','parent'].includes(k))walk(item,visit);}
export function validateGlueProgram(ast){
 const checked=publicJSExports(ast); // exact seven sync funcs + terminal empty_util
 const imports=[],urls=[],topAwaits=[];
 for(const node of ast.body){need(node.type!=='ImportDeclaration','No static JS imports in this observed glue mode');if(node.type==='ExpressionStatement'&&node.expression?.type==='AwaitExpression')topAwaits.push(node.expression.argument);}
 walk(ast,node=>{if(node.type==='ImportExpression'){need(node.source?.type==='Literal'&&node.source.value==='node:fs/promises','Only observed Node builtin filesystem dynamic import');imports.push(node.source.value);}if(node.type==='NewExpression'&&node.callee?.type==='Identifier'&&node.callee.name==='URL')urls.push(node);});
 need(imports.length===1&&urls.length===1,'Exactly one core URL/Node builtin loader import');const url=urls[0];
 need(url.arguments?.length===2&&url.arguments[0]?.type==='Literal'&&url.arguments[0].value==='./codec_cost.core.wasm','Exact observed same-directory core filename');
 const base=url.arguments[1];need(base?.type==='MemberExpression'&&!base.computed&&base.property?.name==='url'&&base.object?.type==='MetaProperty'&&base.object.meta?.name==='import'&&base.object.property?.name==='meta','Exact import.meta.url core base');
 need(topAwaits.length===1&&topAwaits[0]?.type==='Identifier'&&topAwaits[0].name==='$init','Actual one top-level await $init protocol');
 need(!checked.names.includes('then'),'No namespace then export before dynamic import assimilation');
 return Object.freeze({...checked,coreRelativePath:'codec_cost.core.wasm',nodeBuiltinLoader:'node:fs/promises',topLevelInitializationAwaited:true});
}
export function validateNamespace(ns){
 need(ns!==null&&typeof ns==='object','Actual ESM namespace');const names=Object.getOwnPropertyNames(ns).sort();need(JSON.stringify(names)===JSON.stringify([...ABI_NAMES,'_util'].sort()),'Runtime names match seven ABI funcs plus explicit empty helper');need(!Object.hasOwn(ns,'then'),'No callable namespace then');
 for(const name of ABI_NAMES)need(typeof ns[name]==='function','Actual synchronous declared function binding '+name);
 const util=ns._util;need(util!==null&&typeof util==='object'&&Object.getPrototypeOf(util)===Object.prototype&&Reflect.ownKeys(util).length===0,'Runtime helper remains empty ordinary object');
 return true;
}
export function scalarArguments(name,args){
 need(['identity','setup','batch','checkpoint'].includes(name)&&Array.isArray(args),'Measured worker exposes identity/setup/batch/checkpoint only; never observe/stage/validate');
 const arity={identity:0,setup:1,batch:2,checkpoint:0};need(args.length===arity[name],'Exact scalar arity');
 for(const value of args)need(Number.isSafeInteger(value)&&value>=0&&value<=0xffffffff&&!Object.is(value,-0),'Exact u32 scalar; no coercion');
 if(name==='setup')need(args[0]<30,'Thirty original primary IDs');
 if(name==='batch'){need(args[0]<120,'Original codec/control ranges');if(args[0]<30)nValue(args[0],args[1]);else need(args[1]===1,'Controls remain exactly N1');}
}
export function validatePackageBytes(bytes){need(new TextDecoder('utf-8',{fatal:true}).decode(bytes)==='{\"type\":\"module\"}\n','Exact cf31 source-written same-directory ESM package classification');return true;}
export function captureArtifactRows(artifact){
 need(artifact?.parentAuditedActualComponent===true,'Parent actual-artifact admission required');return Object.freeze(Object.fromEntries(['component','glue','core','dts','wit','transpileMetadata','packageJson'].map(name=>[name,descriptor(artifact[name])])));
}
export async function loadTimingSession(artifact){
 // Capture descriptor primitives BEFORE the first await. Caller mutation cannot
 // redirect this loader or its recheck. Actual parent proof admission is required.
 const rows=captureArtifactRows(artifact);
 need(rows.core.path===join(dirname(rows.glue.path),'codec_cost.core.wasm')&&rows.dts.path===join(dirname(rows.glue.path),'codec_cost.d.ts')&&rows.glue.path.endsWith('/transpiled/codec_cost.js')&&rows.packageJson.path===join(dirname(rows.glue.path),'package.json'),'Actual observed relative core/d.ts/glue tuple');
 const parserRow=descriptor(PARSER);for(const row of Object.values(rows))await regular(row,{maxBytes:64*1024*1024});await regular(parserRow);
 validatePackageBytes(await regular(rows.packageJson));
 const glue=new TextDecoder('utf-8',{fatal:true}).decode(await regular(rows.glue)),dts=new TextDecoder('utf-8',{fatal:true}).decode(await regular(rows.dts));parsePublicWit(new TextDecoder('utf-8',{fatal:true}).decode(await regular(rows.wit)));checkTranspileMetadata(JSON.parse(await regular(rows.transpileMetadata)));parsePublicDts(dts);
 const parser=await import(pathToFileURL(parserRow.path).href);need(typeof parser.parse==='function','Pinned actual Acorn parse export');validateGlueProgram(parser.parse(glue,{ecmaVersion:'latest',sourceType:'module'}));
 const recheck=async()=>{await regular(parserRow);for(const row of Object.values(rows))await regular(row,{maxBytes:64*1024*1024});};await recheck();
 // This is the actual observed standard direct ESM/TLA entry, not a guessed
 // instantiate(imports) API. A fresh owned Node process supplies each fresh case.
 const namespace=await import(pathToFileURL(rows.glue.path).href);validateNamespace(namespace);await recheck();
 return Object.freeze({invoke(name,args){scalarArguments(name,args);return namespace[name](...args);},recheck,generatedModuleImported:true,initializationCompletedByModuleTLA:true,externalWasiImports:[],engineResetOrCrossProcessReuseClaim:false});
}
