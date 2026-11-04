function check(condition, message) { if (!condition) throw new Error(message); }
let calls = 0;
export async function run() {
  const root = await import('node:path');
  const bare = await import('path');
  const posix = await import('node:path/posix');
  const barePosix = await import('path/posix');
  const win32 = await import('node:path/win32');
  const bareWin32 = await import('path/win32');
  check(root === await import('node:path') && bare === await import('path'), 'root module caching');
  check(posix === await import('node:path/posix') && win32 === await import('node:path/win32'), 'subpath caching');
  check(root.default === bare.default && root.default === posix.default && root.default === barePosix.default, 'POSIX alias identity');
  check(root.win32 === win32.default && root.win32 === bareWin32.default, 'Win32 alias identity');
  check(root.posix.win32 === root.win32 && root.win32.posix === root.posix, 'shared graph');
  calls++;
  return JSON.stringify({ calls, nativeAliases: 6, caching: true, identities: true });
}
