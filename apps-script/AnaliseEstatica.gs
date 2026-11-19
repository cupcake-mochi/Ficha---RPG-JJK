// ANALISE estática · 17/11/2026 (fase 1 do plano da ANALISE estática).
//
// As 18.480 fórmulas da coluna B da ANALISE pesavam em toda edição da ficha. Numa cópia da Era, o ± caiu de ~17,1 s
// para ~14,1 s com a coluna congelada, e o CSV exportado saiu igual ao vivo nas 18.500 linhas. Só o bot lê essa aba.
// Aqui a coluna B vira valor numa exportação sob pedido:
// - os modelos (o texto de cada fórmula) moram na aba oculta ANALISE_MODELOS, que o link do bot (sheet=ANALISE)
//   não baixa. A linha N de lá é a linha N da ANALISE;
// - exportar escreve os modelos na coluna B em blocos, espera o cálculo e troca cada bloco pelo valor. O progresso
//   fica guardado depois de cada bloco: se o tempo acabar, a próxima exportação continua de onde parou;
// - a primeira edição depois de exportar marca analise.estado = desatualizada; as outras só leem uma propriedade.
// Três jeitos de exportar: o menu Bot (PC), a caixa da CARTEIRA AT4 (celular, que não tem menu) e o fim do
// construir(). O arquivo fica fora do módulo comprimido do pacote R53: a marca roda em toda edição e não pode
// esperar o módulo abrir.
//
// Quem mexer nas fórmulas da ANALISE depois da exportação: escreva a fórmula na coluna B e rode Exportar pelo menu.
// O menu junta as fórmulas vivas da coluna B aos modelos antes de exportar. A caixa da CARTEIRA não junta, para caber
// nos 30 s do gatilho simples.

var ANALISE_EST_ = {
  aba: 'ANALISE', modelos: 'ANALISE_MODELOS', carteira: 'CARTEIRA',
  caixa: 'AT4', linhaCaixa: 4, colunaCaixa: 46, texto: 'AH4', faixa: 'AH4:AS4', molde: 'AH3:AT3', destino: 'AH4:AT4',
  prop: 'analise_estado', propProx: 'analise_exportar_prox', propLinhas: 'analise_linhas', propCaixa: 'analise_caixa',
  propModelos: 'analise_modelos_n', propBlocoMs: 'analise_bloco_ms', propTotal: 'analise_modelos_total',
  propFeitas: 'analise_exportar_feitas',
  estados: ['viva', 'exportando', 'em_dia', 'desatualizada'],
  // Medido na cópia da Era (17/11), com a ANALISE viva:
  // - cada leitura da planilha custa de 2 a 3 s, do tamanho que for (10 linhas ou 18.499; até o getLastRow).
  //   Escrita fica pendente e só pesa no flush. Por isso a caixa lê uma vez só (os modelos) e o resto vem das propriedades;
  // - um bloco de 6.000 linhas levou 10 s: leitura 1,8 s, cálculo 3,9 s, congelamento 4,3 s;
  // - criar os modelos levou 21 s (ler as fórmulas 7,9 s, gravar a aba 13,4 s), mais ~8 s de abertura do gatilho.
  // Um bloco só começa se o tempo gasto mais a duração do último bloco (guardada) couber no limite. Na caixa o limite
  // é 16 s contados do começo do onEdit: os ~7 s de antes dele também saem dos 30 s do gatilho simples, e um bloco
  // pode levar mais que o anterior (na Era: 6,7 s e depois 8,5 s; a marcação inteira deu 26,6 s).
  // Na oficial do Ciclo (18/11) a caixa com blocos de 6.500 linhas deu 24,1 s, 26,0 s e 29,1 s: o bloco garantido
  // ficou lento demais para os 30 s. A caixa usa blocos de 4.000 linhas (~5 marcações, cada uma longe do limite);
  // menu e montagem, sem o limite do gatilho, seguem com 6.500.
  // Medido de novo numa cópia do Ciclo (18/11): o bloco quase não pesa; pesam a leitura dos 18.480 modelos (~5 s), os
  // dois flush (~5 s e ~4 s) e as escritas do fim (~5 s). Por isso a caixa lê só as linhas de cada bloco (o total e as
  // fórmulas já feitas vêm das propriedades) e só escreve o estado na ANALISE quando ele muda.
  bloco: 6500, blocoCaixa: 4000, blocoMsPadrao: 12000, limiteCaixa: 16000, limiteMenu: 300000, limiteMontagem: 90000,
  versao: '13'
};

