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
  var sh=ss.getSheetByName(SALARIO_.config),v=sh.getRange('G323:G329').getValues().map(function(r){return r[0];});
  var c={emissao:salarioDia_(v[0]),ligado:v[2]===true,dias:salarioInt_(v[3],1,3650,'o intervalo em dias'),
    meta:salarioInt_(v[4],1,1000,'a meta de participações'),minimo:v[5],verifica:v[6]===true,bases:{},pesos:{}};
  if(!isFinite(c.emissao))throw Error('Informe uma data de emissão válida em G323.');
  if(typeof c.minimo!=='number'||!isFinite(c.minimo)||c.minimo<0||c.minimo>1)throw Error('A parcela mínima deve estar entre 0% e 100%.');
  sh.getRange('G339:G343').getValues().forEach(function(r,i){c.bases[SALARIO_.graus[i]]=salarioInt_(r[0],0,1e12,'o salário de '+SALARIO_.graus[i]);});
  sh.getRange('P339:P344').getValues().forEach(function(r,i){c.pesos[SALARIO_.tipos[i]]=salarioInt_(r[0],0,1000,'o peso de '+SALARIO_.tipos[i]);});
  c.proximo=salarioDia_(sh.getRange('G333').getValue());
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
function salarioStatus_(ss,texto) {ss.getSheetByName(SALARIO_.config).getRange('G331').setValue(texto);}
function salarioLigacoes_(ss) {
  var p=ss.getSheetByName('FICHA PESSOAL');
  var formula='=O86+SUM(\'SALÁRIOS\'!J2:J)';
  if(p.getRange('W86').getFormula()!==formula)p.getRange('W86').setFormula(formula);
}
function salarioBloqueado_(ss,fn,espera) {
  var lock=LockService.getDocumentLock();if(!lock.tryLock(espera||1500))return false;
  try {return fn();}finally{try{SpreadsheetApp.flush();}finally{lock.releaseLock();}}
}
/** Fechamentos [início,fim): a missão do dia do vencimento pertence ao próximo ciclo. */
function salarioApurar_(ss,hoje,cache) {
  cache=cache||{};
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
  config.getRange('G333').setValue(salarioData_(inicio+c.dias));
  config.getRange('G348:G351').setValues([[salarioData_(inicio)],[p],[Object.prototype.hasOwnProperty.call(c.bases,grau)?salarioValor_(c.bases[grau],p,c.meta,c.minimo,c.verifica):'Grau inválido'],[novos.length?salarioData_(inicio):ultimo?ultimo[2]:'Nenhum']]);
  salarioStatus_(ss,!c.ligado?'Salário pausado; períodos pendentes serão apurados ao religar.':!personagem?'Aguardando o nome do personagem na CARTEIRA.':inicio+c.dias<=hoje?'Há períodos pendentes; execute Conferir salários novamente.':'Em dia · próximo fechamento '+salarioTextoDia_(inicio+c.dias));
  return {novos:novos.length,inicio:inicio,proximo:inicio+c.dias,pontos:p};
}
function salarioSeguro_(ss,espera) {return salarioBloqueado_(ss,function(){try{return salarioApurar_(ss,salarioHoje_());}catch(err){salarioStatus_(ss,'⚠ '+err.message);console.log('Salários: '+err.message);return false;}},espera);}
function salarioPronto_(ss) {var sh=ss.getSheetByName(SALARIO_.dados);return !!sh&&!!sh.getRange('L2').getValue();}
function salarioAbrir_() {
  var ss=SpreadsheetApp.getActive();if(!salarioPronto_(ss))return;
  var estado=salarioEstado_(ss);
  if(estado.agenda&&estado.agenda!==ScriptApp.getScriptId()){
    salarioBloqueado_(ss,function(){var atual=salarioEstado_(ss);delete atual.agenda;salarioSalvarEstado_(ss,atual);ss.getSheetByName(SALARIO_.config).getRange('G353').setValue('Ao abrir ou editar · ative a conferência diária nesta cópia');});
  }
  SpreadsheetApp.getUi().createMenu('Salários').addItem('Conferir salários agora','conferirSalarios')
    .addItem('Data da missão selecionada…','definirDataMissaoSalario').addSeparator()
    .addItem('Ativar conferência diária','ativarSalarioDiario').addItem('Desativar conferência diária','desativarSalarioDiario').addToUi();
  salarioLigacoes_(ss);
  var vencimento=salarioDia_(ss.getSheetByName(SALARIO_.config).getRange('G333').getValue());
  // O acionador diário tem seis minutos; o evento simples de abertura tem somente trinta segundos.
  if(!estado.agenda&&(!isFinite(vencimento)||vencimento<=salarioHoje_()))salarioSeguro_(ss);
}
function salarioEditar_(e) {
  if(!e||!e.range||e.salarioProcessado_)return false;e.salarioProcessado_=true;
  var r=e.range,n=r.getSheet().getName(),ss=e.source||SpreadsheetApp.getActive();
  var config=n===SALARIO_.config&&salarioToca_(r,320,355,3,17);
  var missao=n==='FICHA PESSOAL'&&(salarioToca_(r,15,87,49,72)||salarioToca_(r,11,11,28,30));
  var nome=n==='CARTEIRA'&&salarioToca_(r,9,15,15,45);
  var total=n==='FICHA PESSOAL'&&salarioToca_(r,86,86,23,30);
  if(!config&&!missao&&!nome&&!total)return false;if(!salarioPronto_(ss))return false;
  // Com a rotina ativada, a edição instalável registra missões sem disputar o orçamento dos cartões/XP.
  if(!e.salarioInstalavel_&&PropertiesService.getScriptProperties().getProperty('salario_edicao')===ScriptApp.getScriptId()){
    if(total)salarioLigacoes_(ss);
    return config||total&&!missao;
  }
  salarioBloqueado_(ss,function(){
    try {
      var cfg=ss.getSheetByName(SALARIO_.config),st=salarioEstado_(ss);
      if(total)salarioLigacoes_(ss);
      if(config&&salarioToca_(r,324,324,7,10)&&cfg.getRange('G324').getValue()===true){cfg.getRange('G323').setValue(salarioData_(salarioHoje_()));cfg.getRange('G324').setValue(false);}
      var hoje=salarioHoje_();
      if(missao&&!config){
        var c=salarioConfig_(ss),g=String(ss.getSheetByName('FICHA PESSOAL').getRange('AB11').getValue()),ms=salarioSincronizar_(ss,st,hoje,false,true);
        salarioHistoricoGrau_(ss,st,hoje,g);
        if(!isFinite(c.proximo)||c.proximo<=hoje)salarioApurar_(ss,hoje,{config:c,estado:st,missoes:ms});
        else {var p=salarioPontos_(ms,st.inicio,c.proximo,c.pesos);ms.gravar();salarioSalvarEstado_(ss,st);cfg.getRange('G349:G350').setValues([[p],[salarioValor_(c.bases[g],p,c.meta,c.minimo,c.verifica)]]);}
      } else salarioApurar_(ss,hoje,{estado:st});
    }catch(err){salarioStatus_(ss,'⚠ '+err.message);console.log('Salários: '+err.message);}
  },e.salarioInstalavel_?120000:1500);
  return config||total&&!missao;
}
function conferirSalarios() {var ss=SpreadsheetApp.getActive();if(!salarioPronto_(ss))throw Error('Instale o módulo de salários primeiro.');return salarioSeguro_(ss,120000);}
function salarioDiario() {conferirSalarios();}
function salarioRegistrarEdicao(e) {if(e){e.salarioInstalavel_=true;return salarioEditar_(e);}}
function ativarSalarioDiario() {
  var ss=SpreadsheetApp.getActive();if(!salarioPronto_(ss))throw Error('Instale salários primeiro.');
  var triggers=ScriptApp.getProjectTriggers();
  var ja=triggers.some(function(t){return t.getHandlerFunction()==='salarioDiario';});
  if(!ja)ScriptApp.newTrigger('salarioDiario').timeBased().everyDays(1).atHour(3).inTimezone('America/Sao_Paulo').create();
  if(!triggers.some(function(t){return t.getHandlerFunction()==='salarioRegistrarEdicao';}))ScriptApp.newTrigger('salarioRegistrarEdicao').forSpreadsheet(ss).onEdit().create();
  PropertiesService.getScriptProperties().setProperty('salario_edicao',ScriptApp.getScriptId());
  salarioBloqueado_(ss,function(){var estado=salarioEstado_(ss);estado.agenda=ScriptApp.getScriptId();salarioSalvarEstado_(ss,estado);ss.getSheetByName(SALARIO_.config).getRange('G353').setValue('Diária · 03h–04h · Brasília');});
  return {diario:true,edicoes:true};
}
function desativarSalarioDiario() {
  ScriptApp.getProjectTriggers().forEach(function(t){if(t.getHandlerFunction()==='salarioDiario')ScriptApp.deleteTrigger(t);});
  var ss=SpreadsheetApp.getActive();salarioBloqueado_(ss,function(){var estado=salarioEstado_(ss);delete estado.agenda;salarioSalvarEstado_(ss,estado);ss.getSheetByName(SALARIO_.config).getRange('G353').setValue('Ao abrir ou editar a ficha');});
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
    if(!cfg||!pp||!carteira||cfg.getRange('C320:Q355').getValues().some(function(r){return r.some(function(v){return v!=='';});}))throw Error('Área de configuração ocupada; migração interrompida.');
    var ds=ss.insertSheet(SALARIO_.dados),livro=ss.insertSheet(SALARIO_.livro);
    ds.getRange('A1:C1000').setNumberFormat('@');ds.getRange('F1:F1000').setNumberFormat('@');
    ds.getRange('A1:G1').setValues([['Identidade','Missão','Tipo','Data de conclusão (serial)','Presente','Caixa','Primeiro registro']]);ds.getRange('L1').setValue('Estado do módulo');
    livro.getRange('A1:L1').setValues([['Período','Início (inclusive)','Fim (exclusive)','Creditado em','Grau no fechamento','Salário de referência','Participações','Meta','Parcela','Salário creditado','Critério','Regra no fechamento']]);
    livro.setFrozenRows(1);livro.setHiddenGridlines(true);livro.getRange('A1:L1').setBackground('#4B273F').setFontColor('#FFFFFF').setFontWeight('bold').setWrap(true);livro.setRowHeight(1,50);
    livro.setColumnWidths(1,12,135);livro.setColumnWidth(1,210);livro.setColumnWidth(11,260);livro.hideColumns(12);
    livro.getRange('B2:D1000').setNumberFormat('dd/mm/yyyy');livro.getRange('F2:F1000').setNumberFormat('"¥ "#,##0');livro.getRange('I2:I1000').setNumberFormat('0%');livro.getRange('J2:J1000').setNumberFormat('"¥ "#,##0');
    livro.getRange('A1:K1000').protect().setDescription('Histórico fechado de salários; evite alterar pagamentos manualmente.').setWarningOnly(true);
    cfg.getRange('C320:Q355').breakApart().setBackground('#FFF8F3').setFontFamily('Roboto').setFontSize(10).setFontColor('#382B35').setVerticalAlignment('middle');
    cfg.getRange('C320:Q320').merge().setValue('14 · EMISSÃO E SALÁRIOS').setBackground('#4B273F').setFontColor('#FFFFFF').setFontWeight('bold');
    cfg.getRange('C321:Q321').merge().setValue('Data fixa e ciclos em dias corridos de Brasília. O histórico SALÁRIOS guarda cada crédito.').setWrap(true);cfg.setRowHeight(321,36);
    var labels={323:'Data de emissão',324:'Usar a data de hoje · Brasília',325:'Salário automático',326:'Intervalo entre salários · dias',327:'Participações para 100%',328:'Parcela mínima',329:'Verificar missões',331:'Situação',333:'Próximo fechamento',334:'Salários já creditados',335:'Referência do Grau atual',348:'Início do ciclo aberto',349:'Participações no ciclo',350:'Salário previsto',351:'Último fechamento',353:'Conferência automática'};
    Object.keys(labels).forEach(function(k){var row=+k;cfg.getRange(row,3,1,4).merge().setValue(labels[k]).setFontWeight('bold').setWrap(true);cfg.getRange(row,7,1,row===331||row===353?11:4).merge();cfg.setRowHeight(row,row===331||row===353?42:30);});
    cfg.getRange('G331:Q331').setWrap(true);cfg.getRange('G353:Q353').setWrap(true);
    [[323,salarioData_(salarioHoje_())],[324,false],[325,true],[326,30],[327,3],[328,0.25],[329,true],[353,'Ao abrir ou editar a ficha']].forEach(function(v){cfg.getRange(v[0],7).setValue(v[1]);});
    [324,325,329].forEach(function(r){cfg.getRange(r,7).insertCheckboxes().setValue(r!==324);});
    [323,333,348,351].forEach(function(r){cfg.getRange(r,7).setNumberFormat('dd/mm/yyyy');});
    [334,335,350].forEach(function(r){cfg.getRange(r,7).setNumberFormat('"¥ "#,##0');});cfg.getRange('G328').setNumberFormat('0%');
    cfg.getRange('G323').setDataValidation(SpreadsheetApp.newDataValidation().requireDate().setAllowInvalid(false).build()).setNote('Esta data inicia o ciclo. Uma reemissão posterior ao último pagamento reinicia a contagem, preservando créditos anteriores. Uma data anterior nunca repete períodos pagos.');
    cfg.getRange('G324').setNote('Marque para gravar a data atual de Brasília. A caixa desmarca depois de salvar; a data permanece fixa.');
    cfg.getRange('G326:G327').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberBetween(1,3650).setAllowInvalid(false).build());
    cfg.getRange('G328').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberBetween(0,1).setAllowInvalid(false).build());
    cfg.getRange('C337:J337').merge().setValue('SALÁRIO POR GRAU').setFontWeight('bold');cfg.getRange('K337:Q337').merge().setValue('PESO DAS MISSÕES').setFontWeight('bold');
    SALARIO_.graus.forEach(function(g,i){cfg.getRange(339+i,3,1,4).merge().setValue(g);cfg.getRange(339+i,7,1,4).merge().setValue(150000*Math.pow(2,i)).setNumberFormat('"¥ "#,##0');});
    SALARIO_.tipos.forEach(function(t,i){cfg.getRange(339+i,11,1,5).merge().setValue(t);cfg.getRange(339+i,16,1,2).merge().setValue([1,1,2,3,0,0][i]);cfg.setRowHeight(339+i,30);});
    cfg.getRange('P343').setNote('O livro não define participação salarial de solo. Padrão 0; a campanha pode configurar.');cfg.getRange('P344').setNote(cfg.getRange('P343').getNote());
    cfg.getRange('G339:G343').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberGreaterThanOrEqualTo(0).setAllowInvalid(false).build());
    cfg.getRange('P339:P344').setDataValidation(SpreadsheetApp.newDataValidation().requireNumberGreaterThanOrEqualTo(0).setAllowInvalid(false).build());
    cfg.getRange('C355:Q355').merge().setValue('Missões novas recebem a data ao preencher NOME + TIPO. Para corrigir: menu Salários → Data da missão selecionada. Solos só contam se configurados.').setWrap(true);cfg.setRowHeight(355,54);
    cfg.getRange('G334').setFormula('=SUM(\'SALÁRIOS\'!J2:J)');
    cfg.getRange('G335').setFormula('=IFERROR(VLOOKUP(\'FICHA PESSOAL\'!AB11;C339:G343;5;FALSE);0)');
    if(cfg.getRange('O32').getValue()==='')cfg.getRange('O32:Q33').merge().setFormula('=HYPERLINK("#gid='+cfg.getSheetId()+'&range=C320";"14 · Emissão e salários")').setFontWeight('bold');
    carteira.getRange('AH3').setFormula('="Emitida "&TEXT(\'CONFIGURAÇÃO\'!G323;"dd.mm.yyyy")');
    pp.getRange('O85').setValue('IENES · AJUSTE MANUAL');pp.getRange('O86').setNote('Saldo e gastos manuais. Fórmulas continuam livres. Os salários ficam separados e somam no TOTAL DISPONÍVEL à direita.');
    pp.getRange('W85').setValue('TOTAL DISPONÍVEL');pp.getRange('W86').setFormula('=O86+SUM(\'SALÁRIOS\'!J2:J)').setNumberFormat('"¥ "#,##0').setNote('Saldo manual de O86 + salários fechados. Consulte valores, prazos e participação em CONFIGURAÇÃO → Emissão e salários.');
    var estado={versao:1,inicio:salarioHoje_(),graus:[],ultimaEmissao:salarioHoje_()};
    salarioSincronizar_(ss,estado,salarioHoje_(),true);salarioSalvarEstado_(ss,estado);ds.hideSheet();
    return salarioApurar_(ss,salarioHoje_());
  });
}
