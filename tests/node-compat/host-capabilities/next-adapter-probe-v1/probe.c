// Actual guest deployment probe. Not JavaScript, a Node API, or the Next app.
#include "bindings.h"
#include <wasi/api.h>
#include <stdlib.h>
#include <string.h>

// Avoid libc's Preview1 proc_exit dependency. All probe invariants fail closed.
_Noreturn void abort(void) { __builtin_trap(); }

static uint32_t counter;
static char output[16384];
static size_t used;
static void raw(const char *text) {
  size_t length = strlen(text);
  if (length > sizeof(output) - used) abort();
  memcpy(output + used, text, length); used += length;
}
static void number(uint64_t value) {
  char digits[21]; size_t count = 0;
  do { digits[count++] = (char)('0' + value % 10); value /= 10; } while (value);
  while (count) { char part[2] = {digits[--count], 0}; raw(part); }
}
static void boolean(bool value) { raw(value ? "true" : "false"); }
static void quoted(const uint8_t *bytes, size_t length) {
  static const char hex[] = "0123456789abcdef";
  raw("\"");
  for (size_t i = 0; i < length; ++i) {
    uint8_t c = bytes[i];
    if (c == '"' || c == '\\') { char part[3] = {'\\', (char)c, 0}; raw(part); }
    else if (c < 32) { char part[7] = {'\\','u','0','0',hex[c >> 4],hex[c & 15],0}; raw(part); }
    else { char part[2] = {(char)c, 0}; raw(part); }
  }
  raw("\"");
}
static bindings_string_t string(const char *text) {
  return (bindings_string_t){(uint8_t *)text, strlen(text)};
}
static bool equals(bindings_string_t text, const char *expected) {
  return text.len == strlen(expected) && !memcmp(text.ptr, expected, text.len);
}

static void environment(void) {
  bindings_list_tuple2_string_string_t values;
  wasi_cli_environment_get_environment(&values);
  raw(",\"environmentMarker\":"); bool found = false;
  for (size_t i = 0; i < values.len; ++i) if (equals(values.ptr[i].f0, "STARLING_NEXT_PROBE")) {
    quoted(values.ptr[i].f1.ptr, values.ptr[i].f1.len); found = true; break;
  }
  if (!found) raw("null");
  bindings_list_tuple2_string_string_free(&values);
  bindings_list_string_t args; wasi_cli_environment_get_arguments(&args);
  raw(",\"argumentCount\":"); number(args.len); bindings_list_string_free(&args);
  bindings_string_t cwd;
  raw(",\"initialCwd\":");
  if (wasi_cli_environment_initial_cwd(&cwd)) { quoted(cwd.ptr, cwd.len); bindings_string_free(&cwd); }
  else raw("null");
}

static void app_read(wasi_filesystem_types_borrow_descriptor_t dir) {
  bindings_string_t path = string("message.txt");
  wasi_filesystem_types_own_descriptor_t file;
  wasi_filesystem_types_error_code_t error = 255;
  bool opened = wasi_filesystem_types_method_descriptor_open_at(dir, 0, &path, 0,
    WASI_FILESYSTEM_TYPES_DESCRIPTOR_FLAGS_READ, &file, &error);
  bool matched = false;
  if (opened) {
    bindings_tuple2_list_u8_bool_t value;
    if (wasi_filesystem_types_method_descriptor_read(wasi_filesystem_types_borrow_descriptor(file), 64, 0, &value, &error)) {
      const char *expected = "app-readable\n";
      matched = value.f0.len == strlen(expected) && !memcmp(value.f0.ptr, expected, value.f0.len);
      bindings_list_u8_free(&value.f0);
    }
    wasi_filesystem_types_descriptor_drop_own(file);
  }
  raw(",\"readFixture\":"); boolean(matched);
  path = string("app-write-probe.tmp");
  bool writable = wasi_filesystem_types_method_descriptor_open_at(dir, 0, &path,
    WASI_FILESYSTEM_TYPES_OPEN_FLAGS_CREATE | WASI_FILESYSTEM_TYPES_OPEN_FLAGS_EXCLUSIVE,
    WASI_FILESYSTEM_TYPES_DESCRIPTOR_FLAGS_WRITE, &file, &error);
  raw(",\"createAllowed\":"); boolean(writable);
  raw(",\"createError\":"); if (writable) raw("null"); else number(error);
  if (writable) {
    wasi_filesystem_types_descriptor_drop_own(file);
    if (!wasi_filesystem_types_method_descriptor_unlink_file_at(dir, &path, &error)) abort();
  }
}

