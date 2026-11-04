// Explicit static CJS fixture; only admitted literal builtin requires.
module.exports = {
  cjs: require('node:stream'),
  cjsAlias: require('stream'),
  cjsPromises: require('node:stream/promises'),
  cjsPromisesAlias: require('stream/promises'),
};
