/* Deterministic cost allocation and exact-cent variance bridge. */
function compareBank(d,base,current){
 const cents=v=>Math.round(Number(v)*100), sum=a=>a.reduce((s,v)=>s+v,0), k=(p,c)=>p+"|"+c;
 const pick=(name,sel)=>d[name].filter(x=>x.mes===sel.month&&x.cenario===sel.scenario);
 const b=Object.fromEntries(pick("custos",base).map(x=>[x.custo_id,x])), a=Object.fromEntries(pick("custos",current).map(x=>[x.custo_id,x]));
 const sides=[base,current];const source=[b,a], driver=sides.map(s=>pick("direcionadores",s)), cap=sides.map(s=>pick("capacidade",s)), vol=sides.map(s=>pick("volumetria",s));
 if(Object.keys(b).length!==12||Object.keys(a).length!==12)throw Error("Incomplete cost source");
 const rows=[],controls=[];
 const effects=["volume","mix","time","rate","fixed","source","allocation","idle"];
 function add(id,dest,channel,event,baseValue,currentValue,changes,evidence){
   const x=a[id];const all=Object.fromEntries(effects.map(e=>[e,changes[e]||0]));const delta=currentValue-baseValue;
   if(sum(Object.values(all))!==delta)throw Error("Bridge mismatch "+id+" "+dest);
   rows.push({id,product:dest,area:x.area_dona_id,category:x.categoria,nature:x.natureza,contract:x.contrato_id||id,driver:x.direcionador,channel,event,description:x.descricao,base:baseValue,current:currentValue,delta,effects:all,evidence});
 }
 function alloc(total,weights){
   const denom=sum(weights);if(denom<=0)throw Error("Missing or zero allocation driver");
   const raw=weights.map(w=>total*w/denom),out=raw.map(Math.floor);
   let remainder=total-sum(out);const order=raw.map((v,i)=>({i,f:v-out[i]})).sort((x,y)=>y.f-x.f||x.i-y.i);
   for(let j=0;j<remainder;j++)out[order[j%order.length].i]++;
   return out;
 }
 for(const id of Object.keys(b)){
  const x=b[id],y=a[id], totals=[cents(x.valor_total_brl),cents(y.valor_total_brl)];
  for(const z of [x,y])if(cents(z.valor_fixo_brl)+cents(z.valor_variavel_brl)!==cents(z.valor_total_brl))throw Error("Fixed/variable source mismatch "+id);
  const start=rows.length;
  if(y.direcionador==="minutos_tdabc"){
   const vv=vol.map(v=>v.filter(z=>z.minutos_ativos_por_caso!==""&&z.evento.startsWith("CONTESTACAO")).sort((u,v)=>k(u.produto_id,u.evento+u.canal).localeCompare(k(v.produto_id,v.evento+v.canal))));
   const keys=vv[0].map(z=>k(z.produto_id,z.evento+z.canal));
   if(vv[1].length!==keys.length||vv[1].some((z,i)=>k(z.produto_id,z.evento+z.canal)!==keys[i]))throw Error("TDABC event grain mismatch");
   const cs=cap.map(c=>c.find(z=>z.custo_id===id));if(cs.some(c=>!c||Number(c.capacidade_pratica_minutos)<=0))throw Error("Missing capacity");
   const capacities=cs.map(c=>Number(c.capacidade_pratica_minutos)), rates=totals.map((t,i)=>t/capacities[i]);
   const volumes=vv.map(v=>sum(v.map(z=>Number(z.volume))));if(volumes[0]<=0)throw Error("No baseline volume for mix");
   const consumed=vv.map(v=>sum(v.map(z=>Number(z.volume)*Number(z.minutos_ativos_por_caso))));
   if(cs.some((c,i)=>Math.abs(Number(c.minutos_consumidos)-consumed[i])>1e-6))throw Error("TDABC consumption mismatch");
   const attributed=[0,0];
   for(let i=0;i<keys.length;i++){
     const p=vv[0][i],q=vv[1][i],v0=Number(p.volume),v1=Number(q.volume),t0=Number(p.minutos_ativos_por_caso),t1=Number(q.minutos_ativos_por_caso);
     const steps=[v0*t0*rates[0],volumes[1]*v0/volumes[0]*t0*rates[0],v1*t0*rates[0],v1*t1*rates[0],v1*t1*rates[1]].map(Math.round);
     attributed[0]+=steps[0];attributed[1]+=steps[4];
     add(id,q.produto_id,q.canal,q.evento,steps[0],steps[4],{volume:steps[1]-steps[0],mix:steps[2]-steps[1],time:steps[3]-steps[2],rate:steps[4]-steps[3]}, {rule:"TDABC: volume → mix → time → rate",costs:[x,y],events:[p,q],capacity:cs,groupVolume:volumes,rateCents:rates,stepsCents:steps});
   }
   const idle=totals.map((t,i)=>t-attributed[i]);
   const over=consumed.some((v,i)=>v>capacities[i]);
   // A signed balance is preserved, but overcapacity is explicitly flagged as pending.
   add(id,over?"PENDING":"IDLE","NA","NA",idle[0],idle[1],{idle:idle[1]-idle[0]},{rule:"TDABC balance: group cost minus attributed cost",costs:[x,y],capacity:cs,consumed,attributedCents:attributed,balanceCents:idle,overcapacity:over});
   controls.push({id,kind:"capacity",ok:!over,base:consumed[0]/capacities[0],current:consumed[1]/capacities[1]});
  }else if(y.natureza==="direto"){
   const f0=cents(x.valor_fixo_brl),f1=cents(y.valor_fixo_brl),v0=cents(x.valor_variavel_brl),v1=cents(y.valor_variavel_brl),q0=Number(x.quantidade_faturavel),q1=Number(y.quantidade_faturavel);
   const contract=d.contratos.find(c=>c.contrato_id===id);const ref=Number(contract?.tarifa_unitaria_brl||0)*100;
   const billed=vol.map(v=>sum(v.filter(z=>z.produto_id===y.produto_direto_id&&z.evento===contract?.evento_faturavel).map(z=>Number(z.volume))));
   if(contract?.evento_faturavel&&(billed[0]!==q0||billed[1]!==q1))throw Error("Billable volume mismatch "+id);
   // Use the contractual tariff when it reconciles to the baseline; otherwise implied unit rate.
   const rate=q0>0?(Math.round(q0*ref)===v0?ref:v0/q0):ref;
   const volumeEffect=Math.round(q1*rate)-Math.round(q0*rate);
   add(id,y.produto_direto_id,"NA","NA",totals[0],totals[1],{fixed:f1-f0,volume:volumeEffect,rate:v1-v0-volumeEffect},{rule:"Direct: fixed cost, volume at base tariff, remaining variable price effect",costs:[x,y],contract,billedVolume:billed,baseRateCents:rate});
  }else if(y.natureza==="corporativo"){
   add(id,"CORP","NA","NA",totals[0],totals[1],{source:totals[1]-totals[0]},{rule:"Corporate cost remains corporate",costs:[x,y]});
  }else{
   const products=d.produtos.map(z=>z.produto_id);
   const weights=driver.map(list=>products.map(p=>Number(list.find(z=>z.direcionador===y.direcionador&&z.produto_id===p)?.quantidade??NaN)));
   if(weights.some(w=>w.some(v=>!Number.isFinite(v)||v<0)||sum(w)<=0)){
     add(id,"PENDING","NA","NA",totals[0],totals[1],{source:totals[1]-totals[0]},{rule:"Unallocated: incomplete or zero driver",costs:[x,y],weights});controls.push({id,kind:"driver",ok:false});
   }else{
     const v0=alloc(totals[0],weights[0]),vMid=alloc(totals[1],weights[0]),v1=alloc(totals[1],weights[1]);
     for(let i=0;i<products.length;i++)add(id,products[i],"NA","NA",v0[i],v1[i],{source:vMid[i]-v0[i],allocation:v1[i]-vMid[i]},{rule:"Shared: source cost at old weights, then new allocation weights",costs:[x,y],driver:y.direcionador,products,weights,allocationCents:[v0[i],vMid[i],v1[i]],share:[weights[0][i]/sum(weights[0]),weights[1][i]/sum(weights[1])]});
     controls.push({id,kind:"driver",ok:true});
   }
  }
  const dest=rows.slice(start);for(let i=0;i<2;i++)if(sum(dest.map(r=>i?r.current:r.base))!==totals[i])throw Error("Cost reconciliation mismatch "+id);
  controls.push({id,kind:"reconciliation",ok:true,base:totals[0],current:totals[1]});
 }
 return {base,current,rows,controls,effects,sourceBase:sum(Object.values(b).map(x=>cents(x.valor_total_brl))),sourceCurrent:sum(Object.values(a).map(x=>cents(x.valor_total_brl)))};
}

