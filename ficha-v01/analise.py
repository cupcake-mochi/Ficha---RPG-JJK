# -*- coding: utf-8 -*-
"""A aba ANALISE: tudo o que o bot precisa para dizer "essa ficha tá aprovada" (14/10/2026, B47, fase 1).

O Mizuki: "a gente precisa de uma pagina, de preferencia oculta ... Aonde mostra TODAS as informações da ficha que podem
vir a requisitar uma 'analise' ... ela ser dificil de ler pros jogadores n alterarem é até bom, MAS o objetivo principal é
ser leitura para o nosso bot". O plano e o esquema (o "contrato" com o bot) moram fora do repositório, em
Planejamento-ficha/B47-analise-e-configuracao/ (PLANO.md e ESQUEMA-ANALISE.md); o resumo está no PENDENCIAS.md, B47.

O desenho: uma aba oculta, sem cor e fora da troca de paleta, com quatro colunas e uma informação por linha:

    A chave    fixa, minúscula, sem acento, com ponto entre os níveis (atributo.forca.base, feitico.7.pecas)
    B valor    fórmula que lê a ficha (a caixa de marcar sai como 1 ou 0; a vazia sai vazia)
    C célula   de onde o valor saiu, para o mestre achar na ficha
    D parte    cabeçalho, entrada, resultado ou aviso

Esconder não protege (o jogador é dono da cópia): o bot lê as entradas, refaz as contas e compara com os resultados.
Ele lê pelo link aberto, com a Sheets API ou com a exportação em CSV da aba
(https://docs.google.com/spreadsheets/d/<id>/gviz/tq?tqx=out:csv&sheet=ANALISE). Os números saem como a planilha os
mostra (vírgula decimal numa planilha em português): quem normaliza é o leitor (ler-analise.py, na raiz).

Nenhuma chave se reaproveita com outro sentido: mudou a regra, entra chave nova e FORMATO sobe.
"""
import json, os, re, unicodedata
import indice_ficha as ix

NOME = "ANALISE"
FORMATO = 5
PARTES = ("cabeçalho", "entrada", "resultado", "aviso", "configuração")


def chave(*partes):
    """'Corpo a Corpo', 'à distância' -> 'corpo_a_corpo', 'a_distancia'"""
    out = []
    for p in partes:
        s = unicodedata.normalize("NFKD", str(p)).encode("ascii", "ignore").decode().lower()
        out.append(re.sub(r"[^a-z0-9]+", "_", s).strip("_"))
    return ".".join(out)


def _ref(aba, a1):
    lin, col = ix._lc(a1)
    nome = f"'{aba}'" if not re.fullmatch(r"[A-Z_]+", aba) else aba
    return f"{nome}!${ix._letras(col)}${lin}"


