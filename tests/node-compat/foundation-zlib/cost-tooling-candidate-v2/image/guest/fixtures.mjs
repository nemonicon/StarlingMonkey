// SOURCE ONLY. No fixture or codec is evaluated at module initialization.
export const fixtureSpecs=Object.freeze([
 Object.freeze({id:'empty',bytes:0,pattern:'empty'}),
 Object.freeze({id:'small-repeat',bytes:64,pattern:'repeat-abc123'}),
 Object.freeze({id:'small-prng',bytes:64,pattern:'xorshift32-low-byte',seed:0x6d2b79f5}),
 Object.freeze({id:'large-repeat',bytes:524288,pattern:'repeat-abc123'}),
 Object.freeze({id:'large-prng',bytes:524288,pattern:'xorshift32-low-byte',seed:0x6d2b79f5})
]);
export function fixtureBytes(spec){
 const output=new Uint8Array(spec.bytes),repeat=[97,98,99,49,50,51];let state=spec.seed>>>0;
 for(let i=0;i<output.length;i++){
  if(spec.pattern==='repeat-abc123')output[i]=repeat[i%repeat.length];
  else if(spec.pattern==='xorshift32-low-byte'){state^=state<<13;state^=state>>>17;state^=state<<5;output[i]=state&255;}
  else throw new Error('Unknown nonempty fixture pattern');
 }
 return output;
}
export function consumeFNV1a(bytes){let hash=2166136261;for(let i=0;i<bytes.length;i++)hash=Math.imul(hash^bytes[i],16777619)>>>0;return hash;}
