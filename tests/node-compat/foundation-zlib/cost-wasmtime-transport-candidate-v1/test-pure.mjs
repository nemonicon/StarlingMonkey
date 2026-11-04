// Pure text/data only. This file imports no guest/provider/library/process API.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {waveString,invocation,parseScalarStringOutput,argvAccounting,WIRE_CODE_UNITS} from './scalar-transport.mjs';
const checks=[];function check(name,fn){fn();checks.push({name,passed:true});}
const parse=text=>parseScalarStringOutput({stdoutBytes:new TextEncoder().encode(text),rawDurablyRetained:true});
for(const s of['','ASCII','quote" slash\\ apostrophe\'','\n\r\t\0\b\f','\uFEFF\u2028\u007f','😀','literal \\u{feff}','{"schemaVersion":1,"kind":"primary","caseId":0}'])check('pure WAVE string roundtrip '+JSON.stringify(s),()=>assert.equal(parse(waveString(s)+'\n'),s));
check('WAVE argument escaping uses braces for NUL, not JSON u0000',()=>assert.equal(waveString('\0'),'"\\u{0}"'));
check('actual no-argument identity expression',()=>assert.equal(invocation('identity'),'identity()'));
check('actual setup numeric expression',()=>assert.equal(invocation('setup',[29]),'setup(29)'));
check('actual finite numeric pair',()=>assert.equal(invocation('batch',[0,1]),'batch(0, 1)'));
check('validate nested JSON is one WAVE string parameter',()=>assert.equal(invocation('validate',['{"a":1}']),'validate("{\\"a\\":1}")'));
for(const value of[null,1,{},new String('x')])check('no string argument coercion '+typeof value,()=>assert.throws(()=>waveString(value)));
for(const s of['\ud800','\udfff','x'.repeat(WIRE_CODE_UNITS+1)])check('reject invalid/overwire input '+s.length,()=>assert.throws(()=>waveString(s)));
for(const text of['0\n','{}\n','("a", "b")\n','"x"','"x"\n\n',' "x"\n','"a" extra\n','"a\nb"\n','"\\0"\n','"\\b"\n','"\\f"\n','"\\/"\n','"\\u0000"\n','"\\u{}"\n','"\\u{d800}"\n','"\\u{110000}"\n','"\\u{0000000}"\n','"\\q"\n'])check('reject malformed/nonstrict stdout '+JSON.stringify(text),()=>assert.throws(()=>parse(text)));
check('invalid UTF8 refuses',()=>assert.throws(()=>parseScalarStringOutput({stdoutBytes:new Uint8Array([34,0xed,0xa0,0x80,34,10]),rawDurablyRetained:true})));
check('unexpected leading UTF8 BOM is not silently stripped',()=>assert.throws(()=>parse('\uFEFF"x"\n')));
check('raw-retention prerequisite refuses false',()=>assert.throws(()=>parseScalarStringOutput({stdoutBytes:new TextEncoder().encode('"x"\n'),rawDurablyRetained:false})));
check('literal escaped Unicode text stays literal',()=>assert.equal(parse('"\\\\u{feff}"\n'),'\\u{feff}'));
check('pinned WAVE escaped apostrophe decoded exactly',()=>assert.equal(parse('"\\\'"\n'),"'"));
const account=argvAccounting({argv:['/wt','run','--invoke','identity()','/c.wasm'],environment:{PATH:'/bin'},argMax:1048576});
check('account final argv/env/pointer bytes exactly',()=>assert.equal(account.totalBytes,account.argumentBytes.reduce((a,b)=>a+b,0)+10+64));
check('no per-argument proof or runtime authority invented',()=>{assert.equal(account.allArgumentsBelowKnownLimit,null);assert.equal(account.runtimeFeasibilityProved,false);});
check('wire allowance can exceed aggregate OS budget',()=>assert.equal(argvAccounting({argv:['/wt','x'.repeat(1048576)],environment:{},argMax:1048576}).strictlyBelowArgMax,false));
for(const argv of[['x\0y'],[1]])check('reject invalid argv type/NUL',()=>assert.throws(()=>argvAccounting({argv,environment:{},argMax:1048576})));
check('known per-argument limit is independent',()=>assert.equal(argvAccounting({argv:['/wt','12345'],environment:{},argMax:1048576,perArgumentLimit:5}).allArgumentsBelowKnownLimit,false));
const path=process.env.COST_WT_TRANSPORT_PURE_RESULT;assert.equal(typeof path,'string');await writeFile(path,JSON.stringify({schemaVersion:1,passed:true,checks:checks.length,details:checks,componentGuestCodecWorkerOrExportActionsInvoked:false,sourceOnly:true},null,2)+'\n',{flag:'wx'});process.stdout.write(JSON.stringify({passed:true,checks:checks.length,exportCalls:0})+'\n');
