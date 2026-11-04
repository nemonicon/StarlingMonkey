#include "builtin.h"
#include "node-compat-entropy.h"

namespace builtins::node_compat::entropy {
// Each component instance has its own linear memory and therefore its own
// private barrier. No content-JS setter, environment value or host handle exists.
static bool deployed = false;

Status status() {
#ifdef NODE_COMPAT_ENTROPY_RUNTIME_ONLY
  return deployed ? Status::Ready : Status::BeforeRuntime;
#else
  return Status::Disabled;
#endif
}

void begin_engine(bool pre_initialize) { deployed = !pre_initialize; }

static bool fail(JSContext *cx, const char *operation, const char *code) {
  JS_ReportErrorASCII(cx, "%s: %s", operation, code);
  JS::RootedValue exception(cx);
  if (!JS_GetPendingException(cx, &exception) || !exception.isObject()) return false;
  JS::RootedObject error(cx, &exception.toObject());
  JS::RootedString code_string(cx, JS_NewStringCopyZ(cx, code));
  if (!code_string) return false;
  JS::RootedString operation_string(cx, JS_NewStringCopyZ(cx, operation));
  if (!operation_string) return false;
  JS::RootedValue code_value(cx, JS::StringValue(code_string));
  JS::RootedValue operation_value(cx, JS::StringValue(operation_string));
  JS_ClearPendingException(cx);
  // Preserve any OOM raised while attaching diagnostic fields.
  if (!JS_DefineProperty(cx, error, "code", code_value, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, error, "operation", operation_value, JSPROP_ENUMERATE)) return false;
  JS_SetPendingException(cx, exception);
  return false;
}

bool require(JSContext *cx, const char *operation) {
  const auto state = status();
  if (state == Status::Ready) return true;
  return fail(cx, operation, state == Status::Disabled ? "ERR_SM_ENTROPY_DISABLED"
                                                      : "ERR_SM_ENTROPY_INITIALIZATION");
}

bool invalid_result(JSContext *cx, const char *operation) {
  return fail(cx, operation, "ERR_SM_ENTROPY_HOST_RESULT");
}

void enter_deployed_execution() { deployed = true; }
} // namespace builtins::node_compat::entropy

extern "C" void sm_node_enter_deployed_execution() {
  builtins::node_compat::entropy::enter_deployed_execution();
}
