/** Ensaios de execução real no Google. Nunca instalar nas oficiais. */
var QA_ID_='COLE_O_ID_DA_COPIA_DESCARTAVEL';
function qaSS_(){var ss=SpreadsheetApp.getActive();if(ss.getId()!==QA_ID_)throw Error('Somente QA descartável');return ss;}
function qaRun_(name,fn){
 var ss=qaSS_(),t=Date.now(),checks=0,failures=[],times=[],saved=[],props=PropertiesService.getDocumentProperties(),before=props.getProperties();
 function keep(sh,a){var r=ss.getSheetByName(sh).getRange(a),v=r.getValues(),f=r.getFormulas();saved.push({r:r,v:v.map(function(row,i){return row.map(function(x,j){return f[i][j]||r53Literal_(x);});}),dv:r.getDataValidations(),notes:r.getNotes()});return r;}
 function eq(a,b,label){checks++;if(JSON.stringify(a)!==JSON.stringify(b)){failures.push({label:label,actual:a,expected:b});console.log('QA FALHA '+JSON.stringify(failures[failures.length-1]));}}
 function edit(sh,a,v,extra){var r=ss.getSheetByName(sh).getRange(a),old=r.getValue();r.clearDataValidations();r.setValue(v);var e={source:ss,range:r,oldValue:String(old),value:typeof v==='boolean'?String(v).toUpperCase():String(v)};Object.keys(extra||{}).forEach(function(k){e[k]=extra[k];});var start=Date.now();onEdit(e);SpreadsheetApp.flush();times.push({cell:sh+'!'+a,ms:Date.now()-start});return r;}
 var error='';try{fn({ss:ss,keep:keep,eq:eq,edit:edit,props:props});}catch(err){error=String(err.stack||err);console.log(error);}finally{
   saved.reverse().forEach(function(x){x.r.clearDataValidations();x.r.setValues(x.v);x.r.setDataValidations(x.dv);x.r.setNotes(x.notes);});
   var after=props.getProperties();Object.keys(after).forEach(function(k){if(/^(r53_|salario_)/.test(k)&&!(k in before))props.deleteProperty(k);});Object.keys(before).forEach(function(k){if(/^(r53_|salario_)/.test(k))props.setProperty(k,before[k]);});SpreadsheetApp.flush();
 }
 var out={name:name,checks:checks,failures:failures,error:error,ms:Date.now()-t,times:times};
 var sh=ss.getSheetByName('QA_EVENTOS')||ss.insertSheet('QA_EVENTOS');sh.appendRow([new Date(),name,checks,failures.length,error,JSON.stringify(out)]);console.log('QA_RESULT '+JSON.stringify(out));return out;
}
function qaPrepararCartao_(q,id){
 var g=R53_EDITOR_.contextos.filter(function(g){return g.id===id;})[0];if(!g)throw Error(id);
 var s=q.ss.getSheetByName(g.aba),a=g.area_editor;
 q.keep(g.aba,s.getRange(a[0],a[1],a[2]-a[0]+1,a[3]-a[1]+1).getA1Notation());
 var store=q.ss.getSheetByName(R53_EDITOR_.storage);q.keep(R53_EDITOR_.storage,store.getRange(g.editor+2,2,R53_EDITOR_.campos.length,g.classes.length).getA1Notation());
 var sep=g.classe_maxima.lastIndexOf('!'),sheet=g.classe_maxima.slice(0,sep).replace(/^'|'$/g,'');q.keep(sheet,g.classe_maxima.slice(sep+1)).setValue(7);
 s.getRange(g.cel.nome).setValue('QA '+id);if(g.cel.classe)s.getRange(g.cel.classe).setValue(g.classes[0]);
 store.getRange(g.editor+2,2,R53_EDITOR_.campos.length,g.classes.length).setValues(R53_EDITOR_.campos.map(function(f){return g.classes.map(function(){return R53_EDITOR_.defaults[f[0]];});}));
 R53_REF_CACHE_={};r53Mostrar_(q.ss,g,g.classes[0]===null?7:g.classes[0]);return g;
}
function qaContratoContextos(){return qaRun_('Estrutura dos 249 contextos',function(q){
 var seen={},slots={},n=0,dims={};q.ss.getSheets().forEach(function(sh){dims[sh.getName()]=[sh.getMaxRows(),sh.getMaxColumns()];});R53_EDITOR_.contextos.forEach(function(g){q.eq(!!seen[g.id],false,'id '+g.id);seen[g.id]=true;var sh=dims[g.aba];q.eq(g.area_editor[2]<=sh[0],true,g.id+' linhas');q.eq(g.area_editor[3]<=sh[1],true,g.id+' colunas');
 g.classes.forEach(function(cl,j){var key=(g.editor+2)+':'+(j+2);q.eq(!!slots[key],false,g.id+' versão '+cl);slots[key]=true;n++;});
 q.eq(g.editor+1+R53_EDITOR_.campos.length<=dims[R53_EDITOR_.storage][0],true,g.id+' armazenamento');});q.eq(Object.keys(seen).length,249,'249 contextos');q.eq(n>249,true,'versões por Classe');
 });}

