// Bounded Node22 public stream/input reference only. No proposal factory/guest.
import assert from 'node:assert/strict';
import * as consumers from 'node:stream/consumers';
import {Buffer} from 'node:buffer';
import {Readable} from 'node:stream';
import {ReadableStream} from 'node:stream/web';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {extraCase,extraNames} from './extras.mjs';
const hash=raw=>createHash('sha256').update(raw).digest('hex');
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
assert.equal(hash(await readFile(process.execPath)),'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
const cases=[];for(let index=0;index<extraNames.length;index++)cases.push({name:extraNames[index],result:await extraCase(consumers,{Buffer,Readable,ReadableStream},index)});
const output=new URL('./extra-node-oracle.json',import.meta.url);
await writeFile(output,JSON.stringify({schemaVersion:1,node:process.version,nodeExecutableSha256:hash(await readFile(process.execPath)),sourceSha256:hash(await readFile(new URL('./extras.mjs',import.meta.url))),cases,publicNodeHostReferenceOnly:true,proposalFactoryOr355GuestExecuted:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({node:process.version,cases:cases.length,guestExecuted:false}));