/** Menu do PC. O app do Android não roda o onOpen; lá vale a caixa da CARTEIRA. */
function analiseMenu_() {
  SpreadsheetApp.getUi().createMenu('Bot').addItem('Exportar para o bot', 'exportarParaOBot').addToUi();
}

/** Entrada do menu Bot: junta as fórmulas vivas aos modelos e exporta com até 5 minutos. */
function exportarParaOBot() {
  var r = analiseExportar_(Date.now(), ANALISE_EST_.limiteMenu, true);
  SpreadsheetApp.getActive().toast(analiseFrase_(r), 'Bot', 10);
  return r;
}

/**
 * Chamado no fim do construir(): a ficha nova nasce exportada. Se o tempo acabar, o menu ou a caixa continuam.
 * Só com o pacote R53: os ganchos do onEdit (a marca de desatualizada) e do onOpen (o menu) moram no Codigo de
 * entrada do pacote (r53/empacotar_script.py). Sem ele, congelar deixaria a ANALISE parada sem ninguém marcar.
 */
function analiseExportarNaMontagem_() {
  if (typeof r53Modulo_ !== 'function') return 'viva (sem o pacote R53, os ganchos não existem)';
  var r = analiseExportar_(Date.now(), ANALISE_EST_.limiteMontagem, true);
  return r.estado + ' ' + r.feitas + '/' + r.total;
}

/**
 * Gancho do onEdit, chamado antes de tudo. Devolve true quando a edição já foi tratada aqui
 * (a caixa da CARTEIRA, ou uma escrita na coluna B da ANALISE congelada).
 */
function analiseNaEdicao_(e) {
  try {
    if (!e || !e.range || e.r53AnaliseVista_) return false;
    e.r53AnaliseVista_ = true;
    var C = ANALISE_EST_, r = e.range, nome = e.r53SalAba_ || r.getSheet().getName();
    if (nome === C.carteira && r.getRow() === C.linhaCaixa && r.getColumn() === C.colunaCaixa &&
        r.getNumRows() === 1 && r.getNumColumns() === 1) return analiseCaixa_(e);
    var props = PropertiesService.getDocumentProperties();
    var est = props.getProperty(C.prop) || analiseSincronizar_(props);
    if (est === 'viva' || nome === C.modelos) return false;
    var ss = e.source || SpreadsheetApp.getActive();
    // A coluna B congelada não recebe a conta de volta: ela é refeita na próxima exportação.
    var naB = nome === C.aba && r.getColumn() <= 2 && r.getLastColumn() >= 2;
    if (naB) r.getSheet().getRange(r.getRow(), 2, r.getNumRows(), 1).clearContent();
    if (est === 'exportando' && props.getProperty(C.propProx)) {
      // Editou no meio: os blocos já congelados podem ter ficado velhos. A próxima exportação recomeça.
      props.deleteProperty(C.propProx);
      if (!naB) analiseTexto_(ss, props, 'exportando', 'recomeça');
    }
    // Na coluna B a marca é sempre regravada: a limpeza pode ter levado a própria célula do estado.
    if (est === 'em_dia' || naB) analiseMarcar_(ss, null, props, 'desatualizada');
    return naB;
  } catch (err) {
    console.log('ANALISE estática: ' + err.message);
    return false;
  }
}

/**
 * A caixa "Exportar para o bot" da CARTEIRA: exporta o que couber e desmarca. Qualquer toque exporta, marcando ou
 * desmarcando: uma marcação que passa dos 30 s do gatilho morre antes de desmarcar, e o toque seguinte (que desmarca)
 * tem de continuar a exportação, não ser perdido (medido em 18/11: o tempo fora do código varia de 6 a 14 s).
 */
