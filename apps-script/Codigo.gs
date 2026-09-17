/**
 * Projeto M · o que roda DEPOIS da ficha estar montada.
 *
 * O Ficha.gs constrói a planilha. Este arquivo cuida do que depende de ela já
 * existir: cor de estado, notas de regra, proteção de fórmula, e o gatilho que
 * faz a caixinha de ± funcionar.
 *
 * Nenhum endereço de célula está escrito aqui. Tudo sai do índice que a
 * própria ficha publica na aba DADOS, então o layout pode mudar sem quebrar
 * este arquivo.
 */

var IDX_COL_CAMPO = 53;   // BA
var IDX_COL_CEL   = 54;   // BB

function indice() {
  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS');
  var vals = dados.getRange(1, IDX_COL_CAMPO, dados.getLastRow(), 2).getValues();
  var m = {};
  vals.forEach(function (l) { if (l[0] && l[1]) m[l[0]] = String(l[1]); });
  return m;
}

function cel_(idx, chave) {
  return idx[chave] ? idx[chave].replace(/\$/g, '') : null;
}

/**
 * A decisão A5: osso cheio, âmbar abaixo da metade, vermelho abaixo de um
 * quarto. Os hex estão repetidos aqui porque o Apps Script não lê o
 * repositório — se eles mudarem lá, o conferir-decisoes.py acende.
 */
function corDeEstado_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var regras = [];
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var atual = idx[r], max = idx[r + '_max'];
    if (!atual || !max) return;
    var alvo = ficha.getRange(cel_(idx, r));
    [[0.25, '#C2334D'], [0.5, '#D89B3A']].forEach(function (par) {
      regras.push(SpreadsheetApp.newConditionalFormatRule()
        .whenFormulaSatisfied('=AND(N(' + max + ')>0,' + atual + '/' + max +
                              '<=' + par[0] + ')')
        .setFontColor(par[1]).setRanges([alvo]).build());
    });
  });
  // 17/09/2026: as caixas de X de Y ficam vermelhas quando a conta avisa que passou. O texto do aviso
  // sai da fórmula da própria caixa, e estes trechos são os que ela escreve.
  var avisos = ['pontos disponíveis', 'pontos de corpo', 'marcos escolhidos', 'perícias disponíveis',
                'ofícios disponíveis', 'testes disponíveis', 'aptidões disponíveis', 'passivas do leque']
    .map(function (k) { return cel_(idx, k); })
    .filter(function (c) { return c; })
    .map(function (c) { return ficha.getRange(c); });
  if (avisos.length) {
    [' a mais', 'passou de', 'só no nível', 'nenhum acima'].forEach(function (trecho) {
      regras.push(SpreadsheetApp.newConditionalFormatRule()
        .whenTextContains(trecho).setFontColor('#C2334D').setRanges(avisos).build());
    });
  }
  ficha.setConditionalFormatRules(regras);
  return regras.length + ' regra(s)';
}

/**
 * A nota mora no título da caixa, e não no número. 17/09/2026, pedido do Mizuki: as notas do Marco
 * Escolhido estavam no valor, e as outras no título. O título é a célula de cima quando ela é texto
 * digitado. A caixa que escreve o próprio cabeçalho em fórmula, como a de Feitiços, fica com a nota.
 *
 * A decisão mora no tituloOuCaixa_, sem planilha em volta, e o regressao-delta.js roda ela no node.
 */
function tituloOuCaixa_(acima) {
  if (!acima || acima.formula) return 'caixa';
  return (typeof acima.valor === 'string' && acima.valor.trim()) ? 'título' : 'caixa';
}

function alvoDaNota_(aba, a1) {
  var cel = aba.getRange(a1);
  if (cel.getRow() === 1) return cel;
  var acima = aba.getRange(cel.getRow() - 1, cel.getColumn());
  var m = acima.getMergedRanges();
  if (m.length) acima = aba.getRange(m[0].getRow(), m[0].getColumn());
  return tituloOuCaixa_({ formula: acima.getFormula(), valor: acima.getValue() }) === 'título' ? acima : cel;
}

