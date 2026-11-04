const bare = require('buffer').Buffer;
const canonical = require('node:buffer').Buffer;
module.exports = function allocators() { return [bare.allocUnsafe, canonical.allocUnsafe]; };
