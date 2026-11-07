// Pure DATA gates, called with actual operation-local state by the adapter.
export function isObservedClosedOutput({observed,raw,caught,tag,responseSet}) {
  return observed===true&&raw===caught&&tag==='closed'&&responseSet===true;
}
export function mayReturnHandledClosed({classified,cancelReturned,readerReleased,cleanupReturned,requestAborted,fatalSet}) {
  return classified===true&&cancelReturned===true&&readerReleased===true&&cleanupReturned===true&&
    requestAborted===true&&fatalSet===false;
}
