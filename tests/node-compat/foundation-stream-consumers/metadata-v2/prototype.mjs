// Real finite ESM bindings for the isolated host-only prototype.
import { createConsumersModule } from './create-module.mjs';
const module = createConsumersModule();
export const arrayBuffer = module.arrayBuffer;
export const blob = module.blob;
export const buffer = module.buffer;
export const text = module.text;
export const json = module.json;
export default module.default;
