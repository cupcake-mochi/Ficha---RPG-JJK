# -*- coding: utf-8 -*-
"""Engano de formatação manual da planilha viva, corrigido na saída e não na planilha.

A planilha viva é editada à mão no Sheets, e de vez em quando a formatação de uma caixa sai diferente
da irmã do lado sem que ninguém tenha querido. Este módulo é a lista desses enganos: cada um é achado
comparando a caixa com a irmã, e corrigido aqui pra a correção não morrer na próxima vez que o
Ficha.gs for regerado. Quando o Mizuki consertar a formatação na planilha viva e reexportar, a
correção vira letra morta (o estilo já sai igual) e a linha pode sair.

19/09/2026, achado testando no Sheets:

  · A lombada (a faixa escura de tinta, colunas A:B, com o nome da aba girado) da FICHA parava na linha 144
    e a da INVOCAÇÃO na 120, quando as abas têm 150 e 126 linhas: sobravam as últimas linhas com o fundo
    comum, e numa paleta clara — em que o tinta é um pastel diferente do fundo — a faixa aparecia
    cortada. Na ficha de fábrica não se via, porque o tinta e o fundo escuros quase não se distinguem.
  · A moldura da ficha (o cabeçalho e a lombada, em tinta) e o miolo (em fundo) não tinham NADA entre eles: numa
    paleta clara, em que os dois são pastéis quase iguais, o miolo se misturava com a moldura. Pedido do
    Mizuki: "uma linha simples que realmente separa essas duas partes". Ganham uma divisória na cor da régua
    (`_divisorias`), no traço médio das outras bordas — a régua tem só 1,8 de contraste contra o fundo, e
    num traço fino ela sumiria; se pesar, é a constante DIVISORIA_TRACO.
  · A caixa ORIGEM da CARTEIRA (AK17:AT17) nasceu com borda BRANCA e FINA (thin/#FFFFFF) em três lados
    e nenhuma no quarto, e a CAMINHO (O17:X17), do lado, tem régua média (medium/#8A7EC4) nos quatro.
    Como a borda branca nunca é a régua, a troca de paleta também não repintava ela: ficava branca em
    toda paleta. A caixa passa a ter, célula a célula, a borda da CAMINHO — são as duas de dez
    colunas, e o desenho é o mesmo.
"""
import json
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI
from openpyxl.utils.cell import range_boundaries

DIVISORIA_TRACO = ["medium", "FF8A7EC4"]   # o mesmo traço e a mesma cor (a régua) de toda borda da ficha


def _acha_ou_cria(layout, novo):
    chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(novo)
    return len(layout["estilos"]) - 1


def _origem_igual_caminho(layout):
    car = next(a for a in layout["abas"] if a["nome"] == "CARTEIRA")
    reg = {r[0]: r for r in car["celulas"]}
    deslocamento = CI("AK") - CI("O")
    if reg["AK17"][1] != "ORIGEM" or reg["O17"][1] != "CAMINHO":
        raise SystemExit("correcoes_borda: a ORIGEM ou a CAMINHO saiu do lugar (AK17/O17) — "
                         "o desenho da CARTEIRA mudou, e a correção precisa ser reescrita")
    n = 0
    for col in range(CI("AK"), CI("AT") + 1):
        alvo, molde = reg.get(f"{L(col)}17"), reg.get(f"{L(col - deslocamento)}17")
        if alvo is None or molde is None or alvo[2] is None or molde[2] is None:
            raise SystemExit(f"correcoes_borda: falta estilo em {L(col)}17 ou {L(col - deslocamento)}17")
        fonte, fundo, bordas, alinha, fmt = json.loads(json.dumps(layout["estilos"][alvo[2]]))
        bordas_molde = json.loads(json.dumps(layout["estilos"][molde[2]][2]))
        if bordas != bordas_molde:
            alvo[2] = _acha_ou_cria(layout, [fonte, fundo, bordas_molde, alinha, fmt])
            n += 1
    return n


def _lombada_ate_o_fim(layout):
    """A lombada (fundo tinta nas colunas A e B) vai até a última linha da aba, e não até onde a
    planilha viva parou de pintar ela. O estilo é o da última linha que já era lombada."""
    tinta = "FF0A0810"
    n = 0
    for nome in ("FICHA", "INVOCAÇÃO"):
        aba = next(a for a in layout["abas"] if a["nome"] == nome)
        reg = {r[0]: r for r in aba["celulas"]}
        fim = aba["linhas"] + 2   # as duas linhas de folga que o emissor dava embaixo, e agora a lombada cobre
        for col in ("A", "B"):
            spine = [int(c[1:]) for c, r in reg.items()
                     if c[0] == col and c[1:].isdigit() and r[2] is not None
                     and layout["estilos"][r[2]][1] == tinta]
            ultima = max(spine)
            molde = reg[f"{col}{ultima}"][2]
            for lin in range(ultima + 1, fim + 1):
                coord = f"{col}{lin}"
                if coord in reg:
                    if reg[coord][2] != molde:
                        reg[coord][2] = molde
                        n += 1
                else:
                    novo = [coord, None, molde]
                    aba["celulas"].append(novo)
                    reg[coord] = novo
                    n += 1
    return n


