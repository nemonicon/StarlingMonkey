import { OutgoingResponse, OutgoingBody, ResponseOutparam, Fields } from 'wasi:http/types@0.2.10';
import { spawn, ChildProcess } from 'node:child_process';
import { run as runNativeChecks } from '../fixtures/component.mjs';

// These values are snapshotted once. Counter observations describe state seen
// through this export; they do not identify whether a host reuses Wasm instances.
const snapshotMarker = 'HTTP module initialized during componentization';
const encoder = new TextEncoder();

function captureUnsupported(operation) {
  try { operation(); }
  catch (error) {
    if (error.code !== 'ERR_SM_NODE_UNSUPPORTED') throw error;
    return { code: error.code, module: error.module, operation: error.operation, profile: error.profile };
  }
  throw new Error('Unsupported process operation unexpectedly returned');
}

export function createIncomingHandler(runNativeChecks) {
  let requestCount = 0;
  return {
  async handle(incomingRequest, responseOutparam) {
    let status = 200;
    let report;
    try {
      const native = JSON.parse(await runNativeChecks());
      report = {
        schema: 1,
        requestTag: incomingRequest.pathWithQuery() ?? '',
        componentInstanceRequestCount: ++requestCount,
        snapshotMarker,
        native,
        unsupported: captureUnsupported(() => spawn('must-never-start')),
        unsupportedConstructor: captureUnsupported(() => new ChildProcess()),
      };
      if (native.failure) status = 500;
    } catch (error) {
      status = 500;
      report = { schema: 1, failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } };
    }

    let responseSet = false;
    let body;
    let stream;
    let finished = false;
    try {
      const response = new OutgoingResponse(Fields.fromList([
        ['content-type', encoder.encode('application/json; charset=utf-8')],
        ['cache-control', encoder.encode('no-store')],
      ]));
      response.setStatusCode(status);
      body = response.body();
      ResponseOutparam.set(responseOutparam, { tag: 'ok', val: response });
      responseSet = true; // Both response and outparam ownership transferred.
      stream = body.write();
      const bytes = encoder.encode(JSON.stringify(report));
      // WASI's blocking-write-and-flush convenience operation admits at most
      // 4096 bytes per call. Chunk even diagnostic/path-dependent payloads.
      for (let offset = 0; offset < bytes.length; offset += 4096) {
        stream.blockingWriteAndFlush(bytes.subarray(offset, offset + 4096));
      }
      stream[Symbol.dispose]();
      stream = undefined;
      OutgoingBody.finish(body, undefined);
      finished = true; // finish consumes the outgoing-body resource.
    } finally {
      if (stream) stream[Symbol.dispose]();
      if (body && !finished) body[Symbol.dispose]();
      if (!responseSet) responseOutparam[Symbol.dispose]();
      incomingRequest[Symbol.dispose]();
    }
  },
  };
}

export const incomingHandler = createIncomingHandler(runNativeChecks);