/** A regra aparece ao passar o mouse, sem gastar pixel na tela. */
function notasDeRegra_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var notas = {
    'defesa': 'Defesa = 10 + Destreza + proteção. Com uniforme ou escudo no EQUIPAMENTO, a Destreza ' +
              'para no teto dele. O Buff/Debuff do lado soma por cima.',
    'proteção': 'Traje e Revestimento DESLIGAM a proteção do cobrir-se e entregam a ' +
                'deles no lugar. Escudo soma por cima de qualquer uma das duas.',
    'iniciativa': 'Iniciativa = d20 + Destreza. Quem tirar mais age primeiro. O Buff/Debuff do lado ' +
                  'soma por cima.',
    'maestria': 'Vira 2 no nível 10, 3 no 18, 4 no 26. Não é "a cada oito níveis".',
    'cd de feitiço': 'CD de feitiço = 8 + o atributo da sua técnica + maestria. ' +
                     'O atributo é o que você escolhe em ATRIBUTO DE CONJURAÇÃO.',
    'conjuração': 'Ataque de conjuração = d20 + o atributo da sua técnica + maestria. O atributo é o ' +
                  'que você escolhe em ATRIBUTO DE CONJURAÇÃO.',
    'corpo a corpo': 'Ataque corpo a corpo = d20 + Força + maestria. A ficha usa o atributo de ' +
                     'ATRIBUTO DE ATAQUE - CORPO A CORPO: troque só se uma regra mandar.',
    'à distância': 'Ataque à distância = d20 + Destreza + maestria. A ficha usa o atributo de ' +
                   'ATRIBUTO DE ATAQUE - À DISTÂNCIA: troque só se uma regra mandar.',
    'deslocamento': 'O seu deslocamento base é 9 metros, e você corta esse total em quantos pedaços ' +
                    'quiser dentro do turno. O Buff/Debuff do lado soma em metros.',
    'vida_temp': 'Vida temporária não acumula: fica a maior, com teto de metade ' +
                 'da vida máxima. Some no fim da cena, e é gasta antes da vida ' +
                 'normal — a caixinha de ± desconta daqui primeiro e só o que ' +
                 'sobrar desce na vida. Dano com Rasga Escudo ignora isto: ' +
                 'edite a vida na mão.',
    'energia_temp': 'Energia temporária não acumula: fica a maior, com teto de ' +
                    'metade do PE máximo (o Braseiro e o Trindade dão 2). Some no ' +
                    'fim da cena, e a caixinha de ± queima daqui antes do seu PE.',
    'integridade_temp': 'Nenhuma regra do manual concede integridade temporária. ' +
                        'Se algo conceder, vale a regra das outras duas: não acumula, ' +
                        'e o teto é metade da Integridade máxima.',
    'equipamento': 'Escolha o que você veste: uniforme, escudo, ou os dois. Vazio = ' +
                   'nem uniforme nem escudo, e vale a proteção do cobrir-se. Todo ' +
                   'feiticeiro registrado recebe o Traje 1 na matrícula. Com dois tetos ' +
                   'de Destreza, vale o menor.',
    'refino escolhido': 'Quantas vezes você escolheu Refino num marco. Cada escolha ' +
                        'dá +1 além do +1 de graça do marco. Conta no máximo uma por ' +
                        'marco que você já passou, e o refino para em 10.',
    'marco corpo': 'Quantas vezes você escolheu Corpo num marco. Cada uma dá +1 ponto de atributo, e ' +
                   '+1 perícia ou ofício treinado. Do nível 10 em diante, pode especializar um que já ' +
                   'treina no lugar. Marque em Pontos de Marco de Corpo em qual atributo o ponto foi.',
    'marco leque': 'Quantas vezes você escolheu Leque num marco. Cada uma dá +1 espaço de feitiço, e ' +
                   'uma Passiva que não custa espaço. Anote essa Passiva na coluna Passivas do Leque.',
    'marcos escolhidos': 'Os marcos caem nos níveis 6, 10, 14, 18, 22, 26 e 30. Em cada um, ' +
                         'escolha Refino, Corpo ou Leque, e marque embaixo quantas vezes escolheu cada.',
    'buff de defesa': 'Soma na Defesa o que nenhuma outra caixa cobre, como a Couraça (+1 ' +
                      'vestindo uniforme) ou um efeito que dura. Número negativo reduz.',
    'pontos disponíveis': 'Quantos pontos de atributo faltam distribuir nas caixas pequenas, ' +
                          'de quantos você tem: 9 da criação, e +1 por marco que já passou. ' +
                          'Avisa se passou, se um atributo passou de 6, ou se algum passou ' +
                          'de 3 antes do primeiro marco.',
    'pontos de corpo': 'Cada escolha de Corpo no Marco Escolhido é um ponto de Corpo: ' +
                       'marque embaixo em qual atributo ele foi. Ele soma no número grande.',
    'perícias disponíveis': 'Na criação: 9 perícias e 2 ofícios, ou 10 perícias e nenhum ofício. ' +
                            'Cada marco de Corpo dá +1 perícia ou ofício, ou uma especialização ' +
                            'do nível 10 em diante. A ficha deduz para qual lista ele foi; se ' +
                            'passar nas duas, as duas caixas avisam. Guia, Emanador e Evocador ' +
                            'podem trocar 2 perícias por treino em arma, e isso a ficha não conta.',
    'ofícios disponíveis': 'Na criação: 2 ofícios, ou nenhum trocando os dois por mais uma perícia. ' +
                           'Cada marco de Corpo dá +1 perícia ou ofício, e a ficha deduz para ' +
                           'qual lista ele foi.',
    'testes disponíveis': 'Dois treinados: um do Caminho e um da Origem, os dois à sua escolha.',
    'escolhas de perícia': 'O que ainda falta marcar: as perícias e os ofícios da criação, e as ' +
                           'escolhas dos marcos de Corpo (+1 perícia, +1 ofício, ou uma especialização ' +
                           'do nível 10 em diante). A ficha começa contando 9 perícias e 2 ofícios, e só ' +
                           'passa para 10 e nenhum quando você marca a décima perícia.',
    'aptidões disponíveis': 'Duas de graça no refino 1, +1 por escolha de Refino, e duas quando o ' +
                            'refino já está em 10 na hora de escolher. A ficha conta como se as ' +
                            'escolhas de Refino tivessem sido as últimas: se você escolheu Refino ' +
                            'cedo, no nível 26 ou 30 confira com o mestre. As duas de graça já vêm ' +
                            'anotadas nas duas primeiras linhas.',
    'feitiços disponíveis': 'Disponível: os espaços de feitiço, menos cada feitiço anotado com Classe ' +
                            'acima de 0, menos a Classe das Passivas da coluna Passivas - Regras. ' +
                            'Conhecidos (Total): os espaços de feitiço. Classe 0: quantos feitiços de ' +
                            'Classe 0 grátis ainda cabem.',
    'passivas': 'Passiva é efeito que fica ligado sozinho, e custa espaço de feitiço: a Classe dela, ' +
                'de Livre a 3, diz quantos espaços cobra, e sai de Feitiços - Disponível. A Passiva ' +
                'que veio de uma escolha de Leque vai na coluna do lado, e não custa espaço.',
    'passivas do leque': 'Cada escolha de Leque dá uma Passiva que não custa espaço de feitiço. ' +
                         'As Passivas da coluna da esquerda custam, e entram na conta de Feitiços.',
    'caminho': 'Ao escolher o Caminho, as duas perícias fixas dele são marcadas sozinhas. ' +
               'Ofício e Teste de Resistência são à sua escolha. Se a Trilha escolhida não for ' +
               'do Caminho novo, ela volta para Escolha sua Trilha.',
    'trilha': 'O menu mostra só as Trilhas do Caminho escolhido.'
  };
  var buff = 'Soma no número do lado o que nenhuma outra caixa cobre, como um efeito que dura. ' +
             'Número negativo reduz.';
  ['iniciativa', 'cd de feitiço', 'conjuração', 'corpo a corpo', 'à distância'].forEach(function (k) {
    notas['buff de ' + k] = buff;
  });
  notas['buff de deslocamento'] = 'Soma no deslocamento, em metros, o que nenhuma outra caixa cobre. ' +
                                  'Número negativo reduz.';
  var n = 0;
  Object.keys(notas).forEach(function (k) {
    var c = cel_(idx, k);
    if (!c) return;
    var alvo = alvoDaNota_(ficha, c);
    // a ficha que já tinha a nota no número não fica com duas
    if (alvo.getA1Notation() !== c) ficha.getRange(c).clearNote();
    alvo.setNote(notas[k]);
    n++;
  });
  // a CARTEIRA não publica índice: a nota vai no rótulo, achado pelo texto
  var carteira = ss.getSheetByName('CARTEIRA');
  var rotulos = {
    'PORTADOR': 'O nome do personagem. A FICHA puxa o nome daqui.',
    'SERVIDOR USADO': 'O servidor onde esta ficha é usada.',
    'REGISTRADO POR': 'O seu nick, o do jogador.'
  };
  if (carteira) {
    carteira.getDataRange().getValues().forEach(function (linha, i) {
      linha.forEach(function (v, j) {
        var nota = rotulos[String(v).trim()];
        if (nota) { carteira.getRange(i + 1, j + 1).setNote(nota); n++; }
      });
    });
  }
  return n + ' nota(s) · ' + notasDeGraca_(ss, idx);
}

