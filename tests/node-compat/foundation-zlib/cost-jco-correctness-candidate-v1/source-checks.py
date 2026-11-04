#!/usr/bin/env python3
"""Bounded read/data checks only. No imported owner helper or action bodies."""
from pathlib import Path
import argparse, json, hashlib, re
D=Path(__file__).resolve().parent
REPO=D.parents[3]
checks=[]
def need(value,label):
    if not value: raise AssertionError(label)
    checks.append(label)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source_index(name,sha):
    p=D.parent/name/'index.json';raw=p.read_bytes();need(hashlib.sha256(raw).hexdigest()==sha,'exact parent index '+name)
    value=json.loads(raw);seen=set()
    for row in value['files']:
        name=row['path'];need(name not in seen and not Path(name).is_absolute() and all(x not in ('','.','..') for x in name.split('/')),'finite unique parent member '+name);seen.add(name)
        f=p.parent/name;need(f.is_file() and not f.is_symlink() and f.stat().st_size==row['bytes'] and digest(f)==row['sha256'],'original parent member bytes '+str(f))
    return len(value['files'])
def main():
    counts={}
    for name,sha in [
        ('cost-guest-oracle-candidate-v2','ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8'),
        ('cost-component-candidate-v1','a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9'),
        ('cost-component-wit-amendment-v1','e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa')]:counts[name]=source_index(name,sha)
    origin=json.loads((D/'copied-source.json').read_text())
    for row in origin['files']:
        p=Path(row['path']);need(p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],'exact original fixture/case source '+p.name)
        if 'copy' in row:need((D/row['copy']).read_bytes()==p.read_bytes(),'fixture copy byte-identical')
        else:
            text=p.read_text();found=re.search(r'export const cases=Object.freeze\((\[.*?\])\.map\(Object.freeze\)\)',text,re.S)
            need(found is not None,'actual cases export construction located');need(json.loads(found.group(1))==json.loads((D/row['derivedJSON']).read_text()),'all30 unchanged case records reconstructed')
    for row in origin['copies']:need(Path(row['origin']).read_bytes()==(D/row['copy']).read_bytes() and digest(D/row['copy'])==row['sha256'],'existing reviewed lifecycle primitive exact '+row['copy'])
    slots=json.loads((D/'implementation-slots.json').read_text());need(slots['runtimeActionsEnabled'] is False and all(v is None for v in slots['independentActualComponentReviews'].values()),'all three actual component review slots NULL')
    need(slots['actualGeneratedLoadingProtocol'] is None and slots['freshNodeMatrixDecoderImplementation'] is None,'no guessed generated loader or active Node decoder')
    need(slots['stockWasmtimeStringAbiProof'] is None and slots['largestWasmtimeArgvProof'] is None,'no invented WT string/argv proof')
    authority=json.loads((D/'root-authority.template.json').read_text());need(authority['actionAllowed'] is False and authority['correctnessSourceIndexSha256'] is None,'Root authority template unissued/NULL')
    need(authority['pilotOrTimingAllowed'] is False and authority['stockWasmtimeExecutionAllowed'] is False and authority['operationalAdmission'] is False,'no action-domain expansion')
    transport=(D/'transport.mjs').read_text();need('value=invoke(exportName,args)' in transport and 'value=await invoke' not in transport,'raw synchronous scalar avoids thenable assimilation')
    need(transport.index("'-raw.json'")<transport.index("need(typeof value==='string'"),'typed raw persistence precedes scalar type check')
    need(transport.index("'-counterexample.json'")<transport.index("exact mismatch; full counterexample"),'full counterexample precedes compact mismatch')
    need("propertiesRead:false" in transport and "value.toJSON" not in transport,'opaque carrier does not use toJSON')
    source=(D/'scenarios.mjs').read_text();need(source.index("prefix+'-setup','setup',[caseId]")<source.index("prefix+'-stage','stage',[JSON.stringify(record)]"),'crossdecode setup precedes stage')
    need(source.count("'-pair-counterexample.json'")==2,'separate/validate pair mismatches retain complete counterexamples')
    collector=(D/'collector.mjs').read_text();need('own.previousFullBytesUnchanged===true' in collector,'full prior-output stability field required')
    need('controlOperations' in collector and "step(this.#counts,'observe',1)" in collector,'named entries and codec calls checked separately')
    gate=(D/'admission.mjs').read_text();need('implementationReady(slots)' in gate and 'await import(' not in gate,'closed implementation gate before dynamic code')
    need('new immutable source cut is required' in gate,'caller-shaped slots cannot enable source revision')
    run=(D/'run.mjs').read_text();need('await correctnessPreflight(options)' in run and not any(x in run for x in ['DurableOutput.create','await import(','runOwnedCommand(']),'entry cannot open output or workers after NULL slots')
    node=(D/'node-edges.mjs').read_text();need('await decodeNodeStream(' in node and 'earlierNodeOwnDecodeIsNotReused:true' in node,'fresh existing Node decoder API schedule, not old decoded rows')
    need("binary?writeBytes(path,value):write(path,value)" in node,'Node binary and typed JSON retention remain separate')
    need('whole raw bytes/hash' not in run,'no placeholder runtime pass')
    for p in D.glob('*.mjs'):
        if p.name=='test-pure.mjs':continue
        text=p.read_text();need(not re.search(r"(?:from|import\()\s*['\"](?:node:zlib|fflate|.*(?:guest|runtime)\.mjs)",text),'no provider/codec/guest import in '+p.name)
    return {'schemaVersion':1,'state':'COST_JCO_CORRECTNESS_BOUNDED_SOURCE_DATA_CHECKS_PASSED','checks':len(checks),'labels':checks,'parentIndexedCounts':counts,'ownerHelpersOrActionsInvoked':False,'codecsOrGuestInvoked':False,'runtimeAcceptanceClaim':False}
if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--output',required=True);o=Path(args.parse_args().output);o.mkdir(mode=0o700)
    try:r=main()
    except Exception as e:
        r={'state':'SOURCE_CHECKS_FAILED','checks':len(checks),'labels':checks,'errorType':type(e).__name__,'message':str(e),'ownerHelpersOrActionsInvoked':False};(o/'results.json').write_text(json.dumps(r,indent=2)+'\n');raise
    (o/'results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'state':r['state'],'checks':r['checks'],'output':str(o)}))
