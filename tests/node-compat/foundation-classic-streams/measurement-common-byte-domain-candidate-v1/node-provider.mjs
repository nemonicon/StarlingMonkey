// Real pinned Node host oracle, never a guest/native-scheduler substitute.
import * as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import {Buffer} from 'node:buffer';
import {EventEmitter} from 'node:events';
import {StringDecoder} from 'node:string_decoder';
export const dependencies={Buffer,EventEmitter,StringDecoder,nextTick:process.nextTick};
export {stream,promises};
export default stream.default;