function simulateBank(d,selection,params){
 const clone=JSON.parse(JSON.stringify(d)), scenario="simulation", pick=r=>r.mes===selection.month&&r.cenario===selection.scenario;
 const names=["custos","direcionadores","capacidade","volumetria"];
 for(const name of names)clone[name].push(...d[name].filter(pick).map(r=>({...r,cenario:scenario})));
 const chosen=r=>r.mes===selection.month&&r.cenario===scenario;
 const money=x=>(Math.round(x*100)/100).toFixed(2);
 const cost=clone.custos.find(r=>chosen(r)&&r.custo_id===params.id);
 if(!cost)throw Error("Unknown scenario cost");const clamp=(v,min,max)=>Math.min(max,Math.max(min,Number(v)||0));
 const fixed=clamp(params.fixed,-100,200)/100, variable=clamp(params.variable,-100,200)/100, driver=clamp(params.driver,-100,200)/100, practical=clamp(params.practical,-90,200)/100, time=clamp(params.time,-100,200)/100;
 cost.valor_fixo_brl=money(Number(cost.valor_fixo_brl)*(1+fixed));cost.valor_variavel_brl=money(Number(cost.valor_variavel_brl)*(1+variable));cost.valor_total_brl=money(Number(cost.valor_fixo_brl)+Number(cost.valor_variavel_brl));
 if(cost.direcionador==="minutos_tdabc"){
   const cap=clone.capacidade.find(r=>chosen(r)&&r.custo_id===cost.custo_id);
   const records=clone.volumetria.filter(r=>chosen(r)&&r.evento.startsWith("CONTESTACAO")&&r.minutos_ativos_por_caso!=="");
   for(const r of records)r.minutos_ativos_por_caso=String(Math.round(Number(r.minutos_ativos_por_caso)*(1+time)*10000)/10000);
   const used=records.reduce((s,r)=>s+Number(r.volume)*Number(r.minutos_ativos_por_caso),0);
   cap.capacidade_pratica_minutos=String(Math.max(1,Math.round(Number(cap.capacidade_pratica_minutos)*(1+practical))));cap.minutos_consumidos=String(used);
   const drv=clone.direcionadores.find(r=>chosen(r)&&r.direcionador==="minutos_tdabc"&&r.produto_id==="P01");if(drv)drv.quantidade=String(used);
 } else if(cost.natureza==="indireto") {
   const drv=clone.direcionadores.find(r=>chosen(r)&&r.direcionador===cost.direcionador&&r.produto_id===params.product);
   if(drv)drv.quantidade=String(Number(drv.quantidade)*(1+driver));
 }
 return {data:clone,selection:{month:selection.month,scenario}};
}
