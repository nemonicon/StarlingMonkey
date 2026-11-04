// Actual common bundle entry. Provider is a finite source-resolver choice.
import * as provider from 'benchmark:provider';
import {createWorkload} from './workload.mjs';
const workload=createWorkload(provider); // No setup input, stream or queued work yet.
export const setup=workload.setup;
export async function run(iterations){return(await workload.run(iterations)).checksum;}
// Correctness world only: ordinary public results/traces; never a timing export.
export async function inspect(iterations){return JSON.stringify(await workload.run(iterations,{trace:true}));}
