"""DATA-only publication checker. No CLI/native tool/guest execution."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,stat
HERE=Path(__file__).resolve().parent
def match(data,row):
    assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256'],row['path'];return data
def external(row):return match(Path(row['path']).read_bytes(),row)
def main(originals):
    idx=json.loads((HERE/'index.json').read_text());assert len(idx['files'])==len({r['path']for r in idx['files']})
    assert {r['path']for r in idx['files']}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p!=HERE/'index.json'}
    for r in idx['files']:match((HERE/r['path']).read_bytes(),r)
    result=json.loads((HERE/'root-result.json').read_text());a=json.loads((HERE/'authority.json').read_text())
    assert result['passed']is True and result['error']is None and result['state']=='NEXT_SELECTIVE_ADAPTER_CORE_DATA_VALIDATED_V1'
    assert result['sourceIndex']==a['sourceIndex']and result['actualCliBuildIndex']==a['actualCliBuildIndex']
    assert result['initialProtection']==result['finalProtection']=={'files':15433,'trees':5,'unchanged':True}
    assert result['engineOrGuestExecuted']is False and result['globalPinsOrPackageModified']is False
    assert result['final13InterfaceComponentVersionResourceClosureProved']is False
    assert result['rawCandidate']['sha256']==result['publishedAdapter']['sha256']=='d30ade5b0a146ab1f6cbb878322fa937ec19c4a2b09f7497e9f08e49fb13cfd7'
    assert result['rawCandidate']['bytes']==result['publishedAdapter']['bytes']==49672
    assert [x['label']for x in result['commands']]==['selective-cli','wasm-tools-validate','wasm-tools-print']
    for c in result['commands']:
        label=c['label'];t=json.loads(match((HERE/'raw'/label/'terminal.json').read_bytes(),c['terminal']))
        assert c['rawExitCode']==t['rawExitCode']==0 and c['clean']is True
        assert t['timeout']is False and t['forcedCleanup']is False and t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
        assert all(t[k]==[]for k in('signals','interruptedSignals','errors','remainingObservedPids'))
        started=json.loads((HERE/'raw'/label/'started.json').read_text());assert started['argv']==c['argv']and started['pid']==t['pid']
        assert started['timeoutSeconds']==(120 if label=='selective-cli' else 60)
        for stream in ('stdout','stderr'):match((HERE/'raw'/label/(stream+'.log')).read_bytes(),t[stream])
        assert(HERE/'raw'/label/'stderr.log').read_bytes()==b''
    assert result['commands'][0]['argv']==[a['pins']['newCli']['path'],'prune-next-http-adapter','--input',a['pins']['normalizedInput']['path'],'--output',a['rawCliOutput']]
    for item,operation in zip(result['commands'][1:],['validate','print']):
        assert item['argv']==[a['pins']['wasmTools']['path'],operation,a['rawCliOutput']]
    audit=json.loads(match((HERE/'raw/core-data-audit.json').read_bytes(),result['coreAudit']))
    assert(audit['originalBodiesCompared'],audit['originalBodiesIdenticalWithMapping'],audit['newCanonicalNoneStubs'],audit['newDefensiveTrapStubs'])==(93,92,3,4)
    assert(audit['functionImports'],audit['locals'],audit['totalFunctions'])==(56,100,156)
    assert audit['constructorChangedOnly']is True and audit['allLocalsTypesPreserved']is True and audit['nonDebugCustomSectionsIdentical']is True
    assert audit['metadataSha256']=='7485a77ee78375ef134c4cebca67142ded37cd68891130b0213986a27f84c072'and audit['metadataBytes']==10730
    assert audit['finalSelected13ComponentVersionResourceClosureProved']is False and len(audit['functionMapping'])==156
    match((HERE/'raw/wasm-tools-print/stdout.log').read_bytes(),result['wasmPrintedData'])
    if originals:
        norm=external(result['normalizedInput']);candidate=external(result['publishedAdapter']);external(result['rawCandidate']);external(result['nativeCli'])
        assert stat.S_IMODE(Path(result['publishedAdapter']['path']).stat().st_mode)==0o600 and Path(result['publishedAdapter']['path']).stat().st_nlink==1
        spec=importlib.util.spec_from_file_location('actual_core_data_audit',HERE/'audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        assert m.audit(norm,candidate)==audit
        for row in a['pins'].values():external(row)
    return dict(passed=True,actualSelectiveCliInvocations=1,dataToolCommands=2,ownedCommandsClean=3,
      originalBodiesAudited=93,newStubs=7,publishedAdapter=result['publishedAdapter'],originalBinaryAuditRepeated=originals,
      finalVersionResourceWorldGateProved=False,guestExecuted=False)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--originals',action='store_true');args=parser.parse_args()
    print(json.dumps(main(args.originals)))