/**
 * As duas aptidões de graça já vêm anotadas, e a nota delas acompanha a Origem: com Restrição
 * Celestial · sem energia, as duas linhas viram as duas Bênçãos de graça. A nota não segue fórmula,
 * então o onEdit refaz quando a Origem muda. O texto resume o manual; o conferir-ficha-xlsx.py
 * confere que os números dele estão lá.
 */
var NOTAS_DE_GRACA = {
  'Cobrir-se de energia': 'De graça no refino 1. Sem Traje e sem Revestimento, a sua proteção é ' +
                          '1/3 do refino + 1. Escudo soma com ela. Como Reação, por 2 PE: Redução de ' +
                          'Dano de 1,5 × refino num golpe, e você fica sem proteção até o fim do seu ' +
                          'próximo turno.',
  'Canalizar energia': 'De graça no refino 1. O seu ataque com arma ou soco vem imbuído de energia ' +
                       'amaldiçoada, e fere maldição. Com arma: 1d4 de dano a mais no refino 1, 2d4 no ' +
                       '3, 3d4 no 6, 4d4 no 9, e 4d6 no 10. Não entra em feitiço.',
  'Defesa sem Armadura': 'De graça na Lapidação 1. Sem Traje e sem Revestimento, a sua proteção é ' +
                         '1/3 da Lapidação + 1. Escudo soma com ela. Como Reação, por 2 PE: Redução de ' +
                         'Dano de 1,5 × Lapidação num golpe, e você fica sem proteção até o fim do seu ' +
                         'próximo turno. Barreira de energia não segura você.',
  'Estímulo Muscular': 'De graça na Lapidação 1. Escolha uma perícia e um Teste de Resistência na ' +
                       'criação: 1× por cena, e 2× na Lapidação 10, vantagem numa rolagem de um dos ' +
                       'dois. Com arma: 1d4 de dano a mais na Lapidação 1, 2d4 na 3, 3d4 na 6, 4d4 ' +
                       'na 9, e 4d6 na 10.'
};

