// Exact-release behavioral oracle. This does not provide a guest ALS implementation.
import assert from 'node:assert/strict';
import { AsyncLocalStorage, AsyncResource, executionAsyncId, executionAsyncResource } from 'node:async_hooks';
import { createHash } from 'node:crypto';
import { readFile as readFileCallback } from 'node:fs';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

assert.equal(process.version, 'v22.14.0', 'Use the pinned Node v22.14.0 executable');
assert.deepEqual(process.execArgv, [], 'Run this file without Node feature flags');
assert(!process.env.NODE_OPTIONS, 'Run without NODE_OPTIONS to measure release defaults');
const ROOT = '<undefined>';
const here = dirname(fileURLToPath(import.meta.url));
const cases = [];
const pending = () => {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
};
const tick = () => new Promise(done => queueMicrotask(done));

async function test(name, body) {
  const storage = new AsyncLocalStorage();
  const observations = [];
  const mark = (label, extra = {}) => {
    const store = storage.getStore();
    const resource = executionAsyncResource();
    const observation = {
      label, store: store === undefined ? ROOT : store,
      resourceKind: resource?.constructor?.name ?? '<unknown>',
      executionAsyncId: executionAsyncId(), ...extra,
    };
    observations.push(observation);
    return observation.store;
  };
  try {
    await body(storage, mark, observations);
    cases.push({ name, passed: true, observations });
  } finally {
    storage.disable();
  }
}

await test('run return, throw and temporary-context restoration', async (als, mark) => {
  assert.equal(mark('before'), ROOT);
  const marker = {};
  const returned = als.run('A', () => {
    assert.equal(mark('inside-A'), 'A');
    assert.equal(als.run('B', () => mark('inside-B')), 'B');
    assert.equal(mark('after-nested-run'), 'A');
    try { als.run('THROW', () => { mark('inside-throw'); throw marker; }); }
    catch (error) { assert.equal(error, marker); }
    assert.equal(mark('after-throw'), 'A');
    return marker;
  });
  assert.equal(returned, marker);
  assert.equal(mark('after'), ROOT);
});

await test('interleaved pending, settled and primitive awaits', async (als, mark, observations) => {
  const a = pending(), b = pending();
  const worker = (name, gate) => als.run(name, async () => {
    mark(name + ':before');
    await gate;
    assert.equal(mark(name + ':pending'), name);
    await Promise.resolve('already settled');
    assert.equal(mark(name + ':settled'), name);
    await 1;
    assert.equal(mark(name + ':primitive'), name);
  });
  const pa = worker('A', a.promise), pb = worker('B', b.promise);
  als.run('RESOLVER', () => { b.resolve(); a.resolve(); });
  await Promise.all([pa, pb]);
  assert.equal(mark('after-workers'), ROOT);
  assert.deepEqual(observations.map(x => x.label), [
    'A:before', 'B:before', 'B:pending', 'A:pending', 'B:settled',
    'A:settled', 'B:primitive', 'A:primitive', 'after-workers',
  ]);
});

await test('pending then handlers capture registration including empty root', async (als, mark) => {
  const gate = als.run('PROMISE-CREATION', pending);
  const a = als.run('A', () => gate.promise.then(() => assert.equal(mark('registered-A'), 'A')));
  const root = gate.promise.then(() => assert.equal(mark('registered-root'), ROOT));
  const b = als.run('B', () => gate.promise.then(() => assert.equal(mark('registered-B'), 'B')));
  als.run('RESOLVER', () => gate.resolve());
  await Promise.all([a, root, b]);
  assert.equal(mark('after'), ROOT);
});

await test('settled then handlers capture registration rather than promise creation', async (als, mark) => {
  const promise = als.run('PROMISE-CREATION', () => Promise.resolve());
  await Promise.all([
    als.run('A', () => promise.then(() => assert.equal(mark('registered-A'), 'A'))),
    promise.then(() => assert.equal(mark('registered-root'), ROOT)),
    als.run('B', () => promise.then(() => assert.equal(mark('registered-B'), 'B'))),
  ]);
});

await test('thenable assimilation uses resolved promise creation context', async (als, mark) => {
  const gate = als.run('PROMISE-CREATION-A', pending);
  const thenable = als.run('THENABLE-OBJECT-C', () => ({
    then(resolve) {
      assert.equal(mark('thenable.then'), 'PROMISE-CREATION-A');
      resolve(7);
    },
  }));
  const waiter = als.run('AWAIT-REGISTRATION-D', async () => {
    assert.equal(await gate.promise, 7);
    assert.equal(mark('await-continuation'), 'AWAIT-REGISTRATION-D');
  });
  als.run('RESOLVER-B', () => gate.resolve(thenable));
  await waiter;
});

