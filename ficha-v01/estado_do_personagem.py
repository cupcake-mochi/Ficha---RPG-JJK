# -*- coding: utf-8 -*-
"""O estado do personagem, embaixo das barras da FICHA (08/10/2026, o B41).

Da revisão do que o livro manda registrar e a ficha não tinha, o Mizuki escolheu: "Traços, sequelas, cicatrizes,
exaustão, resistencias e imunidades, integridade da entidade com alma, espaço de feitiço ocupado por invocação". Do
estudo (mockup/revisao-estudo.png) ficou a forma A, "mas acredito que pode ser +- como na C, colocar espaços separados":
uma linha embaixo das barras, com as quatro caixas separadas, no mesmo passo das caixas do REGISTRO.

E, dos Legados: "acho que ter um espaço para acesso na ficha pra ver pelo menos o legado de exceção/mecanico seria
ideal, lembrando q da pra criar legado, ent n precisa fazer lista". Os dois Legados são escritos no dossiê da FICHA
PESSOAL, em texto livre, e aqui ficam espelhados, para consulta na mesa.

14/10/2026 (B46, o livro R51). Do estudo das Origens (mockup/origens-estudo.html), o Mizuki escolheu a forma A para o
Morrendo, "mas no 'tempo para receber', acho q deveria deixar claro oq é", e as Sequelas em caixinhas de marcar, "tipo
dnd com as caixinhas de marcar falhas e sucessos, mas so pras sequelas". E os dois Legados saíram do livro: o espelho
embaixo das barras passa a mostrar a marcante e as duas menores da Origem, com a frequência de cada uma.

As linhas quem abre é o linhas_novas.py. Este módulo as preenche, antes do índice (que acha as caixas pelo rótulo):

    +1  SE A VIDA CHEGAR A 0 · MORRENDO (a faixa que explica a linha)                          (14/10/2026, B46)
    +2  AGUENTAR        INSISTIR 1ª VEZ      INSISTIR 2ª EM DIANTE   PRAZO ATÉ SER DERROTADO  os rótulos
    +3  [número]        [número]             [número]                [rodadas]                 o ficha_pessoal.py escreve
    +4  de onde vem     de onde vem          de onde vem             o que é o prazo
    +5
    +6  DESCANSO        O ÚLTIMO DESCANSO                                                      (09/10/2026, B43)
    +7  [menu]          o que o último descanso mudou
    +8
    +9  SEQUELAS        EXAUSTÃO         RESISTÊNCIAS     IMUNIDADES        os rótulos
    +10 [☐ ☐ ☐]         [0 a 3]          texto            texto
    +11 a janela        o efeito         (segunda linha)  (segunda linha)
    +12
    +13 MARCANTE                 MENOR 1                  MENOR 2                              (14/10/2026, B46)
    +14 o nome, da FICHA PESSOAL (o ficha_pessoal.py escreve)
    +15 a frequência
    +16

O Morrendo (livro R50 e R51, itens 195 e 197): ao cair, Aguentar pede de tratamento 1/4 da vida máxima, para cima, sem
teto; Insistir pede 1/3 na primeira vez da cena e 1/2 nas seguintes, para cima, com teto de 15 × a maior Classe. A janela
é de 3 rodadas menos 1 por Sequela; com três, Derrotado na hora. A linha é só de leitura: não guarda o tratamento recebido
(a ficha não tem caixa do que muda de turno em turno), e o número sai da vida máxima e da CLASSE MÁXIMA da FICHA.


O descanso (09/10/2026, B43). O Mizuki: "Problema q tem tipos, ficaria na ficha e como fariamos?". Um menu com os quatro
tipos do livro (curto ou longo, em lugar propício ou fora); o onEdit do Codigo.gs faz a conta nas caixas, devolve o menu
ao convite e escreve ao lado o que mudou. Do estudo (mockup/descanso-estudo.png) ele escolheu a forma A: uma linha
própria entre as barras e o estado.

As caixas de texto esticam (08/10/2026): a de resistências e a de imunidades, pela linha de baixo delas. Quem declara é a chave `esticam` da aba, e quem estica é o Codigo.gs.

O que é conta e depende da FICHA PESSOAL ou do índice (o espelho da Origem, os números do Morrendo e a Exaustão no
DESLOCAMENTO) é o ficha_pessoal.py que escreve, quando sabe os endereços.

As regras, do livro (Dano e recuperação): a Sequela vem de sair de uma queda, e 0, 1, 2 ou 3 antes de cair dão janela
de 3, 2 ou 1 rodada, ou Derrotado na hora; o descanso longo desmarca todas; a Exaustão vem da quarta luta do dia em diante, até 3 degraus: 1,
desvantagem em perícias e ofícios; 2, deslocamento limitado a 4,5 m; 3, desvantagem em ataques e TRs.
"""
import json, re
import indice_ficha as ix

