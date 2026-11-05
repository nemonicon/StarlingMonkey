// Separate expected packaging failure; never reaches snapshot with a live timer.
setTimeout(()=>{},0);
export function run(){return 'unreachable';}
