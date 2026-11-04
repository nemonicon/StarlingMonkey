// Host-only ordinary algorithm test driver. This is not a component fixture.
#include "bounded-zlib.template.h"
#include <iostream>
#include <string>
#include <vector>

int main() {
  using namespace node_compat_zlib_candidate;
  unsigned operation, format;
  size_t limit;
  std::string hex;
  while (std::cin >> operation >> format >> limit >> hex) {
    if (operation > 1 || format > 2 || (hex != "-" && hex.size() % 2)) return 2;
    std::vector<uint8_t> input;
    auto nibble = [](char c) -> int {
      if (c >= '0' && c <= '9') return c - '0';
      if (c >= 'a' && c <= 'f') return c - 'a' + 10;
      return -1;
    };
    if (hex != "-") {
      for (size_t i = 0; i < hex.size(); i += 2) {
        const int a = nibble(hex[i]), b = nibble(hex[i + 1]);
        if (a < 0 || b < 0) return 2;
        input.push_back(static_cast<uint8_t>(a * 16 + b));
      }
    }
    Result result = run(input, static_cast<Format>(format), operation == 1, limit);
    std::cout << static_cast<int>(result.status) << ' ' << result.zlib_status << ' ';
    constexpr char digits[] = "0123456789abcdef";
    if (result.status != Status::Ok || result.output.view().empty()) std::cout << '-';
    else for (uint8_t byte : result.output.view()) std::cout << digits[byte >> 4] << digits[byte & 15];
    std::cout << '\n';
  }
}
