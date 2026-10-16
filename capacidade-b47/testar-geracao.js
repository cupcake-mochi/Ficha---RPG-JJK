// Contraprova: complementos/abas antigas não contaminam a geração reduzida.
const fs=require('fs'),vm=require('vm'),cp=require('child_process'),path=require('path'),assert=require('assert');
const dir=path.join(__dirname,'../apps-script');
const files=fs.readdirSync(dir).filter(n=>n.endsWith('.gs')&&!['Codigo.gs','Habilidades.gs'].includes(n)).sort();
const oldP=cp.execFileSync('git',['show','4187df3:apps-script/PecasAnalise3.gs'],{encoding:'utf8'});
const oldA=cp.execFileSync('git',['show','4187df3:apps-script/Criacao.gs'],{encoding:'utf8'});
function load(stale,first,skip){const ctx=vm.createContext({});if(first&&stale)vm.runInContext(stale,ctx);for(const f of files.filter(f=>f!==skip))vm.runInContext(fs.readFileSync(path.join(dir,f),'utf8'),ctx);if(!first&&stale)vm.runInContext(stale,ctx);return ctx;}
let count=0;
for(const [label,stale] of [['legado PecasAnalise3',oldP],['aba Criacao antiga',oldA]])for(const first of [true,false]){
 const c=load(stale,first,label.startsWith('aba')?'Criacao.gs':null),an=c.ABAS.find(a=>a.nome==='ANALISE'),keys=an.vals.filter(v=>v[1]===1&&v[0]>1).map(v=>v[2]);
 assert.equal(keys.length,7356);assert.equal(new Set(keys).size,7356);
 assert.ok(an.vals.every(v=>v[0]<=an.rows));
 c.SpreadsheetApp={getActive(){throw Error('TOCOU_GOOGLE');}};
 assert.throws(()=>c.montar_(),/Apague do projeto/);count++;console.log('OK '+label+' carregada '+(first?'antes':'depois'));
}
const c=load(null,false);c.SpreadsheetApp={getActive(){throw Error('GUARDA_PASSOU');}};
assert.throws(()=>c.montar_(),/GUARDA_PASSOU/);count++;console.log('OK projeto consistente passa a guarda');
console.log(JSON.stringify({resultado:'OK',checagens:count,tipo:'VM; sem Google'}));
