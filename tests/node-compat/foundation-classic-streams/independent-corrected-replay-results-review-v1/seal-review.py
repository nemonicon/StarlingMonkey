#!/usr/bin/env python3
"""Seal only this owned independent text packet; invoke no project code."""
from pathlib import Path
import hashlib,json,datetime,ast
HERE=Path(__file__).resolve().parent

def row(path,relative=True):
    assert path.is_file() and not path.is_symlink()
    data=path.read_bytes();data.decode('utf-8')
    return {'path':str(path.relative_to(HERE)) if relative else str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}

def main():
    replay='replay' in HERE.name
    value=json.loads((HERE/'results.json').read_text())
    expected='INDEPENDENT_CORRECTED_EIGHT_STAGE_REPLAY_COMPLETED_RESULTS_REVIEW_PASSED' if replay else 'INDEPENDENT_FIVE_CORRECTED_FOLLOWON_RESULTS_VERIFIED_WITH_KNOWN_COUNTEREXAMPLES'
    assert value['state']==expected
    audit=json.loads((HERE/'final-interface-audit.json').read_text())
    assert audit['components']==(40 if replay else 20)
    for item in audit['audits']:
        actual=row(HERE/item['path']);assert actual['sha256']==item['sha256'] and actual['bytes']==item['bytes']
    for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=path.name)
    assert not any(path.name=='__pycache__' for path in HERE.rglob('*'))
    if replay:
        scope={'freshStages':8,'freshOptionalModules':6,'rootEvidenceReferencesRehashed':46,'physicalComponentOccurrences':value['physicalFinalComponentCount'],'declaredEngineComponentCounts':value['componentCountsByDeclaredActualEngine'],'coreGlueRelations':sum(bool(x['matches']) for x in value['coreGlueReview']),'wasmtimeOnlyAliasComponents':1,'ordinaryRunStringWorlds':37,'postBindingInspectResultAndApiWorlds':3,'outputRegularFilesRehashed':value['outputRegularFilesRehashed'],'historicalControls':value['historicalControls'],'sourceIndexedFiles':83,'rootInputRows':2293,'capabilityInputRows':2292,'runtimeInputRows':6414,'runtimeToolLinks':22,'frozenNativeFilesPerVariant':474,'nativeSources':342,'externalEmbeddingSources':3,'actualCurrentEngineSha256':value['actualEngineSha256'],'terminalEvidence':value['rootTerminalEvidence'],'terminalObservedByThisReader':False,'retainedCounterexamples':value['retainedCounterexamples'],'fatalDiscardCases':value['fatalDiscardCases']}
    else:
        scope={'gates':value['gates'],'physicalComponentOccurrences':value['actualDerivedComponentCount'],'rootArtifactRecordsPerGate':[11,80,81,32,27],'coreGlueRelations':len(value['coreGlueReview']),'sourceIndexedFiles':83,'rootInputRows':2293,'capabilityInputRows':2292,'runtimeInputRows':6414,'runtimeToolLinks':22,'frozenNativeFilesPerVariant':474,'nativeSources':342,'externalEmbeddingSources':3,'getterNodeReads':[1,1,0],'getterJcoWasmtimeReads':[0,0,0],'getterNodeAndJcoRawStdoutAvailable':False,'getterWasmtimeRawStdoutIndependentlyDecoded':True,'symbolRegistryParity':False,'gcScope':'Combined owners only','terminalObservedByThisReader':False}
    raw=value['rawHostEvidence']
    receipt={'schemaVersion':1,'state':'INDEPENDENT_CORRECTED_REPLAY_RESULTS_SEALED' if replay else 'INDEPENDENT_CORRECTED_FIVE_FOLLOWON_RESULTS_SEALED_WITH_COUNTEREXAMPLES','sealedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':row(HERE/'results.json'),'interfaceAudit':row(HERE/'final-interface-audit.json'),'scope':scope,'rootSourceFamilyIndexSha256':'a08aec2d8a28f6bb91251841b617be20820c23ab085e526d0dc107439b061c6e','sourcePeerIndexSha256':'85296020f2f792c01107e10d9602de5f586881c3cde3628e1c1b30226f6dbf1d','runtimeFamilyIndexSha256':'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78','reviewedNativePinsSha256':'182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb','nativeRootReviewSha256':'ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0','sourceContractVersion':'sm-classic-trace-source-v1','unchangedNativePaths':339,'changedNativePaths':3,'rawHostRecordAvailability':{k:v for k,v in raw.items() if k!='records'},'recordCountsAreNotInvocationCounts':True,'rawMissingStdoutInventedOrDecoded':False,'readers':[row(path) for path in sorted(HERE.glob('*.py'))],'readerMistakesOrPreparationNotes':[row(path) for path in sorted((HERE/'history').rglob('*')) if path.is_file()],'executedProjectHelperNodeGuestPreflightBuildComponentizerTranspilerHostOrReplay':False,'staticWasmToolsOnly':True,'nativeOrRuntimeAcceptanceClaim':False,'performanceClaim':False,'completeNodeCompatibilityClaim':False,'overallRoadmapComplete':False,'concreteBlockers':[],'limitations':value['limitations']}
    (HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    files=[]
    for path in sorted(HERE.rglob('*')):
        assert not path.is_symlink()
        if path.is_file() and path.name!='index.json':files.append(row(path))
    index={'schemaVersion':1,'state':receipt['state'],'files':files,'runtimeAcceptanceClaim':False,'performanceClaim':False}
    (HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps({'packet':HERE.name,'index':row(HERE/'index.json'),'receipt':row(HERE/'review-receipt.json'),'results':row(HERE/'results.json'),'files':len(files)}))
if __name__=='__main__':main()
