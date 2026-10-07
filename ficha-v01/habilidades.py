# -*- coding: utf-8 -*-
"""As Habilidades: a seção 7 da FICHA deixa de ser "Anotações" e vira cartas, uma por degrau de Caminho e uma por
entrega de Trilha. É a limpeza 27 (B34).

O desenho foi fechado com o Mizuki por estudo em 02/10/2026 (mockup/habilidades-estudo.html):
  · a forma C, as cartas, na linguagem do menu rápido ("Vai a C mesmo"): um bloco para o Caminho (cinco cartas e uma de
    anotação) e um para a Trilha (quatro cartas, as escolhas da Trilha e uma de anotação), três por fileira;
  · escrita à mão por enquanto ("nem precisa de automação AINDA (deixar preparado é o ideal), ja q o livro está sendo
    reescrito"): o jogador escreve o nome e o resumo de cada habilidade, e a forma já é a do livro, com o nível de cada
    carta fixo, para que o nome e o texto possam vir de lá depois sem refazer a seção;
  · a carta acima do nível do personagem avisa quando abre, e o que estiver escrito nela fica riscado até lá ("A e o
    texto fica 'riscado' (esqueci o nome), até desbloquear"). O aviso fica na etiqueta do nível, porque o nome é onde o
    jogador escreve: "Nível 15" quando já abriu, "Abre no 15" quando não. O riscado é regra de cor da FICHA (o
    corDeEstado_ do Codigo.gs lê a lista `condicional_gs` que este módulo declara), e só risca: não muda cor, para não
    brigar com a troca de paleta.

Os níveis vêm da tabela "Entregas por nível" do capítulo 35 (cinco degraus de Caminho nos níveis 2, 7, 15, 23 e 30;
quatro entregas de Trilha nos níveis 2, 11, 19 e 27), e são os mesmos para todos os Caminhos.

05/10/2026, as cartas com o livro (B37). O Mizuki escolheu que a carta traga o livro e que o jogador possa apagar e
escrever por cima ("B - mas dando permissão para o jogador apagar o texto e colocar oq preferir"), e no mesmo dia as pôs
numa coluna só ("faça ser apenas uma coluna ao invés de três ... n esqueça do espaçamento de uma linha entre uma carta e
outra"), com a caixa do texto esticando conforme o Caminho e a Trilha escolhidos ("Acompanha a Escolha, mas ainda tendo a
caixa retratil da descrição"). Cada carta tem a largura da seção: a etiqueta do nível e o nome numa linha, a caixa do
texto em CAIXA linhas, num grupo de linhas que abre e fecha, e uma linha vazia antes da carta seguinte.

Quem escreve é o Codigo.gs (habilidadesDaFicha_), quando o Caminho ou a Trilha mudam: o nome e o texto inteiro do
livro, como valor solto, para o jogador poder escrever por cima, e a carta que o jogador mudou fica como está, com o
livro na nota. O texto vem legível ("espaçar os paragrafos e talz"): uma linha em branco entre os parágrafos, e os
subtítulos do livro numa linha própria, em negrito (texto rico). É ele também que estica a caixa: conta as linhas do texto com a largura de cada letra da Roboto 10
(larguras-roboto-10.json, do medir_fonte.py) e divide a altura pelas linhas da caixa. Este módulo publica na DADOS_AM o
endereço do nome e do texto de cada carta (ADDRESS, que anda com a planilha) e escreve o apps-script/Habilidades.gs, com
o texto do livro (habilidades-do-livro.json, do extrair_habilidades.py) e a medida da carta. O texto mora num arquivo
de script próprio porque são 200 KB: o Ficha.gs passaria do teto de 900 KB que o conferir-ficha-xlsx guarda. A rota do
Batedor se escolhe no menu de Trilha (ficha_automatica.trilhas_do_menu), e a Rajada Marcial do Pugilista vai na carta
do nível 7 do Caminho ("o nv7 seria do caminho mesmo").

A seção cresce, e o menu rápido (limpeza 26) começa onde ela termina: o monta.py passa ao menu_rapido.trocas a linha
nova e as células desta seção, para ele não apagar nenhuma. A arte de respingos que morava no canto direito da seção
(ficha-2.png) muda para o lado direito do título, onde as cartas não chegam.
"""
import json, os, re
import indice_ficha as ix
import ficha_amaldicoada as fa
import menu_rapido as mr

