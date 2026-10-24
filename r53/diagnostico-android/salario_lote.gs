/**
 * Fechamento do salário em lote, no acionador simples (teste em cópia descartável, 24/10/2026).
 *
 * Cópia sem rotina ativada não fecha o salário: a conferência leva ~80 s e o onEdit tem 30 s. Depois da edição original,
 * compara hoje com o próximo fechamento guardado nas propriedades, sem ler a planilha. Vencido, lê uma vez só
 * DADOS_SALARIOS (missões carimbadas, estado e a coluna N, que junta por fórmula config, Grau, nome e livro), faz a
 * conta do salarioApurar_ na memória e grava tudo no fim. Mesma regra, mesmo bloqueio, mesma trava de período repetido.
 */
var R53_SAL_PROP_ = 'salario_proximo', R53_SAL_REPARAR_ = 'salario_lote_reparar', R53_SAL_LINHAS_ = 1000;
// O tempo das APIs não é previsível. Este limite só admite o início do lote;
// a validação do onEdit inteiro no Google continua obrigatória antes da promoção.
var R53_SAL_INICIAR_MS_ = 8000;

/** A edição é entregue integralmente ao wrapper já instalado, com o evento original.
 * Não há return do salário antes dos cartões/XP/paleta, nem replay desses efeitos.
 * Se faltar orçamento, somente o salário aguarda uma nova edição. */
function r53SalarioOnEdit_(e) {
  var inicio = Date.now(), fase = 'edicao', edicaoMs, resultado;
  try {
    // Invalidar antes do processamento: uma edição de regra/Grau pode consumir
    // todo o prazo, e o vencimento antigo não pode continuar escondendo a revisão.
    try {
      if (e && e.range && r53SalarioAreaPropria_(e.range))
        PropertiesService.getDocumentProperties().deleteProperty(R53_SAL_PROP_);
    } catch (err) { console.log('SAL invalidação: ' + err.message); }
    resultado = r53OnEditOriginal_(e);
    SpreadsheetApp.flush();
    edicaoMs = Date.now() - inicio;
    fase = 'salario';
    if (edicaoMs < R53_SAL_INICIAR_MS_) r53SalarioLote_(e);
    else console.log('SAL adiado: edição e flush consumiram ' + edicaoMs + ' ms');
    fase = 'concluido';
    return resultado;
  } finally {
    console.log('R53_ONEDIT ' + JSON.stringify({ms: Date.now() - inicio, edicaoMs: edicaoMs, fase: fase}));
  }
}
// Coluna N de DADOS_SALARIOS, linha a linha a partir da 2.
var R53_SAL_FORMULAS_ = [
  ["Emissão", "='CONFIGURAÇÃO'!O38"], ["Salário automático", "='CONFIGURAÇÃO'!O40"],
  ["Intervalo (dias)", "='CONFIGURAÇÃO'!O41"], ["Participações para 100%", "='CONFIGURAÇÃO'!O42"],
  ["Parcela mínima", "='CONFIGURAÇÃO'!O43"], ["Verificar missões", "='CONFIGURAÇÃO'!O44"],
  ["Próximo fechamento", "='CONFIGURAÇÃO'!O48"],
  ["Grau 4", "='CONFIGURAÇÃO'!O54"], ["Grau 3", "='CONFIGURAÇÃO'!O55"], ["Grau 2", "='CONFIGURAÇÃO'!O56"],
  ["Grau 1", "='CONFIGURAÇÃO'!O57"], ["Especial", "='CONFIGURAÇÃO'!O58"],
  ["Peso Curta", "='CONFIGURAÇÃO'!O62"], ["Peso Padrão", "='CONFIGURAÇÃO'!O63"], ["Peso Longa", "='CONFIGURAÇÃO'!O64"],
  ["Peso Final de arco", "='CONFIGURAÇÃO'!O65"], ["Peso Solo simples", "='CONFIGURAÇÃO'!O66"],
  ["Peso Solo complexa", "='CONFIGURAÇÃO'!O67"],
  ["Grau atual", "='FICHA PESSOAL'!AB11"], ["Personagem", "=CARTEIRA!O9"],
  ["Fechamentos no livro", "=COUNTA('SALÁRIOS'!A2:A)"], ["Linhas do livro", "=ROWS('SALÁRIOS'!A:A)"],
  ["Fim do último fechamento", "=IFERROR(INDEX('SALÁRIOS'!C2:C,N22),\"\")"],
  ["Períodos já pagos", "=TEXTJOIN(\"|\",TRUE,'SALÁRIOS'!A2:A)"]
];

