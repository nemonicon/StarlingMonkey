// Host algorithm check only: canonical factory with real Node dependencies/queue.
import {createClassicStreams} from '../../../../builtins/node-compat/classic-streams/classic-streams.mjs';
import {Buffer} from 'node:buffer';
import * as events from 'node:events';
import {StringDecoder} from 'node:string_decoder';
export const dependencies={Buffer,EventEmitter:events.EventEmitter,StringDecoder,nextTick:process.nextTick};
const graph=createClassicStreams({...dependencies,events,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
export const stream=graph.root,promises=graph.promises;
export default graph.root.default;
