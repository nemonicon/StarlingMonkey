// Dependency-free validation of the exact JSON Schema vocabulary used by the
// adjacent manifest schema. Unknown schema keywords fail closed. Normal CMake
// builds consume the generated header and do not run this build-time code.
const vocabulary = new Set(['$schema', '$id', '$defs', '$ref', 'description',
  'type', 'required', 'properties', 'additionalProperties', 'propertyNames',
  'items', 'uniqueItems', 'minItems', 'minLength', 'pattern', 'minimum',
  'maximum', 'enum', 'const']);
const own = (object, key) => Object.hasOwn(object, key);
const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
function schemaVocabulary(schema, path = '$schema') {
  for (const key of Object.keys(schema)) if (!vocabulary.has(key)) throw new Error(`${path}: unsupported schema keyword ${key}`);
  for (const keyword of ['$defs', 'properties']) {
    for (const [key, value] of Object.entries(schema[keyword] ?? {})) schemaVocabulary(value, `${path}.${keyword}.${key}`);
  }
  for (const keyword of ['additionalProperties', 'propertyNames', 'items']) {
    if (isObject(schema[keyword])) schemaVocabulary(schema[keyword], `${path}.${keyword}`);
  }
}

export function validateManifest(manifest, rootSchema) {
  schemaVocabulary(rootSchema);
  function fail(path, message) { throw new Error(`Invalid Node profile manifest ${path}: ${message}`); }
  function validate(value, schema, path) {
    if (schema.$ref) {
      if (!schema.$ref.startsWith('#/')) fail(path, 'external schema references are forbidden');
      let target = rootSchema;
      for (const key of schema.$ref.slice(2).split('/').map(k => k.replaceAll('~1', '/').replaceAll('~0', '~'))) {
        if (!isObject(target) || !own(target, key)) fail(path, `unknown schema reference ${schema.$ref}`);
        target = target[key];
      }
      validate(value, target, path);
    }
    if (own(schema, 'const') && value !== schema.const) fail(path, `must equal ${JSON.stringify(schema.const)}`);
    if (schema.enum && !schema.enum.includes(value)) fail(path, `must be one of ${schema.enum.join(', ')}`);
    if (schema.type) {
      const valid = schema.type === 'object' ? isObject(value)
        : schema.type === 'array' ? Array.isArray(value)
        : schema.type === 'integer' ? Number.isSafeInteger(value)
        : schema.type === 'number' ? typeof value === 'number' && Number.isFinite(value)
        : typeof value === schema.type;
      if (!valid) fail(path, `expected ${schema.type}`);
    }
    if (typeof value === 'string') {
      if (schema.minLength !== undefined && [...value].length < schema.minLength) fail(path, 'string is too short');
      if (schema.pattern && !new RegExp(schema.pattern, 'u').test(value)) fail(path, 'string does not match schema pattern');
    }
    if (typeof value === 'number') {
      if (schema.minimum !== undefined && value < schema.minimum) fail(path, 'number below minimum');
      if (schema.maximum !== undefined && value > schema.maximum) fail(path, 'number above maximum');
    }
    if (Array.isArray(value)) {
      if (schema.minItems !== undefined && value.length < schema.minItems) fail(path, 'too few items');
      if (schema.items) value.forEach((item, index) => validate(item, schema.items, `${path}[${index}]`));
      // Every array in this restricted schema contains strings; item validation
      // above rejects objects before uniqueness is checked.
      if (schema.uniqueItems && new Set(value).size !== value.length) fail(path, 'duplicate items');
    }
    if (isObject(value)) {
      for (const key of schema.required ?? []) if (!own(value, key)) fail(path, `missing ${key}`);
      for (const [key, child] of Object.entries(value)) {
        if (schema.propertyNames) validate(key, schema.propertyNames, `${path} key ${JSON.stringify(key)}`);
        if (own(schema.properties ?? {}, key)) validate(child, schema.properties[key], `${path}.${key}`);
        else if (schema.additionalProperties === false) fail(path, `unexpected ${key}`);
        else if (isObject(schema.additionalProperties)) validate(child, schema.additionalProperties, `${path}.${key}`);
      }
    }
  }
  validate(manifest, rootSchema, '$');
  if (!Object.keys(manifest.modules).length) throw new Error('Node profile must select at least one module');
  const aliases = new Set();
  for (const [id, module] of Object.entries(manifest.modules)) {
    if (!module.exports.includes('default')) throw new Error(`${id}: explicit default binding required`);
    if (module.exports.includes('then')) throw new Error(`${id}: then export would make namespace assimilation observable`);
    for (const alias of module.aliases) {
      if (aliases.has(alias)) throw new Error(`${id}: alias collision ${alias}`);
      aliases.add(alias);
    }
    for (const name of [...(module.importOnlyExports ?? []), ...Object.keys(module.numericExports ?? {})]) {
      if (name === 'default' || !module.exports.includes(name)) throw new Error(`${id}: undeclared member ${name}`);
    }
  }
  return manifest;
}