function notasDeGraca_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  SpreadsheetApp.flush();
  var n = 0;
  ['aptidão de graça 1', 'aptidão de graça 2'].forEach(function (k) {
    var c = cel_(idx, k);
    if (!c) return;
    var cel = ficha.getRange(c);
    var nota = NOTAS_DE_GRACA[String(cel.getValue()).trim()];
    cel.setNote(nota || '');
    if (nota) n++;
  });
  return n + ' nota(s) de graça';
}

/**
 * O jogador não apaga fórmula sem querer. Avisa, não bloqueia: o mestre precisa poder mexer.
 *
 * 17/09/2026: a lista de campos virou varredura, a pedido do Mizuki, porque o resultado das perícias,
 * dos ofícios e dos Testes de Resistência e o cabeçalho dos Feitiços ficavam de fora, e cada caixa
 * nova pedia lembrar de pôr o nome aqui. Toda fórmula da FICHA e da CARTEIRA é travada, menos as três
 * barras de agora, que a decisão A4 deixa editáveis. Rodar de novo troca as travas, não duplica.
 */
var LIVRES_DA_TRAVA = ['vida', 'energia', 'integridade'];

function protegerFormulas_(ss, idx) {
  var livres = LIVRES_DA_TRAVA.map(function (k) { return cel_(idx, k); });
  var n = 0;
  ['FICHA', 'CARTEIRA'].forEach(function (nome) {
    var aba = ss.getSheetByName(nome);
    if (!aba) return;
    aba.getProtections(SpreadsheetApp.ProtectionType.RANGE).forEach(function (p) {
      if (p.getDescription().indexOf('fórmula · ') === 0) p.remove();
    });
    aba.getDataRange().getFormulas().forEach(function (linha, i) {
      linha.forEach(function (formula, j) {
        if (!formula) return;
        var cel = aba.getRange(i + 1, j + 1);
        if (nome === 'FICHA' && livres.indexOf(cel.getA1Notation()) >= 0) return;
        var p = cel.protect();
        p.setDescription('fórmula · ' + nome + '!' + cel.getA1Notation());
        p.setWarningOnly(true);
        n++;
      });
    });
  });
  return n + ' célula(s)';
}

