import { createHmac } from 'node:crypto';
// The getter succeeds. Actual embedding.cpp then drains the queued job before
// its final snapshot boundary, still without a deployed export call.
export const api = {
  get run() {
    queueMicrotask(() => createHmac('sha256', Uint8Array.of(1, 2, 3)));
    return () => 'UNEXPECTED_INITIALIZATION_ACCEPTANCE';
  }
};
