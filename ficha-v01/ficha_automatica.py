# -*- coding: utf-8 -*-
"""A ficha que conta sozinha: os X de Y, os marcos e as Passivas do Leque. E a limpeza 12.

Em 17/09/2026 o Mizuki redesenhou a FICHA no Sheets: o atributo ganhou a caixa pequena (o que o jogador
distribui) embaixo da grande (o total), os pontos de marco de Corpo por atributo, o `Marco Escolhido`
com Refino, Atributo e Feitico, o `Buff/Debuff` da Defesa, e caixas `X de Y` em pontos, pericias,
oficios, Testes de Resistencia e aptidoes. Esta limpeza escreve as contas delas, e divide as Passivas
em normais e do Leque, com duas linhas a mais.

O que o livro decide, e de onde sai (tudo lido do manual.txt ou do catalogo):
  - atributo grande = pequeno + marcos de Corpo nele; pontos = os da criacao + 1 por marco; teto 6
  - cada marco escolhe Corpo, Refino ou Leque, uma escolha por marco que ja passou
  - Corpo: +1 pericia OU oficio, ou uma especializacao do nivel 10 em diante
  - criacao: 9 pericias e 2 oficios, ou 10 e nenhum -- a ficha deduz a rota (decisao do Mizuki, abaixo)
  - Refino: +1 aptidao, e 2 quando o refino ja esta no teto; 2 aptidoes de graca no refino 1
  - Leque: +1 espaco de feitico e +1 Passiva que nao custa espaco

Decisao do Mizuki sobre a rota do oficio: a ficha nao pergunta. Ela mostra o maximo de cada lista, e
quando o jogador marca alem da base de uma, entende que o marco de Corpo foi para ela; se marcar alem
nas duas, as duas caixas dizem quantos passaram. A conta: com p pericias, o oficios, s especializacoes
e c marcos de Corpo, o que sobra e `k = c - s`; passou quem nao cabe em nenhuma das duas rotas
(`min(max(0,p-9)+max(0,o-2), max(0,p-10)+max(0,o)) - k`); e o maximo de pericias e o melhor das duas
rotas descontando o que os oficios ja gastaram do Corpo, e o de oficios o inverso.

Aptidoes no teto: o livro da duas quando o refino ja esta no teto na hora de escolher, e isso depende
da ORDEM das escolhas, que a ficha nao guarda. Medido em 17/09/2026: a ordem so muda o numero em quatro
combinacoes, todas no nivel 26 ou 30, e em uma aptidao. A ficha conta as escolhas de Refino como as
ultimas, que e o jeito que da mais, e a nota da celula manda conferir com o mestre.
"""
import json, os, re

