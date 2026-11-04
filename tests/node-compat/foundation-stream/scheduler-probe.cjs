// Exact Node host oracle only; no component/host capability claim.
const { pathToFileURL } = require('node:url');
async function main() {
  const mode = process.argv[2], boundary = process.argv[3];
  const scheduler = mode === 'node' ? { nextTick: process.nextTick.bind(process) } : await import(pathToFileURL(process.argv[4]));
  const run = () => {
    const trace = [];
    Promise.resolve().then(() => trace.push('promise-first'));
    scheduler.nextTick(() => { trace.push('tick'); scheduler.nextTick(() => trace.push('nested-tick')); });
    queueMicrotask(() => trace.push('microtask'));
    setImmediate(() => process.stdout.write(JSON.stringify({ mode, boundary, trace })+'\n'));
  };
  if (boundary === 'task') setImmediate(run);
  else Promise.resolve().then(run);
}
main().catch(error => { console.error(error); process.exitCode = 1; });
