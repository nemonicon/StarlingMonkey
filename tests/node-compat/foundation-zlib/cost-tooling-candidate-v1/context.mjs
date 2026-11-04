// Read/hash fresh publication contexts only. No package, codec or owner imports.
import {readFile,lstat,realpath,readdir,readlink} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,isAbsolute,relative} from 'node:path';
import {canonical,need,regular,sha,publicationProof} from './authority.mjs';
const MAX_SMALL=32*1024*1024;
const nativeRoot='/private/tmp/starling-node-compat/production-zlib-v4/native-freeze';
function local(name){need(typeof name==='string'&&name&&!name.includes('\\')&&!name.includes('\0')&&!isAbsolute(name)&&name.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Finite relative context member');return name;}
function freeze(value){if(value&&typeof value==='object'){for(const item of Object.values(value))freeze(item);Object.freeze(value);}return value;}
function inside(root,path){const value=relative(root,path);return value&&!value.startsWith('../')&&!isAbsolute(value);}
function canonicalAlias(path){return canonical(path).replace(/^\/tmp(?=\/|$)/,'/private/tmp');}
export async function streamHash(row,{maximumBytes=1024*1024*1024}={}){
 canonical(row.path);sha(row.sha256);need(Number.isSafeInteger(row.bytes)&&row.bytes>=0&&row.bytes<=maximumBytes,'Finite streamed file size');
 const parent=await realpath(dirname(row.path));need(parent===canonicalAlias(dirname(row.path)),'No unknown streamed ancestor alias');
 const info=await lstat(row.path);need(info.isFile()&&!info.isSymbolicLink()&&info.size===row.bytes,'Streamed ordinary expected-size file');
 const digest=createHash('sha256');let bytes=0;for await(const block of createReadStream(row.path,{highWaterMark:1024*1024})){digest.update(block);bytes+=block.length;}
 const after=await lstat(row.path);need(info.dev===after.dev&&info.ino===after.ino&&info.size===after.size&&info.mtimeMs===after.mtimeMs&&info.ctimeMs===after.ctimeMs,'Streamed file changed');
 need(bytes===row.bytes&&digest.digest('hex')===row.sha256,'Streamed file digest mismatch');return true;
}
export async function loadPublication(indexDescriptor,authority){
 await authority.recheck();
 const raw=await regular(indexDescriptor),index=JSON.parse(raw),root=await realpath(dirname(indexDescriptor.path));
 need(index.schemaVersion===1&&index.state==='FRESH_ZLIB350_COST_SOURCE_PUBLICATION_V1'&&index.toolingSourceIndexSha256===authority.checked.candidateIndexSha256,'Exact fresh source context');
 need(indexDescriptor.sha256===authority.checked.publicationIndexSha256,'Root action binds exact publication index');
 const initial=await lstat(root);need(initial.isDirectory()&&!initial.isSymbolicLink()&&(initial.mode&0o777)===0o700,'Owned private source root');
 need(index.rootIdentity?.device===initial.dev&&index.rootIdentity?.inode===initial.ino,'Publication root identity');
 const actualProof=await publicationProof(authority,indexDescriptor.sha256,index.rootIdentity);
 const records=new Map(),links=new Map();
 for(const value of index.files){local(value.path);need(!records.has(value.path),'Unique published source');records.set(value.path,freeze({...value,path:join(root,value.path),relativePath:value.path}));}
 for(const value of index.links){local(value.destination);local(value.mappedTarget);need(!links.has(value.destination),'Unique published link');links.set(value.destination,freeze({...value}));}
 async function member(name,collect=false){local(name);const row=records.get(name);need(row,'Unrecorded source member');await streamHash(row);if(!collect)return true;need(row.bytes<=MAX_SMALL,'Bounded collected source');return regular(row);}
 async function tree(){
  const files=new Set(),symlinks=new Set(),directories=new Set();
  async function walk(path,prefix){for(const entry of await readdir(path,{withFileTypes:true})){const name=prefix+entry.name,full=join(path,entry.name),info=await lstat(full);
    if(info.isSymbolicLink()){symlinks.add(name);const expected=links.get(name);need(expected,'Unknown publication symlink');need(await readlink(full)===expected.newLinkText&&await realpath(full)===join(root,expected.mappedTarget),'Only explicitly rebased tool link');}
    else if(info.isDirectory()){need((info.mode&0o777)===0o700,'Private publication directories');directories.add(name);await walk(full,name+'/');}
    else{need(info.isFile()&&info.nlink===1,'Regular publication file only');files.add(name);}
   }}
  await walk(root,'');need(files.size===records.size+2&&files.has('index.json')&&files.has('completion.json'),'Exact publication closure count');
  for(const name of records.keys())need(files.has(name),'Missing publication member');need(symlinks.size===links.size,'Exact link closure');
  need(Array.isArray(index.directories)&&directories.size===index.directories.length&&index.directories.every(v=>directories.has(local(v))),'Exact publication directory closure');
 }
 const context=JSON.parse(await member('context.json',true));
 const completionRow=authority.authority.sourcePublicationCompletion;need(completionRow&&canonicalAlias(completionRow.path)===join(root,'completion.json'),'Exact source completion descriptor');
 const completion=JSON.parse(await regular(completionRow));need(completion.schemaVersion===1&&completion.state==='SOURCE_PUBLICATION_PENDING_INDEPENDENT_REVIEW'&&completion.index.sha256===indexDescriptor.sha256&&completion.index.bytes===indexDescriptor.bytes&&completion.sourceIndexSha256===authority.checked.candidateIndexSha256,'Actual source completion binding');
 for(const key of['packagingRoot','toolchainRoot','packagerRoot','guestRoot','fflateBrowser','existingNativeFacts'])local(context[key]);
 need(context.maxRenderedInputUtf8Bytes===33554432&&context.maxBundleUtf8Bytes===33554432,'Approved32MiB source bounds');
 const facts=freeze(JSON.parse(await member(context.existingNativeFacts,true)));
 need(facts.state==='EXISTING_BUILD_VALIDATION_FACTS_NOT_COST_OR_OPERATIONAL_AUTHORITY','Existing facts are not action admission');
 async function recheck(){
  await authority.recheck();await actualProof.recheck();await regular(indexDescriptor);await regular(completionRow);const now=await lstat(root);need(now.dev===initial.dev&&now.ino===initial.ino&&(now.mode&0o777)===0o700,'Fresh source root changed');
  for(const row of records.values()){await streamHash(row);const info=await lstat(row.path);need((info.mode&0o7777)===row.mode&&info.nlink===1,'Source mode/link drift');}
  await tree();
 }
 async function readExternal(row){const path=canonicalAlias(row.path);need(inside(nativeRoot,path),'Only immutable genuine350 freeze references');need(row.bytes<=MAX_SMALL,'Bounded native JSON/source read');return regular(row);}
 async function hashExternal(row){need(inside(nativeRoot,canonicalAlias(row.path)),'Only immutable genuine350 freeze references');return streamHash(row);}
 async function frozenRow(row){need(inside(nativeRoot+'/source',canonicalAlias(row.path)),'Only actual frozen native source');const info=await lstat(row.path);return{...row,bytes:info.size};}
 const publicContext={publicationRoot:root,publicationIndexSha256:indexDescriptor.sha256,guestSourceIndexSha256:sha(context.guestSourceIndexSha256),packagingRoot:join(root,context.packagingRoot),toolchainRoot:join(root,context.toolchainRoot),packagerRoot:join(root,context.packagerRoot),guestRoot:join(root,context.guestRoot),fflateBrowserPath:join(root,context.fflateBrowser),existingNativeFacts:facts,
  readRepository:async name=>member(context.packagingRoot+'/'+local(name),true),readExternal,hashExternal,
  hashFrozenSource:async row=>hashExternal(await frozenRow(row)),readFrozenSource:async row=>readExternal(await frozenRow(row)),
  checkGuestFile:async path=>{canonical(path);const name=relative(root,path);need(inside(join(root,context.guestRoot),path),'Guest source stays in immutable publication');return member(name);},recheck};
 await recheck();return Object.freeze(publicContext);
}
export async function loadOracleRender(proof,authority,context){
 need(proof&&proof.index&&proof.result&&proof.module&&proof.oracle,'Separate actual Node oracle/render proof required');
 const index=JSON.parse(await regular(proof.index));need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length<=256,'Finite oracle/render index');
 const root=await realpath(dirname(proof.index.path));let result=null,moduleFound=0,oracleFound=0;const rows=[];let resultFound=0;const names=new Set();
 for(const entry of index.files){local(entry.path);need(!names.has(entry.path),'Unique oracle-proof member');names.add(entry.path);const row=freeze({path:join(root,entry.path),sha256:entry.sha256,bytes:entry.bytes});await streamHash(row,{maximumBytes:64*1024*1024});rows.push(row);
  if(row.path===canonicalAlias(proof.result.path)){need(row.sha256===proof.result.sha256&&row.bytes===proof.result.bytes,'Exact oracle result');result=JSON.parse(await regular(row));resultFound++;}
  if(row.path===canonicalAlias(proof.module.path)){need(row.sha256===proof.module.sha256&&row.bytes===proof.module.bytes&&row.bytes<=33554432,'Exact32MiB rendered oracle module');moduleFound++;}
  if(row.path===canonicalAlias(proof.oracle.path)){need(row.sha256===proof.oracle.sha256&&row.bytes===proof.oracle.bytes&&row.bytes<=33554432,'Exact actual Node oracle');oracleFound++;}
 }
 need(resultFound===1&&moduleFound===1&&oracleFound===1&&result.schemaVersion===1&&result.state==='ROOT_REVIEWED_ZLIB_COST_NODE_ORACLE_RENDER_V1'&&result.nodeVersion==='v22.14.0'&&result.codecCases===30&&result.nodeEncoderStreams===15,'New reviewed actual oracle/render result');
 need(result.toolingSourceIndexSha256===authority.checked.candidateIndexSha256&&result.sourcePublicationIndexSha256===authority.checked.publicationIndexSha256&&result.guestSourceIndexSha256===context.guestSourceIndexSha256&&result.nodeExecutableSha256==='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','Exact source/context/Node render proof');
 need(result.oracle?.sha256===proof.oracle.sha256&&result.oracle?.bytes===proof.oracle.bytes&&result.module?.sha256===proof.module.sha256&&result.module?.bytes===proof.module.bytes&&result.externalNodeActionExitCode===0&&result.operationalAdmission===false&&result.timingAllowed===false,'Root review binds actual artifacts and finite scope');
 const expected=freeze({...proof.module});
 async function recheck(){await authority.recheck();await regular(proof.index);for(const row of rows)await streamHash(row,{maximumBytes:64*1024*1024});}
 return Object.freeze({oracleRenderRoot:root,oracleInputsPath:proof.module.path,
  checkOracleFile:async path=>{need(path===expected.path,'Only exact separately sealed rendered module');return streamHash(expected,{maximumBytes:33554432});},recheck});
}
