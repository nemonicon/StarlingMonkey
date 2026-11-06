// Optional production npm-package packaging. The original finite profile
// bundler remains unchanged. This adds no guest builtin or host capability.
import { createHash } from 'node:crypto';
import { builtinModules } from 'node:module';
import { isAbsolute } from 'node:path';
import { pathToFileURL } from 'node:url';
import { builtinMap } from './module-selection.mjs';
import {findUnboundReferences} from './frameworks/package-bundler-bindings-v2/bindings.mjs';
import {runtimeReferenceAudit} from './package-environment-guards.mjs';

export const PACKAGE_BUNDLER_VERSION = 'sm-production-package-bundler-v2';
// Prefix-only names such as node:test must not reserve an unrelated npm "test".
const nodeBuiltins = new Set(builtinModules);
const digest = code => createHash('sha256').update(code).digest('hex');
function refusal(message) { const error=new Error(message); error.code='ERR_SM_PACKAGE_BUNDLE_UNSUPPORTED'; throw error; }
function walk(node, visitor, parent=null, key='') {
  if(!node || typeof node!=='object')return;
  if(typeof node.type==='string')visitor(node,parent,key);
  for(const [field,value] of Object.entries(node)) {
    if(field==='parent')continue;
    if(Array.isArray(value))for(const child of value)walk(child,visitor,node,field);
    else if(value && typeof value==='object')walk(value,visitor,node,field);
  }
}
function names(pattern, result=[]) {
  if(!pattern)return result;
  if(pattern.type==='Identifier')result.push(pattern.name);
  else if(pattern.type==='RestElement')names(pattern.argument,result);
  else if(pattern.type==='AssignmentPattern')names(pattern.left,result);
  else if(pattern.type==='ArrayPattern')for(const value of pattern.elements)names(value,result);
  else if(pattern.type==='ObjectPattern')for(const value of pattern.properties)names(value.value??value.argument,result);
  return result;
}
function propertyKey(node,parent,key) {
  return key==='key' && !parent?.computed && ['Property','MethodDefinition','PropertyDefinition'].includes(parent?.type) ||
    key==='property' && parent?.type==='MemberExpression' && !parent.computed ||
    key==='exported' && parent?.type==='ExportSpecifier';
}

