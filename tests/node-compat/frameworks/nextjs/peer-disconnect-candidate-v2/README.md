# Observed-I/O abort and specific output-close successor

Held Source only; no new host reference, WASI call, component, engine, compiler,
network, GC/OOM, fault, reset or DEBUG workload. Actual target/authority/review
slots are NULL. Baselinef3fc/55ba and its actual raw1 inconclusive result remain
unchanged. This candidate changes isolated JS entry/adapter Source, not native
Source, public manifests, engine metadata, CMake flags or the13-interface8025
standard WASI0.2.10 world.

The actual baseline observed input1024 followed by `last-operation-failed`, an
application catch/finally with Request.signal false, and healthy inspection4.
Output delivered4096 before a real subsequent `closed` write; source/reader
cancellation and finally returned, then the collector correctly refused inspect.
The exact original result is referenced in `plan.json`; its `observationsValid`
is true but `collectorAccepted` is false. These observations select this bounded
fix; they are not reclassified as a completed cleanup test.

## Changed behavior

One real native AbortController is created inside the native fresh request
callback, before constructing its Request. The genuine Request receives its
signal. The existing native constructor validates that signal and creates a
dependent native signal; the existing controller drives native abort/reason and
event steps. `native-api-refs.json` pins actualV7 Source. AbortController/Signal
whole files match production; the Request signal-constructor span matches,
while its whole composed file also contains existing ALS edits. The initial
overbroad whole-file equality assertion is retained as a Source-only preparation
failure, corrected before any actor action.

On an actual input `last-operation-failed`, the adapter derives the same primary
body error, releases its input handles, errors the Web body, then synchronously
aborts in that turn before the reader's rejection continuation resumes. Existing
EOF `closed` is still EOF and does **not** abort. Unknown throws pass through the
original normalizer without being classified as transport failures. Cleanup or
abort refusal is recorded as fatal state and prevents a later handled return.
The first observed I/O reason remains sticky; an already-aborted controller is
not treated as a new signal event. Request creation records whether abort
preceded listener registration, so a pre-created abort is not fabricated as a
later delivered event. No idle independent peer-disconnect signal is introduced.

A normal handled return is allowed only for the actual output-write invocation's
own-data `closed` result, with the **same caught value** and an already consumed
response outparam. The real reader.cancel must return, its lock release must
return, the Request signal must be aborted, and every existing finally cleanup
call must return. Only then is `known-output-closed-handled-return` emitted and
the async handler returns normally. The incomplete outgoing body is disposed
after its stream, never finished successfully; no second response is attempted.
Last-operation-failed writes are signalled then rethrown. Unknown, trap, abort,
cancel, lock or disposal failures cannot satisfy the handled-return gate.

Reader locks are released on other settled response paths too. Existing
child-before-parent native disposal ordering and the donor's sequential-finally
failure limitation remain: a thrown cleanup can skip later cleanup, and no
handled return follows. Actual dispose-returned logs are not native registry,
GC-root, physical Store or post-Store-death counters. Cancellation awaits the
real Web-stream cancellation algorithm; no further data is read from a failed
peer to manufacture a drain or successful finish.

## Explicitly deferred and future validation

IncomingBody.finish still returns an immediately disposed, **uninspected**
future. No typed httpErrorCode extraction is added. The actual tool's
`get_result_types` recognizes a top-level Result; future.get has an
Option<nestedResults> signature. Its exact nested JS lifting was not established,
so no invented result shape or call was implemented. HTTP receive/trailer
completion and immediate idle-peer abort remain unsupported claims.

Future Root construction/runtime must bind this new Source/entry and a genuine
collector successor. The old8e021 collector intentionally rejects the new policy
and handled-return marker. Expected controls are healthy EOF with signalfalse,
the real failed input with signaltrue/same primary reason, and real outputclosed
with completed adapter calls before the new marker. A later same-factory tagged
inspection may prove retained JS observations only. Other errors, changed tags,
missing callbacks or cleanup failures remain failed/inconclusive. No actor runs
or native/full-Next/snapshot/security/adoption claim comes from these Source
checks.

`build-entry.py --check` only verifies text assembly. Grammar and `test-data.mjs`
use no AbortController, Request, resource, stream, timer, socket or guest objects;
the latter checks actual policy functions against inert operation-state DATA.
They do not stand in for native I/O proof. The author also wrote the baseline
diagnostic; independent Source review remains a separate Root step.
