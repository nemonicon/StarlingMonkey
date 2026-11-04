// Ordinary API corpus. Receiver cases may run in a guest ONLY after the host
// preflight verifies all four exact corrected Blob/File source hashes.
const encodeNumber = value => Number.isNaN(value) ? 'NaN' : value === Infinity ? '+Infinity' :
  value === -Infinity ? '-Infinity' : Object.is(value, -0) ? '-0' : value;
const failure = error => ({ name: error.name, ...(error.code === undefined ? {} : { code: error.code }) });
async function outcome(run) {
  let value;
  try { value = run(); } catch (error) { return { phase: 'throw', ...failure(error) }; }
  try { return { phase: 'fulfilled', value: await value }; }
  catch (error) { return { phase: 'reject', ...failure(error) }; }
}

export async function ordinaryCases({ Blob: B, File: F }) {
  const rows = [];
  const add = async (name, run) => rows.push({ name, result: await run() });
  const bytes = async blob => [...new Uint8Array(await blob.arrayBuffer())];
  await add('empty fresh storage and minimum one-unit text', async () => {
    const empty = new B(), first = await empty.arrayBuffer(), second = await empty.arrayBuffer();
    return { emptyText: await empty.text(), emptySize: empty.size, independent: first !== second,
      emptyBytes: [...await empty.bytes()], oneByte: await new B([new Uint8Array([65])]).text() };
  });
  await add('UTF8 strings repair each source part', async () => {
    const blob = new B(['A', '\u20ac', '\ud83d\ude00', '\ud800']);
    return { text: await blob.text(), bytes: await bytes(blob), split: await new B(['\ud83d', '\ude00']).text() };
  });
  await add('UTF8 BOM removal malformed and truncated replacement', async () => [
    await new B([new Uint8Array([0xef,0xbb,0xbf,65])]).text(),
    await new B([new Uint8Array([0xe2,0x82])]).text(),
    await new B([new Uint8Array([0xff,65])]).text()]);
  await add('only visible view bytes copied at construction', async () => {
    const input = new Uint8Array([0,65,66,0]), view = new DataView(input.buffer,1,2);
    const blob = new B([view, new Uint8Array(input.buffer,2,1)]); input.fill(90);
    return { bytes: await bytes(blob), size: blob.size, text: await blob.text() };
  });
  await add('ArrayBuffer and nonbyte typed views use raw byte range', async () => {
    const storage = new Uint8Array([0,1,2,3,4,5]), typed = new Uint16Array(storage.buffer,2,2);
    const blob = new B([storage.buffer,typed]); storage.fill(99); return bytes(blob);
  });
  await add('arrayBuffer and bytes outputs are independent copies', async () => {
    const blob = new B(['ABC']), a = await blob.arrayBuffer(), b = await blob.arrayBuffer(), c = await blob.bytes();
    new Uint8Array(a)[0] = 90; c[1] = 89;
    return { a: [...new Uint8Array(a)], b: [...new Uint8Array(b)], c: [...c],
      independent: a !== b && a !== c.buffer && b !== c.buffer, source: await blob.text() };
  });
  await add('nested Blob and File are immutable byte parts', async () => {
    const base = new B(['A'],{type:'TEXT/PLAIN'}), file = new F([base,'B'],'x.txt',{lastModified:17});
    const joined = new B([file,base,'C']); return { bytes: await bytes(joined), type: joined.type,
      fileType: file.type, name: file.name, lastModified: file.lastModified, fileIsBlob: file instanceof B };
  });
  await add('finite integer slices clamp and preserve original', async () => {
    const blob = new B(['abcdef'],{type:'TEXT/PLAIN'});
    const variants = [[0,6],[-3,-1],[2,2],[-99,99],[4,1]];
    const result = [];
    for (const [start,end] of variants) { const s = blob.slice(start,end,'TEXT/X'); result.push({ text: await s.text(),type:s.type,size:s.size }); }
    return { variants: result, source: await blob.text() };
  });
  await add('ordinary ASCII MIME normalization', async () => [
    new B([],{type:'TEXT/PLAIN;X=A'}).type,new B([],{type:'a\u0080b'}).type,new B([],{type:'a\nb'}).type]);
  await add('explicit finite integer File fields and slice result', async () => {
    const file = new F(['AB'],'plain.txt',{type:'TEXT/PLAIN',lastModified:-17}), slice = file.slice(1);
    return { name:file.name,lastModified:file.lastModified,type:file.type,size:file.size,text:await file.text(),
      tag:Object.prototype.toString.call(file),sliceText:await slice.text(),sliceIsBlob:slice instanceof B,sliceIsFile:slice instanceof F };
  });
  await add('bounded repeated reads and small-object pressure', async () => {
    let sum=0; const files=[];
    for(let i=0;i<64;i++)files.push(new F([new Uint8Array([i])],'f'+i,{lastModified:i}));
    for(const file of files)sum+=(await file.bytes())[0];
    return { objects:files.length,sum,lastText:await files.at(-1).text() };
  });
  return rows;
}

