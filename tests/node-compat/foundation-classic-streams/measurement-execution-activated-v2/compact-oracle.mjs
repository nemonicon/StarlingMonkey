// Data calculation only; derives every1..16 compact checksum from oracle iteration1.
export function compactExpected(oracle,index,iterations){
 if(!Number.isInteger(iterations)||iterations<1||iterations>16)throw new RangeError('Finite1..16');
 const one=oracle[index-index%2].expected;if(one.iterations!==1||one.records.length!==1)throw new Error('Exact one-iteration oracle needed');
 const record=one.records[0],step=(hash,value)=>Math.imul(hash^(value>>>0),16777619)>>>0;let aggregate=2166136261;
 for(let i=0;i<iterations;i++){aggregate=step(aggregate,record.checksum);aggregate=step(aggregate,record.units);}
 return{result:{scenario:one.scenario,iterations,checksum:aggregate|0,unsignedChecksum:aggregate>>>0,totalUnits:one.totalUnits*iterations,scheduledCallbacks:one.scheduledCallbacks*iterations,records:[]}};
}
