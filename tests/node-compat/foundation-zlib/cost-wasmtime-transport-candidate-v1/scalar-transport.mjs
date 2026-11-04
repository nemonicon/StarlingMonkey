// Pure bounded SOURCE proposal. No process, component, guest or codec is loaded.
const need=(v,m)=>{if(!v)throw new Error('ERR_STOCK_WT_TRANSPORT: '+m);};
export const WIRE_CODE_UNITS=2097152;
function scalar(cp){return cp<=0x10ffff&&!(cp>=0xd800&&cp<=0xdfff);}
export function waveString(value){
 need(typeof value==='string'&&value.length<=WIRE_CODE_UNITS,'Complete bounded string, no coercion/clipping');
 let result='"';
 for(const ch of value){const cp=ch.codePointAt(0);need(scalar(cp),'WIT UTF8 requires Unicode scalar values');
  if(ch==='"'||ch==='\\')result+='\\'+ch;
  else if(ch==='\n')result+='\\n';else if(ch==='\r')result+='\\r';else if(ch==='\t')result+='\\t';
  else if(cp<0x20||cp>=0x7f)result+='\\u{'+cp.toString(16)+'}';else result+=ch;
 }return result+'"';
}
export function invocation(name,args=[]){
 need(['identity','setup','observe','batch','checkpoint','stage','validate'].includes(name)&&Array.isArray(args),'Finite actual seven-function ABI');
 const count={identity:0,setup:1,observe:1,batch:2,checkpoint:0,stage:1,validate:1};need(args.length===count[name],'Exact signature arity');
 if(name==='stage'||name==='validate')return name+'('+waveString(args[0])+')';
 for(const n of args)need(Number.isInteger(n)&&!Object.is(n,-0)&&n>=0&&n<=4294967295,'Exact u32 argument');
 if(name==='setup'||name==='observe'||name==='batch')need(args[0]<30,'This untimed probe template uses only primary IDs');
 if(name==='batch')need(args[1]===1,'No timing/calibration request in this template');
 return name+'('+args.join(', ')+')';
}
export function parseScalarStringOutput({stdoutBytes,rawDurablyRetained}){
 need(rawDurablyRetained===true,'Persist complete raw stdout BEFORE parser/assertions');
 need(stdoutBytes instanceof Uint8Array&&stdoutBytes.byteLength<=16*1024*1024,'Bounded complete raw capture; never truncate');
 const raw=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(stdoutBytes);
 need(raw.endsWith('\n')&&!raw.endsWith('\n\n'),'Exactly one pinned-macOS println LF');
 const text=raw.slice(0,-1);need(text.length>=2&&text[0]==='"'&&text.at(-1)==='"','One typed WAVE string result, not number/tuple/JSON object');
 let result='';
 for(let at=1;at<text.length-1;at++){
  const ch=text[at];
  if(ch==='\\'){
   const escape=text[++at];need(at<text.length-1,'Complete escape');
   if(escape==='u'){
    need(text[++at]==='{','WAVE unicode uses braces, not JSON uXXXX');const end=text.indexOf('}',at+1),digits=text.slice(at+1,end);
    need(end>at&&end<text.length-1&&/^[0-9a-fA-F]{1,6}$/.test(digits),'One through six hex digits');
    const cp=Number.parseInt(digits,16);need(scalar(cp),'Valid Unicode scalar escape');result+=String.fromCodePoint(cp);at=end;
   }else{const escapes={'\\':'\\','"':'"',"'":"'",t:'\t',n:'\n',r:'\r'};need(Object.hasOwn(escapes,escape),'Only pinned WAVE escapes');result+=escapes[escape];}
  }else{
   const cp=text.codePointAt(at);need(ch!=='"'&&scalar(cp)&&!(cp<=0x1f||cp>=0x7f&&cp<=0x9f),'No raw control, extra quote or malformed scalar');
   result+=String.fromCodePoint(cp);if(cp>0xffff)at++;
  }
 }
 need(result.length<=WIRE_CODE_UNITS,'Complete decoded guest string exceeds wire cap');return result;
}
export function argvAccounting({argv,environment,argMax,perArgumentLimit=null}){
 need(Array.isArray(argv)&&argv.length>0&&argv.every(s=>typeof s==='string'&&!s.includes('\0')),'Exact final argv strings, no shell');
 need(environment&&Object.getPrototypeOf(environment)===Object.prototype,'Explicit final child environment, not ambient inference');
 need(Object.entries(environment).every(([k,v])=>k&&!k.includes('=')&&!k.includes('\0')&&typeof v==='string'&&!v.includes('\0')),'Exact environment entries');
 need(Number.isSafeInteger(argMax)&&argMax>0,'Observed host ARG_MAX');
 if(perArgumentLimit!==null)need(Number.isSafeInteger(perArgumentLimit)&&perArgumentLimit>0,'Explicit independently justified per-argument bound');
 const argumentBytes=argv.map(s=>new TextEncoder().encode(s).length+1);
 const environmentBytes=Object.entries(environment).reduce((n,[k,v])=>n+new TextEncoder().encode(k+'='+v).length+1,0);
 const pointerBytes=8*(argv.length+Object.keys(environment).length+2),totalBytes=argumentBytes.reduce((a,b)=>a+b,0)+environmentBytes+pointerBytes;
 return{argumentBytes,environmentBytes,pointerBytes,totalBytes,argMax,strictlyBelowArgMax:totalBytes<argMax,perArgumentLimit,allArgumentsBelowKnownLimit:perArgumentLimit===null?null:argumentBytes.every(n=>n<perArgumentLimit),kernelPaddingAndPerArgumentSemanticsNotProved:true,runtimeFeasibilityProved:false};
}
