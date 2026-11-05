import required from './native-cjs-interop.cjs';
import buffer, {Buffer} from 'node:buffer';
import stream from 'node:stream';
import events from 'node:events';
export function run() {
  const bytes = required.bare.Buffer.from(new Uint8Array([104,105]));
  return JSON.stringify({
    marker:required.state.marker,
    canonicalDefault:required.canonical===buffer,
    bareDefault:required.bare===buffer,
    nestedDefault:required.state.buffer===buffer,
    constructorIdentity:required.bare.Buffer===Buffer && Buffer===globalThis.Buffer,
    streamDefault:required.stream===stream,
    streamCallable:typeof required.stream==='function',
    streamSelf:required.stream.Stream===required.stream,
    eventDefault:required.events===events,
    noNamespaceDefault:Object.hasOwn(required.bare,'default')===false,
    text:bytes.toString('utf8'),hex:bytes.toString('hex'),
  });
}
