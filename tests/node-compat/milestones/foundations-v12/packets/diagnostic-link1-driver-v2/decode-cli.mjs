// Host-only exact function copy from foundations/native-scalar-harness.mjs.
// Kept local so raw diagnostic packaging never imports the production selector.
import assert from 'node:assert/strict';
export function decodeCliString(source) {
  let normalized = '';
  for (let index = 0; index < source.length; index++) {
    const char = source[index];
    if (char !== '\\') { normalized += char; continue; }
    const next = source[++index];
    if (next === 'u' && source[index + 1] === '{') {
      const end = source.indexOf('}', index + 2), digits = source.slice(index + 2, end);
      assert(end > index && /^[0-9a-fA-F]+$/.test(digits));
      normalized += JSON.stringify(String.fromCodePoint(parseInt(digits, 16))).slice(1, -1); index = end;
    } else if (next === "'") normalized += "'";
    else normalized += next === '0' ? '\\u0000' : '\\' + next;
  }
  try { return JSON.parse(normalized); }
  catch (error) { throw new Error('Wasmtime CLI string decoding: '+error.message); }
}
