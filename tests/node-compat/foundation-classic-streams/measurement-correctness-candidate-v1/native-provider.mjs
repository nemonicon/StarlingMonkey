// Only real installed modules and the finite reviewed diagnostic binding.
import Stream,* as stream from 'node:stream';
import * as promises from 'node:stream/promises';
import {Buffer} from 'node:buffer';
import {EventEmitter} from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {nextTick} from 'starling:test-classic-benchmark';
if(stream.default!==Stream||Buffer!==globalThis.Buffer||typeof nextTick!=='function')throw new Error('Native provider identities required');
export const dependencies={Buffer,EventEmitter,StringDecoder,nextTick};
export {stream,promises};
