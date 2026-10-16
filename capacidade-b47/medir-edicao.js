// CPU do gatilho de texto em VM, sem latência de serviços e sem Google.
const fs=require('fs'),vm=require('vm'),path=require('path');
const model=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const spec=model.layout.abas.find(a=>a.nome==='CONFIGURAÇÃO');
const field=model.registros.find(g=>g.tipo==='melhoria'&&g.n===1).requisitos;
const row=Number(field.match(/\d+/)[0]);let reads=0;
const values={[field]:'Texto de medição. '+('Requisitos e efeitos precisam continuar inteiros e legíveis. '.repeat(40))};
const sheet={getRange(a){return {getDisplayValue(){return values[a]||'';}}},setRowHeights(){}};
const ctx=vm.createContext({ABAS:[spec],SpreadsheetApp:{getActive(){return {getSheetByName(){return sheet;}};}}});
for(const file of ['Codigo.gs','Habilidades.gs'])vm.runInContext(fs.readFileSync(path.join(__dirname,'../apps-script',file),'utf8'),ctx);
const edit={range:{getSheet(){return sheet;},getRow(){reads++;return row;},getColumn(){reads++;return 2;},getNumRows(){reads++;return 1;},getNumColumns(){reads++;return 1;}}};
const samples=[];
for(let i=0;i<120;i++){
 reads=0;const start=performance.now();ctx.esticarCaixas_(edit,'CONFIGURAÇÃO');
 if(reads!==4)throw Error('Leituras de Range divergentes: '+reads);
 if(i>=20)samples.push(performance.now()-start);
}
samples.sort((a,b)=>a-b);
console.log(JSON.stringify({tipo:'simulação VM; CPU, sem latência de serviços',grupos:spec.esticam.length,amostras:samples.length,mediana_ms:(samples[49]+samples[50])/2,p95_ms:samples[94],leituras_range:4},null,2));
