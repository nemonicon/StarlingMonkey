// Staged guest-only algorithm, compiled by the host-side fault tests below.
// No production file includes this header yet.
#ifndef SM_PROFILE_STAGED_ENTROPY_FILL_H
#define SM_PROFILE_STAGED_ENTROPY_FILL_H
#include <stddef.h>

typedef int (*sm_entropy_copy_chunk)(void *context, unsigned char *destination, size_t length);

static void sm_entropy_clear(unsigned char *destination, size_t length) {
  // Do not permit dead-store elimination of failure cleanup.
  volatile unsigned char *bytes = destination;
  while (length-- != 0) *bytes++ = 0;
}

// The callback owns/frees its temporary buffer before returning. It returns1
// only after copying exactly length bytes. Its output is invalid on failure.
// Caller supplies a valid native output span; no JS data pointer is retained.
static int sm_entropy_fill_chunks(unsigned char *destination, size_t length,
                                  sm_entropy_copy_chunk copy, void *context) {
  const size_t chunk_limit = 65536;
  if (length == 0) return 1;
  if (!destination || !copy) return 0;
  size_t offset = 0;
  while (offset < length) {
    const size_t remaining = length - offset;
    const size_t chunk = remaining < chunk_limit ? remaining : chunk_limit;
    if (copy(context, destination + offset, chunk) != 1) {
      sm_entropy_clear(destination, length);
      return 0;
    }
    offset += chunk;
  }
  return 1;
}
#endif
