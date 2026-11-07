// Inert Source model only: the VM compiler is a spy, no imports are executed.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const paths=[new URL('../http-bridge-candidate-v1/module-host-provider.mjs',import.meta.url),new URL('./module-host-provider.mjs',import.meta.url)];
const sentinel=Symbol('inert-default-loader');
let checks=0;
for(let i=0;i<paths.length;i++) {
 const source=await readFile(paths[i],'utf8');
 const match=/compile\(source, filename\) \{([\s\S]*?)\n    \},/.exec(source);assert(match);
 const compiled=new Set();let recorded;
 const compileFunction=(...args)=>{recorded=args;return 'inert-return';};
 const body=new Function('compileFunction','compiled','vmConstants','source','filename',match[1]);
 assert.equal(body(compileFunction,compiled,{USE_MAIN_CONTEXT_DEFAULT_LOADER:sentinel},'inert-source','/owned/driver.cjs'),'inert-return');checks++;
 assert.deepEqual([...compiled],['/owned/driver.cjs']);checks++;
 assert.equal(recorded[0],'inert-source');checks++;
 assert.deepEqual(recorded[1],['exports','require','module','__filename','__dirname']);checks++;
 assert.equal(recorded[2].filename,'/owned/driver.cjs');checks++;
 assert.equal(Object.hasOwn(recorded[2],'importModuleDynamically'),i===1);checks++;
 if(i===1){assert.equal(recorded[2].importModuleDynamically,sentinel);checks++;}
}
console.log(JSON.stringify({sourceOnly:true,checks,actualVmCompilerOrDynamicImportOrFilesystemFixtureInvoked:false}));