export async function receiverCases({Blob:B,File:F}) {
  const rows=[];
  for(const method of ['arrayBuffer','bytes','text','slice','stream']) {
    for(const [kind,receiver] of [['plain',{}],['prototype',B.prototype],['null',null]])
      rows.push({api:'Blob.'+method,receiver:kind,result:await outcome(()=>B.prototype[method].call(receiver))});
  }
  for(const [C,name] of [[B,'size'],[B,'type'],[F,'name'],[F,'lastModified']])
    for(const [kind,receiver] of [['plain',{}],['prototype',C.prototype]])
      rows.push({api:C.name+'.'+name,receiver:kind,result:await outcome(()=>Object.getOwnPropertyDescriptor(C.prototype,name).get.call(receiver))});
  return rows;
}

// Node-only known-deviation inventory: this is never included by the future
// guest fixture. No detach/shared/RAB or poisoned Error.prototype operation.
export async function nodeOnlyCases({Blob:B,File:F}) {
  const rows=[],add=async(name,run)=>rows.push({name,result:await run()});
  await add('options getter and conversion order',async()=>{
    const log=[],part={toString(){log.push('part-toString');return 'A';}};
    const type={toString(){log.push('type-toString');return 'TEXT/PLAIN';}};
    const options={get type(){log.push('get-type');return type;},get endings(){log.push('get-endings');return {toString(){log.push('endings-toString');return 'transparent';}};}};
    const parts={[Symbol.iterator](){log.push('iterator');return [part][Symbol.iterator]();}};
    const blob=new B(parts,options);return {log,text:await blob.text(),type:blob.type};
  });
  await add('MIME primitive conversion',async()=>{
    const result=[];for(const type of [17,true,null,undefined,Symbol('mime')])result.push({type:typeof type,result:await outcome(()=>new B([],{type}).type)});return result;
  });
  await add('endings conversion validation and native LF',async()=>{
    const rows=[];for(const endings of ['transparent','native','invalid',null,17])rows.push({endings,result:await outcome(async()=>new B(['a\r\nb\rc\n'],{endings}).text())});return rows;
  });
  await add('option dictionary primitive inputs',async()=>{
    const result=[];for(const options of [null,17,true,'x'])result.push({kind:typeof options,result:await outcome(()=>new B([],options).size)});return result;
  });
  await add('File field order and well-formed name',async()=>{
    const log=[],file=new F([{toString(){log.push('part');return 'A';}}],{toString(){log.push('name');return '\ud800.txt';}},
      {get type(){log.push('type');return 'TEXT/X';},get endings(){log.push('endings');return 'transparent';},get lastModified(){log.push('lastModified');return 7;}});
    return {log,name:file.name,lastModified:file.lastModified};
  });
  await add('File numeric lastModified semantics',async()=>{
    const result=[];for(const value of [1.75,-1.75,NaN,Infinity,-Infinity,-0,1n])
      result.push({input:String(value),result:await outcome(()=>encodeNumber(new F([],'n',{lastModified:value}).lastModified))});return result;
  });
  await add('File default timestamp is a live Node clock fact',async()=>{
    const before=Date.now(),file=new F([],'n'),after=Date.now();return {withinWindow:file.lastModified>=before&&file.lastModified<=after};
  });
  await add('slice full numeric coercion',async()=>{
    const blob=new B(['abc']),result=[];for(const end of [Infinity,NaN,1.75])result.push(await blob.slice(1,end).text());return result;
  });
  await add('ordinary iterator conversion error closes once',async()=>{
    const log=[],sentinel=new Error('part conversion');
    function* parts(){try{yield {toString(){log.push('convert');throw sentinel;}};}finally{log.push('finally');}}
    let same=false;try{new B(parts());}catch(error){same=error===sentinel;}return {same,log};
  });
  await add('Node Blob stream supports BYOB and cancellation',async()=>{
    const blob=new B(['ab']),reader=blob.stream().getReader({mode:'byob'}),first=await reader.read(new Uint8Array(3));
    await reader.cancel('done');reader.releaseLock();return {bytes:[...first.value],done:first.done,text:await blob.text()};
  });
  await add('nonempty result settlement ordering',async()=>{
    const rows=[];for(const method of ['arrayBuffer','bytes','text']){
      const log=[],promise=new B(['A'])[method]();promise.then(()=>log.push(method));
      Promise.resolve().then(()=>log.push('promise'));queueMicrotask(()=>log.push('microtask'));
      await promise;await Promise.resolve();rows.push({method,log});
    }return rows;
  });
  return rows;
}