/** Rodar uma vez pelo editor (na base, antes de copiar): monta a coluna de leitura e corrige o texto da agenda. */
function prepararSalarioLote() {
  var ss = SpreadsheetApp.getActive(), sh = ss.getSheetByName(SALARIO_.dados);
  sh.getRange(1, 13, 1, 2).setValues([['Leitura do fechamento em lote', 'Valor']]);
  sh.getRange(2, 13, R53_SAL_FORMULAS_.length, 1).setValues(R53_SAL_FORMULAS_.map(function (l) { return [l[0]]; }));
  sh.getRange(2, 14, R53_SAL_FORMULAS_.length, 1).setFormulas(R53_SAL_FORMULAS_.map(function (l) { return [l[1]]; }));
  if (PropertiesService.getScriptProperties().getProperty('salario_edicao') !== ScriptApp.getScriptId())
    ss.getSheetByName(SALARIO_.config).getRange('O74').setValue('Na primeira edição após o vencimento');
  PropertiesService.getDocumentProperties().deleteProperty(R53_SAL_PROP_);
  console.log('SAL coluna de leitura pronta em DADOS_SALARIOS!M1:N' + (R53_SAL_FORMULAS_.length + 1));
}

/** Áreas que o salarioEditar_ já trata (e que mudam o próximo fechamento). */
function r53SalarioAreaPropria_(r) {
  var n = r.getSheet().getName();
  return n === SALARIO_.config && salarioToca_(r, 35, 76, 11, 17)
    || n === 'FICHA PESSOAL' && (salarioToca_(r, 15, 87, 49, 72) || salarioToca_(r, 11, 11, 28, 30) || salarioToca_(r, 86, 86, 23, 30))
    || n === 'CARTEIRA' && (salarioToca_(r, 3, 3, 46, 46) || salarioToca_(r, 9, 15, 15, 45));
}

/** Chamado depois da edição original e seu flush. Nunca cancela a edição. */
function r53SalarioLote_(e) {
  if (!e || !e.range) return false;
  var t0 = Date.now(), r = e.range, props = PropertiesService.getDocumentProperties();
  if (r.getSheet().getName() === 'CARTEIRA' && r.getA1Notation() === 'C27') return false;
  if (r53SalarioAreaPropria_(r)) { props.deleteProperty(R53_SAL_PROP_); return false; }
  if (PropertiesService.getScriptProperties().getProperty('salario_edicao') === ScriptApp.getScriptId()) return false;
  var hoje = salarioHoje_(), proximo = Number(props.getProperty(R53_SAL_PROP_));
  if (proximo && hoje < proximo && !props.getProperty(R53_SAL_REPARAR_)) return false;
  var ss = e.source || SpreadsheetApp.getActive();
  var marca = function (o) { console.log('SAL ' + o + ' ' + (Date.now() - t0) + ' ms'); };
  marca('início');
  var lock = LockService.getDocumentLock();
  if (!lock.tryLock(1500)) return false;
  try {
    // Outra edição pode ter fechado enquanto esta esperava o bloqueio.
    proximo = Number(props.getProperty(R53_SAL_PROP_));
    if (proximo && hoje < proximo && !props.getProperty(R53_SAL_REPARAR_)) return false;
    var feito = r53SalarioFechar_(ss, hoje, props, marca);
    SpreadsheetApp.flush();
    marca('flush confirmado');
    // A propriedade só permite pular leituras depois de confirmar livro, estado e painel.
    props.setProperty(R53_SAL_PROP_, String(feito.proximo));
    props.deleteProperty(R53_SAL_REPARAR_);
    return feito.novos > 0;
  } catch (err) {
    props.deleteProperty(R53_SAL_PROP_);
    console.log('Salários: ' + err.message);
    // Um setter pode falhar depois de enfileirar o livro. Tenta concluir essa
    // fila ainda sob lock; a marca de reparação continua mesmo se este flush passar.
    try { SpreadsheetApp.flush(); }
    catch (flushErr) { console.log('Salários: flush de recuperação falhou: ' + flushErr.message); }
    // Não escreve um status após falha: criaria novas escritas não confirmadas.
    return false;
  } finally { lock.releaseLock(); }
}

