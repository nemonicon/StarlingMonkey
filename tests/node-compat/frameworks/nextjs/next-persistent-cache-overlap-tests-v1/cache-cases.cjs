'use strict';
// Source-only fixed suite. Imports and calls occur only when a future runner invokes it.
const fs = require('node:fs');
const path = require('node:path').posix;
const { Buffer } = require('node:buffer');
const { createHash } = require('node:crypto');
const Module = require('node:module');
const HANDLER = Object.freeze({sha256:'c1013ea6b84ca9bd0cab6d34090568152122f68c28bd0d8668d0cc3ccc4452c9',bytes:17798});
const DELEGATE = Object.freeze({sha256:'427a5a07865eb68f0335ef701636bc1e065e8809552d243333d22e5eefcaae29',bytes:28206});
const NODE_FS = Object.freeze({sha256:'6bc8642f72edfd01f57072915271eb8fe5e959fe56c2f44005f6d9a258abb0a7',bytes:1300});
const TAG = 'portable-fetch-v1';
const IDS = Object.freeze(['overlap-invalidation','duplicate-tuple','slot-collision','reset-during-computation',
  'association-limit','busy-publication','corrupt-read-poisons','invalid-set-consumes','value-and-shape-bounds',
  'layout-and-record-bounds','unsupported-batch-no-mutation']);
const hash = b => createHash('sha256').update(b).digest('hex');
function thrown(value) {
  const out = {type:value===null?'null':typeof value};
  if(value===null||['string','boolean','number'].includes(typeof value))out.value=value;
  if(value!==null&&(typeof value==='object'||typeof value==='function'))for(const k of ['name','message','code','operation','module']){
    const d=Object.getOwnPropertyDescriptor(value,k);if(d&&Object.hasOwn(d,'value')&&typeof d.value==='string')out[k]=d.value.slice(0,1024);
  }
  return out;
}
function requireCondition(ok,label) { if(!ok)throw new Error(label); }
function directory(p) {
  const s=fs.lstatSync(p);requireCondition(s.isDirectory()&&!s.isSymbolicLink()&&fs.realpathSync(p)===p,'canonical existing directory: '+p);
}
function canonical(p) { requireCondition(typeof p==='string'&&p.startsWith('/')&&p.length<=2048&&!p.includes('\0')&&path.normalize(p)===p,'canonical absolute path');return p; }
function checked(p,pin) {
  const s=fs.lstatSync(p);requireCondition(s.isFile()&&!s.isSymbolicLink()&&s.nlink===1&&fs.realpathSync(p)===p&&s.size===pin.bytes,'pinned ordinary Source');
  const b=fs.readFileSync(p);requireCondition(b.length===pin.bytes&&hash(b)===pin.sha256,'actual handler/delegate Source pin');
  return {path:p,...pin};
}
function inventory(root) {
  const files=[];let bytes=0,dirs=0;
  function walk(p){directory(p);dirs++;requireCondition(dirs<=128,'suite directory cap');
    for(const name of fs.readdirSync(p).sort()){
      requireCondition(typeof name==='string'&&!['.','..'].includes(name)&&!name.includes('/'),'ordinary child name');
      const q=path.join(p,name),s=fs.lstatSync(q);requireCondition(!s.isSymbolicLink(),'no suite symlinks');
      if(s.isDirectory())walk(q);else{
        requireCondition(s.isFile()&&s.nlink===1&&s.size>=0&&s.size<=65537&&fs.realpathSync(q)===q,'bounded ordinary suite file');
        bytes+=s.size;requireCondition(files.length<256&&bytes<=1048576,'suite logical file/byte cap');
        const b=fs.readFileSync(q);requireCondition(b.length===s.size,'suite file exact bytes');files.push({path:q.slice(root.length+1),bytes:b.length,sha256:hash(b)});
      }
    }
  }walk(root);return {files,directories:dirs,logicalBytes:bytes,modeOrWasiRightsInferred:false};
}
function key(n){return n.toString(16).padStart(64,'0');}
function getContext(idx=1,extra={}){return {kind:'FETCH',fetchIdx:idx,tags:[TAG],...extra};}
function setContext(idx=1,extra={}){return {fetchCache:true,fetchIdx:idx,tags:[TAG],...extra};}
function value(body){return {kind:'FETCH',data:{headers:{},body,status:200,url:''},revalidate:60};}
function barrier(){let release;const promise=new Promise(r=>{release=r;});return {promise,release};}
async function releaseAndCollect(tasks,hold,action){
  // Observe every task immediately, release even on an invalidation/reset error,
  // and retain the original primary including a falsy rejection.
  const collecting=Promise.allSettled(tasks);let failed=false,primary;
  try{await action();}catch(error){failed=true;primary=error;}
  hold.release();const completed=await collecting;
  if(failed)throw primary;
  for(const item of completed)if(item.status==='rejected')throw item.reason;
}

