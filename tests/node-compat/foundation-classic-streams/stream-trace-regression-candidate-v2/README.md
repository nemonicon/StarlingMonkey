This is a NEW source-only11-case successor to sealed v1/636dfc. It retains the
exact original eight public64byte cases and adds only three ordinary supported
object-mode Writable calls using payload={id:1}: write(payload),
write(payload,callback), and write(payload,'utf8',callback). No null encoding is
ever supplied as input; there are no odd encodings, Proxies, invalid receivers,
fatal probes or new host capabilities. Hook completion and optional user-write
callback counts are recorded separately, with exact object identity/value/keys.

Pinned Node22 observes undefined, null, and string'utf8' hook encodings for those
three calls. The JSON carrier deliberately distinguishes {type:'undefined'},
{type:'object',value:null}, and {type:'string',value:'utf8'}. The current canonical
factory on Node dependencies observes utf8 for all three. Thus the host model
has six gaps: the four preserved v1 byte/order gaps plus two object-default gaps;
the explicit UTF8 control matches. Actual guest outcomes are not assumed. The
new one-argument case makes the undefined-vs-null distinction explicit without
testing a null input overload.

The first unsealed reverse proof rejected overlapping loop replacements; its
partial owned sources are preserved. The first unsealed10-case Node attempt
rejected an overly narrow reviewer encoding-carrier assertion when the ordinary
callback overload produced null. That source/failure is retained. A corrected
10-case Node success is also preserved before Root requested the11-case scope.
These are source/oracle preparation observations, not guest/product failures.

Three finite reverse proofs bind cases, driver and Node-oracle edits to v1.
Guest, future entry and actual runtime-v3 preflight template remain byte-identical.
The future driver validates all11 cases with per-kind byte/object invariants,
retains actual Node comparison data, and does not force guest=model or parity.
The same exact normal-OFF b827/873c and runtime index7e952 are required; selected
interfaces stay empty and run()->string stays the sole application export.
Existing tracked output/completion and native/source rechecks remain unchanged.
Root must supply an explicit NEW fresh NODE_COMPAT_STREAM_TRACE_OUTPUT later;
there is no fallback, overwrite, old result reuse or fixed old-output relocation.

V1 already has real component evidence: Root80465 raw0 and independent7db354
confirm its four gaps across three retained calls, fresh Jco and fresh Wasmtime.
This packet preserves that evidence and all old source/results. V2 preparation
runs only ordinary Node oracle/model and pure/source/syntax checks. It does not
invoke native preflight, bundling, componentizer, guest or target host. New v2
guest execution requires Root's delta review and separate authorization. No live
factory/source342, manifests, native pins or APIs change; the five-edit semantic
proposal and future integration remain separate. No full streams/Node parity,
reset/ALS, GC/root, memory or performance claim follows.
