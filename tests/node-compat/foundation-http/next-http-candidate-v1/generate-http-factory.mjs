import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read = name => readFileSync(new URL(name, import.meta.url), 'utf8');
const inputs = {bridge: read('bridge.mjs'), core: read('http-core.mjs'), inventory: read('inventory.node-v22.14.0.json'),
  publicManifest: read('export-manifest.http.node-v22.14.0.json'), privateManifest: read('private-http-export-manifest.v1.json')};
const inventory = JSON.parse(inputs.inventory);
if (inventory.inventoryVersion !== 'next-http-node-v22.14.0-v1') throw Error('Wrong HTTP inventory');
const manifest = JSON.parse(inputs.publicManifest), privateManifest = JSON.parse(inputs.privateManifest);
for (const [id, row] of Object.entries(inventory.modules))
  if (JSON.stringify(manifest.modules[id].exports) !== JSON.stringify(row.exports)) throw Error('HTTP export inventory mismatch');
if (privateManifest.specifier !== 'starling:node-http' || privateManifest.publicNodeManifest !== false ||
    privateManifest.exports.join() !== 'createServerHandler,runFreshRequest,runNeutralServer') throw Error('Private HTTP export mismatch');
let bridge = inputs.bridge;
for (const line of ["import {Readable, Writable} from 'node:stream';\n", "import {EventEmitter} from 'node:events';\n", "import {Buffer} from 'node:buffer';\n"]) {
  if (bridge.split(line).length !== 2) throw Error('Changed bridge import');
  bridge = bridge.replace(line, '');
}
bridge = bridge.replaceAll('export class ', 'class ').replace('export function createRequestBridge(', 'function createRequestBridge(');
for (const [old, replacement] of [
  ['  constructor(request) {\n    super({autoDestroy: true});', '  constructor(request) {\n    a.checkDeployed();\n    if (!(request instanceof Request)) throw failure("ERR_SM_NODE_UNSUPPORTED", "IncomingMessage requires this profile Web Request transport");\n    super({autoDestroy: true});'],
  ['  constructor(request, {highWaterMark = 64 * 1024} = {}) {\n    super({highWaterMark, autoDestroy: true});', '  constructor(request, {highWaterMark = 64 * 1024} = {}) {\n    a.checkDeployed();\n    if (!(request instanceof BridgeIncomingMessage)) throw failure("ERR_SM_NODE_UNSUPPORTED", "ServerResponse requires the paired profile IncomingMessage");\n    super({highWaterMark, autoDestroy: true});'],
]) {
  if (bridge.split(old).length !== 2) throw Error('Changed HTTP constructor guard anchor');
  bridge = bridge.replace(old, replacement);
}
const core = inputs.core.replace('export function createHttpFacade(', 'function createHttpFacade(');
if (/^\s*(?:import|export)\b/m.test(bridge + core)) throw Error('Unhandled module syntax');
const source = `(function(a){\nconst {Readable,Writable,EventEmitter,Buffer}=a;\n${bridge}\n${core}\na.inventory=${JSON.stringify(inventory)};\nreturn createHttpFacade(a,{BridgeIncomingMessage,BridgeServerResponse,createRequestBridge});\n})`;
if (source.includes(')SM_HTTP"')) throw Error('Raw string collision');
const hash = createHash('sha256').update(JSON.stringify(inputs)).digest('hex');
const header = `// Generated HTTP guest factory v1; all-input digest ${hash}\nstatic constexpr const char kNextHttpFactorySource[]=R"SM_HTTP(${source})SM_HTTP";\n`;
const target = new URL('next-http-factory.generated.h', import.meta.url);
if (process.argv.includes('--check')) { if (readFileSync(target, 'utf8') !== header) throw Error('Stale HTTP header'); }
else writeFileSync(target, header);
console.log(JSON.stringify({generated: true, sha256: hash, publicModules: Object.keys(inventory.modules)}));