function analiseCaixa_(e) {
  var ss = e.source || SpreadsheetApp.getActive(), r = null, v = String(e.value).toUpperCase();
  if (v !== 'TRUE' && v !== 'FALSE') return true;
  try {
    r = analiseExportar_(typeof e.r53Inicio_ === 'number' ? e.r53Inicio_ : Date.now(), ANALISE_EST_.limiteCaixa, false);
  } catch (err) {
    console.log('ANALISE estática, caixa: ' + err.message);
    ss.toast(err.message, 'Bot', 10);
  } finally {
    e.range.setValue(false);
  }
  if (r) ss.toast(analiseFrase_(r), 'Bot', 8);
  return true;
}

/**
 * Exporta a coluna B da ANALISE em blocos até o limite de tempo (contado de t0).
 * juntar: lê as fórmulas vivas da coluna B e as guarda nos modelos antes (menu e montagem).
 */
function analiseExportar_(t0, limite, juntar) {
  var C = ANALISE_EST_, ss = SpreadsheetApp.getActive(), an = ss.getSheetByName(C.aba);
  if (!an) throw new Error('Esta ficha não tem a aba ANALISE.');
  var trava = LockService.getDocumentLock();
  if (!trava.tryLock(3000)) return {estado: 'ocupada', feitas: 0, total: 0, ms: Date.now() - t0};
  try {
    var props = PropertiesService.getDocumentProperties();
    // Os modelos antes das linhas de estado: sem modelos, o erro sai sem mexer em nada.
    var lidos = analiseModelos_(ss, an, juntar, props), modelos = lidos.lista || [];
    // Na caixa as linhas de estado vêm da propriedade (ler a coluna A custaria mais uma leitura). Menu e montagem relêem.
    var linhas = null;
    if (!juntar) { try { linhas = JSON.parse(props.getProperty(C.propLinhas) || 'null'); } catch (err) { linhas = null; } }
    if (!linhas || !linhas.versao || !linhas.estado || !linhas.data) linhas = analiseLinhas_(an, props);
    var total = lidos.total, ultima = lidos.n + 1, prox = Number(props.getProperty(C.propProx)) || 2;
    if (prox < 2 || prox > ultima + 1) prox = 2;
    // As fórmulas já exportadas antes de prox: guardadas junto com o progresso, ou contadas na lista inteira.
    // Sem a conta guardada, a caixa recomeça do começo: é o lado seguro.
    var feitas = 0, guardadas = null;
    if (prox > 2 && lidos.lista) feitas = analiseContar_(modelos, prox);
    else if (prox > 2) {
      guardadas = props.getProperty(C.propFeitas);
      if (guardadas === null || isNaN(Number(guardadas))) prox = 2; else feitas = Number(guardadas);
    }
    analiseCaixaInstalar_(ss, props);
    // A caixa só escreve o estado se ele mudar (cada escrita pesa no fim da execução); menu e montagem marcam já.
    if (juntar || props.getProperty(C.prop) !== 'exportando') analiseMarcar_(ss, an, props, 'exportando', linhas, feitas + '/' + total);
    var est = Number(props.getProperty(C.propBlocoMs)) || C.blocoMsPadrao, blocos = 0;
    var tam = juntar ? C.bloco : C.blocoCaixa;
    // Um bloco por execução fica garantido se a execução não criou os modelos e ainda não gastou metade do limite: sem
    // isso, um bloco medido acima do limite travaria a caixa para sempre.
    while (prox <= ultima && (Date.now() - t0 + est < limite || (!blocos && !lidos.novos && Date.now() - t0 < limite / 2))) {
      var tb = Date.now(), fim = Math.min(prox + tam - 1, ultima);
      if (!lidos.lista) analiseLerBloco_(lidos.m, modelos, prox, fim);
      analiseEscreverBloco_(an, modelos, prox, fim);
      SpreadsheetApp.flush();
      var faixa = an.getRange(prox, 2, fim - prox + 1, 1);
      faixa.copyTo(faixa, {contentsOnly: true});
      // Congelado de fato antes de guardar o progresso: escrita pendente se perde quando o tempo acaba (17/11).
      SpreadsheetApp.flush();
      for (var j = prox; j <= fim; j++) if (modelos[j - 2]) feitas++;
      prox = fim + 1;
      props.setProperty(C.propFeitas, String(feitas));
      props.setProperty(C.propProx, String(prox));
      est = Date.now() - tb;
      props.setProperty(C.propBlocoMs, String(est));
      blocos++;
    }
    if (prox <= ultima) {
      if (juntar) analiseMarcar_(ss, an, props, 'exportando', linhas, feitas + '/' + total);
      else { props.setProperty(C.prop, 'exportando'); analiseTexto_(ss, props, 'exportando', feitas + '/' + total); }
      return {estado: 'exportando', feitas: feitas, total: total, ms: Date.now() - t0};
    }
    an.getRange(linhas.versao, 2).setValue("'" + C.versao);
    props.deleteProperty(C.propProx);
    props.deleteProperty(C.propFeitas);
    analiseMarcar_(ss, an, props, 'em_dia', linhas);
    return {estado: 'em_dia', feitas: total, total: total, ms: Date.now() - t0};
  } finally {
    trava.releaseLock();
  }
}

