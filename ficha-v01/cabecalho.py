# -*- coding: utf-8 -*-
"""Limpeza 23 (01/10/2026): o cabeçalho da FICHA no molde do estudo da Ficha Pessoal.

Pedido do Mizuki testando no Sheets, com a Ficha Pessoal recém-montada: "o ficha pessoal e o ficha deveriam ter
esse cabeçalho mais único, semelhante do protótipo, ficaria mais legal de ler e visualizar a ficha. A própria
carteira tem isso e fica bem mais bonito". O cabeçalho da FICHA era o nome do sistema em letra miúda, o nome da
personagem grande à esquerda, e à direita a palavra CATÁLOGO com o carimbo de versão. Sem nome digitado, sobrava uma
faixa quase vazia.

O molde novo é o da CARTEIRA e do estudo: à esquerda a marca 呪術, o título da aba e uma linha de apoio; à direita o
nome da personagem e, embaixo dele, o Caminho, a Trilha e o nível.

    D2:G4   呪術                         H2:Z3  FICHA DE REGISTRO          AB2:AT3  Kaori
                                         H4:Z4  Projeto M · v0.258 · em dia   AB4:AT4  Bastião · Muro · nível 2

O carimbo de versão continua, agora na linha de apoio. A palavra CATÁLOGO sai: para o Mizuki, catálogo é a aba da
invocação. A linha 3 perde a altura maior que tinha para o nome grande, e as cinco linhas do cabeçalho ficam iguais.

Roda logo depois do desenho da mesa (ficha_layout.py) e ANTES do índice (indice_ficha.py): o nome muda de célula, e o
índice da DADOS publica o endereço dele. A Ficha Pessoal copia este cabeçalho e troca o título e a linha de apoio.
"""
import json, re
import indice_ficha as ix
import ficha_automatica as fa

TINTA, OSSO, FRACO, BLOCO = "FF0A0810", "FFE8DCD4", "FF998BA9", "FF756588"
MARCA = "呪術"
TITULO_DA_FICHA = "FICHA DE REGISTRO"
# onde cada peça mora: (canto, última célula)
C_MARCA, C_TITULO, C_APOIO = ("D2", "G4"), ("H2", "Z3"), ("H4", "Z4")
C_NOME, C_QUEM = ("AB2", "AT3"), ("AB4", "AT4")
ULTIMA_LINHA = 5          # o cabeçalho são as linhas 1 a 5; a 6 é a pincelada
ESTILOS = {
    "marca":  [["Yuji Syuku", 22.0, BLOCO, False, False], TINTA, None, ["center", "center", False, 0], None],
    "titulo": [["Oswald", 13.0, OSSO, False, False], TINTA, None, ["left", "bottom", False, 0], None],
    "apoio":  [["Roboto", 9.0, FRACO, False, False], TINTA, None, ["left", "top", False, 0], None],
    "nome":   [["Castoro", 15.0, OSSO, False, False], TINTA, None, ["right", "bottom", False, 0], None],
    "quem":   [["Roboto", 9.0, FRACO, False, False], TINTA, None, ["right", "top", False, 0], None],
    "vazio":  [["Roboto", 11.0, "FFF4F1F7", False, False], TINTA, None, ["left", "center", False, 0], None],
}


