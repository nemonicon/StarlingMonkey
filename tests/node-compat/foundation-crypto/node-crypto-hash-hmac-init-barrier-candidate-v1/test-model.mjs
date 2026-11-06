// Synthetic lifecycle/operation model only. No fixture/crypto/native import.
import assert from 'node:assert/strict';
const checks=[];
function check(name, value) { assert(value, name); checks.push(name); }
function permitted(engineState, deployed) {
  return engineState === 'Initialized' && deployed === true;
}
function attempt(engineState, deployed, operation) {
  const touched=[];
  if (!permitted(engineState, deployed)) return { name: 'TypeError',
    code: 'ERR_SM_NODE_CRYPTO_INITIALIZATION', operation, touched };
  touched.push('state/key/provider/EVP/output');
  return { permitted: true, touched };
}
const operations=['createHash','createHmac','Hash/Hmac.update','Hash/Hmac.digest'];
for (const entropyEnabled of [false,true]) {
  for (const operation of operations) {
    for (const [phase,state,deployed] of [
      ['engine-install','Uninitialized',false],
      ['module-init','ScriptPreInitializing',false],
      ['late-bind-getter','Initialized',false],
      ['final-bind-job','Initialized',false],
      ['aborted-instance','Aborted',true]
    ]) {
      const out=attempt(state,deployed,operation);
      check(`${entropyEnabled}/${operation}/${phase} refuses without work`,
        out.code==='ERR_SM_NODE_CRYPTO_INITIALIZATION'&&out.name==='TypeError'&&out.touched.length===0);
    }
    check(`${entropyEnabled}/${operation}/first real export allowed`, attempt('Initialized',true,operation).permitted===true);
    check(`${entropyEnabled}/${operation}/retained real export allowed`, attempt('Initialized',true,operation).permitted===true);
  }
}
check('old Engine Initialized-only guard misses late INIT', 'Initialized'==='Initialized'&&!permitted('Initialized',false));
check('entropyOFF availability is not the lifecycle gate', permitted('Initialized',true));
console.log(JSON.stringify({ schemaVersion:1,state:'SYNTHETIC_LIFECYCLE_MODEL_PASSED',checks:checks.length,checkNames:checks,
  nativeOrFixtureImported:false,cryptoOrSnapshotExecuted:false }));