// =====================================================================
// GATILHO SIMPLES · roda sozinho, inclusive na cópia de cada jogador,
// e não pede autorização de ninguém.
// =====================================================================
function onEdit(e) {
  if (!e || !e.range) return;
  var aba = e.range.getSheet().getName();
  if (aba !== 'FICHA') return;
  var idx = indice();
  aplicarDelta_(e, idx);
  prenderTemp_(e, idx);
  marcarPericiasDoCaminho_(e, idx);
  trilhaDoCaminho_(e, idx);
  if (e.range.getA1Notation() === cel_(idx, 'origem')) notasDeGraca_(SpreadsheetApp.getActive(), idx);
}

/**
 * A Trilha que não é do Caminho novo volta para o texto de escolha. 17/09/2026, pedido do Mizuki: o
 * menu da Trilha já mostra só as do Caminho, mas a escolhida antes ficava na caixa. Trilha ainda não
 * escolhida fica como está.
 *
 * A conta mora no trilhaQueFica_, sem planilha em volta, e o regressao-delta.js roda ela no node.
 */
function trilhaQueFica_(tabela, caminho, trilha, vazio) {
  if (trilha === '' || trilha === vazio) return trilha;
  var dele = tabela.some(function (l) { return l.trilha === trilha && l.caminho === caminho; });
  return dele ? trilha : vazio;
}

function trilhaDoCaminho_(e, idx) {
  var cc = cel_(idx, 'caminho'), ct = cel_(idx, 'trilha');
  if (!cc || !ct || cc !== e.range.getA1Notation()) return;
  var ss = SpreadsheetApp.getActive();
  // a tabela de menus da DADOS: o cabeçalho tem "Trilha", "Caminho da Trilha" e "menu de Trilha", e a
  // primeira linha do menu é o texto de escolha
  var dados = ss.getSheetByName('DADOS').getDataRange().getValues();
  for (var r = 0; r + 1 < dados.length; r++) {
    var cT = dados[r].indexOf('Trilha'), cC = dados[r].indexOf('Caminho da Trilha');
    var cM = dados[r].indexOf('menu de Trilha');
    if (cT < 0 || cC < 0 || cM < 0) continue;
    var tabela = [];
    for (var l = r + 1; l < dados.length && dados[l][cT]; l++) {
      tabela.push({ trilha: String(dados[l][cT]), caminho: String(dados[l][cC]) });
    }
    var caixa = ss.getSheetByName('FICHA').getRange(ct);
    var antes = String(caixa.getValue());
    var fica = trilhaQueFica_(tabela, String(e.value || ''), antes, String(dados[r + 1][cM]));
    if (fica !== antes) caixa.setValue(fica);
    return;
  }
}

/**
 * As perícias fixas do Caminho, marcadas quando o jogador escolhe o Caminho. 17/09/2026, pedido do
 * Mizuki. O livro fixa duas perícias por Caminho e deixa ofício e Teste de Resistência à escolha, então
 * só perícia é marcada. As do Caminho de antes são desmarcadas, a não ser que o novo também as fixe.
 *
 * A conta mora no periciasDoCaminho_, sem planilha em volta, e o regressao-delta.js roda ela no node.
 */
function periciasDoCaminho_(tabela, novo, velho) {
  var fixas = function (nome) {
    var linha = tabela.filter(function (l) { return l.caminho === nome; })[0];
    return linha ? linha.pericias.filter(function (p) { return p; }) : [];
  };
  var marcar = fixas(novo);
  var desmarcar = fixas(velho).filter(function (p) { return marcar.indexOf(p) < 0; });
  return { marcar: marcar, desmarcar: desmarcar };
}

