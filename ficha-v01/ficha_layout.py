# -*- coding: utf-8 -*-
"""O desenho que mudou a pedido da mesa em 17/09/2026. E a limpeza 13, e roda antes de todas.

Ela mexe so em desenho -- mesclagem, estilo, rotulo, texto fixo, imagem e margem --, e roda primeiro
porque o indice da DADOS e as contas saem dos rotulos que ela deixa. O que ela faz:

  - a caixinha de Buff/Debuff sai do EQUIPAMENTO e vai para o lado da DEFESA, e a INICIATIVA, a CD de
    feitico, a CONJURACAO, o CORPO A CORPO, o A DISTANCIA e o DESLOCAMENTO ganham uma igual: a caixa
    perde as duas ultimas colunas, e elas viram a caixinha, no estilo da que o Mizuki desenhou;
  - o Marco Escolhido passa a dizer Refino, Corpo e Leque, que e o nome do livro;
  - as caixas de marcar ficam centralizadas;
  - a caixa das escolhas de pericia fica em letra menor, para a frase caber em duas linhas;
  - na CARTEIRA, a foto cresce uma coluna de cada lado e tres linhas para baixo, com a moldura
    redesenhada na proporcao nova; o nome do sistema sai da DADOS; o portador e o registrado por
    ganham texto de exemplo; e a MESA DE ORIGEM vira SERVIDOR USADO;
  - a CARTEIRA, a INVOCACAO e o CATALOGO ganham a coluna de respiro da direita que a FICHA ja tinha, e
    o CATALOGO perde as colunas pintadas que sobravam depois dela;
  - a caixa da ORIGEM, na CARTEIRA, perde tamanho de fonte -- o nome mais comprido estourava a caixa.

Nenhum endereco esta escrito: tudo sai dos rotulos e das mesclagens da planilha viva.
"""
import json, os, re

import indice_ficha as ix

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))
COM_BUFF = ["DEFESA", "INICIATIVA", "CD DE FEITIÇO", "CONJURAÇÃO", "CORPO A CORPO", "À DISTÂNCIA", "DESLOCAMENTO"]
MARCOS = {"Atributo": "Corpo", "Feitiço": "Leque"}
FONTE_DAS_ESCOLHAS = 10.0
FONTE_DA_ORIGEM = 10.0
NOME_PORTADOR = "Coloque o nome do personagem aqui"
NICK = "Nick do jogador"
FOTO_A_MAIS = {"esquerda": 1, "direita": 1, "baixo": 3}


def _aba(layout, nome):
    return ix._aba(layout, nome)


def _estilo(layout, base, **mudar):
    """o indice de um estilo igual ao `base` com os campos trocados; cria se nao existir"""
    fonte, fundo, bordas, alinha, fmt = (json.loads(json.dumps(layout["estilos"][base])) if base is not None
                                         else [None, None, None, None, None])
    if "alinha" in mudar:
        alinha = mudar["alinha"]
    if "fonte" in mudar:
        fonte = mudar["fonte"]
    if "fundo" in mudar:
        fundo = mudar["fundo"]
    novo = [fonte, fundo, bordas, alinha, fmt]
    chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(novo)
    return len(layout["estilos"]) - 1


def _merge_de(aba, coord):
    return next((m for m in aba["mescladas"] if m.split(":")[0] == coord), None)


def _cobre(m, lin, col):
    a, b = m.split(":")
    (l1, c1), (l2, c2) = ix._lc(a), ix._lc(b)
    return l1 <= lin <= l2 and c1 <= col <= c2


