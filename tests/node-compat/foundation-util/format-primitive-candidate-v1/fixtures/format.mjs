// UNCOMPILED. No formatter call at INIT; all calls happen in ordinary run().
import util,{format,inspect} from 'node:util';
import sys from 'node:sys';
import {positiveCases,settings} from '../cases.mjs';
let calls=0;
export function run(){
 const saved={...inspect.defaultOptions},records=[];
 try{
  for(const setting of settings){
   inspect.defaultOptions={numericSeparator:setting.numericSeparator,colors:setting.colors};
   for(const{id,args}of positiveCases())records.push({setting:setting.id,id,value:format(...args)});
  }
 }finally{inspect.defaultOptions=saved;}
 return JSON.stringify({schemaVersion:1,call:++calls,records,formatDefaultIdentity:util.format===format,sysDefaultIdentity:sys===util,sysFormatIdentity:sys.format===format});
}
