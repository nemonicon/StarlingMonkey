// Host-only source strings for three required successful paired components.
export const controls=[
 {name:'handled-throw',pair:'deployed-throw',expected:{handled:'TICK_DEPLOYED_THROW'},body:
  "return new Promise(resolve=>nextTick(()=>{try{throw new Error('TICK_DEPLOYED_THROW')}catch(error){resolve(JSON.stringify({handled:error.message}))}}))"},
 {name:'handled-rejection',pair:'deployed-rejection',expected:{handled:'TICK_DEPLOYED_REJECTION'},body:
  "return new Promise(resolve=>nextTick(()=>{const p=(async()=>{throw new Error('TICK_DEPLOYED_REJECTION')})();queueMicrotask(()=>p.catch(error=>resolve(JSON.stringify({handled:error.message}))));return p;}))"},
 {name:'finite-checkpoint-budget',pair:'checkpoint-work-limit',expected:{callbacks:65536},body:
  "return new Promise(resolve=>{let callbacks=0;function repeat(){callbacks++;if(callbacks===65536)resolve(JSON.stringify({callbacks}));else nextTick(repeat)}nextTick(repeat)})"}
];
