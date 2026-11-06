// Pure profile initialization only. No IO, clocks, entropy, tasks or resources.
// Main Node-compatible realm alias; auxiliary VM realms remain independent.
export function installNodeGlobalAlias(target=globalThis) {
  if(target===null||(typeof target!=='object'&&typeof target!=='function'))
    throw new TypeError('Node global alias target must be an object');
  const descriptor=Object.getOwnPropertyDescriptor(target,'global');
  if(descriptor!==undefined) {
    if(!Object.hasOwn(descriptor,'value')||descriptor.value!==target||
       descriptor.writable!==true||descriptor.enumerable!==true||descriptor.configurable!==true)
      throw new TypeError('Existing global property does not match Node22 profile');
    return false;
  }
  Object.defineProperty(target,'global',{value:target,writable:true,enumerable:true,configurable:true});
  return true;
}
