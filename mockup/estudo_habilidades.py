# -*- coding: utf-8 -*-
"""Monta o estudo da seção 7 da FICHA, que deixa de ser "Anotações" e vira "Habilidades" (mockup/habilidades-estudo.html).

Pedido do Mizuki em 02/10/2026, antes de pôr o catálogo em dia (B33): "Recomendo que refaçamos o 'anotações' (ja que
agora caminho da 5 habilidades)", com protótipos de formato. E, no meio da rodada: "nem precisa de automação AINDA
(deixar preparado é o ideal), ja q o livro está sendo reescrito, deixando claro isso".

Então a seção é escrita pelo jogador, e a forma já é a que o livro dá: o Caminho entrega cinco degraus (níveis 2, 7,
15, 23 e 30) e a Trilha quatro entregas (2, 11, 19 e 27). Quando o livro assentar, cada caixa pode passar a vir do livro
sem redesenho.

Os exemplos saem do capítulo 35 do livro no disco do Claude 2 (a v0.331, sem commit, que está sendo reescrita): os
nomes de cada nível vêm da tabela de habilidades do Caminho e da Trilha, e o "texto do jogador" de exemplo é o começo do
texto do livro, como alguém anotaria. Nada aqui é regra nova, e o livro não é editado.

    python3 mockup/estudo_habilidades.py
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
LIVRO = "/media/mizuki/HD Externo II/Claude/Claude 2/sistema/05-material/livro/manual"
CAP = open(os.path.join(LIVRO, "35-caminhos-e-trilhas.md"), encoding="utf-8").read()
CAMINHOS = ["Bastião", "Vanguarda", "Guia", "Emanador", "Evocador", "Incursor"]
NIV_CAM, NIV_TRI = [2, 7, 15, 23, 30], [2, 11, 19, 27]


def limpa(t):
    """o texto corrido do livro, sem marcação: citação, negrito, crase, títulos, tabelas e listas viram frases"""
    linhas = []
    for l in t.split("\n"):
        l = re.sub(r"^>\s?", "", l).strip()
        if not l or l.startswith("{:") or re.match(r"^\|?[-| ]+\|?$", l):
            continue
        if l.startswith("|"):
            l = " — ".join(c.strip() for c in l.strip("|").split("|") if c.strip())
        l = re.sub(r"^#+\s*", "", l)
        l = re.sub(r"^[-*]\s+", "", l)
        linhas.append(l)
    t = " ".join(linhas)
    t = re.sub(r"[`*_]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def frases(t, teto):
    """as primeiras frases do texto que cabem em `teto` letras; uma frase só, cortada na palavra, se nem ela cabe"""
    out = ""
    for f in re.split(r"(?<=[.!?])\s+", t):
        if len(out) + len(f) + 1 > teto:
            break
        out = (out + " " + f).strip()
    if not out:
        out = t[:teto].rsplit(" ", 1)[0] + "…"
    return out


def secao(inicio, fim_rx):
    i = CAP.index(inicio)
    m = re.compile(fim_rx, re.M).search(CAP, i + len(inicio))
    return CAP[i:m.start() if m else len(CAP)]


def tabela_de_niveis(bloco):
    """os nomes de cada nível, da primeira tabela que abre com 'Nível |' no bloco. A segunda coluna é a habilidade; a do
    Batedor tem uma coluna por rota (Yumi, Besta, Arma de Fogo), e aí os nomes vão juntos, com a rota na frente"""
    m = re.search(r"^\| Nível \|(.*)\|\n\|[-| ]+\|\n((?:\|.*\|\n?)+)", bloco, re.M)
    if not m:
        # as Trilhas do Guia não têm tabela: o nome está na própria linha do nível ("> **Nível 2: `Obras de Apoio`.**")
        out = {}
        for n, nome in re.findall(r"^(?:> \*\*Nível |#{3,5} Nível )(\d+)[:\s—-]+`?([^`.*\n]+)", bloco, re.M):
            out.setdefault(int(n), []).append(nome.strip())
        return {n: " e ".join(v) for n, v in out.items()}
    cab = [x.strip() for x in m.group(1).split("|")]
    por_rota = not cab[0].startswith("Habilidade")
    out = {}
    for l in m.group(2).strip().split("\n"):
        c = [x.strip() for x in l.strip("|").split("|")]
        nomes = " · ".join(f"{r}: {v}" for r, v in zip(cab, c[1:])) if por_rota else c[1]
        out[int(re.sub(r"\D", "", c[0]))] = re.sub(r"[`*]", "", nomes).rstrip(".")
    return out


def textos_por_nivel(bloco, niveis):
    """o texto de cada nível: tudo o que vem depois de '**Nível N' (citação) ou de um título 'Nível N', até o próximo"""
    marcas = [(m.start(), int(m.group(1))) for m in re.finditer(r"^(?:> \*\*Nível |#{3,5} Nível )(\d+)", bloco, re.M)]
    out = {n: "" for n in niveis}
    for k, (ini, n) in enumerate(marcas):
        fim = marcas[k + 1][0] if k + 1 < len(marcas) else len(bloco)
        if n in out:
            out[n] += "\n" + bloco[ini:fim]
    return {n: limpa(t) for n, t in out.items()}


def slots(bloco, niveis, fonte):
    nomes, textos = tabela_de_niveis(bloco), textos_por_nivel(bloco, niveis)
    out = []
    for n in niveis:
        t = re.sub(r"^Nível \d+\s*[:—–-]?\s*", "", textos[n])
        # o resumo de exemplo não repete o nome que já está na linha de cima, nem a frase que aponta para o texto de baixo
        so_nome = {x.strip().rstrip(".") for x in re.split(r",| e |·|:", nomes.get(n, "")) if x.strip()}
        t = " ".join(f for f in re.split(r"(?<=[.!?])\s+", t)
                     if f.rstrip(".") not in so_nome and not re.match(r"^Nível \d+", f) and "abaixo" not in f)
        uso = []
        if re.search(r"\bAção Bônus\b", t[:400]): uso.append("Ação Bônus")
        if re.search(r"\bReação\b", t[:400]): uso.append("Reação")
        if re.search(r"[Uu]ma vez por cena|1× por cena", t[:600]): uso.append("1× por cena")
        out.append({"fonte": fonte, "nivel": n, "nomes": nomes.get(n, ""), "livro": len(t),
                    "resumo": frases(t, 220), "linha": frases(t, 95), "uso": " · ".join(uso) or "Passiva"})
    return out


dados = {"caminhos": [], "niv_cam": NIV_CAM, "niv_tri": NIV_TRI}
for i, cam in enumerate(CAMINHOS):
    prox = CAMINHOS[i + 1] if i + 1 < len(CAMINHOS) else None
    bloco = secao(f"## {cam}\n", r"^## " + re.escape(prox) + r"\n" if prox else r"\Z")
    base = bloco.split("### Trilha:")[0]
    trilhas = re.findall(r"^### Trilha: (.+)$", bloco, re.M)
    c = {"nome": cam, "slots": slots(base, NIV_CAM, "Caminho"), "trilhas": []}
    for t in trilhas:
        tb = secao(f"### Trilha: {t}\n", r"^### Trilha: |^## ")
        c["trilhas"].append({"nome": t, "slots": slots(tb, NIV_TRI, "Trilha")})
    dados["caminhos"].append(c)

# a conferência do leitor: cinco degraus e quatro entregas com nome e texto em todos, nos seis Caminhos
faltas = [f"{c['nome']} {s['nivel']}" for c in dados["caminhos"] for s in c["slots"] if not (s["nomes"] and s["livro"])]
faltas += [f"{t['nome']} {s['nivel']}" for c in dados["caminhos"] for t in c["trilhas"] for s in t["slots"] if not (s["nomes"] and s["livro"])]
if faltas or sum(len(c["trilhas"]) for c in dados["caminhos"]) != 18:
    raise SystemExit(f"estudo_habilidades: o leitor do capítulo 35 não achou tudo: {faltas}")
todos = [s["livro"] for c in dados["caminhos"] for s in c["slots"] + [x for t in c["trilhas"] for x in t["slots"]]]
dados["livro_min"], dados["livro_max"], dados["livro_med"] = min(todos), max(todos), sorted(todos)[len(todos) // 2]

css = re.search(r"<style>([\s\S]*?)</style>", open(os.path.join(AQUI, "ficha-pessoal-estudo.html"), encoding="utf-8").read()).group(1)
modelo = open(os.path.join(AQUI, "habilidades-estudo.modelo.html"), encoding="utf-8").read()
html = modelo.replace("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/", css).replace("/*DADOS*/", json.dumps(dados, ensure_ascii=False))
open(os.path.join(AQUI, "habilidades-estudo.html"), "w", encoding="utf-8").write(html)
print(f"mockup/habilidades-estudo.html: 6 Caminhos, 18 Trilhas; o texto do livro de um nível vai de {dados['livro_min']} a "
      f"{dados['livro_max']} letras (mediana {dados['livro_med']})")
