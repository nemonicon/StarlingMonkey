export const identity = {
  echoU32: value => value,
  constantU32: () => 0xffffffff,
  echoS32: value => value,
  echoF32: value => value,
  echoF64: value => value,
  echoU64: value => value,
  echoS64: value => value,
  echoList: value => value,
  echoPayload: value => value,
  echoResult(ok, value) { if (ok) return value; throw value; },
};
