const buffer = require('buffer');
const childProcess = require('node:child_process');
const __smBuiltin0 = { Buffer: 'local Buffer marker' };
const __smModule = 'local module marker';
function nestedChild(__smBuiltin1) { return require('node:child_process'); }
module.exports = { Buffer: buffer.Buffer, buffer, childProcess,
  localMarker: __smBuiltin0.Buffer, moduleMarker: __smModule, nestedChild };