def trocas(layout, fa, fp_tr, fam, fiv):
    idx = ix.indice(layout)
    linhas = []                                         # [chave, fórmula, célula, parte]

    def lê(k, ref, parte="entrada", caixa=False):
        # O CSV do gviz escolhe um único tipo para cada coluna. Misturar números e texto
        # fazia os textos da coluna B saírem vazios; o contrato publica todos como texto.
        v = f'=N({ref})&""' if caixa else f'=IF(ISBLANK({ref}),"",{ref}&"")'
        linhas.append([k, v, ref.replace("$", ""), parte])

    def fixo(k, v, parte="cabeçalho"):
        linhas.append([k, str(v), "", parte])

    def junta(k, refs, parte="entrada"):
        """várias caixas numa linha só, separadas por ' · ' (as peças de um feitiço)"""
        linhas.append([k, '=TEXTJOIN(" · ",TRUE,' + ",".join(refs) + ")", " ".join(r.replace("$", "") for r in refs), parte])

    F = lambda k: _ref("FICHA", idx[k])
    # --- cabeçalho
    fonte = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manual-fonte.json"), encoding="utf-8"))
    fixo("formato.versao", FORMATO)
    linhas.append(["ficha.versao", '=DADOS!$B$1&""', "DADOS!B1", "cabeçalho"])
    linhas.append(["ficha.sistema", '=DADOS!$F$1&""', "DADOS!F1", "cabeçalho"])
    fixo("ficha.livro", re.match(r"(Ciclo Maldito R\d+)", fonte["livro"]).group(1))

    # --- entradas da FICHA
    for k in ("nome", "caminho", "trilha", "origem", "nivel", "xp"):
        lê(chave(k), F(k))
    for nome, _, _ in ix.ATRS:
        lê(chave("atributo", nome, "base"), F("atr_base_" + nome))
        if idx.get("corpo_" + nome):
            lê(chave("atributo", nome, "corpo"), F("corpo_" + nome))
    for k, c in (("marco.refino", "refino escolhido"), ("marco.corpo", "marco corpo"), ("marco.leque", "marco leque"),
                 ("marcos.escolhidos", "marcos escolhidos")):
        if idx.get(c):
            lê(k, F(c))
    CAT = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catalogo-projeto-m.json"), encoding="utf-8"))
    cx = fa["caixas"]
    for nome, t, e in zip(CAT["pericias"], cx["pericias"], cx["pericias_espec"]):
        lê(chave("pericia", nome, "treino"), _ref("FICHA", t), caixa=True)
        lê(chave("pericia", nome, "especialista"), _ref("FICHA", e), caixa=True)
    for nome, t, e in zip(CAT["oficios"], cx["oficios"], cx["oficios_espec"]):
        lê(chave("oficio", nome, "treino"), _ref("FICHA", t), caixa=True)
        lê(chave("oficio", nome, "especialista"), _ref("FICHA", e), caixa=True)
    trs = [t for t, v in CAT["testes_de_resistencia"].items() if isinstance(v, dict)]
    for nome, t in zip(trs, cx["testes"]):
        lê(chave("tr", nome, "treino"), _ref("FICHA", t), caixa=True)
    for k in ("sequela 1", "sequela 2", "sequela 3"):
        lê(chave("sequela", k[-1]), F(k), caixa=True)
    for k in ("exaustão", "resistências", "imunidades", "treinado em armas", "trocou por arma", "grupo de arma da trilha"):
        if idx.get(k):
            lê(chave(k), F(k))
    for k in sorted(c for c in idx if c.startswith("buff de ")):
        lê(chave("buff", k[len("buff de "):]), F(k))

    # --- entradas da FICHA PESSOAL
    import ficha_pessoal as fp
    G, P = fp_tr["G"], lambda a1: _ref(fp.NOME, a1)
    for k, c in (("grau", "grau"), ("em_uso.principal", "principal"), ("em_uso.secundaria", "secundaria"),
                 ("em_uso.vestindo", "vestindo"), ("origem.legados", "legados"), ("origem.oficio_compativel", "oficio"),
                 ("origem.ce4", "ce4")):
        lê(k, P(G[c]))
    for i, (campo, _, _) in enumerate(fp.CAPS):
        lê(chave("origem", campo), P(G["cap_menu"][i]))
        lê(chave("origem", campo, "texto"), P(G["cap_texto"][i]))
    for nome, (col, lin, _) in sorted(G["armas"].items()):
        lê(chave("treino.arma", nome), P(f"{ix._letras(col)}{lin}"), caixa=True)
    for n, l in enumerate(range(G["equip_ini"], G["equip_fim"] + 1), start=1):
        junta(f"equipavel.{n}", [P(f"D{l}"), P(f"AI{l}")])
    for n, l in enumerate(range(G["itens_ini"], G["itens_fim"] + 1), start=1):
        for k, cols in enumerate(fp.COLS_ITENS):
            (_, i1, _), (_, q1, _), _ = cols
            junta(f"item.{(k * (G['itens_fim'] - G['itens_ini'] + 1)) + n}", [P(f"{i1}{l}"), P(f"{q1}{l}")])
    for b_, b in enumerate(fp.BLOCOS, start=1):
        for n, l in enumerate(range(G["missao_ini"], G["missao_fim"] + 1), start=1):
            junta(f"missao.{b_}.{n}", [P(f"{ix._letras(b + k)}{l}") for k in (fp.C_MISSAO, fp.C_XP, fp.C_ADIC, fp.C_DESC, fp.C_TOTAL)])

    # --- entradas da FICHA AMALDIÇOADA: os feitiços (uma linha por lugar, as peças juntas), as passivas, as aptidões e
    # os pactos. A conta de cada lugar mora na DADOS_AM (fam["FEIT"]), com os erros e os avisos que a aba já calcula
    AM = "FICHA AMALDIÇOADA"
    FT = fam["FEIT"]
    for i, lugar in enumerate(fam["lugares"]):
        base = chave(lugar[0], lugar[2])
        for c in ("classe", "nome", "forma"):
            lê(f"{base}.{c}", FT(c, i))
        junta(f"{base}.pecas", [FT(f"m{j}", i) for j in range(1, 5)])
        junta(f"{base}.restricoes", [FT(f"r{j}", i) for j in range(1, 3)])
        for c in ("pe", "dano", "alcance", "resolve"):
            lê(f"{base}.{c}", FT(c, i), "resultado")
        for c in ("erros", "avisos"):
            lê(f"{base}.{c}", FT(c, i), "aviso")
    for n, c in enumerate(fam["passivas_c"], start=1):
        lê(f"passiva.{n}", _ref(AM, c["nome"]))
    for n, c in enumerate(fam["aptidoes_c"], start=1):
        lê(f"aptidao.{n}", _ref(AM, c["nome"]))
    for n, c in enumerate(fam["pactos_c"], start=1):
        for k in ("nome", "forma", "modifica", "tamanho", "dou", "recebo", "clausula"):
            lê(f"pacto.{n}.{k}", _ref(AM, c[k]))
    lê("aviso.vagas_de_pacto", _ref(AM, fam["G"]["pac_permanentes"]), "aviso")

    # --- entradas da INVOCAÇÕES: uma linha por campo de cada ficha, e as cartas com as peças juntas
    FI, CARTA = fiv["FI"], fiv["CARTA"]
    for i, g in enumerate(fiv["fichas_c"]):
        base = f"invocacao.{i + 1}"
        for k, c in (("nome", "nome"), ("tipo", "tipo"), ("aquisicao", "aquis"), ("nivel_fixo", "nfixo"), ("talisma", "talisma")):
            lê(f"{base}.{k}", FI(c, i))
        lê(f"{base}.oficio_compativel", _ref("INVOCAÇÕES", g["oficio"]))
        junta(f"{base}.pontos", [FI(f"p{k}", i) for k in range(5)])
        junta(f"{base}.familias", [FI(c, i) for c in fiv["nomes_f"] if re.fullmatch(r"f\d+", c)])
        junta(f"{base}.pericias", [FI(c, i) for c in fiv["nomes_f"] if re.fullmatch(r"per\d+", c)])
        junta(f"{base}.talentos", [FI(c, i) for c in fiv["nomes_f"] if re.fullmatch(r"tal\d+", c)])
        for k, c in (("nivel", "n"), ("classe", "cl"), ("vida.max", "vida"), ("entrada", "ent"), ("retorno", "ret"),
                     ("acerto", "atq"), ("cd", "cd"), ("defesa", "def"), ("deslocamento", "desl")):
            lê(f"{base}.{k}", FI(c, i), "resultado")
        lê(f"{base}.pontos_acima", FI("acima", i), "aviso")
    for n, carta in enumerate(fiv["cartas"]):
        f_, tipo, num = carta[0], carta[1], carta[2]
        base = f"invocacao.{f_ + 1}.{tipo}.{num + 1}"
        for c in ("classe", "nome", "forma"):
            lê(f"{base}.{c}", CARTA(c, n))
        junta(f"{base}.pecas", [CARTA(c, n) for c in fiv["nomes_c"] if re.fullmatch(r"m\d+", c)])
        junta(f"{base}.restricoes", [CARTA(c, n) for c in fiv["nomes_c"] if re.fullmatch(r"r\d+", c)])
        for c in ("pe", "dano"):
            lê(f"{base}.{c}", CARTA(c, n), "resultado")
        for c in ("erros", "avisos"):
            lê(f"{base}.{c}", CARTA(c, n), "aviso")

    # --- resultados da FICHA
    for k in ("vida_max", "energia_max", "integridade_max", "defesa", "proteção", "iniciativa", "cd de feitiço",
              "conjuração", "corpo a corpo", "à distância", "maestria", "deslocamento", "espaços de feitiço",
              "classe máxima", "refino de graça", "classe 0 grátis", "morrendo aguentar", "morrendo insistir 1",
              "morrendo insistir 2", "morrendo prazo", "marcante", "menor 1", "menor 2"):
        if idx.get(k):
            lê(chave(k), F(k), "resultado")
    lê("xp.total", P(G["xp_total"]), "resultado")
    lê("carga", P(G["carga"]), "resultado")

    # --- avisos: os X de Y da FICHA e as marcas da FICHA PESSOAL
    for k in ("pontos disponíveis", "perícias disponíveis", "ofícios disponíveis", "testes disponíveis", "escolhas de perícia"):
        if idx.get(k):
            lê(chave("aviso", k), F(k), "aviso")
    for k in ("marca_treino", "marca_forca_p", "marca_forca_s", "marca_selo", "marca_grau", "marca_forca_v", "requisito", "situacao"):
        lê(chave("aviso", k.replace("marca_", "")), P(G[k]), "aviso")

    # Revisão 2: mantém as chaves antigas e acrescenta as entradas que faltavam.
    # Os endereços vêm das mesmas geometrias usadas para desenhar as abas.
    import ficha_amaldicoada as am
    import ficha_invocacoes as iv
    A = lambda a1: _ref(AM, a1)
    I = lambda a1: _ref("INVOCAÇÕES", a1)
    indice_principal = ix._Ficha(layout)
    lê("tecnica.atributo_escolhido", _ref("FICHA", indice_principal.abaixo(indice_principal.unico("ATRIBUTO DE CONJURAÇÃO"))))
    g = fam["G"]
    for k, c, parte in (
        ("nome", "nome_tecnica", "entrada"), ("tipo_dano", "tipo_dano", "entrada"),
        ("atributo", "atributo", "resultado"), ("rota.escolha", "rota_menu", "entrada"),
        ("rota.nome", "rota_nome", "resultado"), ("regra_propria.categoria", "cp_regra", "entrada"),
        ("regra_propria.espacos", "espacos_regra", "resultado")):
        lê("tecnica." + k, A(g[c]), parte)
    for k, c in (("regra", f"D{g['regra'] + 1}"), ("descricao", f"D{g['descricao'] + 1}"),
                 ("selo", f"L{g['descricao'] + 1}"), ("expressao", f"L{g['descricao'] + 4}"),
                 ("regra_propria.texto", f"D{g['regra_propria'] + 1}")):
        lê("tecnica." + k, A(c))
    for nome, (coluna, _) in zip(fam["R"]["familias"], g["cols_fam"]):
        lê(chave("tecnica", "familia", nome), A(f"{coluna}{g['familias'] + 1}"))
    for n, c in enumerate(g["grupos_menu"], 1):
        lê(f"tecnica.grupo.{n}", A(c))
    for lugar in fam["lugares"]:
        base = chave(lugar[0], lugar[2])
        c = lugar[3]
        lê(base + ".texto", A(c["como"]))
        lê(base + ".acao", A(c["acao"]), "resultado")
    for n, c in enumerate(fam["zero_c"], 1):
        base = f"zero.{n}"
        fixo(base + ".classe", 0, "entrada")
        fixo(base + ".pe", 0, "resultado")
        for k in ("nome", "forma", "dano", "alcance"):
            lê(base + "." + k, A(c[k]), "resultado" if k in ("dano", "alcance") else "entrada")
        lê(base + ".pecas", A(c["mel"]))
        lê(base + ".restricoes", A(c["res"]))
    for k in ("nome", "forma", "dano", "pe", "montagem"):
        lê("maxima." + k, A(g["tm_" + k]), "entrada" if k in ("nome", "forma") else "resultado")
    junta("maxima.pecas", [A(c) for c in fam["tm_mel"]])
    lê("maxima.texto", A(f"D{g['tm_como'] + 1}"))
    for k, c, parte in (("degrau", "degrau", "entrada"), ("nome", "dom_nome", "entrada"),
                         ("custo", "dom_custa", "resultado"), ("requisito", "dom_requisito", "resultado"),
                         ("refino", "dom_refino", "resultado"), ("corrida", "dom_corrida", "resultado")):
        lê("dominio." + k, A(g[c]), parte)
    lê("dominio.texto", A(f"D{g['dom_como'] + 1}"))
    for tipo, cartas in (("passiva", fam["passivas_c"]), ("aptidao", fam["aptidoes_c"])):
        for n, c in enumerate(cartas, 1):
            lê(f"{tipo}.{n}.categoria", A(c["cp"]))
            lê(f"{tipo}.{n}.texto", A(c["texto"]))

    lê("invocacoes.defesa_atributo", I(fiv["CJ"]["usa"]))
    for n, g in enumerate(fiv["fichas_c"], 1):
        base = f"invocacao.{n}"
        for j, (atributo, _) in enumerate(iv.ATRS):
            for k, lista_ in (("base", "pts"), ("buff", "buff"), ("total", "total")):
                lê(base + "." + chave("atributo", atributo, k), I(g[lista_][j]), "resultado" if k == "total" else "entrada")
        for campo, c in zip(("acerto", "cd", "defesa", "vida", "deslocamento"), g["bstat"]):
            lê(base + ".buff." + campo, I(c))
        for campo, c in zip(("fisico", "vigor", "intelecto", "espirito"), g["btr"]):
            lê(base + ".buff.tr." + campo, I(c))
        for campo, c in (("atributo_acerto", "acerto"), ("atributo_fisico", "fis"), ("tr_treinado", "trT"),
                         ("alma", "alma"), ("notas", "notas"), ("definicao", "def")):
            lê(base + "." + campo, I(g[c]))
        for lista_, campo in (("fam", "familia"), ("per", "pericia"), ("perb", "buff.pericia"),
                               ("tal", "talento"), ("talx", "talento_extra"), ("eq", "equipamento")):
            for j, c in enumerate(g[lista_], 1):
                lê(f"{base}.{campo}.{j}", I(c))
        for j, c in enumerate(g["lib"], 1):
            for campo in ("classe", "nome", "pe", "como", "pontos", "acao"):
                lê(f"{base}.liberacao.{j}.{campo}", I(c[campo]), "resultado" if campo in ("pe", "pontos", "acao") else "entrada")
        for tipo in ("tm", "exp"):
            for campo, c in g[tipo].items():
                if campo not in ("r0", "c0"):
                    lê(f"{base}.{tipo}.{campo}", I(c), "resultado" if campo in ("pe", "dados", "acao", "pede") else "entrada")
    for carta in fiv["cartas"]:
        f_, tipo, num, c = carta[:4]
        base = f"invocacao.{f_ + 1}.{tipo}.{num + 1}"
        for campo, origem in (("texto", "como"), ("tipo_dano", "tdano"), ("resolucao_escolha", "rmenu"),
                               ("acao", "acao"), ("resolve", "resolve"), ("alcance", "alcance")):
            lê(base + "." + campo, I(c[origem]), "resultado" if campo in ("acao", "resolve", "alcance") else "entrada")

    vistas = [l[0] for l in linhas]
    repetidas = sorted({k for k in vistas if vistas.count(k) > 1})
    if repetidas:
        raise SystemExit(f"analise: chave repetida {repetidas[:5]}")
    return {"linhas": linhas}


