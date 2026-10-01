# -*- coding: utf-8 -*-
"""Monta o estudo da Ficha Amaldiçoada (mockup/ficha-amaldicoada-estudo.html).

O estudo é um protótipo em HTML, para o Mizuki ver e mexer antes de a aba ser construída no gerador. O desenho da
página (cores, fontes, a folha na grade de 47 colunas) é o do estudo da Ficha Pessoal, que ele aprovou: o CSS é
copiado de lá. Os dados saem do arquivo de dados (catalogo-projeto-m.json) e, no que ele ainda não tem (as Passivas
e as aptidões), das tabelas do livro. Nada de regra é digitado aqui.

    python3 mockup/estudo_amaldicoada.py
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
LIVRO = "/media/mizuki/HD Externo II/Claude/Claude 2/sistema/05-material/livro/manual"
CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
DEC = json.load(open(os.path.join(RAIZ, "decisoes-ficha.json"), encoding="utf-8"))


def tabela_do_livro(arquivo, titulo):
    """as linhas da tabela que vem depois de **titulo** no capítulo, como listas de células sem a crase"""
    linhas = open(os.path.join(LIVRO, arquivo), encoding="utf-8").read().split("\n")
    i = next(k for k, l in enumerate(linhas) if l.strip() == f"**{titulo}**")
    out = []
    for l in linhas[i + 1:]:
        if l.startswith("|"):
            cel = [c.strip().replace("`", "").replace("**", "") for c in l.strip().strip("|").split("|")]
            if not set("".join(cel)) <= set("-: "):
                out.append(cel)
        elif out:
            break
    return out[1:]          # sem o cabeçalho


passivas = [{"n": c[0], "cp": c[1], "faz": c[2]} for c in tabela_do_livro("40-fundamento.md", "Lista")]
aptidoes = [{"n": c[0], "req": c[1], "cp": c[2], "escala": c[3]} for c in tabela_do_livro("45-aptidoes-e-refino.md", "Como ler uma aptidão")]

def prontos_do_livro():
    """os feitiços prontos do capítulo de Fundamento, lidos da tabela `Como foi montado`: enchem o exemplo de ficha
    cheia e servem de prova da conta, porque cada um traz o resultado que o livro imprime"""
    from math import ceil
    preco = lambda peso, c: {"Leve": ceil(c / 2), "Media": c, "Pesada": ceil(c * 1.5)}[peso]
    txt = open(os.path.join(LIVRO, "40-fundamento.md"), encoding="utf-8").read()
    txt = txt[txt.index("## Feitiços prontos"):txt.index("### Técnicas Máximas")]
    out, classe, lib = [], None, False
    for l in txt.split("\n"):
        m = re.match(r"### Classe (\d)", l)
        if m:
            classe = int(m.group(1))
        elif l.startswith("### Liberações"):
            lib = True
        if not l.startswith("| `"):
            continue
        nome, como, resultado = [c.strip() for c in l.strip().strip("|").split("|")]
        f = {"nome": nome.strip("`"), "classe": classe, "lib": lib, "mel": [], "res": [], "livro": resultado.replace("`", "")}
        for peca in como.split(" · "):
            m = re.match(r"Classe (\d)$", peca)
            if m:
                f["classe"] = int(m.group(1)); continue
            n = re.match(r"`([^`]+)`", peca).group(1)
            valor = re.search(r"\(([−+])(\d+)", peca)
            if n in CAT["formas"] and "forma" not in f:
                f["forma"] = n
            elif n in CAT["restricoes"]:
                niveis = CAT["restricoes"][n]["devolve"].split(" ou ")
                nv = [x for x in niveis if preco(x, f["classe"]) == int(valor.group(2))]
                assert valor.group(1) == "+" and nv, (f["nome"], peca)
                f["res"].append(n if len(niveis) == 1 else n + "|" + nv[0])
            else:
                assert (n in CAT["melhorias"] or n in CAT["condicoes"]) and valor.group(1) == "−", (f["nome"], peca)
                f["mel"].append(n)
        m = re.search(r"(\d+) dados viram", resultado) or re.search(r"(\d+)d8", resultado)
        t = re.search(r"(\d+) de vida temporária", resultado)
        f["dados"] = int(m.group(1)) if m else int(t.group(1)) // 3 if t else 0 if "zero dano" in resultado else None
        out.append(f)
    return out


dados = {
    "prontos": prontos_do_livro(),
    "versao": CAT["_meta"]["versao"],
    "familias": CAT["familias"],
    "formas": CAT["formas"],
    "melhorias": CAT["melhorias"],
    "restricoes": CAT["restricoes"],
    "condicoes": CAT["condicoes"],
    "pares": [[p["a"], p["b"]] for p in DEC["A3_incompatibilidades"]["pares"]],
    "espalham": CAT["fundamento"]["espalham_dano_e_contam_no_teto"],
    "passivas": passivas,
    "aptidoes": aptidoes,
}

velho = open(os.path.join(AQUI, "ficha-pessoal-estudo.html"), encoding="utf-8").read()
css = re.search(r"<style>\n(.*?)</style>", velho, re.S).group(1)
modelo = open(os.path.join(AQUI, "ficha-amaldicoada-estudo.modelo.html"), encoding="utf-8").read()
assert modelo.count("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/") == 1 and modelo.count("/*DADOS*/") == 1
saida = modelo.replace("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/", css).replace(
    "/*DADOS*/", json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
destino = os.path.join(AQUI, "ficha-amaldicoada-estudo.html")
open(destino, "w", encoding="utf-8").write(saida)
print(f"{destino}: {len(saida) // 1024} KB · {len(dados['melhorias'])} Melhorias, {len(dados['restricoes'])} Restrições, "
      f"{len(dados['formas'])} Formas, {len(passivas)} Passivas, {len(aptidoes)} aptidões")