await test('root-created promise assimilation stays empty despite resolver context', async (als, mark) => {
  const gate = pending();
  const waiter = als.run('AWAIT-A', async () => {
    await gate.promise;
    assert.equal(mark('await-continuation'), 'AWAIT-A');
  });
  als.run('RESOLVER-B', () => gate.resolve({
    then(resolve) { assert.equal(mark('thenable.then'), ROOT); resolve(); },
  }));
  await waiter;
});

await test('Promise.resolve thenable uses call-time promise creation context', async (als, mark) => {
  const thenable = als.run('OBJECT-CREATION', () => ({
    then(resolve) { assert.equal(mark('thenable.then'), 'RESOLVE-A'); resolve('ok'); },
  }));
  const promise = als.run('RESOLVE-A', () => Promise.resolve(thenable));
  await als.run('AWAIT-B', async () => {
    assert.equal(await promise, 'ok');
    assert.equal(mark('await-continuation'), 'AWAIT-B');
  });
});

await test('finally and subsequent reactions keep separate registration contexts', async (als, mark) => {
  const gate = pending();
  const final = als.run('FINALLY-A', () => gate.promise.finally(() => {
    assert.equal(mark('finally'), 'FINALLY-A');
  }));
  const after = als.run('THEN-B', () => final.then(value => {
    assert.equal(value, 11);
    assert.equal(mark('after-finally'), 'THEN-B');
  }));
  als.run('RESOLVER-C', () => gate.resolve(11));
  await after;
});

await test('all and race retain each user callback registration context', async (als, mark) => {
  const a = pending(), b = pending();
  const all = als.run('ALL-CREATION', () => Promise.all([a.promise, b.promise]));
  const race = als.run('RACE-CREATION', () => Promise.race([a.promise, b.promise]));
  const allObserver = als.run('ALL-CALLBACK', () => all.then(value => {
    assert.deepEqual(value, [1, 2]);
    assert.equal(mark('all-callback'), 'ALL-CALLBACK');
  }));
  const raceObserver = als.run('RACE-CALLBACK', () => race.then(value => {
    assert.equal(value, 2);
    assert.equal(mark('race-callback'), 'RACE-CALLBACK');
  }));
  als.run('RESOLVE-B', () => b.resolve(2));
  als.run('RESOLVE-A', () => a.resolve(1));
  await Promise.all([allObserver, raceObserver]);
});

await test('queueMicrotask captures the registration context', async (als, mark) => {
  const waits = [];
  const schedule = label => waits.push(new Promise(done => queueMicrotask(() => {
    assert.equal(mark(label), label === 'root' ? ROOT : label);
    done();
  })));
  als.run('A', () => schedule('A'));
  schedule('root');
  als.run('B', () => schedule('B'));
  await Promise.all(waits);
});

await test('native timeout callback captures registration and cancellation suppresses callback', async (als, mark) => {
  const one = new Promise(done => als.run('TIMEOUT-A', () => setTimeout(() => {
    assert.equal(mark('timeout-A'), 'TIMEOUT-A'); done();
  }, 1)));
  let cancelledFired = false;
  const cancelled = als.run('CANCELLED-B', () => setTimeout(() => { cancelledFired = true; }, 5));
  clearTimeout(cancelled);
  await one;
  await new Promise(done => setTimeout(done, 10));
  assert.equal(cancelledFired, false);
  assert.equal(mark('after-cancelled-window', { cancelledFired }), ROOT);
});

await test('interval enterWith changes the same resource for later callbacks', async (als, mark) => {
  let count = 0;
  await new Promise(done => als.run('INTERVAL-A', () => {
    const timer = setInterval(() => {
      count++;
      if (count === 1) {
        assert.equal(mark('first-start'), 'INTERVAL-A');
        als.run('TEMP', () => assert.equal(mark('temporary-run'), 'TEMP'));
        assert.equal(mark('after-temporary-run'), 'INTERVAL-A');
        als.enterWith('INTERVAL-B');
        assert.equal(mark('first-after-enterWith'), 'INTERVAL-B');
      } else {
        clearInterval(timer);
        assert.equal(mark('second-start'), 'INTERVAL-B');
        done();
      }
    }, 1);
  }));
  assert.equal(count, 2);
  assert.equal(mark('after-interval'), ROOT);
});

await test('native filesystem callback and promise I/O retain registration contexts', async (als, mark) => {
  const callback = new Promise((done, reject) => als.run('FS-CALLBACK-A', () => {
    readFileCallback(fileURLToPath(import.meta.url), (error, bytes) => {
      if (error) { reject(error); return; }
      assert(bytes.length > 0);
      assert.equal(mark('fs-callback'), 'FS-CALLBACK-A'); done();
    });
  }));
  const promise = als.run('FS-AWAIT-B', async () => {
    assert((await readFile(fileURLToPath(import.meta.url))).length > 0);
    assert.equal(mark('fs-await'), 'FS-AWAIT-B');
  });
  await Promise.all([callback, promise]);
});

