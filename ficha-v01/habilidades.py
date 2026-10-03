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

A seção cresce, e o menu rápido (limpeza 26) começa onde ela termina: o monta.py passa ao menu_rapido.trocas a linha
nova e as células desta seção, para ele não apagar nenhuma. A arte de respingos que morava no canto direito da seção
(ficha-2.png) muda para o lado direito do título, onde as cartas não chegam.
"""
import indice_ficha as ix
import ficha_amaldicoada as fa
import menu_rapido as mr

NOME = "FICHA"
DA = fa.DA
NIV_CAMINHO, NIV_TRILHA = (2, 7, 15, 23, 30), (2, 11, 19, 27)
POR, W, X = mr.POR, mr.W, mr.X                # as cartas do menu rápido: três por fileira, 13 colunas
C1, CN = mr.C1, mr.CN
TAG, TX = 3, 6                                # a etiqueta do nível tem 3 colunas ("Abre no 15"); o texto, 6 linhas
ARTE = "ficha-2.png"
ESTILOS = {**mr.ESTILOS,
           "tag": [["Oswald", 10.0, mr.fp.OSSO, False, False], mr.fp.ACENTO, mr.fp._CAIXA, ["center", "center", False, 0], None]}


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
    cH = D.tabela("habilidades", ["habilidade: carta", "nível da carta", "etiqueta da carta"],
                  [[f"{fonte} {n}", n, f'=IF({NIV}>={n},"Nível {n}","Abre no {n}")'] for fonte, n in lista])
    escolha = lambda k: f'IF(OR({F_(k)}="",LEFT({F_(k)},7)="Escolha"),"","  ·  "&UPPER({F_(k)}))'
    cT = D.tabela("habilidades_titulos", ["habilidades: título", "texto do título"],
                  [["Caminho", f'="CAMINHO"&{escolha("caminho")}&"  ·  CINCO DEGRAUS"'],
                   ["Trilha", f'="TRILHA"&{escolha("trilha")}&"  ·  QUATRO ENTREGAS"']])
    etiqueta = lambda i: f"={DA}${fa.L(cH + 2)}${2 + i}"
    titulo = lambda i: f"={DA}${fa.L(cT + 1)}${2 + i}"

    # --- a seção na FICHA
    f = _Folha(layout)
    grupos, riscar = [], []
    f.cel[f"D{r7}"] = (7, num_est)
    f.mesclas.append(f"D{r7}:F{r7 + 1}")
    f.cel[f"G{r7}"] = ("HABILIDADES", tit_est)
    f.mesclas.append(f"G{r7}:{fa.L(tit_fim)}{r7}")
    r = r7 + 3
    a_secao = r

    def carta(r, x, i):
        """a carta de uma habilidade: a etiqueta do nível, o nome e o texto, os dois escritos pelo jogador"""
        tag = f.add("tag", x, r, x + TAG - 1, r, etiqueta(i))
        nome = f.add("nm", x + TAG, r, x + W - 1, r, None)
        texto = f.add("desc", x, r + 1, x + W - 1, r + TX, None)
        riscar.append({"faixas": [f"{nome}:{fa._a1(x + W - 1, r)}", f"{texto}:{fa._a1(x + W - 1, r + TX)}"],
                       "formula": f'=LEFT(${fa.L(x)}${r},4)="Abre"', "riscado": True})

    def livre(r, x, rotulo):
        f.add("cab", x, r, x + W - 1, r, rotulo)
        f.add("desc", x, r + 1, x + W - 1, r + TX, None)

    cheias = []
    def bloco(id_, i_titulo, itens):
        nonlocal r
        cab = r
        f.add("cab", C1, cab, CN, cab, titulo(i_titulo))
        r = cab + 1
        fil = -(-len(itens) // POR)
        for fi in range(fil):
            fileira = itens[fi * POR:(fi + 1) * POR]
            for j, it in enumerate(fileira):
                if isinstance(it, int):
                    carta(r, X[j], it)
                else:
                    livre(r, X[j], it)
            if all(isinstance(it, int) for it in fileira) and len(fileira) == POR:
                cheias.append(r)
            # o texto da fileira é um grupo; o + fica na linha das etiquetas, e só a primeira fileira nasce aberta
            grupos.append([r + 1, r + TX, fi > 0])
            r += 1 + TX
            if fi + 1 < fil:
                r += 1
        r += 1
        grupos.append([cab + 1, r - 1, False])

    nc = len(NIV_CAMINHO)
    bloco("caminho", 0, list(range(nc)) + ["Anotações"])
    bloco("trilha", 1, list(range(nc, len(lista))) + ["Escolhas da Trilha", "Anotações"])
    fim = r
    grupos.append([a_secao, fim - 1, False])
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
    copias = [[cheias[0], cheias[0] + TX, cheias[1:], C1, CN]] if len(cheias) > 1 else []
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
