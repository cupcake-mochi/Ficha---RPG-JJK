/** ±: usa o valor do evento entregue; a trava serializa somente estes ajustes.
 * Não reconstrói eventos descartados pelo Google nem ordena eventos fora de ordem.
 * x = {d:delta,a:atual,m:max,t:temp,cheio:atual vazio significa máximo}.
 * Sempre consome o caminho, mesmo numa falha: não repetir uma gravação parcial.
 */
function r53DeltaExecutar_(e, x, calcular) {
  var trava, passo = null, presa = false, escreveu = false, enviou = false;
  var aba = e.range.getSheet();
  try {
    var unica = e.range.getNumRows() === 1 && e.range.getNumColumns() === 1;
    // Uma exclusão antiga não deve consumir a entrada que chegou depois dela.
    if (unica && e.value === undefined && e.oldValue !== undefined) return true;
    var evento = unica && e.value !== undefined;
    if (evento) {
      passo = Number(e.value);
      // No pt-BR, o evento pode trazer o texto com vírgula, mesmo quando a célula é numérica.
      if (isNaN(passo) && typeof e.value === 'string' &&
          /^[+-]?\d+(?:\.\d{3})*,\d+$/.test(e.value.trim()) &&
          (e.source || aba.getParent()).getSpreadsheetLocale() === 'pt_BR') {
        passo = Number(e.value.trim().replace(/\./g, '').replace(',', '.'));
      }
    }
    if (evento && (!isFinite(passo) || !passo)) return true;
    trava = LockService.getDocumentLock();
    // Dá tempo para o desconto anterior gravar, com espera limitada no onEdit.
    if (!trava || !trava.tryLock(12000)) throw Error('outro ajuste de recurso ainda está em execução');
    presa = true;
    var enderecos = [x.d, x.a, x.m].concat(x.t ? [x.t] : []);
    var pos = enderecos.map(function (a) {
      var m = /^([A-Z]+)([0-9]+)$/.exec(a), c = 0;
      if (!m) throw Error('endereço de recurso inválido');
      for (var i = 0; i < m[1].length; i++) c = c * 26 + m[1].charCodeAt(i) - 64;
      return [Number(m[2]), c];
    });
    var ls = pos.map(function (p) { return p[0]; }), cs = pos.map(function (p) { return p[1]; });
    var l = Math.min.apply(null, ls), c = Math.min.apply(null, cs);
    var v = aba.getRange(l, c, Math.max.apply(null, ls)-l+1, Math.max.apply(null, cs)-c+1).getValues();
    var q = function (i) { return v[pos[i][0]-l][pos[i][1]-c]; };
    var comandoAtual = Number(q(0));
    if (!evento) passo = comandoAtual;
    if (!isFinite(passo) || !passo) return true;
    var max = Number(q(2)) || 0, atual = q(1);
    var antes = x.t ? Math.max(0, Number(q(3)) || 0) : 0;
    if (x.cheio && (atual === '' || atual === null)) atual = max;
    var fim = calcular(atual, max, antes, passo);
    escreveu = true;
    aba.getRange(x.a).setValue(fim.atual);
    if (x.t && fim.temp !== antes) aba.getRange(x.t).setValue(fim.temp);
    // Usa a leitura sob a trava, antes de escrever. Reler depois das escritas
    // força um envio intermediário ao Sheets e prolonga a contenção.
    if (comandoAtual === passo) aba.getRange(x.d).clearContent();
    SpreadsheetApp.flush();
    enviou = true;
  } catch (err) {
    console.log('ajuste ±: ' + err.message);
    try {
      var alvo = aba.getName() + '!' + x.d;
      var ajuste = passo !== null && isFinite(passo) ? 'Ajuste ' + passo + ' em ' + alvo : 'Ajuste em ' + alvo;
      var mensagem = escreveu ? ajuste + ' pode ter sido aplicado parcialmente. Confira os saldos antes de repetir.' :
        ajuste + ' não aplicado. Confira os saldos e repita esse ajuste se necessário.';
      (e.source || SpreadsheetApp.getActive()).toast(mensagem, 'Recursos', 10);
    } catch (aviso) { console.log('aviso ±: ' + aviso.message); }
  } finally {
    if (presa) {
      // Uma falha parcial também precisa ser enviada antes de liberar a trava.
      try { if (escreveu && !enviou) SpreadsheetApp.flush(); }
      catch (envio) { console.log('envio ±: ' + envio.message); }
      try { trava.releaseLock(); }
      catch (liberar) { console.log('trava ±: ' + liberar.message); }
    }
  }
  return true;
}
