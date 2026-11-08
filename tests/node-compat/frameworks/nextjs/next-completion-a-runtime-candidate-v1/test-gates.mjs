// Evaluate only the actual isolated final expressions against inert DATA.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const native=fileURLToPath(new URL('./run-contracts.mjs',import.meta.url));
const stock=fileURLToPath(new URL('../next-portable-cache-stock-candidate-v1/run-stock.mjs',import.meta.url));
let checks=0;
for(const path of [native,stock]) {
 const source=await readFile(path,'utf8');
 const match=/result\.passed\s*=\s*(result\.originalContractPassed\s*&&[^;]+);/.exec(source);
 assert(match);assert.equal(source.match(/result\.originalContractPassed\s*=/g).length,1);
 const gate=new Function('result','return ('+match[1]+');');
 for(const original of [true,false])for(const supplemental of [true,false])for(const portable of [true,false]) {
  const observed=gate({originalContractPassed:original,supplementalValidation:{passed:supplemental},portableCacheValidation:{passed:portable}});
  assert.equal(observed,original&&supplemental&&portable);checks++;
 }
 for(const portableCacheValidation of [undefined,null,{}, {passed:1},{passed:'true'}]) {
  assert.equal(gate({originalContractPassed:true,supplementalValidation:{passed:true},portableCacheValidation}),false);checks++;
 }
}
console.log(JSON.stringify({sourceOnly:true,checks,actorOrCollectorOrNextInvoked:false}));
