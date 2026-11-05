'use strict';
// Offline: exige snapshot atual, valida a base e não deduz a intenção de um Buff.
const fs=require('node:fs'),path=require('node:path');
const {sha,trocar}=require('./preparar_recursos_fila');
const {planejarCelulas}=require('./preparar_pilha_5156');
const plano=require('./reserva_bolsa_plano.json');
const BASE='bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130';
function molde(){let m=fs.readFileSync(path.join(__dirname,'pilha_5156_molde.gs'),'utf8').replaceAll('r53AjustarPilha516_','r53AjustarReservaBolsa_').replaceAll('R53_PILHA_516_','R53_RESERVA_BOLSA_').replaceAll('Pilha 51–56:','Reserva/Bolsa:');
 m=trocar(m,'else op.lista.push([op.delta.r, op.delta.c, op.delta.depois, 0]);','else op.lista.push(op.delta.addr ? [op.delta.addr, op.delta.depois] : [op.delta.r, op.delta.c, op.delta.depois, 0]);');
 return 'var R53_RESERVA_BOLSA_='+JSON.stringify(plano)+';\n'+m;}
function prepararCodigo(src){
 if(sha(src)!==BASE)throw Error('Código divergente: exige PR67 ensaiada');
 const a='r53AjustarOrigensRecursos_(R53_MODULO_.__estado().abas);';
 src=trocar(src,a,a+' r53AjustarReservaBolsa_(R53_MODULO_.__estado().abas);');
 const root='function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53DescansoEdit_(e))return r53ContinuarPaletaPendente_(e);return r53SalarioOnEdit_(e);}';
 src=trocar(src,root,root.replace('if(r53DescansoEdit_(e))','if(r53RestaurarCargaOrigem_(e))return r53ContinuarPaletaPendente_(e);if(r53DescansoEdit_(e))'));
 return src+'\n'+molde()+'\n'+fs.readFileSync(path.join(__dirname,'../../apps-script/ReservaBolsa.gs'),'utf8');
}
const normalizar=s=>typeof s==='string'&&s.startsWith('=')?s.split(/("(?:[^"]|"")*")/).map((t,i)=>i%2?t:t.replace(/'([A-Za-z_][A-Za-z_0-9]*)'!/g,'$1!')).join(''):s;
const AUX=[['FICHA',11,24],['FICHA',52,19],['FICHA',52,33],['DADOS_CUSTOM',121,2],['DADOS_CUSTOM',123,2],['FICHA',30,16],['FICHA PESSOAL',86,12],...['B','C','E'].flatMap(c=>[3,13].map(r=>['DADOS_CONFIG',r,c.charCodeAt(0)-64])),...Array.from({length:30},(_,i)=>[3,4,5,6].map(c=>['CONFIGURAÇÃO',i+11,c])).flat()];
function conferirCompensacoes(snapshot){
 const ids=new Map(),names=new Map();
 for(const x of snapshot.cells){if(!Number.isSafeInteger(x.sheetId)||x.sheetId<0||typeof x.aba!=='string'||!x.aba)throw Error('Identidade de aba inválida');if(ids.has(x.aba)&&ids.get(x.aba)!==x.sheetId||names.has(x.sheetId)&&names.get(x.sheetId)!==x.aba)throw Error('Mapeamento de abas divergente');ids.set(x.aba,x.sheetId);names.set(x.sheetId,x.aba);}
 const le=(a,r,c)=>{const xs=snapshot.cells.filter(x=>!x.addr&&x.aba===a&&x.r===r&&x.c===c);if(xs.length!==1||!Object.hasOwn(xs[0],'effective'))throw Error('Leitura efetiva ausente ou duplicada: '+a+'!'+r+','+c);const v=xs[0].effective;if(v&&typeof v==='object')throw Error('Erro ou valor efetivo inválido em '+a+'!'+r+','+c);return v;};
 // Ler todas as sentinelas impede instalar com snapshot incompleto, mesmo sem uma menor ativa.
 const values=AUX.map(([a,r,c])=>le(a,r,c));
 const ori=values[0],menores=values.slice(1,3),custom=values[3],base=values[4];
 if(typeof ori!=='string'||menores.some(x=>typeof x!=='string')||typeof custom!=='boolean'||typeof base!=='string')throw Error('Metadados de Origem inválidos');
 const herda=b=>ori===b||custom===true&&base===b;
 const ativos=[herda('Restrição Celestial · Restrição corporal')&&menores.includes('Reserva Excedente'),herda('Híbrido')&&menores.includes('Bolsa Orgânica')];
 for(const [i,nome]of ['PE','carga'].entries()){
  if(!ativos[i])continue;
  const row=i?13:3,somar=le('DADOS_CONFIG',row,2),trocas=le('DADOS_CONFIG',row,3),aviso=le('DADOS_CONFIG',row,5);
  if(aviso!==''||![0,1].includes(trocas))throw Error('CONFIGURAÇÃO de '+nome+' exige revisão');
  if(trocas===1)continue; // Resultado final explícito: a fórmula não acrescenta bônus.
  const buff=values[5+i];
  for(const [campo,v]of [['Buff',buff],['Somar',somar]])if(v!==''&&(typeof v!=='number'||!Number.isFinite(v)||v!==0))throw Error('Revisar possível compensação manual de '+nome+' em '+campo+'; nenhuma entrada foi alterada');
  // A soma líquida pode ser zero apesar de uma compensação positiva e outra penalidade.
  for(let row=11;row<=40;row++)if(le('CONFIGURAÇÃO',row,3)===true&&le('CONFIGURAÇÃO',row,4)===(i?'Limite de carga':'PE máximo')&&le('CONFIGURAÇÃO',row,5)==='somar'&&le('CONFIGURAÇÃO',row,6)!==0)throw Error('Revisar possível compensação manual de '+nome+' em CONFIGURAÇÃO linha '+row+'; nenhuma entrada foi alterada');
 }
 return {reservaAtiva:ativos[0],bolsaAtiva:ativos[1]};
}
function planejar(snapshot,reverter=false){
 if(!snapshot||!Array.isArray(snapshot.cells))throw Error('Snapshot ausente');
 if(!reverter)conferirCompensacoes(snapshot);
 return planejarCelulas({...snapshot,cells:snapshot.cells.map(d=>({...d,value:normalizar(d.value??null)}))},reverter,plano.map(d=>({...d,antes:normalizar(d.antes),depois:normalizar(d.depois)})));
}
// Somente comparadores históricos. Retira todos os seis alvos, atomicamente.
function reverterModelo(abas){
 const ops=plano.map(d=>{const a=abas.find(a=>a.nome===d.aba),lista=a&&(d.addr?a.notas:a.vals),v=lista&&lista.filter(v=>d.addr?v[0]===d.addr:v[0]===d.r&&v[1]===d.c),pos=d.addr?1:2;if(!v||v.length!==1||v[0][pos]!==d.depois)throw Error('Molde Reserva/Bolsa divergente');return {d,lista,v:v[0],pos};});
 for(const {d,lista,v,pos}of ops)if(d.antes===null)lista.splice(lista.indexOf(v),1);else v[pos]=d.antes;
 return abas;
}
module.exports={BASE,plano,AUX,molde,prepararCodigo,planejar,conferirCompensacoes,reverterModelo,normalizar};
if(require.main===module){const [a,b]=process.argv.slice(2);fs.writeFileSync(b,prepararCodigo(fs.readFileSync(a,'utf8')));console.log(sha(fs.readFileSync(b,'utf8')));}
