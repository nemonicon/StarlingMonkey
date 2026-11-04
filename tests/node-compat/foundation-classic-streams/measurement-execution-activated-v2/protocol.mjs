// Finite measurement domain. Importing this module performs no action.
export const ids=Object.freeze(['pipeline-view-64-hwm-plus1','pipeline-copy-64-hwm-plus1','pipeline-view-524288-hwm-plus1','pipeline-copy-524288-hwm-plus1']);
export const controls=Object.freeze(['checksum-input-only','byte-input-and-copy-construction-only','stream-construction-and-clean-close-only']);
export const cases=Object.freeze([...ids.map(id=>[id,false]),...controls.map(id=>[id,true])].flatMap(([id,control])=>[1,16].map(iterations=>Object.freeze({id,control,iterations}))));
export const arms=Object.freeze(['native-on','canonical-on','canonical-off','stock-on']);
export const comparisons=Object.freeze([Object.freeze({id:'same-engine-binding',arms:['native-on','canonical-on']}),Object.freeze({id:'whole-profile',arms:['canonical-on','canonical-off']}),Object.freeze({id:'different-stock-provider',arms:['canonical-on','stock-on']})]);
export const measurementCaseIndices=Object.freeze([1,3,5,7,9,11,13]);
export const protocol=Object.freeze({freshProcessesPerArmCaseComparison:3,warmups:3,samples:7,maxIterations:16,comparisons:3,commonCorrectnessCases:8,controlCorrectnessCases:6,measurementFamilies:7,timedWorkerProcesses:126,calibrationWorkers:42,totalWorkerProcesses:168,calibrationTargetMs:25,guestImports:[],schedulerBudgetRaised:false});
export function orderFor(repetition,pair){return repetition%2?[...pair].reverse():[...pair];}
export function chooseBatch(firstArmMs,secondArmMs){if(![firstArmMs,secondArmMs].every(value=>Number.isFinite(value)&&value>0))throw new RangeError('Positive public one-iteration costs required');return Math.max(1,Math.min(16,Math.floor(25/Math.max(firstArmMs,secondArmMs))));}
export function selectedCase(index){if(!Number.isInteger(index)||index<0||index>=cases.length)throw new RangeError('Finite fourteen-case domain required');return cases[index];}
