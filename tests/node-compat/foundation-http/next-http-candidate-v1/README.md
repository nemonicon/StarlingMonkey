This experimental baseline registers real `node:http`/`http` and
`node:https`/`https` module records through the existing
`api::Engine::define_builtin_module`. Its generated factory captures the actual
installed classic Readable/Writable, EventEmitter and native-backed Buffer.
Named/default bindings share initial values; the CommonJS default remains
mutable. The public manifest declares the exact pinned Node22.14.0 export names.

The implemented transport is Node-shaped IncomingMessage/ServerResponse over
Web Request/Response, with header/status handling, input EOF/abort, owned output
bytes, backpressure and close/error paths. Constructors require deployed
execution and this specific transport. Raw sockets, ClientRequest, listen and
TLS remain explicit throwing operations. Agent/HTTPS Agent are configuration
objects with pure naming and no resources; connection methods throw
`ERR_SM_NODE_UNSUPPORTED`. METHODS/STATUS_CODES preserve real protocol-data
types. This is not complete Node HTTP compatibility.

`starling:node-http` is a separate versioned **guest builtin**, with
`createServerHandler`, `runFreshRequest` and `runNeutralServer`. These functions
bind the genuine new native context entries, with no identity fallback or
custom host service. Shared readiness is created neutrally before admission.
The WASI adapter enters the native request owner before headers/body/Request
conversion. The later component-entry descendant additionally handles failure
before native callback entry; see its separate ownership models and derivation.

The canonical/generated host checks pass62 cases. The native registrar/kernel
also passes the actual joined SDK frontend; linking and guest semantics remain
pending. The stronger full Next host controls exercise these same exported
message classes. V1 exposes Readable.toWeb failures; V2 fixes HTTP behavior with
the bounded stream extension, while retaining a browser abort diagnostic.
Neither is native context or Wasm evidence.

`independent-review-v1/root-module-integration.json` supplies explicit default-OFF
CMake flags, actual registrar edits and16 mappings for this family and the
finite import family. HTTP is installed under `builtins/node-compat/next-http/`;
preserve that directory context for C++ includes and the generator's sibling
inputs. The selected entry explicitly imports standard WASI HTTP0.2.10 and IO
interfaces. Host transport and outgoing fetch policy remain separate from these
guest module bindings. No P2 socket TLS implementation is assumed.