static void cache_io(wasi_filesystem_types_borrow_descriptor_t dir) {
  bindings_string_t tmp = string("probe.tmp"), link = string("probe.link"), renamed = string("probe.renamed");
  wasi_filesystem_types_error_code_t error = 255;
  wasi_filesystem_types_own_descriptor_t file;
  bool opened = wasi_filesystem_types_method_descriptor_open_at(dir, 0, &tmp,
    WASI_FILESYSTEM_TYPES_OPEN_FLAGS_CREATE | WASI_FILESYSTEM_TYPES_OPEN_FLAGS_TRUNCATE,
    WASI_FILESYSTEM_TYPES_DESCRIPTOR_FLAGS_READ | WASI_FILESYSTEM_TYPES_DESCRIPTOR_FLAGS_WRITE, &file, &error);
  bool wrote = false, read = false;
  if (opened) {
    bindings_list_u8_t bytes = {(uint8_t *)"cache-data\n", 11}; uint64_t count;
    wrote = wasi_filesystem_types_method_descriptor_write(wasi_filesystem_types_borrow_descriptor(file), &bytes, 0, &count, &error) && count == bytes.len;
    bindings_tuple2_list_u8_bool_t value;
    if (wasi_filesystem_types_method_descriptor_read(wasi_filesystem_types_borrow_descriptor(file), 64, 0, &value, &error)) {
      read = value.f0.len == bytes.len && !memcmp(value.f0.ptr, bytes.ptr, bytes.len);
      bindings_list_u8_free(&value.f0);
    }
    wasi_filesystem_types_descriptor_drop_own(file);
  }
  bool linked = opened && wasi_filesystem_types_method_descriptor_link_at(dir, 0, &tmp, dir, &link, &error);
  bool second = false; uint8_t second_error = 255;
  if (linked) second = wasi_filesystem_types_method_descriptor_link_at(dir, 0, &tmp, dir, &link, &second_error);
  bool moved = linked && wasi_filesystem_types_method_descriptor_rename_at(dir, &link, dir, &renamed, &error);
  bool unlinked = true;
  if (linked) unlinked = wasi_filesystem_types_method_descriptor_unlink_file_at(dir, moved ? &renamed : &link, &error);
  if (opened) unlinked = wasi_filesystem_types_method_descriptor_unlink_file_at(dir, &tmp, &error) && unlinked;
  raw(",\"create\":"); boolean(opened); raw(",\"write\":"); boolean(wrote); raw(",\"read\":"); boolean(read);
  raw(",\"link\":"); boolean(linked); raw(",\"secondLink\":"); boolean(second);
  raw(",\"secondLinkError\":"); if (linked && !second) number(second_error); else raw("null");
  raw(",\"rename\":"); boolean(moved); raw(",\"unlink\":"); boolean(unlinked && opened);
}

static void filesystem(void) {
  wasi_filesystem_preopens_list_tuple2_own_descriptor_string_t dirs;
  wasi_filesystem_preopens_get_directories(&dirs);
  if (dirs.len > 32) abort();
  raw(",\"preopens\":[");
  for (size_t i = 0; i < dirs.len; ++i) {
    if (i) raw(","); raw("{\"name\":"); quoted(dirs.ptr[i].f1.ptr, dirs.ptr[i].f1.len);
    wasi_filesystem_types_borrow_descriptor_t dir = wasi_filesystem_types_borrow_descriptor(dirs.ptr[i].f0);
    uint8_t flags = 0, error = 255;
    bool ok = wasi_filesystem_types_method_descriptor_get_flags(dir, &flags, &error);
    raw(",\"descriptorFlags\":"); if (ok) number(flags); else raw("null");
    if (equals(dirs.ptr[i].f1, "/app")) app_read(dir);
    if (equals(dirs.ptr[i].f1, "/cache")) cache_io(dir);
    raw("}");
    wasi_filesystem_types_descriptor_drop_own(dirs.ptr[i].f0);
  }
  raw("]");
  // Generated tuple/list free releases names/array, NOT the owned descriptors.
  wasi_filesystem_preopens_list_tuple2_own_descriptor_string_free(&dirs);
}

