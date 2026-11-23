# -*- coding: utf-8 -*-
"""Regressão das cartas R53 contra as fórmulas reais de uma cópia da oficial, no Google Planilhas.

Substitui a parte de conta de carta dos três testes pré-R53 (regressao-amaldicoada, regressao-invocacoes e
regressao-familias-invocacao), que montavam fichas no modelo de peças antigo e recalculavam no LibreOffice.

O gabarito:
  1. os casos do autor R53 (r53/testes/casos.json), que o avaliador local já aprova (r53/testes/verificar.py);
  2. as montagens que o livro imprime (ficha-v01/tecnica-do-livro.json), passadas para carta R53: o feitiço com os
     dados do livro distribuídos em dano tem de sair válido, com esses dados e sem sobra.
Ficam de fora os casos que trazem catálogo, Família ou Forma próprios: pedem uma aba de catálogo de teste.

O motor: as linhas feitico.1 a feitico.36 da DADOS_R53 de uma cópia DESCARTÁVEL. As entradas (B:AX) recebem os
valores do caso, no lugar do vínculo com a carta; as fórmulas de resultado (AY:FZ) ficam como a oficial as tem. Na
coluna GB, uma fórmula compara cada resultado com o esperado e escreve OK ou o que divergiu. Nada de construir(),
de importar .xlsx ou de LibreOffice.

Sem credencial nova: quem grava e lê é o conector do Google da conversa, então o teste tem dois passos.

    python regressao-r53-planilha.py montar 1      # imprime o JSON do lote 1: entradas B2:AX37 e fórmulas GB2:GB37
    python regressao-r53-planilha.py conferir 1 lidos.json   # lidos.json: a lista lida de GB2:GB37

Antes de montar, confere o próprio gabarito no avaliador local: se ele não reproduz um caso, o gabarito está errado.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "r53"), str(ROOT / "r53/testes")]
from modelo import INPUTS, ARVORE, DEFAULTS, OPCOES, calcular, arvore  # noqa: E402
from verificar import CASOS, BASE                                # noqa: E402
from formulas import native, x, evaluate                         # noqa: E402

# A carta da planilha é montada com registro_livre=True (ficha-v01/cartoes_diretos.py): o tipo do TR e a
# adjudicação moram na descrição da carta, e o modelo dispensa de propósito os avisos que pediam esses campos
# separados ("Escolha o tipo do TR", "TR da aplicação" etc., r53/modelo.py, err()). O gabarito da planilha é
# essa mesma variante; o caso do autor continua conferido na variante estrita, em gabarito().
LIVRE = arvore(registro_livre=True)


def calcular_livre(entradas):
    env = {**DEFAULTS, **entradas, "_familias": {}, "_formas": {}}
    for k, expr in LIVRE.items():
        env[k] = evaluate(expr, env, OPCOES)
    return env

LINHAS = 36                       # feitico.1..feitico.36 = linhas 2..37 da DADOS_R53
COL_CHECK = "GB"
CAMPOS = INPUTS + list(ARVORE)    # a mesma ordem do cabeçalho da DADOS_R53 (conferida em cabecalho())


def col(n):
    s = ""
    while n:
        n, a = divmod(n - 1, 26)
        s = chr(a + 65) + s
    return s


COLS = {k: col(i + 1) for i, k in enumerate(CAMPOS)}


def rotulo(m):
    """o livro escreve a peça pelo nome curto; o menu R53 traz a condição e o terreno com o detalhe.
    A Rede de contenção não diz qual terreno: os dois do menu são Leve, de Controle, e custam igual."""
    if m in OPCOES:
        return m
    if "Condição · " + m in OPCOES:
        return "Condição · " + m
    return {"Terreno": "Terreno · terreno difícil"}[m]


def casos_livro():
    tec = json.loads((ROOT / "ficha-v01/tecnica-do-livro.json").read_text(encoding="utf-8"))
    out = []
    for e in tec["feiticos_prontos"]:
        c, lib, dados = e["classe"], e["lib"], e["dados"]
        p = dados - (c if lib else 0)
        ent = {"classe": c, "forma": e["forma"], "dano": dados > 0, "p_dano": p}
        if lib:
            ent["modalidade"] = "Liberação Máxima"
        for i, m in enumerate(e["mel"], 1):
            ent[f"m{i}"] = rotulo(m)
        for i, r in enumerate(e["res"], 1):
            ent[f"r{i}"] = r.split("|")[0]
            ent[f"r{i}_valida"] = True
        for f in e["livres"]:
            ent["fam_" + f] = "Livre"
        out.append({"nome": "Livro • " + e["nome"], "entrada": ent,
                    "esperado": {"dano_d8": dados, "saldo": p, "valida": True}})
    return out


def todos(estrito=False):
    proprios = [c for c in CASOS if not (c.get("catalogo") or c.get("familias_custom") or c.get("formas"))]
    casos = proprios + casos_livro()
    if estrito:
        return casos
    out = []
    for c in casos:
        livre = calcular_livre({**BASE, **c["entrada"]})
        inteiro = lambda v: int(v) if isinstance(v, float) and v.is_integer() else v   # 4.0 do avaliador é o 4 do caso
        esp = {k: inteiro(livre[k]) for k in c["esperado"]}
        contem = {k: v for k, v in c.get("contem", {}).items() if v in str(livre[k])}
        nao = {k: v for k, v in c.get("nao_contem", {}).items() if v not in str(livre[k])}
        mudou = esp != c["esperado"] or contem != c.get("contem", {}) or nao != c.get("nao_contem", {})
        out.append({**c, "nome": c["nome"] + (" (registro livre)" if mudou else ""), "esperado": esp,
                    "contem": contem, "nao_contem": nao})
    return out


def gabarito():
    """o avaliador local tem de reproduzir cada caso; senão o problema é o gabarito, não a planilha"""
    erros = []
    for caso in todos(estrito=True):
        obt = calcular({**BASE, **caso["entrada"]})
        for k, v in caso["esperado"].items():
            if obt[k] != v:
                erros.append(f"{caso['nome']}: {k} esperado {v!r}, avaliador {obt[k]!r}")
    return erros


def lotes():
    t = todos()
    return [t[i:i + LINHAS] for i in range(0, len(t), LINHAS)]


def checagem(caso, lin):
    partes = []
    for k, v in caso["esperado"].items():
        c = f"{COLS[k]}{lin}"
        lit = native(x(v), {}, "", [], separator=";")
        partes.append(f'IFERROR(IF({c}={lit};"";"{k}="&{c});"{k}=#ERRO")')
    for k, v in caso.get("contem", {}).items():
        c = f"{COLS[k]}{lin}"
        partes.append(f'IF(ISNUMBER(SEARCH({native(x(v), {}, "", [], separator=";")};{c}));"";"{k} sem o trecho")')
    for k, v in caso.get("nao_contem", {}).items():
        c = f"{COLS[k]}{lin}"
        partes.append(f'IF(ISNUMBER(SEARCH({native(x(v), {}, "", [], separator=";")};{c}));"{k} com trecho proibido";"")')
    return '=LET(e;TEXTJOIN(" | ";TRUE;' + ";".join(partes) + ');IF(e="";"OK";"FALHA "&e))'


def montar(n):
    lote = lotes()[n - 1]
    entradas, formulas = [], []
    for i in range(LINHAS):
        lin = i + 2
        if i < len(lote):
            v = {**DEFAULTS, **BASE, "nome": lote[i]["nome"], **lote[i]["entrada"]}   # a linha só calcula com nome
            entradas.append([v[k] for k in INPUTS[1:]])          # B:AX; a coluna A (id) fica
            formulas.append([checagem(lote[i], lin)])
        else:
            entradas.append([DEFAULTS[k] for k in INPUTS[1:]])
            formulas.append([""])
    ultima = col(len(INPUTS))
    return {"entradas": {"range": f"DADOS_R53!B2:{ultima}{LINHAS + 1}", "values": entradas},
            "checagem": {"range": f"DADOS_R53!{COL_CHECK}2:{COL_CHECK}{LINHAS + 1}", "formulas": formulas},
            "casos": [c["nome"] for c in lote]}


def conferir(n, arquivo):
    lote = lotes()[n - 1]
    lidos = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    if isinstance(lidos, dict):
        lidos = lidos.get("values", [])
    lidos = [(r[0] if r else "") for r in lidos]
    falhas = 0
    for i, caso in enumerate(lote):
        got = lidos[i] if i < len(lidos) else "(não lido)"
        ok = got == "OK"
        falhas += not ok
        print(f"  [{'OK' if ok else 'FALHA'}] {caso['nome']}" + ("" if ok else f"  <- {got}"))
    print(f"\nlote {n}: {len(lote) - falhas} de {len(lote)} batem com as fórmulas da planilha")
    return falhas


def cabecalho(arquivo):
    """o cabeçalho lido de DADOS_R53!A1:FZ1 tem de ser o do modelo, na mesma ordem"""
    lido = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    lido = lido["values"][0] if isinstance(lido, dict) else lido
    return [f"coluna {col(i + 1)}: planilha {a!r}, modelo {b!r}" for i, (a, b) in enumerate(zip(lido, CAMPOS)) if a != b] + \
           ([f"tamanho: planilha {len(lido)}, modelo {len(CAMPOS)}"] if len(lido) != len(CAMPOS) else [])


if __name__ == "__main__":
    erros = gabarito()
    if erros:
        print("O GABARITO NÃO BATE COM O AVALIADOR LOCAL:\n  " + "\n  ".join(erros))
        sys.exit(1)
    acao = sys.argv[1] if len(sys.argv) > 1 else "resumo"
    if acao == "montar":
        print(json.dumps(montar(int(sys.argv[2])), ensure_ascii=False))
    elif acao == "conferir":
        sys.exit(1 if conferir(int(sys.argv[2]), sys.argv[3]) else 0)
    elif acao == "cabecalho":
        e = cabecalho(sys.argv[2])
        print("\n".join(e) if e else "o cabeçalho da DADOS_R53 é o do modelo")
        sys.exit(1 if e else 0)
    else:
        print(f"{len(todos())} casos no gabarito, todos reproduzidos pelo avaliador local; {len(lotes())} lotes de até {LINHAS}")
