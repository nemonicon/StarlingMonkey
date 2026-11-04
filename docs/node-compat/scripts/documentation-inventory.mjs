// Node's generated API JSON sometimes calls a property "Type" or "return".
// The backticked declaration, not that parser placeholder, names the API.
const aliases = {
  async_context: 'async_hooks', events: 'events', webstreams: 'stream/web',
  webcrypto: 'crypto', 'single-executable-applications': 'sea',
  tracing: 'trace_events', globals: '@globals', modules: 'module',
};
const collections = ['modules', 'miscs', 'classes', 'methods', 'properties',
  'events', 'globals', 'classMethods', 'ctors'];

export function collectDocumentationAPI(docs, { moduleIds, reflectedRows }) {
  const admitted = new Set([...moduleIds, '@globals']);
  const reflected = new Map();
  for (const { module, api } of reflectedRows) {
    if (!reflected.has(module)) reflected.set(module, new Set());
    reflected.get(module).add(api);
  }
  const rows = [], excluded = [];
  function walk(node, id, path, collectionKind = '', ownerClass = '') {
    if (!node || typeof node !== 'object') return;
    if (node.source) {
      const source = node.source.split('/').at(-1).replace(/\.md$/, '');
      id = aliases[source] ?? source;
    }
    const isProperty = collectionKind === 'properties';
    const declaration = /^`([^`]+)`/.exec(node.textRaw ?? '')?.[1];
    let name = (node.name ?? '').replaceAll('`', '');
    if (isProperty && ['Type', 'return'].includes(name)) {
      if (!declaration || /[()\s]/.test(declaration)) {
        throw new Error(`Cannot identify documented property: ${node.textRaw}`);
      }
      name = declaration;
    }
    const next = name ? [...path, name] : path;
    if (node.type === 'class' || node.type === 'global') ownerClass = name;
    if (isProperty || ['method', 'class', 'property', 'event', 'global', 'classMethod', 'ctor'].includes(node.type)) {
      let canonical = next.join('/');
      if (node.type === 'class' || node.type === 'global') canonical = name;
      if (ownerClass && ['methods', 'classMethods', 'properties'].includes(collectionKind)) {
        canonical = `${ownerClass}.${collectionKind === 'classMethods' ? '' : 'prototype.'}${name}`;
      }
      if (isProperty) {
        // An actual namespace binding wins over a misleading documentation
        // heading parent (e.g. asyncWrapProviders appears under AsyncHook).
        const known = reflected.get(id) ?? new Set();
        const owner = ownerClass.split('.').at(-1);
        const instance = `${owner}.prototype.${name}`;
        const staticMember = `${owner}.${name}`;
        if (ownerClass && known.has(instance)) canonical = instance;
        else if (ownerClass && known.has(staticMember)) canonical = staticMember;
        else if (known.has(name) && !ownerClass) canonical = name;
        else if (declaration?.includes('.') && known.has(declaration)) canonical = declaration;
        else if (!ownerClass) {
          // Nested constants are finite reflected objects, not prototype fields.
          const candidates = [...known].filter(api => api.endsWith(`.${name}`));
          if (candidates.length === 1) canonical = candidates[0];
        }
        // This pinned markdown heading is nested under AsyncHook by Node's
        // converter, although asyncWrapProviders is a reflected module export.
        if (id === 'async_hooks' && name === 'asyncWrapProviders' && known.has(name)) canonical = name;
      }
      const bufferMethod = /\bbuf\.([a-zA-Z_$][\w$]*)/.exec(node.textRaw ?? '');
      const bufferStatic = /\bBuffer\.([a-zA-Z_$][\w$]*)/.exec(node.textRaw ?? '');
      if (id === 'buffer' && bufferMethod) canonical = `Buffer.prototype.${bufferMethod[1]}`;
      else if (id === 'buffer' && bufferStatic) canonical = `Buffer.${bufferStatic[1]}`;
      const row = { module: id, api: canonical, kind: isProperty ? 'property' : node.type, detail: node.textRaw ?? '' };
      // errors, esm, permissions and n-api are documentation chapters, not
      // importable Node builtins. Keep an exclusion record rather than inventing
      // module IDs or discarding an export from the runtime inventory.
      if (admitted.has(id)) rows.push(row);
      else excluded.push({ ...row, reason: 'Documentation chapter is not a builtin module or global namespace' });
    }
    for (const collection of collections) {
      for (const child of node[collection] ?? []) walk(child, id, next, collection, ownerClass);
    }
  }
  walk(docs, '@globals', []);
  return { rows, excluded };
}