def _com_lado(layout, indice, lado):
    """o estilo `indice` com a divisória no `lado` (top/bottom/left/right)."""
    fonte, fundo, bordas, alinha, fmt = json.loads(json.dumps(layout["estilos"][indice]))
    bordas = dict(bordas or {})
    bordas[lado] = list(DIVISORIA_TRACO)
    return _acha_ou_cria(layout, [fonte, fundo, bordas, alinha, fmt])


def _blocos(aba):
    dono = {}
    for m in aba["mescladas"]:
        c1, r1, c2, r2 = range_boundaries(m)
        for rr in range(r1, r2 + 1):
            for cc in range(c1, c2 + 1):
                dono[(rr, cc)] = (r1, c1, r2, c2)
    return dono


def _colunas_do_registro(aba, linha, de=1):
    cols = set()
    for r in aba["celulas"]:
        letras = "".join(ch for ch in r[0] if ch.isalpha())
        if r[0][len(letras):] == str(linha) and CI(letras) >= de:
            cols.add(CI(letras))
    return sorted(cols)


def _linhas_da_divisoria(layout):
    """Onde a linha que separa a moldura (cabeçalho e lombada, em tinta) do miolo passa:
      · FICHA: embaixo do cabeçalho (linha 5, da coluna C pra direita) e à direita da lombada (coluna B, da
        linha 6 até o fim);
      · INVOCAÇÃO: à direita da lombada (coluna B, do começo ao fim);
      · CARTEIRA: embaixo do cabeçalho (linha 4, de ponta a ponta) — o cartão inteiro é tinta, e o cabeçalho é
        papel.
    Devolve [(aba, [(linha, coluna)], lado, coordenada-molde)]."""
    A = {a["nome"]: a for a in layout["abas"]}
    return [
        ("FICHA", [(5, c) for c in _colunas_do_registro(A["FICHA"], 5, de=3)], "bottom", "C5"),
        ("FICHA", [(r, 2) for r in range(6, A["FICHA"]["linhas"] + 3)], "right", "B6"),
        ("INVOCAÇÃO", [(r, 2) for r in range(1, A["INVOCAÇÃO"]["linhas"] + 3)], "right", "B6"),
        ("CARTEIRA", [(4, c) for c in _colunas_do_registro(A["CARTEIRA"], 4)], "bottom", "A4"),
    ]


def celulas_da_divisoria(layout):
    """{(aba, coordenada): {lados}} de TODA célula que o gerador acaba com a divisória — o canto do bloco
    mesclado, que é onde ela é gravada, e o perímetro dele, onde o openpyxl a copia. O comparar-ficha-01.py
    usa isto pra saber que essa diferença é esperada."""
    out = {}
    for nome, alvos, lado, _ in _linhas_da_divisoria(layout):
        aba = next(a for a in layout["abas"] if a["nome"] == nome)
        dono = _blocos(aba)
        for r, c in alvos:
            if (r, c) in dono:
                r1, c1, r2, c2 = dono[(r, c)]
                if (lado == "bottom" and r != r2) or (lado == "right" and c != c2):
                    continue
                borda = ([(r2, cc) for cc in range(c1, c2 + 1)] if lado == "bottom"
                         else [(rr, c2) for rr in range(r1, r2 + 1)])
                borda.append((r1, c1))          # o canto, onde a borda e gravada, mesmo quando nao e da beirada
            else:
                borda = [(r, c)]
            for rr, cc in borda:
                out.setdefault((nome, f"{L(cc)}{rr}"), set()).add(lado)
    return out


def _divisorias(layout):
    """Grava a divisória no estilo da célula: a borda de célula que mora numa mesclagem vai no CANTO do
    bloco (é ali que o Sheets guarda o formato), e só se o lado dela for mesmo a beirada do bloco — senão a
    linha cortaria o bloco ao meio, e ela é pulada. Célula sem registro copia o estilo do molde."""
    n = 0
    for nome, alvos, lado, molde in _linhas_da_divisoria(layout):
        aba = next(a for a in layout["abas"] if a["nome"] == nome)
        reg = {r[0]: r for r in aba["celulas"]}
        dono = _blocos(aba)
        for r, c in alvos:
            if (r, c) in dono:
                r1, c1, r2, c2 = dono[(r, c)]
                if (lado == "bottom" and r != r2) or (lado == "right" and c != c2):
                    continue
                r, c = r1, c1
            coord = f"{L(c)}{r}"
            if coord not in reg:
                reg[coord] = [coord, None, reg[molde][2]]
                aba["celulas"].append(reg[coord])
            novo = _com_lado(layout, reg[coord][2], lado)
            if novo != reg[coord][2]:
                reg[coord][2] = novo
                n += 1
    return n


def aplica(layout):
    """Devolve quantas células mudaram de estilo."""
    return _origem_igual_caminho(layout) + _lombada_ate_o_fim(layout) + _divisorias(layout)
