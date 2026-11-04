// Pure inventory tests over a pinned, already captured graph; no bundler/action.
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {priorStockModules} from './stock-graph.mjs';
const here=dirname(fileURLToPath(import.meta.url)),source=join(here,'../measurement-execution-activated-v2/stock-source-graph.json');
const raw=await readFile(source),hash=x=>createHash('sha256').update(x).digest('hex');
assert.equal(hash(raw),'9afe8893edacd4333f6422fc2eaadb71ec28cba44127c08d1227064b9cd7e18d');
const graph=JSON.parse(raw),checks=[];
function ok(name,fn){fn();checks.push(name);}
function no(name,mutate){ok(name,()=>{const value=structuredClone(graph);mutate(value);assert.throws(()=>priorStockModules(value));});}
ok('actual graph has no provider key',()=>assert(!Object.hasOwn(graph,'provider')));
ok('exact real three guest rows remove only three IDs',()=>{const expected=graph.modules.filter(id=>!graph.sourceBeforeAfter.some(row=>row.path===id));assert.deepEqual(priorStockModules(graph),expected);assert.equal(expected.length,99);});
no('missing row',g=>g.sourceBeforeAfter.pop());
no('extra row',g=>g.sourceBeforeAfter.push(g.sourceBeforeAfter[0]));
no('duplicate row',g=>g.sourceBeforeAfter[2]=g.sourceBeforeAfter[0]);
no('wrong name',g=>g.sourceBeforeAfter[0].path=g.sourceBeforeAfter[0].path.replace('entry.mjs','other.mjs'));
no('relative ID',g=>g.sourceBeforeAfter[0].path='entry.mjs');
no('wrong digest type',g=>g.sourceBeforeAfter[0].sha256=null);
no('wrong byte count',g=>g.sourceBeforeAfter[0].bytes=-1);
no('extra row key',g=>g.sourceBeforeAfter[0].ignored=true);
no('physical digest mismatch',g=>g.physicalSources.find(r=>r.path===g.sourceBeforeAfter[0].path).sha256='0'.repeat(64));
no('physical row absent',g=>g.physicalSources=g.physicalSources.filter(r=>r.path!==g.sourceBeforeAfter[0].path));
no('physical duplicate',g=>g.physicalSources.push(g.physicalSources[0]));
no('module duplicate',g=>g.modules[0]=g.modules[1]);
no('module removed',g=>g.modules.pop());
no('invented row with missing actual module',g=>g.modules[g.modules.indexOf(g.sourceBeforeAfter[0].path)]='/unrelated/entry.mjs');
const output=resolve(process.argv[2]??'');assert(output.startsWith('/tmp/starling-node-compat/'));await mkdir(output,{recursive:false});
await writeFile(join(output,'results.json'),JSON.stringify({schemaVersion:1,state:'PURE_STOCK_INVENTORY_TESTS_PASSED',passed:checks.length,checks,actualGraph:{path:source,sha256:hash(raw),bytes:raw.length},actualGraphProviderKeyPresent:false,priorModuleCount:99,ownerActionsOrBundlerOrGuestExecuted:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:checks.length,output}));
