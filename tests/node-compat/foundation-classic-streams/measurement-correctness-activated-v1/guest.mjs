import * as provider from './native-provider.mjs';
import {createWorkload,scenarioIds} from './workload.mjs';
import {encodingCases} from './encoding-cases.mjs';
const workload=createWorkload(provider),cases=scenarioIds.flatMap(id=>[1,16].map(iterations=>({id,iterations})));
let calls=0;
// One case per exported entry: await/Promise never resets the native checkpoint
// work budget within a sixteen-iteration case. No setup stream exists at init.
export async function run(index){
 if(!Number.isInteger(index)||index<0||index>=20)throw new RangeError('Finite correctness index0..19 required');
 const {id,iterations}=cases[index],setup=workload.setup(id);
 return JSON.stringify({schemaVersion:1,calls:++calls,caseIndex:index,setup,result:await workload.run(iterations,{trace:true})});
}
export async function boundaries(){return JSON.stringify({schemaVersion:1,calls:++calls,observed:await encodingCases(provider)});}
