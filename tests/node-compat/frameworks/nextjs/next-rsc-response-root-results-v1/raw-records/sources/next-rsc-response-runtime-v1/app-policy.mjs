// Pure fresh-app DATA policy, inlined into the authenticated actor.
import assert from 'node:assert/strict';
export function relativeMember(name){
 assert.equal(typeof name,'string');assert(name&&!name.includes('\\')&&!name.includes('\0'));
 assert(name.split('/').every(x=>x!==''&&x!=='.'&&x!=='..'));return name;
}
export function sourceDirectoryNames(input){
 const names=input.directories.map(x=>relativeMember(x.path));assert.equal(new Set(names).size,names.length);
 return ['.',...names].sort();
}
export function ownedDirectoryNames(input,policy){
 assert.deepEqual(policy.additionalDirectories,['.next/cache']);
 const names=sourceDirectoryNames(input);assert(names.includes('.next'));assert(!names.includes('.next/cache'));
 assert(!input.files.some(x=>x.path==='.next/cache'||x.path.startsWith('.next/cache/')));
 return [...names,'.next/cache'].sort();
}
export function validateFreshInput(input,build,plan){
 const policy=plan.applicationSchema;
 assert.equal(policy.name,'fresh-next-standalone-root-excluded-v1');assert.equal(input.schemaVersion,1);
 assert.equal(policy.sourceDirectoriesExcludeRoot,true);assert.equal(input.root,plan.applicationSource);
 assert.equal(input.regularFiles,input.files.length);assert.equal(input.regularFiles,policy.files);
 assert.equal(input.bytes,input.files.reduce((sum,x)=>sum+x.bytes,0));assert.equal(input.bytes,policy.bytes);
 assert.equal(input.directories.length,policy.directoriesExcludingRoot);assert.deepEqual(input.symlinks,[]);
 assert.equal(new Set(input.files.map(x=>relativeMember(x.path))).size,input.files.length);
 const dirs=sourceDirectoryNames(input);assert(!input.directories.some(x=>x.path==='.'));
 assert(input.files.every(x=>!dirs.includes(x.path)));
 const owned=ownedDirectoryNames(input,policy);assert.equal(owned.length,policy.ownedDirectoriesIncludingRoot);
 assert.equal(build.schemaVersion,1);assert.equal(build.state,'NEXT_APP_BUILD_PASSED_UNREVIEWED_V1');
 assert.equal(build.passed,true);assert.deepEqual(build.errors,[]);assert.equal(build.originalInputsPreserved,true);
 assert.equal(build.outputRoot,plan.applicationBuildOutputRoot);assert.equal(build.sourceOnlyPreparation,false);
 assert.deepEqual(build.applicationInventoryDescriptor,plan.applicationInputs);assert.deepEqual(build.applicationInventory,input);
 const versions={next:'16.4.5',react:'19.3.1','react-dom':'19.3.1'};
 assert.deepEqual(build.installedVersions,versions);assert.deepEqual(build.installedVersionsBeforeNextBuild,versions);
 const root=plan.applicationRootIdentity;
 assert.deepEqual(Object.keys(root).sort(),['dev','ino','mode','nlink']);
 for(const value of Object.values(root))assert(Number.isSafeInteger(value)&&value>=0);
 assert(root.ino>0&&root.nlink>0&&root.mode<=0o777);return true;
}
