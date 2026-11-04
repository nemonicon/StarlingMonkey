const root = require('assert');
const canonical = require('node:assert');
const strict = require('assert/strict');
const canonicalStrict = require('node:assert/strict');
module.exports = function inspect(rootDefault, strictDefault) {
  let call, construct;
  try { root.deepStrictEqual({}, {}); } catch (error) { call = error.code; }
  try { new strict.rejects(); } catch (error) { construct = error.code; }
  return { rootType: typeof root, strictType: typeof strict,
    same: root === canonical && root === rootDefault && strict === canonicalStrict && strict === strictDefault,
    strictGraph: root.strict === strict && strict.strict === strict && root.ok === strict.ok,
    aliasOverrides: strict.equal === root.strictEqual && strict.notEqual === root.notStrictEqual,
    defaultProperty: typeof root.default, rejectedCall: call, rejectedConstruction: construct };
};
