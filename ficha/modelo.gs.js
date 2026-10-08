/**
 * Projeto M · a ficha nasce aqui dentro.
 *
 * Rode UMA função: construir(). Ela apaga o que existir e monta as abas
 * do zero, nativas: cor, fonte, mesclagem, altura de linha em pixel, menu
 * suspenso, caixa de seleção, imagem no tamanho certo e cor de estado.
 *
 * Por que não é mais um .xlsx importado: a conversão quebrava seis coisas
 * diferentes, e a pior delas era invisível — imagem vinda de importação não
 * aparece para a API, então nem dava para consertar o tamanho dela.
 */

/**
 * AS FILEIRAS QUE SÃO CÓPIA. A FICHA AMALDIÇOADA tem treze fileiras de cartas de feitiço iguais. No ABAS só a primeira
 * vem escrita; de cada cópia vem só o que é diferente dela. Aqui, quando o script carrega, cada cópia volta a ser
 * escrita por extenso: o resto do script (a montagem, a troca de paleta, a régua) lê o ABAS inteiro, como sempre leu.
 * Cada entrada de `copias` é [primeira linha, última linha, [a linha onde cada cópia começa]]. A mesma conta mora no
 * ficha/emitir_gs.py (`expandir`), e o gerador para se a cópia expandida não devolver a aba inteira.
 */
function expandirCopias_(spec) {
  if (!(spec.copias || []).length || spec.copias_feitas) return spec;
  var A1 = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/;
  var linhas = function (a1) { var m = A1.exec(a1.replace(/\$/g, '')); return [Number(m[2]), Number(m[4] || m[2])]; };
  var desce = function (a1, dl) {
    var m = A1.exec(a1);
    return m[1] + (Number(m[2]) + dl) + (m[3] ? ':' + m[3] + (Number(m[4]) + dl) : '');
  };
  var escritas = {};
  spec.vals.forEach(function (t) { escritas[t[0] + ',' + t[1]] = true; });
  var molde = { vals: spec.vals.slice(), fundos: spec.fundos.slice(), merges: spec.merges.slice(),
                bordas: (spec.bordas || []).map(function (b) { return b[3].slice(); }),
                dv: (spec.dv || []).slice(), caixas: (spec.caixas || []).slice(), formatos: (spec.formatos || []).slice() };
  var temDv = {}, temFmt = {};
  molde.dv.forEach(function (d) { temDv[d[0]] = true; });
  molde.formatos.forEach(function (f) { temFmt[f[0]] = true; });
  spec.copias.forEach(function (k) {
    var r1 = k[0], r2 = k[1];
    var dentro = function (l) { return l >= r1 && l <= r2; };
    var noMolde = function (a1) { var l = linhas(a1); return dentro(l[0]) && dentro(l[1]); };
    k[2].forEach(function (d) {
      var dl = d - r1;
      molde.vals.forEach(function (t) {
        if (dentro(t[0]) && !escritas[(t[0] + dl) + ',' + t[1]]) spec.vals.push([t[0] + dl, t[1]].concat(t.slice(2)));
      });
      molde.fundos.forEach(function (f) { if (dentro(f[0])) spec.fundos.push([f[0] + dl].concat(f.slice(1))); });
      molde.merges.forEach(function (m) { if (dentro(m[0]) && dentro(m[2])) spec.merges.push([m[0] + dl, m[1], m[2] + dl, m[3]]); });
      molde.bordas.forEach(function (lista, i) {
        lista.forEach(function (a1) { if (noMolde(a1)) spec.bordas[i][3].push(desce(a1, dl)); });
      });
      molde.dv.forEach(function (x) { if (noMolde(x[0]) && !temDv[desce(x[0], dl)]) spec.dv.push([desce(x[0], dl), x[1]]); });
      molde.caixas.forEach(function (c) { if (dentro(c[1]) && dentro(c[1] + c[2] - 1)) spec.caixas.push([c[0], c[1] + dl, c[2]]); });
      molde.formatos.forEach(function (f) { if (noMolde(f[0]) && !temFmt[desce(f[0], dl)]) spec.formatos.push([desce(f[0], dl), f[1]]); });
    });
  });
  spec.copias_feitas = true;
  return spec;
}
ABAS.forEach(expandirCopias_);

/**
 * AS ABAS QUE MORAM EM OUTRO ARQUIVO (06/10/2026). A INVOCAÇÕES e a DADOS_INVOC não cabem neste arquivo, e vêm no
 * Invocacoes.gs, que só declara a lista delas (ABAS_DA_INVOCACAO). Esta função põe cada uma no ABAS, depois da aba que
 * ela nomeia em `depois`, com as fileiras copiadas já por extenso. O Apps Script não promete a ordem em que carrega os
 * arquivos: quem carregar por último chama a função (o Invocacoes.gs, no fim dele; ou este arquivo, logo abaixo), e a
 * aba que já entrou não entra de novo. Sem o Invocacoes.gs no projeto, a ficha é montada sem as duas abas.
 */
