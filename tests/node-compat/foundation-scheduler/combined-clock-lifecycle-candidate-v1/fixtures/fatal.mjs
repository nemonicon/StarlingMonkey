// Fresh disposable component only. Expected fatal ABI failure is not an error-code proof.
export async function run(){await new Promise(()=>setTimeout(()=>{throw new Error('RESOURCE_UNHANDLED_TIMER_CALLBACK');},0));return 'unreachable';}