// P1 declarations/types are those in pinned SDK30 wasi/wasip1.h, not guessed.
static void preview1_adapter(void) {
  const char stdout_marker[] = "P1_STDOUT_OK\n";
  const char stderr_marker[] = "P1_STDERR_OK\n";
  __wasi_ciovec_t output_vec = {(const uint8_t *)stdout_marker, sizeof(stdout_marker)-1};
  __wasi_size_t stdout_count = 0, stderr_count = 0;
  __wasi_errno_t stdout_error = __wasi_fd_write(1, &output_vec, 1, &stdout_count);
  output_vec.buf = (const uint8_t *)stderr_marker;
  output_vec.buf_len = sizeof(stderr_marker)-1;
  __wasi_errno_t stderr_error = __wasi_fd_write(2, &output_vec, 1, &stderr_count);
  __wasi_fdstat_t stdin_stat;
  __wasi_errno_t stat0_error = __wasi_fd_fdstat_get(0, &stdin_stat);
  uint8_t stdin_byte = 0; __wasi_size_t stdin_count = 99;
  __wasi_iovec_t input_vec = {&stdin_byte, 1};
  __wasi_errno_t read0_error = __wasi_fd_read(0, &input_vec, 1, &stdin_count);
  __wasi_timestamp_t mono = 0, wall = 0, mono_res = 0, wall_res = 0;
  __wasi_errno_t mono_error = __wasi_clock_time_get(__WASI_CLOCKID_MONOTONIC, 1, &mono);
  __wasi_errno_t wall_error = __wasi_clock_time_get(__WASI_CLOCKID_REALTIME, 1, &wall);
  __wasi_errno_t mono_res_error = __wasi_clock_res_get(__WASI_CLOCKID_MONOTONIC, &mono_res);
  __wasi_errno_t wall_res_error = __wasi_clock_res_get(__WASI_CLOCKID_REALTIME, &wall_res);
  uint8_t random[8] = {0}; __wasi_errno_t random_error = __wasi_random_get(random, sizeof(random));
  bool app_found = false, read_equal = false; __wasi_fd_t app = 0, file = 0;
  __wasi_errno_t open_error = __WASI_ERRNO_BADF, read_error = __WASI_ERRNO_BADF, close_error = __WASI_ERRNO_BADF;
  __wasi_size_t file_count = 0;
  for (__wasi_fd_t fd = 3; fd < 64; ++fd) {
    __wasi_prestat_t pre;
    if (__wasi_fd_prestat_get(fd, &pre) != 0 || pre.tag != __WASI_PREOPENTYPE_DIR || pre.u.dir.pr_name_len > 256) continue;
    uint8_t name[256];
    if (__wasi_fd_prestat_dir_name(fd, name, pre.u.dir.pr_name_len) != 0) continue;
    if (pre.u.dir.pr_name_len == 4 && !memcmp(name, "/app", 4)) {app = fd; app_found = true; break;}
  }
  if (app_found) {
    // SDK30's public C helper takes a NUL-terminated path (no path_len argument).
    open_error = __wasi_path_open(app, 0, "message.txt", 0, __WASI_RIGHTS_FD_READ, 0, 0, &file);
    if (open_error == 0) {
      uint8_t data[64]; __wasi_iovec_t vec = {data, sizeof(data)};
      read_error = __wasi_fd_read(file, &vec, 1, &file_count);
      read_equal = read_error == 0 && file_count == strlen("app-readable\n") && !memcmp(data, "app-readable\n", file_count);
      close_error = __wasi_fd_close(file);
    }
  }
  raw(",\"p1\":{\"stdoutError\":"); number(stdout_error);
  raw(",\"stdoutBytes\":"); number(stdout_count);
  raw(",\"stderrError\":"); number(stderr_error);
  raw(",\"stderrBytes\":"); number(stderr_count);
  raw(",\"fdstat0Error\":"); number(stat0_error);
  raw(",\"read0Error\":"); number(read0_error);
  raw(",\"appPreopenFound\":"); boolean(app_found);
  raw(",\"fileOpenError\":"); number(open_error);
  raw(",\"fileReadError\":"); number(read_error);
  raw(",\"fileReadBytes\":"); number(file_count);
  raw(",\"fileReadEqual\":"); boolean(read_equal);
  raw(",\"fileCloseError\":"); number(close_error);
  raw(",\"monotonicError\":"); number(mono_error);
  raw(",\"monotonicNs\":\""); number(mono); raw("\"");
  raw(",\"wallError\":"); number(wall_error);
  raw(",\"wallNs\":\""); number(wall); raw("\"");
  raw(",\"monotonicResolutionError\":"); number(mono_res_error);
  raw(",\"monotonicResolution\":"); number(mono_res);
  raw(",\"wallResolutionError\":"); number(wall_res_error);
  raw(",\"wallResolution\":"); number(wall_res);
  raw(",\"randomError\":"); number(random_error);
  raw(",\"randomHex\":\"");
  for (size_t i = 0; i < sizeof(random); ++i) {
    static const char hex[] = "0123456789abcdef";
    char pair[3] = {hex[random[i] >> 4], hex[random[i] & 15], 0}; raw(pair);
  }
  raw("\"}");
}

