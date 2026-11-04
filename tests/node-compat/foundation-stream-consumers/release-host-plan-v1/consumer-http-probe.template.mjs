// SOURCE TEMPLATE ONLY. No handler, component, oracle or action is wired here.
// Uses only the actual reviewed355 public text/json APIs and supported inputs.
import {text, json} from 'node:stream/consumers';
let calls = 0;
export async function runConsumerHttpProbe() {
  const call = ++calls;
  async function* utf8Chunks() {
    yield new Uint8Array([0xe2]);
    yield new Uint8Array([0x82, 0xac]);
  }
  async function* jsonChunks() {
    yield '{"consumer":';
    yield 'true}';
  }
  return {schema: 1, calls: call, text: await text(utf8Chunks()), json: await json(jsonChunks())};
}
// Future untimed Node/guest proof must observe text="€", json={consumer:true}.
// This probes fixed per-request fixture data, not an HTTP request-body adapter,
// cancellation/backpressure, request isolation or physical instance reuse.
