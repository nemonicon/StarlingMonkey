// New private integration API authored here; not an existing embedding API.
#ifndef STARLING_ASYNC_CONTEXT_RUNTIME_H
#define STARLING_ASYNC_CONTEXT_RUNTIME_H
#include "async_context_store.h"
#include "js/Class.h"
namespace core::async_context {
bool prepare_before_self_hosted(JSContext* cx);
bool initialize_realms(JSContext* cx, JS::HandleObject content,
                       JS::HandleObject initializer);
ResourceStore& store();
JSObject* create_kernel(JSContext* cx);
// Actual new native request-entry boundary for the HTTP adapter. Async child
// resources retain the fresh owner root after this synchronous call returns.
bool run_fresh_request(JSContext* cx, JS::HandleValue callback,
                        JS::HandleValue receiver,
                        const JS::HandleValueArray& arguments,
                        JS::MutableHandleValue result);
// HTTP's private native kernel may bind this JSNative as runFreshRequest.
// Signature: (callback, receiver, ...args); not a public async_hooks export.
bool run_fresh_request_native(JSContext* cx, unsigned argc, JS::Value* vp);
// Readiness/global cache initialization must run here BEFORE HTTP admission.
// Returning a Promise preserves this neutral owner in its async descendants.
bool run_neutral_server(JSContext* cx, JS::HandleValue callback,
                        JS::HandleValue receiver,
                        const JS::HandleValueArray& arguments,
                        JS::MutableHandleValue result);
bool run_neutral_server_native(JSContext* cx, unsigned argc, JS::Value* vp);
// Called by existing pre-snapshot/reset guards; never drains or repairs state.
bool require_quiescent_server_boundary(JSContext* cx);
// New shared-compartment data realms use a static non-GC RealmPrivate marker.
// They cannot enqueue async jobs; Promise allocation marks the call unsupported.
static constexpr uint32_t DataRealmAsyncSlot = JSCLASS_GLOBAL_SLOT_COUNT;
bool initialize_data_realm(JSContext* cx, JS::HandleObject global);
bool is_data_realm(JS::Realm* realm);
void note_data_realm_async(JS::Realm* realm);
bool data_realm_async_attempted(JS::HandleObject global);
void shutdown_before_context(JSContext* cx);
} // namespace core::async_context
#endif
