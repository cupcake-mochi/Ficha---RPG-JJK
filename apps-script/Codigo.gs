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
 *
 * 19/09/2026, pedido do Mizuki testando no Sheets, depois da Bateria de Cores: o vermelho e o
 * âmbar são cores FIXAS, de propósito — a decisão A5 não muda aviso de estado por tema, senão
 * "vida caindo" deixava de ter uma cor só. Mas só trocar a FONTE pra um vermelho fixo, em cima de
 * um FUNDO que muda de tema pra tema, dava exatamente o problema que ele apontou: nalgumas
 * paletas claras/rosadas o vermelho da fonte quase se perde dentro do fundo, porque ninguém
 * garantia contraste entre os dois. Pro vermelho (o tier mais grave, "passou da conta"), o
 * conserto força FUNDO E FONTE junto — vermelho sólido com fonte branca —, pra não depender do
 * tema por trás pra ficar legível. O âmbar continua só na fonte, porque é aviso mais brando.
 */
function corDeEstado_(ss, idx) {
  var ficha = ss.getSheetByName('FICHA');
  var regras = [];
  ['vida', 'energia', 'integridade'].forEach(function (r) {
    var atual = idx[r], max = idx[r + '_max'];
    if (!atual || !max) return;
    var alvo = ficha.getRange(cel_(idx, r));
    var formula25 = '=AND(N(' + max + ')>0,' + atual + '/' + max + '<=0.25)';
    var formula50 = '=AND(N(' + max + ')>0,' + atual + '/' + max + '<=0.5)';
    regras.push(SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied(formula25)
      .setBackground('#C2334D').setFontColor('#FFFFFF').setRanges([alvo]).build());
    regras.push(SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied(formula50)
      .setFontColor('#D89B3A').setRanges([alvo]).build());
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
        .whenTextContains(trecho)
        .setBackground('#C2334D').setFontColor('#FFFFFF').setRanges(avisos).build());
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
                            'passar nas duas, as duas caixas avisam. Guia, Emanador e Evocador podem ' +
                            'trocar 2 perícias por treino numa arma, até duas vezes: é a caixa de ' +
                            'Treinamento em Armas que desconta.',
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
    'trilha': 'O menu mostra só as Trilhas do Caminho escolhido.',
    'treinado em armas': 'Automático pelo Caminho, sem escolha: Bastião e Vanguarda treinam todas ' +
                         'as armas; Guia, Emanador e Evocador treinam só Arma de Fogo e Balestra.',
    'nivel': 'Editável a qualquer hora, sem aviso. Digitar XP na caixa ao lado calcula e escreve o ' +
             'nível sozinho, pela curva do capítulo 18 — mas quem não usa XP sobe aqui na mão.',
    'xp': 'Some o total acumulado, não o gasto na última missão. Ao digitar aqui, o nível ao lado ' +
         'sobe sozinho pra curva do capítulo 18. Apagar esta caixa não mexe no nível.',
    'trocou por arma': 'Só vale pra Guia, Emanador e Evocador. Cada troca é 2 das 5 perícias ' +
                       'livres do Caminho por treino numa arma específica — não a categoria, não ' +
                       'o tipo, uma arma da lista. Pode repetir até 2 vezes.',
    'grupo de arma da trilha': 'Só a Empunhadura do Arremate (Emanador, nível 2) preenche sozinha: ' +
                               'um grupo de arma à escolha, treinado, com o acerto e o dano por ' +
                               'Inteligência ou Essência. Qual grupo é você quem escreve.'
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

/**
 * O Spreadsheet Service falha de vez em quando no meio de um construir() longo -- "Service
 * Spreadsheet failed", erro transitório do Google por causa da fila de operações, não do código.
 * 17/09/2026, achado do Mizuki: quebrou bem na protegerFormulas_, que é a mais pesada (uma
 * chamada por célula de fórmula). Tenta de novo com uma pausa curta antes de desistir.
 */
function _comRetentativa_(fn, tentativas) {
  tentativas = tentativas || 4;
  for (var i = 0; i < tentativas; i++) {
    try {
      return fn();
    } catch (e) {
      if (i === tentativas - 1) throw e;
      Utilities.sleep(500 * (i + 1));
    }
  }
}

function protegerFormulas_(ss, idx) {
  SpreadsheetApp.flush();                        // esvazia a fila antes de começar a pesada
  var livres = LIVRES_DA_TRAVA.map(function (k) { return cel_(idx, k); });
  var n = 0;
  ['FICHA', 'CARTEIRA'].forEach(function (nome) {
    var aba = ss.getSheetByName(nome);
    if (!aba) return;
    _comRetentativa_(function () {
      aba.getProtections(SpreadsheetApp.ProtectionType.RANGE).forEach(function (p) {
        if (p.getDescription().indexOf('fórmula · ') === 0) p.remove();
      });
    });
    aba.getDataRange().getFormulas().forEach(function (linha, i) {
      linha.forEach(function (formula, j) {
        if (!formula) return;
        var cel = aba.getRange(i + 1, j + 1);
        if (nome === 'FICHA' && livres.indexOf(cel.getA1Notation()) >= 0) return;
        _comRetentativa_(function () {
          var p = cel.protect();
          p.setDescription('fórmula · ' + nome + '!' + cel.getA1Notation());
          p.setWarningOnly(true);
        });
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
  // A troca de paleta NÃO passa mais por aqui — ela precisa de mais que os 30 segundos que um
  // onEdit simples tem, e mora num gatilho instalável à parte. Ver instalarGatilhoPaleta_.
  if (aba !== 'FICHA') return;
  var idx = indice();
  aplicarDelta_(e, idx);
  prenderTemp_(e, idx);
  marcarPericiasDoCaminho_(e, idx);
  trilhaDoCaminho_(e, idx);
  nivelPelaXP_(e, idx);
  grupoDeArmaDaTrilha_(e, idx);
  trocaArmaDoCaminho_(e, idx);
  if (e.range.getA1Notation() === cel_(idx, 'origem')) notasDeGraca_(SpreadsheetApp.getActive(), idx);
}

/**
 * A caixa "Trocou por arma?" fica presa no valor de um Caminho anterior quando o jogador muda de
 * Caminho — o desconto já para de valer sozinho (só entra pros três não-marciais), mas a caixa
 * continuava mostrando "1 arma" ou "2 armas" mesmo depois de virar Bastião ou Vanguarda, o que
 * confunde. 17/09/2026, achado do Mizuki: volta pra "Não trocou" toda vez que o Caminho muda.
 */
function trocaArmaDoCaminho_(e, idx) {
  var cc = cel_(idx, 'caminho'), ca = cel_(idx, 'trocou por arma');
  if (!cc || !ca || cc !== e.range.getA1Notation()) return;
  e.range.getSheet().getRange(ca).setValue('Não trocou');
}

/**
 * A única Trilha dos três Caminhos não-marciais que dá treino de arma: a Empunhadura do Arremate
 * (Emanador), nível 2. Ela concede um grupo de arma à escolha, treinado, com o acerto e o dano por
 * Inteligência ou Essência — mas qual grupo é decisão do jogador, então a ficha só avisa e deixa a
 * caixa livre pra ele escrever. 17/09/2026, pedido do Mizuki: aproveita a linha que tinha sobrado
 * no Treinamento em Armas. Só preenche se a caixa estiver vazia, pra não apagar o que já foi
 * escrito; trocar de Trilha de novo não limpa o que ficou.
 */
function grupoDeArmaDaTrilha_(e, idx) {
  var ct = cel_(idx, 'trilha'), cg = cel_(idx, 'grupo de arma da trilha');
  if (!ct || !cg || ct !== e.range.getA1Notation()) return;
  if (String(e.value || '') !== 'Arremate') return;
  var cc = cel_(idx, 'caminho');
  if (!cc || String(e.range.getSheet().getRange(cc).getValue()) !== 'Emanador') return;
  var alvo = e.range.getSheet().getRange(cg);
  if (String(alvo.getValue() || '') === '') alvo.setValue('Escolha o grupo de arma (Empunhadura)');
}

/**
 * O nível sobe sozinho quando o XP muda, pela curva do capítulo 18: acha o maior nível cujo XP
 * acumulado cabe no que foi digitado, e põe o valor solto — sem fórmula, sem trava — porque mesa
 * que não usa XP sobe de nível na mão, e isso não pode ficar bloqueado. 17/09/2026, pedido do Mizuki.
 * Apagar a caixa de XP não mexe no nível: só some o número se alguém digitar outro no lugar.
 *
 * A tabela mora na DADOS, sob os rótulos "nível" e "xp acumulado", e quem escreve é a
 * ficha_automatica.py, a partir da curva de custo por degrau do catálogo (capítulo 18 do manual).
 */
function nivelPelaXP_(e, idx) {
  var cx = cel_(idx, 'xp'), cn = cel_(idx, 'nivel');
  if (!cx || !cn || cx !== e.range.getA1Notation()) return;
  if (e.value === undefined || e.value === '') return;
  var xp = Number(e.value);
  if (isNaN(xp)) return;
  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS').getDataRange().getValues();
  for (var r = 0; r + 1 < dados.length; r++) {
    var cNiv = dados[r].indexOf('nível'), cXp = dados[r].indexOf('xp acumulado');
    if (cNiv < 0 || cXp < 0) continue;
    var melhor = null;
    for (var i = r + 1; i < dados.length && dados[i][cNiv] !== ''; i++) {
      if (Number(dados[i][cXp]) <= xp) melhor = dados[i][cNiv];
    }
    if (melhor !== null) e.range.getSheet().getRange(cn).setValue(melhor);
    return;
  }
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
        var cel = ficha.getRange(i + 1, j - 1);
        cel.setValue(marcado);
        // 17/09/2026, pedido do Mizuki: a nota diz de onde veio, pra nao confundir com marcada a mao
        cel.setNote(marcado ? 'Treinado pelo Caminho ' + e.value : '');
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

/**
 * A BATERIA DE CORES — 17-18/09/2026, pedido do Mizuki.
 *
 * 61 temas, cada um em versão Claro e Escuro — 122 escolhas no menu da
 * CARTEIRA. As cores vêm de paletas reais (Color Hunt, as mais curtidas) e
 * de pesquisa cultural — festas do ano, ocidentais e asiáticas; yokai,
 * lendas e criaturas da Ásia e do próprio anime —, derivadas e conferidas
 * contra o contraste WCAG pelo `medidas/paletas-grandes/derivar.py` do
 * repositório. Os treze papéis por tema são os nomes do `ficha/estilo.py`
 * (FUNDO, PAINEL, PAINEL_ALTO, LINHA, TEXTO, TEXTO_FRACO, TINTA, PAPEL,
 * PAINEL_BAIXO, BLOCO) mais dois que a ficha usa sem nomear — o "3B3360"
 * dos menus grandes (MENU_GRANDE) e o "8A7EC4" do fio embaixo do valor
 * (REGUA) —, e o ACENTO, que não tinha dono antes e passa a pintar a FAIXA
 * dos títulos de seção.
 *
 * O que NÃO muda: âmbar e vermelho (decisão A5, em corDeEstado_) continuam
 * fixos em toda paleta, porque são aviso de estado — vida caindo —, não
 * gosto de quem lê. O osso (a terceira cor da A5, "vida cheia") saiu desse
 * grupo em 18/09/2026: testando no Sheets, ele apareceu como cor PADRÃO de
 * texto (não de vida) em boa parte da ficha, e numa paleta clara ficava
 * ilegível sobre fundo claro. Ele agora é resolvido por PAPEL DE FUNDO —
 * `osso_por_papel`, dentro de cada entrada do PALETAS, com o mesmo contraste
 * WCAG das outras treze — porque uma célula em osso pode estar sobre fundo,
 * painel, menu_grande ou acento, cada um com contraste diferente; ver
 * `resolve_osso_por_papel` no derivar.py e o uso em repintarPaleta_.
 */
var PALETAS = {
  "Mizuki": {
    "claro": {
      "fundo": "FDF2F7",
      "painel": "FAD6E7",
      "painel_alto": "F5B7D4",
      "linha": "F0BCD4",
      "texto": "1E1320",
      "texto_fraco": "2D0A1A",
      "acento": "E32175",
      "tinta": "FBE4EF",
      "papel": "FDEDF4",
      "painel_baixo": "FCE7F1",
      "bloco": "C22B71",
      "menu_grande": "FFB6D8",
      "regua": "CB015E",
      "osso_por_papel": {
        "fundo": "1E1320",
        "painel": "1E1320",
        "painel_alto": "1E1320",
        "linha": "1E1320",
        "texto": "FBE4EF",
        "texto_fraco": "FBE4EF",
        "acento": "000000",
        "tinta": "1E1320",
        "papel": "1E1320",
        "painel_baixo": "1E1320",
        "bloco": "FFFFFF",
        "menu_grande": "1E1320",
        "regua": "FBE4EF"
      },
      "aviso_por_papel": {
        "fundo": "D71B6D",
        "painel": "BD185F",
        "painel_alto": "A21452",
        "painel_baixo": "CC1A67",
        "papel": "D01A69",
        "menu_grande": "A51553",
        "tinta": "C81965",
        "acento": "13020A"
      }
    },
    "escuro": {
      "fundo": "1B111D",
      "painel": "311E33",
      "painel_alto": "492D4D",
      "linha": "64163B",
      "texto": "FBE4EF",
      "texto_fraco": "F1BFD6",
      "acento": "F8C7DC",
      "tinta": "150817",
      "papel": "251727",
      "painel_baixo": "301E33",
      "bloco": "D44085",
      "menu_grande": "46244B",
      "regua": "B377BB",
      "osso_por_papel": {
        "fundo": "FBE4EF",
        "painel": "FBE4EF",
        "painel_alto": "FBE4EF",
        "linha": "FBE4EF",
        "texto": "1E1320",
        "texto_fraco": "1E1320",
        "acento": "1E1320",
        "tinta": "FBE4EF",
        "papel": "FBE4EF",
        "painel_baixo": "FBE4EF",
        "bloco": "000000",
        "menu_grande": "FBE4EF",
        "regua": "1E1320"
      },
      "aviso_por_papel": {
        "fundo": "F8C7DC",
        "painel": "F8C7DC",
        "painel_alto": "F8C7DC",
        "painel_baixo": "F8C7DC",
        "papel": "F8C7DC",
        "menu_grande": "F8C7DC",
        "tinta": "F8C7DC",
        "acento": "AC1656"
      }
    }
  },
  "Noite": {
    "claro": {
      "fundo": "F7F5F9",
      "painel": "E8E2EE",
      "painel_alto": "D6CBE1",
      "linha": "D6D0DC",
      "texto": "151122",
      "texto_fraco": "1B1720",
      "acento": "3B3360",
      "tinta": "F0E7F8",
      "papel": "F5F2F7",
      "painel_baixo": "F2EEF5",
      "bloco": "756588",
      "menu_grande": "DACDE8",
      "regua": "66428A",
      "osso_por_papel": {
        "fundo": "151122",
        "painel": "151122",
        "painel_alto": "151122",
        "linha": "151122",
        "texto": "F0ECF4",
        "texto_fraco": "F0ECF4",
        "acento": "F0ECF4",
        "tinta": "151122",
        "papel": "151122",
        "painel_baixo": "151122",
        "bloco": "F0ECF4",
        "menu_grande": "151122",
        "regua": "F0ECF4"
      },
      "aviso_por_papel": {
        "fundo": "3B3360",
        "painel": "3B3360",
        "painel_alto": "3B3360",
        "painel_baixo": "3B3360",
        "papel": "3B3360",
        "menu_grande": "3B3360",
        "tinta": "3B3360",
        "acento": "A8A0CD"
      }
    },
    "escuro": {
      "fundo": "13101E",
      "painel": "211C36",
      "painel_alto": "322A51",
      "linha": "3C3446",
      "texto": "F0ECF4",
      "texto_fraco": "D7D2DE",
      "acento": "7569AF",
      "tinta": "0B0817",
      "papel": "191529",
      "painel_baixo": "211B35",
      "bloco": "89799C",
      "menu_grande": "29204F",
      "regua": "816FC3",
      "osso_por_papel": {
        "fundo": "F0ECF4",
        "painel": "F0ECF4",
        "painel_alto": "F0ECF4",
        "linha": "F0ECF4",
        "texto": "151122",
        "texto_fraco": "151122",
        "acento": "FFFFFF",
        "tinta": "F0ECF4",
        "papel": "F0ECF4",
        "painel_baixo": "F0ECF4",
        "bloco": "151122",
        "menu_grande": "F0ECF4",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "8175B6",
        "painel": "8A7FBB",
        "painel_alto": "9A91C4",
        "painel_baixo": "8A7FBB",
        "papel": "8378B7",
        "menu_grande": "9187BF",
        "tinta": "7C70B3",
        "acento": "F9F8FB"
      }
    }
  },
  "Blush": {
    "claro": {
      "fundo": "FFF0F0",
      "painel": "FFD1D1",
      "painel_alto": "FFADAD",
      "linha": "E8C4CB",
      "texto": "1D1616",
      "texto_fraco": "280F14",
      "acento": "D64024",
      "tinta": "FFE0E0",
      "papel": "FFEAEA",
      "painel_baixo": "FFE4E4",
      "bloco": "AB4257",
      "menu_grande": "FFB6B6",
      "regua": "CC0000",
      "osso_por_papel": {
        "fundo": "280F14",
        "painel": "280F14",
        "painel_alto": "280F14",
        "linha": "280F14",
        "texto": "FFE0E0",
        "texto_fraco": "FFE0E0",
        "acento": "000000",
        "tinta": "280F14",
        "papel": "280F14",
        "painel_baixo": "280F14",
        "bloco": "FFE0E0",
        "menu_grande": "280F14",
        "regua": "FFE0E0"
      },
      "aviso_por_papel": {
        "fundo": "C83C22",
        "painel": "AF341D",
        "painel_alto": "922C19",
        "painel_baixo": "BD3920",
        "papel": "C43B21",
        "menu_grande": "992E1A",
        "tinta": "BD3920",
        "acento": "090301"
      }
    },
    "escuro": {
      "fundo": "1A1414",
      "painel": "2E2424",
      "painel_alto": "453636",
      "linha": "58222D",
      "texto": "FFE0E0",
      "texto_fraco": "E9C6CD",
      "acento": "F7D6D0",
      "tinta": "170808",
      "papel": "231B1B",
      "painel_baixo": "2D2323",
      "bloco": "BE576B",
      "menu_grande": "402E2E",
      "regua": "A58D8D",
      "osso_por_papel": {
        "fundo": "FFE0E0",
        "painel": "FFE0E0",
        "painel_alto": "FFE0E0",
        "linha": "FFE0E0",
        "texto": "280F14",
        "texto_fraco": "280F14",
        "acento": "280F14",
        "tinta": "FFE0E0",
        "papel": "FFE0E0",
        "painel_baixo": "FFE0E0",
        "bloco": "000000",
        "menu_grande": "FFE0E0",
        "regua": "280F14"
      },
      "aviso_por_papel": {
        "fundo": "F7D6D0",
        "painel": "F7D6D0",
        "painel_alto": "F7D6D0",
        "painel_baixo": "F7D6D0",
        "papel": "F7D6D0",
        "menu_grande": "F7D6D0",
        "tinta": "F7D6D0",
        "acento": "AF341E"
      }
    }
  },
  "Crepúsculo": {
    "claro": {
      "fundo": "FFFBF0",
      "painel": "FFF2D1",
      "painel_alto": "FFE8AD",
      "linha": "E8C4D1",
      "texto": "270C1E",
      "texto_fraco": "280F18",
      "acento": "DB5757",
      "tinta": "FFF6E0",
      "papel": "FFF9EA",
      "painel_baixo": "FFF7E4",
      "bloco": "AB4266",
      "menu_grande": "FFEAB6",
      "regua": "CC9300",
      "osso_por_papel": {
        "fundo": "270C1E",
        "painel": "270C1E",
        "painel_alto": "270C1E",
        "linha": "270C1E",
        "texto": "FFF6E0",
        "texto_fraco": "FFF6E0",
        "acento": "270C1E",
        "tinta": "270C1E",
        "papel": "270C1E",
        "painel_baixo": "270C1E",
        "bloco": "FFF6E0",
        "menu_grande": "270C1E",
        "regua": "270C1E"
      },
      "aviso_por_papel": {
        "fundo": "D53A3A",
        "painel": "D22D2D",
        "painel_alto": "C52A2A",
        "painel_baixo": "D43535",
        "papel": "D43535",
        "menu_grande": "CA2B2B",
        "tinta": "D33131",
        "acento": "370C0C"
      }
    },
    "escuro": {
      "fundo": "230B1B",
      "painel": "3F1330",
      "painel_alto": "5E1C47",
      "linha": "582235",
      "texto": "FFF6E0",
      "texto_fraco": "E9C6D2",
      "acento": "EA9D9D",
      "tinta": "180712",
      "papel": "300E24",
      "painel_baixo": "3E132F",
      "bloco": "BE577B",
      "menu_grande": "5F0F43",
      "regua": "E052AF",
      "osso_por_papel": {
        "fundo": "FFF6E0",
        "painel": "FFF6E0",
        "painel_alto": "FFF6E0",
        "linha": "FFF6E0",
        "texto": "270C1E",
        "texto_fraco": "270C1E",
        "acento": "270C1E",
        "tinta": "FFF6E0",
        "papel": "FFF6E0",
        "painel_baixo": "FFF6E0",
        "bloco": "000000",
        "menu_grande": "FFF6E0",
        "regua": "270C1E"
      },
      "aviso_por_papel": {
        "fundo": "EA9D9D",
        "painel": "EA9D9D",
        "painel_alto": "EA9D9D",
        "painel_baixo": "EA9D9D",
        "papel": "EA9D9D",
        "menu_grande": "EA9D9D",
        "tinta": "EA9D9D",
        "acento": "811C1C"
      }
    }
  },
  "Alfazema": {
    "claro": {
      "fundo": "FEFBF0",
      "painel": "FDF4D3",
      "painel_alto": "FCECB1",
      "linha": "D6CEDF",
      "texto": "1D1616",
      "texto_fraco": "1B1621",
      "acento": "4489C4",
      "tinta": "FEF8E2",
      "papel": "FEFAEB",
      "painel_baixo": "FEF9E5",
      "bloco": "755D90",
      "menu_grande": "FFEFB6",
      "regua": "CCA100",
      "osso_por_papel": {
        "fundo": "1D1616",
        "painel": "1D1616",
        "painel_alto": "1D1616",
        "linha": "1D1616",
        "texto": "FEF8E2",
        "texto_fraco": "FEF8E2",
        "acento": "1D1616",
        "tinta": "1D1616",
        "papel": "1D1616",
        "painel_baixo": "1D1616",
        "bloco": "FEF8E2",
        "menu_grande": "1D1616",
        "regua": "1D1616"
      },
      "aviso_por_papel": {
        "fundo": "3777AE",
        "painel": "3572A7",
        "painel_alto": "336EA1",
        "painel_baixo": "3777AE",
        "papel": "3777AE",
        "menu_grande": "3470A4",
        "tinta": "3675AB",
        "acento": "0E1E2B"
      }
    },
    "escuro": {
      "fundo": "1A1313",
      "painel": "2F2323",
      "painel_alto": "473434",
      "linha": "3C304A",
      "texto": "FEF8E2",
      "texto_fraco": "D7CFE0",
      "acento": "B0CDE6",
      "tinta": "170808",
      "papel": "241A1A",
      "painel_baixo": "2E2222",
      "bloco": "8972A3",
      "menu_grande": "432C2C",
      "regua": "AD8585",
      "osso_por_papel": {
        "fundo": "FEF8E2",
        "painel": "FEF8E2",
        "painel_alto": "FEF8E2",
        "linha": "FEF8E2",
        "texto": "1D1616",
        "texto_fraco": "1D1616",
        "acento": "1D1616",
        "tinta": "FEF8E2",
        "papel": "FEF8E2",
        "painel_baixo": "FEF8E2",
        "bloco": "000000",
        "menu_grande": "FEF8E2",
        "regua": "1D1616"
      },
      "aviso_por_papel": {
        "fundo": "B0CDE6",
        "painel": "B0CDE6",
        "painel_alto": "B0CDE6",
        "painel_baixo": "B0CDE6",
        "papel": "B0CDE6",
        "menu_grande": "B0CDE6",
        "tinta": "B0CDE6",
        "acento": "295881"
      }
    }
  },
  "Meia-Noite": {
    "claro": {
      "fundo": "F1F7FE",
      "painel": "D4E8FC",
      "painel_alto": "B2D6FA",
      "linha": "B7BEF5",
      "texto": "060F2D",
      "texto_fraco": "070B30",
      "acento": "4A6FFF",
      "tinta": "E2F0FD",
      "papel": "ECF5FE",
      "painel_baixo": "E6F1FD",
      "bloco": "1D2FD0",
      "menu_grande": "B6DAFF",
      "regua": "0065CC",
      "osso_por_papel": {
        "fundo": "070B30",
        "painel": "070B30",
        "painel_alto": "070B30",
        "linha": "070B30",
        "texto": "E2F0FD",
        "texto_fraco": "E2F0FD",
        "acento": "070B30",
        "tinta": "070B30",
        "papel": "070B30",
        "painel_baixo": "070B30",
        "bloco": "E2F0FD",
        "menu_grande": "070B30",
        "regua": "E2F0FD"
      },
      "aviso_por_papel": {
        "fundo": "345EFF",
        "painel": "2450FF",
        "painel_alto": "083BFF",
        "painel_baixo": "2F59FF",
        "papel": "345EFF",
        "menu_grande": "0E3FFF",
        "tinta": "2F59FF",
        "acento": "000B37"
      }
    },
    "escuro": {
      "fundo": "060D28",
      "painel": "0A1748",
      "painel_alto": "0F236B",
      "linha": "0F186B",
      "texto": "E2F0FD",
      "texto_fraco": "BAC0F5",
      "acento": "7692FF",
      "tinta": "04091B",
      "papel": "081236",
      "painel_baixo": "0A1746",
      "bloco": "3345E2",
      "menu_grande": "00186E",
      "regua": "3561FD",
      "osso_por_papel": {
        "fundo": "E2F0FD",
        "painel": "E2F0FD",
        "painel_alto": "E2F0FD",
        "linha": "E2F0FD",
        "texto": "070B30",
        "texto_fraco": "070B30",
        "acento": "070B30",
        "tinta": "E2F0FD",
        "papel": "E2F0FD",
        "painel_baixo": "E2F0FD",
        "bloco": "E2F0FD",
        "menu_grande": "E2F0FD",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "7692FF",
        "painel": "7692FF",
        "painel_alto": "7692FF",
        "painel_baixo": "7692FF",
        "papel": "7692FF",
        "menu_grande": "7692FF",
        "tinta": "7692FF",
        "acento": "001E95"
      }
    }
  },
  "Pôr do Sol": {
    "claro": {
      "fundo": "FFFBF0",
      "painel": "FFF3D1",
      "painel_alto": "FFEAAD",
      "linha": "FFE6AD",
      "texto": "330000",
      "texto_fraco": "372600",
      "acento": "DA6000",
      "tinta": "FFF7E0",
      "papel": "FFFAEA",
      "painel_baixo": "FFF8E4",
      "bloco": "EDA400",
      "menu_grande": "FFECB6",
      "regua": "CC9800",
      "osso_por_papel": {
        "fundo": "330000",
        "painel": "330000",
        "painel_alto": "330000",
        "linha": "330000",
        "texto": "FFF7E0",
        "texto_fraco": "FFF7E0",
        "acento": "330000",
        "tinta": "330000",
        "papel": "330000",
        "painel_baixo": "330000",
        "bloco": "330000",
        "menu_grande": "330000",
        "regua": "330000"
      },
      "aviso_por_papel": {
        "fundo": "BD5300",
        "painel": "B65000",
        "painel_alto": "AE4D00",
        "painel_baixo": "B95200",
        "papel": "BD5300",
        "menu_grande": "B24E00",
        "tinta": "B95200",
        "acento": "331600"
      }
    },
    "escuro": {
      "fundo": "2E0000",
      "painel": "520000",
      "painel_alto": "7A0000",
      "linha": "7A5500",
      "texto": "FFF7E0",
      "texto_fraco": "FFE7B0",
      "acento": "FFA259",
      "tinta": "1F0000",
      "papel": "3E0000",
      "painel_baixo": "500000",
      "bloco": "FFB716",
      "menu_grande": "6E0000",
      "regua": "FF3333",
      "osso_por_papel": {
        "fundo": "FFF7E0",
        "painel": "FFF7E0",
        "painel_alto": "FFF7E0",
        "linha": "FFF7E0",
        "texto": "330000",
        "texto_fraco": "330000",
        "acento": "330000",
        "tinta": "FFF7E0",
        "papel": "FFF7E0",
        "painel_baixo": "FFF7E0",
        "bloco": "330000",
        "menu_grande": "FFF7E0",
        "regua": "330000"
      },
      "aviso_por_papel": {
        "fundo": "FFA259",
        "painel": "FFA259",
        "painel_alto": "FFA259",
        "painel_baixo": "FFA259",
        "papel": "FFA259",
        "menu_grande": "FFA259",
        "tinta": "FFA259",
        "acento": "783500"
      }
    }
  },
  "Sálvia": {
    "claro": {
      "fundo": "FBF8F4",
      "painel": "F2EADE",
      "painel_alto": "E8D9C5",
      "linha": "DBD1D1",
      "texto": "1B1E15",
      "texto_fraco": "1F1818",
      "acento": "997B4E",
      "tinta": "F8F1E7",
      "papel": "F9F5F0",
      "painel_baixo": "F7F3EC",
      "bloco": "856868",
      "menu_grande": "F0DDC5",
      "regua": "9F6F2D",
      "osso_por_papel": {
        "fundo": "1F1818",
        "painel": "1F1818",
        "painel_alto": "1F1818",
        "linha": "1F1818",
        "texto": "F6F1E9",
        "texto_fraco": "F6F1E9",
        "acento": "000000",
        "tinta": "1F1818",
        "papel": "1F1818",
        "painel_baixo": "1F1818",
        "bloco": "FFFFFF",
        "menu_grande": "1F1818",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "876D45",
        "painel": "7F6641",
        "painel_alto": "735C3A",
        "painel_baixo": "856B44",
        "papel": "856B44",
        "menu_grande": "755E3C",
        "tinta": "826942",
        "acento": "19140D"
      }
    },
    "escuro": {
      "fundo": "181B13",
      "painel": "2B3022",
      "painel_alto": "414832",
      "linha": "453636",
      "texto": "F6F1E9",
      "texto_fraco": "DCD3D3",
      "acento": "EAE2D6",
      "tinta": "121708",
      "papel": "212519",
      "painel_baixo": "2A2F21",
      "bloco": "987C7C",
      "menu_grande": "3C442A",
      "regua": "A1B181",
      "osso_por_papel": {
        "fundo": "F6F1E9",
        "painel": "F6F1E9",
        "painel_alto": "F6F1E9",
        "linha": "F6F1E9",
        "texto": "1F1818",
        "texto_fraco": "1F1818",
        "acento": "1F1818",
        "tinta": "F6F1E9",
        "papel": "F6F1E9",
        "painel_baixo": "F6F1E9",
        "bloco": "1F1818",
        "menu_grande": "F6F1E9",
        "regua": "1F1818"
      },
      "aviso_por_papel": {
        "fundo": "EAE2D6",
        "painel": "EAE2D6",
        "painel_alto": "EAE2D6",
        "painel_baixo": "EAE2D6",
        "papel": "EAE2D6",
        "menu_grande": "EAE2D6",
        "tinta": "EAE2D6",
        "acento": "775F3D"
      }
    }
  },
  "Recife": {
    "claro": {
      "fundo": "F1FEFE",
      "painel": "D4FCFB",
      "painel_alto": "B3F9F8",
      "linha": "C1EAEB",
      "texto": "2E0505",
      "texto_fraco": "0D292A",
      "acento": "ED4747",
      "tinta": "E3FDFC",
      "papel": "ECFDFD",
      "painel_baixo": "E6FDFD",
      "bloco": "3AB1B4",
      "menu_grande": "B6FFFE",
      "regua": "00CCC8",
      "osso_por_papel": {
        "fundo": "2E0505",
        "painel": "2E0505",
        "painel_alto": "2E0505",
        "linha": "2E0505",
        "texto": "E3FDFC",
        "texto_fraco": "E3FDFC",
        "acento": "2E0505",
        "tinta": "2E0505",
        "papel": "2E0505",
        "painel_baixo": "2E0505",
        "bloco": "2E0505",
        "menu_grande": "2E0505",
        "regua": "2E0505"
      },
      "aviso_por_papel": {
        "fundo": "E51616",
        "painel": "DC1515",
        "painel_alto": "D21515",
        "painel_baixo": "E01616",
        "papel": "E01616",
        "menu_grande": "D71515",
        "tinta": "E01616",
        "acento": "3D0606"
      }
    },
    "escuro": {
      "fundo": "290505",
      "painel": "490909",
      "painel_alto": "6D0D0D",
      "linha": "1E5C5D",
      "texto": "E3FDFC",
      "texto_fraco": "C4EBEC",
      "acento": "F7ADAD",
      "tinta": "1B0303",
      "papel": "370707",
      "painel_baixo": "480808",
      "bloco": "4FC4C6",
      "menu_grande": "6E0000",
      "regua": "FF3333",
      "osso_por_papel": {
        "fundo": "E3FDFC",
        "painel": "E3FDFC",
        "painel_alto": "E3FDFC",
        "linha": "E3FDFC",
        "texto": "2E0505",
        "texto_fraco": "2E0505",
        "acento": "2E0505",
        "tinta": "E3FDFC",
        "papel": "E3FDFC",
        "painel_baixo": "E3FDFC",
        "bloco": "2E0505",
        "menu_grande": "E3FDFC",
        "regua": "2E0505"
      },
      "aviso_por_papel": {
        "fundo": "F7ADAD",
        "painel": "F7ADAD",
        "painel_alto": "F7ADAD",
        "painel_baixo": "F7ADAD",
        "papel": "F7ADAD",
        "menu_grande": "F7ADAD",
        "tinta": "F7ADAD",
        "acento": "9F1010"
      }
    }
  },
  "Vinho": {
    "claro": {
      "fundo": "FFF8F0",
      "painel": "FFEAD1",
      "painel_alto": "FFD9AD",
      "linha": "EDD9C0",
      "texto": "33000D",
      "texto_fraco": "2B1E0C",
      "acento": "D45060",
      "tinta": "FFF1E0",
      "papel": "FFF5EA",
      "painel_baixo": "FFF3E4",
      "bloco": "B87F35",
      "menu_grande": "FFDDB6",
      "regua": "CC6E00",
      "osso_por_papel": {
        "fundo": "33000D",
        "painel": "33000D",
        "painel_alto": "33000D",
        "linha": "33000D",
        "texto": "FFF1E0",
        "texto_fraco": "FFF1E0",
        "acento": "000000",
        "tinta": "33000D",
        "papel": "33000D",
        "painel_baixo": "33000D",
        "bloco": "33000D",
        "menu_grande": "33000D",
        "regua": "33000D"
      },
      "aviso_por_papel": {
        "fundo": "CF3C4E",
        "painel": "C73143",
        "painel_alto": "B82D3E",
        "painel_baixo": "CD3547",
        "papel": "CE394B",
        "menu_grande": "BC2E3F",
        "tinta": "CD3547",
        "acento": "270A0D"
      }
    },
    "escuro": {
      "fundo": "2E000B",
      "painel": "520014",
      "painel_alto": "7A001F",
      "linha": "5F421B",
      "texto": "FFF1E0",
      "texto_fraco": "EEDBC2",
      "acento": "D45060",
      "tinta": "1F0008",
      "papel": "3E000F",
      "painel_baixo": "500014",
      "bloco": "CB934A",
      "menu_grande": "6E001C",
      "regua": "FF3366",
      "osso_por_papel": {
        "fundo": "FFF1E0",
        "painel": "FFF1E0",
        "painel_alto": "FFF1E0",
        "linha": "FFF1E0",
        "texto": "33000D",
        "texto_fraco": "33000D",
        "acento": "000000",
        "tinta": "FFF1E0",
        "papel": "FFF1E0",
        "painel_baixo": "FFF1E0",
        "bloco": "33000D",
        "menu_grande": "FFF1E0",
        "regua": "33000D"
      },
      "aviso_por_papel": {
        "fundo": "D45060",
        "painel": "DA6775",
        "painel_alto": "E38D98",
        "painel_baixo": "DA6775",
        "papel": "D65968",
        "menu_grande": "E0828D",
        "tinta": "D45060",
        "acento": "270A0D"
      }
    }
  },
  "Neon": {
    "claro": {
      "fundo": "FFFCF0",
      "painel": "FFF6D1",
      "painel_alto": "FFF0AD",
      "linha": "FEAFFD",
      "texto": "150132",
      "texto_fraco": "360135",
      "acento": "FF2B67",
      "tinta": "FFF9E0",
      "papel": "FFFBEA",
      "painel_baixo": "FFFAE4",
      "bloco": "E904E6",
      "menu_grande": "FFF2B6",
      "regua": "CCA600",
      "osso_por_papel": {
        "fundo": "150132",
        "painel": "150132",
        "painel_alto": "150132",
        "linha": "150132",
        "texto": "FFF9E0",
        "texto_fraco": "FFF9E0",
        "acento": "150132",
        "tinta": "150132",
        "papel": "150132",
        "painel_baixo": "150132",
        "bloco": "150132",
        "menu_grande": "150132",
        "regua": "150132"
      },
      "aviso_por_papel": {
        "fundo": "E40041",
        "painel": "E0003F",
        "painel_alto": "D6003C",
        "painel_baixo": "E40041",
        "papel": "E40041",
        "menu_grande": "DB003E",
        "tinta": "E40041",
        "acento": "460014"
      }
    },
    "escuro": {
      "fundo": "13012D",
      "painel": "210150",
      "painel_alto": "320279",
      "linha": "780277",
      "texto": "FFF9E0",
      "texto_fraco": "FEB2FD",
      "acento": "FF467A",
      "tinta": "0D001E",
      "papel": "19013D",
      "painel_baixo": "21014F",
      "bloco": "FB1AF8",
      "menu_grande": "2C006E",
      "regua": "8633FF",
      "osso_por_papel": {
        "fundo": "FFF9E0",
        "painel": "FFF9E0",
        "painel_alto": "FFF9E0",
        "linha": "FFF9E0",
        "texto": "150132",
        "texto_fraco": "150132",
        "acento": "150132",
        "tinta": "FFF9E0",
        "papel": "FFF9E0",
        "painel_baixo": "FFF9E0",
        "bloco": "150132",
        "menu_grande": "FFF9E0",
        "regua": "FFF9E0"
      },
      "aviso_por_papel": {
        "fundo": "FF467A",
        "painel": "FF467A",
        "painel_alto": "FF467A",
        "painel_baixo": "FF467A",
        "papel": "FF467A",
        "menu_grande": "FF467A",
        "tinta": "FF467A",
        "acento": "570018"
      }
    }
  },
  "Oceano Profundo": {
    "claro": {
      "fundo": "F1FEFB",
      "painel": "D5FBF4",
      "painel_alto": "B5F8EB",
      "linha": "C4E1E9",
      "texto": "0B0D28",
      "texto_fraco": "0F2328",
      "acento": "2E6FA0",
      "tinta": "E3FCF8",
      "papel": "ECFDFA",
      "painel_baixo": "E7FDF8",
      "bloco": "4197AD",
      "menu_grande": "B6FFF1",
      "regua": "00CCA5",
      "osso_por_papel": {
        "fundo": "0B0D28",
        "painel": "0B0D28",
        "painel_alto": "0B0D28",
        "linha": "0B0D28",
        "texto": "E3FCF8",
        "texto_fraco": "E3FCF8",
        "acento": "E3FCF8",
        "tinta": "0B0D28",
        "papel": "0B0D28",
        "painel_baixo": "0B0D28",
        "bloco": "0B0D28",
        "menu_grande": "0B0D28",
        "regua": "0B0D28"
      },
      "aviso_por_papel": {
        "fundo": "2E6FA0",
        "painel": "2E6FA0",
        "painel_alto": "2E6FA0",
        "painel_baixo": "2E6FA0",
        "papel": "2E6FA0",
        "menu_grande": "2E6FA0",
        "tinta": "2E6FA0",
        "acento": "E3EFF7"
      }
    },
    "escuro": {
      "fundo": "0A0C24",
      "painel": "121640",
      "painel_alto": "1B2060",
      "linha": "214E59",
      "texto": "E3FCF8",
      "texto_fraco": "C6E2EA",
      "acento": "2F72A4",
      "tinta": "070818",
      "papel": "0D1030",
      "painel_baixo": "11153F",
      "bloco": "55AAC0",
      "menu_grande": "0D1361",
      "regua": "4E5AE4",
      "osso_por_papel": {
        "fundo": "E3FCF8",
        "painel": "E3FCF8",
        "painel_alto": "E3FCF8",
        "linha": "E3FCF8",
        "texto": "0B0D28",
        "texto_fraco": "0B0D28",
        "acento": "E3FCF8",
        "tinta": "E3FCF8",
        "papel": "E3FCF8",
        "painel_baixo": "E3FCF8",
        "bloco": "0B0D28",
        "menu_grande": "E3FCF8",
        "regua": "E3FCF8"
      },
      "aviso_por_papel": {
        "fundo": "3682BB",
        "painel": "3888C3",
        "painel_alto": "4D96CC",
        "painel_baixo": "3888C3",
        "papel": "3785BF",
        "menu_grande": "3D8CC7",
        "tinta": "357FB7",
        "acento": "E8F1F8"
      }
    }
  },
  "Tropical": {
    "claro": {
      "fundo": "FFFAF0",
      "painel": "FFF1D1",
      "painel_alto": "FFE6AD",
      "linha": "B0FDE9",
      "texto": "04242F",
      "texto_fraco": "023628",
      "acento": "F04000",
      "tinta": "FFF6E0",
      "papel": "FFF9EA",
      "painel_baixo": "FFF7E4",
      "bloco": "06E7AC",
      "menu_grande": "FFE9B6",
      "regua": "CC8F00",
      "osso_por_papel": {
        "fundo": "04242F",
        "painel": "04242F",
        "painel_alto": "04242F",
        "linha": "04242F",
        "texto": "FFF6E0",
        "texto_fraco": "FFF6E0",
        "acento": "000000",
        "tinta": "04242F",
        "papel": "04242F",
        "painel_baixo": "04242F",
        "bloco": "04242F",
        "menu_grande": "04242F",
        "regua": "04242F"
      },
      "aviso_por_papel": {
        "fundo": "D43900",
        "painel": "CC3600",
        "painel_alto": "C03300",
        "painel_baixo": "D03700",
        "papel": "D43900",
        "menu_grande": "C43400",
        "tinta": "D03700",
        "acento": "300D00"
      }
    },
    "escuro": {
      "fundo": "04202A",
      "painel": "073A4A",
      "painel_alto": "0B5770",
      "linha": "037759",
      "texto": "FFF6E0",
      "texto_fraco": "B3FDEA",
      "acento": "FF7F50",
      "tinta": "03161C",
      "papel": "052C39",
      "painel_baixo": "073949",
      "bloco": "1CF9BF",
      "menu_grande": "00536E",
      "regua": "33CCFF",
      "osso_por_papel": {
        "fundo": "FFF6E0",
        "painel": "FFF6E0",
        "painel_alto": "FFF6E0",
        "linha": "FFF6E0",
        "texto": "04242F",
        "texto_fraco": "04242F",
        "acento": "04242F",
        "tinta": "FFF6E0",
        "papel": "FFF6E0",
        "painel_baixo": "FFF6E0",
        "bloco": "04242F",
        "menu_grande": "FFF6E0",
        "regua": "04242F"
      },
      "aviso_por_papel": {
        "fundo": "FF7F50",
        "painel": "FF7F50",
        "painel_alto": "FFB093",
        "painel_baixo": "FF7F50",
        "papel": "FF7F50",
        "menu_grande": "FFA887",
        "tinta": "FF7F50",
        "acento": "6A1C00"
      }
    }
  },
  "Obsidiana": {
    "claro": {
      "fundo": "FAF9F5",
      "painel": "EFECE1",
      "painel_alto": "E2DDCB",
      "linha": "E8D5C4",
      "texto": "1D1616",
      "texto_fraco": "281B0F",
      "acento": "412D15",
      "tinta": "F8F5E7",
      "papel": "F8F6F2",
      "painel_baixo": "F5F4EE",
      "bloco": "AB7442",
      "menu_grande": "E8E2CC",
      "regua": "8C7C40",
      "osso_por_papel": {
        "fundo": "1D1616",
        "painel": "1D1616",
        "painel_alto": "1D1616",
        "linha": "1D1616",
        "texto": "F4F2EB",
        "texto_fraco": "F4F2EB",
        "acento": "F4F2EB",
        "tinta": "1D1616",
        "papel": "1D1616",
        "painel_baixo": "1D1616",
        "bloco": "1D1616",
        "menu_grande": "1D1616",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "412D15",
        "painel": "412D15",
        "painel_alto": "412D15",
        "painel_baixo": "412D15",
        "papel": "412D15",
        "menu_grande": "412D15",
        "tinta": "412D15",
        "acento": "C6904F"
      }
    },
    "escuro": {
      "fundo": "1A1414",
      "painel": "2E2424",
      "painel_alto": "453636",
      "linha": "583C22",
      "texto": "F4F2EB",
      "texto_fraco": "E9D7C6",
      "acento": "9C6C32",
      "tinta": "170808",
      "papel": "231B1B",
      "painel_baixo": "2D2323",
      "bloco": "BE8857",
      "menu_grande": "402E2E",
      "regua": "A58D8D",
      "osso_por_papel": {
        "fundo": "F4F2EB",
        "painel": "F4F2EB",
        "painel_alto": "F4F2EB",
        "linha": "F4F2EB",
        "texto": "1D1616",
        "texto_fraco": "1D1616",
        "acento": "000000",
        "tinta": "F4F2EB",
        "papel": "F4F2EB",
        "painel_baixo": "F4F2EB",
        "bloco": "1D1616",
        "menu_grande": "F4F2EB",
        "regua": "1D1616"
      },
      "aviso_por_papel": {
        "fundo": "A87436",
        "painel": "BB813C",
        "painel_alto": "CB9A5E",
        "painel_baixo": "BB813C",
        "papel": "AF7938",
        "menu_grande": "C6904F",
        "tinta": "A47134",
        "acento": "000000"
      }
    }
  },
  "Brasa": {
    "claro": {
      "fundo": "FDF4F1",
      "painel": "FADFD6",
      "painel_alto": "F7C7B5",
      "linha": "FAB4B2",
      "texto": "2D0A06",
      "texto_fraco": "340503",
      "acento": "740A03",
      "tinta": "FCEAE3",
      "papel": "FDF1EC",
      "painel_baixo": "FCECE7",
      "bloco": "DF130E",
      "menu_grande": "FFCAB6",
      "regua": "CC3500",
      "osso_por_papel": {
        "fundo": "2D0A06",
        "painel": "2D0A06",
        "painel_alto": "2D0A06",
        "linha": "2D0A06",
        "texto": "FCEAE3",
        "texto_fraco": "FCEAE3",
        "acento": "FCEAE3",
        "tinta": "2D0A06",
        "papel": "2D0A06",
        "painel_baixo": "2D0A06",
        "bloco": "FFFFFF",
        "menu_grande": "2D0A06",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "740A03",
        "painel": "740A03",
        "painel_alto": "740A03",
        "painel_baixo": "740A03",
        "papel": "740A03",
        "menu_grande": "740A03",
        "tinta": "740A03",
        "acento": "FB7C73"
      }
    },
    "escuro": {
      "fundo": "290905",
      "painel": "491009",
      "painel_alto": "6D180E",
      "linha": "730A07",
      "texto": "FCEAE3",
      "texto_fraco": "FAB7B5",
      "acento": "ED1406",
      "tinta": "1B0603",
      "papel": "370C07",
      "painel_baixo": "471009",
      "bloco": "F12923",
      "menu_grande": "6E0C00",
      "regua": "FF4A33",
      "osso_por_papel": {
        "fundo": "FCEAE3",
        "painel": "FCEAE3",
        "painel_alto": "FCEAE3",
        "linha": "FCEAE3",
        "texto": "2D0A06",
        "texto_fraco": "2D0A06",
        "acento": "000000",
        "tinta": "FCEAE3",
        "papel": "FCEAE3",
        "painel_baixo": "FCEAE3",
        "bloco": "000000",
        "menu_grande": "FCEAE3",
        "regua": "2D0A06"
      },
      "aviso_por_papel": {
        "fundo": "F91608",
        "painel": "FA4B40",
        "painel_alto": "FB7C74",
        "painel_baixo": "FA4B40",
        "papel": "FA3326",
        "menu_grande": "FB746B",
        "tinta": "F11406",
        "acento": "140201"
      }
    }
  },
  "Sangue": {
    "claro": {
      "fundo": "FFF0F0",
      "painel": "FFD1D1",
      "painel_alto": "FFADAD",
      "linha": "DFCDCD",
      "texto": "000033",
      "texto_fraco": "221515",
      "acento": "9E2A3A",
      "tinta": "FFE0E0",
      "papel": "FFEAEA",
      "painel_baixo": "FFE4E4",
      "bloco": "915C5C",
      "menu_grande": "FFB6B6",
      "regua": "CC0000",
      "osso_por_papel": {
        "fundo": "000033",
        "painel": "000033",
        "painel_alto": "000033",
        "linha": "000033",
        "texto": "FFE0E0",
        "texto_fraco": "FFE0E0",
        "acento": "FFE0E0",
        "tinta": "000033",
        "papel": "000033",
        "painel_baixo": "000033",
        "bloco": "FFFFFF",
        "menu_grande": "000033",
        "regua": "FFE0E0"
      },
      "aviso_por_papel": {
        "fundo": "9E2A3A",
        "painel": "9E2A3A",
        "painel_alto": "932736",
        "painel_baixo": "9E2A3A",
        "papel": "9E2A3A",
        "menu_grande": "9B2939",
        "tinta": "9E2A3A",
        "acento": "EFC2C8"
      }
    },
    "escuro": {
      "fundo": "00002E",
      "painel": "000052",
      "painel_alto": "00007A",
      "linha": "4B3030",
      "texto": "FFE0E0",
      "texto_fraco": "E0CFCF",
      "acento": "BF3346",
      "tinta": "00001F",
      "papel": "00003E",
      "painel_baixo": "000050",
      "bloco": "A47171",
      "menu_grande": "00006E",
      "regua": "3333FF",
      "osso_por_papel": {
        "fundo": "FFE0E0",
        "painel": "FFE0E0",
        "painel_alto": "FFE0E0",
        "linha": "FFE0E0",
        "texto": "000033",
        "texto_fraco": "000033",
        "acento": "FFFFFF",
        "tinta": "FFE0E0",
        "papel": "FFE0E0",
        "painel_baixo": "FFE0E0",
        "bloco": "000033",
        "menu_grande": "FFE0E0",
        "regua": "FFE0E0"
      },
      "aviso_por_papel": {
        "fundo": "CE485A",
        "painel": "D15263",
        "painel_alto": "D66473",
        "painel_baixo": "D15263",
        "papel": "CF4B5D",
        "menu_grande": "D45D6D",
        "tinta": "CE485A",
        "acento": "F7E3E6"
      }
    }
  },
  "Abismo": {
    "claro": {
      "fundo": "F5FAF9",
      "painel": "E1EFEE",
      "painel_alto": "C9E3E2",
      "linha": "B5F2F7",
      "texto": "16042F",
      "texto_fraco": "052E32",
      "acento": "065084",
      "tinta": "E7F8F7",
      "papel": "F1F8F8",
      "painel_baixo": "EDF6F5",
      "bloco": "17C7D6",
      "menu_grande": "CBEAE9",
      "regua": "3C908B",
      "osso_por_papel": {
        "fundo": "16042F",
        "painel": "16042F",
        "painel_alto": "16042F",
        "linha": "16042F",
        "texto": "EBF5F4",
        "texto_fraco": "EBF5F4",
        "acento": "EBF5F4",
        "tinta": "16042F",
        "papel": "16042F",
        "painel_baixo": "16042F",
        "bloco": "16042F",
        "menu_grande": "16042F",
        "regua": "16042F"
      },
      "aviso_por_papel": {
        "fundo": "065084",
        "painel": "065084",
        "painel_alto": "065084",
        "painel_baixo": "065084",
        "papel": "065084",
        "menu_grande": "065084",
        "tinta": "065084",
        "acento": "7DC6F9"
      }
    },
    "escuro": {
      "fundo": "14042A",
      "painel": "23074B",
      "painel_alto": "340A70",
      "linha": "0C676F",
      "texto": "EBF5F4",
      "texto_fraco": "B8F2F7",
      "acento": "0870B9",
      "tinta": "0D031C",
      "papel": "1A0539",
      "painel_baixo": "220749",
      "bloco": "2CD9E8",
      "menu_grande": "2D006E",
      "regua": "8733FF",
      "osso_por_papel": {
        "fundo": "EBF5F4",
        "painel": "EBF5F4",
        "painel_alto": "EBF5F4",
        "linha": "EBF5F4",
        "texto": "16042F",
        "texto_fraco": "16042F",
        "acento": "EBF5F4",
        "tinta": "EBF5F4",
        "papel": "EBF5F4",
        "painel_baixo": "EBF5F4",
        "bloco": "16042F",
        "menu_grande": "EBF5F4",
        "regua": "EBF5F4"
      },
      "aviso_por_papel": {
        "fundo": "097FD2",
        "painel": "0A89E2",
        "painel_alto": "0C95F4",
        "painel_baixo": "0A85DC",
        "papel": "0982D7",
        "menu_grande": "0A8FEC",
        "tinta": "097CCD",
        "acento": "E1F2FE"
      }
    }
  },
  "Arcano": {
    "claro": {
      "fundo": "FFFCF0",
      "painel": "FFF6D1",
      "painel_alto": "FFEFAD",
      "linha": "D0B7F6",
      "texto": "070033",
      "texto_fraco": "170631",
      "acento": "B13BFF",
      "tinta": "FFF9E0",
      "papel": "FFFBEA",
      "painel_baixo": "FFFAE4",
      "bloco": "641BD2",
      "menu_grande": "FFF1B6",
      "regua": "CCA300",
      "osso_por_papel": {
        "fundo": "070033",
        "painel": "070033",
        "painel_alto": "070033",
        "linha": "070033",
        "texto": "FFF9E0",
        "texto_fraco": "FFF9E0",
        "acento": "070033",
        "tinta": "070033",
        "papel": "070033",
        "painel_baixo": "070033",
        "bloco": "FFF9E0",
        "menu_grande": "070033",
        "regua": "070033"
      },
      "aviso_por_papel": {
        "fundo": "AB2BFF",
        "painel": "A51CFF",
        "painel_alto": "A011FF",
        "painel_baixo": "A926FF",
        "papel": "A926FF",
        "menu_grande": "A216FF",
        "tinta": "A926FF",
        "acento": "1C002F"
      }
    },
    "escuro": {
      "fundo": "06002E",
      "painel": "0B0052",
      "painel_alto": "11007A",
      "linha": "330E6D",
      "texto": "FFF9E0",
      "texto_fraco": "D1B9F6",
      "acento": "B13BFF",
      "tinta": "04001F",
      "papel": "09003E",
      "painel_baixo": "0B0050",
      "bloco": "7830E5",
      "menu_grande": "0F006E",
      "regua": "5033FF",
      "osso_por_papel": {
        "fundo": "FFF9E0",
        "painel": "FFF9E0",
        "painel_alto": "FFF9E0",
        "linha": "FFF9E0",
        "texto": "070033",
        "texto_fraco": "070033",
        "acento": "070033",
        "tinta": "FFF9E0",
        "papel": "FFF9E0",
        "painel_baixo": "FFF9E0",
        "bloco": "FFF9E0",
        "menu_grande": "FFF9E0",
        "regua": "FFF9E0"
      },
      "aviso_por_papel": {
        "fundo": "B13BFF",
        "painel": "B442FF",
        "painel_alto": "BD58FF",
        "painel_baixo": "B442FF",
        "papel": "B13BFF",
        "menu_grande": "B94FFF",
        "tinta": "B13BFF",
        "acento": "1C002F"
      }
    }
  },
  "Rubi": {
    "claro": {
      "fundo": "FDF2F6",
      "painel": "FAD7E3",
      "painel_alto": "F5B7CD",
      "linha": "EAC2D1",
      "texto": "2F0414",
      "texto_fraco": "290E18",
      "acento": "670D2F",
      "tinta": "FBE4EC",
      "papel": "FDEDF2",
      "painel_baixo": "FCE7EF",
      "bloco": "B13C67",
      "menu_grande": "FFB6D0",
      "regua": "CB014A",
      "osso_por_papel": {
        "fundo": "2F0414",
        "painel": "2F0414",
        "painel_alto": "2F0414",
        "linha": "2F0414",
        "texto": "FBE4EC",
        "texto_fraco": "FBE4EC",
        "acento": "FBE4EC",
        "tinta": "2F0414",
        "papel": "2F0414",
        "painel_baixo": "2F0414",
        "bloco": "FBE4EC",
        "menu_grande": "2F0414",
        "regua": "FBE4EC"
      },
      "aviso_por_papel": {
        "fundo": "670D2F",
        "painel": "670D2F",
        "painel_alto": "670D2F",
        "painel_baixo": "670D2F",
        "papel": "670D2F",
        "menu_grande": "670D2F",
        "tinta": "670D2F",
        "acento": "ED73A1"
      }
    },
    "escuro": {
      "fundo": "2A0412",
      "painel": "4B0620",
      "painel_alto": "710A31",
      "linha": "5B1F35",
      "texto": "FBE4EC",
      "texto_fraco": "EBC4D3",
      "acento": "E11C67",
      "tinta": "1C020C",
      "papel": "390519",
      "painel_baixo": "4A0620",
      "bloco": "C4517B",
      "menu_grande": "6E002A",
      "regua": "FF3380",
      "osso_por_papel": {
        "fundo": "FBE4EC",
        "painel": "FBE4EC",
        "painel_alto": "FBE4EC",
        "linha": "FBE4EC",
        "texto": "2F0414",
        "texto_fraco": "2F0414",
        "acento": "FFFFFF",
        "tinta": "FBE4EC",
        "papel": "FBE4EC",
        "painel_baixo": "FBE4EC",
        "bloco": "000000",
        "menu_grande": "FBE4EC",
        "regua": "2F0414"
      },
      "aviso_por_papel": {
        "fundo": "E63578",
        "painel": "EA548D",
        "painel_alto": "EF7DA9",
        "painel_baixo": "EA548D",
        "papel": "E74180",
        "menu_grande": "EE76A4",
        "tinta": "E4266E",
        "acento": "FFFFFF"
      }
    }
  },
  "Ardósia": {
    "claro": {
      "fundo": "FAF8F4",
      "painel": "F1EADF",
      "painel_alto": "E6DAC7",
      "linha": "D1D5DB",
      "texto": "15191E",
      "texto_fraco": "181B1F",
      "acento": "897E6D",
      "tinta": "F8F2E7",
      "papel": "F9F6F1",
      "painel_baixo": "F7F3ED",
      "bloco": "687385",
      "menu_grande": "EDDFC7",
      "regua": "987234",
      "osso_por_papel": {
        "fundo": "15191E",
        "painel": "15191E",
        "painel_alto": "15191E",
        "linha": "15191E",
        "texto": "F5F1EA",
        "texto_fraco": "F5F1EA",
        "acento": "000000",
        "tinta": "15191E",
        "papel": "15191E",
        "painel_baixo": "15191E",
        "bloco": "FFFFFF",
        "menu_grande": "15191E",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "7B7162",
        "painel": "72695B",
        "painel_alto": "675E52",
        "painel_baixo": "776D5E",
        "papel": "796F60",
        "menu_grande": "6B6355",
        "tinta": "776D5E",
        "acento": "171512"
      }
    },
    "escuro": {
      "fundo": "13161B",
      "painel": "212730",
      "painel_alto": "323B48",
      "linha": "363C45",
      "texto": "F5F1EA",
      "texto_fraco": "D3D7DC",
      "acento": "948979",
      "tinta": "080E17",
      "papel": "191E25",
      "painel_baixo": "21272F",
      "bloco": "7C8798",
      "menu_grande": "2A3544",
      "regua": "8194B1",
      "osso_por_papel": {
        "fundo": "F5F1EA",
        "painel": "F5F1EA",
        "painel_alto": "F5F1EA",
        "linha": "F5F1EA",
        "texto": "15191E",
        "texto_fraco": "15191E",
        "acento": "15191E",
        "tinta": "F5F1EA",
        "papel": "F5F1EA",
        "painel_baixo": "F5F1EA",
        "bloco": "15191E",
        "menu_grande": "F5F1EA",
        "regua": "15191E"
      },
      "aviso_por_papel": {
        "fundo": "948979",
        "painel": "988D7D",
        "painel_alto": "ABA396",
        "painel_baixo": "988D7D",
        "papel": "948979",
        "menu_grande": "A49B8D",
        "tinta": "948979",
        "acento": "25221E"
      }
    }
  },
  "Musgo": {
    "claro": {
      "fundo": "F3FCF8",
      "painel": "DAF6EA",
      "painel_alto": "BEEFD9",
      "linha": "D3E4C8",
      "texto": "18240F",
      "texto_fraco": "192512",
      "acento": "255F38",
      "tinta": "E6F9F1",
      "papel": "EEFBF5",
      "painel_baixo": "EAFAF2",
      "bloco": "6D9F4E",
      "menu_grande": "BCF8DD",
      "regua": "16B66F",
      "osso_por_papel": {
        "fundo": "18240F",
        "painel": "18240F",
        "painel_alto": "18240F",
        "linha": "18240F",
        "texto": "E6F9F1",
        "texto_fraco": "E6F9F1",
        "acento": "E6F9F1",
        "tinta": "18240F",
        "papel": "18240F",
        "painel_baixo": "18240F",
        "bloco": "18240F",
        "menu_grande": "18240F",
        "regua": "18240F"
      },
      "aviso_por_papel": {
        "fundo": "255F38",
        "painel": "255F38",
        "painel_alto": "255F38",
        "painel_baixo": "255F38",
        "papel": "255F38",
        "menu_grande": "255F38",
        "tinta": "255F38",
        "acento": "97D6AC"
      }
    },
    "escuro": {
      "fundo": "16200E",
      "painel": "273918",
      "painel_alto": "3B5625",
      "linha": "385228",
      "texto": "E6F9F1",
      "texto_fraco": "D4E5CA",
      "acento": "3A9558",
      "tinta": "0F1708",
      "papel": "1E2B13",
      "painel_baixo": "273818",
      "bloco": "81B263",
      "menu_grande": "345519",
      "regua": "94CE64",
      "osso_por_papel": {
        "fundo": "E6F9F1",
        "painel": "E6F9F1",
        "painel_alto": "E6F9F1",
        "linha": "E6F9F1",
        "texto": "18240F",
        "texto_fraco": "18240F",
        "acento": "000000",
        "tinta": "E6F9F1",
        "papel": "E6F9F1",
        "painel_baixo": "E6F9F1",
        "bloco": "18240F",
        "menu_grande": "E6F9F1",
        "regua": "18240F"
      },
      "aviso_por_papel": {
        "fundo": "3A9558",
        "painel": "45B269",
        "painel_alto": "87D09F",
        "painel_baixo": "44AE67",
        "papel": "3EA05E",
        "menu_grande": "80CD99",
        "tinta": "3A9558",
        "acento": "0D2013"
      }
    }
  },
  "Terra": {
    "claro": {
      "fundo": "F9F8F6",
      "painel": "EDEAE3",
      "painel_alto": "DFDACD",
      "linha": "D1DBD4",
      "texto": "161D18",
      "texto_fraco": "181F1A",
      "acento": "9D7759",
      "tinta": "F8F4E7",
      "papel": "F7F6F2",
      "painel_baixo": "F4F3EF",
      "bloco": "688571",
      "menu_grande": "E5DFCF",
      "regua": "82734A",
      "osso_por_papel": {
        "fundo": "161D18",
        "painel": "161D18",
        "painel_alto": "161D18",
        "linha": "161D18",
        "texto": "F3F1EC",
        "texto_fraco": "F3F1EC",
        "acento": "000000",
        "tinta": "161D18",
        "papel": "161D18",
        "painel_baixo": "161D18",
        "bloco": "000000",
        "menu_grande": "161D18",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "8D6B50",
        "painel": "83634A",
        "painel_alto": "765943",
        "painel_baixo": "88674D",
        "papel": "8B694F",
        "menu_grande": "7B5D46",
        "tinta": "8B694F",
        "acento": "1A140F"
      }
    },
    "escuro": {
      "fundo": "141A16",
      "painel": "242E27",
      "painel_alto": "35453A",
      "linha": "36453A",
      "texto": "F3F1EC",
      "texto_fraco": "D3DCD6",
      "acento": "A27B5C",
      "tinta": "08170C",
      "papel": "1B231D",
      "painel_baixo": "232D26",
      "bloco": "7C9885",
      "menu_grande": "2D4133",
      "regua": "88AA92",
      "osso_por_papel": {
        "fundo": "F3F1EC",
        "painel": "F3F1EC",
        "painel_alto": "F3F1EC",
        "linha": "F3F1EC",
        "texto": "161D18",
        "texto_fraco": "161D18",
        "acento": "161D18",
        "tinta": "F3F1EC",
        "papel": "F3F1EC",
        "painel_baixo": "F3F1EC",
        "bloco": "161D18",
        "menu_grande": "F3F1EC",
        "regua": "161D18"
      },
      "aviso_por_papel": {
        "fundo": "A27B5C",
        "painel": "AF8D71",
        "painel_alto": "C3A995",
        "painel_baixo": "AD8A6F",
        "papel": "A78264",
        "menu_grande": "BEA38D",
        "tinta": "A27B5C",
        "acento": "201912"
      }
    }
  },
  "Eclipse": {
    "claro": {
      "fundo": "FFF6F0",
      "painel": "FFE3D1",
      "painel_alto": "FFCEAD",
      "linha": "C1D5EC",
      "texto": "1D1616",
      "texto_fraco": "0D1B2A",
      "acento": "0B192C",
      "tinta": "FFEDE0",
      "papel": "FFF3EA",
      "painel_baixo": "FFEFE4",
      "bloco": "3873B6",
      "menu_grande": "FFD3B6",
      "regua": "CC5100",
      "osso_por_papel": {
        "fundo": "1D1616",
        "painel": "1D1616",
        "painel_alto": "1D1616",
        "linha": "1D1616",
        "texto": "FFEDE0",
        "texto_fraco": "FFEDE0",
        "acento": "FFEDE0",
        "tinta": "1D1616",
        "papel": "1D1616",
        "painel_baixo": "1D1616",
        "bloco": "FFFFFF",
        "menu_grande": "1D1616",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "0B192C",
        "painel": "0B192C",
        "painel_alto": "0B192C",
        "painel_baixo": "0B192C",
        "papel": "0B192C",
        "menu_grande": "0B192C",
        "tinta": "0B192C",
        "acento": "4983D2"
      }
    },
    "escuro": {
      "fundo": "1A1414",
      "painel": "2E2424",
      "painel_alto": "453636",
      "linha": "1D3B5E",
      "texto": "FFEDE0",
      "texto_fraco": "C3D7ED",
      "acento": "3776CD",
      "tinta": "170808",
      "papel": "231B1B",
      "painel_baixo": "2D2323",
      "bloco": "4D87C8",
      "menu_grande": "402E2E",
      "regua": "A58D8D",
      "osso_por_papel": {
        "fundo": "FFEDE0",
        "painel": "FFEDE0",
        "painel_alto": "FFEDE0",
        "linha": "FFEDE0",
        "texto": "1D1616",
        "texto_fraco": "1D1616",
        "acento": "000000",
        "tinta": "FFEDE0",
        "papel": "FFEDE0",
        "painel_baixo": "FFEDE0",
        "bloco": "1D1616",
        "menu_grande": "FFEDE0",
        "regua": "1D1616"
      },
      "aviso_por_papel": {
        "fundo": "4881D1",
        "painel": "5C8FD6",
        "painel_alto": "7DA6DE",
        "painel_baixo": "5C8FD6",
        "papel": "4E86D3",
        "menu_grande": "709DDB",
        "tinta": "3E7BCF",
        "acento": "020508"
      }
    }
  },
  "Oliva": {
    "claro": {
      "fundo": "FBF8F4",
      "painel": "F3EADE",
      "painel_alto": "E9DAC4",
      "linha": "D9DBD1",
      "texto": "1A1E15",
      "texto_fraco": "1E1F18",
      "acento": "697565",
      "tinta": "F8F1E7",
      "papel": "F9F6F0",
      "painel_baixo": "F8F3EB",
      "bloco": "808568",
      "menu_grande": "F1DFC4",
      "regua": "A37129",
      "osso_por_papel": {
        "fundo": "1A1E15",
        "painel": "1A1E15",
        "painel_alto": "1A1E15",
        "linha": "1A1E15",
        "texto": "F7F1E9",
        "texto_fraco": "F7F1E9",
        "acento": "FFFFFF",
        "tinta": "1A1E15",
        "papel": "1A1E15",
        "painel_baixo": "1A1E15",
        "bloco": "000000",
        "menu_grande": "1A1E15",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "697565",
        "painel": "626D5E",
        "painel_alto": "596356",
        "painel_baixo": "677363",
        "papel": "677363",
        "menu_grande": "5D6759",
        "tinta": "667162",
        "acento": "F7F8F7"
      }
    },
    "escuro": {
      "fundo": "171B13",
      "painel": "293022",
      "painel_alto": "3D4733",
      "linha": "424536",
      "texto": "F7F1E9",
      "texto_fraco": "DBDCD3",
      "acento": "758270",
      "tinta": "0F1708",
      "papel": "1F241A",
      "painel_baixo": "282F21",
      "bloco": "94987C",
      "menu_grande": "37432B",
      "regua": "99AF83",
      "osso_por_papel": {
        "fundo": "F7F1E9",
        "painel": "F7F1E9",
        "painel_alto": "F7F1E9",
        "linha": "F7F1E9",
        "texto": "1A1E15",
        "texto_fraco": "1A1E15",
        "acento": "000000",
        "tinta": "F7F1E9",
        "papel": "F7F1E9",
        "painel_baixo": "F7F1E9",
        "bloco": "1A1E15",
        "menu_grande": "F7F1E9",
        "regua": "1A1E15"
      },
      "aviso_por_papel": {
        "fundo": "798774",
        "painel": "8C9887",
        "painel_alto": "AAB3A6",
        "painel_baixo": "8C9887",
        "papel": "808D7B",
        "menu_grande": "A5AEA1",
        "tinta": "758270",
        "acento": "131613"
      }
    }
  },
  "Púrpura Real": {
    "claro": {
      "fundo": "F9F2FD",
      "painel": "EDD7F9",
      "painel_alto": "DFB9F4",
      "linha": "DFB9F3",
      "texto": "22052E",
      "texto_fraco": "22082F",
      "acento": "7A1CAC",
      "tinta": "F3E5FB",
      "papel": "F7EDFC",
      "painel_baixo": "F4E8FB",
      "bloco": "9122CC",
      "menu_grande": "E5B6FE",
      "regua": "8306C6",
      "osso_por_papel": {
        "fundo": "22052E",
        "painel": "22052E",
        "painel_alto": "22052E",
        "linha": "22052E",
        "texto": "F3E5FB",
        "texto_fraco": "F3E5FB",
        "acento": "F3E5FB",
        "tinta": "22052E",
        "papel": "22052E",
        "painel_baixo": "22052E",
        "bloco": "F3E5FB",
        "menu_grande": "22052E",
        "regua": "F3E5FB"
      },
      "aviso_por_papel": {
        "fundo": "7A1CAC",
        "painel": "7A1CAC",
        "painel_alto": "7A1CAC",
        "painel_baixo": "7A1CAC",
        "papel": "7A1CAC",
        "menu_grande": "7A1CAC",
        "tinta": "7A1CAC",
        "acento": "DDB3F3"
      }
    },
    "escuro": {
      "fundo": "1E0529",
      "painel": "360849",
      "painel_alto": "500C6E",
      "linha": "4B1169",
      "texto": "F3E5FB",
      "texto_fraco": "E1BCF4",
      "acento": "A63BDF",
      "tinta": "14031C",
      "papel": "290638",
      "painel_baixo": "350848",
      "bloco": "A537DE",
      "menu_grande": "4C006E",
      "regua": "C133FF",
      "osso_por_papel": {
        "fundo": "F3E5FB",
        "painel": "F3E5FB",
        "painel_alto": "F3E5FB",
        "linha": "F3E5FB",
        "texto": "22052E",
        "texto_fraco": "22052E",
        "acento": "FFFFFF",
        "tinta": "F3E5FB",
        "papel": "F3E5FB",
        "painel_baixo": "F3E5FB",
        "bloco": "FFFFFF",
        "menu_grande": "F3E5FB",
        "regua": "22052E"
      },
      "aviso_por_papel": {
        "fundo": "AF4FE2",
        "painel": "B862E5",
        "painel_alto": "C47CEA",
        "painel_baixo": "B862E5",
        "papel": "B255E3",
        "menu_grande": "C176E9",
        "tinta": "AC48E1",
        "acento": "FBF5FD"
      }
    }
  },
  "Céu de Verão": {
    "claro": {
      "fundo": "FAF8F5",
      "painel": "EFEBE1",
      "painel_alto": "E2DCCA",
      "linha": "CBE1DD",
      "texto": "0C1927",
      "texto_fraco": "142320",
      "acento": "4587A5",
      "tinta": "F8F4E7",
      "papel": "F8F6F2",
      "painel_baixo": "F6F3EE",
      "bloco": "57968B",
      "menu_grande": "E9E2CC",
      "regua": "8D783F",
      "osso_por_papel": {
        "fundo": "0C1927",
        "painel": "0C1927",
        "painel_alto": "0C1927",
        "linha": "0C1927",
        "texto": "F4F2EB",
        "texto_fraco": "F4F2EB",
        "acento": "000000",
        "tinta": "0C1927",
        "papel": "0C1927",
        "painel_baixo": "0C1927",
        "bloco": "0C1927",
        "menu_grande": "0C1927",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "3D7792",
        "painel": "3A718A",
        "painel_alto": "34657C",
        "painel_baixo": "3C758F",
        "papel": "3D7792",
        "menu_grande": "366A81",
        "tinta": "3C758F",
        "acento": "0C171C"
      }
    },
    "escuro": {
      "fundo": "0B1723",
      "painel": "14283E",
      "painel_alto": "1E3C5D",
      "linha": "2D4D48",
      "texto": "F4F2EB",
      "texto_fraco": "CDE2DF",
      "acento": "66A3BF",
      "tinta": "070F17",
      "papel": "0F1F2F",
      "painel_baixo": "13283D",
      "bloco": "6CA99F",
      "menu_grande": "11355D",
      "regua": "5597DD",
      "osso_por_papel": {
        "fundo": "F4F2EB",
        "painel": "F4F2EB",
        "painel_alto": "F4F2EB",
        "linha": "F4F2EB",
        "texto": "0C1927",
        "texto_fraco": "0C1927",
        "acento": "0C1927",
        "tinta": "F4F2EB",
        "papel": "F4F2EB",
        "painel_baixo": "F4F2EB",
        "bloco": "0C1927",
        "menu_grande": "F4F2EB",
        "regua": "0C1927"
      },
      "aviso_por_papel": {
        "fundo": "66A3BF",
        "painel": "66A3BF",
        "painel_alto": "75ACC5",
        "painel_baixo": "66A3BF",
        "papel": "66A3BF",
        "menu_grande": "69A5C0",
        "tinta": "66A3BF",
        "acento": "1B3541"
      }
    }
  },
  "Cerâmica": {
    "claro": {
      "fundo": "FEFAF0",
      "painel": "FDEFD3",
      "painel_alto": "FBE3B1",
      "linha": "F5E3B8",
      "texto": "0A2926",
      "texto_fraco": "302407",
      "acento": "E2512C",
      "tinta": "FEF5E2",
      "papel": "FEF8EB",
      "painel_baixo": "FEF6E5",
      "bloco": "CF9B1F",
      "menu_grande": "FFE7B6",
      "regua": "CC8A00",
      "osso_por_papel": {
        "fundo": "0A2926",
        "painel": "0A2926",
        "painel_alto": "0A2926",
        "linha": "0A2926",
        "texto": "FEF5E2",
        "texto_fraco": "FEF5E2",
        "acento": "000000",
        "tinta": "0A2926",
        "papel": "0A2926",
        "painel_baixo": "0A2926",
        "bloco": "0A2926",
        "menu_grande": "0A2926",
        "regua": "0A2926"
      },
      "aviso_por_papel": {
        "fundo": "CE401C",
        "painel": "C23D1B",
        "painel_alto": "BA3A1A",
        "painel_baixo": "CA3F1C",
        "papel": "CE401C",
        "menu_grande": "BE3B1A",
        "tinta": "CA3F1C",
        "acento": "2F0F07"
      }
    },
    "escuro": {
      "fundo": "092522",
      "painel": "0F423C",
      "painel_alto": "17645B",
      "linha": "6B5010",
      "texto": "FEF5E2",
      "texto_fraco": "F5E4BB",
      "acento": "E76F51",
      "tinta": "061917",
      "papel": "0C322E",
      "painel_baixo": "0F413C",
      "bloco": "E1AF34",
      "menu_grande": "09665B",
      "regua": "46ECD9",
      "osso_por_papel": {
        "fundo": "FEF5E2",
        "painel": "FEF5E2",
        "painel_alto": "FEF5E2",
        "linha": "FEF5E2",
        "texto": "0A2926",
        "texto_fraco": "0A2926",
        "acento": "0A2926",
        "tinta": "FEF5E2",
        "papel": "FEF5E2",
        "painel_baixo": "FEF5E2",
        "bloco": "0A2926",
        "menu_grande": "FEF5E2",
        "regua": "0A2926"
      },
      "aviso_por_papel": {
        "fundo": "E76F51",
        "painel": "EC8C74",
        "painel_alto": "F5C5B9",
        "painel_baixo": "EB8971",
        "papel": "E77154",
        "menu_grande": "F6C8BC",
        "tinta": "E76F51",
        "acento": "4E180B"
      }
    }
  },
  "Algodão-Doce": {
    "claro": {
      "fundo": "FCF3F3",
      "painel": "F6DADA",
      "painel_alto": "EFBEBE",
      "linha": "F2BBBB",
      "texto": "1A1320",
      "texto_fraco": "2E0909",
      "acento": "F10000",
      "tinta": "F9E7E7",
      "papel": "FBEEEE",
      "painel_baixo": "FAEAEA",
      "bloco": "C72626",
      "menu_grande": "F8BCBC",
      "regua": "B61616",
      "osso_por_papel": {
        "fundo": "1A1320",
        "painel": "1A1320",
        "painel_alto": "1A1320",
        "linha": "1A1320",
        "texto": "F9E7E7",
        "texto_fraco": "F9E7E7",
        "acento": "000000",
        "tinta": "1A1320",
        "papel": "1A1320",
        "painel_baixo": "1A1320",
        "bloco": "F9E7E7",
        "menu_grande": "1A1320",
        "regua": "F9E7E7"
      },
      "aviso_por_papel": {
        "fundo": "E10000",
        "painel": "C90000",
        "painel_alto": "AD0000",
        "painel_baixo": "D90000",
        "papel": "DD0000",
        "menu_grande": "AD0000",
        "tinta": "D50000",
        "acento": "1C0000"
      }
    },
    "escuro": {
      "fundo": "18111D",
      "painel": "2A1E34",
      "painel_alto": "3F2D4E",
      "linha": "671414",
      "texto": "F9E7E7",
      "texto_fraco": "F2BDBD",
      "acento": "FFE2E2",
      "tinta": "100817",
      "papel": "201727",
      "painel_baixo": "2A1D33",
      "bloco": "D93C3C",
      "menu_grande": "39234B",
      "regua": "9D76BC",
      "osso_por_papel": {
        "fundo": "F9E7E7",
        "painel": "F9E7E7",
        "painel_alto": "F9E7E7",
        "linha": "F9E7E7",
        "texto": "1A1320",
        "texto_fraco": "1A1320",
        "acento": "1A1320",
        "tinta": "F9E7E7",
        "papel": "F9E7E7",
        "painel_baixo": "F9E7E7",
        "bloco": "000000",
        "menu_grande": "F9E7E7",
        "regua": "1A1320"
      },
      "aviso_por_papel": {
        "fundo": "FFE2E2",
        "painel": "FFE2E2",
        "painel_alto": "FFE2E2",
        "painel_baixo": "FFE2E2",
        "papel": "FFE2E2",
        "menu_grande": "FFE2E2",
        "tinta": "FFE2E2",
        "acento": "D00000"
      }
    }
  },
  "Eucalipto": {
    "claro": {
      "fundo": "F7FBF4",
      "painel": "E7F2DE",
      "painel_alto": "D4E8C4",
      "linha": "CBE2D0",
      "texto": "151E1C",
      "texto_fraco": "142317",
      "acento": "4F8F71",
      "tinta": "EEF8E7",
      "papel": "F4F9F0",
      "painel_baixo": "F1F8EC",
      "bloco": "569865",
      "menu_grande": "D8F0C5",
      "regua": "5EA12B",
      "osso_por_papel": {
        "fundo": "151E1C",
        "painel": "151E1C",
        "painel_alto": "151E1C",
        "linha": "151E1C",
        "texto": "EFF7E9",
        "texto_fraco": "EFF7E9",
        "acento": "000000",
        "tinta": "151E1C",
        "papel": "151E1C",
        "painel_baixo": "151E1C",
        "bloco": "151E1C",
        "menu_grande": "151E1C",
        "regua": "151E1C"
      },
      "aviso_por_papel": {
        "fundo": "467E64",
        "painel": "42775E",
        "painel_alto": "3D6E57",
        "painel_baixo": "447C62",
        "papel": "447C62",
        "menu_grande": "3F725A",
        "tinta": "437A60",
        "acento": "101D17"
      }
    },
    "escuro": {
      "fundo": "131B19",
      "painel": "21302D",
      "painel_alto": "324843",
      "linha": "2C4E34",
      "texto": "EFF7E9",
      "texto_fraco": "CDE3D2",
      "acento": "88BDA4",
      "tinta": "081713",
      "papel": "192522",
      "painel_baixo": "212F2C",
      "bloco": "6AAB79",
      "menu_grande": "2A443E",
      "regua": "81B1A5",
      "osso_por_papel": {
        "fundo": "EFF7E9",
        "painel": "EFF7E9",
        "painel_alto": "EFF7E9",
        "linha": "EFF7E9",
        "texto": "151E1C",
        "texto_fraco": "151E1C",
        "acento": "151E1C",
        "tinta": "EFF7E9",
        "papel": "EFF7E9",
        "painel_baixo": "EFF7E9",
        "bloco": "151E1C",
        "menu_grande": "EFF7E9",
        "regua": "151E1C"
      },
      "aviso_por_papel": {
        "fundo": "88BDA4",
        "painel": "88BDA4",
        "painel_alto": "88BDA4",
        "painel_baixo": "88BDA4",
        "papel": "88BDA4",
        "menu_grande": "88BDA4",
        "tinta": "88BDA4",
        "acento": "29493A"
      }
    }
  },
  "Pêssego": {
    "claro": {
      "fundo": "FFFBF0",
      "painel": "FFF4D1",
      "painel_alto": "FFECAD",
      "linha": "FFD9AD",
      "texto": "330800",
      "texto_fraco": "371E00",
      "acento": "F53E00",
      "tinta": "FFF8E0",
      "papel": "FFFAEA",
      "painel_baixo": "FFF9E4",
      "bloco": "ED8000",
      "menu_grande": "FFEEB6",
      "regua": "CC9D00",
      "osso_por_papel": {
        "fundo": "330800",
        "painel": "330800",
        "painel_alto": "330800",
        "linha": "330800",
        "texto": "FFF8E0",
        "texto_fraco": "FFF8E0",
        "acento": "330800",
        "tinta": "330800",
        "papel": "330800",
        "painel_baixo": "330800",
        "bloco": "330800",
        "menu_grande": "330800",
        "regua": "330800"
      },
      "aviso_por_papel": {
        "fundo": "D83700",
        "painel": "D03500",
        "painel_alto": "C83300",
        "painel_baixo": "D43600",
        "papel": "D83700",
        "menu_grande": "C83300",
        "tinta": "D43600",
        "acento": "390E00"
      }
    },
    "escuro": {
      "fundo": "2E0800",
      "painel": "520D00",
      "painel_alto": "7A1400",
      "linha": "7A4200",
      "texto": "FFF8E0",
      "texto_fraco": "FFDBB0",
      "acento": "FFB399",
      "tinta": "1F0500",
      "papel": "3E0A00",
      "painel_baixo": "500D00",
      "bloco": "FF9416",
      "menu_grande": "6E1200",
      "regua": "FF5533",
      "osso_por_papel": {
        "fundo": "FFF8E0",
        "painel": "FFF8E0",
        "painel_alto": "FFF8E0",
        "linha": "FFF8E0",
        "texto": "330800",
        "texto_fraco": "330800",
        "acento": "330800",
        "tinta": "FFF8E0",
        "papel": "FFF8E0",
        "painel_baixo": "FFF8E0",
        "bloco": "330800",
        "menu_grande": "FFF8E0",
        "regua": "330800"
      },
      "aviso_por_papel": {
        "fundo": "FFB399",
        "painel": "FFB399",
        "painel_alto": "FFB399",
        "painel_baixo": "FFB399",
        "papel": "FFB399",
        "menu_grande": "FFB399",
        "tinta": "FFB399",
        "acento": "962600"
      }
    }
  },
  "Outono": {
    "claro": {
      "fundo": "FFFCF0",
      "painel": "FFF5D1",
      "painel_alto": "FFEEAD",
      "linha": "B6BCF7",
      "texto": "131820",
      "texto_fraco": "060A32",
      "acento": "F84000",
      "tinta": "FFF9E0",
      "papel": "FFFBEA",
      "painel_baixo": "FFF9E4",
      "bloco": "182AD5",
      "menu_grande": "FFF0B6",
      "regua": "CCA100",
      "osso_por_papel": {
        "fundo": "060A32",
        "painel": "060A32",
        "painel_alto": "060A32",
        "linha": "060A32",
        "texto": "FFF9E0",
        "texto_fraco": "FFF9E0",
        "acento": "060A32",
        "tinta": "060A32",
        "papel": "060A32",
        "painel_baixo": "060A32",
        "bloco": "FFF9E0",
        "menu_grande": "060A32",
        "regua": "060A32"
      },
      "aviso_por_papel": {
        "fundo": "D73700",
        "painel": "CF3500",
        "painel_alto": "C63300",
        "painel_baixo": "D33600",
        "papel": "D73700",
        "menu_grande": "CB3400",
        "tinta": "D33600",
        "acento": "3A0F00"
      }
    },
    "escuro": {
      "fundo": "11151D",
      "painel": "1F2633",
      "painel_alto": "2E384C",
      "linha": "0C156E",
      "texto": "FFF9E0",
      "texto_fraco": "B8BEF7",
      "acento": "FF7444",
      "tinta": "080D17",
      "papel": "171D27",
      "painel_baixo": "1E2532",
      "bloco": "2D3FE8",
      "menu_grande": "253149",
      "regua": "798FB9",
      "osso_por_papel": {
        "fundo": "FFF9E0",
        "painel": "FFF9E0",
        "painel_alto": "FFF9E0",
        "linha": "FFF9E0",
        "texto": "060A32",
        "texto_fraco": "060A32",
        "acento": "060A32",
        "tinta": "FFF9E0",
        "papel": "FFF9E0",
        "painel_baixo": "FFF9E0",
        "bloco": "FFF9E0",
        "menu_grande": "FFF9E0",
        "regua": "060A32"
      },
      "aviso_por_papel": {
        "fundo": "FF7444",
        "painel": "FF7444",
        "painel_alto": "FF794A",
        "painel_baixo": "FF7444",
        "papel": "FF7444",
        "menu_grande": "FF7444",
        "tinta": "FF7444",
        "acento": "661A00"
      }
    }
  },
  "Aquarela": {
    "claro": {
      "fundo": "F2FDF4",
      "painel": "D7F9DE",
      "painel_alto": "B9F4C4",
      "linha": "ADE2FF",
      "texto": "000133",
      "texto_fraco": "002337",
      "acento": "656FFF",
      "tinta": "E5FBE9",
      "papel": "EDFCF0",
      "painel_baixo": "E8FBEC",
      "bloco": "0098ED",
      "menu_grande": "B6FEC4",
      "regua": "06C62A",
      "osso_por_papel": {
        "fundo": "000133",
        "painel": "000133",
        "painel_alto": "000133",
        "linha": "000133",
        "texto": "E5FBE9",
        "texto_fraco": "E5FBE9",
        "acento": "000133",
        "tinta": "000133",
        "papel": "000133",
        "painel_baixo": "000133",
        "bloco": "000133",
        "menu_grande": "000133",
        "regua": "000133"
      },
      "aviso_por_papel": {
        "fundo": "535EFF",
        "painel": "4753FF",
        "painel_alto": "3B48FF",
        "painel_baixo": "4D59FF",
        "papel": "4D59FF",
        "menu_grande": "4753FF",
        "tinta": "4D59FF",
        "acento": "000659"
      }
    },
    "escuro": {
      "fundo": "00012E",
      "painel": "000252",
      "painel_alto": "00037A",
      "linha": "004F7A",
      "texto": "E5FBE9",
      "texto_fraco": "B0E3FF",
      "acento": "B5BAFF",
      "tinta": "00011F",
      "papel": "00013E",
      "painel_baixo": "000250",
      "bloco": "16ACFF",
      "menu_grande": "00036E",
      "regua": "3337FF",
      "osso_por_papel": {
        "fundo": "E5FBE9",
        "painel": "E5FBE9",
        "painel_alto": "E5FBE9",
        "linha": "E5FBE9",
        "texto": "000133",
        "texto_fraco": "000133",
        "acento": "000133",
        "tinta": "E5FBE9",
        "papel": "E5FBE9",
        "painel_baixo": "E5FBE9",
        "bloco": "000133",
        "menu_grande": "E5FBE9",
        "regua": "E5FBE9"
      },
      "aviso_por_papel": {
        "fundo": "B5BAFF",
        "painel": "B5BAFF",
        "painel_alto": "B5BAFF",
        "painel_baixo": "B5BAFF",
        "papel": "B5BAFF",
        "menu_grande": "B5BAFF",
        "tinta": "B5BAFF",
        "acento": "0011FE"
      }
    }
  },
  "Natal": {
    "claro": {
      "fundo": "FFFCF0",
      "painel": "FEF6D3",
      "painel_alto": "FCEFB0",
      "linha": "ECDCC1",
      "texto": "270C0C",
      "texto_fraco": "2A1F0D",
      "acento": "A31D1D",
      "tinta": "FEF9E1",
      "papel": "FEFBEB",
      "painel_baixo": "FEFAE5",
      "bloco": "B58739",
      "menu_grande": "FFF2B6",
      "regua": "CCA900",
      "osso_por_papel": {
        "fundo": "270C0C",
        "painel": "270C0C",
        "painel_alto": "270C0C",
        "linha": "270C0C",
        "texto": "FEF9E1",
        "texto_fraco": "FEF9E1",
        "acento": "FEF9E1",
        "tinta": "270C0C",
        "papel": "270C0C",
        "painel_baixo": "270C0C",
        "bloco": "270C0C",
        "menu_grande": "270C0C",
        "regua": "270C0C"
      },
      "aviso_por_papel": {
        "fundo": "A31D1D",
        "painel": "A31D1D",
        "painel_alto": "A31D1D",
        "painel_baixo": "A31D1D",
        "papel": "A31D1D",
        "menu_grande": "A31D1D",
        "tinta": "A31D1D",
        "acento": "F3BCBC"
      }
    },
    "escuro": {
      "fundo": "230B0B",
      "painel": "3E1414",
      "painel_alto": "5D1E1E",
      "linha": "5D461D",
      "texto": "FEF9E1",
      "texto_fraco": "ECDDC3",
      "acento": "D92C2C",
      "tinta": "170707",
      "papel": "2F0F0F",
      "painel_baixo": "3D1414",
      "bloco": "C79B4E",
      "menu_grande": "5D1111",
      "regua": "DD5555",
      "osso_por_papel": {
        "fundo": "FEF9E1",
        "painel": "FEF9E1",
        "painel_alto": "FEF9E1",
        "linha": "FEF9E1",
        "texto": "270C0C",
        "texto_fraco": "270C0C",
        "acento": "FEF9E1",
        "tinta": "FEF9E1",
        "papel": "FEF9E1",
        "painel_baixo": "FEF9E1",
        "bloco": "270C0C",
        "menu_grande": "FEF9E1",
        "regua": "270C0C"
      },
      "aviso_por_papel": {
        "fundo": "DE4848",
        "painel": "E25D5D",
        "painel_alto": "E87D7D",
        "painel_baixo": "E25D5D",
        "papel": "E05353",
        "menu_grande": "E67272",
        "tinta": "DD4141",
        "acento": "FDF6F6"
      }
    }
  },
  "Halloween": {
    "claro": {
      "fundo": "FEF7F1",
      "painel": "FCE7D4",
      "painel_alto": "F9D3B3",
      "linha": "E8C5CC",
      "texto": "121023",
      "texto_fraco": "271015",
      "acento": "441752",
      "tinta": "FDEFE3",
      "papel": "FEF4EC",
      "painel_baixo": "FDF1E6",
      "bloco": "AA4358",
      "menu_grande": "FFD7B6",
      "regua": "CC5E00",
      "osso_por_papel": {
        "fundo": "121023",
        "painel": "121023",
        "painel_alto": "121023",
        "linha": "121023",
        "texto": "FDEFE3",
        "texto_fraco": "FDEFE3",
        "acento": "FDEFE3",
        "tinta": "121023",
        "papel": "121023",
        "painel_baixo": "121023",
        "bloco": "FDEFE3",
        "menu_grande": "121023",
        "regua": "121023"
      },
      "aviso_por_papel": {
        "fundo": "441752",
        "painel": "441752",
        "painel_alto": "441752",
        "painel_baixo": "441752",
        "papel": "441752",
        "menu_grande": "441752",
        "tinta": "441752",
        "acento": "C176D9"
      }
    },
    "escuro": {
      "fundo": "110F1F",
      "painel": "1D1A37",
      "painel_alto": "2C2753",
      "linha": "58232E",
      "texto": "FDEFE3",
      "texto_fraco": "E9C7CE",
      "acento": "A941CA",
      "tinta": "090817",
      "papel": "16142A",
      "painel_baixo": "1D1A37",
      "bloco": "BD586D",
      "menu_grande": "221C52",
      "regua": "7469C9",
      "osso_por_papel": {
        "fundo": "FDEFE3",
        "painel": "FDEFE3",
        "painel_alto": "FDEFE3",
        "linha": "FDEFE3",
        "texto": "121023",
        "texto_fraco": "121023",
        "acento": "FFFFFF",
        "tinta": "FDEFE3",
        "papel": "FDEFE3",
        "painel_baixo": "FDEFE3",
        "bloco": "000000",
        "menu_grande": "FDEFE3",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "B254CF",
        "painel": "B761D3",
        "painel_alto": "C177D9",
        "painel_baixo": "B761D3",
        "papel": "B45AD1",
        "menu_grande": "BC6AD5",
        "tinta": "AF4ECE",
        "acento": "FBF5FC"
      }
    }
  },
  "Páscoa": {
    "claro": {
      "fundo": "FBFFF0",
      "painel": "F3FFD1",
      "painel_alto": "EAFFAD",
      "linha": "BEE5EF",
      "texto": "2F041A",
      "texto_fraco": "0B262C",
      "acento": "199A2A",
      "tinta": "F7FFE0",
      "papel": "FAFFEA",
      "painel_baixo": "F8FFE4",
      "bloco": "2FA2BE",
      "menu_grande": "ECFFB6",
      "regua": "98CC00",
      "osso_por_papel": {
        "fundo": "2F041A",
        "painel": "2F041A",
        "painel_alto": "2F041A",
        "linha": "2F041A",
        "texto": "F7FFE0",
        "texto_fraco": "F7FFE0",
        "acento": "2F041A",
        "tinta": "2F041A",
        "papel": "2F041A",
        "painel_baixo": "2F041A",
        "bloco": "2F041A",
        "menu_grande": "2F041A",
        "regua": "2F041A"
      },
      "aviso_por_papel": {
        "fundo": "168825",
        "painel": "168524",
        "painel_alto": "158324",
        "painel_baixo": "168524",
        "papel": "168524",
        "menu_grande": "158324",
        "tinta": "168524",
        "acento": "06240A"
      }
    },
    "escuro": {
      "fundo": "2B0318",
      "painel": "4C062A",
      "painel_alto": "72093F",
      "linha": "185462",
      "texto": "F7FFE0",
      "texto_fraco": "C0E6EF",
      "acento": "DAF9DE",
      "tinta": "1C0210",
      "papel": "390420",
      "painel_baixo": "4B062A",
      "bloco": "45B5D0",
      "menu_grande": "6E0039",
      "regua": "FF339D",
      "osso_por_papel": {
        "fundo": "F7FFE0",
        "painel": "F7FFE0",
        "painel_alto": "F7FFE0",
        "linha": "F7FFE0",
        "texto": "2F041A",
        "texto_fraco": "2F041A",
        "acento": "2F041A",
        "tinta": "F7FFE0",
        "papel": "F7FFE0",
        "painel_baixo": "F7FFE0",
        "bloco": "2F041A",
        "menu_grande": "F7FFE0",
        "regua": "2F041A"
      },
      "aviso_por_papel": {
        "fundo": "DAF9DE",
        "painel": "DAF9DE",
        "painel_alto": "DAF9DE",
        "painel_baixo": "DAF9DE",
        "papel": "DAF9DE",
        "menu_grande": "DAF9DE",
        "tinta": "DAF9DE",
        "acento": "157F22"
      }
    }
  },
  "Réveillon": {
    "claro": {
      "fundo": "FCFAF2",
      "painel": "F7F1D9",
      "painel_alto": "F1E7BB",
      "linha": "E8E4C4",
      "texto": "1D1616",
      "texto_fraco": "28250F",
      "acento": "E43636",
      "tinta": "FAF6E5",
      "papel": "FCF9EE",
      "painel_baixo": "FBF7E9",
      "bloco": "ABA042",
      "menu_grande": "FBEFBA",
      "regua": "BE9C0E",
      "osso_por_papel": {
        "fundo": "1D1616",
        "painel": "1D1616",
        "painel_alto": "1D1616",
        "linha": "1D1616",
        "texto": "FAF6E5",
        "texto_fraco": "FAF6E5",
        "acento": "000000",
        "tinta": "1D1616",
        "papel": "1D1616",
        "painel_baixo": "1D1616",
        "bloco": "1D1616",
        "menu_grande": "1D1616",
        "regua": "1D1616"
      },
      "aviso_por_papel": {
        "fundo": "E12121",
        "painel": "D71D1D",
        "painel_alto": "CB1B1B",
        "painel_baixo": "DC1D1D",
        "papel": "E01E1E",
        "menu_grande": "D31C1C",
        "tinta": "DC1D1D",
        "acento": "210404"
      }
    },
    "escuro": {
      "fundo": "1A1414",
      "painel": "2E2424",
      "painel_alto": "453636",
      "linha": "585222",
      "texto": "FAF6E5",
      "texto_fraco": "E9E5C6",
      "acento": "E43636",
      "tinta": "170808",
      "papel": "231B1B",
      "painel_baixo": "2D2323",
      "bloco": "BEB357",
      "menu_grande": "402E2E",
      "regua": "A58D8D",
      "osso_por_papel": {
        "fundo": "FAF6E5",
        "painel": "FAF6E5",
        "painel_alto": "FAF6E5",
        "linha": "FAF6E5",
        "texto": "1D1616",
        "texto_fraco": "1D1616",
        "acento": "000000",
        "tinta": "FAF6E5",
        "papel": "FAF6E5",
        "painel_baixo": "FAF6E5",
        "bloco": "1D1616",
        "menu_grande": "FAF6E5",
        "regua": "1D1616"
      },
      "aviso_por_papel": {
        "fundo": "E64343",
        "painel": "EA6262",
        "painel_alto": "EF8686",
        "painel_baixo": "E95E5E",
        "papel": "E85151",
        "menu_grande": "ED7676",
        "tinta": "E43636",
        "acento": "210404"
      }
    }
  },
  "Carnaval": {
    "claro": {
      "fundo": "FFFCF0",
      "painel": "FFF7D1",
      "painel_alto": "FFF1AD",
      "linha": "C4E8DA",
      "texto": "131920",
      "texto_fraco": "10281E",
      "acento": "ED4497",
      "tinta": "FFFAE0",
      "papel": "FFFBEA",
      "painel_baixo": "FFFAE4",
      "bloco": "43AA82",
      "menu_grande": "FFF2B6",
      "regua": "CCA800",
      "osso_por_papel": {
        "fundo": "131920",
        "painel": "131920",
        "painel_alto": "131920",
        "linha": "131920",
        "texto": "FFFAE0",
        "texto_fraco": "FFFAE0",
        "acento": "131920",
        "tinta": "131920",
        "papel": "131920",
        "painel_baixo": "131920",
        "bloco": "131920",
        "menu_grande": "131920",
        "regua": "131920"
      },
      "aviso_por_papel": {
        "fundo": "DF1578",
        "painel": "D51573",
        "painel_alto": "D11471",
        "painel_baixo": "DA1576",
        "papel": "DA1576",
        "menu_grande": "D11471",
        "tinta": "DA1576",
        "acento": "410623"
      }
    },
    "escuro": {
      "fundo": "11161D",
      "painel": "1E2834",
      "painel_alto": "2C3B4E",
      "linha": "225843",
      "texto": "FFFAE0",
      "texto_fraco": "C7E9DB",
      "acento": "F599C6",
      "tinta": "080F17",
      "papel": "171E27",
      "painel_baixo": "1D2733",
      "bloco": "58BD95",
      "menu_grande": "22354C",
      "regua": "7595BD",
      "osso_por_papel": {
        "fundo": "FFFAE0",
        "painel": "FFFAE0",
        "painel_alto": "FFFAE0",
        "linha": "FFFAE0",
        "texto": "131920",
        "texto_fraco": "131920",
        "acento": "131920",
        "tinta": "FFFAE0",
        "papel": "FFFAE0",
        "painel_baixo": "FFFAE0",
        "bloco": "131920",
        "menu_grande": "FFFAE0",
        "regua": "131920"
      },
      "aviso_por_papel": {
        "fundo": "F599C6",
        "painel": "F599C6",
        "painel_alto": "F599C6",
        "painel_baixo": "F599C6",
        "papel": "F599C6",
        "menu_grande": "F599C6",
        "tinta": "F599C6",
        "acento": "8B0E4B"
      }
    }
  },
  "Ano Novo Chinês": {
    "claro": {
      "fundo": "FFF9F0",
      "painel": "FEECD2",
      "painel_alto": "FEDEAF",
      "linha": "F5C0B8",
      "texto": "280B0B",
      "texto_fraco": "300C07",
      "acento": "CF6314",
      "tinta": "FFF3E1",
      "papel": "FFF7EB",
      "painel_baixo": "FFF4E5",
      "bloco": "D0351E",
      "menu_grande": "FFE1B6",
      "regua": "CC7A00",
      "osso_por_papel": {
        "fundo": "280B0B",
        "painel": "280B0B",
        "painel_alto": "280B0B",
        "linha": "280B0B",
        "texto": "FFF3E1",
        "texto_fraco": "FFF3E1",
        "acento": "280B0B",
        "tinta": "280B0B",
        "papel": "280B0B",
        "painel_baixo": "280B0B",
        "bloco": "FFF3E1",
        "menu_grande": "280B0B",
        "regua": "280B0B"
      },
      "aviso_por_papel": {
        "fundo": "B75712",
        "painel": "AC5211",
        "painel_alto": "9F4C0F",
        "painel_baixo": "B35611",
        "papel": "B75712",
        "menu_grande": "A24E10",
        "tinta": "B35611",
        "acento": "291404"
      }
    },
    "escuro": {
      "fundo": "240A0A",
      "painel": "411111",
      "painel_alto": "611A1A",
      "linha": "6B1B0F",
      "texto": "FFF3E1",
      "texto_fraco": "F5C2BA",
      "acento": "EB7F31",
      "tinta": "180606",
      "papel": "310D0D",
      "painel_baixo": "401111",
      "bloco": "E24A33",
      "menu_grande": "620C0C",
      "regua": "E64C4C",
      "osso_por_papel": {
        "fundo": "FFF3E1",
        "painel": "FFF3E1",
        "painel_alto": "FFF3E1",
        "linha": "FFF3E1",
        "texto": "280B0B",
        "texto_fraco": "280B0B",
        "acento": "280B0B",
        "tinta": "FFF3E1",
        "papel": "FFF3E1",
        "painel_baixo": "FFF3E1",
        "bloco": "280B0B",
        "menu_grande": "FFF3E1",
        "regua": "280B0B"
      },
      "aviso_por_papel": {
        "fundo": "EB7F31",
        "painel": "EB7F31",
        "painel_alto": "EB7F31",
        "painel_baixo": "EB7F31",
        "papel": "EB7F31",
        "menu_grande": "EB7F31",
        "tinta": "EB7F31",
        "acento": "522708"
      }
    }
  },
  "Tanabata": {
    "claro": {
      "fundo": "FFFDF0",
      "painel": "FFF8D1",
      "painel_alto": "FFF3AD",
      "linha": "ADFFFD",
      "texto": "000633",
      "texto_fraco": "003736",
      "acento": "003161",
      "tinta": "FFFAE0",
      "papel": "FFFCEA",
      "painel_baixo": "FFFBE4",
      "bloco": "00EDE6",
      "menu_grande": "FFF4B6",
      "regua": "CCAD00",
      "osso_por_papel": {
        "fundo": "000633",
        "painel": "000633",
        "painel_alto": "000633",
        "linha": "000633",
        "texto": "FFFAE0",
        "texto_fraco": "FFFAE0",
        "acento": "FFFAE0",
        "tinta": "000633",
        "papel": "000633",
        "painel_baixo": "000633",
        "bloco": "000633",
        "menu_grande": "000633",
        "regua": "000633"
      },
      "aviso_por_papel": {
        "fundo": "003161",
        "painel": "003161",
        "painel_alto": "003161",
        "painel_baixo": "003161",
        "papel": "003161",
        "menu_grande": "003161",
        "tinta": "003161",
        "acento": "379CFF"
      }
    },
    "escuro": {
      "fundo": "00062E",
      "painel": "000A52",
      "painel_alto": "000F7A",
      "linha": "007A77",
      "texto": "FFFAE0",
      "texto_fraco": "B0FFFD",
      "acento": "0069CF",
      "tinta": "00041F",
      "papel": "00083E",
      "painel_baixo": "000A50",
      "bloco": "16FFF8",
      "menu_grande": "000E6E",
      "regua": "334CFF",
      "osso_por_papel": {
        "fundo": "FFFAE0",
        "painel": "FFFAE0",
        "painel_alto": "FFFAE0",
        "linha": "FFFAE0",
        "texto": "000633",
        "texto_fraco": "000633",
        "acento": "FFFAE0",
        "tinta": "FFFAE0",
        "papel": "FFFAE0",
        "painel_baixo": "FFFAE0",
        "bloco": "000633",
        "menu_grande": "FFFAE0",
        "regua": "FFFAE0"
      },
      "aviso_por_papel": {
        "fundo": "0078ED",
        "painel": "007DF7",
        "painel_alto": "128AFF",
        "painel_baixo": "007DF7",
        "papel": "007BF2",
        "menu_grande": "0885FF",
        "tinta": "0076E8",
        "acento": "DCEEFF"
      }
    }
  },
  "Hanami": {
    "claro": {
      "fundo": "FBFAF4",
      "painel": "F2EFDE",
      "painel_alto": "E8E3C4",
      "linha": "CFDFCD",
      "texto": "260D0D",
      "texto_fraco": "172215",
      "acento": "438D6C",
      "tinta": "F8F6E7",
      "papel": "F9F8F0",
      "painel_baixo": "F7F6EC",
      "bloco": "61925C",
      "menu_grande": "F0EAC5",
      "regua": "A08F2C",
      "osso_por_papel": {
        "fundo": "260D0D",
        "painel": "260D0D",
        "painel_alto": "260D0D",
        "linha": "260D0D",
        "texto": "F6F4E9",
        "texto_fraco": "F6F4E9",
        "acento": "260D0D",
        "tinta": "260D0D",
        "papel": "260D0D",
        "painel_baixo": "260D0D",
        "bloco": "260D0D",
        "menu_grande": "260D0D",
        "regua": "260D0D"
      },
      "aviso_por_papel": {
        "fundo": "3C7F61",
        "painel": "39785C",
        "painel_alto": "346E55",
        "painel_baixo": "3B7D5F",
        "papel": "3B7D5F",
        "menu_grande": "377358",
        "tinta": "3B7D5F",
        "acento": "0B1812"
      }
    },
    "escuro": {
      "fundo": "220C0C",
      "painel": "3C1515",
      "painel_alto": "5B2020",
      "linha": "324B2F",
      "texto": "F6F4E9",
      "texto_fraco": "D1E1CF",
      "acento": "C0E1D2",
      "tinta": "170808",
      "papel": "2E1010",
      "painel_baixo": "3C1515",
      "bloco": "75A570",
      "menu_grande": "5B1313",
      "regua": "D95959",
      "osso_por_papel": {
        "fundo": "F6F4E9",
        "painel": "F6F4E9",
        "painel_alto": "F6F4E9",
        "linha": "F6F4E9",
        "texto": "260D0D",
        "texto_fraco": "260D0D",
        "acento": "260D0D",
        "tinta": "F6F4E9",
        "papel": "F6F4E9",
        "painel_baixo": "F6F4E9",
        "bloco": "260D0D",
        "menu_grande": "F6F4E9",
        "regua": "260D0D"
      },
      "aviso_por_papel": {
        "fundo": "C0E1D2",
        "painel": "C0E1D2",
        "painel_alto": "C0E1D2",
        "painel_baixo": "C0E1D2",
        "papel": "C0E1D2",
        "menu_grande": "C0E1D2",
        "tinta": "C0E1D2",
        "acento": "31684F"
      }
    }
  },
  "Obon": {
    "claro": {
      "fundo": "FCFAF3",
      "painel": "F5EFDC",
      "painel_alto": "ECE3C0",
      "linha": "F6C8B6",
      "texto": "11240F",
      "texto_fraco": "311206",
      "acento": "E3530D",
      "tinta": "F8F5E7",
      "papel": "FAF8EF",
      "painel_baixo": "F9F6EA",
      "bloco": "D44D19",
      "menu_grande": "F5EAC0",
      "regua": "AE901E",
      "osso_por_papel": {
        "fundo": "311206",
        "painel": "311206",
        "painel_alto": "311206",
        "linha": "311206",
        "texto": "F8F5E7",
        "texto_fraco": "F8F5E7",
        "acento": "311206",
        "tinta": "311206",
        "papel": "311206",
        "painel_baixo": "311206",
        "bloco": "000000",
        "menu_grande": "311206",
        "regua": "311206"
      },
      "aviso_por_papel": {
        "fundo": "C9490B",
        "painel": "BD450B",
        "painel_alto": "AE400A",
        "painel_baixo": "C5480B",
        "papel": "C5480B",
        "menu_grande": "B6420A",
        "tinta": "C1470B",
        "acento": "311203"
      }
    },
    "escuro": {
      "fundo": "0F200E",
      "painel": "1B3919",
      "painel_alto": "285625",
      "linha": "6D280D",
      "texto": "F8F5E7",
      "texto_fraco": "F7CAB9",
      "acento": "F5824A",
      "tinta": "091708",
      "papel": "142B13",
      "painel_baixo": "1A3818",
      "bloco": "E6612F",
      "menu_grande": "1D5519",
      "regua": "6BCE64",
      "osso_por_papel": {
        "fundo": "F8F5E7",
        "painel": "F8F5E7",
        "painel_alto": "F8F5E7",
        "linha": "F8F5E7",
        "texto": "311206",
        "texto_fraco": "311206",
        "acento": "311206",
        "tinta": "F8F5E7",
        "papel": "F8F5E7",
        "painel_baixo": "F8F5E7",
        "bloco": "311206",
        "menu_grande": "F8F5E7",
        "regua": "311206"
      },
      "aviso_por_papel": {
        "fundo": "F5824A",
        "painel": "F5824A",
        "painel_alto": "F8AA83",
        "painel_baixo": "F5824A",
        "papel": "F5824A",
        "menu_grande": "F8A57D",
        "tinta": "F5824A",
        "acento": "602305"
      }
    }
  },
  "Setsubun": {
    "claro": {
      "fundo": "FFFCF0",
      "painel": "FFF6D1",
      "painel_alto": "FFEFAD",
      "linha": "FFCDAD",
      "texto": "2D062B",
      "texto_fraco": "371500",
      "acento": "B12C00",
      "tinta": "FFF9E0",
      "papel": "FFFBEA",
      "painel_baixo": "FFFAE4",
      "bloco": "ED5C00",
      "menu_grande": "FFF1B6",
      "regua": "CCA300",
      "osso_por_papel": {
        "fundo": "2D062B",
        "painel": "2D062B",
        "painel_alto": "2D062B",
        "linha": "2D062B",
        "texto": "FFF9E0",
        "texto_fraco": "FFF9E0",
        "acento": "FFF9E0",
        "tinta": "2D062B",
        "papel": "2D062B",
        "painel_baixo": "2D062B",
        "bloco": "2D062B",
        "menu_grande": "2D062B",
        "regua": "2D062B"
      },
      "aviso_por_papel": {
        "fundo": "B12C00",
        "painel": "B12C00",
        "painel_alto": "B12C00",
        "painel_baixo": "B12C00",
        "papel": "B12C00",
        "menu_grande": "B12C00",
        "tinta": "B12C00",
        "acento": "FFCDBC"
      }
    },
    "escuro": {
      "fundo": "290527",
      "painel": "480945",
      "painel_alto": "6C0E67",
      "linha": "7A2F00",
      "texto": "FFF9E0",
      "texto_fraco": "FFCFB0",
      "acento": "E33800",
      "tinta": "1B041A",
      "papel": "370734",
      "painel_baixo": "470944",
      "bloco": "FF7016",
      "menu_grande": "6E0068",
      "regua": "FF33F3",
      "osso_por_papel": {
        "fundo": "FFF9E0",
        "painel": "FFF9E0",
        "painel_alto": "FFF9E0",
        "linha": "FFF9E0",
        "texto": "2D062B",
        "texto_fraco": "2D062B",
        "acento": "000000",
        "tinta": "FFF9E0",
        "papel": "FFF9E0",
        "painel_baixo": "FFF9E0",
        "bloco": "2D062B",
        "menu_grande": "FFF9E0",
        "regua": "2D062B"
      },
      "aviso_por_papel": {
        "fundo": "EC3A00",
        "painel": "FF4D13",
        "painel_alto": "FF835A",
        "painel_baixo": "FF4D13",
        "papel": "FB3E00",
        "menu_grande": "FF7F55",
        "tinta": "E83900",
        "acento": "170600"
      }
    }
  },
  "Kitsune": {
    "claro": {
      "fundo": "FFFCF0",
      "painel": "FFF7D1",
      "painel_alto": "FFF1AD",
      "linha": "FFECAD",
      "texto": "331300",
      "texto_fraco": "372A00",
      "acento": "CC7000",
      "tinta": "FFFAE0",
      "papel": "FFFCEA",
      "painel_baixo": "FFFAE4",
      "bloco": "EDB500",
      "menu_grande": "FFF2B6",
      "regua": "CCAA00",
      "osso_por_papel": {
        "fundo": "331300",
        "painel": "331300",
        "painel_alto": "331300",
        "linha": "331300",
        "texto": "FFFAE0",
        "texto_fraco": "FFFAE0",
        "acento": "331300",
        "tinta": "331300",
        "papel": "331300",
        "painel_baixo": "331300",
        "bloco": "331300",
        "menu_grande": "331300",
        "regua": "331300"
      },
      "aviso_por_papel": {
        "fundo": "AD5F00",
        "painel": "AA5D00",
        "painel_alto": "A35A00",
        "painel_baixo": "AD5F00",
        "papel": "AD5F00",
        "menu_grande": "A75B00",
        "tinta": "AD5F00",
        "acento": "331C00"
      }
    },
    "escuro": {
      "fundo": "2E1100",
      "painel": "521E00",
      "painel_alto": "7A2E00",
      "linha": "7A5E00",
      "texto": "FFFAE0",
      "texto_fraco": "FFEDB0",
      "acento": "FF8C00",
      "tinta": "1F0B00",
      "papel": "3E1700",
      "painel_baixo": "501E00",
      "bloco": "FFC816",
      "menu_grande": "6E2A00",
      "regua": "FF7F33",
      "osso_por_papel": {
        "fundo": "FFFAE0",
        "painel": "FFFAE0",
        "painel_alto": "FFFAE0",
        "linha": "FFFAE0",
        "texto": "331300",
        "texto_fraco": "331300",
        "acento": "331300",
        "tinta": "FFFAE0",
        "papel": "FFFAE0",
        "painel_baixo": "FFFAE0",
        "bloco": "331300",
        "menu_grande": "FFFAE0",
        "regua": "331300"
      },
      "aviso_por_papel": {
        "fundo": "FF8C00",
        "painel": "FF8C00",
        "painel_alto": "FF9D26",
        "painel_baixo": "FF8C00",
        "papel": "FF8C00",
        "menu_grande": "FF8C00",
        "tinta": "FF8C00",
        "acento": "5D3300"
      }
    }
  },
  "Tengu": {
    "claro": {
      "fundo": "FAF9F4",
      "painel": "F1EEDF",
      "painel_alto": "E7E1C6",
      "linha": "D6DBD1",
      "texto": "330000",
      "texto_fraco": "1B1F18",
      "acento": "6D0808",
      "tinta": "F8F5E7",
      "papel": "F9F7F1",
      "painel_baixo": "F7F5EC",
      "bloco": "758568",
      "menu_grande": "EEE7C6",
      "regua": "9C8930",
      "osso_por_papel": {
        "fundo": "330000",
        "painel": "330000",
        "painel_alto": "330000",
        "linha": "330000",
        "texto": "F6F4EA",
        "texto_fraco": "F6F4EA",
        "acento": "F6F4EA",
        "tinta": "330000",
        "papel": "330000",
        "painel_baixo": "330000",
        "bloco": "330000",
        "menu_grande": "330000",
        "regua": "330000"
      },
      "aviso_por_papel": {
        "fundo": "6D0808",
        "painel": "6D0808",
        "painel_alto": "6D0808",
        "painel_baixo": "6D0808",
        "papel": "6D0808",
        "menu_grande": "6D0808",
        "tinta": "6D0808",
        "acento": "F57979"
      }
    },
    "escuro": {
      "fundo": "2E0000",
      "painel": "520000",
      "painel_alto": "7A0000",
      "linha": "3C4536",
      "texto": "F6F4EA",
      "texto_fraco": "D7DCD3",
      "acento": "E71111",
      "tinta": "1F0000",
      "papel": "3E0000",
      "painel_baixo": "500000",
      "bloco": "88987C",
      "menu_grande": "6E0000",
      "regua": "FF3333",
      "osso_por_papel": {
        "fundo": "F6F4EA",
        "painel": "F6F4EA",
        "painel_alto": "F6F4EA",
        "linha": "F6F4EA",
        "texto": "330000",
        "texto_fraco": "330000",
        "acento": "FFFFFF",
        "tinta": "F6F4EA",
        "papel": "F6F4EA",
        "painel_baixo": "F6F4EA",
        "bloco": "330000",
        "menu_grande": "F6F4EA",
        "regua": "330000"
      },
      "aviso_por_papel": {
        "fundo": "EF2B2B",
        "painel": "F25454",
        "painel_alto": "F68181",
        "painel_baixo": "F25050",
        "papel": "F13C3C",
        "menu_grande": "F57575",
        "tinta": "EE1717",
        "acento": "FFFFFF"
      }
    }
  },
  "Yuki-Onna": {
    "claro": {
      "fundo": "F1F8FE",
      "painel": "D4EBFC",
      "painel_alto": "B3DCFA",
      "linha": "B2DAFB",
      "texto": "04152F",
      "texto_fraco": "031E34",
      "acento": "0C7DD9",
      "tinta": "E2F2FD",
      "papel": "ECF6FE",
      "painel_baixo": "E6F3FD",
      "bloco": "0C83E1",
      "menu_grande": "B6E0FF",
      "regua": "0076CC",
      "osso_por_papel": {
        "fundo": "04152F",
        "painel": "04152F",
        "painel_alto": "04152F",
        "linha": "04152F",
        "texto": "E2F2FD",
        "texto_fraco": "E2F2FD",
        "acento": "000000",
        "tinta": "04152F",
        "papel": "04152F",
        "painel_baixo": "04152F",
        "bloco": "04152F",
        "menu_grande": "04152F",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "0B73C7",
        "painel": "0A6AB8",
        "painel_alto": "095EA3",
        "painel_baixo": "0B70C3",
        "papel": "0B70C3",
        "menu_grande": "0962AA",
        "tinta": "0B6EC0",
        "acento": "010F19"
      }
    },
    "escuro": {
      "fundo": "03132A",
      "painel": "06214C",
      "painel_alto": "093271",
      "linha": "064374",
      "texto": "E2F2FD",
      "texto_fraco": "B4DCFB",
      "acento": "90CAF9",
      "tinta": "020C1C",
      "papel": "051939",
      "painel_baixo": "06214A",
      "bloco": "2296F3",
      "menu_grande": "002B6E",
      "regua": "3383FF",
      "osso_por_papel": {
        "fundo": "E2F2FD",
        "painel": "E2F2FD",
        "painel_alto": "E2F2FD",
        "linha": "E2F2FD",
        "texto": "04152F",
        "texto_fraco": "04152F",
        "acento": "04152F",
        "tinta": "E2F2FD",
        "papel": "E2F2FD",
        "painel_baixo": "E2F2FD",
        "bloco": "04152F",
        "menu_grande": "E2F2FD",
        "regua": "04152F"
      },
      "aviso_por_papel": {
        "fundo": "90CAF9",
        "painel": "90CAF9",
        "painel_alto": "90CAF9",
        "painel_baixo": "90CAF9",
        "papel": "90CAF9",
        "menu_grande": "90CAF9",
        "tinta": "90CAF9",
        "acento": "08528F"
      }
    }
  },
  "Kappa": {
    "claro": {
      "fundo": "F3FBFB",
      "painel": "DCF4F2",
      "painel_alto": "C1ECE8",
      "linha": "C2D4EA",
      "texto": "09092A",
      "texto_fraco": "0E1A29",
      "acento": "232F72",
      "tinta": "E7F8F7",
      "papel": "EFFAF9",
      "painel_baixo": "EBF9F7",
      "bloco": "3C70B1",
      "menu_grande": "C0F5F0",
      "regua": "20ACA0",
      "osso_por_papel": {
        "fundo": "09092A",
        "painel": "09092A",
        "painel_alto": "09092A",
        "linha": "09092A",
        "texto": "E8F8F6",
        "texto_fraco": "E8F8F6",
        "acento": "E8F8F6",
        "tinta": "09092A",
        "papel": "09092A",
        "painel_baixo": "09092A",
        "bloco": "E8F8F6",
        "menu_grande": "09092A",
        "regua": "09092A"
      },
      "aviso_por_papel": {
        "fundo": "232F72",
        "painel": "232F72",
        "painel_alto": "232F72",
        "painel_baixo": "232F72",
        "papel": "232F72",
        "menu_grande": "232F72",
        "tinta": "232F72",
        "acento": "919CDD"
      }
    },
    "escuro": {
      "fundo": "080826",
      "painel": "0E0F44",
      "painel_alto": "151666",
      "linha": "1F3A5B",
      "texto": "E8F8F6",
      "texto_fraco": "C4D5EB",
      "acento": "5062C9",
      "tinta": "050519",
      "papel": "0B0B33",
      "painel_baixo": "0E0E43",
      "bloco": "5184C4",
      "menu_grande": "060768",
      "regua": "4144F1",
      "osso_por_papel": {
        "fundo": "E8F8F6",
        "painel": "E8F8F6",
        "painel_alto": "E8F8F6",
        "linha": "E8F8F6",
        "texto": "09092A",
        "texto_fraco": "09092A",
        "acento": "E8F8F6",
        "tinta": "E8F8F6",
        "papel": "E8F8F6",
        "painel_baixo": "E8F8F6",
        "bloco": "09092A",
        "menu_grande": "E8F8F6",
        "regua": "E8F8F6"
      },
      "aviso_por_papel": {
        "fundo": "6474CF",
        "painel": "6A7AD1",
        "painel_alto": "7684D5",
        "painel_baixo": "6A7AD1",
        "papel": "6777D0",
        "menu_grande": "707FD3",
        "tinta": "6272CE",
        "acento": "EBEDF9"
      }
    }
  },
  "Nekomata": {
    "claro": {
      "fundo": "F9F9F6",
      "painel": "EDECE3",
      "painel_alto": "E0DDCD",
      "linha": "DBD7D1",
      "texto": "32012F",
      "texto_fraco": "1F1C18",
      "acento": "D06000",
      "tinta": "F8F5E7",
      "papel": "F7F6F2",
      "painel_baixo": "F5F4EE",
      "bloco": "857A68",
      "menu_grande": "E6E2CF",
      "regua": "857B47",
      "osso_por_papel": {
        "fundo": "32012F",
        "painel": "32012F",
        "painel_alto": "32012F",
        "linha": "32012F",
        "texto": "F3F2EC",
        "texto_fraco": "F3F2EC",
        "acento": "32012F",
        "tinta": "32012F",
        "papel": "32012F",
        "painel_baixo": "32012F",
        "bloco": "000000",
        "menu_grande": "32012F",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "B85500",
        "painel": "AD5000",
        "painel_alto": "9C4800",
        "painel_baixo": "B45300",
        "papel": "B45300",
        "menu_grande": "A34B00",
        "tinta": "B45300",
        "acento": "261200"
      }
    },
    "escuro": {
      "fundo": "2D012A",
      "painel": "50024B",
      "painel_alto": "780271",
      "linha": "453F36",
      "texto": "F3F2EC",
      "texto_fraco": "DCD9D3",
      "acento": "F97300",
      "tinta": "1E011C",
      "papel": "3D0139",
      "painel_baixo": "4F024A",
      "bloco": "988E7C",
      "menu_grande": "6E0068",
      "regua": "FF33F3",
      "osso_por_papel": {
        "fundo": "F3F2EC",
        "painel": "F3F2EC",
        "painel_alto": "F3F2EC",
        "linha": "F3F2EC",
        "texto": "32012F",
        "texto_fraco": "32012F",
        "acento": "32012F",
        "tinta": "F3F2EC",
        "papel": "F3F2EC",
        "painel_baixo": "F3F2EC",
        "bloco": "32012F",
        "menu_grande": "F3F2EC",
        "regua": "32012F"
      },
      "aviso_por_papel": {
        "fundo": "F97300",
        "painel": "F97300",
        "painel_alto": "FF8F2E",
        "painel_baixo": "F97300",
        "papel": "F97300",
        "menu_grande": "FF8114",
        "tinta": "F97300",
        "acento": "532600"
      }
    }
  },
  "Ryu": {
    "claro": {
      "fundo": "FBFAF3",
      "painel": "F4EFDC",
      "painel_alto": "ECE3C1",
      "linha": "EEE0BF",
      "texto": "15171E",
      "texto_fraco": "2B220C",
      "acento": "B4752B",
      "tinta": "F8F5E7",
      "papel": "FAF8EF",
      "painel_baixo": "F9F6EB",
      "bloco": "BB9232",
      "menu_grande": "F5EAC0",
      "regua": "AC8F20",
      "osso_por_papel": {
        "fundo": "15171E",
        "painel": "15171E",
        "painel_alto": "15171E",
        "linha": "15171E",
        "texto": "F8F4E8",
        "texto_fraco": "F8F4E8",
        "acento": "15171E",
        "tinta": "15171E",
        "papel": "15171E",
        "painel_baixo": "15171E",
        "bloco": "15171E",
        "menu_grande": "15171E",
        "regua": "15171E"
      },
      "aviso_por_papel": {
        "fundo": "9F6726",
        "painel": "936023",
        "painel_alto": "8A5A21",
        "painel_baixo": "9C6525",
        "papel": "9C6525",
        "menu_grande": "905E22",
        "tinta": "996325",
        "acento": "241709"
      }
    },
    "escuro": {
      "fundo": "13151B",
      "painel": "222530",
      "painel_alto": "333748",
      "linha": "614B1A",
      "texto": "F8F4E8",
      "texto_fraco": "EEE1C1",
      "acento": "DAA464",
      "tinta": "080B17",
      "papel": "1A1C24",
      "painel_baixo": "21242F",
      "bloco": "CEA547",
      "menu_grande": "2A2F44",
      "regua": "828DB0",
      "osso_por_papel": {
        "fundo": "F8F4E8",
        "painel": "F8F4E8",
        "painel_alto": "F8F4E8",
        "linha": "F8F4E8",
        "texto": "15171E",
        "texto_fraco": "15171E",
        "acento": "15171E",
        "tinta": "F8F4E8",
        "papel": "F8F4E8",
        "painel_baixo": "F8F4E8",
        "bloco": "15171E",
        "menu_grande": "F8F4E8",
        "regua": "15171E"
      },
      "aviso_por_papel": {
        "fundo": "DAA464",
        "painel": "DAA464",
        "painel_alto": "DAA464",
        "painel_baixo": "DAA464",
        "papel": "DAA464",
        "menu_grande": "DAA464",
        "tinta": "DAA464",
        "acento": "5A3B15"
      }
    }
  },
  "Kirin": {
    "claro": {
      "fundo": "FFFDF0",
      "painel": "FFF9D1",
      "painel_alto": "FFF5AD",
      "linha": "FEDCAF",
      "texto": "2F0404",
      "texto_fraco": "361F01",
      "acento": "C77100",
      "tinta": "FFFBE0",
      "papel": "FFFCEA",
      "painel_baixo": "FFFCE4",
      "bloco": "E98704",
      "menu_grande": "FFF6B6",
      "regua": "CCB300",
      "osso_por_papel": {
        "fundo": "2F0404",
        "painel": "2F0404",
        "painel_alto": "2F0404",
        "linha": "2F0404",
        "texto": "FFFBE0",
        "texto_fraco": "FFFBE0",
        "acento": "2F0404",
        "tinta": "2F0404",
        "papel": "2F0404",
        "painel_baixo": "2F0404",
        "bloco": "2F0404",
        "menu_grande": "2F0404",
        "regua": "2F0404"
      },
      "aviso_por_papel": {
        "fundo": "AC6200",
        "painel": "A96000",
        "painel_alto": "A35C00",
        "painel_baixo": "AC6200",
        "papel": "AC6200",
        "menu_grande": "A65E00",
        "tinta": "A96000",
        "acento": "2E1A00"
      }
    },
    "escuro": {
      "fundo": "2A0404",
      "painel": "4B0707",
      "painel_alto": "700A0A",
      "linha": "784602",
      "texto": "FFFBE0",
      "texto_fraco": "FEDDB2",
      "acento": "FF9B17",
      "tinta": "1C0303",
      "papel": "390505",
      "painel_baixo": "4A0707",
      "bloco": "FB9B1A",
      "menu_grande": "6E0000",
      "regua": "FF3333",
      "osso_por_papel": {
        "fundo": "FFFBE0",
        "painel": "FFFBE0",
        "painel_alto": "FFFBE0",
        "linha": "FFFBE0",
        "texto": "2F0404",
        "texto_fraco": "2F0404",
        "acento": "2F0404",
        "tinta": "FFFBE0",
        "papel": "FFFBE0",
        "painel_baixo": "FFFBE0",
        "bloco": "2F0404",
        "menu_grande": "FFFBE0",
        "regua": "2F0404"
      },
      "aviso_por_papel": {
        "fundo": "FF9B17",
        "painel": "FF9B17",
        "painel_alto": "FF9B17",
        "painel_baixo": "FF9B17",
        "papel": "FF9B17",
        "menu_grande": "FF9B17",
        "tinta": "FF9B17",
        "acento": "663A00"
      }
    }
  },
  "Kyuubi": {
    "claro": {
      "fundo": "FFFDF0",
      "painel": "FEF9D2",
      "painel_alto": "FDF3B0",
      "linha": "F7C6B6",
      "texto": "2F0904",
      "texto_fraco": "321106",
      "acento": "CF6D04",
      "tinta": "FEFBE1",
      "papel": "FEFCEB",
      "painel_baixo": "FEFBE5",
      "bloco": "D54818",
      "menu_grande": "FFF5B6",
      "regua": "CCB300",
      "osso_por_papel": {
        "fundo": "2F0904",
        "painel": "2F0904",
        "painel_alto": "2F0904",
        "linha": "2F0904",
        "texto": "FEFBE1",
        "texto_fraco": "FEFBE1",
        "acento": "2F0904",
        "tinta": "2F0904",
        "papel": "2F0904",
        "painel_baixo": "2F0904",
        "bloco": "000000",
        "menu_grande": "2F0904",
        "regua": "2F0904"
      },
      "aviso_por_papel": {
        "fundo": "B35E03",
        "painel": "AC5B03",
        "painel_alto": "A95903",
        "painel_baixo": "B05D03",
        "papel": "B35E03",
        "menu_grande": "A95903",
        "tinta": "B05D03",
        "acento": "301901"
      }
    },
    "escuro": {
      "fundo": "2A0804",
      "painel": "4B0F06",
      "painel_alto": "71170A",
      "linha": "6E250C",
      "texto": "FEFBE1",
      "texto_fraco": "F7C8B8",
      "acento": "FB9E3A",
      "tinta": "1C0602",
      "papel": "390B05",
      "painel_baixo": "4A0F06",
      "bloco": "E85D2D",
      "menu_grande": "6E0E00",
      "regua": "FF4D33",
      "osso_por_papel": {
        "fundo": "FEFBE1",
        "painel": "FEFBE1",
        "painel_alto": "FEFBE1",
        "linha": "FEFBE1",
        "texto": "2F0904",
        "texto_fraco": "2F0904",
        "acento": "2F0904",
        "tinta": "FEFBE1",
        "papel": "FEFBE1",
        "painel_baixo": "FEFBE1",
        "bloco": "2F0904",
        "menu_grande": "FEFBE1",
        "regua": "2F0904"
      },
      "aviso_por_papel": {
        "fundo": "FB9E3A",
        "painel": "FB9E3A",
        "painel_alto": "FB9E3A",
        "painel_baixo": "FB9E3A",
        "papel": "FB9E3A",
        "menu_grande": "FB9E3A",
        "tinta": "FB9E3A",
        "acento": "6A3802"
      }
    }
  },
  "Baku": {
    "claro": {
      "fundo": "F5F5FA",
      "painel": "E2E1EF",
      "painel_alto": "CBCAE2",
      "linha": "CBCEE1",
      "texto": "070F2C",
      "texto_fraco": "141623",
      "acento": "1B1A55",
      "tinta": "E8E7F8",
      "papel": "F2F2F8",
      "painel_baixo": "EEEEF6",
      "bloco": "566097",
      "menu_grande": "CDCCE9",
      "regua": "423E8E",
      "osso_por_papel": {
        "fundo": "070F2C",
        "painel": "070F2C",
        "painel_alto": "070F2C",
        "linha": "070F2C",
        "texto": "EBEBF4",
        "texto_fraco": "EBEBF4",
        "acento": "EBEBF4",
        "tinta": "070F2C",
        "papel": "070F2C",
        "painel_baixo": "070F2C",
        "bloco": "EBEBF4",
        "menu_grande": "070F2C",
        "regua": "EBEBF4"
      },
      "aviso_por_papel": {
        "fundo": "1B1A55",
        "painel": "1B1A55",
        "painel_alto": "1B1A55",
        "painel_baixo": "1B1A55",
        "papel": "1B1A55",
        "menu_grande": "1B1A55",
        "tinta": "1B1A55",
        "acento": "8180D8"
      }
    },
    "escuro": {
      "fundo": "060E27",
      "painel": "0B1846",
      "painel_alto": "112569",
      "linha": "2D314E",
      "texto": "EBEBF4",
      "texto_fraco": "CDD0E2",
      "acento": "6361CF",
      "tinta": "04091A",
      "papel": "091335",
      "painel_baixo": "0B1845",
      "bloco": "6B74AA",
      "menu_grande": "011A6D",
      "regua": "3A64F8",
      "osso_por_papel": {
        "fundo": "EBEBF4",
        "painel": "EBEBF4",
        "painel_alto": "EBEBF4",
        "linha": "EBEBF4",
        "texto": "070F2C",
        "texto_fraco": "070F2C",
        "acento": "FFFFFF",
        "tinta": "EBEBF4",
        "papel": "EBEBF4",
        "painel_baixo": "EBEBF4",
        "bloco": "000000",
        "menu_grande": "EBEBF4",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "7371D4",
        "painel": "7D7BD7",
        "painel_alto": "8D8BDC",
        "painel_baixo": "7D7BD7",
        "papel": "7876D5",
        "menu_grande": "8583D9",
        "tinta": "706ED3",
        "acento": "F2F2FB"
      }
    }
  },
  "Jorogumo": {
    "claro": {
      "fundo": "FEF1FA",
      "painel": "FCD4F0",
      "painel_alto": "FAB3E4",
      "linha": "E4B4F9",
      "texto": "030530",
      "texto_fraco": "250433",
      "acento": "720455",
      "tinta": "FDE2F5",
      "papel": "FEECF8",
      "painel_baixo": "FDE6F6",
      "bloco": "9E12DB",
      "menu_grande": "FFB6E8",
      "regua": "CC008D",
      "osso_por_papel": {
        "fundo": "030530",
        "painel": "030530",
        "painel_alto": "030530",
        "linha": "030530",
        "texto": "FDE2F5",
        "texto_fraco": "FDE2F5",
        "acento": "FDE2F5",
        "tinta": "030530",
        "papel": "030530",
        "painel_baixo": "030530",
        "bloco": "FDE2F5",
        "menu_grande": "030530",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "720455",
        "painel": "720455",
        "painel_alto": "720455",
        "painel_baixo": "720455",
        "papel": "720455",
        "menu_grande": "720455",
        "tinta": "720455",
        "acento": "FA74D7"
      }
    },
    "escuro": {
      "fundo": "02052C",
      "painel": "04084D",
      "painel_alto": "060D74",
      "linha": "520A71",
      "texto": "FDE2F5",
      "texto_fraco": "E5B7F9",
      "acento": "C40792",
      "tinta": "02031D",
      "papel": "03063B",
      "painel_baixo": "04084C",
      "bloco": "B128ED",
      "menu_grande": "00076E",
      "regua": "333FFF",
      "osso_por_papel": {
        "fundo": "FDE2F5",
        "painel": "FDE2F5",
        "painel_alto": "FDE2F5",
        "linha": "FDE2F5",
        "texto": "030530",
        "texto_fraco": "030530",
        "acento": "FDE2F5",
        "tinta": "FDE2F5",
        "papel": "FDE2F5",
        "painel_baixo": "FDE2F5",
        "bloco": "FFFFFF",
        "menu_grande": "FDE2F5",
        "regua": "FDE2F5"
      },
      "aviso_por_papel": {
        "fundo": "E208A8",
        "painel": "EC08AF",
        "painel_alto": "F726C0",
        "painel_baixo": "EC08AF",
        "papel": "E708AC",
        "menu_grande": "F60DB9",
        "tinta": "E208A8",
        "acento": "FEE1F6"
      }
    }
  },
  "Tanuki": {
    "claro": {
      "fundo": "FBF6F3",
      "painel": "F4E3DC",
      "painel_alto": "ECCEC0",
      "linha": "D1D2DB",
      "texto": "0A1F29",
      "texto_fraco": "18191F",
      "acento": "A56F63",
      "tinta": "F8EDE7",
      "papel": "FAF3EF",
      "painel_baixo": "F9EFEA",
      "bloco": "686C85",
      "menu_grande": "F5D1C0",
      "regua": "AE4B1E",
      "osso_por_papel": {
        "fundo": "18191F",
        "painel": "18191F",
        "painel_alto": "18191F",
        "linha": "18191F",
        "texto": "F8EDE7",
        "texto_fraco": "F8EDE7",
        "acento": "000000",
        "tinta": "18191F",
        "papel": "18191F",
        "painel_baixo": "18191F",
        "bloco": "FFFFFF",
        "menu_grande": "18191F",
        "regua": "F8EDE7"
      },
      "aviso_por_papel": {
        "fundo": "996459",
        "painel": "8C5B50",
        "painel_alto": "7B5047",
        "painel_baixo": "946155",
        "papel": "976357",
        "menu_grande": "7E5248",
        "tinta": "915F54",
        "acento": "19100E"
      }
    },
    "escuro": {
      "fundo": "091C25",
      "painel": "0F3242",
      "painel_alto": "174A63",
      "linha": "363745",
      "texto": "F8EDE7",
      "texto_fraco": "D3D4DC",
      "acento": "A77166",
      "tinta": "061319",
      "papel": "0C2632",
      "painel_baixo": "0F3141",
      "bloco": "7C8098",
      "menu_grande": "094765",
      "regua": "47B6EB",
      "osso_por_papel": {
        "fundo": "F8EDE7",
        "painel": "F8EDE7",
        "painel_alto": "F8EDE7",
        "linha": "F8EDE7",
        "texto": "18191F",
        "texto_fraco": "18191F",
        "acento": "000000",
        "tinta": "F8EDE7",
        "papel": "F8EDE7",
        "painel_baixo": "F8EDE7",
        "bloco": "18191F",
        "menu_grande": "F8EDE7",
        "regua": "18191F"
      },
      "aviso_por_papel": {
        "fundo": "AA766B",
        "painel": "B78B82",
        "painel_alto": "CCACA6",
        "painel_baixo": "B78B82",
        "papel": "B07F75",
        "menu_grande": "C9A7A1",
        "tinta": "A77166",
        "acento": "1C1210"
      }
    }
  },
  "Nurarihyon": {
    "claro": {
      "fundo": "F8F6F6",
      "painel": "EBE5E5",
      "painel_alto": "DBD1D1",
      "linha": "E7CDC5",
      "texto": "1D1616",
      "texto_fraco": "271510",
      "acento": "AE6F00",
      "tinta": "F8E7E7",
      "papel": "F6F3F3",
      "painel_baixo": "F3F0F0",
      "bloco": "A95B44",
      "menu_grande": "E0D4D4",
      "regua": "725A5A",
      "osso_por_papel": {
        "fundo": "1D1616",
        "painel": "1D1616",
        "painel_alto": "1D1616",
        "linha": "1D1616",
        "texto": "F2EEEE",
        "texto_fraco": "F2EEEE",
        "acento": "000000",
        "tinta": "1D1616",
        "papel": "1D1616",
        "painel_baixo": "1D1616",
        "bloco": "FFFFFF",
        "menu_grande": "1D1616",
        "regua": "F2EEEE"
      },
      "aviso_por_papel": {
        "fundo": "9D6400",
        "painel": "8E5B00",
        "painel_alto": "805100",
        "painel_baixo": "976000",
        "papel": "9A6200",
        "menu_grande": "835300",
        "tinta": "945E00",
        "acento": "1A1100"
      }
    },
    "escuro": {
      "fundo": "1A1414",
      "painel": "2E2424",
      "painel_alto": "453636",
      "linha": "572F23",
      "texto": "F2EEEE",
      "texto_fraco": "E8CFC7",
      "acento": "FFB22C",
      "tinta": "170808",
      "papel": "231B1B",
      "painel_baixo": "2D2323",
      "bloco": "BC7059",
      "menu_grande": "402E2E",
      "regua": "A58D8D",
      "osso_por_papel": {
        "fundo": "F2EEEE",
        "painel": "F2EEEE",
        "painel_alto": "F2EEEE",
        "linha": "F2EEEE",
        "texto": "1D1616",
        "texto_fraco": "1D1616",
        "acento": "1D1616",
        "tinta": "F2EEEE",
        "papel": "F2EEEE",
        "painel_baixo": "F2EEEE",
        "bloco": "1D1616",
        "menu_grande": "F2EEEE",
        "regua": "1D1616"
      },
      "aviso_por_papel": {
        "fundo": "FFB22C",
        "painel": "FFB22C",
        "painel_alto": "FFB22C",
        "painel_baixo": "FFB22C",
        "papel": "FFB22C",
        "menu_grande": "FFB22C",
        "tinta": "FFB22C",
        "acento": "6E4600"
      }
    }
  },
  "Momotaro": {
    "claro": {
      "fundo": "FFFEF0",
      "painel": "FFFBD1",
      "painel_alto": "FFF7AD",
      "linha": "D9E1CB",
      "texto": "2B1608",
      "texto_fraco": "1D2314",
      "acento": "D86B04",
      "tinta": "FFFCE0",
      "papel": "FFFDEA",
      "painel_baixo": "FFFCE4",
      "bloco": "7D9657",
      "menu_grande": "FFF8B6",
      "regua": "CCB800",
      "osso_por_papel": {
        "fundo": "2B1608",
        "painel": "2B1608",
        "painel_alto": "2B1608",
        "linha": "2B1608",
        "texto": "FFFCE0",
        "texto_fraco": "FFFCE0",
        "acento": "2B1608",
        "tinta": "2B1608",
        "papel": "2B1608",
        "painel_baixo": "2B1608",
        "bloco": "2B1608",
        "menu_grande": "2B1608",
        "regua": "2B1608"
      },
      "aviso_por_papel": {
        "fundo": "B85B03",
        "painel": "B45903",
        "painel_alto": "B05703",
        "painel_baixo": "B45903",
        "papel": "B85B03",
        "menu_grande": "B05703",
        "tinta": "B45903",
        "acento": "361B01"
      }
    },
    "escuro": {
      "fundo": "271407",
      "painel": "45240C",
      "painel_alto": "683612",
      "linha": "414D2D",
      "texto": "FFFCE0",
      "texto_fraco": "DAE2CD",
      "acento": "FDC086",
      "tinta": "1A0D05",
      "papel": "351B09",
      "painel_baixo": "44230C",
      "bloco": "91A96C",
      "menu_grande": "6B2F03",
      "regua": "F6883C",
      "osso_por_papel": {
        "fundo": "FFFCE0",
        "painel": "FFFCE0",
        "painel_alto": "FFFCE0",
        "linha": "FFFCE0",
        "texto": "2B1608",
        "texto_fraco": "2B1608",
        "acento": "2B1608",
        "tinta": "FFFCE0",
        "papel": "FFFCE0",
        "painel_baixo": "FFFCE0",
        "bloco": "2B1608",
        "menu_grande": "FFFCE0",
        "regua": "2B1608"
      },
      "aviso_por_papel": {
        "fundo": "FDC086",
        "painel": "FDC086",
        "painel_alto": "FDC086",
        "painel_baixo": "FDC086",
        "papel": "FDC086",
        "menu_grande": "FDC086",
        "tinta": "FDC086",
        "acento": "854202"
      }
    }
  },
  "Urashima Tarō": {
    "claro": {
      "fundo": "F9F9F6",
      "painel": "ECECE4",
      "painel_alto": "DDDDD0",
      "linha": "C1EBE5",
      "texto": "14151F",
      "texto_fraco": "0D2A25",
      "acento": "118AB2",
      "tinta": "F8F8E7",
      "papel": "F6F6F3",
      "painel_baixo": "F4F4EF",
      "bloco": "3AB4A0",
      "menu_grande": "E2E2D2",
      "regua": "7B7B51",
      "osso_por_papel": {
        "fundo": "14151F",
        "painel": "14151F",
        "painel_alto": "14151F",
        "linha": "14151F",
        "texto": "F2F2ED",
        "texto_fraco": "F2F2ED",
        "acento": "14151F",
        "tinta": "14151F",
        "papel": "14151F",
        "painel_baixo": "14151F",
        "bloco": "14151F",
        "menu_grande": "14151F",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "0F7CA0",
        "painel": "0E7394",
        "painel_alto": "0D6886",
        "painel_baixo": "0F789A",
        "papel": "0F7A9D",
        "menu_grande": "0D6C8B",
        "tinta": "0F7A9D",
        "acento": "031921"
      }
    },
    "escuro": {
      "fundo": "12131C",
      "painel": "1F2132",
      "painel_alto": "2F324C",
      "linha": "1E5D53",
      "texto": "F2F2ED",
      "texto_fraco": "C4ECE6",
      "acento": "118AB2",
      "tinta": "080917",
      "papel": "181926",
      "painel_baixo": "1F2132",
      "bloco": "4FC6B4",
      "menu_grande": "262949",
      "regua": "7A81B8",
      "osso_por_papel": {
        "fundo": "F2F2ED",
        "painel": "F2F2ED",
        "painel_alto": "F2F2ED",
        "linha": "F2F2ED",
        "texto": "14151F",
        "texto_fraco": "14151F",
        "acento": "14151F",
        "tinta": "F2F2ED",
        "papel": "F2F2ED",
        "painel_baixo": "F2F2ED",
        "bloco": "14151F",
        "menu_grande": "F2F2ED",
        "regua": "14151F"
      },
      "aviso_por_papel": {
        "fundo": "118AB2",
        "painel": "1295C0",
        "painel_alto": "15A8D8",
        "painel_baixo": "1295C0",
        "papel": "118EB7",
        "menu_grande": "14A0CF",
        "tinta": "118AB2",
        "acento": "031921"
      }
    }
  },
  "Kaguya-Hime": {
    "claro": {
      "fundo": "FAF8F4",
      "painel": "F1EADF",
      "painel_alto": "E6DAC6",
      "linha": "CBD3E1",
      "texto": "0A0E29",
      "texto_fraco": "141A23",
      "acento": "4B5694",
      "tinta": "F8F2E7",
      "papel": "F9F6F1",
      "painel_baixo": "F7F3EC",
      "bloco": "576E97",
      "menu_grande": "EEDFC7",
      "regua": "9A7332",
      "osso_por_papel": {
        "fundo": "0A0E29",
        "painel": "0A0E29",
        "painel_alto": "0A0E29",
        "linha": "0A0E29",
        "texto": "F6F1EA",
        "texto_fraco": "F6F1EA",
        "acento": "F6F1EA",
        "tinta": "0A0E29",
        "papel": "0A0E29",
        "painel_baixo": "0A0E29",
        "bloco": "F6F1EA",
        "menu_grande": "0A0E29",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "4B5694",
        "painel": "4B5694",
        "painel_alto": "4B5694",
        "painel_baixo": "4B5694",
        "papel": "4B5694",
        "menu_grande": "4B5694",
        "tinta": "4B5694",
        "acento": "CFD3E7"
      }
    },
    "escuro": {
      "fundo": "090D25",
      "painel": "101741",
      "painel_alto": "182362",
      "linha": "2D394E",
      "texto": "F6F1EA",
      "texto_fraco": "CDD5E2",
      "acento": "5D69AD",
      "tinta": "060918",
      "papel": "0C1132",
      "painel_baixo": "101740",
      "bloco": "6B82AA",
      "menu_grande": "0A1764",
      "regua": "495FE9",
      "osso_por_papel": {
        "fundo": "F6F1EA",
        "painel": "F6F1EA",
        "painel_alto": "F6F1EA",
        "linha": "F6F1EA",
        "texto": "0A0E29",
        "texto_fraco": "0A0E29",
        "acento": "F6F1EA",
        "tinta": "F6F1EA",
        "papel": "F6F1EA",
        "painel_baixo": "F6F1EA",
        "bloco": "0A0E29",
        "menu_grande": "F6F1EA",
        "regua": "F6F1EA"
      },
      "aviso_por_papel": {
        "fundo": "6D78B5",
        "painel": "7580B9",
        "painel_alto": "868FC2",
        "painel_baixo": "7580B9",
        "papel": "707BB7",
        "menu_grande": "7D87BD",
        "tinta": "6B76B4",
        "acento": "EFF0F7"
      }
    }
  },
  "Amaterasu": {
    "claro": {
      "fundo": "FEFAF1",
      "painel": "FCF0D4",
      "painel_alto": "FAE5B2",
      "linha": "F5CBB8",
      "texto": "300303",
      "texto_fraco": "301407",
      "acento": "DD5800",
      "tinta": "FDF5E2",
      "papel": "FEF8EC",
      "painel_baixo": "FDF6E6",
      "bloco": "CF571E",
      "menu_grande": "FFEAB6",
      "regua": "CC8F00",
      "osso_por_papel": {
        "fundo": "300303",
        "painel": "300303",
        "painel_alto": "300303",
        "linha": "300303",
        "texto": "FDF5E2",
        "texto_fraco": "FDF5E2",
        "acento": "300303",
        "tinta": "300303",
        "papel": "300303",
        "painel_baixo": "300303",
        "bloco": "000000",
        "menu_grande": "300303",
        "regua": "300303"
      },
      "aviso_por_papel": {
        "fundo": "C34E00",
        "painel": "B84900",
        "painel_alto": "B14600",
        "painel_baixo": "C04C00",
        "papel": "C34E00",
        "menu_grande": "B44800",
        "tinta": "C04C00",
        "acento": "2C1200"
      }
    },
    "escuro": {
      "fundo": "2B0303",
      "painel": "4D0505",
      "painel_alto": "730707",
      "linha": "6B2D10",
      "texto": "FDF5E2",
      "texto_fraco": "F5CDBB",
      "acento": "FF6500",
      "tinta": "1D0202",
      "papel": "3A0404",
      "painel_baixo": "4C0505",
      "bloco": "E16C34",
      "menu_grande": "6E0000",
      "regua": "FF3333",
      "osso_por_papel": {
        "fundo": "FDF5E2",
        "painel": "FDF5E2",
        "painel_alto": "FDF5E2",
        "linha": "FDF5E2",
        "texto": "300303",
        "texto_fraco": "300303",
        "acento": "300303",
        "tinta": "FDF5E2",
        "papel": "FDF5E2",
        "painel_baixo": "FDF5E2",
        "bloco": "300303",
        "menu_grande": "FDF5E2",
        "regua": "300303"
      },
      "aviso_por_papel": {
        "fundo": "FF6500",
        "painel": "FF6500",
        "painel_alto": "FF7A22",
        "painel_baixo": "FF6500",
        "papel": "FF6500",
        "menu_grande": "FF6F11",
        "tinta": "FF6500",
        "acento": "512000"
      }
    }
  },
  "Vazio Infinito": {
    "claro": {
      "fundo": "F1F1FD",
      "painel": "D6D6FA",
      "painel_alto": "B7B7F6",
      "linha": "C1C0EC",
      "texto": "0F0B28",
      "texto_fraco": "0D0D2A",
      "acento": "162E93",
      "tinta": "E4E4FB",
      "papel": "EDEDFD",
      "painel_baixo": "E7E7FC",
      "bloco": "3937B6",
      "menu_grande": "B6B6FF",
      "regua": "0000CC",
      "osso_por_papel": {
        "fundo": "0F0B28",
        "painel": "0F0B28",
        "painel_alto": "0F0B28",
        "linha": "0F0B28",
        "texto": "E4E4FB",
        "texto_fraco": "E4E4FB",
        "acento": "E4E4FB",
        "tinta": "0F0B28",
        "papel": "0F0B28",
        "painel_baixo": "0F0B28",
        "bloco": "E4E4FB",
        "menu_grande": "0F0B28",
        "regua": "E4E4FB"
      },
      "aviso_por_papel": {
        "fundo": "162E93",
        "painel": "162E93",
        "painel_alto": "162E93",
        "painel_baixo": "162E93",
        "papel": "162E93",
        "menu_grande": "162E93",
        "tinta": "162E93",
        "acento": "8DA0EE"
      }
    },
    "escuro": {
      "fundo": "0D0A24",
      "painel": "171140",
      "painel_alto": "231A60",
      "linha": "1D1C5E",
      "texto": "E4E4FB",
      "texto_fraco": "C3C3ED",
      "acento": "4362E3",
      "tinta": "090718",
      "papel": "120D31",
      "painel_baixo": "17113F",
      "bloco": "4E4CC9",
      "menu_grande": "170C62",
      "regua": "604DE5",
      "osso_por_papel": {
        "fundo": "E4E4FB",
        "painel": "E4E4FB",
        "painel_alto": "E4E4FB",
        "linha": "E4E4FB",
        "texto": "0F0B28",
        "texto_fraco": "0F0B28",
        "acento": "FFFFFF",
        "tinta": "E4E4FB",
        "papel": "E4E4FB",
        "painel_baixo": "E4E4FB",
        "bloco": "E4E4FB",
        "menu_grande": "E4E4FB",
        "regua": "E4E4FB"
      },
      "aviso_por_papel": {
        "fundo": "5672E6",
        "painel": "5F7AE7",
        "painel_alto": "6F87EA",
        "painel_baixo": "5F7AE7",
        "papel": "5C77E7",
        "menu_grande": "657FE8",
        "tinta": "536FE5",
        "acento": "EFF2FD"
      }
    }
  },
  "Santuário Malévolo": {
    "claro": {
      "fundo": "FFF4F0",
      "painel": "FFDFD1",
      "painel_alto": "FFC6AD",
      "linha": "FFBCAD",
      "texto": "1B0033",
      "texto_fraco": "370A00",
      "acento": "500073",
      "tinta": "FFEAE0",
      "papel": "FFF1EA",
      "painel_baixo": "FFECE4",
      "bloco": "ED2A00",
      "menu_grande": "FFCCB6",
      "regua": "CC3F00",
      "osso_por_papel": {
        "fundo": "1B0033",
        "painel": "1B0033",
        "painel_alto": "1B0033",
        "linha": "1B0033",
        "texto": "FFEAE0",
        "texto_fraco": "FFEAE0",
        "acento": "FFEAE0",
        "tinta": "1B0033",
        "papel": "1B0033",
        "painel_baixo": "1B0033",
        "bloco": "1B0033",
        "menu_grande": "1B0033",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "500073",
        "painel": "500073",
        "painel_alto": "500073",
        "painel_baixo": "500073",
        "papel": "500073",
        "menu_grande": "500073",
        "tinta": "500073",
        "acento": "D36EFF"
      }
    },
    "escuro": {
      "fundo": "19002E",
      "painel": "2C0052",
      "painel_alto": "42007A",
      "linha": "7A1600",
      "texto": "FFEAE0",
      "texto_fraco": "FFBEB0",
      "acento": "AC00F7",
      "tinta": "10001F",
      "papel": "21003E",
      "painel_baixo": "2B0050",
      "bloco": "FF3F16",
      "menu_grande": "3C006E",
      "regua": "A133FF",
      "osso_por_papel": {
        "fundo": "FFEAE0",
        "painel": "FFEAE0",
        "painel_alto": "FFEAE0",
        "linha": "FFEAE0",
        "texto": "1B0033",
        "texto_fraco": "1B0033",
        "acento": "FFFFFF",
        "tinta": "FFEAE0",
        "papel": "FFEAE0",
        "painel_baixo": "FFEAE0",
        "bloco": "1B0033",
        "menu_grande": "FFEAE0",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "BE28FF",
        "painel": "C643FF",
        "painel_alto": "D066FF",
        "painel_baixo": "C643FF",
        "papel": "C031FF",
        "menu_grande": "CC58FF",
        "tinta": "BA1BFF",
        "acento": "FAEDFF"
      }
    }
  },
  "Dez Sombras": {
    "claro": {
      "fundo": "FEF5F0",
      "painel": "FDE1D3",
      "painel_alto": "FBC9B2",
      "linha": "D1C5E7",
      "texto": "171122",
      "texto_fraco": "181027",
      "acento": "412B6B",
      "tinta": "FDEBE2",
      "papel": "FEF1EB",
      "painel_baixo": "FEEDE6",
      "bloco": "6846A7",
      "menu_grande": "FFCDB6",
      "regua": "CC4100",
      "osso_por_papel": {
        "fundo": "171122",
        "painel": "171122",
        "painel_alto": "171122",
        "linha": "171122",
        "texto": "FDEBE2",
        "texto_fraco": "FDEBE2",
        "acento": "FDEBE2",
        "tinta": "171122",
        "papel": "171122",
        "painel_baixo": "171122",
        "bloco": "FDEBE2",
        "menu_grande": "171122",
        "regua": "FFFFFF"
      },
      "aviso_por_papel": {
        "fundo": "412B6B",
        "painel": "412B6B",
        "painel_alto": "412B6B",
        "painel_baixo": "412B6B",
        "papel": "412B6B",
        "menu_grande": "412B6B",
        "tinta": "412B6B",
        "acento": "AD98D6"
      }
    },
    "escuro": {
      "fundo": "140F1F",
      "painel": "241A37",
      "painel_alto": "372853",
      "linha": "362456",
      "texto": "FDEBE2",
      "texto_fraco": "D3C8E8",
      "acento": "8161BF",
      "tinta": "0D0817",
      "papel": "1C142A",
      "painel_baixo": "241A36",
      "bloco": "7C5BBA",
      "menu_grande": "2F1D51",
      "regua": "8B6AC8",
      "osso_por_papel": {
        "fundo": "FDEBE2",
        "painel": "FDEBE2",
        "painel_alto": "FDEBE2",
        "linha": "FDEBE2",
        "texto": "171122",
        "texto_fraco": "171122",
        "acento": "FFFFFF",
        "tinta": "FDEBE2",
        "papel": "FDEBE2",
        "painel_baixo": "FDEBE2",
        "bloco": "FFFFFF",
        "menu_grande": "FDEBE2",
        "regua": "000000"
      },
      "aviso_por_papel": {
        "fundo": "8B6EC4",
        "painel": "9479C9",
        "painel_alto": "A38BD0",
        "painel_baixo": "9479C9",
        "papel": "9073C6",
        "menu_grande": "9A81CC",
        "tinta": "8769C2",
        "acento": "F9F8FC"
      }
    }
  }
};

var PALETA_DE_FABRICA_ = {
  fundo: '120F1D', painel: '1E1733', painel_alto: '3D2E78', linha: '493F54',
  texto: 'F4F1F7', texto_fraco: '998BA9', tinta: '0A0810', papel: '17131F',
  painel_baixo: '1B142F', bloco: '756588', acento: '211940',
  menu_grande: '3B3360', regua: '8A7EC4',
};

var NOME_CEL_PALETA_ = 'PALETA_ESCOLHIDA';
// O rótulo tem intervalo nomeado próprio desde que rótulo e valor passaram a ter larguras
// diferentes (18/09/2026) — sem isso, repintarBordas_ não tinha como reconstruir a largura do
// rótulo a partir da do valor, porque não são mais a mesma.
var NOME_CEL_PALETA_ROTULO_ = 'PALETA_ROTULO';
// A caixinha de aviso embaixo do valor, com o mesmo problema do rótulo: a borda dela só se repinta se
// o repintarBordas_ souber onde ela mora.
var NOME_CEL_PALETA_AVISO_ = 'PALETA_AVISO';
var TEXTO_AVISO_PALETA_ = 'Aguarde de 30 a 40 segundos para ver o tema inteiro — depende do tema.';

/**
 * O valor que a caixa nasce mostrando, antes de qualquer escolha.
 *
 * NÃO é "Noite · Escuro": o `Noite` do catálogo (a paleta "roxa atual") saiu
 * do `derivar.py`, que ajusta cada tema pro contraste WCAG — e por isso os
 * treze tons do `Noite · Escuro` do catálogo já não são mais, em nenhum dos
 * treze, os mesmos hex que `PALETA_DE_FABRICA_` guarda (o que a ficha usa de
 * verdade desde que nasce, em `montarAba_`). Achado testando no Sheets em
 * 18/09/2026: a cor nunca trocava porque o "antes" de todo primeiro repaint
 * vinha de `PALETAS['Noite']['escuro']` — um tema válido, então a busca por
 * hex batia contra cores que a ficha nunca teve, e `troca` saía vazio pra
 * TODA a ficha, não só pra caixa nova.
 *
 * Esta string não existe no catálogo (não tem ' · ' nem bate com nome de
 * tema), então `coresDoNome_` sempre devolve null pra ela, e o "antes" cai
 * no `|| PALETA_DE_FABRICA_` de `repintarPaleta_` — o mesmo fallback que já
 * existia, só que agora alguém aciona ele.
 */
var PALETA_INICIAL_ = 'Escolha uma paleta';

/**
 * Acha a caixa da maior imagem da aba, pra ancorar a paleta embaixo dela.
 *
 * Bug do dia 1 (achado testando no Sheets em 18/09/2026): Sheet.getImages()
 * só devolve imagem SOLTA sobre a grade (OverGridImage) — e a ficha nunca
 * solta imagem, decisão do Mizuki de 15/09/2026 registrada bem aqui em cima,
 * em montarAba_ (Ficha.gs): toda foto entra DENTRO da célula, com
 * newCellImage(). Pra essa ficha, cart.getImages() sempre volta vazio, então
 * configurarPaleta_ caía direto no "sem foto pra ancorar" e a caixa nunca
 * nascia — nem no construir(), nem no onOpen. Os 16 validadores passavam
 * porque nenhum deles roda a função de verdade contra um Sheets, só leem o
 * texto do arquivo.
 *
 * A troca: varrer os VALORES da área usada (getValues(), uma leitura só) até
 * achar um que seja imagem (a CellImage tem a propriedade valueType, sempre
 * igual a ValueType.IMAGE — é propriedade, não método; o verificar(), no
 * modelo.gs.js, já lia certo), e usar a mesclagem de quem achar. Mede pela
 * altura em linha da mesclagem, não em pixel — não tem pixel pra medir sem
 * OverGridImage mesmo.
 */
function acharCaixaDaFoto_(sh) {
  var nl = sh.getLastRow(), nc = sh.getLastColumn();
  if (nl < 1 || nc < 1) return null;
  var vals = sh.getRange(1, 1, nl, nc).getValues();
  var melhor = null, melhorAltura = 0;
  for (var r = 0; r < nl; r++) {
    for (var c = 0; c < nc; c++) {
      var v = vals[r][c];
      if (!v || v.valueType !== SpreadsheetApp.ValueType.IMAGE) continue;
      var celula = sh.getRange(r + 1, c + 1);
      var mesclas = celula.getMergedRanges();
      var caixa = mesclas.length ? mesclas[0] : celula;
      if (caixa.getNumRows() > melhorAltura) { melhorAltura = caixa.getNumRows(); melhor = caixa; }
    }
  }
  return melhor;
}

/**
 * Confere se a caixa da paleta já existe DE VERDADE — não só se o nome
 * consta na lista de intervalos nomeados, mas se ele ainda aponta pra uma
 * célula de uma aba viva.
 *
 * O Google não documenta se um intervalo nomeado preso a uma aba apagada
 * morre junto ou fica órfão apontando pra ela. Se ficar órfão, getRangeByName
 * ainda acha o NOME, mas ler algo dele (a aba que ele mora) explode.
 */
/**
 * Remove os intervalos nomeados da paleta que EXISTEM, e só eles.
 *
 * Bug achado testando no Sheets em 19/09/2026: `ss.removeNamedRange(nome)` num nome que não existe não
 * estoura na hora — o Spreadsheet Service enfileira a operação e o erro ("O intervalo "PALETA_AVISO" não
 * existe.") aparece na PRÓXIMA leitura, várias linhas depois, fora do try/catch que embrulhava a chamada.
 * O `PALETA_AVISO` era novo, então na primeira rodada do construir() depois dele nascer não existia, e o
 * construir() inteiro caía dentro do acharCaixaDaFoto_. Os dois nomes antigos só passavam porque já existiam
 * de uma rodada anterior — numa planilha nova, sem nenhum dos três, os três iam falhar. Listar os que
 * existem e remover cada um pelo próprio objeto não tem esse caminho.
 */
function removerNomesDaPaleta_(ss) {
  var meus = [NOME_CEL_PALETA_, NOME_CEL_PALETA_ROTULO_, NOME_CEL_PALETA_AVISO_];
  ss.getNamedRanges().forEach(function (nr) {
    if (meus.indexOf(nr.getName()) >= 0) nr.remove();
  });
}

function paletaJaMontada_(ss) {
  var alvo = ss.getRangeByName(NOME_CEL_PALETA_);
  if (!alvo) return false;
  try {
    alvo.getSheet().getName();
    return true;
  } catch (err) {
    removerNomesDaPaleta_(ss);
    return false;
  }
}

/**
 * Instala um gatilho INSTALÁVEL de onEdit pra aplicarPaleta_ — sem ele, a troca de tema roda
 * dentro do onEdit simples, que tem 30 segundos de orçamento. Achado testando no Sheets em
 * 18/09/2026: repintar a ficha inteira (~29 mil células em 7 abas: fundo, fonte, borda) não cabe
 * nisso, e o Apps Script mata a execução no meio sem avisar — a primeira troca, mais rápida às
 * vezes coube; a partir da segunda, quase nunca. Como a paleta_atual só é gravada no FIM de
 * repintarPaleta_, uma execução morta no meio nunca chega lá: a próxima troca compara contra um
 * "antes" que não é o que está pintado de verdade, e a ficha parece "travada" numa paleta antiga
 * pra sempre — o sintoma exato que o Mizuki descreveu.
 *
 * Gatilho instalável tem 6 minutos de orçamento, não 30 segundos — o mesmo de uma função rodada
 * na mão. Continua sendo a mesma aplicarPaleta_(e) de sempre, só que citada aqui, não dentro do
 * onEdit(e). Idempotente: confere se já existe antes de criar outro.
 *
 * ⚠ Pede autorização nova na próxima vez que rodar alguma função na mão (o construir(), por
 * exemplo) — criar gatilho é um escopo que o script não usava até agora.
 */
function instalarGatilhoPaleta_(ss) {
  // Em try/catch pra não travar o resto de configurarPaleta_ (nem o construir() inteiro, que não
  // embrulha essa chamada) se a criação do gatilho falhar por algum motivo — a caixa da paleta e
  // o resto da ficha continuam valendo sem ele; só a troca de tema fica sem o orçamento maior.
  try {
    var jaTem = ScriptApp.getProjectTriggers().some(function (t) {
      return t.getHandlerFunction() === 'aplicarPaleta_' && t.getEventType() === ScriptApp.EventType.ON_EDIT;
    });
    if (!jaTem) ScriptApp.newTrigger('aplicarPaleta_').forSpreadsheet(ss).onEdit().create();
  } catch (err) { /* silencioso — ver comentário acima */ }
}

/**
 * Cria a caixa da paleta na CARTEIRA, embaixo da foto.
 *
 * Bug achado testando no Sheets em 18/09/2026: o intervalo nomeado
 * SOBREVIVE ao construir() apagar e recriar a CARTEIRA — o nome da aba é o
 * mesmo ("CARTEIRA"), e o Google parece religar o intervalo nomeado à aba
 * nova pelo nome, não por um id interno. Isso quer dizer que "já existia"
 * (paletaJaMontada_) continuava batendo depois de uma rodada de construir()
 * inteira, com uma versão MAIS NOVA do Codigo.gs — a caixa antiga (posição,
 * largura, borda) sobrevivia por baixo da ficha nova inteira, porque
 * configurarPaleta_ nunca era chamada de novo pra valer. Foi assim que a
 * borda da caixa ficou presa na régua velha mesmo com o resto da ficha
 * repintado: repintarBordas_ procurava o intervalo NOME_CEL_PALETA_ROTULO_
 * (criado só numa versão mais nova desta função), não achava, e pulava as
 * duas bordas da caixa inteira.
 *
 * O `force` existe por causa disso: o construir() (Ficha.gs) sempre chama
 * com `force=true`, porque ele MESMO já decidiu apagar tudo — a caixa da
 * paleta não é exceção. O onOpen chama sem `force`, porque aí sim precisa
 * ser idempotente: reabrir a ficha não pode apagar uma paleta que o jogador
 * já escolheu.
 */
function configurarPaleta_(ss, force) {
  instalarGatilhoPaleta_(ss);
  if (force) {
    removerNomesDaPaleta_(ss);
  } else if (paletaJaMontada_(ss)) {
    return 'já existia';
  }
  var cart = ss.getSheetByName('CARTEIRA');
  if (!cart) return 'sem CARTEIRA';
  var caixaFoto = acharCaixaDaFoto_(cart);
  if (!caixaFoto) return 'sem foto pra ancorar';
  // Posição pedida pelo Mizuki em 18/09/2026, contra o Kaori.xlsx: cinco linhas abaixo da foto
  // pro rótulo (não duas — sobrava pouco ar), o valor com o dobro da altura (duas linhas, não
  // uma). E as duas larguras são DIFERENTES, não a mesma — achado numa correção depois da
  // primeira tentativa: o rótulo fica dois mais estreito que a foto (até a coluna I), e o valor
  // fica dois mais LARGO que a foto (até a M) — a caixa evasa pra baixo, não um retângulo só.
  var linhaBase = caixaFoto.getLastRow();
  var col = caixaFoto.getColumn();
  var largRotulo = caixaFoto.getNumColumns() - 2;
  var largValor = caixaFoto.getNumColumns() + 2;

  var rotulo = cart.getRange(linhaBase + 5, col, 1, largRotulo);
  var valor = cart.getRange(linhaBase + 6, col, 2, largValor);
  // 19/09/2026, pedido do Mizuki: "galera é impaciente". A troca repinta a ficha inteira, célula a
  // célula, e leva de 30 a 40 segundos conforme o tema — uma linha logo embaixo do menu, do mesmo
  // tamanho dele, avisa que é pra esperar.
  var aviso = cart.getRange(linhaBase + 8, col, 1, largValor);

  // O mesmo par rótulo/valor de toda caixa de campo da ficha (CAMINHO, NÍVEL, ...): Oswald
  // pequeno e sem negrito no rótulo, Castoro grande no valor, moldura média na cor da régua
  // fechando os dois como uma peça só — copiado célula a célula de O17:O18 (CAMINHO) no
  // Kaori.xlsx que o Mizuki testou, porque a caixa da paleta tinha nascido sem nenhuma borda e
  // com a fonte errada (Roboto em vez de Castoro) no valor.
  var BORDA_CAIXA = SpreadsheetApp.BorderStyle.SOLID_MEDIUM;

  rotulo.merge()
    .setValue('PALETA')
    .setFontFamily('Oswald').setFontSize(8).setFontWeight('normal')
    .setFontColor('#' + PALETA_DE_FABRICA_.texto_fraco)
    .setHorizontalAlignment('center').setVerticalAlignment('middle')
    .setBackground('#' + PALETA_DE_FABRICA_.painel_alto)
    .setBorder(true, true, true, true, false, false, '#' + PALETA_DE_FABRICA_.regua, BORDA_CAIXA);

  var opcoes = [];
  Object.keys(PALETAS).forEach(function (nome) {
    opcoes.push(nome + ' · Claro', nome + ' · Escuro');
  });
  // Igual ao menu do Caminho e da Trilha (menusSuspensos_, modelo.gs.js): allowInvalid true,
  // porque o valor inicial (PALETA_INICIAL_) não é uma opção de verdade da lista, só um convite.
  var regra = SpreadsheetApp.newDataValidation()
    .requireValueInList(opcoes, true).setAllowInvalid(true).build();

  valor.merge()
    .setValue(PALETA_INICIAL_)
    .setDataValidation(regra)
    .setFontFamily('Castoro').setFontSize(15)
    .setFontColor('#' + PALETA_DE_FABRICA_.texto)
    .setHorizontalAlignment('center').setVerticalAlignment('middle')
    .setBackground('#' + PALETA_DE_FABRICA_.painel)
    .setBorder(true, true, true, true, false, false, '#' + PALETA_DE_FABRICA_.regua, BORDA_CAIXA);

  aviso.merge()
    .setValue(TEXTO_AVISO_PALETA_)
    .setFontFamily('Oswald').setFontSize(7).setFontWeight('normal').setFontStyle('normal')
    .setFontColor('#' + PALETA_DE_FABRICA_.texto_fraco)
    .setHorizontalAlignment('center').setVerticalAlignment('middle')
    .setBackground('#' + PALETA_DE_FABRICA_.painel)
    .setBorder(true, true, true, true, false, false, '#' + PALETA_DE_FABRICA_.regua, BORDA_CAIXA);

  ss.setNamedRange(NOME_CEL_PALETA_, valor);
  ss.setNamedRange(NOME_CEL_PALETA_ROTULO_, rotulo);
  ss.setNamedRange(NOME_CEL_PALETA_AVISO_, aviso);
  PropertiesService.getDocumentProperties().setProperty('paleta_atual', PALETA_INICIAL_);
  return 'criada em CARTEIRA!' + valor.getA1Notation();
}

/**
 * Roda no onOpen: garante que a caixa da paleta existe mesmo numa planilha
 * que já foi montada antes desta rodada, sem precisar rodar o construir()
 * de novo. Não faz mais nada além disso — silencioso se já existir.
 */
function onOpen(e) {
  try { configurarPaleta_(SpreadsheetApp.getActive()); } catch (err) { /* silencioso: não trava a abertura */ }
}

/**
 * Chega aqui pelo onEdit, quando a célula editada é a da paleta. Lê o nome
 * escolhido ("Tema · Claro" ou "Tema · Escuro"), e manda repintar — contra a
 * paleta que estava valendo antes, guardada numa propriedade do documento
 * (não numa célula, pra não competir com o índice da DADOS, que é do
 * Python).
 *
 * Bug achado testando no Sheets em 18/09/2026: a cor nunca trocava, porque
 * a caixa da paleta é mesclada (C24:K24) e num edit numa célula mesclada o
 * Apps Script devolve em e.range só a célula-âncora ("C24"), nunca o
 * intervalo inteiro — o antigo `e.range.getA1Notation() !== alvo.getA1Notation()`
 * comparava "C24" contra "C24:K24", que nunca bate, então a função sempre
 * voltava sem fazer nada. Os outros onEdit da ficha (trilhaDoCaminho_ e
 * companhia) não caem nessa porque comparam contra o endereço de uma célula
 * só, vindo do índice; aqui o alvo é o range mesclado inteiro, então o
 * conserto é comparar contra a célula-âncora dele.
 *
 * Segundo bug achado testando no Sheets em 18/09/2026, o "trava depois de
 * algumas trocas" que o Mizuki descreveu: nada aqui impedia DUAS execuções
 * deste gatilho de rodar ao mesmo tempo — o gatilho instalável não serializa
 * edições diferentes sozinho, e trocar de tema rápido demais (escolher um
 * tema enquanto o repaint do anterior ainda está no meio, ~7 abas por
 * getBackgrounds()/setBackgrounds()) dispara a segunda execução ANTES da
 * primeira terminar de escrever. As duas leem 'paleta_atual' e o
 * getBackgrounds() da própria aba ao mesmo tempo; a que escreve por último
 * decide o valor de 'paleta_atual', mas a ficha na tela pode ficar com uma
 * mistura de cor da execução 1 e da execução 2 — nem o tema antigo nem o
 * novo. `repintarPaleta_` só sabe repintar comparando o hex ATUAL da célula
 * contra o hex ESPERADO de cada um dos treze papéis da paleta anterior
 * (`papelPorHexAntes`); uma célula com hex misturado não bate com papel
 * nenhum, e fica presa nessa cor pra sempre — nenhuma troca futura encontra
 * ela de novo, porque a busca é sempre "qual papel tinha exatamente este
 * hex", não "que cor está mais perto". A borda (`repintarBordas_`) não sofre
 * disso porque ela compara contra um alvo FIXO (a régua de fábrica), não
 * contra o "antes" da troca — só fundo e fonte dependem do histórico, e só
 * eles travam.
 *
 * O conserto é LockService: serializa as execuções do MESMO documento, sem
 * afetar a ficha de outro jogador (cada cópia da planilha tem seu próprio
 * lock). A segunda troca agora ESPERA a primeira terminar de vez (ler,
 * repintar, escrever) antes de começar a ler 'paleta_atual' — se não
 * esperasse isso, ela podia ler um 'paleta_atual' que a primeira ainda não
 * tinha escrito, e a mistura continuaria possível mesmo com o lock. Se a
 * espera estourar (fila grande demais), a troca é abandonada em silêncio —
 * melhor que travar uma célula pro resto da vida da ficha.
 */
function aplicarPaleta_(e) {
  var alvo = SpreadsheetApp.getActive().getRangeByName(NOME_CEL_PALETA_);
  if (!alvo || e.range.getA1Notation() !== alvo.getCell(1, 1).getA1Notation()) return;
  var novo = String(e.value || '').trim();
  if (!novo || !PALETAS[novo.split(' · ')[0]]) return;

  var lock = LockService.getDocumentLock();
  try {
    if (!lock.tryLock(300000)) return; // 5 min de espera; sobra 1 min do orçamento de 6 do gatilho
    var props = PropertiesService.getDocumentProperties();
    var antigo = props.getProperty('paleta_atual') || PALETA_INICIAL_;
    if (novo === antigo) return;
    repintarPaleta_(SpreadsheetApp.getActive(), antigo, novo);
    props.setProperty('paleta_atual', novo);
  } finally {
    lock.releaseLock();
  }
}

function coresDoNome_(nome) {
  var p = nome.split(' · ');
  var tema = PALETAS[p[0]];
  if (!tema) return null;
  return tema[p[1] === 'Claro' ? 'claro' : 'escuro'];
}

/** A cor "vida cheia" da decisão A5 — nunca é um papel de tema, ver OSSO_POR_PAPEL_ abaixo. */
var OSSO_HEX_ = '#E8DCD4';

/**
 * O âmbar de texto PADRÃO (o "sobrou ponto" da INVOCAÇÃO, o "MORRE DE VEZ", ...) — não confundir com o
 * âmbar de ESTADO da vida/energia/integridade, que é regra condicional (corDeEstado_) e fica fixo pela
 * decisão A5. Este é a fonte de célula de verdade, e seguia amarelo em toda paleta: pedido do Mizuki em
 * 19/09/2026, testando no Sheets. Ver `aviso_por_papel` dentro de cada entrada do PALETAS, e o
 * `resolve_aviso_por_papel` no derivar.py.
 */
var AMBAR_HEX_ = '#D89B3A';

/**
 * As células que nasceram com o âmbar padrão, achadas no `ABAS` (o estilo delas) e não pela cor que
 * têm agora — depois da primeira troca a fonte delas já não é mais âmbar, e uma busca por cor não
 * acharia elas de novo. Achar pelo endereço faz a troca reversível: em toda paleta a fonte delas é
 * recalculada do zero, sem depender do que estava ali antes.
 */
function celulasDeAviso_(spec) {
  var mapa = {};
  (spec.vals || []).forEach(function (t) {
    var estilo = t.length > 3 ? spec.estilos[t[3]] : null;
    if (estilo && String(estilo[2] || '').toUpperCase() === AMBAR_HEX_) mapa[(t[0] - 1) + ',' + (t[1] - 1)] = true;
  });
  return mapa;
}

// ---------------------------------------------------------------------------------------------
// LEGIBILIDADE — 19/09/2026, o "problema grande" que o Mizuki apontou testando no Sheets.
//
// Trocar a fonte e o fundo cada um pelo SEU papel não garante que o par novo se leia: numa paleta
// clara o `texto` e o `texto_fraco` viram escuros, e uma célula cujo fundo é escuro em toda paleta
// (a `tinta`) ou é o `acento` escuro de um tema claro ficava com fonte escura em cima de fundo
// escuro — "9 de 23 na criação — ou 10, trocando os dois ofícios da Origem" impossível de ler. O
// derivar.py mede contraste de texto contra fundo e painel; o resto dos pares nunca foi medido.
//
// Esta é a rede de segurança que roda DEPOIS da troca de papéis, célula a célula: se o par
// fonte/fundo novo lê pior que o par de FÁBRICA da mesma célula (medido no ABAS, então sem histórico
// nenhum pra contaminar), a fonte é trocada por uma cor DA PALETA que leia — sem se obrigar ao preto
// e ao branco, que só entram por último. O critério é "pior que o desenho", e não "abaixo de 4,5":
// a lombada, o selo e os rótulos fracos nasceram de propósito com contraste baixo, e não devem
// virar texto gritante só porque ficaram abaixo de um piso que nunca foi deles.
// ---------------------------------------------------------------------------------------------
var PISO_LEGIVEL_ = 4.5;
// O texto que nasceu discreto de propósito (a lombada girada, o "caminho" embaixo do selo: contraste 2,0
// na ficha de fábrica) também tem de se ler — o Mizuki apontou que ele "se perde no fundo". Nunca cai
// abaixo disto, mesmo que o desenho tivesse menos.
var PISO_DISCRETO_ = 3.0;
var LUM_CACHE_ = {};

function luminanciaHex_(hex) {
  var h = String(hex || '').toUpperCase();
  if (LUM_CACHE_[h] !== undefined) return LUM_CACHE_[h];
  var m = /^#?([0-9A-F]{6})$/.exec(h);
  var lum = 0;
  if (m) {
    var v = m[1], k = [0.2126, 0.7152, 0.0722];
    for (var i = 0; i < 3; i++) {
      var c = parseInt(v.substr(i * 2, 2), 16) / 255;
      lum += k[i] * (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
    }
  }
  LUM_CACHE_[h] = lum;
  return lum;
}

function contrasteHex_(a, b) {
  var la = luminanciaHex_(a), lb = luminanciaHex_(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

/** O contraste que cada célula tinha na ficha de FÁBRICA, lido do ABAS — o mesmo que o montarAba_ pintou. */
function contrasteDeFabrica_(spec) {
  var nl = spec.rows, nc = spec.cols;
  var bg0 = String(spec.fundo_base === undefined ? '#120F1D' : spec.fundo_base).toUpperCase();
  var fc0 = String((spec.padrao || ['Roboto', 11, '#F4F1F7'])[2]).toUpperCase();
  var bg = [], fc = [], r, c;
  for (r = 0; r < nl; r++) {
    bg.push(new Array(nc).fill(bg0));
    fc.push(new Array(nc).fill(fc0));
  }
  (spec.fundos || []).forEach(function (f) {
    for (var cc = f[1]; cc <= f[2]; cc++) bg[f[0] - 1][cc - 1] = String(f[3]).toUpperCase();
  });
  (spec.vals || []).forEach(function (t) {
    var e = t.length > 3 ? spec.estilos[t[3]] : null;
    if (e && e[2]) fc[t[0] - 1][t[1] - 1] = String(e[2]).toUpperCase();
  });
  var out = [];
  for (r = 0; r < nl; r++) {
    var linha = new Array(nc);
    for (c = 0; c < nc; c++) linha[c] = contrasteHex_(fc[r][c], bg[r][c]);
    out.push(linha);
  }
  return out;
}

/**
 * Devolve `fonte` se ela ainda lê sobre `fundo` tão bem quanto o desenho pedia (com folga de 10%);
 * senão, a cor da lista que lê no MÍNIMO o que o desenho pedia (nunca mais que 4,5) e que mais se
 * aproxima do contraste que o desenho tinha — a lombada fica discreta, o texto corrido fica firme.
 * As duas últimas da lista (branco e preto) levam uma penalidade: só ganham se a paleta não der.
 */
function fonteLegivel_(fonte, fundo, desenho, cands, cache) {
  var alvo = Math.min(PISO_LEGIVEL_, Math.max(desenho, PISO_DISCRETO_));
  var chave = fonte + '|' + fundo + '|' + Math.round(desenho * 4);
  if (cache[chave] !== undefined) return cache[chave];
  var resultado = fonte;
  if (contrasteHex_(fonte, fundo) < alvo * 0.9) {
    var desejado = Math.max(alvo, Math.min(desenho, 8));
    var melhor = null, melhorNota = Infinity, maior = fonte, maiorC = contrasteHex_(fonte, fundo);
    cands.forEach(function (cd) {
      var cc = contrasteHex_(cd.hex, fundo);
      if (cc > maiorC) { maior = cd.hex; maiorC = cc; }
      if (cc < alvo) return;
      var nota = Math.abs(Math.log(cc) - Math.log(desejado)) + (cd.extremo ? 0.5 : 0);
      if (nota < melhorNota) { melhor = cd.hex; melhorNota = nota; }
    });
    resultado = melhor || maior;
  }
  cache[chave] = resultado;
  return resultado;
}

/** As cores que a rede de segurança pode oferecer: a paleta nova, a variante oposta do mesmo tema, e por último branco e preto. */
function candidatosDeFonte_(agora, oposta) {
  var lista = [];
  [agora, oposta].forEach(function (p) {
    if (!p) return;
    ['texto', 'texto_fraco', 'linha', 'bloco', 'acento', 'papel', 'fundo', 'painel', 'tinta'].forEach(function (k) {
      if (p[k]) lista.push({ hex: '#' + String(p[k]).toUpperCase(), extremo: false });
    });
  });
  lista.push({ hex: '#FFFFFF', extremo: true }, { hex: '#000000', extremo: true });
  return lista;
}

function coresOpostas_(nome) {
  var p = String(nome).split(' · ');
  var tema = PALETAS[p[0]];
  return tema ? tema[p[1] === 'Claro' ? 'escuro' : 'claro'] : null;
}

/**
 * O papel de um hex em QUALQUER uma das 61 paletas (as 122 entradas, claro e
 * escuro) mais a de fábrica — não só a paleta ANTERIOR. Existe pra CURAR uma
 * célula que ficou presa numa cor de mais de uma troca atrás.
 *
 * Achado testando no Sheets em 19/09/2026, depois do LockService: mesmo
 * serializado, `repintarPaleta_` só reconhecia uma célula comparando contra
 * os doze papéis da paleta IMEDIATAMENTE anterior (`papelPorHexAntes`) — uma
 * célula que, por qualquer motivo (uma corrida de ANTES deste conserto, uma
 * cor colada na mão, um F5 no meio do caminho), ficasse com o hex de uma
 * paleta de duas ou mais trocas atrás nunca mais era achada, porque a busca
 * só olhava um passo pra trás. O Mizuki descreveu isso como "nem tudo está
 * mudando", com só duas das sete abas acompanhando direito.
 *
 * Esta função é a segunda tentativa, não a primeira: `repintarPaleta_`
 * sempre confere contra a paleta anterior PRIMEIRO — isso decide sozinho,
 * sem ambiguidade, no caminho normal (sem corrupção nenhuma) — e só cai
 * aqui quando aquilo não acha nada. Nove hex, dos 1296 distintos que as 61
 * paletas usam, repetem entre PAPÉIS diferentes (ex.: "453636" é
 * painel_alto em cinco temas escuros e linha no Sálvia escuro); pra esses, o
 * primeiro tema a registrar o hex decide o papel aqui embaixo — uma escolha
 * arbitrária, mas que só entra em jogo pra uma célula que já estava presa, e
 * mesmo errando o papel por um desses nove ela sai da cor errada pra uma
 * cor VÁLIDA de algum papel, nunca mais fica parada pra sempre.
 */
function papelPorHexGlobal_() {
  var papeis = ['fundo', 'painel', 'painel_alto', 'linha', 'texto', 'texto_fraco',
                'tinta', 'papel', 'painel_baixo', 'bloco', 'acento', 'menu_grande'];
  var mapa = {};
  function registra(tema) {
    papeis.forEach(function (papel) {
      var hex = '#' + String(tema[papel] || '').toUpperCase();
      if (!mapa[hex]) mapa[hex] = papel;
    });
  }
  registra(PALETA_DE_FABRICA_);
  Object.keys(PALETAS).forEach(function (nome) {
    registra(PALETAS[nome].claro);
    registra(PALETAS[nome].escuro);
  });
  return mapa;
}

// ---------------------------------------------------------------------------------------------
// A ARTE — 19/09/2026, pedido do Mizuki testando no Sheets: "as imagens dos símbolos, das gotinhas,
// das linhas, da foto têm cores fixas, e vai rolar o que rolou no Eucalipto" (o selo vermelho e a
// pincelada roxa numa ficha toda verde).
//
// Imagem não troca de cor sozinha. Mas toda a arte da ficha é de UMA cor — o que varia é o alfa (a
// textura do pincel, o desgaste do selo) — e o emissor a escreve como PNG de PALETA: 256 entradas
// iguais, e o índice do pixel é o próprio alfa. Recolorir é reescrever os 768 bytes da paleta e refazer
// o CRC do bloco, sem tocar em pixel nenhum: milissegundos, e nenhuma imagem extra guardada por tema.
//
// A troca só mexe na imagem que tem o título de alt "PM-ARTE:" — a que o construir() pôs. A foto que o
// jogador coloca no lugar da moldura não tem esse título, e não é tocada.
// ---------------------------------------------------------------------------------------------
var TAG_ARTE_ = 'PM-ARTE:';
var PISO_ARTE_ = 3.0;
// o papel da paleta que cada imagem segue. As duas pinceladas e a moldura da foto são discretas (bloco), a
// pincelada clara do meio é o traço que separa (texto fraco), e o selo e as gotinhas são o acento vivo
// do tema (régua, a cor mais saturada que ele tem).
var PAPEL_DA_ARTE_ = {
  'carteira-1': 'bloco', 'carteira-2': 'bloco', 'carteira-3': 'acento', 'carteira-4': 'regua',
  'ficha-1': 'bloco', 'ficha-2': 'regua'
};
var CRC_TABELA_ = null;

function crc32_(bytes, ini, fim) {
  if (!CRC_TABELA_) {
    CRC_TABELA_ = [];
    for (var n = 0; n < 256; n++) {
      var c = n;
      for (var k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      CRC_TABELA_.push(c >>> 0);
    }
  }
  var crc = 0xFFFFFFFF;
  for (var i = ini; i < fim; i++) crc = CRC_TABELA_[(crc ^ bytes[i]) & 255] ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

function byteAssinado_(v) { return v > 127 ? v - 256 : v; }

/** O mesmo PNG de paleta com a cor `hex` ("#RRGGBB") em todas as entradas. Devolve base64. */
function pngComCor_(b64, hex) {
  var bytes = Utilities.base64Decode(b64);
  var rgb = [parseInt(hex.substr(1, 2), 16), parseInt(hex.substr(3, 2), 16), parseInt(hex.substr(5, 2), 16)];
  var pos = 8;                                   // depois da assinatura de 8 bytes
  while (pos + 12 <= bytes.length) {
    var len = ((bytes[pos] & 255) * 16777216) + ((bytes[pos + 1] & 255) << 16) + ((bytes[pos + 2] & 255) << 8) + (bytes[pos + 3] & 255);
    var tipo = String.fromCharCode(bytes[pos + 4] & 255, bytes[pos + 5] & 255, bytes[pos + 6] & 255, bytes[pos + 7] & 255);
    if (tipo === 'PLTE') {
      for (var i = 0; i < len; i++) bytes[pos + 8 + i] = byteAssinado_(rgb[i % 3]);
      var crc = crc32_(bytes, pos + 4, pos + 8 + len);     // o CRC cobre o tipo e os dados
      bytes[pos + 8 + len] = byteAssinado_((crc >>> 24) & 255);
      bytes[pos + 9 + len] = byteAssinado_((crc >>> 16) & 255);
      bytes[pos + 10 + len] = byteAssinado_((crc >>> 8) & 255);
      bytes[pos + 11 + len] = byteAssinado_(crc & 255);
      return Utilities.base64Encode(bytes);
    }
    pos += 12 + len;
  }
  throw new Error('PNG sem bloco de paleta: a arte não foi escrita como PNG de uma cor');
}

/**
 * Recolore cada imagem NOSSA na cor do papel dela na paleta nova, escolhida pra ler contra o fundo que a
 * célula dela tem agora (o mesmo `fonteLegivel_` das fontes, com piso de 3,0). Roda depois de o fundo ter
 * sido trocado, porque é dele que a cor depende. Uma imagem que falha não derruba a troca inteira.
 */
function repintarArte_(ss, agora, candidatos) {
  var cache = {}, feitas = 0;
  ABAS.forEach(function (spec) {
    var sh = ss.getSheetByName(spec.nome);
    if (!sh) return;
    (spec.imgs || []).forEach(function (im) {
      var papel = PAPEL_DA_ARTE_[String(im[4]).replace(/-\d+x\d+\.png$/, '')];
      if (!papel || !ARTE[im[4]] || agora[papel] === undefined) return;
      try {
        var cel = sh.getRange(im[0], im[1]);
        var v = cel.getValue();
        if (!v || v.valueType !== SpreadsheetApp.ValueType.IMAGE) return;
        if (String(v.getAltTextTitle()) !== TAG_ARTE_ + im[4]) return;      // a foto do jogador, por exemplo
        var fundo = String(cel.getBackground()).toUpperCase();
        var cor = fonteLegivel_('#' + String(agora[papel]).toUpperCase(), fundo, PISO_ARTE_, candidatos, cache);
        if (String(v.getAltTextDescription()) === cor) return;              // já está dessa cor
        cel.setValue(SpreadsheetApp.newCellImage()
          .setSourceUrl('data:image/png;base64,' + pngComCor_(ARTE[im[4]], cor))
          .setAltTextTitle(TAG_ARTE_ + im[4]).setAltTextDescription(cor).build());
        feitas++;
      } catch (err) {
        Logger.log('arte ' + spec.nome + ' ' + im[4] + ': ' + err.message);
      }
    });
  });
  return feitas;
}

/**
 * O repaint em si. Pra cada célula, acha o papel do hex que ela tem AGORA — primeiro contra a
 * paleta anterior (papelPorHexAntes, sem ambiguidade), e só se não achar, contra QUALQUER paleta
 * (papelPorHexGlobal_, a busca de resgate) —, e escreve o hex desse mesmo papel na paleta NOVA. Em
 * toda aba, no fundo (interior) e na fonte, em bloco via getBackgrounds()/setBackgrounds() e
 * getFontColors()/setFontColors(), que são rápidos mesmo em milhares de células porque cada aba
 * custa só duas idas e voltas à planilha, não uma por célula. A régua (a borda) vai à parte, em
 * repintarBordas_ — ela não é um papel de fundo/fonte.
 *
 * O OSSO (E8DCD4, "vida cheia" da decisão A5) é um caso à parte, achado
 * testando no Sheets em 18/09/2026: o gerador Python usa ele também como cor
 * PADRÃO de texto por boa parte da ficha, sem relação com vida — e numa
 * paleta clara isso ficava ilegível, porque um hex só não serve pra toda
 * célula: a mesma OSSO pode estar em cima de fundo, painel, painel_alto,
 * menu_grande ou acento, com contraste diferente em cada. Pedido do Mizuki:
 * em vez de UM substituto, um substituto POR PAPEL DE FUNDO, calculado com o
 * mesmo contraste WCAG dos outros treze — é o `osso_por_papel` que o
 * `derivar.py` grava pra cada uma das 122 entradas, e mora dentro do PALETAS.
 * Achar o papel da célula é olhar o fundo dela ANTES da troca (`f`, nesta
 * função) contra o mesmo papelDoFundo que decide o fundo — a régua/vida não
 * mudam de papel entre paletas, só de hex.
 */
function repintarPaleta_(ss, nomeAntigo, nomeNovo) {
  var antes = coresDoNome_(nomeAntigo) || PALETA_DE_FABRICA_;
  var agora = coresDoNome_(nomeNovo);
  if (!agora) return;

  var papeis = ['fundo', 'painel', 'painel_alto', 'linha', 'texto', 'texto_fraco',
                'tinta', 'papel', 'painel_baixo', 'bloco', 'acento', 'menu_grande'];
  var papelPorHexAntes = {};
  papeis.forEach(function (papel) {
    papelPorHexAntes['#' + String(antes[papel] || '').toUpperCase()] = papel;
  });
  var papelPorHexGlobal = papelPorHexGlobal_();
  var ossoNovo = agora.osso_por_papel || {};
  var avisoNovo = agora.aviso_por_papel || {};
  var candidatos = candidatosDeFonte_(agora, coresOpostas_(nomeNovo));
  var cacheLegivel = {};

  ABAS.forEach(function (spec) {
    var sh = ss.getSheetByName(spec.nome);
    if (!sh) return;
    // ABAS.rows/cols, não getLastRow()/getLastColumn(): achado em 18/09/2026 — essas duas só
    // contam célula com VALOR, e boa parte da tinta de fundo da ficha (a CARTEIRA sozinha tem
    // 14 linhas de fundo puro, sem valor nenhum, do fim do cartão pra baixo) não tem valor
    // nenhum, só cor. getLastRow() parava antes delas, e elas nunca eram lidas nem trocadas —
    // "as partes externas da ficha" que ficavam pretas depois da troca de tema. spec.rows e
    // spec.cols são o tamanho de verdade: o mesmo que montarAba_ pintou por inteiro.
    var nl = spec.rows, nc = spec.cols;
    var faixa = sh.getRange(1, 1, nl, nc);

    var fundos = faixa.getBackgrounds();
    var fontes = faixa.getFontColors();
    var mudouFundo = false, mudouFonte = false;
    var avisos = celulasDeAviso_(spec);
    var desenho = contrasteDeFabrica_(spec);

    for (var r = 0; r < nl; r++) {
      for (var c = 0; c < nc; c++) {
        var f = (fundos[r][c] || '').toUpperCase();
        var t = (fontes[r][c] || '').toUpperCase();
        var papelDoFundo = papelPorHexAntes[f] || papelPorHexGlobal[f];

        var novoFundo = f;
        if (papelDoFundo && agora[papelDoFundo] !== undefined) {
          novoFundo = '#' + String(agora[papelDoFundo]).toUpperCase();
          if (novoFundo !== f) { fundos[r][c] = novoFundo; mudouFundo = true; }
        }

        var novaFonte = t;
        if (avisos[r + ',' + c]) {
          novaFonte = '#' + String(avisoNovo[papelDoFundo] || agora.texto).toUpperCase();
        } else if (t === OSSO_HEX_) {
          var novoOsso = papelDoFundo && ossoNovo[papelDoFundo];
          if (novoOsso) novaFonte = '#' + String(novoOsso).toUpperCase();
        } else {
          var papelDaFonte = papelPorHexAntes[t] || papelPorHexGlobal[t];
          if (papelDaFonte && agora[papelDaFonte] !== undefined) {
            novaFonte = '#' + String(agora[papelDaFonte]).toUpperCase();
          }
        }

        novaFonte = fonteLegivel_(novaFonte, novoFundo, desenho[r][c], candidatos, cacheLegivel);
        if (novaFonte !== t) { fontes[r][c] = novaFonte; mudouFonte = true; }
      }
    }
    if (mudouFundo) faixa.setBackgrounds(fundos);
    if (mudouFonte) faixa.setFontColors(fontes);
  });

  repintarArte_(ss, agora, candidatos);

  // Sempre chama, sem comparar "mudou de verdade" antes — repintarBordas_ compara contra a régua
  // DE FÁBRICA (fixa), não contra `antes`, então não tem "não mudou" que valha a pena pular; e
  // chamar sempre faz a régua se autocorrigir mesmo se uma troca anterior tiver ficado pra trás.
  var paraRegua = '#' + String(agora.regua || '').toUpperCase();
  repintarBordas_(ss, paraRegua);
}

/**
 * A régua (a borda) — achado em 18/09/2026 que dava pra fazer sem varrer
 * célula a célula, ao contrário do que a versão anterior desta função
 * registrava. O motivo de pensar que precisava ler bordo a bordo era supor
 * que a cor variava célula a célula, do jeito que fundo e fonte variam — mas
 * a borda NÃO é assim aqui: a única cor de borda do script inteiro é a
 * régua ("8A7EC4") — até 19/09/2026 havia também um branco fixo de três specs,
 * que era engano de formatação da caixa ORIGEM e foi corrigido, ver
 * `ficha-v01/correcoes_borda.py` —, e ela vem inteira do `ABAS` (a mesma lista
 * global que o `Ficha.gs` usa pra montar a ficha, com o `bordas` de cada
 * aba: lado, traço, cor, faixas). Repintar é só re-desenhar essas mesmas
 * faixas com a cor nova — mas contra um alvo FIXO, não contra o "antes"
 * de cada troca.
 *
 * Bug achado testando no Sheets em 18/09/2026: a versão anterior comparava
 * `b[2]` (a cor ORIGINAL gravada no ABAS — sempre "8A7EC4", porque o
 * Ficha.gs só grava a régua de fábrica, nunca muda depois) contra `deRegua`
 * (a régua da paleta ANTERIOR, que só é "8A7EC4" na primeiríssima troca —
 * "Escolha uma paleta" para o primeiro tema escolhido). A partir da segunda
 * troca, `deRegua` já é a régua de algum tema de verdade (nunca mais
 * "8A7EC4"), a comparação nunca mais batia, e as bordas do resto da ficha
 * paravam de mudar pra sempre — só a borda da própria caixa da paleta (que
 * não faz essa comparação, sempre repinta direto) continuava acompanhando.
 * É exatamente o "só mudou a borda do botão da paleta" que o Mizuki
 * descreveu depois da segunda troca.
 *
 * O conserto: comparar contra `PALETA_DE_FABRICA_.regua` (a mesma constante
 * sempre, não o "antes" de cada chamada) — TODA faixa de régua do ABAS tem
 * essa cor gravada, sempre, então o filtro acha as mesmas ~20 faixas em
 * qualquer troca, e repinta pra régua atual sem depender de rastrear o
 * histórico. `repintarPaleta_` passou a chamar isso incondicionalmente, sem
 * comparar "mudou de verdade" antes — a régua sempre se autocorrige.
 *
 * A caixa da paleta em si também tem borda na régua, mas nasce depois de o
 * `Ficha.gs` rodar (em configurarPaleta_) e não mora no ABAS — repintada à
 * parte, no fim desta função.
 */
function repintarBordas_(ss, paraRegua) {
  var deRegua = '#' + PALETA_DE_FABRICA_.regua.toUpperCase();
  var TRACO = { thin: 'SOLID', medium: 'SOLID_MEDIUM', thick: 'SOLID_THICK', dashed: 'DASHED',
                mediumDashed: 'DASHED', dotted: 'DOTTED', hair: 'DOTTED', double: 'DOUBLE' };
  ABAS.forEach(function (spec) {
    var aba = ss.getSheetByName(spec.nome);
    if (!aba) return;
    (spec.bordas || []).forEach(function (b) {
      if (String(b[2]).toUpperCase() !== deRegua) return;
      var lado = b[0], traco = SpreadsheetApp.BorderStyle[TRACO[b[1]] || 'SOLID'];
      for (var i = 0; i < b[3].length; i += 400) {
        aba.getRangeList(b[3].slice(i, i + 400)).setBorder(
          lado === 'top' ? true : null, lado === 'left' ? true : null,
          lado === 'bottom' ? true : null, lado === 'right' ? true : null,
          null, null, paraRegua, traco);
      }
    });
  });

  var BORDA_CAIXA = SpreadsheetApp.BorderStyle.SOLID_MEDIUM;
  var valorPaleta = ss.getRangeByName(NOME_CEL_PALETA_);
  var rotuloPaleta = ss.getRangeByName(NOME_CEL_PALETA_ROTULO_);
  var avisoPaleta = ss.getRangeByName(NOME_CEL_PALETA_AVISO_);
  if (valorPaleta && rotuloPaleta) {
    [rotuloPaleta, valorPaleta, avisoPaleta].forEach(function (r) {
      if (r) r.setBorder(true, true, true, true, false, false, paraRegua, BORDA_CAIXA);
    });
  }
}
