# Repeated Next disconnect and recovery

This is the next functional lifecycle gate after the full three-arm comparison
in commit `6f388aa8`. It uses the same engine `e3075c14`, Next component `bfb106fe`,
observer envelope `f1c32f45`, application and 13 standard WASI 0.2.10 interfaces.
The application and existing browser assertions are unchanged. This probe does
not execute the browser or replace the passing full application suite.

The fixed host order is Wasmtime 42.0.1, stock wasmCloud 2.11.0, then matched
Node 22.14.0. Original process limits are 600, 600 and 300 seconds. Each client
has a fixed 180-second overall budget, three warm-up cycles and sixteen recorded
cycles. Each cycle makes six sequential requests on independently owned sockets:

1. Consume `/stream` completely and require observed shell-before-ready delivery.
2. Request `/stream`, retain the first actual body bytes, then destroy that client request.
3. Send the declared malformed JSON to `/api/json` and require its complete 400 response.
4. Read `/api/context` with predeclared cycle-specific cookie/header values.
5. Read `/api/context` without those values and require both fields to be null.
6. Read `/api/fs-crypto` and require the existing exact text and SHA-256 response.

There are 114 planned calls per arm: 95 complete normal/error responses and
19 intentional disconnect observations. Every input value and limit is fixed
before execution. There are no retries, fallback endpoints, timing-based
disconnect triggers or unbounded output production. Warm-up labels do not turn
this functional test into a performance benchmark.

The collector distinguishes HTTP completion, consumer end, local destruction
and request/response/socket close. Node's parsed-message completion flag and
request destruction have separate meanings in the pinned
[HTTP API](https://nodejs.org/download/release/v22.14.0/docs/api/http.html#messagecomplete).
[Destroying a client request](https://nodejs.org/download/release/v22.14.0/docs/api/http.html#requestdestroyerror)
does not establish that the guest observed cancellation. The first body callback
may already contain a complete buffered response; that observation remains
explicit and does not become proof of peer-side cancellation.

A known, retained HTTP failure with closed local resources remains a failed
outcome and can be followed by the remaining fixed recovery calls. Uncertain
capture publication or cleanup stops the suffix. Overall budget expiry records
unattempted calls. Acceptance requires all declared calls, exact normal/error
responses, known intentional-close outcomes, complete publication, preserved
inputs and normal process shutdown. Local protocol controls cover the collector
before any real application arm starts.

This gate observes application recovery. It does not prove native handle counts,
garbage collection, resource retirement, same-Store reuse or stable memory use.
Stock wasmCloud's P2 instance lifecycle remains a documented host limit. Further
repeatability, clean-checkout reproduction, cost and promotion gates remain open.

Status: all three fixed runs completed. All 342 client observations pass, while
both guest hosts emit abort diagnostics and the matched Node bridge actor fails
with transport errors. The independent review and saved checker preserve this
negative lifecycle result; see `actual-probe-review.json` and `README.md`.
