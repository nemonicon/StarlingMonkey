// Pure owned-lifecycle policy. No process/clock/timer is started on import.
import {need,integer} from './planner.mjs';
export const MEASUREMENT_CWD='/Users/dan/dev/StarlingMonkey';
export const MEASUREMENT_ENV=Object.freeze({PATH:'/usr/bin:/bin:/usr/sbin:/sbin',LANG:'C',LC_ALL:'C',TZ:'UTC',
 RAYON_NUM_THREADS:'1',BINARYEN_CORES:'1',CARGO_BUILD_JOBS:'1',PYTHONDONTWRITEBYTECODE:'1'});
export const GLOBAL_HARD_MAX_MS=86400000;
export function lifecycleBounds({timeoutMs,publicCallTimeoutMs=600000,maxOutputBytes}){
 integer(timeoutMs,1,7200000,'whole owned worker bound');integer(publicCallTimeoutMs,1,600000,'public-call maximum; production phase pins600000, benign regression may be shorter');
 integer(maxOutputBytes,1,1048576,'bounded progress-only pipes');return true;
}
export function armedAck(event){need(event?.event==='cost-public-call-start','ack only for public-call start');return{event:'cost-public-call-armed',sequence:event.sequence,name:event.name};}
export function validateArmedAck(value,event){
 need(value&&typeof value==='string'&&value.length<=256,'bounded private parent ACK');const actual=JSON.parse(value),wanted=armedAck(event);
 need(JSON.stringify(actual)===JSON.stringify(wanted),'exact parent armed ACK for this call');return true;
}
// Markers are trusted only as a bounded operational watchdog protocol. Codec
// sample times are separately retained worker monotonic nanosecond intervals.
export class CallWatchdog{
 #active=null;#seen=0;#timeout;
 constructor({publicCallTimeoutMs=600000}={}){integer(publicCallTimeoutMs,1,600000,'bounded external public-call watchdog');this.#timeout=publicCallTimeoutMs;}
 accept(event,nowMs){
  need(typeof nowMs==='number'&&Number.isFinite(nowMs)&&nowMs>=0,'monotonic operational clock');
  need(event&&typeof event==='object'&&!Array.isArray(event),'ordinary progress marker');
  if(event.event==='cost-worker-complete'){need(this.#active===null,'completion outside public call');return;}
  need(['cost-public-call-start','cost-public-call-end'].includes(event.event),'exact bounded progress marker');
  integer(event.sequence,0,31,'finite per-worker call sequence');need(['identity','setup','batch','checkpoint'].includes(event.name),'finite public name');
  if(event.event==='cost-public-call-start'){
   need(this.#active===null&&event.sequence===this.#seen,'strict nonoverlapping call order');
   this.#active={sequence:event.sequence,name:event.name,startedMs:nowMs};
  }else{
   need(this.#active&&event.sequence===this.#active.sequence&&event.name===this.#active.name,'matching public-call end');
   need(nowMs-this.#active.startedMs<=this.#timeout,'public call plus raw-fsync deadline exceeded');this.#active=null;this.#seen++;
  }
 }
 expired(nowMs){return this.#active!==null&&nowMs-this.#active.startedMs>this.#timeout;}
 finish(){need(this.#active===null,'no incomplete public-call marker');return this.#seen;}
}
export function remainingBudget({startMs,nowMs,globalBudgetMs,workerBudgetMs}){
 integer(globalBudgetMs,1,GLOBAL_HARD_MAX_MS,'preselected global phase budget');integer(workerBudgetMs,1,7200000,'exact worker budget');
 need(Number.isFinite(startMs)&&Number.isFinite(nowMs)&&nowMs>=startMs,'monotonic global interval');
 need(nowMs-startMs+workerBudgetMs<=globalBudgetMs,'global budget cannot fit next full worker; fail phase without clipping/extension');return true;
}
