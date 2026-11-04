// Exact-release edge oracle for the experimental token/resource model.
import assert from 'node:assert/strict';
import {
  AsyncLocalStorage, AsyncResource, createHook, executionAsyncId,
} from 'node:async_hooks';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

assert.equal(process.version, 'v22.14.0');
assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS, 'Measure the pinned release default configuration');
const ROOT = '<undefined>';
const here = dirname(fileURLToPath(import.meta.url));
const cases = [];
const ids = new WeakMap();
const initEvents = [];
let active;
const value = storage => storage.getStore() ?? ROOT;
const gate = () => {
  let resolve, reject;
  const promise = new Promise((done, fail) => { resolve = done; reject = fail; });
  return { promise, resolve, reject };
};
const hooks = createHook({
  init(asyncId, type, triggerAsyncId, resource) {
    ids.set(resource, asyncId);
    if (active && (type === 'PROMISE' || type.startsWith('edge-'))) {
      initEvents.push({ case: active.name, asyncId, type, triggerAsyncId,
        currentExecutionAsyncId: executionAsyncId(), store: value(active.a),
        ...(active.b ? { secondStore: value(active.b) } : {}) });
    }
  },
});
hooks.enable();

async function test(name, body, second = false) {
  const a = new AsyncLocalStorage(), b = second ? new AsyncLocalStorage() : null;
  const observations = [];
  active = { name, a, b };
  const mark = (label, extra = {}) => {
    const row = { label, store: value(a), ...(b ? { secondStore: value(b) } : {}),
      executionAsyncId: executionAsyncId(), ...extra };
    observations.push(row);
    return row;
  };
  try {
    const details = await body(a, mark, b);
    const relevant = new Set(details?.relevantAsyncIds ?? []);
    cases.push({ name, passed: true, observations, details,
      relevantInitEvents: initEvents.filter(event => event.case === name && relevant.has(event.asyncId)) });
  } finally {
    a.disable(); b?.disable(); active = null;
  }
}

for (const settled of [false, true]) {
  await test(`real Promise species result controls callback resource (${settled ? 'settled' : 'pending'})`, async (als, mark) => {
    const source = als.run('SOURCE', gate);
    if (settled) source.resolve(3);
    let createdResult;
    source.promise.constructor = {
      get [Symbol.species]() {
        assert.equal(mark('species-getter').store, 'REGISTER');
        return function Species(executor) {
          assert.equal(mark('species-constructor-before').store, 'REGISTER');
          const result = als.run('SPECIES', () => new Promise(executor));
          createdResult = result;
          assert.equal(mark('species-constructor-after', { resultAsyncId: ids.get(result) }).store, 'REGISTER');
          return result;
        };
      },
    };
    const result = als.run('REGISTER', () => source.promise.then(input => {
      assert.equal(input, 3);
      const row = mark('reaction');
      assert.equal(row.store, 'SPECIES');
      assert.equal(row.executionAsyncId, ids.get(createdResult));
      return 7;
    }));
    assert.equal(result, createdResult);
    if (!settled) als.run('RESOLVER', () => source.resolve(3));
    assert.equal(await result, 7);
    assert.equal(mark('after-await').store, ROOT);
    return { sourceAsyncId: ids.get(source.promise), resultAsyncId: ids.get(result),
      relevantAsyncIds: [ids.get(source.promise), ids.get(result)],
      verified: 'The callback executes on the real result Promise resource created inside the species constructor, under SPECIES rather than REGISTER.' };
  });
}

for (const settled of [false, true]) {
  await test(`plain-object species has no result Promise callback resource (${settled ? 'settled' : 'pending'})`, async (als, mark) => {
    const source = als.run('SOURCE', gate), completed = gate();
    if (settled) source.resolve(3);
    const plain = {};
    source.promise.constructor = {
      get [Symbol.species]() {
        assert.equal(mark('species-getter').store, 'REGISTER');
        return function PlainSpecies(executor) {
          als.run('SPECIES', () => {
            assert.equal(mark('species-constructor').store, 'SPECIES');
            executor(result => {
              assert.equal(result, 7);
              assert.equal(mark('capability-resolve').store, ROOT);
              completed.resolve();
            }, completed.reject);
          });
          return plain;
        };
      },
    };
    const result = als.run('REGISTER', () => source.promise.then(input => {
      assert.equal(input, 3);
      const row = mark('reaction');
      assert.equal(row.store, ROOT);
      assert.equal(row.executionAsyncId, 0);
      return 7;
    }));
    assert.equal(result, plain);
    assert.equal(ids.has(result), false, 'Plain species result has no async init resource ID');
    if (!settled) als.run('RESOLVER', () => source.resolve(3));
    await completed.promise;
    assert.equal(mark('after-await').store, ROOT);
    return { sourceAsyncId: ids.get(source.promise), resultHasAsyncId: ids.has(result),
      relevantAsyncIds: [ids.get(source.promise)],
      verified: 'The callback and capability resolver run on shared root resource ID0, without REGISTER or SPECIES, because the result capability is not a Promise.' };
  });
}

