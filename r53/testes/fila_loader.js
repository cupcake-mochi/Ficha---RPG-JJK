'use strict';
// Confere localmente o carregador da fila contra a captura instalada.
// Uso: node r53/testes/fila_loader.js <pasta da captura .gs> <Codigo novo>
const fs=require('fs'),vm=require('vm'),zlib=require('zlib'),crypto=require('crypto'),assert=require('assert'),path=require('path');
const [pasta,novoPath]=process.argv.slice(2);
if(!pasta||!novoPath)throw Error('Informe a pasta da captura e o Codigo novo');
const antigo=fs.readFileSync(path.join(pasta,'Codigo.gs'),'utf8'),novo=fs.readFileSync(novoPath,'utf8');
const outros=fs.readdirSync(pasta).filter(n=>n.endsWith('.gs')&&n!=='Codigo.gs').map(n=>fs.readFileSync(path.join(pasta,n),'utf8'));

// 1. Diferença textual restrita: âncora do carregador, função nova e paleta leve.
const leve='// GERADO por r53/paleta_leve.js',marca='// FILA: Sementes, barras e paleta pós-lock';
const a0=antigo.slice(0,antigo.indexOf(leve)),n0=novo.slice(0,novo.indexOf(marca));
assert.strictEqual(n0,a0.replace('r53CorrecaoAndroid_(r53CorrecaoAbertura_(code))','r53CorrecaoFila_(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code)))'));
assert.strictEqual(novo.slice(novo.indexOf(leve)),fs.readFileSync(path.join(__dirname,'../../apps-script/PaletaAndroid.gs'),'utf8'));

function utilities(){return {
 base64Decode:s=>Buffer.from(s,'base64'),
 newBlob:(b)=>({bytes:Buffer.from(b)}),
 ungzip:(blob)=>({getDataAsString:()=>zlib.gunzipSync(blob.bytes).toString('utf8')}),
 computeDigest:(alg,text)=>Array.from(crypto.createHash('sha256').update(text,'utf8').digest()).map(b=>b>127?b-256:b),
 DigestAlgorithm:{SHA_256:'sha256'},Charset:{UTF_8:'utf8'}};}
function carregar(codigo){
 let pendente=false,menus=0,leves=0;
 const ctx={Utilities:utilities(),console:{log(){}},
  PropertiesService:{getDocumentProperties:()=>({getProperty:()=>pendente?'tema':null})},
  SpreadsheetApp:{getActive:()=>null},ScriptApp:{getScriptId:()=>'x'}};
 vm.createContext(ctx);
 outros.concat([codigo]).forEach(t=>vm.runInContext(t,ctx));
 return {ctx,abrir(p){pendente=p;const m=ctx.r53Modulo_;ctx.r53Modulo_=()=>{throw Error('Abertura carregou catálogos');};
   const s=ctx.salarioAbrir_,r=ctx.r53Menu_,l=ctx.r53PaletaLeve_;ctx.salarioAbrir_=()=>menus++;ctx.r53Menu_=()=>menus++;ctx.r53PaletaLeve_=()=>({continuar:()=>leves++});
   ctx.onOpen({});Object.assign(ctx,{r53Modulo_:m,salarioAbrir_:s,r53Menu_:r,r53PaletaLeve_:l});return {menus,leves};}};
}
const velho=carregar(antigo),n=carregar(novo);
// 2. Abertura leve preservada.
assert.deepStrictEqual(n.abrir(false),{menus:2,leves:0});
assert.deepStrictEqual(n.abrir(true),{menus:4,leves:1});
// 3. Módulos carregam com geração única; só os alvos previstos mudam.
const mv=velho.ctx.r53Modulo_(),mn=n.ctx.r53Modulo_();
assert.strictEqual(mn.__estado().sobras.length,0);
assert.strictEqual(mn.__estado().geracao,mv.__estado().geracao);
const sn=mn.__estado();
const modNovo=fs.readFileSync(novoPath+'.modulo.js','utf8');
const R=/\[(\d+),(\d+),"((?:[^"\\]|\\.)*)",(\d+)\]/g;
const cel=(t,k)=>[...t.matchAll(R)].filter(m=>m[1]+','+m[2]===k).map(m=>m[0]);
['2,93','3,93','4,93','5,93'].forEach((k,i)=>assert(cel(modNovo,k).some(e=>e.includes(['Domínio Simples','Energia Reversa','Pétala','Aptidão Própria'][i])),k));
['2,97','3,97','4,97','5,97'].forEach((k,i)=>assert(cel(modNovo,k).some(e=>e.includes('INDEX($CO$2:$CO$5,'+(i+1)+')')),k));
assert(modNovo.includes('["J16","DADOS_AM!$CS$2:$CS$5"]')&&!modNovo.includes('$CS$2:$CS$4"]'));
[26,30,34].forEach(r=>assert(modNovo.includes('IF(OR(N($D$'+r+')<=0,N($J$'+r+')<=0)')));
assert(modNovo.includes('      var estados = props.getProperties();\n      if (!estados[PROP_PENDENTE_]) return;'));
assert(!modNovo.includes('$CO$2:$CO$1,'));
// 4. Paleta leve carrega com o hash novo.
const pl=n.ctx.r53PaletaLeve_();assert.strictEqual(typeof pl.trocar,'function');assert.strictEqual(typeof pl.continuar,'function');
console.log(JSON.stringify({resultado:'OK',geracao:sn.geracao,abas:sn.abas.length,sobras:0,
 sha256_novo:crypto.createHash('sha256').update(novo).digest('hex'),caracteres:novo.length,
 limite:'VM local com serviços simulados; não executa Sheets nem mede Android.'}));