ABA = "FICHA"
BLOCOS = (("D", "M"), ("O", "X"), ("Z", "AI"), ("AK", "AT"))        # o passo das caixas do REGISTRO
ROTULOS = ("SEQUELAS", "EXAUSTÃO", "RESISTÊNCIAS", "IMUNIDADES")
GRAUS = '"0,1,2,3"'                                                   # o menu da Exaustão
# 14/10/2026 (B46): as três caixinhas das Sequelas, na caixa de D a M (colunas F, H e J), e o que cada uma é no índice
CAIXINHAS = ("F", "H", "J")
SEQUELAS = tuple(f"sequela {i}" for i in (1, 2, 3))
# a linha do Morrendo: o rótulo de cada caixa (é por ele que o índice a acha) e o que o índice a chama
FAIXA_DO_MORRENDO = "SE A VIDA CHEGAR A 0 · MORRENDO · a cura que você precisa receber para levantar, e o prazo para recebê-la"
MORRENDO = (("morrendo aguentar", "AGUENTAR · FICA INCONSCIENTE"), ("morrendo insistir 1", "INSISTIR · 1ª VEZ NA CENA"),
            ("morrendo insistir 2", "INSISTIR · 2ª VEZ EM DIANTE"), ("morrendo prazo", "PRAZO ATÉ SER DERROTADO"))
# o espelho da Origem: a marcante e as duas menores, em três terços da largura
ORIGEM = (("marcante", "MARCANTE"), ("menor 1", "MENOR 1"), ("menor 2", "MENOR 2"))
TERCOS = (("D", "Q"), ("S", "AE"), ("AG", "AT"))
LINHAS = 16                                                           # as linhas que o desenho pede ao linhas_novas.py
LINHAS_DO_MORRENDO = 5                                                # a faixa, o rótulo, o número, o de onde vem e uma em branco
LINHAS_DO_DESCANSO = 3                                                # o rótulo, o menu e uma em branco, antes do estado
# o menu do descanso: o convite, que é como ele nasce e como o script o devolve, e os quatro tipos do livro
SEM_DESCANSO = "Escolha o descanso"
DESCANSOS = ("Curto · lugar propício", "Curto · fora", "Longo · lugar propício", "Longo · fora")
ROTULOS_DO_DESCANSO = ("DESCANSO", "O ÚLTIMO DESCANSO")
LIMITE_DA_EXAUSTAO = 4.5                                              # metros, do degrau 2 em diante

