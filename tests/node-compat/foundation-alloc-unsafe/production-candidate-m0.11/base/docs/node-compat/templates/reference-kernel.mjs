// TEST DOUBLE ONLY. This deliberately slow, host-free JS implementation permits
// checking the facade inside a component before the native kernel is compiled.
export function hexDecode(text) {
  let length = 0;
  while (length < Math.floor(text.length / 2) && /^[0-9a-f]{2}$/i.test(text.slice(2 * length, 2 * length + 2))) ++length;
  const result = new Uint8Array(length);
  for (let i = 0; i < length; ++i) result[i] = parseInt(text.slice(2 * i, 2 * i + 2), 16);
  return result;
}
export function hexEncode(bytes) {
  let result = '';
  for (const byte of bytes) result += byte.toString(16).padStart(2, '0');
  return result;
}
