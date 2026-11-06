// Real pinned Node differentials +explicit TEST-ONLY provider. Never imports app,
// calls native guest provider, starts a server or runs a target engine.
import assert from 'node:assert/strict';
import * as nodeUrl from 'node:url';
import * as nodeOs from 'node:os';
import paths from 'node:path';
import {readFile,writeFile,mkdtemp,mkdir,rm,stat,realpath} from 'node:fs/promises';
import {createStartupFacade} from './startup-core.mjs';
import {createEventsFacade} from '../../../../builtins/node-compat/events.mjs';
import querystring from '../../../../builtins/node-compat/querystring.mjs';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
const inventory=JSON.parse(await readFile(new URL('./startup-builtin-inventory.node-v22.14.0.json',import.meta.url),'utf8')).modules;
const EE=createEventsFacade(Symbol('test-only-protected-key')).EventEmitter;
class TestURL extends nodeUrl.URL {static canParse=undefined;}
// Subclass inherits REAL Node URL parsing; the missing static method exercises
// the actual new guest canParse algorithm, not Node's existing static method.
const owned=await mkdtemp('/private/tmp/starling-node-compat/next-startup-v1-host-');
let cwd=owned;await mkdir(paths.join(owned,'sub'));
let deployed=false,reads=0,now=123456789012345n,checks=0;const writes=[],tickQueue=[],builtins=new Map();
const provider={
 checkDeployed(){if(!deployed)throw Object.assign(Error('INIT'),{code:'ERR_SM_NODE_STARTUP_INITIALIZATION'});},
 initial(){this.checkDeployed();reads++;return{environment:[['HOME',owned],['TMPDIR',owned+'/'],['NEXT_RUNTIME','nodejs'],['__proto__','safe']],arguments:['app.wasm','next-entry']};},
 monotonic(){this.checkDeployed();return now;},cwd(){this.checkDeployed();return cwd;},
 chdir(p){this.checkDeployed();const next=paths.resolve(cwd,p);if(next!==owned&&!next.startsWith(owned+'/'))throw Object.assign(Error('rights'),{code:'EACCES'}); // actual host FS test only
  if(!actualDirectories.has(next))throw Object.assign(Error('not directory'),{code:'ENOTDIR'});cwd=next;},
 write(fd,value){this.checkDeployed();writes.push({fd,bytes:[...typeof value==='string'?Buffer.from(value):value]});},
 getBuiltin(id){return builtins.get(id);},errnoConstants:Object.freeze({errno:Object.freeze({EACCES:13,ENOENT:2})})};
