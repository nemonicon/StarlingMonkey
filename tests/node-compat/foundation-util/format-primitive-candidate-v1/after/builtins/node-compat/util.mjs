// Optional bounded Node22 util facade. Host-independent; explicit deferred bindings.
import types from './util-types.mjs';
import {unsupported} from './util-unsupported.mjs';
import {inspectColors,inspectColorAliases,inspectStyles,inspectDefaults} from './util-metadata.mjs';
import {inherits,promisify,toUSVString} from './util-core.mjs';
export {types,inherits,promisify,toUSVString};
const Assign=Object.assign,ArrayIsArray=Array.isArray,TypeErrorCtor=TypeError,DefineError=Object.defineProperty;
export const TextEncoder=globalThis.TextEncoder;
export const TextDecoder=globalThis.TextDecoder;
export const MIMEParams=unsupported('node:util','MIMEParams');
export const MIMEType=unsupported('node:util','MIMEType');
export const _errnoException=unsupported('node:util','_errnoException');
export const _exceptionWithHostPort=unsupported('node:util','_exceptionWithHostPort');
export const _extend=unsupported('node:util','_extend');
export const aborted=unsupported('node:util','aborted');
export const callbackify=unsupported('node:util','callbackify');
export const debuglog=unsupported('node:util','debuglog');
export const deprecate=unsupported('node:util','deprecate');
// Bounded adaptation of Node22 internal/util/inspect.js format parser and
// primitive number/color rendering. LICENSE.util applies. No object inspection.
const FormatApply=Reflect.apply,FormatSlice=String.prototype.slice;
const FormatCode=String.prototype.charCodeAt,FormatIncludes=String.prototype.includes;
const FormatString=String,FormatNumber=Number,FormatIs=Object.is;
const FormatFinite=Number.isFinite,FormatNaN=Number.isNaN,FormatTrunc=Math.trunc;
const FormatRangeError=RangeError,FormatDeferred=unsupported('node:util','format');
function formatSlice(s,a,b){return FormatApply(FormatSlice,s,[a,b]);}
function formatUnsupported(reason){
  try{FormatDeferred();}catch(error){DefineError(error,'reason',{__proto__:null,value:reason,writable:true,enumerable:true,configurable:true});throw error;}
}
function formatLimit(limit){
  const error=new FormatRangeError('Bounded util.format limit exceeded: '+limit);
  for(const[key,value]of [['code','ERR_SM_NODE_UTIL_FORMAT_LIMIT'],['module','node:util'],['operation','format'],['profile','sm-node-22.14.0-m0.8'],['limit',limit]])DefineError(error,key,{__proto__:null,value,writable:true,enumerable:true,configurable:true});
  throw error;
}
function formatSeparator(s){
  let result='',i=s.length;const start=s[0]==='-'?1:0;
  for(;i>=start+4;i-=3)result='_'+formatSlice(s,i-3,i)+result;
  return i===s.length?s:formatSlice(s,0,i)+result;
}
function formatSeparatorEnd(s){
  let result='',i=0;for(;i<s.length-3;i+=3)result+=formatSlice(s,i,i+3)+'_';
  return i===0?s:result+formatSlice(s,i);
}
function formatNumberText(number){
  if(!defaults.numericSeparator)return FormatIs(number,-0)?'-0':FormatString(number);
  const integer=FormatTrunc(number),text=FormatString(integer);
  if(integer===number){
    if(!FormatFinite(number)||FormatApply(FormatIncludes,text,['e']))return text;
    return formatSeparator(text);
  }
  if(FormatNaN(number))return text;
  return formatSeparator(text)+'.'+formatSeparatorEnd(formatSlice(FormatString(number),text.length+1));
}
function formatColor(text,type){
  const style=inspect.styles[type];
  if(style!==undefined){const color=inspect.colors[style];if(color!==undefined)return '\u001b['+color[0]+'m'+text+'\u001b['+color[1]+'m';}
  return text;
}
function formatPrimitive(value){
  if(typeof value==='string')return value;
  const type=value===null?'null':typeof value;
  const text=type==='number'?formatNumberText(value):FormatString(value);
  return defaults.colors?formatColor(text,type):text;
}
export function format(...args){
  if(new.target)formatUnsupported('construction');
  if(args.length>32)formatLimit('arguments');
  let input=0;
  for(let i=0;i<args.length;i++){
    const value=args[i],type=typeof value;
    if(value!==null&&type!=='string'&&type!=='number'&&type!=='boolean'&&type!=='undefined')formatUnsupported('operand:'+type);
    if(type==='string'){if(value.length>16384)formatLimit('string-code-units');input+=value.length;if(input>65536)formatLimit('input-code-units');}
  }
  let a=0,str='',join='';const first=args[0];
  const append=text=>{if(str.length+text.length>65536)formatLimit('output-code-units');str+=text;};
  if(typeof first==='string'){
    // Node does not parse even %% when the format is the only argument.
    if(args.length===1)return first;
    let lastPos=0;
    for(let i=0;i<first.length-1;i++)if(FormatApply(FormatCode,first,[i])===37){
      const next=FormatApply(FormatCode,first,[++i]);let text;
      if(a+1!==args.length){
        switch(next){
          case 115:{const value=args[++a];text=typeof value==='number'?formatNumberText(value):FormatString(value);break;}
          case 100:text=formatNumberText(FormatNumber(args[++a]));break;
          case 37:append(formatSlice(first,lastPos,i));lastPos=i+1;continue;
          case 105:case 102:case 106:case 111:case 79:case 99:formatUnsupported('directive:%'+FormatString(first[i]));break;
          default:continue;
        }
        if(lastPos!==i-1)append(formatSlice(first,lastPos,i-1));
        append(text);lastPos=i+1;
      }else if(next===37){append(formatSlice(first,lastPos,i));lastPos=i+1;}
    }
    if(lastPos!==0){a++;join=' ';if(lastPos<first.length)append(formatSlice(first,lastPos));}
  }
  while(a<args.length){append(join);append(formatPrimitive(args[a]));join=' ';a++;}
  return str;
}
export const formatWithOptions=unsupported('node:util','formatWithOptions');
export const getCallSite=unsupported('node:util','getCallSite');
export const getCallSites=unsupported('node:util','getCallSites');
export const getSystemErrorMap=unsupported('node:util','getSystemErrorMap');
export const getSystemErrorMessage=unsupported('node:util','getSystemErrorMessage');
export const getSystemErrorName=unsupported('node:util','getSystemErrorName');
export const inspect=unsupported('node:util','inspect');
export const isArray=unsupported('node:util','isArray');
export const isBoolean=unsupported('node:util','isBoolean');
export const isBuffer=unsupported('node:util','isBuffer');
export const isDate=unsupported('node:util','isDate');
export const isDeepStrictEqual=unsupported('node:util','isDeepStrictEqual');
export const isError=unsupported('node:util','isError');
export const isFunction=unsupported('node:util','isFunction');
export const isNull=unsupported('node:util','isNull');
export const isNullOrUndefined=unsupported('node:util','isNullOrUndefined');
export const isNumber=unsupported('node:util','isNumber');
export const isObject=unsupported('node:util','isObject');
export const isPrimitive=unsupported('node:util','isPrimitive');
export const isRegExp=unsupported('node:util','isRegExp');
export const isString=unsupported('node:util','isString');
export const isSymbol=unsupported('node:util','isSymbol');
export const isUndefined=unsupported('node:util','isUndefined');
export const log=unsupported('node:util','log');
export const parseArgs=unsupported('node:util','parseArgs');
export const parseEnv=unsupported('node:util','parseEnv');
export const stripVTControlCharacters=unsupported('node:util','stripVTControlCharacters');
export const styleText=unsupported('node:util','styleText');
export const transferableAbortController=unsupported('node:util','transferableAbortController');
export const transferableAbortSignal=unsupported('node:util','transferableAbortSignal');
export const debug=debuglog;
for(const alias of inspectColorAliases)Object.defineProperty(inspectColors,alias.key,{get(){return this[alias.target];},set(value){this[alias.target]=value;},enumerable:alias.enumerable,configurable:alias.configurable});
inspect.custom=Symbol.for('nodejs.util.inspect.custom');inspect.colors=inspectColors;inspect.styles=inspectStyles;
const defaults=Object.seal(inspectDefaults);
Object.defineProperty(inspect,'defaultOptions',{enumerable:false,configurable:false,get:()=>defaults,set:value=>{if(value===null||typeof value!=='object'||ArrayIsArray(value)){const error=new TypeErrorCtor('Invalid inspect defaults');DefineError(error,'code',{__proto__:null,value:'ERR_INVALID_ARG_TYPE',writable:true,enumerable:true,configurable:true});throw error;}Assign(defaults,value);}});
const util={MIMEParams,MIMEType,TextDecoder,TextEncoder,_errnoException,_exceptionWithHostPort,_extend,aborted,callbackify,debug,debuglog,deprecate,format,formatWithOptions,getCallSite,getCallSites,getSystemErrorMap,getSystemErrorMessage,getSystemErrorName,inherits,inspect,isArray,isBoolean,isBuffer,isDate,isDeepStrictEqual,isError,isFunction,isNull,isNullOrUndefined,isNumber,isObject,isPrimitive,isRegExp,isString,isSymbol,isUndefined,log,parseArgs,parseEnv,promisify,stripVTControlCharacters,styleText,toUSVString,transferableAbortController,transferableAbortSignal,types};
export default util;