function qaCurto_(name,fn){return qaRun_(name,function(q){q.keep(R53_EDITOR_.amparo.aba,R53_EDITOR_.amparo.faixa).setValues([Array(13).fill('Normal')]);q.props.setProperty('salario_proximo',String(salarioHoje_()+1));var g=qaPrepararCartao_(q,'feitico.1');fn(q,g,q.ss.getSheetByName(g.aba));});}
function qaClasses(){return qaCurto_('Classes independentes',function(q,g,sh){
 var v=R53_EDITOR_.campos.map(function(f){return R53_EDITOR_.defaults[f[0]];});v[r53Campo_('pontos1')]=3;v[r53Campo_('pontos2')]=2;v[r53Campo_('funcao1')]='Dano';v[r53Campo_('funcao2')]='Cura';r53Gravar_(q.ss,g,3,v);v[r53Campo_('pontos1')]=4;r53Gravar_(q.ss,g,4,v);
 q.edit(g.aba,g.cel.classe,3);q.eq(sh.getRange(g.funcoes_diretas.dano).getValue(),3,'Classe3 dano');q.eq(sh.getRange(g.funcoes_diretas.cura).getValue(),2,'Classe3 cura');q.edit(g.aba,g.cel.classe,4);q.eq(sh.getRange(g.funcoes_diretas.dano).getValue(),4,'Classe4 independente');q.edit(g.aba,g.cel.classe,3);q.eq(sh.getRange(g.funcoes_diretas.dano).getValue(),3,'Retorno preservado');
 });}
