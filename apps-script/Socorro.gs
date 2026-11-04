/** Registro explícito da queda: a referência não acompanha mudanças posteriores do máximo. */
function r53SocorroNovaQueda_(s, escolha) {
  if(s.atual!==0)throw Error('Registre a queda quando a vida estiver em zero.');
  if(!Number.isSafeInteger(s.maximo)||s.maximo<1||!Number.isSafeInteger(s.classe)||s.classe<1||!Number.isSafeInteger(s.sequelas)||s.sequelas<0)
    throw Error('Confira máximo de vida, Classe e Sequelas.');
  if([1,2,3].indexOf(escolha)<0)throw Error('Escolha 1 (Aguentar), 2 (Insistir pela primeira vez) ou 3 (Insistir novamente).');
  if(!s.regras||s.regras.length!==5||s.regras.some(function(v){return typeof v!=='number'||!isFinite(v)||v<0;})||!Number.isSafeInteger(s.regras[4]))throw Error('Confira as regras de Morrendo na CONFIGURAÇÃO.');
  var necessario=Math.ceil(Number((s.maximo*s.regras[escolha-1]).toFixed(10)));
  if(escolha!==1)necessario=Math.min(necessario,s.regras[3]*s.classe);
  if(!Number.isSafeInteger(necessario)||necessario<1)throw Error('O tratamento necessário deve ser um inteiro positivo. Confira a CONFIGURAÇÃO.');
  var janela=Math.max(0,s.regras[4]-s.sequelas);
  return {versao:1,referencia:s.maximo,classe:s.classe,escolha:escolha,necessario:necessario,tratamento:0,janela:janela,status:janela?'Morrendo':'Derrotado'};
}
function r53SocorroContaCura_(estado,s,bruto) {
  if(estado.status!=='Morrendo'||estado.janela<1)throw Error('Cura comum não encerra Derrotado ou uma janela esgotada. Resolva a situação com o mestre.');
  if(s.atual!==0)throw Error('O registro está em Morrendo, mas a vida foi alterada. Confira o registro antes de continuar.');
  var conta=r53ContaCura_(s,bruto), total=estado.tratamento+conta.ganho;
  if(!Number.isSafeInteger(total))throw Error('Tratamento fora do limite suportado.');
  var depois=JSON.parse(JSON.stringify(estado));depois.tratamento=total;
  var saiu=total>=estado.necessario;
  if(saiu)depois.status='Socorrido';
  return {estado:depois,vida:saiu?Math.min(s.maximo,total):0,saiu:saiu,ganho:conta.ganho,reduz:conta.reduz};
}
function r53SocorroLer_(ss) {
  var aba=ss.getSheetByName('SOCORRO');if(!aba)return null;
  if(aba.getRange('A2').getValue()!=='SOCORRO_R53_1')throw Error('Já existe uma aba SOCORRO sem o formato esperado. Nada foi alterado.');
  var estado;try{estado=JSON.parse(aba.getRange('B2').getValue());}catch(e){throw Error('Registro de socorro inválido. Confira antes de continuar.');}
  if(!estado||estado.versao!==1||['Morrendo','Derrotado','Socorrido','Encerrado manualmente','Encerrado no descanso'].indexOf(estado.status)<0||![estado.referencia,estado.classe,estado.necessario,estado.tratamento,estado.janela].every(Number.isSafeInteger)||estado.referencia<1||estado.classe<1||estado.necessario<1||estado.tratamento<0||estado.janela<0||[1,2,3].indexOf(estado.escolha)<0)throw Error('Registro de socorro inconsistente. Nada foi alterado.');
  return estado;
}
function r53SocorroRecursos_(ss) {
  var s=r53LerCura_(ss),f=ss.getSheetByName('FICHA');
  s.classe=f.getRange('Z73').getValue();
  s.caixas=['F48','H48','J48'].map(function(a){return f.getRange(a).getValue();});
  s.extras=f.getRange('J50').getValue();if(s.extras==='')s.extras=0;
  if(!s.caixas.every(function(x){return typeof x==='boolean';})||!Number.isSafeInteger(s.extras)||s.extras<0)throw Error('Confira as Sequelas antes de continuar.');
  s.sequelas=s.caixas.filter(function(x){return x;}).length+s.extras;
  s.regras=ss.getSheetByName('DADOS_CONFIG').getRange('S10:S14').getValues().map(function(r){return r[0];});return s;
}
function r53SocorroCelula_(v){return {userEnteredValue:typeof v==='number'?{numberValue:v}:typeof v==='boolean'?{boolValue:v}:{stringValue:String(v)}};}
/** Uma única requisição atômica: registro, vida e Sequela não ficam pela metade. */
function r53SocorroGravar_(ss,estado,recursos,vida,sequela,alteracoes) {
  if(typeof Sheets==='undefined')throw Error('O serviço Google Sheets deste projeto não está disponível. Nenhuma alteração foi aplicada.');
  var aba=ss.getSheetByName('SOCORRO'),id=aba?aba.getSheetId():73018010,requests=[];
  if(!aba){while(ss.getSheets().some(function(s){return s.getSheetId()===id;}))id++;
    requests.push({addSheet:{properties:{sheetId:id,title:'SOCORRO',gridProperties:{rowCount:30,columnCount:3}}}});
  }
  var escolha=['','Aguentar','Insistir · primeira vez na cena','Insistir · segunda vez em diante'][estado.escolha];
  var rows=[['SOCORRO','Registro da queda'],['SOCORRO_R53_1',JSON.stringify(estado)],['',''],['Estado',estado.status],['Máximo de referência',estado.referencia],['Maior Classe na queda',estado.classe],['Escolha registrada',escolha],['Tratamento necessário',estado.necessario],['Tratamento recebido',estado.tratamento],['Janela restante (rodadas)',estado.janela],['Como usar','Recursos → Aplicar cura acumula tratamento enquanto estiver Morrendo.'],['Janela','Use Consumir rodada da janela após cada volta completa ou dano posterior que alcance a vida.'],['Limites','Estabilização, resgates expressos e saída de Derrotado exigem resolução manual com o mestre. Não use cura comum para essas exceções.'],['Previsão','As caixas de Morrendo na FICHA calculam a próxima queda. Este registro conserva os valores da queda atual.'],['Insistir','A contagem por cena é informada ao registrar; manter-se agindo não é uma nova escolha.']];
  requests.push({updateCells:{start:{sheetId:id,rowIndex:0,columnIndex:0},rows:rows.map(function(r){return {values:r.map(r53SocorroCelula_)};}),fields:'userEnteredValue'}});
  requests.push({updateDimensionProperties:{range:{sheetId:id,dimension:'ROWS',startIndex:1,endIndex:2},properties:{hiddenByUser:true},fields:'hiddenByUser'}});
  requests.push({updateDimensionProperties:{range:{sheetId:id,dimension:'COLUMNS',startIndex:0,endIndex:1},properties:{pixelSize:240},fields:'pixelSize'}});
  requests.push({updateDimensionProperties:{range:{sheetId:id,dimension:'COLUMNS',startIndex:1,endIndex:2},properties:{pixelSize:640},fields:'pixelSize'}});
  requests.push({repeatCell:{range:{sheetId:id,startRowIndex:0,endRowIndex:15,startColumnIndex:0,endColumnIndex:2},cell:{userEnteredFormat:{wrapStrategy:'WRAP',verticalAlignment:'TOP'}},fields:'userEnteredFormat'}});
  var fid=ss.getSheetByName('FICHA').getSheetId();
  requests.push({updateCells:{start:{sheetId:fid,rowIndex:38,columnIndex:3},rows:[{values:[{note:'As caixas abaixo são uma previsão da próxima queda. Durante Morrendo, use o registro congelado na aba SOCORRO (menu Recursos → Registrar queda).'}]}],fields:'note'}});
  if(vida!==null)requests.push({updateCells:{start:{sheetId:fid,rowIndex:25,columnIndex:3},rows:[{values:[r53SocorroCelula_(vida)]}],fields:'userEnteredValue'}});
  if(sequela){var livre=recursos.caixas.indexOf(false),pos=livre<0?[49,9]:[47,[5,7,9][livre]];
    requests.push({updateCells:{start:{sheetId:fid,rowIndex:pos[0],columnIndex:pos[1]},rows:[{values:[r53SocorroCelula_(livre<0?recursos.extras+1:true)]}],fields:'userEnteredValue'}});
  }
  Sheets.Spreadsheets.batchUpdate({requests:requests.concat(alteracoes || [])},ss.getId());
}
function registrarQueda() {
  var ui=SpreadsheetApp.getUi(),ss=SpreadsheetApp.getActive(),s,anterior,estado;
  try{s=r53SocorroRecursos_(ss);anterior=r53SocorroLer_(ss);if(r53SocorroAtivo_(anterior))throw Error('Há uma queda em andamento. Consulte SOCORRO; não registre a mesma queda novamente.');if(s.atual!==0)throw Error('A vida precisa estar em zero para registrar uma queda.');}catch(e){ui.alert(e.message);return;}
  var resposta=ui.prompt('Registrar queda','Registre imediatamente ao cair. Máximo atual: '+s.maximo+'.\n1 = Aguentar\n2 = Insistir pela primeira vez na cena\n3 = Insistir novamente na cena\nInforme 1, 2 ou 3. Se o máximo já mudou desde a queda, confira a referência com o mestre antes de registrar.',ui.ButtonSet.OK_CANCEL);
  if(resposta.getSelectedButton()!==ui.Button.OK)return;
  try{var escolha=resposta.getResponseText().trim();if(!/^[123]$/.test(escolha))throw Error('Informe 1, 2 ou 3.');estado=r53SocorroNovaQueda_(s,Number(escolha));}catch(e){ui.alert(e.message);return;}
  if(ui.alert('Confirmar queda','Referência: '+estado.referencia+' · tratamento necessário: '+estado.necessario+' · janela: '+estado.janela+'\nEstado: '+estado.status+'. Os valores ficarão registrados em SOCORRO.',ui.ButtonSet.YES_NO)!==ui.Button.YES)return;
  var lock=LockService.getDocumentLock();if(!lock.tryLock(5000)){ui.alert('Outra operação está em andamento. Tente novamente.');return;}var erro;
  try{if(JSON.stringify(s)!==JSON.stringify(r53SocorroRecursos_(ss))||JSON.stringify(anterior)!==JSON.stringify(r53SocorroLer_(ss)))throw Error('A ficha mudou durante a confirmação. Confira e tente novamente.');r53SocorroGravar_(ss,estado,s,null,false);}catch(e){erro=e.message;}finally{lock.releaseLock();}
  if(erro)ui.alert(erro);else ss.toast('Referência e tratamento registrados na aba SOCORRO.','Queda registrada',6);
}
function consumirRodadaSocorro() {
  var ss=SpreadsheetApp.getActive(),ui=SpreadsheetApp.getUi(),antes;
  try{antes=r53SocorroLer_(ss);if(!antes||antes.status!=='Morrendo')throw Error('Não há janela de Morrendo ativa.');}catch(e){ui.alert(e.message);return;}
  if(ui.alert('Consumir uma rodada','Use após uma volta completa desde a queda, ou uma ocorrência posterior de dano que alcance a vida. Não conte o golpe da queda nem dano totalmente absorvido pela vida temporária.\nJanela: '+antes.janela+' → '+(antes.janela-1)+'.',ui.ButtonSet.YES_NO)!==ui.Button.YES)return;
  var lock=LockService.getDocumentLock();if(!lock.tryLock(5000)){ui.alert('Outra operação está em andamento. Tente novamente.');return;}var erro;
  try{if(JSON.stringify(antes)!==JSON.stringify(r53SocorroLer_(ss)))throw Error('O registro mudou. Confira SOCORRO e tente novamente.');var depois=JSON.parse(JSON.stringify(antes));depois.janela--;if(!depois.janela)depois.status='Derrotado';r53SocorroGravar_(ss,depois,null,null,false);}catch(e){erro=e.message;}finally{lock.releaseLock();}if(erro)ui.alert(erro);
}
function r53SocorroAplicarCura_(ss,bruto) {
  var ui=SpreadsheetApp.getUi(),s,antes,conta;
  try{s=r53SocorroRecursos_(ss);antes=r53SocorroLer_(ss);if(!r53SocorroAtivo_(antes))throw Error('Vida em zero: use Recursos → Registrar queda antes de aplicar cura.');conta=r53SocorroContaCura_(antes,s,bruto);}catch(e){ui.alert(e.message);return;}
  if(conta.ganho===0){ui.alert('Cura zero: o tratamento e a vida foram preservados.');return;}
  var texto='Referência da queda: '+antes.referencia+' · necessário: '+antes.necessario+'\nCura válida: '+conta.ganho+(conta.reduz?' (redução do Corpo Exaurido aplicada)':'')+'\nTratamento: '+antes.tratamento+' → '+conta.estado.tratamento+'\n'+(conta.saiu?'Encerra Morrendo: vida '+conta.vida+' e uma Sequela.':'Tratamento insuficiente: vida continua zero.')+'\nA vida temporária não muda. Confirme apenas cura válida para este alvo.';
  if(ui.alert('Confirmar tratamento',texto,ui.ButtonSet.YES_NO)!==ui.Button.YES)return;
  var lock=LockService.getDocumentLock();if(!lock.tryLock(5000)){ui.alert('Outra operação está em andamento. Tente novamente.');return;}var erro;
  try{if(JSON.stringify(s)!==JSON.stringify(r53SocorroRecursos_(ss))||JSON.stringify(antes)!==JSON.stringify(r53SocorroLer_(ss)))throw Error('A ficha ou o tratamento mudou durante a confirmação. Confira e tente novamente.');r53SocorroGravar_(ss,conta.estado,s,conta.vida,conta.saiu);}catch(e){erro=e.message;}finally{lock.releaseLock();}
  if(erro)ui.alert(erro);else ss.toast(conta.saiu?'Socorro concluído; uma Sequela registrada.':'Tratamento acumulado; vida permanece zero.','Socorro',6);
}
/** Saída administrativa explícita para exceções resolvidas com o mestre; não concede recursos. */
function encerrarRegistroSocorro() {
  var ss=SpreadsheetApp.getActive(),ui=SpreadsheetApp.getUi(),antes;
  try{antes=r53SocorroLer_(ss);if(!r53SocorroAtivo_(antes))throw Error('Não há registro ativo para encerrar.');}catch(e){ui.alert(e.message);return;}
  if(ui.alert('Encerrar registro manualmente','Use somente após resolver com o mestre uma estabilização, resgate expresso ou saída de Derrotado. Confira vida, tratamento e Sequela manualmente antes de encerrar.\nEsta opção só arquiva o registro; não cura, não altera a janela nem acrescenta Sequela.',ui.ButtonSet.YES_NO)!==ui.Button.YES)return;
  var lock=LockService.getDocumentLock();if(!lock.tryLock(5000)){ui.alert('Outra operação está em andamento. Tente novamente.');return;}var erro;
  try{if(JSON.stringify(antes)!==JSON.stringify(r53SocorroLer_(ss)))throw Error('O registro mudou. Confira antes de encerrar.');antes.status='Encerrado manualmente';r53SocorroGravar_(ss,antes,null,null,false);}catch(e){erro=e.message;}finally{lock.releaseLock();}if(erro)ui.alert(erro);
}
function r53SocorroAtivo_(estado){return !!estado&&['Morrendo','Derrotado'].indexOf(estado.status)>=0;}