def aba(layout, tr):
    """a aba inteira: oculta, sem cor própria (a da folha), quatro colunas e uma linha por informação"""
    neutro = [["Roboto", 12, "000000", False, False], "FFFFFF", None, None, None]
    if neutro not in layout["estilos"]:
        layout["estilos"].append(neutro)
    estilo = layout["estilos"].index(neutro)
    cel = [["A1", "chave", estilo], ["B1", "valor", estilo], ["C1", "célula", estilo], ["D1", "parte", estilo]]
    for i, (k, v, c, p) in enumerate(tr["linhas"], start=2):
        # Um literal começando por aspa simples é tratado pelo Sheets como escape.
        # A fórmula de texto conserva o endereço completo das abas com espaços.
        endereco = '="' + c.replace('"', '""') + '"' if c.startswith("'") else c
        cel += [[f"A{i}", k, estilo], [f"B{i}", v, estilo], [f"C{i}", endereco, estilo], [f"D{i}", p, estilo]]
    n = len(tr["linhas"]) + 1
    return {"nome": NOME, "estado": "hidden", "linhas": n, "colunas": 4,
            "padrao": ["Roboto", 12, "#000000"], "fundo_base": "#FFFFFF",
            "colunas_larg": [[1, 1, 34.0], [2, 2, 60.0], [3, 3, 34.0], [4, 4, 12.0]],
            "linhas_alt": [], "altura_padrao": 15.75, "grade": True, "celulas": cel, "mescladas": [], "menus": [],
            "condicional": [], "imagens": []}
