# -*- coding: utf-8 -*-
"""O menu rápido: a seção 8 da FICHA deixa de ser digitada e passa a mostrar o que está na FICHA AMALDIÇOADA. É a
limpeza 26.

O desenho foi fechado com o Mizuki por estudo, em cinco rodadas, em 02/10/2026 (mockup/menu-rapido-estudo.html):
  · vale para todo mundo ("B"), e a Ficha Amaldiçoada muda conforme a Origem para o menu ler a mesma coisa em qualquer
    rota (ficha_amaldicoada.py, as quatro rotas);
  · mini-cartas, três por fileira, de 13 colunas ("três por fileira");
  · um grupo que fecha para cada bloco, um para cada par de fileiras empilhadas, e um para a descrição de cada fileira
    ("colocar menu retratil para cada grupo de 2 feitiços é obrigatorio");
  · a Ficha Amaldiçoada mostra a conta, e o menu mostra o que o jogador escreveu ("a ficha amaldiçoada apresenta o
    calculo, menu rapido as informações do jogador"): a carta de feitiço traz o "Como é", e a peça criada vai descrita
    nele; a de Passiva e a de aptidão, o "seu texto", ou o do livro quando ele está vazio.

As alturas das caixas de texto são as que fazem caber o que aparece na caixa de origem: 7 linhas para o "Como é" do
feitiço (476 px e 5 linhas lá, 364 px aqui), 5 para a Técnica Máxima e o Domínio, em carta da largura da seção (a caixa
de lá ocupa a aba inteira), 5 para a Passiva e 6 para a aptidão (o texto do livro, quando o jogador não escreve).

Nada aqui se digita: toda caixa é uma referência a uma célula da DADOS_AM, onde a lista é montada sem buraco (o feitiço
de nome apagado some, e o de baixo sobe). As linhas do menu ficam fora da trava de fórmula do script (trava em linha de
grupo faz o Sheets avisar quem clica no +), e quem escrever por cima recebe a conta de volta pelo onEdit.
"""
import indice_ficha as ix
import ficha_pessoal as fp
import ficha_amaldicoada as fa

NOME = "FICHA"
DA = fa.DA
POR, W, X = 3, 13, (4, 19, 34)               # três cartas de 13 colunas, de D a AT, com duas colunas de folga entre elas
NUM = (3, 4, 6)                              # a linha de números: PE, Forma e como resolve
ALT = {"feitico": 7, "largo": 5, "passiva": 5, "aptidao": 6}
CAP = {"feiticos": fa.N_FEITICOS, "passivas": 2 + fa.PAGAS + fa.DO_LEQUE, "aptidoes": 2 + fa.N_APT}
C1, CN = 4, 46                               # D e AT

_C = fp._CAIXA
ESTILOS = {
    "cab":   [["Oswald", 9.0, fp.OSSO, False, False], fp.ALTO, _C, ["left", "center", False, 0], None],
    "lote":  [["Oswald", 9.0, fp.FRACO, False, False], fp.PAPEL, _C, ["left", "center", False, 0], None],
    "cl":    [["Oswald", 11.0, fp.OSSO, False, False], fp.ACENTO, _C, ["center", "center", False, 0], None],
    "nm":    [["Castoro", 11.0, fp.OSSO, False, False], fp.ACENTO, _C, ["left", "center", False, 0], None],
    "vl":    [["Roboto", 9.0, fp.OSSO, False, False], fp.PAINEL, _C, ["center", "center", False, 0], None],
    "desc":  [["Roboto", 10.0, fp.TEXTO, False, False], fp.PAPEL, _C, ["left", "top", True, 0], None],
}


class _Folha:
    """as caixas novas da seção, com o estilo de cada uma no layout"""
    def __init__(self, layout):
        self.layout, self.cel, self.mesclas, self._e = layout, {}, [], {}

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

    def add(self, estilo, c1, l1, c2, l2, valor=None):
        coord = fa._a1(c1, l1)
        self.cel[coord] = (valor, self.estilo(estilo) if isinstance(estilo, str) else estilo)
        if (c1, l1) != (c2, l2):
            self.mesclas.append(f"{coord}:{fa._a1(c2, l2)}")
        return coord