/** Quantas fórmulas ficam antes da linha prox (os modelos começam na linha 2). */
function analiseContar_(modelos, prox) {
  var n = 0;
  for (var i = 0; i < modelos.length && i + 2 < prox; i++) if (modelos[i]) n++;
  return n;
}

/** Lê da aba de modelos só as linhas ini..fim (a linha N de lá é a linha N da ANALISE). */
function analiseLerBloco_(m, modelos, ini, fim) {
  m.getRange(ini, 1, fim - ini + 1, 1).getValues().forEach(function (r, k) { modelos[ini - 2 + k] = String(r[0] || ''); });
}

/** Escreve os modelos das linhas ini..fim em trechos contínuos (uma chamada por trecho). */
function analiseEscreverBloco_(an, modelos, ini, fim) {
  var l = ini;
  while (l <= fim) {
    if (!modelos[l - 2]) { l++; continue; }
    var trecho = [], de = l;
    while (l <= fim && modelos[l - 2]) { trecho.push([modelos[l - 2]]); l++; }
    an.getRange(de, 2, trecho.length, 1).setFormulas(trecho);
  }
}

/**
 * Os modelos, um por linha da ANALISE a partir da linha 2 ('' onde a coluna B não é fórmula), e se foram gravados
 * agora (novos). Cria a ANALISE_MODELOS a partir das fórmulas vivas quando ela não existe ou está vazia (uma
 * execução que morreu no meio da gravação deixa a aba criada e vazia).
 */
function analiseModelos_(ss, an, juntar, props) {
  var C = ANALISE_EST_, m = ss.getSheetByName(C.modelos), lista = [], mudou = false, i;
  var n = Number(props.getProperty(C.propModelos)) || 0, total = Number(props.getProperty(C.propTotal)) || 0;
  // Caixa com os números guardados: não lê nada aqui; cada bloco lê só as próprias linhas (analiseLerBloco_).
  if (m && n > 0 && total > 0 && !juntar) return {lista: null, m: m, n: n, total: total, novos: false};
  if (m) {
    // Uma leitura só na caixa: o número de modelos vem da propriedade.
    if (!n || juntar) n = m.getLastRow() - 1;
    if (n > 0) lista = m.getRange(2, 1, n, 1).getValues().map(function (r) { return String(r[0] || ''); });
  }
  var vazia = !lista.some(Boolean);
  if (vazia || juntar) {
    var last = an.getLastRow();
    var vivas = last >= 2 ? an.getRange(2, 2, last - 1, 1).getFormulas() : [];
    for (i = 0; i < vivas.length; i++) {
      if (vivas[i][0] && lista[i] !== vivas[i][0]) { lista[i] = vivas[i][0]; mudou = true; }
    }
    for (i = 0; i < lista.length; i++) if (lista[i] === undefined) lista[i] = '';
  }
  if (!lista.some(Boolean)) {
    throw new Error('A coluna B da ANALISE não tem fórmulas e a aba ANALISE_MODELOS não existe ou está vazia: ' +
      'não há de onde exportar.');
  }
  var novos = !m || vazia || mudou;
  if (novos) {
    analiseGuardarModelos_(ss, m, lista);
    SpreadsheetApp.flush();
  }
  for (total = 0, i = 0; i < lista.length; i++) if (lista[i]) total++;
  props.setProperty(C.propModelos, String(lista.length));
  props.setProperty(C.propTotal, String(total));
  return {lista: lista, m: m, n: lista.length, total: total, novos: novos};
}

