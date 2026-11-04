import {runComposed} from './checks.mjs';
import expected from 'node-compat:stream-composed-oracles';
let calls=0;
export async function run(){const report=await runComposed(expected);return JSON.stringify({calls:++calls,...report});}