function juntarAbas_(extras) {
  if (typeof ABAS === 'undefined' || !ABAS || !extras) return;
  extras.forEach(function (spec) {
    if (ABAS.some(function (s) { return s.nome === spec.nome; })) return;
    expandirCopias_(spec);
    var i = -1;
    ABAS.forEach(function (s, k) { if (s.nome === spec.depois) i = k; });
    if (i < 0) ABAS.push(spec); else ABAS.splice(i + 1, 0, spec);
  });
}
if (typeof ABAS_DA_INVOCACAO !== 'undefined' && ABAS_DA_INVOCACAO) juntarAbas_(ABAS_DA_INVOCACAO);

var ETAPAS_ = [];      // o tempo de cada etapa da última montagem, para o registro

/**
 * O relógio da montagem. Cada etapa que termina vai para o registro de execução NA HORA, com o tempo dela: se o
 * Apps Script cortar a função aos seis minutos, o registro mostra em que etapa ela estava e quanto cada uma levou.
 * Até 01/10/2026 o construir() só escrevia no fim, e uma montagem que estourava o tempo não deixava pista nenhuma.
 */
function relogio_() {
  var t0 = new Date().getTime(), ant = t0;
  ETAPAS_ = [];
  return {
    etapa: function (nome) {
      var agora = new Date().getTime(), seg = Math.round((agora - ant) / 100) / 10;
      ant = agora;
      ETAPAS_.push(nome + ' ' + seg + 's');
      Logger.log(Math.round((agora - t0) / 1000) + 's · ' + nome + ' (' + seg + 's)');
    },
    passou: function () { return new Date().getTime() - t0; }
  };
}

// Se a montagem das abas passar disto, o acabamento fica para a função acabar(): seis minutos é o teto do Apps
// Script, e o acabamento (cor de estado, notas, saltos, caixa da paleta) pode ser refeito sozinho, a montagem não.
// 01/10/2026: o Mizuki mediu o acabamento em 90 s (as travas sozinhas levavam 83), e o teto desceu de 270 para 250 s.
// 07/10/2026: sem as travas o acabamento levou 17,4 s no registro dele, num dia de Sheets lento (cor de estado 3,5,
// notas 1,3, notas da ficha pessoal 4,7, saltos 6,4, caixa da paleta 1,5), e o teto sobe para 300 s.
var TETO_DA_MONTAGEM_ = 300000;

// 07/10/2026, a INVOCAÇÕES com doze fichas: a montagem das abas sozinha já não cabe com folga nos seis minutos. O
// Mizuki mediu 288 s com uma ficha (187 s de abas, 101 s de menus e acabamento), e as doze trazem mais de dez vezes as
// células dela. A montagem agora PARA SOZINHA antes de começar uma aba que pode não acabar, guarda em que aba parou e
// pede o continuar(), que segue dali. Uma aba que o Apps Script corta no meio não tem conserto (o grupo de linhas
// nasceria duas vezes), e por isso a conta é feita antes de começar, com folga.
//
// O custo de cada aba, pela medida dele em 06/10/2026 (segundos por mil células, contando a aba inteira, linhas vezes
// colunas): CARTEIRA 2,1 · FICHA 2,1 · FICHA AMALDIÇOADA 2,0 · INVOCAÇÕES 1,5 · FICHA PESSOAL 1,3 · e as ocultas, que
// não têm mesclagem nem borda, DADOS 0,52 · DADOS_AM 0,58 · DADOS_INVOC 0,53. A estimativa usa o pior de cada tipo com
// uns 15% a mais, e nenhuma aba começa se a estimativa dela passar do limite da execução, a não ser a primeira da vez.
// 07/10/2026, à noite, com as doze fichas e o Sheets lento (as abas criadas em 165 s, contra 63 s na véspera): a
// DADOS_INVOC levou 89,6 s (70.650 células: 1,27 ms cada, contra os 0,7 da estimativa), a DADOS_AM 35,4 s (26.316: 1,35) e
// os menus, que vêm depois da última aba e ninguém estimava, 35,1 s. A execução fechou em 304 s. A oculta passa a 1,4 ms
// por célula, e o limite desce de 300 para 270 s, para os menus caberem depois da última aba.
var MS_POR_CELULA_ = 2.4, MS_POR_CELULA_OCULTA_ = 1.4;
var LIMITE_DA_EXECUCAO_ = 270000;
var CHAVE_DA_MONTAGEM_ = 'montagem_parada';
var RETOMADA_ = null;       // o continuar() põe aqui a aba em que a montagem parou; o construir() começa do zero

function custoDaAba_(spec) {
  return spec.rows * spec.cols * (spec.oculta ? MS_POR_CELULA_OCULTA_ : MS_POR_CELULA_);
}

/**
 * Segue a montagem que o construir() parou para não estourar os seis minutos. Rode quando o registro pedir, quantas
 * vezes ele pedir: cada vez monta as abas que couberem, e a última faz os menus e o acabamento.
 */
function continuar() {
  var parada = PropertiesService.getDocumentProperties().getProperty(CHAVE_DA_MONTAGEM_);
  if (parada === null || !(Number(parada) > 0) || !(Number(parada) <= ABAS.length)) {
    throw new Error('não há montagem parada para continuar: rode construir() (ou acabar(), se só faltar o acabamento).');
  }
  RETOMADA_ = Number(parada);
  try {
    construir();
  } finally {
    RETOMADA_ = null;
  }
}

