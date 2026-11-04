// Drives only the traced aggregation methods, with every returned byte written.
export function demandChecks(BufferCtor, List) {
  const make = values => BufferCtor.from(new Uint8Array(values));
  const list = new List(); list.push(make([1, 2])); list.push(make([3, 4, 5]));
  const joined = list.concat(5);
  const second = new List(); second.push(make([1, 2])); second.push(make([3, 4, 5]));
  const consumed = second._getBuffer(3);
  return { concat: [...joined], concatBrand: BufferCtor.isBuffer(joined), originalNodes: list.length,
    consumed: [...consumed], consumedBrand: BufferCtor.isBuffer(consumed), remainingNodes: second.length,
    remaining: [...second.head.data], outputVisibleRangeDisjoint: consumed.buffer !== second.head.data.buffer ||
      consumed.byteOffset + consumed.byteLength <= second.head.data.byteOffset ||
      second.head.data.byteOffset + second.head.data.byteLength <= consumed.byteOffset };
}
