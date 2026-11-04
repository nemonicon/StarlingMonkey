// Deliberately finite vertical-slice bundler contract. The custom engine owns
// these real modules and global Buffer; this plugin never bundles a JS adapter.
import { builtinModules } from 'node:module';
import { readFileSync } from 'node:fs';
import { dirname, isAbsolute, resolve } from 'node:path';
import { builtinMap } from './module-selection.mjs';

export const manifest = builtinMap();
const otherBuiltins = new Set(builtinModules);

function visit(node, callback, parent = null, key = '') {
  if (!node || typeof node !== 'object') return;
  if (typeof node.type === 'string') callback(node, parent, key);
  for (const [field, value] of Object.entries(node)) {
    if (field === 'parent') continue;
    if (Array.isArray(value)) for (const child of value) visit(child, callback, node, field);
    else if (value && typeof value === 'object') visit(value, callback, node, field);
  }
}
function bindingNames(pattern, names = []) {
  if (!pattern) return names;
  if (pattern.type === 'Identifier') names.push(pattern.name);
  else if (pattern.type === 'RestElement') bindingNames(pattern.argument, names);
  else if (pattern.type === 'AssignmentPattern') bindingNames(pattern.left, names);
  else if (pattern.type === 'ArrayPattern') for (const p of pattern.elements) bindingNames(p, names);
  else if (pattern.type === 'ObjectPattern') for (const p of pattern.properties) bindingNames(p.value ?? p.argument, names);
  return names;
}

export function createProfilePlugin(parseAst, { virtualModules = {}, builtinManifests } = {}) {
  const admitted = builtinManifests ? builtinMap(builtinManifests) : manifest;
  for (const id of Object.keys(virtualModules)) {
    if (/^(?:jco:|wasmcloud:)/.test(id)) throw new Error(`Nonstandard host adapter is not admitted: ${id}`);
    if (id.includes('\0') || typeof virtualModules[id] !== 'string') throw new Error(`Invalid virtual module declaration: ${id}`);
    if (Object.hasOwn(admitted, id) || id.startsWith('node:') || otherBuiltins.has(id)) {
      throw new Error(`Virtual module cannot replace a native builtin: ${id}`);
    }
  }
  const commonjsSources = new Map();
  return {
    name: 'starling-native-node-profile',
    resolveId(source, importer) {
      if (Object.hasOwn(virtualModules, source)) return '\0' + source;
      if (Object.hasOwn(admitted, source)) return { id: admitted[source], external: true };
      if (source.startsWith('node:') || otherBuiltins.has(source)) {
        throw new Error(`Node builtin is not admitted by this profile: ${source}`);
      }
      if (/^(?:jco:|wasmcloud:)/.test(source)) throw new Error(`Nonstandard host adapter is not admitted: ${source}`);
      if (source.endsWith('.cjs')) {
        // Rolldown determines script-vs-module from the resolved extension.
        // Give our explicitly lowered .cjs source an ESM identity before it
        // parses the transformed import/export declarations.
        const original = isAbsolute(source) ? source : resolve(importer ? dirname(importer) : process.cwd(), source);
        const esmId = original + '.native-profile.mjs';
        commonjsSources.set(esmId, original);
        return esmId;
      }
      return null;
    },
    load(id) {
      if (commonjsSources.has(id)) return readFileSync(commonjsSources.get(id), 'utf8');
      if (id.startsWith('\0')) return Object.hasOwn(virtualModules, id.slice(1)) ? virtualModules[id.slice(1)] : null;
    },
    transform(code, id) {
      if (id.startsWith('\0')) return null;
      const ast = parseAst(code, {}, commonjsSources.get(id) ?? id);
      const commonjs = commonjsSources.has(id);
      const calls = [];
      const identifiers = new Set();
      let requiresBinding = false;
      visit(ast, (node, parent, key) => {
        if (node.type === 'Identifier') identifiers.add(node.name);
        let bindings = [];
        if (node.type === 'VariableDeclarator') bindings = bindingNames(node.id);
        if (/^(?:FunctionDeclaration|FunctionExpression|ArrowFunctionExpression)$/.test(node.type)) {
          bindings = [node.id?.name, ...node.params.flatMap(p => bindingNames(p))];
        }
        if (node.type === 'ImportSpecifier' || node.type === 'ImportDefaultSpecifier' || node.type === 'ImportNamespaceSpecifier') bindings = [node.local.name];
        if (node.type === 'CatchClause') bindings = bindingNames(node.param);
        if (bindings.includes('require')) requiresBinding = true;
        if (node.type === 'CallExpression' && node.callee.type === 'Identifier' && node.callee.name === 'require') {
          if (!commonjs || node.optional || node.arguments.length !== 1 || node.arguments[0].type !== 'Literal' || typeof node.arguments[0].value !== 'string') {
            throw new Error(`Only literal require of admitted builtins in .cjs is supported: ${id}`);
          }
          const specifier = node.arguments[0].value;
          if (!Object.hasOwn(admitted, specifier)) throw new Error(`CommonJS require is not admitted: ${specifier}`);
          const canonical = admitted[specifier];
          calls.push({ start: node.start, end: node.end, canonical });
        }
        if (node.type === 'Identifier' && node.name === 'require' && !(parent?.type === 'CallExpression' && key === 'callee')) {
          // Reject aliasing, require.resolve, and scope-dependent lowering.
          throw new Error(`require may only be a direct admitted call: ${id}`);
        }
        if (commonjs && node.type === 'Identifier' && ['__dirname', '__filename'].includes(node.name)) {
          throw new Error(`CommonJS filename bindings have no profile policy: ${id}`);
        }
      });
      if (requiresBinding) throw new Error(`Shadowed require is outside the static contract: ${id}`);
      if (!commonjs) return null;
      const imports = [...new Set(calls.map(c => c.canonical))];
      function freshIdentifier(base) {
        let name = base;
        for (let suffix = 1; identifiers.has(name); suffix++) name = `${base}_${suffix}`;
        identifiers.add(name);
        return name;
      }
      // Avoid capture by declarations or parameters in ANY nested source
      // scope, rather than assuming bundler-private prefixes cannot collide.
      const importNames = imports.map((_, i) => freshIdentifier(`__smBuiltin${i}`));
      const moduleName = freshIdentifier('__smModule');
      for (const call of calls.sort((a, b) => b.start - a.start)) {
        code = code.slice(0, call.start) + importNames[imports.indexOf(call.canonical)] + code.slice(call.end);
      }
      const prefix = imports.map((name, i) => `import ${importNames[i]} from ${JSON.stringify(name)};`).join('\n');
      // Only default CJS interop is promised. Real Node builtins provide the
      // same named members through this explicitly selected default object.
      return { code: `${prefix}\nconst ${moduleName}={exports:{}};\n(function(module,exports){\n${code}\n}).call(${moduleName}.exports,${moduleName},${moduleName}.exports);\nexport default ${moduleName}.exports;\n`, map: null };
    },
  };
}

