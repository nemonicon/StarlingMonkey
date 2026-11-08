'use strict';

// New sequential application contract, not a replacement interpretation of the
// old module-global counter. Importing this module performs no filesystem IO.
const { lstatSync, realpathSync, mkdirSync, readdirSync,
  readFileSync, writeFileSync, renameSync } = require('node:fs');
const MODULE = 'next-fs-callback-generation-v1';
const NAMESPACE = 'app-callback-generation-v1';
const MAX_BYTES = 128;
const MAX_GENERATION = 1000000;

function failure(code, operation, message, cause) {
  const error = new Error(message);
  error.code = code; error.operation = operation; error.module = MODULE;
  if (arguments.length === 4) error.cause = cause;
  return error;
}
function need(ok, code, operation, message) {
  if (!ok) throw failure(code, operation, message);
}
function directory(name) {
  const stat = lstatSync(name);
  need(stat.isDirectory() && !stat.isSymbolicLink() && realpathSync(name) === name,
    'ERR_SM_CALLBACK_PROFILE', 'directory', 'Expected canonical owned directory');
}
function record(name, missingAllowed) {
  let before;
  try { before = lstatSync(name); }
  catch (error) {
    if (missingAllowed && error && error.code === 'ENOENT') return null;
    throw error;
  }
  need(before.isFile() && !before.isSymbolicLink() && before.nlink === 1 &&
    Number.isSafeInteger(before.size) && before.size > 0 && before.size <= MAX_BYTES &&
    realpathSync(name) === name,
  'ERR_SM_CALLBACK_CORRUPT', 'read', 'Unexpected record type, alias or size');
  const bytes = readFileSync(name);
  const after = lstatSync(name);
  need(bytes.length <= MAX_BYTES && bytes.length === before.size &&
    after.isFile() && !after.isSymbolicLink() && after.nlink === 1 &&
    after.size === bytes.length && realpathSync(name) === name,
  'ERR_SM_CALLBACK_CORRUPT', 'read', 'Record changed or exceeded its bound');
  const text = bytes.toString('utf8');
  const match = /^\{"schemaVersion":1,"generation":([1-9][0-9]*)\}\n$/.exec(text);
  need(match && match[0] === text, 'ERR_SM_CALLBACK_CORRUPT', 'decode',
    'Expected canonical versioned integer record');
  const generation = Number(match[1]);
  need(Number.isSafeInteger(generation) && generation >= 1 && generation <= MAX_GENERATION,
    'ERR_SM_CALLBACK_LIMIT', 'decode', 'Generation is outside the selected bound');
  return generation;
}

function nextCallbackGeneration() {
  // Resolve the actual runtime cwd only when Next invokes the cached callback.
  // The parent cache mount is externally owned; never create its ancestors.
  try {
    const cwd = process.cwd();
    need(typeof cwd === 'string' && cwd.startsWith('/') && !cwd.includes('\0'),
      'ERR_SM_CALLBACK_PROFILE', 'cwd', 'Expected absolute runtime cwd');
    directory(cwd);
    const cache = (cwd === '/' ? '' : cwd) + '/.next/cache';
    directory(cache);
    const root = cache + '/' + NAMESPACE;
    try { mkdirSync(root); }
    catch (error) { if (!error || error.code !== 'EEXIST') throw error; }
    directory(root);
    const names = readdirSync(root);
    need(names.length <= 2, 'ERR_SM_CALLBACK_LIMIT', 'layout', 'Namespace member bound exceeded');
    need(!names.includes('generation.pending'), 'ERR_SM_CALLBACK_BUSY', 'layout',
      'Pending publication exists; no retry or online reclamation');
    need(names.every((name) => name === 'generation.json'),
      'ERR_SM_CALLBACK_CORRUPT', 'layout', 'Unexpected namespace member');
    const committed = root + '/generation.json';
    const pending = root + '/generation.pending';
    // Only genuine ENOENT, when no committed name was listed, is initial zero.
    const previous = record(committed, !names.includes('generation.json'));
    const generation = previous === null ? 1 : previous + 1;
    need(generation <= MAX_GENERATION, 'ERR_SM_CALLBACK_LIMIT', 'advance',
      'Generation limit reached; never wrap or reset');
    const text = '{"schemaVersion":1,"generation":' + generation + '}\n';
    need(text.length <= MAX_BYTES, 'ERR_SM_CALLBACK_LIMIT', 'encode', 'Record bound exceeded');
    try { writeFileSync(pending, text, { flag: 'wx' }); }
    catch (error) {
      throw failure(error && error.code === 'EEXIST' ? 'ERR_SM_CALLBACK_BUSY' : 'ERR_SM_CALLBACK_IO',
        'write', 'Exclusive pending write failed; no retry or reclamation', error);
    }
    need(record(pending, false) === generation, 'ERR_SM_CALLBACK_CORRUPT', 'verify.pending',
      'Pending bytes do not match the proposed generation');
    renameSync(pending, committed);
    // A successful rename consumes pending. Any later failure still throws;
    // it does not roll back, recreate pending, reset state or count as success.
    need(record(committed, false) === generation, 'ERR_SM_CALLBACK_CORRUPT', 'verify.committed',
      'Committed bytes do not match the proposed generation');
    directory(cache); directory(root);
    const finalNames = readdirSync(root);
    need(finalNames.length === 1 && finalNames[0] === 'generation.json',
      'ERR_SM_CALLBACK_CORRUPT', 'verify.layout', 'Unexpected final namespace members');
    // Sequential cooperative writers only. No CAS, process exclusion, fsync,
    // power-loss durability or hostile path-replacement guarantee is claimed.
    return generation;
  } catch (error) {
    if (error && error.module === MODULE) throw error;
    throw failure('ERR_SM_CALLBACK_IO', 'advance',
      'Filesystem operation failed; publication may be uncertain, no retry or rollback', error);
  }
}

module.exports = { nextCallbackGeneration };
