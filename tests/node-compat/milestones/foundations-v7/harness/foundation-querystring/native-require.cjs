const bare = require('querystring');
const canonical = require('node:querystring');
module.exports = function inspect(defaultObject) {
  let call, construct;
  try { bare.unescapeBuffer(3); } catch (error) { call = error.code; }
  try { new canonical.unescapeBuffer(3); } catch (error) { construct = error.code; }
  return { type: typeof bare, same: bare === canonical && bare === defaultObject,
    encodeAlias: bare.encode === bare.stringify, decodeAlias: bare.decode === bare.parse,
    nullParsePrototype: Object.getPrototypeOf(bare.parse('a=b')) === null,
    defaultProperty: typeof bare.default, rejectedCall: call, rejectedConstruction: construct };
};
