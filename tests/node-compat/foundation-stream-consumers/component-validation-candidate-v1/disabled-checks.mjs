// Pure host assertions on finite native-bootstrap/guest records.
import assert from 'node:assert/strict';
export function assertDisabledManifests(manifests){
 assert(Array.isArray(manifests)&&manifests.length>0);let core=null;
 for(const manifest of manifests){assert(manifest.modules&&typeof manifest.modules==='object');for(const[canonical,module]of Object.entries(manifest.modules)){assert.notEqual(canonical,'node:stream/consumers');assert.notEqual(canonical,'stream/consumers');assert(Array.isArray(module.aliases));assert(!module.aliases.includes('stream/consumers'));if(canonical==='node:child_process'){assert.equal(core,null);core=manifest;}}}
 assert(core&&core.modules['node:buffer']);return{profileVersion:core.profileVersion,exports:[...core.modules['node:child_process'].exports].sort()};
}
export function assertSmoke(value,calls,core){
 assert.equal(value.calls,calls);const expected={sharedHex:'090203',copyHex:'010203',viewHex:'0203',sharedBacking:true,sharedOffset:2,viewBacking:true,viewOffset:3,copyIndependent:true,globalBuffer:true};assert.deepEqual(value.bytes,expected);assert.deepEqual(value.snapshot.bytes,expected);
 for(const fields of [value.call,value.construction,value.snapshot.call,value.snapshot.construction])for(const[key,wanted]of Object.entries({code:'ERR_SM_NODE_UNSUPPORTED',module:'node:child_process',operation:'exec',profile:core.profileVersion}))assert.deepEqual(fields[key],{own:true,type:'string',value:wanted});
 assert.deepEqual(value.namespace,core.exports);assert.equal(value.defaultNamed,true);assert.equal(value.allCallable,true);assert.equal(value.thenType,'undefined');assert.equal(value.defaultThenType,'undefined');
}
