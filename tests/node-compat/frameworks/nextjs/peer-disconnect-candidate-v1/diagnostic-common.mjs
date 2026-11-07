// Pure declarations. No context capture, I/O, timers or resources during INIT.
export const peerMarker='NEXT_PEER_DISCONNECT_DIAGNOSTIC_V1';
export function errorData(value) {
  const record={type:typeof value,isNull:value===null};
  if(value===null||['string','boolean'].includes(typeof value))record.value=value;
  if(typeof value==='number')record.value=Number.isFinite(value)?value:String(value);
  if(value!==null&&(typeof value==='object'||typeof value==='function')) {
    for(const key of ['name','message','code','tag']) {
      const descriptor=Object.getOwnPropertyDescriptor(value,key);
      if(descriptor&&Object.hasOwn(descriptor,'value')&&
          ['string','boolean','number'].includes(typeof descriptor.value))
        record[key]=typeof descriptor.value==='string'?descriptor.value.slice(0,1024):
          typeof descriptor.value==='number'&&!Number.isFinite(descriptor.value)?String(descriptor.value):descriptor.value;
    }
    const payload=Object.getOwnPropertyDescriptor(value,'payload');
    if(payload&&Object.hasOwn(payload,'value')) {
      const p=payload.value;
      if(p!==null&&(typeof p==='object'||typeof p==='function')) {
        const tag=Object.getOwnPropertyDescriptor(p,'tag');
        if(tag&&Object.hasOwn(tag,'value')&&typeof tag.value==='string')record.payloadTag=tag.value;
      }
    }
  }
  return record;
}
export function createPeerState({AsyncLocalStorage,writeLog,origin}) {
  const storage=new AsyncLocalStorage();
  let firstLabel,ordinal=0,sequence=0;
  const requests=[];
  const emit=(request,phase,detail={})=>{
    const event={schemaVersion:1,marker:peerMarker,origin,sequence:++sequence,
      firstLabel:firstLabel??null,ordinal:request?.ordinal??0,label:request?.label??null,
      route:request?.route??null,phase,context:storage.getStore()??null,...detail};
    if(request) {
      if(request.events.length>=192)throw new RangeError('Peer diagnostic event cap');
      request.events.push(event);
    }
    writeLog(event);
    return event;
  };
  return {storage,emit,begin(label,route){
    if(typeof label!=='string'||label.length<1||label.length>128)throw new TypeError('Bounded case label required');
    if(requests.length>=12)throw new RangeError('Peer request cap');
    firstLabel??=label;
    const request={ordinal:++ordinal,label,route,events:[]};requests.push(request);
    return request;
  },inspect(){return{firstLabel:firstLabel??null,lastOrdinal:ordinal,requests:requests.map(r=>
    ({ordinal:r.ordinal,label:r.label,route:r.route,events:r.events.slice()}))};}};
}
