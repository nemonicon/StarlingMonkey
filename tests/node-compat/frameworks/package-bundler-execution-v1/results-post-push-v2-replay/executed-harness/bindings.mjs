// Structural lexical binding analysis for ordinary JavaScript ESTree/Oxc ASTs.
// It does not evaluate code, model TDZ/control flow or supply runtime globals.
class Scope {
  constructor(parent, kind) { this.parent = parent; this.kind = kind; this.bindings = new Set(); }
  has(name) { return this.bindings.has(name) || (this.parent !== null && this.parent.has(name)); }
  varScope() {
    let current = this;
    while (!['program', 'function-body', 'static-block'].includes(current.kind)) current = current.parent;
    return current;
  }
}

/** Return the original, unmodified Identifier nodes which refer to a selected
 * name with no lexical binding in this AST. Forward declarations count as
 * bindings; a TDZ reference is therefore bound, not an ambient-global use.
 * `names` is a Set or array of identifier names. */
export function findUnboundReferences(ast, names) {
  if (!ast || ast.type !== 'Program') throw new TypeError('Expected an Oxc/ESTree Program');
  if (!(names instanceof Set) && !Array.isArray(names)) throw new TypeError('Expected a Set or array of names');
  const selected = new Set(names);
  for (const name of selected) if (typeof name !== 'string') throw new TypeError('Identifier names must be strings');
  const references = [];
  const reference = (node, scope) => { if (selected.has(node.name)) references.push({ node, scope }); };

  function bindPattern(node, bindingScope, evaluationScope) {
    if (!node) return;
    switch (node.type) {
      case 'Identifier': bindingScope.bindings.add(node.name); return;
      case 'RestElement': bindPattern(node.argument, bindingScope, evaluationScope); return;
      case 'AssignmentPattern': bindPattern(node.left, bindingScope, evaluationScope); visit(node.right, evaluationScope); return;
      case 'ArrayPattern': for (const item of node.elements) bindPattern(item, bindingScope, evaluationScope); return;
      case 'ObjectPattern':
        for (const item of node.properties) {
          if (item.type === 'RestElement') bindPattern(item.argument, bindingScope, evaluationScope);
          else { if (item.computed) visit(item.key, evaluationScope); bindPattern(item.value, bindingScope, evaluationScope); }
        }
        return;
      default: throw new TypeError('Unsupported binding pattern: ' + node.type);
    }
  }

  function assignmentTarget(node, scope) {
    if (!node) return;
    switch (node.type) {
      case 'Identifier': reference(node, scope); return;
      case 'RestElement': assignmentTarget(node.argument, scope); return;
      case 'AssignmentPattern': assignmentTarget(node.left, scope); visit(node.right, scope); return;
      case 'ArrayPattern': for (const item of node.elements) assignmentTarget(item, scope); return;
      case 'ObjectPattern':
        for (const item of node.properties) {
          if (item.type === 'RestElement') assignmentTarget(item.argument, scope);
          else { if (item.computed) visit(item.key, scope); assignmentTarget(item.value, scope); }
        }
        return;
      default: visit(node, scope);
    }
  }

  function functionNode(node, parent) {
    // Body var/functions are deliberately not visible to parameter defaults.
    const parameters = new Scope(parent, 'function-parameters');
    if (node.type !== 'ArrowFunctionExpression') parameters.bindings.add('arguments');
    if (node.id) parameters.bindings.add(node.id.name);
    for (const parameter of node.params) bindPattern(parameter, parameters, parameters);
    const body = new Scope(parameters, 'function-body');
    visit(node.body, body);
  }

  function property(node, scope) {
    if (node.computed) visit(node.key, scope);
    visit(node.value, scope); // A shorthand value is a reference; its key is not.
  }

  function visit(node, scope) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) { for (const child of node) visit(child, scope); return; }
    if (typeof node.type !== 'string') return;
    switch (node.type) {
      case 'Program': for (const statement of node.body) visit(statement, scope); return;
      case 'Identifier': reference(node, scope); return;
      case 'Literal': case 'PrivateIdentifier': case 'ThisExpression': case 'Super':
      case 'MetaProperty': case 'TemplateElement': case 'EmptyStatement': case 'DebuggerStatement': return;
      case 'VariableDeclaration':
        for (const declaration of node.declarations) {
          bindPattern(declaration.id, node.kind === 'var' ? scope.varScope() : scope, scope);
          visit(declaration.init, scope);
        }
        return;
      case 'FunctionDeclaration': if (node.id) scope.bindings.add(node.id.name); functionNode(node, scope); return;
      case 'FunctionExpression': case 'ArrowFunctionExpression': functionNode(node, scope); return;
      case 'BlockStatement': {
        const block = new Scope(scope, 'block');
        for (const statement of node.body) visit(statement, block);
        return;
      }
      case 'StaticBlock': {
        const block = new Scope(scope, 'static-block');
        for (const statement of node.body) visit(statement, block);
        return;
      }
      case 'ClassDeclaration': case 'ClassExpression': {
        if (node.type === 'ClassDeclaration' && node.id) scope.bindings.add(node.id.name);
        const inner = new Scope(scope, 'class'); if (node.id) inner.bindings.add(node.id.name);
        visit(node.superClass, inner); visit(node.body, inner); return;
      }
      case 'ClassBody': for (const element of node.body) visit(element, scope); return;
      case 'MethodDefinition': case 'PropertyDefinition': case 'AccessorProperty': property(node, scope); return;
      case 'ObjectExpression':
        for (const item of node.properties) {
          if (item.type === 'SpreadElement') visit(item.argument, scope);
          else property(item, scope);
        }
        return;
      case 'MemberExpression': visit(node.object, scope); if (node.computed) visit(node.property, scope); return;
      case 'ImportDeclaration': for (const item of node.specifiers) scope.bindings.add(item.local.name); return;
      case 'ExportNamedDeclaration':
        visit(node.declaration, scope);
        if (!node.source) for (const item of node.specifiers) visit(item.local, scope);
        return;
      case 'ExportDefaultDeclaration': visit(node.declaration, scope); return;
      case 'ExportAllDeclaration': return;
      case 'CatchClause': {
        const caught = new Scope(scope, 'catch'); bindPattern(node.param, caught, caught); visit(node.body, caught); return;
      }
      case 'ForStatement': {
        const loop = new Scope(scope, 'loop');
        visit(node.init, loop); visit(node.test, loop); visit(node.update, loop); visit(node.body, loop); return;
      }
      case 'ForInStatement': case 'ForOfStatement': {
        const loop = new Scope(scope, 'loop');
        if (node.left.type === 'VariableDeclaration') visit(node.left, loop); else assignmentTarget(node.left, loop);
        visit(node.right, loop); visit(node.body, loop); return;
      }
      case 'SwitchStatement': {
        visit(node.discriminant, scope);
        const switched = new Scope(scope, 'switch');
        for (const item of node.cases) { visit(item.test, switched); for (const statement of item.consequent) visit(statement, switched); }
        return;
      }
      case 'LabeledStatement': visit(node.body, scope); return;
      case 'BreakStatement': case 'ContinueStatement': return;
      case 'AssignmentExpression': assignmentTarget(node.left, scope); visit(node.right, scope); return;
      case 'UpdateExpression': assignmentTarget(node.argument, scope); return;
      case 'WithStatement': throw new TypeError('Dynamic with-scope is outside this lexical analyzer');
      case 'ObjectPattern': case 'ArrayPattern': case 'AssignmentPattern': case 'RestElement':
        throw new TypeError('Pattern encountered outside a declaration or assignment target');
      default:
        if (node.type.startsWith('JSX') || node.type.startsWith('TS')) throw new TypeError('Expected lowered JavaScript, not ' + node.type);
        // Ordinary expression/control-flow nodes introduce no lexical scope.
        for (const [key, value] of Object.entries(node)) {
          if (['parent', 'type', 'loc', 'range', 'comments', 'tokens'].includes(key)) continue;
          if (value && typeof value === 'object') visit(value, scope);
        }
    }
  }

  visit(ast, new Scope(null, 'program'));
  return references.filter(({ node, scope }) => !scope.has(node.name)).map(({ node }) => node);
}
