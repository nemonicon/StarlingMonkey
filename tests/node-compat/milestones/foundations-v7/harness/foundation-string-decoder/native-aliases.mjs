// No static native import: exercise first deployed synthetic-module loading.
let calls=0;
function check(condition,message){if(!condition)throw Error(message);}
export async function run(){
  try{
    const canonical=await import('node:string_decoder');
    const bare=await import('string_decoder');
    check(canonical===await import('node:string_decoder')&&bare===await import('string_decoder'),'module cache');
    for(const namespace of [canonical,bare]){
      check(JSON.stringify(Object.keys(namespace).sort())==='["StringDecoder","default"]','finite namespace');
      check(namespace.then===undefined&&namespace.missing===undefined,'safe namespace inspection');
      check(await Promise.resolve(namespace)===namespace,'no accidental thenable');
    }
    check(canonical.default===bare.default&&canonical.StringDecoder===bare.StringDecoder,'alias binding identity');
    check(canonical.default.StringDecoder===canonical.StringDecoder,'default named identity');
    check(new canonical.StringDecoder().end(Uint8Array.of(97))==='a','uncached import usable');
    return JSON.stringify({calls:++calls,nativeAliases:2,caching:true,identities:true});
  }catch(error){return JSON.stringify({failure:{name:error.name,code:error.code,message:error.message}});}
}
