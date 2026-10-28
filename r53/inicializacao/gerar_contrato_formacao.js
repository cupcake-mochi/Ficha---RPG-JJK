'use strict';
// Lista explícita de entradas pessoais; não procura campos por cor ou por fórmula.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const {separadores}=require('./gerar_contrato_pessoal');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);
for(const n of ['Ficha','Pessoal','Salarios','R53Cartoes1'])vm.runInContext(fs.readFileSync(path.join(root,'apps-script/'+n+'.gs'),'utf8'),g);
const sheets=new Map(g.ABAS.map(s=>[s.nome,{...s,cells:new Map(s.vals.map(x=>[x[0]+','+x[1],x[2]]))}]));
for(const s of g.VALORES_CUSTOM_)if(sheets.has(s.nome))for(const [r,c,v]of s.vals)sheets.get(s.nome).cells.set(r+','+c,v);
// O preparador salarial substitui a apresentação antiga de W86.
if(g.SALARIO_.formula!==true)throw Error('modo salarial não suportado');
sheets.get('FICHA PESSOAL').cells.set('86,23',g.SALARIO_.f.total);
const digest=f=>crypto.createHash('sha256').update(JSON.stringify(f)).digest('hex');
function aspas(f){return f.replace(/"(?:[^"]|"")*"|[^"]+/g,t=>t[0]==='"'?t:t.replace(/'(FICHA|DADOS_PROGRESSAO|DADOS_CUSTOM|DADOS_SALARIOS|DADOS_AM|DADOS_CRIACAO)'!/g,'$1!'));}
const variantes=f=>[...new Set([f,separadores(f),aspas(f),aspas(separadores(f))])];
function coord(a){const m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a);if(!m)throw Error(a);const col=t=>[...t].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0);return [+m[2],col(m[1]),+(m[4]||m[2]),col(m[3]||m[1])];}
const letra=c=>{let s='';while(c){c--;s=String.fromCharCode(65+c%26)+s;c=Math.floor(c/26);}return s;};
function dados(aba,faixa){const s=sheets.get(aba),[r,c,r2,c2]=coord(faixa);if(!s||r2>s.rows||c2>s.cols)throw Error('fora da grade '+aba+'!'+faixa);return Array.from({length:r2-r+1},(_,i)=>Array.from({length:c2-c+1},(_,j)=>s.cells.get((r+i)+','+(c+j))??''));}
function entrada(aba,faixa,tipo){const s=sheets.get(aba),[r,c,r2,c2]=coord(faixa),valores=dados(aba,faixa),notas=[];
 for(let rr=r;rr<=r2;rr++){const linha=[];for(let cc=c;cc<=c2;cc++){
  if(s.merges.some(m=>rr>=m[0]&&rr<=m[2]&&cc>=m[1]&&cc<=m[3]&&(rr!==m[0]||cc!==m[1])))throw Error('interior de mescla '+aba+'!'+letra(cc)+rr);
  const v=valores[rr-r][cc-c],formula=typeof v==='string'&&v.startsWith('=');
  if(tipo==='estado_familia'&&v!=='Neutra'||tipo==='bool'&&(v!==false)||tipo==='bonus'&&(v!==''&&v!==0)||tipo==='formula'&&!formula||tipo!=='formula'&&formula)throw Error('tipo inesperado '+aba+'!'+faixa);
  linha.push(s.notas?.find(x=>x[0]===letra(cc)+rr)?.[1]||'');
 }notas.push(linha);}
 return {aba,faixa,tipo,valores,notas,equivalentes:valores.map(l=>l.map(v=>tipo==='formula'?variantes(v):[]))};
}
function guard(aba,faixa){const valores=dados(aba,faixa);return {aba,faixa,celulas:valores.map(l=>l.map(v=>typeof v==='string'&&v.startsWith('=')?{formulas:variantes(v).map(digest)}:{valor:v}))};}
const F='FICHA',P='FICHA PESSOAL',A='FICHA AMALDIÇOADA';
const build=(entradas,guardas,leituras)=>({entradas:entradas.map(x=>entrada(...x)),guardas:guardas.map(x=>guard(...x)),leituras});
const perBool=['D80:E90','T79:U90','D94:E103'],perBonus=['R80:R90','AH79:AH90','AL94:AL103'];
const ofBool=['D108:E113','Q108:R112','D118:E127','AF108:AF111'],ofBonus=['O108:O113','AB108:AB112','AL118:AL127','AJ108:AJ111'];
const origem=[['AB11','texto'],['D44','texto'],['R44','texto'],['AH44','texto'],['D45','formula'],['R45','formula'],['AH45','formula'],['D54','texto'],['AH54','formula'],['D58','formula']];
// Somente âncoras pessoais do cabeçalho. Nome/atributo/CD vêm de outras abas.
const tecnica=['J12','J16','D18','J18','P18','D22','D26','L26','L29','D33','P33'];
const contrato={versao:1,dominios:{
 grau_origem:build(origem.map(([a,t])=>[P,a,t]),['AB10','D40','R40','AH40','D43','R43','AH43','D53','AH53','D41','R41','AH41','D51','R51','AH51','AH55','D57','W86'].map(a=>[P,a]),{[P]:'D10:AT86'}),
 pericias:build([...perBool.map(a=>[F,a,'bool']),...perBonus.map(a=>[F,a,'bonus'])],['F80:F90','V79:V90','D91','F94:F103','W94:W103','AD94:AD103','P80','AF79','AK89','AK105'].map(a=>[F,a]),{[F]:'D78:AN105'}),
 oficios_tr:build([...ofBool.map(a=>[F,a,'bool']),...ofBonus.map(a=>[F,a,'bonus']),...['K108:K113','X108:X112','AK108','AK81'].map(a=>[F,a,'texto']),[F,'W118:W127','formula']],['F108:F113','S108:S112','AG108:AG111','AK109:AK111','D115','F118:F127','AD118:AD127','N108','AA108','AP108','AF114','AN114','AK79','AK83'].map(a=>[F,a]),{[F]:'D78:AT127'}),
 armas:build(['D','M','V','AE','AM'].map(c=>[P,c+'71:'+c+'83','bool']),['D69','E71:E83','N71:N83','W71:W83','AF71:AF83','AN71:AN83','D67'].map(a=>[P,a]),{[P]:'D67:AT83'}),
 tecnica:build(tecnica.map(a=>[A,a,'texto']),['D9','D11','J11','L11','P11','R11','D15','D21','D25','L28','D32','P32','R32','D12','L12','P12','R12','J15','P15','D16','P16','D17','J17','P17','D19','J19','P19','L25','R33'].map(a=>[A,a]),{[A]:'D9:T34'}),
 familias:build([...['D37:G37','J37:M37','P37'].map(a=>[A,a,'estado_familia']),[A,'O41:O50','formula']],['D36:G36','J36:M36','P36','Q36','Q37','D38','D39','D40','O40','D41:D50'].map(a=>[A,a]),{[A]:'D36:T50'}),
 equipados:build([['D64','texto'],['S64','texto'],['AH64','texto'],['L86','bonus'],['AN86','texto']].map(([a,t])=>[P,a,t]),['D61','D63','S63','AH63','D66','S66','AH66','D85','L85','AF85','AN85','D86','AF86'].map(a=>[P,a]),{[P]:'D61:AT87'}),
 equipaveis:build([...['D92:D99','K92:K99'].map(a=>[P,a,'texto']),...['M','S','U','W','AE','AG','AI','AK','AQ'].map(c=>[P,c+'92:'+c+'99','formula'])],['D89',...['D','K','M','S','U','W','AE','AG','AI','AK','AQ'].map(c=>c+'91')].map(a=>[P,a]),{[P]:'D89:AT99'}),
 itens:build([...['D','T','Z','AP'].map(c=>[P,c+'104:'+c+'109','texto']),...['V','AR'].map(c=>[P,c+'104:'+c+'109','formula'])],['D101',...['D','T','V','Z','AP','AR'].map(c=>c+'103')].map(a=>[P,a]),{[P]:'D101:AT109'})
}};
// O Google em pt_BR salva o fallback decimal dos Volumes como 0,1.
// Acrescentar só esta representação da fórmula inteira, sem normalizar entrada arbitrária.
function variantesVolume(f) {
 const v=variantes(f),locais=v.filter(x=>x.includes(';')).map(x=>{
  if(!/;0\.1\)\)$/.test(x))throw Error('fallback de Volume mudou; revisar a fórmula');
  return x.replace(/;0\.1\)\)$/, ';0,1))');
 });
 return [...new Set([...v,...locais])];
}
for(const x of contrato.dominios.itens.entradas)if(x.tipo==='formula')
 x.equivalentes=x.valores.map(l=>l.map(variantesVolume));