await test('disable without re-enable hides an old pending continuation store', async (als, mark) => {
  const gate = pending();
  const old = als.run('OLD', async () => {
    await gate.promise;
    assert.equal(mark('old-after-disable'), ROOT);
  });
  als.disable(); gate.resolve(); await old;
});

await test('disable then re-enable can reveal the old pending resource store again', async (als, mark) => {
  const gate = pending();
  const old = als.run('OLD', async () => {
    await gate.promise;
    assert.equal(mark('old-after-reenable'), 'OLD');
  });
  als.disable();
  als.run('NEW', () => assert.equal(mark('new-run'), 'NEW'));
  gate.resolve(); await old;
});

await test('a continuation registered while disabled remains empty after re-enable', async (als, mark) => {
  const first = pending(), second = pending(), registered = pending();
  const old = als.run('OLD', async () => {
    await first.promise;
    assert.equal(mark('old-first-disabled'), ROOT);
    registered.resolve();
    await second.promise;
    assert.equal(mark('old-second-after-reenable'), ROOT);
  });
  als.disable(); first.resolve(); await registered.promise;
  als.run('NEW', () => assert.equal(mark('new-run'), 'NEW'));
  second.resolve(); await old;
});

await test('separate ALS instances preserve independent stores', async (als, mark) => {
  const second = new AsyncLocalStorage(), gate = pending();
  try {
    const work = als.run('ONE', () => second.run('TWO', async () => {
      await gate.promise;
      assert.equal(mark('both-after-await', { secondStore: second.getStore() }), 'ONE');
      assert.equal(second.getStore(), 'TWO');
    }));
    gate.resolve(); await work;
    assert.equal(mark('after', { secondStore: second.getStore() ?? ROOT }), ROOT);
    assert.equal(second.getStore(), undefined);
  } finally { second.disable(); }
});

await test('snapshot restores capture context and then restores its caller', async (als, mark) => {
  const invoke = als.run('SNAPSHOT-A', () => AsyncLocalStorage.snapshot());
  als.run('CALLER-B', () => {
    invoke(() => assert.equal(mark('snapshot-body'), 'SNAPSHOT-A'));
    assert.equal(mark('snapshot-caller-after'), 'CALLER-B');
  });
  assert.equal(mark('after'), ROOT);
});

await test('resource reuse retains enterWith state; fresh resource starts empty', async (als, mark) => {
  const reused = new AsyncResource('oracle-reused', { requireManualDestroy: true });
  const fresh = new AsyncResource('oracle-fresh', { requireManualDestroy: true });
  try {
    reused.runInAsyncScope(() => {
      assert.equal(mark('reused-first-before'), ROOT);
      als.enterWith('REQUEST-ONE');
      assert.equal(mark('reused-first-after'), 'REQUEST-ONE');
    });
    assert.equal(mark('outer-after-first'), ROOT);
    reused.runInAsyncScope(() => assert.equal(mark('reused-second'), 'REQUEST-ONE'));
    fresh.runInAsyncScope(() => assert.equal(mark('fresh-second'), ROOT));
    assert.equal(mark('outer-after-second'), ROOT);
  } finally { reused.emitDestroy(); fresh.emitDestroy(); }
});

await tick();
const source = await readFile(fileURLToPath(import.meta.url));
const report = {
  schemaVersion: 1,
  verifiedAtUtc: new Date().toISOString(),
  node: process.version,
  executable: process.execPath,
  executableSha256: createHash('sha256').update(await readFile(process.execPath)).digest('hex'),
  execArgv: process.execArgv,
  nodeOptionsPresent: Boolean(process.env.NODE_OPTIONS),
  sourceSha256: createHash('sha256').update(source).digest('hex'),
  caseCount: cases.length,
  observationCount: cases.reduce((count, value) => count + value.observations.length, 0),
  cases,
  findings: [
    'Promise reactions and await continuations retain their registration context, including an empty context when resolved inside another store.',
    'A thenable assimilation job uses the promise resource creation context, which can differ from both resolver context and thenable-object creation context.',
    'enterWith mutates the currently executing resource context: an interval or explicitly reused AsyncResource sees that mutation in a later callback.',
    'disable hides stores while disabled; re-enabling before an old continuation resumes can reveal its previous resource store. It is not permanent generation invalidation.',
    'A new continuation registered while disabled does not inherit the old store merely because the ALS instance is subsequently re-enabled.',
    'Independent request resources start independently; reusing one resource does not itself clear prior enterWith state.',
  ],
  scope: 'Executed behavior of exact Node v22.14.0 default flags. This is an oracle, not a guest implementation or a claim that SpiderMonkey hooks already reproduce it. Filesystem I/O only reads this oracle source; no external service is contacted.',
};
await writeFile(join(here, 'node-oracle-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ node: report.node, cases: report.caseCount, observations: report.observationCount, passed: true }, null, 2));
