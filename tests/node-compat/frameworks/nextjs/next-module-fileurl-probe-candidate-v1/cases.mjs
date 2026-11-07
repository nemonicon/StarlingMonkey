// Source-only declarations. Import, createRequire and fixture access are ordinary-call only.
export const probeModes = Object.freeze(['guard', 'interop']);
export const guardCaseIds = Object.freeze(['cjs-dynamic-builtin', 'guard-natural-fileurl-refusal']);
export const interopCaseIds = Object.freeze([
  'cjs-dynamic-builtin', 'default-require-cache-identity', 'same-namespace',
  'thenable-default-not-assimilated', 'class-default-construction',
  'undefined-default', 'nan-default', 'negative-zero-default', 'throw-null-preserved',
  'query-refusal', 'fragment-refusal', 'encoded-separator-refusal',
  'uppercase-scheme-refusal', 'extension-refusal', 'url-byte-limit-refusal',
  'decoded-path-limit-refusal',
]);

function probeOwnData(object, key) {
  if (object === null || (typeof object !== 'object' && typeof object !== 'function')) return undefined;
  const descriptor = Object.getOwnPropertyDescriptor(object, key);
  return descriptor && Object.hasOwn(descriptor, 'value') ? descriptor.value : undefined;
}

function failureData(value) {
  const data = {type: typeof value, isNull: value === null};
  if (value === null || typeof value === 'boolean' || typeof value === 'string') data.value = value;
  if (typeof value === 'number') data.value = Number.isFinite(value) ? value : String(value);
  for (const key of ['name', 'message', 'code', 'operation', 'module']) {
    const item = probeOwnData(value, key);
    if (item === undefined) data[key] = {type: 'undefined'};
    else if (item === null || ['boolean', 'string', 'number'].includes(typeof item))
      data[key] = {type: typeof item, value: typeof item === 'string' ? item.slice(0, 512) : item};
    else data[key] = {type: typeof item};
  }
  return data;
}

function check(value, message) {
  if (value !== true) throw new Error('Module file-URL probe assertion: ' + message);
}

async function rejection(action) {
  try { return {rejected: false, value: await action()}; }
  catch (value) { return {rejected: true, value}; }
}

function refusalObservation(result, code, operation, specifier) {
  check(result.rejected === true, 'expected an actual rejected import');
  const error = result.value;
  const observation = {
    rejected: true,
    isTypeError: error instanceof TypeError,
    code: probeOwnData(error, 'code'), operation: probeOwnData(error, 'operation'),
    moduleMatchesActualSpecifier: probeOwnData(error, 'module') === specifier,
    error: failureData(error),
  };
  check(observation.isTypeError && observation.code === code && observation.operation === operation &&
    observation.moduleMatchesActualSpecifier, 'exact native refusal fields');
  return observation;
}

function namespaceObservation(namespace, expected) {
  const names = Object.getOwnPropertyNames(namespace);
  const observation = {
    prototypeNull: Object.getPrototypeOf(namespace) === null,
    ownNames: names,
    noOwnThen: !Object.hasOwn(namespace, 'then'),
    defaultSame: Object.is(namespace.default, expected),
  };
  check(observation.prototypeNull && names.length === 1 && names[0] === 'default' &&
    observation.noOwnThen && observation.defaultSame, 'single-default genuine namespace and exact value');
  return observation;
}

