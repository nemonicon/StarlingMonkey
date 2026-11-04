export const identity={
 echoS64:value=>value,echoU64:value=>value,
 echoSignedList:value=>value,echoUnsignedList:value=>value,echoRecord:value=>value,
 echoResult(ok,value){if(ok)return value;throw value;},
};