NOME = "FICHA"
DA = fa.DA
NIV_CAMINHO, NIV_TRILHA = (2, 7, 15, 23, 30), (2, 11, 19, 27)
C1, CN = mr.C1, mr.CN                         # a seção inteira, de D a AT: a carta tem a largura dela
W = CN - C1 + 1
TAG, CAIXA = 3, 4                             # a etiqueta do nível tem 3 colunas ("Abre no 15"); a caixa do texto, 4 linhas
PX_COLUNA = 28                                # as colunas da FICHA têm 28 px no Sheets (as 13 do menu rápido dão 364 px)
LINHA_PX, RESPIRO_PX, MINIMA_PX = 18, 6, 21   # a linha de texto da Roboto 10 no Sheets, a folga da caixa e a linha comum
                                              # (a linha de texto é estimada: falta medir no Sheets)
ARTE = "ficha-2.png"
ESTILOS = {**mr.ESTILOS,
           "tag": [["Oswald", 10.0, mr.fp.OSSO, False, False], mr.fp.ACENTO, mr.fp._CAIXA, ["center", "center", False, 0], None]}
FONTE_CAMINHO, FONTE_TRILHA, FONTE_JUNTO = "Caminho", "Trilha", "Caminho com a Trilha"


def livro():
    """o habilidades-do-livro.json, que o extrair_habilidades.py lê do manual.txt"""
    return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "habilidades-do-livro.json"), encoding="utf-8"))


def medida():
    """a medida da carta que o Codigo.gs usa para esticar a caixa: a largura do texto, a altura da linha, e a largura
    de cada letra da Roboto 10"""
    F = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "larguras-roboto-10.json"), encoding="utf-8"))
    return {"largura": W * PX_COLUNA - RESPIRO_PX, "linha": LINHA_PX, "respiro": RESPIRO_PX, "minima": MINIMA_PX,
            "caixa": CAIXA, "media": F["media"], "larguras": F["larguras"]}


def linhas_na_carta(texto, M=None):
    """quantas linhas o texto ocupa na caixa: as palavras de cada parágrafo, uma atrás da outra, pela largura de cada
    letra. É a conta do linhasDoTexto_ do Codigo.gs, passo por passo (a soma é uma letra por vez, como lá)"""
    M = M or medida()
    def lg(t):
        x = 0.0
        for ch in t:
            x += M["larguras"].get(ch, M["media"])
        return x
    esp, n = M["larguras"][" "], 0
    for par in str(texto).split("\n"):
        n += 1
        linha = None
        for p in (x for x in par.split(" ") if x):
            w = lg(p)
            if linha is None:
                linha = w
            elif linha + esp + w <= M["largura"]:
                linha += esp + w
            else:
                n += 1
                linha = w
    return n


