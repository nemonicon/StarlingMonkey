'use strict'
const uncurry=fn=>(receiver,...args)=>Apply(fn,receiver,args)
const Freeze=Object.freeze,GetOwn=Object.getOwnPropertyDescriptors,DefineAll=Object.defineProperties,SetProto=Object.setPrototypeOf
class SafeSet extends NativeSet {}
DefineAll(SafeSet.prototype,GetOwn(NativeSet.prototype))
SetProto(SafeSet.prototype,null)
Freeze(SafeSet.prototype);Freeze(SafeSet)
module.exports={
 AggregateError:AggregateErrorCtor,ArrayIsArray:NativeArray.isArray,
 ArrayPrototypeIncludes:uncurry(NativeArray.prototype.includes),ArrayPrototypeIndexOf:uncurry(NativeArray.prototype.indexOf),
 ArrayPrototypeJoin:uncurry(NativeArray.prototype.join),ArrayPrototypeMap:uncurry(NativeArray.prototype.map),
 ArrayPrototypePop:uncurry(NativeArray.prototype.pop),ArrayPrototypePush:uncurry(NativeArray.prototype.push),ArrayPrototypeSlice:uncurry(NativeArray.prototype.slice),
 Error:ErrorCtor,FunctionPrototypeCall:uncurry(Function.prototype.call),FunctionPrototypeSymbolHasInstance:uncurry(Function.prototype[NativeSymbol.hasInstance]),
 MathFloor:Math.floor,Number:NativeNumber,NumberIsInteger:NativeNumber.isInteger,NumberIsNaN:NativeNumber.isNaN,
 NumberMAX_SAFE_INTEGER:NativeNumber.MAX_SAFE_INTEGER,NumberMIN_SAFE_INTEGER:NativeNumber.MIN_SAFE_INTEGER,NumberParseInt:NativeNumber.parseInt,
 ObjectDefineProperties:DefineAll,ObjectDefineProperty:Define,ObjectGetOwnPropertyDescriptor:GetDescriptor,ObjectKeys:NativeObject.keys,ObjectSetPrototypeOf:SetProto,
 Promise:PromiseCtor,PromisePrototypeCatch:uncurry(PromiseCtor.prototype.catch),PromisePrototypeThen:uncurry(PromiseCtor.prototype.then),PromiseReject:PromiseCtor.reject.bind(PromiseCtor),PromiseResolve:PromiseCtor.resolve.bind(PromiseCtor),
 ReflectApply:Apply,RegExpPrototypeTest:uncurry(RegExp.prototype.test),SafeSet,String:NativeString,
 StringPrototypeSlice:uncurry(NativeString.prototype.slice),StringPrototypeToLowerCase:uncurry(NativeString.prototype.toLowerCase),
 StringPrototypeToUpperCase:uncurry(NativeString.prototype.toUpperCase),StringPrototypeTrim:uncurry(NativeString.prototype.trim),
 Symbol:NativeSymbol,SymbolFor:NativeSymbol.for,SymbolAsyncIterator:NativeSymbol.asyncIterator,SymbolHasInstance:NativeSymbol.hasInstance,SymbolIterator:NativeSymbol.iterator,
 SymbolDispose:disposeSymbol,SymbolAsyncDispose:asyncDisposeSymbol,TypedArrayPrototypeSet:uncurry(NativeUint8Array.prototype.set),Boolean:NativeBoolean,Uint8Array:NativeUint8Array
}
