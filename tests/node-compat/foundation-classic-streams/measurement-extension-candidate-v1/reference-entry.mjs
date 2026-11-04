// UNEXECUTED same-bounded-factory arm. The module ID is diagnostic-only.
// Resolve this exact relative entry, never substitute installed node:stream.
import {createClassicStreams} from '../../../../builtins/node-compat/classic-streams/classic-streams.mjs';
import {Buffer} from 'node:buffer';
import * as events from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {nextTick} from 'starling:test-classic-benchmark';

const graph=createClassicStreams({Buffer,events,StringDecoder,nextTick,
  AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
export const stream=graph.root;
export const promises=graph.promises;
export const dependencies={Buffer,EventEmitter:events.EventEmitter,StringDecoder,nextTick};
export default graph.root.default;
