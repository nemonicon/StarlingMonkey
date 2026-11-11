// Pure comparison Source. Root supplies already-returned, bounded parsed JSON.
// No input is read, no expectation is manufactured and neither input is mutated.
const CASE_IDS = ['readable-pull', 'readable-cancel', 'writable-write-close', 'writable-abort',
  'transform-write-flush', 'bind-throw-reject', 'snapshot-throw-reject', 'queue-microtask'];
const EXECUTION_METADATA = ['executionKind', 'nodeVersion', 'execArgv', 'nodeOptionsPresent',
  'guestExecuted', 'boundaryMode', 'nativeBoundaryClaimRequiresExternalProof'];

function withoutExecutionMetadata(value) {
  return Object.fromEntries(Object.entries(value).filter(([key]) => !EXECUTION_METADATA.includes(key)));
}
function differences(left, right, path, out) {
  if (out.length >= 32 || Object.is(left, right)) return;
  if (left === null || right === null || typeof left !== typeof right || typeof left !== 'object' ||
      Array.isArray(left) !== Array.isArray(right)) { out.push(path); return; }
  if (Array.isArray(left)) {
    if (left.length !== right.length) out.push(`${path}.length`);
    for (let index = 0; index < Math.min(left.length, right.length) && out.length < 32; index++) {
      differences(left[index], right[index], `${path}[${index}]`, out);
    }
    return;
  }
  const keys = [...new Set([...Object.keys(left), ...Object.keys(right)])].sort();
  for (const key of keys) {
    if (out.length >= 32) break;
    if (!Object.hasOwn(left, key) || !Object.hasOwn(right, key)) out.push(`${path}.${key}`);
    else differences(left[key], right[key], `${path}.${key}`, out);
  }
}
function collected(report) {
  return report !== null && typeof report === 'object' && report.schemaVersion === 1 &&
    report.suite === 'PUBLIC_ALS_WEB_STREAM_CONTEXT_OBSERVATIONS_V1' && report.passed === true &&
    report.completedAllCases === true && report.fullNextAccepted === false &&
    report.nativeAsyncResourceTested === false && report.expectationsFrozen === false &&
    report.webStreamContextComparisonPerformed === false && Array.isArray(report.records) &&
    report.records.length === CASE_IDS.length && report.records.every((record, index) =>
      record.id === CASE_IDS[index] && record.fulfilled === true && record.primarySet === false &&
      record.passed === true && Array.isArray(record.events) && Array.isArray(record.checks) &&
      record.checks.every(check => check.passed === true) && record.cleanup?.knownComplete === true &&
      record.cleanup.pendingTasks === 0 && record.cleanup.heldLocks === 0 &&
      record.cleanup.liveDeadlineTimers === 0 && Array.isArray(record.cleanup.errors) && record.cleanup.errors.length === 0) &&
    report.records.reduce((count, record) => count + record.checks.length, 0) === 95;
}

export function compareWebStreamContextReports(node, guest) {
  const nodeCollected = collected(node), guestCollected = collected(guest);
  const nodeExecutionMetadataValid = nodeCollected && node.executionKind === 'node-reference' &&
    node.nodeVersion === 'v22.14.0' && Array.isArray(node.execArgv) && node.execArgv.length === 0 &&
    node.nodeOptionsPresent === false && node.guestExecuted === false && node.boundaryMode === 'public-only' &&
    node.nativeBoundaryClaimRequiresExternalProof === false;
  const guestExecutionMetadataValid = guestCollected && guest.executionKind === 'component-guest' &&
    guest.guestExecuted === true && guest.boundaryMode === 'native-boundaries' &&
    guest.nativeBoundaryClaimRequiresExternalProof === true &&
    !['nodeVersion', 'execArgv', 'nodeOptionsPresent'].some(key => Object.hasOwn(guest, key));
  const differingPaths = [];
  if (node !== null && guest !== null && typeof node === 'object' && typeof guest === 'object') {
    // Entire remaining reports, including every record/event/detail/check and unknown key.
    differences(withoutExecutionMetadata(node), withoutExecutionMetadata(guest), '$', differingPaths);
  } else differingPaths.push('$');
  return { schemaVersion: 1, state: 'PUBLIC_ALS_WEB_STREAM_CONTEXT_SAMPLE_COMPARISON_V1',
    nodeCollected, guestCollected, nodeExecutionMetadataValid, guestExecutionMetadataValid,
    executionMetadataComparedSeparately: [...EXECUTION_METADATA],
    allOtherFieldsComparedWithoutProjection: true, differingPaths, differenceListLimit: 32,
    passed: nodeExecutionMetadataValid && guestExecutionMetadataValid && differingPaths.length === 0,
    nativeBoundaryIdentityRequiresExternalProof: true, publicAsyncResourceRefusalComparedToNode: false,
    cloneCancelComparedHere: false, fullNextAccepted: false };
}