await test('run restores only its own ALS instance entry', async (a, mark, b) => {
  a.run('A', () => {
    b.enterWith('B');
    const row = mark('inside');
    assert.deepEqual([row.store, row.secondStore], ['A', 'B']);
  });
  let row = mark('after-a-run');
  assert.deepEqual([row.store, row.secondStore], [ROOT, 'B']);
  await new Promise(done => queueMicrotask(() => {
    row = mark('captured-child');
    assert.deepEqual([row.store, row.secondStore], [ROOT, 'B']);
    done();
  }));
  return { verified: 'Restoring the entire prior context map would incorrectly discard the other instance’s enterWith mutation.' };
}, true);

await test('nested thenable jobs share one mutable Promise resource; earlier child keeps snapshot', async (als, mark) => {
  const source = als.run('CREATION-A', gate), childDone = gate();
  let firstAsyncId;
  const observed = als.run('AWAIT-D', async () => {
    assert.equal(await source.promise, 9);
    assert.equal(mark('await-continuation').store, 'AWAIT-D');
  });
  als.run('RESOLVER-B', () => source.resolve({
    then(resolveFirst) {
      const first = mark('first-thenable');
      assert.equal(first.store, 'CREATION-A');
      firstAsyncId = first.executionAsyncId;
      assert.equal(firstAsyncId, ids.get(source.promise));
      queueMicrotask(() => {
        assert.equal(mark('child-captured-before-mutation').store, 'CREATION-A');
        childDone.resolve();
      });
      als.enterWith('MUTATED-X');
      assert.equal(mark('first-after-enterWith').store, 'MUTATED-X');
      resolveFirst({ then(resolveSecond) {
        const second = mark('second-thenable');
        assert.equal(second.store, 'MUTATED-X');
        assert.equal(second.executionAsyncId, firstAsyncId);
        resolveSecond(9);
      } });
    },
  }));
  await Promise.all([observed, childDone.promise]);
  assert.equal(mark('outer-after').store, ROOT);
  return { promiseAsyncId: ids.get(source.promise), relevantAsyncIds: [ids.get(source.promise)],
    verified: 'The same target Promise resource retains enterWith changes across assimilation jobs, while an independently created child retains its earlier map value.' };
});

await test('plain species callbacks share a mutable root resource without leaking into earlier children', async (als, mark) => {
  const source = gate(), completed = gate(), insideChild = gate(), outsideChild = gate();
  source.promise.constructor = { [Symbol.species]: function PlainSpecies(executor) {
    executor(() => {}, completed.reject); return {};
  } };
  let count = 0;
  const finish = () => { if (++count === 2) completed.resolve(); };
  als.run('REGISTER-A', () => source.promise.then(() => {
    assert.equal(mark('first-plain-before').store, ROOT);
    als.enterWith('ROOT-X');
    const row = mark('first-plain-after');
    assert.equal(row.store, 'ROOT-X'); assert.equal(row.executionAsyncId, 0);
    queueMicrotask(() => {
      assert.equal(mark('inside-child-after-mutation').store, 'ROOT-X'); insideChild.resolve();
    });
    finish();
  }));
  als.run('REGISTER-B', () => source.promise.then(() => {
    const row = mark('second-plain');
    assert.equal(row.store, 'ROOT-X'); assert.equal(row.executionAsyncId, 0); finish();
  }));
  queueMicrotask(() => {
    assert.equal(mark('outside-child-captured-before').store, ROOT); outsideChild.resolve();
  });
  source.resolve();
  await Promise.all([completed.promise, insideChild.promise, outsideChild.promise]);
  assert.equal(mark('ordinary-await-after').store, ROOT);
  return { relevantAsyncIds: [ids.get(source.promise)],
    verified: 'ID0 is a mutable shared resource, not a new immutable-empty context for each plain-species job. Pre-existing and newly registered child resources keep their respective captures.' };
});

