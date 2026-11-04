// All package/old-runner imports follow actual fixed-artifact admission.
import assert from 'node:assert/strict';
import {resolve} from 'node:path';
import {verifyProductionTicks,requireFreshOutput,completeRegression} from './preflight.mjs';
const admission=await verifyProductionTicks({gcStress:false});
await requireFreshOutput('NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT');
for(const[key,value]of Object.entries({NODE_COMPAT_ALLOCATOR_OLD_ENGINE:'/tmp/starling-node-compat/foundations-v7/native-freeze/off-foundations.engine.wasm',NODE_COMPAT_ALLOCATOR_OLD_SOURCE_ROOT:'/tmp/starling-node-compat/foundations-v7/native-freeze/source'}))if(process.env[key])assert.equal(resolve(process.env[key]),value,'Historical control paths are fixed for this gate');
await import('./runners/allocator.mjs');
await completeRegression('NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT',admission);
