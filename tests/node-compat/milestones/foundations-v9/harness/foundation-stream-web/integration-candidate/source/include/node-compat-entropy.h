// Private guest policy for the opt-in Node compatibility profile. These are
// ordinary guest symbols, not Component Model imports/exports or content APIs.
#ifndef STARLING_NODE_COMPAT_ENTROPY_H
#define STARLING_NODE_COMPAT_ENTROPY_H

#include "js/TypeDecls.h"
#include <cstddef>
#include <cstdint>

namespace builtins::node_compat::entropy {
enum class Status { Disabled, BeforeRuntime, Ready };

Status status();
void begin_engine(bool pre_initialize);
bool require(JSContext *cx, const char *operation);
bool invalid_result(JSContext *cx, const char *operation);

inline void clear(uint8_t *bytes, size_t length) {
  volatile uint8_t *cursor = bytes;
  while (length-- != 0) *cursor++ = 0;
}
} // namespace builtins::node_compat::entropy

extern "C" void sm_node_enter_deployed_execution();
extern "C" int sm_node_secure_random_fill(unsigned char *destination, size_t length);

#endif
