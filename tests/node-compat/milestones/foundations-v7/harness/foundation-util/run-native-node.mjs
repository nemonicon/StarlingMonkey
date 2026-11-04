import assert from 'node:assert/strict';
import * as util from 'node:util';
import * as types from 'node:util/types';
import * as sys from 'node:sys';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {runComponentCases} from './component-cases.mjs';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../..'),hash=data=>createHash('sha256').update(data).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const proof=JSON.parse(await readFile(join(here,'production-source-results.json'))),scope=JSON.parse(await readFile(join(here,'prototype-scope.json'))),sources={};
for(const input of proof.sourceFiles){const bytes=await readFile(join(repo,'builtins/node-compat',input.path));assert.equal(hash(bytes),input.sha256);sources[input.path]=input.sha256;}
const variants=[];for(const sharedArrayBuffer of [false,true]){const features={sharedArrayBuffer,transfer:true,resizable:true};variants.push(await runComponentCases({util,types,sys,predicateNames:scope.typesImplemented,features}));}
const report={schemaVersion:1,state:'pinned-node-supported-oracles-and-production-source-pins',node:process.version,executableSha256:hash(await readFile(process.execPath)),productionSourceProofSha256:hash(await readFile(join(here,'production-source-results.json'))),registrarSha256:hash(await readFile(join(repo,'builtins/node-compat/register.cpp'))),sources,checksSha256:hash(await readFile(join(here,'component-cases.mjs'))),scopeSha256:hash(await readFile(join(here,'prototype-scope.mjs'))),variants,expectedExports:{util:Object.keys(util).sort(),types:Object.keys(types).sort(),sys:Object.keys(sys).sort()},scope:'Actual public Node utilities for supported pure cases; no reference native-kernel delegation. SABfalse variant permits explicit target constructor absence; no target cross-realm proof.'};
await writeFile(join(here,'native-node-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,variants:variants.map(value=>({features:value.features,checks:value.checks}))}));
