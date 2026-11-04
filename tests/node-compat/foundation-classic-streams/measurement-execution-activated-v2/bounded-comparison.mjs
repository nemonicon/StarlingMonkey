// Host correctness reporting only. Inputs are finite records parsed from JSON.
export class RecordedMismatch extends Error {
 constructor(label){super('Classic correctness mismatch: '+label);}
}
export async function requireExactJSON({label,actual,expected,context=null,writeCounterexample}){
 if(JSON.stringify(actual)===JSON.stringify(expected))return;
 // Preserve complete records before constructing even a compact error. Never
 // ask Node assert/inspect to expand a large guest trace difference.
 await writeCounterexample({label,actual,expected,context,runtimeAcceptanceClaim:false});
 throw new RecordedMismatch(label);
}
