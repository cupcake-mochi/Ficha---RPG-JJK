/** Emissão e salários. Apenas a planilha vinculada; sem rede ou acesso a outras fichas. */
var SALARIO_ = {versao:1, config:'CONFIGURAÇÃO', dados:'DADOS_SALARIOS', livro:'SALÁRIOS',
  primeira:15, ultima:87, colunas:[49,55,61,67], tipos:['Curta','Padrão','Longa','Final de arco','Solo simples','Solo complexa'],
  graus:['Grau 4','Grau 3','Grau 2','Grau 1','Especial']};

function salarioHoje_() {return salarioDiaISO_(Utilities.formatDate(new Date(),'America/Sao_Paulo','yyyy-MM-dd'));}
function salarioDiaISO_(s) {var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s);if(!m)return NaN;return Math.floor(Date.UTC(+m[1],+m[2]-1,+m[3])/86400000)+25569;}
function salarioDia_(v) {
  if(v instanceof Date)return salarioDiaISO_(Utilities.formatDate(v,'America/Sao_Paulo','yyyy-MM-dd'));
  if(typeof v==='number'&&isFinite(v)&&v>0&&v%1===0)return v;
  return NaN;
}
function salarioData_(d) {return new Date((d-25569)*86400000+12*3600000);}
function salarioTextoDia_(d) {return Utilities.formatDate(salarioData_(d),'America/Sao_Paulo','dd/MM/yyyy');}
function salarioLiteral_(s) {s=String(s);return /^[=+\-@']/.test(s)?"'"+s:s;}
function salarioToca_(r,l1,l2,c1,c2) {return r.getRow()<=l2&&r.getLastRow()>=l1&&r.getColumn()<=c2&&r.getLastColumn()>=c1;}
function salarioInt_(v,min,max,nome) {if(typeof v!=='number'||!isFinite(v)||v%1||v<min||v>max)throw Error('Revise '+nome+'.');return v;}
function salarioPercentual_(p,meta,minimo,verifica) {return verifica?minimo+(1-minimo)*Math.min(meta,Math.max(0,p))/meta:1;}
function salarioValor_(base,p,meta,minimo,verifica) {return Math.floor(base*salarioPercentual_(p,meta,minimo,verifica)+1e-8);}
function salarioEstado_(ss) {var sh=ss.getSheetByName(SALARIO_.dados),v=sh.getRange('L2').getValue();return v?JSON.parse(v):{};}
function salarioSalvarEstado_(ss,s) {ss.getSheetByName(SALARIO_.dados).getRange('L2').setValue(JSON.stringify(s));}
function salarioConfig_(ss) {
  var sh=ss.getSheetByName(SALARIO_.config),v=sh.getRange('O38:O44').getValues().map(function(r){return r[0];});
  var c={emissao:salarioDia_(v[0]),ligado:v[2]===true,dias:salarioInt_(v[3],1,3650,'o intervalo em dias'),
    meta:salarioInt_(v[4],1,1000,'a meta de participações'),minimo:v[5],verifica:v[6]===true,bases:{},pesos:{}};
  if(!isFinite(c.emissao))throw Error('Informe uma data de emissão válida em O38.');
  if(typeof c.minimo!=='number'||!isFinite(c.minimo)||c.minimo<0||c.minimo>1)throw Error('A parcela mínima deve estar entre 0% e 100%.');
  sh.getRange('O54:O58').getValues().forEach(function(r,i){c.bases[SALARIO_.graus[i]]=salarioInt_(r[0],0,1e12,'o salário de '+SALARIO_.graus[i]);});
  sh.getRange('O62:O67').getValues().forEach(function(r,i){c.pesos[SALARIO_.tipos[i]]=salarioInt_(r[0],0,1000,'o peso de '+SALARIO_.tipos[i]);});
  c.proximo=salarioDia_(sh.getRange('O48').getValue());
  return c;
}
function salarioMissoesAtuais_(ss) {
  var pessoal=ss.getSheetByName('FICHA PESSOAL'),faixa=pessoal.getRange(15,49,73,24),notas=faixa.getNotes(),out=[];
  out.faixa=faixa;out.notas=notas;out.limpar=[];
  // Leia somente as entradas literais. Os totais de XP ao lado podem exigir o recálculo da ficha inteira.
  SALARIO_.colunas.forEach(function(col){var v=pessoal.getRange(15,col,73,2).getValues();for(var i=0;i<73;i++){
    var nome=String(v[i][0]||'').trim(),tipo=String(v[i][1]||'').trim();
    var match=/\[Salário: ([^\] ·]+) · [^\]]+\]/.exec(notas[i][col-49]);
    if(nome&&SALARIO_.tipos.indexOf(tipo)>=0)out.push({key:col+':'+(i+15),nome:nome,tipo:tipo,id:match?match[1]:'',row:i,off:col-49});
    if(!nome&&match)out.limpar.push([i,col-49]);
  }});return out;
}
/** A identidade viaja na nota da célula. Uma cópia da mesma missão não renova sua data. */
function salarioSincronizar_(ss,estado,hoje,baseline,adiar) {
  var sh=ss.getSheetByName(SALARIO_.dados),n=Math.max(0,sh.getLastRow()-1);
  var old=n?sh.getRange(2,1,n,7).getValues().filter(function(r){return r[0];}):[],map={},seen={},changed=false;
  var porCaixa={};old.forEach(function(r){map[r[0]]=r;if(r[4]===true)porCaixa[r[5]]=r;});
  var atuais=salarioMissoesAtuais_(ss),notesChanged=false;
  function semMarca(s){return s.replace(/(?:\n)?\[Salário: [^\]\n]+\]/g,'');}
  atuais.forEach(function(m){
    var row=m.id?map[m.id]:porCaixa[m.key],id=row?row[0]:(m.id||Utilities.getUuid());
    if(seen[id])return;seen[id]=true;
    // Corrigir o nome conserva a data; para uma nova missão, limpe primeiro o nome antigo.
    if(!row){row=[id,salarioLiteral_(m.nome),m.tipo,baseline?'':hoje,true,m.key,hoje];old.push(row);map[id]=row;changed=true;}
    if(row[1]!==m.nome||row[2]!==m.tipo||row[4]!==true||row[5]!==m.key){row[1]=salarioLiteral_(m.nome);row[2]=m.tipo;row[4]=true;row[5]=m.key;changed=true;}
    var note=semMarca(atuais.notas[m.row][m.off])+'\n[Salário: '+id+' · '+(row[3]!==''?salarioTextoDia_(row[3]):'data pendente')+']';
    if(atuais.notas[m.row][m.off]!==note){atuais.notas[m.row][m.off]=note;notesChanged=true;}
  });
  atuais.limpar.forEach(function(p){atuais.notas[p[0]][p[1]]=semMarca(atuais.notas[p[0]][p[1]]);notesChanged=true;});
  old.forEach(function(r){if(!seen[r[0]]&&r[4]===true){r[4]=false;changed=true;}});
  var max=sh.getMaxRows();
  old.gravar=function(){
    if(changed&&old.length){
      if(max<old.length+1)sh.insertRowsAfter(max,old.length+1-max);
      // O Sheets interpreta "49:18" como duração. A caixa precisa continuar texto para a correção de datas.
      sh.getRange(2,1,old.length,7).setValues(old.map(function(r){var v=r.slice();v[5]="'"+r[5];return v;}));
    }
    if(notesChanged)atuais.faixa.setNotes(atuais.notas);
  };
  if(!adiar)old.gravar();
  return old;
}
function salarioPontos_(missoes,inicio,fim,pesos) {return missoes.reduce(function(n,r){return n+(r[4]===true&&typeof r[3]==='number'&&r[3]>=inicio&&r[3]<fim?(pesos[r[2]]||0):0);},0);}
function salarioGrauNoFim_(hist,fim) {var g='';hist.forEach(function(r){if(r[0]<fim)g=r[1];});return g;}
function salarioHistoricoGrau_(ss,estado,hoje,grau) {
  var hist=estado.graus||[];
  if(!hist.length)hist.push([Math.min(estado.inicio,hoje),grau]);
  else if(hist[hist.length-1][1]!==grau)hist.push([hoje,grau]);
  estado.graus=hist;return hist;
}
function salarioFechamentos_(ss) {var sh=ss.getSheetByName(SALARIO_.livro),n=sh.getLastRow()-1,rows=n>0?sh.getRange(2,1,n,12).getValues().filter(function(r){return r[0];}):[];rows.proximaLinha=n+2;rows.maxLinhas=sh.getMaxRows();return rows;}
function salarioStatus_(ss,texto) {var c=ss.getSheetByName(SALARIO_.config).getRange('O46');if(SALARIO_.formula&&String(texto).charAt(0)!=='⚠')c.setFormula(SALARIO_.f.painel.O46);else c.setValue(texto);}
function salarioLigacoes_(ss) {
  var p=ss.getSheetByName('FICHA PESSOAL');
  var formula=SALARIO_.formula?SALARIO_.f.total:'=O86+SUM(\'SALÁRIOS\'!J2:J)';
  if(p.getRange('W86').getFormula()!==formula)p.getRange('W86').setFormula(formula);
}
function salarioBloqueado_(ss,fn,espera) {
  var lock=LockService.getDocumentLock();if(!lock.tryLock(espera||1500))return false;
  try {return fn();}finally{try{SpreadsheetApp.flush();}finally{lock.releaseLock();}}
}
/** Fechamentos [início,fim): a missão do dia do vencimento pertence ao próximo ciclo. */
function salarioApurar_(ss,hoje,cache) {
  cache=cache||{};
  if(SALARIO_.formula){
    var ms=cache.missoes||salarioSincronizar_(ss,cache.estado||salarioEstado_(ss),hoje,false,true);if(ms.gravar)ms.gravar();
    SpreadsheetApp.flush();var feito=salarioCongelar_(ss,hoje);salarioStatus_(ss,'');return feito;
  }
  var c=cache.config||salarioConfig_(ss),estado=cache.estado||salarioEstado_(ss),missoes=cache.missoes||salarioSincronizar_(ss,estado,hoje,false,true);
  var pagos=salarioFechamentos_(ss),ultimo=pagos.length?pagos[pagos.length-1]:null;
  if(ultimo){estado.inicio=Math.max(salarioDia_(ultimo[2]),c.emissao);}
  else {estado.inicio=c.emissao;if(estado.graus&&estado.graus.length)estado.graus[0][0]=Math.min(c.emissao,estado.graus[0][0]);}
  var grau=String(ss.getSheetByName('FICHA PESSOAL').getRange('AB11').getValue()),hist=salarioHistoricoGrau_(ss,estado,hoje,grau);
  var personagem=String(ss.getSheetByName('CARTEIRA').getRange('O9').getValue()||'').trim();
  if(personagem==='Coloque o nome do personagem aqui')personagem='';
  var inicio=estado.inicio,novos=[],prazo=Date.now()+12000;
  if(c.ligado&&personagem){
    while(inicio+c.dias<=hoje&&novos.length<120&&Date.now()<prazo){
      var fim=inicio+c.dias,g=salarioGrauNoFim_(hist,fim);
      if(!Object.prototype.hasOwnProperty.call(c.bases,g))throw Error('Grau sem referência no fechamento. Revise o histórico.');
      var pontos=salarioPontos_(missoes,inicio,fim,c.pesos),pct=salarioPercentual_(pontos,c.meta,c.minimo,c.verifica);
      var id='SAL1:'+inicio+':'+fim;
      if(pagos.some(function(r){return r[0]===id;}))throw Error('Período já registrado. Revise o histórico de salários.');
      novos.push([id,salarioData_(inicio),salarioData_(fim),salarioData_(hoje),g,c.bases[g],pontos,c.meta,pct,salarioValor_(c.bases[g],pontos,c.meta,c.minimo,c.verifica),
        c.verifica?'Participação no período':'Participação dispensada pela campanha',JSON.stringify({dias:c.dias,minimo:c.minimo,pesos:c.pesos,personagem:personagem})]);
      inicio=fim;
    }
    if(novos.length){var sh=ss.getSheetByName(SALARIO_.livro),at=pagos.proximaLinha;
      if(pagos.maxLinhas<at+novos.length)sh.insertRowsAfter(pagos.maxLinhas,at+novos.length-pagos.maxLinhas);
      sh.getRange(at,1,novos.length,12).setValues(novos);
    }
  }
  if(missoes.gravar)missoes.gravar();
  estado.inicio=inicio;estado.ultimaEmissao=c.emissao;salarioSalvarEstado_(ss,estado);
  var config=ss.getSheetByName(SALARIO_.config),p=salarioPontos_(missoes,inicio,inicio+c.dias,c.pesos);
  config.getRange('O48').setValue(salarioData_(inicio+c.dias));
  config.getRange('O69:O72').setValues([[salarioData_(inicio)],[p],[Object.prototype.hasOwnProperty.call(c.bases,grau)?salarioValor_(c.bases[grau],p,c.meta,c.minimo,c.verifica):'Grau inválido'],[novos.length?salarioData_(inicio):ultimo?ultimo[2]:'Nenhum']]);
  salarioStatus_(ss,!c.ligado?'Salário pausado; períodos pendentes serão apurados ao religar.':!personagem?'Aguardando o nome do personagem na CARTEIRA.':inicio+c.dias<=hoje?'Há períodos pendentes; execute Conferir salários novamente.':'Em dia · próximo fechamento '+salarioTextoDia_(inicio+c.dias));
  return {novos:novos.length,inicio:inicio,proximo:inicio+c.dias,pontos:p};
}
function salarioSeguro_(ss,espera) {return salarioBloqueado_(ss,function(){try{return salarioApurar_(ss,salarioHoje_());}catch(err){salarioStatus_(ss,'⚠ '+err.message);console.log('Salários: '+err.message);return false;}},espera);}
function salarioPronto_(ss) {var sh=ss.getSheetByName(SALARIO_.dados);return !!sh&&!!sh.getRange('L2').getValue();}
function salarioMenu_() {
  SpreadsheetApp.getUi().createMenu('Salários').addItem('Conferir salários agora','conferirSalarios')
    .addItem('Data da missão selecionada…','definirDataMissaoSalario').addSeparator()
    .addItem('Ativar conferência diária','ativarSalarioDiario').addItem('Desativar conferência diária','desativarSalarioDiario').addToUi();
}
function salarioAbrir_() {
  salarioMenu_();
  // Abrir nunca fecha períodos: cópias também têm apenas 30 s. O diário,
  // a edição e Conferir salários fazem a apuração com bloqueio do documento.
}
function salarioEditar_(e) {
  if(!e||!e.range||e.salarioProcessado_)return false;e.salarioProcessado_=true;
  var r=e.range,n=r.getSheet().getName(),ss=e.source||SpreadsheetApp.getActive();
  var config=n===SALARIO_.config&&salarioToca_(r,35,76,11,17);
  var missao=n==='FICHA PESSOAL'&&(salarioToca_(r,15,87,49,72)||salarioToca_(r,11,11,28,30));
  var emitir=n==='CARTEIRA'&&salarioToca_(r,3,3,46,46);
  var nome=n==='CARTEIRA'&&salarioToca_(r,9,15,15,45);
  var total=n==='FICHA PESSOAL'&&salarioToca_(r,86,86,23,30);
  if(SALARIO_.formula&&n==='FICHA PESSOAL'&&salarioToca_(r,86,87,15,21)&&salarioGasto_(ss,r,e))return true;
  if(SALARIO_.formula&&n==='FICHA PESSOAL'&&salarioToca_(r,10,12,61,71)&&salarioCorrigirData_(ss,r,e))return true;
  if(SALARIO_.formula&&nome&&salarioPrimeiroNome_(e)){salarioBloqueado_(ss,function(){ss.getSheetByName(SALARIO_.config).getRange('O38').setValue(salarioData_(salarioHoje_()));},1500);return false;}
  if(!config&&!missao&&!nome&&!total&&!emitir)return false;
  // Com a rotina ativada, a edição instalável registra missões sem disputar o orçamento dos cartões/XP.
  if(!e.salarioInstalavel_&&PropertiesService.getScriptProperties().getProperty('salario_edicao')===ScriptApp.getScriptId()){
    if(total)salarioLigacoes_(ss);
    return config||emitir||total&&!missao;
  }
  // O estado é lido já sob bloqueio abaixo. Não repetir a leitura de L2
  // antes dele: cada consulta pode aguardar o recálculo da ficha.
  if(!ss.getSheetByName(SALARIO_.dados))return false;
  salarioBloqueado_(ss,function(){
    try {
      // A troca vai antes de qualquer leitura: até ela chegar, a fórmula paga o passado com o valor novo.
      var chave=SALARIO_.formula&&salarioChaveTroca_(r,n);
      if(chave){salarioRegistrarTroca_(ss,chave,e);return;}
      var cfg=ss.getSheetByName(SALARIO_.config),st=salarioEstado_(ss);
      if(total)salarioLigacoes_(ss);
      var controle=(config&&salarioToca_(r,39,39,15,17))||emitir;
      var reemitido=controle&&(e.value!==undefined?String(e.value).toUpperCase()==='TRUE':(emitir?r.getSheet().getRange('AT3'):cfg.getRange('O39')).getValue()===true);
      if(reemitido){
        // Não há fechamento vencido depois de emitir hoje. Só altere o ciclo
        // aberto; o livro de pagamentos e os gastos nunca participam desta ação.
        var dia=salarioHoje_(),dias=salarioInt_(cfg.getRange('O41').getValue(),1,3650,'o intervalo em dias');
        st.inicio=dia;st.ultimaEmissao=dia;salarioSalvarEstado_(ss,st);
        cfg.getRange('O38').setValue(salarioData_(dia));cfg.getRange('O39').setValue(false);ss.getSheetByName('CARTEIRA').getRange('AT3').setValue(false);
        if(SALARIO_.formula){salarioStatus_(ss,'');return;}
        cfg.getRange('O48').setValue(salarioData_(dia+dias));cfg.getRange('O69').setValue(salarioData_(dia));
        cfg.getRange('O70').setFormula('=SUMPRODUCT(N(\'DADOS_SALARIOS\'!E2:E=TRUE);N(ISNUMBER(\'DADOS_SALARIOS\'!D2:D));N(\'DADOS_SALARIOS\'!D2:D>=INT(O69));N(\'DADOS_SALARIOS\'!D2:D<INT(O48));IFERROR(VLOOKUP(\'DADOS_SALARIOS\'!C2:C;K62:O67;5;FALSE);0))');
        cfg.getRange('O71').setFormula('=ROUNDDOWN(O50*IF(O44;O43+(1-O43)*MIN(O42;MAX(0;O70))/O42;1);0)');
        salarioStatus_(ss,'Emissão atualizada · próximo fechamento '+salarioTextoDia_(dia+dias));
        return;
      }
      var hoje=salarioHoje_();
      // Por fórmula a edição só registra a missão; o pagamento já aparece na hora e o livro congela depois.
      if(SALARIO_.formula){if(missao&&!config&&salarioToca_(r,15,87,49,72))salarioSincronizar_(ss,st,hoje,false);return;}
      if(missao&&!config){
        var c=salarioConfig_(ss),g=String(ss.getSheetByName('FICHA PESSOAL').getRange('AB11').getValue()),ms=salarioSincronizar_(ss,st,hoje,false,true);
        salarioHistoricoGrau_(ss,st,hoje,g);
        if(!isFinite(c.proximo)||c.proximo<=hoje)salarioApurar_(ss,hoje,{config:c,estado:st,missoes:ms});
        else {var p=salarioPontos_(ms,st.inicio,c.proximo,c.pesos);ms.gravar();salarioSalvarEstado_(ss,st);cfg.getRange('O70:O71').setValues([[p],[salarioValor_(c.bases[g],p,c.meta,c.minimo,c.verifica)]]);}
      } else salarioApurar_(ss,hoje,{estado:st});
    }catch(err){salarioStatus_(ss,'⚠ '+err.message);console.log('Salários: '+err.message);}
  },e.salarioInstalavel_?120000:1500);
  return config||emitir||total&&!missao;
}
function conferirSalarios() {var ss=SpreadsheetApp.getActive();if(!salarioPronto_(ss))throw Error('Instale o módulo de salários primeiro.');return salarioSeguro_(ss,120000);}
function salarioDiario() {conferirSalarios();}
function salarioAposAbrir() {if(typeof revisarAbertura==='function')return revisarAbertura();}
function salarioRegistrarEdicao(e) {if(e){e.salarioInstalavel_=true;return salarioEditar_(e);}}
function ativarSalarioDiario() {
  var ss=SpreadsheetApp.getActive();if(!salarioPronto_(ss))throw Error('Instale salários primeiro.');
  var triggers=ScriptApp.getProjectTriggers();
  var ja=triggers.some(function(t){return t.getHandlerFunction()==='salarioDiario';});
  if(!ja)ScriptApp.newTrigger('salarioDiario').timeBased().everyDays(1).atHour(3).inTimezone('America/Sao_Paulo').create();
  if(!triggers.some(function(t){return t.getHandlerFunction()==='salarioRegistrarEdicao';}))ScriptApp.newTrigger('salarioRegistrarEdicao').forSpreadsheet(ss).onEdit().create();
  if(!triggers.some(function(t){return t.getHandlerFunction()==='salarioAposAbrir';}))ScriptApp.newTrigger('salarioAposAbrir').forSpreadsheet(ss).onOpen().create();
  PropertiesService.getScriptProperties().setProperty('salario_edicao',ScriptApp.getScriptId());
  salarioBloqueado_(ss,function(){var estado=salarioEstado_(ss);estado.agenda=ScriptApp.getScriptId();salarioSalvarEstado_(ss,estado);ss.getSheetByName(SALARIO_.config).getRange('O74').setValue('Diária · 03h–04h · Brasília');});
  return {diario:true,edicoes:true};
}
function desativarSalarioDiario() {
  ScriptApp.getProjectTriggers().forEach(function(t){if(t.getHandlerFunction()==='salarioDiario')ScriptApp.deleteTrigger(t);});
  var ss=SpreadsheetApp.getActive();salarioBloqueado_(ss,function(){var estado=salarioEstado_(ss);delete estado.agenda;salarioSalvarEstado_(ss,estado);ss.getSheetByName(SALARIO_.config).getRange('O74').setValue('Ao abrir ou editar a ficha');});
}
function definirDataMissaoSalario() {
  var ss=SpreadsheetApp.getActive(),r=ss.getActiveRange(),ui=SpreadsheetApp.getUi();
  if(!r||r.getSheet().getName()!=='FICHA PESSOAL'||r.getRow()<15||r.getRow()>87||r.getColumn()<49||r.getColumn()>72)throw Error('Selecione uma missão no painel MISSÕES E XP.');
  var col=49+6*Math.floor((r.getColumn()-49)/6),key=col+':'+r.getRow();
  var answer=ui.prompt('Data da missão','Data real de conclusão (dd/mm/aaaa). Períodos pagos ficam preservados.',ui.ButtonSet.OK_CANCEL);
  if(answer.getSelectedButton()!==ui.Button.OK)return;
  var m=/^(\d{2})\/(\d{2})\/(\d{4})$/.exec(answer.getResponseText().trim());if(!m)throw Error('Use dd/mm/aaaa.');
  var day=salarioDiaISO_(m[3]+'-'+m[2]+'-'+m[1]);if(salarioTextoDia_(day)!==m[0]||day>salarioHoje_())throw Error('Informe uma data válida, até hoje.');
  salarioBloqueado_(ss,function(){
    var pagos=salarioFechamentos_(ss),limite=pagos.length?salarioDia_(pagos[pagos.length-1][2]):-Infinity;
    if(day<limite)throw Error('Esse período já foi pago. O histórico não é recalculado.');
    var rows=salarioSincronizar_(ss,salarioEstado_(ss),salarioHoje_(),false),i=rows.findIndex(function(v){return v[5]===key&&v[4]===true;});
    if(i<0)throw Error('Preencha o nome e o tipo da missão primeiro.');
    ss.getSheetByName(SALARIO_.dados).getRange(i+2,4).setValue(day);salarioApurar_(ss,salarioHoje_());
  });
}
/** Migração incremental idempotente. Nunca constrói novamente a ficha. */
function instalarSalarios() {
  var ss=SpreadsheetApp.getActive();return salarioBloqueado_(ss,function(){
    if(salarioPronto_(ss))return salarioApurar_(ss,salarioHoje_());
    if(ss.getSheetByName(SALARIO_.dados)||ss.getSheetByName(SALARIO_.livro))throw Error('Instalação parcial: preserve os dados e revise antes de continuar.');
    var cfg=ss.getSheetByName(SALARIO_.config),pp=ss.getSheetByName('FICHA PESSOAL'),carteira=ss.getSheetByName('CARTEIRA');
    if(!cfg||!pp||!carteira||cfg.getRange('K35:Q95').getValues().some(function(r){return r.some(function(v){return v!=='';});}))throw Error('Área de configuração ocupada; migração interrompida.');
    var ds=ss.insertSheet(SALARIO_.dados),livro=ss.insertSheet(SALARIO_.livro);
    ds.getRange('A1:C1000').setNumberFormat('@');ds.getRange('F1:F1000').setNumberFormat('@');
    ds.getRange('A1:G1').setValues([['Identidade','Missão','Tipo','Data de conclusão (serial)','Presente','Caixa','Primeiro registro']]);ds.getRange('L1').setValue('Estado do módulo');
    livro.getRange('A1:L1').setValues([['Período','Início (inclusive)','Fim (exclusive)','Creditado em','Grau no fechamento','Salário de referência','Participações','Meta','Parcela','Salário creditado','Critério','Regra no fechamento']]);
    livro.setFrozenRows(1);livro.setHiddenGridlines(true);livro.getRange('A1:L1').setBackground('#4B273F').setFontColor('#FFFFFF').setFontWeight('bold').setWrap(true);livro.setRowHeight(1,50);
    livro.setColumnWidths(1,12,135);livro.setColumnWidth(1,210);livro.setColumnWidth(11,260);livro.hideColumns(12);
    livro.getRange('B2:D1000').setNumberFormat('dd/mm/yyyy');livro.getRange('F2:F1000').setNumberFormat('"¥ "#,##0');livro.getRange('I2:I1000').setNumberFormat('0%');livro.getRange('J2:J1000').setNumberFormat('"¥ "#,##0');
    livro.getRange('A1:K1000').protect().setDescription('Histórico fechado de salários; evite alterar pagamentos manualmente.').setWarningOnly(true);
    salarioCriarPainel_(cfg,carteira);
    pp.getRange('O85').setValue('IENES · AJUSTE MANUAL');pp.getRange('O86').setNote('Saldo e gastos manuais. Fórmulas continuam livres. Os salários ficam separados e somam no TOTAL DISPONÍVEL à direita.');
    pp.getRange('W85').setValue('TOTAL DISPONÍVEL');pp.getRange('W86').setFormula('=O86+SUM(\'SALÁRIOS\'!J2:J)').setNumberFormat('"¥ "#,##0').setNote('Saldo manual de O86 + salários fechados. Consulte valores, prazos e participação em CONFIGURAÇÃO → Emissão e salários.');
    var estado={versao:1,inicio:salarioHoje_(),graus:[],ultimaEmissao:salarioHoje_()};
    salarioSincronizar_(ss,estado,salarioHoje_(),true);salarioSalvarEstado_(ss,estado);ds.hideSheet();livro.hideSheet();
    if(SALARIO_.formula)salarioPrepararFormulas_(ss);
    return salarioApurar_(ss,salarioHoje_());
  });
}

