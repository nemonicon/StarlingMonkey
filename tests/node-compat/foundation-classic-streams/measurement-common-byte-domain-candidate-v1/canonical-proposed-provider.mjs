// Proposed5c host model only; never relabel the installed342 factory as fixed.
import {createClassicStreams} from '../trace-semantics-candidate-v1/proposed/classic-streams.mjs';
import {Buffer} from 'node:buffer';
import * as events from 'node:events';
import {StringDecoder} from 'node:string_decoder';
export const dependencies={Buffer,EventEmitter:events.EventEmitter,StringDecoder,nextTick:process.nextTick};
const graph=createClassicStreams({...dependencies,events,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
export const stream=graph.root,promises=graph.promises;