async function runCacheSuite({applicationRoot,testRoot,report}) {
  requireCondition(report&&typeof report==='object'&&!Array.isArray(report),'caller retains a partial report object');
  Object.assign(report,{schemaVersion:1,state:'PERSISTENT_CACHE_REAL_FS_SUITE_RUNNING_V1',passed:false,plannedCaseIds:[...IDS],cases:[],unattemptedCaseIds:[...IDS],assertions:0,
    actualCacheFilesystemUsed:false,actualNextDelegateUsed:false,cacheImplementationModified:false,fakeDependencies:false,
    overlapScope:'Deterministically held application-computation promises between real get and set; no mid-sync-FS or concurrent-process execution claim.',
    legacyGenerationGateChanged:false,fullNextAccepted:false,guestExecutedRequiresExternalParentProof:true});
  let active;
  function check(ok,label){const a={label,passed:ok===true};active.assertions.push(a);report.assertions++;if(!a.passed)throw new Error(label);}
  async function refuses(action,code,operation){let caught=false,v;try{await action();}catch(e){caught=true;v=e;}
    if(!caught){check(false,'expected '+code);return;}
    if(!v||v.code!==code||(operation!==undefined&&v.operation!==operation)){
      active.assertions.push({label:'unexpected original rejection',passed:false,expectedCode:code,expectedOperation:operation??null,actual:thrown(v)});report.assertions++;throw v;
    }
    check(true,'original rejection '+code+(operation?' / '+operation:''));return v;
  }
  try{
    applicationRoot=canonical(applicationRoot);testRoot=canonical(testRoot);report.actualCacheFilesystemUsed=true;directory(applicationRoot);directory(testRoot);
    requireCondition(testRoot!==applicationRoot&&!testRoot.startsWith(applicationRoot+'/')&&!applicationRoot.startsWith(testRoot+'/'),'source and owned test roots disjoint');
    requireCondition(fs.readdirSync(testRoot).length===0,'owned suite root must initially be empty');
    report.applicationRoot=applicationRoot;report.testRoot=testRoot;
    report.handler=checked(path.join(applicationRoot,'cache-handler.cjs'),HANDLER);
    report.delegate=checked(path.join(applicationRoot,'node_modules/next/dist/server/lib/incremental-cache/file-system-cache.js'),DELEGATE);
    report.nodeFsHelper=checked(path.join(applicationRoot,'node_modules/next/dist/server/lib/node-fs-methods.js'),NODE_FS);
    const req=Module.createRequire(path.join(applicationRoot,'server.js'));
    requireCondition(req('next/package.json').version==='16.4.5','actual pinned Next package');
    const Handler=req(path.join(applicationRoot,'cache-handler.cjs'));
    const nodeFs=req('next/dist/server/lib/node-fs-methods.js').nodeFs;
    requireCondition(typeof Handler==='function'&&nodeFs&&typeof nodeFs.readFile==='function'&&typeof nodeFs.stat==='function','real Next nodeFs helper');
    function fixture(id,{cache=true}={}){
      const root=path.join(testRoot,id);fs.mkdirSync(root);fs.mkdirSync(root+'/.next');fs.mkdirSync(root+'/.next/server');if(cache)fs.mkdirSync(root+'/.next/cache');
      const storage=root+'/.next/cache/portable-fetch-v2';
      const make=()=>{const h=new Handler({dev:false,flushToDisk:true,maxMemoryCacheSize:0,serverDistDir:root+'/.next/server',fs:nodeFs,revalidatedTags:[]});report.actualNextDelegateUsed=true;return h;};
      const entries=()=>fs.readdirSync(storage+'/entries').sort();
      const entry=()=>{const names=entries().filter(n=>n.endsWith('.json'));requireCondition(names.length===1,'one API-published entry expected');return storage+'/entries/'+names[0];};
      return {root,storage,make,entries,entry};
    }
    const cases=[
      ['overlap-invalidation',async()=>{
        const f=fixture('overlap-invalidation'),a=f.make(),b=f.make(),k=key(1),hold=barrier();
        const tasks=[a,b].map((h,i)=>(async()=>{check(await h.get(k,getContext(i+1))===null,'overlapping computation starts on real miss');await hold.promise;await h.set(k,value('old-'+i),setContext(i+1));})());
        // Both synchronous get bodies have run; no FS/entropy provider is replaced.
        await releaseAndCollect(tasks,hold,()=>f.make().revalidateTag(TAG,{expire:0}));
        check(await f.make().get(k,getContext(10))===null,'both delayed old-epoch writes skipped');
        const fresh=f.make();await fresh.get(k,getContext(11));await fresh.set(k,value('fresh'),setContext(11));
        check((await f.make().get(k,getContext(12))).value.data.body==='fresh','fresh computation recovers after overlap');
      }],
      ['duplicate-tuple',async()=>{
        const f=fixture('duplicate-tuple'),h=f.make(),k=key(2),hold=barrier();
        const tasks=[0,1].map(i=>(async()=>{await h.get(k,getContext(1));await hold.promise;await h.set(k,value('duplicate-'+i),setContext(1));})());await releaseAndCollect(tasks,hold,()=>{});
        check(f.entries().length===0,'overlapping same tuple cannot publish first/last winner');
        await h.get(k,getContext(2));await h.set(k,value('distinct'),setContext(2));
        await h.set(k,value('late-reuse'),setContext(1));
        check((await f.make().get(k,getContext(3))).value.data.body==='distinct','poisoned tuple cannot overwrite later distinct computation');
      }],
      ['slot-collision',async()=>{
        const f=fixture('slot-collision'),a=f.make(),b=f.make(),ka='00'+'1'.repeat(62),kb='40'+'2'.repeat(62);
        await Promise.all([a.get(ka,getContext(1)),b.get(kb,getContext(2))]);
        await a.set(ka,value('A'),setContext(1));await b.set(kb,value('B'),setContext(2));
        check(f.entries().filter(n=>n.endsWith('.json')).length===1,'documented same slot remains one bounded file');
        check(await f.make().get(ka,getContext(3))===null,'collision is miss rather than wrong-key data');
        check((await f.make().get(kb,getContext(4))).value.data.body==='B','last complete collision publication is readable');
      }],
      ['reset-during-computation',async()=>{
        const f=fixture('reset-during-computation'),h=f.make(),k=key(3),hold=barrier();
        const pending=(async()=>{await h.get(k,getContext(1));await hold.promise;await h.set(k,value('delayed'),setContext(1));})();
        await releaseAndCollect([pending],hold,()=>h.resetRequestCache());
        await h.get(k,getContext(2));await h.set(k,value('still-disabled'),setContext(2));
        check(f.entries().length===0,'post-start reset permanently disables same-instance delayed/new writes');
        const fresh=f.make();fresh.resetRequestCache();await fresh.get(k,getContext(3));await fresh.set(k,value('new-instance'),setContext(3));
        check((await f.make().get(k,getContext(4))).value.data.body==='new-instance','initial reset on fresh instance remains operational');
      }],
      ['association-limit',async()=>{
        const f=fixture('association-limit'),h=f.make();for(let i=0;i<64;i++)await h.get(key(i),getContext(i));
        await h.set(key(0),value('at64'),setContext(0));check((await f.make().get(key(0),getContext(70))).value.data.body==='at64','64 associations still permit associated publication');
        await h.get(key(64),getContext(64));await h.set(key(1),value('after65'),setContext(1));await h.get(key(0),getContext(80));await h.set(key(0),value('re-enabled'),setContext(80));
        check((await f.make().get(key(0),getContext(81))).value.data.body==='at64','65th association disables all later same-instance writes without eviction/reuse');
      }],
      ['busy-publication',async()=>{
        const f=fixture('busy-publication'),k=key(4),a=f.make();await a.get(k,getContext(1));await a.set(k,value('old'),setContext(1));
        const target=f.entry(),pending=target.replace(/\.json$/,'.pending'),before=fs.readFileSync(target);fs.writeFileSync(pending,'retained-incomplete',{flag:'wx'});
        const b=f.make();await b.get(k,getContext(2));await refuses(()=>b.set(k,value('new'),setContext(2)),'ERR_SM_CACHE_BUSY','publish.write');
        check(fs.readFileSync(target).equals(before)&&fs.readFileSync(pending,'utf8')==='retained-incomplete','busy publication preserves target and pending bytes');
        await b.set(k,value('retry'),setContext(2));check(fs.readFileSync(target).equals(before),'failed publication consumed tuple; no silent retry/reclamation');
      }],
      ['corrupt-read-poisons',async()=>{
        const f=fixture('corrupt-read-poisons'),k=key(5),a=f.make();await a.get(k,getContext(1));await a.set(k,value('good'),setContext(1));
        const target=f.entry(),original=fs.readFileSync(target);fs.writeFileSync(target,'{}');const b=f.make();
        await refuses(()=>b.get(k,getContext(2)),'ERR_SM_CACHE_CORRUPT','read');check(fs.readFileSync(target,'utf8')==='{}','corrupt file is not removed or replaced online');
        fs.writeFileSync(target,original); // Explicit owned fixture repair, not cache recovery behavior.
        await b.set(k,value('poisoned'),setContext(2));check(fs.readFileSync(target).equals(original),'failed read poisons its computation association after fixture repair');
        check((await f.make().get(k,getContext(3))).value.data.body==='good','fresh instance reads explicitly restored original bytes');
      }],
      ['invalid-set-consumes',async()=>{
        const f=fixture('invalid-set-consumes'),h=f.make(),k=key(6);await h.get(k,getContext(1));
        await refuses(()=>h.set(k,{kind:'FETCH',data:{},revalidate:60},setContext(1)),'ERR_SM_CACHE_CORRUPT','value.data');
        await h.set(k,value('corrected-retry'),setContext(1));check(f.entries().length===0,'validation rejection consumes tuple before corrected delayed retry');
        await h.get(k,getContext(2));await h.set(k,value('new-computation'),setContext(2));
        check((await f.make().get(k,getContext(3))).value.data.body==='new-computation','new computation after refusal can publish');
      }],
      ['value-and-shape-bounds',async()=>{
        const f=fixture('value-and-shape-bounds'),h=f.make(),k=key(7),base=Buffer.byteLength(JSON.stringify(value('')),'utf8');
        const exact=value('x'.repeat(32768-base));check(Buffer.byteLength(JSON.stringify(exact),'utf8')===32768,'construct exact documented FETCH value byte boundary');
        await h.get(k,getContext(1));await h.set(k,exact,setContext(1));check((await f.make().get(k,getContext(2))).value.data.body.length===exact.data.body.length,'exact32768 value accepted');
        const target=f.entry(),before=fs.readFileSync(target);await h.get(k,getContext(3));await refuses(()=>h.set(k,value(exact.data.body+'x'),setContext(3)),'ERR_SM_CACHE_LIMIT','value');
        await h.set(k,value('retry'),setContext(3));check(fs.readFileSync(target).equals(before),'over-limit value cannot publish and cannot reuse consumed tuple');
        let invoked=0;const accessor=value('x');Object.defineProperty(accessor.data,'body',{enumerable:true,get(){invoked++;throw 0;}});
        await h.get(k,getContext(4));await refuses(()=>h.set(k,accessor,setContext(4)),'ERR_SM_CACHE_PROFILE','json');check(invoked===0,'value getter is not invoked, including falsy throw body');
        await h.get(k,getContext(5));const bad=value('x');bad.data.url='u'.repeat(2049);await refuses(()=>h.set(k,bad,setContext(5)),'ERR_SM_CACHE_PROFILE','value.data');
        await h.get(k,getContext(6));const fields=value('x');fields.data.headers=Object.fromEntries(Array.from({length:65},(_,i)=>['h'+i,'']));await refuses(()=>h.set(k,fields,setContext(6)),'ERR_SM_CACHE_LIMIT','json');
        check(fs.readFileSync(target).equals(before),'all shape/bounds refusals leave published value unchanged');
      }],
      ['layout-and-record-bounds',async()=>{
        const absent=fixture('missing-parent',{cache:false});await refuses(()=>absent.make().get(key(8),getContext(1)),'ERR_SM_CACHE_IO','layout');
        check(fs.readdirSync(absent.root+'/.next').sort().join(',')==='server','missing private parent is not created implicitly');
        const f=fixture('layout-and-record-bounds'),h=f.make(),k=key(8);await h.get(k,getContext(1));await h.set(k,value('small'),setContext(1));
        const target=f.entry(),before=fs.readFileSync(target);fs.writeFileSync(target,Buffer.alloc(65537,32));
        await refuses(()=>f.make().get(k,getContext(2)),'ERR_SM_CACHE_CORRUPT','layout');check(fs.lstatSync(target).size===65537,'over-cap stat refusal leaves original owned fixture file intact');
        fs.writeFileSync(target,before);const epoch=f.storage+'/epochs/'+fs.readdirSync(f.storage+'/epochs').find(n=>n.endsWith('.json')),eb=fs.readFileSync(epoch);fs.writeFileSync(epoch,Buffer.alloc(2049,32));
        await refuses(()=>f.make().get(k,getContext(3)),'ERR_SM_CACHE_CORRUPT','layout');fs.writeFileSync(epoch,eb);
        check((await f.make().get(k,getContext(4))).value.data.body==='small','fresh handler recovers after explicit fixture-only record restoration');
      }],
      ['unsupported-batch-no-mutation',async()=>{
        const f=fixture('unsupported-batch-no-mutation'),h=f.make(),k=key(9);await h.get(k,getContext(1));await h.set(k,value('before'),setContext(1));
        const before=inventory(f.root);await refuses(()=>h.revalidateTag([TAG,'_N_T_/layout'],{expire:0}),'ERR_SM_CACHE_UNSUPPORTED','revalidateTag');
        check(JSON.stringify(inventory(f.root))===JSON.stringify(before),'whole invalidation batch refuses before persistent mutation');
        check((await f.make().get(k,getContext(2))).value.data.body==='before','unsupported mutation does not invalidate published value');
      }],
    ];
    requireCondition(cases.map(x=>x[0]).join(',')===IDS.join(','),'fixed suite table');
    for(const [id,body]of cases){active={id,passed:false,assertions:[]};report.cases.push(active);report.unattemptedCaseIds=IDS.slice(report.cases.length);await body();active.passed=true;}
    report.inventory=inventory(testRoot);report.state='PERSISTENT_CACHE_REAL_FS_SUITE_PASSED_V1';report.passed=true;return report;
  }catch(error){report.state='PERSISTENT_CACHE_REAL_FS_SUITE_FAILED_V1';report.passed=false;report.thrown=thrown(error);if(active)active.thrown=thrown(error);throw error;}
}
module.exports={runCacheSuite,describeThrown:thrown};
