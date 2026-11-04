import * as nativeBuffer from 'node:buffer';
import { run as runBaselineChecks } from '../fixtures/component.mjs';
import { checkCapturedIntrinsics } from './intrinsics-checks.mjs';

export async function run() {
  try {
    const baseline = JSON.parse(await runBaselineChecks());
    if (baseline.failure) return JSON.stringify(baseline);
    return JSON.stringify({ ...baseline, intrinsics: checkCapturedIntrinsics(nativeBuffer) });
  } catch (error) {
    return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } });
  }
}
