// Shared ordinary order cases. Production brand still requires compiled API.
export async function guardCases(web,track=(reader)=>reader){
const {ReadableStream,ReadableStreamBYOBReader}=web;
const definitions=[
  ['default',()=>({})],['null-options',()=>({options:null})],['array-options',()=>({options:[]})],
  ['function-options',()=>({options:function(){}})],['number-options',()=>({options:1})],
  ['min-one',()=>({options:{min:1}})],['min-two',()=>({options:{min:2}})],
  ['min-null',()=>({options:{min:null}})],['min-string',()=>({options:{min:'1'}})],
  ['min-fraction',()=>({options:{min:1.5}})],['min-zero',()=>({options:{min:0}})],
  ['min-nan',()=>({options:{min:NaN}})],['min-infinity',()=>({options:{min:Infinity}})],
  ['min-too-large',()=>({options:{min:5}})],
  ['min-getter',trace=>({options:{get min(){trace.push('min');return 1;}}})],
  ['throwing-min',trace=>({options:{get min(){trace.push('min');throw Error('sentinel');}}})],
  ['invalid-receiver-first',trace=>({receiver:{},view:{},options:{get min(){trace.push('min');throw Error('sentinel');}}})],
  ['spoof-receiver-first',trace=>({receiver:Object.create(ReadableStreamBYOBReader.prototype),view:{},options:{get min(){trace.push('min');throw Error('sentinel');}}})],
  ['proxy-genuine-receiver',(_trace,reader)=>({receiver:new Proxy(reader,{})})],
  ['invalid-view-before-options',trace=>({view:{},options:{get min(){trace.push('min');throw Error('sentinel');}}})],
  ['arraybuffer-view-rejected',()=>({view:new ArrayBuffer(4)})],
  ['zero-view-before-min',trace=>({view:new Uint8Array(0),options:{get min(){trace.push('min');throw Error('sentinel');}}})],
  ['zero-view-invalid-options',()=>({view:new Uint8Array(0),options:1})],
  ['shadowed-view-fields',trace=>{const view=new Uint8Array(4);for(const key of ['buffer','byteLength','length'])Object.defineProperty(view,key,{get(){trace.push(key);throw Error('sentinel');}});return{view,options:{min:1}};}],
];
const cases=[];
for(const[name,make]of definitions){
  const trace=[],stream=new ReadableStream({type:'bytes',start(controller){controller.enqueue(Uint8Array.of(9,10));controller.close();}}),reader=track(stream.getReader({mode:'byob'}));
  const state=make(trace,reader),view=state.view??new Uint8Array(4),receiver=Object.hasOwn(state,'receiver')?state.receiver:reader;
  const result={name,trace};
  try{const value=await ReadableStreamBYOBReader.prototype.read.call(receiver,view,state.options);result.value={done:value.done,bytes:[...value.value]};}
  catch(error){result.error={name:error.name};if(error.code!==undefined)result.error.code=error.code;result.error.sentinel=error.message==='sentinel';}
  await reader.cancel();await reader.closed;reader.releaseLock();cases.push(result);
}
return cases;
}
