# -*- coding: utf-8 -*-
"""A aba GLOSSÁRIO: o que cada atributo, perícia, ofício e termo da FICHA representa, pra quem
nunca jogou. Nasce entre a DADOS e a INVOCAÇÃO -- não atrapalha quem já sabe folhear pra CARTEIRA,
FICHA, INVOCAÇÃO, CATÁLOGO, e fica perto da FICHA pra quem ainda tá aprendendo.

Não existe planilha viva desta aba: ao contrário das outras seis, ela nasce inteira aqui, sem
desenho do Mizuki por trás. Por isso ela reaproveita os MESMOS índices de estilo que o CATÁLOGO já
usa pra tabela de três colunas (ponto/nome/o que faz) -- mesma fonte, cor e borda, sem inventar
nada visual novo. O comparar-ficha-01.py sabe que ela não tem original pra comparar.

O texto sai do catálogo (perícias, ofícios) e do manual.txt (atributos, treino, maestria, refino) --
nada aqui é escrito de cabeça. 17/09/2026, pedido do Mizuki.
"""
import json, os, re

import indice_ficha as ix

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# os estilos que o CATALOGO ja usa pra tabela de tres colunas: titulo, tag, cabecalho de secao,
# cabecalho de coluna (centro e esquerda), e as tres colunas alternando linha A/B
E_TITULO, E_TAG, E_SECAO, E_NOTA = 160, 122, 163, 164
E_COL_CENTRO, E_COL_ESQ = 50, 133
E_D = (63, 168)     # coluna estreita (D:G) -- centralizada
E_H = (96, 139)     # coluna do nome (H:O) -- Castoro, esquerda
E_P = (143, 169)    # coluna larga (P:AT) -- Roboto, esquerda

# 34 colunas, nao 51 como o CATALOGO: o conferir-ficha-xlsx.py cobra 1200-1366px de toda aba
# visivel que nao e da invocacao, pra caber num notebook -- 34 x 39px = 1326px
COLS = 34
C_D, C_G = 2, 4         # coluna estreita -- atributo do oficio/pericia
C_H, C_O = 5, 10        # coluna do nome
C_P, C_AT = 11, 33      # coluna larga -- o que faz
SEC_TITULO_FIM, SEC_NOTA_INI = 12, 13          # onde o titulo da secao termina e a nota comeca
PAGINA_TITULO_FIM, PAGINA_TAG_INI = 22, 23     # o mesmo, pro titulo da pagina
ALTURA_DADO = 30.0     # linha de dado, mais alta que o padrao de 15.75 -- cabe a quebra de linha
MARGEM = C_AT + 1      # a coluna de respiro da direita, pedido do Mizuki em 17/09/2026


FUNDO_CANVAS = "FF120F1D"   # o mesmo fundo que a FICHA, a DADOS, a INVOCACAO e o CATALOGO usam
                            # fora da caixa -- e nao a cor da linha, que muda por dentro da tabela


def _estilo_flat(layout, cor):
    """um estilo sem borda e sem fonte, so com o fundo `cor` -- a moldura (coluna A e a margem da
    direita) que fica igual em toda linha, ao contrario da tabela por dentro. 17/09/2026, achado
    do Mizuki: a margem estava seguindo a cor de cada linha, e devia ser fixa, como nas outras abas."""
    novo = [None, cor, None, None, None]
    chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(novo)
    return len(layout["estilos"]) - 1


def _estilo_com_borda(layout, indice, lado, traco, cor):
    """o mesmo estilo, com mais um lado de borda. 19/09/2026, achado do Mizuki: o título da página
    saía sem a borda da esquerda. No CATÁLOGO, de onde o estilo vem, a ponta esquerda do título é uma
    célula a parte (C1:C2) com borda própria, e este estilo — o do canto do título — só leva o de cima
    e o de baixo; o GLOSSÁRIO copiava só o canto, e perdia a ponta."""
    fonte, fundo, bordas, alinha, fmt = json.loads(json.dumps(layout["estilos"][indice]))
    bordas = dict(bordas or {})
    bordas[lado] = [traco, cor]
    novo = [fonte, fundo, bordas, alinha, fmt]
    chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(novo)
    return len(layout["estilos"]) - 1