await test('repeated AsyncResource calls retain mutation while an earlier child stays unchanged', async (als, mark) => {
  const resource = als.run('RESOURCE-A', () => new AsyncResource('edge-reused', { requireManualDestroy: true }));
  const child = gate();
  try {
    resource.runInAsyncScope(() => {
      assert.equal(mark('resource-first-before').store, 'RESOURCE-A');
      queueMicrotask(() => {
        assert.equal(mark('child-captured-before').store, 'RESOURCE-A'); child.resolve();
      });
      als.enterWith('RESOURCE-B');
      assert.equal(mark('resource-first-after').store, 'RESOURCE-B');
    });
    assert.equal(mark('outer-between').store, ROOT);
    resource.runInAsyncScope(() => assert.equal(mark('resource-second').store, 'RESOURCE-B'));
    await child.promise;
    assert.equal(mark('outer-after').store, ROOT);
    return { resourceAsyncId: resource.asyncId(), relevantAsyncIds: [resource.asyncId()],
      verified: 'The resource cell changes, but a previously created child cell must not alias that mutable cell.' };
  } finally { resource.emitDestroy(); }
});

await test('disable then re-enable exposes an old pending resource store', async (als, mark) => {
  const pending = gate();
  const old = als.run('OLD', async () => {
    await pending.promise;
    assert.equal(mark('old-after-reenable').store, 'OLD');
  });
  als.disable();
  als.run('NEW', () => assert.equal(mark('new-run').store, 'NEW'));
  pending.resolve(); await old;
  assert.equal(mark('outer-after').store, ROOT);
  return { verified: 'Re-enable does not permanently invalidate old resource entries. A generation scheme that permanently deletes OLD would diverge.' };
});

hooks.disable();
// A custom species reject path must propagate a reaction assertion/error rather
// than resolving the completion gate and falsely reporting success.
const rejectionMarker = {};
const rejectionGate = gate();
const rejectionSource = Promise.resolve();
rejectionSource.constructor = { [Symbol.species]: function PlainRejectingSpecies(executor) {
  executor(rejectionGate.resolve, rejectionGate.reject); return {};
} };
rejectionSource.then(() => { throw rejectionMarker; });
await assert.rejects(rejectionGate.promise, error => error === rejectionMarker);
const report = {
  schemaVersion: 1, verifiedAtUtc: new Date().toISOString(), node: process.version,
  executable: process.execPath,
  executableSha256: createHash('sha256').update(await readFile(process.execPath)).digest('hex'),
  sourceSha256: createHash('sha256').update(await readFile(fileURLToPath(import.meta.url))).digest('hex'),
  execArgv: process.execArgv, nodeOptionsPresent: Boolean(process.env.NODE_OPTIONS),
  cases, caseCount: cases.length,
  observationCount: cases.reduce((count, item) => count + item.observations.length, 0),
  assertionPropagationChecked: true,
  predecessor: {sourcePath: 'node-promise-edge-oracle-v1.mjs',sourceSha256:createHash('sha256').update(await readFile(join(here,'node-promise-edge-oracle-v1.mjs'))).digest('hex'),resultsPath:'node-promise-edge-oracle-v1-results.json',resultsSha256:createHash('sha256').update(await readFile(join(here,'node-promise-edge-oracle-v1-results.json'))).digest('hex'),reason:'Preserve the original observations; corrected current species completion gates reject on handler failure instead of potentially swallowing assertion errors.'},
  findings: [
    'Real Promise species controls the result resource: construction in SPECIES makes its reaction execute in SPECIES, even though registration and the getter/constructor caller use REGISTER.',
    'A plain-object species result has no Promise init resource; its callback executes on shared resource0, not REGISTER or SPECIES.',
    'enterWith mutates a resource cell; subsequent jobs on the same promise, explicit AsyncResource or root resource can observe that mutation.',
    'Independent child resources capture the earlier map; their cells must not alias the parent resource cell.',
    'run restores only its own AsyncLocalStorage instance entry, preserving changes made to other instances.',
    'disable then re-enable can reveal an existing pending resource store again.',
  ],
  scope: 'Executed exact Node v22.14.0 defaults. These are behavioral oracle observations, not a SpiderMonkey implementation claim. Async IDs identify relationships in this run and are not stable constants. No external service or production file is used.',
};
await writeFile(join(here, 'node-promise-edge-oracle-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ node: report.node, cases: report.caseCount, observations: report.observationCount, passed: true }, null, 2));
