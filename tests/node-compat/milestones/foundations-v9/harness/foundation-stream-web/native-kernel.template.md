# Uncompiled native constructor and brand template

[`native-kernel.template.cpp`](native-kernel.template.cpp) is proposed guest
code. It has **not been compiled, linked or executed**. The existing component
receipts validate retained JavaScript constructor behavior; they do not validate
this C++ retrieval route. No production source or CMake flag selects it.

The template uses actual pinned APIs and repository roots:

- `JS_GetClassObject(cx, JSProtoKey, MutableHandleObject)` from SpiderMonkey147
  `jsapi.h:204`, with real stream/queuing keys from `js/ProtoKey.h`.
- Public `BuiltinImpl<Impl>::proto_obj` from `include/builtin.h:238`, populated
  by the existing TransformStream/controller and TextEncoder/Decoder installers.
- `JS::IsReadableStreamBYOBReader(JSObject*)` from `js/Stream.h:282`, preceded
  by `js::IsScriptedProxy` rejection. This avoids a user-observable getter or
  destructive read merely to identify a receiver.
- Existing `JS_NewPlainObject`, rooted values and `JS_DefineProperty`/
  `JS_DefineFunction` for a private record. `create_stream_web_kernel` is a new
  internal function implemented by this template, not an embedding API claimed
  to exist already.

The single factory argument contains sixteen keys: thirteen actual native
stream/strategy constructors, private `TextEncoder`/`TextDecoder`, and
`isReadableStreamBYOBReader(value) -> boolean`. The latter accepts any JS value,
returns false for nonobjects/proxies and must not read application properties.
Proxy rejection is a bounded-profile deviation: the separate Node oracle shows
that Node22 accepts a Proxy of a genuine BYOB reader. This stronger native
brand must not be described as exact Node receiver semantics.
The future strict JS facade supplies its own codec-stream classes and explicit
deferred compression functions. The kernel retains no compression constructor
or temporary stream/writer promise and borrows no byte storage.

Integration must use the content realm and immediately root the returned
object, following the existing `register.cpp::install` treatment of
`create_kernel`. The target needs the source-root include directory and existing
`builtin_web_streams` and `builtin_web_text_codec` dependencies. Normal builtin
installation order follows `cmake/add_builtin.cmake` appending `INSTALL_BUILTINS`
in declaration order; CMake `add_dependencies` alone does not establish runtime
installation order. Those existing web declarations currently precede Node
compatibility. The template rejects missing roots/constructors instead of
creating an incomplete record.

Before production registration:

1. Harden native TransformStreamDefaultController receiver validation before
   exposing its constructor. Source review shows its class-instance prototype
   can pass the inherited class check with an uninitialized Stream slot; the
   getter/method paths then call `.toObject()` on that slot. No old-native
   prototype call was executed. Install a reviewed native guard or an explicit
   facade guard before testing invalid prototype access on a new implementation.
2. Compile against the exact SDK/SM archive and verify the actual target flags,
   source inputs and installation order. Confirm the public getter returns the
   same hidden writer/controller constructors as real native instances.
3. Test actual native brand behavior for genuine/released readers, primitives,
   prototype/tag spoofs, ordinary/revoked proxies and any supported realm
   wrappers. The isolated fixture's registry is not production brand evidence.
4. Validate guarded BYOB option access/error order against Node22 before calling
   native `read`. Preserve constructor/prototype identity; reject unsupported
   minimum-fill requests explicitly.
5. Register only an explicitly selected finite manifest through the existing
   builtin-module API. Test aliases/default/CJS/snapshot/initialization errors,
   pure zero imports and both selected HTTP hosts. Writable-controller signal,
   codec/iterator limits and compression deferrals remain explicit.