def _estilo_com_quebra(layout, indice):
    """o mesmo estilo, com wrap_text ligado -- pra descricao nao estourar a coluna estreita desta
    aba (34 colunas, nao as 51 do CATALOGO). Acha um estilo igual se ja existir, senao cria."""
    fonte, fundo, bordas, alinha, fmt = json.loads(json.dumps(layout["estilos"][indice]))
    novo = [fonte, fundo, bordas, [alinha[0], alinha[1], True, alinha[3]], fmt]
    chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(novo)
    return len(layout["estilos"]) - 1


def _limpa(txt):
    """A extracao as vezes vaza pedaco de tabela vizinha (ex: Provocar). Corta na primeira frase
    que fecha o pensamento -- ate dois pontos finais -- e tira espaco duplo."""
    txt = re.sub(r"\s+", " ", txt).strip()
    partes = txt.split(". ")
    return ". ".join(partes[:2]).rstrip(".") + "."


_ATRS = ["Força", "Destreza", "Constituição", "Inteligência", "Essência"]


def _atributos_governa(M):
    """a tabela ATRIBUTO / O QUE GOVERNA, do capitulo 1 -- cada linha ate o nome do proximo
    atributo, e a ultima ate o numero de pagina que a extracao do manual deixa colado"""
    anc = M.find("O QUE GOVERNA")
    if anc < 0:
        raise SystemExit("nao achei a tabela 'O QUE GOVERNA' dos atributos no manual.txt")
    janela = M[anc:anc + 800]
    out = []
    for i, nome in enumerate(_ATRS):
        prox = _ATRS[i + 1] if i + 1 < len(_ATRS) else None
        rx = rf"{nome}\s+(.+?)\s+{prox}\s" if prox else rf"{nome}\s+([^\d]+?)\s+\d"
        pad = re.search(rx, janela)
        if not pad:
            raise SystemExit(f"nao achei 'o que governa' do atributo {nome!r}")
        out.append((nome, pad.group(1).strip()))
    return out


# pra que serve cada perícia -- uma frase antes do exemplo (que já vem do catálogo), no molde de
# "a perícia mede X" que o D&D usa. 17/09/2026, pedido do Mizuki: o "onde é usado" vira exemplo,
# não definição -- quem nunca jogou precisa saber o que cobrar antes de ver a lista de casos.
PROPOSITO_PERICIA = {
    "Atletismo": "mede seu corpo em esforço físico direto.",
    "Acrobacia": "mede seu equilíbrio e o controle fino do próprio corpo em movimento.",
    "Furtividade": "mede sua capacidade de passar despercebido.",
    "Pontaria": "mede sua precisão ao mirar num alvo específico, fora de uma rolagem de ataque.",
    "Prestidigitação": "mede a destreza manual fina — mão rápida, gesto discreto.",
    "Investigação": "mede sua capacidade de vasculhar um lugar e ligar pistas soltas.",
    "Intuição": "mede sua leitura racional do comportamento alheio — dedução sobre gente.",
    "Ocultismo": "mede seu conhecimento técnico de maldições e do funcionamento da energia amaldiçoada.",
    "Religião": "mede seu conhecimento do lado sagrado e ritual do jujutsu.",
    "História": "mede sua memória do que já aconteceu e de quem estava lá.",
    "Hierarquia": "mede seu conhecimento da política entre clãs e feiticeiros — quem manda em quem.",
    "Medicina": "mede seu conhecimento teórico de ferimento, veneno e doença.",
    "Sobrevivência": "mede sua capacidade de aguentar e se orientar num ambiente hostil.",
    "Natureza": "mede seu conhecimento do mundo natural — planta, bicho, clima, terreno.",
    "Lidar com Animais": "mede sua capacidade de acalmar, montar ou conduzir um animal.",
    "Tecnologia": "mede seu domínio de equipamento e sistema moderno.",
    "Sentir Energia": "mede sua sensibilidade direta à energia amaldiçoada.",
    "Percepção": "mede sua atenção ao que os cinco sentidos comuns captam — o lado mundano.",
    "Persuasão": "mede sua capacidade de convencer alguém a fazer o que você quer porque quer.",
    "Enganação": "mede sua capacidade de mentir de um jeito convincente.",
    "Intimidação": "mede sua capacidade de fazer alguém recuar pela ameaça ou pela presença.",
    "Atuação": "mede sua capacidade de performar ou sustentar um papel diante de alguém.",
    "Provocar": "mede sua capacidade de tirar alguém do sério e puxá-lo pra cima de você — o oposto de Intimidação.",
}
PROPOSITO_OFICIO = {
    "Condução": "mede sua capacidade de operar um veículo.",
    "Arrombamento": "mede sua capacidade de vencer uma trava sem ter a chave.",
    "Herbalismo": "mede seu conhecimento prático de planta, aplicado a cura e a veneno.",
    "Forja": "mede sua capacidade de fabricar, afiar e manter arma e ferramenta.",
    "Caligrafia": "mede sua capacidade de produzir documento escrito, oficial ou falsificado.",
    "Burocracia": "mede seu domínio da máquina administrativa jujutsu por dentro.",
    "Entalhador": "mede sua capacidade de moldar madeira, pedra ou osso.",
    "Alfaiate": "mede sua capacidade de cortar, costurar e remendar tecido.",
    "Culinária": "mede sua capacidade de cozinhar de verdade.",
    "Instrumento": "mede sua capacidade de tocar um instrumento musical.",
    "Jogatina": "mede sua capacidade de jogar um jogo de aposta e ler quem está na mesa.",
}
PROPOSITO_ATRIBUTO = {
    "Força": "quanto o seu corpo aguenta e impõe, na base do músculo.",
    "Destreza": "sua velocidade e precisão — o corpo respondendo rápido, a mira certa.",
    "Constituição": "sua resistência bruta a dano e a desgaste.",
    "Inteligência": "o que você sabe e deduz — o raciocínio frio.",
    "Essência": "sua sensibilidade à energia amaldiçoada e às pessoas — o que você sente, não o que você calcula.",
}