// Notas vivas antigas não podem acompanhar as mãos/carga da cópia nova.
// O conteúdo dessas células continua protegido; a fase de automações regenerará as notas.
contrato.dominios.equipados.somenteNotas=['D66','S66','D86','AF86'].map(a=>{
 const x=entrada(P,a,'formula');
 return {aba:x.aba,faixa:x.faixa,notas:x.notas};
});
for(const d of Object.values(contrato.dominios))for(const x of [...d.entradas,...d.guardas,...(d.somenteNotas||[])]){
 const a=coord(x.faixa),b=d.leituras[x.aba]&&coord(d.leituras[x.aba]);
 if(!b||a[0]<b[0]||a[1]<b[1]||a[2]>b[2]||a[3]>b[3])throw Error('guarda/entrada fora da leitura '+x.aba+'!'+x.faixa);
}
// A extensão B47 mudou os campos custom: apenas os novos seletores/âncoras.
if(contrato.dominios.grau_origem.entradas[0].valores[0][0]!=='Grau 4')throw Error('mudou o Grau de fábrica; revisar a regra inicial');
const text='/** Contrato de formação gerado das fontes públicas, sem dados de jogador. */\nvar R53_NOVA_FORMACAO_CONTRATO_ = '+JSON.stringify(contrato,null,2)+';\n';
if(require.main===module){const file=path.join(__dirname,'contrato_formacao.gs');if(process.argv.includes('--conferir')){if(fs.readFileSync(file,'utf8')!==text)throw Error('contrato de formação desatualizado; revisar antes de regenerar');console.log('Contrato de formação igual às fontes.');}else fs.writeFileSync(file,text);}
module.exports={contrato,variantes,variantesVolume,coord,dados,letra};