function construir() {
  var ss = SpreadsheetApp.getActive();
  var feito = [], rel = relogio_();
  var props = PropertiesService.getDocumentProperties();
  var de = RETOMADA_ === null ? 0 : RETOMADA_, parou = -1;

  // O idioma da planilha manda na pontuação de TODA fórmula que o script escreve, o setValues e
  // a regra de cor inclusive: numa planilha em português COUNTIF(a,b) vira #ERROR! e 0.25 não é
  // número. Foi o que o teste de 15/09/2026 mostrou, com as 104 fórmulas de vírgula quebradas.
  // A montagem roda em inglês, e no fim ela força pt_BR — não devolve o idioma de antes. Achado em
  // 18/09/2026: "o idioma de antes" supõe que a planilha já nasceu em português, e uma planilha
  // nova do Google Sheets nasce no idioma da conta de quem criou, não do produto. Restaurar
  // devolvia a mesma en_US que a montagem tinha acabado de ligar — a ficha é em português sempre,
  // então o fim é sempre pt_BR, mesmo se ela parar no meio.
  var idioma = ss.getSpreadsheetLocale();
  var falta = false;
  ss.setSpreadsheetLocale('en_US');
  try {
    var abas;
    if (de === 0) {
      // do zero: a montagem parada que houver deixa de valer
      props.deleteProperty(CHAVE_DA_MONTAGEM_);
      // uma aba de rascunho segura o lugar enquanto as antigas somem
      var velha = ss.getSheetByName('__montando__');
      if (velha) ss.deleteSheet(velha);        // sobra de uma execução que parou no meio
      var temp = ss.insertSheet('__montando__', 0);
      ss.getSheets().forEach(function (a) {
        if (a.getName() !== '__montando__') ss.deleteSheet(a);
      });

      // TODAS as abas nascem primeiro, vazias e já do tamanho certo, na ordem do ABAS. Só depois cada uma é
      // preenchida: a CARTEIRA cita a FICHA e a FICHA cita a DADOS, e fórmula gravada antes de a aba citada existir
      // (ou antes de ela ter a coluna citada) fica em #REF!. Até 01/10/2026 as fórmulas esperavam numa fila e eram
      // gravadas depois, em 144 chamadas; agora vão junto com os valores, numa gravação por aba.
      abas = ABAS.map(function (spec, i) { return criarAba_(ss, spec, i + 1); });
      ss.deleteSheet(temp);
      rel.etapa('abas criadas');
    } else {
      // seguindo de onde parou: as abas já nasceram todas, e as primeiras já estão preenchidas
      abas = ABAS.map(function (spec) { return ss.getSheetByName(spec.nome); });
      ABAS.forEach(function (spec, i) {
        if (!abas[i]) throw new Error('a planilha não tem a aba ' + spec.nome + ': rode construir(), do começo.');
      });
    }

    ABAS.forEach(function (spec, i) {
      if (i < de || parou >= 0) return;
      // a aba que pode não acabar nesta execução fica para a próxima; a primeira da vez sempre é montada
      if (i > de && rel.passou() + custoDaAba_(spec) > LIMITE_DA_EXECUCAO_) {
        parou = i;
        return;
      }
      try {
        feito.push(montarAba_(abas[i], spec));
      } catch (err) {
        throw new Error('parou montando a aba ' + spec.nome + ': ' + err.message);
      }
      rel.etapa(spec.nome);
    });
    if (parou >= 0) {
      props.setProperty(CHAVE_DA_MONTAGEM_, String(parou));
      Logger.log('A MONTAGEM PAROU ANTES DA ABA ' + ABAS[parou].nome + ', em ' + Math.round(rel.passou() / 1000) +
                 's, PARA NÃO ESTOURAR OS SEIS MINUTOS: rode a função continuar(). Faltam ' + (ABAS.length - parou) +
                 ' aba(s), os menus e o acabamento. · ' + feito.join(' · ') + ' · tempos: ' + ETAPAS_.join(', '));
      return;
    }
    props.deleteProperty(CHAVE_DA_MONTAGEM_);

    // 19/09/2026, testando no Sheets: o Mizuki reportou borda errada logo no construir() — a
    // FICHA!AK17 branca, a GLOSSÁRIO!B4 sem borda esquerda —, mas os dados (a viva ORIGINAL, o
    // ABAS gerado, e o .xlsx exportado depois) concordam os três: a borda gravada está certa nos
    // três lugares, sem exceção nenhuma. Casos relatados na comunidade apontam célula MESCLADA como o
    // ponto onde a borda desenhada na tela pode ficar pra trás da fila sem um flush no meio. Não é
    // prova, é tentativa dirigida: obrigar a fila a esvaziar aqui, com as abas já de pé mas antes do
    // menu que vem depois. Custa uma ida a mais ao servidor, uma vez por construir(), não por aba.
    SpreadsheetApp.flush();
    rel.etapa('fila esvaziada');

    // Os menus suspensos SÓ agora: eles apontam para a aba DADOS, e ela tem de estar preenchida.
    feito.push('menus: ' + menusSuspensos_(ss));
    rel.etapa('menus');

    // A ordem em que elas aparecem é a ordem do ABAS. Elas já nascem nessa ordem; só se o Sheets as tiver posto
    // em outra é que cada uma é movida.
    var nomes = ss.getSheets().map(function (a) { return a.getName(); });
    if (nomes.join('|') !== ABAS.map(function (spec) { return spec.nome; }).join('|')) {
      ABAS.forEach(function (spec, i) {
        ss.setActiveSheet(ss.getSheetByName(spec.nome));
        ss.moveActiveSheet(i + 1);
      });
    }
    ss.setActiveSheet(ss.getSheetByName(ABAS[0].nome));

    if (rel.passou() > TETO_DA_MONTAGEM_) {
      falta = true;
    } else {
      acabamento_(ss, feito, rel);
    }
  } finally {
    ss.setSpreadsheetLocale('pt_BR');
  }
  feito.push('idioma de antes: ' + idioma + ' · idioma final: pt_BR');

  var seg = Math.round(rel.passou() / 1000);
  if (falta) {
    Logger.log('AS ABAS ESTÃO DE PÉ em ' + seg + 's, MAS FALTA O ACABAMENTO: rode a função acabar(). · ' + feito.join(' · ') +
               ' · tempos: ' + ETAPAS_.join(', '));
  } else {
    Logger.log('FICHA PRONTA em ' + seg + 's · ' + feito.join(' · ') + ' · tempos: ' + ETAPAS_.join(', '));
  }
}

