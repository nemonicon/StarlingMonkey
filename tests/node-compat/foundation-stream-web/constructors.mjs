import {observeConstructors} from './constructors-cases.mjs';
export async function run(){
  try{return JSON.stringify({passed:true,observations:await observeConstructors(globalThis)});}
  catch(error){return JSON.stringify({failure:{name:error.name,code:error.code,message:error.message}});}
}