import indice_ficha as ix

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_NUM = {"uma": 1, "um": 1, "duas": 2, "dois": 2, "três": 3, "tres": 3, "quatro": 4, "cinco": 5,
        "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10}
LINHAS_A_MAIS = 2
ESCOLHA_CAMINHO = "Escolha seu Caminho"
ESCOLHA_TRILHA = "Escolha sua Trilha"
SEM_TECNICA = " · Sem Técnica"
from ficha_layout import NOME_PORTADOR
ROTULOS_CORRIGIDOS = {"Pontos Dísponíveis": "Pontos Disponíveis",
                      "Péricias Dispóniveis": "Perícias Disponíveis",
                      "Ofícios Dispóniveis": "Ofícios Disponíveis",
                      "Testes de Résistência Dispóniveis": "Testes de Resistência Disponíveis"}


def _so_col(coord):
    return re.match(r"[A-Z]+", coord).group(0)


def _n(p):
    return int(p) if p.isdigit() else _NUM[p.lower()]


def regras(CAT=None):
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    M = " ".join(open(os.path.join(RAIZ, "manual.txt"), encoding="utf-8").read().split())
    achar = {
        "com": r"ficando com os ofícios (\d+) de \d+ (\d+) de \d+",
        "troca": r"trocando os dois (\d+) de \d+ (\d+) de \d+",
        "gratis": r"No refino 1 você já tem (\w+) aptidões, de graça",
        "tetos": r"Teto de atributo: (\d+)\. Teto de refino: (\d+)\.",
        "no_teto": r"Se o seu refino já estiver no teto, você leva (\w+) aptidões",
        "especializa": r"Do nível (\d+) em diante, no lugar da perícia ou do ofício novo, você pode especializar",
    }
    m = {k: re.search(rx, M) for k, rx in achar.items()}
    falta = [k for k, v in m.items() if not v]
    if falta:
        raise SystemExit(f"nao achei no manual.txt as frases de {falta}")
    cr = CAT["atributos"]["criacao"]
    ga = re.search(r"duas aptidões, de graça: (.+?) , que dá .{0,80}?, e (.+?) , que permite", M)
    gb = re.search(r"(\w[\w ]+?) e (\w[\w ]+?) vêm de graça na Lapidação 1", M)
    sem = re.search(r"você escolhe uma semente: (\w+) aptidão que vem aberta", M)
    if not (ga and gb and sem):
        raise SystemExit("nao achei no manual.txt as aptidoes de graca, as Bencaos de graca ou a semente")
    rotas = CAT["rotas_de_criacao"]
    marcial = [r["origem"] for r in rotas if r["rota"] == "Técnica Marcial"]
    sem_energia = [o for o in marcial if "sem energia" in o]
    # 17/09/2026, achado do Mizuki: a mesma frase se repete no quadro de armas (capitulo 14), sem o
    # travessao em volta dos nomes e colada numa tabela de dados numericos -- sem ancorar no que vem
    # antes, o re.search pulava a ocorrencia limpa (bloqueada pelo travessao) e caia na sujeira.
    tz = re.search(r"corpo a corpo\s*—\s*([\w, ]+?)\s*—\s*treinam as treze categorias", M)
    du = re.search(r"conjuradores\s*—\s*([\w, ]+?)\s*—\s*treinam Arma de Fogo e Balestra", M)
    if not (tz and du):
        raise SystemExit("nao achei no manual.txt quem treina todas as armas e quem treina so duas")
    def _lista_e(s):
        return [p.strip() for p in s.replace(" e ", ", ").split(", ") if p.strip()]
    extra = {"aptidoes_de_graca": [ga.group(1), ga.group(2)], "bencaos_de_graca": [gb.group(1), gb.group(2)],
             "semente": _n(sem.group(1)), "marcial": marcial, "sem_energia": sem_energia[0],
             "caminhos_todas_armas": _lista_e(tz.group(1)), "caminhos_duas_armas": _lista_e(du.group(1))}
    return dict(extra, **{"pericias_com": int(m["com"].group(1)), "oficios_com": int(m["com"].group(2)),
            "pericias_troca": int(m["troca"].group(1)), "oficios_troca": int(m["troca"].group(2)),
            "aptidoes_gratis": _n(m["gratis"].group(1)), "aptidoes_no_teto": _n(m["no_teto"].group(1)),
            "teto_atributo": int(m["tetos"].group(1)), "teto_refino": int(m["tetos"].group(2)),
            "especializa": int(m["especializa"].group(1)),
            "pontos_criacao": cr["pontos"], "teto_criacao": cr["teto_por_atributo"],
            "testes": CAT["testes_de_resistencia"]["treinados_na_criacao"]})


def _A(c, aba=""):
    lin, col = ix._lc(c)
    return f"{aba}${ix._letras(col)}${lin}"


def _N(c, aba=""):
    return f'IFERROR(VALUE({_A(c, aba)}&""),0)'


def _faixas(celulas):
    """celulas de uma coluna em faixas continuas: ["D64:D74", "T63:T74"]"""
    por = {}
    for c in celulas:
        lin, col = ix._lc(c)
        por.setdefault(col, []).append(lin)
    out = []
    for col, lins in sorted(por.items()):
        lins.sort()
        ini = ant = lins[0]
        for l in lins[1:] + [None]:
            if l is not None and l == ant + 1:
                ant = l
                continue
            L = ix._letras(col)
            out.append(f"${L}${ini}:${L}${ant}")
            if l is not None:
                ini = ant = l
    return out


def _conta_verdade(faixas):
    return "+".join(f"COUNTIF(FICHA!{f},TRUE)" for f in faixas) or "0"


def trocas(layout, CAT=None):
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    R = regras(CAT)
    idx = ix.indice(layout)
    f = ix._Ficha(layout)
    ficha, dados = ix._aba(layout, "FICHA"), ix._aba(layout, "DADOS")
    fcel = {r[0]: r for r in ficha["celulas"]}
    dcel = {r[0]: r for r in dados["celulas"]}
    # a caixa de TREINAMENTO EM ARMAS: a limpeza 13 renomeia ANOTACOES RAPIDAS antes desta rodar, e
    # tem quatro linhas de duas alturas embaixo do titulo -- treinado em, a troca, e o rotulo que muda
    tit_armas = next((c for c, v in fcel.items() if isinstance(v[1], str) and v[1].strip() == "TREINAMENTO EM ARMAS"), None)
    if tit_armas is None:
        raise SystemExit("nao achei 'TREINAMENTO EM ARMAS' na FICHA: rode a limpeza 13 antes desta")
    _lt, _ct = ix._lc(tit_armas)
    TREINADO_EM = f"{ix._letras(_ct)}{_lt + 1}"
    TROCA_ARMA = f"{ix._letras(_ct)}{_lt + 3}"
    LABEL_EXTRA = f"{ix._letras(_ct)}{_lt + 5}"
    GRUPO_TRILHA = f"{ix._letras(_ct)}{_lt + 7}"      # a linha que sobrou livre: a Empunhadura do Arremate
    precisa = ["nivel", "refino de graça", "refino escolhido", "marco corpo", "marco leque", "marcos escolhidos",
               "pontos disponíveis", "pontos de corpo", "perícias disponíveis", "ofícios disponíveis",
               "testes disponíveis", "espaços de feitiço"] + \
              [p + n for p in ("atr_", "atr_base_", "corpo_") for n, _, _ in ix.ATRS]
    falta = [k for k in precisa if not idx.get(k)]
    if falta:
        raise SystemExit(f"a FICHA nao tem as caixas {falta}: a ficha automatica e da planilha de 17/09/2026")
    cel = {"FICHA": {}, "DADOS": {}}
    merges_sai, merges_entra, menus_troca = [], [], {}

    # --- os rotulos com erro de digitacao, e o segundo "3" das anotacoes, que e o 4
    for c, v in fcel.items():
        if isinstance(v[1], str) and v[1].strip() in ROTULOS_CORRIGIDOS:
            cel["FICHA"][c] = (ROTULOS_CORRIGIDOS[v[1].strip()], c)
    for base in ("Skill Base de Caminho", "Skill Base de Trilha"):
        achados = sorted((c for c, v in fcel.items() if isinstance(v[1], str) and v[1].startswith(base)), key=ix._lc)
        for i, c in enumerate(achados, start=1):
            if fcel[c][1] != f"{base} {i}":
                cel["FICHA"][c] = (f"{base} {i}", c)

    # --- as celulas de treino: o nome vem do catalogo, o treino fica duas colunas antes e a
    #     especializacao uma, e o Teste de Resistencia treina uma coluna antes
    def caixas(nomes, desloc):
        out = []
        for nome in nomes:
            c = next((k for k, v in fcel.items() if isinstance(v[1], str) and v[1].strip() == nome), None)
            if c is None:
                raise SystemExit(f"nao achei {nome!r} na FICHA")
            lin, col = ix._lc(c)
            alvo = f"{ix._letras(col - desloc)}{lin}"
            if not isinstance(fcel.get(alvo, [None, None])[1], bool):
                raise SystemExit(f"a caixa de {nome!r} devia estar em {alvo}")
            out.append(alvo)
        return out
    trs = [t for t, v in CAT["testes_de_resistencia"].items() if isinstance(v, dict)]
    PER_T, PER_E = caixas(CAT["pericias"], 2), caixas(CAT["pericias"], 1)
    OFI_T, OFI_E = caixas(CAT["oficios"], 2), caixas(CAT["oficios"], 1)
    TR_T = caixas(trs, 1)

    # --- a area das Passivas: cabecalho, linhas, e as duas a mais. Depois da primeira vez a planilha viva ja
    #     volta dividida e com as linhas novas, e a limpeza so reescreve o cabecalho do Leque.
    classe = sorted((c for c, v in fcel.items() if v[1] == "Classe" and ix._lc(c)[1] > ix._col("U")), key=ix._lc)
    cab = classe[0]
    lc, cc = ix._lc(cab)
    menu_p = next(m for m in ficha["menus"] if m["onde"].split()[0].startswith(ix._letras(cc)))
    faixas_p = menu_p["onde"].split()
    esq, dir_ = faixas_p[0], faixas_p[1]
    l_ini, l_fim = ix._lc(esq.split(":")[0])[0], ix._lc(esq.split(":")[1])[0]
    c_esq, c_dir = ix._lc(esq.split(":")[0])[1], ix._lc(dir_.split(":")[0])[1]
    cab_leque = [c for c, v in fcel.items() if ix._lc(c)[0] == lc and isinstance(v[1], str) and "Passivas do Leque" in v[1]]
    if cab_leque:
        novo_fim = l_fim
        c4 = ix._lc(cab_leque[0])[1]
        molde_cab = cab_leque[0]
    else:
        blocos = sorted((m for m in ficha["mescladas"] if ix._lc(m.split(":")[0])[0] == l_fim
                         and ix._lc(m.split(":")[0])[1] >= c_esq), key=lambda m: ix._lc(m.split(":")[0])[1])
        novo_fim = l_fim + LINHAS_A_MAIS
        for r in range(l_fim + 1, novo_fim + 1):
            if any(fcel.get(f"{ix._letras(col)}{r}", [None, None])[1] not in (None, "")
                   for col in range(c_esq, ix._lc(blocos[-1].split(":")[1])[1] + 1)):
                raise SystemExit(f"a linha {r} das Passivas ja tem valor")
            for col in range(c_esq, ix._lc(blocos[-1].split(":")[1])[1] + 1):
                L = ix._letras(col)
                cel["FICHA"][f"{L}{r}"] = (fcel.get(f"{L}{l_fim}", [None, None])[1] if col in (c_esq, c_dir) else None,
                                           f"{L}{l_fim}")
            for m in blocos:
                a, b = m.split(":")
                merges_entra.append(f"{_so_col(a)}{r}:{_so_col(b)}{r}")
        menus_troca[menu_p["onde"]] = " ".join(
            f"{_so_col(x.split(':')[0])}{l_ini}:{_so_col(x.split(':')[1])}{novo_fim}" for x in faixas_p)
        # o cabecalho: a faixa que ia das Passivas ate o fim vira duas, no molde das linhas de baixo
        cab_txt = next(m for m in ficha["mescladas"] if ix._lc(m.split(":")[0]) == (lc, cc + 2))
        fim_col = ix._lc(cab_txt.split(":")[1])[1]
        cols = sorted({ix._lc(m.split(":")[0])[1]: ix._lc(m.split(":")[1])[1] for m in blocos}.items())
        if len(cols) != 4:
            raise SystemExit(f"a linha das Passivas devia ter quatro caixas, tem {cols}")
        merges_sai.append(cab_txt)
        for ini_c, fim_c in cols:
            merges_entra.append(f"{ix._letras(ini_c)}{lc}:{ix._letras(fim_c)}{lc}")
        (c1, f1), (c2, f2), (c3, f3), (c4, f4) = cols
        for col in range(c2, fim_col + 1):                       # o estilo de cada celula do cabecalho
            L = ix._letras(col)
            if col == c2:
                ref = f"{L}{lc}"
            elif col == c3:
                ref = f"{ix._letras(c1)}{lc}"
            elif col in (f2, f3, f4):
                ref = f"{ix._letras(fim_col)}{lc}"
            elif col == c4:
                ref = f"{ix._letras(c2)}{lc}"
            else:
                ref = f"{ix._letras(c2 + 1)}{lc}"
            cel["FICHA"][f"{L}{lc}"] = (fcel.get(f"{L}{lc}", [None, None])[1] if col == c2 else None, ref)
        cel["FICHA"][f"{ix._letras(c3)}{lc}"] = ("Classe", f"{ix._letras(c1)}{lc}")
        molde_cab = f"{ix._letras(c2)}{lc}"

    # --- a lista de Feitiços ganha duas linhas, no molde da ultima -- o mesmo pedido que ja estendeu
    #     as Passivas (LINHAS_A_MAIS), mas cada lista tem o fim dela: a das Passivas mora nas colunas
    #     depois de "U", a dos Feitiços comeca em "D", e o COUNTIF do cabecalho e quem sabe onde ela
    #     acaba hoje. 17/09/2026, pedido do Mizuki.
    feit_hdr = next(c for c, v in fcel.items() if isinstance(v[1], str) and "Feitiços - Disponível" in v[1])
    m_ctf = re.search(r"COUNTIF\(([A-Z]+)(\d+):[A-Z]+(\d+),", fcel[feit_hdr][1])
    if not m_ctf:
        raise SystemExit("nao achei o COUNTIF da lista de Feitiços no cabecalho 'Feitiços - Disponível'")
    c_feit_letra, l_feit_ini, l_feit_fim = m_ctf.group(1), int(m_ctf.group(2)), int(m_ctf.group(3))
    c_feit = ix._col(c_feit_letra)
    blocos_feit = sorted((m for m in ficha["mescladas"] if ix._lc(m.split(":")[0])[0] == l_feit_fim
                          and c_feit <= ix._lc(m.split(":")[0])[1] < c_esq), key=lambda m: ix._lc(m.split(":")[0])[1])
    if len(blocos_feit) != 2:
        raise SystemExit(f"a linha dos Feitiços devia ter duas caixas (Classe e nome), achei {len(blocos_feit)}")
    novo_fim_feit = l_feit_fim + LINHAS_A_MAIS
    for r in range(l_feit_fim + 1, novo_fim_feit + 1):
        c_fim_feit = ix._lc(blocos_feit[-1].split(":")[1])[1]
        if any(fcel.get(f"{ix._letras(col)}{r}", [None, None])[1] not in (None, "")
               for col in range(c_feit, c_fim_feit + 1)):
            raise SystemExit(f"a linha {r} dos Feitiços ja tem valor")
        for col in range(c_feit, c_fim_feit + 1):
            Lc = ix._letras(col)
            cel["FICHA"][f"{Lc}{r}"] = (fcel.get(f"{Lc}{l_feit_fim}", [None, None])[1] if col == c_feit else None,
                                        f"{Lc}{l_feit_fim}")
        for m in blocos_feit:
            a, b = m.split(":")
            merges_entra.append(f"{_so_col(a)}{r}:{_so_col(b)}{r}")
    menus_troca[f"{c_feit_letra}{l_feit_ini}:{c_feit_letra}{l_feit_fim}"] = \
        f"{c_feit_letra}{l_feit_ini}:{c_feit_letra}{novo_fim_feit}"
    # o cabecalho cita a lista duas vezes (COUNTIF e COUNTIFS), e a segunda usa outra coluna (a do
    # nome, pra saber se a linha foi preenchida) -- toda faixa que termina na ultima linha da lista
    # move junto, senao o COUNTIFS fica com faixas de tamanho diferente e vira erro de referencia
    nova_formula_feit = re.sub(rf"([A-Z]+){l_feit_ini}:([A-Z]+){l_feit_fim}\b",
                               rf"\g<1>{l_feit_ini}:\g<2>{novo_fim_feit}", fcel[feit_hdr][1])
    cel["FICHA"][feit_hdr] = (nova_formula_feit, feit_hdr)

    # --- a lista de aptidoes: as mescladas que comecam na coluna das Passivas, entre o cabecalho de
    #     cima e o das Passivas
    ref_apt = idx.get("espaços de feitiço")
    atual = next(c for c, v in fcel.items() if isinstance(v[1], str) and "Refino Atual" in v[1])
    la, ca = ix._lc(atual)
    apt = sorted(ix._lc(m.split(":")[0])[0] for m in ficha["mescladas"]
                 if ix._lc(m.split(":")[0])[1] == ca and la < ix._lc(m.split(":")[0])[0] < lc)
    APT = f"${ix._letras(ca)}${apt[0]}:${ix._letras(ca)}${apt[-1]}"

    # --- a tabela de contas, escondida na DADOS, depois da tabela de equipamento
    lin_cab = ix._lc(next(r[0] for r in dados["celulas"] if r[1] == "marcos"))[0]
    eq = next((r[0] for r in dados["celulas"] if r[1] == "equipamento" and ix._lc(r[0])[0] == lin_cab), None)
    if eq is None:
        raise SystemExit("a tabela de equipamento da DADOS nao existe: rode a limpeza 10 antes desta")
    c_nome = ix._lc(eq)[1] + 5
    c_val = c_nome + 1
    ref_cab = next(r[0] for r in dados["celulas"] if r[1] == "marcos")
    ref_txt = next(r[0] for r in dados["celulas"] if ix._lc(r[0]) == (lin_cab + 1, 1))
    ref_num = f"{ref_cab[:-len(str(lin_cab))]}{lin_cab + 1}"
    H = {}
    contas = []

    def conta(nome, formula):
        lin = lin_cab + 1 + len(contas)
        H[nome] = f"DADOS!${ix._letras(c_val)}${lin}"
        contas.append((nome, formula))

    graca = fcel[idx["refino de graça"]][1]
    mc = re.search(r"COUNTIF\((DADOS![^,]+),", graca)
    NIV = _A(idx["nivel"], "FICHA!")
    ORI = _A(idx["origem"], "FICHA!")
    CAM = _A(idx["caminho"], "FICHA!")
    conta("marcos que já passou", f'=COUNTIF({mc.group(1)},"<="&{NIV})')
    conta("pontos de atributo", f"={R['pontos_criacao']}+{H['marcos que já passou']}")
    conta("pontos distribuídos", "=" + "+".join(_N(idx["atr_base_" + n], "FICHA!") for n, _, _ in ix.ATRS))
    conta("maior atributo", "=MAX(" + ",".join(_A(idx["atr_" + n], "FICHA!") for n, _, _ in ix.ATRS) + ")")
    conta("maior atributo pequeno", "=MAX(" + ",".join(_N(idx["atr_base_" + n], "FICHA!") for n, _, _ in ix.ATRS) + ")")
    conta("marcos de Corpo", "=" + _N(idx["marco corpo"], "FICHA!"))
    conta("pontos de Corpo usados", "=" + "+".join(_N(idx["corpo_" + n], "FICHA!") for n, _, _ in ix.ATRS))
    conta("marcos escolhidos", "=" + "+".join(_N(idx[k], "FICHA!") for k in ("refino escolhido", "marco corpo", "marco leque")))
    conta("perícias treinadas", "=" + _conta_verdade(_faixas(PER_T)))
    conta("ofícios treinados", "=" + _conta_verdade(_faixas(OFI_T)))
    conta("especializações", "=" + _conta_verdade(_faixas(PER_E + OFI_E)))
    conta("Corpo que sobra", f"={H['marcos de Corpo']}-{H['especializações']}")
    p, o, k = H["perícias treinadas"], H["ofícios treinados"], H["Corpo que sobra"]
    pc, oc, pt, ot = R["pericias_com"], R["oficios_com"], R["pericias_troca"], R["oficios_troca"]
    # a rota do oficio: fica a de 9 e 2 enquanto ela couber, e so passa para a de 10 e nenhum quando a de 9 e 2
    # deixa de caber e a outra cabe (decisao do Mizuki, 17/09/2026: a ficha nasce mostrando 9 e 2)
    e_com = f"(MAX(0,{p}-{pc})+MAX(0,{o}-{oc}))"
    e_tro = f"(MAX(0,{p}-{pt})+MAX(0,{o}-{ot}))"
    conta("rota do ofício", f"=IF({e_com}<={k},1,IF({e_tro}<={k},2,IF({e_com}<={e_tro},1,2)))")
    # a troca de pericia por arma: so nos tres Caminhos que nao treinam arma de verdade, e so conta se
    # o jogador marcou na caixa de TREINAMENTO EM ARMAS -- cada troca e 2 das cinco livres por 1 arma,
    # ate duas vezes (peca 07 §6 do sistema, e a extensao dela que o Mizuki confirmou em 17/09/2026)
    duas_or = "OR(" + ",".join(f'{CAM}="{n}"' for n in R["caminhos_duas_armas"]) + ")"
    TROCA_ARMA_F = _A(TROCA_ARMA, "FICHA!")   # esta conta mora na DADOS: sem o prefixo, AK65 lia a
                                              # propria DADOS, vazia, em vez da FICHA
    conta("perícias por arma", f'=IF({duas_or},IF({TROCA_ARMA_F}="2 armas (-4 pericias)",4,'
                                f'IF({TROCA_ARMA_F}="1 arma (-2 pericias)",2,0)),0)')
    conta("perícias da rota", f"=IF({H['rota do ofício']}=1,{pc},{pt})-{H['perícias por arma']}")
    conta("ofícios da rota", f"=IF({H['rota do ofício']}=1,{oc},{ot})")
    conta("Corpo nas perícias", f"=MAX(0,{p}-{H['perícias da rota']})")
    conta("Corpo nos ofícios", f"=MAX(0,{o}-{H['ofícios da rota']})")
    conta("Corpo por escolher", f"={k}-{H['Corpo nas perícias']}-{H['Corpo nos ofícios']}")
    conta("treinos a mais", f"=MAX(0,-{H['Corpo por escolher']})")
    # o que falta, na rota que a ficha mostra e na sem oficio: a caixa das escolhas diz as duas quando o jogador
    # esta na de 9 e 2 sem oficio marcado, porque ele pode ter trocado os oficios na criacao
    conta("perícias que faltam", f"=MAX(0,{H['perícias da rota']}-{p})")
    conta("ofícios que faltam", f"=MAX(0,{H['ofícios da rota']}-{o})")
    conta("perícias que faltam sem ofício", f"=MAX(0,{pt}-{p})")
    conta("Corpo por escolher sem ofício", f"={k}-MAX(0,{p}-{pt})-MAX(0,{o}-{ot})")
    conta("testes treinados", "=" + _conta_verdade(_faixas(TR_T)))
    conta("sem energia", f'=IF({ORI}="{R["sem_energia"]}",1,0)')
    conta("sem técnica", f'=IF(ISNUMBER(SEARCH("{SEM_TECNICA}",{ORI})),1,0)')
    conta("técnica marcial", "=IF(OR(" + ",".join(f'{ORI}="{o_}"' for o_ in R["marcial"]) + "),1,0)")
    conta("refino escolhido", f"=MIN({_N(idx['refino escolhido'], 'FICHA!')},{H['marcos que já passou']})")
    conta("refino atual", f"=MIN({R['teto_refino']},{_A(idx['refino de graça'], 'FICHA!')}+{H['refino escolhido']})")
    r_, m_ = H["refino escolhido"], H["marcos que já passou"]
    conta("aptidões a mais no teto",
          f"=MAX(0,{r_}-MAX(0,CEILING(({R['teto_refino']}-{m_}+{r_})/2,1)-1))*({R['aptidoes_no_teto']}-1)")
    conta("máximo de aptidões",
          f"={R['aptidoes_gratis']}+{R['semente']}*{H['sem técnica']}+{r_}+{H['aptidões a mais no teto']}")
    conta("aptidões anotadas", f'=COUNTIF(FICHA!{APT},"?*")')
    conta("escolhas de Leque", "=" + _N(idx["marco leque"], "FICHA!"))
    conta("Passivas do Leque anotadas",
          f'=COUNTIF(FICHA!${ix._letras(c_dir + 2)}${l_ini}:${ix._letras(c_dir + 2)}${novo_fim},"?*")')
    cel["DADOS"][f"{ix._letras(c_nome)}{lin_cab}"] = ("contas da ficha", ref_cab)
    cel["DADOS"][f"{ix._letras(c_val)}{lin_cab}"] = ("valor", ref_cab)
    for i, (nome, form) in enumerate(contas, start=1):
        cel["DADOS"][f"{ix._letras(c_nome)}{lin_cab + i}"] = (nome, ref_txt)
        cel["DADOS"][f"{ix._letras(c_val)}{lin_cab + i}"] = (form, ref_num)

    # --- os menus de Caminho e de Trilha, com a frase de escolher, e a Trilha filtrada pelo Caminho
    c_cam = c_val + 2
    DEC = json.load(open(os.path.join(RAIZ, "decisoes-ficha.json"), encoding="utf-8"))
    caminhos = DEC["C1_evocador"]["caminhos_no_menu"]
    trilhas = list(CAT["trilhas"])
    CAM = _A(idx["caminho"], "FICHA!")
    tab = [("menu de Caminho", [ESCOLHA_CAMINHO] + [f"=$A${4 + i}" for i in range(len(caminhos))]),
           ("Trilha", [f"=$L${4 + i}" for i in range(len(trilhas))]),
           ("Caminho da Trilha", [CAT["trilhas"][tr_] for tr_ in trilhas]),
           ("menu de Trilha", [ESCOLHA_TRILHA,
                               f'=IFERROR(FILTER(${ix._letras(c_cam + 1)}${lin_cab + 1}:${ix._letras(c_cam + 1)}${lin_cab + len(trilhas)},'
                               f'${ix._letras(c_cam + 2)}${lin_cab + 1}:${ix._letras(c_cam + 2)}${lin_cab + len(trilhas)}={CAM}),"")'])]
    for j, (titulo, itens) in enumerate(tab):
        col = ix._letras(c_cam + j)
        cel["DADOS"][f"{col}{lin_cab}"] = (titulo, ref_cab)
        for i, v in enumerate(itens, start=1):
            cel["DADOS"][f"{col}{lin_cab + i}"] = (v, ref_txt)
    menus_formula = {"FICHA": {
        idx["caminho"]: f"DADOS!${ix._letras(c_cam)}${lin_cab + 1}:${ix._letras(c_cam)}${lin_cab + 1 + len(caminhos)}",
        idx["trilha"]: f"DADOS!${ix._letras(c_cam + 3)}${lin_cab + 1}:${ix._letras(c_cam + 3)}${lin_cab + 1 + len(trilhas)}",
        idx["origem"]: f"DADOS!$I$4:$I${3 + len(origens_do_menu(CAT))}"}}

    # --- a curva de XP, do capitulo 18: cada nivel guarda o XP acumulado pra chegar nele, somado dos
    # custos por degrau da tabela_impressa do catalogo. O onEdit do Codigo.gs le esta tabela e poe o
    # nivel sozinho quando o XP muda -- valor solto, sem formula, pra continuar editavel a mao nas
    # mesas que sobem de nivel sem XP. 17/09/2026, pedido do Mizuki.
    tab_prog = CAT["progressao"]["tabela_impressa"]
    niveis_prog = sorted((int(n) for n in tab_prog if int(n) >= 2), key=int)
    c_niv, c_xpa = c_cam + len(tab), c_cam + len(tab) + 1
    cel["DADOS"][f"{ix._letras(c_niv)}{lin_cab}"] = ("nível", ref_cab)
    cel["DADOS"][f"{ix._letras(c_xpa)}{lin_cab}"] = ("xp acumulado", ref_cab)
    acumulado = 0
    for i, n in enumerate(niveis_prog, start=1):
        cel["DADOS"][f"{ix._letras(c_niv)}{lin_cab + i}"] = (n, ref_num)
        cel["DADOS"][f"{ix._letras(c_xpa)}{lin_cab + i}"] = (acumulado, ref_num)
        custo = tab_prog[str(n)]["xp"]
        if custo != "—":
            acumulado += int(str(custo).replace(".", ""))

    # as colunas da tabela de contas e dos menus sao desta limpeza: o que a exportacao trouxe de uma rodada
    # anterior e reescrito, e a linha que sobrar fica vazia. Fora delas, nada pode ser sobrescrito.
    donas = set(range(c_nome, c_cam + len(tab) + 2))
    for coord, r in dcel.items():
        if ix._lc(coord)[1] in donas and ix._lc(coord)[0] >= lin_cab and coord not in cel["DADOS"] and r[1] is not None:
            cel["DADOS"][coord] = (None, coord)
    for coord in cel["DADOS"]:
        v = dcel.get(coord, [None, None])[1]
        if v is not None and v != cel["DADOS"][coord][0] and ix._lc(coord)[1] not in donas:
            raise SystemExit(f"a tabela de contas cairia em DADOS!{coord}, que ja tem {v!r}")

    # --- a coluna de oficio fixo sai da tabela dos Caminhos: o livro da os dois oficios a escolha
    for c, v in dcel.items():
        if v[1] == "ofício fixo":
            lin0, col0 = ix._lc(c)
            for r in range(lin0, lin0 + 1 + len(CAT["caminhos"])):
                alvo = f"{ix._letras(col0)}{r}"
                if dcel.get(alvo, [None, None])[1] is not None:
                    cel["DADOS"][alvo] = (None, alvo)

    # --- as formulas da FICHA
    H_ = H
    def texto(usados, total, extra=""):
        return f'IF({usados}>{total},{usados}-{total}&" a mais",{extra}{total}-{usados}&" de "&{total})'
    def poe(chave, formula):
        cel["FICHA"][idx[chave]] = (formula, idx[chave])
    for n, _, _ in ix.ATRS:
        poe("atr_" + n, f"={_N(idx['atr_base_' + n])}+{_N(idx['corpo_' + n])}")
    poe("pontos disponíveis",
        f'=IF({H_["pontos distribuídos"]}>{H_["pontos de atributo"]},{H_["pontos distribuídos"]}-{H_["pontos de atributo"]}&" a mais",'
        f'IF({H_["maior atributo"]}>{R["teto_atributo"]},"Um atributo passou de {R["teto_atributo"]}",'
        f'IF(AND({H_["marcos que já passou"]}=0,{H_["maior atributo pequeno"]}>{R["teto_criacao"]}),"Na criação, nenhum acima de {R["teto_criacao"]}",'
        f'{H_["pontos de atributo"]}-{H_["pontos distribuídos"]}&" de "&{H_["pontos de atributo"]})))')
    poe("pontos de corpo", f'="Pontos de Marco de Corpo Disponíveis - "&{texto(H_["pontos de Corpo usados"], H_["marcos de Corpo"])}')
    poe("marcos escolhidos",
        f'=IF({H_["marcos escolhidos"]}>{H_["marcos que já passou"]},{H_["marcos escolhidos"]}-{H_["marcos que já passou"]}&" a mais",'
        f'IF({H_["marcos que já passou"]}=0,"Escolha 1 a cada 4 Nv",'
        f'{H_["marcos que já passou"]}-{H_["marcos escolhidos"]}&" de "&{H_["marcos que já passou"]}&" para escolher"))')
    esp = fcel[idx["espaços de feitiço"]][1]
    leq = _N(idx["marco leque"])
    if leq not in esp:
        poe("espaços de feitiço", f"{esp}+{leq}")
    feit = next(c for c, v in fcel.items() if isinstance(v[1], str) and "Feitiços - Disponível" in v[1])
    fv = fcel[feit][1]
    L1, L2 = ix._letras(c_esq), ix._letras(c_esq + 1)
    fv2 = re.sub(r"SUM\([A-Z]+\d+:[A-Z]+\d+,[A-Z]+\d+:[A-Z]+\d+\)|SUM\([A-Z]+\d+:[A-Z]+\d+\)",
                 f"SUM({L1}{l_ini}:{L2}{novo_fim})", fv)
    if fv2 != fv:
        cel["FICHA"][feit] = (fv2, feit)
    SE = H_["sem energia"]
    cel["FICHA"][atual] = (
        f'=IF({SE}=1,"Lapidação Atual: ","Refino Atual: ")&{H_["refino atual"]}&"/{R["teto_refino"]} - "&'
        f'IF({SE}=1,"Bênçãos","Aptidões")&" Disponíveis: "&{texto(H_["aptidões anotadas"], H_["máximo de aptidões"])}', atual)
    # o titulo da secao 8 segue o capitulo 11 (Sem Tecnica: "onde o livro escreve feitico, leia
    # Manejo") e o capitulo 20 (Tecnica Marcial: "leia Kata"), e a Restricao sem energia continua
    # com Bencaos em vez de Aptidoes -- ela tambem e Tecnica Marcial, entao vem primeiro na
    # checagem. 17/09/2026, pedido do Mizuki: nao funde as duas, cada rota tem o nome dela.
    titulo_apt = next(c for c, v in fcel.items() if isinstance(v[1], str) and v[1].strip() == "APTIDÕES E FEITIÇOS")
    cel["FICHA"][titulo_apt] = (
        f'=IF({SE}=1,"BÊNÇÃOS E KATAS",IF({H_["técnica marcial"]}=1,"APTIDÕES E KATAS",'
        f'IF({H_["sem técnica"]}=1,"APTIDÕES E MANEJOS","APTIDÕES E FEITIÇOS")))', titulo_apt)
    # o cabecalho da lista (F122) tambem dizia "Feitiços" antes do "Disponível" -- mesma troca, sem
    # perder a faixa D124:D144 que a extensao de duas linhas ja corrigiu ali (por isso le de `cel`,
    # nao de `fcel`, que ainda tem o texto velho). 17/09/2026, achado do Mizuki.
    palavra_feit = (f'IF({H_["técnica marcial"]}=1,"Katas",IF({H_["sem técnica"]}=1,"Manejos","Feitiços"))')
    feit_atual = cel["FICHA"].get(feit_hdr, (fcel[feit_hdr][1], feit_hdr))[0]
    cel["FICHA"][feit_hdr] = (feit_atual.replace('="Feitiços - Disponível: "',
                                                  f'=({palavra_feit})&" - Disponível: "'), feit_hdr)
    for i_ in (1, 2):
        chave = f"aptidão de graça {i_}"
        if idx.get(chave):
            poe(chave, f'=IF({SE}=1,"{R["bencaos_de_graca"][i_ - 1]}","{R["aptidoes_de_graca"][i_ - 1]}")')
    ESP_ = f'AND({H_["especializações"]}>0,{_A(idx["nivel"])}<{R["especializa"]})'
    for campo, usados, base_, corpo_ in (("perícias disponíveis", p, H_["perícias da rota"], H_["Corpo nas perícias"]),
                                         ("ofícios disponíveis", o, H_["ofícios da rota"], H_["Corpo nos ofícios"])):
        poe(campo, f'=IF({ESP_},"Especialização só no nível {R["especializa"]}",'
                   f'IF({H_["treinos a mais"]}>0,{H_["treinos a mais"]}&" a mais",'
                   f'{base_}+{corpo_}-{usados}&" de "&({base_}+{corpo_})))')
    if idx.get("escolhas de perícia"):
        # 17/09/2026: a frase junta o que falta da criacao e do marco de Corpo, sem os itens que sao zero
        def qtd(n, um, varios):
            return f'{n}&IF({n}=1," {um}"," {varios}")'
        def lista(itens):
            partes = []
            for i_, (n, um, varios) in enumerate(itens):
                antes, depois = [x[0] for x in itens[:i_]], [x[0] for x in itens[i_ + 1:]]
                sep = ""
                if antes:
                    fecha = f'IF(OR({",".join(d + ">0" for d in depois)}),", "," e ")' if depois else '" e "'
                    sep = f'IF(AND({n}>0,OR({",".join(a + ">0" for a in antes)})),{fecha},"")&'
                partes.append(f'{sep}IF({n}>0,{qtd(n, um, varios)},"")')
            return "&".join(partes)
        CORPO_ = ("escolha de Corpo", "escolhas de Corpo")
        fp_, fo_, u_ = H_["perícias que faltam"], H_["ofícios que faltam"], H_["Corpo por escolher"]
        fp2_, u2_ = H_["perícias que faltam sem ofício"], H_["Corpo por escolher sem ofício"]
        o_rota = f'"Falta: "&{lista([(fp_, "perícia", "perícias"), (fo_, "ofício", "ofícios"), (u_,) + CORPO_])}'
        o_dica = (f'IF(AND({u_}>0,{fp_}+{fo_}=0)," (+1 perícia, +1 ofício"&'
                  f'IF({_A(idx["nivel"])}>={R["especializa"]}," ou uma especialização","")&")","")')
        o_sem = (f'IF(AND({H_["rota do ofício"]}=1,{o}<={ot}),", ou "&'
                 f'{lista([(fp2_, "perícia", "perícias"), (u2_,) + CORPO_])}&" sem ofício","")')
        poe("escolhas de perícia",
            f'=IF({ESP_},"Especialização só no nível {R["especializa"]}: tire a marcação",'
            f'IF({H_["treinos a mais"]}>0,"Marcou "&{H_["treinos a mais"]}&" a mais: tire uma perícia, um ofício ou uma especialização",'
            f'IF({fp_}+{fo_}+{u_}=0,"Tudo escolhido",'
            f'{o_rota}&{o_dica}&{o_sem})))')
    poe("testes disponíveis", f'={texto(H_["testes treinados"], str(R["testes"]))}')
    if cab_leque or c4:
        cel["FICHA"][f"{ix._letras(c4)}{lc}"] = (
            f'="Passivas do Leque - "&{texto(H_["Passivas do Leque anotadas"], H_["escolhas de Leque"])}', molde_cab)
    # os Buffs somam no resultado da caixa ao lado
    for chave in ("iniciativa", "cd de feitiço", "conjuração", "corpo a corpo", "à distância", "deslocamento"):
        b = idx.get("buff de " + chave)
        if not b or not idx.get(chave):
            continue
        atual_f = fcel[idx[chave]][1]
        if not isinstance(atual_f, str) or _N(b) in atual_f:
            continue
        m_d20 = re.match(r'^="d20 \+ "\s*&\s*\+?(.*)$', atual_f)
        m_m = re.match(r"^(\d+) m$", atual_f.strip())
        if m_d20:
            poe(chave, f'="d20 + "&({m_d20.group(1)}+{_N(b)})')
        elif m_m:
            poe(chave, f'=({m_m.group(1)}+{_N(b)})&" m"')
        elif atual_f.startswith("="):
            poe(chave, f"{atual_f}+{_N(b)}")
    # o Caminho e a Trilha nascem pedindo a escolha, e a vida e a energia esperam o Caminho
    poe("caminho", ESCOLHA_CAMINHO)
    poe("trilha", ESCOLHA_TRILHA)
    # --- a caixa de TREINAMENTO EM ARMAS: o que o Caminho treina de graca, a troca por pericia e o
    #     rotulo que muda com ela. 17/09/2026, pedido do Mizuki no teste do B23.
    todas_or = "OR(" + ",".join(f'{CAM}="{n}"' for n in R["caminhos_todas_armas"]) + ")"
    cel["FICHA"][TREINADO_EM] = (
        f'=IF({CAM}="{ESCOLHA_CAMINHO}","—",IF({todas_or},"Treinado em Todas as Armas",'
        f'"Treinado em Arma de Fogo e Balestra"))', TREINADO_EM)
    if fcel.get(TROCA_ARMA, [None, None])[1] in (None, ""):
        cel["FICHA"][TROCA_ARMA] = ("Não trocou", TROCA_ARMA)
    cel["FICHA"][LABEL_EXTRA] = (
        f'=IF({TROCA_ARMA}="Não trocou","Anotações e Equipamentos","Treinamentos Extras")', LABEL_EXTRA)
    for chave in ("vida_max", "energia_max"):
        vf = fcel[idx[chave]][1]
        if isinstance(vf, str) and vf.startswith("=") and not vf.startswith("=IFERROR("):
            poe(chave, f'=IFERROR({vf[1:]},"")')
    nome = idx.get("nome")
    if nome:
        cel["FICHA"][nome] = (f'=IF(OR(CARTEIRA!$O$9="",CARTEIRA!$O$9="{NOME_PORTADOR}"),"",CARTEIRA!$O$9)', nome) \
            if "CARTEIRA!O9" in str(fcel[nome][1]) or "CARTEIRA!$O$9" in str(fcel[nome][1]) else cel["FICHA"].get(nome, (fcel[nome][1], nome))
    # --- a CARTEIRA: o que ela mostra de Caminho, Trilha e Origem, o codigo e a tecnica declarada
    cart = ix._aba(layout, "CARTEIRA")
    ccel = {r[0]: r for r in cart["celulas"]}
    cel["CARTEIRA"] = {}
    for c, r in ccel.items():
        v = r[1]
        if not isinstance(v, str):
            continue
        for campo, frase in (("D11", ESCOLHA_CAMINHO), ("N11", ESCOLHA_TRILHA)):
            alvo = f"FICHA!{idx['caminho' if campo == 'D11' else 'trilha']}"
            if v.startswith(f'=IF({alvo}="",') and frase not in v:
                cel["CARTEIRA"][c] = (v.replace(f'=IF({alvo}="",', f'=IF(OR({alvo}="",{alvo}="{frase}"),', 1), c)
        if v.strip() in ("TÉCNICA DECLARADA",) or (v.startswith("=") and "DECLARADA" in v):
            cel["CARTEIRA"][c] = (f'=IF({H_["técnica marcial"]}=1,"TÉCNICA MARCIAL DECLARADA",'
                                  f'IF({H_["sem técnica"]}=1,"ESTILO DECLARADO","TÉCNICA AMALDIÇOADA DECLARADA"))', c)

    # --- as caixas que esta limpeza escreve entram no indice, depois da ultima linha dele
    ult = max(ix._lc(k)[0] for k, v in dcel.items() if k.startswith("BA") and v[1])
    novos = [("aptidões disponíveis", atual), ("passivas do leque", f"{ix._letras(c4)}{lc}"),
             ("treinado em armas", TREINADO_EM), ("trocou por arma", TROCA_ARMA),
             ("grupo de arma da trilha", GRUPO_TRILHA)]
    i_ = 0
    for campo, coord in novos:
        if campo not in idx:
            i_ += 1
            cel["DADOS"][f"BA{ult + i_}"] = (campo, f"BA{ult}")
            cel["DADOS"][f"BB{ult + i_}"] = (ix.FORMULA.format(c=coord), f"BB{ult}")
    menus_novos = {"FICHA": [{"onde": TROCA_ARMA, "tipo": "list",
                              "formula": '"Não trocou,1 arma (-2 pericias),2 armas (-4 pericias)"',
                              "vazio_ok": True, "mostra_seta": True}]}
    return {"celulas": cel, "mescladas_sai": {"FICHA": merges_sai}, "mescladas": {"FICHA": merges_entra},
            "menus_troca": {"FICHA": menus_troca}, "menus_formula": menus_formula, "menus_novos": menus_novos, "contas": H,
            "caixas": {"pericias": PER_T, "oficios": OFI_T, "testes": TR_T, "pericias_espec": PER_E, "oficios_espec": OFI_E,
                       "aptidoes": [f"{ix._letras(ca)}{r}" for r in apt],
                       "passivas_classe": [f"{ix._letras(c_esq)}{r}" for r in range(l_ini, novo_fim + 1)],
                       "leque_nome": [f"{ix._letras(c_dir + 2)}{r}" for r in range(l_ini, novo_fim + 1)],
                       "leque_classe": [f"{ix._letras(c_dir)}{r}" for r in range(l_ini, novo_fim + 1)],
                       "feitico_classe": sorted((c for c, v in fcel.items() if ix._lc(c)[1] == ix._lc(feit)[1] - 2
                                                 and ix._lc(feit)[0] < ix._lc(c)[0] <= novo_fim_feit and isinstance(v[1], (int, float))),
                                                key=ix._lc)},
            "textos": {"aptidoes": atual, "feiticos": feit, "passivas_do_leque": f"{ix._letras(c4)}{lc}"}}


def origens_do_menu(CAT):
    """a lista do menu de Origem: a ordem das rotas de criacao do catalogo, com a Sem Tecnica aberta nas
    cinco Origens principais e a Restricao Celestial nos dois ramos. 17/09/2026, pedido do Mizuki: a ficha
    precisa saber a rota para mudar a tecnica declarada e as aptidoes de graca."""
    out = []
    for r in CAT["rotas_de_criacao"]:
        if r["rota"] == "Sem Técnica":
            out += [f"{o}{SEM_TECNICA}" for o in CAT["sub_origem"]["Sem Técnica"]["origens"]]
        else:
            out.append(r["origem"])
    return out


def aplica(layout, tr):
    n = ix.aplica(layout, tr["celulas"])
    for nome, faixas in tr["mescladas_sai"].items():
        aba = ix._aba(layout, nome)
        antes = len(aba["mescladas"])
        aba["mescladas"] = [m for m in aba["mescladas"] if m not in faixas]
        n += antes - len(aba["mescladas"])
    for nome, faixas in tr["mescladas"].items():
        aba = ix._aba(layout, nome)
        novas = [x for x in faixas if x not in aba["mescladas"]]
        aba["mescladas"] += novas
        n += len(novas)
    for nome, formulas in tr.get("menus_formula", {}).items():
        aba = ix._aba(layout, nome)
        for m in aba["menus"]:
            if m["onde"] in formulas and m["formula"] != formulas[m["onde"]]:
                m["formula"] = formulas[m["onde"]]
                n += 1
    for nome, trocas_ in tr["menus_troca"].items():
        aba = ix._aba(layout, nome)
        for m in aba["menus"]:
            if m["onde"] in trocas_:
                m["onde"] = trocas_[m["onde"]]
                n += 1
    for nome, novos_ in tr.get("menus_novos", {}).items():
        aba = ix._aba(layout, nome)
        existentes = {m["onde"] for m in aba["menus"]}
        for m in novos_:
            if m["onde"] not in existentes:
                aba["menus"].append(m)
                n += 1
    return n