# as cores são as da FICHA (o rótulo no acento alto, a caixa no painel, o texto fraco e o papel da FICHA PESSOAL)
OSSO, FRACO, ACENTO, PAINEL, FUNDO, REGUA = "FFE8DCD4", "FF998BA9", "FF3D2E78", "FF1E1733", "FF17131F", "FF8A7EC4"
_CAIXA = {l: ["medium", REGUA] for l in ("bottom", "left", "right", "top")}
_LADOS = lambda *ls: {l: ["medium", REGUA] for l in ls}
ESTILOS = {
    # 14/10/2026 (B46): a caixa das Sequelas é feita de células soltas (as caixinhas não podem estar mescladas), e a borda
    # de fora vai em cada uma: a da ponta esquerda, as do meio e a da ponta direita
    "seq_esq": [["Oswald", 12.0, OSSO, False, False], PAINEL, _LADOS("left", "top", "bottom"), ["center", "center", False, 0], None],
    "seq_meio": [["Oswald", 12.0, OSSO, False, False], PAINEL, _LADOS("top", "bottom"), ["center", "center", False, 0], None],
    "seq_dir": [["Oswald", 12.0, OSSO, False, False], PAINEL, _LADOS("right", "top", "bottom"), ["center", "center", False, 0], None],
    # a faixa que explica a linha do Morrendo: o fundo do título de seção (o acento da paleta, como na FICHA PESSOAL)
    "faixa": [["Oswald", 9.0, OSSO, False, False], "FF211940", _CAIXA, ["left", "center", False, 0], None],
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


def conta_das_sequelas(cels):
    """quantas caixinhas estão marcadas"""
    return "+".join(f"N({c})" for c in cels)


def janela(cels):
    """o que a caixa das Sequelas diz embaixo: a janela da próxima queda"""
    n = conta_das_sequelas(cels)
    return (f'=IF({n}<=0,"Próxima queda: 3 rodadas de janela",IF({n}=1,"Próxima queda: 2 rodadas de janela",'
            f'IF({n}=2,"Próxima queda: 1 rodada de janela","Próxima queda: Derrotado na hora")))')


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
    m = depois + 1                                    # a faixa do Morrendo
    d = m + LINHAS_DO_MORRENDO                        # o rótulo do descanso
    r = d + LINHAS_DO_DESCANSO                        # os rótulos do estado
    o = r + 4                                         # o rótulo do espelho da Origem
    return {"faixa_morrendo": f"D{m}",
            "morrendo": {k: f"{c1}{m + 2}" for (k, _), (c1, _) in zip(MORRENDO, BLOCOS)},
            "morrendo_sub": {k: f"{c1}{m + 3}" for (k, _), (c1, _) in zip(MORRENDO, BLOCOS)},
            "descanso": f"{BLOCOS[0][0]}{d + 1}", "ultimo_descanso": f"{BLOCOS[1][0]}{d + 1}",
            "rot": {n: f"{c1}{r}" for n, (c1, _) in zip(ROTULOS, BLOCOS)},
            "sequelas": [f"{c}{r + 1}" for c in CAIXINHAS], "exaustao": f"{BLOCOS[1][0]}{r + 1}",
            "janela": f"{BLOCOS[0][0]}{r + 2}", "efeito": f"{BLOCOS[1][0]}{r + 2}",
            "resistencias": f"{BLOCOS[2][0]}{r + 1}", "imunidades": f"{BLOCOS[3][0]}{r + 1}",
            "origem_rot": {k: f"{c1}{o}" for (k, _), (c1, _) in zip(ORIGEM, TERCOS)},
            "origem": {k: f"{c1}{o + 1}" for (k, _), (c1, _) in zip(ORIGEM, TERCOS)},
            "origem_freq": {k: f"{c1}{o + 2}" for (k, _), (c1, _) in zip(ORIGEM, TERCOS)}}


def trocas(layout, ln):
    """as caixas que entram nas linhas novas: {"celulas": {FICHA: {coord: (valor, estilo)}}, "mescladas", "menus", "G"}"""
    if ln["n"] != LINHAS:
        raise SystemExit(f"estado_do_personagem: o desenho pede {LINHAS} linhas novas, e o linhas_novas abriu {ln['n']}")
    G = lugares(ln["depois"])
    m = ln["depois"] + 1
    d = m + LINHAS_DO_MORRENDO
    r = d + LINHAS_DO_DESCANSO
    o = r + 4
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

    # o Morrendo: a faixa de ponta a ponta e as quatro caixas no passo das do REGISTRO. Os números e o texto de baixo
    # são conta, e quem escreve é o ficha_pessoal.py (pelo índice, que acha cada caixa pelo rótulo)
    add("faixa", BLOCOS[0][0], m, BLOCOS[-1][1], m, FAIXA_DO_MORRENDO)
    for (k, rot), (c1, c2) in zip(MORRENDO, BLOCOS):
        add("rot", c1, m + 1, c2, m + 1, rot)
        assert add("num", c1, m + 2, c2, m + 2) == G["morrendo"][k]
        assert add("sub", c1, m + 3, c2, m + 3) == G["morrendo_sub"][k]
    # o descanso: o menu no passo da primeira caixa, e o registro do último descanso no resto da linha
    (m1, m2), (u1, _), _, (_, u2) = BLOCOS
    add("rot", m1, d, m2, d, ROTULOS_DO_DESCANSO[0])
    add("rot", u1, d, u2, d, ROTULOS_DO_DESCANSO[1])
    assert add("menu", m1, d + 1, m2, d + 1, SEM_DESCANSO) == G["descanso"]
    assert add("reg", u1, d + 1, u2, d + 1) == G["ultimo_descanso"]
    for rot, (c1, c2) in zip(ROTULOS, BLOCOS):
        add("rot", c1, r, c2, r, rot)
    (s1, s2), (e1, e2), (r1, r2), (i1, i2) = BLOCOS
    # as Sequelas: três caixinhas de marcar (a célula com FALSO vira caixa de seleção na montagem), soltas na caixa
    c_s1, c_s2 = ix._lc(f"{s1}1")[1], ix._lc(f"{s2}1")[1]
    for col in range(c_s1, c_s2 + 1):
        letra = ix._letras(col)
        estilo = "seq_esq" if col == c_s1 else "seq_dir" if col == c_s2 else "seq_meio"
        add(estilo, letra, r + 1, letra, r + 1, False if letra in CAIXINHAS else None)
    assert add("num", e1, r + 1, e2, r + 1, 0) == G["exaustao"]
    fixa = lambda a1: "$" + re.sub(r"(\d+)$", r"$\1", a1)
    assert add("sub", s1, r + 2, s2, r + 2, janela([fixa(c) for c in G["sequelas"]])) == G["janela"]
    assert add("sub", e1, r + 2, e2, r + 2, efeito(fixa(G["exaustao"]))) == G["efeito"]
    assert add("txt", r1, r + 1, r2, r + 2) == G["resistencias"]
    assert add("txt", i1, r + 1, i2, r + 2) == G["imunidades"]
    # o espelho da Origem: o rótulo, o nome e a frequência de cada capacidade (as contas, o ficha_pessoal.py escreve)
    for (k, rot), (c1, c2) in zip(ORIGEM, TERCOS):
        assert add("rot", c1, o, c2, o, rot) == G["origem_rot"][k]
        assert add("reg", c1, o + 1, c2, o + 1) == G["origem"][k]
        assert add("sub", c1, o + 2, c2, o + 2) == G["origem_freq"][k]
    menus = [{"onde": G["exaustao"], "tipo": "list", "formula": GRAUS, "vazio_ok": True, "mostra_seta": True},
             {"onde": G["descanso"], "tipo": "list", "formula": '"' + ",".join((SEM_DESCANSO,) + DESCANSOS) + '"',
              "vazio_ok": True, "mostra_seta": True}]
    # 08/10/2026, do teste no Sheets: "textos de aproximadamente 170 caracteres ficam cortados pela altura das caixas".
    # As duas caixas de texto esticam com o que for escrito, como as cartas de Habilidades: o esticarCaixas_ do
    # Codigo.gs conta as linhas do texto mais comprido e acerta a altura da linha de baixo da caixa (a de cima é a das
    # caixinhas das Sequelas e do número da Exaustão, e fica como está: `fixo` é a altura dela, que a conta desconta)
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
