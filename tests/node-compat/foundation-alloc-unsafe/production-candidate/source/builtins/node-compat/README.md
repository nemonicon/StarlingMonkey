# Bounded Node v22.14.0 profile

Enable explicitly with `-DENABLE_BUILTIN_NODE_COMPAT=ON`. The default build excludes this profile. It requires the existing web TextEncoder/TextDecoder builtin and introduces no host capabilities or WASI interfaces.

The [versioned export manifest](export-manifest.node-v22.14.0.json) defines the selected surface: a partial `node:buffer` and an import-only `node:child_process`. Bare aliases resolve to the same exported values; global `Buffer` equals the named export. Default objects are frozen data-property objects. Full Node, full Buffer, dynamic CommonJS `require`, and CommonJS mutation synchronization are outside this profile.

The Buffer facade preserves real Uint8Array storage, shared ArrayBuffer views for `from(ArrayBuffer)`, `slice` and `subarray`, copying `from(Uint8Array)`, offsets, and default typed-array species behavior. UTF-8 uses the native web codecs; hex loops run in guest C++. Supported encodings are `utf8`, `utf-8`, and `hex`. Allocations are bounded to 16 MiB, hex strings to 32 MiB, and input strings to 1,048,576 UTF-16 code units. `alloc` accepts integer sizes and numeric fill only. Other Node Buffer operations are explicit throwing functions.

Unsupported operations throw `ERR_SM_NODE_UNSUPPORTED`, including during componentization. Fixed ArrayBuffer storage is required. Node-specific methods and constructors reject detached, resizable, shared and invalid backing stores before accessing bytes. Inherited Uint8Array methods retain the engine's native error behavior. Node-valid but unsupported encodings and overloads are refused; error messages and validation order are not an exact Node reproduction. User-modified constructors/species, cross-realm inputs and exotic coercions remain outside the selected overload contract.

Canonical `.mjs` sources are packaged into [factories.generated.h](factories.generated.h) by a small dependency-free generator that accepts only their exact import/export forms. Normal CMake builds compile the checked-in header and do not execute Node or npm. After modifying any canonical source or manifest, run:

```sh
node builtins/node-compat/generate-factories.mjs
node builtins/node-compat/generate-factories.mjs --check
```

Native kernels retain no JS pointers across calls and borrow byte pointers only inside a no-GC scope. Optional `-DNODE_COMPAT_GC_STRESS=ON` forces compacting collections at safe rooted allocation boundaries in test builds; it adds no JS export or host service. The experimental profile remains off by default. [Native integration checks](../../tests/node-compat/README.md) passed normal and compacting-GC builds; the [standard HTTP fixture](../../tests/node-compat/wasmcloud/README-host.md) also passed on unmodified wasmCloud 2.11.0. [A/B measurements](../../tests/node-compat/bench/README.md) compare the selected operations with the existing Jco adapter. Exhaustive OOM tests, broader compatibility and production request lifecycle work remain open. See [the architecture audit](../../docs/node-compat/README.md) for the original scope and source findings.
