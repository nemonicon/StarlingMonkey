// Dormant definitions only. Called by the existing deployed createServerHandler API.
export const gzipCases = Object.freeze(['small', 'large']);
export function payloadFor(caseId) {
  if (caseId === 'small') return new TextEncoder().encode('NEXT_GZIP_COMPOSITION_SMALL_V1\nplain finite response\n');
  if (caseId !== 'large') throw new TypeError('Unknown gzip case');
  const out = new Uint8Array(2 * 1024 * 1024);
  let state = 0x6d2b79f5;
  for (let i = 0; i < out.length; i++) {
    state ^= state << 13; state ^= state >>> 17; state ^= state << 5;
    state >>>= 0; out[i] = state >>> 24;
  }
  return out;
}
export function createGzipCompositionHandler(zlib) {
  if (typeof zlib?.createGzip !== 'function') throw new TypeError('Selected node:zlib.createGzip required');
  return function handler(req, res) {
    const match = /^\/gzip-composition\/(small|large)$/.exec(req.url);
    if (req.method !== 'GET' || !match) { res.statusCode = 404; res.end('fixed GET cases only'); return; }
    const caseId = match[1], input = payloadFor(caseId);
    const record = {schemaVersion: 1, suite: 'GZIP_COMPOSITION_PUBLIC_EVENTS_V1', caseId,
      sequence: 0, event: null, inputBytes: input.length, compressedBytes: 0, dataChunks: 0,
      inputWriteFalseCount: 0, inputDrainCount: 0, responseWriteFalseCount: 0,
      responseDrainCount: 0, pauseCount: 0, resumeCount: 0, gzipFinish: false,
      gzipEnd: false, resEndCalled: false, resFinish: false, resClose: false,
      gzipClose: false, error: null};
    let compressor, offset = 0, failed = false, errorSet = false;
    const emit = event => {
      record.event = event; record.sequence++;
      if (record.sequence > 16) throw new Error('Bounded event record limit');
      console.log('NEXT_GZIP_COMPOSITION_V1 ' + JSON.stringify(record));
    };
    function fail(stage, error) {
      if (!errorSet) {
        errorSet = true; failed = true;
        record.error = {stage, type: error === null ? 'null' : typeof error,
          name: typeof error?.name === 'string' ? error.name : null,
          message: typeof error?.message === 'string' ? error.message : String(error)};
        emit('error');
      }
      compressor?.destroy(error instanceof Error ? error : new Error('Non-Error stream failure', {cause: error}));
      res.destroy(error instanceof Error ? error : new Error('Non-Error response failure', {cause: error}));
    }
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Encoding', 'gzip');
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Gzip-Composition-Case', caseId);
    emit('start');
    try {
      compressor = zlib.createGzip({chunkSize: 16384, readableHighWaterMark: 65536, writableHighWaterMark: 65536});
      compressor.on('error', error => fail('gzip', error));
      res.on('error', error => fail('response', error));
      compressor.on('data', chunk => {
        if (failed) return;
        try {
          record.compressedBytes += chunk.byteLength; record.dataChunks++;
          if (record.compressedBytes > 3 * 1024 * 1024) throw new RangeError('Compressed output cap');
          if (res.write(chunk) === false) {
            record.responseWriteFalseCount++; record.pauseCount++; compressor.pause();
            if (record.responseWriteFalseCount === 1) emit('first-response-backpressure');
          }
        } catch (error) { fail('write', error); }
      });
      const responseDrain = () => {
        if (failed) return;
        record.responseDrainCount++; record.resumeCount++; compressor.resume();
        if (record.responseDrainCount === 1) emit('first-response-drain');
      };
      res.on('drain', responseDrain);
      compressor.on('finish', () => { record.gzipFinish = true; emit('gzip-finish'); });
      compressor.on('end', () => {
        record.gzipEnd = true; emit('gzip-end');
        if (!failed) { record.resEndCalled = true; emit('response-end-call'); res.end(); }
      });
      compressor.on('close', () => { record.gzipClose = true; emit('gzip-close'); });
      res.on('finish', () => { record.resFinish = true; emit('response-finish'); });
      res.on('close', () => {
        record.resClose = true; res.off('drain', responseDrain);
        // A prematurely closed response cannot provide another drain event.
        // Retire this probe-owned paused compressor through its public API.
        if (!record.resFinish) fail('response-close-before-finish', new Error('Response closed before finish'));
        emit('response-close');
      });
      function feed() {
        if (failed) return;
        try {
          while (offset < input.length) {
            const end = Math.min(offset + 32768, input.length), part = input.subarray(offset, end);
            offset = end;
            if (compressor.write(part) === false) {
              record.inputWriteFalseCount++;
              compressor.once('drain', () => {
                record.inputDrainCount++;
                if (record.inputDrainCount === 1) emit('first-input-drain');
                feed();
              });
              return;
            }
          }
          compressor.end();
        } catch (error) { fail('feed', error); }
      }
      feed();
    } catch (error) { fail('setup', error); }
  };
}