/** Usa o cálculo do descanso normal em uma ação autorizada pelo menu. */
function descansarComQueda() {
  var ss = SpreadsheetApp.getActive(), ui = SpreadsheetApp.getUi(), queda;
  try {
    queda = r53SocorroLer_(ss);
    if (!r53SocorroAtivo_(queda)) throw Error('Não há queda ativa. Use o descanso na FICHA.');
  } catch (erro) { ui.alert(erro.message); return; }
  var resposta = ui.prompt('Descanso longo com queda ativa',
    'Use após o mestre confirmar o descanso e a recuperação do personagem vivo.\n1 = lugar propício\n2 = fora de lugar propício\nSe a recuperação encerrar a queda, as Sequelas serão removidas ao final.',
    ui.ButtonSet.OK_CANCEL);
  if (resposta.getSelectedButton() !== ui.Button.OK) return;
  var escolha = resposta.getResponseText().trim();
  if (escolha !== '1' && escolha !== '2') { ui.alert('Informe 1 ou 2.'); return; }
  var tipo = escolha === '1' ? 'Longo · lugar propício' : 'Longo · fora';
  var lock = LockService.getDocumentLock(), erroDescanso;
  if (!lock.tryLock(5000)) { ui.alert('Outra operação está em andamento. Tente novamente.'); return; }
  try { r53DescansarComQueda(tipo, queda); }
  catch (erro) { erroDescanso = erro.message; }
  finally { lock.releaseLock(); }
  if (erroDescanso) ui.alert(erroDescanso);
}
