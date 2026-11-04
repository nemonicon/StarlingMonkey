// Pure source/data checks; generated glue is never evaluated by these functions.
import {need} from './authority.mjs';
export const NAMES=Object.freeze(['inspect','run','clear','validate']);
const ARITY=Object.freeze({inspect:0,run:1,clear:0,validate:0});
export function exactAbi(map){need(map&&Object.keys(map).length===4&&NAMES.every(n=>map[n]===(n==='run'?'(u32) -> string':'() -> string')),'Exactly four ordinary string functions');return true;}
export function parsePublicWit(text){
 need(typeof text==='string'&&Buffer.byteLength(text)<=1048576,'Bounded emitted WIT');const source=text.replace(/\/\/[^\n]*/g,'').replace(/\/\*[\s\S]*?\*\//g,'').trim();need(!/\bimport\b/.test(source),'Actual zero external imports');
 const world=/^package\s+root:component;\s*world\s+root\s*\{([\s\S]*)\}$/.exec(source);need(world,'Exact finite root world');const out={};
 for(const part of world[1].split(';').map(s=>s.trim()).filter(Boolean)){const m=/^export\s+([a-z]+):\s*func\(([^)]*)\)\s*->\s*string$/.exec(part);need(m&&!Object.hasOwn(out,m[1]),'Only unique ordinary scalar exports');const params=m[2].trim();need(!params||/^[a-z][a-z-]*:\s*u32$/.test(params),'Only run u32 parameter');out[m[1]]='('+(params?'u32':'')+') -> string';}exactAbi(out);return Object.freeze(out);
}
export function checkTranspileMetadata(value){need(value&&Array.isArray(value.imports)&&value.imports.length===0&&Array.isArray(value.exports)&&value.exports.length===4&&new Set(value.exports.map(v=>v[0])).size===4&&value.exports.every(v=>Array.isArray(v)&&v.length===2&&NAMES.includes(v[0])&&v[1]==='function'),'Actual zero-import four-function Jco metadata');return true;}
export function parsePublicDts(text){
 need(typeof text==='string'&&Buffer.byteLength(text)<=262144,'Bounded d.ts');const source=text.replace(/\/\/[^\n]*/g,'').replace(/\/\*[\s\S]*?\*\//g,'').trim(),parts=source.split(';').map(s=>s.trim()).filter(Boolean),out={};need(parts.length===4,'Four d.ts declarations only');
 for(const part of parts){const m=/^export\s+function\s+([a-z]+)\(([^)]*)\)\s*:\s*string$/.exec(part);need(m&&NAMES.includes(m[1])&&!Object.hasOwn(out,m[1]),'Expected declaration name/result');need(m[1]==='run'?/^[A-Za-z][A-Za-z0-9]*:\s*number$/.test(m[2].trim()):m[2].trim()==='','Exact declaration arity/types');out[m[1]]=m[1]==='run'?'(u32) -> string':'() -> string';}exactAbi(out);return Object.freeze(out);
}
function walk(v,visit){if(!v||typeof v!=='object')return;if(Array.isArray(v)){for(const x of v)walk(x,visit);return;}visit(v);for(const[k,x]of Object.entries(v))if(!['loc','range','parent'].includes(k))walk(x,visit);}
export function publicJSExports(ast){
 need(ast?.type==='Program'&&Array.isArray(ast.body),'Parser Program');const funcs=new Map(),exported=[];let helper=null;
 for(const node of ast.body){const d=node.type==='ExportNamedDeclaration'?node.declaration:node;if(d?.type==='FunctionDeclaration'&&NAMES.includes(d.id?.name)){need(!funcs.has(d.id.name)&&!d.async&&!d.generator&&d.params.length===ARITY[d.id.name]&&d.params.every(p=>p.type==='Identifier'),'Four unique sync ABI declarations');funcs.set(d.id.name,d);}}
 for(const node of ast.body){need(!['ExportDefaultDeclaration','ExportAllDeclaration'].includes(node.type),'No default/star export');if(node.type!=='ExportNamedDeclaration')continue;need(!node.source&&!node.attributes?.length&&!node.assertions?.length,'No reexports');
  for(const e of node.specifiers??[]){need(e.type==='ExportSpecifier'&&e.local?.type==='Identifier'&&e.exported?.type==='Identifier'&&e.local.name===e.exported.name&&funcs.has(e.local.name),'Only same-name actual function exports');exported.push(e.local.name);}
  const d=node.declaration;if(!d)continue;if(d.type==='FunctionDeclaration'){need(funcs.get(d.id?.name)===d,'Only four public funcs');exported.push(d.id.name);}else{need(!helper&&d.type==='VariableDeclaration'&&d.kind==='const'&&d.declarations.length===1&&d.declarations[0].id?.name==='_util'&&d.declarations[0].init?.type==='ObjectExpression'&&d.declarations[0].init.properties.length===0&&node===ast.body.at(-1),'Only terminal literal empty Jco helper');helper=node;exported.push('_util');}}
 need(funcs.size===4&&new Set(exported).size===exported.length&&NAMES.every(n=>exported.includes(n))&&(exported.length===4||exported.length===5&&helper),'Four callable ABI funcs; optional one empty non-WIT helper only');
 for(const node of ast.body){if(node!==helper)walk(node,n=>need(!(n.type==='Identifier'&&n.name==='_util'),'Helper has no other references'));walk(node,n=>{if(['AssignmentExpression','UpdateExpression'].includes(n.type))walk(n.left??n.argument,t=>need(!(t.type==='Identifier'&&NAMES.includes(t.name)),'No ABI reassignment'));});}
 return Object.freeze({names:Object.freeze(exported.sort()),abiFunctionNames:NAMES,helper:helper?Object.freeze({name:'_util',kind:'empty-ordinary-object',notWitExport:true}):null,generatedModuleImported:false});
}
export function componentOptions(d,wit){return{engine:d.engine.path,preview2Adapter:d.adapter.path,witWorld:wit,worldName:'validation',selectedInterfaces:[],disableFeatures:['stdio','random','clocks','http','fetch-event'],enableAot:false,env:{}};}
export function checkOwnedTerminal(v){need(v?.closed===true&&v.status===0&&v.signal===null&&v.ownedGroupGone===true&&v.terminalExitZeroObserved===true&&v.spawnError===null&&v.timedOut===false&&v.externalSignal===null&&v.outputLimitExceeded===false&&Array.isArray(v.errors)&&v.errors.length===0,'Actual owned child raw0/cleanup/full terminal required');return true;}