function qaInvalidos(){return qaCurto_('Entradas inválidas e fórmula',function(q,g,sh){[-1,'=1+1'].forEach(function(v){q.edit(g.aba,g.funcoes_diretas.dano,v);q.eq(sh.getRange(g.funcoes_diretas.dano).getValue(),0,'Recusa '+v);});var c=Object.keys(g.formulas)[0];q.edit(g.aba,c,999);q.eq(qaFormula_(sh.getRange(c).getFormula()),qaFormula_(g.formulas[c]),'Fórmula recuperada');});}
function qaFila(){return qaCurto_('Edições pendentes e atrasadas',function(q,g,sh){sh.getRange(g.funcoes_diretas.dano).setValue(1);q.edit(g.aba,g.cel.classe,3);q.eq(sh.getRange(g.cel.classe).getValue(),1,'Segura versão pendente');q.eq(r53LerVersao_(q.ss,g,1)[r53Campo_('pontos1')],1,'Preserva pontos');q.edit(g.aba,g.cel.classe,3);sh.getRange(g.funcoes_diretas.dano).setValue(0);onEdit({source:q.ss,range:sh.getRange(g.funcoes_diretas.dano),oldValue:'0',value:'2'});q.eq(r53LerVersao_(q.ss,g,3)[r53Campo_('pontos1')],2,'Payload atrasado');});}
function qaUltimaEntidade(){return qaRun_('Última entidade máxima',function(q){q.keep(R53_EDITOR_.amparo.aba,R53_EDITOR_.amparo.faixa).setValues([Array(13).fill('Normal')]);q.props.setProperty('salario_proximo',String(salarioHoje_()+1));var g=qaPrepararCartao_(q,'entidade.12.maxima.1'),sh=q.ss.getSheetByName(g.aba);q.edit(g.aba,g.funcoes_diretas.dano,true);q.eq(r53LerVersao_(q.ss,g,7)[r53Campo_('funcao1')],'Dano','Dano fixo');q.edit(g.aba,g.funcoes_diretas.vt,true);q.eq(sh.getRange(g.funcoes_diretas.vt).getValue(),'—','VT bloqueado');});}
function qaSalarioFechamento(){return qaRun_('Salário: três períodos e idempotência',function(q){
 var ss=q.ss,hoje=salarioHoje_(),ds=ss.getSheetByName(SALARIO_.dados),pp=ss.getSheetByName('FICHA PESSOAL');
 q.keep('CARTEIRA','O9').setValue('Personagem QA');q.keep('FICHA PESSOAL','AB11').setValue('Grau 4');q.keep('FICHA PESSOAL','O86').clearContent();
 q.keep(SALARIO_.config,'O40:O44').setValues([[true],[30],[3],[.25],[true]]);q.keep(SALARIO_.config,'O54:O58').setValues([[150000],[300000],[600000],[1200000],[2400000]]);q.keep(SALARIO_.config,'O62:O67').setValues([[1],[1],[2],[3],[1],[1]]);
 q.keep(SALARIO_.dados,'A2:J1000').clearContent();q.keep(SALARIO_.dados,'N2').setValue(salarioData_(hoje-90));q.keep(SALARIO_.livro,'A2:L1000').clearContent();q.keep(SALARIO_.extrato,'A2:C1000').clearContent();
 ds.getRange('A2:G4').setValues([['qa1','Missão um','Curta',hoje-80,true,'49:15',hoje-80],['qa2','Missão dois','Longa',hoje-50,true,'49:16',hoje-50],['qa3','Missão três',SALARIO_.tipos[3],hoje-30,true,'49:17',hoje-30]]);SpreadsheetApp.flush();
 q.eq(ds.getRange('Q3').getValue(),3,'Três períodos vencidos');q.eq(ds.getRange('Q4').getValue(),337500,'1, 2 e 3 participações');var total=pp.getRange('W86').getValue();
 q.eq(total,337500,'Saldo inclui pendente');var first=salarioCongelar_(ss,hoje);SpreadsheetApp.flush();q.eq(first.novos,3,'Três créditos gravados');q.eq(ds.getRange('Q4').getValue(),0,'Pendente zerado');q.eq(pp.getRange('W86').getValue(),total,'Saldo estável após congelar');
 var second=salarioCongelar_(ss,hoje);SpreadsheetApp.flush();q.eq(second.novos,0,'Reexecução não duplica');q.eq(pp.getRange('W86').getValue(),total,'Saldo estável após repetir');
 });}
function qaDinheiro(){return qaRun_('Ienes: ganho, gasto e entrada inválida',function(q){q.keep(SALARIO_.extrato,'A2:C1000').clearContent();q.keep('FICHA PESSOAL','O86').clearContent();q.props.setProperty('salario_extrato','0');q.props.setProperty('salario_proximo',String(salarioHoje_()+1));
 [1000,-250,'abc'].forEach(function(v){q.edit('FICHA PESSOAL','O86',v,{salarioInstalavel_:true});});var v=q.ss.getSheetByName(SALARIO_.extrato).getRange('B2:B4').getValues();q.eq(v,[[1000],[-250],['']],'Só os dois valores válidos registrados');q.eq(q.ss.getSheetByName('FICHA PESSOAL').getRange('O86').getValue(),'abc','Inválido não consumido');
 q.eq(isNaN(salarioDataDigitada_('31/02/2026')),true,'Recusa data impossível');q.eq(isFinite(salarioDataDigitada_('29/02/2024')),true,'Aceita bissexto');q.eq(salarioNumero_('¥ 1.234,50'),1234.5,'Moeda brasileira');});}

