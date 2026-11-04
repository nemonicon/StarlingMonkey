// UNEXECUTED installed-binding arm. Same public workload/provider interface.
import Stream,* as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import {Buffer} from 'node:buffer';
import {EventEmitter} from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {nextTick} from 'starling:test-classic-benchmark';
export {stream,promises};
export const dependencies={Buffer,EventEmitter,StringDecoder,nextTick};
export default Stream;
