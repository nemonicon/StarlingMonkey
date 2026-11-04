import {correctnessPreflight} from './runtime-preflight.mjs';
const admission=await correctnessPreflight();
const {runCorrectness}=await import('./component-driver.mjs');
await runCorrectness(admission);
