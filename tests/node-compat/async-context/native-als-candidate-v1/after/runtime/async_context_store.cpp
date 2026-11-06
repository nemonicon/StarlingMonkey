// SOURCE-ONLY DRAFT. Native store core; Promise/task wiring remains separate.
#include "async_context_store.h"
#include "node_tick_queue.h"
#include "js/CallAndConstruct.h"
#include "js/Object.h"
#include "js/Promise.h"
#include "js/Realm.h"
#include "jsapi.h"

namespace core::async_context {
using namespace JS;
namespace {
const JSClass StateClass = {"NodeALSState", JSCLASS_HAS_RESERVED_SLOTS(1), nullptr};
const JSClass NodeClass = {"NodeALSBinding", JSCLASS_HAS_RESERVED_SLOTS(3), nullptr};
// Slot1 owns the request root. Every captured child carries this owner, so
// Promise jobs re-enter the right root even after the initial JS call returns.
const JSClass ResourceClass = {"NodeALSResource", JSCLASS_HAS_RESERVED_SLOTS(2), nullptr};
bool state_ok(JSContext* cx, HandleObject state) {
  if (state && JS::GetClass(state) == &StateClass) return true;
  return InternalTickQueue::fail(cx, JSEXN_TYPEERR, "ERR_INVALID_ARG_TYPE",
                                  "Invalid AsyncLocalStorage receiver");
}
bool limit(JSContext* cx) {
  return InternalTickQueue::fail(cx, JSEXN_RANGEERR,
      "ERR_SM_NODE_ASYNC_CONTEXT_LIMIT", "Async context binding limit exceeded");
}
} // namespace

bool ResourceStore::is_resource(JSObject* object) {
  return object && JS::GetClass(object) == &ResourceClass;
}
bool ResourceStore::initialize(JSContext* cx) {
  MOZ_RELEASE_ASSERT(!current_ && !root_);
  RootedObject empty(cx);
  if (!fresh_root(cx, &empty)) return false;
  root_ = empty;
  current_ = empty;
  return true;
}
bool ResourceStore::fresh_root(JSContext* cx, MutableHandleObject result) const {
  RootedObject resource(cx, JS_NewObject(cx, &ResourceClass));
  if (!resource) return false;
  JS::SetReservedSlot(resource, 0, NullValue());
  JS::SetReservedSlot(resource, 1, ObjectValue(*resource));
  result.set(resource);
  return true;
}
bool ResourceStore::create_state(JSContext* cx, MutableHandleObject result) {
  RootedObject state(cx, JS_NewObject(cx, &StateClass));
  if (!state) return false;
  JS::SetReservedSlot(state, 0, BooleanValue(false));
  result.set(state);
  return true;
}
bool ResourceStore::enabled(JSContext* cx, HandleObject state, bool* result) const {
  if (!state_ok(cx, state)) return false;
  *result = JS::GetReservedSlot(state, 0).toBoolean();
  return true;
}
bool ResourceStore::set_enabled(JSContext* cx, HandleObject state, bool enabled) {
  if (!state_ok(cx, state)) return false;
  JS::SetReservedSlot(state, 0, BooleanValue(enabled));
  return true;
}
bool ResourceStore::get(JSContext* cx, HandleObject state, bool raw,
                        MutableHandleValue result) const {
  if (!state_ok(cx, state)) return false;
  if (!raw && !JS::GetReservedSlot(state, 0).toBoolean()) {
    result.setUndefined();
    return true;
  }
  const Value* head = &JS::GetReservedSlot(current_, 0);
  while (head->isObject()) {
    JSObject* node = &head->toObject();
    if (&JS::GetReservedSlot(node, 0).toObject() == state) {
      result.set(JS::GetReservedSlot(node, 1));
      return true;
    }
    head = &JS::GetReservedSlot(node, 2);
  }
  result.setUndefined();
  return true;
}
bool ResourceStore::set(JSContext* cx, HandleObject state, HandleValue value) {
  if (!state_ok(cx, state)) return false;
  const Value* head = &JS::GetReservedSlot(current_, 0);
  size_t count = 0;
  while (head->isObject()) {
    JSObject* node = &head->toObject();
    if (&JS::GetReservedSlot(node, 0).toObject() == state) {
      // Existing binding restoration cannot allocate or replace an exception.
      JS::SetReservedSlot(node, 1, value);
      return true;
    }
    head = &JS::GetReservedSlot(node, 2);
    ++count;
  }
  if (count >= MaxBindingsPerResource) return limit(cx);
  RootedObject node(cx, JS_NewObject(cx, &NodeClass));
  if (!node) return false;
  JS::SetReservedSlot(node, 0, ObjectValue(*state));
  JS::SetReservedSlot(node, 1, value);
  JS::SetReservedSlot(node, 2, JS::GetReservedSlot(current_, 0));
  JS::SetReservedSlot(current_, 0, ObjectValue(*node));
  return true;
}
bool ResourceStore::clone(JSContext* cx, HandleObject source, bool enabled_only,
                          MutableHandleObject result) const {
  MOZ_RELEASE_ASSERT(is_resource(source));
  JS::Realm* realm = JS::GetCurrentRealmOrNull(cx);
  if (!realm || JS::GetCompartmentForRealm(realm) !=
      JS::GetCompartment(source))
    return InternalTickQueue::fail(cx, JSEXN_TYPEERR, "ERR_SM_NODE_UNSUPPORTED",
        "Cross-compartment async resources are outside this profile");
  RootedObject resource(cx, JS_NewObject(cx, &ResourceClass));
  if (!resource) return false;
  RootedObject copied(cx);
  RootedValue head(cx, JS::GetReservedSlot(source, 0));
  size_t count = 0;
  while (head.isObject()) {
    RootedObject node(cx, &head.toObject());
    RootedObject state(cx, &JS::GetReservedSlot(node, 0).toObject());
    if (++count > MaxBindingsPerResource) return limit(cx);
    if (!enabled_only || JS::GetReservedSlot(state, 0).toBoolean()) {
      RootedObject copy(cx, JS_NewObject(cx, &NodeClass));
      if (!copy) return false;
      JS::SetReservedSlot(copy, 0, ObjectValue(*state));
      JS::SetReservedSlot(copy, 1, JS::GetReservedSlot(node, 1));
      JS::SetReservedSlot(copy, 2, ObjectOrNullValue(copied));
      copied = copy;
    }
    head = JS::GetReservedSlot(node, 2);
  }
  JS::SetReservedSlot(resource, 0, ObjectOrNullValue(copied));
  JS::SetReservedSlot(resource, 1, JS::GetReservedSlot(source, 1));
  result.set(resource);
  return true;
}
ResourceStore::Scope::Scope(JSContext* cx, ResourceStore& store,
                           HandleObject resource)
    : store_(store), previous_(cx, store.current_), previous_root_(cx, store.root_) {
  MOZ_RELEASE_ASSERT(ResourceStore::is_resource(resource));
  const Value& owner = JS::GetReservedSlot(resource, 1);
  MOZ_RELEASE_ASSERT(owner.isObject() && ResourceStore::is_resource(&owner.toObject()));
  store_.root_ = &owner.toObject();
  store_.current_ = resource;
}
ResourceStore::Scope::~Scope() {
  store_.current_ = previous_;
  store_.root_ = previous_root_;
}
bool ResourceStore::invoke(JSContext* cx, HandleObject resource,
                           HandleValue callback, HandleValue receiver,
                           const HandleValueArray& arguments,
                           MutableHandleValue result) {
  if (!is_resource(resource)) return InternalTickQueue::fail(cx, JSEXN_TYPEERR,
      "ERR_INVALID_ARG_TYPE", "Invalid captured async resource");
  if (callback.isObject() &&
      (!JS::GetObjectRealmOrNull(&callback.toObject()) ||
       JS::GetCompartment(&callback.toObject()) != JS::GetCompartment(resource)))
    return InternalTickQueue::fail(cx, JSEXN_TYPEERR, "ERR_SM_NODE_UNSUPPORTED",
        "Cross-compartment async callbacks are outside this profile");
  Scope scope(cx, *this, resource);
  return JS::Call(cx, receiver, callback, arguments, result);
}
JSObject* ResourceStore::promise_metadata(JSContext* cx, HandleObject object,
                                         js::AutoEnterOOMUnsafeRegion& oom) const {
  if (!JS::IsPromiseObject(object)) return nullptr;
  if (JS::GetCompartment(object) != JS::GetCompartment(current_)) return nullptr;
  RootedObject resource(cx);
  if (!capture(cx, &resource)) oom.crash("AsyncLocalStorage Promise metadata allocation");
  return resource;
}
} // namespace core::async_context
