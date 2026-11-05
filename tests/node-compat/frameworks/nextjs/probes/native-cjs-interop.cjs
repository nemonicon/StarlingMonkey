const state = require('./native-cjs-state.cjs');
module.exports = {
  bare: require('buffer'),
  canonical: require('node:buffer'),
  stream: require('stream'),
  events: require('node:events'),
  state,
};
