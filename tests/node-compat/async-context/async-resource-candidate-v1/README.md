# Bounded AsyncResource entry facade

Source candidate for the real Next `send` failure on engine `4623640b`. No engine,
guest request, compiler or native build ran while authoring this family. The
selected host checks use pinned Node v22.14.0's **actual** AsyncLocalStorage
snapshot backend and compare it with Node's actual AsyncResource. They do not
prove the guest backend or complete async_hooks compatibility.

The actual retained stderr contains 17 deferred AsyncResource failures. Among
the 406 files compiled in the earlier full Next host control, the sole textual
AsyncResource demand is `next/dist/compiled/send/index.js:47`: on-finished caches
the async_hooks module object, reads its AsyncResource property lazily, creates
a resource with a type string, then uses
`resource.runInAsyncScope.bind(resource, callback, null)`. At line 59, send has
already created and piped its real ReadStream before registering this listener.
The original exception interrupts that registration. Public asset HTTP500 and
browser failures are consistent with this branch; stderr does not establish a
separate native filesystem defect.

`installAsyncResourceFacade(asyncHooks)` changes only the writable CJS/default
AsyncResource data binding. Import and installation perform no capture, I/O,
bootstrap, scheduling or Promise workload. Install once during pure entry INIT,
before `Module.createRequire(...)("next")` and app.prepare. The existing deployed
startup bootstrap must run before application code constructs resources. The
facade **does not itself enforce** that native phase boundary; no deployed-only
capture API is exported to this JS entry. Do not use constructor capture during
INIT or claim captured contexts are reusable/reset-safe snapshots.

The constructor captures `AsyncLocalStorage.snapshot()` once at construction.
`runInAsyncScope(fn, thisArg, ...args)` invokes a real native snapshot around
`Reflect.apply`. In actual V7, snapshot calls kernel.capture, which clones the
enabled native store bindings; kernel.invoke enters ResourceStore::Scope. Its
C++ destructor restores the caller on both return and throw. The facade has a
WeakMap holding these actual native-backed snapshot closures; there is no JS
context stack, Promise patch, synthetic ID or new host interface. Scheduling
inside the callback uses the existing real Promise/task capture mechanisms.

Selected support is only a string constructor with no options and
runInAsyncScope. A 4,096 code-unit type bound and 1,023 user-argument bound are
explicit profile limits. Invalid callbacks get coded ERR_INVALID_ARG_TYPE,
where pinned Node22's corresponding TypeError is uncoded. Invalid receivers
are refused. Static/instance bind, emitDestroy, asyncId, triggerAsyncId,
constructor options and the existing hook/execution APIs remain coded deferred
operations. There is no fake destroy notification or lifecycle ID.

The full eight-name Node22 export inventory and provider constants are unchanged.
The included versioned manifest describes this **entry selection**, not an
installed native factory amendment. Existing frozen ESM named AsyncResource
bindings retain the old deferred function; only CJS/default is patched. Next's
observed send callsite reads that default property lazily, so it is covered.
Code that cached the old constructor before installation is outside this path.

The test suite checks constructor capture, multiple stores, caller restoration,
receiver/arguments/return identity, nested scopes, all falsy thrown values,
Promise rejection, await/timer propagation, disable/re-enable and disabled exit
capture, plus the exact on-finished wrapper shape. It retains the first failed
host attempt: the test incorrectly expected Node's callback TypeError to have
a code. The facade was unchanged for that correction; old raw failure remains.

`host-raw.tar.gz` losslessly retains both original0af runs and the final run,
including all stdout, stderr, started/status/terminal files and monitor data.
The final index closes this Source family. Sources and actual observation
references are in source-inputs.json; original files were bookended unchanged.
All full-app, native-guest, ownership/teardown, hooks, snapshot/reuse, security,
cost and adoption gates remain separate. Root must issue the next component and
ordinary guest action; these host checks do not grant one.
