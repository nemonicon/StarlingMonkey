// Public Jco instantiateCore hook. Observe only exported WebAssembly.Memory
// objects and buffer.byteLength; never create a view or read guest bytes.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
export async function loadCompiled(record){
  const modules=new Map();
  for(const file of record.coreFiles)modules.set(file,await WebAssembly.compile(await readFile(resolve(dirname(record.modulePath),file))));
  const binding=await import(pathToFileURL(record.modulePath));
  return async function instantiate(){
    const memories=new Set();
    const exports=await binding.instantiate(name=>{assert(modules.has(name),'Unknown core module '+name);return modules.get(name);},{},
      async(module,imports)=>{const instance=await WebAssembly.instantiate(module,imports);for(const value of Object.values(instance.exports))if(value instanceof WebAssembly.Memory)memories.add(value);return instance;});
    assert(memories.size>0,'Public core exports must expose Memory objects for later boundary observations');
    return{exports,memories:[...memories]};
  };
}
export const memoryLengths=instance=>instance.memories.map(memory=>memory.buffer.byteLength);
