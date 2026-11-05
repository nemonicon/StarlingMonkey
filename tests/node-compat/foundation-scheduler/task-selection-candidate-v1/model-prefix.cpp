// Standalone model substitutes only task ownership and standard host polling.
// Actual select function bodies are inserted verbatim by check-source.py.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <vector>
template<class T> using RefPtr = std::shared_ptr<T>;
constexpr int INVALID_POLLABLE_HANDLE = -1;
constexpr int IMMEDIATE_TASK_HANDLE = -2;
namespace host_api { struct Pollable {}; }
template<class T> struct WASIHandle { using Borrowed = int; };
struct wasi_clocks_monotonic_clock_own_pollable_t { int __handle; };
static std::optional<wasi_clocks_monotonic_clock_own_pollable_t> immediately_ready;
static std::vector<std::vector<int>> polls;
static std::vector<size_t> ready;
static int subscriptions = 0;
static auto wasi_clocks_monotonic_clock_subscribe_duration(int duration) {
  assert(duration == 0); ++subscriptions;
  return wasi_clocks_monotonic_clock_own_pollable_t{77};
}
static size_t poll_handles(std::vector<int> handles) {
  polls.push_back(handles);
  if (handles.empty()) throw std::logic_error("instrumented-empty-poll");
  assert(!ready.empty());
  for (size_t index : ready) assert(index < handles.size());
  return *std::min_element(ready.begin(), ready.end());
}
namespace api {
struct AsyncTask {
  int handle;
  explicit AsyncTask(int value): handle(value) {}
  int id() { return handle; }
  static std::optional<size_t> select(std::vector<RefPtr<AsyncTask>>& tasks);
};
struct LegacyAsyncTask {
  int handle;
  explicit LegacyAsyncTask(int value): handle(value) {}
  int id() { return handle; }
  static size_t select(std::vector<RefPtr<LegacyAsyncTask>>& tasks);
};
}
