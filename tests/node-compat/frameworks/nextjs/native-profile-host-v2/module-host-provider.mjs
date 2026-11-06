// HOST CONTROL ONLY. No candidate native kernel/ALS or Wasm guest executes.
import * as nodeModule from 'node:module';
import {readFileSync,statSync,realpathSync} from 'node:fs';
import {compileFunction,createContext,runInContext} from 'node:vm';
import {AsyncLocalStorage} from 'node:async_hooks';
import {createModuleAPI} from '../../../foundation-module/node-module-candidate-v1/module-core.mjs';
import {createBufferModule} from '../../../buffer-next-candidate-v1/native/builtins/node-compat/buffer-facade.mjs';
import {hostKernel} from '../../../buffer-next-candidate-v1/host-kernel.mjs';
import {createEventsFacade} from '../../../../../builtins/node-compat/events.mjs';
import {createStringDecoderModule} from '../../../../../builtins/node-compat/string-decoder.mjs';
import {createClassicStreams} from '../../../../../builtins/node-compat/classic-streams/classic-streams.mjs';
import {installReadableToWeb} from '../../../foundation-classic-streams/readable-toweb-candidate-v1/readable-toweb.mjs';
const hostRequire=nodeModule.createRequire(import.meta.url),originalHostBuffer=globalThis.Buffer;

export function createHostProfile(filename,observations){
 const buffer=createBufferModule(hostKernel),events=createEventsFacade(Symbol('TEST-ONLY native protected AbortTarget key'));
 const decoder=createStringDecoderModule(buffer.Buffer);
 const classic=createClassicStreams({Buffer:buffer.Buffer,events,StringDecoder:decoder.StringDecoder,nextTick:process.nextTick,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
 installReadableToWeb(classic,ReadableStream);
 const sandbox={};for(const key of Reflect.ownKeys(globalThis))if(!['global','globalThis','Buffer'].includes(key))Object.defineProperty(sandbox,key,Object.getOwnPropertyDescriptor(globalThis,key));
 sandbox.Buffer=buffer.Buffer;const context=createContext(sandbox);context.global=context;
 const source=(relative,delimiter)=>{const path=new URL(relative,import.meta.url);const header=readFileSync(path,'utf8'),marker='R"'+delimiter+'(';const at=header.indexOf(marker);if(at<0)throw Error('Missing factory marker');const end=header.indexOf(')'+delimiter+'"',at+marker.length);if(end<0)throw Error('Missing factory end');return runInContext(header.slice(at+marker.length,end),context,{filename:path.pathname});};
 const carrier=new AsyncLocalStorage();let nextOwner=0;
 const metrics={neutralEntries:0,freshEntries:0,prepareOwners:[],conversionOwners:[],bridgeOwners:[],pairedClassChecks:0};
 function runNeutralServer(fn,receiver,...args){metrics.neutralEntries++;return carrier.exit(()=>Reflect.apply(fn,receiver,args));}
 function runFreshRequest(fn,receiver,...args){const root={requestOwner:++nextOwner};metrics.freshEntries++;return carrier.run(root,()=>Reflect.apply(fn,receiver,args));}
 const httpFactory=source('../../../foundation-http/next-http-candidate-v1/next-http-factory.generated.h','SM_HTTP');
 const http=httpFactory({Readable:classic.root.Readable,Writable:classic.root.Writable,EventEmitter:events.EventEmitter,Buffer:buffer.Buffer,runNeutralServer,runFreshRequest,checkDeployed(){}});
 const imports=source('../../../foundation-next-imports/next-imports-candidate-v1/next-imports-factory.generated.h','SM_IMPORTS')();
 const overrides=new Map();
 function selected(id,value){overrides.set(id,value);overrides.set('node:'+id,value);}
 for(const [id,value]of [['http',http.http.default],['https',http.https.default],['events',events.default],['stream',classic.root.default],['stream/promises',classic.promises.default],['string_decoder',decoder.default],['buffer',buffer.default]])selected(id,value);
 for(const [id,record]of Object.entries(imports)){overrides.set(id,record.default);overrides.set(id.slice(5),record.default);}
 const builtins=new Set(),compiled=new Set(),selectedHits=new Map(),hostHits=new Set();
 const provider={cwd:()=>process.cwd(),kind(path){try{const s=statSync(path);return s.isFile()?'file':s.isDirectory()?'directory':'other';}catch(e){if(['ENOENT','ENOTDIR'].includes(e.code))return null;throw e;}},readText:p=>readFileSync(p,'utf8'),realpath:p=>realpathSync(p),getBuiltin(id){builtins.add(id);if(overrides.has(id)){const value=overrides.get(id);if(value===undefined)throw Error('Selected facade missing: '+id);selectedHits.set(id,(selectedHits.get(id)||0)+1);return value;}hostHits.add(id);return hostRequire(id);},compile(code,filename){compiled.add(filename);return compileFunction(code,['exports','require','module','__filename','__dirname'],{filename,parsingContext:context});}};
 const api=createModuleAPI(provider,nodeModule.builtinModules,['node:sea','node:sqlite','node:test','node:test/reporters'],Object.keys(nodeModule),nodeModule.constants);
 const require=api.createRequire(filename);
 observations.snapshot=()=>({builtins:[...builtins].sort(),selectedFacadeHits:Object.fromEntries([...selectedHits].sort()),unselectedHostBuiltins:[...hostHits].sort(),compiled:[...compiled].sort(),cachedModules:Object.keys(api.default._cache).length,candidateModuleIdentity:require('node:module')===api.default,hostBufferUnchanged:globalThis.Buffer===originalHostBuffer,privateGlobalBufferSameAsSelected:context.Buffer===require('node:buffer').Buffer,contextMetrics:metrics});
 observations.hostBufferUnchanged=()=>globalThis.Buffer===originalHostBuffer;
 observations.nativeProviderExecuted=false;observations.nativeALSExecuted=false;observations.guestExecuted=false;
 return {require,hosting:http.hosting,
  noteConversion(){const owner=carrier.getStore()?.requestOwner;if(!owner)throw Error('Conversion outside fresh TEST owner');metrics.conversionOwners.push(owner);},
  notePrepare(){metrics.prepareOwners.push(carrier.getStore()?.requestOwner??null);},
  wrapHandler(handler){return function(req,res){if(!(req instanceof http.http.IncomingMessage)||!(res instanceof http.http.ServerResponse))throw Error('Bridge classes differ from selected HTTP exports');const owner=carrier.getStore()?.requestOwner;if(!owner)throw Error('Bridge outside fresh TEST owner');metrics.pairedClassChecks++;metrics.bridgeOwners.push(owner);return Reflect.apply(handler,this,[req,res]);};},
 };
}