def trocas(layout, tr, r0=None, guarda=frozenset()):
    """o que a limpeza muda na FICHA, na DADOS e na DADOS_AM. Lê a FICHA depois das limpezas de cima, e a DADOS_AM
    das trocas da Ficha Amaldiçoada (tr), que ainda não entrou no layout.
    02/10/2026: a seção 7 virou as Habilidades (limpeza 27) e cresceu. `r0` é a linha onde o menu começa agora (o fim
    dela), e `guarda` são as células dela, que o menu não apaga mesmo estando nas linhas da seção 8 de hoje. O estilo
    do título e do fundo continua sendo lido da seção 8 de hoje."""
    ficha, dados = ix._aba(layout, NOME), ix._aba(layout, "DADOS")
    fcel = {r[0]: r for r in ficha["celulas"]}
    # a seção 8 de hoje: a linha do número dela, e o que está daí para baixo
    r8 = next(ix._lc(c)[0] for c, r in fcel.items() if ix._lc(c)[1] == C1 and r[1] in (8, 8.0, "8"))
    r0 = r8 if r0 is None else r0
    fim_velho = ficha["linhas"]
    num_est, tit_est, fundo = fcel[f"D{r8}"][2], fcel[f"G{r8}"][2], fcel[f"C{r8 + 2}"][2]
    tit_fim = next(ix._lc(m.split(":")[1])[1] for m in ficha["mescladas"] if m.split(":")[0] == f"G{r8}")
    G, D, R = tr["G"], tr["D"], tr["R"]
    AM = fa.AM
    ROTA, rot = tr["ROTA"], tr["rotulo"]
    col = tr["col"]

    # --- as tabelas do menu na DADOS_AM: a lista sem buraco de cada bloco
    FEIT = lambda k: fa._faixa(col[k], 2, col[k], 1 + fa.N_FEITICOS)          # só as linhas de feitiço, sem as de Liberação
    lin_lib = lambda k, i: fa._abs(col[k], 2 + fa.N_FEITICOS + i)
    cF = D.prox
    mf = lambda k, n: f"${fa.L(cF + k)}{n}"
    campos = ["classe", "nome", "pe", "forma", "resolve", "como"]
    D.tabela("menu_feiticos", ["menu: feitiço", "lugar na conta"] + [f"menu: {k}" for k in campos],
             [[k + 1, (lambda n, k=k: f"=IFERROR(MATCH({k + 1},{FEIT('ordem')},0),0)")] +
              [(lambda n, c=c: f'=IF({mf(1, n)}=0,"",INDEX({FEIT(c)},{mf(1, n)}))') for c in campos]
              for k in range(CAP["feiticos"])])
    cL = D.prox
    D.tabela("menu_libs", ["menu: liberação"] + [f"menu da liberação: {k}" for k in campos],
             [[i + 1] + [f'=IF({lin_lib("tem", i)}=0,"",{lin_lib(c, i)})' for c in campos] for i in range(fa.N_LIB)])
    # a Técnica Máxima e o Domínio, em carta larga
    dom, maxc = R["dominio"], tr["H"]["maior classe"].replace(DA, "")
    deg = tr["H"]["degrau do domínio"].replace(DA, "")
    nomes_d = [d["degrau"] for d in dom["degraus"]]
    formas = D.faixa("formas")
    cM = D.prox
    D.tabela("menu_maximas", ["menu: carta larga", "nome dela", "pe dela", "forma dela", "resolve dela", "como é dela"],
             [["Técnica Máxima", f'={fa._A(G["tm_nome"], AM)}&""',
               # a Forma nasce escolhida na aba: sem nome, a carta fica vazia, como a de feitiço
               # antes do nível dela, a aba mostra "—" no PE, e o menu também
               f'=IF({fa._A(G["tm_nome"], AM)}="","",IF(ISNUMBER({fa._A(G["tm_pe"], AM)}),{fa._A(G["tm_pe"], AM)}&" PE",{fa._A(G["tm_pe"], AM)}&""))',
               f'=IF({fa._A(G["tm_nome"], AM)}="","",{fa._A(G["tm_forma"], AM)}&"")',
               f'=IF({fa._A(G["tm_nome"], AM)}="","",IFERROR(VLOOKUP({fa._A(G["tm_forma"], AM)},{formas},8,FALSE),""))',
               f'={fa._A(f"D{G['tm_como'] + 1}", AM)}&""'],
              ["Domínio",
               f'=IF({ROTA}<>1,"Esta rota não tem Expansão de Domínio",{fa._A(G["dom_nome"], AM)}&"")',
               f'=IF(OR({ROTA}<>1,{deg}=""),"",IF({deg}="{nomes_d[2]}",{dom["pe_por_classe_sem_barreira"]},{dom["pe_por_classe"]})*{maxc}&" PE")',
               f'=IF({ROTA}<>1,"",{deg})',
               f'=IF(OR({ROTA}<>1,{deg}=""),"",IF({deg}="{nomes_d[0]}","Rola","Acontece"))',
               f'=IF({ROTA}<>1,"",{fa._A(f"D{G['dom_como'] + 1}", AM)}&"")']])
    # as Passivas: a Livre e a Regra Própria, da Técnica, e as doze cartas sem buraco
    cP = D.T["carta_passiva"][0]
    PAS = D.faixa("passivas")          # o resumo do livro (ficha_amaldicoada.resumo): inteiro se cabe na caixa, a primeira frase se não
    PCOL = lambda k: fa._faixa(cP + k, 2, cP + k, 1 + fa.PAGAS + fa.DO_LEQUE)
    reg_txt, livre_txt = fa._A(f"D{G['regra_propria'] + 1}", AM), fa._A(f"L{G['descricao'] + 4}", AM)
    cPm = D.prox
    mp = lambda k, n: f"${fa.L(cPm + k)}{n}"
    livro = lambda faz, seu: f'IF({seu}<>"",{seu},IF({faz}<>"","Do livro: "&{faz},""))'
    linhas_p = [["Passiva Livre", 0, "Livre", "Passiva Livre", f'={livre_txt}&""'],
                ["Regra Própria", 0, f'=IF(N({fa._A(G["cp_regra"], AM)})=0,"—","CP "&{fa._A(G["cp_regra"], AM)})', "Regra Própria",
                 f'=IF({reg_txt}="","Esta técnica não tem Regra Própria",{reg_txt}&"")']]
    linhas_p += [[f"Passiva {k + 1}", (lambda n, k=k: f"=IFERROR(MATCH({k + 1},{PCOL(8)},0),0)"),
                  (lambda n: f'=IF({mp(1, n)}=0,"",IF(INDEX({PCOL(2)},{mp(1, n)})=0,"","CP "&INDEX({PCOL(2)},{mp(1, n)})))'),
                  (lambda n: f'=IF({mp(1, n)}=0,"",INDEX({PCOL(1)},{mp(1, n)}))'),
                  (lambda n: f'=IF({mp(1, n)}=0,"",' + livro(f'IFERROR(VLOOKUP(INDEX({PCOL(1)},{mp(1, n)}),{PAS},7,FALSE),"")',
                                                             f"INDEX({PCOL(7)},{mp(1, n)})") + ")")]
                 for k in range(fa.PAGAS + fa.DO_LEQUE)]
    D.tabela("menu_passivas", ["menu: passiva", "lugar da passiva", "classe passiva no menu", "passiva no menu", "texto da passiva no menu"], linhas_p)
    # as aptidões: as duas de graça (o texto é o do livro), e as doze cartas sem buraco
    cA = D.T["carta_aptidao"][0]
    ACOL = lambda k: fa._faixa(cA + k, 2, cA + k, 1 + fa.N_APT)
    APT = D.faixa("aptidoes")
    cAm = D.prox
    ma = lambda k, n: f"${fa.L(cAm + k)}{n}"
    linhas_a = [[f"De graça {i + 1}", 0, "—", f"={rot(f'graça {i + 1}').replace(DA, '')}",
                 (lambda n: f'="Do livro: "&IFERROR(VLOOKUP({ma(3, n)},{APT},10,FALSE),"")')] for i in range(2)]
    linhas_a += [[f"Aptidão {k + 1}", (lambda n, k=k: f"=IFERROR(MATCH({k + 1},{ACOL(7)},0),0)"),
                  (lambda n: f'=IF({ma(1, n)}=0,"",INDEX({ACOL(3)},{ma(1, n)}))'),
                  (lambda n: f'=IF({ma(1, n)}=0,"",INDEX({ACOL(1)},{ma(1, n)}))'),
                  (lambda n: f'=IF({ma(1, n)}=0,"",' + livro(f'IFERROR(VLOOKUP(INDEX({ACOL(1)},{ma(1, n)}),{APT},10,FALSE),"")',
                                                             f"INDEX({ACOL(6)},{ma(1, n)})") + ")")]
                 for k in range(fa.N_APT)]
    D.tabela("menu_aptidoes", ["menu: aptidão", "lugar da aptidão", "classe passiva da aptidão no menu", "aptidão no menu",
                               "texto da aptidão no menu"], linhas_a)
    # os títulos e as legendas, pela rota
    R_ = lambda k: rot(k).replace(DA, "")
    H = tr["H"]
    n_feit = H["feitiços montados"].replace(DA, "")
    rotulos = [
        ("título", f'="MENU RÁPIDO · "&UPPER({R_("feitiços")})&", PASSIVAS E "&UPPER({R_("aptidões")})'),
        ("feitiços", f'=UPPER({R_("feitiços")})&"  ·  "&{n_feit}&" de {CAP["feiticos"]}"'),
        ("máximas", f'=UPPER({R_("liberação")})&", "&UPPER({R_("técnica máxima")})&IF({ROTA}=1," E DOMÍNIO","")'),
        ("passivas", f'="PASSIVAS  ·  "&(COUNTIF({fa._faixa(cPm + 3, 2, cPm + 3, 1 + len(linhas_p))},"?*")-2)&" de {fa.PAGAS + fa.DO_LEQUE}, '
                     f'mais a Livre e a Regra Própria"'),
        ("aptidões", f'=UPPER({R_("aptidões")})&"  ·  "&COUNTIF({fa._faixa(cAm + 3, 4, cAm + 3, 1 + len(linhas_a))},"?*")&" de {fa.N_APT}, '
                     f'mais as duas de graça"'),
        ("tag lib", f'=IF({ROTA}>=3,"Rup","Lib")'), ("tag tm", f'=IF({ROTA}=1,"Máx",IF({ROTA}=2,"Auge","Ōgi"))'), ("tag dom", '="Dom"'),
    ]
    for i in range(1, CAP["feiticos"] // POR):
        if i % 2 == 0:
            rotulos.append((f"par {i}", f'=UPPER({R_("feitiços")})&" {i * POR + 1} A {min(CAP["feiticos"], (i + 2) * POR)}"'))
    for nome_b, cap in (("passivas", CAP["passivas"]), ("aptidões", CAP["aptidoes"])):
        for i in range(2, -(-cap // POR), 2):
            r_txt = f'"PASSIVAS' if nome_b == "passivas" else f'UPPER({R_("aptidões")})&"'
            rotulos.append((f"par {nome_b} {i}", f'={r_txt} {i * POR + 1} A {min(cap, (i + 2) * POR)}"'))
    cR = D.prox
    D.tabela("menu_rotulos", ["menu: rótulo", "texto do rótulo"], [[k, v] for k, v in rotulos])
    TXT = {k: f"={DA}${fa.L(cR + 1)}${2 + i}" for i, (k, _) in enumerate(rotulos)}
    ref = lambda c0, linha, k: f"={DA}${fa.L(c0 + k)}${2 + linha}"

    # --- a seção na FICHA
    f = _Folha(layout)
    grupos = []
    cheias = {}                    # as fileiras de três cartas, pela altura: as cópias da primeira (ver o aplica)
    r = r0
    f.cel[f"D{r}"] = (8, num_est)
    f.mesclas.append(f"D{r}:F{r + 1}")
    f.cel[f"G{r}"] = (TXT["título"], tit_est)
    f.mesclas.append(f"G{r}:{fa.L(tit_fim)}{r}")
    r += 3
    a_secao = r

    def carta(r, x, lc, linha, tag=None, alt=ALT["feitico"]):
        """a carta de feitiço: a Classe e o nome, o PE, a Forma e como resolve, e o "Como é" """
        a = NUM[0]
        f.add("cl", x, r, x + 1, r, TXT[tag] if tag else ref(lc, linha, 2))
        f.add("nm", x + 2, r, x + W - 1, r, ref(lc, linha, 3 if not tag else 2))
        k = (lambda j: j) if tag else (lambda j: j + 1)       # a tabela das Liberações não tem a coluna do lugar
        f.add("vl", x, r + 1, x + a - 1, r + 1, ref(lc, linha, k(3)))
        f.add("vl", x + a, r + 1, x + a + NUM[1] - 1, r + 1, ref(lc, linha, k(4)))
        f.add("vl", x + a + NUM[1], r + 1, x + W - 1, r + 1, ref(lc, linha, k(5)))
        f.add("desc", x, r + 2, x + W - 1, r + 1 + alt, ref(lc, linha, k(6)))

    def pequena(r, x, lc, linha, alt):
        f.add("cl", x, r, x + 1, r, ref(lc, linha, 2))
        f.add("nm", x + 2, r, x + W - 1, r, ref(lc, linha, 3))
        f.add("desc", x, r + 1, x + W - 1, r + alt, ref(lc, linha, 4))

    def bloco(id_, titulo, cap, alt, poe, d_ini, pares, legenda):
        nonlocal r
        cab = r
        f.add("cab", C1, cab, CN, cab, TXT[titulo])
        r = cab + 1
        fil, par = -(-cap // POR), None
        for fi in range(fil):
            if pares and fi % 2 == 0:
                if fi > 0:
                    f.add("lote", C1, r, CN, r, TXT[legenda(fi)])
                    r += 1
                par = r
            for j in range(POR):
                i = fi * POR + j
                if i < cap:
                    poe(r, X[j], i)
            if (fi + 1) * POR <= cap:
                cheias.setdefault(alt, []).append(r)
            # a descrição da fileira: o + fica na linha de cima dela, e só a primeira fileira do bloco nasce aberta
            grupos.append([r + d_ini, r + alt - 1, fi > 0])
            r += alt
            fim_do_par = pares and (fi % 2 == 1 or fi + 1 == fil)
            if fim_do_par:
                grupos.append([par, r - 1, fi >= 2])                   # só o primeiro par nasce aberto
            elif fi + 1 < fil:
                r += 1
        r += 1
        grupos.append([cab + 1, r - 1, False])

    bloco("feitiços", "feitiços", CAP["feiticos"], 2 + ALT["feitico"], lambda rr, x, i: carta(rr, x, cF, i, None), 2, True,
          lambda fi: f"par {fi}")
    # as Liberações numa fileira, e a Técnica Máxima e o Domínio em carta larga
    cab = r
    f.add("cab", C1, cab, CN, cab, TXT["máximas"])
    r = cab + 1
    for j in range(fa.N_LIB):
        carta(r, X[j], cL, j, "tag lib")
    if fa.N_LIB == POR:
        cheias[2 + ALT["feitico"]].append(r)
    grupos.append([r + 2, r + 1 + ALT["feitico"], False])
    r += 2 + ALT["feitico"] + 1
    for i, tag in ((0, "tag tm"), (1, "tag dom")):
        f.add("cl", C1, r, C1 + 1, r, TXT[tag])
        f.add("nm", C1 + 2, r, 27, r, ref(cM, i, 1))
        f.add("vl", 28, r, 31, r, ref(cM, i, 2))
        f.add("vl", 32, r, 37, r, ref(cM, i, 3))
        f.add("vl", 38, r, CN, r, ref(cM, i, 4))
        f.add("desc", C1, r + 1, CN, r + ALT["largo"], ref(cM, i, 5))
        grupos.append([r + 1, r + ALT["largo"], True])
        r += 1 + ALT["largo"] + 1
    grupos.append([cab + 1, r - 1, False])
    bloco("passivas", "passivas", CAP["passivas"], 1 + ALT["passiva"], lambda rr, x, i: pequena(rr, x, cPm, i, ALT["passiva"]), 1, True,
          lambda fi: f"par passivas {fi}")
    bloco("aptidões", "aptidões", CAP["aptidoes"], 1 + ALT["aptidao"], lambda rr, x, i: pequena(rr, x, cAm, i, ALT["aptidao"]), 1, True,
          lambda fi: f"par aptidões {fi}")
    fim = r
    grupos.append([a_secao, fim - 1, False])
    # dois grupos vizinhos na mesma profundidade virariam um só no Sheets
    prof = lambda g: sum(1 for o in grupos if o[0] <= g[0] and g[1] <= o[1])
    for a_ in grupos:
        for b_ in grupos:
            if a_ is not b_ and b_[0] == a_[1] + 1 and prof(a_) == prof(b_):
                raise SystemExit(f"menu_rapido: os grupos {a_[:2]} e {b_[:2]} estao colados")

    # o fundo das células vazias da seção, como o resto da FICHA
    dentro = set()
    for m in f.mesclas:
        (l1, c1), (l2, c2) = (ix._lc(x) for x in m.split(":"))
        dentro |= {(l, c) for l in range(l1, l2 + 1) for c in range(c1, c2 + 1)}
    dentro |= {ix._lc(c) for c in f.cel}
    for l in range(r0, fim + 1):
        for c in range(3, ficha["colunas"]):
            if (l, c) not in dentro:
                f.cel[fa._a1(c, l)] = (None, fundo)

    # o que sai: as células, as mesclagens, os menus e as alturas da seção 8 de hoje
    sai = {c for c in fcel if ix._lc(c)[0] >= r8 and ix._lc(c)[1] >= 3} - set(guarda)
    mesc_sai = [m for m in ficha["mescladas"] if ix._lc(m.split(":")[0])[0] >= r8 and ix._lc(m.split(":")[0])[1] >= 3]
    menus_sai = [m["onde"] for m in ficha["menus"] if all(ix._lc(p.split(":")[0])[0] >= r8 for p in m["onde"].split())]
    # o índice: as seis caixas da seção 8 saem dele, e as duas contas da DADOS que liam a seção leem a Ficha Amaldiçoada
    dcel = {x[0]: x for x in dados["celulas"]}
    saem_do_indice = ("feitiços disponíveis", "passivas", "aptidão de graça 1", "aptidão de graça 2", "aptidões disponíveis", "passivas do leque")
    cel_dados = {}
    for c, x in dcel.items():
        if c.startswith("BA") and x[1] in saem_do_indice:
            cel_dados[c] = (None, c)
            cel_dados["BB" + c[2:]] = (None, "BB" + c[2:])
        if x[1] in ("aptidões anotadas", "Passivas do Leque anotadas"):
            lin, cc = ix._lc(c)
            valor = H["aptidões anotadas"] if x[1] == "aptidões anotadas" else H["passivas do Leque"]
            cel_dados[fa._a1(cc + 1, lin)] = (f"={valor}", fa._a1(cc + 1, lin))
    return {"r0": r0, "r8_velho": r8, "fim": fim, "fim_velho": fim_velho, "celulas": {NOME: {c: (v[0], c) for c, v in f.cel.items()}, "DADOS": cel_dados},
            "_estilos": f.cel, "sai": sai - set(f.cel), "mescladas_sai": {NOME: mesc_sai}, "mescladas": {NOME: f.mesclas},
            "menus_sai": {NOME: menus_sai}, "grupos": grupos,
            "copias": [[v[0], v[0] + alt - 1, v[1:], C1, CN] for alt, v in cheias.items() if len(v) > 1]}


def aplica(layout, tm):
    """põe o menu na FICHA. Devolve quantas células mudaram"""
    ficha = ix._aba(layout, NOME)
    n = 0
    ficha["celulas"] = [c for c in ficha["celulas"] if c[0] not in tm["sai"]]
    por = {c[0]: c for c in ficha["celulas"]}
    for coord, (v, est) in tm["_estilos"].items():
        if coord in por:
            por[coord][1], por[coord][2] = v, est
        else:
            ficha["celulas"].append([coord, v, est])
        n += 1
    n += ix.aplica(layout, {"DADOS": tm["celulas"]["DADOS"]})
    ficha["mescladas"] = [m for m in ficha["mescladas"] if m not in tm["mescladas_sai"][NOME]] + tm["mescladas"][NOME]
    ficha["menus"] = [m for m in ficha["menus"] if m["onde"] not in tm["menus_sai"][NOME]]
    ficha["linhas_alt"] = [a for a in ficha["linhas_alt"] if a[0] < tm["r0"]] + [[tm["r0"], 27.0]]
    ficha["linhas"] = tm["fim"]
    ficha["grupos"] = {"linhas": (ficha.get("grupos") or {}).get("linhas", []) + tm["grupos"], "colunas": []}
    # as linhas do menu ficam fora da trava de fórmula do script, e o onEdit devolve a conta de quem escrever por cima
    ficha["sem_trava"] = ficha.get("sem_trava", []) + [[tm["r0"], tm["fim"]]]
    # as fileiras de três cartas são iguais a menos da linha que cada caixa cita: o script mescla a primeira de cada
    # altura e copia o formato para as outras (expandirCopias_ e montarAba_), como na Ficha Amaldiçoada. São mais de
    # duzentas mesclagens a menos uma a uma, e o ABAS não repete o que a cópia traz
    ficha["copias"] = ficha.get("copias", []) + tm["copias"]
    return n
