import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read = n => readFileSync(new URL(n, import.meta.url), 'utf8');
const code = read('imports-core.mjs'), data = read('inventory.node-v22.14.0.json');
const manifestSource = read('export-manifest.next-imports.node-v22.14.0.json'), manifest = JSON.parse(manifestSource);
const inventory = JSON.parse(data);
if (inventory.inventoryVersion !== 'next-imports-node-v22.14.0-v1') throw Error('Unexpected import inventory');
for (const [id, rows] of Object.entries(inventory.modules))
  if (JSON.stringify(manifest.modules[id].exports) !== JSON.stringify([...Object.keys(rows), 'default'].sort())) throw Error('Import export inventory mismatch');
const body = code.replace('export function createNextImportFacades(', 'function createNextImportFacades(');
if (/^\s*(?:import|export)\b/m.test(body)) throw Error('Unsupported import factory syntax');
const source = `(function(){\n${body}\nreturn createNextImportFacades(${JSON.stringify(inventory)});\n})`;
if (source.includes(')SM_IMPORTS"')) throw Error('Raw delimiter collision');
const digest = createHash('sha256').update(code + '\0' + data + '\0' + manifestSource).digest('hex');
const header = `// Explicit guest export factory; input digest ${digest}\nstatic constexpr const char kNextImportsFactorySource[]=R"SM_IMPORTS(${source})SM_IMPORTS";\n`;
const path = new URL('next-imports-factory.generated.h', import.meta.url);
if (process.argv.includes('--check')) { if (readFileSync(path, 'utf8') !== header) throw Error('Stale imports factory'); }
else writeFileSync(path, header);
console.log(JSON.stringify({generated: true, inputSha256: digest, modules: Object.keys(inventory.modules)}));
