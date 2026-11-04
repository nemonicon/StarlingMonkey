// Parse generated source as DATA. Never import/evaluate generated glue.
import {need} from './authority.mjs';
import {NAMES} from '../cost-component-candidate-v1/abi.mjs';
export {NAMES,parsePublicWit,checkTranspileMetadata,checkOwnedTerminal,wasmArgumentFeasibility} from '../cost-component-candidate-v1/abi.mjs';
const ARITY=Object.freeze({identity:0,setup:1,observe:1,batch:2,checkpoint:0,stage:1,validate:1});
function walk(value,visit){
 if(!value||typeof value!=='object')return;
 if(Array.isArray(value)){for(const item of value)walk(item,visit);return;}
 visit(value);for(const [key,item]of Object.entries(value))if(!['parent','loc','range'].includes(key))walk(item,visit);
}
function exactFunction(node,name){
 need(node?.type==='FunctionDeclaration'&&node.id?.name===name&&!node.async&&!node.generator&&Array.isArray(node.params)&&node.params.length===ARITY[name]&&node.params.every(p=>p.type==='Identifier'),'Actual seven same-name synchronous function declarations with exact scalar arities');
}
export function publicJSExports(ast){
 need(ast?.type==='Program'&&Array.isArray(ast.body),'Actual parser Program');
 const functions=new Map(),exported=[],allBindings=new Map();let helper=null;
 // Count top-level bindings independently of the public export names.
 const binding=(name,node)=>{need(typeof name==='string'&&!allBindings.has(name),'Unique top-level public binding');allBindings.set(name,node);};
 for(const node of ast.body){
  const declaration=node.type==='ExportNamedDeclaration'?node.declaration:node;
  if(declaration?.type==='FunctionDeclaration'&&NAMES.includes(declaration.id?.name)){
   const name=declaration.id.name;binding(name,declaration);exactFunction(declaration,name);functions.set(name,declaration);
  }else if(declaration?.type==='VariableDeclaration')for(const item of declaration.declarations??[]){
   if(item.id?.type==='Identifier'&&(NAMES.includes(item.id.name)||item.id.name==='_util'))binding(item.id.name,item);
  }
 }
 for(const node of ast.body){
  need(node.type!=='ExportDefaultDeclaration'&&node.type!=='ExportAllDeclaration','No default/star public glue exports');
  if(node.type!=='ExportNamedDeclaration')continue;
  need(!node.source&&!node.attributes?.length&&!node.assertions?.length,'No public glue re-export dependency');
  for(const item of node.specifiers??[]){
   need(item.type==='ExportSpecifier'&&item.exported?.type==='Identifier'&&item.local?.type==='Identifier'&&item.exported.name===item.local.name&&NAMES.includes(item.exported.name),'Only same-name ABI function specifiers; no then, aliases or unknown helpers');
   exactFunction(functions.get(item.local.name),item.local.name);exported.push(item.exported.name);
  }
  if(!node.declaration)continue;
  const d=node.declaration;
  if(d.type==='FunctionDeclaration'){
   need(NAMES.includes(d.id?.name),'Only named ABI public functions');exactFunction(d,d.id.name);exported.push(d.id.name);continue;
  }
  need(d.type==='VariableDeclaration'&&d.kind==='const'&&d.declarations?.length===1,'Only one exact const helper declaration');
  const item=d.declarations[0];need(!helper&&item.id?.type==='Identifier'&&item.id.name==='_util'&&item.init?.type==='ObjectExpression'&&item.init.properties?.length===0,'Only literal empty ordinary-object _util helper');
  need(node===ast.body.at(-1),'The empty helper is the terminal top-level declaration');helper=node;exported.push('_util');
 }
 need(functions.size===7&&exported.length===8&&new Set(exported).size===8&&NAMES.every(name=>exported.includes(name))&&helper,'Seven ABI functions plus exactly one explicit empty _util helper');
 // No earlier or later mutation/escape of the helper; do not infer emptiness
 // from its initializer while accepting another reference that changes it.
 for(const node of ast.body){
  if(node!==helper)walk(node,n=>need(!(n.type==='Identifier'&&n.name==='_util'),'No other _util references/bindings'));
  walk(node,n=>{
   if(n.type==='AssignmentExpression'||n.type==='UpdateExpression'){
    const target=n.type==='AssignmentExpression'?n.left:n.argument;
    walk(target,t=>need(!(t.type==='Identifier'&&NAMES.includes(t.name)),'No reassignment/update of ABI function bindings'));
   }
  });
 }
 return Object.freeze({names:Object.freeze(exported.sort()),abiFunctionNames:Object.freeze([...NAMES].sort()),glueHelpers:Object.freeze([Object.freeze({name:'_util',role:'jco-generated-non-callable-helper',declarationKind:'const',initializer:'empty-ordinary-object-literal',declaredProperties:0,otherReferences:0,terminalTopLevelDeclaration:true,notWitExport:true})])});
}
export function parsePublicDts(text){
 need(typeof text==='string'&&Buffer.byteLength(text,'utf8')<=262144,'Bounded declaration source');
 const source=text.replace(/\/\/[^\n]*/g,'').replace(/\/\*[\s\S]*?\*\//g,'').trim(),parts=source.split(';').map(s=>s.trim()).filter(Boolean),out={};
 need(parts.length===7,'Exactly seven public declaration functions; glue helper is not a declared WIT function');
 for(const part of parts){
  const m=/^export\s+function\s+([a-z]+)\(([^)]*)\)\s*:\s*string$/.exec(part);need(m&&NAMES.includes(m[1])&&!Object.hasOwn(out,m[1]),'Only exact scalar function declarations');
  const types=m[2].trim()?m[2].split(',').map(p=>{const r=/^\s*[A-Za-z][A-Za-z0-9]*\s*:\s*(number|string)\s*$/.exec(p);need(r,'Only actual declaration scalar parameters');return r[1];}):[];
  need(types.length===ARITY[m[1]]&&types.every(t=>t===(['stage','validate'].includes(m[1])?'string':'number')),'Exact declaration arity/types');out[m[1]]='('+types.join(',')+') -> string';
 }
 return Object.freeze(out);
}
