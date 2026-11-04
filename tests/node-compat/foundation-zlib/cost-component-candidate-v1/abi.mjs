// Pure scalar DATA ABI checks. No public guest export is invoked.
import {need} from './authority.mjs';
import {ABI,exactABI} from './collector.mjs';
export {wasmArgumentFeasibility} from './collector.mjs';
export const NAMES=Object.freeze(Object.keys(ABI));
export function parsePublicWit(text){
 need(typeof text==='string'&&text.length<=1024*1024,'Bounded actual emitted WIT');
 const source=text.replace(/\/\/[^\n]*/g,'').replace(/\/\*[\s\S]*?\*\//g,'').trim();
 need(!/\bimport\b/.test(source),'Actual component imports must be empty');
 const world=/^package\s+root:component;\s*world\s+root\s*\{([\s\S]*)\}\s*$/.exec(source);need(world,'Only finite public scalar root world');
 const declarations=world[1].trim().split(';').map(v=>v.trim()).filter(Boolean),exports={};
 for(const declaration of declarations){const match=/^export\s+([a-z]+):\s*func\(([^)]*)\)\s*->\s*(string)$/.exec(declaration);need(match,'No extra interface/type/resource or unknown public declaration');
  const [,name,params,result]=match;need(!Object.hasOwn(exports,name),'Unique public function');
  const types=params.trim()?params.split(',').map(param=>{const parsed=/^\s*[a-z][a-z-]*:\s*(u32|string)\s*$/.exec(param);need(parsed,'Only expected scalar parameter type');return parsed[1];}):[];
  exports[name]='('+types.join(',')+') -> '+result;
 }
 exactABI(exports,[]);return Object.freeze(exports);
}
export function checkTranspileMetadata(value){
 need(value&&Array.isArray(value.imports)&&value.imports.length===0&&Array.isArray(value.exports),'Actual Jco import/export metadata');
 need(value.exports.length===7&&new Set(value.exports.map(v=>v[0])).size===7&&value.exports.every(v=>Array.isArray(v)&&v.length===2&&NAMES.includes(v[0])&&v[1]==='function'),'Exactly seven transpiled public functions; no instances');return true;
}
export function checkOwnedTerminal(value){
 need(value?.closed===true&&value.status===0&&value.signal===null&&value.ownedGroupGone===true&&value.terminalExitZeroObserved===true,'Raw worker0 and owned cleanup required; not a correctness pass');
 need(value.spawnError===null&&value.timedOut===false&&value.externalSignal===null&&value.outputLimitExceeded===false&&Array.isArray(value.errors)&&value.errors.length===0,'Complete clean owned terminal, not status0 alone');return true;
}
export function publicJSExports(ast){
 need(ast?.type==='Program'&&Array.isArray(ast.body),'Actual parser Program');const names=[];
 for(const node of ast.body){
  if(node.type==='ExportDefaultDeclaration'||node.type==='ExportAllDeclaration')throw new Error('No default/star public glue exports');
  if(node.type!=='ExportNamedDeclaration')continue;need(!node.source,'No public glue re-export dependency');
  for(const item of node.specifiers??[]){const exported=item.exported;need(exported?.type==='Identifier'&&typeof exported.name==='string','Finite named glue export');names.push(exported.name);}
  if(node.declaration){const decl=node.declaration;if(decl.type==='FunctionDeclaration')names.push(decl.id?.name);else if(decl.type==='VariableDeclaration')for(const item of decl.declarations){need(item.id?.type==='Identifier','Finite public variable binding');names.push(item.id.name);}else throw new Error('Unknown public glue declaration');}
 }
 need(names.length===7&&new Set(names).size===7&&names.every(name=>NAMES.includes(name)),'Actual generated JS exposes exactly the seven declared names');return Object.freeze(names.sort());
}