def linhas_do_livro(HAB=None, CAT=None):
    """a tabela que o Codigo.gs lê para escrever as cartas: [dono, fonte, nível, nome, texto, linhas, títulos]. A
    entrega de Trilha que mora na carta do Caminho (o nível 7 do Pugilista) entra como "Caminho com a Trilha", já junta
    com a habilidade do Caminho daquele nível: os dois nomes, e os dois textos, o da Trilha com um título dela"""
    HAB = HAB or livro()
    if CAT is None:
        CAT = json.load(open(os.path.join(fa.RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    M = medida()
    out = [[d, FONTE_CAMINHO, int(n), h["nome"], h["texto"], h["titulos"]] for d, por in HAB["caminhos"].items() for n, h in por.items()]
    out += [[d, FONTE_TRILHA, int(n), h["nome"], h["texto"], h["titulos"]] for d, por in HAB["trilhas"].items() for n, h in por.items()]
    for t, por in HAB["no_caminho"].items():
        cam = CAT["trilhas"][t.split(" · ")[0]]
        for n, h in por.items():
            base, curto = HAB["caminhos"][cam][n], re.split(r", | e ", h["nome"])[0]
            tit = f"{t} · {h['nome']}"
            out.append([t, FONTE_JUNTO, int(n), f"{base['nome']} · {curto}", f"{base['texto']}\n\n{tit}\n\n{h['texto']}",
                        base["titulos"] + [tit] + h["titulos"]])
    return [l[:5] + [linhas_na_carta(l[4], M), l[5]] for l in out]


class _Folha(mr._Folha):
    def estilo(self, nome):
        import json
        if nome not in self._e:
            novo = json.loads(json.dumps(ESTILOS[nome]))
            chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
            achou = next((i for i, e in enumerate(self.layout["estilos"]) if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave), None)
            if achou is None:
                self.layout["estilos"].append(novo)
                achou = len(self.layout["estilos"]) - 1
            self._e[nome] = achou
        return self._e[nome]


def arte_no_titulo(im, r7):
    """a arte de respingos ao lado do título da seção: três colunas (AQ a AS), nas três primeiras linhas da seção"""
    return dict(im, col=CN - 3, lin=r7, larg=3 * 28, alt=27 + 2 * 21, desloc_x=0, desloc_y=0)


def linha_do_titulo(ficha, n):
    """a linha do número de uma seção da FICHA (o 7 ou o 8, na coluna D)"""
    return next(ix._lc(r[0])[0] for r in ficha["celulas"] if ix._lc(r[0])[1] == C1 and r[1] in (n, float(n), str(n)))


def cartas():
    """as nove cartas de habilidade, na ordem do bloco: [(fonte, nível)]"""
    return [("Caminho", n) for n in NIV_CAMINHO] + [("Trilha", n) for n in NIV_TRILHA]


def escreve_gs(destino, linhas=None):
    """o apps-script/Habilidades.gs: o livro e a medida da carta, que o Codigo.gs lê. Gerado; não se edita"""
    linhas = linhas if linhas is not None else linhas_do_livro()
    chaves = ("dono", "fonte", "nivel", "nome", "texto", "linhas", "titulos")
    corpo = ",\n".join("  " + json.dumps(dict(zip(chaves, l)), ensure_ascii=False) for l in linhas)
    txt = ("/**\n * GERADO pelo ficha-v01/monta.py (habilidades.escreve_gs), do ficha-v01/habilidades-do-livro.json, que o\n"
           " * extrair_habilidades.py lê do manual.txt, e do ficha-v01/larguras-roboto-10.json. Não edite à mão: rode o monta.py.\n *\n"
           " * As habilidades de cada Caminho e de cada Trilha, para as cartas da seção 7 da FICHA, e a medida da carta. O\n"
           " * habilidadesDaFicha_, no Codigo.gs, escreve o nome e o texto na carta, com os títulos em negrito, e estica a\n"
           " * caixa. Fonte \"Caminho com a Trilha\" é a entrega de Trilha que mora na carta do Caminho (o nível 7 do\n"
           " * Pugilista). \"linhas\" é quantas linhas o texto ocupa, contadas pelo gerador; o regressao-delta.js confere\n"
           " * que o script conta igual.\n */\n"
           f"var HABILIDADES_DO_LIVRO_ = [\n{corpo}\n];\n\n"
           f"var MEDIDA_DAS_CARTAS_ = {json.dumps(medida(), ensure_ascii=False)};\n")
    open(destino, "w", encoding="utf-8").write(txt)
    return len(linhas), len(txt)


def trocas(layout, tr):
    """o que a limpeza muda na FICHA e na DADOS_AM. Lê a FICHA depois das limpezas de cima, e a DADOS_AM das trocas
    da Ficha Amaldiçoada (tr), que ainda não entrou no layout"""
    ficha = ix._aba(layout, NOME)
    fcel = {r[0]: r for r in ficha["celulas"]}
    r7, r8 = linha_do_titulo(ficha, 7), linha_do_titulo(ficha, 8)
    num_est, tit_est, fundo = fcel[f"D{r7}"][2], fcel[f"G{r7}"][2], fcel[f"C{r7 + 2}"][2]
    tit_fim = next(ix._lc(m.split(":")[1])[1] for m in ficha["mescladas"] if m.split(":")[0] == f"G{r7}")
    idx = ix.indice(layout)
    D, H = tr["D"], tr["H"]
    NIV = H["nível"].replace(DA, "")
    F_ = lambda k: fa._A(idx[k], "FICHA!")

    # --- a DADOS_AM: a etiqueta de cada carta pelo nível da FICHA, e o título de cada bloco pelo Caminho e pela Trilha
    lista = cartas()
    cH = D.tabela("habilidades", ["habilidade: carta", "nível da carta", "etiqueta da carta", "célula do nome", "célula do texto"],
                  [[f"{fonte} {n}", n, f'=IF({NIV}>={n},"Nível {n}","Abre no {n}")', None, None] for fonte, n in lista])
    LIVRES = [("Caminho", "Anotações"), ("Trilha", "Escolhas da Trilha"), ("Trilha", "Anotações")]
    cL = D.tabela("habilidades_livres", ["habilidade livre: carta", "célula do texto livre"],
                  [[f"{b} · {n}", None] for b, n in LIVRES])
    escolha = lambda k: f'IF(OR({F_(k)}="",LEFT({F_(k)},7)="Escolha"),"","  ·  "&UPPER({F_(k)}))'
    cT = D.tabela("habilidades_titulos", ["habilidades: título", "texto do título"],
                  [["Caminho", f'="CAMINHO"&{escolha("caminho")}&"  ·  CINCO NÍVEIS"'],
                   ["Trilha", f'="TRILHA"&{escolha("trilha")}&"  ·  QUATRO NÍVEIS"']])
    etiqueta = lambda i: f"={DA}${fa.L(cH + 2)}${2 + i}"
    titulo = lambda i: f"={DA}${fa.L(cT + 1)}${2 + i}"

    # --- a seção na FICHA
    f = _Folha(layout)
    grupos, riscar, pos = [], [], {}
    f.cel[f"D{r7}"] = (7, num_est)
    f.mesclas.append(f"D{r7}:F{r7 + 1}")
    f.cel[f"G{r7}"] = ("HABILIDADES", tit_est)
    f.mesclas.append(f"G{r7}:{fa.L(tit_fim)}{r7}")
    r = r7 + 3
    a_secao = r

    def carta(r, i):
        """a carta de uma habilidade: a etiqueta do nível e o nome numa linha, e a caixa do texto embaixo, que o
        Codigo.gs escreve do livro e o jogador pode trocar"""
        f.add("tag", C1, r, C1 + TAG - 1, r, etiqueta(i))
        nome = f.add("nm", C1 + TAG, r, CN, r, None)
        texto = f.add("desc", C1, r + 1, CN, r + CAIXA, None)
        pos[i] = (nome, texto)
        riscar.append({"faixas": [f"{nome}:{fa._a1(CN, r)}", f"{texto}:{fa._a1(CN, r + CAIXA)}"],
                       "formula": f'=LEFT(${fa.L(C1)}${r},4)="Abre"', "riscado": True})

    def livre(r, rotulo):
        f.add("cab", C1, r, CN, r, rotulo)
        livres.append(f.add("desc", C1, r + 1, CN, r + CAIXA, None))

    cheias, livres = [], []
    def bloco(id_, i_titulo, itens):
        nonlocal r
        cab = r
        f.add("cab", C1, cab, CN, cab, titulo(i_titulo))
        r = cab + 1
        for k, it in enumerate(itens):
            if isinstance(it, int):
                carta(r, it)
                cheias.append(r)
            else:
                livre(r, it)
            # a caixa do texto é um grupo de linhas: o + fica na linha do nome, e todas nascem abertas
            grupos.append([r + 1, r + CAIXA, False])
            r += 1 + CAIXA
            if k + 1 < len(itens):
                r += 1                          # uma linha vazia entre uma carta e outra
        r += 1
        grupos.append([cab + 1, r - 1, False])

    nc = len(NIV_CAMINHO)
    bloco("caminho", 0, list(range(nc)) + [LIVRES[0][1]])
    bloco("trilha", 1, list(range(nc, len(lista))) + [n for b, n in LIVRES[1:]])
    fim = r
    grupos.append([a_secao, fim - 1, False])
    for i, (cn, ct) in pos.items():
        D.poe(cH + 3, 2 + i, ix.FORMULA.format(c=cn))
        D.poe(cH + 4, 2 + i, ix.FORMULA.format(c=ct))
    for i, ct in enumerate(livres):
        D.poe(cL + 1, 2 + i, ix.FORMULA.format(c=ct))
    prof = lambda g: sum(1 for o in grupos if o[0] <= g[0] and g[1] <= o[1])
    for a_ in grupos:
        for b_ in grupos:
            if a_ is not b_ and b_[0] == a_[1] + 1 and prof(a_) == prof(b_):
                raise SystemExit(f"habilidades: os grupos {a_[:2]} e {b_[:2]} estao colados")

    # a arte de respingos, ao lado do título: três colunas, as três primeiras linhas da seção
    arte = None
    for im in ficha.get("imagens", []):
        if im["arquivo"] == ARTE:
            arte = arte_no_titulo(im, r7)

    # o fundo das células vazias da seção, como o resto da FICHA
    dentro = set()
    for m in f.mesclas:
        (l1, c1), (l2, c2) = (ix._lc(x) for x in m.split(":"))
        dentro |= {(l, c) for l in range(l1, l2 + 1) for c in range(c1, c2 + 1)}
    dentro |= {ix._lc(c) for c in f.cel}
    for l in range(r7, fim):
        for c in range(3, ficha["colunas"]):
            if (l, c) not in dentro:
                f.cel[fa._a1(c, l)] = (None, fundo)

    # o que sai: a seção 7 de hoje (as caixas, as mesclagens, as alturas e a mesclagem da arte)
    no_velho = lambda c: r7 <= ix._lc(c)[0] < r8 and ix._lc(c)[1] >= 3
    sai = {c for c in fcel if no_velho(c)} - set(f.cel)
    mesc_sai = [m for m in ficha["mescladas"] if no_velho(m.split(":")[0])]
    copias = [[cheias[0], cheias[0] + CAIXA, cheias[1:], C1, CN]] if len(cheias) > 1 else []
    return {"r7": r7, "r8_velho": r8, "fim": fim, "celulas": {NOME: {c: (v[0], c) for c, v in f.cel.items()}},
            "_estilos": f.cel, "sai": sai, "mescladas_sai": {NOME: mesc_sai}, "mescladas": {NOME: f.mesclas},
            "grupos": grupos, "riscar": riscar, "arte": arte, "copias": copias, "cartas": lista,
            "tabela": cH, "titulos": cT}


def aplica(layout, tm):
    """põe a seção na FICHA. Devolve quantas células mudaram. Roda antes do menu_rapido.aplica"""
    ficha = ix._aba(layout, NOME)
    ficha["celulas"] = [c for c in ficha["celulas"] if c[0] not in tm["sai"]]
    por = {c[0]: c for c in ficha["celulas"]}
    n = 0
    for coord, (v, est) in tm["_estilos"].items():
        if coord in por:
            por[coord][1], por[coord][2] = v, est
        else:
            ficha["celulas"].append([coord, v, est])
        n += 1
    ficha["mescladas"] = [m for m in ficha["mescladas"] if m not in tm["mescladas_sai"][NOME]] + tm["mescladas"][NOME]
    # as alturas: o título da seção fica com a do título, e as linhas finas de hoje (5,25) saem; as que estão depois da
    # seção nova são da seção 8 de hoje, e o menu rápido cuida delas
    ficha["linhas_alt"] = ([a for a in ficha["linhas_alt"] if a[0] < tm["r7"]] + [[tm["r7"], 27.0]] +
                           [a for a in ficha["linhas_alt"] if a[0] >= tm["fim"]])
    ficha["grupos"] = {"linhas": (ficha.get("grupos") or {}).get("linhas", []) + tm["grupos"], "colunas": []}
    # as etiquetas e os títulos são conta: ficam fora da trava (moram em linha de grupo), e o onEdit devolve a conta
    ficha["sem_trava"] = ficha.get("sem_trava", []) + [[tm["r7"], tm["fim"] - 1]]
    ficha["condicional_gs"] = ficha.get("condicional_gs", []) + tm["riscar"]
    ficha["copias"] = ficha.get("copias", []) + tm["copias"]
    if tm["arte"]:
        ficha["imagens"] = [tm["arte"] if im["arquivo"] == ARTE else im for im in ficha["imagens"]]
    return n
