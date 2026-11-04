// Preserve the real DEBUG implementation while removing only DWARF custom
// sections that push the snapshotted engine past the packager's byte-list cap.
// Usage: node strip-debug.mjs RAW_ENGINE DERIVED_ENGINE WASM_TOOLS
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

assert.equal(process.version, 'v22.14.0');
assert.equal(process.argv.length, 5, 'Usage: node strip-debug.mjs RAW_ENGINE DERIVED_ENGINE WASM_TOOLS');
const [inputPath, outputPath, toolPath] = process.argv.slice(2).map(path => resolve(path));
assert.notEqual(inputPath, outputPath, 'Preserve the original debug artifact');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const input = await readFile(inputPath);
const metadataBytes = await readFile(inputPath + '.build.json');
const metadata = JSON.parse(metadataBytes);
assert.equal(metadata.engineSha256, hash(input));
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE, 'Debug');
assert.equal(metadata.oomTesting, true);
const toolVersion = spawnSync(toolPath, ['--version'], { encoding: 'utf8' });
assert.equal(toolVersion.status, 0, toolVersion.stderr);
assert.match(toolVersion.stdout, /^wasm-tools 1\.235\.0\b/);
const toolSha256 = hash(await readFile(toolPath));
// Pin the verified macOS arm64 artifact used by this gate. Other platforms
// require their own reviewed tool-artifact pin before extending this helper.
assert.equal(toolSha256, 'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d');

function sections(bytes) {
  assert.deepEqual([...bytes.subarray(0, 8)], [0, 97, 115, 109, 1, 0, 0, 0], 'Expected a core Wasm module');
  let position = 8;
  function uleb() {
    let result = 0, multiplier = 1;
    for (let i = 0; i < 5; i++) {
      assert(position < bytes.length, 'Truncated section LEB');
      const byte = bytes[position++];
      result += (byte & 127) * multiplier;
      if (!(byte & 128)) return result;
      multiplier *= 128;
    }
    assert.fail('Invalid section LEB');
  }
  const entries = [];
  while (position < bytes.length) {
    const id = bytes[position++], size = uleb(), start = position, end = start + size;
    assert(end <= bytes.length, 'Truncated section');
    let name;
    if (id === 0) {
      const length = uleb();
      assert(position + length <= end, 'Truncated custom name');
      name = bytes.toString('utf8', position, position + length);
    }
    const entry = { id, ...(name === undefined ? {} : { name }), bytes: size,
      payloadSha256: hash(bytes.subarray(start, end)) };
    // Retain bytes for a direct equality check; exclude them from JSON reports.
    Object.defineProperty(entry, 'payload', { value: bytes.subarray(start, end) });
    entries.push(entry);
    position = end;
  }
  return entries;
}
await mkdir(dirname(outputPath), { recursive: true });
const args = ['strip', '--delete', '^\\.debug_', inputPath, '-o', outputPath];
const result = spawnSync(toolPath, args, { encoding: 'utf8', timeout: 120000 });
assert.equal(result.status, 0, result.error?.message || result.stderr);
const derived = await readFile(outputPath);
const before = sections(input), after = sections(derived);
const removed = before.filter(section => section.id === 0 && section.name.startsWith('.debug_'));
assert(removed.length > 0, 'Expected actual DWARF sections');
const retained = before.filter(section => !removed.includes(section));
assert.deepEqual(after, retained,
  'Every standard section and retained custom payload must remain byte-identical');
after.forEach((section, index) => assert(section.payload.equals(retained[index].payload),
  'Section payload bytes changed: ' + (section.name ?? section.id)));
const derivation = { kind: 'strip-dwarf-custom-sections-only', derivedAtUtc: new Date().toISOString(),
  rawEnginePath: inputPath, rawEngineSha256: hash(input), rawEngineBytes: input.length,
  rawMetadataPath: inputPath + '.build.json', rawMetadataSha256: hash(metadataBytes),
  tool: { path: toolPath, version: toolVersion.stdout.trim(), sha256: toolSha256 },
  command: [toolPath, ...args], helperPath: fileURLToPath(import.meta.url),
  helperSha256: hash(await readFile(fileURLToPath(import.meta.url))),
  removedSections: removed, beforeSections: before, afterSections: after,
  standardSectionPayloadsIdentical: true, retainedCustomSectionPayloadsIdentical: true,
  codeAndDataUnchanged: true, debugImplementationPreserved: true,
  reason: 'Remove DWARF payload before snapshotting/packaging to keep returned byte lists within the generated splicer binding limits. DEBUG allocator code and OOM simulator remain unchanged.' };
const derivedMetadata = { ...metadata, enginePath: outputPath,
  engineSha256: hash(derived), engineBytes: derived.length, derivation };
await writeFile(outputPath + '.build.json', JSON.stringify(derivedMetadata, null, 2) + '\n');
console.log(JSON.stringify({ engine: outputPath, engineSha256: derivedMetadata.engineSha256,
  engineBytes: derived.length, removedSections: removed.map(section => section.name),
  standardSectionPayloadsIdentical: true, retainedCustomSectionPayloadsIdentical: true }, null, 2));
