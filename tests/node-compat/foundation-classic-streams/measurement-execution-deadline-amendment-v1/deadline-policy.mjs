// Operational deadlines, never throughput measurements or universal adequacy.
export const deadlinePolicy=Object.freeze({publicCaseMs:600000,pilotMs:600000,sourceAuditMs:180000,workerHardMaxMs:7200000,cleanupGraceMs:5000,heartbeatMs:30000,startupFloorMs:120000,workSafetyFactor:2,warmups:3,samples:7});
export function workerBudget(pilot,iterations){
 if(!pilot||![pilot.firstBatchMs,pilot.wholeProcessElapsedMs].every(value=>Number.isFinite(value)&&value>0))throw new RangeError('Recorded positive public pilot costs required');
 if(!Number.isInteger(iterations)||iterations<1||iterations>16)throw new RangeError('Chosen finite1..16 iterations required');
 const sampleAndWarmupMs=pilot.firstBatchMs*iterations*(3+7),firstBatchAllowanceMs=pilot.firstBatchMs*iterations;
 const observedStartupAndEvidenceMs=Math.max(0,pilot.wholeProcessElapsedMs-pilot.firstBatchMs),startupAllowanceMs=120000+2*observedStartupAndEvidenceMs;
 const requestedMs=Math.ceil(2*sampleAndWarmupMs+firstBatchAllowanceMs+startupAllowanceMs);
 return Object.freeze({iterations,pilotIterationMs:pilot.firstBatchMs,pilotWholeProcessMs:pilot.wholeProcessElapsedMs,sampleAndWarmupMs,firstBatchAllowanceMs,observedStartupAndEvidenceMs,startupAllowanceMs,workSafetyFactor:2,requestedMs,hardMaxMs:7200000,admitted:requestedMs<=7200000,
  scope:'Operational estimate only. Insufficient budget refuses the whole arm/family; no clipping, sample reduction or N change.'});
}
