# Instalar e medir os consertos 1–3 da ficha numa CÓPIA DE TESTE (Apps Script)

Você está no navegador, logado no Google como **cupcakemochi1201** (no Brave ela é a conta `/u/1`;
se as páginas abrirem em outra conta, troque o `/u/1` dos endereços pela posição certa). Tarefa:
medir quatro edições numa cópia de teste da planilha, instalar dois consertos no projeto Apps Script
**dessa cópia** e medir de novo. Responda em português do Brasil, tom direto.

## Regras duras

- Trabalhe SÓ na cópia **"TESTE pacote leve — pode apagar"**:
  - planilha: https://docs.google.com/spreadsheets/d/1kQuSggqnX1C6hu07HlTRXd_UYyyBGLJdHDgdM4Oyovg/edit
  - projeto: https://script.google.com/u/1/home/projects/1Sl3XTWIfZTb8o1EVfnhy46TJ0dFCXDqgPWmlMbFSrMDCPkB6-6vdd3iY/edit
  - execuções: https://script.google.com/u/1/home/projects/1Sl3XTWIfZTb8o1EVfnhy46TJ0dFCXDqgPWmlMbFSrMDCPkB6-6vdd3iY/executions
- **NUNCA** abra nem mexa nas oficiais: `1MQqh…` (Era da Revolução) e `1pgLD…` (Ciclo Maldito),
  nem nos projetos delas. Se algum link levar pra elas, pare.
- Não execute `construir`, `continuar` nem `acabar`. Não crie acionadores, não mude permissões,
  não aceite pedido de autorização novo (se aparecer, pare e me avise).
- Os trechos abaixo conferem o hash do que está instalado antes de gravar e devolvem um texto
  começando com `ERRO:` sem gravar nada se algo não bater. Se aparecer `ERRO:`, **pare** e me traga
  a mensagem inteira. Não tente consertar nem reescrever o trecho.
- Toda célula que você editar na planilha volta ao valor original no fim.

## Como medir uma edição

Edite a célula **na planilha, à mão** (clicar, digitar ou escolher no menu, Enter): é isso que
dispara o gatilho `onEdit`. Depois abra a página de execuções, espere a execução `onEdit` mais
nova terminar (atualize a página) e anote a **duração** e o **status** (Concluído / Tempo limite /
Falha). Uma edição por vez: espere a anterior terminar antes da próxima.

As quatro edições (anote o valor original de cada célula antes de mexer):

1. **CARTEIRA!A1** — digite `x`, Enter. Meça. Depois apague (Delete) e meça também.
2. **FICHA AMALDIÇOADA!B500** — digite `x`, Enter. Meça. Depois apague.
3. **FICHA PESSOAL!D64** (arma na mão principal) — escolha outra arma no menu da célula. Meça.
   Confira se a nota da caixa logo abaixo da mão (passe o mouse) passou a falar da arma nova.
   Depois volte a arma original.
4. **FICHA!D21** (Força, atributo base) — some 1 ao número que estiver lá. Meça. Depois volte.

Referência de antes (medido em 25/10): 1, 2 e 3 estouravam em ~30,6 s (tempo limite).

## Passo 1 · Medir ANTES

Faça as quatro edições acima e anote tudo.

## Passo 2 · Instalar

Abra o projeto no editor. No console de desenvolvedor da aba do editor (ou pela sua ferramenta de
executar JavaScript na página), rode os trechos abaixo **exatamente como estão**. Eles usam o
`monaco` da página. Se um deles responder "Esperava os cinco arquivos R53_CODIGO_" ou
"não encontrado", abra uma vez cada arquivo do projeto na barra lateral (Codigo.gs, EditorR53.gs,
Ficha.gs, Invocacoes.gs, Analise.gs, Configuracao.gs, Origens.gs) e rode de novo.

**2a. Conserto 1 (EditorR53.gs).** Esperado: `{antes: "bc3004641a1a", depois: "d2e572232a58"}`.

