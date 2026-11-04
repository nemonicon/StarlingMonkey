// FUTURE source strings only. No guest or packager is executed on import.
const prefix="import {compose} from 'node:stream';\n";
const validate=`function record(error){
 if(error?.code!=='ERR_SM_NODE_UNSUPPORTED'||error.module!=='node:stream'||error.operation!=='compose'||error.profile!=='sm-node-22.14.0-m0.12')throw new Error('Deployed caught error contract');
 for(const key of ['code','module','operation','profile'])if(!Object.hasOwn(error,key))throw new Error('Missing own deployed error '+key);
 return{code:error.code,module:error.module,operation:error.operation,profile:error.profile};
}\n`;

export const deployedFatal={name:'deployed_fatal',policy:'One invocation per fresh instance; terminal failure; discard, never reuse',
  source:prefix+`export function run(){compose();return 'UNEXPECTED_FATAL_RETURN';}\n`};

export const deployedCleanControls=[
  {name:'deployed_caught',kind:'caught',source:prefix+validate+`let calls=0;
export async function run(){
 let error;try{compose();}catch(caught){error=record(caught);}
 if(!error)throw new Error('Unsupported operation unexpectedly returned');
 return JSON.stringify({kind:'caught',calls:++calls,error,completed:true});
}\n`},
  {name:'deployed_handled_later',kind:'handled-later',source:prefix+validate+`let calls=0;
export async function run(){
 let reactionRan=false;
 const pending=Promise.resolve().then(()=>{reactionRan=true;compose();});
 // The rejecting reaction is registered first. Attach its handler from a later
 // Promise job in the same event-loop checkpoint, using public Promise APIs.
 await Promise.resolve();
 if(!reactionRan)throw new Error('Rejecting reaction did not run before late handler');
 const error=await pending.catch(record);
 if(!error)throw new Error('Unsupported reaction unexpectedly fulfilled');
 return JSON.stringify({kind:'handled-later',calls:++calls,error,completed:true,handledAfterReaction:true});
}\n`},
];
