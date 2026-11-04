// Dependency-free context/resource assertions shared by the real Node oracle
// and explicitly labeled guest completion-resource experiments.
function failure(message) {
  const error = new Error(message || 'Resource model assertion failed');
  error.code = 'ERR_RESOURCE_MODEL_ASSERTION';
  throw error;
}
function assert(condition, message) { if (!condition) failure(message); }
assert.equal = (actual, expected, message) => {
  if (!Object.is(actual, expected)) failure(message || 'Expected identical values');
};
function sameStructure(actual, expected) {
  if (Object.is(actual, expected)) return true;
  if (!actual || !expected || typeof actual !== 'object' || typeof expected !== 'object') return false;
  if (Object.getPrototypeOf(actual) !== Object.getPrototypeOf(expected)) return false;
  const actualKeys = Reflect.ownKeys(actual), expectedKeys = Reflect.ownKeys(expected);
  if (actualKeys.length !== expectedKeys.length) return false;
  for (const key of actualKeys) {
    if (!Object.prototype.hasOwnProperty.call(expected, key) || !sameStructure(actual[key], expected[key])) return false;
  }
  return true;
}
assert.deepEqual = (actual, expected, message) => {
  if (!sameStructure(actual, expected)) failure(message || 'Expected structurally equal values');
};

export async function runResourceEdgeCases({ AsyncLocalStorage, AsyncResource, queueMicrotask }) {
  const ROOT = '<undefined>';
  const cases = [];
  const value = storage => storage.getStore() ?? ROOT;
  const gate = () => {
    let resolve, reject;
    const promise = new Promise((done, fail) => { resolve = done; reject = fail; });
    return { promise, resolve, reject };
  };
  async function test(name, body, second = false) {
    const a = new AsyncLocalStorage(), b = second ? new AsyncLocalStorage() : null;
    const observations = [];
    const mark = label => {
      const row = { label, store: value(a), ...(b ? { secondStore: value(b) } : {}) };
      observations.push(row);
      return row;
    };
    try {
      const details = await body(a, mark, b);
      cases.push({ name, passed: true, observations, details });
    } finally { a.disable(); b?.disable(); }
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
            assert.equal(mark('species-constructor-after').store, 'REGISTER');
            return result;
          };
        },
      };
      const result = als.run('REGISTER', () => source.promise.then(input => {
        assert.equal(input, 3);
        const row = mark('reaction');
        assert.equal(row.store, 'SPECIES');
        return 7;
      }));
      assert.equal(result, createdResult);
      if (!settled) als.run('RESOLVER', () => source.resolve(3));
      assert.equal(await result, 7);
      assert.equal(mark('after-await').store, ROOT);
      return { verified: 'The callback executes on the real result Promise resource created inside the species constructor, under SPECIES rather than REGISTER.' };
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
        return 7;
      }));
      assert.equal(result, plain);

      if (!settled) als.run('RESOLVER', () => source.resolve(3));
      await completed.promise;
      assert.equal(mark('after-await').store, ROOT);
      return { verified: 'The callback and capability resolver run on shared root resource ID0, without REGISTER or SPECIES, because the result capability is not a Promise.' };
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

    const observed = als.run('AWAIT-D', async () => {
      assert.equal(await source.promise, 9);
      assert.equal(mark('await-continuation').store, 'AWAIT-D');
    });
    als.run('RESOLVER-B', () => source.resolve({
      then(resolveFirst) {
        const first = mark('first-thenable');
        assert.equal(first.store, 'CREATION-A');
        queueMicrotask(() => {
          assert.equal(mark('child-captured-before-mutation').store, 'CREATION-A');
          childDone.resolve();
        });
        als.enterWith('MUTATED-X');
        assert.equal(mark('first-after-enterWith').store, 'MUTATED-X');
        resolveFirst({ then(resolveSecond) {
          const second = mark('second-thenable');
          assert.equal(second.store, 'MUTATED-X');
          resolveSecond(9);
        } });
      },
    }));
    await Promise.all([observed, childDone.promise]);
    assert.equal(mark('outer-after').store, ROOT);
    return { verified: 'The same target Promise resource retains enterWith changes across assimilation jobs, while an independently created child retains its earlier map value.' };
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
      assert.equal(row.store, 'ROOT-X');
      queueMicrotask(() => {
        assert.equal(mark('inside-child-after-mutation').store, 'ROOT-X'); insideChild.resolve();
      });
      finish();
    }));
    als.run('REGISTER-B', () => source.promise.then(() => {
      const row = mark('second-plain');
      assert.equal(row.store, 'ROOT-X'); finish();
    }));
    queueMicrotask(() => {
      assert.equal(mark('outside-child-captured-before').store, ROOT); outsideChild.resolve();
    });
    source.resolve();
    await Promise.all([completed.promise, insideChild.promise, outsideChild.promise]);
    assert.equal(mark('ordinary-await-after').store, ROOT);
    return { verified: 'ID0 is a mutable shared resource, not a new immutable-empty context for each plain-species job. Pre-existing and newly registered child resources keep their respective captures.' };
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
      return { verified: 'The resource cell changes, but a previously created child cell must not alias that mutable cell.' };
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


  // Verify that the custom species rejection path cannot swallow a failed handler.
  const marker = {}, completed = gate(), source = Promise.resolve();
  source.constructor = { [Symbol.species]: function RejectingSpecies(executor) {
    executor(completed.resolve, completed.reject); return {};
  } };
  source.then(() => { throw marker; });
  let rejected = false;
  try { await completed.promise; }
  catch (error) { assert.equal(error, marker); rejected = true; }
  assert(rejected, 'Species rejection must propagate handler failure');
  return {
    cases, caseCount: cases.length,
    observationCount: cases.reduce((count, item) => count + item.observations.length, 0),
    assertionPropagationChecked: true,
    comparisonScope: 'store semantics only; lifecycle/ID assertions excluded',
  };
}
