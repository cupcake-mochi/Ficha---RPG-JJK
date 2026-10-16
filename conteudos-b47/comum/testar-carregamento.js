'use strict';
// Transporte real gerado: ordens alternativas, metadados e guardas sem Google.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..');
const model=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const reference=process.argv[3]&&JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const expectedCount=model.entidades?8190:model.personagem?7960:7436;
const expectedTabs=model.entidades?22:model.personagem?21:18;
const dir=path.join(root,'apps-script');
const files=['Ficha.gs',...fs.readdirSync(dir).filter(n=>n.endsWith('.gs')&&!['Ficha.gs','Codigo.gs','Habilidades.gs'].includes(n)).sort()];
const sources=Object.fromEntries(files.map(n=>[n,fs.readFileSync(path.join(dir,n),'utf8')]));
// --exportar-pecas sai antes de sem_invocacao.aplica; a geração canônica
// retira exatamente estas três abas históricas, sem permitir outras faltas.
const retired=new Set(['INVOCAÇÃO','CATÁLOGO','DADOS_INV']);
assert.deepEqual(model.layout.abas.filter(a=>retired.has(a.nome)).map(a=>a.nome).sort(),[...retired].sort());
const modelTabs=Object.fromEntries(model.layout.abas.filter(a=>!retired.has(a.nome)).map(a=>[a.nome,a]));
const expectedKeys=modelTabs.ANALISE.celulas.filter(c=>/^A\d+$/.test(c[0])&&c[0]!=='A1').map(c=>c[1]).sort();
let count=0;
function load(order,omit,stale){
 const c=vm.createContext({});
 for(const file of order){
  if(file===omit)continue;
  let source=sources[file];
  if(file===stale)source=source.replace(/"geracao"\s*:\s*"[a-f0-9]+"/g,'"geracao":"0000000000000000"');
  vm.runInContext(source,c,{filename:file});
 }
 return c;
}
function check(order){
 const c=load(order);
 const abas=JSON.parse(JSON.stringify(c.ABAS));
 assert.equal(abas.length,expectedTabs);
 assert.deepEqual(abas.map(a=>a.nome).sort(),Object.keys(modelTabs).sort());
 const analise=abas.find(a=>a.nome==='ANALISE');
 const keys=analise.vals.filter(v=>v[1]===1&&v[0]>1).map(v=>v[2]).sort();
 assert.deepEqual(keys,expectedKeys);
 assert.equal(new Set(keys).size,expectedCount);
 if(reference){
  for(const aba of abas){
   const vals=aba.vals.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
   const expected=reference.find(a=>a.nome===aba.nome).vals.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
   assert.deepEqual(vals,expected,'Valores completos Python/JS: '+aba.nome);
  }
 }
 const danos=abas.find(a=>a.nome==='DADOS_DANOS');
 assert.equal(danos.rows,modelTabs.DADOS_DANOS.linhas+2); // margem nativa do emissor
 const cfg=abas.find(a=>a.nome==='CONFIGURAÇÃO');
 assert.ok(cfg.rows>=modelTabs['CONFIGURAÇÃO'].linhas,'Grade inclui as últimas linhas declaradas');
 const read=(spec,r,col)=>spec.vals.find(v=>v[0]===r&&v[1]===col)?.[2];
 assert.equal(read(cfg,1735,2),'TIPO DE DANO · 1');
 assert.equal(read(cfg,1847,10),'TIPO DE DANO · 10');
 for(const g of model.danos.registros){
  assert.ok(cfg.esticam.some(box=>box.gatilhos.includes(g.definicao)));
  assert.ok(cfg.esticam.some(box=>box.gatilhos.includes(g.efeito)));
 }
 for(const g of model.personagem?.registros||[]){
  for(const key of ['requisitos','efeito'])assert.ok(cfg.esticam.some(box=>box.gatilhos.includes(g.campos[key])));
 }
 c.SpreadsheetApp={getActive(){throw new Error('GOOGLE_SENTINELA');}};
 assert.throws(()=>c.montar_(),/GOOGLE_SENTINELA/);
 count++;
}
const orders=[files,files.slice().reverse()];
for(const file of ['Danos.gs','DanosPainel.gs','PecasPainel.gs',
 ...(model.personagem?['FormasPersonagem.gs','PersonagemFormas1.gs','PersonagemPainel.gs']:[]),
 ...(model.entidades?['Entidades.gs','EntidadesPainel.gs','EntidadesAnalise.gs']:[])]){
 const rest=files.filter(f=>f!==file);
 orders.push([file,...rest],[...rest,file]);
}
for(const order of orders){check(order);if(global.gc)global.gc();}
for(const missing of ['Danos.gs','DanosPainel.gs',
 ...(model.personagem?files.filter(f=>/^(?:FormasPersonagem|AptidoesPersonagem|TalentosPersonagem|Personagem(?:Formas\d+|Painel|Analise))\.gs$/.test(f)):[]),
 ...(model.entidades?['Entidades.gs','EntidadesPainel.gs','EntidadesAnalise.gs']:[])]){
 const c=load(files,missing);
 c.SpreadsheetApp={getActive(){throw new Error('GOOGLE_TOCADO');}};
 assert.throws(()=>c.montar_(),new RegExp('Falta o '+missing.replace('.','\\.')));
 count++;if(global.gc)global.gc();
}
for(const order of [files,files.slice().reverse()]){
 const c=load(order,null,'Danos.gs');
 c.SpreadsheetApp={getActive(){throw new Error('GOOGLE_TOCADO');}};
 assert.throws(()=>c.montar_(),/geração anterior/);
 count++;if(global.gc)global.gc();
}
console.log(JSON.stringify({resultado:'OK',checagens:count,ordens:orders.length,abas:expectedTabs,chaves:expectedCount,referencia_python:!!reference,tipo:'VM; sem Google'}));