export async function bundlePackages({rolldown,parseAst,require:toolRequire,input,builtinManifests}) {
  if(!Array.isArray(builtinManifests) || !builtinManifests.length)refusal('Explicit compiled native manifests are required');
  const admitted=builtinMap(builtinManifests), sourceInputs=new Map(), decisions=[];
  if(typeof toolRequire?.resolve!=='function')refusal('Use the pinned loadToolchain result');
  const {esmExternalRequirePlugin}=await import(pathToFileURL(toolRequire.resolve('rolldown/plugins')));
  const canonicalNatives=[...new Set(Object.values(admitted))];
  const plugin={
    name:PACKAGE_BUNDLER_VERSION,
    resolveId(source,importer) {
      if(Object.hasOwn(admitted,source)) {
        decisions.push({source,importer:importer??null,canonical:admitted[source],kind:'native-external'});
        // The builtin plugin must own its externals. An early external:true
        // would bypass its required CJS-default bridge and leave runtime require.
        return null;
      }
      if(source.startsWith('node:') || nodeBuiltins.has(source))refusal(`Node builtin is not admitted by this profile: ${source}`);
      if(/^(?:jco:|wasmcloud:)/.test(source))refusal(`Nonstandard host adapter is not admitted: ${source}`);
      if(/\.(?:node|wasm)(?:\?|$)/.test(source))refusal(`Native addon or executable asset is outside this package contract: ${source}`);
      return null;
    },
    transform(code,id) {
      if(id.startsWith('\0'))return null;
      sourceInputs.set(id,{id,kind:isAbsolute(id)?'filesystem-module-transform-input':'generated-module-transform-input',transformInputSha256:digest(code),transformInputBytes:Buffer.byteLength(code),transformInputCode:isAbsolute(id)?undefined:code});
      if(id.endsWith('.json')) { JSON.parse(code); return null; }
      const ast=parseAst(code,{},id), replacements=[];
      const implicitModule=new Set(findUnboundReferences(ast,['module']));
      let shadowed=false;
      walk(ast,(node,parent,key)=>{
        let bindings=[];
        if(node.type==='VariableDeclarator')bindings=names(node.id);
        if(/^(?:FunctionDeclaration|FunctionExpression|ArrowFunctionExpression)$/.test(node.type))bindings=[node.id?.name,...node.params.flatMap(p=>names(p))];
        if(['ImportSpecifier','ImportDefaultSpecifier','ImportNamespaceSpecifier'].includes(node.type))bindings=[node.local.name];
        if(node.type==='CatchClause')bindings=names(node.param);
        if(bindings.includes('require'))shadowed=true;
        if(node.type==='CallExpression' && node.callee.type==='Identifier' && node.callee.name==='require') {
          const arg=node.arguments[0];
          if(node.optional || node.arguments.length!==1 || arg.type!=='Literal' || typeof arg.value!=='string')refusal(`Only literal package or native require is supported: ${id}`);
          if(Object.hasOwn(admitted,arg.value)) {
            decisions.push({source:arg.value,importer:id,canonical:admitted[arg.value],kind:'native-require-default'});
            if(arg.value!==admitted[arg.value])replacements.push({start:arg.start,end:arg.end,canonical:admitted[arg.value]});
          }
        }
        if(node.type==='Identifier' && node.name==='require' && !propertyKey(node,parent,key) &&
          !(parent?.type==='CallExpression' && key==='callee'))refusal(`require aliases, resolution and runtime loader state are unsupported: ${id}`);
        if(node.type==='Identifier' && implicitModule.has(node)) {
          const exported=parent?.type==='MemberExpression' && key==='object' &&
            ((!parent.computed && parent.property.name==='exports') || (parent.computed && parent.property.value==='exports'));
          const existenceProbe=parent?.type==='UnaryExpression' && parent.operator==='typeof' && key==='argument';
          if(!exported && !existenceProbe)refusal(`CommonJS module aliases and loader state are unsupported: ${id}`);
        }
        if(['ImportDeclaration','ExportNamedDeclaration','ExportAllDeclaration'].includes(node.type) && node.source &&
          Object.hasOwn(admitted,node.source.value) && node.source.value!==admitted[node.source.value])
          replacements.push({start:node.source.start,end:node.source.end,canonical:admitted[node.source.value]});
      });
      if(shadowed)refusal(`Shadowed require is outside the package contract: ${id}`);
      if(!replacements.length)return null;
      for(const row of replacements.sort((a,b)=>b.start-a.start))code=code.slice(0,row.start)+JSON.stringify(row.canonical)+code.slice(row.end);
      return {code,map:null};
    },
  };
  const build=await rolldown({input,platform:'neutral',
    resolve:{mainFields:['main','module'],conditionNames:['node']},
    transform:{define:{'process.env.NODE_ENV':JSON.stringify('production')}},
    treeshake:true,plugins:[plugin,esmExternalRequirePlugin({external:canonicalNatives})]});
  try {
    const generated=await build.generate({format:'esm',codeSplitting:false,externalLiveBindings:true});
    if(generated.output.length!==1 || generated.output[0].type!=='chunk')refusal('Exactly one ESM output chunk is required');
    const chunk=generated.output[0], allowed=new Set(Object.values(admitted)), moduleIds=Object.keys(chunk.modules??{});
    if(chunk.imports.some(id=>!allowed.has(id)))refusal(`Unexpected residual import: ${chunk.imports.join(',')}`);
    if(moduleIds.some(id=>/node_modules\/(?:buffer|unenv|jco-std)(?:\/|$)|node-builtins/.test(id)))refusal('JavaScript builtin adapter leaked into package graph');
    const outputAst=parseAst(chunk.code), environment=runtimeReferenceAudit(outputAst);
    const residual=environment.blocked.map(node=>node.name);
    walk(outputAst,node=>{if(node.type==='ImportExpression')residual.push('dynamic-import');});
    if(residual.length)refusal(`Unprovided runtime loader/environment references: ${[...new Set(residual)].join(',')}`);
    return {version:PACKAGE_BUNDLER_VERSION,code:chunk.code,imports:chunk.imports,moduleIds,
      admittedBuiltins:[...allowed].sort(),sourceInputs:[...sourceInputs.values()].sort((a,b)=>a.id.localeCompare(b.id)),decisions,
      policy:{nodeEnv:'production',platform:'neutral',conditions:['node'],nativeRequire:'canonical ESM default',
        runtimeRequireProvided:false,processShimProvided:false,builtinAdapters:false,filenameGlobalsProvided:false,hostCapabilitiesAdded:false,
        optionalEnvironmentGuards:'original typeof/recognized if-and-or branches, lexical bindings respected',
        reflection:'ordinary JS property access; no exhaustive static loader-alias analysis or security-sandbox claim',
        packageNamedBindings:'Rolldown live binding behavior may differ from Node CJS snapshots',
        sourceLedger:'plugin transform input hashes, not complete physical dependency or package-resolution closure'}};
  }finally{await build.close();}
}
