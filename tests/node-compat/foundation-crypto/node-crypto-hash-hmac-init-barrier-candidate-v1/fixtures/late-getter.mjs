import { createHash } from 'node:crypto';
// Actual bindgen.rs emits `local = __iface.run` during bindExports. That occurs
// after finish_pre_initialization but BEFORE the existing deployed call hook.
export const api = {
  get run() {
    createHash('sha256');
    return () => 'UNEXPECTED_INITIALIZATION_ACCEPTANCE';
  }
};
