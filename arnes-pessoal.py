# -*- coding: utf-8 -*-
"""Arnes de perturbacao do regressao-pessoal.js: o que o Codigo.gs faz pela FICHA PESSOAL.

As tres regras do projeto, e nenhuma pode ser pulada:
  1. numa copia isolada, nunca nos arquivos reais
  2. a base tem que passar NA COPIA antes de perturbar
  3. cada perturbacao tem que MUDAR o arquivo de verdade antes de eu ler o resultado

Cada perturbacao e um defeito que o script poderia ter, e a agulha e a frase da checagem que tem de acender.
"""
import os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
PRECISA = ["regressao-pessoal.js", "regressao-construir.js", "medidas/sheets-de-mentira.js", "catalogo-projeto-m.json", "manual.txt", "apps-script/Codigo.gs",
           "apps-script/Ficha.gs", "apps-script/Habilidades.gs",   # 05/10/2026: o texto das cartas da seção 7
           "apps-script/Invocacoes.gs"]                             # 06/10/2026: as abas da invocação, que se juntam ao ABAS
NODE = shutil.which("node") or shutil.which("nodejs")


def roda(pasta, teste="regressao-pessoal.js"):
    r = subprocess.run([NODE, teste], cwd=pasta, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def copia():
    d = tempfile.mkdtemp(prefix="arnes-pessoal-")
    for f in PRECISA:
        os.makedirs(os.path.dirname(os.path.join(d, f)), exist_ok=True)
        shutil.copy(os.path.join(AQUI, f), os.path.join(d, f))
    return d


if NODE is None:
    print("node nao existe nesta maquina: o arnes da FICHA PESSOAL nao roda aqui.")
    sys.exit(0)

print("=" * 70)
print("PASSO 1 - a base passa NA COPIA?  (sem isso toda perturbacao e falso positivo)")
base = copia()
for _t in ("regressao-pessoal.js", "regressao-construir.js"):
    cod, saida = roda(base, _t)
    print(f"  {_t}: codigo de saida {cod}  -> {'passa limpa' if cod == 0 else 'JA FALHA'}")
    assert cod == 0, "A BASE FALHA NA COPIA. O arnes inteiro seria falso positivo.\n" + saida
shutil.rmtree(base)
print("  base limpa. pode perturbar.\n")

CONTA = {"acendeu": 0, "verde": 0, "erros": []}


def edita(nome, arquivo, antes_txt, depois_txt, agulha, espera_verde=False, teste="regressao-pessoal.js"):
    d = copia()
    alvo = os.path.join(d, arquivo)
    antes = open(alvo, encoding="utf-8").read()
    if antes.count(antes_txt) != 1:
        print(f"  [INUTIL        ] {nome:62} -> o trecho aparece {antes.count(antes_txt)} vez(es) no arquivo")
        CONTA["erros"].append(nome); shutil.rmtree(d); return
    open(alvo, "w", encoding="utf-8").write(antes.replace(antes_txt, depois_txt))
    cod, saida = roda(d, teste)
    shutil.rmtree(d)
    acesas = [l for l in saida.splitlines() if l.startswith("  FALHA ") or l.startswith(">>> O construir() PAROU")]
    if espera_verde:
        bom, veredito = cod == 0, "FICOU VERDE" if cod == 0 else "ACENDEU A ESMO"
    else:
        bom = cod != 0 and any(agulha in l for l in acesas)
        veredito = "ACENDEU" if bom else ("acendeu outra" if cod != 0 else "NAO ACENDEU")
    print(f"  [{veredito:14}] {nome:62} -> saida {cod}, {len(acesas)} checagem(ns)")
    if bom:
        CONTA["verde" if espera_verde else "acendeu"] += 1
    else:
        CONTA["erros"].append(nome)


C = "apps-script/Codigo.gs"
print("PASSO 2 - cada defeito acende a checagem dele")
edita("a caixa do grupo marca ao contrario", C,
      "(marcadas[a.caixa] === true) !== valor) muda[a.caixa] = valor;", "(marcadas[a.caixa] === true) !== valor) muda[a.caixa] = !valor;",
      "o grupo marca e desmarca as armas dele")
edita("o grupo fica marcado com uma arma so", C,
      ".every(function (a) { return marcadas[a.caixa] === true; });", ".some(function (a) { return marcadas[a.caixa] === true; });",
      "uma arma marcada sozinha não marca o grupo")
edita("a caixa do grupo mexe em arma de outro grupo", C,
      "if (a.categoria === grupo.categoria && (marcadas", "if ((marcadas", "o grupo marca e desmarca as armas dele")
edita("sem Caminho, o treino do conjurador entra", C,
      "out[x.caixa] = existe && (tudo ||", "out[x.caixa] = (tudo ||", "sem Caminho escolhido, nenhuma caixa")
edita("todo Caminho treina todas as armas", C,
      "var existe = caminhos.indexOf(caminho) >= 0, tudo = todas.indexOf(caminho) >= 0;",
      "var existe = caminhos.indexOf(caminho) >= 0, tudo = existe;", "só Arma de Fogo e Balestra")
edita("o XP desce o nivel", C, "return alvo > atual ? alvo : null;", "return alvo !== atual ? alvo : null;", "o XP nunca desce o nível")
edita("o XP passa do limiar do feito", C, "if (limiar && atual <= limiar) alvo = Math.min(alvo, limiar);", "", "o limiar do feito")
edita("o limiar segura quem ja passou dele", C, "if (limiar && atual <= limiar)", "if (limiar)", "quem já passou do limiar sobe pelo XP")
edita("o nivel sobe um XP antes da hora", C, "if (Number(l.xp) <= xp) melhor = Number(l.nivel);",
      "if (Number(l.xp) <= xp + 12.5) melhor = Number(l.nivel);", "12,5 antes ainda não")
edita("o Volume digitado e apagado pela conta", C, "if (l[0] || valores[i][0] !== '') return;", "if (l[0]) return;",
      "Volume digitado por cima da conta fica")
edita("o Volume apagado nao volta", C, "aba.getRange(f.l1 + i, f.c1).setFormulaR1C1(molde[0]);", "", "apagar o Volume do item traz a conta de volta")
edita("digitar no dossie le a DADOS inteira", C, "if (!treino && !missao && !notas) return;", "", "digitar no dossiê não lê a DADOS inteira")
edita("a nota e regravada mesmo igual", C, "if (caixa.getNote() !== texto) { caixa.setNote(texto); n++; }", "caixa.setNote(texto); n++;",
      "uma segunda passada não grava de novo")
edita("o onEdit nao reconhece a FICHA PESSOAL", C, "if (aba === ABA_PESSOAL_) {", "if (aba === 'OUTRA ABA') {", "marcar o grupo Lâmina Curta")
edita("o indice da aba e lido da coluna errada", C, "var IDXP_COL_CAMPO = ", "var IDXP_COL_CAMPO = 1 + ", "o IDXP_COL_CAMPO do Codigo.gs aponta")
edita("a missao do segundo bloco nao conta", C, "return k.indexOf('missões ') === 0 && toca(k); });",
      "return k === 'missões 1' && toca(k); });", "missão no segundo bloco também sobe")
edita("o Caminho escolhido nao marca o treino", C, "if (caminho) treinoPeloCaminho_(ss, dados, String(e.value || ''));", "",
      "Bastião: as 65 caixas de treino marcadas")
F = "apps-script/Ficha.gs"
edita("a cor de aviso procura um texto que a formula nao escreve", F, '"contem":"Falta Força"', '"contem":"Sem Força"',
      "cada regra de cor de aviso procura um texto")
edita("o painel de XP nasce aberto", F, '"col":[[48,72,true,1]', '"col":[[48,72,false,1]', "a aba fecha o treino em grupo de linhas aberto")
edita("a extensao nasce aberta", F, ',true,2]]}', ',false,2]]}', "a extensão é um segundo grupo de colunas")
# 07/10/2026: as travas de aviso sairam; a aba declara as caixas livres, que o onEdit nao devolve
edita("uma conta da aba passa a ser caixa livre, e deixa de voltar", F, '"livres":["', '"livres":["D20","', "a aba declara livres só o Volume de cada item")
edita("a missao da extensao nao conta", C, "return k.indexOf('missões ') === 0 && toca(k); });",
      "return (k === 'missões 1' || k === 'missões 2') && toca(k); });", "a da extensão, também sobe o nível")

print("\nPASSO 2b - o construir() inteiro, no Sheets de mentira rigoroso")
K = "regressao-construir.js"
edita("nome de metodo errado no molde (shiftColumGroupDepth)", F, ".shiftColumnGroupDepth(1)", ".shiftColumGroupDepth(1)",
      "o Apps Script não tem Range.shiftColumGroupDepth", teste=K)
edita("o grupo de dentro pedido na profundidade errada", F, "aba.getColumnGroup(g[0], g[3]).collapse()", "aba.getColumnGroup(g[0], g[3] + 1).collapse()",
      "não há grupo dessa profundidade", teste=K)
edita("o painel fecha antes da extensao", F, "var deDentro = function (a, b) { return b[3] - a[3]; };", "var deDentro = function (a, b) { return a[3] - b[3]; };",
      "a extensão fecha antes do painel", teste=K)
# 03/10/2026: desde o B35 a CARTEIRA, a primeira aba, tem uma nota de uma linha só (a da foto); a faixa de uma linha a menos
# fica vazia ali, e a montagem para logo nela, antes de chegar à matriz das outras
edita("as notas de caixa com a faixa de uma linha a menos", F, "aba.getRange(r1, c1, r2 - r1 + 1, c2 - c1 + 1).setNotes(notas);",
      "aba.getRange(r1, c1, r2 - r1, c2 - c1 + 1).setNotes(notas);", "o construir() roda inteiro", teste=K)
edita("o botao do grupo fica depois dele", F, "var ANTES = SpreadsheetApp.GroupControlTogglePosition.BEFORE;", "var ANTES = SpreadsheetApp.GroupControlTogglePosition.AFTER;",
      "com o botão em cima", teste=K)
edita("o acabar() deixa as travas de formula de uma ficha de antes", C, "=== 0) { p.remove(); n++; }", "=== 0) { n++; }",
      "tira as travas de fórmula de uma ficha montada antes", teste=K)
edita("o acabar() tira tambem a trava que o mestre criou", C, "if (String(p.getDescription()).indexOf('fórmula · ') === 0) {",
      "if (String(p.getDescription()).length) {", "tira as travas de fórmula de uma ficha montada antes", teste=K)
edita("a ficha volta a nascer com trava", C, "  var n = 0;\n  ss.getSheets().forEach(function (aba) {\n    _comRetentativa_(function () {",
      "  var n = 0;\n  ss.getSheets()[0].getRange('A1').protect();\n  ss.getSheets().forEach(function (aba) {\n    _comRetentativa_(function () {",
      "nenhuma aba nasce com trava", teste=K)
edita("a nota de caixa vai para a celula errada", F, "onde.forEach(function (o) { notas[o[0] - r1][o[1] - c1] = o[2]; });",
      "onde.forEach(function (o) { notas[0][0] = o[2]; });", "notas de caixa estão nas células delas", teste=K)
edita("a aba sai uma coluna menor que o desenho", F, "if (temC < nc) aba.insertColumnsAfter(temC, nc - temC);",
      "if (temC < nc - 1) aba.insertColumnsAfter(temC, nc - 1 - temC);", "sai da aba", teste=K)
# 01/10/2026: o construir() que vai menos vezes ao servidor. Cada atalho novo tem o defeito dele.
edita("a mesclagem em lote junta linhas que nao sao vizinhas", F, "while (j + 1 < v.length && v[j + 1] === v[j] + 1) j++;",
      "while (j + 1 < v.length && v[j + 1] <= v[j] + 3) j++;", "mescla", teste=K)
edita("a formula fica fora da gravacao dos valores", F, "    v[t[0] - 1][t[1] - 1] = t[2];\n    if (typeof t[2] === 'string' && t[2].charAt(0) === '=') formulas++;",
      "    if (typeof t[2] === 'string' && t[2].charAt(0) === '=') formulas++; else v[t[0] - 1][t[1] - 1] = t[2];", "toda fórmula do ABAS chega à célula dela", teste=K)
edita("a aba e preenchida antes de as outras nascerem", F, "      abas = ABAS.map(function (spec, i) { return criarAba_(ss, spec, i + 1); });\n      ss.deleteSheet(temp);",
      "      abas = ABAS.map(function (spec, i) { var a = criarAba_(ss, spec, i + 1); if (i === 0) montarAba_(a, spec); return a; });\n      ss.deleteSheet(temp);",
      "nenhuma fórmula é gravada antes de a aba que ela cita existir", teste=K)
edita("a nota de regra vai sempre para a caixa, nunca para o titulo", C, "return tituloOuCaixa_(acima) === 'título' ? [la, ca] : [l, c];", "return [l, c];",
      "as notas de regra da FICHA moram no título", teste=K)
edita("o construir() nunca passa a vez ao acabar()", F, "var TETO_DA_MONTAGEM_ = 300000;", "var TETO_DA_MONTAGEM_ = 300000000000;",
      "avisa que falta o acabar()", teste=K)
# 07/10/2026: a montagem que para sozinha antes de estourar os seis minutos, e o continuar()
edita("a montagem nunca para, e estoura os seis minutos", F, "if (i > de && rel.passou() + custoDaAba_(spec) > LIMITE_DA_EXECUCAO_) {",
      "if (false) {", "para ANTES de começar uma aba", teste=K)
edita("o continuar() recomeca da primeira aba, em vez de seguir", F, "      if (i < de || parou >= 0) return;", "      if (parou >= 0) return;",
      "fica igual à de uma montagem que não parou", teste=K)
edita("a montagem para sem guardar em que aba parou", F, "      props.setProperty(CHAVE_DA_MONTAGEM_, String(parou));", "",
      "guarda em que aba parou", teste=K)
edita("a montagem parada nao e esquecida quando as abas acabam", F, "    props.deleteProperty(CHAVE_DA_MONTAGEM_);\n\n    // 19/09/2026, testando no Sheets",
      "\n    // 19/09/2026, testando no Sheets", "segue de onde o anterior parou", teste=K)
edita("o acabar() roda por cima de uma montagem parada", F, "  if (parada !== null) throw new Error('a montagem das abas parou antes da aba '", "  if (false) throw new Error('a montagem das abas parou antes da aba '",
      "não roda por cima de uma montagem parada", teste=K)
edita("o construir() do zero segue a montagem parada de antes", F, "      // do zero: a montagem parada que houver deixa de valer\n      props.deleteProperty(CHAVE_DA_MONTAGEM_);",
      "", "não deixa valendo a parada de antes", teste=K)
edita("a copia das fileiras ignora as faixas de colunas e atravessa a lombada", F, "var faixasDe = function (k) { return k[5] || [[k[3] || 1, k[4] || nc]]; };",
      "var faixasDe = function (k) { return [[k[3] || 1, k[4] || nc]]; };", "corta uma mesclagem", teste=K)
edita("a lista de invocacoes leva todas as linhas a mesma ficha", C, "'&range=' + l['alvo do salto'] + '\"' + sep + nome", "'&range=H9\"' + sep + nome",
      "leva ao número da ficha dela", teste=K)
edita("a caixa de ± da invocacao esquece a vida temporaria", C, "  var fim = aplicaPasso_(tem === '' || tem === null ? max : tem, max, antes, passo);",
      "  var fim = aplicaPasso_(tem === '' || tem === null ? max : tem, max, 0, passo);", "a caixa de ± de cada ficha de invocação", teste=K)
edita("a caixa de ± da invocacao parte de zero com a vida em branco", C, "  var fim = aplicaPasso_(tem === '' || tem === null ? max : tem, max, antes, passo);",
      "  var fim = aplicaPasso_(tem, max, antes, passo);", "a caixa de ± de cada ficha de invocação", teste=K)
edita("a caixa de ± da invocacao nao se limpa", C, "  if (fim.temp !== antes) temp.setValue(fim.temp);\n  e.range.clearContent();\n  return true;",
      "  if (fim.temp !== antes) temp.setValue(fim.temp);\n  return true;", "a caixa de ± de cada ficha de invocação", teste=K)
edita("o acabar() roda em portugues, e a regra de cor quebra", F, "  ss.setSpreadsheetLocale('en_US');\n  try {\n    acabamento_(ss, feito, rel);",
      "  try {\n    acabamento_(ss, feito, rel);", "o acabar() escreve a regra de cor com a planilha em inglês", teste=K)
edita("o Caminho escolhido nao chega a FICHA PESSOAL", C, "try { fichaMexeNaPessoal_(e, idx); } catch (err) { console.log('ficha pessoal: ' + err.message); }", "",
      "escolher Bastião na FICHA passa por todos os gatilhos", teste=K)

# 01/10/2026 (B30): a nota que diz de onde vem o menu mora na caixa em que a arma e escolhida, e nao no rotulo de cima
edita("a nota da mao principal volta para o rotulo", F, '["D49","Para uma arma aparecer neste menu', '["D48","Para uma arma aparecer neste menu',
      "a caixa de escolha de cada mão nasce com a nota")
edita("a DADOS deixa de publicar a nota da arma da mao secundaria", F, '"arma da secundária"', '""', "a DADOS publica as cinco notas")
# 01/10/2026 (B31): a caixa calculada da FICHA AMALDICOADA em que alguem digitou por cima volta a ser a conta
edita("a conta digitada por cima nao volta", C, "      if (cel.getFormula() === t[2]) return;\n      cel.setFormula(t[2]);", "      if (cel.getFormula() === t[2]) return;",
      "digitar por cima de uma caixa calculada devolve a conta", teste=K)
edita("a conta volta sem aviso na tela", C, "  if (n) {\n    ss.toast(doMenu", "  if (false) {\n    ss.toast(doMenu",
      "digitar por cima de uma caixa calculada devolve a conta", teste=K)
# 07/10/2026: toda caixa calculada volta, em toda aba, e a fórmula de fábrica é escrita na pontuação do idioma da planilha
edita("a formula de fabrica volta na pontuacao do ingles, numa planilha em portugues", C,
      "  if (/^en/i.test(String(idioma || ''))) return f;\n  var out = '', i = 0, n = f.length, chaves = 0;",
      "  if (true) return f;\n  var out = '', i = 0, n = f.length, chaves = 0;", "a fórmula de fábrica vira a do idioma da planilha", teste=K)
edita("o numero com ponto fica com ponto na planilha em portugues", C, "      out += m.replace('.', ',');", "      out += m;",
      "a fórmula de fábrica vira a do idioma da planilha", teste=K)
edita("a conta da FICHA em que alguem escreve por cima nao volta", C,
      "  try { devolverConta_(e, 'FICHA'); } catch (err) { console.log('ficha, a conta: ' + err.message); }\n", "",
      "escrever por cima de uma conta da FICHA, da CARTEIRA ou da FICHA PESSOAL", teste=K)
edita("a conta da CARTEIRA em que alguem escreve por cima nao volta", C,
      "    try { devolverConta_(e, 'CARTEIRA'); } catch (err) { console.log('carteira: ' + err.message); }\n", "",
      "escrever por cima de uma conta da FICHA, da CARTEIRA ou da FICHA PESSOAL", teste=K)
edita("a conta da FICHA PESSOAL em que alguem escreve por cima nao volta", C,
      "    try { devolverConta_(e, ABA_PESSOAL_); } catch (err) { console.log('ficha pessoal, a conta: ' + err.message); }\n", "",
      "escrever por cima de uma conta da FICHA, da CARTEIRA ou da FICHA PESSOAL", teste=K)
edita("a caixa livre (a vida, o Volume do item) e devolvida como se fosse conta", C, "    if (livres[a1_(t[0], t[1])]) return;\n", "",
      "ficam como o jogador escreveu, sem aviso", teste=K)
edita("a conta que o Sheets nao entende fica em #ERROR!", C,
      "  var erradas = outras.filter(function (o) { return String(o[0].getDisplayValue()) === '#ERROR!'; });", "  var erradas = [];",
      "é gravada em inglês, com a planilha em inglês por um instante", teste=K)
edita("o religamento escreve o salto com virgula numa planilha em portugues", C,
      "  var sep = /^en/i.test(String(ss.getSpreadsheetLocale())) ? ',' : ';';", "  var sep = ',';",
      "volta com a ligação, com ponto e vírgula", teste=K)
edita("o salto da FICHA AMALDICOADA em que alguem escreve por cima fica sem a ligacao", C,
      "      if (e.range.getRow() <= LINHA_DOS_SALTOS_) ligarSaltosDe_(SpreadsheetApp.getActive(), ABA_AMALDICOADA_, DADOS_DA_AMALDICOADA_);\n", "",
      "o salto em que alguém escreve por cima volta a ser a ligação", teste=K)
edita("uma conta da FICHA PESSOAL que mora em grupo nao volta", C,
      "    livres = livres || livresDaAba_(spec);\n    if (livres[a1_(t[0], t[1])]) return;",
      "    livres = livres || livresDaAba_(spec);\n    if (livres[a1_(t[0], t[1])] || (nome === ABA_PESSOAL_ && t[1] >= 48)) return;",
      "toda conta que não é livre volta", teste=K)
edita("o onEdit nao reconhece a FICHA AMALDICOADA", C, "if (aba === ABA_AMALDICOADA_) {", "if (aba === 'OUTRA ABA DE NOME PARECIDO') {",
      "digitar por cima de uma caixa calculada devolve a conta", teste=K)
# 02/10/2026, as Habilidades (B34): o riscado das cartas acima do nível é regra de cor declarada no ABAS, que o corDeEstado_
# junta às dele; sem isso a troca de todas as regras da FICHA apaga o riscado
edita("o corDeEstado_ apaga o riscado das Habilidades", C,
      "  ((spec && spec.condicional) || []).forEach(function (c) { regras.push(regraDeCor_(ficha, c)); });\n", "",
      "risca o nome e o texto das 9 cartas", teste=K)
edita("escrever por cima da etiqueta de nivel nao devolve a conta", C,
      "    try { devolverConta_(e, 'FICHA'); } catch (err) { console.log('menu rápido: ' + err.message); }\n", "",
      "escrever por cima da etiqueta de nível devolve a conta", teste=K)
# 03/10/2026, a moldura da foto da CARTEIRA saiu de dentro da caixa (ficha-v01/moldura_foto.py): a caixa nasce vazia, e a da
# paleta se ancora na caixa que a CARTEIRA declara, e não na imagem mais alta
# (sem a caixa declarada, a caixa da paleta cai embaixo de outra arte, e o merge dela pega um pedaço de outra caixa: a
# montagem para, como pararia no Sheets)
edita("a caixa da paleta volta a se ancorar na imagem mais alta", C, "  if (spec && spec.foto) {", "  if (false) {",
      "o construir() roda inteiro", teste=K)
edita("a CARTEIRA deixa de declarar a caixa da foto", F, '"foto":[8,3,21,11]', '"foto_":[8,3,21,11]',
      "o construir() roda inteiro", teste=K)
edita("a CARTEIRA declara a caixa da foto uma linha mais curta", F, '"foto":[8,3,21,11]', '"foto":[8,3,20,11]',
      "a caixa da paleta nasce embaixo da foto", teste=K)
# 05/10/2026, a opção B das Habilidades: escolher o Caminho e a Trilha escreve as cartas pelo onEdit de verdade
edita("o onEdit esquece as cartas de Habilidades", C,
      "  try { habilidadesDaFicha_(e, idx); } catch (err) { console.log('habilidades: ' + err.message); }\n", "",
      "escreve as 9 cartas", teste=K)
edita("as cartas trocam o endereço do nome pelo do texto", C,
      "var cNm = h.indexOf('célula do nome'), cTx = h.indexOf('célula do texto'), cL",
      "var cNm = h.indexOf('célula do texto'), cTx = h.indexOf('célula do nome'), cL", "escreve as 9 cartas", teste=K)
edita("o script ignora o que está escrito nas cartas", C,
      "cartasDaFicha_(HABILIDADES_DO_LIVRO_, D.cartas, caminho, trilha, atuais)",
      "cartasDaFicha_(HABILIDADES_DO_LIVRO_, D.cartas, caminho, trilha, atuais.map(function () { return { nome: '', texto: '' }; }))",
      "o texto que o jogador escreveu fica", teste=K)
edita("a caixa não estica quando o Caminho e a Trilha mudam", C,
      "    ficha.setRowHeights(c.linha, MEDIDA_DAS_CARTAS_.caixa, alturaDaCaixa_(n.texto, MEDIDA_DAS_CARTAS_));\n", "",
      "a caixa de cada carta estica", teste=K)
edita("escrever numa carta não estica a caixa", C,
      "    try { caixaDeHabilidadeEditada_(e); } catch (err) { console.log('habilidades: ' + err.message); }\n", "",
      "escrever numa carta encolhe", teste=K)
edita("o texto do livro vai sem negrito", C, "if (n.texto !== '' && n.texto === n.livro) escreverTextoDoLivro_(",
      "if (false) escreverTextoDoLivro_(", "subtítulos do livro em negrito", teste=K)
# 05/10/2026, o nome da técnica espelha a CARTEIRA: quem escreve por cima recebe a conta, e o aviso manda escrever lá
edita("o aviso do nome da técnica esquece a CARTEIRA", C,
      "    if ((spec.da_carteira || []).indexOf(a1_(t[0], t[1])) >= 0) daCarteira = true;\n", "",
      "o aviso manda escrever na CARTEIRA", teste=K)
edita("a FICHA AMALDIÇOADA deixa de declarar a caixa que vem da CARTEIRA", F, '"da_carteira":["D12"]', '"da_carteira":[]',
      "o aviso manda escrever na CARTEIRA", teste=K)
print("\nPASSO 3 - o contra-teste: mudanca que nao muda a regra fica verde")
edita("renomear uma variavel de dentro da conta", C, "var todas = armas.filter(function (a) { return a.categoria === arma.categoria; })\n"
      "                   .every(function (a) { return marcadas[a.caixa] === true; });\n  if ((marcadas[dono.caixa] === true) !== todas) muda[dono.caixa] = todas;",
      "var inteiro = armas.filter(function (a) { return a.categoria === arma.categoria; })\n"
      "                   .every(function (a) { return marcadas[a.caixa] === true; });\n  if ((marcadas[dono.caixa] === true) !== inteiro) muda[dono.caixa] = inteiro;",
      "", espera_verde=True)

print()
print("=" * 70)
if CONTA["erros"]:
    print(f">>> {len(CONTA['erros'])} PERTURBACAO(OES) NAO FIZERAM O QUE DEVIAM: {CONTA['erros']}")
    sys.exit(1)
print(f">>> TUDO OK — {CONTA['acendeu']} perturbacoes acendem a checagem certa, e o contra-teste fica verde.")
