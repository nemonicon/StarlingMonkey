// Host parser and pure AST analysis only. Parsed React files are never imported.
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { findUnboundReferences } from './bindings.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),require=createRequire('/private/tmp/starling-node-compat/toolchain/package.json');
assert.equal(process.version,'v22.14.0');
const {parseAst}=await import(pathToFileURL(require.resolve('rolldown/parseAst')));
const selected=['process','global','require','__dirname','__filename','arguments'];
const fixtures=[
 ['bare-global','process;',['process']],
 ['provided-process-param','function f(process){return process.value;}',[]],
 ['provided-global-param','function f(global){return global.value;}',[]],
 ['local-does-not-protect-other-function','function f(process){return process;}function g(){return process;}',['process']],
 ['module-var-hoist','process;var process=1;',[]],
 ['module-let-tdz-is-bound','process;let process=1;',[]],
 ['nested-block-var-hoist','function f(){return process;{var process=1;}}',[]],
 ['block-let-no-leak','{let process=1;process;}process;',['process']],
 ['block-function-no-leak','{function process(){}process;}process;',['process']],
 ['function-declaration-hoist','function f(){return process;function process(){}}process;',['process']],
 ['function-expression-self-only','const x=function process(){return process;};process;',['process']],
 ['named-function-default','const x=function process(a=process){return a;};',[]],
 ['parameter-default-not-body-var','function f(x=process){var process=1;return process;}',['process']],
 ['parameter-default-not-body-function','function f(x=process){function process(){}return process;}',['process']],
 ['parameter-default-local-tdz','function f(process=process){return process;}',[]],
 ['destructuring-default-not-body-var','function f({x=process}={}){var process;return x;}',['process']],
 ['computed-binding-key','const {[process]:p}=value;',['process']],
 ['pattern-key-is-not-binding','const {process:local}=value;process;',['process']],
 ['pattern-shorthand-binding','const {process}=value;process;',[]],
 ['array-rest-binding','const [process,...global]=value;process;global;',[]],
 ['nested-object-rest-binding','const {x:{process},...global}=value;process;global;',[]],
 ['assignment-pattern-reference','({process}=value);',['process']],
 ['assignment-default-reference','({x:process=global}=value);',['process','global']],
 ['property-key-not-reference','({process:1,method(){return process;}});',['process']],
 ['property-shorthand-reference-once','({process});',['process']],
 ['computed-property-is-reference','({[process]:global});',['process','global']],
 ['member-key-versus-value','obj.process;obj[process];',['process']],
 ['import-default-binding',"import process from 'fixture';process;",[]],
 ['import-aliased-name',"import {process as local} from 'fixture';process;",['process']],
 ['import-local-name',"import {value as process} from 'fixture';process;",[]],
 ['import-namespace',"import * as global from 'fixture';global.process;",[]],
 ['external-reexport-no-local-ref',"export {process as global} from 'fixture';",[]],
 ['local-export-reference',"const process=1;export {process as global};",[]],
 ['default-export-expression','export default process;',['process']],
 ['catch-binding-no-leak','try{}catch(process){process;}process;',['process']],
 ['catch-destructuring','try{}catch({process:global}){global;}global;',['global']],
 ['for-let-no-leak','for(let process of values){process;}process;',['process']],
 ['for-var-hoists','for(var process of values){}process;',[]],
 ['for-header-closure','for(let process=0;process<1;process++){(()=>process)();}process;',['process']],
 ['for-assignment-reference','for({process}of values){}',['process']],
 ['switch-discriminant-outside-case-lexical','switch(process){case 1:let process=1;break;}',['process']],
 ['switch-var-hoist','switch(process){case 1:var process=1;break;}',[]],
 ['class-declaration-binding','class process{method(){return process;}}process;',[]],
 ['named-class-inner-only','const X=class process extends process{[process](){return process;}};process;',['process']],
 ['class-keys-and-fields','class X{process(){return process;}[global](){return global;}field=process;}',['process','global','global','process']],
 ['class-static-var-isolated','class X{static{var process=1;process;}static{process;}}',['process']],
 ['class-static-var-not-field-scope','class X{static{var process;}static field=process;}',['process']],
 ['private-property-not-identifier-ref','class X{#process=1;method(){return this.#process;}}',[]],
 ['label-not-identifier-ref','process:for(;;){break process;}',[]],
 ['normal-function-arguments','function f(){return arguments;}arguments;',['arguments']],
 ['arrow-inherits-arguments','function f(){return ()=>arguments;}',[]],
 ['top-arrow-arguments-unbound','const f=()=>arguments;',['arguments']],
 ['provided-require-is-lexically-bound','function f(require){return require("fixture");}',[]],
 ['computed-method-key-outer','const x={ [process](process){return process;} };',['process']],
 ['normal-getter-method','const x={get process(){return process;}};',['process']],
 ['unicode-ranges',"const π='€';process;",['process']],
 ['optional-member-key','obj?.process;process?.value;',['process']],
 ['typeof-global-is-reference','typeof process;',['process']],
 ['independent-nested-parameter','function f(process){return()=>process;}process;',['process']],
 ['nested-var-does-not-bind-parent','function f(){var global;}global;',['global']],
];
const rows=[];
for(const[id,source,expected]of fixtures){
 const ast=parseAst(source),before=structuredClone(ast),actual=findUnboundReferences(ast,new Set(selected));
 assert.deepEqual(actual.map(n=>n.name),expected,id);assert.deepEqual(ast,before,id+' does not mutate AST');
 for(const node of actual){assert.equal(node.type,'Identifier');assert.equal(source.slice(node.start,node.end),node.name,id+' exact Oxc ranges');}
 assert.deepEqual(findUnboundReferences(ast,selected),actual,id+' array and Set API');
 rows.push({id,source,expected,observed:actual.map(({name,start,end})=>({name,start,end})),passed:true});
}
// Real installed production sources are parsed as DATA, never evaluated. The
// React error-reporting branch has three genuine unbound process references.
const application='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-run-20261105-02/application';
const files=[
 {path:join(application,'node_modules/react/cjs/react.production.js'),expectedProcessReferences:3},
 {path:join(application,'node_modules/react-dom/cjs/react-dom-server.edge.production.js'),expectedProcessReferences:0},
];
const real=[];
for(const item of files){const bytes=await readFile(item.path),source=bytes.toString('utf8'),ast=parseAst(source,{},item.path),before=structuredClone(ast),actual=findUnboundReferences(ast,['process']);
 assert.equal(actual.length,item.expectedProcessReferences,item.path);assert.deepEqual(ast,before);
 real.push({...item,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,observed:actual.map(({name,start,end})=>({name,start,end})),parsedOnly:true,moduleImported:false});}
const output=join(HERE,'evidence');await mkdir(output);
const helper=await readFile(join(HERE,'bindings.mjs'));
const result={schemaVersion:1,state:'PURE_OXC_LEXICAL_BINDING_TESTS_PASSED',node:process.version,helperSha256:createHash('sha256').update(helper).digest('hex'),syntheticCases:rows.length,cases:rows,realSourceCases:real,
 realRendererLocalProcessClaim:false,realReactUnboundProcessPreserved:true,analyzedModulesExecuted:false,guestExecuted:false,nativeEngineExecuted:false,compilerInvoked:false};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify({state:result.state,syntheticCases:rows.length,realSourceCases:real.map(x=>({path:x.path,unboundProcess:x.observed.length})),helperSha256:result.helperSha256})+'\n');
