#!/usr/bin/env python3
"""Seal only this new independent UTF-8 text packet; execute no reviewed helper."""
from pathlib import Path
import datetime, hashlib, json, stat
HERE=Path(__file__).resolve().parent

def row(path, relative=False):
    before=path.lstat()
    assert stat.S_ISREG(before.st_mode)
    data=path.read_bytes()
    data.decode('utf-8')
    after=path.lstat()
    assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
    return {'path':str(path.relative_to(HERE)) if relative else str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}

def main():
    results=json.loads((HERE/'results.json').read_text())
    native=json.loads((HERE/'native-results.json').read_text())
    assert results['state']=='INDEPENDENT_CORRECTED_CLASSIC_COMPLETED_RESULTS_REVIEW_PASSED'
    assert native['state']=='CORRECTED_CLASSIC_CURRENT_SOURCE_NATIVE_REHASH_PASSED'
    receipt={
      'schemaVersion':1,'state':'INDEPENDENT_CORRECTED_CLASSIC_COMPLETED_RESULT_REVIEW_SEALED',
      'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'results':row(HERE/'results.json',True),'nativeResults':row(HERE/'native-results.json',True),
      'readers':[row(HERE/name,True) for name in ['verify-native.py','verify-results.py','seal-review.py']],
      'verifiedFiles':[row(HERE/name,True) for name in ['native-verified-files.json','verified-files.json']],
      'sourceFamilyIndexSha256':results['activatedIndex']['sha256'],
      'runtimePinsSha256':results['pinsSha256'],'rootNativeReviewSha256':results['rootAuthoritySha256'],
      'composedRootReceipt':results['composedRootReceipt'],'composedRootReferencesRehashed':12,
      'sourceFilesRehashed':26,'consumedInputsRehashed':6414,'toolTrees':2,'toolLinks':22,
      'sourceContractVersion':'sm-classic-trace-source-v1','actualNativePaths':342,'unchangedNativePaths':339,'changedNativePaths':3,'externalEmbeddingPaths':3,
      'nativeFreezes':{k:{'engineSha256':v['engine']['sha256'],'filesRehashed':v['frozenFilesRehashed']} for k,v in native['native'].items()},
      'enabledVariants':{k:{'publishedFiles':v['publishedFilesRehashed'],'components':len(v['structuralWitAudits']),'imports':v['externalComponentImports'],'coreGlueRelations':len(v['exactCoreComponentGlueRelations']),'ordinaryNodeGroups':19,'deferredCallNew':48,'overloads':17,'limits':3,'initializers':65,'retainedCalls':3,'freshJco':1,'freshWasmtime':1} for k,v in results['variants'].items()},
      'disabled':{'publishedFiles':10,'admissionDenials':8,'componentBuilt':False,'hostExecuted':False},
      'terminalExitEvidence':{k:v['terminalExitEvidence'] for k,v in results['variants'].items()} | {'disabled-off':results['disabled']['terminalExitEvidence']},
      'allPastRawTerminalStatusesObservedByThisReader':False,
      'freshStaticWitAudits':15,'exactCoreComponentGlueRelations':12,
      'nodeOracleCompared':True,'newNodeOracleExecuted':False,
      'rawMainAndSuccessfulCleanWasmtimeStdoutAvailable':False,
      'missingRawStdoutNotIndependentlyDecoded':True,'fatalRawStreamsChecked':True,
      'separateNode11EvidenceTransferred':False,
      'gcScope':'Combined owners and callbacks only; no isolated queue-root/prototype-key proof',
      'fatalScope':'Failed instances discarded; generic trap does not identify error origin; own fields checked in source and recorded clean-control parsed observations',
      'readerMistakesPreserved':['history/native-reader-attempt1.py.txt','history/native-reader-attempt1.failure.txt','history/reader-correction1.json'],
      'executedProjectHelpers':False,'guestHostBuildOrJavaScriptAdmissionExecuted':False,
      'nativeOrRuntimeAcceptanceClaim':False,'performanceClaim':False,'completeNodeStreamsClaim':False,'overallRoadmapComplete':False,
      'limitations':results['limits'],'concreteBlockers':[]}
    (HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    files=[]
    for path in sorted(HERE.rglob('*')):
        assert not path.is_symlink()
        if path.is_file() and path.name!='index.json':files.append(row(path,True))
    index={'schemaVersion':1,'state':'INDEPENDENT_CORRECTED_CLASSIC_COMPLETED_RESULT_REVIEW_SEALED','files':files,'runtimeAcceptanceClaim':False,'performanceClaim':False}
    (HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps({'index':row(HERE/'index.json',True),'receipt':row(HERE/'review-receipt.json',True),'results':row(HERE/'results.json',True),'files':len(files)}))
if __name__=='__main__':main()