export async function collectFileUrlProbe(mode) {
  if (!probeModes.includes(mode)) throw new TypeError('Unknown predeclared probe mode');
  const expectedIds = mode === 'guard' ? guardCaseIds : interopCaseIds;
  const records = [];
  const run = async (id, body) => {
    try { records.push({id, passed: true, observation: await body()}); }
    catch (error) { records.push({id, passed: false, error: failureData(error)}); }
  };
  // This function is invoked by the deployed GET handler, never during INIT.
  // The driver is loaded by the installed CJS loader. Its unmodified function
  // contains the natural import() expression; no eval or private metadata API.
  const {createRequire} = await import('node:module');
  const require = createRequire('/probe/driver.cjs');
  const driver = require('/probe/driver.cjs');
  check(typeof driver.load === 'function', 'real CJS driver');
  const targetUrl = 'file:///probe/target.cjs';
  await run('cjs-dynamic-builtin', async () => {
    const namespace = await driver.load('node:path');
    const builtin = require('node:path');
    const sameJoin = namespace.join === builtin.join;
    const joined = namespace.join('/probe', 'child');
    check(sameJoin && joined === '/probe/child', 'CJS import(node:path) remains usable');
    return {sameJoin, joined};
  });
  if (mode === 'guard') {
    await run('guard-natural-fileurl-refusal', async () => refusalObservation(
      await rejection(() => driver.load(targetUrl)),
      'ERR_SM_MODULE_IMPORT_REFERRER', 'module_load_hook', targetUrl));
  } else {
    let firstNamespace;
    await run('default-require-cache-identity', async () => {
      const value = require('/probe/target.cjs');
      firstNamespace = await driver.load(targetUrl);
      const observed = namespaceObservation(firstNamespace, value);
      const filename = require.resolve('/probe/target.cjs');
      const cache = probeOwnData(require.cache, filename);
      const loaded = probeOwnData(cache, 'loaded') === true;
      const cacheSame = probeOwnData(cache, 'exports') === value;
      check(filename === '/probe/target.cjs' && loaded && cacheSame && value.marker === 'target-value',
        'completed real require cache and value identity');
      return {...observed, filename, loaded, cacheSame, marker: value.marker};
    });
    await run('same-namespace', async () => {
      const again = await driver.load(targetUrl);
      const same = firstNamespace !== undefined && again === firstNamespace;
      check(same, 'successful repeated canonical import namespace identity');
      return {same};
    });
    await run('thenable-default-not-assimilated', async () => {
      const value = require('/probe/thenable.cjs');
      const namespace = await driver.load('file:///probe/thenable.cjs');
      const observed = namespaceObservation(namespace, value);
      const thenReads = value.inspectThenReads();
      check(thenReads === 0, 'default export then getter was not read');
      return {...observed, thenReads};
    });
    await run('class-default-construction', async () => {
      const Constructor = require('/probe/class.cjs');
      const namespace = await driver.load('file:///probe/class.cjs');
      const observed = namespaceObservation(namespace, Constructor);
      const instance = new namespace.default(7);
      const prototypeSame = Object.getPrototypeOf(instance) === Constructor.prototype;
      const result = instance.describe();
      check(prototypeSame && result === 'class:7', 'genuine class default can construct');
      return {...observed, prototypeSame, result};
    });
    for (const [id, name, predicate] of [
      ['undefined-default', 'undefined', value => value === undefined],
      ['nan-default', 'nan', value => Number.isNaN(value)],
      ['negative-zero-default', 'negative-zero', value => Object.is(value, -0)],
    ]) {
      await run(id, async () => {
        const path = '/probe/' + name + '.cjs';
        const value = require(path), namespace = await driver.load('file://' + path);
        const observed = namespaceObservation(namespace, value);
        const expectedPrimitive = predicate(namespace.default);
        check(expectedPrimitive, 'selected primitive default survives');
        return {...observed, expectedPrimitive};
      });
    }
    await run('throw-null-preserved', async () => {
      const path = '/probe/throw-null.cjs';
      const result = await rejection(() => driver.load('file://' + path));
      const rejectedNull = result.rejected && result.value === null;
      const noCompletedCacheEntry = !Object.hasOwn(require.cache, path);
      check(rejectedNull && noCompletedCacheEntry, 'original falsy throw and original CJS failed-load cleanup');
      return {rejectedNull, noCompletedCacheEntry, error: failureData(result.value)};
    });
    for (const [id, url] of [
      ['query-refusal', targetUrl + '?probe=1'],
      ['fragment-refusal', targetUrl + '#probe'],
      ['encoded-separator-refusal', 'file:///probe%2ftarget.cjs'],
      ['uppercase-scheme-refusal', 'FILE:///probe/target.cjs'],
      ['extension-refusal', 'file:///probe/target.js'],
      ['url-byte-limit-refusal', 'file:///probe/' + 'x'.repeat(12297) + '.cjs'],
      ['decoded-path-limit-refusal', 'file:///probe/' + 'x'.repeat(4096) + '.cjs'],
    ]) {
      await run(id, async () => refusalObservation(await rejection(() => driver.load(url)),
        'ERR_SM_MODULE_FILE_URL_UNSUPPORTED', 'module_file_url', url));
    }
  }
  const exactCaseIds = records.length === expectedIds.length &&
    records.every((record, index) => record.id === expectedIds[index]);
  return {
    schemaVersion: 1, suite: 'REAL_COMPONENT_CJS_FILE_URL_PROBE_V1', mode,
    caseCount: records.length, expectedCaseCount: expectedIds.length, records,
    exactCaseIds, profilePassed: exactCaseIds && records.every(record => record.passed === true),
    guardRefusalIsNodeCompatibilityPass: false,
    nodeReferenceExecuted: false, applicationImported: false,
    fullNextClaim: false, namespaceLimit8192Exercised: false,
    symlinkReentrancyRealmOrRaceParityProved: false,
  };
}
