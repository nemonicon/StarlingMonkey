import {createClassicStreams} from './classic-streams.mjs';
import {Buffer} from 'node:buffer';
import * as events from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {nextTick} from 'starling:test-classic-benchmark';
export const dependencies={Buffer,EventEmitter:events.EventEmitter,StringDecoder,nextTick};
const graph=createClassicStreams({...dependencies,events,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
export const stream=graph.root,promises=graph.promises;
export default graph.root.default;
