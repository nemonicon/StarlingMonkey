// SOURCE-ONLY DRAFT. Not installed or compiled by any current profile.
#ifndef STARLING_ASYNC_CONTEXT_STORE_H
#define STARLING_ASYNC_CONTEXT_STORE_H
#include "js/RootingAPI.h"
#include "js/TypeDecls.h"
#include "js/ValueArray.h"
#include "jsfriendapi.h"
#include <cstddef>

namespace core::async_context {

// An execution resource owns a mutable list. Child capture copies enabled
// bindings, preserving store VALUE identity without sharing mutable nodes.
class ResourceStore {
  JS::PersistentRootedObject current_;
  JS::PersistentRootedObject root_;
  JS::PersistentRootedObject server_;
public:
  static constexpr size_t MaxBindingsPerResource = 256;
  explicit ResourceStore(JSContext* cx) : current_(cx), root_(cx), server_(cx) {}
  bool initialize(JSContext* cx);
  bool fresh_root(JSContext* cx, JS::MutableHandleObject result) const;
  bool ready() const { return current_.get() != nullptr; }
  JS::HandleObject current() const { return current_; }
  JS::HandleObject root() const { return root_; }
  // Stable infrastructure owner, never derived from the calling request.
  JS::HandleObject server() const { return server_; }
  bool at_server_boundary() const { return current_.get() == server_.get() && root_.get() == server_.get(); }
  bool create_state(JSContext* cx, JS::MutableHandleObject result);
  bool enabled(JSContext* cx, JS::HandleObject state, bool* result) const;
  bool set_enabled(JSContext* cx, JS::HandleObject state, bool enabled);
  bool get(JSContext* cx, JS::HandleObject state, bool raw,
           JS::MutableHandleValue result) const;
  bool set(JSContext* cx, JS::HandleObject state, JS::HandleValue value);
  bool clone(JSContext* cx, JS::HandleObject source, bool enabled_only,
             JS::MutableHandleObject result) const;
  bool capture(JSContext* cx, JS::MutableHandleObject result) const {
    return clone(cx, current_, true, result);
  }
  bool invoke(JSContext* cx, JS::HandleObject resource,
              JS::HandleValue callback, JS::HandleValue receiver,
              const JS::HandleValueArray& arguments,
              JS::MutableHandleValue result);
  // SM147's builder/table policy is explicitly fatal on allocation failure.
  // This is not a fallible Promise hook or an OOM safety claim.
  JSObject* promise_metadata(JSContext* cx, JS::HandleObject object,
                            js::AutoEnterOOMUnsafeRegion& oom) const;
  static bool is_resource(JSObject* object);

  class Scope {
    ResourceStore& store_;
    JS::RootedObject previous_;
    JS::RootedObject previous_root_;
  public:
    Scope(JSContext* cx, ResourceStore& store, JS::HandleObject resource);
    ~Scope();
    Scope(const Scope&) = delete;
    Scope& operator=(const Scope&) = delete;
  };
};
} // namespace core::async_context
#endif