def conteudo(CAT=None, M=None):
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    if M is None:
        M = " ".join(open(os.path.join(RAIZ, "manual.txt"), encoding="utf-8").read().split())
    def _maiuscula(s):
        return s[0].upper() + s[1:] if s else s
    atributos = [(n, _maiuscula(f"{PROPOSITO_ATRIBUTO[n]} Governa: {g}")) for n, g in _atributos_governa(M)]
    pericias = sorted(((n, v["atributo"], _maiuscula(f"{PROPOSITO_PERICIA[n]} Exemplo: {_limpa(v['descricao'])}"))
                       for n, v in CAT["pericias"].items()), key=lambda x: x[0])
    oficios = sorted(((n, _maiuscula(f"{PROPOSITO_OFICIO[n]} Exemplo: {_limpa(v)}"))
                      for n, v in CAT["oficios"].items()), key=lambda x: x[0])
    conceitos = [
        ("Treino", "Ter a perícia ou o ofício marcado na ficha. O mestre põe uma CD; com Destreza 3 e "
                   "maestria 1, uma Furtividade treinada rola d20 + 4, sem treino d20 + 3 (capítulo 2)."),
        ("Maestria", "O bônus que mede o tempo de estrada do personagem: começa em 1 e sobe um ponto a "
                     "cada oito níveis. Entra em toda rolagem de ataque, na CD dos seus feitiços, e no "
                     "que você treinou (capítulo 1)."),
        ("Refino", "O eixo de controle da ficha: é o refino que compra as suas Aptidões. Poder é quanto "
                   "você tem — Refino é quanto você não desperdiça (capítulo 13)."),
    ]
    return {"atributos": atributos, "pericias": pericias, "oficios": oficios, "conceitos": conceitos}


def _secao(linhas_out, mesclas, alturas, titulo, nota, cab, dados, lin0, e_d, e_h, e_p):
    """emite uma secao inteira (cabecalho + cabecalho de coluna + linhas de dado), devolve a
    proxima linha livre. `dados` e uma lista de tuplas (2 ou 3 campos, D/H/P). `e_d/e_h/e_p` sao
    os pares de estilo (com quebra de linha) ja resolvidos pro layout que vai receber a aba."""
    lin = lin0
    mesclas.append(f"{ix._letras(C_D)}{lin}:{ix._letras(SEC_TITULO_FIM)}{lin}")
    linhas_out[f"{ix._letras(C_D)}{lin}"] = (titulo, E_SECAO)
    if nota:
        mesclas.append(f"{ix._letras(SEC_NOTA_INI)}{lin}:{ix._letras(C_AT)}{lin}")
        linhas_out[f"{ix._letras(SEC_NOTA_INI)}{lin}"] = (nota, E_NOTA)
    lin += 1
    for col, (c0, c1), rot, e in ((0, (C_D, C_G), cab[0], E_COL_CENTRO if cab[0] else None),
                                   (1, (C_H, C_O), cab[1], E_COL_ESQ),
                                   (2, (C_P, C_AT), cab[2], E_COL_ESQ)):
        if rot is None:
            continue
        mesclas.append(f"{ix._letras(c0)}{lin}:{ix._letras(c1)}{lin}")
        linhas_out[f"{ix._letras(c0)}{lin}"] = (rot, e)
    lin += 1
    for i, linha in enumerate(dados):
        par = i % 2
        if len(linha) == 2:
            nome, desc = linha
            campos = (None, nome, desc)
        else:
            campos = linha
        for col, (c0, c1), estilos in ((0, (C_D, C_G), e_d), (1, (C_H, C_O), e_h), (2, (C_P, C_AT), e_p)):
            v = campos[col]
            mesclas.append(f"{ix._letras(c0)}{lin}:{ix._letras(c1)}{lin}")
            linhas_out[f"{ix._letras(c0)}{lin}"] = (v, estilos[par])
        alturas.append([lin, ALTURA_DADO])
        lin += 1
    return lin + 1                                       # uma linha em branco antes da proxima secao


