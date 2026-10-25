/** Painel de missões: mesmo XP/nível, sem carregar os catálogos de combate. */
function salarioMissaoDireta_(e) {
 var r=e.range,l1=r.getRow(),l2=r.getLastRow(),c1=r.getColumn(),c2=r.getLastColumn();
 if(r.getSheet().getName()!=='FICHA PESSOAL'||l1<15||l2>87||c1<49||c2>72)return false;
 var ss=e.source||SpreadsheetApp.getActive(),sh=r.getSheet(),idioma;
 SALARIO_MISSOES_MOLDES_.forEach(function(t){
  if(t[0]<l1||t[0]>l2||t[1]<c1||t[1]>c2)return;
  sh.getRange(t[0],t[1]).setFormula(r53Formula_(t[2],ss));
 });
 // O índice e a curva continuam sendo os da campanha, inclusive custom.
 // Excluir as linhas 1–3 evita consultar todos os resultados de combate.
 var dados=ss.getSheetByName('DADOS').getRange('AQ4:DP100').getValues(),xpCell,nivelCell;
 dados.forEach(function(row){if(row[76]==='xp total')xpCell=String(row[77]);if(row[10]==='nivel')nivelCell=String(row[11]);});
 if(!xpCell||!nivelCell)throw Error('Índice de XP/nível ausente.');
 var total=Number(sh.getRange(xpCell).getValue());if(isNaN(total))return true;
 var tabela=salarioTabelaDados_(dados,'nível',['xp acumulado']).map(function(l){return {nivel:l['nível'],xp:l['xp acumulado']};});
 var limiar=Number((salarioTabelaDados_(dados,'limiar do feito')[0]||{})['limiar do feito'])||0;
 var cell=ss.getSheetByName('FICHA').getRange(nivelCell),atual=Number(cell.getValue())||0;
 var sobe=salarioNivelQueSobe_(tabela,total,atual,limiar);if(sobe!==null)cell.setValue(sobe);
 if(typeof r53ContinuarPaletaPendente_==='function')r53ContinuarPaletaPendente_(e);
 else if(typeof continuarPaleta_==='function')continuarPaleta_(e.r53Inicio_||Date.now(),null,false,r);
 return true;
}

function salarioTabelaDados_(dados,chave,outras){
 outras=outras||[];
 for(var r=0;r<dados.length;r++){
  var c=dados[r].indexOf(chave);if(c<0)continue;
  var cols=outras.map(function(o){return dados[r].indexOf(o);});if(cols.some(function(n){return n<0;}))continue;
  var out=[];for(var l=r+1;l<dados.length&&dados[l][c]!==''&&dados[l][c]!==null;l++){
   var item={};item[chave]=dados[l][c];outras.forEach(function(o,i){item[o]=dados[l][cols[i]];});out.push(item);
  }return out;
 }return [];
}
function salarioNivelQueSobe_(tabela,xp,atual,limiar){
 var alvo=null;tabela.forEach(function(l){if(Number(l.xp)<=xp)alvo=Number(l.nivel);});
 if(alvo===null)return null;if(limiar&&atual<=limiar)alvo=Math.min(alvo,limiar);return alvo>atual?alvo:null;
}
