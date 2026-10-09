# -*- coding: utf-8 -*-
"""O estado do personagem, embaixo das barras da FICHA (08/10/2026, o B41).

Da revisão do que o livro manda registrar e a ficha não tinha, o Mizuki escolheu: "Traços, sequelas, cicatrizes,
exaustão, resistencias e imunidades, integridade da entidade com alma, espaço de feitiço ocupado por invocação". Do
estudo (mockup/revisao-estudo.png) ficou a forma A, "mas acredito que pode ser +- como na C, colocar espaços separados":
uma linha embaixo das barras, com as quatro caixas separadas, no mesmo passo das caixas do REGISTRO.

E, dos Legados: "acho que ter um espaço para acesso na ficha pra ver pelo menos o legado de exceção/mecanico seria
ideal, lembrando q da pra criar legado, ent n precisa fazer lista". Os dois Legados são escritos no dossiê da FICHA
PESSOAL, em texto livre, e aqui ficam espelhados, para consulta na mesa.

As linhas quem abre é o linhas_novas.py. Este módulo as preenche, antes do índice (que acha as caixas pelo rótulo):

    +1  DESCANSO        O ÚLTIMO DESCANSO                                   (09/10/2026, B43)
    +2  [menu]          o que o último descanso mudou
    +3
    +4  SEQUELAS        EXAUSTÃO         RESISTÊNCIAS     IMUNIDADES        os rótulos
    +5  [0 a 3]         [0 a 3]          texto            texto
    +6  a janela        o efeito         (segunda linha)  (segunda linha)
    +7
    +8  LEGADO 1                         LEGADO 2
    +9  o espelho da FICHA PESSOAL, em duas linhas
    +10
    +11

O descanso (09/10/2026, B43). O Mizuki: "Problema q tem tipos, ficaria na ficha e como fariamos?". Um menu com os quatro
tipos do livro (curto ou longo, em lugar propício ou fora); o onEdit do Codigo.gs faz a conta nas caixas, devolve o menu
ao convite e escreve ao lado o que mudou. Do estudo (mockup/descanso-estudo.png) ele escolheu a forma A: uma linha
própria entre as barras e o estado.

As caixas de texto esticam (08/10/2026): a de resistências e a de imunidades, pela linha de baixo delas, e o espelho
dos Legados, pelas duas linhas dele. Quem declara é a chave `esticam` da aba, e quem estica é o Codigo.gs.

O que é conta e depende da FICHA PESSOAL (o espelho dos Legados e a Exaustão no DESLOCAMENTO) é o ficha_pessoal.py
que escreve, quando sabe os endereços dela.

As regras, do livro (Dano e Recuperação): a Sequela vem de sair de uma queda, e 0, 1, 2 ou 3 antes de cair dão janela
de 3, 2 ou 1 rodada, ou Derrotado na hora; a Exaustão vem da quarta luta do dia em diante, até 3 degraus: 1,
desvantagem em perícias e ofícios; 2, deslocamento limitado a 4,5 m; 3, desvantagem em ataques e TRs.
"""
import json
import indice_ficha as ix

ABA = "FICHA"
BLOCOS = (("D", "M"), ("O", "X"), ("Z", "AI"), ("AK", "AT"))        # o passo das caixas do REGISTRO
ROTULOS = ("SEQUELAS", "EXAUSTÃO", "RESISTÊNCIAS", "IMUNIDADES")
LEGADOS = ("LEGADO 1", "LEGADO 2")
METADES = (("D", "X"), ("Z", "AT"))
LEGADO_LINHAS = 2                                                     # as linhas do espelho de cada Legado
GRAUS = '"0,1,2,3"'                                                   # o menu das duas caixas de número
LINHAS = 11                                                           # as linhas que o desenho pede ao linhas_novas.py
LINHAS_DO_DESCANSO = 3                                                # o rótulo, o menu e uma em branco, antes do estado
# o menu do descanso: o convite, que é como ele nasce e como o script o devolve, e os quatro tipos do livro
SEM_DESCANSO = "Escolha o descanso"
DESCANSOS = ("Curto · lugar propício", "Curto · fora", "Longo · lugar propício", "Longo · fora")
ROTULOS_DO_DESCANSO = ("DESCANSO", "O ÚLTIMO DESCANSO")
LIMITE_DA_EXAUSTAO = 4.5                                              # metros, do degrau 2 em diante

