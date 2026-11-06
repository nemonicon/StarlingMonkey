// Synthetic transport DATA only. Does not import companion or run any process.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const refs=JSON.parse(await readFile(new URL('./references.json',import.meta.url)));
const bytes=await readFile(refs.wave.path);assert(bytes.length===refs.wave.bytes&&createHash('sha256').update(bytes).digest('hex')===refs.wave.sha256);
const {parseScalarStringOutput}=await import(pathToFileURL(refs.wave.path));let cases=0;
for(const [raw,value]of [['"whole"\n','whole'],['"a\\n\\\"b"\n','a\n"b'],['"\\u{1f680}"\n','🚀']]){assert.equal(parseScalarStringOutput({stdoutBytes:Buffer.from(raw),rawDurablyRetained:true}),value);cases++;}
for(const raw of ['"x"','"x"\n\n','"x"\ntrailer','0\n','{"x":1}\n','"\\uD800"\n','"\\u{d800}"\n','"\\x41"\n','"raw\ncontrol"\n']){assert.throws(()=>parseScalarStringOutput({stdoutBytes:Buffer.from(raw),rawDurablyRetained:true}));cases++;}
assert.throws(()=>parseScalarStringOutput({stdoutBytes:Buffer.from('"x"\n'),rawDurablyRetained:false}));cases++;
console.log(JSON.stringify({schemaVersion:1,syntheticWaveCases:cases,wholeTypedTransportOnly:true,companionOrWasmtimeOrGuestExecuted:false}));