/** A conta do salarioApurar_ sobre uma leitura só; a recuperação relê também o livro persistido. */
function r53SalarioFechar_(ss, hoje, props, marca) {
  var dados = ss.getSheetByName(SALARIO_.dados), v = dados.getRange(1, 1, R53_SAL_LINHAS_, 14).getValues();
  marca('leitura');
  var n = function (i) { return v[i + 1][13]; };            // N2 = n(0)
  var c = {emissao: salarioDia_(n(0)), ligado: n(1) === true, dias: salarioInt_(n(2), 1, 3650, 'o intervalo em dias'),
    meta: salarioInt_(n(3), 1, 1000, 'a meta de participações'), minimo: n(4), verifica: n(5) === true,
    proximo: salarioDia_(n(6)), bases: {}, pesos: {}};
  if (!isFinite(c.emissao)) throw Error('Informe uma data de emissão válida em O38.');
  if (typeof c.minimo !== 'number' || !isFinite(c.minimo) || c.minimo < 0 || c.minimo > 1) throw Error('A parcela mínima deve estar entre 0% e 100%.');
  SALARIO_.graus.forEach(function (g, i) { c.bases[g] = salarioInt_(n(7 + i), 0, 1e12, 'o salário de ' + g); });
  SALARIO_.tipos.forEach(function (t, i) { c.pesos[t] = salarioInt_(n(12 + i), 0, 1000, 'o peso de ' + t); });
  var grau = String(n(18)), personagem = String(n(19) || '').trim();
  if (personagem === 'Coloque o nome do personagem aqui') personagem = '';
  var nPagos = Number(n(20)) || 0, linhasLivro = Number(n(21)) || 0, ultimoFim = salarioDia_(n(22));
  var pagos = {};
  String(n(23) || '').split('|').forEach(function (id) { if (id) pagos[id] = true; });
  var reparar = !!props.getProperty(R53_SAL_REPARAR_), livro = ss.getSheetByName(SALARIO_.livro);
  if (reparar) {
    // Não confia no resumo por fórmulas após uma resposta de escrita incerta.
    // O livro efetivamente persistido é a autoridade, mesmo com L2/painel adiantados.
    var ultimaLinha = livro.getLastRow(), linhas = ultimaLinha > 1 ? livro.getRange(2, 1, ultimaLinha - 1, 12).getValues() : [];
    pagos = {}; nPagos = 0; ultimoFim = NaN; linhasLivro = livro.getMaxRows();
    linhas.forEach(function (l) {
      if (!l[0] || pagos[l[0]] || !isFinite(salarioDia_(l[2])) || typeof l[9] !== 'number' || !isFinite(l[9]))
        throw Error('Livro de salários incompleto ou repetido; preserve o histórico e revise antes de continuar.');
      pagos[l[0]] = true; nPagos++; ultimoFim = salarioDia_(l[2]);
    });
    marca('livro relido para recuperação');
  }
  var estado = v[1][11] ? JSON.parse(v[1][11]) : {};
  var missoes = v.slice(1).filter(function (l) { return l[0]; });

  if (nPagos && isFinite(ultimoFim)) estado.inicio = Math.max(ultimoFim, c.emissao);
  else { estado.inicio = c.emissao; if (estado.graus && estado.graus.length) estado.graus[0][0] = Math.min(c.emissao, estado.graus[0][0]); }
  var hist = salarioHistoricoGrau_(ss, estado, hoje, grau), inicio = estado.inicio, novos = [];
  if (c.ligado && personagem) {
    while (inicio + c.dias <= hoje && novos.length < 120) {
      var fim = inicio + c.dias, g = salarioGrauNoFim_(hist, fim);
      if (!Object.prototype.hasOwnProperty.call(c.bases, g)) throw Error('Grau sem referência no fechamento. Revise o histórico.');
      var pontos = salarioPontos_(missoes, inicio, fim, c.pesos), pct = salarioPercentual_(pontos, c.meta, c.minimo, c.verifica);
      var id = 'SAL1:' + inicio + ':' + fim;
      if (pagos[id]) throw Error('Período já registrado. Revise o histórico de salários.');
      novos.push([id, salarioData_(inicio), salarioData_(fim), salarioData_(hoje), g, c.bases[g], pontos, c.meta, pct,
        salarioValor_(c.bases[g], pontos, c.meta, c.minimo, c.verifica),
        c.verifica ? 'Participação no período' : 'Participação dispensada pela campanha',
        JSON.stringify({dias: c.dias, minimo: c.minimo, pesos: c.pesos, personagem: personagem, lote: true})]);
      inicio = fim;
    }
  }
  marca('calculado (' + novos.length + ' fechamentos)');
  // Nada vencido (pausado, sem nome ou primeira edição numa cópia sem a data guardada): só guarda quando olhar de
  // novo, sem gravar na planilha. Nomear o personagem ou mexer na configuração apaga essa data (área própria).
  if (!novos.length && !reparar) {
    return {novos: 0, proximo: c.ligado && personagem ? Math.max(inicio + c.dias, hoje + 1) : hoje + 1};
  }
  // Persistida ANTES da primeira escrita. Sobrevive a exceção/timeout, incluindo
  // livro gravado com falha posterior no estado, painel ou flush.
  props.setProperty(R53_SAL_REPARAR_, '1');
  if (novos.length) {
    var at = nPagos + 2;
    if (linhasLivro < at + novos.length - 1) livro.insertRowsAfter(linhasLivro, at + novos.length - 1 - linhasLivro);
    livro.getRange(at, 1, novos.length, 12).setValues(novos);
  }
  estado.inicio = inicio; estado.ultimaEmissao = c.emissao;
  dados.getRange('L2').setValue(JSON.stringify(estado));
  var cfg = ss.getSheetByName(SALARIO_.config), p = salarioPontos_(missoes, inicio, inicio + c.dias, c.pesos);
  cfg.getRange('O48').setValue(salarioData_(inicio + c.dias));
  cfg.getRange('O69:O72').setValues([[salarioData_(inicio)], [p],
    [Object.prototype.hasOwnProperty.call(c.bases, grau) ? salarioValor_(c.bases[grau], p, c.meta, c.minimo, c.verifica) : 'Grau inválido'],
    [novos.length ? salarioData_(inicio) : nPagos ? salarioData_(ultimoFim) : 'Nenhum']]);
  salarioStatus_(ss, !c.ligado ? 'Salário pausado; períodos pendentes serão apurados ao religar.' :
    !personagem ? 'Aguardando o nome do personagem na CARTEIRA.' :
    inicio + c.dias <= hoje ? 'Há períodos pendentes; confira salários novamente.' :
    'Em dia · próximo fechamento ' + salarioTextoDia_(inicio + c.dias));
  marca('gravações enfileiradas');
  return {novos: novos.length, proximo: c.ligado && personagem ? inicio + c.dias : hoje + 1};
}
