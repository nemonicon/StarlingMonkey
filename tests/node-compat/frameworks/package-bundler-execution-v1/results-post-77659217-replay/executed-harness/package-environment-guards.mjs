import {findUnboundReferences} from './frameworks/package-bundler-bindings-v2/bindings.mjs';

const optionalNames=new Set(['process','global','__dirname','__filename']);
const reserved=[...optionalNames,'require','module','__require'];
const union=(a,b)=>new Set([...a,...b]);
const intersection=(a,b)=>new Set([...a].filter(x=>b.has(x)));

// A deliberately finite syntactic guard recognizer, not a proof that arbitrary
// JavaScript cannot throw or mutate a global. Source code is never rewritten.
// The environment supplies no Node process/loader/filename globals. Normal
// typeof checks and the branches they guard can still use JavaScript's ordinary
// absent-global semantics (as React's optional process.emit fallback does).
export function runtimeReferenceAudit(ast) {
  const unbound=new Set(findUnboundReferences(ast,reserved));
  const blocked=[],guarded=[];
  function presence(expression,truth){
    if(!expression)return new Set();
    if(expression.type==='UnaryExpression'&&expression.operator==='!')return presence(expression.argument,!truth);
    if(expression.type==='LogicalExpression'){
      const a=presence(expression.left,truth),b=presence(expression.right,truth);
      return expression.operator==='&&' ? (truth?union(a,b):intersection(a,b)) :
        expression.operator==='||' ? (truth?intersection(a,b):union(a,b)) : new Set();
    }
    if(expression.type!=='BinaryExpression'||!['===','==','!==','!='].includes(expression.operator))return new Set();
    let probe=expression.left,literal=expression.right;
    if(literal?.type==='UnaryExpression') [probe,literal]=[literal,probe];
    if(probe?.type!=='UnaryExpression'||probe.operator!=='typeof'||probe.argument.type!=='Identifier'||
       !unbound.has(probe.argument)||!optionalNames.has(probe.argument.name)||literal?.type!=='Literal'||typeof literal.value!=='string')return new Set();
    const equal=expression.operator==='==='||expression.operator==='=='?truth:!truth;
    return (literal.value==='undefined'?!equal:equal)?new Set([probe.argument.name]):new Set();
  }
  function visit(node,present=new Set(),parent=null,key=''){
    if(!node||typeof node!=='object')return;
    if(node.type==='Identifier'&&unbound.has(node)){
      const optional=optionalNames.has(node.name);
      const isTypeof=parent?.type==='UnaryExpression'&&parent.operator==='typeof'&&key==='argument';
      (optional&&(isTypeof||present.has(node.name))?guarded:blocked).push(node);return;
    }
    if(node.type==='IfStatement'){
      visit(node.test,present,node,'test');
      visit(node.consequent,union(present,presence(node.test,true)),node,'consequent');
      visit(node.alternate,union(present,presence(node.test,false)),node,'alternate');return;
    }
    if(node.type==='ConditionalExpression'){
      visit(node.test,present,node,'test');
      visit(node.consequent,union(present,presence(node.test,true)),node,'consequent');
      visit(node.alternate,union(present,presence(node.test,false)),node,'alternate');return;
    }
    if(node.type==='LogicalExpression'){
      visit(node.left,present,node,'left');
      const after=node.operator==='&&'?presence(node.left,true):node.operator==='||'?presence(node.left,false):new Set();
      visit(node.right,union(present,after),node,'right');return;
    }
    // A closure can execute later; an outer presence test does not authorize its
    // body. Each function must guard its own ambient accesses.
    const inner=/^(?:FunctionDeclaration|FunctionExpression|ArrowFunctionExpression)$/.test(node.type)?new Set():present;
    for(const [field,value]of Object.entries(node)){
      if(['parent','loc','range','comments','tokens'].includes(field))continue;
      if(Array.isArray(value))for(const child of value)visit(child,inner,node,field);
      else if(value&&typeof value==='object')visit(value,inner,node,field);
    }
  }
  visit(ast);return {blocked,guarded};
}
