// Appended as an IIFE only by the explicit test-only spliceBindings wrapper.
(()=>{
 const state={ticks:0};
 defineBuiltinModule('starling:test-initializer-observation',{state,default:state});
 import('starling:test-initializer-ticks').then(({nextTick})=>nextTick(()=>{state.ticks++;}));
})();
