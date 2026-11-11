import { AsyncLocalStorage } from 'node:async_hooks';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { runWebStreamContextCases, describeThrown } from './cases.mjs';

// Root owns execution. This CLI creates one new directory; it never removes anything.
if (process.argv.length !== 3) throw new Error('usage: node run-node.mjs ABSOLUTE_FRESH_OUTPUT_DIRECTORY');
if (process.version !== 'v22.14.0' || process.execArgv.length !== 0 || Object.hasOwn(process.env, 'NODE_OPTIONS')) {
  throw new Error('requires exact Node v22.14.0, empty execArgv and absent NODE_OPTIONS');
}
const output = process.argv[2];
if (!path.isAbsolute(output) || path.resolve(output) !== output || path.basename(output) === '') {
  throw new Error('output must be a canonical absolute fresh directory');
}
if (fs.realpathSync(path.dirname(output)) !== path.dirname(output)) throw new Error('output parent must be canonical');
fs.mkdirSync(output, { mode: 0o700 });
const report = { executionKind: 'node-reference', nodeVersion: process.version,
  execArgv: [...process.execArgv], nodeOptionsPresent: false, guestExecuted: false };
let primarySet = false, primary;
try { await runWebStreamContextCases({ AsyncLocalStorage, runFresh: callback => callback(), boundaryMode: 'public-only', report }); }
catch (error) { primarySet = true; primary = error; report.unexpectedRejection = describeThrown(error); report.passed = false; }
let publication;
try {
  const bytes = Buffer.from(`${JSON.stringify(report, null, 2)}\n`);
  if (bytes.length > 128 * 1024) throw new Error('result exceeds 128 KiB');
  const file = path.join(output, 'result.json');
  const descriptor = fs.openSync(file, 'wx', 0o600);
  let writePrimarySet = false, writePrimary;
  try { fs.writeFileSync(descriptor, bytes); fs.fsyncSync(descriptor); }
  catch (error) { writePrimarySet = true; writePrimary = error; }
  finally {
    try { fs.closeSync(descriptor); }
    catch (error) { if (!writePrimarySet) { writePrimarySet = true; writePrimary = error; } }
  }
  if (writePrimarySet) throw writePrimary;
  const saved = fs.readFileSync(file);
  if (!saved.equals(bytes)) throw new Error('result readback mismatch');
  publication = { path: file, bytes: bytes.length, sha256: crypto.createHash('sha256').update(bytes).digest('hex') };
  fs.writeSync(1, `${JSON.stringify({ state: 'NODE_WEB_STREAM_CONTEXT_OBSERVATIONS_SAVED_V1', result: publication,
    passed: report.passed === true, webStreamContextComparisonPerformed: false })}\n`);
} catch (error) {
  if (!primarySet) { primarySet = true; primary = error; }
  else { try { fs.writeSync(2, `${JSON.stringify({ secondaryPublicationError: describeThrown(error) })}\n`); } catch {} }
}
if (primarySet) throw primary;
if (report.passed !== true) process.exitCode = 1;