function analiseGuardarModelos_(ss, m, lista) {
  var C = ANALISE_EST_, n = lista.length + 1;
  if (!m) m = ss.insertSheet(C.modelos, ss.getSheets().length);
  if (m.getMaxRows() < n) m.insertRowsAfter(m.getMaxRows(), n - m.getMaxRows());
  if (m.getMaxColumns() > 1) m.deleteColumns(2, m.getMaxColumns() - 1);
  m.getRange(1, 1).setValue('Modelos da coluna B da ANALISE, lidos pelo "Exportar para o bot". ' +
    'A linha N daqui é a linha N de lá. Não edite.');
  // O apóstrofo guarda a fórmula como texto; a leitura devolve o texto sem ele.
  m.getRange(2, 1, lista.length, 1).setValues(lista.map(function (f) { return [f ? "'" + f : '']; }));
  if (!m.isSheetHidden()) m.hideSheet();
}

/** As linhas de formato.versao, analise.estado e analise.exportada_em; cria as duas últimas no fim da aba. */
function analiseLinhas_(an, props) {
  var linhas = analiseLinhasExistentes_(an), last = an.getLastRow(), novas = [];
  if (!linhas.versao) throw new Error('A ANALISE não tem a chave formato.versao.');
  if (!linhas.estado) { linhas.estado = last + 1 + novas.length; novas.push(['analise.estado', 'viva']); }
  if (!linhas.data) { linhas.data = last + 1 + novas.length; novas.push(['analise.exportada_em', '']); }
  if (novas.length) {
    if (an.getMaxRows() < last + novas.length) an.insertRowsAfter(an.getMaxRows(), last + novas.length - an.getMaxRows());
    an.getRange(last + 1, 1, novas.length, 2).setValues(novas);
    // Gravadas antes da propriedade apontar para elas: escrita pendente se perde quando o tempo acaba.
    SpreadsheetApp.flush();
  }
  props.setProperty(ANALISE_EST_.propLinhas, JSON.stringify(linhas));
  return linhas;
}

function analiseLinhasExistentes_(an) {
  var linhas = {}, last = an.getLastRow();
  if (last < 1) return linhas;
  an.getRange(1, 1, last, 1).getValues().forEach(function (r, i) {
    if (r[0] === 'formato.versao') linhas.versao = i + 1;
    else if (r[0] === 'analise.estado') linhas.estado = i + 1;
    else if (r[0] === 'analise.exportada_em') linhas.data = i + 1;
  });
  return linhas;
}

/**
 * Sem a propriedade (cópia da ficha, ou primeira edição depois de instalar): lê o estado na própria ANALISE uma vez.
 * Estado desconhecido vira desatualizada, que é o lado seguro: o bot pede exportação.
 */
function analiseSincronizar_(props) {
  var C = ANALISE_EST_, ss = SpreadsheetApp.getActive(), an = ss.getSheetByName(C.aba), est = 'viva';
  if (an) {
    var linhas = analiseLinhasExistentes_(an);
    if (linhas.estado) {
      est = String(an.getRange(linhas.estado, 2).getValue() || 'viva');
      if (linhas.versao && linhas.data) props.setProperty(C.propLinhas, JSON.stringify(linhas));
    }
  }
  if (C.estados.indexOf(est) < 0) est = 'desatualizada';
  var cart = ss.getSheetByName(C.carteira);
  if (cart) {
    var dv = cart.getRange(C.caixa).getDataValidation();
    if (dv && dv.getCriteriaType() === SpreadsheetApp.DataValidationCriteria.CHECKBOX) props.setProperty(C.propCaixa, '1');
  }
  props.setProperty(C.prop, est);
  return est;
}

