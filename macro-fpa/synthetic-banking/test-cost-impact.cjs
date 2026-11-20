const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const dir=path.join(__dirname,'../../docs/banking-cost-sandbox');
const raw=fs.readFileSync(path.join(dir,'data.js'),'utf8');
const model=fs.readFileSync(path.join(dir,'model.js'),'utf8');
const {D,compare,simulate}=new Function(raw+'\n'+model+'\nreturn {D:BANK_DATA,compare:compareBank,simulate:simulateBank}')();
const selections=Array.from({length:12},(_,i)=>['orcado','realizado'].map(scenario=>({month:'2025-'+String(i+1).padStart(2,'0'),scenario}))).flat();
let pairs=0;
for(const base of selections)for(const cur of selections){
 const x=compare(D,base,cur);
 assert.equal(x.rows.reduce((s,r)=>s+r.base,0),x.sourceBase);
 assert.equal(x.rows.reduce((s,r)=>s+r.current,0),x.sourceCurrent);
 assert.equal(x.rows.reduce((s,r)=>s+r.delta,0),x.sourceCurrent-x.sourceBase);
 for(const r of x.rows)assert.equal(Object.values(r.effects).reduce((s,v)=>s+v,0),r.delta);
 assert.equal(x.rows.reduce((s,r)=>s+r.effects.allocation,0),0);
 if(base===cur)assert.ok(x.rows.every(r=>r.delta===0&&Object.values(r.effects).every(v=>v===0)));
 pairs++;
}
const base={month:'2025-07',scenario:'orcado'},current={month:'2025-07',scenario:'realizado'};
const original=compare(D,base,current);
const before=JSON.stringify(D);
for(const id of D.custos.filter(r=>r.mes===current.month&&r.cenario===current.scenario).map(r=>r.custo_id)){
 const s=simulate(D,current,{id});const m=compare(s.data,base,s.selection);
 assert.equal(m.sourceCurrent,original.sourceCurrent);
 assert.deepEqual(m.rows.map(r=>[r.id,r.product,r.current]),original.rows.map(r=>[r.id,r.product,r.current]));
}
const s=simulate(D,current,{id:'C04',product:'P01',driver:50});
const m=compare(s.data,base,s.selection);
assert.equal(m.sourceCurrent,original.sourceCurrent);
assert.ok(m.rows.some((r,i)=>r.current!==original.rows[i].current));
const direct=simulate(D,current,{id:'C01',volume:20,variable:10});
assert.ok(compare(direct.data,base,direct.selection).sourceCurrent>original.sourceCurrent);
const overload=simulate(D,current,{id:'I01',practical:-50,volume:20});
assert.ok(compare(overload.data,base,overload.selection).rows.some(r=>r.product==='PENDING'));
assert.equal(JSON.stringify(D),before);
console.log(pairs+' comparisons and simulation checks passed');
