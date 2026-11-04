// UNEXECUTED application initializer failure fixture.
import {DecompressionStream} from 'node:stream/web';
let failure;
try{DecompressionStream("gzip");}catch(error){failure=error;}
if(failure?.code==='ERR_SM_NODE_UNSUPPORTED'&&failure.module==='node:stream/web'&&failure.operation==='DecompressionStream'&&failure.profile==='sm-node-22.14.0-m0.9')throw Error('EXPECTED_STREAM_WEB_DECOMPRESSIONSTREAM_CALL');
throw Error('UNEXPECTED_STREAM_WEB_UNSUPPORTED_BEHAVIOR');
export function run(){return 'unreachable';}
