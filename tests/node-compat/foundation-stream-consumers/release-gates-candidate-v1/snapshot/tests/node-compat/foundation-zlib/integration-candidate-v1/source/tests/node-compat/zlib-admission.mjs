// Source proposal guard only. No positive artifact authority exists.
export function validateZlibSourceAdmission(metadata) {
  const hinted = Object.hasOwn(metadata, 'zlibEnabled') || Object.hasOwn(metadata, 'zlibPolicy') ||
    Object.hasOwn(metadata.observedCMakeOptions ?? {}, 'NODE_COMPAT_ZLIB') ||
    (Array.isArray(metadata.sourceManifest) && metadata.sourceManifest.some(row => row.path?.startsWith('builtins/node-compat/zlib/')));
  if (!hinted) return null;
  const error = new Error('Bounded zlib activation awaits full child-source, recipe, linked-codec and actual guest review');
  error.code = 'ERR_SM_NODE_ZLIB_ACTIVATION_PENDING';
  throw error;
}