/**
 * O acabamento: a cor de estado, as notas, as travas de fórmula, as notas da FICHA PESSOAL, os saltos da FICHA
 * AMALDIÇOADA e a caixa da paleta.
 * Cada passo pode ser refeito sem estragar o que já está lá, e é por isso que ele pode rodar sozinho, pelo acabar().
 */
function acabamento_(ss, feito, rel) {
  var idx = indice();
  feito.push('cor de estado: ' + corDeEstado_(ss, idx));
  rel.etapa('cor de estado');
  feito.push('notas: ' + notasDeRegra_(ss, idx));
  rel.etapa('notas');
  feito.push('ficha pessoal: ' + configurarPessoal_(ss));
  rel.etapa('notas da ficha pessoal');
  feito.push('saltos: ' + ligarSaltos_(ss));
  rel.etapa('saltos da ficha amaldiçoada');
  feito.push('paleta: ' + configurarPaleta_(ss, true));
  rel.etapa('caixa da paleta');
  // 07/10/2026: as travas de aviso saíram (a conta em que alguém escreve por cima volta sozinha, pelo onEdit). Aqui
  // só saem as de uma ficha montada antes, quando o acabar() roda nela.
  feito.push('travas: ' + tirarTravasDeFormula_(ss));
  rel.etapa('travas de antes');
}

/**
 * Só o acabamento, numa planilha que o construir() já montou. Rode esta se o construir() avisar que faltou o
 * acabamento, ou se ele tiver parado no meio dele. A regra de cor é escrita com vírgula e ponto, então o idioma
 * vai para o inglês enquanto ela roda, como no construir().
 */
function acabar() {
  var ss = SpreadsheetApp.getActive(), feito = [], rel = relogio_();
  var faltam = ABAS.filter(function (spec) { return !ss.getSheetByName(spec.nome); });
  if (faltam.length) throw new Error('a planilha não tem a aba ' + faltam[0].nome + ': rode construir() antes.');
  var parada = PropertiesService.getDocumentProperties().getProperty(CHAVE_DA_MONTAGEM_);
  if (parada !== null) throw new Error('a montagem das abas parou antes da aba ' + (ABAS[Number(parada)] || {}).nome + ': rode continuar() antes do acabar().');
  ss.setSpreadsheetLocale('en_US');
  try {
    acabamento_(ss, feito, rel);
  } finally {
    ss.setSpreadsheetLocale('pt_BR');
  }
  Logger.log('ACABAMENTO PRONTO em ' + Math.round(rel.passou() / 1000) + 's · ' + feito.join(' · ') + ' · tempos: ' + ETAPAS_.join(', '));
}

/** A aba vazia, na posição dela e já com o número de linhas e de colunas que vai ter. */
function criarAba_(ss, spec, posicao) {
  var aba = ss.insertSheet(spec.nome, posicao);
  var nc = spec.cols, nr = spec.rows, temC = aba.getMaxColumns(), temR = aba.getMaxRows();
  if (temC > nc) aba.deleteColumns(nc + 1, temC - nc);
  if (temR > nr) aba.deleteRows(nr + 1, temR - nr);
  if (temC < nc) aba.insertColumnsAfter(temC, nc - temC);
  if (temR < nr) aba.insertRowsAfter(temR, nr - temR);
  return aba;
}

/**
 * As mesclagens em lotes. Uma mesclagem de uma linha só que se repete nas linhas de baixo com as mesmas colunas (a
 * tabela de perícias, a de itens, a de missões) vira uma chamada de mergeAcross na faixa inteira; a de uma coluna só
 * que se repete nas colunas do lado vira uma de mergeVertically. O resto continua uma a uma. O resultado na planilha
 * é o mesmo; o que muda é o número de idas ao servidor. Cada grupo é [tipo, linha, coluna, última linha, última coluna].
 */
