// Host packaging helper: exact source excerpts, not a Stream implementation.
export function bufferListDemandModule(source) {
  const names = ['constructor', 'push', 'concat', '_getBuffer'];
  const methods = names.map(name => {
    const start = source.indexOf(`  ${name}(`);
    if (start < 0) throw new Error('Missing pinned BufferList method '+name);
    const end = source.indexOf('\n  }', start);
    if (end < 0) throw new Error('Missing BufferList method terminator '+name);
    return source.slice(start, end+4);
  });
  const text = `// Test-only exact BufferList allocation demand excerpts.\n`+
    `export function createDemandList(Buffer) {\n`+
    `const Uint8Array = globalThis.Uint8Array;\n`+
    `const apply = Reflect.apply, set = Uint8Array.prototype.set;\n`+
    `const TypedArrayPrototypeSet = (receiver, source, offset) => apply(set, receiver, [source, offset]);\n`+
    `class BufferList {\n${methods.join('\n')}\n}\nreturn BufferList;\n}\n`;
  return { text, excerpts: Object.fromEntries(names.map((name, index) => [name, methods[index]])) };
}
