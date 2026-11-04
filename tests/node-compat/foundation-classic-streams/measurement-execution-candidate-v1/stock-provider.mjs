// Actual stock Jco adapters resolve these IDs; no provider/scheduler overrides.
import * as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import {Buffer} from 'node:buffer';
import {EventEmitter} from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {nextTick} from 'benchmark:stock-scheduler';
export const dependencies={Buffer,EventEmitter,StringDecoder,nextTick};
export {stream,promises};
export default stream.default;
