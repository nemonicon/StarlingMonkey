// UNEXECUTED application initializer failure fixture.
import {CompressionStream} from 'node:stream/web';
let failure;
try{new CompressionStream("gzip");}catch(error){failure=error;}
if(failure?.code==='ERR_SM_NODE_UNSUPPORTED'&&failure.module==='node:stream/web'&&failure.operation==='CompressionStream'&&failure.profile==='sm-node-22.14.0-m0.9')throw Error('EXPECTED_STREAM_WEB_COMPRESSIONSTREAM_CONSTRUCT');
throw Error('UNEXPECTED_STREAM_WEB_UNSUPPORTED_BEHAVIOR');
export function run(){return 'unreachable';}