def aba(layout, CAT=None, M=None):
    """a aba GLOSSARIO inteira, pronta pra entrar em layout['abas']. So mexe no `layout` pra
    registrar os tres pares de estilo com quebra de linha -- o resto reaproveita o que o
    CATALOGO ja usa."""
    e_d = tuple(_estilo_com_quebra(layout, i) for i in E_D)
    e_h = tuple(_estilo_com_quebra(layout, i) for i in E_H)
    e_p = tuple(_estilo_com_quebra(layout, i) for i in E_P)

    dados = conteudo(CAT, M)
    cel, mesclas, alturas = {}, [], [[1, 16.0], [2, 16.0]]
    mesclas.append(f"{ix._letras(C_D)}1:{ix._letras(PAGINA_TITULO_FIM)}2")
    e_titulo = _estilo_com_borda(layout, E_TITULO, "left", "medium", "FF8A7EC4")
    cel[f"{ix._letras(C_D)}1"] = ("O GLOSSÁRIO — o que cada coisa da ficha quer dizer", e_titulo)
    mesclas.append(f"{ix._letras(PAGINA_TAG_INI)}1:{ix._letras(C_AT)}2")
    cel[f"{ix._letras(PAGINA_TAG_INI)}1"] = ("Capítulo 1 · 2 · 13", E_TAG)

    lin = 4
    lin = _secao(cel, mesclas, alturas, "ATRIBUTOS",
                 "O número é o modificador. Escala de 0 a 6, sem tabela de conversão.",
                 (None, "ATRIBUTO", "O QUE GOVERNA"), dados["atributos"], lin, e_d, e_h, e_p)
    lin = _secao(cel, mesclas, alturas, "PERÍCIAS",
                 "9 de 23 na criação — ou 10, trocando os dois ofícios da Origem.",
                 ("ATRIBUTO", "NOME", "O QUE FAZ"), dados["pericias"], lin, e_d, e_h, e_p)
    lin = _secao(cel, mesclas, alturas, "OFÍCIOS",
                 "2 de 11 na criação. O atributo é do mestre, na hora — não é fixo.",
                 (None, "NOME", "O QUE FAZ"), dados["oficios"], lin, e_d, e_h, e_p)
    lin = _secao(cel, mesclas, alturas, "CONCEITOS", None, (None, "TERMO", "O QUE SIGNIFICA"),
                 dados["conceitos"], lin, e_d, e_h, e_p)

    # a moldura -- coluna A e a margem da direita -- fica no mesmo fundo em toda linha, igual as
    # outras abas: nao acompanha a cor de dentro da tabela.
    e_canvas = _estilo_flat(layout, FUNDO_CANVAS)
    for r in range(1, lin):
        cel[f"A{r}"] = (None, e_canvas)
        cel[f"{ix._letras(MARGEM)}{r}"] = (None, e_canvas)

    return {
        "nome": "GLOSSÁRIO", "estado": "visible", "linhas": lin, "colunas": COLS,
        "colunas_larg": [[1, COLS, 5.0]], "linhas_alt": alturas,
        "altura_padrao": 15.75, "grade": False,
        "celulas": [[k, v[0], v[1]] for k, v in cel.items()],
        "mescladas": mesclas, "menus": [], "condicional": [], "imagens": [],
    }
