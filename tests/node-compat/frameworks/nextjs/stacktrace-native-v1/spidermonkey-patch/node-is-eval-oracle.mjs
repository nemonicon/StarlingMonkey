// Dormant host-only oracle. Root may run pinned Node22; no native guest action.
import vm from 'node:vm';
const before=Object.getOwnPropertyDescriptor(Error,'prepareStackTrace');
function capture(){const x={};Error.captureStackTrace(x,capture);return x.stack.slice(0,2).map(f=>({isEval:f.isEval(),fileName:f.getFileName(),functionName:f.getFunctionName(),evalOriginType:typeof f.getEvalOrigin()}));}
const rows=[];
function keep(id,frames){rows.push({id,frames});}
try{
 Error.prepareStackTrace=(_,frames)=>frames;
 function ordinary(){return capture();}keep('ordinary-function',ordinary());
 keep('direct-eval-top',eval('capture()'));
 keep('direct-eval-nested-function',eval('(function nestedEval(){return capture()})')());
 keep('direct-eval-sourceURL',eval('capture()\n//# sourceURL=ordinary-source.js'));
 keep('direct-eval-nested-sourceURL',eval('(function nestedEval(){return capture()})\n//# sourceURL=ordinary-source.js')());
 keep('function-constructor',new Function('capture','return capture()')(capture));
 keep('function-constructor-nested',new Function('capture','return function nestedDynamic(){return capture()}')(capture)());
 keep('function-constructor-sourceURL',new Function('capture','return capture()\n//# sourceURL=ordinary-source.js')(capture));
 keep('async-function-constructor',await Object.getPrototypeOf(async function(){}).constructor('capture','return capture()')(capture));
 keep('generator-constructor',Object.getPrototypeOf(function*(){}).constructor('capture','yield capture()')(capture).next().value);
 keep('async-generator-constructor',(await Object.getPrototypeOf(async function*(){}).constructor('capture','yield capture()')(capture).next()).value);
 keep('managed-compileFunction',vm.compileFunction('return capture()',['capture'],{filename:'ordinary-source.js'})(capture));
 keep('managed-compileFunction-sourceURL',vm.compileFunction('return capture()\n//# sourceURL=ordinary-source.js',['capture'],{filename:'ordinary-source.js'})(capture));
 // Indirect eval obtains capture through an explicit fresh private VM context.
 const context=vm.createContext({capture});
 keep('indirect-eval-top',vm.runInContext('(0,eval)("capture()")',context,{filename:'ordinary-source.js'}));
 keep('indirect-eval-nested',vm.runInContext('(0,eval)("(function nestedIndirect(){return capture()})")()',context,{filename:'ordinary-source.js'}));
 keep('managed-script-sourceURL',vm.runInContext('capture()\n//# sourceURL=ordinary-source.js',context,{filename:'ordinary-source.js'}));
}finally{if(before)Object.defineProperty(Error,'prepareStackTrace',before);else delete Error.prepareStackTrace;}
console.log(JSON.stringify({schemaVersion:1,node:process.version,rows,guestExecuted:false}));
