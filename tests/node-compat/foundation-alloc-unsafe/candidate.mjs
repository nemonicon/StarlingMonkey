// Isolated dependency proposal, NOT installed in the production Buffer module.
// Trusted installation/test code supplies the existing native Buffer constructor.
const Apply = Reflect.apply;
const Trunc = Math.trunc;
const Finite = Number.isFinite;
const TypeErrorCtor = TypeError;
const RangeErrorCtor = RangeError;
const MAX_LENGTH = 16777216;
function failure(Ctor, code, message) {
  const error = new Ctor(`${code}: Buffer.allocUnsafe ${message}`);
  error.code = code; error.module = 'node:buffer'; error.operation = 'Buffer.allocUnsafe';
  return error;
}
export function createAllocUnsafeCandidate(BufferCtor) {
  // Capture at trusted installation, before application mutation. This factory
  // is test-only; it is not a proposed public guest installer or new export.
  const alloc = BufferCtor.alloc;
  return function allocUnsafe(size) {
    if (typeof size !== 'number') throw failure(TypeErrorCtor, 'ERR_INVALID_ARG_TYPE', 'size must be a number');
    // Validate BEFORE truncation: negative fractions must not silently become0.
    if (!Finite(size) || size < 0 || size > MAX_LENGTH)
      throw failure(RangeErrorCtor, 'ERR_OUT_OF_RANGE', 'size must be between0 and16777216');
    // Existing alloc owns/brands fresh zeroed fixed storage. No pool, allocator
    // transfer, uninitialized byte exposure, raw span or catch/fallback is added.
    return Apply(alloc, BufferCtor, [Trunc(size)]);
  };
}
