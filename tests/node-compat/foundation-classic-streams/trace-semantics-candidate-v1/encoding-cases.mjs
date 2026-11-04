// Ordinary object/byte mode encoding and return-value boundaries only.
const encoded=value=>value===undefined?{type:'undefined'}:value===null?{type:'null'}:{type:typeof value,value};
export async function encodingCases(provider){
 const {stream,promises,dependencies:{Buffer,nextTick}}=provider,rows=[];
 for(const encoding of [undefined,null,'utf8','not-an-encoding']){
  const observed=[];const sink=new stream.Writable({objectMode:true,highWaterMark:1,write(value,enc,callback){observed.push({value,encoding:encoded(enc),receiver:this===sink,arguments:arguments.length});callback();}});
  let accepted;try{accepted=sink.write({value:1},encoding);}catch(error){const closed=new Promise(resolve=>sink.once('close',resolve));sink.destroy();await closed;rows.push({id:'object-'+JSON.stringify(encoded(encoding)),error:{name:error.name,code:error.code},observed});continue;}
  sink.end();await promises.finished(sink);rows.push({id:'object-'+JSON.stringify(encoded(encoding)),accepted,observed,finished:sink.writableFinished});
 }
 for(const highWaterMark of [0,1,64])for(const bytes of [0,1,64]){
  const observed=[];const sink=new stream.Writable({highWaterMark,write(value,enc,callback){observed.push({bytes:value.length,encoding:enc});callback();}});
  const accepted=sink.write(Buffer.alloc(bytes));sink.end();await promises.finished(sink);rows.push({id:'sync-hwm-'+highWaterMark+'-bytes-'+bytes,accepted,observed,finished:sink.writableFinished});
 }
 const observed=[];const sink=new stream.Writable({objectMode:true,highWaterMark:1,write(value,enc,callback){observed.push(encoded(enc));callback();}});
 await new Promise((resolve,reject)=>{sink.write({value:2},error=>error?reject(error):resolve());});sink.end();await promises.finished(sink);
 rows.push({id:'object-public-callback-overload-encoding',observed});
 await new Promise(resolve=>nextTick(resolve));return rows;
}