/** Painel visível junto aos atalhos; livros de escrituração são abas técnicas ocultas. */
function salarioCriarPainel_(cfg,carteira) {
  cfg.getRange('K35:Q95').breakApart().setBackground('#FFF8F3').setFontFamily('Roboto').setFontSize(10).setFontColor('#382B35').setVerticalAlignment('middle').setWrap(true);
  function titulo(a,t){cfg.getRange(a).merge().setValue(t).setBackground('#4B273F').setFontColor('#FFFFFF').setFontWeight('bold');}
  titulo('K35:Q35','14 · EMISSÃO E SALÁRIOS');
  cfg.getRange('K36:Q36').merge().setValue('Data fixa em Brasília. Marque na carteira ou abaixo para emitir hoje.');cfg.setRowHeight(36,38);
  var labels={38:'Data de emissão',39:'Usar a data de hoje · Brasília',40:'Salário automático',41:'Intervalo entre salários · dias',42:'Participações para 100%',43:'Parcela mínima',44:'Verificar missões',46:'Situação',48:'Próximo fechamento',49:'Salários já creditados',50:'Referência do Grau atual',69:'Início do ciclo aberto',70:'Participações no ciclo',71:'Salário previsto',72:'Último fechamento',74:'Conferência automática'};
  Object.keys(labels).forEach(function(k){var row=+k;cfg.getRange(row,11,1,4).merge().setValue(labels[k]).setFontWeight('bold');cfg.getRange(row,15,1,3).merge();cfg.setRowHeight(row,row===46||row===74?54:30);});
  [[38,salarioData_(salarioHoje_())],[39,false],[40,true],[41,30],[42,3],[43,0.25],[44,true],[74,'Ao abrir ou editar a ficha']].forEach(function(v){cfg.getRange(v[0],15).setValue(v[1]);});
  [39,40,44].forEach(function(r){cfg.getRange(r,15).insertCheckboxes().setValue(r!==39);});
  [38,48,69,72].forEach(function(r){cfg.getRange(r,15).setNumberFormat('dd/mm/yyyy');});
  [49,50,71].forEach(function(r){cfg.getRange(r,15).setNumberFormat('"¥ "#,##0');});cfg.getRange('O43').setNumberFormat('0%');
  cfg.getRange('O38').setDataValidation(SpreadsheetApp.newDataValidation().requireDate().setAllowInvalid(false).build()).setNote('Data fixa. Reemitir após o último fechamento reinicia o ciclo sem apagar créditos; antecipar não repete pagamentos.');
  cfg.getRange('O39').setNote('Grava a data atual em America/Sao_Paulo e desmarca ao salvar.');
  cfg.getRange('O41:O42').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberBetween(1,3650).setAllowInvalid(false).build());
  cfg.getRange('O43').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberBetween(0,1).setAllowInvalid(false).build());
  titulo('K52:Q52','SALÁRIO POR GRAU');titulo('K60:Q60','PESO DAS MISSÕES');
  SALARIO_.graus.forEach(function(g,i){cfg.getRange(54+i,11,1,4).merge().setValue(g);cfg.getRange(54+i,15,1,3).merge().setValue(150000*Math.pow(2,i)).setNumberFormat('"¥ "#,##0');});
  SALARIO_.tipos.forEach(function(t,i){cfg.getRange(62+i,11,1,4).merge().setValue(t);cfg.getRange(62+i,15,1,3).merge().setValue([1,1,2,3,1,1][i]);});
  cfg.getRange('O54:O58').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberGreaterThanOrEqualTo(0).setAllowInvalid(false).build());
  cfg.getRange('O62:O67').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberGreaterThanOrEqualTo(0).setAllowInvalid(false).build());
  cfg.getRange('O66:O67').setNote('Participação salarial de solo: padrão 1 por decisão da campanha; configurável.');
  cfg.getRange('K76:Q76').merge().setValue('Missão conta ao preencher nome + tipo. Corrigir data: menu Salários → Data da missão selecionada.');cfg.setRowHeight(76,48);
  cfg.getRange('O49').setFormula('=SUM(\'SALÁRIOS\'!J2:J)');
  cfg.getRange('O50').setFormula('=IFERROR(VLOOKUP(\'FICHA PESSOAL\'!AB11;K54:O58;5;FALSE);0)');
  titulo('K78:Q78','ÚLTIMOS 10 CRÉDITOS · MAIS RECENTE PRIMEIRO');
  [['K80','Fechamento'],['L80:M80','Grau'],['N80:O80','Partic. / meta'],['P80:Q80','Creditado']].forEach(function(v){cfg.getRange(v[0]).merge().setValue(v[1]).setFontWeight('bold');});
  for(var i=1;i<=10;i++){
    var row=80+i;
    [['K',1],['L',3],['N',5],['P',8]].forEach(function(v){var col=v[0],expr='INDEX(SORT(FILTER(\'SALÁRIOS\'!C$2:J;\'SALÁRIOS\'!A$2:A<>" ");1;FALSE);'+i+';'+v[1]+')';expr=expr.replace('<>" "','<>""');if(col==='N')expr+='&" / "&INDEX(SORT(FILTER(\'SALÁRIOS\'!C$2:J;\'SALÁRIOS\'!A$2:A<>"");1;FALSE);'+i+';6)';var a=col+row+(col==='K'?'':':'+({L:'M',N:'O',P:'Q'}[col])+row);cfg.getRange(a).merge().setFormula('=IFERROR('+expr+';"")');});
    cfg.getRange('K'+row).setNumberFormat('dd/mm/yyyy');cfg.getRange('P'+row).setNumberFormat('"¥ "#,##0');
  }
  cfg.getRange('K93:Q95').merge().setValue('Os créditos são somados ao ajuste manual em FICHA PESSOAL. Continue lançando seus gastos nesse ajuste. O registro integral é guardado automaticamente em uma aba técnica oculta.');
  carteira.getRange('AH3:AT3').breakApart();carteira.getRange('AH3:AS3').merge().setFormula('="Emitida "&TEXT(\'CONFIGURAÇÃO\'!O38;"dd.mm.yyyy")');
  carteira.getRange('AT3').insertCheckboxes().setValue(false).setNote('Emitir hoje: grava a data atual do Brasil e desmarca após salvar.');
}

