// Helper temporário de ensaio: instalar só na descartável identificada abaixo.
// Remover do projeto após os ensaios; não pertence aos 20 GS de produção.
function b47Destino_() {
  var ss = SpreadsheetApp.getActive();
  if (ss.getId() !== '1hBogVNW0vqeLYwa0PNl04Y2Nel9-7nrCoODWq1FKsb4') throw Error('Destino não autorizado');
  return ss;
}
function b47Log_(value) { console.log('B47_RESULTADO ' + JSON.stringify(value)); }
function b47Auditar() {
  var t = Date.now(), ss = b47Destino_(), rows = ss.getSheetByName('ANALISE').getRange('A1:D7357').getValues();
  var keys = rows.slice(1).map(function(r){return r[0];});
  var tabs = ['FICHA','FICHA AMALDIÇOADA','INVOCAÇÕES','CONFIGURAÇÃO','DADOS_CUSTOM','DADOS_PROGRESSAO','DADOS_CRIACAO','DADOS_MELHORIAS','DADOS_RESTRICOES','DADOS_AM','DADOS_INVOC'];
  var errors = [], cells = 0;
  tabs.forEach(function(name){
    var vals = ss.getSheetByName(name).getDataRange().getDisplayValues();
    vals.forEach(function(row,y){row.forEach(function(v,x){cells++;if (/^#(REF!|ERROR!|VALUE!|DIV\/0!|N\/A$|NAME\?|NUM!|SPILL!)/.test(v)) errors.push([name,y+1,x+1,v]);});});
  });
  b47Log_({ensaio:'auditoria',destino:ss.getId(),geracao:GERACAO_,versao:rows[1][1],chaves:keys.length,unicas:new Set(keys).size,celulas:cells,erros:errors,segundos:(Date.now()-t)/1000});
}
function b47Alturas() {
  var sh=b47Destino_().getSheetByName('CONFIGURAÇÃO'), report={ensaio:'alturas',campos:{},alturas:{}};
  ['B1028','J1028','B1722','J1722'].forEach(function(a){report.campos[a]={tamanho:sh.getRange(a).getDisplayValue().length,nota:sh.getRange(a).getNote()};});
  [1028,1029,1030,1031,1032,1722,1723,1724,1725,1726,1727,1728].forEach(function(r){report.alturas[r]=sh.getRowHeight(r);});
  b47Log_(report);
}
function b47Textos() {
  var ss=b47Destino_(),sh=ss.getSheetByName('CONFIGURAÇÃO'), originals=[], heights={}, stages=[], t=Date.now(), failure=null;
  ['B1028','J1028','B1722','J1722'].forEach(function(a){var r=sh.getRange(a);originals.push({a:a,valor:r.getValue(),formula:r.getFormula(),nota:r.getNote()});});
  [1028,1029,1030,1031,1032,1722,1723,1724,1725,1726,1727,1728].forEach(function(r){heights[r]=sh.getRowHeight(r);});
  function change(a,v){var r=sh.getRange(a);r.setValue(v);SpreadsheetApp.flush();var start=Date.now();onEdit({range:r,source:ss,value:v});SpreadsheetApp.flush();stages.push({etapa:a,tamanho:v.length,altura:sh.getRowHeight(r.getRow()),segundos:(Date.now()-start)/1000});}
  try {
    change('B1028','Texto longo de teste B47. '.repeat(100));
    change('J1028','Texto vizinho maior de teste B47. '.repeat(110));
    change('B1028','');change('J1028','');
    change('J1722','Última Restrição: texto longo de teste B47. '.repeat(80));change('J1722','');
  } catch(e){failure=String(e.stack||e);}
  finally {
    originals.forEach(function(o){sh.getRange(o.a).setValue(o.formula||o.valor).setNote(o.nota);});
    Object.keys(heights).forEach(function(r){sh.setRowHeightsForced(Number(r),1,heights[r]);});SpreadsheetApp.flush();
    var differences=[];originals.forEach(function(o){var r=sh.getRange(o.a);if(r.getValue()!==o.valor||r.getFormula()!==o.formula||r.getNote()!==o.nota)differences.push(o.a);});Object.keys(heights).forEach(function(r){if(sh.getRowHeight(Number(r))!==heights[r])differences.push('linha '+r);});
    b47Log_({ensaio:'textos_onEdit_invocado',destino:ss.getId(),geracao:GERACAO_,etapas:stages,erro:failure,restauracao_divergencias:differences,segundos:(Date.now()-t)/1000});
  }
}
function b47ReusoEHeranca() {
  var ss=b47Destino_(), t=Date.now(), originals=[], checks=[], failure=null;
  function check(n,v){checks.push({teste:n,ok:!!v});}
  B47_REUSO_.forEach(function(p){var r=ss.getRange(p[0]);originals.push({r:r,v:r.getValue(),f:r.getFormula(),n:r.getNote()});});
  try {
    B47_REUSO_.forEach(function(p){ss.getRange(p[0]).setValue(p[1]);});SpreadsheetApp.flush();
    var rows=ss.getSheetByName('ANALISE').getRange('A2:B7357').getValues(),values={};rows.forEach(function(r){values[r[0]]=String(r[1]);});
    for(var n=1;n<=12;n++)check('Cinco cadastros reutilizados na invocação '+n,values['invocacao.'+n+'.familia.9']==='B47 Família compartilhada'&&values['invocacao.'+n+'.pericia.1']==='B47 Perícia compartilhada'&&values['invocacao.'+n+'.oficio_compativel']==='B47 Ofício compartilhado'&&values['invocacao.'+n+'.bas.1.pecas'].indexOf('B47 Pressa compartilhada')>=0&&values['invocacao.'+n+'.bas.1.restricoes'].indexOf('B47 Gesto compartilhado')>=0);
    var nine=[];for(var i=1;i<=9;i++)nine.push(values['invocacao.1.familia.'+i]);check('Nove posições preservam escolhas distintas',nine.length===9&&new Set(nine).size===9&&nine.every(function(v){return !!v;}));
    var mel=ss.getSheetByName('DADOS_MELHORIAS').getRange('O2:Y113').getValues(),res=ss.getSheetByName('DADOS_RESTRICOES').getRange('M2:Q54').getValues();
    // Os menus U/V e Q exibem o NOME custom; os campos mecânicos e a identidade
    // canônica da base conservam os valores do livro. A primeira execução
    // comparava também esses rótulos, produzindo duas falhas de oráculo.
    function same(table,alias,base,indices){var a=table.find(function(r){return r[0]===alias;}),b=table.find(function(r){return r[0]===base;});return a&&b&&indices.every(function(i){return a[i]===b[i];});}
    check('Melhoria herda identidade e campos mecânicos do livro',same(mel,'B47 Pressa compartilhada','Rápido',[1,2,3,4,5,8,9,10]));check('Restrição herda identidade e campos mecânicos do livro',same(res,'B47 Gesto compartilhado','Gesto',[1,2,3]));
  } catch(e){failure=String(e.stack||e);}
  finally {
    originals.forEach(function(o){o.r.setValue(o.f||o.v).setNote(o.n);});SpreadsheetApp.flush();var dif=[];
    originals.forEach(function(o){if(o.r.getValue()!==o.v||o.r.getFormula()!==o.f||o.r.getNote()!==o.n)dif.push(o.r.getSheet().getName()+'!'+o.r.getA1Notation());});
    b47Log_({ensaio:'reuso_heranca',destino:ss.getId(),geracao:GERACAO_,testes:checks,erro:failure,entradas_restauradas:originals.length,divergencias_restauracao:dif,segundos:(Date.now()-t)/1000});
  }
}
function b47Cenarios() {
  var ss = b47Destino_(), cfg = ss.getSheetByName('CONFIGURAÇÃO'), t = Date.now();
  var rows = ss.getSheetByName('ANALISE').getRange('A2:D7357').getValues(), contract = {};
  rows.forEach(function(r){contract[r[0]]=r;});
  var originals = {}, checks = [], restore = [], error = null;
  function source(k) { var r = contract[k];if(!r || !/^('[^']+'|[A-Z_]+)![A-Z]+[0-9]+$/.test(r[2]))throw Error('Fonte inválida '+k);return ss.getRange(r[2]); }
  function save(r) { var k=r.getSheet().getName()+'!'+r.getA1Notation();if(!originals[k]) originals[k]={range:r,values:r.getValues(),formulas:r.getFormulas(),notes:r.getNotes()}; }
  function set(k,v) { var r=source(k);save(r);r.setValue(v); }
  function cell(a,v) { var r=cfg.getRange(a);save(r);r.setValue(v); }
  function read(sh,a) { return ss.getSheetByName(sh).getRange(a).getValue(); }
  function check(n,ok) { checks.push({teste:n,ok:!!ok}); }
  function flush() { SpreadsheetApp.flush(); }
  try {
    Object.keys(B47_DEFAULTS_).forEach(function(k){set(k,B47_DEFAULTS_[k]);});
    set('invocacao.1.autonomia','Autônoma');
    [['pericia',1,'B47 Rito*','Essência'],['pericia',2,'B47 Ritox','Força'],['pericia',10,'B47 Última perícia ? ~','Destreza'],['oficio',1,'B47 Ofício 1','Inteligência'],['oficio',10,'B47 Último ofício *','Constituição']].forEach(function(p){set('custom.'+p[0]+'.'+p[1]+'.nome',p[2]);set('custom.'+p[0]+'.'+p[1]+'.atributo',p[3]);});
    [1,10].forEach(function(n){set('custom.familia.'+n+'.nome','B47 Família '+n+' * ? ~');set('custom.familia.'+n+'.estado','Neutra');});
    set('custom.melhoria.1.nome','B47 Pressa herdada');set('custom.melhoria.1.base','Rápido');
    set('custom.melhoria.30.nome','B47 Melhoria ? ~');set('custom.melhoria.30.base','Nenhuma');set('custom.melhoria.30.peso','Média');
    set('custom.restricao.1.nome','B47 Gesto herdado');set('custom.restricao.1.base','Gesto');
    set('custom.restricao.30.nome','B47 Restrição ? ~');set('custom.restricao.30.base','Nenhuma');set('custom.restricao.30.devolucao','Leve');
    flush();
    check('Primeiras/décimas Perícias e Ofícios; atributos',read('DADOS_PROGRESSAO','AG25')==='B47 Rito*'&&read('DADOS_PROGRESSAO','AG34')==='B47 Última perícia ? ~'&&read('DADOS_PROGRESSAO','AH34')==='Destreza'&&read('DADOS_PROGRESSAO','AJ13')==='B47 Ofício 1'&&read('DADOS_PROGRESSAO','AJ22')==='B47 Último ofício *'&&read('DADOS_PROGRESSAO','AK22')==='Constituição');
    check('Nomes com curingas literais são distintos',read('DADOS_PROGRESSAO','G2')===''&&read('DADOS_PROGRESSAO','G3')==='');
    check('Pools alcançam décimas vagas',read('DADOS_PROGRESSAO','AV11')==='B47 Última perícia ? ~'&&read('DADOS_PROGRESSAO','AW11')==='B47 Último ofício *');
    ['familia','melhoria','restricao'].forEach(function(group){var last=group==='familia'?10:30;[1,last].forEach(function(n){var warning=contract['aviso.custom.'+group+'.'+n][2];check('Cadastro válido '+group+' '+n,ss.getRange(warning).getValue()==='');});});
    for(var n=1;n<=12;n++) {set('invocacao.'+n+'.familia.9','B47 Família 10 * ? ~');set('invocacao.'+n+'.pericia.1','B47 Rito*');}
    flush();var atual=ss.getSheetByName('ANALISE').getRange('A2:B7357').getValues(), values={};atual.forEach(function(r){values[r[0]]=r[1];});
    for(var n=1;n<=12;n++)check('Reuso Família/Perícia na invocação '+n,values['invocacao.'+n+'.familia.9']==='B47 Família 10 * ? ~'&&values['invocacao.'+n+'.pericia.1']==='B47 Rito*');
    var before=[Number(values['invocacao.1.limite_familias']),Number(values['invocacao.1.limite_livres']),values['invocacao.2.limite_familias'],values['invocacao.2.limite_livres']];
    set('invocacao.1.autonomia','Não autônoma');flush();var after=ss.getSheetByName('ANALISE').getRange('A2:B7357').getValues(), av={};after.forEach(function(r){av[r[0]]=r[1];});
    check('Autonomia individual acrescenta uma Livre e uma abertura',Number(av['invocacao.1.limite_familias'])===before[0]+1&&Number(av['invocacao.1.limite_livres'])===before[1]+1&&av['invocacao.2.limite_familias']===before[2]&&av['invocacao.2.limite_livres']===before[3]);
    var count={pericia:0,oficio:0};Object.keys(contract).forEach(function(k){var m=k.match(/^personagem\.(pericia|oficio)_custom\.(\d+)\.nome$/);if(m){count[m[1]]++;check('Menu personagem '+k,!!source(k).getDataValidation());}});check('23 escolhas de Perícia e 11 de Ofício preservadas',count.pericia===23&&count.oficio===11);
    set('custom.pericia.10.tipo','Ofício');flush();check('Tipo incorreto invalida somente a décima Perícia',read('DADOS_PROGRESSAO','G11')!==''&&read('DADOS_PROGRESSAO','AG34')===''&&read('DADOS_PROGRESSAO','AJ22')==='B47 Último ofício *');set('custom.pericia.10.tipo','Perícia');
    set('custom.pericia.2.nome','B47 Rito*');flush();check('Duplicata literal exata invalida ambos',read('DADOS_PROGRESSAO','G2')!==''&&read('DADOS_PROGRESSAO','G3')!==''&&read('DADOS_PROGRESSAO','AG25')==='');set('custom.pericia.2.nome','B47 Ritox');
    set('custom.pericia.3.nome','');set('custom.pericia.3.tipo','');set('custom.oficio.2.nome','');set('custom.oficio.2.tipo','');flush();check('TIPO apagado em cartão vazio não gera avisos',read('DADOS_PROGRESSAO','G4')===''&&read('DADOS_PROGRESSAO','G13')==='');
  } catch(e) {error=String(e.stack||e);}
  finally {
    Object.keys(originals).forEach(function(k){var o=originals[k],v=o.values.map(function(row,y){return row.map(function(v,x){return o.formulas[y][x]||v;});});o.range.setValues(v);o.range.setNotes(o.notes);});flush();
    Object.keys(originals).forEach(function(k){var o=originals[k];if(JSON.stringify(o.range.getValues())!==JSON.stringify(o.values)||JSON.stringify(o.range.getFormulas())!==JSON.stringify(o.formulas)||JSON.stringify(o.range.getNotes())!==JSON.stringify(o.notes))restore.push(k);});
    b47Log_({ensaio:'cenarios',destino:ss.getId(),geracao:GERACAO_,testes:checks,erro:error,entradas_restauradas:Object.keys(originals).length,divergencias_restauracao:restore,segundos:(Date.now()-t)/1000});
  }
}

var B47_DEFAULTS_ = {"custom.pericia.1.tipo":"Perícia","custom.pericia.1.nome":null,"custom.pericia.1.mestre_viu":false,"custom.pericia.1.atributo":null,"custom.pericia.1.efeito":null,"custom.pericia.2.tipo":"Perícia","custom.pericia.2.nome":null,"custom.pericia.2.mestre_viu":false,"custom.pericia.2.atributo":null,"custom.pericia.2.efeito":null,"custom.pericia.3.tipo":"Perícia","custom.pericia.3.nome":null,"custom.pericia.3.mestre_viu":false,"custom.pericia.3.atributo":null,"custom.pericia.3.efeito":null,"custom.pericia.10.tipo":"Perícia","custom.pericia.10.nome":null,"custom.pericia.10.mestre_viu":false,"custom.pericia.10.atributo":null,"custom.pericia.10.efeito":null,"custom.oficio.1.tipo":"Ofício","custom.oficio.1.nome":null,"custom.oficio.1.mestre_viu":false,"custom.oficio.1.atributo":null,"custom.oficio.1.efeito":null,"custom.oficio.2.tipo":"Ofício","custom.oficio.2.nome":null,"custom.oficio.2.mestre_viu":false,"custom.oficio.2.atributo":null,"custom.oficio.2.efeito":null,"custom.oficio.10.tipo":"Ofício","custom.oficio.10.nome":null,"custom.oficio.10.mestre_viu":false,"custom.oficio.10.atributo":null,"custom.oficio.10.efeito":null,"custom.familia.1.nome":null,"custom.familia.1.estado":"Neutra","custom.familia.1.mestre_viu":false,"custom.familia.1.descricao":null,"custom.familia.10.nome":null,"custom.familia.10.estado":"Neutra","custom.familia.10.mestre_viu":false,"custom.familia.10.descricao":null,"custom.melhoria.1.nome":null,"custom.melhoria.1.base":"Nenhuma","custom.melhoria.1.familia":null,"custom.melhoria.1.peso":null,"custom.melhoria.1.exige_tr":null,"custom.melhoria.1.requisitos":null,"custom.melhoria.1.efeito":null,"custom.melhoria.1.mestre_viu":false,"custom.melhoria.30.nome":null,"custom.melhoria.30.base":"Nenhuma","custom.melhoria.30.familia":null,"custom.melhoria.30.peso":null,"custom.melhoria.30.exige_tr":null,"custom.melhoria.30.requisitos":null,"custom.melhoria.30.efeito":null,"custom.melhoria.30.mestre_viu":false,"custom.restricao.1.nome":null,"custom.restricao.1.base":"Nenhuma","custom.restricao.1.devolucao":null,"custom.restricao.1.frequencia":null,"custom.restricao.1.efeito":null,"custom.restricao.1.mestre_viu":false,"custom.restricao.30.nome":null,"custom.restricao.30.base":"Nenhuma","custom.restricao.30.devolucao":null,"custom.restricao.30.frequencia":null,"custom.restricao.30.efeito":null,"custom.restricao.30.mestre_viu":false};

var B47_REUSO_ = [["'CONFIGURAÇÃO'!B799","Perícia"],["'CONFIGURAÇÃO'!B801","B47 Perícia compartilhada"],["'CONFIGURAÇÃO'!F799",false],["'CONFIGURAÇÃO'!E802","Essência"],["'CONFIGURAÇÃO'!B804",null],["'CONFIGURAÇÃO'!J925","Ofício"],["'CONFIGURAÇÃO'!J927","B47 Ofício compartilhado"],["'CONFIGURAÇÃO'!N925",false],["'CONFIGURAÇÃO'!M928","Constituição"],["'CONFIGURAÇÃO'!J930",null],["'CONFIGURAÇÃO'!J999","B47 Família compartilhada"],["'CONFIGURAÇÃO'!M1000","Neutra"],["'CONFIGURAÇÃO'!N997",false],["'CONFIGURAÇÃO'!J1002",null],["'CONFIGURAÇÃO'!B1015","B47 Pressa compartilhada"],["'CONFIGURAÇÃO'!E1016","Rápido"],["'CONFIGURAÇÃO'!E1017",null],["'CONFIGURAÇÃO'!E1018",null],["'CONFIGURAÇÃO'!E1019",null],["'CONFIGURAÇÃO'!B1022",null],["'CONFIGURAÇÃO'!B1028",null],["'CONFIGURAÇÃO'!F1013",false],["'CONFIGURAÇÃO'!B1408","B47 Gesto compartilhado"],["'CONFIGURAÇÃO'!E1409","Gesto"],["'CONFIGURAÇÃO'!E1410",null],["'CONFIGURAÇÃO'!E1411",null],["'CONFIGURAÇÃO'!B1414",null],["'CONFIGURAÇÃO'!F1406",false],["'INVOCAÇÕES'!R50","B47 Família compartilhada"],["'INVOCAÇÕES'!O38","B47 Perícia compartilhada"],["'INVOCAÇÕES'!L43","B47 Ofício compartilhado"],["'INVOCAÇÕES'!J67","B47 Pressa compartilhada"],["'INVOCAÇÕES'!J71","B47 Gesto compartilhado"],["'INVOCAÇÕES'!R248","B47 Família compartilhada"],["'INVOCAÇÕES'!O236","B47 Perícia compartilhada"],["'INVOCAÇÕES'!L241","B47 Ofício compartilhado"],["'INVOCAÇÕES'!J265","B47 Pressa compartilhada"],["'INVOCAÇÕES'!J269","B47 Gesto compartilhado"],["'INVOCAÇÕES'!R446","B47 Família compartilhada"],["'INVOCAÇÕES'!O434","B47 Perícia compartilhada"],["'INVOCAÇÕES'!L439","B47 Ofício compartilhado"],["'INVOCAÇÕES'!J463","B47 Pressa compartilhada"],["'INVOCAÇÕES'!J467","B47 Gesto compartilhado"],["'INVOCAÇÕES'!R644","B47 Família compartilhada"],["'INVOCAÇÕES'!O632","B47 Perícia compartilhada"],["'INVOCAÇÕES'!L637","B47 Ofício compartilhado"],["'INVOCAÇÕES'!J661","B47 Pressa compartilhada"],["'INVOCAÇÕES'!J665","B47 Gesto compartilhado"],["'INVOCAÇÕES'!R842","B47 Família compartilhada"],["'INVOCAÇÕES'!O830","B47 Perícia compartilhada"],["'INVOCAÇÕES'!L835","B47 Ofício compartilhado"],["'INVOCAÇÕES'!J859","B47 Pressa compartilhada"],["'INVOCAÇÕES'!J863","B47 Gesto compartilhado"],["'INVOCAÇÕES'!R1040","B47 Família compartilhada"],["'INVOCAÇÕES'!O1028","B47 Perícia compartilhada"],["'INVOCAÇÕES'!L1033","B47 Ofício compartilhado"],["'INVOCAÇÕES'!J1057","B47 Pressa compartilhada"],["'INVOCAÇÕES'!J1061","B47 Gesto compartilhado"],["'INVOCAÇÕES'!AK50","B47 Família compartilhada"],["'INVOCAÇÕES'!AH38","B47 Perícia compartilhada"],["'INVOCAÇÕES'!AE43","B47 Ofício compartilhado"],["'INVOCAÇÕES'!AC67","B47 Pressa compartilhada"],["'INVOCAÇÕES'!AC71","B47 Gesto compartilhado"],["'INVOCAÇÕES'!AK248","B47 Família compartilhada"],["'INVOCAÇÕES'!AH236","B47 Perícia compartilhada"],["'INVOCAÇÕES'!AE241","B47 Ofício compartilhado"],["'INVOCAÇÕES'!AC265","B47 Pressa compartilhada"],["'INVOCAÇÕES'!AC269","B47 Gesto compartilhado"],["'INVOCAÇÕES'!AK446","B47 Família compartilhada"],["'INVOCAÇÕES'!AH434","B47 Perícia compartilhada"],["'INVOCAÇÕES'!AE439","B47 Ofício compartilhado"],["'INVOCAÇÕES'!AC463","B47 Pressa compartilhada"],["'INVOCAÇÕES'!AC467","B47 Gesto compartilhado"],["'INVOCAÇÕES'!AK644","B47 Família compartilhada"],["'INVOCAÇÕES'!AH632","B47 Perícia compartilhada"],["'INVOCAÇÕES'!AE637","B47 Ofício compartilhado"],["'INVOCAÇÕES'!AC661","B47 Pressa compartilhada"],["'INVOCAÇÕES'!AC665","B47 Gesto compartilhado"],["'INVOCAÇÕES'!AK842","B47 Família compartilhada"],["'INVOCAÇÕES'!AH830","B47 Perícia compartilhada"],["'INVOCAÇÕES'!AE835","B47 Ofício compartilhado"],["'INVOCAÇÕES'!AC859","B47 Pressa compartilhada"],["'INVOCAÇÕES'!AC863","B47 Gesto compartilhado"],["'INVOCAÇÕES'!AK1040","B47 Família compartilhada"],["'INVOCAÇÕES'!AH1028","B47 Perícia compartilhada"],["'INVOCAÇÕES'!AE1033","B47 Ofício compartilhado"],["'INVOCAÇÕES'!AC1057","B47 Pressa compartilhada"],["'INVOCAÇÕES'!AC1061","B47 Gesto compartilhado"],["'INVOCAÇÕES'!O48","Alcance"],["'INVOCAÇÕES'!P48","Área"],["'INVOCAÇÕES'!Q48","Mira"],["'INVOCAÇÕES'!R48","Controle"],["'INVOCAÇÕES'!S48","Auxiliares"],["'INVOCAÇÕES'!O50","Castigo"],["'INVOCAÇÕES'!P50","Tempo"],["'INVOCAÇÕES'!Q50","Marca"]];
