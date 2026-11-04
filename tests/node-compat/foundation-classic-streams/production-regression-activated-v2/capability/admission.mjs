import assert from 'node:assert/strict';
import {resolve,relative,isAbsolute} from 'node:path';
export function validatePinBoundary(root,paths=[]){
  assert.equal(typeof root,'string');assert(!root.includes('\0')&&isAbsolute(root));
  assert.equal(root,resolve(root),'Pin root must be canonical');
  for(const path of paths){assert.equal(typeof path,'string');assert(!path.includes('\0')&&isAbsolute(path));
    assert.equal(path,resolve(path),'Pin child path must be canonical');const rel=relative(root,path);assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel));}
}
