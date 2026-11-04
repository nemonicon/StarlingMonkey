// FUTURE initialization-failure vectors. Merely importing this host module does
// not evaluate any guest snippet or load a componentizer.
const prefix="import * as stream from 'node:stream';\nimport * as promises from 'node:stream/promises';\n";
const expressions=[['compose','stream.compose'],['duplexPair','stream.duplexPair'],
  ...['Readable','Writable','Duplex'].flatMap(name=>['fromWeb','toWeb'].map(method=>[name+'.'+method,'stream.'+name+'.'+method])),
  ['Duplex.from','stream.Duplex.from'],
  ...['compose','map','filter','forEach','toArray','some','find','every','flatMap','drop','take','reduce','iterator'].map(name=>['Readable.prototype.'+name,'stream.Readable.prototype.'+name]),
  ...['Readable','Writable'].map(name=>[name+'.prototype[Symbol.asyncDispose]','stream.'+name+'.prototype[Symbol.asyncDispose]'])];
export const deferredInitializers=expressions.flatMap(([operation,expression])=>[false,true].map(construct=>({
  name:operation.replace(/[^a-zA-Z0-9]+/g,'-')+(construct?'-new':'-call'),operation,construct,
  expectedCode:'ERR_SM_NODE_UNSUPPORTED',
  source:prefix+'const unavailable='+expression+';\n'+(construct?'new unavailable();':'unavailable();')+'\nexport function run(){return "unreachable";}\n',
})));
export const overloadInitializers=[];
for(const [shape,value] of [['readable','{getReader(){}}'],['writable','{getWriter(){}}'],['transform-pair','{readable:{},writable:{}}']]) {
  const sink='new stream.Writable({write(value,encoding,callback){callback();}})';
  const invokes=[['callback-pipeline','stream.pipeline(value,'+sink+',()=>{})'],
    ['promise-pipeline','promises.pipeline(value,'+sink+')'],
    ['callback-finished','stream.finished(value,()=>{})'],
    ['promise-finished','promises.finished(value)'],
    ['addAbortSignal','stream.addAbortSignal(new AbortController().signal,value)']];
  for(const [operation,invoke] of invokes) overloadInitializers.push({name:shape+'-'+operation,operation,shape,
    expectedCode:'ERR_SM_NODE_UNSUPPORTED',source:prefix+'const value='+value+';\n'+invoke+';\nexport function run(){return "unreachable";}\n'});
}
for(const [operation,invoke] of [['callback-function-stage','stream.pipeline(function stage(){},new stream.Writable({write(value,encoding,callback){callback();}}),()=>{})'],
  ['promise-function-stage','promises.pipeline(function stage(){},new stream.Writable({write(value,encoding,callback){callback();}}))']]) {
  overloadInitializers.push({name:operation,operation,expectedCode:'ERR_SM_NODE_UNSUPPORTED',
    source:prefix+invoke+';\nexport function run(){return "unreachable";}\n'});
}
export const unsupportedInitializers=[...deferredInitializers,...overloadInitializers];
export const caughtInitializer={name:'caught-top-level-control',
  source:prefix+`let error;try{stream.compose();}catch(caught){error=caught;}
if(error?.code!=='ERR_SM_NODE_UNSUPPORTED'||!Object.hasOwn(error,'code'))throw new Error('Caught initialization error contract');
export function run(){return 'caught-top-level-control';}
`};
