// Bounded ordinary-API vectors for future differential comparison. No candidate
// is installed here; all chunks are owned, fixed and unshared. No fault probes.
export async function streamChecks(stream, promises, consumers, Buffer) {
  const cases = [];
  async function check(name, run) { cases.push({ name, result: await run() }); }
  await check('module and promise identity graph', () => ({ defaultIsStream: stream.default === stream.Stream,
    self: stream.Stream.Stream === stream.Stream, promises: stream.promises === promises.default,
    defaultMethods: ['Readable', 'Writable', 'Duplex', 'Transform', 'PassThrough', 'pipeline', 'finished'].every(name => stream.default[name] === stream[name]) }));
  await check('object pipeline and transform flush', async () => {
    const values = [], transform = new stream.Transform({ objectMode: true,
      transform(value, encoding, callback) { callback(null, value * 2); },
      flush(callback) { this.push('tail'); callback(); } });
    const sink = new stream.Writable({ objectMode: true, write(value, encoding, callback) { values.push(value); callback(); } });
    await promises.pipeline(stream.Readable.from([1, 2, 3]), transform, sink);
    return { values, finished: sink.writableFinished, readableEnded: transform.readableEnded, destroyed: transform.destroyed && sink.destroyed };
  });
  await check('backpressure and drain', async () => {
    const trace = []; let complete;
    const sink = new stream.Writable({ objectMode: true, highWaterMark: 1,
      write(value, encoding, callback) { trace.push('write:'+value); complete = callback; } });
    const drain = new Promise(resolve => sink.once('drain', () => { trace.push('drain'); resolve(); }));
    trace.push('return:'+sink.write(1, () => trace.push('callback')));
    complete(); await drain; sink.end(); await promises.finished(sink);
    return { trace, writableLength: sink.writableLength, finished: sink.writableFinished };
  });
  await check('cork writev callbacks and finish', async () => {
    const trace = [];
    const sink = new stream.Writable({ objectMode: true,
      write(value, encoding, callback) { trace.push('write:'+value); callback(); },
      writev(chunks, callback) { trace.push('writev:'+chunks.map(entry => entry.chunk).join(',')); callback(); } });
    sink.on('finish', () => trace.push('finish')); sink.on('close', () => trace.push('close'));
    sink.cork(); sink.write(1, () => trace.push('callback1')); sink.write(2, () => trace.push('callback2'));
    trace.push('before-uncork'); sink.uncork(); sink.end(); await promises.finished(sink); return trace;
  });
  await check('destroy identity and one error close', async () => {
    const first = new Error('first'), second = new Error('second'), trace = [];
    const source = new stream.Readable({ read() {} });
    const closed = new Promise(resolve => source.once('close', () => { trace.push('close'); resolve(); }));
    source.on('error', error => trace.push(error === first ? 'first-error' : 'other-error'));
    source.destroy(first); source.destroy(second); trace.push('after-destroy'); await closed;
    return { trace, destroyed: source.destroyed, firstErrorRetained: source.errored === first };
  });
  await check('byte view shared backing offsets', () => {
    const backing = new Uint8Array([0, 65, 66, 0]), input = new Uint8Array(backing.buffer, 1, 2);
    const source = new stream.Readable({ read() {} }); source.push(input); input[0] = 90;
    const output = source.read(); output[1] = 89; source.destroy();
    return { bytes: [...output], input: [...input], isBuffer: Buffer.isBuffer(output),
      sharedBuffer: output.buffer === backing.buffer, byteOffset: output.byteOffset, length: output.length };
  });
  await check('Node22 DataView byte write', async () => {
    const bytes = new Uint8Array([0, 65, 66, 0]), input = new DataView(bytes.buffer, 1, 2); let observed;
    const sink = new stream.Writable({ write(value, encoding, callback) {
      observed = { bytes: [...value], isBuffer: Buffer.isBuffer(value), shared: value.buffer === bytes.buffer,
        offset: value.byteOffset, length: value.length }; value[0] = 90; callback();
    } });
    sink.end(input); await promises.finished(sink); return { observed, changedOriginal: bytes[1] === 90 };
  });
  await check('consumer streaming UTF8 BOM and incomplete bytes', async () => {
    async function* chunks() { yield new Uint8Array([0xEF, 0xBB]); yield new Uint8Array([0xBF, 0xE2, 0x82]); yield new Uint8Array([0xAC, 0xFF]); }
    return consumers.text(chunks());
  });
  await check('consumer mutable Blob part timing', async () => {
    async function* chunks() { const bytes = new Uint8Array([65]); yield bytes; bytes[0] = 66; yield bytes; bytes[0] = 67; }
    return [...new Uint8Array(await consumers.arrayBuffer(chunks()))];
  });
  await check('consumer JSON chunks', async () => {
    async function* chunks() { yield '{"value":'; yield new Uint8Array([49]); yield '}'; }
    return consumers.json(chunks());
  });
  await check('pipeline abort cleanup', async () => {
    const controller = new AbortController(), reason = new Error('cancel');
    const source = new stream.Readable({ objectMode: true, read() {} });
    const sink = new stream.Writable({ objectMode: true, write(value, encoding, callback) { callback(); } });
    const result = promises.pipeline(source, sink, { signal: controller.signal }); controller.abort(reason);
    let failure; try { await result; } catch (error) { failure = error; }
    return { name: failure?.name, code: failure?.code, causeSame: failure?.cause === reason,
      sourceDestroyed: source.destroyed, sinkDestroyed: sink.destroyed };
  });
  return cases;
}
