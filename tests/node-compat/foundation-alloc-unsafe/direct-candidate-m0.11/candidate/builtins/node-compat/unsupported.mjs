// No host capability is consulted, including at snapshot time.
export const PROFILE_VERSION = 'sm-node-22.14.0-m0.11';

// Capture trusted installation-time constructors/intrinsics before application
// code can replace them. Own data descriptors bypass inherited field hooks.
const ProfileError = Error;
const DefineErrorProperty = Object.defineProperty;

export function unsupported(module, operation) {
  const error = new ProfileError(`${module}.${operation} is unavailable in ${PROFILE_VERSION}`);
  DefineErrorProperty(error, 'code', { __proto__: null, value: 'ERR_SM_NODE_UNSUPPORTED', writable: true, enumerable: true, configurable: true });
  DefineErrorProperty(error, 'module', { __proto__: null, value: module, writable: true, enumerable: true, configurable: true });
  DefineErrorProperty(error, 'operation', { __proto__: null, value: operation, writable: true, enumerable: true, configurable: true });
  DefineErrorProperty(error, 'profile', { __proto__: null, value: PROFILE_VERSION, writable: true, enumerable: true, configurable: true });
  throw error;
}

export function unavailable(module, operation) {
  // Ordinary functions throw on both invocation and construction. No Proxy,
  // getters, then member, or host operation is involved.
  return function unavailableOperation() { unsupported(module, operation); };
}
