// No host capability is consulted, including at snapshot time.
export const PROFILE_VERSION = 'sm-node-22.14.0-m0.1';

export function unsupported(module, operation) {
  const error = new Error(`${module}.${operation} is unavailable in ${PROFILE_VERSION}`);
  error.code = 'ERR_SM_NODE_UNSUPPORTED';
  error.module = module;
  error.operation = operation;
  error.profile = PROFILE_VERSION;
  throw error;
}

export function unavailable(module, operation) {
  // Ordinary functions throw on both invocation and construction. No Proxy,
  // getters, then member, or host operation is involved.
  return function unavailableOperation() { unsupported(module, operation); };
}
