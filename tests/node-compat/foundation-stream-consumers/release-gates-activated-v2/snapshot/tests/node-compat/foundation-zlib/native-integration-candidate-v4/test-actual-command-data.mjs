// Same captured64 records, JavaScript grammar only. No compiler/engine/loader.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {validateCompileForcedInclude,validateSelectedCompileInput} from './compile-input.mjs';
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,4);assert(!process.env.NODE_OPTIONS);
const original=JSON.parse(await readFile(process.argv[2])),output=resolve(process.argv[3]);assert(output.startsWith('/tmp/starling-node-compat/'));await mkdir(output);
const selected=original.selectedCompileInput;validateSelectedCompileInput(selected);const checks=[];
assert.equal(original.actualCommandRecords.length,64);
for(const row of original.actualCommandRecords){assert.equal(validateCompileForcedInclude(row.tokens,selected),selected.requiredForcedInclude.path);checks.push(row.kind+':'+row.source);}
const base=original.actualCommandRecords[0].tokens,at=base.indexOf('-include');
for(const[name,tokens]of [['missing',[...base.slice(0,at),...base.slice(at+2)]],['extra',[...base,'-include',selected.requiredForcedInclude.path]],['other-root',[...base.slice(0,at+1),'/tmp/elsewhere/js-confdefs.h',...base.slice(at+2)]],['joined',[...base.slice(0,at),'-include'+selected.requiredForcedInclude.path,...base.slice(at+2)]],['PCH',[...base,'-include-pch','/tmp/not-a-pch']],['imacros',[...base,'-imacros','/tmp/not-a-header']]]){
 assert.throws(()=>validateCompileForcedInclude(tokens,selected));checks.push('negative:'+name);
}
const changed=structuredClone(selected);changed.requiredForcedInclude.sha256='0'.repeat(64);assert.throws(()=>validateCompileForcedInclude(base,changed));checks.push('changed pinned header hash');
for(const token of ['-Wp,-include,/tmp/not-a-header','-Xpreprocessor','-Xclang']){assert.throws(()=>validateCompileForcedInclude([...base,token],selected));checks.push('pass-through refused:'+token);}
const result={schemaVersion:1,state:'ACTUAL64_JS_COMPILE_INCLUDE_GRAMMAR_PASSED',count:checks.length,checks,compilerOrEngineOrGuestExecuted:false};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({checks:checks.length,actualCommands:64,output}));