function gruposDeMescla_(merges) {
  var grupos = [], lin = {}, col = {};
  merges.forEach(function (m) {
    if (m[0] === m[2] && m[1] !== m[3]) (lin[m[1] + ',' + m[3]] = lin[m[1] + ',' + m[3]] || []).push(m[0]);
    else if (m[1] === m[3] && m[0] !== m[2]) (col[m[0] + ',' + m[2]] = col[m[0] + ',' + m[2]] || []).push(m[1]);
    else grupos.push(['m', m[0], m[1], m[2], m[3]]);
  });
  var corridas = function (mapa, monta) {
    Object.keys(mapa).forEach(function (k) {
      var a = Number(k.split(',')[0]), b = Number(k.split(',')[1]);
      var v = mapa[k].slice().sort(function (x, y) { return x - y; }), i = 0;
      while (i < v.length) {
        var j = i;
        while (j + 1 < v.length && v[j + 1] === v[j] + 1) j++;
        grupos.push(monta(a, b, v[i], v[j]));
        i = j + 1;
      }
    });
  };
  corridas(lin, function (c1, c2, r1, r2) { return [r1 === r2 ? 'm' : 'a', r1, c1, r2, c2]; });
  corridas(col, function (r1, r2, c1, c2) { return [c1 === c2 ? 'm' : 'v', r1, c1, r2, c2]; });
  return grupos;
}

/**
 * Uma regra de cor que o gerador declara na aba (`condicional` no ABAS): o texto que começa ou contém um trecho, ou uma
 * fórmula; e o que ela faz (o fundo, a letra, o riscado). A FICHA refaz todas as regras dela no corDeEstado_, e por
 * isso as declaradas entram de novo lá.
 */
function regraDeCor_(aba, c) {
  var regra = SpreadsheetApp.newConditionalFormatRule();
  regra = c.formula ? regra.whenFormulaSatisfied(c.formula) : c.comeca ? regra.whenTextStartsWith(c.comeca) : regra.whenTextContains(c.contem);
  regra.setRanges(c.faixas.map(function (a1) { return aba.getRange(a1); }));
  if (c.fundo) regra.setBackground(c.fundo);
  if (c.fonte) regra.setFontColor(c.fonte);
  if (c.riscado) regra.setStrikethrough(true);
  return regra.build();
}

