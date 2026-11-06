"""Read/hash/AST/data checks only; no Rust CLI, Wasm encoder or guest call."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
refs=json.loads((HERE/'references.json').read_text());checks=0
def need(value,message):
    global checks
    assert value,message;checks+=1
def checked(row):
    raw=Path(row['path']).read_bytes();need(len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']);return raw
for key in ('normalizedInput','clockOnlyOldAdapter','coreReaderDonor','oldStubWasi','oldCli','splicerCore61685','existingNativeCli','currentGeneratedBindings','targetWorld','guestEntrySourceIndex','oldToolBuildContract','oldToolBuildInputLedger','toolCargoManifest'):
    checked(refs[key])
for row in refs['oldToolBuildReview'].values():
    if isinstance(row,dict) and 'path' in row:checked(row)
for row in refs['wirmApis']:checked(row)
need((HERE/'core_data.py').read_bytes()==checked(refs['coreReaderDonor']),'Exact pure DATA reader')
need((HERE/'after/stub_wasi.rs').read_bytes()==checked(refs['oldStubWasi'])+b'\n'+(HERE/'next-adapter-policy.rs').read_bytes(),'Append only tool method')
derivations=json.loads((HERE/'derivations.json').read_text());cli=(HERE/'after/splicer.rs').read_text()
for change in reversed(derivations['cli']):
    need(cli.count(change['after'])==1,'One CLI inverse seam');cli=cli.replace(change['after'],change['before'])
need(cli.encode()==checked(refs['oldCli']),'Exact old CLI reversal')
data=json.loads((HERE/'data-analysis.json').read_text())
need(data['flatAbiMismatches']==[] and len(data['flatAbiComparedPublicImports'])==55,'Actual primitive ABI comparison')
need(all(r['same'] and r['oldFlatType']==r['newGeneratedCFlatType'] for r in data['flatAbiComparedPublicImports']),'All55 complete signatures')
need([r['functionIndex'] for r in data['removedImports']]==[49,50,51,52,53,54,56],'Exact seven removed imports')
need(len(data['retainedImports'])==56,'Retained56 imports')
need((data['plannedFunctionImports'],data['plannedLocals'],data['plannedTotalFunctions'])==(56,100,156),'Counts without projection')
need(data['constructor']['removedInstructionRangeHalfOpen']==[10,32] and data['constructor']['newInstructionCount']==226,'Actual constructor range')
need(data['constructor']['newOps']==[[32,[2]],[65,[2]],[54,[2,8]]],'Badfd tag without handle')
need(len(data['models']['constructorNegatives'])==6 and data['models']['canonicalNoneSyntheticPayloads']==3,'Host DATA models')
for key in ('fullCanonicalResourceEnumCompatibilityProved','finalVersionMergeAnd13InterfaceGraphProved','actualAdapterTransformed','actualRustToolExecuted','adapterOrGuestExecuted'):
    need(data[key] is False,'No false actual proof '+key)
policy=(HERE/'next-adapter-policy.rs').read_text()
for marker in ['ops.len() != 245','ops[10]','ops[11]','ops[22]','ops[23]','ops[32]',
               'ops[..10]','&ops[32..]','local_index: 2','value: 2','offset: 8',
               'Operator::ReturnCallIndirect','body.i32_store8','unreachable_stub']:
    need(marker in policy,'Real API seam '+marker)
need('stub_stdio(' not in policy and 'stub_io_streams(' not in policy,'Preserve stdio/streams')
need('create_new(true)' in (HERE/'after/splicer.rs').read_text() and
     'set_permissions(fs::Permissions::from_mode(0o600))' in (HERE/'after/splicer.rs').read_text(),'Exclusive held-fd writer')
plan=json.loads((HERE/'adapter-plan.json').read_text())
for row in plan['afterimages']:checked(row['source'])
need(plan['actualNewCli'] is None and plan['actualAdapter'] is None and plan['rootAuthority'] is None,'No actual self-grant')
need(len(plan['standardSelectedInterfaces'])==13 and not any('sockets' in x for x in plan['standardSelectedInterfaces']),'No capability widening')
for q in HERE.glob('*.py'):ast.parse(q.read_text(),filename=str(q));checks+=1
print(json.dumps({'sourceDataChecks':checks,'rustCompiled':False,'adapterTransformed':False,'guestExecuted':False}))
