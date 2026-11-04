import * as stream from 'node:stream';
import {Buffer} from 'node:buffer';
import {makeInput,checksum,runCases} from './cases.mjs';
const input=makeInput(Buffer),snapshot={bytes:input.length,checksum:checksum(input)};let calls=0;
export async function run(){return JSON.stringify({schema:1,calls:++calls,snapshot,observed:await runCases({stream,Buffer,input,queueMicrotask})});}
