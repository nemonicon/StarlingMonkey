# Disconnect abort Source triage

The leading hypothesis is an adapter ordering problem: aborting the incoming Request destroys the bridge's outgoing Web stream **before** the adapter cancels its reader. The cancellation can then reject with the bridge-created `ECONNRESET: Request aborted`; the adapter promotes that cancellation failure to a rejected standard incoming-handler export. This is a Source-supported suspected path, not a proved direct cause or an authorized patch.

Root reports the closed Wasmtime sample completed 95 normal +19 intentional calls with clean process ownership, while stderr contained19 request-abort/native-abort diagnostics. R's separate closed-stderr census reported19 `Request aborted`,19 `Redirecting call to abort() to mozalloc_abort`,19 worker/backtrace blocks, and zero `Promise rejected but never handled` or `ERR_SM_NODE_EXECUTION_REJECTION` markers. C did not reopen runtime outputs. Functional recovery and these negative diagnostics must both remain recorded; process recovery does not establish an instance survived.

## Selected Source path

1. In [guest-entry.mjs](/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-public-correlation-entry-v1/guest-entry.mjs:616), `createWasiHttpHandler.handleResources` catches an actual `blockingWriteAndFlush` failure (710). At729 it calls `abortObservedIo(primary)` for an observed `closed` or `last-operation-failed` output after response publication. `abortObservedIo` calls the real `ioAbort.abort(reason)` at619. This happens **before** the known-closed branch awaits `responseReader.cancel(primary)` at733.
2. In [bridge.mjs](/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/native-source/builtins/node-compat/next-http/bridge.mjs:79), `BridgeIncomingMessage.onAbort` creates a **new** `failure('ECONNRESET', 'Request aborted')` and calls `this.socket.destroy(error)` (79–83). `RequestTransport.destroy` destroys both its request and response (40–47). `BridgeServerResponse._destroy` errors its Web response controller when the body is not already closed (220–230).
3. The generated [next-http-factory.generated.h](/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/native-source/builtins/node-compat/next-http/next-http-factory.generated.h:81) contains those same abort/body-error operations. [next-http.cpp](/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/native-source/builtins/node-compat/next-http/next-http.cpp:36) evaluates that captured factory and supplies the actual selected classic Readable/Writable/EventEmitter/Buffer. The guest imports `createServerHandler` from this registered `starling:node-http`, rather than the host-only bridge file in the repository.
4. [request-response.cpp](/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/native-source/builtins/web/fetch/request-response.cpp:380) stores a supplied genuine ReadableStream as the Response BodyStream (380–386); `body_get` returns that stored stream (1422–1439). The bridge's controller and the adapter's response reader therefore act on the same supplied stream in this path. Cancellation of an already-errored stream is the specific rejection behavior the next public Node control should reproduce, including exact error identity.
5. Back in the entry, a cancellation rejection at733 is passed to `rememberFailure` (734). The original first unknown/falsy primary is preserved; after cleanup, `if(primarySet) throw primaryValue` at755 rejects the async handler. This is distinct from the supported normal-return path for an exactly classified closed output.
6. [embedding.cpp](/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/componentize-source/embedding/embedding.cpp:219) installs a catch reaction on the exported Promise. `call_catch_handler` dumps its rejection at219–224; after event-loop processing, `call()` directly calls `abort()` if the original export Promise is not fulfilled (500–506). The separate strict unhandled-rejection branch at489–493 reports a named diagnostic through [engine.cpp](/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/native-source/runtime/engine.cpp:398). The reported absence of those named markers is consistent with export rejection; it does not independently identify which rejection or trap occurred.

## Smallest next regression and repair candidate

First add a bounded shared **public JS bridge control** under pinned Node22: construct a real Web Request/AbortController and the unchanged bridge, publish/read one response chunk, then compare abort-before-reader-cancel with reader-cancel-before-abort. Record settled outcomes and exact cancellation reason identity; attach handlers to reader cancellation and reader.closed before inducing errors. Add a successful normal-drain control plus cancellation-rejecting `false` and object reasons so a fix cannot hide unknown/falsy cleanup failures. This control exercises actual Web/classic stream APIs, with no fake WASI backend, guest counters or host-resource claim.

The narrow guest-side candidate is to change **only** the exactly observed closed-output branch: retire/cancel its response reader before delivering the I/O abort that destroys the same bridge stream, then still propagate the Request signal and verify reader-release/owned cleanup before returning. Keep input-read abort behavior and unknown/`last-operation-failed` failures separately classified. Do not simply ignore all cancel rejections, remove abort propagation, swallow arbitrary errors, or weaken the embedding rejection policy. The precise ordering needs the Node control and then a fresh guest selector/component to validate it.

Root should run the unchanged fixed19-cycle/114-call real-host probe on that separately versioned guest entry with the admitted e307 engine and standard13 interfaces, followed by matched controls. Require unchanged normal/intent outcomes and recovery, explicit diagnostics census, normal host/owner cleanup, and preserved old negative results. No native rebuild is implied by an entry-only candidate. A clean stderr result, if obtained, still would not prove same-Store reuse, native-handle retirement or full Next/Node promotion.

## What remains uncertain

No actual cancellation rejection value, stream state transition or handler Promise identity was captured by C. A different abort listener, a pending classic-stream callback, an unrelated unhandled Promise, or a separate native failure could contribute. The request-abort Error's allocation stack alone is not its throw site. The simple public bridge control plus a fresh ordinary-HTTP guest sample must discriminate the suspected path before adoption; live targets and frozen Sources stay unchanged in this audit.

## Pins and scope

The selected full52 metadata below binds the e307 engine and its actual435 native inputs plus3 embedding inputs. C hashed/bookended these finite Source files and joined their rows to that metadata; no binary payload, helper, compiler, parser, Node or host was invoked. Entry bytes remain immutable022f. Related authorship: C authored/reviewed adapter and construction ancestors; this is a focused complementary Source audit.

| Role | SHA256 | Bytes |
|---|---|---:|
| entry | `022fccdfb1d9f603f7cbed6136edb99d1e7767fad4a3fd5e6c808acdcb3c236e` | 48063 |
| bridge | `756580fcbb7940ea4fcd3135b9631b7c87c6a85b73d194b1adb251e9f28318f5` | 10565 |
| factory | `16001217b9f1997374523da702bf34f706d60b891f0a8f2bea1bc6bff8858e70` | 20027 |
| registration | `159c77044c2d4bd7eadb474ce133545cbe2afeb6a364817e7dbff085ddccc75c` | 3335 |
| response | `0431184d4562972c98538494caf46d2b11cdf0280f51d0e7143cd8534526442e` | 130742 |
| embedding | `62376b242d9ee4349363a3985c2c394fba940db74e73c03515249df84164db25` | 29751 |
| engine | `8ea9ac4670ecacaa5da053e6e912520d599c1c6c8801245b508526b708c6acce` | 28146 |
| metadata | `c7e225af3046b87939ec057ecf6c4ecbea3a3102a77c1fc05e4bf6f39b74f026` | 1161902 |

Selected engine (metadata row only): `e3075c14ec903831fb43dd305fb9c21eeaeb99a0d0a71c052fbda3a914faa965` / 31353161 bytes. No engine bytes were read.
