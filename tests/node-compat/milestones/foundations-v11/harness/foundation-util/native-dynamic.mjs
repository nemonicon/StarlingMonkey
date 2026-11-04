// Unbundled fixture: none of the six builtin spellings is preloaded.
let previous,count=0;
export async function run(){
  const util=await import('node:util'),bare=await import('util'),types=await import('node:util/types'),bareTypes=await import('util/types'),sys=await import('node:sys'),bareSys=await import('sys');
  const current=[util,bare,types,bareTypes,sys,bareSys];
  const report={calls:++count,cached:!previous||current.every((value,index)=>value===previous[index]),sharedValues:bare.default===util.default&&sys.default===util.default&&bareSys.default===util.default&&types.default===util.types&&bareTypes.default===util.types,sysNamespaceDistinct:sys!==util,namespaceNullPrototype:current.every(value=>Object.getPrototypeOf(value)===null),thenAbsent:current.every(value=>value.then===undefined),encoderIdentity:util.TextEncoder===globalThis.TextEncoder,boxed:types.isNumberObject(Object(1))&&!types.isNumberObject(1),proxySafe:types.isUint8Array(new Proxy(new Uint8Array(1),{}))===false,exports:[Object.keys(util).length,Object.keys(types).length,Object.keys(sys).length]};
  previous=current;return JSON.stringify(report);
}
