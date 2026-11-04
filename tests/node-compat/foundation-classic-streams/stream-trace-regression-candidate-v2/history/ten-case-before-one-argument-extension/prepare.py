"""New source-only ten-case successor. Never changes parent/current native files."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'stream-trace-regression-candidate-v1'
PARENT_SHA='636dfc0561891ff23f028b19289693aa77452fc25e8c5b415f1bf4a191afe7ac'
OBJECT_CASES=""" for(const explicitUtf8 of [false,true]){
  const trace=boundedTrace(),payload={id:1};let writeCalls=0,callbackCalls=0,finish=0,close=0,accepted,samePayload=false,valueId,encoding;
  let resolveClosed,rejectClosed;const closed=new Promise((resolve,reject)=>{resolveClosed=resolve;rejectClosed=reject;});
  const sink=new stream.Writable({objectMode:true,write(value,suppliedEncoding,callback){writeCalls++;samePayload=value===payload;valueId=value.id;
   encoding=suppliedEncoding===undefined?{type:'undefined'}:{type:typeof suppliedEncoding,value:suppliedEncoding};
   trace.push('object-write',samePayload,typeof suppliedEncoding);callback();}});
  sink.on('error',rejectClosed);sink.on('finish',()=>{finish++;trace.push('finish');});sink.on('close',()=>{close++;trace.push('close');resolveClosed();});
  const callback=error=>{if(error){rejectClosed(error);return;}callbackCalls++;trace.push('user-write-callback');};trace.push('before-write');
  accepted=explicitUtf8?sink.write(payload,'utf8',callback):sink.write(payload,callback);trace.push('write-return',accepted);sink.end();trace.push('after-end');await closed;
  check(writeCalls===1&&callbackCalls===1&&samePayload&&valueId===1&&finish===1&&close===1,'Object-mode valid-operation invariants failed');
  check(encoding.type==='undefined'||encoding.type==='string'||(encoding.type==='object'&&encoding.value===null),'Finite encoding carrier expected');
  results.push({id:'object-'+(explicitUtf8?'explicit-utf8':'default-encoding'),kind:'object-writable',explicitUtf8,accepted,writeCalls,callbackCalls,samePayload,valueId,payloadKeys:Object.keys(payload),encoding,finish,close,events:trace.events});
 }
"""
OLD_VALIDATE="""  for(let i=0;i<8;i++){const row=value.observed[i],expected=oracle.nodeObserved[i];assert.equal(row.id,expected.id);assert.equal(row.bytes,64);assert.equal(row.checksum,expected.checksum);assert.equal(row.writeCalls,1);assert.equal(row.callbackCalls,1);assert(row.events.length<128);}"""
NEW_VALIDATE="""  for(let i=0;i<10;i++){const row=value.observed[i],expected=oracle.nodeObserved[i];assert.equal(row.id,expected.id);assert.equal(row.kind,expected.kind);assert.equal(row.writeCalls,1);assert.equal(row.callbackCalls,1);assert(row.events.length<128);
   if(row.kind==='object-writable'){assert.equal(row.samePayload,true);assert.equal(row.valueId,1);assert.deepEqual(row.payloadKeys,['id']);assert.equal(row.finish,1);assert.equal(row.close,1);assert(['undefined','string','object'].includes(row.encoding.type));
    if(row.encoding.type==='undefined')assert.deepEqual(row.encoding,{type:'undefined'});else if(row.encoding.type==='object')assert.deepEqual(row.encoding,{type:'object',value:null});else assert.equal(typeof row.encoding.value,'string');
   }else{assert.equal(row.bytes,64);assert.equal(row.checksum,expected.checksum);}}"""
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    raw=(PARENT/'index.json').read_bytes();assert sha(raw)==PARENT_SHA
    for row in json.loads(raw)['files']:assert sha((PARENT/row['path']).read_bytes())==row['sha256']
    records=[];unchanged=[]
    def produce(name,edits):
        old=(PARENT/name).read_text();new=old;proof=[]
        for before,after,count in edits:
            assert new.count(before)==count,(name,before,new.count(before));new=new.replace(before,after);proof.append({'old':before,'new':after,'occurrences':count})
        reverse=new
        for edit in reversed(proof):assert reverse.count(edit['new'])==edit['occurrences'];reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse==old
        with(HERE/name).open('x')as stream:stream.write(new)
        records.append({'path':name,'beforeSha256':sha(old.encode()),'afterSha256':sha(new.encode()),'edits':proof,'reverseExact':True})
    for name in ['guest.mjs','preflight.template.mjs','run-component.UNEXECUTED.mjs']:
        data=(PARENT/name).read_bytes()
        with(HERE/name).open('xb')as stream:stream.write(data)
        unchanged.append({'path':name,'sha256':sha(data),'byteIdentical':True})
    produce('cases.mjs',[(' return results;\n',OBJECT_CASES+' return results;\n',1)])
    produce('component-driver.mjs',[
      ('assert.equal(oracle.groups,8);','assert.equal(oracle.groups,10);',1),
      ('assert.equal(value.observed.length,8);','assert.equal(value.observed.length,10);',1),
      (OLD_VALIDATE,NEW_VALIDATE,1),('const differences=[];for(let i=0;i<8;i++)','const differences=[];for(let i=0;i<10;i++)',1),
      ("const report={schemaVersion:1,status:","const report={schemaVersion:1,caseCount:10,status:",1),
      ("Observation gate: valid64byte operations", "Observation gate: eight valid64byte cases plus two ordinary object-mode encoding cases",1)])
    produce('node-oracle.mjs',[
      ('assert.equal(native.length,8);assert.equal(model.length,8);','assert.equal(native.length,10);assert.equal(model.length,10);',1),
      ('groups:8','groups:10',2),
      ('Bounded64byte writable HWM65/64/63 plus PassThrough pipeline sync/microtask callback traces; public state only.',
       'Original eight bounded64byte cases plus ordinary object-mode default/explicit-utf8 encoding probes; public state only.',1)])
    with(HERE/'transformation-proof.json').open('x')as stream:
        json.dump({'schemaVersion':1,'state':'FINITE_PUBLIC_OBJECT_ENCODING_SOURCE_EXTENSION','parentIndexSha256':PARENT_SHA,
         'originalEightCaseSourceUnchanged':True,'newCases':2,'records':records,'unchanged':unchanged,
         'nativeOrGuestOrHostOrComponentizerExecuted':False},stream,indent=2);stream.write('\n')
if __name__=='__main__':main()
