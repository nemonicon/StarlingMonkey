#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>

#include "builtin.h"
#include "extension-api.h"
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
#include "clock-lifecycle-diagnostics.h"
#endif
#include "config-parser.h"
#include "host_api.h"
#include "wasi/api.h"
#include "wasi/libc-environ.h"
#include "wizer.h"
#ifdef MEM_STATS
#include <string>
#endif

api::Engine *engine;

api::Engine* initialize(std::vector<std::string_view> args) {
  auto config_parser = starling::ConfigParser();
  config_parser.apply_env()->apply_args(std::move(args));
  return new api::Engine(config_parser.take());
}

static api::Engine *ENGINE = nullptr;

__attribute__((weak))
int main(int argc, const char *argv[]) {
  MOZ_ASSERT_UNREACHABLE("main() should not be called");
}

static uint64_t mono_clock_offset = 0;
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
namespace {
diagnostics::clock_lifecycle::NativeClockState diagnostic_native_clock;
void diagnostic_clock_increment(std::uint64_t& value) {
  if (value == std::numeric_limits<std::uint64_t>::max()) diagnostic_native_clock.overflow = true;
  else ++value;
}
}
namespace diagnostics::clock_lifecycle {
NativeClockState native_clock_state() {
  auto result = diagnostic_native_clock;
  result.offsetNs = mono_clock_offset; // SAME TU, actual native static, no clock call
  return result;
}
}
#endif
#define NSECS_PER_SEC 1000000000;

// This overrides wasi-libc's weakly linked implementation of clock_gettime to ensure that
// monotonic clocks really are monotonic, even across resumptions of wizer snapshots.
int clock_gettime(clockid_t clock, timespec * ts) {
  __wasi_clockid_t clock_id = 0;
  if (clock == CLOCK_REALTIME) {
    clock_id = __WASI_CLOCKID_REALTIME;
  } else if (clock == CLOCK_MONOTONIC) {
    clock_id = __WASI_CLOCKID_MONOTONIC;
  } else {
    return EINVAL;
  }
  __wasi_timestamp_t t = 0;
  auto errno = __wasi_clock_time_get(clock_id, 1, &t);
  if (errno != 0) {
    return EINVAL;
  }
  if (clock == CLOCK_MONOTONIC) {
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
    diagnostic_clock_increment(diagnostic_native_clock.monotonicCalls);
    diagnostic_native_clock.monotonicSamplePresent = true;
    diagnostic_native_clock.lastMonotonicRawNs = t;
    diagnostic_native_clock.lastOffsetAppliedNs = mono_clock_offset;
    if (t > std::numeric_limits<std::uint64_t>::max() - mono_clock_offset)
      diagnostic_native_clock.adjustmentOverflow = true;
    diagnostic_native_clock.lastMonotonicAdjustedNs = t + mono_clock_offset;
#endif
    t += mono_clock_offset;
  }
  ts->tv_sec = t / NSECS_PER_SEC;
  ts->tv_nsec = t % NSECS_PER_SEC;
  return 0;
}

void wizen() {
  std::string args;
  std::getline(std::cin, args);
  auto config_parser = starling::ConfigParser();
  config_parser.apply_env()->apply_args(args);
  auto config = config_parser.take();
  config->pre_initialize = true;
  ENGINE = new api::Engine(std::move(config));
  ENGINE->finish_pre_initialization();

  // Ensure that the monotonic clock is always increasing, even across multiple resumptions.
  __wasi_timestamp_t t = 0;
  MOZ_RELEASE_ASSERT(!__wasi_clock_time_get(__WASI_CLOCKID_MONOTONIC, 1, &t));
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  const auto diagnostic_offset_before = mono_clock_offset;
#endif
  mono_clock_offset = std::max(mono_clock_offset, t);
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  diagnostic_clock_increment(diagnostic_native_clock.wizenTransitions);
  diagnostic_native_clock.wizenSamplePresent = true;
  diagnostic_native_clock.lastWizenRawNs = t;
  diagnostic_native_clock.lastWizenOffsetBeforeNs = diagnostic_offset_before;
  diagnostic_native_clock.lastWizenOffsetAfterNs = mono_clock_offset;
#endif
  __wasilibc_deinitialize_environ();
}

WIZER_INIT(wizen);

/**
 * The main entry function for the runtime.
 *
 * The runtime will be initialized with a configuration derived in the following way:
 * 1. If a command line is provided, it will be parsed and used.
 * 2. Otherwise, the env var `STARLINGMONKEY_CONFIG` will be split into a command line and used.
 * 3. Otherwise, a default configuration is used. In particular, the runtime will attempt to
 *    load the file `./index.js` and run it as the top-level module script.
 */
extern "C" bool exports_wasi_cli_run_run() {
  auto arg_strings = host_api::environment_get_arguments();
  std::vector<std::string_view> args;
  args.reserve(arg_strings.size());
  for (auto& arg : arg_strings) { args.push_back(arg);
}

  auto config_parser = starling::ConfigParser();
  config_parser.apply_env()->apply_args(args);
  ENGINE = new api::Engine(config_parser.take());
  return true;
}

/**
 * Initialize the runtime with the configuration provided via an environment variable.
 *
 * This initializer checks for the environment variable `STARLINGMONKEY_CONFIG` and parses
 * it as a command line arguments string. The variable not being set is treated as an empty
 * command line.
 */
extern "C" bool init_from_environment() {
  auto config_parser = starling::ConfigParser();
  config_parser.apply_env();
  ENGINE = new api::Engine(config_parser.take());
  return true;
}
