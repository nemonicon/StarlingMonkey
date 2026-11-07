'use strict';
const assert = require('node:assert/strict');
const {createRequire} = require('node:module');
const {pathToFileURL} = require('node:url');
const path = require('node:path');

(async () => {
  assert.equal(process.version, 'v22.14.0');
  const fixtureRoot = process.argv[2];
  assert.equal(path.resolve(fixtureRoot), fixtureRoot);
  const driverPath = path.join(fixtureRoot, 'driver.cjs');
  const targetPath = path.join(fixtureRoot, 'target.cjs');
  const localRequire = createRequire(driverPath);
  const driver = localRequire(driverPath);
  const builtin = await driver.load('node:path');
  assert.equal(builtin.join, localRequire('node:path').join);
  assert.equal(builtin.join('/probe', 'child'), '/probe/child');
  const expected = localRequire(targetPath);
  const namespace = await driver.load(pathToFileURL(targetPath).href);
  const again = await driver.load(pathToFileURL(targetPath).href);
  assert.equal(namespace.default, expected);
  assert.equal(namespace, again);
  assert.equal(expected.marker, 'target-value');
  assert.equal(localRequire.cache[targetPath].loaded, true);
  assert.equal(localRequire.cache[targetPath].exports, expected);
  console.log(JSON.stringify({state: 'PINNED_NODE_NATURAL_CJS_FILEURL_REFERENCE_PASSED_V1',
    node: process.version, builtinJoinSame: true, naturalFileUrlImportSucceeded: true,
    defaultSameRequireExports: true, repeatedNamespaceSame: true, cacheLoaded: true,
    namespaceOwnNames: Object.getOwnPropertyNames(namespace),
    namespacePrototypeNull: Object.getPrototypeOf(namespace) === null,
    fixtureUrl: pathToFileURL(targetPath).href,
    hostCanonicalFileUrlUsedInsteadOfGuestProbePath: true,
    guardRefusalIsNodeParity: false, interopProfileFullParityClaimed: false}));
})().catch(error => { console.error(error); process.exitCode = 1; });
