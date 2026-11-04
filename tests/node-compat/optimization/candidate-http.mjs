import { createIncomingHandler } from '../wasmcloud/http.mjs';
import { run } from './candidate-component.mjs';

export const incomingHandler = createIncomingHandler(run);
