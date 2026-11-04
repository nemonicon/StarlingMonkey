const bare = require('events');
const canonical = require('node:events');
module.exports = function inspectCommonJS(EventEmitter) {
  let callCode, constructCode;
  try { bare.once(); } catch (error) { callCode = error.code; }
  try { new canonical.EventEmitterAsyncResource(); } catch (error) { constructCode = error.code; }
  return { same: bare === canonical && bare === EventEmitter, constructorAlias: bare.EventEmitter === bare,
    defaultProperty: typeof bare.default, errorMonitorType: typeof bare.errorMonitor,
    rejectedCall: callCode, rejectedConstruction: constructCode };
};
