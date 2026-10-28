'use strict';
// Alvos explícitos do cabeçalho/mesa/talentos das entidades; nenhum cartão R53.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const {separadores}=require('./gerar_contrato_pessoal');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),g);
const s=g.ABAS.find(x=>x.nome==='INVOCAÇÕES'),cells=new Map(s.vals.map(([r,c,v])=>[r+','+c,v])),notes=new Map(s.notas);
for(const sh of g.VALORES_CUSTOM_||[])if(sh.nome===s.nome)for(const [r,c,v]of sh.vals)cells.set(r+','+c,v);
const pos=a=>{const m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a);if(!m)throw Error('endereço inválido '+a);const col=t=>[...t].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0);return [+m[2],col(m[1]),+(m[4]||m[2]),col(m[3]||m[1])];};
const letra=n=>{let out='';while(n){n--;out=String.fromCharCode(65+n%26)+out;n=Math.floor(n/26);}return out;};
const canon=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canon).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canon(v[k])).join(',')+'}';
const hash=v=>crypto.createHash('sha256').update(canon(v)).digest('hex');
function varianteArrayPt(f){let out='',texto=false,paren=0,matriz=[];for(let i=0;i<f.length;i++){
 const ch=f[i];if(ch==='"'){if(texto&&f[i+1]==='"'){out+='""';i++;continue;}texto=!texto;}
 if(!texto){if(ch==='(')paren++;if(ch===')')paren--;if(ch==='{')matriz.push(paren);if(ch==='}')matriz.pop();}
 out+=!texto&&ch===','?(matriz.length&&paren===matriz.at(-1)?'\\':';'):ch;
 }if(texto||matriz.length||paren)throw Error('fórmula incompleta');return out;}
function variantes(f){const aspas=t=>t.replace(/"(?:[^"]|"")*"|[^"]+/g,x=>x[0]==='"'?x:x.replace(/'(DADOS_INVOC|DADOS_CRIACAO|DADOS_ENTIDADES|DADOS_PROGRESSAO|DADOS_R53|DADOS_R53_CATALOGO|FICHA)'!/g,'$1!'));const v=[f,f.startsWith('=IFERROR(SPARKLINE(')?varianteArrayPt(f):separadores(f)];return [...new Set(v.flatMap(x=>[x,aspas(x)]))];}
function visitar(a,fn){const p=pos(a);for(let r=p[0];r<=p[2];r++)for(let c=p[1];c<=p[3];c++)fn(letra(c)+r,r,c);}
function matriz(a,fn){const p=pos(a);return Array.from({length:p[2]-p[0]+1},(_,i)=>Array.from({length:p[3]-p[1]+1},(_,j)=>fn(p[0]+i,p[1]+j)));}
const valor=(r,c)=>cells.get(r+','+c)??'';
function contem(a,r,c){const p=pos(a);return r>=p[0]&&r<=p[2]&&c>=p[1]&&c<=p[3];}
function menu(r,c){let out=null;for(const [onde,de]of s.dv)if(contem(onde,r,c)){
 const lista=/^"(.*)"$/.exec(de),ref=/^'?([^'!]+)'?!\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)$/.exec(de);
 if(!lista&&!ref)throw Error('menu novo em entidade');
 out={tipo:lista?'VALUE_IN_LIST':'VALUE_IN_RANGE',argumentos:lista?[lista[1].split(','),true]:[{aba:ref[1],faixa:ref[2]+ref[3]+':'+ref[4]+ref[5]},true],permiteInvalido:!(s.menus_estritos||[]).includes(onde),ajuda:''};
 }if(s.caixas.some(x=>c===x[0]&&r>=x[1]&&r<x[1]+x[2]))throw Error('checkbox inesperado em dados da entidade');return out;}