```js
await (async () => { try {
const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");
const ms = monaco.editor.getModels().filter(m => m.getValue().indexOf("function r53SincronizarFamilias_(") >= 0);
if (ms.length !== 1) throw new Error("EditorR53 não encontrado uma vez só: " + ms.length);
const v = ms[0].getValue(), antes = await sha(v);
if (antes !== "bc3004641a1a28c148885638955e6db66ffebaa01cd8acea30415cbbcd30e993") throw new Error("EditorR53 instalado diferente: " + antes);
const velho = "function r53SincronizarFamilias_(ss) {\n var current=r53Amparo_(ss),props=PropertiesService.getDocumentProperties(),raw=props.getProperty('r53_amparo_direto'),prev=raw?JSON.parse(raw):[];\n if(JSON.stringify(prev)===JSON.stringify(current))return false;\n", novo = "function r53SincronizarFamilias_(ss) {\n var current=r53Amparo_(ss),props=PropertiesService.getDocumentProperties(),raw=props.getProperty('r53_amparo_direto');\n // As propriedades do documento não vão na cópia da planilha. Sem estado, a\n // cópia herda os cartões já acertados: guardar o atual em vez de varrer 249.\n if(!raw){props.setProperty('r53_amparo_direto',JSON.stringify(current));return false;}\n var prev=JSON.parse(raw);\n if(JSON.stringify(prev)===JSON.stringify(current))return false;\n";
if (v.split(velho).length !== 2) throw new Error("bloco antigo não encontrado uma vez só");
const w = v.replace(velho, () => novo), depois = await sha(w);
if (depois !== "d2e572232a58643addb44847710cd0b4568ba5b8f8c95e8ac9d894e777ab48ef") throw new Error("saiu diferente do testado: " + depois);
ms[0].setValue(w);
return {antes: antes.slice(0, 12), depois: depois.slice(0, 12)};
} catch (err) { return "ERRO: " + err.message; } })()
```

**2b. Consertos 2 e 3 (módulo).** Esperado: `remendos: 8`, `hash_antigo: "2667ef41d84e"`,
`hash_novo: "9d1cec81cf90"`.