void exports_wasi_http_incoming_handler_handle(exports_wasi_http_incoming_handler_own_incoming_request_t request,
  exports_wasi_http_incoming_handler_own_response_outparam_t outparam) {
  used = 0; raw("{\"schemaVersion\":1,\"probe\":\"next-selective-adapter-probe-v1\",\"counter\":"); number(++counter);
  uint64_t before = wasi_clocks_monotonic_clock_now();
  wasi_io_poll_own_pollable_t wait = wasi_clocks_monotonic_clock_subscribe_duration(1000000);
  wasi_io_poll_method_pollable_block(wasi_io_poll_borrow_pollable(wait));
  wasi_io_poll_pollable_drop_own(wait);
  uint64_t after = wasi_clocks_monotonic_clock_now();
  raw(",\"monotonicBefore\":\""); number(before); raw("\",\"monotonicAfter\":\""); number(after); raw("\"");
  wasi_clocks_wall_clock_datetime_t wall; wasi_clocks_wall_clock_now(&wall);
  raw(",\"wallSeconds\":"); number(wall.seconds); raw(",\"wallNanoseconds\":"); number(wall.nanoseconds);
  uint64_t random = wasi_random_random_get_random_u64();
  raw(",\"randomHex\":\"");
  for (int shift = 60; shift >= 0; shift -= 4) { char hex[2] = {"0123456789abcdef"[(random >> shift) & 15], 0}; raw(hex); }
  raw("\""); environment(); filesystem(); preview1_adapter(); raw("}");

  bindings_tuple2_field_name_field_value_t header_values[2] = {
    {string("content-type"), {(uint8_t *)"application/json", 16}},
    {string("cache-control"), {(uint8_t *)"no-store", 8}},
  };
  bindings_list_tuple2_field_name_field_value_t entries = {header_values, 2};
  wasi_http_types_own_fields_t fields; wasi_http_types_header_error_t header_error;
  if (!wasi_http_types_static_fields_from_list(&entries, &fields, &header_error)) abort();
  wasi_http_types_own_outgoing_response_t response = wasi_http_types_constructor_outgoing_response(fields);
  wasi_http_types_own_outgoing_body_t body;
  if (!wasi_http_types_method_outgoing_response_body(wasi_http_types_borrow_outgoing_response(response), &body)) abort();
  wasi_http_types_result_own_outgoing_response_error_code_t result = {.is_err = false, .val.ok = response};
  wasi_http_types_static_response_outparam_set(outparam, &result);
  wasi_http_types_own_output_stream_t stream;
  if (!wasi_http_types_method_outgoing_body_write(wasi_http_types_borrow_outgoing_body(body), &stream)) abort();
  for (size_t position = 0; position < used;) {
    size_t count = used - position; if (count > 4096) count = 4096;
    bindings_list_u8_t part = {(uint8_t *)output + position, count}; wasi_io_streams_stream_error_t error;
    if (!wasi_io_streams_method_output_stream_blocking_write_and_flush(wasi_io_streams_borrow_output_stream(stream), &part, &error)) {
      if (error.tag == WASI_IO_STREAMS_STREAM_ERROR_LAST_OPERATION_FAILED)
        wasi_io_error_error_drop_own(error.val.last_operation_failed);
      wasi_io_streams_stream_error_free(&error); abort();
    }
    position += count;
  }
  wasi_io_streams_output_stream_drop_own(stream);
  wasi_http_types_error_code_t error;
  if (!wasi_http_types_static_outgoing_body_finish(body, NULL, &error)) { wasi_http_types_error_code_free(&error); abort(); }
  wasi_http_types_incoming_request_drop_own(request);
}
