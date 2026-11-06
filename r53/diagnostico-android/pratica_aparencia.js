'use strict';
// Atualiza apenas o registro das áreas novas; não troca nem agenda paletas.
const rect=a=>{const p=a.split(':').map(x=>{const m=/^([A-Z]+)(\d+)$/.exec(x);if(!m)throw Error('Faixa inválida');return[+m[2],[...m[1]].reduce((n,c)=>26*n+c.charCodeAt(0)-64,0)];});return[p[0][0],p[0][1],p.at(-1)[0],p.at(-1)[1]];};
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const a1=([r,c,rr,cc])=>col(c)+r+(r===rr&&c===cc?'':':'+col(cc)+rr);
const hit=(a,b)=>a[0]<=b[2]&&a[2]>=b[0]&&a[1]<=b[3]&&a[3]>=b[1];
function subtract(a,b){if(!hit(a,b))return[a];const r=Math.max(a[0],b[0]),c=Math.max(a[1],b[1]),rr=Math.min(a[2],b[2]),cc=Math.min(a[3],b[3]),out=[];if(a[0]<r)out.push([a[0],a[1],r-1,a[3]]);if(rr<a[2])out.push([rr+1,a[1],a[2],a[3]]);if(a[1]<c)out.push([r,a[1],rr,c-1]);if(cc<a[3])out.push([r,cc+1,rr,a[3]]);return out;}
function aplicar(map){
 const out=JSON.parse(JSON.stringify(map)),name='FICHA AMALDIÇOADA',old=map.abas[name],dst=out.abas[name];if(!old)throw Error('Mapa da aba ausente');
 const edits=[[328,4,328,20],[563,4,567,20]];
 for(const channel of ['b','f']){
  for(const [role,ranges]of Object.entries(old[channel]))dst[channel][role]=ranges.flatMap(s=>edits.reduce((xs,b)=>xs.flatMap(a=>subtract(a,b)),[rect(s)])).map(a1);
  function roleAt(r,c){const roles=Object.entries(old[channel]).filter(([k,rs])=>rs.some(s=>hit(rect(s),[r,c,r,c]))).map(([k])=>k);if(roles.length!==1)throw Error('Papel ausente/ambíguo no exemplar '+r+','+c);return roles[0];}
  function put(target,r,c){const role=roleAt(r,c),cut=rect(target);for(const [k,rs]of Object.entries(dst[channel]))dst[channel][k]=rs.flatMap(s=>subtract(rect(s),cut)).map(a1);(dst[channel][role]??=[]).push(target);}
  for(let c=1;c<=21;c++)put(a1([562,c,569,c]),561,c);
  put('D328:T328',327,18);put('D563:T563',320,4);put('D564:T564',327,18);
  for(const r of [565,566,567])for(const [c,end]of [[4,5],[6,8],[10,11],[12,14],[16,16],[17,17],[18,20]])put(a1([r,c,r,end]),r===565?322:327,r===565&&c===17?16:c);
 }
 return out;
}
module.exports={aplicar,rect,a1,hit,subtract};
