/** Nível inicial e base do XP de cópia nova. Requer financeiro concluído.
 * Não distribui atributos, concede marcos, escolhe Caminho ou inicializa recursos.
 * Não integra o bot nem altera fórmulas; usa o executor de financeiro.gs.
 */
var R53_NOVA_PROG_ = {
  diario: 'r53_nova_ficha_progressao_v1', escritasPorExecucao: 4, orcamentoMs: 210000,
  regra: '=IF(F46="",E46,IF(IFERROR(AND(ISNUMBER(F46),F46>=1,INT(F46)=F46,F46<=30),FALSE),F46,NA()))',
  xp: "=SUM('FICHA PESSOAL'!$BA$15:$BA$87)+SUM('FICHA PESSOAL'!$BG$15:$BG$87)+SUM('FICHA PESSOAL'!$BM$15:$BM$87)+SUM('FICHA PESSOAL'!$BS$15:$BS$87)+N(DADOS!$CZ$54)"
};
function r53NovaProgInteiro_(n) { return typeof n === 'number' && Number.isSafeInteger(n) && n >= 0; }
function r53NovaProgDados_(ss) {
  var config = ss.getSheetByName('CONFIGURAÇÃO'), dados = ss.getSheetByName('DADOS'), ficha = ss.getSheetByName('FICHA');
  if (!config || !dados || !ficha) r53NovaFinErro_('faltam abas da progressão inicial.');
  if (config.getRange('C46').getValue() !== 'Nível inicial' || dados.getRange('CY54').getValue() !== 'xp base' ||
      dados.getRange('CY47').getValue() !== 'xp total') r53NovaFinErro_('layout da progressão não reconhecido.');
  var regra = config.getRange('E46:G46'), valores = regra.getValues()[0], formulas = regra.getFormulas()[0];
  if (formulas[0] || formulas[1] ||
      (formulas[2] !== R53_NOVA_PROG_.regra && formulas[2] !== R53_NOVA_PROG_.regra.replace(/,/g, ';')))
    r53NovaFinErro_('regra de nível inicial fora do contrato.');
  var nivel = valores[1] === '' ? valores[0] : valores[1];
  if (!r53NovaProgInteiro_(nivel) || nivel < 1 || nivel > 30 || valores[2] !== nivel)
    r53NovaFinErro_('nível inicial inválido ou resultado ainda não calculado.');
  if (dados.getRange('CZ47').getFormulas()[0][0] !== R53_NOVA_PROG_.xp ||
      ficha.getRange('AN11').getFormulas()[0][0] !== '=DADOS!$CZ$47')
    r53NovaFinErro_('fórmula do XP não reconhecida; não sobrescrever.');
  var range = dados.getRange('AQ5:AR33'), curva = range.getValues(), fc = range.getFormulas();
  if (curva.length !== 29 || fc.length !== 29) r53NovaFinErro_('curva de XP incompleta.');
  curva.forEach(function(l, i) {
    // DADOS_CONFIG reinicia o acumulado no nível inicial da mesa. O prefixo
    // abaixo dele é exatamente "—", não uma curva numérica do nível 2.
    var abaixo = i + 2 < nivel;
    if (l.length !== 2 || l[0] !== i + 2 || fc[i][0] || fc[i][1] !== '=DADOS_CONFIG!$Z$' + (i + 3) ||
        (abaixo ? l[1] !== '—' : !r53NovaProgInteiro_(l[1]) ||
          (i + 2 === nivel && l[1] !== 0) ||
          (i > 0 && i + 1 >= nivel && l[1] < curva[i - 1][1])))
      r53NovaFinErro_('curva de XP inválida ou ainda não calculada.');
  });
  return {nivel: nivel, base: nivel === 1 ? 0 : curva[nivel - 2][1],
          regra: [valores, formulas], curva: [curva, fc]};
}
function r53NovaProgFormulaMissao_(linha, grupo) {
  var cols = [['AX', 'AY', 'AZ'], ['BD', 'BE', 'BF'], ['BJ', 'BK', 'BL'], ['BP', 'BQ', 'BR']][grupo];
  var x = '$' + cols[0] + linha, a = '$' + cols[1] + linha, d = '$' + cols[2] + linha;
  var v = 'ROUND(VLOOKUP(' + x + ',DADOS!$CL$5:$CM$10,2,FALSE)*IF(' + a + '="",1,VLOOKUP(' + a +
    ',DADOS!$CO$5:$CP$7,2,FALSE))*IF(' + d + '="",1,VLOOKUP(' + d + ',DADOS!$CR$5:$CS$15,2,FALSE)),4)';
  return '=IF(' + x + '="","",IFERROR(IF(' + v + '>0,MAX(1,FLOOR(' + v + ',1)),0),""))';
}
function r53NovaProgMissoes_(ss) {
  var sh = ss.getSheetByName('FICHA PESSOAL');
  if (!sh) r53NovaFinErro_('falta o painel de missões.');
  var r = sh.getRange('AW15:BS87'), v = r.getValues(), f = r.getFormulas(), n = r.getNotes(), out = [];
  if (v.length !== 73 || f.length !== 73 || n.length !== 73) r53NovaFinErro_('painel de missões incompleto.');
  for (var i = 0; i < 73; i++) {
    if (v[i].length !== 23 || f[i].length !== 23 || n[i].length !== 23) r53NovaFinErro_('painel de missões incompatível.');
    for (var c = 0; c < 23; c++) {
      if (c % 6 < 4) {
        if (v[i][c] !== '' || f[i][c] !== '' || n[i][c] !== '')
          r53NovaFinErro_('missões não estão limpas; não inicializar a progressão.');
        out.push([v[i][c], f[i][c], n[i][c]]);
      } else if (c % 6 === 4) {
        var esperada = r53NovaProgFormulaMissao_(i + 15, Math.floor(c / 6));
        if ((f[i][c] !== esperada && f[i][c] !== esperada.replace(/,/g, ';')) || (v[i][c] !== '' && v[i][c] !== 0))
          r53NovaFinErro_('total de missão incompatível ou ainda não recalculado.');
        out.push([v[i][c], f[i][c]]);
      }
    }
  }
  return out;
}
function r53NovaProgPrecondicao_(ss, contexto) {
  var raw = PropertiesService.getDocumentProperties().getProperty(R53_NOVA_FIN_.diario), j;
  try { j = raw && JSON.parse(raw); } catch (err) { j = null; }
  if (!j || j.concluido !== true || !j.plano || j.assinatura !== r53NovaFinHash_(j.plano) ||
      r53NovaFinCanon_(j.plano.vinculo) !== r53NovaFinCanon_(r53NovaFinContexto_(ss, contexto)) ||
      j.plano.layout !== r53NovaFinHash_(r53NovaFinOperacoes_(ss)))
    r53NovaFinErro_('financeiro da mesma operação ainda não foi concluído.');
  r53NovaProgMissoes_(ss);
}
function r53NovaProgOperacoes_(ss) {
  var dados = r53NovaProgDados_(ss);
  return [{aba: 'FICHA', faixa: 'AH11', tipo: 'valor', valor: dados.nivel, formulasLivres: false},
          {aba: 'DADOS', faixa: 'CZ54', tipo: 'valor', valor: dados.base, formulasLivres: false}];
}
function r53NovaProgPreservados_(ss) {
  var dados = r53NovaProgDados_(ss);
  return r53NovaFinHash_([dados, r53NovaProgMissoes_(ss),
    r53NovaFinLer_(ss, {aba: 'CONFIGURAÇÃO', faixa: 'C46:H46'}),
    ss.getSheetByName('DADOS').getRange('CZ47').getFormulas(),
    ss.getSheetByName('FICHA').getRange('AN11').getFormulas()]);
}
function r53NovaProgPerfil_() {
  return {nome: 'nivel_e_base_xp', diario: R53_NOVA_PROG_.diario, limites: R53_NOVA_PROG_,
          precondicao: r53NovaProgPrecondicao_, operacoes: r53NovaProgOperacoes_, preservados: r53NovaProgPreservados_,
          pendente: ['identidade', 'atributos_e_escolhas', 'marcos_e_recursos', 'inventario', 'cartoes', 'automacoes', 'prova_nativa']};
}
function r53NovaFichaProgressaoPrevia(ss, contexto) { return r53NovaPerfilPrevia_(ss, contexto, r53NovaProgPerfil_()); }
function r53NovaFichaProgressaoAplicar(ss, contexto, assinatura) {
  return r53NovaPerfilAplicar_(ss, contexto, assinatura, r53NovaProgPerfil_());
}
