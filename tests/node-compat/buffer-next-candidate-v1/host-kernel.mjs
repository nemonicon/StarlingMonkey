// TEST ONLY: real host Node byte primitives, never a guest/native proof.
import {Buffer as B,isAscii,isUtf8} from 'node:buffer';
const view=v=>B.from(v.buffer,v.byteOffset,v.byteLength);
export const hostKernel={
 hexDecode:s=>new Uint8Array(B.from(s,'hex')),hexEncode:b=>view(b).toString('hex'),
 decode:(s,m)=>new Uint8Array(B.from(s,['base64','latin1','utf16le'][m])),
 encode:(v,m)=>view(v).toString(['base64','base64url','latin1','ascii','utf16le'][m]),
 concat:(v,n)=>new Uint8Array(B.concat(v.map(view),n)),
 copy:(s,t,so,to,n)=>view(s).copy(view(t),to,so,so+n),
 compare:(a,b)=>B.compare(view(a),view(b)),search:(h,n,o)=>view(h).indexOf(view(n),o),
 validate:(v,ascii)=>(ascii?isAscii:isUtf8)(v),
 fill:(t,p,s,e)=>{view(t).fill(view(p),s,e);return t;},
};