/** Grava o estado na ANALISE, na propriedade e no texto da CARTEIRA. */
function analiseMarcar_(ss, an, props, estado, linhas, extra) {
  var C = ANALISE_EST_;
  an = an || ss.getSheetByName(C.aba);
  if (!linhas) { try { linhas = JSON.parse(props.getProperty(C.propLinhas) || 'null'); } catch (err) { linhas = null; } }
  if (an && !linhas) linhas = analiseLinhas_(an, props);
  var quando = null;
  if (an && linhas) {
    an.getRange(linhas.estado, 2).setValue(estado);
    if (estado === 'em_dia') {
      quando = new Date();
      an.getRange(linhas.data, 2).setValue("'" + Utilities.formatDate(quando, ss.getSpreadsheetTimeZone(), "yyyy-MM-dd'T'HH:mm:ss"));
    }
  }
  props.setProperty(C.prop, estado);
  analiseTexto_(ss, props, estado, quando ? Utilities.formatDate(quando, ss.getSpreadsheetTimeZone(), 'dd/MM HH:mm') : extra);
}

function analiseTexto_(ss, props, estado, extra) {
  var C = ANALISE_EST_;
  if (props.getProperty(C.propCaixa) !== '1') return;
  var cart = ss.getSheetByName(C.carteira);
  if (!cart) return;
  var t = estado === 'em_dia' ? 'Bot: em dia · ' + extra
    : estado === 'exportando' ? (extra === 'recomeça' ? 'Bot: editada no meio · toque de novo' : 'Bot: exportando ' + extra + ' · toque de novo')
    : estado === 'desatualizada' ? 'Bot: desatualizada · marque ao lado'
    : 'Bot: marque ao lado para exportar';
  cart.getRange(C.texto).setValue(t);
}

/** A caixa na linha 4 da CARTEIRA, no mesmo estilo da linha 3. Não escreve por cima de nada. */
function analiseCaixaInstalar_(ss, props) {
  var C = ANALISE_EST_;
  if (props.getProperty(C.propCaixa) === '1') return;
  var cart = ss.getSheetByName(C.carteira);
  if (!cart) return;
  var destino = cart.getRange(C.destino);
  var ocupada = destino.getValues()[0].some(function (v) { return v !== '' && v !== false; });
  if (ocupada) {
    // Cópia da ficha: a caixa veio junto, a propriedade não. Sem isto a cópia pagaria esta leitura a cada marcação
    // (~3 s, medido em 18/11) e o texto ao lado nunca mudaria.
    var dv = cart.getRange(C.caixa).getDataValidation();
    if (dv && dv.getCriteriaType() === SpreadsheetApp.DataValidationCriteria.CHECKBOX) { props.setProperty(C.propCaixa, '1'); return; }
    console.log('ANALISE estática: CARTEIRA ' + C.destino + ' ocupada; a caixa não foi instalada.');
    return;
  }
  cart.getRange(C.molde).copyTo(destino, {formatOnly: true});
  // 18/11/2026: num construir() do zero, a linha 3 ainda é uma mesclagem só (AH3:AT3; quem a separa é o
  // instalarSalarios), e a cópia do formato levava a mesclagem junto, prendendo a caixa AT4 dentro dela.
  destino.breakApart();
  try { cart.getRange(C.faixa).merge(); } catch (err) { console.log('ANALISE estática, mescla: ' + err.message); }
  cart.getRange(C.caixa).insertCheckboxes().setValue(false);
  SpreadsheetApp.flush();
  props.setProperty(C.propCaixa, '1');
}

function analiseFrase_(r) {
  if (r.estado === 'em_dia') return 'ANALISE exportada: ' + r.total + ' fórmulas em ' + Math.round(r.ms / 1000) + ' s.';
  if (r.estado === 'exportando') return 'Exportadas ' + r.feitas + ' de ' + r.total + '. Toque na caixa de novo (ou use o menu Bot) para continuar.';
  if (r.estado === 'ocupada') return 'Outra exportação está rodando. Tente de novo em instantes.';
  return String(r.estado);
}