def trocas(layout, CAT=None):
    """{"celulas": {aba: {coord: (valor, estilo)}}, "mescladas_sai", "mescladas", "celulas_sai",
    "imagens", "larguras", "arte"} -- o estilo e o indice em layout["estilos"], que pode ter crescido"""
    L = layout
    cel, sai, entra, some, imagens, larguras, arte = {}, {}, {}, {}, {}, {}, {}

    def poe(aba, coord, valor, estilo):
        cel.setdefault(aba, {})[coord] = (valor, estilo)

    ficha = _aba(L, "FICHA")
    fcel = {r[0]: r for r in ficha["celulas"]}
    est = lambda c: fcel.get(c, [None, None, None])[2]
    val = lambda c: fcel.get(c, [None, None, None])[1]

    # --- 1. as caixinhas de Buff/Debuff ---------------------------------------------------------
    buffs = sorted((c for c, r in fcel.items() if r[1] == "Buff/Debuff"), key=ix._lc)
    if buffs:
        molde = buffs[0]                                   # a que o Mizuki desenhou
        lb, cb = ix._lc(molde)
        m_lab = [m for m in ficha["mescladas"] if _cobre(m, lb, cb - 1) and m.split(":")[0] != molde][0]
        rot_eq = m_lab.split(":")[0]
        v_eq = _merge_de(ficha, f"{re.match(r'[A-Z]+', rot_eq).group(0)}{lb + 1}")
        v_bf = _merge_de(ficha, f"{re.match(r'[A-Z]+', molde).group(0)}{lb + 1}")
        c_bf1 = ix._lc(molde)[1]
        E_BUFF = {"rot1": est(molde), "rot2": est(f"{ix._letras(c_bf1 + 1)}{lb}"),
                  "val1": est(f"{ix._letras(c_bf1)}{lb + 1}"), "val2": est(f"{ix._letras(c_bf1 + 1)}{lb + 1}")}
        # o EQUIPAMENTO volta a ser uma caixa so: as duas colunas do Buff voltam para ela
        if val(rot_eq) == "EQUIPAMENTO":
            c0 = ix._lc(rot_eq)[1]
            fim = ix._lc(molde)[1] + 1
            for lin, m_main, m_buff in ((lb, m_lab, _merge_de(ficha, molde)), (lb + 1, v_eq, v_bf)):
                sai.setdefault("FICHA", []).extend([m_main, m_buff])
                entra.setdefault("FICHA", []).append(f"{ix._letras(c0)}{lin}:{ix._letras(fim)}{lin}")
                borda = est(m_main.split(":")[1])
                meio = est(f"{ix._letras(c0 + 1)}{lin}")
                for col in range(ix._lc(m_main.split(":")[1])[1], fim + 1):
                    poe("FICHA", f"{ix._letras(col)}{lin}", None, borda if col == fim else meio)
        for rot in COM_BUFF:
            achados = [c for c, r in fcel.items() if isinstance(r[1], str) and r[1].strip() == rot]
            if len(achados) != 1:
                continue
            r0 = achados[0]
            lr, c0 = ix._lc(r0)
            m_r = _merge_de(ficha, r0)
            if not m_r:
                continue
            c1 = ix._lc(m_r.split(":")[1])[1]
            vizinho = f"{ix._letras(c1 - 1)}{lr}"
            if val(vizinho) == "Buff/Debuff":                # ja tem
                continue
            m_v = _merge_de(ficha, f"{ix._letras(c0)}{lr + 1}")
            for lin, m_main, e1, e2, v in ((lr, m_r, E_BUFF["rot1"], E_BUFF["rot2"], "Buff/Debuff"),
                                           (lr + 1, m_v, E_BUFF["val1"], E_BUFF["val2"], 0)):
                sai.setdefault("FICHA", []).append(m_main)
                entra.setdefault("FICHA", []).extend([f"{ix._letras(c0)}{lin}:{ix._letras(c1 - 2)}{lin}",
                                                      f"{ix._letras(c1 - 1)}{lin}:{ix._letras(c1)}{lin}"])
                poe("FICHA", f"{ix._letras(c1 - 2)}{lin}", val(f"{ix._letras(c1 - 2)}{lin}"), est(f"{ix._letras(c1)}{lin}"))
                poe("FICHA", f"{ix._letras(c1 - 1)}{lin}", v, e1)
                poe("FICHA", f"{ix._letras(c1)}{lin}", None, e2)
        for c in buffs:                                    # a caixinha velha do EQUIPAMENTO some
            if c == molde and val(rot_eq) == "EQUIPAMENTO":
                poe("FICHA", c, None, cel["FICHA"].get(c, (None, est(c)))[1])
                poe("FICHA", f"{ix._letras(ix._lc(c)[1])}{lb + 1}", None,
                    cel["FICHA"].get(f"{ix._letras(ix._lc(c)[1])}{lb + 1}", (None, est(f'{ix._letras(ix._lc(c)[1])}{lb + 1}')))[1])

    # --- 2. Refino, Corpo e Leque -----------------------------------------------------------------
    marco = [c for c, r in fcel.items() if r[1] == "Marco Escolhido"]
    if marco:
        lm = ix._lc(marco[0])[0]
        for c, r in fcel.items():
            if ix._lc(c)[0] == lm and r[1] in MARCOS:
                poe("FICHA", c, MARCOS[r[1]], est(c))

    # --- 3. as caixas de marcar, centralizadas -----------------------------------------------------
    for c, r in fcel.items():
        if isinstance(r[1], bool):
            base = cel.get("FICHA", {}).get(c, (r[1], r[2]))[1]
            e = L["estilos"][base] if base is not None else None
            alinha = (e[3] if e and e[3] else [None, None, False, 0])
            if alinha[0] != "center":
                poe("FICHA", c, r[1], _estilo(L, base, alinha=["center", "center", alinha[2], alinha[3]]))

    # --- 3b. a caixa das escolhas de perícia, em letra menor ---------------------------------------
    # o Mizuki desenhou "Escolha uma Pericia ou Oficio" em 14, numa linha so; a frase que a limpeza 12 escreve
    # junta o que falta da criacao e do marco de Corpo, e em 14 ela corta. Em FONTE_DAS_ESCOLHAS cabem duas linhas.
    for c, r in fcel.items():
        v = r[1]
        if isinstance(v, str) and (ix._norm(v).startswith("escolha uma pericia") or
                                   (v.startswith("=") and "Tudo escolhido" in v)):
            e = L["estilos"][r[2]] if r[2] is not None else None
            if e and e[0] and e[0][1] != FONTE_DAS_ESCOLHAS:
                poe("FICHA", c, v, _estilo(L, r[2], fonte=[e[0][0], FONTE_DAS_ESCOLHAS] + e[0][2:]))

    # --- 3c. ANOTACOES RAPIDAS vira o titulo de TREINAMENTO EM ARMAS: o corpo (o texto do que o Caminho
    #     treina, o menu da troca de pericia por arma e o rotulo que muda) e da ficha_automatica.py, que
    #     sabe o Caminho e o manual. 17/09/2026, pedido do Mizuki.
    for c, r in fcel.items():
        if isinstance(r[1], str) and r[1].strip() == "ANOTAÇÕES RÁPIDAS":
            poe("FICHA", c, "TREINAMENTO EM ARMAS", est(c))
            lt, ct = ix._lc(c)
            # a troca de pericia por arma e o rotulo que muda: destaque no roxo que ja separa linha
            # na zebra do CATALOGO (FF3D2E78), pra distinguir do "treinado em" e da linha livre
            for desloc in (3, 5):
                alvo = f"{ix._letras(ct)}{lt + desloc}"
                if est(alvo) is not None:
                    poe("FICHA", alvo, val(alvo), _estilo(L, est(alvo), fundo="FF3D2E78"))
            # a linha da Empunhadura (a de baixo) herdou a letra grande da caixa de notas livres --
            # o texto do aviso e mais comprido, entao a fonte cai pra 10, achado do Mizuki em 17/09/2026
            alvo7 = f"{ix._letras(ct)}{lt + 7}"
            if est(alvo7) is not None:
                e7 = L["estilos"][est(alvo7)]
                if e7[0]:
                    poe("FICHA", alvo7, val(alvo7), _estilo(L, est(alvo7), fonte=[e7[0][0], 10.0] + e7[0][2:]))

    # --- 4. a CARTEIRA -----------------------------------------------------------------------------
    cart = _aba(L, "CARTEIRA")
    ccel = {r[0]: r for r in cart["celulas"]}
    cest = lambda c: ccel.get(c, [None, None, None])[2]
    for c, r in ccel.items():
        v = r[1]
        if isinstance(v, str) and v.strip().upper() == "ERA DA REVOLUÇÃO":
            poe("CARTEIRA", c, "=UPPER(DADOS!$F$1)", cest(c))
        elif v == "MESA DE ORIGEM":
            poe("CARTEIRA", c, "SERVIDOR USADO", cest(c))
        elif v == "PORTADOR":
            alvo = ix._letras(ix._lc(c)[1]) + str(ix._lc(c)[0] + 1)
            if ccel.get(alvo, [None, None])[1] != NOME_PORTADOR:
                poe("CARTEIRA", alvo, NOME_PORTADOR, cest(alvo))
        elif v == "REGISTRADO POR":
            alvo = ix._letras(ix._lc(c)[1]) + str(ix._lc(c)[0] + 1)
            if ccel.get(alvo, [None, None])[1] in (None, ""):
                poe("CARTEIRA", alvo, NICK, cest(alvo))
        elif v == "ORIGEM":
            # 17/09/2026, achado do Mizuki no teste do B23: "Sem Técnica, com uma das cinco
            # principais" mede 385px em Castoro 15, contra ~304px de caixa -- estoura. Em 10 cabem
            # folgados os nove nomes de Origem, inclusive o mais longo.
            alvo = ix._letras(ix._lc(c)[1]) + str(ix._lc(c)[0] + 1)
            rv = ccel.get(alvo)
            if rv and rv[2] is not None:
                e = L["estilos"][rv[2]]
                if e[0] and e[0][1] != FONTE_DA_ORIGEM:
                    poe("CARTEIRA", alvo, rv[1], _estilo(L, rv[2], fonte=[e[0][0], FONTE_DA_ORIGEM] + e[0][2:]))
    for c, r in fcel.items():                                 # o cabecalho pequeno da FICHA
        if isinstance(r[1], str) and r[1].strip().upper() == "ERA DA REVOLUÇÃO":
            poe("FICHA", c, "=UPPER(DADOS!$F$1)", r[2])
    # a foto: a imagem da moldura, e a caixa dela
    fotos = [i for i in cart["imagens"] if i["larg"] < i["alt"] and i["alt"] > 150]
    if fotos:
        foto = fotos[0]
        larg_px = round(8 * L["_meta"]["largura_limpa"]["exportada"] - 1)
        alt = {int(r): round(p * 4 / 3) for r, p in cart["linhas_alt"]}
        rpx = lambda r: alt.get(r, 21)
        caixa_velha = next((m for m in cart["mescladas"] if m.split(":")[0] == f"{ix._letras(foto['col'])}{foto['lin']}"), None)
        c_ini = foto["col"] - FOTO_A_MAIS["esquerda"]
        if caixa_velha:
            (l1, c1), (l2, c2) = ix._lc(caixa_velha.split(":")[0]), ix._lc(caixa_velha.split(":")[1])
            c_fim, l_fim = c2 + FOTO_A_MAIS["direita"], l2 + FOTO_A_MAIS["baixo"]
            nova = dict(foto, col=c_ini, larg=larg_px * (c_fim - c_ini + 1),
                        alt=sum(rpx(r) for r in range(l1, l_fim + 1)), desloc_x=0, desloc_y=0)
            imagens["CARTEIRA"] = [nova if i is foto else i for i in cart["imagens"]]
            sai.setdefault("CARTEIRA", []).append(caixa_velha)
            entra.setdefault("CARTEIRA", []).append(f"{ix._letras(c_ini)}{l1}:{ix._letras(c_fim)}{l_fim}")
            for lin in range(l1, l_fim + 1):
                for col in range(c_ini, c_fim + 1):
                    k = f"{ix._letras(col)}{lin}"
                    if ccel.get(k, [None, None])[1] not in (None, ""):
                        raise SystemExit(f"a foto maior cairia em CARTEIRA!{k}, que tem valor")
            arte[foto["arquivo"]] = (nova["larg"], nova["alt"])

    # --- 5. a coluna de respiro da direita ---------------------------------------------------------
    for nome in ("CARTEIRA", "INVOCAÇÃO", "CATÁLOGO"):
        aba = _aba(L, nome)
        acel = {r[0]: r for r in aba["celulas"]}
        fim_caixas = max(ix._lc(m.split(":")[1])[1] for m in aba["mescladas"])
        for c, r in acel.items():                       # a ultima coluna com borda de caixa
            e = L["estilos"][r[2]] if r[2] is not None else None
            if e and e[2]:
                fim_caixas = max(fim_caixas, ix._lc(c)[1])
        margem = fim_caixas + 1
        linhas = sorted({ix._lc(c)[0] for c in acel})
        for lin in linhas:
            fundo = None
            for col in range(fim_caixas, 0, -1):         # o fundo da linha: a celula solta, sem borda
                k = f"{ix._letras(col)}{lin}"
                if any(_cobre(m, lin, col) for m in aba["mescladas"]):
                    continue
                r = acel.get(k)
                e = L["estilos"][r[2]] if r and r[2] is not None else None
                if e and e[1] and not e[2]:
                    fundo = r[2]
                    break
            poe(nome, f"{ix._letras(margem)}{lin}", None, fundo)
        for c, r in acel.items():                        # o que passa da margem sai
            if ix._lc(c)[1] > margem:
                some.setdefault(nome, []).append(c)
        larguras[nome] = margem
    return {"celulas": cel, "mescladas_sai": sai, "mescladas": entra, "celulas_sai": some,
            "imagens": imagens, "larguras": larguras, "arte": arte}


