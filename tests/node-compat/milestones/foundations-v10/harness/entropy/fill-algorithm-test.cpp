// Meaningful failure-path tests for the staged fill algorithm. These mocks are
// ordinary local C++ callbacks, not guest imports or external host services.
#include "fill-algorithm.h"
#include <cassert>
#include <cstdio>
#include <memory>
#include <vector>

struct Source {
  size_t calls = 0;
  size_t fail_at = 0;
  size_t short_at = 0;
  size_t live_temps = 0;
  size_t max_request = 0;
};

static int copy_chunk(void *opaque, unsigned char *destination, size_t length) {
  auto &source = *static_cast<Source *>(opaque);
  ++source.calls;
  if (length > source.max_request) source.max_request = length;
  if (source.calls == source.fail_at) return 0;
  ++source.live_temps;
  struct Decrement { Source &source; ~Decrement() { --source.live_temps; } } decrement{source};
  std::unique_ptr<unsigned char[]> bytes(new unsigned char[length]);
  const size_t actual = source.calls == source.short_at ? length - 1 : length;
  if (actual != length) return 0;
  for (size_t i = 0; i < length; ++i) bytes[i] = static_cast<unsigned char>((i + source.calls * 17) & 255);
  for (size_t i = 0; i < length; ++i) destination[i] = bytes[i];
  return 1;
}

int main() {
  size_t cases = 0;
  for (size_t length : {size_t(0), size_t(1), size_t(65535), size_t(65536), size_t(65537), size_t(131089)}) {
    Source source;
    std::vector<unsigned char> output(length, 0xaa);
    assert(sm_entropy_fill_chunks(output.data(), output.size(), copy_chunk, &source) == 1);
    assert(source.calls == (length + 65535) / 65536);
    assert(source.max_request <= 65536);
    assert(source.live_temps == 0);
    for (size_t i = 0; i < length; ++i) {
      const size_t call = i / 65536 + 1;
      assert(output[i] == static_cast<unsigned char>(((i % 65536) + call * 17) & 255));
    }
    ++cases;
  }
  for (size_t failure : {size_t(1), size_t(2), size_t(3)}) {
    for (bool short_result : {false, true}) {
      Source source;
      if (short_result) source.short_at = failure; else source.fail_at = failure;
      std::vector<unsigned char> output(131089, 0xaa);
      assert(sm_entropy_fill_chunks(output.data(), output.size(), copy_chunk, &source) == 0);
      assert(source.calls == failure && source.live_temps == 0);
      for (auto byte : output) assert(byte == 0);
      ++cases;
    }
  }
  Source source;
  assert(sm_entropy_fill_chunks(nullptr, 4, copy_chunk, &source) == 0 && source.calls == 0); ++cases;
  assert(sm_entropy_fill_chunks(nullptr, 0, copy_chunk, &source) == 1 && source.calls == 0); ++cases;
  std::puts("{\"algorithmCases\":14,\"passed\":true,\"productionBridgeCompiled\":false}");
  assert(cases == 14);
}
