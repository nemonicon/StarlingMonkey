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