def aplica(layout, tr):
    n = 0
    for nome, cels in tr["celulas"].items():
        aba = _aba(layout, nome)
        por = {r[0]: r for r in aba["celulas"]}
        for coord, (valor, estilo) in cels.items():
            if coord in por:
                if por[coord][1] != valor or por[coord][2] != estilo:
                    por[coord][1], por[coord][2] = valor, estilo
                    n += 1
            else:
                aba["celulas"].append([coord, valor, estilo])
                n += 1
    for nome, cs in tr["celulas_sai"].items():
        aba = _aba(layout, nome)
        antes = len(aba["celulas"])
        aba["celulas"] = [r for r in aba["celulas"] if r[0] not in cs]
        n += antes - len(aba["celulas"])
    for nome, ms in tr["mescladas_sai"].items():
        aba = _aba(layout, nome)
        aba["mescladas"] = [m for m in aba["mescladas"] if m not in ms]
    for nome, ms in tr["mescladas"].items():
        aba = _aba(layout, nome)
        aba["mescladas"] += [m for m in ms if m not in aba["mescladas"]]
    for nome, ims in tr["imagens"].items():
        _aba(layout, nome)["imagens"] = ims
    for nome, fim in tr["larguras"].items():
        aba = _aba(layout, nome)
        largs = aba["colunas_larg"]
        if largs and largs[-1][1] != fim:
            largs[-1][1] = fim
            n += 1
        aba["colunas"] = fim
    return n


