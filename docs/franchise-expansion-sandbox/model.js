function createScenario(seed=42){
 let n=seed>>>0;const rand=()=>{n=(1664525*n+1013904223)>>>0;return n/4294967296};
 const hubs=[["Osasco",-23.532,-46.792],["Barueri",-23.511,-46.877],["São Paulo",-23.551,-46.634],["Guarulhos",-23.454,-46.533],["ABC",-23.659,-46.532],["Cotia",-23.604,-46.919],["Santana de Parnaíba",-23.444,-46.918]];
 const segments=[["Grocery",590],["Fashion",350],["Pharmacy",480],["Food service",420],["Specialty retail",390]];
 const stages=["PROSPECT","QUALIFIED","DISCOVERY","PROPOSAL","NEGOTIATION","SIGNED","LOST"];
 const clients=[],partners=[];
 hubs.forEach(([region,lat,lon],i)=>{
  const count=65+Math.floor(rand()*40);
  for(let j=0;j<count;j++){const [segment,base]=segments[Math.floor(rand()*segments.length)];const ticket=Math.round(base*(.8+rand()*.8));clients.push({id:`R${i+1}-${String(j+1).padStart(3,"0")}`,region,segment,lat:lat+(rand()-.5)*.085,lon:lon+(rand()-.5)*.085,ticket})}
  for(let j=0;j<3;j++){const score=40+Math.floor(rand()*60);const stage=stages[(i*3+j)%stages.length];partners.push({id:`P${i+1}-${j+1}`,name:`Software House ${String(i*3+j+1).padStart(2,"0")}`,region,lat:lat+(rand()-.5)*.045,lon:lon+(rand()-.5)*.045,fit:score,stage})}
 });
 return {seed,clients,partners,hubs,segments:segments.map(x=>x[0])};
}

function distance(a,b){const rad=Math.PI/180,dlat=(b.lat-a.lat)*rad,dlon=(b.lon-a.lon)*rad;const x=Math.sin(dlat/2)**2+Math.cos(a.lat*rad)*Math.cos(b.lat*rad)*Math.sin(dlon/2)**2;return 6371*2*Math.asin(Math.sqrt(Math.min(1,x)))}

function analyze(data,radius=5,penetration=.15,share=.7,segment="ALL",opts={}){
 const clamp=(v,min,max,fallback)=>Number.isFinite(Number(v))?Math.max(min,Math.min(max,Number(v))):fallback;
 const horizon=Math.floor(clamp(opts.horizon??12,1,36,12)), opps=clamp(opts.opps??15,0,200,15), win=clamp(opts.win??.09,0,1,.09), utilization=clamp(opts.utilization??.8,0,1,.8);
 radius=clamp(radius,0,50,5);penetration=clamp(penetration,0,1,.15);share=clamp(share,0,1,.7);
 const prob={PROSPECT:.10,QUALIFIED:.25,DISCOVERY:.40,PROPOSAL:.60,NEGOTIATION:.80,SIGNED:1,LOST:0};
 const clients=data.clients.filter(c=>segment==="ALL"||c.segment===segment);
 const partners=data.partners.map((p,i)=>{
   const headcount=Math.floor(clamp(p.headcount??(4+(i*7)%23),0,500,4));
   const sellers=clamp(p.sellers??Math.max(1,Math.round(headcount*.25)),0,headcount,0);
   return {...p,headcount,sellers,radius:clamp(p.radiusOverride??radius,0,50,radius),reachable:0,allocated:0,potential:0,weighted:0,projected:0};
 });
 const assignment=new Map();
 for(const c of clients){const eligible=partners.filter(p=>p.stage!=="LOST").map(p=>({p,d:distance(c,p)})).filter(x=>x.d<=x.p.radius).sort((a,b)=>a.d-b.d||a.p.id.localeCompare(b.p.id));for(const x of eligible)x.p.reachable++;
 if(eligible.length){const p=eligible[0].p;p.allocated++;p.potential+=c.ticket;assignment.set(c.id,p.id)}}
 for(const p of partners){
   p.avgTicket=p.allocated?p.potential/p.allocated:0;
   p.monthlyCapacity=p.sellers*opps*win*utilization;
   p.monthlyDemand=p.allocated*penetration/horizon;
   p.targetWins=p.allocated*penetration;
   p.wins=Math.min(p.targetWins,p.monthlyCapacity*horizon);
   p.avgMonthlyWins=p.wins/horizon;
   p.projected=p.wins*p.avgTicket*share;
   p.weighted=p.projected*prob[p.stage];
   p.unserved=Math.max(0,p.targetWins-p.wins);
   p.bottleneck=p.stage==="LOST"?"lost":!p.allocated?"noMarket":p.unserved>1e-8?"teamLimit":"marketLimit";
   p.requiredSellers=opps*win*utilization>0?Math.ceil(Math.max(0,p.monthlyDemand-1e-10)/(opps*win*utilization)):p.monthlyDemand>0?null:0;
   p.score=Math.round(p.fit*.5+Math.min(100,p.wins*2)*.5)
 }
 const byRegion=data.hubs.map(([region,lat,lon])=>{const rs=clients.filter(c=>c.region===region),ps=partners.filter(p=>p.region===region);return{region,lat,lon,clients:rs.length,tam:rs.reduce((s,c)=>s+c.ticket,0),covered:rs.filter(c=>assignment.has(c.id)).length,partners:ps.filter(p=>p.stage!=="LOST").length}});
 const eligible=partners.filter(p=>p.stage!=="LOST"),open=eligible.filter(p=>p.stage!=="SIGNED"),signed=eligible.filter(p=>p.stage==="SIGNED");
 return {clients,partners,assignment,byRegion,totalPotential:clients.reduce((s,c)=>s+c.ticket,0),covered:assignment.size,weighted:open.reduce((s,p)=>s+p.weighted,0),signed:signed.reduce((s,p)=>s+p.projected,0),stages:Object.keys(prob),horizon,opps,win,utilization,share,penetration,monthlyCapacity:eligible.reduce((s,p)=>s+p.monthlyCapacity,0),monthlyWins:eligible.reduce((s,p)=>s+p.avgMonthlyWins,0),unserved:eligible.reduce((s,p)=>s+p.unserved,0),weightedMonthlyWins:open.reduce((s,p)=>s+p.avgMonthlyWins*prob[p.stage],0),signedMonthlyWins:signed.reduce((s,p)=>s+p.avgMonthlyWins,0)};
}