/** Salário por fórmula (24/10/2026). O pendente é calculado na hora pela planilha, em qualquer aparelho e cópia,
 * sem gatilho: DADOS_SALARIOS!P11 lista cada período vencido depois do livro e Q4 soma. O script só registra trocas
 * (H:J, "valor até a troca") e congela a tabela no livro quando houver tempo. Vale o Grau do dia do fechamento. */
SALARIO_.formula = true;
SALARIO_.f = {aux:[["Salário por fórmula", "Valor"], ["Início do 1º período pendente", "=LET(ult;MAX('SALÁRIOS'!C2:C);em;INT('CONFIGURAÇÃO'!O38);IF(ult>0;MAX(ult;em);em))"], ["Períodos vencidos", "=LET(nome;CARTEIRA!O9;IF(AND('CONFIGURAÇÃO'!O40=TRUE;LEN(nome)>0;nome<>\"Coloque o nome do personagem aqui\");MAX(0;FLOOR((TODAY()-Q2)/'CONFIGURAÇÃO'!O41));0))"], ["A creditar", "=IF($Q$3=0;0;SUM(INDEX(P11:Y;0;9)))"], ["Trocas registradas", "=COUNTA(H2:H)"], ["Fechamentos no livro", "=COUNTA('SALÁRIOS'!A2:A)"], ["Linhas do livro", "=ROWS('SALÁRIOS'!A:A)"], ["Intervalo (dias)", "='CONFIGURAÇÃO'!O41"]], cab:["Período", "Início", "Fim", "Grau", "Salário de referência", "Participações", "Meta", "Parcela", "Salário", "Critério"], tabela:"=IF($Q$3=0;\"\";LET(lin;LAMBDA(k;LET(s;$Q$2+k*'CONFIGURAÇÃO'!$O$41;e;s+'CONFIGURAÇÃO'!$O$41;h;LAMBDA(ch;atual;IFERROR(INDEX(FILTER('DADOS_SALARIOS'!$J$2:$J;'DADOS_SALARIOS'!$I$2:$I=ch;'DADOS_SALARIOS'!$H$2:$H>=e);1);atual));g;h(\"Grau\";'FICHA PESSOAL'!$AB$11);base;h(\"base:\"&g;IFERROR(VLOOKUP(g;'CONFIGURAÇÃO'!$K$54:$O$58;5;0);0));metav;h(\"meta\";'CONFIGURAÇÃO'!$O$42);mini;h(\"minimo\";'CONFIGURAÇÃO'!$O$43);vf;h(\"verifica\";'CONFIGURAÇÃO'!$O$44);p;SUM(MAP('CONFIGURAÇÃO'!$K$62:$K$67;'CONFIGURAÇÃO'!$O$62:$O$67;LAMBDA(t;w;h(\"peso:\"&t;w)*COUNTIFS('DADOS_SALARIOS'!$C$2:$C;t;'DADOS_SALARIOS'!$E$2:$E;TRUE;'DADOS_SALARIOS'!$D$2:$D;\">=\"&s;'DADOS_SALARIOS'!$D$2:$D;\"<\"&e))));pc;IF(vf;mini+(1-mini)*MIN(metav;MAX(0;p))/metav;1);HSTACK(\"SAL1:\"&s&\":\"&e;s;e;g;base;p;metav;pc;ROUNDDOWN(base*pc+0,00000001;0);IF(vf;\"Participação no período\";\"Participação dispensada pela campanha\"))));REDUCE(lin(0);SEQUENCE($Q$3;1;0);LAMBDA(acc;k;IF(k=0;acc;VSTACK(acc;lin(k)))))))", painel:{"O46": "=IF(O40<>TRUE;\"Salário pausado; períodos pendentes serão pagos ao religar.\";IF(NOT(AND(LEN(CARTEIRA!O9)>0;CARTEIRA!O9<>\"Coloque o nome do personagem aqui\"));\"Aguardando o nome do personagem na CARTEIRA.\";\"Em dia · próximo fechamento \"&TEXT(O48;\"dd/mm/yyyy\")))", "O48": "='DADOS_SALARIOS'!Q2+('DADOS_SALARIOS'!Q3+1)*O41", "O49": "=SUM('SALÁRIOS'!J2:J)+'DADOS_SALARIOS'!Q4", "O69": "='DADOS_SALARIOS'!Q2+'DADOS_SALARIOS'!Q3*O41", "O70": "=SUMPRODUCT(N('DADOS_SALARIOS'!E2:E=TRUE);N(ISNUMBER('DADOS_SALARIOS'!D2:D));N('DADOS_SALARIOS'!D2:D>=INT(O69));N('DADOS_SALARIOS'!D2:D<INT(O69)+O41);IFERROR(VLOOKUP('DADOS_SALARIOS'!C2:C;K62:O67;5;FALSE);0))", "O71": "=ROUNDDOWN(O50*IF(O44;O43+(1-O43)*MIN(O42;MAX(0;O70))/O42;1);0)", "O72": "=IF(INT(O69)>INT(O38);O69;\"Nenhum\")"},
  total:"=N(O86)+IFERROR(SUM(EXTRATO!B2:B);0)+SUM('SALÁRIOS'!J2:J)+'DADOS_SALARIOS'!Q4"};
