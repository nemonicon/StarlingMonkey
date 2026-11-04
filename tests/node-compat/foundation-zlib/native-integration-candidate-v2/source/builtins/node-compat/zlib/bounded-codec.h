// Isolated proposal: not installed, linked into an engine, or Node support.
// This native-only kernel has no JS pointers, callbacks, host calls or handles.
#ifndef NODE_COMPAT_BOUNDED_ZLIB_TEMPLATE_H
#define NODE_COMPAT_BOUNDED_ZLIB_TEMPLATE_H

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <span>
#include <utility>
#include <zlib.h>

namespace node_compat_zlib_candidate {

constexpr size_t MaxInput = 1024 * 1024;
constexpr size_t MaxOutput = 16 * 1024 * 1024;
constexpr size_t ChunkSize = 16 * 1024;

enum class Format { Zlib, Gzip, Raw };
enum class Status {
  Ok, InputLimit, OutputLimit, OutOfMemory, InvalidData, IncompleteData,
  DictionaryRequired, TrailingData, InternalError,
};

// malloc/realloc/free form one allocator family; never transfer this pointer to
// JS's ArrayBuffer adoption APIs. A future guest wrapper copies into a rooted
// JS-owned Uint8Array, then destroys this native owner.
class Bytes {
  uint8_t *data_ = nullptr;
  size_t size_ = 0;
  size_t capacity_ = 0;

public:
  Bytes() = default;
  Bytes(const Bytes &) = delete;
  Bytes &operator=(const Bytes &) = delete;
  Bytes(Bytes &&other) noexcept
      : data_(std::exchange(other.data_, nullptr)),
        size_(std::exchange(other.size_, 0)),
        capacity_(std::exchange(other.capacity_, 0)) {}
  Bytes &operator=(Bytes &&other) noexcept {
    if (this != &other) {
      std::free(data_);
      data_ = std::exchange(other.data_, nullptr);
      size_ = std::exchange(other.size_, 0);
      capacity_ = std::exchange(other.capacity_, 0);
    }
    return *this;
  }
  ~Bytes() { std::free(data_); }
  std::span<const uint8_t> view() const { return {data_, size_}; }
  Status append(std::span<const uint8_t> input, size_t limit) {
    if (size_ > limit || input.size() > limit - size_) return Status::OutputLimit;
    const size_t needed = size_ + input.size();
    if (needed > capacity_) {
      const size_t doubled = capacity_ > limit / 2 ? limit : capacity_ * 2;
      const size_t capacity = std::max(needed, std::max(std::min(ChunkSize, limit), doubled));
      void *replacement = std::realloc(data_, capacity);
      if (!replacement) return Status::OutOfMemory;
      data_ = static_cast<uint8_t *>(replacement);
      capacity_ = capacity;
    }
    if (!input.empty()) std::memcpy(data_ + size_, input.data(), input.size());
    size_ = needed;
    return Status::Ok;
  }
};

struct Result {
  Status status = Status::InternalError;
  // Diagnostic integer only; a wrapper must not return partial bytes on error.
  int zlib_status = Z_OK;
  Bytes output;
};

class Stream {
  bool initialized_ = false;
  bool encode_;

public:
  z_stream value{};
  explicit Stream(bool encode) : encode_(encode) {}
  Stream(const Stream &) = delete;
  Stream &operator=(const Stream &) = delete;
  ~Stream() {
    if (initialized_) {
      if (encode_) deflateEnd(&value);
      else inflateEnd(&value);
    }
  }
  int init(Format format) {
    const int bits = format == Format::Gzip ? 31 : format == Format::Raw ? -15 : 15;
    const int status = encode_ ? deflateInit2(&value, Z_DEFAULT_COMPRESSION,
        Z_DEFLATED, bits, 8, Z_DEFAULT_STRATEGY) : inflateInit2(&value, bits);
    initialized_ = status == Z_OK;
    return status;
  }
};

// Complete-buffer operation, selected defaults only. Decoding is deliberately
// strict: exactly one member and no trailing bytes. This differs from Node's
// gunzip concatenation and some trailing-data behavior. It is an internal
// candidate, not an existing public Node overload.
inline Result run(std::span<const uint8_t> input, Format format, bool encode,
                  size_t output_limit = MaxOutput) {
  Result result;
  if (input.size() > MaxInput || input.size() > std::numeric_limits<uInt>::max()) {
    result.status = Status::InputLimit;
    return result;
  }
  if (output_limit > MaxOutput) {
    result.status = Status::OutputLimit;
    return result;
  }
  Stream stream(encode);
  result.zlib_status = stream.init(format);
  if (result.zlib_status != Z_OK) {
    result.status = result.zlib_status == Z_MEM_ERROR ? Status::OutOfMemory : Status::InternalError;
    return result;
  }
  // zlib's historical signature is mutable; neither deflate nor inflate
  // modifies these input bytes. The caller owns them throughout this call.
  stream.value.next_in = input.empty() ? nullptr : const_cast<uint8_t *>(input.data());
  stream.value.avail_in = static_cast<uInt>(input.size());
  std::array<uint8_t, ChunkSize> chunk;
  for (;;) {
    const uInt before = stream.value.avail_in;
    stream.value.next_out = chunk.data();
    stream.value.avail_out = static_cast<uInt>(chunk.size());
    result.zlib_status = encode ? deflate(&stream.value, Z_FINISH)
                                : inflate(&stream.value, Z_NO_FLUSH);
    if (result.zlib_status != Z_OK && result.zlib_status != Z_STREAM_END &&
        result.zlib_status != Z_BUF_ERROR) {
      result.status = result.zlib_status == Z_MEM_ERROR ? Status::OutOfMemory :
          result.zlib_status == Z_NEED_DICT ? Status::DictionaryRequired :
          result.zlib_status == Z_DATA_ERROR ? Status::InvalidData : Status::InternalError;
      return result;
    }
    const size_t written = chunk.size() - stream.value.avail_out;
    result.status = result.output.append({chunk.data(), written}, output_limit);
    if (result.status != Status::Ok) return result;
    if (result.zlib_status == Z_STREAM_END) {
      result.status = stream.value.avail_in == 0 ? Status::Ok : Status::TrailingData;
      return result;
    }
    // Progress, rather than output fullness, determines whether another call
    // is possible. Exhausted input without STREAM_END is truncated input.
    if (written == 0 && stream.value.avail_in == before) {
      result.status = encode ? Status::InternalError : Status::IncompleteData;
      return result;
    }
  }
}
} // namespace node_compat_zlib_candidate
#endif
