// ROOT-AUTHORIZED BENIGN HOST TEST ONLY. No guest/provider/codec/tool imports.
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {createParentHandshake} from './public-call-channel.mjs';
import {need} from './planner.mjs';
const mode=process.argv[2],root=process.argv[3];need(['normal','unfinished-raw0','blocking'].includes(mode),'finite benign fixture mode');
const output=await DurableOutput.create(root),channel=createParentHandshake({input:process.stdin,output:process.stdout});
try{
 await output.write('before.json',{schemaVersion:1,fixture:mode,sequence:0,name:'batch',noGuestCodecOrProvider:true,partial:true},{json:true});
 await channel.start({event:'cost-public-call-start',sequence:0,name:'batch'});
 if(mode==='blocking'){for(;;){/* deliberately synchronous benign CPU; parent must interrupt */}}
 await output.write('raw.json',{schemaVersion:1,fixture:mode,returned:{type:'string',value:'benign-host-fixture',fullPrimitiveCaptured:true},partial:true},{json:true});
 if(mode==='normal'){channel.end({event:'cost-public-call-end',sequence:0,name:'batch'});process.stdout.write(JSON.stringify({event:'cost-worker-complete'})+'\n');}
 await output.recheck();
}finally{channel.close();await output.close();}
