import buffer,{Buffer}from'node:buffer';
const snapshot=Buffer.allocUnsafe(32.9),snapshotBacking=snapshot.buffer,snapshotView=snapshot.subarray(4,12);
for(let i=0;i<snapshot.length;i++)snapshot[i]=i;
let calls=0;
function check(value,message){if(!value)throw new Error(message);}
export function run(){
  const a=Buffer.allocUnsafe(127.9),backing=a.buffer,view=a.subarray(3,8),empty=new Buffer.allocUnsafe(0);
  check([...a].every(byte=>byte===0),'zero initialization');a[3]=91;
  let roundtrips=0;for(let i=0;i<8;i++){
    check(Buffer.from('00017fff80','hex').toString('hex')==='00017fff80','native hex');roundtrips++;
  }
  check(buffer.Buffer===Buffer&&Buffer===globalThis.Buffer,'canonical constructor');
  check(Buffer.isBuffer(a)&&Buffer.isBuffer(view)&&Buffer.isBuffer(snapshot)&&Buffer.isBuffer(snapshotView)&&Buffer.isBuffer(empty),'private brands');
  check(a.length===127&&a.byteOffset===0&&backing.byteLength===127&&a.buffer===backing,'owned backing');
  check(view.buffer===backing&&view.byteOffset===3&&view.length===5&&view[0]===91,'shared view');
  check(empty.length===0&&empty.byteOffset===0&&empty.buffer.byteLength===0&&empty.buffer!==backing,'empty backing');
  check(snapshot.buffer===snapshotBacking&&snapshotView.buffer===snapshotBacking&&snapshotView.byteOffset===4,'snapshot backing');
  view[0]++;snapshotView[0]++;
  check(a[3]===92&&snapshot[4]===5+calls,'view writes');
  return JSON.stringify({calls:++calls,roundtrips,brands:5,ownedLength:a.length,viewOffset:view.byteOffset,snapshotByte:snapshot[4]});
}