import * as provider from 'benchmark:provider';
import {createWorkload} from './workload.mjs';
const workload=createWorkload(provider);
export const setup=workload.setup;
export async function inspect(iterations){return JSON.stringify(await workload.run(iterations,{trace:true}));}
