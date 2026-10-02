/**
 * Teste de bancada da forma C (02/10/2026): o script esconde na FICHA AMALDIÇOADA o que a rota não usa, quando a
 * Origem muda na FICHA. Antes de construir a aba nas quatro rotas, isto confere no Sheets de verdade o que o Sheets de
 * mentira não sabe dizer:
 *   1. a linha escondida pelo script continua escondida quando alguém abre e fecha o grupo em volta dela;
 *   2. o Domínio volta como estava (fechado ou aberto) quando a Origem volta para uma rota que tem Domínio;
 *   3. funciona numa cópia da planilha, só com o gatilho simples (onEdit), sem autorizar nada.
 *
 * Rodar: numa planilha em branco, Extensões > Apps Script, apague o que tiver, cole este arquivo, salve, e execute
 * montarTeste (ele pede autorização uma vez, porque é você rodando à mão). O roteiro do teste fica escrito na aba FICHA.
 *
 * Não mexe em nada da sua ficha de verdade: ele só cria as abas FICHA e FICHA AMALDIÇOADA na planilha em branco.
 */

// a lista do menu de Origem da FICHA, na ordem do ficha_automatica.origens_do_menu
var ORIGENS = ['Latente', 'Receptáculo', 'Descendente', 'Reencarnado', 'Feto', 'Restrição Celestial · corpo pela técnica',
               'Latente · Sem Técnica', 'Receptáculo · Sem Técnica', 'Descendente · Sem Técnica', 'Reencarnado · Sem Técnica',
               'Feto · Sem Técnica', 'Corpo Amaldiçoado', 'Restrição Celestial · sem energia'];
var AM = 'FICHA AMALDIÇOADA';
// as faixas que a rota decide, na aba de teste: [primeira linha, quantas, quem vê]
var FAIXAS = [
  { nome: 'a linha da rota', de: 4, n: 3, ve: function (r) { return r !== 'Fundamento'; } },
  { nome: 'a Expansão de Domínio', de: 14, n: 6, ve: function (r) { return r === 'Fundamento'; } },
  { nome: 'a linha do Estímulo Muscular', de: 24, n: 2, ve: function (r) { return r === 'Técnica Marcial sem energia'; } }
];

function montarTeste() {
  var ss = SpreadsheetApp.getActive();
  var ficha = ss.getSheetByName('FICHA') || ss.insertSheet('FICHA');
  var am = ss.getSheetByName(AM) || ss.insertSheet(AM);
  ficha.clear(); am.clear();
  am.showRows(1, am.getMaxRows());
  try { am.getRange(1, 1, am.getMaxRows(), 1).shiftRowGroupDepth(-8); } catch (err) { }   // rodar de novo zera os grupos

  ficha.getRange('A2').setValue('Origem');
  ficha.getRange('B2').setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(ORIGENS, true).build()).setValue('Latente');
  ficha.getRange('A3').setValue('Rota');
  ficha.getRange('A4').setValue('Relatório');
  ficha.setColumnWidth(2, 260); ficha.setColumnWidth(4, 560);
  var roteiro = [
    'ROTEIRO (anote o que acontecer em cada passo; o relatório da linha 4 ajuda)',
    '1. Em B2, escolha "Corpo Amaldiçoado". Na FICHA AMALDIÇOADA: as linhas 14 a 19 (Domínio) e 24 a 25 (Estímulo) somem; as linhas 4 a 6 (linha da rota) aparecem.',
    '2. Em B2, escolha "Latente". As linhas 4 a 6 somem; a linha 14 volta, e o Domínio volta FECHADO (só a linha 14, com o +).',
    '3. Na FICHA AMALDIÇOADA, abra o Domínio (+ ao lado da linha 14). Volte aqui, escolha "Corpo Amaldiçoado" e depois "Latente". O Domínio tem de voltar ABERTO.',
    '4. Com "Latente" (linhas 4 a 6 escondidas), feche a Técnica (− ao lado da linha 1) e abra de novo. As linhas 4 a 6 têm de continuar escondidas.',
    '5. Escolha "Restrição Celestial · sem energia". As linhas 24 e 25 aparecem.',
    '6. Arquivo > Fazer uma cópia. Na cópia, sem rodar nada, repita o passo 1. Tem de funcionar igual.'
  ];
  ficha.getRange(6, 1, roteiro.length, 1).setValues(roteiro.map(function (t) { return [t]; }));

  // a aba de teste: os rótulos dizem o que cada linha imita
  var linhas = {
    1: 'TÉCNICA (título da seção; o − dela fecha as linhas 2 a 12)', 2: 'nome · tipo de dano · atributo · CD', 3: '(valores)',
    4: 'LINHA DA ROTA: rota · semente ou equipamento', 5: '(valores da linha da rota)', 6: '(atributo de cada grupo)',
    7: 'REGRA', 8: '(texto)', 9: 'DESCRIÇÃO · SELO', 10: '(texto)', 11: 'REGRA PRÓPRIA', 12: 'FAMÍLIAS',
    14: 'EXPANSÃO DE DOMÍNIO (título; o + dela abre as linhas 15 a 19)', 15: 'degrau · custa · dura · raio · desconto', 16: '(valores)',
    17: 'COMO É POR DENTRO', 18: '(texto)', 19: '(texto)',
    21: 'APTIDÕES E REFINO (título; o − dela fecha as linhas 22 a 25)', 22: 'refino · compradas · cobrir-se · canalizar · reação', 23: '(valores)',
    24: 'ESTÍMULO MUSCULAR: perícia · Teste · usos', 25: '(valores do Estímulo)'
  };
  Object.keys(linhas).forEach(function (r) { am.getRange(Number(r), 1).setValue(linhas[r]); });
  am.setColumnWidth(1, 520);
  [1, 14, 21].forEach(function (r) { am.getRange(r, 1).setFontWeight('bold').setBackground('#F5B7D4'); });

  // os grupos como a aba de verdade: o + fica na linha antes do grupo
  am.setRowGroupControlPosition(SpreadsheetApp.GroupControlTogglePosition.BEFORE);
  am.getRange('A2:A12').shiftRowGroupDepth(1);
  am.getRange('A15:A19').shiftRowGroupDepth(1);
  am.getRange('A22:A25').shiftRowGroupDepth(1);
  am.getRowGroup(15, 1).collapse();                      // o Domínio nasce fechado, como desde o B29
  aplicarRota_(ss, 'Latente');
}

