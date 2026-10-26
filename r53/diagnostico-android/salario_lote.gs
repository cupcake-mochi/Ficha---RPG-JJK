/**
 * Salário nas cópias sem rotina ativada (24/10/2026).
 *
 * O valor pendente é calculado por fórmula (Salarios.gs, SALARIO_.f): aparece na hora em qualquer aparelho, sem
 * gatilho. Este módulo só congela no livro, quando sobra tempo, os períodos que a fórmula já mostra. Congelar é uma
 * leitura e uma gravação; se não acontecer, nada some nem paga em dobro, porque a fórmula recomeça no fim do livro.
 * Medido: uma edição desta ficha gasta 18–24 s sozinha, e o app do Android não roda o onOpen.
 */
var R53_SAL_PROP_ = 'salario_proximo';
// O tempo das APIs não é previsível. Este limite só admite o início do congelamento depois da edição.
var R53_SAL_INICIAR_MS_ = 8000;

/** A edição é entregue integralmente ao wrapper já instalado, com o evento original.
 * Não há return do salário antes dos cartões/XP/paleta, nem replay desses efeitos. */
function r53SalarioOnEdit_(e) {
  var inicio = Date.now(), fase = 'edicao', edicaoMs, resultado;
  try {
    try {
      // 26/10/2026: o nome da aba fica guardado no evento. Perguntado de novo depois do flush, ele esperava o
      // recálculo da edição (4,6–4,8 s medidos na cópia em toda edição rápida).
      if (e && e.range) {
        e.r53SalAba_ = e.range.getSheet().getName();
        if (r53SalarioAreaPropria_(e.range, e.r53SalAba_)) PropertiesService.getDocumentProperties().deleteProperty(R53_SAL_PROP_);
      }
    } catch (err) { console.log('SAL invalidação: ' + err.message); }
    resultado = r53OnEditOriginal_(e);
    SpreadsheetApp.flush();
    edicaoMs = Date.now() - inicio;
    fase = 'salario';
    if (edicaoMs < R53_SAL_INICIAR_MS_) r53SalarioLote_(e);
    fase = 'concluido';
    return resultado;
  } finally {
    console.log('R53_ONEDIT ' + JSON.stringify({ms: Date.now() - inicio, edicaoMs: edicaoMs, fase: fase}));
  }
}

/** Rodar uma vez pelo editor: colunas da fórmula, painel e total. Não mexe no livro nem nas missões. */
function prepararSalarioLote() {
  var ss = SpreadsheetApp.getActive();
  salarioBloqueado_(ss, function () { salarioPrepararFormulas_(ss); }, 30000);
  PropertiesService.getDocumentProperties().deleteProperty(R53_SAL_PROP_);
  console.log('SAL fórmulas prontas em DADOS_SALARIOS!P1:Y11 e no painel');
}

/** Áreas que o salarioEditar_ já trata (e que mudam o próximo fechamento). */
function r53SalarioAreaPropria_(r, aba) {
  var n = aba || r.getSheet().getName();
  return n === SALARIO_.config && salarioToca_(r, 35, 76, 11, 17)
    || n === 'FICHA PESSOAL' && (salarioToca_(r, 15, 87, 49, 72) || salarioToca_(r, 11, 11, 28, 30) || salarioToca_(r, 86, 86, 23, 30))
    || n === 'CARTEIRA' && (salarioToca_(r, 3, 3, 46, 46) || salarioToca_(r, 9, 15, 15, 45));
}

/** Chamado depois da edição original e seu flush. Nunca cancela a edição. */
function r53SalarioLote_(e) {
  if (!e || !e.range) return false;
  var t0 = Date.now(), r = e.range, props = PropertiesService.getDocumentProperties(), aba = e.r53SalAba_ || r.getSheet().getName();
  if (aba === 'CARTEIRA' && r.getRow() === 27 && r.getLastRow() === 27 && r.getColumn() === 3 && r.getLastColumn() === 3) return false;
  if (r53SalarioAreaPropria_(r, aba)) { props.deleteProperty(R53_SAL_PROP_); return false; }
  return r53SalarioConferir_(e.source || SpreadsheetApp.getActive(), t0, props);
}

/** Chamado no onOpen (PC e navegador; o app do Android não roda). */
function r53SalarioAbrir_() {
  var t0 = Date.now(), feito = false;
  try { feito = r53SalarioConferir_(SpreadsheetApp.getActive(), t0, PropertiesService.getDocumentProperties()); }
  catch (err) { console.log('SAL abertura: ' + err.message); }
  console.log('R53_ABRIR ' + JSON.stringify({ms: Date.now() - t0, fechou: feito}));
  return feito;
}

/** Compara datas sem ler a planilha; vencido, congela sob bloqueio. */
function r53SalarioConferir_(ss, t0, props) {
  if (PropertiesService.getScriptProperties().getProperty('salario_edicao') === ScriptApp.getScriptId()) return false;
  var hoje = salarioHoje_(), proximo = Number(props.getProperty(R53_SAL_PROP_));
  if (proximo && hoje < proximo) return false;
  var marca = function (o) { console.log('SAL ' + o + ' ' + (Date.now() - t0) + ' ms'); };
  var lock = LockService.getDocumentLock();
  if (!lock.tryLock(1500)) return false;
  try {
    // Outra execução pode ter congelado enquanto esta esperava o bloqueio.
    proximo = Number(props.getProperty(R53_SAL_PROP_));
    if (proximo && hoje < proximo) return false;
    marca('início');
    var feito = salarioCongelar_(ss, hoje);
    SpreadsheetApp.flush();
    marca('congelados ' + feito.novos);
    if (isFinite(feito.proximo) && feito.proximo > hoje) props.setProperty(R53_SAL_PROP_, String(feito.proximo));
    return feito.novos > 0;
  } catch (err) {
    props.deleteProperty(R53_SAL_PROP_);
    console.log('Salários: ' + err.message);
    return false;
  } finally { lock.releaseLock(); }
}
