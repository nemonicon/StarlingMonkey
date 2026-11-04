// FUTURE gate: all checked-in engine pins are deliberately null. Preflight must
// fail before this module imports any toolchain, componentizer, or guest driver.
import { classicPreflight } from '../runtime-preflight.mjs';

const variant=process.env.NODE_COMPAT_CLASSIC_VARIANT??'normal-off';
const admission=await classicPreflight({variant});
await admission.recheck();
const {runClassicGate}=await import('./component-driver.mjs');
await runClassicGate(admission);