function montarAba_(aba, spec) {
  var nc = spec.cols, nr = spec.rows;
  aba.setHiddenGridlines(true);
  aba.setColumnWidths(1, nc, spec.larg);
  // as colunas que fogem da largura base, em faixas
  (spec.largs || []).forEach(function (g) {
    var c2 = Math.min(g[1], nc);
    if (g[0] <= c2) aba.setColumnWidths(g[0], c2 - g[0] + 1, g[2]);
  });

  // matrizes locais: escrever célula a célula no Sheets é lento demais
  var pad = spec.padrao || ['Roboto', 11, '#F4F1F7'];
  var v = mat_(nr, nc, ''), bg = mat_(nr, nc, spec.fundo_base === undefined ? '#120F1D' : spec.fundo_base);
  var ff = mat_(nr, nc, pad[0]), fs = mat_(nr, nc, pad[1]);
  var fc = mat_(nr, nc, pad[2]), fw = mat_(nr, nc, 'normal');
  var ha = mat_(nr, nc, 'left'), va = mat_(nr, nc, 'middle');
  var fst = mat_(nr, nc, 'normal'), wr = mat_(nr, nc, false);
  var giradas = [], formulas = 0;

  // fundo em faixas: [linha, colIni, colFim, cor]
  spec.fundos.forEach(function (f) {
    for (var c = f[1]; c <= f[2]; c++) bg[f[0] - 1][c - 1] = f[3];
  });
  spec.vals.forEach(function (t) {
    // A fórmula vai na mesma matriz dos valores: o setValues lê como fórmula o texto que começa com "=", e a aba
    // que ela cita já existe (ver o construir). O setValues lê a pontuação no idioma da planilha, e é por isso
    // que a montagem é em inglês.
    v[t[0] - 1][t[1] - 1] = t[2];
    if (typeof t[2] === 'string' && t[2].charAt(0) === '=') formulas++;
    if (t.length > 3) {
      var e = spec.estilos[t[3]];
      ff[t[0] - 1][t[1] - 1] = e[0];
      fs[t[0] - 1][t[1] - 1] = e[1];
      if (e[2]) fc[t[0] - 1][t[1] - 1] = e[2];
      fw[t[0] - 1][t[1] - 1] = e[3] ? 'bold' : 'normal';
      ha[t[0] - 1][t[1] - 1] = e[4];
      va[t[0] - 1][t[1] - 1] = e[5] === 'center' ? 'middle' : e[5];
      if (e[6]) giradas.push([t[0], t[1], e[6]]);
      if (e[7]) fst[t[0] - 1][t[1] - 1] = 'italic';
      if (e[8]) wr[t[0] - 1][t[1] - 1] = true;
    }
  });

  var r = aba.getRange(1, 1, nr, nc);
  r.setBackgrounds(bg).setFontFamilies(ff).setFontSizes(fs)
   .setFontColors(fc).setFontWeights(fw)
   .setHorizontalAlignments(ha).setVerticalAlignments(va)
   .setFontStyles(fst).setWraps(wr);
  r.setValues(v);
  // 01/10/2026, a DADOS_AM: a conta de cada feitiço são cem fórmulas iguais a menos da linha. Só a primeira linha de
  // cada retângulo vem no ABAS, e o resto é a cópia dela para baixo, que é o que o Sheets faz quando alguém arrasta
  // a alça da célula: a linha de toda referência sem cifrão anda junto. Cada retângulo é [linha, coluna, última
  // linha, última coluna].
  (spec.abaixo || []).forEach(function (b) {
    var n = b[3] - b[1] + 1;
    aba.getRange(b[0], b[1], 1, n).copyTo(aba.getRange(b[0] + 1, b[1], b[2] - b[0], n));
  });

  // A rotação NÃO entra em lote: setTextRotations quer objetos TextRotation, e
  // não graus, então uma matriz de números é recusada. Como só a lombada é
  // girada -- duas células por aba --, uma chamada por célula sai barato.
  giradas.forEach(function (g) { aba.getRange(g[0], g[1]).setTextRotation(g[2]); });

  // altura em PIXEL, calculada pela maior letra da linha. Era isto que estava
  // cortando o 'd20 + 0' pela metade no caminho antigo.
  aba.setRowHeights(1, nr, 21);
  var linhas = Object.keys(spec.alturas).map(Number).sort(function (a, b) { return a - b; });
  var ini = null, ant = null, alt = null;
  linhas.concat([null]).forEach(function (l) {
    var h = l === null ? null : spec.alturas[String(l)];
    if (ini !== null && (l === null || l !== ant + 1 || h !== alt)) {
      aba.setRowHeights(ini, ant - ini + 1, alt);
      ini = null;
    }
    if (l !== null && ini === null) { ini = l; alt = h; }
    ant = l;
  });

  // 01/10/2026, a FICHA AMALDIÇOADA: as fileiras de cartas são todas iguais, e cada uma tem quase cinquenta
  // mesclagens. Só a primeira fileira de cada tipo é mesclada aqui; as outras recebem o FORMATO dela por cópia, e a
  // mesclagem vem junto. Cada cópia é [primeira linha, última linha, [a linha onde cada cópia começa]]. O valor de
  // cada célula já está no lugar e a cópia de formato não toca nele.
  var copias = spec.copias || [];
  // 07/10/2026, a INVOCAÇÕES: a cópia pode ir em mais de uma faixa de colunas (k[5], uma por coluna de fichas), porque
  // a lombada de cada coluna de fichas atravessa as fileiras copiadas. Sem o k[5], é a faixa de k[3] a k[4].
  var faixasDe = function (k) { return k[5] || [[k[3] || 1, k[4] || nc]]; };
  var naCopia = function (m) {
    return copias.some(function (k) {
      return faixasDe(k).some(function (f) { return m[1] >= f[0] && m[3] <= f[1]; }) &&
             k[2].some(function (d) { return m[0] >= d && m[2] <= d + k[1] - k[0]; });
    });
  };
  var mesclar = function (lista) {
    gruposDeMescla_(lista).forEach(function (g) {
      var faixa = aba.getRange(g[1], g[2], g[3] - g[1] + 1, g[4] - g[2] + 1);
      if (g[0] === 'a') faixa.mergeAcross();
      else if (g[0] === 'v') faixa.mergeVertically();
      else faixa.merge();
    });
  };
  mesclar(copias.length ? spec.merges.filter(function (m) { return !naCopia(m); }) : spec.merges);
  var copiadas = '';
  if (copias.length) {
    var veio = true;
    copias.forEach(function (k) {
      // k[3] e k[4] são a primeira e a última coluna da cópia: a lombada fica de fora, porque as mesclagens dela
      // atravessam as fileiras, e o Sheets não copia meia mesclagem
      var alt = k[1] - k[0] + 1, ultima = k[2][k[2].length - 1];
      faixasDe(k).forEach(function (f) {
        var c1 = f[0], larg = f[1] - c1 + 1, molde = aba.getRange(k[0], c1, alt, larg);
        k[2].forEach(function (d) {
          molde.copyTo(aba.getRange(d, c1, alt, larg), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
        });
        // a prova de que a mesclagem veio com o formato: a primeira mesclagem da última cópia tem de existir
        var prova = spec.merges.filter(function (m) { return m[0] >= ultima && m[2] <= ultima + alt - 1 && m[1] >= c1 && m[3] <= c1 + larg - 1; })[0];
        if (prova && !aba.getRange(prova[0], prova[1]).isPartOfMerge()) veio = false;
      });
    });
    if (!veio) {
      // o Sheets não trouxe as mesclagens: desfaz o que tiver vindo pela metade e faz uma a uma, como nas outras abas
      copias.forEach(function (k) {
        faixasDe(k).forEach(function (f) {
          k[2].forEach(function (d) { aba.getRange(d, f[0], k[1] - k[0] + 1, f[1] - f[0] + 1).breakApart(); });
        });
      });
      mesclar(spec.merges.filter(naCopia));
    }
    copiadas = veio ? ', fileiras copiadas' : ', FILEIRAS MESCLADAS UMA A UMA (a cópia de formato não trouxe a mesclagem)';
  }

  // As bordas, os quatro lados, com o traço e a cor da planilha viva: uma chamada por lado, traço e
  // cor, com as faixas numa RangeList. Até 15/09/2026 só a de cima entrava, e só em célula com valor.
  var TRACO = { thin: 'SOLID', medium: 'SOLID_MEDIUM', thick: 'SOLID_THICK', dashed: 'DASHED',
                mediumDashed: 'DASHED', dotted: 'DOTTED', hair: 'DOTTED', double: 'DOUBLE' };
  (spec.bordas || []).forEach(function (b) {
    var lado = b[0], traco = SpreadsheetApp.BorderStyle[TRACO[b[1]] || 'SOLID'];
    for (var i = 0; i < b[3].length; i += 400) {
      aba.getRangeList(b[3].slice(i, i + 400)).setBorder(
        lado === 'top' ? true : null, lado === 'left' ? true : null,
        lado === 'bottom' ? true : null, lado === 'right' ? true : null,
        null, null, b[2], traco);
    }
  });

  // As imagens DENTRO da célula, numa caixa mesclada: solta, ela arrasta com o mouse. Decisão do
  // Mizuki em 15/09/2026. A arte já vem no formato da caixa, porque o Sheets encaixa sem esticar.
  // A caixa que a planilha exportada já traz mesclada não é mesclada de novo: quem diz é a lista de
  // mesclagens da própria aba, sem perguntar ao Sheets.
  spec.imgs.forEach(function (im) {
    if (!ARTE[im[4]]) return;
    var caixa = aba.getRange(im[0], im[1], im[2] - im[0] + 1, im[3] - im[1] + 1);
    var jaMesclada = spec.merges.some(function (m) {
      return m[0] <= im[2] && m[2] >= im[0] && m[1] <= im[3] && m[3] >= im[1];
    });
    if ((im[2] > im[0] || im[3] > im[1]) && !jaMesclada) caixa.merge();
    // O título de alt marca a imagem como NOSSA (a troca de paleta recolore só o que tem este título, e nunca
    // a foto que o jogador pôs no lugar), e a descrição guarda a cor que ela tem agora, pra a troca não
    // reenviar uma imagem que já está da cor certa. Ver repintarArte_ no Codigo.gs.
    aba.getRange(im[0], im[1]).setValue(SpreadsheetApp.newCellImage()
      .setSourceUrl('data:image/png;base64,' + ARTE[im[4]])
      .setAltTextTitle('PM-ARTE:' + im[4]).setAltTextDescription('fabrica').build());
  });

  // as caixas de seleção, nas posições que o gerador mediu
  // (a aba que pede a validação em matriz recebe as caixas junto com os menus, no menusSuspensos_)
  if (!spec.validacao_em_matriz) {
    (spec.caixas || []).forEach(function (cx) {
      aba.getRange(cx[1], cx[0], cx[2], 1).insertCheckboxes();
    });
  }

  // 01/10/2026, a FICHA PESSOAL: o formato de número, a nota da caixa, a cor de aviso e os grupos que fecham.
  // Só a aba que declara cada um recebe; as outras saem como saíam.
  // uma chamada por formato, com as células dele numa lista: a FICHA AMALDIÇOADA tem quarenta caixas de Classe
  var porFormato = {};
  (spec.formatos || []).forEach(function (f) { (porFormato[f[1]] = porFormato[f[1]] || []).push(f[0]); });
  Object.keys(porFormato).forEach(function (fmt) { aba.getRangeList(porFormato[fmt]).setNumberFormat(fmt); });
  // as notas de caixa numa gravação só, na faixa que vai da primeira à última célula com nota
  if ((spec.notas || []).length) {
    var onde = spec.notas.map(function (n) {
      var m = /^([A-Z]+)(\d+)/.exec(n[0]), c = 0;
      for (var i = 0; i < m[1].length; i++) c = c * 26 + m[1].charCodeAt(i) - 64;
      return [Number(m[2]), c, n[1]];
    });
    var r1 = Math.min.apply(null, onde.map(function (o) { return o[0]; })), r2 = Math.max.apply(null, onde.map(function (o) { return o[0]; }));
    var c1 = Math.min.apply(null, onde.map(function (o) { return o[1]; })), c2 = Math.max.apply(null, onde.map(function (o) { return o[1]; }));
    var notas = mat_(r2 - r1 + 1, c2 - c1 + 1, '');
    onde.forEach(function (o) { notas[o[0] - r1][o[1] - c1] = o[2]; });
    aba.getRange(r1, c1, r2 - r1 + 1, c2 - c1 + 1).setNotes(notas);
  }
  if ((spec.condicional || []).length) {
    aba.setConditionalFormatRules(spec.condicional.map(function (c) { return regraDeCor_(aba, c); }));
  }
  if (spec.grupos) {
    // O botão de fechar fica ANTES do grupo: na linha do título da lista, e na coluna antes do painel.
    var ANTES = SpreadsheetApp.GroupControlTogglePosition.BEFORE;
    aba.setRowGroupControlPosition(ANTES);
    aba.setColumnGroupControlPosition(ANTES);
    // Cada grupo é [primeira, última, fechado, profundidade]. Um grupo pode morar dentro de outro (a extensão do
    // painel de XP, dentro do painel): todos nascem primeiro, e depois fecham de dentro para fora.
    var deDentro = function (a, b) { return b[3] - a[3]; };
    (spec.grupos.lin || []).forEach(function (g) { aba.getRange(g[0], 1, g[1] - g[0] + 1, 1).shiftRowGroupDepth(1); });
    (spec.grupos.col || []).forEach(function (g) { aba.getRange(1, g[0], 1, g[1] - g[0] + 1).shiftColumnGroupDepth(1); });
    // 01/10/2026: a FICHA AMALDIÇOADA tem cinquenta grupos de linhas, e quase todos nascem fechados. Quando os
    // fechados são a maioria, todos fecham numa chamada só e os que nascem abertos são abertos de fora para dentro.
    var lin = spec.grupos.lin || [], fechados = lin.filter(function (g) { return g[2]; }).length;
    if (fechados > lin.length - fechados) {
      aba.collapseAllRowGroups();
      lin.slice().sort(function (a, b) { return a[3] - b[3]; }).forEach(function (g) { if (!g[2]) aba.getRowGroup(g[0], g[3]).expand(); });
    } else {
      lin.slice().sort(deDentro).forEach(function (g) { if (g[2]) aba.getRowGroup(g[0], g[3]).collapse(); });
    }
    (spec.grupos.col || []).slice().sort(deDentro).forEach(function (g) { if (g[2]) aba.getColumnGroup(g[0], g[3]).collapse(); });
  }

  if (spec.oculta) aba.hideSheet();
  return spec.nome + ': ' + spec.vals.length + ' células, ' + formulas +
       ' fórmulas, ' + spec.imgs.length + ' imagens' + copiadas;
}

function mat_(nr, nc, valor) {
  var m = [];
  for (var i = 0; i < nr; i++) {
    var l = [];
    for (var j = 0; j < nc; j++) l.push(valor);
    m.push(l);
  }
  return m;
}

/** Os menus suspensos, depois que todas as abas existem. */
function menusSuspensos_(ss) {
  var n = 0;
  ABAS.forEach(function (spec) {
    var aba = ss.getSheetByName(spec.nome);
    var regraDe = function (de) {
      // O Sheets exporta menu de itens como lista escrita, "a,b,c", e ela nao e intervalo:
      // passar ela ao getRange parou a montagem em 'Range not found' (teste de 15/09/2026).
      var regra = SpreadsheetApp.newDataValidation().setAllowInvalid(true);
      var lista = /^"(.*)"$/.exec(de);
      if (lista) {
        regra.requireValueInList(lista[1].split(','), true);
      } else {
        regra.requireValueInRange(ss.getRange(de.replace(/\$/g, '')), true);
      }
      return regra.build();
    };
    if (spec.validacao_em_matriz) {
      // 01/10/2026, a FICHA AMALDIÇOADA: mais de duzentas faixas de menu e quarenta de caixa de seleção. Uma regra por
      // lista, postas numa matriz do tamanho da aba e gravadas de uma vez. A célula sem regra fica sem validação.
      var regras = mat_(spec.rows, spec.cols, null), porLista = {};
      var poe = function (l1, c1, l2, c2, regra) {
        for (var i = l1; i <= l2; i++) for (var j = c1; j <= c2; j++) regras[i - 1][j - 1] = regra;
      };
      (spec.dv || []).forEach(function (d) {
        var f = limitesA1_(d[0]);
        poe(f.l1, f.c1, f.l2, f.c2, porLista[d[1]] || (porLista[d[1]] = regraDe(d[1])));
        n++;
      });
      if ((spec.caixas || []).length) {
        var caixa = SpreadsheetApp.newDataValidation().requireCheckbox().build();
        spec.caixas.forEach(function (cx) { poe(cx[1], cx[0], cx[1] + cx[2] - 1, cx[0], caixa); });
      }
      aba.getRange(1, 1, spec.rows, spec.cols).setDataValidations(regras);
      return;
    }
    (spec.dv || []).forEach(function (d) {
      aba.getRange(d[0].replace(/\$/g, '')).setDataValidation(regraDe(d[1]));
      n++;
    });
  });
  return n + ' menu(s)';
}

/**
 * Confere a ficha montada, sem mexer em nada. Rode esta se quiser saber se
 * ficou tudo de pé -- ela não altera a planilha.
 */
function verificar() {
  var ss = SpreadsheetApp.getActive();
  var falhas = [];
  ABAS.forEach(function (spec) {
    var aba = ss.getSheetByName(spec.nome);
    if (!aba) { falhas.push('falta a aba ' + spec.nome); return; }
    spec.imgs.forEach(function (im) {
      var cel = aba.getRange(im[0], im[1]), val = cel.getValue();
      if (!val || val.valueType !== SpreadsheetApp.ValueType.IMAGE) {
        falhas.push(spec.nome + ': falta a imagem ' + im[4] + ' em ' + cel.getA1Notation());
      }
    });
  });
  var idx = indice();
  ['vida_max', 'defesa', 'maestria', 'cd de feitiço'].forEach(function (k) {
    if (!idx[k]) falhas.push('o índice não tem ' + k);
  });
  var fontes = {};
  ABAS.forEach(function (spec) {
    (spec.estilos || []).forEach(function (e) { fontes[e[0]] = true; });
  });
  Logger.log(falhas.length ? ('PROBLEMAS: ' + falhas.join(' · '))
                           : ('TUDO DE PÉ · fontes usadas: ' + Object.keys(fontes).join(', ')));
}
