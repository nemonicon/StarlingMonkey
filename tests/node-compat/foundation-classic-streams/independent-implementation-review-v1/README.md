# Classic implementation: independent source and host review

The sealed source candidate743037e2 and separate allocation-order amendment
f723d0c9 pass this bounded review. Neither is applied or compiled; no installed
classic module, candidate engine, component, guest or native scheduler test
exists. Current306 native source inputs remain unchanged.

The reviewer rehashes223 indexed text files,342 source/provenance inputs,24 raw
licensed modules,24 transformed modules and the generated factory. The private
cache preserves CJS cycles without a public require/process API. The finite
root24/promises3 records, callable/mutable default graph, shared constructors,
explicit deferred operations and selected interfaces[] are source contracts.
They are not complete classic-stream or Node compatibility.

Two review findings were corrected before the source seal: Web Transform/pair
shapes are rejected before private Web dispatch, and custom-promisify getters
follow mutations of promises.default while named bindings stay snapshots. The
owner-preserved named-helper recursion is also corrected. Fresh independent
Node host execution passed19 differential groups in each of two dependency
arms,48 deferred call/new checks,17 overload refusals and four mutable-default
observations. The report bytes equal the sealed owner's report. Generation
--check passed without writing a header.

One additional C++ source finding required the separate amendment. The original
proposal checked JS_NewPlainObject only after allocating nextTick. The corrected
register changes only immediate null checking before the next allocating JSAPI
and a separate nextTick check. The complete corrected patch0574b88e must replace
the original native proposal for any future integration. This preserves the
first failure by source reasoning; no genuine OOM/fault path was run or proved.

The proposed bridge uses existing evaluate_factory/define_builtin_module and
EventLoop::create_internal_next_tick, with Rooted dependencies/records across
allocations. JS-owned byte windows and existing native Buffer/decoder operations
avoid a new native borrow or allocator transfer. Callback/argument/state tracing
would rely on the existing native FIFO; that lifetime is not proved by a Node
host algorithm run. One host arm uses a JS reference hex kernel, Node codecs/
nextTick and a non-native abort option symbol.

New finite producer/source/admission rules, native syntax and default-OFF flag
integration, actual zero-import components, initializer/deferred/alias/CJS,
queue/encoding/cancellation/boundary, snapshot/retained/fresh, ordinary Release-GC
and same-byte target-host gates remain mandatory. No public process, ALS/reset/
request teardown, complete reflection, GC-root isolation or performance benefit
is claimed. [results.json](results.json) preserves exact scope and limits;
[host-mirrors.json](host-mirrors.json) indexes copies of only fresh host evidence.
No candidate, amendment, live source or previous result was edited by review.
