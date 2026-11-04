/** Cura recebida pelo personagem. Independente do módulo pesado e da caixa ±. */
function r53CuraMenu_() {
  SpreadsheetApp.getUi().createMenu('Recursos').addItem('Aplicar cura', 'aplicarCuraRecebida').addItem('Registrar queda', 'registrarQueda').addItem('Consumir rodada da janela', 'consumirRodadaSocorro').addItem('Encerrar registro manualmente', 'encerrarRegistroSocorro').addToUi();
}
function r53ContaCura_(s, bruto) {
  if (!Number.isSafeInteger(bruto) || bruto < 0) throw Error('Informe uma cura inteira, igual ou maior que zero.');
  if (!Number.isSafeInteger(s.atual) || s.atual < 0 || !Number.isSafeInteger(s.maximo) || s.maximo < 1 || typeof s.corporal !== 'boolean')
    throw Error('Confira a vida atual, o máximo e a configuração de Origem antes de aplicar cura.');
  var reduz = s.corporal && s.corpo === 'Corpo Exaurido';
  var ganho = reduz && bruto > 0 ? Math.max(1, Math.floor(bruto / 2)) : bruto;
  var aplicado = Math.min(ganho, Math.max(0, s.maximo - s.atual));
  return { reduz: reduz, ganho: ganho, aplicado: aplicado, depois: s.atual + aplicado };
}
function r53LerCura_(ss) {
  var ficha=ss.getSheetByName('FICHA'), custom=ss.getSheetByName('DADOS_CUSTOM');
  if(!ficha||!custom)throw Error('Esta ficha não tem a estrutura necessária para aplicar cura.');
  var v=ficha.getRange('D26:J26').getValues()[0];
  return {atual:v[0],maximo:v[6],corpo:ficha.getRange('D52').getValue(),corporal:custom.getRange('B126').getValue()};
}
function aplicarCuraRecebida() {
  var ui=SpreadsheetApp.getUi(),ss=SpreadsheetApp.getActive();
  var resposta=ui.prompt('Aplicar cura — personagem (FICHA)',
    'Informe a cura recebida antes da redução do Corpo Exaurido. Para ajustes já calculados, use a caixa ±. Esta ação não cura invocações.',ui.ButtonSet.OK_CANCEL);
  if(resposta.getSelectedButton()!==ui.Button.OK)return;
  var texto=resposta.getResponseText().trim();
  if(!/^\d+$/.test(texto)){ui.alert('Informe um número inteiro igual ou maior que zero.');return;}
  var s,conta,bruto=Number(texto);
  try{s=r53LerCura_(ss);conta=r53ContaCura_(s,bruto);}catch(err){ui.alert(err.message);return;}
  try {
    var queda=typeof r53SocorroLer_==='function'?r53SocorroLer_(ss):null;
    if(s.atual===0||(queda&&r53SocorroAtivo_(queda))) {
      if(typeof r53SocorroAplicarCura_!=='function')throw Error('Vida em zero: registre o tratamento de Morrendo antes de alterar a vida.');
      r53SocorroAplicarCura_(ss,bruto);return;
    }
  } catch(err) {ui.alert(err.message);return;}
  if(!conta.aplicado){ui.alert('Nenhuma vida será acrescentada. A vida atual foi preservada.');return;}
  var resumo='Cura informada: '+bruto+'\n'+(conta.reduz?'Corpo Exaurido: metade, arredondada para baixo, mínimo 1.\n':'')+
    'Ganho após a regra: '+conta.ganho+'\nVida: '+s.atual+' → '+conta.depois+' (máximo '+s.maximo+').\nA vida temporária não muda.';
  if(ui.alert('Confirmar cura do personagem',resumo,ui.ButtonSet.YES_NO)!==ui.Button.YES)return;
  // Não segurar lock durante o diálogo: o Apps Script suspende a execução nele.
  var lock=LockService.getDocumentLock(),erro=null;
  if(!lock.tryLock(5000)){ui.alert('Outra operação está em andamento. Tente novamente.');return;}
  try{
    var atual=r53LerCura_(ss);
    if(JSON.stringify(atual)!==JSON.stringify(s))throw Error('A vida ou a Origem mudou durante a confirmação. Confira a ficha e aplique a cura novamente.');
    ss.getSheetByName('FICHA').getRange('D26').setValue(conta.depois);
    SpreadsheetApp.flush();
  }catch(err){erro=err.message;}finally{lock.releaseLock();}
  if(erro){ui.alert(erro);return;}
  ss.toast('Vida '+s.atual+' → '+conta.depois+' · cura aplicada '+conta.aplicado,'Cura recebida',6);
}
