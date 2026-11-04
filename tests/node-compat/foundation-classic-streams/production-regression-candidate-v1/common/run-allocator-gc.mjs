import {verifyProductionTicks,requireFreshOutput,completeRegression} from './preflight.mjs';
const admission=await verifyProductionTicks({gcStress:true});
await requireFreshOutput('NODE_COMPAT_ALLOCATOR_GC_OUTPUT');
await import('./runners/allocator-gc.mjs');
await completeRegression('NODE_COMPAT_ALLOCATOR_GC_OUTPUT',admission);
