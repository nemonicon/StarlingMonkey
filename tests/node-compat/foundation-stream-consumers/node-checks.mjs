// Ordinary bounded Node reference cases; no native guest probes or raw memory.
const U8 = Uint8Array;
const BlobCtor = Blob;
const BufferCtor = globalThis.Buffer;
function ensure(value, label) { if (!value) throw new Error('Consumer reference: '+label); }
async function outcome(run) {
  try { return { fulfilled: true, value: await run() }; }
  catch (error) { return { fulfilled: false, name: error.name, ...(error.code === undefined ? {} : {code:error.code}) }; }
}
async function* from(chunks) { for (const chunk of chunks) yield chunk; }
export async function textChecks(consumers) {
  const cases = [];
  async function check(name, run) { cases.push({name,result:await run()}); }
  await check('empty and string chunks', async () => [await consumers.text([]), await consumers.text(['ab','cd']), await consumers.text('abc')]);
  await check('split UTF8 BOM and incomplete final sequence', async () => consumers.text(from([
    new U8([0xef]),new U8([0xbb,0xbf,65]),new U8([0xe2]),new U8([0x82,0xac,0xe2,0x82])])));
  await check('strings do not flush a pending byte decoder', async () => consumers.text(from([
    new U8([0xe2]),'X',new U8([0x82,0xac])])));
  await check('strings do not consume decoder BOM state', async () => consumers.text(['A',new U8([0xef,0xbb,0xbf,66]),'\ufeffC']));
  await check('string surrogate halves concatenate without UTF8 conversion', async () => consumers.text(['\ud83d','\ude00']));
  await check('typed views decode only visible raw bytes', async () => {
    const a = new U8([0,65,66,0]);
    return [await consumers.text([new DataView(a.buffer,1,2)]), await consumers.text([new U8(a.buffer,1,2)]),
      await consumers.text([new Uint16Array(new U8([65,66]).buffer)]), await consumers.text([a.buffer])];
  });
  await check('eager decoding precedes later mutation of reused chunk', async () => {
    async function* source() { const a=new U8([65]); yield a; a[0]=66; yield a; a[0]=67; }
    return consumers.text(source());
  });
  await check('undefined byte chunk is an empty decoder input', async () => consumers.text([undefined,new U8([65]),undefined]));
  await check('invalid byte chunks reject with error type and code', async () => {
    const cases=[];
    for(const value of [null,1,false,{},Symbol('part'),new BlobCtor(['a'])]) cases.push(await outcome(()=>consumers.text([value])));
    return cases;
  });
  await check('sync iterator yielded promises are unwrapped', async () => consumers.text([Promise.resolve('A'),Promise.resolve(new U8([66]))]));
  await check('async iterator yielded promise value is not unwrapped', async () => {
    let step=0;
    const source = {[Symbol.asyncIterator](){return this;}, async next(){return step++ ? {done:true} : {done:false,value:Promise.resolve('A')};}};
    return outcome(()=>consumers.text(source));
  });
  await check('body decoding failure closes the iterator once', async () => {
    const log=[],sentinel=new Error('return failure'); let step=0;
    const source = {[Symbol.asyncIterator](){log.push('iterator');return this;}, async next(){log.push('next');return step++ ? {done:true} : {done:false,value:{}};},
      async return(){log.push('return');throw sentinel;}};
    const error = await outcome(()=>consumers.text(source)); return {error,log};
  });
  await check('next rejection propagates original error without return', async () => {
    const sentinel=new Error('source failure'),log=[];
    const source={[Symbol.asyncIterator](){return this;},async next(){log.push('next');throw sentinel;},async return(){log.push('return');return {done:true};}};
    let same=false;try{await consumers.text(source);}catch(error){same=error===sentinel;}
    return {same,log};
  });
  await check('sync iterator body failure invokes finally', async () => {
    const log=[];
    function* source(){try{yield new U8([65]);yield {};}finally{log.push('finally');}}
    return {error:await outcome(()=>consumers.text(source())),log};
  });
  await check('json consumes streaming text before parsing', async () => {
    const log=[];
    async function* valid(){try{yield new U8([0xef,0xbb]);yield new U8([0xbf,123,34,120,34,58]);yield '2}';}finally{log.push('complete');}}
    return {value:await consumers.json(valid()),log};
  });
  await check('json syntax failure occurs after iterator completion', async () => {
    const log=[];
    async function* invalid(){try{yield '{';yield 'bad';}finally{log.push('complete');}}
    return {error:await outcome(()=>consumers.json(invalid())),log};
  });
  await check('literal BOM json differs from byte BOM', async () => ({
    literal:await outcome(()=>consumers.json(['\ufeff{"x":1}'])),bytes:await consumers.json([new U8([0xef,0xbb,0xbf,123,34,120,34,58,49,125])])}));
  await check('native Promise result and supported async non-construction', async () => {
    const promise=consumers.text(['a']); const result={promise:promise instanceof Promise,then:typeof promise.then,value:await promise};
    for(const name of ['text','json']) { try {Reflect.construct(consumers[name],[[]]);result[name]='returned';} catch(e){result[name]={name:e.name,...(e.code===undefined?{}:{code:e.code})};} }
    return result;
  });
  return cases;
}
export async function blobChecks(consumers) {
  const cases=[];
  async function check(name,run){cases.push({name,result:await run()});}
  await check('blob parts remain references through iterator completion',async()=>{
    const log=[];async function* source(){const a=new U8([65]);try{yield a;a[0]=66;yield a;a[0]=67;}finally{log.push('complete');}}
    return {bytes:[...new U8(await consumers.arrayBuffer(source()))],log};
  });
  await check('blob mutation at final done is observed',async()=>{
    const a=new U8([65]);let step=0;
    const source={[Symbol.asyncIterator](){return this;},async next(){if(step++===0)return {value:a,done:false};a[0]=90;return {done:true};}};
    return [...new U8(await consumers.arrayBuffer(source))];
  });
  await check('mixed string and incomplete bytes use a different path from text',async()=>{
    const chunks=[new U8([0xe2]),'X',new U8([0x82,0xac])],blob=await consumers.blob(chunks);
    return {text:await consumers.text(chunks),blobText:await blob.text(),bytes:[...new U8(await blob.arrayBuffer())]};
  });
  await check('Blob string parts repair surrogates independently',async()=>{
    const chunks=['\ud83d','\ude00'];return {text:await consumers.text(chunks),blobText:await(await consumers.blob(chunks)).text()};
  });
  await check('object parts convert after source completion',async()=>{
    let value='A';const log=[],part={toString(){log.push('convert:'+value);return value;}};
    async function* source(){yield part;value='B';log.push('complete');}
    const output=await consumers.blob(source());return {log,text:await output.text()};
  });
  await check('Blob part conversion failure happens after iteration without close',async()=>{
    const log=[];let step=0;
    const source={[Symbol.asyncIterator](){return this;},async next(){log.push('next');return step++===0?{value:Symbol('part'),done:false}:{done:true};},async return(){log.push('return');return {done:true};}};
    return {error:await outcome(()=>consumers.blob(source)),log};
  });
  await check('Blob output type and Node global Buffer.Blob identity',async()=>{
    const original=new BlobCtor(['A'],{type:'TEXT/PLAIN'}),output=await consumers.blob([original,'B']);
    return {globalEqualsBufferBlob:BlobCtor=== (await import('node:buffer')).Blob,instance:output instanceof BlobCtor,
      prototype:Object.getPrototypeOf(output)===BlobCtor.prototype,size:output.size,type:output.type,originalType:original.type,text:await output.text()};
  });
  await check('native Blob constructor snapshots parts and returned arrays are independent',async()=>{
    const a=new U8([0,65,66,0]),blob=new BlobCtor([new DataView(a.buffer,1,2)]);a[1]=90;
    const first=await blob.arrayBuffer(),second=await blob.arrayBuffer(),bytes=await blob.bytes();new U8(first)[0]=88;bytes[1]=89;
    return {size:blob.size,first:[...new U8(first)],second:[...new U8(second)],bytes:[...bytes],
      independent:first!==second&&first!==bytes.buffer&&second!==bytes.buffer,blobText:await blob.text()};
  });
  await check('consumer buffer is a real Buffer over exact returned bytes',async()=>{
    const output=await consumers.buffer([new U8([65,66])]);ensure(BufferCtor.isBuffer(output),'real Buffer');
    return {bytes:[...output],isBuffer:BufferCtor.isBuffer(output),offset:output.byteOffset,backingBytes:output.buffer.byteLength};
  });
  await check('Blob stream default reader reads copied owned bytes',async()=>{
    const blob=new BlobCtor(['abc']),reader=blob.stream().getReader(),first=await reader.read();first.value[0]=90;
    const last=await reader.read();reader.releaseLock();return {first:[...first.value],done:last.done,blobText:await blob.text()};
  });
  await check('Blob stream is a byte stream with ordinary BYOB reads',async()=>{
    const reader=new BlobCtor(['ab']).stream().getReader({mode:'byob'}),value=await reader.read(new U8(3));
    await reader.cancel();reader.releaseLock();return {bytes:[...value.value],done:value.done};
  });
  await check('Blob text removes BOM and replaces malformed UTF8',async()=>[
    await new BlobCtor([new U8([0xef,0xbb,0xbf,65])]).text(),await new BlobCtor([new U8([0xe2,0x82])]).text()]);
  return cases;
}
