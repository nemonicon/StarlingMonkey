'use strict';
const object = {}, symbol = Symbol('argument');
const result = { invalidCallbacks: [], callbacks: [] };
for (const value of [undefined, null, 1, 'callback', {}, []]) {
  try { process.nextTick(value); result.invalidCallbacks.push({ threw: false }); }
  catch (error) { result.invalidCallbacks.push({ name: error.name, code: error.code }); }
}
result.returnIsUndefined = process.nextTick.call({ unusedReceiver: true }, function (a, b, c) {
  result.callbacks.push({ receiverUndefined: this === undefined,
    argumentCount: arguments.length, objectIdentity: a === object,
    symbolIdentity: b === symbol, primitive: c });
  return 'ignored callback return';
}, object, symbol, 17) === undefined;
const constructed = new process.nextTick(function () { result.constructedCallbackRan = true; });
result.publicNodeNextTickConstructible = typeof constructed === 'object';
setImmediate(() => process.stdout.write(JSON.stringify(result) + '\n'));