# as cores são as da FICHA (o rótulo no acento alto, a caixa no painel, o texto fraco e o papel da FICHA PESSOAL)
OSSO, FRACO, ACENTO, PAINEL, FUNDO, REGUA = "FFE8DCD4", "FF998BA9", "FF3D2E78", "FF1E1733", "FF17131F", "FF8A7EC4"
_CAIXA = {l: ["medium", REGUA] for l in ("bottom", "left", "right", "top")}
ESTILOS = {
    "rot": [["Oswald", 8.0, OSSO, False, False], ACENTO, _CAIXA, ["center", "center", False, 0], None],
    "num": [["Oswald", 12.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "sub": [["Roboto", 8.0, FRACO, False, False], FUNDO, _CAIXA, ["center", "center", True, 0], None],
    "txt": [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["left", "top", True, 0], None],
    "menu": [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "reg": [["Roboto", 9.0, OSSO, False, False], PAINEL, _CAIXA, ["left", "center", False, 0], None],
}


def _estilo(layout, nome):
    chave = json.dumps(ESTILOS[nome], ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(json.loads(json.dumps(ESTILOS[nome])))
    return len(layout["estilos"]) - 1


def janela(cel):
    """o que a caixa das Sequelas diz embaixo: a janela da próxima queda"""
    return (f'=IF(N({cel})<=0,"Próxima queda: 3 rodadas de janela",IF(N({cel})=1,"Próxima queda: 2 rodadas de janela",'
            f'IF(N({cel})=2,"Próxima queda: 1 rodada de janela","Próxima queda: Derrotado na hora")))')


def efeito(cel):
    """o que a caixa da Exaustão diz embaixo: os efeitos somam"""
    return (f'=IF(N({cel})<=0,"Sem penalidade",IF(N({cel})=1,"Desvantagem em perícias e ofícios",'
            f'IF(N({cel})=2,"Desv. em perícias e ofícios · até 4,5 m",'
            f'"Desv. em perícias, ofícios, ataques e TRs · até 4,5 m")))')


def largura_px(c1, c2):
    """a largura útil, em pixels do Sheets, de uma caixa de texto que vai da coluna c1 à c2 da FICHA: é a conta da
    carta de Habilidades (habilidades.medida), que o Codigo.gs usa para saber quantas linhas o texto ocupa"""
    import habilidades as hb
    return (ix._lc(f"{c2}1")[1] - ix._lc(f"{c1}1")[1] + 1) * hb.PX_COLUNA - hb.RESPIRO_PX


def lugares(depois):
    """os endereços das caixas, pela linha depois da qual as novas abriram"""
    r = depois + 1 + LINHAS_DO_DESCANSO
    d = depois + 1
    g = {"descanso": f"{BLOCOS[0][0]}{d + 1}", "ultimo_descanso": f"{BLOCOS[1][0]}{d + 1}",
         "rot": {n: f"{c1}{r}" for n, (c1, _) in zip(ROTULOS, BLOCOS)},
         "sequelas": f"{BLOCOS[0][0]}{r + 1}", "exaustao": f"{BLOCOS[1][0]}{r + 1}",
         "janela": f"{BLOCOS[0][0]}{r + 2}", "efeito": f"{BLOCOS[1][0]}{r + 2}",
         "resistencias": f"{BLOCOS[2][0]}{r + 1}", "imunidades": f"{BLOCOS[3][0]}{r + 1}",
         "legado_rot": [f"{c1}{r + 4}" for c1, _ in METADES], "legado": [f"{c1}{r + 5}" for c1, _ in METADES]}
    return g


def trocas(layout, ln):
    """as caixas que entram nas linhas novas: {"celulas": {FICHA: {coord: (valor, estilo)}}, "mescladas", "menus", "G"}"""
    if ln["n"] != LINHAS:
        raise SystemExit(f"estado_do_personagem: o desenho pede {LINHAS} linhas novas, e o linhas_novas abriu {ln['n']}")
    r = ln["depois"] + 1 + LINHAS_DO_DESCANSO
    d = ln["depois"] + 1
    G = lugares(ln["depois"])
    E = {k: _estilo(layout, k) for k in ESTILOS}
    cel, mescla = {}, []

    def add(estilo, c1, l1, c2, l2, valor=None):
        (la, ca), (lb, cb) = ix._lc(f"{c1}{l1}"), ix._lc(f"{c2}{l2}")
        for lin in range(la, lb + 1):
            for col in range(ca, cb + 1):
                cel[f"{ix._letras(col)}{lin}"] = (valor if (lin, col) == (la, ca) else None, E[estilo])
        if (la, ca) != (lb, cb):
            mescla.append(f"{c1}{l1}:{c2}{l2}")
        return f"{c1}{l1}"

    # o descanso: o menu no passo da primeira caixa, e o registro do último descanso no resto da linha
    (m1, m2), (u1, _), _, (_, u2) = BLOCOS
    add("rot", m1, d, m2, d, ROTULOS_DO_DESCANSO[0])
    add("rot", u1, d, u2, d, ROTULOS_DO_DESCANSO[1])
    assert add("menu", m1, d + 1, m2, d + 1, SEM_DESCANSO) == G["descanso"]
    assert add("reg", u1, d + 1, u2, d + 1) == G["ultimo_descanso"]
    for rot, (c1, c2) in zip(ROTULOS, BLOCOS):
        add("rot", c1, r, c2, r, rot)
    (s1, s2), (e1, e2), (r1, r2), (i1, i2) = BLOCOS
    fixa = lambda col, lin: f"${col}${lin}"
    assert add("num", s1, r + 1, s2, r + 1, 0) == G["sequelas"]
    assert add("num", e1, r + 1, e2, r + 1, 0) == G["exaustao"]
    assert add("sub", s1, r + 2, s2, r + 2, janela(fixa(s1, r + 1))) == G["janela"]
    assert add("sub", e1, r + 2, e2, r + 2, efeito(fixa(e1, r + 1))) == G["efeito"]
    assert add("txt", r1, r + 1, r2, r + 2) == G["resistencias"]
    assert add("txt", i1, r + 1, i2, r + 2) == G["imunidades"]
    for k, (rot, (c1, c2)) in enumerate(zip(LEGADOS, METADES)):
        assert add("rot", c1, r + 4, c2, r + 4, rot) == G["legado_rot"][k]
        assert add("txt", c1, r + 5, c2, r + 5 + LEGADO_LINHAS - 1) == G["legado"][k]
    menus = [{"onde": f"{G['sequelas']} {G['exaustao']}", "tipo": "list", "formula": GRAUS, "vazio_ok": True, "mostra_seta": True},
             {"onde": G["descanso"], "tipo": "list", "formula": '"' + ",".join((SEM_DESCANSO,) + DESCANSOS) + '"',
              "vazio_ok": True, "mostra_seta": True}]
    # 08/10/2026, do teste no Sheets: "textos de aproximadamente 170 caracteres ficam cortados pela altura das caixas".
    # As duas caixas de texto esticam com o que for escrito, como as cartas de Habilidades: o esticarCaixas_ do
    # Codigo.gs conta as linhas do texto mais comprido e acerta a altura da linha de baixo da caixa (a de cima é a do
    # número das Sequelas e da Exaustão, e fica como está: `fixo` é a altura dela, que a conta desconta)
    import habilidades as hb
    # cada texto: [a largura dele, as células que o formam, a primeira linha que estica, quantas, o fixo]. A chave não
    # se chama `caixas` porque esse nome o ABAS já usa para as caixas de seleção
    estica = [{"gatilhos": [f"{r1}{r + 1}:{r2}{r + 2}", f"{i1}{r + 1}:{i2}{r + 2}"], "aba": ABA,
               "textos": [[largura_px(r1, r2), [G["resistencias"]], r + 2, 1, hb.MINIMA_PX],
                          [largura_px(i1, i2), [G["imunidades"]], r + 2, 1, hb.MINIMA_PX]]}]
    return {"celulas": {ABA: cel}, "mescladas": {ABA: mescla}, "menus": {ABA: menus}, "G": G, "linhas": ln["linhas"],
            "esticam": {ABA: estica}}


def aplica(layout, tr):
    n = 0
    for nome, cels in tr["celulas"].items():
        aba = ix._aba(layout, nome)
        por = {c[0]: c for c in aba["celulas"]}
        for coord, (valor, estilo) in cels.items():
            if coord in por:
                if por[coord][1] != valor or por[coord][2] != estilo:
                    por[coord][1], por[coord][2] = valor, estilo
                    n += 1
            else:
                aba["celulas"].append([coord, valor, estilo])
                n += 1
        aba["mescladas"] += [m for m in tr["mescladas"].get(nome, []) if m not in aba["mescladas"]]
        aba["menus"] += [m for m in tr["menus"].get(nome, []) if m not in aba["menus"]]
        aba["esticam"] = aba.get("esticam", []) + [x for x in tr.get("esticam", {}).get(nome, []) if x not in aba.get("esticam", [])]
    return n