/** Valor anterior de uma regra que muda o pagamento de períodos passados. Uma célula por vez (oldValue). */
function salarioChaveTroca_(r,n) {
  if(r.getRow()!==r.getLastRow())return '';
  if(n==='FICHA PESSOAL'&&r.getRow()===11&&r.getColumn()>=28&&r.getColumn()<=30)return 'Grau';
  if(n!==SALARIO_.config||r.getColumn()>15||r.getLastColumn()<15)return '';
  var l=r.getRow();
  if(l===42)return 'meta';if(l===43)return 'minimo';if(l===44)return 'verifica';
  if(l>=54&&l<=58)return 'base:'+SALARIO_.graus[l-54];
  if(l>=62&&l<=67)return 'peso:'+SALARIO_.tipos[l-62];
  return '';
}
function salarioValorTroca_(chave,v) {
  if(v===undefined||v===null||v==='')return undefined;
  if(chave==='Grau')return String(v);
  if(chave==='verifica')return v===true||String(v).toUpperCase()==='TRUE';
  var x=typeof v==='number'?v:Number(String(v).replace(',','.'));return isFinite(x)?x:undefined;
}
function salarioRegistrarTroca_(ss,chave,e) {
  var antes=salarioValorTroca_(chave,e.oldValue),agora=salarioValorTroca_(chave,e.value);
  if(antes===undefined||antes===agora)return false;
  // A contagem fica nas propriedades para não esperar uma leitura (3–5 s nesta ficha). Numa cópia ela não vem
  // junto: aí lê Q5 (=COUNTA de H) uma vez. A linha de cada troca é gravada sozinha, e o flush vem logo depois.
  var props=PropertiesService.getDocumentProperties(),guardado=props.getProperty('salario_trocas'),sh=ss.getSheetByName(SALARIO_.dados);
  var n=guardado!==null&&guardado!==''?Number(guardado):Number(sh.getRange('Q5').getValue())||0;
  sh.getRange(n+2,8,1,3).setValues([[salarioHoje_(),chave,antes]]);
  SpreadsheetApp.flush();
  props.setProperty('salario_trocas',String(n+1));
  return true;
}
/** Copia para o livro os períodos que a fórmula já calcula. Uma leitura; a fórmula recomeça no fim do livro. */
function salarioCongelar_(ss,hoje) {
  var sh=ss.getSheetByName(SALARIO_.dados),v=sh.getRange('P2:Y130').getValues();
  var nLivro=Number(v[4][1])||0,linhas=Number(v[5][1])||0,dias=Number(v[6][1])||0;
  var tabela=v.slice(9).filter(function(l){return /^SAL1:/.test(l[0]);});
  var proximo=Number(v[0][1])+(Number(v[1][1])+1)*dias;
  if(!tabela.length)return {novos:0,proximo:proximo};
  var novos=tabela.map(function(l){return [l[0],salarioData_(l[1]),salarioData_(l[2]),salarioData_(hoje),l[3],l[4],l[5],l[6],l[7],l[8],l[9],JSON.stringify({formula:true,dias:dias})];});
  var livro=ss.getSheetByName(SALARIO_.livro),at=nLivro+2;
  if(linhas<at+novos.length-1)livro.insertRowsAfter(linhas,at+novos.length-1-linhas);
  livro.getRange(at,1,novos.length,12).setValues(novos);
  return {novos:novos.length,proximo:proximo};
}
/** Uma vez por ficha (pelo editor ou na instalação): colunas auxiliares, painel e total em fórmula. */
function salarioPrepararFormulas_(ss) {
  var d=ss.getSheetByName(SALARIO_.dados),cfg=ss.getSheetByName(SALARIO_.config);
  d.getRange('H1:J1').setValues([['Troca (dia)','Regra','Valor até a troca']]);
  d.getRange(1,16,SALARIO_.f.aux.length,1).setValues(SALARIO_.f.aux.map(function(l){return [l[0]];}));
  d.getRange(1,17,1,1).setValue('Valor');
  d.getRange(2,17,SALARIO_.f.aux.length-1,1).setFormulas(SALARIO_.f.aux.slice(1).map(function(l){return [l[1]];}));
  d.getRange('P10:Y10').setValues([SALARIO_.f.cab]);d.getRange('P11').setFormula(SALARIO_.f.tabela);
  Object.keys(SALARIO_.f.painel).forEach(function(a){cfg.getRange(a).setFormula(SALARIO_.f.painel[a]);});
  cfg.getRange('O74').setValue('Na hora, por fórmula');
  // Últimos 10 créditos: livro + pendente da fórmula, numa faixa só (AA:AH), lida pelo painel.
  if(d.getMaxColumns()<34)d.insertColumnsAfter(d.getMaxColumns(),34-d.getMaxColumns());
  d.getRange('AA1').setValue('Últimos créditos (livro + pendente)');d.getRange('AA2').setFormula(SALARIO_.f.ultimos);
  for(var i=1;i<=10;i++)[['K',1],['L',3],['N',5],['P',8]].forEach(function(v){cfg.getRange(v[0]+(80+i)).setFormula(salarioUltimo_(i,v[1],v[0]==='N'));});
  salarioPrepararCarteira_(ss);
  salarioPrepararCorrecao_(ss);
  salarioLigacoes_(ss);
  return true;
}
function atualizarSalarioFormula() {var ss=SpreadsheetApp.getActive();return salarioBloqueado_(ss,function(){return salarioPrepararFormulas_(ss);},30000);}