def desenha_arte(tr):
    """a moldura da foto redesenhada na proporcao da caixa nova, com a arte de arte/gera.py"""
    import sys
    sys.path.insert(0, os.path.join(RAIZ, "arte"))
    import gera
    for arquivo, (larg, alt) in tr["arte"].items():
        escala = 460 / alt                               # a moldura foi desenhada com 460 de altura
        # SEM fundo: até 19/09/2026 a moldura levava um miolo roxo-escuro quase opaco, que não muda
        # de paleta — numa paleta clara ficava uma caixa preta no meio do cartão. Só o contorno e o
        # "FOTO 顔" ficam, e o miolo é o fundo da célula, que segue o tema.
        img = gera.moldura(larg=round(larg * escala), alt=460, fundo=(0, 0, 0, 0))
        img.save(os.path.join(AQUI, "arte", arquivo))
    _pincelada_de_meio_tom(os.path.join(AQUI, "arte", "carteira-3.png"))


# a cor da pincelada clara do meio da CARTEIRA: tinha o osso (E0D0D0) e sumia inteira sobre o fundo
# claro de uma paleta clara. Luminância relativa de 0,17 — a que dá o MESMO contraste (4,0) contra o
# mais escuro (o tinta dos temas escuros) e contra o mais claro (o tinta dos claros) —, porque uma
# imagem não troca de cor com a paleta e precisa ler nas duas pontas.
PINCELADA_DE_MEIO_TOM = (130, 112, 108)


def _pincelada_de_meio_tom(caminho):
    from PIL import Image
    if not os.path.exists(caminho):
        return
    img = Image.open(caminho).convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            a = px[x, y][3]
            if a:
                px[x, y] = PINCELADA_DE_MEIO_TOM + (a,)
    img.save(caminho)
