// Test-only real Node22 reference. These are NOT guest native boundaries.
import {AsyncLocalStorage} from 'node:async_hooks';
import {setTimeout as promiseTimeout} from 'node:timers/promises';
export function createNodeReference(AsyncResource) {
  return{AsyncLocalStorage,AsyncResource,boundaryMode:'node-public-empty-store-projection',
    boundaries(stores){
      function empty(callback,receiver,...args){
        let index=0;
        function enter(){return index===stores.length?Reflect.apply(callback,receiver,args):stores[index++].run(undefined,enter);}
        return enter();
      }
      // Shared cases seed these per-control stores into real enabled state.
      // No projection occurs between disable and re-enable. This references
      // only public empty-store observations, not native owner/enable-bit parity.
      return{runFreshRequest:empty,runNeutralServer:empty};
    },
    nextTick:callback=>process.nextTick(callback),setTimeout,clearTimeout,setImmediate,clearImmediate,promiseTimeout};
}
