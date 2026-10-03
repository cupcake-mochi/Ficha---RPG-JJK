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
           "apps-script/Ficha.gs"]
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
edita("uma formula do painel de XP volta a ser travada", F, '"protegidas":["', '"protegidas":["BA15:BA64","',
      "nenhuma faixa travada encosta em coluna ou linha de grupo")
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
edita("a trava bloqueia em vez de avisar", C, "p.setDescription('fórmula · ' + nome + '!' + a1);\n      p.setWarningOnly(true);",
      "p.setDescription('fórmula · ' + nome + '!' + a1);", "travadas em", teste=K)
edita("a nota de caixa vai para a celula errada", F, "onde.forEach(function (o) { notas[o[0] - r1][o[1] - c1] = o[2]; });",
      "onde.forEach(function (o) { notas[0][0] = o[2]; });", "notas de caixa estão nas células delas", teste=K)
edita("a aba sai uma coluna menor que o desenho", F, "if (temC < nc) aba.insertColumnsAfter(temC, nc - temC);",
      "if (temC < nc - 1) aba.insertColumnsAfter(temC, nc - 1 - temC);", "sai da aba", teste=K)
# 01/10/2026: o construir() que vai menos vezes ao servidor. Cada atalho novo tem o defeito dele.
edita("a trava por faixa junta colunas que nao sao vizinhas", C, "faixas[k][3] === r[1] - 1) { faixas[k][3] = r[3]; return; }",
      "faixas[k][3] <= r[1] - 1) { faixas[k][3] = r[3]; return; }", "nenhuma célula sem fórmula está travada", teste=K)
edita("a trava por faixa esquece a ultima celula da coluna", C, "corridas.push([v[i], Number(c), v[j], Number(c)]);",
      "corridas.push([v[i], Number(c), Math.max(v[i], v[j] - 1), Number(c)]);", "fórmulas estão travadas com aviso", teste=K)
edita("a mesclagem em lote junta linhas que nao sao vizinhas", F, "while (j + 1 < v.length && v[j + 1] === v[j] + 1) j++;",
      "while (j + 1 < v.length && v[j + 1] <= v[j] + 3) j++;", "mescla", teste=K)
edita("a formula fica fora da gravacao dos valores", F, "    v[t[0] - 1][t[1] - 1] = t[2];\n    if (typeof t[2] === 'string' && t[2].charAt(0) === '=') formulas++;",
      "    if (typeof t[2] === 'string' && t[2].charAt(0) === '=') formulas++; else v[t[0] - 1][t[1] - 1] = t[2];", "toda fórmula do ABAS chega à célula dela", teste=K)
edita("a aba e preenchida antes de as outras nascerem", F, "    var abas = ABAS.map(function (spec, i) { return criarAba_(ss, spec, i + 1); });\n    ss.deleteSheet(temp);",
      "    var abas = ABAS.map(function (spec, i) { var a = criarAba_(ss, spec, i + 1); if (i === 0) montarAba_(a, spec); return a; });\n    ss.deleteSheet(temp);",
      "nenhuma fórmula é gravada antes de a aba que ela cita existir", teste=K)
edita("a nota de regra vai sempre para a caixa, nunca para o titulo", C, "return tituloOuCaixa_(acima) === 'título' ? [la, ca] : [l, c];", "return [l, c];",
      "as notas de regra da FICHA moram no título", teste=K)
edita("o construir() nunca passa a vez ao acabar()", F, "var TETO_DA_MONTAGEM_ = 250000;", "var TETO_DA_MONTAGEM_ = 250000000000;",
      "avisa que falta o acabar()", teste=K)
edita("o acabar() duplica as travas", C, "    semAsVelhas(aba);\n    var celulas = [];", "    var celulas = [];", "rodar o acabar() numa ficha pronta não muda nada", teste=K)
edita("o acabar() roda em portugues, e a regra de cor quebra", F, "  ss.setSpreadsheetLocale('en_US');\n  try {\n    acabamento_(ss, feito, rel);",
      "  try {\n    acabamento_(ss, feito, rel);", "o acabar() escreve a regra de cor com a planilha em inglês", teste=K)
edita("o Caminho escolhido nao chega a FICHA PESSOAL", C, "try { fichaMexeNaPessoal_(e, idx); } catch (err) { console.log('ficha pessoal: ' + err.message); }", "",
      "escolher Bastião na FICHA passa por todos os gatilhos", teste=K)

# 01/10/2026 (B30): a nota que diz de onde vem o menu mora na caixa em que a arma e escolhida, e nao no rotulo de cima
edita("a nota da mao principal volta para o rotulo", F, '["D41","Para uma arma aparecer neste menu', '["D40","Para uma arma aparecer neste menu',
      "a caixa de escolha de cada mão nasce com a nota")
edita("a DADOS deixa de publicar a nota da arma da mao secundaria", F, '"arma da secundária"', '""', "a DADOS publica as cinco notas")
# 01/10/2026 (B31): a caixa calculada da FICHA AMALDICOADA em que alguem digitou por cima volta a ser a conta
edita("a conta digitada por cima nao volta", C, "    cel.setFormula(t[2]);\n    n++;", "    n++;", "digitar por cima de uma caixa calculada devolve a conta", teste=K)
edita("a conta volta sem aviso na tela", C, "  if (n) {\n    SpreadsheetApp.getActive().toast(", "  if (false) {\n    SpreadsheetApp.getActive().toast(",
      "digitar por cima de uma caixa calculada devolve a conta", teste=K)
edita("o onEdit regrava formula que nao vale em todo idioma", C, "var REFERENCIA_PURA_ = /^=(?:'[^']+'|[A-Z_]+)!\\$?[A-Z]+\\$?\\d+$/;", "var REFERENCIA_PURA_ = /^=/;",
      "não é regravada pelo script", teste=K)
edita("o onEdit nao reconhece a FICHA AMALDICOADA", C, "if (aba === ABA_AMALDICOADA_) {", "if (aba === 'OUTRA ABA DE NOME PARECIDO') {",
      "digitar por cima de uma caixa calculada devolve a conta", teste=K)
# 02/10/2026, as Habilidades (B34): o riscado das cartas acima do nível é regra de cor declarada no ABAS, que o corDeEstado_
# junta às dele; sem isso a troca de todas as regras da FICHA apaga o riscado
edita("o corDeEstado_ apaga o riscado das Habilidades", C,
      "  ((spec && spec.condicional) || []).forEach(function (c) { regras.push(regraDeCor_(ficha, c)); });\n", "",
      "risca o nome e o texto das 9 cartas", teste=K)
edita("escrever por cima da etiqueta de nivel nao devolve a conta", C,
      "  if (dentroDeSemTrava_('FICHA', e.range)) {", "  if (false) {", "escrever por cima da etiqueta de nível devolve a conta", teste=K)
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