```js
await (async () => { try {
const aplicarIncremento = function aplicarIncremento(code, remendos, desde) {
  if (code.indexOf('var R53_PACOTE_LEVE_ = true;\n') !== 0) throw new Error('O módulo instalado não é o pacote leve');
  remendos.slice(desde).forEach(function (p, i) {
    var n = code.split(p[0]).length - 1;
    if (n !== 1) throw new Error('Remendo ' + (desde + i + 1) + ': âncora encontrada ' + n + ' vez(es)');
    code = code.replace(p[0], function () { return p[1]; });
  });
  return code;
};
const remendos = [["  try { esticarCaixas_(e, 'FICHA'); } catch (err) { console.log('ficha, a caixa que estica: ' + err.message); }\n  // Uma leitura da DADOS serve ao índice, às perícias e à Trilha.\n  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS').getDataRange().getValues();\n  var idx = indiceDosDados_(dados);\n  try { descansar_(e, idx); } catch (err) { console.log('ficha, o descanso: ' + err.message); }\n","  try { esticarCaixas_(e, 'FICHA'); } catch (err) { console.log('ficha, a caixa que estica: ' + err.message); }\n  // O índice sai do molde; a DADOS só é lida quando a edição é numa caixa que precisa dela (Caminho e XP).\n  var dadosLidos = null, lerDados = function () {\n    return dadosLidos || (dadosLidos = faixaDoMolde_(SpreadsheetApp.getActive().getSheetByName('DADOS')).getValues());\n  };\n  var idx = indiceEstatico_() || indiceDosDados_(lerDados());\n  var noCaminho = e.range.getA1Notation() === cel_(idx, 'caminho');\n  try { descansar_(e, idx); } catch (err) { console.log('ficha, o descanso: ' + err.message); }\n"],["  prenderTemp_(e, idx);\n  marcarPericiasDoCaminho_(e, idx, dados);\n  trilhaDoCaminho_(e, idx, dados);\n  try { habilidadesDaFicha_(e, idx); } catch (err) { console.log('habilidades: ' + err.message); }\n","  prenderTemp_(e, idx);\n  marcarPericiasDoCaminho_(e, idx, noCaminho ? lerDados() : null);\n  trilhaDoCaminho_(e, idx, noCaminho ? lerDados() : null);\n  try { habilidadesDaFicha_(e, idx); } catch (err) { console.log('habilidades: ' + err.message); }\n"],["  try { habilidadesDaFicha_(e, idx); } catch (err) { console.log('habilidades: ' + err.message); }\n  nivelPelaXP_(e, idx);\n  grupoDeArmaDaTrilha_(e, idx);\n","  try { habilidadesDaFicha_(e, idx); } catch (err) { console.log('habilidades: ' + err.message); }\n  nivelPelaXP_(e, idx, lerDados);\n  grupoDeArmaDaTrilha_(e, idx);\n"],["  });\n  return m;\n}\n\n","  });\n  return m;\n}\n\n/**\n * O mesmo índice, tirado do molde da DADOS sem ir à planilha. 25/10/2026: cada ida ao servidor custa 1,5 a 2 s\n * nesta ficha, e ler a DADOS inteira pelo getDataRange custava 5 a 6 s em toda edição da FICHA, só para achar\n * endereços que não mudam. As células do índice são ADDRESS(ROW(FICHA!X)...) ou texto; outra conta devolve null,\n * e quem chama lê a planilha como antes.\n */\nvar INDICE_ESTATICO_;\nfunction indiceEstatico_() {\n  if (INDICE_ESTATICO_ !== undefined) return INDICE_ESTATICO_;\n  var spec = typeof ABAS === 'undefined' ? null : ABAS.filter(function (s) { return s.nome === 'DADOS'; })[0];\n  if (!spec) return (INDICE_ESTATICO_ = null);\n  var linhas = {};\n  spec.vals.forEach(function (t) {\n    if (t[1] !== IDX_COL_CAMPO && t[1] !== IDX_COL_CEL) return;\n    (linhas[t[0]] = linhas[t[0]] || {})[t[1] === IDX_COL_CAMPO ? 'k' : 'v'] = t[2];\n  });\n  var m = {};\n  for (var r in linhas) {\n    var k = linhas[r].k, v = linhas[r].v;\n    if (!k || !v) continue;\n    if (typeof v === 'string' && v.charAt(0) === '=') {\n      var partes = [], re = /ADDRESS\\(ROW\\((?:'[^']+'|[A-Z_]+)!\\$?([A-Z]+)\\$?(\\d+)\\)/g, p;\n      while ((p = re.exec(v))) partes.push(p[1] + p[2]);\n      if (!partes.length) return (INDICE_ESTATICO_ = null);\n      v = partes.join(':');\n    }\n    m[k] = String(v);\n  }\n  return (INDICE_ESTATICO_ = m);\n}\n\n/** Várias células da mesma aba numa leitura só, pelo retângulo que cobre todas: {'D26': valor, ...}. */\nfunction lerCelulas_(aba, lista) {\n  var f = lista.map(limitesA1_);\n  var l1 = Math.min.apply(null, f.map(function (x) { return x.l1; })), c1 = Math.min.apply(null, f.map(function (x) { return x.c1; }));\n  var l2 = Math.max.apply(null, f.map(function (x) { return x.l1; })), c2 = Math.max.apply(null, f.map(function (x) { return x.c1; }));\n  var v = aba.getRange(l1, c1, l2 - l1 + 1, c2 - c1 + 1).getValues(), out = {};\n  lista.forEach(function (a1, i) { out[a1] = v[f[i].l1 - l1][f[i].c1 - c1]; });\n  return out;\n}\n\n/** A aba inteira pelo tamanho do molde: o getDataRange sozinho custava 4,7 s na DADOS (medido em 25/10/2026). */\nfunction faixaDoMolde_(aba) {\n  var nome = aba.getName(), spec = typeof ABAS === 'undefined' ? null : ABAS.filter(function (s) { return s.nome === nome; })[0];\n  return spec && spec.rows && spec.cols ? aba.getRange(1, 1, spec.rows, spec.cols) : aba.getDataRange();\n}\n\n"],[" */\nfunction nivelPelaXP_(e, idx) {\n  var cx = cel_(idx, 'xp'), cn = cel_(idx, 'nivel');\n"," */\nfunction nivelPelaXP_(e, idx, lerDados) {\n  var cx = cel_(idx, 'xp'), cn = cel_(idx, 'nivel');\n"],["  if (isNaN(xp)) return;\n  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS').getDataRange().getValues();\n  for (var r = 0; r + 1 < dados.length; r++) {\n","  if (isNaN(xp)) return;\n  var dados = lerDados ? lerDados() : faixaDoMolde_(SpreadsheetApp.getActive().getSheetByName('DADOS')).getValues();\n  for (var r = 0; r + 1 < dados.length; r++) {\n"],["    if (!ct || ct !== e.range.getA1Notation()) return;\n    var antes = e.range.getValue();\n    var depois = tetoTemp_(antes, ficha.getRange(cel_(idx, r + '_max')).getValue());\n    if (depois !== antes) e.range.setValue(depois);\n","    if (!ct || ct !== e.range.getA1Notation()) return;\n    var v = lerCelulas_(ficha, [ct, cel_(idx, r + '_max')]);\n    var antes = v[ct];\n    var depois = tetoTemp_(antes, v[cel_(idx, r + '_max')]);\n    if (depois !== antes) e.range.setValue(depois);\n"],["    if (!cd || cd !== e.range.getA1Notation()) return;\n    var passo = Number(e.range.getValue());\n    if (!passo) return;\n","    if (!cd || cd !== e.range.getA1Notation()) return;\n    var ca = cel_(idx, r), cm = cel_(idx, r + '_max'), ct = cel_(idx, r + '_temp');\n    // As quatro caixas estão na mesma linha: uma leitura em vez de quatro idas ao servidor\n    var v = lerCelulas_(ficha, [cd, ca, cm].concat(ct ? [ct] : []));\n    var passo = Number(v[cd]);\n    if (!passo) return;\n"],["    if (!passo) return;\n    var atual = ficha.getRange(cel_(idx, r));\n    var ct = cel_(idx, r + '_temp');\n    var temp = ct ? ficha.getRange(ct) : null;\n    var antes = temp ? Math.max(0, Number(temp.getValue()) || 0) : 0;\n\n","    if (!passo) return;\n    var antes = ct ? Math.max(0, Number(v[ct]) || 0) : 0;\n\n"],["\n    var fim = aplicaPasso_(atual.getValue(),\n                           ficha.getRange(cel_(idx, r + '_max')).getValue(),\n                           antes, passo);\n\n","\n    var fim = aplicaPasso_(v[ca], v[cm], antes, passo);\n\n"],["\n    atual.setValue(fim.atual);\n    if (temp && fim.temp !== antes) temp.setValue(fim.temp);\n    e.range.clearContent();\n","\n    ficha.getRange(ca).setValue(fim.atual);\n    if (ct && fim.temp !== antes) ficha.getRange(ct).setValue(fim.temp);\n    e.range.clearContent();\n"],["  var ficha = e.range.getSheet();\n  var le = function (k) { var c = cel_(idx, k); return c ? Number(ficha.getRange(c).getValue()) || 0 : 0; };\n  var onde = { vida: 'vida', pe: 'energia', integ: 'integridade', exaustao: 'exaustão' };\n","  var ficha = e.range.getSheet();\n  var onde = { vida: 'vida', pe: 'energia', integ: 'integridade', exaustao: 'exaustão' };\n"],["                                                       .filter(function (c) { return c; });\n  var antes = { vidaMax: le('vida_max'), peMax: le('energia_max'), integMax: le('integridade_max') };\n","                                                       .filter(function (c) { return c; });\n  var cExtras = cel_(idx, 'sequela extras');\n  // Tudo o que o descanso consulta numa leitura só (cada ida ao servidor custa 1,5 a 2 s)\n  var lidas = ['vida_max', 'energia_max', 'integridade_max'].concat(Object.keys(onde).map(function (k) { return onde[k]; }))\n    .map(function (k) { return cel_(idx, k); }).concat(caixinhas, cExtras ? [cExtras] : []).filter(function (c) { return c; });\n  var v = lerCelulas_(ficha, lidas);\n  var le = function (k) { var c = cel_(idx, k); return c ? Number(v[c]) || 0 : 0; };\n  var antes = { vidaMax: le('vida_max'), peMax: le('energia_max'), integMax: le('integridade_max') };\n"],["  Object.keys(onde).forEach(function (k) { antes[k] = le(onde[k]); });\n  var cExtras = cel_(idx, 'sequela extras');\n  var extras = cExtras ? Math.max(0, Number(ficha.getRange(cExtras).getValue()) || 0) : 0;\n  antes.sequelas = caixinhas.filter(function (c) { return ficha.getRange(c).getValue() === true; }).length + extras;\n  var fim = contaDoDescanso_(tipo, antes);\n","  Object.keys(onde).forEach(function (k) { antes[k] = le(onde[k]); });\n  var extras = cExtras ? Math.max(0, Number(v[cExtras]) || 0) : 0;\n  antes.sequelas = caixinhas.filter(function (c) { return v[c] === true; }).length + extras;\n  var fim = contaDoDescanso_(tipo, antes);\n"],["  trocaArmaDoCaminho_(e, idx);\n  try { fichaMexeNaPessoal_(e, idx); } catch (err) { console.log('ficha pessoal: ' + err.message); }\n  continuarPaleta_(inicio, null, false, e.range);\n","  trocaArmaDoCaminho_(e, idx);\n  try { fichaMexeNaPessoalLeve_(e, idx); } catch (err) { console.log('ficha pessoal: ' + err.message); }\n  continuarPaleta_(inicio, null, false, e.range);\n"],["\n/** O índice da FICHA PESSOAL: {campo: 'D39'} ou {campo: 'D45:AT57'}. Lê só as duas colunas dele. */\nfunction indicePessoal_() {\n","\n/**\n * Uma tabela da DADOS lida só nas colunas dela. 25/10/2026: a linha e as colunas do cabeçalho saem do molde, e a\n * leitura vai do cabeçalho até o fim do molde; dá o mesmo que o tabelaDaDados_ com a DADOS inteira, que custava ~7 s.\n * Sem o molde, ou sem o cabeçalho nele, lê a DADOS inteira como antes.\n */\nfunction tabelaLida_(ss, chave, outras) {\n  outras = outras || [];\n  var aba = ss.getSheetByName('DADOS'), nomes = [chave].concat(outras), cab = {};\n  var spec = typeof ABAS === 'undefined' ? null : ABAS.filter(function (s) { return s.nome === 'DADOS'; })[0];\n  if (spec) spec.vals.forEach(function (t) {\n    if (nomes.indexOf(t[2]) < 0) return;\n    var l = cab[t[0]] = cab[t[0]] || {};\n    if (!l[t[2]] || t[1] < l[t[2]]) l[t[2]] = t[1];\n  });\n  var linha = Object.keys(cab).map(Number).sort(function (a, b) { return a - b; })\n    .filter(function (r) { return nomes.every(function (n) { return cab[r][n]; }); })[0];\n  if (!linha) return tabelaDaDados_(aba.getDataRange().getValues(), chave, outras);\n  var cols = nomes.map(function (n) { return cab[linha][n]; });\n  var c1 = Math.min.apply(null, cols), c2 = Math.max.apply(null, cols);\n  return tabelaDaDados_(aba.getRange(linha, c1, spec.rows - linha + 1, c2 - c1 + 1).getValues(), chave, outras);\n}\n\n/**\n * Um índice tirado do molde da DADOS, pelas duas colunas dele (a do campo e a do endereço), como o indiceEstatico_\n * faz com o da FICHA. Endereço que não é ADDRESS(ROW(aba!X)...) nem texto devolve null, e quem chama lê a planilha.\n */\nfunction indiceDoMolde_(colCampo, colCel, cabecalho) {\n  var spec = typeof ABAS === 'undefined' ? null : ABAS.filter(function (s) { return s.nome === 'DADOS'; })[0];\n  if (!spec) return null;\n  var linhas = {};\n  spec.vals.forEach(function (t) {\n    if (t[1] !== colCampo && t[1] !== colCel) return;\n    (linhas[t[0]] = linhas[t[0]] || {})[t[1] === colCampo ? 'k' : 'v'] = t[2];\n  });\n  var m = {};\n  for (var r in linhas) {\n    var k = linhas[r].k, v = linhas[r].v;\n    if (!k || !v || k === cabecalho) continue;\n    if (typeof v === 'string' && v.charAt(0) === '=') {\n      var partes = [], re = /ADDRESS\\(ROW\\((?:'[^']+'|[A-Z_]+)!\\$?([A-Z]+)\\$?(\\d+)\\)/g, p;\n      while ((p = re.exec(v))) partes.push(p[1] + p[2]);\n      if (!partes.length) return null;\n      v = partes.join(':');\n    }\n    m[k] = String(v);\n  }\n  return m;\n}\n\n/**\n * O índice da FICHA PESSOAL: {campo: 'D39'} ou {campo: 'D45:AT57'}. 25/10/2026: sai do molde; reler as duas colunas\n * dele custava duas idas ao servidor em toda edição da aba. Sem o molde, lê só as duas colunas dele.\n */\nvar INDICE_PESSOAL_ESTATICO_;\nfunction indicePessoal_() {\n"],["function indicePessoal_() {\n  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS');\n","function indicePessoal_() {\n  if (INDICE_PESSOAL_ESTATICO_ === undefined) INDICE_PESSOAL_ESTATICO_ = indiceDoMolde_(IDXP_COL_CAMPO, IDXP_COL_CAMPO + 1, 'campo pessoal');\n  if (INDICE_PESSOAL_ESTATICO_) return INDICE_PESSOAL_ESTATICO_;\n  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS');\n"],["\nfunction pessoalEditada_(e) {\n","\n/**\n * As notas vivas com leitura curta. 25/10/2026: da DADOS só as colunas da tabela das notas, e da FICHA PESSOAL só o\n * retângulo das caixas que têm nota; o notasVivas_ lia as duas abas inteiras, e a arma na mão estourava os 30 s. O\n * notasVivas_ fica como está porque o caminho_leve.js o extrai para o Caminho.\n */\nfunction notasVivasLeves_(ss) {\n  var aba = ss.getSheetByName(ABA_PESSOAL_);\n  if (!aba) return 0;\n  var linhas = tabelaLida_(ss, 'nota viva', ['texto da nota', 'caixa da nota'])\n    .filter(function (l) { return l['caixa da nota']; });\n  if (!linhas.length) return 0;\n  var f = linhas.map(function (l) { return limitesA1_(String(l['caixa da nota'])); });\n  var l1 = Math.min.apply(null, f.map(function (x) { return x.l1; })), c1 = Math.min.apply(null, f.map(function (x) { return x.c1; }));\n  var l2 = Math.max.apply(null, f.map(function (x) { return x.l1; })), c2 = Math.max.apply(null, f.map(function (x) { return x.c1; }));\n  // As notas são lidas antes de qualquer escrita, como no notasVivas_.\n  var notas = aba.getRange(l1, c1, l2 - l1 + 1, c2 - c1 + 1).getNotes(), n = 0;\n  linhas.forEach(function (l, i) {\n    var texto = String(l['texto da nota'] || '');\n    if ((notas[f[i].l1 - l1][f[i].c1 - c1] || '') !== texto) { aba.getRange(String(l['caixa da nota'])).setNote(texto); n++; }\n  });\n  return n;\n}\n\nfunction pessoalEditada_(e) {\n"],["  if (notas && volumeDoItem_(e, aba, ip)) SpreadsheetApp.flush();\n  var dados = ss.getSheetByName('DADOS').getDataRange().getValues();\n  if (treino) treinoMarcado_(e, aba, dados, ip);\n","  if (notas && volumeDoItem_(e, aba, ip)) SpreadsheetApp.flush();\n  // As notas leem só a tabela delas. O treino e a missão, que quase sempre chegam por outro caminho, leem a DADOS\n  // pelo tamanho do molde, sem o getDataRange.\n  var dados = treino || missao ? faixaDoMolde_(ss.getSheetByName('DADOS')).getValues() : null;\n  if (treino) treinoMarcado_(e, aba, dados, ip);\n"],["  if (missao) nivelPelaMissao_(ss, dados, ip);\n  if (notas) notasVivas_(ss, dados);\n}\n","  if (missao) nivelPelaMissao_(ss, dados, ip);\n  if (notas) notasVivasLeves_(ss);\n}\n"],["  var nome = String(e.range.getValue() || '');\n  var dados = SpreadsheetApp.getActive().getSheetByName('DADOS').getDataRange().getValues();\n  var doLivro = tabelaDaDados_(dados, 'capacidade da origem').some(function (l) { return l['capacidade da origem'] === nome; });\n  var custom = SpreadsheetApp.getActive().getSheetByName('DADOS_CUSTOM');\n","  var nome = String(e.range.getValue() || '');\n  var doLivro = tabelaLida_(SpreadsheetApp.getActive(), 'capacidade da origem').some(function (l) { return l['capacidade da origem'] === nome; });\n  var custom = SpreadsheetApp.getActive().getSheetByName('DADOS_CUSTOM');\n"],["  notasVivas_(ss, dados);\n}\n","  notasVivas_(ss, dados);\n}\n\n/**\n * O fichaMexeNaPessoal_ do onEdit comum. 25/10/2026: a Força só refaz as notas, e com a leitura curta do\n * notasVivasLeves_ (ler a DADOS inteira custava 8 idas). O Caminho, quando chega aqui, segue pelo de sempre.\n */\nfunction fichaMexeNaPessoalLeve_(e, idx) {\n  var a1 = e.range.getA1Notation();\n  if (a1 === cel_(idx, 'caminho')) return fichaMexeNaPessoal_(e, idx);\n  if (a1 !== cel_(idx, 'atr_base_Força') && a1 !== cel_(idx, 'corpo_Força')) return;\n  notasVivasLeves_(SpreadsheetApp.getActive());\n}\n"]];
const ms = monaco.editor.getModels();
const dados = [];
for (const m of ms) { const v = m.getValue(); const x = /^(\/\/[^\n]*\n)var R53_CODIGO_(\d+)_ = ("[^\n]*");\n?$/.exec(v); if (x) dados[+x[2]] = {m, cab: x[1], s: JSON.parse(x[3])}; }
if (dados.length !== 5 || dados.some(d => !d)) throw new Error("Esperava os cinco arquivos R53_CODIGO_");
const cod = ms.filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);
if (cod.length !== 1) throw new Error("r53Modulo_ não encontrado uma vez só");
const fonte = cod[0].getValue();
if (fonte.indexOf("R53_MODULO_=(new Function(code))();") < 0) throw new Error("O r53Modulo_ não é o do pacote leve");
const hashAntigo = /if\(hash!=='([0-9a-f]{64})'\)throw new Error\('Pacote R53 incompleto/.exec(fonte);
if (!hashAntigo || hashAntigo[1] !== "2667ef41d84e44f565228bae47d7a6b9cf08bb7bfef8c60f2467383075aaee53") throw new Error("Hash instalado diferente do esperado: " + (hashAntigo && hashAntigo[1]));
const b64 = dados.map(d => d.s).join("");
const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
const texto = await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"))).text();
const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");
if (await sha(texto) !== hashAntigo[1]) throw new Error("Pacote instalado diferente do hash conferido");
const code = aplicarIncremento(texto, remendos, 14);
const hashNovo = await sha(code);
if (hashNovo !== "9d1cec81cf90bac42dd044d619843857b9c5fff3538ea0b8a0909899ff62fdce") throw new Error("O módulo saiu diferente do testado no node: " + hashNovo);
const gz = new Uint8Array(await new Response(new Blob([new TextEncoder().encode(code)]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer());
let novo64 = ""; for (let i = 0; i < gz.length; i += 0x8000) novo64 += String.fromCharCode.apply(null, gz.subarray(i, i + 0x8000));
novo64 = btoa(novo64);
const fatias = []; for (let i = 0; i < novo64.length; i += 850000) fatias.push(novo64.slice(i, i + 850000));
if (fatias.length > 5) throw new Error("Pacote passa de cinco arquivos");
dados.forEach((d, i) => d.m.setValue(d.cab + "var R53_CODIGO_" + i + "_ = " + JSON.stringify(fatias[i] || "") + ";\n"));
cod[0].setValue(fonte.replace(hashAntigo[0], hashAntigo[0].replace(hashAntigo[1], hashNovo)));
return {remendos: remendos.length - 14, base64_antes: b64.length, base64_depois: novo64.length, arquivos_com_dados: fatias.length, hash_antigo: hashAntigo[1].slice(0, 12), hash_novo: hashNovo.slice(0, 12)};
} catch (err) { return "ERRO: " + err.message + " | " + String(err.stack).split("\n").slice(0, 3).join(" / "); } })()
```

