// Deployed control helper, inlined in raw entries. Never called during INIT.
// Capture under marker, invoke under a distinct enabled caller, restore caller.
// Default Node22 exit disables the instance; it is tested separately.
export function evaluateCapturedStoreRestoration(state,AsyncLocalStorage,marker) {
  const outerBefore=state.getStore()===marker;
  const snapshot=AsyncLocalStorage.snapshot(),bound=AsyncLocalStorage.bind(()=>state.getStore());
  const otherStore={request:'enabled-caller'};
  const observed=state.run(otherStore,()=>{
    const otherBefore=state.getStore()===otherStore;
    const snapshotMarker=snapshot(()=>state.getStore())===marker;
    const otherAfterSnapshot=state.getStore()===otherStore;
    const boundMarker=bound()===marker;
    const otherAfterBound=state.getStore()===otherStore;
    return {otherBefore,snapshotMarker,otherAfterSnapshot,boundMarker,otherAfterBound};
  });
  return {outerBefore,...observed,outerAfter:state.getStore()===marker};
}
