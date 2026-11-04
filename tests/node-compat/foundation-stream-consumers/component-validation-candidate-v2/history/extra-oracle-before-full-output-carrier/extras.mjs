// Ordinary supported public inputs only. No Blob/native reader/private scheduler.
export const extraNames=Object.freeze([
 'selected node:stream/web ReadableStream text',
 'selected node:stream/web ReadableStream json',
 'selected classic Readable text',
 'selected classic Readable json',
 'exact string/output cap accepts full content',
 'exact4096 empty chunks accept',
 'native Buffer visible offset input is immutable',
 'decoder/json state recovers between calls',
]);
export async function extraCase(c,{Buffer,Readable,ReadableStream},index){
 function web(chunks){return new ReadableStream({start(controller){for(const chunk of chunks)controller.enqueue(chunk);controller.close();}});}
 function classic(chunks){let sent=false;return new Readable({objectMode:true,read(){if(sent)return;sent=true;for(const chunk of chunks)this.push(chunk);this.push(null);}});}
 if(index===0)return c.text(web([new Uint8Array([0xe2]),'X',new Uint8Array([0x82,0xac])]));
 if(index===1)return c.json(web([new Uint8Array([0xef,0xbb,0xbf,123,34,120,34,58]),'2}']));
 if(index===2)return c.text(classic([new Uint8Array([65]),'B',new Uint8Array([67])]));
 if(index===3)return c.json(classic(['{"x":',new Uint8Array([50,125])]));
 if(index===4){const wanted='a'.repeat(1048576),actual=await c.text([wanted]);if(actual!==wanted)throw new Error('Exact cap content');return{length:actual.length,fullContentEqual:true};}
 if(index===5)return{value:await c.text(Array.from({length:4096},()=>'')),chunks:4096};
 if(index===6){const backing=new ArrayBuffer(8),window=new Uint8Array(backing,2,3);window.set([65,66,67]);const input=Buffer.from(backing,2,3),before=input.toString('hex'),value=await c.text([input,'!']);return{value,before,after:input.toString('hex'),offset:input.byteOffset,backingBytes:backing.byteLength,isBuffer:Buffer.isBuffer(input)};}
 if(index===7){let syntax=false;try{await c.json(['{']);}catch(error){syntax=error.name==='SyntaxError';}return{syntax,pendingFlush:await c.text([new Uint8Array([0xe2])]),freshPartial:await c.text([new Uint8Array([0x82,0xac])]),json:await c.json(['{"ok":true}'])};}
 throw new RangeError('Finite extra case index');
}
