// Existing public Jco async instantiation, no core-export or memory inspection.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
export async function loadCompiled(record){
  const modules=new Map();
  for(const file of record.coreFiles)modules.set(file,await WebAssembly.compile(await readFile(resolve(dirname(record.modulePath),file))));
  const binding=await import(pathToFileURL(record.modulePath));
  return async()=>({exports:await binding.instantiate(name=>{assert(modules.has(name));return modules.get(name);},{})});
}
