// Profile-only resource policy. No clock, entropy or host service is used.
const BudgetRangeError = RangeError;
const defineProperty = Object.defineProperty;
export const limits = Object.freeze({
  pathCodeUnits: 4096, patternCodeUnits: 1024, braceAlternatives: 128,
  braceOutputCodeUnits: 32768, braceDepth: 8, braceRewrites: 16,
  extglobDepth: 8, segments: 128, magicSegmentCodeUnits: 256, stateEstimate: 65536,
  workEstimate: 2000000, workUnits: 250000,
  stateKeyCodeUnits: 32768, globstarRecursion: 32, dfaCacheUnits: 262144,
});
export function limit(resource) {
  const error = new BudgetRangeError(`node:path.matchesGlob exceeds profile budget: ${resource}`);
  defineProperty(error, 'code', { value: 'ERR_SM_NODE_PATH_BUDGET', enumerable: true, configurable: true, writable: true });
  defineProperty(error, 'resource', { value: resource, enumerable: true, configurable: true, writable: true });
  throw error;
}
let remaining = 0;
let active = false;
export function tick(cost = 1) {
  remaining -= cost;
  if (remaining < 0) limit('matcher-work');
}
export function withBudget(operation) {
  if (active) limit('reentrant-matcher');
  active = true;
  remaining = limits.workUnits;
  try { return operation(); }
  finally { remaining = 0; active = false; }
}
export function preflight(path, pattern) {
  if (path.length > limits.pathCodeUnits) limit('path-code-units');
  if (pattern.length > limits.patternCodeUnits) limit('pattern-code-units');
  tick(path.length + pattern.length + 1);
  let braces = 0, ext = 0, inClass = false;
  for (let i = 0; i < pattern.length; i++) {
    const ch = pattern[i];
    if (ch === '[') inClass = true;
    else if (ch === ']') inClass = false;
    if (ch === '{' && ++braces > limits.braceDepth) limit('brace-depth');
    if (ch === '}' && braces) braces--;
    if (inClass) continue;
    if ('!?+*@'.includes(ch) && pattern[i + 1] === '(') {
      if (++ext > limits.extglobDepth) limit('extglob-depth');
      i++;
    } else if (ch === ')' && ext) ext--;
  }
  // Unsafe integer endpoints can fail to advance a Number-based range loop.
  for (const match of pattern.matchAll(/\{(-?\d+)\.\.(-?\d+)(?:\.\.(-?\d+))?\}/g)) {
    for (const value of match.slice(1).filter(value => value !== undefined)) {
      if (!Number.isSafeInteger(Number(value))) limit('brace-numeric-domain');
    }
    if (match[3] !== undefined && Number(match[3]) === 0) limit('brace-zero-step');
  }
  if (path.split(/[\\/]/).length > limits.segments) limit('path-segments');
}
export function precompile(path, patterns) {
  if (patterns.length > limits.braceAlternatives) limit('brace-alternatives');
  let chars = 0;
  for (const pattern of patterns) {
    // Brace substitution can create an extglob opener across a group boundary.
    // Recheck the bounded outputs before any matcher graph is constructed.
    preflight('', pattern);
    chars += pattern.length;
    if (chars > limits.braceOutputCodeUnits) limit('brace-output-code-units');
    const segments = pattern.split('/');
    if (segments.length > limits.segments) limit('pattern-segments');
    for (const segment of segments) {
      if (segment.length > limits.magicSegmentCodeUnits && /[?*\[\]()!+@]/.test(segment)) limit('magic-segment-code-units');
    }
  }
  // Charge a conservative four states per pattern code unit, before building
  // any matcher graph. Dynamic work charging below bounds data-dependent states.
  const states = 4 * (chars + patterns.length);
  if (states > limits.stateEstimate) limit('state-estimate');
  if ((path.length + 1) * states > limits.workEstimate) limit('work-estimate');
}
