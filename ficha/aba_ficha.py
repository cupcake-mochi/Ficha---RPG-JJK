# -*- coding: utf-8 -*-
"""A aba FICHA, no registro de documento (decisao C6).

Regua no lugar de caixa, secoes numeradas, lombada na lateral, e as tres
reservas com SPARKLINE colorido pela cor de estado (A5). Nenhum numero
derivado e digitado: tudo formula.
"""
from estilo import *
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

COLS, LINHAS = 46, 146

def monta(wb, CAT, DEC, ref):
    ws = base(wb, "FICHA", COLS, LINHAS)
    R = {}
    def dv(f, c1, r1, c2, r2):
        v = DataValidation(type="list", formula1=f, allow_blank=True, showDropDown=False)
        ws.add_data_validation(v); v.add(f"{L(c1)}{r1}:{L(c2)}{r2}")

    lombada(ws, LINHAS, "PROJETO M", "FICHA DE REGISTRO")

    # ------------------------------------------------------------- cabecalho
    pinta(ws, 3, 1, COLS, 5, TINTA)
    txt(ws, 4, 2, "GUILDA · FICHA DE REGISTRO", nome=TITULO, pt=9, cor=BLOCO, ate=(24, 2))
    R["nome"] = txt(ws, 4, 3, None, nome=DOCUMENTO, pt=26, cor=OSSO, ate=(26, 4))
    txt(ws, 4, 5, "o nome do portador vai na CARTEIRA e cai aqui sozinho",
        nome=CORPO, pt=8, cor=LINHA, ate=(26, 5))
    txt(ws, 34, 2, "CATÁLOGO", nome=TITULO, pt=8, cor=TEXTO_FRACO, al="right", ate=(COLS, 2))
    txt(ws, 34, 3,
        f'=IF({ref["carimbo_local"]}={ref["carimbo_central"]},'
        f'"v"&{ref["carimbo_local"]}&" · em dia",'
        f'"⚠ v"&{ref["carimbo_local"]}&" · a atual é a v"&{ref["carimbo_central"]})',
        nome=SERIE, pt=10, cor=BLOCO, al="right", ate=(COLS, 3))
    arte(ws, "pincelada-roxa.png", 3, 6, 1180, 12)

    # ------------------------------------------------------------- 01 quem é
    r = secao(ws, 8, "01", "QUEM É")
    R["caminho"] = campo(ws, 4, r, 8, "caminho", None)
    dv(ref["Caminhos"], 4, r + 1, 12, r + 1)
    R["trilha"] = campo(ws, 14, r, 8, "trilha", None)
    dv(ref["Trilhas"], 14, r + 1, 22, r + 1)
    R["origem"] = campo(ws, 24, r, 8, "origem", None)
    dv(ref["Origens"], 24, r + 1, 32, r + 1)
    R["nivel"] = campo(ws, 34, r, 4, "nível", 2, pt=20, cor=OSSO, nome=TITULO)
    R["xp"] = campo(ws, 40, r, 6, "xp · na mão", 0, pt=12, cor=TEXTO_FRACO, nome=SERIE)
    NIV = "$" + L(34) + "$" + str(r + 1)
    CAM = "$" + L(4) + "$" + str(r + 1)
    r += 4

    # ------------------------------------------------------------- 02 o corpo
    r = secao(ws, r, "02", "O CORPO")
    for i, a in enumerate(CAT["atributos"]["lista"]):
        c1 = 4 + i * 8
        txt(ws, c1, r, a[:3].upper(), nome=TITULO, pt=8, cor=TEXTO_FRACO, ate=(c1 + 6, r))
        R["atr_" + a] = txt(ws, c1, r + 1, 0, nome=TITULO, pt=24, cor=OSSO, ate=(c1 + 6, r + 2))
        txt(ws, c1, r + 3, a, nome=CORPO, pt=8, cor=LINHA, ate=(c1 + 6, r + 3))
        regua(ws, c1, r + 4, c1 + 6, LINHA)
    FOR = f'${L(R["atr_Força"].column)}${R["atr_Força"].row}'
    CON = f'${L(R["atr_Constituição"].column)}${R["atr_Constituição"].row}'
    DES = f'${L(R["atr_Destreza"].column)}${R["atr_Destreza"].row}'
    ESS = f'${L(R["atr_Essência"].column)}${R["atr_Essência"].row}'
    r += 6

    # As notas do campo TEMP. Cada linha diz de onde ela vem, porque nota de
    # ficha e' regra abreviada e regra abreviada envelhece calada.
    #   ⚠ A do TETO faltava ate a v0.222: a nota da planilha viva dizia tres das
    #     quatro regras e omitia a quarta. O livro publica o teto no capitulo 10
    #     e a peca 1 §5.1.1 do outro repositorio e a dona da conta.
    #   ⚠ E o emitir_gs.py NAO carrega nota — isto vale so para o .xlsx. A
    #     planilha viva precisa do corrigir-notas-temp.gs, na planilha-viva/.
    NOTA_TEMP = {
        "vida": ("Vida temporária é anteparo, e não vida.\n"
                 "• É gasta antes da vida normal.\n"
                 "• Não empilha: duas fontes, fica a maior.\n"
                 "• Teto: metade da sua vida máxima.\n"
                 "• Some no fim da cena.\n"
                 "Livro, cap. 10. A Melhoria Rasga Escudo ignora ela."),
        "energia": ("Energia temporária gasta como PE, e gasta primeiro.\n"
                    "• Acumula até o teto que a própria fonte declarar.\n"
                    "• Hoje só o Braseiro concede, e o teto dele é 2.\n"
                    "• Some no fim da cena."),
        "integridade": ("⚠ Regra nenhuma concede integridade temporária hoje.\n"
                        "O campo existe porque as três reservas são montadas no "
                        "mesmo laço. Está em aberto (B17) e é decisão de desenho: "
                        "ou algo passa a conceder, ou o campo sai."),
    }

    # as tres reservas, com o medidor nativo
    TAB = ref["tabela_caminhos"]
    formulas = [
        ("vida", f'=IF({CAM}="","",(VLOOKUP({CAM},{TAB},3,FALSE)+{CON})'
                 f'+(VLOOKUP({CAM},{TAB},4,FALSE)+{CON})*({NIV}-1))'),
        ("energia", f'=IF({CAM}="","",VLOOKUP({CAM},{TAB},5,FALSE)*{NIV})'),
        # A Integridade deixou de ser plana na v0.145 do sistema, pela decisao
        # da v0.70: ela escala com Essencia. O dono e o capitulo 15 do livro,
        # vendorizado aqui como capitulo-15-dano-e-condicoes.md, e o
        # conferir-kaori.py le a regra de la em vez de guardar ela.
        # A planilha viva ja usa esta formula; era o GERADOR que estava atras.
        ("integridade", f'=20+({ESS}+5)*({NIV}-1)'),
    ]
    for nome_r, f_max in formulas:
        txt(ws, 4, r, nome_r.upper(), nome=TITULO, pt=8, cor=TEXTO_FRACO, ate=(14, r))
        atual = txt(ws, 4, r + 1, 0, nome=TITULO, pt=22, cor=OSSO, ate=(8, r + 2))
        mx = txt(ws, 10, r + 1, f_max, nome=CORPO, pt=10, cor=TEXTO_FRACO, ate=(14, r + 2))
        ca, cm = f"${L(4)}${r+1}", f"${L(10)}${r+1}"
        txt(ws, 16, r + 1, barra(ca, cm, cor_de_estado(ca, cm)), ate=(30, r + 2))
        tp = campo(ws, 32, r, 5, "temp", 0, pt=11, cor=TEXTO_FRACO, nome=SERIE)
        if nome_r in NOTA_TEMP:
            nota(tp, NOTA_TEMP[nome_r])
        dl = campo(ws, 39, r, 5, "±", None, pt=11, cor=OSSO, nome=SERIE)
        R[nome_r], R[nome_r + "_max"] = ca, cm
        R[nome_r + "_temp"] = f"${L(32)}${tp.row}"
        R[nome_r + "_delta"] = f"${L(39)}${dl.row}"
        r += 4
    ITG, ITGM = R["integridade"], R["integridade_max"]
    R["estagio_alma"] = f"${L(4)}${r}"
    txt(ws, 4, r,
        f'=IF({ITG}=""," ",IF({ITG}<=0,"estágio 4 · você não é mais você",'
        f'IF({ITG}<={ITGM}/4,"estágio 3 · desvantagem em ataques e TRs",'
        f'IF({ITG}<={ITGM}/2,"estágio 2 · metade do deslocamento, +1 PE por Classe",'
        f'IF({ITG}<={ITGM}*3/4,"estágio 1 · desvantagem em perícias","alma inteira")))))',
        nome=CORPO, pt=9, cor=TEXTO_FRACO, ate=(COLS, r))
    r += 3

    # -------------------------------------------------- 03 o que cai sozinho
    r = secao(ws, r, "03", "O QUE CAI SOZINHO")
    MAE = f'(1+COUNTIF({ref["m_maestria"]},"<="&{NIV}))'
    REFI = f'(1+COUNTIF({ref["m_marcos"]},"<="&{NIV}))'
    pos = lambda i: (4 + (i % 4) * 11, r + (i // 4) * 4)
    C_PROT, R_PROT = pos(1); C_EQUI, R_EQUI = pos(2)
    PROT, EQUI = f"${L(C_PROT)}${R_PROT+1}", f"${L(C_EQUI)}${R_EQUI+1}"
    # o Bloquear (peca 23) le a Defesa, que e o item 0 desta mesma grade —
    # a celula de valor dele nasce em pos(0), uma linha abaixo do rotulo.
    C_DEF, R_DEF = pos(0)
    DEFESA_CEL = f"${L(C_DEF)}${R_DEF+1}"
    campos = [
        ("defesa",        f'=10+{DES}+{PROT}', TITULO),
        ("proteção",      f'=IF({EQUI}="",FLOOR({REFI}/3,1)+1,{EQUI})', TITULO),
        ("equipamento",   None, DOCUMENTO),
        ("iniciativa",    f'="d20 + "&{DES}', TITULO),
        ("cd de feitiço", f'=10+2+{MAE}', TITULO),
        ("conjuração",    f'="d20 + "&(2+{MAE})', TITULO),
        ("corpo a corpo", f'="d20 + "&{FOR}', TITULO),
        ("à distância",   f'="d20 + "&{DES}', TITULO),
        ("maestria",      f'={MAE}', TITULO),
        ("deslocamento",  "9 m", TITULO),
        # peca 23: "2d10 + (Defesa - 11)". Novo na v0.221 do gerador — a
        # planilha viva ja tinha, o gerador nao.
        ("bloquear",      f'="2d10 + "&({DEFESA_CEL}-11)', TITULO),
    ]
    for i, (rot, val, fnt) in enumerate(campos):
        c1, rr = pos(i)
        campo(ws, c1, rr, 9, rot, val, pt=16, cor=OSSO if val else TEXTO, nome=fnt)
        R[rot] = f"${L(c1)}${rr+1}"
    r += 12

    # ------------------------------------------------------- 04 progressao
    r = secao(ws, r, "04", "PROGRESSÃO · você só digita o nível")
    prog = [("espaços de feitiço", f'=2+INT({NIV}/2)+COUNTIF({ref["m_marcos"]},"<="&{NIV})'),
            ("refino de graça",    f'={REFI}'),
            ("classe máxima",      f'=COUNTIF({ref["m_classe"]},"<="&{NIV})'),
            ("classe 0 grátis",    f'=2+COUNTIF({ref["m_classe0"]},"<="&{NIV})')]
    for i, (rot, val) in enumerate(prog):
        c1 = 4 + i * 11
        campo(ws, c1, r, 9, rot, val, pt=16, cor=OSSO, nome=TITULO)
        R[rot] = f"${L(c1)}${r+1}"
    r += 4

    # Uma linha de pericia OU oficio: Trein + Espec + nome + sigla + valor.
    # A Especializacao e a peca 11 SS3 do JJK---Project: do nivel 10 em
    # diante, no lugar de uma pericia/oficio NOVO no marco, voce especializa
    # um que ja treina e soma METADE da maestria por cima. A formula nao
    # trava nivel nem exige o Trein junto — decisao do Mizuki (17/10): fica
    # so na escolha do jogador, com a tabela de marco como referencia, do
    # mesmo jeito que o resto da ficha nao conta pericia/oficio treinado
    # contra o orcamento da criacao.
    # o bonus, igual nos dois casos: metade da maestria por cima de quem ja
    # treina, e a maestria inteira para quem so treinou.
    def _bonus(cc, rr):
        trein, espec = f"${L(cc)}${rr}", f"${L(cc+1)}${rr}"
        return f'IF({espec}=TRUE,{MAE}+INT({MAE}/2),IF({trein}=TRUE,{MAE},0))'

    # PERICIA: o atributo e FIXO. "Atletismo e sempre Forca" — peca 7 §4, e o
    # capitulo 12 do livro repete: "o atributo dela e o da tabela e nao muda".
    # Entao a formula aponta direto para a celula do atributo.
    def linha_pericia(cc, rr, nome_item, atributo, larg_nome=7):
        txt(ws, cc, rr, None, al="center", cor=OSSO)
        txt(ws, cc + 1, rr, None, al="center", cor=OSSO)
        txt(ws, cc + 2, rr, nome_item, nome=DOCUMENTO, pt=10, cor=TEXTO,
            ate=(cc + 1 + larg_nome, rr))
        c_atr = cc + 2 + larg_nome
        txt(ws, c_atr, rr, atributo[:3], nome=TITULO, pt=8, cor=LINHA,
            ate=(c_atr + 1, rr))
        cel_atr = f'${L(R["atr_" + atributo].column)}${R["atr_" + atributo].row}'
        txt(ws, c_atr + 2, rr, f'={cel_atr}+{_bonus(cc, rr)}',
            nome=TITULO, pt=10, cor=OSSO, al="right", ate=(c_atr + 3, rr))
        regua(ws, cc, rr + 1, c_atr + 3, TINTA)

    # OFICIO: o atributo NAO e fixo. A peca 7 §5 escreve o padrao de cada um e
    # fecha com a clausula que ela mesma chama de "a que importa" — *"o mestre
    # troca quando a ficcao pedir, e diz qual antes da rolagem"*. Se a formula
    # apontasse direto para uma celula de atributo, trocar na mesa exigiria
    # editar formula. Entao o atributo VIRA CELULA, pre-preenchida com o
    # padrao, e o total le dela por IFS — que e o que a planilha viva ja fazia.
    ATRS = CAT["atributos"]["lista"]
    def linha_oficio(cc, rr, nome_item, atributo_padrao, larg_nome=5, larg_atr=4):
        txt(ws, cc, rr, None, al="center", cor=OSSO)
        txt(ws, cc + 1, rr, None, al="center", cor=OSSO)
        txt(ws, cc + 2, rr, nome_item, nome=DOCUMENTO, pt=10, cor=TEXTO,
            ate=(cc + 1 + larg_nome, rr))
        c_atr = cc + 2 + larg_nome
        txt(ws, c_atr, rr, atributo_padrao, nome=CORPO, pt=9, cor=TEXTO_FRACO,
            ate=(c_atr + larg_atr - 1, rr))
        cel = f"${L(c_atr)}${rr}"
        # ⚠ IF ANINHADO, e nao IFS. O IFS e "future function" no formato xlsx:
        # sem o prefixo _xlfn. ele vira #NAME? — e com o prefixo o Google
        # Sheets, que e o destino de verdade, e que nao entende. O IF aninhado
        # funciona nos dois, e a planilha viva usa IFS so porque ela nasceu
        # nativa no Sheets e nunca passou por um .xlsx.
        # Achado recalculando de verdade: o IFERROR engolia o #NAME? e a
        # celula devolvia SO o bonus, calada. Numero errado sem aviso.
        escolha = "0"
        for a in reversed(ATRS):
            alvo = f'${L(R["atr_" + a].column)}${R["atr_" + a].row}'
            escolha = f'IF({cel}="{a}",{alvo},{escolha})'
        c_val = c_atr + larg_atr
        txt(ws, c_val, rr, f'={escolha}+{_bonus(cc, rr)}',
            nome=TITULO, pt=10, cor=OSSO, al="right", ate=(c_val + 1, rr))
        regua(ws, cc, rr + 1, c_val + 1, TINTA)
        return c_atr

    def cabecalho_treino(cols, rr):
        for gc in cols:
            txt(ws, gc, rr, "T", nome=TITULO, pt=7, cor=TEXTO_FRACO, al="center")
            txt(ws, gc + 1, rr, "E", nome=TITULO, pt=7, cor=TEXTO_FRACO, al="center")

    def contagem_treinados(grupos):
        """SUMPRODUCT em vez de somar dois COUNTIF: Trein E Espec marcados na
        mesma linha (o caso normal de uma especializacao de verdade) e UMA
        pericia treinada, nao duas."""
        partes = []
        for cc, r0, n in grupos:
            t = f"{L(cc)}{r0}:{L(cc)}{r0+n-1}"
            e = f"{L(cc+1)}{r0}:{L(cc+1)}{r0+n-1}"
            partes.append(f'SUMPRODUCT((({t}=TRUE)+({e}=TRUE))>0)')
        return "=" + "+".join(partes)

    # --------------------------------------------------------- 05 pericias
    r = secao(ws, r, "05", "PERÍCIAS · marque as 8 ou 9 treinadas", c2=30)
    n1 = 12
    n2 = len(CAT["pericias"]) - n1
    cabecalho_treino((4, 18), r)
    p0 = r + 1
    for i, (nome_p, d) in enumerate(CAT["pericias"].items()):
        cc, rr = 4 + (i // n1) * 14, p0 + (i % n1)
        linha_pericia(cc, rr, nome_p, d["atributo"])
    CAIXAS = [(4, p0, n1), (5, p0, n1), (18, p0, n2), (19, p0, n2)]
    R["perícias treinadas"] = contagem_treinados([(4, p0, n1), (18, p0, n2)])
    r = p0 + n1 + 1

    # ------------------------------------------------------------ 06 oficios
    r = secao(ws, r, "06", "OFÍCIOS · o atributo é sugestão — o mestre decide na mesa", c2=34)
    m1 = 6
    m2 = len(CAT["oficios"]) - m1
    cabecalho_treino((4, 18), r)
    o0 = r + 1
    for i, (nome_o, d) in enumerate(CAT["oficios"].items()):
        cc, rr = 4 + (i // m1) * 14, o0 + (i % m1)
        c_atr = linha_oficio(cc, rr, nome_o, d["atributo_padrao"])
        # o menu: o mestre troca o atributo aqui, sem digitar errado
        dv(ref["Atributos"], c_atr, rr, c_atr, rr)
    CAIXAS += [(4, o0, m1), (5, o0, m1), (18, o0, m2), (19, o0, m2)]
    R["ofícios treinados"] = contagem_treinados([(4, o0, m1), (18, o0, m2)])
    r = o0 + m1 + 1

    # ----------------------------------------- 07 testes de resistencia
    r = secao(ws, r, "07", "TESTES DE RESISTÊNCIA", c2=24)
    TRS = [t for t, v in CAT["testes_de_resistencia"].items() if isinstance(v, dict)]
    BON = CAT["testes_de_resistencia"]["bonus_se_treinado"]
    for i, t in enumerate(TRS):
        rr = r + i
        txt(ws, 4, rr, None, al="center", cor=OSSO)
        txt(ws, 5, rr, t, nome=DOCUMENTO, pt=10, ate=(12, rr))
        atr = CAT["testes_de_resistencia"][t]["atributo"]
        txt(ws, 13, rr, " ou ".join(a[:3] for a in atr), nome=TITULO, pt=8,
            cor=LINHA, ate=(17, rr))
        cel_atr = f'${L(R["atr_"+atr[0]].column)}${R["atr_"+atr[0]].row}'
        txt(ws, 18, rr, f'={cel_atr}+IF(${L(4)}${rr}=TRUE,{BON},0)',
            nome=TITULO, pt=10, cor=OSSO, al="right", ate=(24, rr))
        regua(ws, 4, rr + 1, 24, TINTA)
    CAIXAS.append((4, r, len(TRS)))
    r += len(TRS) + 2

    # -------------------------------------------- 08 aptidoes e feiticos
    # O maximo de espacos de feitico e de Classe 0 sai das MESMAS formulas da
    # secao 04 — nao e escolha, e' o teto em nivel 30. 24 e 5, medido:
    #   espacos(30) = 2 + INT(30/2) + COUNTIF(marcos<=30)   = 2+15+7 = 24
    #   classe0(30) = 2 + COUNTIF([5,11,17]<=30)            = 2+3   = 5
    # A tabela nasce com esse tamanho fixo — sobra em nivel baixo, e o
    # contador (nao a quantidade de linha) e' quem diz quanto usar.
    MARCOS = CAT["progressao"]["marcos"]
    ESPACOS_MAX = 2 + 30 // 2 + sum(1 for m in MARCOS if m <= 30)
    CLASSE0_MAX = 2 + sum(1 for m in (5, 11, 17) if m <= 30)
    r = secao(ws, r, "08", "APTIDÕES E FEITIÇOS", c2=30)

    # -- feiticos de Classe 0: gratis, sem orcamento — so nome, forma e efeito
    txt(ws, 4, r, "CLASSE 0 · GRÁTIS, NÃO OCUPAM ESPAÇO", nome=TITULO, pt=9,
        cor=TEXTO_FRACO, ate=(20, r))
    r += 1
    c0_nome_ini = r
    for i in range(CLASSE0_MAX):
        rr = r + i
        txt(ws, 4, rr, None, nome=DOCUMENTO, pt=10, cor=TEXTO, ate=(13, rr))
        txt(ws, 14, rr, None, nome=DOCUMENTO, pt=10, cor=TEXTO_FRACO, ate=(22, rr))
        txt(ws, 23, rr, None, nome=CORPO, pt=9, cor=TEXTO_FRACO, ate=(COLS, rr))
        regua(ws, 4, rr + 1, COLS, TINTA)
    r += CLASSE0_MAX + 1

    # -- feiticos conhecidos: Classe entra, Pontos e PE saem sozinhos (3xClasse,
    # peca 19 — "o mesmo numero dos pontos"). O jogador so digita nome, forma e
    # o que a Melhoria/Restricao faz.
    txt(ws, 4, r, "CLASSE", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    txt(ws, 7, r, "NOME", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    txt(ws, 17, r, "FORMA", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    txt(ws, 24, r, "PONTOS / PE", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    txt(ws, 28, r, "MELHORIAS · RESTRIÇÕES · O QUE FAZ", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    r += 1
    f_ini = r
    for i in range(ESPACOS_MAX):
        rr = r + i
        cl = txt(ws, 4, rr, None, nome=DOCUMENTO, pt=10, cor=OSSO, al="center", ate=(6, rr))
        txt(ws, 7, rr, None, nome=DOCUMENTO, pt=10, cor=TEXTO, ate=(16, rr))
        txt(ws, 17, rr, None, nome=DOCUMENTO, pt=10, cor=TEXTO_FRACO, ate=(23, rr))
        cel_cl = f"${L(4)}${rr}"
        txt(ws, 24, rr, f'=IF({cel_cl}="","",{cel_cl}*3)', nome=TITULO, pt=10,
            cor=OSSO, al="center", ate=(27, rr))
        txt(ws, 28, rr, None, nome=CORPO, pt=9, cor=TEXTO_FRACO, ate=(COLS, rr))
        regua(ws, 4, rr + 1, COLS, TINTA)
    r += ESPACOS_MAX + 1

    # -- Passivas PAGAS: elas comem espaco de feitico, e o preco e a propria
    # Classe (manual, secao 1: "Classe 1 · 1 espaço", "2 · 2 espaços",
    # "3 · 3 espaços"). Teto de CINCO pagas; a Livre nao conta e mora na secao
    # de baixo.
    PASSIVAS_MAX = 5
    txt(ws, 4, r, "PASSIVAS PAGAS · custam espaço de feitiço, e a Classe é o preço. Máximo 5",
        nome=TITULO, pt=9, cor=TEXTO_FRACO, ate=(30, r))
    r += 1
    txt(ws, 4, r, "CLASSE", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    txt(ws, 7, r, "NOME", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    txt(ws, 17, r, "O QUE ELA FAZ SOZINHA", nome=TITULO, pt=8, cor=TEXTO_FRACO)
    r += 1
    p_ini = r
    for i in range(PASSIVAS_MAX):
        rr = r + i
        txt(ws, 4, rr, None, nome=DOCUMENTO, pt=10, cor=OSSO, al="center", ate=(6, rr))
        txt(ws, 7, rr, None, nome=DOCUMENTO, pt=10, cor=TEXTO, ate=(16, rr))
        txt(ws, 17, rr, None, nome=CORPO, pt=9, cor=TEXTO_FRACO, ate=(COLS, rr))
        regua(ws, 4, rr + 1, COLS, TINTA)
    r += PASSIVAS_MAX + 1

    # o contador: linhas usadas contra o que a peca 8/12 liberou neste nivel.
    # COUNTIF(">0") conta SLOT preenchido, nao ponto gasto — a v0.221 da
    # planilha viva corrigiu o mesmo erro (somava ponto onde devia contar
    # espaco). Ja a Passiva e SOMA e nao contagem, porque a Classe dela E o
    # preco em espaco: uma Classe 3 come tres.
    ESP, CLZ = R["espaços de feitiço"], R["classe 0 grátis"]
    faixa_cl = f"${L(4)}${f_ini}:${L(4)}${f_ini+ESPACOS_MAX-1}"
    faixa_c0 = f"${L(4)}${c0_nome_ini}:${L(4)}${c0_nome_ini+CLASSE0_MAX-1}"
    faixa_ps = f"${L(4)}${p_ini}:${L(4)}${p_ini+PASSIVAS_MAX-1}"
    R["feitiços status"] = (
        f'="Disponível: "&({ESP}-COUNTIF({faixa_cl},">0")-SUM({faixa_ps}))'
        f'&" · Conhecidos: "&{ESP}'
        f'&" · Passivas: "&COUNTIF({faixa_ps},">0")&"/{PASSIVAS_MAX}"'
        f'&" · Classe 0: "&({CLZ}-COUNTIF({faixa_c0},"<>"))&"/"&{CLZ}'
    )
    txt(ws, 4, r, R["feitiços status"], nome=CORPO, pt=10, cor=TEXTO_FRACO, ate=(COLS, r))
    r += 2

    # -- passiva livre, peca 8 passo 5: uma, de graca, e ela NAO conta no teto
    # de cinco nem come espaco — "A Passiva Livre não conta", no manual.
    r = secao(ws, r, "09", "PASSIVA LIVRE · de graça, fora do teto. Não rola dado, não muda número", c2=38)
    txt(ws, 4, r, None, nome=CORPO, pt=10, cor=TEXTO, ate=(COLS, r + 2))
    r += 4

    # -- anotacoes: texto livre, sem numero de regra dentro
    r = secao(ws, r, "10", "ANOTAÇÕES")
    txt(ws, 4, r, None, nome=CORPO, pt=10, cor=TEXTO_FRACO, ate=(COLS, r + 4))
    r += 6

    R["_caixas"] = CAIXAS          # o script le daqui: nada de contar no olho
    arte(ws, "respingo.png", 43, r - 3, 90)
    return R