def _estilo(layout, nome):
    chave = json.dumps(ESTILOS[nome], ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(json.loads(json.dumps(ESTILOS[nome])))
    return len(layout["estilos"]) - 1


def carimbo(sistema="DADOS!$F$1"):
    """a linha de apoio da FICHA: o nome do sistema e o carimbo de versão, que avisa quando a ficha está atrás do livro"""
    return (f'={sistema}&" · "&IF(DADOS!$B$1=DADOS!$D$1,"v"&DADOS!$B$1&" · em dia",'
            f'"⚠ v"&DADOS!$B$1&" · a atual é a v"&DADOS!$D$1)')


def quem(layout, aba=""):
    """o Caminho, a Trilha e o nível numa linha só; vazia enquanto o Caminho não foi escolhido"""
    idx = ix.enderecos(layout)
    ref = lambda k: aba + "$" + re.sub(r"(\d+)$", r"$\1", idx[k])
    cam, tri, niv = ref("caminho"), ref("trilha"), ref("nivel")
    return (f'=IF(OR({cam}="",{cam}="{fa.ESCOLHA_CAMINHO}"),"",{cam}&IF(OR({tri}="",{tri}="{fa.ESCOLHA_TRILHA}"),""," · "&{tri})'
            f'&" · nível "&{niv})')


def trocas(layout):
    """{"celulas": {aba: {coord: (valor, índice do estilo)}}, "mescladas_sai", "mescladas", "alturas_sai"}"""
    ficha = ix._aba(layout, "FICHA")
    por = {r[0]: r for r in ficha["celulas"]}
    do_cab = {c: r for c, r in por.items() if ix._lc(c)[0] <= ULTIMA_LINHA and ix._lc(c)[1] > 2}
    nome_antigo = [c for c, r in do_cab.items() if isinstance(r[1], str) and "CARTEIRA!" in r[1]]
    versao = [c for c, r in do_cab.items() if isinstance(r[1], str) and "em dia" in r[1]]
    if len(nome_antigo) != 1 or len(versao) != 1:
        raise SystemExit(f"o cabecalho da FICHA devia ter um nome ({nome_antigo}) e um carimbo de versao ({versao})")
    formula_do_nome = por[nome_antigo[0]][1]
    e = {k: _estilo(layout, k) for k in ESTILOS}
    cel = {"FICHA": {}, "CARTEIRA": {}}
    # tudo o que o cabeçalho antigo dizia sai, e a célula volta a ser só o fundo de tinta
    for c, r in do_cab.items():
        if r[1] is not None or r[2] != e["vazio"]:
            cel["FICHA"][c] = (None, e["vazio"])
    # as caixas mescladas antigas só tinham a célula do canto: desfeita a mesclagem, as de dentro precisam existir, ou
    # ficam no fundo da aba, sem a tinta e sem a divisória de baixo
    for lin in range(1, ULTIMA_LINHA + 1):
        for col in range(3, ficha["colunas"] + 1):
            c = f"{ix._letras(col)}{lin}"
            if c not in por:
                cel["FICHA"][c] = (None, e["vazio"])
    cel["FICHA"][C_MARCA[0]] = (MARCA, e["marca"])
    cel["FICHA"][C_TITULO[0]] = (TITULO_DA_FICHA, e["titulo"])
    cel["FICHA"][C_APOIO[0]] = (carimbo(), e["apoio"])
    cel["FICHA"][C_NOME[0]] = (formula_do_nome, e["nome"])
    cel["FICHA"][C_QUEM[0]] = (quem(layout), e["quem"])
    # quem lia o nome no lugar antigo passa a ler no novo (o número da CARTEIRA usa as quatro primeiras letras)
    velho = re.compile(r"FICHA!\$?" + re.match(r"[A-Z]+", nome_antigo[0]).group(0) + r"\$?" + re.search(r"\d+", nome_antigo[0]).group(0) + r"(?!\d)")
    novo = "FICHA!$" + re.match(r"[A-Z]+", C_NOME[0]).group(0) + "$" + re.search(r"\d+", C_NOME[0]).group(0)
    for a in layout["abas"]:
        if a["nome"] in ("FICHA", "DADOS"):          # a DADOS é reescrita pelo índice, que vem depois
            continue
        for r in a["celulas"]:
            if isinstance(r[1], str) and r[1].startswith("=") and velho.search(r[1]):
                cel.setdefault(a["nome"], {})[r[0]] = (velho.sub(novo, r[1]), r[2])
    sai = [m for m in ficha["mescladas"] if ix._lc(m.split(":")[1])[0] <= ULTIMA_LINHA and ix._lc(m.split(":")[0])[1] > 2]
    entra = [f"{a}:{b}" for a, b in (C_MARCA, C_TITULO, C_APOIO, C_NOME, C_QUEM)]
    alturas_sai = [a[0] for a in ficha["linhas_alt"] if a[0] <= ULTIMA_LINHA]
    return {"celulas": {k: v for k, v in cel.items() if v}, "mescladas_sai": {"FICHA": sai}, "mescladas": {"FICHA": entra},
            "alturas_sai": {"FICHA": alturas_sai}}


def aplica(layout, tr):
    n = 0
    for nome, cels in tr["celulas"].items():
        aba = ix._aba(layout, nome)
        por = {r[0]: r for r in aba["celulas"]}
        for coord, (valor, estilo) in cels.items():
            if coord in por:
                if por[coord][1] != valor or por[coord][2] != estilo:
                    por[coord][1], por[coord][2] = valor, estilo
                    n += 1
            else:
                aba["celulas"].append([coord, valor, estilo])
                n += 1
    for nome, ms in tr["mescladas_sai"].items():
        aba = ix._aba(layout, nome)
        aba["mescladas"] = [m for m in aba["mescladas"] if m not in ms]
    for nome, ms in tr["mescladas"].items():
        aba = ix._aba(layout, nome)
        aba["mescladas"] += [m for m in ms if m not in aba["mescladas"]]
    for nome, linhas in tr["alturas_sai"].items():
        aba = ix._aba(layout, nome)
        aba["linhas_alt"] = [a for a in aba["linhas_alt"] if a[0] not in linhas]
    return n
