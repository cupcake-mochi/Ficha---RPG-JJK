/** @OnlyCurrentDoc */
/** Diagnóstico manual de leitura. Não instala eventos nem muda células.
 * Adicione como arquivo separado ao projeto vinculado; execute manualmente.
 * Não chame por onOpen/onEdit. O resultado não contém histórico salarial.
 */
function auditarContextoAndroid() {
  var allowed = [
    '1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro',
    '1427V3IO_RSToQcsO1ZgAeArXoT_PdoHukN9jAVkBfy8',
    '1E9V_bvYXUsaCEmHr7dHa79REnRan9mopZ7JX7jkasMY'
  ];
  var ss = SpreadsheetApp.getActive();
  if (!ss || allowed.indexOf(ss.getId()) < 0)
    throw new Error('Diagnóstico restrito à oficial e às duas cópias identificadas.');
  var started = Date.now(), sid = ScriptApp.getScriptId(), timings = {};
  function read(label, fn) {
    var start = Date.now();
    try { return fn(); }
    catch (err) { return {erro: String(err.message || err)}; }
    finally { timings[label] = Date.now() - start; }
  }
  function hash(text) {
    return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,
      String(text), Utilities.Charset.UTF_8).map(function(b) {
        return ('0' + ((b + 256) % 256).toString(16)).slice(-2);
      }).join('');
  }
  function summary(text) {
    if (text === null || text === undefined) return {presente: false};
    var result = {presente: true, caracteres: String(text).length, sha256: hash(text)};
    try {
      var parsed = JSON.parse(text);
      result.tipo = Array.isArray(parsed) ? 'array' : typeof parsed;
      if (parsed && typeof parsed === 'object') result.itens = Object.keys(parsed).length;
    } catch (err) { result.tipo = 'texto'; }
    return result;
  }
  var result = {versao: 1, planilha: ss.getId(), projeto: sid,
    dataUTC: new Date().toISOString(), somenteLeitura: true};
  result.paleta = read('paleta', function() {
    var props = PropertiesService.getDocumentProperties(), out = {};
    ['paleta_atual', 'paleta_pendente', 'paleta_base', 'paleta_menu_versao'].forEach(function(k) {
      out[k] = props.getProperty(k);
    });
    ['paleta_feito', 'paleta_tempos', 'paleta_ultima_troca', 'paleta_detalhe'].forEach(function(k) {
      out[k] = summary(props.getProperty(k));
    });
    var named = ss.getRangeByName('PALETA_ESCOLHIDA');
    out.escolha = named ? named.getCell(1, 1).getValue() : null;
    return out;
  });
  result.acionadores = read('acionadores', function() {
    return ScriptApp.getProjectTriggers().map(function(t) {
      var sourceId = null;
      try { sourceId = t.getTriggerSourceId(); } catch (err) {}
      return {funcao: t.getHandlerFunction(), evento: String(t.getEventType()),
        origem: String(t.getTriggerSource()), planilhaOrigem: sourceId};
    });
  });
  result.salarios = read('salarios', function() {
    var ds = ss.getSheetByName('DADOS_SALARIOS'), cfg = ss.getSheetByName('CONFIGURAÇÃO');
    var raw = ds ? ds.getRange('L2').getValue() : '';
    var state = raw ? JSON.parse(raw) : {};
    var marker = PropertiesService.getScriptProperties().getProperty('salario_edicao');
    return {moduloInicializado: !!raw, versao: state.versao || null,
      agendaPresente: !!state.agenda, agendaApontaEsteProjeto: state.agenda === sid,
      edicaoInstalavelMarcadaNesteProjeto: marker === sid,
      rotuloAgenda: cfg ? cfg.getRange('O74').getValue() : null};
  });
  result.intervalosNomeados = read('nomes', function() {
    return ss.getNamedRanges().map(function(n) {
      var range = n.getRange();
      return {nome: n.getName(), aba: range.getSheet().getName(), faixa: range.getA1Notation()};
    });
  });
  result.temposLeiturasMs = timings;
  result.duracaoMs = Date.now() - started;
  result.limites = [
    'Execução manual não mede abertura ou RAM do Android.',
    'Acionadores visíveis são os acessíveis à conta que executou o diagnóstico.',
    'Um estado diferente não demonstra causalidade; comparar tentativas e horários.',
    'Não lista execuções anteriores; consultar o painel Execuções do projeto.'
  ];
  console.log(JSON.stringify(result));
  return result;
}
