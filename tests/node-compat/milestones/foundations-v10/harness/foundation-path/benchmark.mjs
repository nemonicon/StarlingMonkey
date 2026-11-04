import path from 'node:path';
export function run(iterations) {
  let checksum = 0x811c9dc5;
  for (let i = 0; i < iterations; i++) {
    const value = path.posix.join('a', 'b', '..', 'c').length +
      13 * path.win32.normalize('C:\\a\\..\\b').length +
      (path.matchesGlob('src/file2.js', '**/file{1..3}.{js,ts}') ? 7 : 0);
    checksum = Math.imul(checksum ^ value, 16777619) | 0;
  }
  return checksum | 0;
}
