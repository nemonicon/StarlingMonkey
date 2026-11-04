"""Read-only artifact verification, not an engine/guest invocation."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json
from benchmark_common import HERE,OUTPUT,checked,verify_frozen
def main():
    assert len(sys.argv)==4,'LABEL EXPECTED_FREEZE_RECEIPT_SHA EXPECTED_PACKET_INDEX_SHA'
    label,receipt_sha,index_sha=sys.argv[1:]
    checked(OUTPUT/(label+'-freeze-receipt.json'),receipt_sha)
    spec=importlib.util.spec_from_file_location('benchmark_frozen_verified_packet',HERE/'verify-packet.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.verify(index_sha)
    receipt,metadata,actual_sha=verify_frozen(label);assert actual_sha==receipt_sha and receipt['sourceIndexSha256']==index_sha
    print(json.dumps({'state':'ACTUAL_CLASSIC_BENCHMARK_DIAGNOSTIC_FREEZE_VERIFIED_NOT_EXECUTED','label':label,
      'engineSha256':receipt['engineSha256'],'engineBytes':receipt['engineBytes'],'metadataSha256':receipt['metadataSha256'],
      'freezeReceiptSha256':actual_sha,'recipeSha256':receipt['recipeSha256'],'sourceFiles':342,'addonFiles':2,
      'sourceRoot':str(OUTPUT/'source'),'enginePath':str(OUTPUT/(label+'.engine.wasm')),
      'classicStreamsEnabled':metadata['classicStreamsEnabled'],'diagnosticOnly':True,'guestExecuted':False}))
if __name__=='__main__':main()