function onEdit(e) {
  if (!e || !e.range) return;
  var aba = e.range.getSheet();
  if (aba.getName() !== 'FICHA' || e.range.getA1Notation() !== 'B2') return;
  aplicarRota_(e.source, String(e.range.getValue()));
}

function rotaDa_(origem) {
  if (origem === 'Restrição Celestial · sem energia') return 'Técnica Marcial sem energia';
  if (origem === 'Corpo Amaldiçoado') return 'Técnica Marcial com energia';
  if (origem.indexOf(' · Sem Técnica') >= 0) return 'Sem Técnica';
  return 'Fundamento';
}

/**
 * Esconde ou mostra cada faixa pela rota. Antes de mostrar, anota se o grupo de dentro estava fechado; depois do
 * showRows, confere de novo, e fecha de volta se o Sheets tiver aberto. O relatório diz qual dos dois aconteceu: é isso
 * que decide como o Codigo.gs de verdade vai fazer.
 */
function aplicarRota_(ss, origem) {
  var am = ss.getSheetByName(AM), ficha = ss.getSheetByName('FICHA');
  var rota = rotaDa_(origem), rel = [];
  FAIXAS.forEach(function (f) {
    if (f.ve(rota)) {
      var grupo = null, antes = null;
      try { grupo = am.getRowGroup(f.de + 1, 1); antes = grupo ? grupo.isCollapsed() : null; } catch (err) { grupo = null; }
      am.showRows(f.de, f.n);
      var depois = grupo ? am.getRowGroup(f.de + 1, 1).isCollapsed() : null;
      if (grupo && antes && !depois) { am.getRowGroup(f.de + 1, 1).collapse(); rel.push(f.nome + ': mostrada; o showRows ABRIU o grupo, e o script fechou de volta'); }
      else if (grupo) rel.push(f.nome + ': mostrada; grupo ' + (antes ? 'fechado' : 'aberto') + ' antes e ' + (depois ? 'fechado' : 'aberto') + ' depois');
      else rel.push(f.nome + ': mostrada');
    } else {
      am.hideRows(f.de, f.n);
      rel.push(f.nome + ': escondida');
    }
  });
  ficha.getRange('B3').setValue(rota);
  ficha.getRange('D4').setValue(rel.join(' | '));
  ss.toast('Rota: ' + rota, 'Teste da forma C', 5);
}
