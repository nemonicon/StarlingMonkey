"""Export observed completed data only as UNREVIEWED. Never activate pins."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from benchmark_common import LABELS,OUTPUT,RECIPE,verify_frozen
def main():
    assert len(sys.argv)>=3,'FRESH_OUTPUT_JSON COMPLETED_LABEL [OTHER_COMPLETED_LABEL]'
    target=Path(sys.argv[1]).absolute();assert not target.exists()and not target.is_symlink()
    labels=sys.argv[2:];assert len(labels)==len(set(labels))and all(label in LABELS for label in labels)
    variants={label:None for label in LABELS}
    for label in labels:
        receipt,metadata,receipt_sha=verify_frozen(label)
        variants[label]={'state':'unreviewed-classic-benchmark-diagnostic-freeze-pin-candidate','variant':label,
          'engineSha256':receipt['engineSha256'],'engineBytes':receipt['engineBytes'],'metadataSha256':receipt['metadataSha256'],
          'freezeReceiptSha256':receipt_sha,'freezeRoot':str(OUTPUT),'recipeSha256':RECIPE,
          'sourceIndexSha256':receipt['sourceIndexSha256'],'sourceFiles':342,'addonFiles':2,
          'classicStreamsEnabled':metadata['classicStreamsEnabled'],'reviewRequired':True,'runtimeAcceptanceClaim':False}
    result={'schemaVersion':1,'state':'UNREVIEWED_CLASSIC_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V1','variants':variants,
      'requiresIndependentReviewAndSeparateRootAuthority':True,'consumerPinsModified':False,'runtimeAcceptanceClaim':False}
    with target.open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'output':str(target),'admitted':False,'labels':labels}))
if __name__=='__main__':main()
