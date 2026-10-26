/**
 * Medição de desempenho (25/10/2026). Colar só numa CÓPIA de teste, como arquivo
 * próprio, e executar pelo editor. Não grava nada na planilha.
 *
 * medirVazio: o custo fixo de qualquer execução (o Google carregar o projeto).
 * medirModulo: abrir o módulo como o r53Modulo_ instalado, e abrir o mesmo
 * módulo sem as tabelas que só a montagem usa (DADOS_R53, MONTAGENS, catálogo
 * e ANALISE), que é a opção 3. "rodar escopo global" é o que a opção 2 corta.
 */
function medirVazio() {
  console.log('MEDIR vazio');
}

var MEDIR_SO_MONTAGEM_ = /^var (VALORES_R53_(DADOS|ANALISE|MONTAGENS|CATALOGO)_\d+_|ABAS_R53_(MONTAGENS|DADOS|CATALOGO)_|ABAS_DA_ANALISE|FONTES_DA_ANALISE_) = /;

/** Troca cada tabela da montagem por null; o juntarAbas_/juntarValores_ ignora null. */
function medirSemMontagem_(code) {
  var partes = [], i = 0, cortados = 0;
  var re = /\nvar ([A-Z0-9_]+) = /g, m;
  while ((m = re.exec(code))) {
    if (!MEDIR_SO_MONTAGEM_.test(m[0].slice(1))) continue;
    var fim = code.indexOf('\nif (typeof juntar', m.index);
    if (fim < 0) continue;
    partes.push(code.slice(i, m.index + 1), 'var ' + m[1] + ' = null;');
    i = fim; cortados++;
    re.lastIndex = fim;
  }
  partes.push(code.slice(i));
  return {code: partes.join(''), cortados: cortados};
}

function medirModulo() {
  var marcas = [], t = Date.now();
  var marca = function (nome) { var a = Date.now(); marcas.push(nome + ' ' + (a - t) + ' ms'); t = a; };
  var b64 = [R53_CODIGO_0_, R53_CODIGO_1_, R53_CODIGO_2_, R53_CODIGO_3_, R53_CODIGO_4_].join('');
  marca('juntar base64');
  var code = Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(b64), 'application/gzip')).getDataAsString('UTF-8');
  marca('descompactar (' + Math.round(code.length / 1048576 * 10) / 10 + ' MB)');
  Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, code, Utilities.Charset.UTF_8);
  marca('hash');
  var corrigido = typeof r53CorrecaoCaminho_ === 'function'
    ? r53CorrecaoCaminho_(r53CorrecaoFila_(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code)))) : code;
  marca('correções de texto');
  var f = new Function(corrigido);
  marca('compilar inteiro');
  var mod = f();
  marca('rodar escopo global inteiro');
  var abas = mod.__estado().abas.length;
  var leve = medirSemMontagem_(corrigido);
  marca('cortar a montagem (' + leve.cortados + ' tabelas, ' + Math.round(leve.code.length / 1048576 * 10) / 10 + ' MB)');
  var f2 = new Function(leve.code);
  marca('compilar sem a montagem');
  var mod2 = f2();
  marca('rodar escopo global sem a montagem');
  console.log('MEDIR módulo · abas ' + abas + ' → ' + mod2.__estado().abas.length + '\n' + marcas.join('\n'));
}

/**
 * As edições que hoje estouram os 30 s, sem o limite (pelo editor são 6 min).
 * A primeira edição paga abrir o módulo; as seguintes já o encontram aberto.
 */
function medirEdicoes() {
  var ss = SpreadsheetApp.getActive(), ficha = ss.getSheetByName('FICHA'), out = [];
  var editar = function (a1, valor, antigo) {
    var r = ficha.getRange(a1);
    r.setValue(valor);
    SpreadsheetApp.flush();
    var t = Date.now();
    onEdit({range: r, value: String(valor), oldValue: antigo, source: ss});
    SpreadsheetApp.flush();
    out.push(a1 + ' = ' + valor + ': ' + (Date.now() - t) + ' ms');
  };
  editar('AN11', 3000, '0');
  editar('AN11', 6000, '3000');
  editar('AM26', -3, undefined);
  editar('AM26', -2, undefined);
  console.log('MEDIR edições\n' + out.join('\n'));
}

/** Quanto custa cada ida à planilha: leitura solta, leitura que espera o recálculo, gravação. */
function medirLeituras() {
  var ss = SpreadsheetApp.getActive(), f = ss.getSheetByName('FICHA'), d = ss.getSheetByName('DADOS'), out = [], t;
  var m = function (nome, fn) { t = Date.now(); fn(); out.push(nome + ': ' + (Date.now() - t) + ' ms'); };
  m('ler 1 célula', function () { f.getRange('A1').getValue(); });
  m('ler outra célula', function () { f.getRange('B2').getValue(); });
  m('ler a DADOS inteira', function () { d.getDataRange().getValues(); });
  m('ler a FICHA inteira', function () { f.getDataRange().getValues(); });
  m('gravar célula solta e ler', function () { f.getRange('AX1').setValue('x'); f.getRange('A1').getValue(); });
  m('gravar XP e ler', function () { f.getRange('AN11').setValue(1234); f.getRange('A1').getValue(); });
  m('ler de novo, nada pendente', function () { f.getRange('B2').getValue(); });
  m('gravar Caminho e ler', function () { f.getRange('D11').setValue('Bastião'); f.getRange('A1').getValue(); });
  m('gravar Caminho de volta e ler', function () { f.getRange('D11').setValue('Emanador'); f.getRange('A1').getValue(); });
  m('apagar a célula solta e gravar', function () { f.getRange('AX1').clearContent(); SpreadsheetApp.flush(); });
  console.log('MEDIR leituras\n' + out.join('\n'));
}

/** Ler a DADOS custa pelo tamanho da faixa ou pelo primeiro toque na aba? */
function medirFatias() {
  var ss = SpreadsheetApp.getActive(), f = ss.getSheetByName('FICHA'), d = ss.getSheetByName('DADOS'), out = [], t;
  var m = function (nome, fn) { t = Date.now(); fn(); out.push(nome + ': ' + (Date.now() - t) + ' ms'); };
  m('FICHA AM26 (primeiro toque)', function () { f.getRange('AM26').getValue(); });
  m('DADOS A1', function () { d.getRange('A1').getValue(); });
  m('DADOS AQ4:AS40', function () { d.getRange('AQ4:AS40').getValues(); });
  m('DADOS inteira', function () { d.getDataRange().getValues(); });
  m('DADOS inteira de novo', function () { d.getDataRange().getValues(); });
  m('FICHA D20:AM40', function () { f.getRange('D20:AM40').getValues(); });
  m('FICHA inteira', function () { f.getDataRange().getValues(); });
  m('FICHA inteira, só valores exibidos', function () { f.getDataRange().getDisplayValues(); });
  var ev = ss.getSheetByName('R53_EVENTOS');
  if (ev) m('R53_EVENTOS 654x2', function () { ev.getRange(1, 1, 654, 2).getValues(); });
  m('DADOS getDataRange sem ler', function () { d.getDataRange(); });
  m('DADOS getLastRow', function () { d.getLastRow(); });
  console.log('MEDIR fatias\n' + out.join('\n'));
}

/** Abrir o módulo instalado, do jeito que cada edição comum abre (antes e depois do pacote leve). */
function medirAbrirModulo() {
  var t = Date.now();
  R53_MODULO_ = null;
  var abas = r53Modulo_().__estado().abas.length;
  console.log('MEDIR abrir o módulo: ' + (Date.now() - t) + ' ms · ' + abas + ' abas no molde');
}
