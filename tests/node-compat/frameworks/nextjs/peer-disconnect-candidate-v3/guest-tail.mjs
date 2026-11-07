// Only functions/bindings at INIT. Actual state, ALS, timers and bootstrap are ordinary-call only.
async function preparePeerServer() {
  const process=bootstrap();
  if(globalThis.process!==process)throw new Error('Native process identity mismatch');
  const state=createPeerState({AsyncLocalStorage,origin:'actual-wasi-guest',
    writeLog:event=>console.error(JSON.stringify(event))});
  const web=createPeerWebHandler(state,{setTimeout:peerTimeout,clearTimeout:peerClearTimeout});
  return createDiagnosticWasiHttpHandler(web,types,runFreshRequest,state);
}
function disposeBeforeEntry(incoming,outparam) {
  let failures=0;
  for(const [kind,value]of [['incoming-request',incoming],['response-outparam',outparam]]) {
    console.error(JSON.stringify({marker:peerMarker,origin:'actual-wasi-guest',phase:'pre-entry-dispose-invocation-attempt',resource:kind}));
    try {value[Symbol.dispose]();console.error(JSON.stringify({marker:peerMarker,origin:'actual-wasi-guest',phase:'pre-entry-dispose-returned',resource:kind}));}
    catch(error){failures++;console.error(JSON.stringify({marker:peerMarker,origin:'actual-wasi-guest',phase:'pre-entry-dispose-failed-suppressed',resource:kind,error:errorData(error)}));}
  }
  if(failures)console.error('NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE',failures);
}
export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:preparePeerServer,disposeBeforeEntry});
