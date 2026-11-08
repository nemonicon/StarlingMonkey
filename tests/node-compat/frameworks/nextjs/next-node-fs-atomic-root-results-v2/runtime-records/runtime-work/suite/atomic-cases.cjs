'use strict';
// Calling the suite is deployed work. Module evaluation performs no filesystem IO or entropy draw.
const fs=require('node:fs');
const path=require('node:path').posix;
const {Buffer}=require('node:buffer');
const {createHash}=require('node:crypto');
const Module=require('node:module');
const PIN=Object.freeze({sha256:'6bc8642f72edfd01f57072915271eb8fe5e959fe56c2f44005f6d9a258abb0a7',bytes:1300});
const IDS=Object.freeze(['create-new','existing-no-replacement','missing-parent-error']);
const hash=b=>createHash('sha256').update(b).digest('hex');
function requireCondition(ok,message){if(!ok)throw new Error(message);}
function describeThrown(value){
  const result={type:value===null?'null':typeof value};
  if(value===null||['string','boolean','number'].includes(typeof value))result.value=value;
  if(value!==null&&(typeof value==='object'||typeof value==='function'))for(const key of ['name','message','code','operation','module']){
    try{const d=Object.getOwnPropertyDescriptor(value,key);if(d&&Object.hasOwn(d,'value')&&typeof d.value==='string')result[key]=d.value.slice(0,1024);}
    catch{result.descriptorUnavailable=true;}
  }
  return result;
}
function canonical(p){requireCondition(typeof p==='string'&&p.startsWith('/')&&p.length<=2048&&!p.includes('\0')&&path.normalize(p)===p,'Canonical absolute path required');return p;}
function directory(p){const s=fs.lstatSync(p);requireCondition(s.isDirectory()&&!s.isSymbolicLink()&&fs.realpathSync(p)===p,'Canonical existing directory required');}
function inventory(root){
  const names=fs.readdirSync(root).sort();requireCondition(names.length<=8,'Owned suite entry cap');
  const files=[];
  for(const name of names){
    requireCondition(typeof name==='string'&&name!=='.'&&name!=='..'&&!name.includes('/'),'Ordinary owned filename required');
    const p=path.join(root,name),s=fs.lstatSync(p);requireCondition(s.isFile()&&!s.isSymbolicLink()&&s.nlink===1&&s.size<=4096&&fs.realpathSync(p)===p,'Bounded unique owned file required');
    const b=fs.readFileSync(p);requireCondition(b.length===s.size,'Stable owned file size');files.push({path:name,bytes:b.length,sha256:hash(b)});
  }
  return {files,logicalBytes:files.reduce((n,x)=>n+x.bytes,0),modesOrInodeIdentityOrWasiRightsInferred:false};
}
async function runNodeFsAtomicSuite({applicationRoot,testRoot,report}){
  requireCondition(report&&typeof report==='object'&&!Array.isArray(report),'Caller-owned partial report required');
  Object.assign(report,{schemaVersion:1,state:'NEXT_NODE_FS_ATOMIC_SUITE_RUNNING_V1',passed:false,plannedCaseIds:[...IDS],cases:[],unattemptedCaseIds:[...IDS],assertions:0,
    actualNextHelperUsed:false,fakeDependencies:false,helperImplementationModified:false,legacyGenerationGateChanged:false,fullNextAccepted:false,
    scope:'Sequential publish-if-absent helper calls in one owned directory. No atomic increment/replacement, CAS, concurrent process, fsync, crash or route-cache persistence proof.'});
  let active;
  function check(ok,label){const row={label,passed:ok===true};active.assertions.push(row);report.assertions++;if(!row.passed)throw new Error(label);}
  try{
    applicationRoot=canonical(applicationRoot);testRoot=canonical(testRoot);directory(applicationRoot);directory(testRoot);
    requireCondition(testRoot!==applicationRoot&&!testRoot.startsWith(applicationRoot+'/')&&!applicationRoot.startsWith(testRoot+'/'),'Source and owned test roots must be disjoint');
    requireCondition(fs.readdirSync(testRoot).length===0,'Owned suite root must initially be empty');
    report.applicationRoot=applicationRoot;report.testRoot=testRoot;
    const helperPath=path.join(applicationRoot,'node_modules/next/dist/server/lib/node-fs-methods.js'),s=fs.lstatSync(helperPath);
    requireCondition(s.isFile()&&!s.isSymbolicLink()&&s.nlink===1&&s.size===PIN.bytes&&fs.realpathSync(helperPath)===helperPath,'Pinned real Next helper required');
    const source=fs.readFileSync(helperPath);requireCondition(source.length===PIN.bytes&&hash(source)===PIN.sha256,'Actual Next helper Source bytes required');
    report.nodeFsHelper={path:helperPath,...PIN};
    const req=Module.createRequire(path.join(applicationRoot,'server.js'));
    requireCondition(req('next/package.json').version==='16.4.5','Actual pinned Next package required');
    const nodeFs=req('next/dist/server/lib/node-fs-methods.js').nodeFs;
    requireCondition(nodeFs&&typeof nodeFs.writeFileAtomic==='function'&&typeof nodeFs.readFile==='function','Real Next nodeFs exports required');
    report.actualNextHelperUsed=true;
    const destination=path.join(testRoot,'published.txt'),original=Buffer.from('next-node-fs-atomic:create:v1\n'),replacement=Buffer.from('must-not-replace:v1\n');
    const cases=[
      ['create-new',async()=>{
        const returned=await nodeFs.writeFileAtomic(destination,original);active.returned=returned;
        check(returned===true,'New destination publication returns true');
        check(Buffer.from(await nodeFs.readFile(destination)).equals(original),'New destination contains exact original bytes');
        check(JSON.stringify(fs.readdirSync(testRoot).sort())===JSON.stringify(['published.txt']),'Successful publication removes its temporary file');
        check(fs.lstatSync(destination).isFile()&&fs.lstatSync(destination).nlink===1,'Published destination is one ordinary remaining link');
      }],
      ['existing-no-replacement',async()=>{
        const before=fs.readFileSync(destination),returned=await nodeFs.writeFileAtomic(destination,replacement);active.returned=returned;
        check(returned===false,'Existing destination returns false for EEXIST');
        check(fs.readFileSync(destination).equals(before)&&before.equals(original),'Existing destination bytes are not replaced');
        check(JSON.stringify(fs.readdirSync(testRoot).sort())===JSON.stringify(['published.txt']),'EEXIST publication removes its temporary file');
        check(fs.lstatSync(destination).nlink===1,'EEXIST leaves the original destination as one remaining link');
      }],
      ['missing-parent-error',async()=>{
        let caught=false,primary;
        try{await nodeFs.writeFileAtomic(path.join(testRoot,'absent/value.txt'),original);}catch(error){caught=true;primary=error;}
        active.originalRejection=caught?describeThrown(primary):null;
        if(!caught){check(false,'Missing parent must reject');return;}
        if(active.originalRejection.code!=='ENOENT')throw primary;
        check(true,'Missing parent preserves the original ENOENT rejection');
        check(JSON.stringify(fs.readdirSync(testRoot).sort())===JSON.stringify(['published.txt']),'Rejected missing-parent call adds no owned entry');
        check(fs.readFileSync(destination).equals(original),'Rejected call leaves the existing destination unchanged');
      }],
    ];
    for(let i=0;i<cases.length;i++){
      const[id,body]=cases[i];active={id,passed:false,assertions:[]};report.cases.push(active);report.unattemptedCaseIds=IDS.slice(i+1);
      try{await body();active.passed=true;}catch(error){active.error=describeThrown(error);throw error;}
    }
    report.inventory=inventory(testRoot);report.state='NEXT_NODE_FS_ATOMIC_SUITE_PASSED_V1';report.passed=true;return report;
  }catch(error){
    report.state='NEXT_NODE_FS_ATOMIC_SUITE_FAILED_V1';report.originalFailure=describeThrown(error);
    try{if(report.testRoot)report.partialInventory=inventory(report.testRoot);}catch(secondary){report.secondaryInventoryFailure=describeThrown(secondary);}
    throw error;
  }
}
module.exports=Object.freeze({runNodeFsAtomicSuite,describeThrown});
