// No static builtin import: probes uncached deployed module creation/cache.
let calls=0;
function ensure(value,message){if(!value)throw Error(message);}
export async function run(){
  const report={calls:++calls};
  try{
    const canonical=await import('node:stream/web'),bare=await import('stream/web');
    ensure(canonical===await import('node:stream/web')&&bare===await import('stream/web'),'same-ID namespace cache');
    const names=Object.keys(canonical).sort();ensure(names.length===18&&JSON.stringify(names)===JSON.stringify(Object.keys(bare).sort()),'finite aliases');
    for(const module of [canonical,bare]){
      ensure(Object.getPrototypeOf(module)===null&&module.then===undefined&&module.missing===undefined&&await Promise.resolve(module)===module,'safe namespace');
      for(const name of names)if(name!=='default')ensure(module[name]===canonical.default[name],'alias/default binding identity');
    }
    ensure(canonical.default===bare.default,'same default record');
    const stream=canonical.ReadableStream.from([7]),iterator=stream.values();
    ensure((await iterator.next()).value===7&&(await iterator.next()).done&&!stream.locked,'uncached native import usable');
    report.aliases=2;report.caching=true;report.identities=true;report.passed=true;
  }catch(error){report.failure={name:error?.name,code:error?.code,message:error?.message};}
  return JSON.stringify(report);
}
