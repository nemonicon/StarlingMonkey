This baseline declares exact pinned Node22.14.0 ESM export inventories for
`node:tty`, `node:inspector`, `node:v8` and `node:dns/promises`, with their bare
aliases and real native module registrations. It supplies the finite names
loaded by the genuine Next application. It is not a V8, inspector or DNS
implementation.

`tty.isatty` returns false for this nonterminal profile; `inspector.url` returns
undefined because no Node inspector exists. Other callable operations and
constructors throw own `ERR_SM_NODE_UNSUPPORTED`, `module` and `operation`
properties when invoked, including application top-level execution during
componentization. Nested exported function objects are finite declared values.
Data constants retain primitive types; deferred accessor data is undefined.
There is no universal Proxy, throwing property getter or accidental thenable.

Named/default values share initial identity. The CommonJS default is an ordinary
mutable object; automatic ESM resynchronization is not claimed. Prototype and
descriptor parity beyond the tested finite declarations is deferred. These
modules introduce no host imports and perform no DNS/socket/TLS operation.

Canonical and generated factories pass422 host checks, including every declared
top-level deferred callable's call/new failure, safe namespace inspection,
meaningful constants and top-level failure. The native registration also passes
the actual joined SDK frontend. No linked engine or guest result follows from
those checks. The full-app host control selects these records without falling
back to stock Node for their names.

The generated header hashes the canonical factory, versioned inventory and
explicit public manifest. Installation uses its own
`builtins/node-compat/next-imports/` directory and the existing registry/CMake
mechanisms; see the sibling HTTP family's explicit integration delta. Both
features default OFF.
