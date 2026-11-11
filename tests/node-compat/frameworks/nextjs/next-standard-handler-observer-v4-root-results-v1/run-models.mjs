// Host-Node inert models only; does not execute the observer Wasm or a WASI host.
import {readFile} from 'node:fs/promises';
import {runObserverV4ModelFixtures} from '../next-standard-handler-return-observer-v4/model-fixtures.mjs';
const fixtures = JSON.parse(await readFile(new URL('../next-standard-handler-return-observer-v4/wire-byte-fixtures.json', import.meta.url), 'utf8'));
console.log(JSON.stringify(runObserverV4ModelFixtures(fixtures)));
