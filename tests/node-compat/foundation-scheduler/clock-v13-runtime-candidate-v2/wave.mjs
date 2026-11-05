// Exact bounded WAVE parser derivation; no process or guest at import.
const need=(v,m)=>{if(!v)throw new Error(m);};
const WIRE_CODE_UNITS=2097152;
const scalar=cp=>cp<=0x10ffff&&!(cp>=0xd800&&cp<=0xdfff);
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
