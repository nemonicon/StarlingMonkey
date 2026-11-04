// UNEXECUTED application initializer unsupported-encoding fixture.
import {TextDecoderStream} from 'node:stream/web';
let failure;try{new TextDecoderStream('utf-16le');}catch(error){failure=error;}
if(failure?.code==='ERR_SM_NODE_UNSUPPORTED')throw Error('EXPECTED_STREAM_WEB_ENCODING_UNSUPPORTED');
throw Error('UNEXPECTED_STREAM_WEB_ENCODING_BEHAVIOR');
export function run(){return 'unreachable';}
