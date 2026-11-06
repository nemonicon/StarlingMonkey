// TEST ONLY mathematical model of proposed native state; never guest evidence.
export function createPerformanceModel(k){
 let ready=false,origin=0n,last=0n,epoch=0;
 const fail=code=>{const e=new Error(code);e.code=code;throw e;};
 function check(){if(!k.deployed())fail('ERR_SM_NODE_PERFORMANCE_INITIALIZATION');}
 function started(){check();if(!ready)fail('ERR_SM_NODE_STARTUP_REQUIRED');}
 const p={now(){started();const n=k.monotonic();if(n<last)fail('ERR_SM_NODE_PERFORMANCE_CLOCK');last=n;return Number(n-origin)/1e6;},get timeOrigin(){started();return epoch;}};
 function startPerformance(){check();if(ready)return origin;const before=k.monotonic(),wall=k.wall(),after=k.monotonic();if(after<before||wall.nanoseconds<0||wall.nanoseconds>=1e9||wall.seconds<0n||wall.seconds>8640000000000n||wall.seconds===8640000000000n&&wall.nanoseconds!==0)fail('ERR_SM_NODE_PERFORMANCE_CLOCK');const midpoint=before+(after-before)/2n,e=Number(wall.seconds)*1000+wall.nanoseconds/1e6;if(e>8640000000000000)fail('ERR_SM_NODE_PERFORMANCE_CLOCK');origin=midpoint;last=midpoint;epoch=e;ready=true;return origin;}
 return{performance:p,startPerformance};
}