const actualDirectories=new Set([await realpath(owned),await realpath(paths.join(owned,'sub'))]);
for(const p of actualDirectories)assert((await stat(p)).isDirectory());
const a={kernel:provider,EventEmitter:EE,URL:TestURL,URLSearchParams:nodeUrl.URLSearchParams,querystring,paths:paths.posix,Buffer,nextTick(cb,...args){tickQueue.push(()=>cb(...args));},inventory};
const graph=createStartupFacade(a),p=graph.process.default,os=graph.os.default,url=graph.url.default;
const outcomes=[];
function test(id,fn){fn();checks++;outcomes.push({id,passed:true});}
function err(fn){try{fn();return null;}catch(e){return{name:e.name,code:e.code??null};}}
function equalResult(id,actual,expected){test(id,()=>assert.deepEqual(actual(),expected()));}
try {
 test('install-no-host-data',()=>{assert.equal(reads,0);assert.deepEqual(Object.keys(p.env),[]);assert.deepEqual(p.argv,[]);assert.equal(graph.state().bootstrapped,false);});
 test('bootstrap-INIT-refused',()=>{assert.equal(err(()=>graph.startup.bootstrap()).code,'ERR_SM_NODE_STARTUP_INITIALIZATION');assert.equal(reads,0);});
 deployed=true;test('bootstrap-real-stable-objects',()=>{const env=p.env,argv=p.argv;assert.equal(graph.startup.bootstrap(),p);assert.equal(p.env,env);assert.equal(p.argv,argv);assert.equal(graph.process.env,env);assert.equal(reads,1);assert.equal(env.__proto__,'safe');assert.equal(Object.getPrototypeOf(env),null);assert.deepEqual(argv,['app.wasm','next-entry']);});
 test('bootstrap-repeat-does-not-reread',()=>{graph.startup.bootstrap();assert.equal(reads,1);});
 for(const[id,ns]of Object.entries({'node:process':graph.process,'node:os':graph.os,'node:url':graph.url}))test('exact-inventory-'+id,()=>assert.deepEqual(Object.keys(ns).sort(),inventory[id]));
 test('default-function-identity',()=>{assert.equal(graph.process.cwd,p.cwd);assert.equal(graph.os.cpus,os.cpus);assert.equal(graph.url.URL,TestURL);assert.equal(graph.url.URLSearchParams,nodeUrl.URLSearchParams);});
 test('process-string-env-mutation',()=>{const key='STARLING_STARTUP_TEST_ONLY';const previous=process.env[key];try{p.env[key]='7';process.env[key]='7';assert.equal(p.env[key],process.env[key]);delete p.env[key];delete process.env[key];assert.equal(p.env[key],process.env[key]);}finally{if(previous!==undefined)process.env[key]=previous;}});
 test('process-env-coercion-explicit-deviation',()=>{p.env.PROFILE_NUMBER=7;assert.equal(p.env.PROFILE_NUMBER,7);delete p.env.PROFILE_NUMBER;});
 test('logical-cwd-real-directory',()=>{assert.equal(p.cwd(),owned);p.chdir('sub');assert.equal(p.cwd(),paths.join(owned,'sub'));p.chdir('..');assert.equal(p.cwd(),owned);});
 test('failed-chdir-preserves-cwd',()=>{const before=p.cwd();assert.equal(err(()=>p.chdir('missing')).code,'ENOTDIR');assert.equal(p.cwd(),before);});
 test('actual-guest-events-methods',()=>{const values=[];const f=v=>values.push(v);p.on('x',f);p.once('x',v=>values.push(v*2));assert.equal(p.listeners('x').length,2);assert.equal(p.emit('x',4),true);p.off('x',f);p.emit('x',9);assert.deepEqual(values,[4,8]);p.removeAllListeners('x');});
 test('nexttick-injected-native-seam',()=>{let value=0;p.nextTick((a,b)=>value=a+b,3,5);assert.equal(value,0);tickQueue.shift()();assert.equal(value,8);});
 test('nexttick-validates-before-enqueue',()=>{assert.equal(err(()=>p.nextTick(null)).code,'ERR_INVALID_ARG_TYPE');assert.equal(tickQueue.length,0);});
 test('hrtime-integer-seconds-nanoseconds',()=>assert.deepEqual(p.hrtime(),[123456,789012345]));
 test('hrtime-delta-normalized',()=>assert.deepEqual(p.hrtime([123456,800000000]),[-1,989012345]));
 test('hrtime-bigint-no-precision-loss',()=>assert.equal(p.hrtime.bigint(),123456789012345n));
 test('uptime-deployed-origin',()=>{now+=2500000000n;assert.equal(p.uptime(),2.5);});
 test('actual-builtin-value-identity',()=>{builtins.set('node:process',p);builtins.set('process',p);assert.equal(p.getBuiltinModule('process'),p);assert.equal(p.getBuiltinModule('node:process'),p);assert.equal(p.getBuiltinModule('missing'),undefined);});
 test('stdio-utf8-and-offset-window',()=>{let done=false;const bytes=Uint8Array.of(99,1,2,88);assert.equal(p.stdout.write('€',()=>done=true),true);p.stderr.write(bytes.subarray(1,3));assert.equal(done,false);tickQueue.shift()();assert.equal(done,true);assert.deepEqual(writes,[{fd:1,bytes:[226,130,172]},{fd:2,bytes:[1,2]}]);});
 test('stdio-bad-encoding-refused',()=>assert.equal(err(()=>p.stdout.write('ff','hex')).code,'ERR_SM_NODE_UNSUPPORTED'));
 test('truthful-guest-facts',()=>{assert.equal(p.platform,'wasi');assert.equal(p.arch,'wasm32');assert.equal(p.pid,undefined);assert.equal(p.versions.v8,undefined);assert.equal(p.version,'v22.14.0');assert.equal(p.release.name,'starlingmonkey');});
 test('os-unknown-cpu-no-fabricated-model',()=>assert.deepEqual(os.cpus(),[]));
 test('os-profile-constants',()=>{assert.equal(os.EOL,'\n');assert.equal(os.endianness(),'LE');assert.equal(os.platform(),'wasi');assert.equal(os.arch(),'wasm32');assert.equal(os.type(),'WASI');assert.equal(os.constants,provider.errnoConstants);assert.equal(os.devNull,undefined);});
 test('os-env-derived-paths',()=>{assert.equal(os.homedir(),owned);assert.equal(os.tmpdir(),owned);});
 test('os-homedir-no-invented-fallback',()=>{const old=p.env.HOME;delete p.env.HOME;assert.equal(err(()=>os.homedir()).code,'ERR_SM_NODE_UNSUPPORTED');p.env.HOME=old;});
 const legacy=[{}, {pathname:'/a?b#c',query:{x:['1','2'],s:'a b'},hash:'tail'}, {protocol:'http',hostname:'example.com',pathname:'a'}, {protocol:'https:',host:'x.test:8080',auth:'u:p@ss',pathname:'/ü'}, {protocol:'http:',hostname:'::1',port:8080,pathname:'/'}, {protocol:'file:',pathname:'/a'}, {protocol:'mailto:',pathname:'a@example.com'}, {slashes:true,host:'x',pathname:'a'}, {pathname:'/a',search:'x=#y',hash:'z'}, {protocol:'wss:',hostname:'x',pathname:'/'}, {protocol:'HTTP:',hostname:'x',pathname:'a'}, {protocol:'https:',hostname:'[::1]',auth:'a:b:c',pathname:'/'}, {query:{zero:0,bool:true,absent:undefined,list:['ü','&']}}, {pathname:'',search:'?',hash:'#'}];
 for(let i=0;i<legacy.length;i++)equalResult('legacy-format-'+i,()=>url.format(legacy[i]),()=>nodeUrl.format(legacy[i]));
 const filePaths=['/a','/a b/ü','/a%23#?','/a\\b','/a\nb\rc\td','/a/../b/','relative/x','../parent','/a//b','/😀','/','/.hidden'];
 for(let i=0;i<filePaths.length;i++){const value=filePaths[i];equalResult('pathToFileURL-'+i,()=>url.pathToFileURL(value,{windows:false}).href,()=>nodeUrl.pathToFileURL(paths.resolve(owned,value)+(value.endsWith('/')&&value!=='/'?'/':''),{windows:false}).href);}
 const fileURLs=['file:///a','file:///a%20b/%E2%82%AC','file://localhost/a','file:///a%5Cb','file:///a?query#hash','http://x/a','file://remote/a','file:///a%2Fb','file:///a%2fb','file:///a%ZZ'];
 for(let i=0;i<fileURLs.length;i++){const value=fileURLs[i];test('fileURLToPath-'+i,()=>{const ae=err(()=>url.fileURLToPath(value,{windows:false})),ne=err(()=>nodeUrl.fileURLToPath(value,{windows:false}));if(ae||ne)assert.deepEqual(ae,ne);else assert.equal(url.fileURLToPath(value),nodeUrl.fileURLToPath(value,{windows:false}));});}
 for(const[value,base]of [['https://x'],['/a','https://x/'],['bad'],['http://[bad'],[42,'http://x/'],['x',null]])equalResult('URL.canParse-'+String(value),()=>TestURL.canParse(value,base),()=>nodeUrl.URL.canParse(value,base));
 test('canParse-conversion-error-not-swallowed',()=>{const X={};assert.throws(()=>TestURL.canParse({toString(){throw X;}}),e=>e===X);assert.equal(err(()=>TestURL.canParse()).code,'ERR_MISSING_ARGS');assert.equal(err(()=>TestURL.canParse(Symbol())).name,'TypeError');});
 equalResult('URL-format-options',()=>url.format(new TestURL('https://u:p@x/a?q#h'),{auth:false,search:false,fragment:false}),()=>nodeUrl.format(new nodeUrl.URL('https://u:p@x/a?q#h'),{auth:false,search:false,fragment:false}));
 for(const[name,ns]of [['process',graph.process],['os',graph.os],['url',graph.url]]){
 const manifest=JSON.parse(await readFile(new URL(`./export-manifest.${name}.node-v22.14.0.json`,import.meta.url),'utf8'));
 for(const key of manifest.modules['node:'+name].unsupportedStatic)for(const construct of [false,true])test('unsupported-'+name+'.'+key+'-'+construct,()=>{let caught;try{construct?new ns[key]():ns[key]();}catch(e){caught=e;}assert.equal(caught?.code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(caught?.profile,'sm-node-22.14.0-m0.20');});}
 const header=await readFile(new URL('./next-startup-factory.generated.h',import.meta.url),'utf8');const source=header.split('R"SM_STARTUP(')[1].split(')SM_STARTUP";')[0];
 const f=new vm.Script(source,{filename:'<generated-startup-source>'}).runInThisContext();let calls=0;const noIO={...a,kernel:{...provider,initial(){calls++;throw Error('must not be called');}}};
 test('actual-generated-factory-no-IO',()=>{const g=f(noIO);assert.equal(calls,0);assert.equal(g.state().bootstrapped,false);for(const name of ['process','os','url'])assert.deepEqual(Object.keys(g[name]).sort(),inventory['node:'+name]);});
 deployed=false;test('deployed-guard-after-bootstrap',()=>{assert.equal(err(()=>p.cwd()).code,'ERR_SM_NODE_STARTUP_INITIALIZATION');assert.equal(err(()=>p.stdout.write('x')).code,'ERR_SM_NODE_STARTUP_INITIALIZATION');assert.equal(err(()=>p.nextTick(()=>{})).code,'ERR_SM_NODE_STARTUP_INITIALIZATION');});
 const result={schemaVersion:1,passed:true,checks,outcomes,node:process.version,realNodeDifferentials:true,testOnlyProvider:true,nativeKernelExecuted:false,applicationExecuted:false,targetEngineExecuted:false,guestExecuted:false,qualification:'Tests cover actual pure guest facade/factory using real Node URL/querystring and existing guest Events with explicit injected host test provider. They do not prove native provider, native FIFO runtime ordering, ABI, link or guest behavior.'};
 await writeFile(new URL('./host-tests.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:true,checks}));
}finally{await rm(owned,{recursive:true,force:true});}
