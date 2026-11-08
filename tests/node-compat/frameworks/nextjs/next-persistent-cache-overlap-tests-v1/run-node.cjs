'use strict';
// Root-owned execution only. Node reference; does not construct or invoke a guest.
const fs=require('node:fs');
const path=require('node:path').posix;
const {runCacheSuite,describeThrown}=require('./cache-cases.cjs');
async function main(){
  if(process.version!=='v22.14.0'||process.argv.length!==4||process.execArgv.length!==0||process.env.NODE_OPTIONS!==undefined)throw new Error('Pinned Node22.14, no execution flags, and explicit applicationRoot/testRoot are required');
  const [applicationRoot,testRoot]=process.argv.slice(2);
  for(const p of [applicationRoot,testRoot])if(!p.startsWith('/')||p.length>2048||p.includes('\0')||path.normalize(p)!==p)throw new Error('Canonical absolute path required');
  const parent=path.dirname(testRoot);let existing=false;
  try{fs.lstatSync(testRoot);existing=true;}catch(error){if(!error||error.code!=='ENOENT')throw error;}
  if(existing)throw new Error('Refusing existing testRoot');
  const ps=fs.lstatSync(parent);if(!ps.isDirectory()||ps.isSymbolicLink()||fs.realpathSync(parent)!==parent)throw new Error('Existing canonical testRoot parent required');
  const app=fs.realpathSync(applicationRoot);if(app!==applicationRoot||testRoot===app||testRoot.startsWith(app+'/')||app.startsWith(testRoot+'/'))throw new Error('Application and fresh output roots must be disjoint');
  fs.mkdirSync(testRoot,{mode:0o700});
  const report={executionKind:'node-reference',guestExecuted:false,applicationGateWaived:false};
  let failed=false,primary;
  try{await runCacheSuite({applicationRoot,testRoot,report});}catch(error){failed=true;primary=error;}
  try{
    const body=Buffer.from(JSON.stringify(report,null,2)+'\n');if(body.length>262144)throw new Error('Report exceeds256KiB');
    fs.writeFileSync(path.join(testRoot,'result.json'),body,{flag:'wx'});
  }catch(publicationError){if(!failed){failed=true;primary=publicationError;}else process.stderr.write(JSON.stringify({secondaryPublicationFailure:describeThrown(publicationError)})+'\n');}
  process.stdout.write(JSON.stringify({state:report.state??'PREFLIGHT_FAILED',passed:report.passed===true,assertions:report.assertions??0,attempted:report.cases?.length??0,unattempted:report.unattemptedCaseIds??[],output:path.join(testRoot,'result.json'),guestExecuted:false})+'\n');
  if(failed)throw primary;
}
main().catch(error=>{process.stderr.write(JSON.stringify({originalFailure:describeThrown(error)})+'\n');process.exitCode=1;});