/** Dinheiro como a vida (24/10/2026): O86 é a caixa ± GASTO / GANHO. O valor digitado vira uma linha da aba oculta
 * EXTRATO e a caixa limpa; o saldo é a soma do extrato. O total soma também o que ainda estiver na caixa, então o
 * valor aparece na hora mesmo se o script não chegar a rodar. Nada lê a ficha no caminho comum. */
SALARIO_.extrato = 'EXTRATO';
SALARIO_.f.ultimos = "=IFERROR(ARRAY_CONSTRAIN(LET(a;VSTACK('SALÁRIOS'!C2:J;HSTACK(R11:R130;R11:R130;S11:X130));SORT(FILTER(a;ISNUMBER(INDEX(a;0;1)));1;FALSE));10;8);\"\")";
function salarioUltimo_(i,k,meta) {
  var c=function(k){return "INDEX('DADOS_SALARIOS'!$AA$2:$AH$11;"+i+';'+k+')';};
  return '=LET(v;'+c(k)+';IF(v="";"";'+(meta?'v&" / "&'+c(6):'v')+'))';
}
function salarioNumero_(v) {
  if(typeof v==='number')return v;
  var s=String(v===undefined||v===null?'':v).replace(/[−–]/g,'-').replace(/[¥\s]/g,'');
  s=/^[+-]?\d{1,3}(\.\d{3})+(,\d+)?$/.test(s)?s.replace(/\./g,'').replace(',','.'):s.replace(',','.');
  var x=s===''?NaN:Number(s);return isFinite(x)?x:NaN;
}
/** Uma vez por ficha: cria o EXTRATO com o saldo que estava em O86 e transforma O86 na caixa de lançamento. */
function salarioPrepararCarteira_(ss) {
  if(ss.getSheetByName(SALARIO_.extrato))return false;
  var pp=ss.getSheetByName('FICHA PESSOAL'),c=pp.getRange('O86'),antes=c.getValue(),formula=c.getFormula();
  var ex=ss.insertSheet(SALARIO_.extrato),linhas=[];
  ex.getRange('A1:C1').setValues([['Data','Valor','Origem']]).setFontWeight('bold').setBackground('#4B273F').setFontColor('#FFFFFF');
  ex.setFrozenRows(1);ex.setColumnWidth(1,140);ex.setColumnWidth(2,120);ex.setColumnWidth(3,320);
  ex.getRange('A2:A').setNumberFormat('dd/mm/yyyy hh:mm');ex.getRange('B2:B').setNumberFormat('"¥ "#,##0;"−¥ "#,##0');
  var saldo=salarioNumero_(antes);
  if(isFinite(saldo)&&saldo!==0)linhas.push([new Date(),saldo,'Saldo anterior (Ienes · ajuste manual'+(formula?', fórmula '+formula:'')+')']);
  if(linhas.length)ex.getRange(2,1,linhas.length,3).setValues(linhas);
  ex.getRange('A1:C').protect().setDescription('Extrato de ienes; os lançamentos entram pela caixa ± GASTO / GANHO da FICHA PESSOAL.').setWarningOnly(true);
  ex.hideSheet();
  pp.getRange('O85').setValue('± GASTO / GANHO');
  c.clearContent().setNumberFormat('"¥ "#,##0;"−¥ "#,##0')
    .setDataValidation(SpreadsheetApp.newDataValidation().requireNumberBetween(-1e12,1e12).setAllowInvalid(false).setHelpText('Digite só o número: −500 para gasto, 2000 para ganho.').build())
    .setNote('Digite o gasto (−500) ou o ganho (2000). O valor entra no saldo, a caixa limpa e o lançamento fica na aba oculta EXTRATO.');
  pp.getRange('W86').setFormula(SALARIO_.f.total).setNote('Saldo do extrato + salários fechados + salário pendente. Valores e prazos em CONFIGURAÇÃO → Emissão e salários; lançamentos na aba oculta EXTRATO.');
  ss.getSheetByName(SALARIO_.config).getRange('K93').setValue('Os créditos somam no TOTAL DISPONÍVEL em FICHA PESSOAL. Gastos e ganhos vão na caixa ± GASTO / GANHO ao lado; cada lançamento fica na aba oculta EXTRATO.');
  PropertiesService.getDocumentProperties().setProperty('salario_extrato',String(linhas.length));
  return true;
}
/** Lança o que foi digitado em O86. true = a edição está tratada (não segue para o resto da ficha). */
function salarioGasto_(ss,r,e) {
  if(!e.salarioInstalavel_&&PropertiesService.getScriptProperties().getProperty('salario_edicao')===ScriptApp.getScriptId())return true;
  var ex=ss.getSheetByName(SALARIO_.extrato);if(!ex)return false;
  var v=salarioNumero_(e.value);
  // Colagem, fórmula ou célula mesclada sem e.value: aí sim lê a caixa (uma leitura).
  if(isNaN(v)&&e.value===undefined)v=salarioNumero_(r.getCell(1,1).getValue());
  if(isNaN(v))return true;
  var caixa=ss.getSheetByName('FICHA PESSOAL').getRange('O86');
  salarioBloqueado_(ss,function(){
    try {
      if(v!==0){
        // Contagem nas propriedades, como nas trocas; numa cópia ela não vem junto e lê a última linha uma vez.
        var props=PropertiesService.getDocumentProperties(),guardado=props.getProperty('salario_extrato');
        var n=guardado!==null&&guardado!==''?Number(guardado):ex.getLastRow()-1;
        ex.getRange(n+2,1,1,3).setValues([[new Date(),v,'Ficha · '+(v<0?'gasto':'ganho')]]);
        caixa.clearContent();SpreadsheetApp.flush();
        props.setProperty('salario_extrato',String(n+1));
      } else caixa.clearContent();
    }catch(err){salarioStatus_(ss,'⚠ '+err.message);console.log('Ienes: '+err.message);}
  },10000);
  return true;
}
/** Corrigir a data de uma missão pelo celular (o app do Android não mostra o menu Salários): o jogador escreve o
 * nome em BI11 e a data em BO11. O resultado (✓ ou ⚠) aparece na própria caixa da data; deu certo, o nome limpa. */
