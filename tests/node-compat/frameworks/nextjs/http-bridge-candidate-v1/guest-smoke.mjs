// Bridge integration control; this is explicitly not the Next application.
import * as types from 'wasi:http/types@0.2.10';
import {createRequestBridge} from './bridge.mjs';
import {createWasiHttpHandler} from './wasi-adapter.mjs';
const handler = createRequestBridge(async (req, res) => {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  res.setHeader('content-type', 'text/plain');
  res.setHeader('x-bridge-control', 'native-guest-streams');
  res.end(req.method + ' ' + req.url + '\n' + Buffer.concat(chunks).toString('utf8'));
});
export const incomingHandler = createWasiHttpHandler(handler, types);
