// Keep the accepted Node helper immutable. Exclude its one Blob-construction
// input because this component gate must not invoke the native Blob at all.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
const hash=value=>createHash('sha256').update(value).digest('hex');
export function guestTextOracle(source, report) {
  assert.equal(hash(source),report.sources['node-checks.mjs']);
  const boundary='export async function blobChecks(consumers) {';
  assert.equal(source.split(boundary).length,2);
  let text=source.slice(0,source.indexOf(boundary));
  for(const part of ["const BlobCtor = Blob;\n","const BufferCtor = globalThis.Buffer;\n",",new BlobCtor(['a'])"]) {
    assert.equal(text.split(part).length,2,part);text=text.replace(part,'');
  }
  assert.doesNotMatch(text,/\bBlob\b|BlobCtor|BufferCtor|blobChecks/);
  const cases=structuredClone(report.text),group=cases.find(c=>c.name==='invalid byte chunks reject with error type and code');
  assert.equal(group.result.length,6);group.result=group.result.slice(0,5);
  return{source:text,cases,selection:{originalHelperSha256:hash(source),guestHelperSha256:hash(text),
    groups:cases.length,originalInvalidInputVectors:6,guestInvalidInputVectors:5,
    excluded:[{group:group.name,index:5,input:"new Blob(['a'])",reason:'Native Blob must not be invoked in this isolated gate; this vector remains Node-only.'}],
    modifications:['Trim unused blobChecks function','Remove unused Blob/Buffer capture declarations','Omit only the Blob invalid-input vector']}};
}