SALARIO_.correcao = {nome:'BI11', data:'BO11', colunaData:67};
function salarioDataDigitada_(v) {
  if(typeof v==='number')return salarioDia_(v);
  if(v instanceof Date)return salarioDia_(v);
  var m=/^(\d{1,2})\/(\d{1,2})(?:\/(\d{2}|\d{4}))?$/.exec(String(v===undefined||v===null?'':v).trim());if(!m)return NaN;
  var z=function(x){return ('0'+x).slice(-2);},ano=m[3]?(m[3].length===2?'20'+m[3]:m[3]):salarioTextoDia_(salarioHoje_()).slice(-4);
  var dia=salarioDiaISO_(ano+'-'+z(m[2])+'-'+z(m[1]));
  return isFinite(dia)&&salarioTextoDia_(dia)===z(m[1])+'/'+z(m[2])+'/'+ano?dia:NaN;
}
/** Uma vez por ficha: a caixa vai no espaço livre sob MAIS MISSÕES, no mesmo formato do XP TOTAL (AW10:BA12). */
function salarioPrepararCorrecao_(ss) {
  var p=ss.getSheetByName('FICHA PESSOAL');
  if(p.getRange('BI10').getValue()!=='')return false;
  var modelo=p.getRange('AW10:BA12'),copia=SpreadsheetApp.CopyPasteType.PASTE_FORMAT;
  modelo.copyTo(p.getRange('BI10:BM12'),copia,false);modelo.copyTo(p.getRange('BO10:BS12'),copia,false);
  p.getRange('BI10:BM10').merge().setValue('CORRIGIR DATA · NOME DA MISSÃO');p.getRange('BO10:BS10').merge().setValue('DATA REAL · dd/mm/aaaa');
  p.getRange('BI11:BM12').merge().setNumberFormat('@').setFontSize(11).setWrap(true)
    .setNote('Escreva o nome da missão como está na lista e, ao lado, a data real em que ela foi concluída.');
  p.getRange('BO11:BS12').merge().setNumberFormat('@').setFontSize(11).setWrap(true)
    .setNote('Data real da missão (dd/mm/aaaa). Aqui aparece ✓ quando a data é corrigida, ou ⚠ com o motivo.');
  ss.getSheetByName(SALARIO_.config).getRange('K76').setValue('Missão conta ao preencher nome + tipo. Corrigir data: caixa CORRIGIR DATA em FICHA PESSOAL (acima de MAIS MISSÕES), ou menu Salários no PC.');
  return true;
}
function salarioCorrigirData_(ss,r,e) {
  if(!e.salarioInstalavel_&&PropertiesService.getScriptProperties().getProperty('salario_edicao')===ScriptApp.getScriptId())return true;
  var p=ss.getSheetByName('FICHA PESSOAL'),cNome=p.getRange(SALARIO_.correcao.nome),cData=p.getRange(SALARIO_.correcao.data);
  var editouData=r.getColumn()>=SALARIO_.correcao.colunaData;
  var feito=function(v){return /^[✓⚠]/.test(String(v));};
  // O nome digitado fica nas propriedades: quem escreve nome e depois data não paga a leitura da caixa (3–5 s).
  var props=PropertiesService.getDocumentProperties(),guardado=props.getProperty('salario_correcao_nome');
  if(!editouData)props.setProperty('salario_correcao_nome',String(e.value===undefined?'':e.value));
  var nome=editouData?(guardado!==null?guardado:cNome.getValue()):e.value,data=editouData?e.value:cData.getValue();
  nome=String(nome===undefined||nome===null?'':nome).trim();
  if(!nome||data===undefined||data===''||feito(data))return true;
  var dia=salarioDataDigitada_(data),hoje=salarioHoje_();
  salarioBloqueado_(ss,function(){
    var aviso=function(t){cData.setValue('⚠ '+t);};
    if(!isFinite(dia))return aviso('Data inválida: use dd/mm/aaaa');
    if(dia>hoje)return aviso('A data não pode ser depois de hoje');
    var sh=ss.getSheetByName(SALARIO_.dados),v=sh.getRange(1,1,sh.getMaxRows(),17).getValues();
    // Q2 tem formato de data: getValues devolve Date, não o número de série.
    var inicio=salarioDia_(v[1][16]);
    if(isFinite(inicio)&&dia<inicio)return aviso('Essa data cai num período já pago');
    var chave=function(x){return String(x).replace(/^'/,'').trim().toLowerCase();},alvo=chave(nome),achou=[];
    for(var i=1;i<v.length;i++)if(v[i][0]&&v[i][4]===true&&chave(v[i][1])===alvo)achou.push(i);
    if(!achou.length)return aviso('Nenhuma missão com esse nome');
    if(achou.length>1)return aviso('Mais de uma missão com esse nome');
    sh.getRange(achou[0]+1,4).setValue(dia);
    cNome.clearContent();cData.setValue('✓ '+nome+': '+salarioTextoDia_(dia));props.setProperty('salario_correcao_nome','');
  },10000);
  return true;
}
/** Cópia nova da ficha: o primeiro nome do personagem emite a carteira hoje. Sem isso a fórmula pagaria os
 * períodos desde a emissão que veio na cópia. Só vale quando o nome anterior estava vazio ou era o texto de exemplo. */
function salarioPrimeiroNome_(e) {
  if(e.value===undefined)return false;
  var vazio=function(v){v=v===undefined||v===null?'':String(v).trim();return v===''||v==='Coloque o nome do personagem aqui';};
  return vazio(e.oldValue)&&!vazio(e.value);
}
// FIM DO SALÁRIO POR FÓRMULA
