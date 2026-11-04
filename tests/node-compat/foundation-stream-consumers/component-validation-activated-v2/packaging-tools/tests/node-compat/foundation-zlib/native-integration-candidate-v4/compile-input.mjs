// Pure captured-command grammar. File authentication belongs to the producer /
// frozen-witness verifier; this function never treats arbitrary bytes as a pin.
import assert from 'node:assert/strict';
export const CODEC_HEADERS=Object.freeze([
 ['zlib.h','8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c',96829],
 ['zconf.h','61c756bba04523c333be09e33830ab617b11401d23583569bb94af2057418e14',16600],
 ['mozzconf.h','c16f8894b2d303dd5bae94c4ed9f76ecd4c942ab7346d5c66c1cc7074d3351d9',5855],
 ['js-confdefs.h','841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6',2283],
].map(row=>Object.freeze(row)));
export function validateSelectedCompileInput(value){
 assert.equal(value?.version,'sm-selected-moz-z-compile-input-v1');
 const root=value.selectedDistribution;assert.equal(typeof root,'string');
 assert(root.startsWith('/')&&!root.includes('\\')&&!root.includes('\0')&&root.split('/').slice(1).every(part=>part&&part!=='.'&&part!=='..'));
 assert.deepEqual(value.archive,{path:root+'/libspidermonkey.a',sha256:'298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc',bytes:538170426});
 const headers=CODEC_HEADERS.map(([name,sha256,bytes])=>({path:root+'/include/'+name,sha256,bytes}));
 assert.deepEqual(value.headers,headers);assert.deepEqual(value.requiredForcedInclude,headers[3]);
 return headers[3].path;
}
export function validateCompileForcedInclude(tokens,selection){
 const path=validateSelectedCompileInput(selection);
 assert.equal(tokens.filter(token=>token==='-include').length,1,'Exactly one selected SM forced include required');
 assert.equal(tokens[tokens.indexOf('-include')+1],path,'Forced include must use selected SM distribution');
 for(const token of tokens)if(token!=='-include')assert(!['-include','-imacros','-Wp,','-Xpreprocessor','-Xclang'].some(prefix=>token.startsWith(prefix)),'No extra/joined/PCH/imacros/pass-through includes');
 return path;
}