function marcarPericiasDoCaminho_(e, idx) {
  var cc = cel_(idx, 'caminho');
  if (!cc || cc !== e.range.getA1Notation()) return;
  var ss = SpreadsheetApp.getActive();
  // a tabela dos Caminhos da DADOS: a linha do cabeçalho tem "Caminho" e as colunas "perícia fixa"
  var dados = ss.getSheetByName('DADOS').getDataRange().getValues();
  var tabela = [];
  for (var r = 0; r < dados.length && !tabela.length; r++) {
    var c0 = dados[r].indexOf('Caminho');
    if (c0 < 0) continue;
    var cols = [];
    dados[r].forEach(function (v, c) { if (String(v).indexOf('perícia fixa') === 0) cols.push(c); });
    if (!cols.length) continue;
    for (var l = r + 1; l < dados.length && dados[l][c0]; l++) {
      tabela.push({ caminho: dados[l][c0], pericias: cols.map(function (c) { return dados[l][c]; }) });
    }
  }
  var plano = periciasDoCaminho_(tabela, e.value, e.oldValue);
  var ficha = ss.getSheetByName('FICHA');
  var vals = ficha.getDataRange().getValues();
  var poe = function (nome, marcado) {
    for (var i = 0; i < vals.length; i++) {
      var j = vals[i].map(function (v) { return String(v).trim(); }).indexOf(nome);
      // o treino fica duas colunas antes do nome, e é caixa de seleção
      if (j >= 2 && typeof vals[i][j - 2] === 'boolean') {
        ficha.getRange(i + 1, j - 1).setValue(marcado);
        return;
      }
    }
  };
  plano.desmarcar.forEach(function (p) { poe(p, false); });
  plano.marcar.forEach(function (p) { poe(p, true); });
}

/**
 * A conta da caixinha de +/-, sem planilha nenhuma em volta.
 *
 * Ela mora separada porque e o unico lugar do projeto onde duas decisoes se
 * encontram: a A4 (a caixinha) e a A2 (a temporaria gasta primeiro). O
 * regressao-delta.js roda esta funcao contra o exemplo publicado no
 * manual-temporario.md, e o Apps Script nao pode ser testado de fora.
 *
 * Perda come a temporaria antes de tocar a reserva. Ganho nao devolve
 * temporaria: ela e um extra por cima, e quem concede e a fonte, no campo
 * TEMP. Quem toma dano com `Rasga Escudo` -- que ignora a temporaria -- edita
 * a reserva na mao; a A4 mantem o atual editavel exatamente para isso.
 */
function aplicaPasso_(atual, max, temp, passo) {
  atual = Number(atual) || 0;
  max = Number(max) || 0;
  temp = Math.max(0, Number(temp) || 0);
  passo = Number(passo) || 0;

  var novo = atual;
  if (passo < 0) {
    var comido = Math.min(temp, -passo);
    temp = temp - comido;
    novo = atual - (-passo - comido);
  } else {
    novo = atual + passo;
  }
  return {
    atual: Math.max(0, max ? Math.min(novo, max) : novo),
    temp: temp
  };
}

/**
 * O teto do campo TEMP, sem planilha nenhuma em volta. É o B19.
 *
 * Decisão A2: a temporária tem teto de metade do máximo. A metade arredonda
 * para baixo, porque o manual arredonda contra quem ganha, e o que se ganha
 * nunca fica abaixo de 1. Campo vazio continua vazio, e sem máximo declarado
 * não há teto para aplicar.
 *
 * O "fica a maior" da A2 não mora aqui: quem digita a temporária pode estar
 * trocando de fonte ou zerando no fim da cena, e o script não sabe qual.
 */
function tetoTemp_(valor, max) {
  if (valor === '' || valor === null || valor === undefined) return valor;
  var v = Number(valor);
  if (isNaN(v)) return valor;
  v = Math.max(0, v);
  max = Number(max) || 0;
  if (max <= 0) return v;
  var teto = Math.max(1, Math.floor(max / 2));
  return Math.min(v, teto);
}

/** Prende no teto o TEMP digitado à mão. A caixinha de ± só desce a temporária. */
function prenderTemp_(e, idx) {
  var ficha = SpreadsheetApp.getActive().getSheetByName('FICHA');
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var ct = cel_(idx, r + '_temp');
    if (!ct || ct !== e.range.getA1Notation()) return;
    var antes = e.range.getValue();
    var depois = tetoTemp_(antes, ficha.getRange(cel_(idx, r + '_max')).getValue());
    if (depois !== antes) e.range.setValue(depois);
  });
}

