import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import crypto from 'node:crypto';
const [address]=process.argv.slice(2);
const ascii=x=>JSON.stringify(x).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
const canonical=x=>x===null||typeof x!=='object'?ascii(x):Array.isArray(x)?'['+x.map(canonical).join(',')+']':
  '{'+Object.keys(x).sort().map(k=>ascii(k)+':'+canonical(x[k])).join(',')+'}';
const digest=x=>crypto.createHash('sha256').update(canonical(x)).digest('hex');
const same=(a,b)=>canonical(a)===canonical(b);
const client=createClient({chain:studionet});
async function read(functionName,args=[]){
  try{return await client.readContract({address,functionName,args});}
  catch{throw Error('Sanitized contract read failure: '+functionName);}
}
function transition(p,q,outcome,root,capacity){
  p=[...p];q=[...q];let evicted='',demoted='';
  if(outcome==='HIT'){
    const lane=p.includes(root)?p:q;
    if(!lane.includes(root))throw Error('Nonresident hit');
    lane.splice(lane.indexOf(root),1);q.push(root);
    if(q.length>Math.floor(capacity/2)){demoted=q.shift();p.push(demoted);}
  }else if(outcome==='MISS'){
    if(p.length+q.length>=capacity)evicted=p.shift();p.push(root);
  }else if(outcome!=='BYPASS')throw Error('Invalid outcome');
  return {probation:p,protected:q,evicted,demoted};
}
try{
  const cache=await read('get_cache');
  let before={probation:[],protected:[],sequence:0,head:''};
  const entries=new Map(),events=[];
  for(let i=0;i<cache.sequence;i++){
    const r=await read('get_event',[i]),{root,...body}=r;
    if(digest(body)!==root||!same(r.binding.before,before))throw Error('Journal chain');
    const active={probation:[],protected:[]},expired=[];
    for(const lane of ['probation','protected'])for(const id of before[lane]){
      const entry=entries.get(id);
      if(!entry)throw Error('Missing admitted entry');
      if(entry.expires<=r.binding.at)expired.push(id);else active[lane].push(id);
    }
    let expected;
    if(r.kind==='PURGE'){
      if(!same(r.expired,expired)||!expired.length)throw Error('Purge binding');
      expected=active;
    }else{
      const b=r.binding,residents=[...active.probation,...active.protected];
      if(!same(b.residents,residents)||!same(b.expired,expired)||b.capacity!==cache.capacity||b.retention!==cache.retention
          ||r.sources.length!==1+residents.length)throw Error('Access binding');
      const specs=[b.spec,...residents.map(id=>entries.get(id).source)];
      const ok=r.sources.every(s=>s.status==='OK');
      if(ok){
        r.sources.forEach((s,j)=>{
          if(s.url!==specs[j].url||s.hash!==specs[j].hash||s.http!==200)throw Error('Acquisition binding');
          if(j>0&&s.text!==entries.get(residents[j-1]).text)throw Error('Cached text changed');
        });
        if(r.labels.length!==residents.length||r.labels.some(x=>!['SAME','DIFFERENT','UNKNOWN'].includes(x)))throw Error('Vector shape');
        let outcome=r.labels.includes('UNKNOWN')||r.labels.filter(x=>x==='SAME').length>1?'BYPASS':r.labels.includes('SAME')?'HIT':'MISS';
        if(r.sources.slice(1).some((s,j)=>s.text===r.sources[0].text&&r.labels[j]!=='SAME'))outcome='BYPASS';
        if(r.outcome!==outcome)throw Error('Decision gate');
      }else if(r.outcome!=='BYPASS'||r.labels.length)throw Error('Failed evidence admitted');
      if(r.outcome==='MISS'){
        const entry={request:b.request,source:b.spec,text:r.sources[0].text,admitted:b.at,expires:b.at+cache.retention};
        if(digest(entry)!==r.representative||entries.has(r.representative))throw Error('Entry root');
        const stored=await read('get_entry',[r.representative]);
        if(!same(stored,entry))throw Error('Entry storage');
        entries.set(r.representative,entry);
      }else if(r.outcome==='HIT'){
        if(r.representative!==residents[r.labels.indexOf('SAME')])throw Error('Wrong representative');
      }else if(r.representative)throw Error('Bypass representative');
      const base=r.outcome==='BYPASS'?before:active;
      expected=transition(base.probation,base.protected,r.outcome,r.representative,cache.capacity);
      if(expected.evicted!==r.evicted||expected.demoted!==r.demoted)throw Error('Victim/demotion');
      const lookup=await read('get_receipt',[b.creator,b.nonce]);
      if(lookup.root!==root)throw Error('Principal-bound receipt');
    }
    const after={probation:expected.probation,protected:expected.protected,sequence:i+1};
    if(!same(after,r.after)||new Set([...after.probation,...after.protected]).size!==after.probation.length+after.protected.length
        ||after.probation.length+after.protected.length>cache.capacity||after.protected.length>Math.floor(cache.capacity/2))throw Error('Queue invariant');
    before={...after,head:root};
    events.push({sequence:i,kind:r.kind,nonce:r.binding.nonce,outcome:r.outcome,labels:r.labels,
      representative:r.representative,evicted:r.evicted,demoted:r.demoted,root});
  }
  const {capacity,retention,...actual}=cache;
  if(!same(actual,before))throw Error('Final layout mismatch');
  console.log(JSON.stringify({address,capacity,retention,...before,events,roots_verified:true,queue_policy_verified:true}));
}catch(error){console.error(error.message);process.exitCode=1;}
