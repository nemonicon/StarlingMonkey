// Only the explicitly owned fresh benchmark child; no process-group signalling.
import {spawn} from 'node:child_process';
import {open,writeFile,readFile} from 'node:fs/promises';
import {finished} from 'node:stream/promises';
import {performance} from 'node:perf_hooks';
export async function collectWorker(entry,args,prefix){
 const stdout=await open(prefix+'.stdout','wx'),stderr=await open(prefix+'.stderr','wx');
 const child=spawn(process.execPath,[entry,...args],{stdio:['ignore','pipe','pipe'],timeout:300000,killSignal:'SIGTERM'}),start=performance.now();let error=null,outBytes=0,errBytes=0;
 child.on('error',value=>{error=value;});
 child.stdout.on('data',chunk=>{outBytes+=chunk.length;if(outBytes>4*1024*1024){error??=new Error('Bounded worker stdout exceeded');child.kill('SIGTERM');}});
 child.stderr.on('data',chunk=>{errBytes+=chunk.length;if(errBytes>4*1024*1024){error??=new Error('Bounded worker stderr exceeded');child.kill('SIGTERM');}});
 const outStream=stdout.createWriteStream({autoClose:false}),errStream=stderr.createWriteStream({autoClose:false});
 for(const stream of [outStream,errStream])stream.on('error',value=>{error??=value;child.kill('SIGTERM');});
 const streams=[finished(outStream).catch(value=>{error??=value;}),finished(errStream).catch(value=>{error??=value;})];
 const closed=new Promise(resolve=>child.once('close',(status,signal)=>resolve([status,signal])));
 child.stdout.pipe(outStream);child.stderr.pipe(errStream);const [status,signal]=await closed;
 await Promise.all(streams);await stdout.close();await stderr.close();
 const record={status,signal,error:error?.message??null,wholeProcessElapsedMs:performance.now()-start,stdoutBytes:outBytes,stderrBytes:errBytes};
 await writeFile(prefix+'.status.json',JSON.stringify(record)+'\n',{flag:'wx'});return{...record,stdout:await readFile(prefix+'.stdout','utf8')};
}
