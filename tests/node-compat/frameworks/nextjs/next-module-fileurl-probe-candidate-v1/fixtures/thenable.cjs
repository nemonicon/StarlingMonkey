let reads = 0;
const value = {inspectThenReads() { return reads; }};
Object.defineProperty(value, 'then', {get() { reads++; throw new Error('probe default then getter read'); }});
module.exports = value;
