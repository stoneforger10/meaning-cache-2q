import assert from 'node:assert/strict';
import {abi} from 'genlayer-js';
const {calldata}=abi;
for(const [name,args] of [['access',['n','stoneforger10','meaning-cache-2q','a'.repeat(40),'examples/a.txt','b'.repeat(64),1792000000]],['purge',[]],['get_cache',[]]]){
  const encoded=calldata.encode(calldata.makeCalldataObject(name,args,{}));
  assert.deepEqual(calldata.encode(calldata.decode(encoded)),encoded);
}
console.log('3 SDK calldata roundtrips passed');
