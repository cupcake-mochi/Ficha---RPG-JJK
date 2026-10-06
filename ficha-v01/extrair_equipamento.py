# -*- coding: utf-8 -*-
"""Lê do livro o que cada propriedade de arma faz, e grava em ficha-v01/equipamento-do-livro.json.

    python3 ficha-v01/extrair_equipamento.py            # lê o manual.txt e regrava o arquivo
    python3 ficha-v01/extrair_equipamento.py --confere  # só compara o arquivo com o manual.txt, sem gravar

Por que este arquivo existe: a FICHA PESSOAL mostra, embaixo da arma em uso, as propriedades dela, e o Mizuki pediu
em 01/10/2026 uma nota dizendo o que cada uma faz. O catalogo-projeto-m.json traz as propriedades de cada arma, mas
não o texto delas. O gerador (ficha_pessoal.py) nunca lê o livro: lê só este arquivo, que mora no repositório.

04/10/2026: o livro passou a ser a candidata reconstruída, e o script lê o manual.txt do repositório pelo livro.py, no
lugar do capítulo em Markdown do HD. A tabela Propriedades do livro novo já escreve a regra inteira de cada uma, então a
"regra da seção" que a v0.331 completava ficou vazia; Volumosa e Embainhada, as restrições de arma, saem das frases
de Armas escondidas que abrem pelo nome delas.

Nenhum texto é digitado aqui: a tabela vira lista, e cada frase tem de estar no manual palavra por palavra.
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import livro as Lv

SAIDA = os.path.join(AQUI, "equipamento-do-livro.json")


def extrai():
    cap = Lv.secao("8. Equipamento")
    fonte = json.load(open(os.path.join(os.path.dirname(AQUI), "manual-fonte.json"), encoding="utf-8"))
    _, props = Lv.tabela(Lv.secao("Propriedades", dentro=cap), "Propriedade")
    escondidas = Lv.paragrafos(Lv.secao("Armas escondidas", dentro=cap))
    restricoes = []
    for nome in ("Volumosa", "Embainhada"):
        p = next(x for x in escondidas if x.startswith(nome + ": "))
        faz = p[len(nome) + 2:]
        restricoes.append({"nome": nome, "faz": faz[:1].upper() + faz[1:], "ver": None})
    alc = next(f for n, f in props if n == "Alcance")
    m = re.fullmatch(r"O alcance corpo a corpo da arma é ([\d,]+ m)\. Sem essa propriedade, o alcance comum é ([\d,]+ m)\.", alc)
    if not m:
        raise SystemExit(f"a propriedade Alcance mudou de frase: {alc!r}")
    return {
        "_meta": {"versao_do_livro": fonte["livro"], "sha256_do_livro": fonte["sha256"], "capitulo": "8. Equipamento",
                  "o_que_e": "o texto das propriedades e das restrições de arma, que o catalogo-projeto-m.json não traz"},
        "propriedades": [{"nome": n, "faz": f, "ver": None} for n, f in props],
        "restricoes": restricoes,
        "a_regra_da_secao": {},
        "alcance_no_corpo_a_corpo": {"padrao": m.group(2), "o_que_chega_mais_longe": m.group(1)},
        "soco": Lv.frase("O dado desarmado é d4 com maestria 1, d6 com maestria 2, d8 com maestria 3 e d10 com maestria 4."),
        "escudo": Lv.frase("Some a proteção de um escudo empunhado à proteção que já utiliza, respeitando o teto de Destreza dele."),
    }


if __name__ == "__main__":
    novo = extrai()
    if "--confere" in sys.argv:
        velho = json.load(open(SAIDA, encoding="utf-8"))
        igual = json.dumps(velho, ensure_ascii=False, sort_keys=True) == json.dumps(novo, ensure_ascii=False, sort_keys=True)
        print("o arquivo bate com o livro" if igual else "o arquivo NAO bate com o livro")
        sys.exit(0 if igual else 1)
    json.dump(novo, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{SAIDA}: {len(novo['propriedades'])} propriedades, {len(novo['restricoes'])} restrições de arma")
