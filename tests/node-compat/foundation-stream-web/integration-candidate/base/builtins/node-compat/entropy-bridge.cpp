#include "host_api.h"
#include "node-compat-entropy.h"
#include <algorithm>
#include <cstring>

extern "C" int sm_node_secure_random_fill(unsigned char *destination, size_t length) {
  using namespace builtins::node_compat::entropy;
  if (status() != Status::Ready) return 0;
  if (length == 0) return 1;
  if (!destination) return 0;
  constexpr size_t ChunkLimit = 65536;
  size_t offset = 0;
  while (offset < length) {
    const size_t chunk = std::min(ChunkLimit, length - offset);
    auto result = host_api::Random::get_bytes(chunk);
    if (result.is_err()) {
      clear(destination, length);
      return 0;
    }
    auto bytes = std::move(result.unwrap());
    if (bytes.size() != chunk || !bytes.begin()) {
      if (bytes.begin()) clear(bytes.begin(), bytes.size());
      clear(destination, length);
      return 0;
    }
    std::memcpy(destination + offset, bytes.begin(), chunk);
    clear(bytes.begin(), bytes.size());
    // HostBytes releases its canonical allocation. Ownership does not transfer
    // to OpenSSL/JS and no seed, pool or RNG resource survives this call.
    offset += chunk;
  }
  return 1;
}
