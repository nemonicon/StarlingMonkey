// Pure orchestration, inlined unchanged into each raw guest entry.
export function createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry}) {
  let readiness;
  return Object.freeze({
    handle(incoming,outparam) {
      let enteredNeutral=false;
      try {
        return runNeutralServer(async () => {
          enteredNeutral=true;
          let handler;
          try {
            // Both promise allocation and all preparation happen neutrally.
            // One sticky promise per component instance: concurrent first
            // requests share success or the original rejection, never retry.
            readiness ??= Promise.resolve().then(prepareServer);
            handler=await readiness;
            if(!handler||typeof handler.handle!=='function')
              throw new TypeError('Preparation must return the real WASI handler');
          } catch(error) {
            disposeBeforeEntry(incoming,outparam);
            throw error;
          }
          // The adapter owns both resources from here. It enters native fresh
          // request context BEFORE constructing headers, body or Web Request.
          return handler.handle(incoming,outparam);
        },undefined);
      } catch(error) {
        if(!enteredNeutral)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  });
}

export function readRoutingOrigin(value) {
  if(typeof value!=='string'||value.length>2048)
    throw new TypeError('Set canonical STARLING_NEXT_ORIGIN before deployment');
  const url=new URL(value);
  if(!['http:','https:'].includes(url.protocol)||!url.hostname||url.username||url.password||
     url.pathname!=='/'||url.search||url.hash||url.origin!==value)
    throw new TypeError('STARLING_NEXT_ORIGIN must be a canonical HTTP(S) origin');
  const port=url.port?Number(url.port):(url.protocol==='https:'?443:80);
  if(!Number.isInteger(port)||port<1||port>65535)throw new TypeError('Invalid routing port');
  return Object.freeze({origin:url.origin,hostname:url.hostname,port});
}
