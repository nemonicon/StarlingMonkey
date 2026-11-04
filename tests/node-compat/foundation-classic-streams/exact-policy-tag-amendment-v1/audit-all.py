"""Static review inventory of all64 bodies, with both mandatory amendments."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PARENT=BASE/'production-regression-candidate-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    original=json.loads((PARENT/'derivations.json').read_bytes())['records'];assert len(original)==64
    registrar=json.loads((BASE/'registrar-ancestry-oracle-amendment-v1/transformation-proof.json').read_bytes())
    policy=json.loads((HERE/'transformation-proof.json').read_bytes())
    mapped={}
    for root,proof in [(BASE/'registrar-ancestry-oracle-amendment-v1',registrar),(HERE,policy)]:
        for row in proof['records']:
            assert row['path']not in mapped
            data=(root/'proposed'/row['path']).read_bytes();assert sha(data)==row['afterSha256']
            mapped[row['path']]=data
    assert len(mapped)==7
    records=[];changed=[];tagged=[]
    for row in original:
        name=row['destinationPath'];before=(PARENT/name).read_bytes();assert sha(before)==row['afterSha256']
        after=mapped.get(name,before);text=after.decode()
        assert "'"+policy['oldStrictPolicyVersion']+"'" not in text,name
        if before!=after:changed.append(name)
        if policy['newStrictPolicyVersion']in text:tagged.append(name)
        lines=[{'line':n,'source':line.strip()}for n,line in enumerate(text.splitlines(),1)
            if re.search(r'(?:metadata|\.pin\b|admitted\.report|registrarSha256|spawnSync|\.version)',line)]
        records.append({'path':name,'beforeSha256':sha(before),'publishedSha256':sha(after),'byteIdentical':before==after,'metadataAndHostPathReviewLines':lines})
    assert len(changed)==7 and len(original)-len(changed)==57
    assert set(tagged)=={row['path']for row in policy['records']}
    gc=mapped['common/runners/allocator-gc.mjs'].decode()
    for old in ['admitted.pinsPath','admitted.pinBytes','admitted.report.commandsPath',"'reviewed-real-production-freeze'"]:assert old not in gc
    observations={
      'exactStrictVersions':'All five current strict-version comparisons use the complete Classic-source tag. No prefix/startsWith acceptance.',
      'patches':'Strict native patch9b2e and embedding-boundary patch84a91 remain unchanged in all four actual receipts; suffix changes only lineage version.',
      'currentSourceCounts':'Actual production guards use342. The allocator old293/m0.1 and delegated m0.8 checks remain separately pinned historical controls, not projected current metadata.',
      'moduleVersions':'Core m0.11, Events m0.10, StringDecoder m0.4, Assert m0.5, Querystring m0.6 and Util m0.7 are independent API versions and remain unchanged by Classic m0.12.',
      'pinSchema':'AllocatorGC now uses actual reviewed-real-classic-production-freeze state and pin commands/freeze paths; undefined old admission pinsPath/pinBytes/report.commandsPath are removed.',
      'registrar':'Mandatory7462 retains exact original three Node oracles and unchanged facade checks; finite19eef-to2848 Classic ancestry only.',
      'nodeSubprocessPaths':'Mandatory7462 rebinds Path to exact existing safe oracle copies with owned output, pre/post hashes and explicit cwd. Other five optional runners have no Node oracle subprocess.',
      'dynamicGuestImports':'Other runtime dynamic paths name generated files created in each fresh owned component output, or exact existing pinned source/entry modules. No factory fallback or public process injection.',
      'focusedFields':'Focused-preflight explicitly adds engineMetadataSha256 from actual pin receiptSHA; focused harness consumes this field. Common GC no longer requests nonexistent report commandsPath.',
      'capabilities':'Scalar OFF[], Runtime random-only0.2.10 and HTTP six standard0.2.10 contracts/type-only clock stay unchanged; component HTTP pin remains null.',
      'scope':'Static source/API-schema audit, not execution of any of the64 bodies or assurance that no future harness defect exists. Guest/facade/oracle bodies remain unchanged.'}
    (HERE/'all64-source-audit.json').write_text(json.dumps({'schemaVersion':1,'state':'ALL64_STATIC_METADATA_PATH_AND_LITERAL_AUDIT_COMPLETE','bodiesReviewed':64,
      'oldBodiesByteIdentical':57,'changedHostHarnessBodies':changed,'exactNewVersionBodies':tagged,'observations':observations,'records':records,'runtimeAcceptanceClaim':False},indent=2)+'\n')
    print(json.dumps({'bodies':64,'oldIdentical':57,'hostChanges':7,'exactTags':5}))
if __name__=='__main__':main()
