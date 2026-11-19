 var ajustesDescanso = [
  [
    "    var pct = PE_DO_DESCANSO_CURTO_[d.propicio ? 0 : fim.exaustao];",
    "    var pct = d.propicio && s.recuperacaoAbundante ? 40 : PE_DO_DESCANSO_CURTO_[d.propicio ? 0 : fim.exaustao];"
  ],
  [
    "  if (vidaMax > 0) fim.vida = d.propicio ? vidaMax : Math.max(fim.vida, metade(vidaMax));",
    "  if (vidaMax > 0) {\n    if (!s.exaurido) {\n      fim.vida = d.propicio ? vidaMax : Math.max(fim.vida, metade(vidaMax));\n    } else if (d.propicio) {\n      var ganhoVida = Math.max(1, Math.floor(vidaMax / 4));\n      fim.vida = Math.max(fim.vida, Math.min(vidaMax, fim.vida + ganhoVida));\n    }\n  }"
  ],
  [
    "  var lidas = ['vida_max', 'energia_max', 'integridade_max'].concat(Object.keys(onde).map(function (k) { return onde[k]; }))",
    "  var campos = ['vida_max', 'energia_max', 'integridade_max', 'origem', 'marcante', 'menor 1', 'menor 2'];\n  var lidas = campos.concat(Object.keys(onde).map(function (k) { return onde[k]; }))"
  ],
  [
    "  var le = function (k) { var c = cel_(idx, k); return c ? Number(v[c]) || 0 : 0; };",
    "  var valor = function (k) { return v[cel_(idx, k)]; };\n  var le = function (k) { return Number(valor(k)) || 0; };"
  ],
  [
    "  var fim = contaDoDescanso_(tipo, antes);",
    "  var corpo = valor('marcante');\n  var abundante = valor('menor 1') === 'Recuperação Abundante' || valor('menor 2') === 'Recuperação Abundante';\n  if (corpo === 'Corpo Exaurido' || abundante) {\n    // A publicada com corpo do livro dispensa outra leitura; custom e corpo próprio dependem da DADOS_CUSTOM.\n    var publicado = valor('origem') === 'Restrição Celestial · Restrição corporal' &&\n      ['Corpo Debilitado', 'Corpo Quebradiço', 'Corpo Exaurido'].indexOf(corpo) >= 0;\n    var custom = publicado ? null : SpreadsheetApp.getActive().getSheetByName('DADOS_CUSTOM');\n    var regras = custom ? custom.getRange(126, 2, 2, 1).getValues() : [[publicado], [publicado]];\n    var corporal = regras[0][0] === true;\n    antes.exaurido = corporal && corpo === 'Corpo Exaurido';\n    antes.recuperacaoAbundante = corporal && abundante && regras[1][0] === true;\n  }\n  var fim = contaDoDescanso_(tipo, antes);"
  ],
  [
    "  var tipo = String(e.range.getValue());",
    "  // 04/11/2026: o evento já traz a escolha; ler a célula custava quase 5 s dos 30 do gatilho.\n  var tipo = String(e.value !== undefined ? e.value : e.range.getValue());"
  ]
];
 ajustesDescanso.forEach(function(par) {
   if (code.split(par[0]).length !== 2) throw new Error('Trecho de descanso divergente.');
   code = code.replace(par[0], function() { return par[1]; });
 });
 [["  var campos = ['vida_max', 'energia_max', 'integridade_max', 'origem', 'marcante', 'menor 1', 'menor 2'];", "  var campos = ['descanso', 'vida_max', 'energia_max', 'integridade_max', 'origem', 'marcante', 'menor 1', 'menor 2'];"], ["  var v = lerCelulas_(ficha, lidas);\n  var valor = function (k) { return v[cel_(idx, k)]; };", "  var v = lerCelulas_(ficha, lidas);\n  // Um evento atrasado não pode reaplicar um descanso já concluído ou substituir outra escolha.\n  // O menu vem na mesma leitura dos recursos, sem uma chamada extra ao Sheets.\n  if (String(v[cd]) !== tipo) return false;\n  var valor = function (k) { return v[cel_(idx, k)]; };"]].forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Guarda QA divergente");code=code.replace(p[0],function(){return p[1];});});
 var socorroDescanso=[["function descansar_(e, idx) {", "function r53DescansarComQueda(tipo, queda, jaConvertido) {\n  var idx = indiceEstatico_();\n  var ficha = SpreadsheetApp.getActive().getSheetByName('FICHA');\n  return descansar_({range: ficha.getRange(cel_(idx, 'descanso')), value: tipo}, idx, queda, jaConvertido);\n}\n\nfunction descansar_(e, idx, quedaConfirmada, jaConvertido) {"], ["  if (String(v[cd]) !== tipo) return false;", "  if (!quedaConfirmada && String(v[cd]) !== tipo) return false;\n  if (quedaConfirmada && v[cd] !== SEM_DESCANSO_) throw Error('Aguarde o menu de descanso voltar a Escolha o descanso.');\n  var queda = DESCANSOS_[tipo].longo && typeof r53SocorroLer_ === 'function'\n    ? r53SocorroLer_(SpreadsheetApp.getActive()) : null;\n  var quedaAtiva = queda && r53SocorroAtivo_(queda);\n  if (quedaConfirmada && (!quedaAtiva || JSON.stringify(quedaConfirmada) !== JSON.stringify(queda))) {\n    throw Error('O registro da queda mudou. Confira SOCORRO e tente novamente.');\n  }\n  if (quedaAtiva && !quedaConfirmada) {\n    e.range.setValue(SEM_DESCANSO_);\n    SpreadsheetApp.getActive().toast('Use Recursos → Descanso longo com queda ativa.', 'Queda em andamento', 8);\n    return false;\n  }"], ["  var fim = contaDoDescanso_(tipo, antes);", "  if (quedaAtiva) {\n    var recursos = antes;\n    var conversao = r53SocorroResolverConversao_(queda, antes.vida, antes.vidaMax, jaConvertido);\n    if (conversao.convertido) recursos = Object.assign({}, antes, {vida: antes.vida + conversao.convertido});\n    var recuperados = contaDoDescanso_(tipo, recursos);\n    var encerrou = recuperados.vida >= 1 &&\n      (queda.status !== 'Derrotado' || antes.integMax === 0 || recuperados.integ >= 1);\n    var textoQueda = textoDoDescanso_(tipo, antes, recuperados) + (encerrou\n      ? ' · queda encerrada; Sequelas removidas após a recuperação'\n      : ' · queda permanece ativa; confira a recuperação com o mestre');\n    var alteracoes = [[cd, SEM_DESCANSO_], [cel_(idx, 'último descanso'), textoQueda]];\n    Object.keys(onde).forEach(function (k) {\n      if (recuperados[k] !== antes[k]) alteracoes.push([cel_(idx, onde[k]), recuperados[k]]);\n    });\n    caixinhas.forEach(function (c) { if (v[c] === true) alteracoes.push([c, false]); });\n    if (cExtras && extras) alteracoes.push([cExtras, 0]);\n    var registro = encerrou ? Object.assign({}, conversao.estado, {status: 'Encerrado no descanso'}) : conversao.estado;\n    r53SocorroGravar_(SpreadsheetApp.getActive(), registro, null, null, false,\n      alteracoes.filter(function (par) { return par[0]; }).map(function (par) {\n        var pos = limitesA1_(par[0]);\n        return {updateCells: {start: {sheetId: ficha.getSheetId(), rowIndex: pos.l1 - 1, columnIndex: pos.c1 - 1},\n          rows: [{values: [r53SocorroCelula_(par[1])]}], fields: 'userEnteredValue'}};\n      }));\n    SpreadsheetApp.getActive().toast(textoQueda, 'Descanso', 8);\n    return true;\n  }\n  var fim = contaDoDescanso_(tipo, antes);"]];
 socorroDescanso.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Descanso SOCORRO: âncora divergente");code=code.replace(p[0],function(){return p[1];});});
 if(code.split(",__estado:function()").length!==2)throw Error("Descanso SOCORRO: exportação divergente");
 code=code.replace(",__estado:function()",",r53DescansarComQueda:r53DescansarComQueda,__estado:function()");