const base={
 identidade:['I13','I43','L43','I47','K47','L47','K50','U45','I66'],
 atributos_treinos:['O20:S20','O21:S21','O26:S26','O31:R31','S29','O34','R34','O38:O44'],
 recursos:['U13','W13','X13','Y13','U18','V18','U22','U27'],
 familias:['O48:S48','O50:R50','R54:R63'],
 inventario:['V33:V35','Y33:Y35','U37:U42','Y37:Y42'],
 talentos_expansao:['J93:J100','J195:J197','O221','O222','O226']
};
const areas=['I9:Y68','I92:Y100','I194:Y197','O220:S227'];
const todos=new Set(),contrato={versao:1,entidades:{},dominios:{}};
function entrada(a){const p=pos(a);visitar(a,(addr,r,c)=>{
 if(r>s.rows||c>s.cols||todos.has(addr))throw Error('alvo sobreposto/fora '+addr);todos.add(addr);
 if(s.merges.some(m=>r>=m[0]&&r<=m[2]&&c>=m[1]&&c<=m[3]&&(r!==m[0]||c!==m[1])))throw Error('interior de mescla '+addr);
 });
 const valores=matriz(a,valor),formulas=valores.flat().filter(v=>typeof v==='string'&&v.startsWith('='));
 if(formulas.length&&formulas.length!==valores.flat().length)throw Error('matriz de entrada mista');
 return {aba:s.nome,faixa:a,tipo:formulas.length?'formula':'valor',valores,notas:matriz(a,(r,c)=>notes.get(letra(c)+r)||''),
 equivalentes:valores.map(l=>l.map(v=>formulas.length?variantes(v):[])),validacoes:matriz(a,menu),
 mesclas:s.merges.filter(m=>m[0]<=p[2]&&m[2]>=p[0]&&m[1]<=p[3]&&m[3]>=p[1]).map(m=>m.slice(0,4))};
}
function guarda(a){const p=pos(a),v=valor(...p);return {faixa:a,...(typeof v==='string'&&v.startsWith('=')?{formulas:variantes(v).map(hash)}:{valor:v})};}
if(s.redutores.length!==12||s.familias_custom.length!==12)throw Error('grade de entidades mudou');
for(let i=0;i<12;i++){
 const p=pos(s.redutores[i][1]),dr=p[0]-13,dc=p[1]-21;
 const shift=a=>{const p=pos(a),cel=(r,c)=>letra(c+dc)+(r+dr);return cel(p[0],p[1])+(a.includes(':')?':'+cel(p[2],p[3]):'');};
 const nomes=Object.fromEntries(Object.entries(base).map(([k,v])=>[k,v.map(shift)]));
 const fam=s.familias_custom[i];if(fam.entidade!==i+1||JSON.stringify(fam.vagas)!==JSON.stringify(['O48','P48','Q48','R48','S48','O50','P50','Q50','R50'].map(shift))||JSON.stringify(fam.linhas.map(x=>x.estado))!==JSON.stringify(Array.from({length:10},(_,j)=>shift('R'+(54+j)))))throw Error('metadados de Famílias divergentes');
 if(s.notas_contextuais.destinos[i]!==shift('I43')||s.redutores[i].join(',')!==['X13','U13','W13','V13'].map(shift).join(',')||!s.livres.includes(shift('V18')))throw Error('metadados de entidade divergentes');
 for(const [addr,expected]of [['I12','NOME'],['I42','TIPO'],['K50','Autônoma'],['I43','Shikigami de técnica'],['I47','Espaço conhecido'],['L47','Sem carga'],['I65','DEFINIÇÃO'],['I194','TALENTOS DA TRILHA · CATEGORIA 1'],['O220','EXPANSÃO DE DOMÍNIO']])if(valor(...pos(shift(addr)))!==expected)throw Error('layout/default mudou em '+shift(addr));
 const entradas={};for(const [nome,alvos]of Object.entries(nomes))entradas[nome]=alvos.map(entrada);
 const conhecidos=new Set();for(const alvos of Object.values(nomes))for(const a of alvos)visitar(a,addr=>conhecidos.add(addr));
 const foto=shift('I15'),guardas=[];
 for(const area of areas.map(shift))visitar(area,(addr,r,c)=>{if(!conhecidos.has(addr)&&addr!==foto&&valor(r,c)!=='')guardas.push(guarda(addr));});
 const leituras=areas.map(shift);
 contrato.entidades[i+1]={guardas,leituras,foto};
 for(const [nome,ent]of Object.entries(entradas))contrato.dominios[(i+1)+'_'+nome]={entidade:i+1,aba:s.nome,entradas:ent};
 // Nenhuma entrada deste protocolo pode coincidir com os 249 cartões R53.
 for(const c of g.R53_EDITOR_.contextos.filter(c=>c.aba===s.nome&&c.entidade===i)){
  const alvos=[...Object.values(c.entradas_diretas),...Object.values(c.cel)];
  for(const addr of conhecidos)if(alvos.includes(addr))throw Error('entrada já coberta pelo editor '+addr);
 }
}
// Defesa usa é escolha pessoal do conjunto; teto e corpos mantidos são fórmulas.
contrato.dominios.conjunto={entidade:null,aba:s.nome,entradas:[entrada('D17')],guardas:['D9','D12','E12','F12','D13','E13','F13','D16','E16','F16','E17','F17'].map(guarda),leituras:['D9:F17'],foto:null};
const text='/** Dados pessoais das entidades: contrato gerado do fonte público completo. */\nvar R53_NOVA_ENTIDADES_CONTRATO_ = '+JSON.stringify(contrato)+';\n';
if(require.main===module){const file=path.join(__dirname,'contrato_entidades.gs');if(process.argv.includes('--conferir')){if(fs.readFileSync(file,'utf8')!==text)throw Error('contrato de entidades desatualizado');console.log('Contrato das entidades igual às fontes.');}else fs.writeFileSync(file,text);}
module.exports={contrato,pos,letra,variantes,visitar,hash};