// O Google omite aspas opcionais de nomes simples de abas ao salvar fórmulas.
function qaFormula_(s){return s.replace(/;/g,',').replace(/'DADOS_R53'!/g,'DADOS_R53!');}
function qaRecuperacao(){return qaCurto_('Recuperação de fórmula normalizada',function(q,g,sh){var c=Object.keys(g.formulas)[0];q.edit(g.aba,c,999);q.eq(qaFormula_(sh.getRange(c).getFormula()),qaFormula_(g.formulas[c]),'Fórmula recuperada');});}
function qaEmissao(){return qaRun_('Emissão e proteção das datas',function(q){var ss=q.ss,hoje=salarioHoje_(),cfg=ss.getSheetByName(SALARIO_.config),d=ss.getSheetByName(SALARIO_.dados);
 q.keep('CARTEIRA','O9').setValue('QA emissão');q.keep('CARTEIRA','AT3').setValue(false);q.keep(SALARIO_.config,'O38:O39');q.keep(SALARIO_.config,'O46');q.keep(SALARIO_.dados,'N2').clearContent();q.props.setProperty('salario_proximo',String(hoje+1));
 q.edit('CARTEIRA','AT3',true,{salarioInstalavel_:true});q.eq(salarioDia_(d.getRange('N2').getValue()),hoje,'Emissão hoje');q.eq(ss.getSheetByName('CARTEIRA').getRange('AT3').getValue(),false,'Checkbox limpa');
 q.edit('CARTEIRA','AT3',true,{salarioInstalavel_:true});q.eq(salarioDia_(d.getRange('N2').getValue()),hoje,'Repetição não retroage');
 salarioMudarEmissao_(ss,cfg,hoje-1);q.eq(salarioDia_(d.getRange('N2').getValue()),hoje,'Recusa retroação');q.eq(cfg.getRange('O46').getValue().indexOf('⚠'),0,'Explica data anterior');
 salarioMudarEmissao_(ss,cfg,hoje+1);q.eq(salarioDia_(d.getRange('N2').getValue()),hoje,'Recusa futuro');q.eq(cfg.getRange('O38').getFormula().charAt(0),'=','Painel permanece em fórmula');
 });}

function qaModalidades(){return qaRun_('Classe zero e liberação da última entidade',function(q){q.keep(R53_EDITOR_.amparo.aba,R53_EDITOR_.amparo.faixa).setValues([Array(13).fill('Normal')]);q.props.setProperty('salario_proximo',String(salarioHoje_()+1));
 var zero=qaPrepararCartao_(q,'classe0.1');q.edit(zero.aba,zero.funcoes_diretas.dano,true);q.eq(r53LerVersao_(q.ss,zero,0)[r53Campo_('funcao1')],'Dano','Classe0 habilita dano');
 var lib=qaPrepararCartao_(q,'entidade.12.liberacao.1');q.edit(lib.aba,lib.funcoes_diretas.dano,4);q.eq(r53LerVersao_(q.ss,lib,lib.classes[0])[r53Campo_('pontos1')],4,'Liberação grava quatro pontos');q.eq(q.ss.getSheetByName(lib.aba).getRange(lib.funcoes_diretas.cura).getValue(),'—','Liberação não libera cura');});}

function qaMissao(){return qaRun_('Missão: registro, nível, identidade e restauração',function(q){
 q.keep('FICHA PESSOAL','AW15:BB16');q.keep('DADOS_SALARIOS','A2:G1000');q.keep('DADOS_SALARIOS','L2');q.keep('FICHA','AH11').setValue(1);
 var pp=q.ss.getSheetByName('FICHA PESSOAL'),ds=q.ss.getSheetByName('DADOS_SALARIOS');pp.getRange('AX15').setValue('Curta');
 q.edit('FICHA PESSOAL','AW15','QA missão nativa');var before=ds.getRange('A2:G2').getValues()[0];q.eq(before[1],'QA missão nativa','Missão registrada');q.eq(before[5],'49:15','Caixa continua texto');q.eq(q.ss.getSheetByName('FICHA').getRange('AH11').getValue(),2,'XP sobe nível 1 para 2');
 q.edit('FICHA PESSOAL','AW15','QA renomeada');var after=ds.getRange('A2:G2').getValues()[0];q.eq(after[0],before[0],'Renomear preserva identidade');q.eq(after[3],before[3],'Renomear preserva data');
 q.edit('FICHA PESSOAL','BA15',999);q.eq(pp.getRange('BA15').getValue(),50,'Fórmula XP recuperada');q.eq(pp.getRange('BA15').getFormula().charAt(0),'=','XP continua fórmula');
 q.edit('FICHA PESSOAL','AW15','');q.eq(ds.getRange('E2').getValue(),false,'Missão removida fica inativa');q.eq(pp.getRange('AW15').getNote().indexOf('[Salário:'),-1,'Marca removida');
 });}

function qaFinalizarMarcadores(){var ss=qaSS_(),props=PropertiesService.getDocumentProperties();props.setProperty('r53_classe_visivel_feitico.1',String(ss.getSheetByName('FICHA AMALDIÇOADA').getRange('D64').getValue()));props.setProperty('r53_amparo_direto',JSON.stringify(ss.getSheetByName(R53_EDITOR_.amparo.aba).getRange(R53_EDITOR_.amparo.faixa).getValues()[0]));props.deleteProperty('salario_proximo');console.log('QA: marcadores alinhados aos dados restaurados.');}
