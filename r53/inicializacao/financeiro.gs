/** Inicialização FINANCEIRA de uma cópia nova. Não inicializa o personagem inteiro.
 * Sem onOpen/onEdit, Drive, rede, criação de gatilhos ou emissão de carteira.
 * O contexto vem do criador confiável da cópia; não é prova fornecida pelo browser.
 * Não instalar nas oficiais. O consumidor continua bloqueado para criação.
 */
var R53_NOVA_FIN_ = {
  versao: 1,
  diario: 'r53_nova_ficha_financeiro_v1',
  escritasPorExecucao: 4,
  orcamentoMs: 210000,
  oficiais: ['1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k', '1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw'],
  propriedadesDocumento: ['salario_extrato', 'salario_trocas', 'salario_correcao_nome', 'salario_proximo'],
  propriedadesScript: ['salario_edicao'],
  formulas: [ ['DADOS_SALARIOS', 'Q2:Q8'], ['DADOS_SALARIOS', 'P11'], ['DADOS_SALARIOS', 'AA2'],
    ['FICHA PESSOAL', 'W86'], ['CONFIGURAÇÃO', 'O38'], ['CARTEIRA', 'AH3'], ['FICHA', 'AN11'] ]
};

function r53NovaFinErro_(texto) { throw new Error('Nova cópia · ' + texto); }
function r53NovaFinCanon_(v) {
  if (Object.prototype.toString.call(v) === '[object Date]') return JSON.stringify({data: v.toISOString()});
  if (v === null || typeof v !== 'object') return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(r53NovaFinCanon_).join(',') + ']';
  return '{' + Object.keys(v).sort().map(function(k) { return JSON.stringify(k) + ':' + r53NovaFinCanon_(v[k]); }).join(',') + '}';
}
function r53NovaFinHash_(v) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, r53NovaFinCanon_(v), Utilities.Charset.UTF_8)
    .map(function(b) { return ('0' + ((b + 256) % 256).toString(16)).slice(-2); }).join('');
}
function r53NovaDiarioSalvar_(props, chave, diario) {
  var texto = JSON.stringify(diario);
  // Margem conservadora dentro do limite por valor do Apps Script. Recusar
  // antes da primeira escrita, sem aceitar um diário que só cabe na VM.
  if (Utilities.newBlob(texto).getBytes().length > 9000)
    r53NovaFinErro_('diário excede o limite; dividir o domínio antes de inicializar.');
  props.setProperty(chave, texto);
}
function r53NovaFinContexto_(ss, contexto) {
  if (!contexto || contexto.versao !== 1 || !/^[a-zA-Z0-9_-]{16,100}$/.test(contexto.operacao || '') ||
      typeof contexto.destino !== 'string' || typeof contexto.modelo !== 'string' || !contexto.modelo ||
      contexto.destino !== ss.getId() || contexto.destino === contexto.modelo ||
      !Array.isArray(contexto.arquivosRegistrados) || contexto.arquivosRegistrados.indexOf(contexto.destino) >= 0 ||
      R53_NOVA_FIN_.oficiais.indexOf(contexto.destino) >= 0 || contexto.responsavelConfirmado !== true ||
      contexto.copiaNovaConfirmada !== true) r53NovaFinErro_('alvo não comprovado como cópia nova.');
  var ativo = SpreadsheetApp.getActive();
  if (!ativo || ativo.getId() !== ss.getId()) r53NovaFinErro_('o documento vinculado não é a cópia indicada.');
  // Não aceitar estado legado desconhecido: este módulo só suporta salário por fórmula.
  if (typeof SALARIO_ === 'undefined' || SALARIO_.formula !== true) r53NovaFinErro_('salário por fórmula não confirmado.');
  return {versao: 1, operacao: contexto.operacao, destino: contexto.destino, modelo: contexto.modelo};
}
function r53NovaFinProps_(op) {
  return op.escopo === 'documento' ? PropertiesService.getDocumentProperties() : PropertiesService.getScriptProperties();
}
function r53NovaFinFaixa_(ss, op) {
  var sh = ss.getSheetByName(op.aba);
  if (!sh) r53NovaFinErro_('falta uma aba do contrato financeiro.');
  return sh.getRange(op.faixa);
}
function r53NovaFinOperacoes_(ss) {
  var ops = [];
  [['EXTRATO', 'C'], ['SALÁRIOS', 'L'], ['DADOS_SALARIOS', 'J']].forEach(function(x) {
    var sh = ss.getSheetByName(x[0]), n = sh && sh.getMaxRows();
    if (!Number.isInteger(n) || n < 2 || n > 5000) r53NovaFinErro_('grade financeira fora do limite; nada foi limpo.');
    ops.push({aba: x[0], faixa: 'A2:' + x[1] + n, tipo: 'limpar', notas: true, formulasLivres: false});
  });
  // Quatro entradas por missão; a quinta coluna é XP calculado e não entra.
  ['AW15:AZ87', 'BC15:BF87', 'BI15:BL87', 'BO15:BR87'].forEach(function(a) {
    ops.push({aba: 'FICHA PESSOAL', faixa: a, tipo: 'limpar', notas: true, formulasLivres: false});
  });
  [['DADOS_SALARIOS', 'N2'], ['FICHA PESSOAL', 'O86'], ['FICHA PESSOAL', 'BI11'], ['FICHA PESSOAL', 'BO11']].forEach(function(x) {
    ops.push({aba: x[0], faixa: x[1], tipo: 'limpar', notas: false, formulasLivres: x[1] === 'O86'});
  });
  ops.push({aba: 'DADOS_SALARIOS', faixa: 'L2', tipo: 'valor', valor: '{"versao":1,"graus":[]}', notas: false, formulasLivres: false});
  [['CONFIGURAÇÃO', 'O39'], ['CARTEIRA', 'AT3']].forEach(function(x) {
    ops.push({aba: x[0], faixa: x[1], tipo: 'valor', valor: false, notas: false, formulasLivres: false});
  });
  // Conteúdo e notas são chamadas separadas do Sheets. Cada uma recebe um passo
  // próprio para que uma queda entre elas seja retomável, sem aceitar edição alheia.
  var passos = [];
  ops.forEach(function(op) {
    passos.push({aba: op.aba, faixa: op.faixa, tipo: op.tipo, valor: op.valor,
                 formulasLivres: op.formulasLivres});
    if (op.notas) passos.push({aba: op.aba, faixa: op.faixa, tipo: 'notas'});
  });
  [['documento', R53_NOVA_FIN_.propriedadesDocumento], ['script', R53_NOVA_FIN_.propriedadesScript]].forEach(function(x) {
    x[1].forEach(function(k) { passos.push({tipo: 'propriedade', escopo: x[0], chave: k}); });
  });
  return passos;
}
function r53NovaFinLer_(ss, op) {
  if (op.tipo === 'propriedade') return r53NovaFinProps_(op).getProperty(op.chave);
  var r = r53NovaFinFaixa_(ss, op);
  if (op.tipo === 'notas' || op.tipo === 'nota' || op.tipo === 'notas_matriz') return r.getNotes();
  var formulas = r.getFormulas(), valores = r.getValues();
  // Apenas equivalências exatas publicadas pelo produtor para estes alvos.
  // Não normalizar fórmulas desconhecidas nem resultados calculados.
  formulas = formulas.map(function(l, i) { return l.map(function(f, k) {
    var lista = op.tipo === 'formula' ? op.formulasEquivalentes :
      op.tipo === 'matriz' && op.formulasEquivalentes && op.formulasEquivalentes[i] ? op.formulasEquivalentes[i][k] : null;
    return f && lista && lista.indexOf(f) >= 0 ? (op.tipo === 'formula' ? op.formula : op.valores[i][k]) : f;
  }); });
  // Resultado em cache pode mudar após limpar o livro. Identificar a fórmula,
  // não seu resultado transitório, evita uma falsa edição concorrente em O86.
  return {valores: valores.map(function(l, i) { return l.map(function(v, k) {
    if (formulas[i][k]) return null;
    if (v !== null && typeof v === 'object' && Object.prototype.toString.call(v) !== '[object Date]')
      r53NovaFinErro_('imagem ou valor de célula não suportado; nada será limpo.');
    if (typeof v === 'number' && !isFinite(v)) r53NovaFinErro_('número de célula inválido.');
    return v;
  }); }),
          formulas: formulas};
}
function r53NovaFinDepois_(atual, op) {
  if (op.tipo === 'propriedade') return null;
  var vazio = function(m, v) { return m.map(function(l) { return l.map(function() { return v; }); }); };
  if (op.tipo === 'notas') return vazio(atual, '');
  if (op.tipo === 'nota') return vazio(atual, op.valor);
  if (op.tipo === 'notas_matriz') return op.notas;
  if (op.tipo === 'formula') return {valores: vazio(atual.valores, null), formulas: vazio(atual.formulas, op.formula)};
  if (op.tipo === 'matriz') return {
    valores: op.valores.map(function(l) { return l.map(function(v) { return typeof v === 'string' && v.charAt(0) === '=' ? null : v; }); }),
    formulas: op.valores.map(function(l) { return l.map(function(v) { return typeof v === 'string' && v.charAt(0) === '=' ? v : ''; }); })
  };
  return {valores: vazio(atual.valores, op.tipo === 'valor' ? op.valor : ''), formulas: vazio(atual.formulas, '')};
}
function r53NovaFinFormulas_() {
  if (!SALARIO_.f || !Array.isArray(SALARIO_.f.aux) || SALARIO_.f.aux.length !== 8)
    r53NovaFinErro_('contrato de fórmulas não reconhecido.');
  return [SALARIO_.f.aux.slice(1).map(function(l) { return [l[1]]; }),
          [[SALARIO_.f.tabela]], [[SALARIO_.f.ultimos]], [[SALARIO_.f.total]],
          [[SALARIO_.f.emissao]], [[SALARIO_.f.carteira]], [['=DADOS!$CZ$47']]];
}
function r53NovaFinFormulaCanon_(s) {
  // O Google remove essas aspas opcionais ao salvar. Não retirar espaços,
  // referências absolutas, operadores ou aspas de nomes com acentos/espaços.
  return s.replace(/'DADOS_SALARIOS'!/g, 'DADOS_SALARIOS!');
}
function r53NovaFinPreservados_(ss) {
  var esperadas = r53NovaFinFormulas_();
  var saida = R53_NOVA_FIN_.formulas.map(function(x, i) {
    var sh = ss.getSheetByName(x[0]);
    if (!sh) r53NovaFinErro_('falta uma aba de fórmulas.');
    var f = sh.getRange(x[1]).getFormulas();
    if (!f.length || f.some(function(l) { return l.some(function(c) { return typeof c !== 'string' || c.charAt(0) !== '='; }); }))
      r53NovaFinErro_('falta uma fórmula financeira protegida.');
    if (f.length !== esperadas[i].length || f.some(function(l, j) {
      return l.length !== esperadas[i][j].length || l.some(function(c, k) {
        var e = esperadas[i][j][k];
        return typeof e !== 'string' || r53NovaFinFormulaCanon_(c) !== r53NovaFinFormulaCanon_(e);
      });
    })) r53NovaFinErro_('fórmula financeira fora do contrato; modelo não suportado.');
    return [x[0], x[1], f];
  });
  // A configuração da campanha e o nível não são parâmetros deste domínio.
  saida.push(['nivel', r53NovaFinLer_(ss, {aba: 'FICHA', faixa: 'AH11'})]);
  saida.push(['campanha', r53NovaFinLer_(ss, {aba: 'CONFIGURAÇÃO', faixa: 'E46:G46'})]);
  return r53NovaFinHash_(saida);
}
function r53NovaFinPerfil_() {
  return {nome: 'financeiro', diario: R53_NOVA_FIN_.diario, limites: R53_NOVA_FIN_,
          operacoes: r53NovaFinOperacoes_, preservados: r53NovaFinPreservados_,
          pendente: ['identidade', 'progressao', 'inventario', 'cartoes', 'automacoes', 'prova_nativa']};
}
function r53NovaFinMontar_(ss, contexto, perfil) {
  perfil = perfil || r53NovaFinPerfil_();
  var vinculo = r53NovaFinContexto_(ss, contexto), ops = perfil.operacoes(ss, contexto), mudancas = 0;
  var passos = ops.map(function(op) {
    var atual = r53NovaFinLer_(ss, op);
    if (atual && atual.formulas && !op.formulasLivres && atual.formulas.some(function(l) { return l.some(Boolean); }))
      r53NovaFinErro_('fórmula inesperada em entrada a inicializar; modelo não suportado.');
    var antes = r53NovaFinHash_(atual), depois = r53NovaFinHash_(r53NovaFinDepois_(atual, op));
    if (antes !== depois) mudancas++;
    return {antes: antes, depois: depois};
  });
  return {vinculo: vinculo, layout: r53NovaFinHash_(ops), preservados: perfil.preservados(ss),
          passos: passos, alteracoes: mudancas};
}
/** Prévia sem gravação. O hash não inclui valores pessoais no retorno. */
function r53NovaFichaFinanceiroPrevia(ss, contexto) {
  return r53NovaPerfilPrevia_(ss, contexto, r53NovaFinPerfil_());
}
/** Executor interno. O perfil vem do código do produtor, nunca do navegador. */
function r53NovaPerfilPrevia_(ss, contexto, perfil) {
  r53NovaFinContexto_(ss, contexto);
  if (perfil.precondicao) perfil.precondicao(ss, contexto);
  var dp = PropertiesService.getDocumentProperties();
  if (dp.getProperty(perfil.diario)) r53NovaFinErro_('já existe uma inicialização; retome a mesma operação.');
  var plano = r53NovaFinMontar_(ss, contexto, perfil);
  return {versao: 1, operacao: plano.vinculo.operacao, destino: plano.vinculo.destino,
          assinatura: r53NovaFinHash_(plano), alteracoes: plano.alteracoes,
          dominio: perfil.nome, criacaoDisponivel: false};
}
/** Aplica/retoma sob trava; nunca sobrescreve estado diferente do antes/depois previsto.
 * Falha/timeout deixa diário incompleto. Uma cópia assim não pode ser cadastrada.
 */
