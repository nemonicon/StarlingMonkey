// Deliberately componentized WITHOUT bundling: exercise both registry keys.
import buffer, * as namespace from 'node:buffer';
import sameBuffer, * as sameNamespace from 'node:buffer';
import bareBuffer, * as bareNamespace from 'buffer';
import child from 'node:child_process';
import bareChild from 'child_process';
export async function run() {
  const dynamicNamespace = await import('node:buffer');
  const dynamicBareNamespace = await import('buffer');
  const dynamicChildNamespace = await import('node:child_process');
  if (buffer !== bareBuffer || buffer !== sameBuffer || namespace !== sameNamespace ||
      namespace === bareNamespace || buffer.Buffer !== globalThis.Buffer ||
      buffer.Buffer !== bareBuffer.Buffer || child !== bareChild || child.spawn !== bareChild.spawn ||
      dynamicNamespace !== namespace || dynamicBareNamespace !== bareNamespace || dynamicChildNamespace.default !== child) {
    throw new Error('native builtin registry alias/cache/global identity failure');
  }
  return 'native registry aliases, dynamic imports and per-specifier caching passed';
}