**2c. Salvar.** Salve o projeto (ícone de disquete / Ctrl+S; todos os arquivos alterados precisam
sair do estado "não salvo": EditorR53.gs, Codigo.gs e os de dados). Depois **recarregue a página
do editor** e rode a conferência. Esperado: `editor: "d2e572232a58"`, `modulo_declarado` e
`modulo_real` iguais a `"9d1cec81cf90"`.

```js
await (async () => { try {
const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");
const ms = monaco.editor.getModels();
const ed = ms.filter(m => m.getValue().indexOf("function r53SincronizarFamilias_(") >= 0);
const dados = []; for (const m of ms) { const x = /^(\/\/[^\n]*\n)var R53_CODIGO_(\d+)_ = ("[^\n]*");\n?$/.exec(m.getValue()); if (x) dados[+x[2]] = JSON.parse(x[3]); }
const cod = ms.filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);
const h = /if\(hash!=='([0-9a-f]{64})'\)throw new Error\('Pacote R53 incompleto/.exec(cod[0].getValue());
const bin = Uint8Array.from(atob(dados.join("")), c => c.charCodeAt(0));
const texto = await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"))).text();
return {editor: ed.length === 1 ? (await sha(ed[0].getValue())).slice(0, 12) : "editor x" + ed.length, modulo_declarado: h && h[1].slice(0, 12), modulo_real: (await sha(texto)).slice(0, 12), arquivos_de_dados: dados.filter(Boolean).length};
} catch (err) { return "ERRO: " + err.message; } })()
```

## Passo 3 · Medir DEPOIS

Repita as quatro edições. Na CARTEIRA, faça a edição `x` **duas vezes** (com o apagar entre elas):
a primeira grava um estado que a cópia não tinha, a segunda é a de regime. Confira de novo a nota
da arma na mão.

## O que me devolver

Uma tabela assim, mais qualquer erro ou coisa estranha que tiver visto:

| Edição | Antes (s, status) | Depois (s, status) | Conferido na tela |
|---|---|---|---|
| CARTEIRA A1 = x | | 1ª: / 2ª: | |
| CARTEIRA A1 apagar | | | |
| FICHA AMALDIÇOADA B500 = x | | | |
| FICHA PESSOAL D64 (arma) | | | nota mudou? |
| FICHA D21 (Força +1) | | | |

E as respostas exatas dos trechos 2a, 2b e da conferência.