function r53NovaFichaFinanceiroAplicar(ss, contexto, assinatura) {
  return r53NovaPerfilAplicar_(ss, contexto, assinatura, r53NovaFinPerfil_());
}
function r53NovaPerfilAplicar_(ss, contexto, assinatura, perfil) {
  var inicio = Date.now();
  var lock = LockService.getDocumentLock();
  if (!lock.tryLock(1500)) r53NovaFinErro_('outra operação em andamento.');
  try {
    var dp = PropertiesService.getDocumentProperties();
    var vinculo = r53NovaFinContexto_(ss, contexto);
    if (perfil.precondicao) perfil.precondicao(ss, contexto);
    var ops = perfil.operacoes(ss, contexto);
    var raw = dp.getProperty(perfil.diario), j, novo = !raw;
    if (raw) {
      try { j = JSON.parse(raw); } catch (err) { r53NovaFinErro_('diário inválido; revisão manual necessária.'); }
      if (!j || !j.plano || !Array.isArray(j.plano.passos) || j.plano.passos.length !== ops.length ||
          typeof j.concluido !== 'boolean' || j.assinatura !== r53NovaFinHash_(j.plano))
        r53NovaFinErro_('diário inválido; revisão manual necessária.');
      if (j.assinatura !== assinatura || r53NovaFinCanon_(j.plano.vinculo) !== r53NovaFinCanon_(vinculo))
        r53NovaFinErro_('operação diferente da inicialização pendente.');
    } else {
      var plano = r53NovaFinMontar_(ss, contexto, perfil);
      if (typeof assinatura !== 'string' || assinatura !== r53NovaFinHash_(plano)) r53NovaFinErro_('a cópia mudou após a prévia.');
      j = {assinatura: assinatura, plano: plano, concluido: false};
      r53NovaDiarioSalvar_(dp, perfil.diario, j);
    }
    if (r53NovaFinHash_(ops) !== j.plano.layout || perfil.preservados(ss) !== j.plano.preservados)
      r53NovaFinErro_('estrutura, fórmula ou configuração mudou; revisão manual necessária.');
    // Validar TODOS os passos antes de retomar qualquer escrita.
    // Uma operação nova acabou de ler TODOS os estados para validar a prévia.
    // Não repetir essa leitura inteira antes das escritas; cada passo alterado
    // é relido antes de gravar e a conclusão exige conferência completa.
    var estados = novo ? j.plano.passos.map(function(p) { return p.antes; }) : ops.map(function(op, i) {
      var h = r53NovaFinHash_(r53NovaFinLer_(ss, op)), p = j.plano.passos[i];
      if (h !== p.antes && h !== p.depois) r53NovaFinErro_('dados editados durante a inicialização; nada será sobrescrito.');
      if (j.concluido && h !== p.depois) r53NovaFinErro_('a cópia já foi usada depois da inicialização.');
      return h;
    });
    var escritas = 0;
    var incompleto = function() {
      return {versao: 1, dominio: perfil.nome, concluido: false, retomar: true,
              operacao: vinculo.operacao, criacaoDisponivel: false};
    };
    for (var i = 0; i < ops.length; i++) {
      var op = ops[i], p = j.plano.passos[i];
      if (estados[i] === p.depois) continue;
      if (escritas >= perfil.limites.escritasPorExecucao || Date.now() - inicio >= perfil.limites.orcamentoMs)
        return incompleto();
      if (r53NovaFinHash_(r53NovaFinLer_(ss, op)) !== p.antes) r53NovaFinErro_('edição concorrente; operação interrompida.');
      if (op.tipo === 'propriedade') r53NovaFinProps_(op).deleteProperty(op.chave);
      else {
        var r = r53NovaFinFaixa_(ss, op);
        if (op.tipo === 'notas') r.clearNote();
        else if (op.tipo === 'nota') r.setNote(op.valor);
        else if (op.tipo === 'notas_matriz') r.setNotes(op.notas);
        else if (op.tipo === 'matriz') r.setValues(op.valores);
        else if (op.tipo === 'formula') r.setFormula(op.formula);
        else if (op.tipo === 'valor') r.setValue(op.valor);
        else r.clearContent();
      }
      SpreadsheetApp.flush();
      if (r53NovaFinHash_(r53NovaFinLer_(ss, op)) !== p.depois) r53NovaFinErro_('gravação não confirmada; revisão manual necessária.');
      escritas++;
    }
    // Reservar tempo para a conferência final. Na retomada sem escrita, todos
    // os passos já foram conferidos acima: não ler o livro inteiro duas vezes.
    if (Date.now() - inicio >= perfil.limites.orcamentoMs) return incompleto();
    SpreadsheetApp.flush();
    if (perfil.preservados(ss) !== j.plano.preservados ||
        ((novo || escritas > 0) && ops.some(function(op, i) { return r53NovaFinHash_(r53NovaFinLer_(ss, op)) !== j.plano.passos[i].depois; })))
      r53NovaFinErro_('pós-condição não confirmada; não cadastrar a cópia.');
    if (!j.concluido) {
      j.concluido = true; r53NovaDiarioSalvar_(dp, perfil.diario, j);
    }
    return {versao: 1, dominio: perfil.nome, concluido: true, criacaoDisponivel: false,
            operacao: vinculo.operacao, pendente: perfil.pendente.slice()};
  } finally { lock.releaseLock(); }
}
