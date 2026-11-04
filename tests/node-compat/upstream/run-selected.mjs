import { spawn } from 'node:child_process';
import { mkdir, open, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { context, output, here } from './common.mjs';

const ctx = await context();
await mkdir(output, { recursive: true });
const names = ['initialization', 'starling', 'run', 'buffer-ownership',
  ...(process.env.NODE_COMPAT_UPSTREAM_SKIP_INTEGRATION === '1' ? [] : ['integration']), 'collect'];
const processes = [];
for (const name of names) {
  const logPath = join(output, name + '.log');
  const log = await open(logPath, 'w');
  const result = await new Promise(resolve => {
    const cp = spawn(process.execPath, [join(here, name + '.mjs')], { stdio: ['ignore', log.fd, log.fd] });
    cp.on('exit', (code, signal) => resolve({ script: name, code, signal, logPath }));
  });
  await log.close();
  processes.push(result);
  console.log(JSON.stringify(result));
  await writeFile(join(output, 'selected-processes.json'), JSON.stringify({ engineSha256: ctx.engineSha256, componentizerProvenance: ctx.componentizerProvenance, processes }, null, 2) + '\n');
}
process.exitCode = processes.some(result => result.code !== 0) ? 1 : 0;