/**
 * Decisão A4: digita -9 na caixinha, o script aplica no atual e limpa.
 * O atual continua editável à mão — sem sinal o gatilho não roda, e sem isso
 * a ficha viraria pedra no meio da sessão.
 *
 * Decisão A2: o passo negativo come a temporária antes da reserva, e o campo
 * TEMP desce junto. Sem isso a caixinha descontava direto da vida e a
 * temporária ficava parada na tela, valendo nada.
 */
function aplicarDelta_(e, idx) {
  var ficha = SpreadsheetApp.getActive().getSheetByName('FICHA');
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var cd = cel_(idx, r + '_delta');
    if (!cd || cd !== e.range.getA1Notation()) return;
    var passo = Number(e.range.getValue());
    if (!passo) return;
    var atual = ficha.getRange(cel_(idx, r));
    var ct = cel_(idx, r + '_temp');
    var temp = ct ? ficha.getRange(ct) : null;
    var antes = temp ? Math.max(0, Number(temp.getValue()) || 0) : 0;

    var fim = aplicaPasso_(atual.getValue(),
                           ficha.getRange(cel_(idx, r + '_max')).getValue(),
                           antes, passo);

    atual.setValue(fim.atual);
    if (temp && fim.temp !== antes) temp.setValue(fim.temp);
    e.range.clearContent();
  });
}

// =====================================================================
// O AUTOTESTE, para rodar de dentro do editor do Apps Script.
//
// O onEdit e gatilho simples: dispara sozinho ao digitar e nao se executa
// a mao -- chamado pelo seletor de funcao ele quebra, porque o `e` vem
// vazio. Entao o que se roda aqui e isto, que nao toca na planilha.
//
// Os mesmos casos moram no regressao-delta.js, que roda no node lendo os
// numeros do manual-temporario.md. Aqui eles estao escritos a mao de
// proposito: o Apps Script nao le o repositorio, e o que se quer saber no
// editor e se a colagem entrou, nao se a regra mudou.
// =====================================================================
function testeDelta() {
  var casos = [
    ['exemplo do manual (18 temp, 20 de dano)', [40, 40, 18, -20], 38, 0],
    ['dano menor que a temporaria',             [40, 40, 18,  -5], 40, 13],
    ['sem temporaria',                          [19, 19,  0,  -9], 10, 0],
    ['cura nao devolve temporaria',             [10, 19,  5,   4], 14, 5],
    ['cura nao passa do maximo',                [17, 19,  0,   9], 19, 0]
  ];
  var falhou = 0;
  casos.forEach(function (c) {
    var r = aplicaPasso_(c[1][0], c[1][1], c[1][2], c[1][3]);
    var ok = (r.atual === c[2] && r.temp === c[3]);
    if (!ok) falhou++;
    Logger.log((ok ? 'OK   ' : 'FALHA') + ' \u00b7 ' + c[0] +
               ' \u00b7 atual ' + r.atual + ' (esperado ' + c[2] + ')' +
               ' \u00b7 temp ' + r.temp + ' (esperado ' + c[3] + ')');
  });
  Logger.log(falhou ? (falhou + ' FALHA(S)') : 'as 5 passaram');
}

// O teto do campo TEMP, com casos do regressao-delta.js escritos à mão pelo
// mesmo motivo do testeDelta: aqui se quer saber se a colagem entrou.
function testeTeto() {
  var casos = [
    ['exemplo do manual (27 com máximo 40)', [27, 40], 20],
    ['abaixo do teto',                       [12, 40], 12],
    ['máximo ímpar arredonda para baixo',    [99, 23], 11],
    ['campo vazio continua vazio',           ['', 40], ''],
    ['sem máximo não há teto',               [27, 0], 27]
  ];
  var falhou = 0;
  casos.forEach(function (c) {
    var r = tetoTemp_(c[1][0], c[1][1]);
    var ok = (r === c[2]);
    if (!ok) falhou++;
    Logger.log((ok ? 'OK   ' : 'FALHA') + ' \u00b7 ' + c[0] +
               ' \u00b7 ' + r + ' (esperado ' + c[2] + ')');
  });
  Logger.log(falhou ? (falhou + ' FALHA(S)') : 'as 5 passaram');
}
