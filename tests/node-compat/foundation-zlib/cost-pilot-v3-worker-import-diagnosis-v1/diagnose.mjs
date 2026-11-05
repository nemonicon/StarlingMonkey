// Read/hash and module-link diagnosis only. Does not call the worker or loader.
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const source = new URL('../cost-pilot-timing-candidate-v3/', import.meta.url);
const indexPath = fileURLToPath(new URL('index.json', source));
const raw = await readFile(indexPath);
const index = {path:indexPath, sha256:createHash('sha256').update(raw).digest('hex'), bytes:raw.length};
if(index.sha256 !== 'c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9') throw Error('unexpected source index');
const authenticator = await import(new URL('source-families.mjs', source));
const audit = await authenticator.captureSourceFamilies(index);
let result;
try {
  const body = await import(new URL('worker-body.mjs', source));
  result = {moduleLinked:true, workerExportType:typeof body.runWorker};
} catch(error) {
  result = {moduleLinked:false, name:error.name, message:error.message, stack:error.stack};
} finally {
  await audit.recheck();
}
console.log(JSON.stringify({schemaVersion:1, sourceIndex:index,
  completeSourceFamilyAuditPassed:true, result,
  runWorkerCalled:false, loaderCalled:false, guestInvoked:false,
  originalWorkerFailureCauseProven:false}));
