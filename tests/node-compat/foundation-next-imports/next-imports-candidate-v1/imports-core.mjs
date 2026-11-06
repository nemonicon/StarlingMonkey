export function createNextImportFacades(inventory) {
  const records = {};
  const unsupported = (module, operation) => {
    const error = new Error(`${module}.${operation} is unavailable in this guest profile`);
    Object.assign(error, {code: 'ERR_SM_NODE_UNSUPPORTED', module, operation});
    throw error;
  };
  function value(module, operation, row) {
    switch (row.type) {
      case 'function': {
        if (module === 'node:tty' && operation === 'isatty') return function isatty() { return false; };
        if (module === 'node:inspector' && operation === 'url') return function url() { return undefined; };
        const fn = ({[operation]: function() { return unsupported(module, operation); }})[operation];
        Object.defineProperty(fn, 'length', {value: row.length, configurable: true});
        return fn;
      }
      case 'symbol': return row.globalKey === undefined ? Symbol(row.description) : Symbol.for(row.globalKey);
      case 'undefined': return undefined;
      case 'object': {
        if (row.value === null) return null;
        const out = {};
        for (const [name, child] of Object.entries(row.properties))
          Object.defineProperty(out, name, {value: value(module, operation + '.' + name, child), writable: true, configurable: true, enumerable: true});
        return out;
      }
      case 'string': case 'number': case 'boolean': return row.value;
      default: throw new TypeError('Invalid finite import inventory');
    }
  }
  for (const [module, rows] of Object.entries(inventory.modules)) {
    const cjs = {};
    for (const [name, row] of Object.entries(rows))
      Object.defineProperty(cjs, name, {value: value(module, name, row), writable: true, configurable: true, enumerable: true});
    records[module] = Object.freeze({...cjs, default: cjs});
  }
  return records;
}
