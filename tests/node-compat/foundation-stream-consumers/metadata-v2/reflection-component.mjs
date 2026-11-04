import * as consumers from './prototype.mjs';
const Descriptor=Object.getOwnPropertyDescriptor,Keys=Reflect.ownKeys;
export function run(){
  const result={};
  for(const name of ['text','json']){
    const fn=consumers[name];
    // Observe key order before requesting descriptors, so this probe cannot
    // repair an incorrect order by its own descriptor access.
    const ownKeys=Keys(fn).map(String);
    result[name]={ownKeys,length:Descriptor(fn,'length'),name:Descriptor(fn,'name')};
  }
  return JSON.stringify(result);
}
