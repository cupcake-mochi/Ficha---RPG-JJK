# -*- coding: utf-8 -*-
"""Confere um feitico do Projeto M contra as oito regras de ouro (manual p.132).
Nenhum valor mora aqui: tudo le do catalogo-projeto-m.json."""
import json, math, sys
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
DEC = json.load(open('decisoes-ficha.json', encoding='utf-8'))
MEL, RES, FUN = CAT["melhorias"], CAT["restricoes"], CAT["fundamento"]
FREQUENCIA = {"Uma Vez", "Condicional", "Aquecer", "Dívida"}   # manual p.124
TETO_MELHORIAS = lambda c: 2 if c <= 2 else (3 if c <= 4 else 4)

def preco(peso, classe, livre):
    base = {"Leve": classe/2, "Media": classe, "Pesada": classe*1.5}[peso]
    p = math.ceil(base)
    return max(1, p - math.ceil(classe/2)) if livre else p   # desconto de Familia Livre, minimo 1

def devolucao(nivel, classe):
    return math.ceil({"Leve": classe/2, "Media": classe}[nivel])

def conferir(f):
    c, livres, fechadas = f["classe"], set(f["familias_livres"]), set(f["familias_fechadas"])
    erros, orcamento = [], 3 * c
    # regra 3
    if len(f["melhorias"]) > TETO_MELHORIAS(c):
        erros.append(f"R3: {len(f['melhorias'])} Melhorias na Classe {c}; o teto e {TETO_MELHORIAS(c)}")
    if len(f["restricoes"]) > 2:
        erros.append(f"R3: {len(f['restricoes'])} Restricoes; o teto e 2")
    # familia fechada
    for m in f["melhorias"]:
        fam = MEL[m]["familia"]
        if fam in fechadas:
            erros.append(f"Familia fechada: '{m}' e de {fam}, que voce fechou")
    # regra 7
    freq = [r for r in f["restricoes"] if r in FREQUENCIA]
    if len(freq) >= 2:
        erros.append(f"R7: {' e '.join(freq)} sao as duas de frequencia")
    # incompatibilidades: pares que nao entram no mesmo feitico.
    # Os pares moram no decisoes-ficha.json, nao aqui, e cada um declara a fonte:
    #   'manual' -> a frase esta escrita na tabela da Familia Tempo
    #   'ficha'  -> decisao A3, que o manual nao carrega (dividida B6 do PENDENCIAS)
    escolhidas = set(f["melhorias"]) | set(f["restricoes"])
    if f.get("forma"):
        escolhidas.add(f["forma"])
    for par in DEC["A3_incompatibilidades"]["pares"]:
        if par["a"] in escolhidas and par["b"] in escolhidas:
            erros.append(f"A3: '{par['a']}' e '{par['b']}' nao entram no mesmo feitico "
                         f"(fonte: {par['fonte']})")

    # nota: Restricao que o Selo ja obriga nao devolve ponto
    devolvido = sum(devolucao(RES[r]["devolve"], c) for r in f["restricoes"]
                    if r not in f.get("obrigadas_pelo_selo", []))
    teto_dev = 2 * c                                          # regra 4
    if devolvido > teto_dev:
        devolvido = teto_dev
    custo = sum(preco(MEL[m]["peso"], c, MEL[m]["familia"] in livres) for m in f["melhorias"])
    # a Forma tambem custa ponto (manual p.110). Ela nao conta no LIMITE de Melhorias (regra 3),
    # mas conta no orcamento. Achado pela regressao contra o Domo de Gelo, p.137.
    forma = f.get("forma")
    if forma and CAT["formas"][forma].get("custa"):
        F = CAT["formas"][forma]
        custo += preco(F["custa"], c, F["familia"] in livres)
    # regra 1: Restricao so paga Melhoria; o excedente some, nunca vira dano
    pago_por_restricao = min(devolvido, custo)
    liquido = custo - pago_por_restricao
    sobra = orcamento - liquido
    if sobra < 0:
        erros.append(f"Orcamento estourado: custo liquido {liquido}, orcamento {orcamento}")
    dados = max(0, sobra)                                     # ponto nao gasto vira 1d8
    # regra 2 tem DUAS metades, e sao tetos diferentes (manual p.132 e p.137):
    #   (a) contra um alvo so: o dano para nos pontos da Classe (3 x Classe).
    #       Liberacao Maxima e a excecao, e pode chegar a 4 x Classe num alvo.
    #   (b) o total, somando alvos e repeticoes: 4 x Classe.
    teto_alvo = 4 * c if f.get("liberacao_maxima") else 3 * c
    if dados > teto_alvo:
        erros.append(f"R2a: {dados}d8 num alvo passa do teto de {teto_alvo} na Classe {c}")
    # (b) total somando alvos e repeticoes. O manual p.135 nomeia as quatro pecas que
    # espalham dano: Salto, Rajada, Mais Um e Queima. Salto e Queima ADICIONAM metade
    # dos dados; Mais Um e Rajada DIVIDEM (a soma das partes nao cresce).
    ESPALHA = {"Salto": 0.5, "Queima": 0.5}
    total = dados + sum(dados * ESPALHA[m] for m in f["melhorias"] if m in ESPALHA)
    if total > 4 * c:
        erros.append(f"R2b: {total:g} dados somando alvos e repeticoes passa do teto de {4*c} na Classe {c}")
    return {"orcamento": orcamento, "custo_bruto": custo, "restricao_devolveu": devolvido,
            "usado_para_pagar": pago_por_restricao, "excedente_perdido": devolvido - pago_por_restricao,
            "custo_liquido": liquido, "dano": f"{dados}d8", "custo_pe": 3*c, "erros": erros}

def mostra(nome, f):
    r = conferir(f)
    print(f"\n{nome}  (Classe {f['classe']})")
    print(f"  orcamento {r['orcamento']} pts | Melhorias custam {r['custo_bruto']} | "
          f"Restricao devolveu {r['restricao_devolveu']} (usou {r['usado_para_pagar']}, "
          f"perdeu {r['excedente_perdido']})")
    print(f"  liquido {r['custo_liquido']} -> dano {r['dano']} | PE {r['custo_pe']}")
    print("  " + ("LEGAL" if not r["erros"] else "ILEGAL:"))
    for e in r["erros"]: print(f"    x {e}")
    return r