export async function bundleProfile({ rolldown, parseAst, input, virtualModules = {}, builtinManifests }) {
  const admitted = builtinManifests ? builtinMap(builtinManifests) : manifest;
  const build = await rolldown({
    input, platform: 'neutral', treeshake: false,
    plugins: [createProfilePlugin(parseAst, { virtualModules, builtinManifests })],
  });
  try {
    const generated = await build.generate({ format: 'esm', codeSplitting: false });
    if (generated.output.length !== 1) throw new Error('Profile requires exactly one ESM output chunk');
    const chunk = generated.output[0];
    const allowed = new Set(Object.values(admitted));
    if (chunk.imports.some(id => !allowed.has(id))) throw new Error(`Unexpected residual import: ${chunk.imports}`);
    const moduleIds = Object.keys(chunk.modules ?? {});
    if (moduleIds.some(id => /node_modules\/(?:buffer|unenv)|node-builtins/.test(id))) throw new Error('JavaScript builtin adapter leaked into profile');
    if (/__require/.test(chunk.code)) throw new Error('Residual dynamic builtin require');
    visit(parseAst(chunk.code), node => {
      if (node.type === 'CallExpression' && node.callee.type === 'Identifier' && node.callee.name === 'require') {
        throw new Error('Residual dynamic builtin require');
      }
    });
    return { code: chunk.code, imports: chunk.imports, moduleIds, admittedBuiltins: [...allowed].sort(),
      globalBufferPolicy: 'custom engine installs canonical native Buffer before application evaluation' };
  } finally { await build.close(); }
}
